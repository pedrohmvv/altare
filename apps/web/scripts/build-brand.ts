import { cpSync, mkdirSync, rmSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { planBrandCopy } from './brand'
import { listFiles } from './files'

const source = fileURLToPath(new URL('../../../docs/design/identidade-visual/', import.meta.url))
const target = fileURLToPath(new URL('../public/brand/', import.meta.url))

const plan = planBrandCopy(listFiles(source))

rmSync(target, { recursive: true, force: true })
for (const { from, to } of plan) {
  mkdirSync(dirname(join(target, to)), { recursive: true })
  cpSync(join(source, from), join(target, to))
}
console.log(`${plan.length} ativos de marca copiados para public/brand`)
