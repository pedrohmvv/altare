/// <reference types="node" />
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { buildGraph, checkBoundaries } from '../scripts/architecture'

const rules = (graph: Record<string, string[]>) => checkBoundaries(graph).map((v) => v.rule)

describe('limites entre camadas (architecture.md §11)', () => {
  it('um primitivo de ui não importa feature nem a camada de API', () => {
    expect(
      rules({
        'src/components/ui/button.tsx': ['src/features/budget/index.ts'],
        'src/components/ui/table.tsx': ['src/lib/api/client.ts'],
      }),
    ).toEqual(['ui-nao-importa-features-nem-api', 'ui-nao-importa-features-nem-api'])
  })

  it('um primitivo de ui pode importar utilitários de lib', () => {
    expect(
      rules({ 'src/components/ui/button.tsx': ['src/lib/cn.ts', 'src/lib/money.ts'] }),
    ).toEqual([])
  })

  it('uma feature só importa outra feature pelo index.ts', () => {
    expect(
      rules({ 'src/features/budget/pages/budget-page.tsx': ['src/features/vendors/copy.ts'] }),
    ).toEqual(['feature-so-por-index'])
    expect(
      rules({ 'src/features/budget/pages/budget-page.tsx': ['src/features/vendors/index.ts'] }),
    ).toEqual([])
  })

  it('uma feature pode importar os próprios arquivos e os primitivos', () => {
    expect(
      rules({
        'src/features/budget/pages/budget-page.tsx': [
          'src/features/budget/copy.ts',
          'src/components/ui/page-header.tsx',
          'src/lib/money.ts',
        ],
      }),
    ).toEqual([])
  })

  it('uma feature não importa app nem routes', () => {
    expect(
      rules({
        'src/features/budget/pages/budget-page.tsx': [
          'src/app/shell/nav-config.ts',
          'src/routes/router.tsx',
        ],
      }),
    ).toEqual(['feature-nao-importa-app-nem-routes', 'feature-nao-importa-app-nem-routes'])
  })

  it('app e routes podem importar as features pelo index', () => {
    expect(
      rules({
        'src/routes/router.tsx': ['src/features/budget/index.ts', 'src/app/shell/app-shell.tsx'],
        'src/app/shell/app-shell.tsx': ['src/components/ui/dialog.tsx'],
      }),
    ).toEqual([])
  })

  it('não admite dependência circular, direta ou em cadeia', () => {
    expect(rules({ 'src/lib/a.ts': ['src/lib/b.ts'], 'src/lib/b.ts': ['src/lib/a.ts'] })).toContain(
      'sem-ciclos',
    )
    expect(
      rules({
        'src/lib/a.ts': ['src/lib/b.ts'],
        'src/lib/b.ts': ['src/lib/c.ts'],
        'src/lib/c.ts': ['src/lib/a.ts'],
      }),
    ).toContain('sem-ciclos')
  })

  it('um grafo em árvore, sem voltas, não tem ciclo', () => {
    expect(
      rules({
        'src/lib/a.ts': ['src/lib/b.ts', 'src/lib/c.ts'],
        'src/lib/b.ts': ['src/lib/c.ts'],
        'src/lib/c.ts': [],
      }),
    ).toEqual([])
  })

  it('lê imports estáticos, dinâmicos, com alias e relativos, e ignora os só de tipo', () => {
    const graph = buildGraph(join(import.meta.dirname))

    // dinâmico, pelo alias
    expect(graph['src/routes/router.tsx']).toContain('src/features/overview/index.ts')
    // estático, pelo alias
    expect(graph['src/routes/router.tsx']).toContain('src/app/shell/app-shell.tsx')
    // relativo
    expect(graph['src/features/overview/pages/overview-page.tsx']).toContain(
      'src/features/overview/copy.ts',
    )
    // `import type { RootSearch } from '@/routes/router'` não é dependência de execução
    expect(graph['src/app/shell/lens-switcher.tsx']).not.toContain('src/routes/router.tsx')
  })

  it('o código de src respeita todas as regras', () => {
    const graph = buildGraph(join(import.meta.dirname))

    expect(Object.keys(graph).length).toBeGreaterThan(50)
    expect(checkBoundaries(graph)).toEqual([])
  })
})
