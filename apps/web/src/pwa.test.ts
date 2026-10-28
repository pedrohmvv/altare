import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import tokens from '../../../docs/design/identidade-visual/tokens.json'
import { manifest, pwaOptions } from '../scripts/pwa-manifest'

const publicFile = (src: string) => join(import.meta.dirname, '..', 'public', src)

/** Largura e altura de um PNG, lidas do cabeçalho IHDR (bytes 16 a 24). */
function pngSize(src: string) {
  const bytes = readFileSync(publicFile(src))
  return `${bytes.readUInt32BE(16)}x${bytes.readUInt32BE(20)}`
}

describe('manifesto do app instalável', () => {
  it('se chama Altare, em português, e abre como um app, sem a barra do navegador', () => {
    expect(manifest.name).toBe('Altare')
    expect(manifest.short_name).toBe('Altare')
    expect(manifest.lang).toBe('pt-BR')
    expect(manifest.display).toBe('standalone')
    expect(manifest.start_url).toBe('/')
    expect(manifest.scope).toBe('/')
  })

  it('descreve o produto com a voz do Altare e sem slogan (D-025)', () => {
    expect(manifest.description).toBe('O planejamento do casamento de vocês, num lugar só.')
    expect(manifest.description.length).toBeLessThanOrEqual(120)
    expect(manifest.description.toLowerCase()).not.toContain('altar no centro')
  })

  it('usa a cor do tokens.json para a barra do sistema e para a tela de abertura', () => {
    expect(manifest.theme_color).toBe(tokens.marca.app_icon.theme_color_claro)
    expect(manifest.background_color).toBe(tokens.marca.app_icon.theme_color_claro)
  })

  it('tem a mesma cor do <meta name="theme-color"> do index.html', () => {
    const html = readFileSync(join(import.meta.dirname, '..', 'index.html'), 'utf-8')
    const meta = /<meta name="theme-color" content="(#[0-9A-Fa-f]{6})"/.exec(html)?.[1]
    expect(meta?.toUpperCase()).toBe(manifest.theme_color.toUpperCase())
  })

  it('traz o ícone de 192 e de 512 px, comum e adaptável ("maskable")', () => {
    const chave = (i: { sizes: string; purpose: string }) => `${i.sizes}/${i.purpose}`
    expect(manifest.icons.map(chave).sort()).toEqual([
      '192x192/any',
      '192x192/maskable',
      '512x512/any',
      '512x512/maskable',
    ])
  })

  it.each(manifest.icons.map((icon) => [icon.src, icon] as const))(
    'o ícone %s existe, é PNG e tem o tamanho que o manifesto diz',
    (src, icon) => {
      expect(existsSync(publicFile(src))).toBe(true)
      expect(icon.type).toBe('image/png')
      expect(pngSize(src)).toBe(icon.sizes)
    },
  )

  it('os ícones são os de marca copiados do guia, nunca um desenhado à parte', () => {
    for (const icon of manifest.icons) {
      expect(icon.src).toMatch(/^\/brand\/app-icon\/altare-app-icon-(192|512)\.png$/)
    }
  })
})

describe('service worker', () => {
  it('a versão nova espera a próxima abertura: não recarrega a tela no meio de um formulário', () => {
    expect(pwaOptions.registerType).toBe('prompt')
  })

  it('o manifesto do plugin é o mesmo deste módulo', () => {
    expect(pwaOptions.manifest).toBe(manifest)
  })

  it('nunca serve a casca no lugar de uma rota da API', () => {
    const { navigateFallbackDenylist } = pwaOptions.workbox
    expect(navigateFallbackDenylist.some((r) => r.test('/api/v1/auth/me'))).toBe(true)
    expect(navigateFallbackDenylist.some((r) => r.test('/api/v1/files/abc'))).toBe(true)
    expect(navigateFallbackDenylist.some((r) => r.test('/orcamento'))).toBe(false)
  })

  it('não guarda nenhuma resposta da API: só o app shell fica em cache (sem escrita offline)', () => {
    expect(pwaOptions.workbox.runtimeCaching ?? []).toEqual([])
  })
})
