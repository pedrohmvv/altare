import { readdirSync, statSync } from 'node:fs'
import { join } from 'node:path'

/** Arquivos de uma pasta (recursivo), como caminhos relativos com "/" e em ordem alfabética. */
export function listFiles(dir: string): string[] {
  return readdirSync(dir, { recursive: true, encoding: 'utf-8' })
    .map((entry) => entry.split('\\').join('/'))
    .filter((entry) => statSync(join(dir, entry)).isFile())
    .sort()
}
