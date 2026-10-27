/// <reference types="node" />
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { marca } from '../../../../docs/design/identidade-visual/tokens.json'

const root = join(import.meta.dirname, '../..')
const html = readFileSync(join(root, 'index.html'), 'utf-8')

const linkHrefs = (rel: string) =>
  [...html.matchAll(new RegExp(`<link[^>]*rel="${rel}"[^>]*href="([^"]+)"`, 'g'))].map(
    (m) => m[1] as string,
  )

describe('index.html', () => {
  it('declara o favicon em SVG, com o .ico de reserva', () => {
    const icons = linkHrefs('icon')
    expect(icons).toContain('/brand/favicon/altare-favicon.svg')
    expect(icons).toContain('/brand/favicon/favicon.ico')
  })

  it('declara o apple-touch-icon de 180 px', () => {
    expect(linkHrefs('apple-touch-icon')).toEqual(['/brand/app-icon/altare-app-icon-180.png'])
  })

  it('só aponta para arquivos que existem em public/', () => {
    const hrefs = [...linkHrefs('icon'), ...linkHrefs('apple-touch-icon')]
    const missing = hrefs.filter((href) => !existsSync(join(root, 'public', href)))
    expect(missing).toEqual([])
  })

  it('usa como theme-color o fundo do tema claro do tokens.json', () => {
    const color = html.match(/<meta[^>]*name="theme-color"[^>]*content="([^"]+)"/)?.[1]
    expect(color).toBe(marca.app_icon.theme_color_claro)
  })
})
