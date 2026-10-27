/// <reference types="node" />
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'

const root = join(import.meta.dirname, '../..')
const main = readFileSync(join(root, 'src/main.tsx'), 'utf-8')
const html = readFileSync(join(root, 'index.html'), 'utf-8')

const imports = [...main.matchAll(/import '([^']+\.css)'/g)].map((m) => m[1] as string)
const preloads = [...html.matchAll(/<link[^>]*rel="preload"[^>]*>/g)].map((m) => m[0])

describe('carregamento das fontes (guia, págs. 25 e 29)', () => {
  it('carrega a Newsreader com o eixo óptico, como o guia a desenha', () => {
    expect(imports).toContain('@fontsource-variable/newsreader/opsz.css')
    expect(imports).toContain('@fontsource-variable/newsreader/opsz-italic.css')
    expect(imports.filter((i) => i.includes('newsreader/wght'))).toEqual([])
  })

  it('faz preload da Newsreader 400 e da Plus Jakarta Sans 400, em latin', () => {
    const hrefs = preloads.map((tag) => tag.match(/href="([^"]+)"/)?.[1])
    expect(hrefs).toContain(
      '/node_modules/@fontsource-variable/newsreader/files/newsreader-latin-opsz-normal.woff2',
    )
    expect(hrefs).toContain(
      '/node_modules/@fontsource-variable/plus-jakarta-sans/files/plus-jakarta-sans-latin-wght-normal.woff2',
    )
  })

  it('declara o preload como fonte woff2 com crossorigin, o que o navegador exige', () => {
    expect(preloads).toHaveLength(2)
    for (const tag of preloads) {
      expect(tag).toContain('as="font"')
      expect(tag).toContain('type="font/woff2"')
      expect(tag).toContain('crossorigin')
    }
  })

  it('só faz preload de arquivos que existem', () => {
    const missing = preloads
      .map((tag) => tag.match(/href="([^"]+)"/)?.[1] as string)
      .filter((href) => !existsSync(join(root, href)))
    expect(missing).toEqual([])
  })
})
