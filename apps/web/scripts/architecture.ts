import { existsSync, readFileSync } from 'node:fs'
import { dirname, join, posix } from 'node:path'
import { listFiles } from './files'

export interface Violation {
  rule: string
  from: string
  to: string
}

/** Arquivo de `src` (caminho `src/...`) e os arquivos de `src` que ele importa. */
export type ImportGraph = Record<string, string[]>

const FEATURE = /^src\/features\/([^/]+)\//

/**
 * Regras de limite do frontend (architecture.md §11, altare-frontend). Substitui o
 * `dependency-cruiser`, que não suporta o Node 25 em uso (só as versões LTS).
 */
export function checkBoundaries(graph: ImportGraph): Violation[] {
  const violations: Violation[] = []
  const add = (rule: string, from: string, to: string) => violations.push({ rule, from, to })

  for (const [from, targets] of Object.entries(graph)) {
    const feature = FEATURE.exec(from)?.[1]
    for (const to of targets) {
      if (from.startsWith('src/components/ui/') && /^src\/(features\/|lib\/api)/.test(to)) {
        add('ui-nao-importa-features-nem-api', from, to)
      }
      const otherFeature = FEATURE.exec(to)?.[1]
      if (
        feature &&
        otherFeature &&
        feature !== otherFeature &&
        !to.endsWith(`${otherFeature}/index.ts`)
      ) {
        add('feature-so-por-index', from, to)
      }
      if (feature && /^src\/(app|routes)\//.test(to)) {
        add('feature-nao-importa-app-nem-routes', from, to)
      }
    }
  }

  return [...violations, ...findCycles(graph)]
}

function findCycles(graph: ImportGraph): Violation[] {
  const cycles: Violation[] = []
  const done = new Set<string>()
  const onPath = new Set<string>()

  const visit = (node: string) => {
    if (done.has(node)) return
    onPath.add(node)
    for (const next of graph[node] ?? []) {
      if (onPath.has(next)) cycles.push({ rule: 'sem-ciclos', from: node, to: next })
      else visit(next)
    }
    onPath.delete(node)
    done.add(node)
  }

  for (const node of Object.keys(graph)) visit(node)
  return cycles
}

// Imports que existem em tempo de execução: `import type` some na compilação e não conta.
const STATIC_IMPORT = /(?:^|\n)\s*(?:import|export)\s+(?!type\b)[^;'"]*?from\s*['"]([^'"]+)['"]/g
const SIDE_EFFECT_IMPORT = /(?:^|\n)\s*import\s*['"]([^'"]+)['"]/g
const DYNAMIC_IMPORT = /import\(\s*['"]([^'"]+)['"]\s*\)/g

function importSpecifiers(source: string): string[] {
  const found = new Set<string>()
  for (const pattern of [STATIC_IMPORT, SIDE_EFFECT_IMPORT, DYNAMIC_IMPORT]) {
    for (const match of source.matchAll(pattern)) found.add(match[1] as string)
  }
  return [...found]
}

function resolveImport(specifier: string, importer: string, root: string): string | undefined {
  const base = specifier.startsWith('@/')
    ? posix.join('src', specifier.slice(2))
    : specifier.startsWith('.')
      ? posix.join(dirname(importer), specifier)
      : undefined
  if (!base) return undefined // pacote de node_modules

  const withoutQuery = base.split('?')[0] as string
  const candidates = [
    withoutQuery,
    `${withoutQuery}.ts`,
    `${withoutQuery}.tsx`,
    `${withoutQuery}/index.ts`,
    `${withoutQuery}/index.tsx`,
  ]
  return candidates.find(
    (candidate) => /\.tsx?$/.test(candidate) && existsSync(join(root, candidate)),
  )
}

/** Lê os arquivos `.ts` e `.tsx` de `src` e monta o grafo de imports entre eles. */
export function buildGraph(srcDir: string): ImportGraph {
  const root = dirname(srcDir)
  const graph: ImportGraph = {}

  for (const file of listFiles(srcDir).filter((f) => /\.tsx?$/.test(f))) {
    const importer = `src/${file}`
    const source = readFileSync(join(srcDir, file), 'utf-8')
    graph[importer] = importSpecifiers(source)
      .map((specifier) => resolveImport(specifier, importer, root))
      .filter((target): target is string => target !== undefined)
  }
  return graph
}
