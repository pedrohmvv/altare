/// <reference types="node" />
import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import realTokens from '../../../../docs/design/identidade-visual/tokens.json'
import { buildTokensCss, type Tokens } from '../../scripts/tokens'

const tokens: Tokens = {
  claro: [
    { token: 'canvas', hex: '#F9F5EC' },
    { token: 'primary', hex: '#3A4B3C' },
  ],
  apoio: { 'primary-ink': '#FFFDF9' },
  tipografia: {
    serif: { familia: 'Newsreader', fallback: 'Georgia, serif' },
    sans: { familia: 'Plus Jakarta Sans', fallback: 'system-ui, sans-serif' },
    mono: { familia: 'JetBrains Mono', fallback: 'ui-monospace, monospace' },
    escala: [
      { token: 'display', familia: 'serif', px: 40, lh: 48, mobile: '32/40', peso: 500 },
      { token: 'body', familia: 'sans', px: 16, lh: 24, mobile: '16/24', peso: 400 },
      { token: 'num', familia: 'mono', px: 16, lh: 24, mobile: '16/24', peso: 400 },
      { token: 'eyebrow', familia: 'sans', px: 12, lh: 16, mobile: '12/16', peso: 600 },
    ],
  },
  forma: {
    raios: { control: 6, pill: 9999 },
    sombras: { 'nivel-1': '0 4px 16px rgb(35 42 34 / .08)' },
    textura_opacidade: 0.035,
  },
  movimento: {
    fast: '150ms cubic-bezier(.2,.8,.2,1)',
    base: '220ms cubic-bezier(.2,.8,.2,1) / cubic-bezier(.4,0,1,1)',
    delight: '400ms (selo de decisão registrada)',
  },
}

const css = buildTokensCss(tokens)
const versionedCss = readFileSync(join(import.meta.dirname, 'tokens.css'), 'utf-8')

describe('buildTokensCss', () => {
  it('avisa no cabeçalho que o arquivo é gerado e não deve ser editado', () => {
    expect(css.startsWith('/*')).toBe(true)
    expect(css).toContain('Não edite')
  })

  it('declara as cores do tema claro como variáveis do :root', () => {
    expect(css).toContain(':root, [data-theme="light"] {')
    expect(css).toContain('color-scheme: light;')
    expect(css).toContain('--canvas: #F9F5EC;')
    expect(css).toContain('--primary: #3A4B3C;')
  })

  it('deriva primary-ink, focus-ring e scrim sem depender do tokens.json', () => {
    expect(css).toContain('--primary-ink: #FFFDF9;')
    expect(css).toContain('--focus-ring: var(--primary);')
    expect(css).toContain('--scrim: rgb(35 42 34 / .45);')
  })

  it('não emite o tema escuro (D-028)', () => {
    expect(css).not.toContain('data-theme="dark"')
  })

  it('zera a paleta padrão do Tailwind antes de mapear as cores semânticas', () => {
    const reset = css.indexOf('--color-*: initial;')
    const mapped = css.indexOf('--color-canvas: var(--canvas);')
    expect(reset).toBeGreaterThan(-1)
    expect(mapped).toBeGreaterThan(reset)
  })

  it('mapeia as famílias pelo nome do Fontsource e da marca, com a reserva de métrica antes dos fallbacks do tokens.json', () => {
    expect(css).toContain(
      '--font-serif: "Newsreader Variable", "Newsreader", "Newsreader Fallback", Georgia, serif;',
    )
    expect(css).toContain(
      '--font-sans: "Plus Jakarta Sans Variable", "Plus Jakarta Sans", "Plus Jakarta Sans Fallback", system-ui, sans-serif;',
    )
    expect(css).toContain(
      '--font-mono: "JetBrains Mono Variable", "JetBrains Mono", "JetBrains Mono Fallback", ui-monospace, monospace;',
    )
  })

  // identity.md §4 e guia, pág. 29: fallbacks com size-adjust para reduzir o salto de layout (D-054).
  it('declara a reserva de cada família com size-adjust sobre uma fonte local', () => {
    expect(css).toContain('font-family: "Newsreader Fallback";\n  src: local("Georgia");')
    expect(css).toContain('font-family: "Plus Jakarta Sans Fallback";\n  src: local("Arial");')
    expect(css).toContain('font-family: "JetBrains Mono Fallback";\n  src: local("Courier New");')
    expect(css.match(/size-adjust: [\d.]+%;/g)).toHaveLength(3)
  })

  it('gera o utilitário de texto com tamanho mobile e o desktop em media query', () => {
    expect(css).toContain('@utility text-display {')
    expect(css).toContain('font-family: var(--font-serif);')
    expect(css).toContain('font-size: 2rem;')
    expect(css).toContain('line-height: 2.5rem;')
    expect(css).toContain('@media (min-width: 48rem) {')
    expect(css).toContain('font-size: 2.5rem;')
    expect(css).toContain('line-height: 3rem;')
  })

  it('não repete a media query quando mobile e desktop têm o mesmo tamanho', () => {
    const body = css.slice(css.indexOf('@utility text-body {'), css.indexOf('@utility text-num {'))
    expect(body).toContain('font-family: var(--font-sans);')
    expect(body).not.toContain('@media')
  })

  it('aplica números tabulares nos tokens mono e caixa-alta no eyebrow', () => {
    const num = css.slice(
      css.indexOf('@utility text-num {'),
      css.indexOf('@utility text-eyebrow {'),
    )
    expect(num).toContain('font-variant-numeric: tabular-nums;')
    expect(css.slice(css.indexOf('@utility text-eyebrow {'))).toContain(
      'text-transform: uppercase;',
    )
  })

  it('expõe raios e sombras do tokens.json', () => {
    expect(css).toContain('--radius-control: 6px;')
    expect(css).toContain('--radius-pill: 9999px;')
    expect(css).toContain('--shadow-nivel-1: 0 4px 16px rgb(35 42 34 / .08);')
  })

  it('expõe a opacidade da textura de papel no :root', () => {
    const root = css.slice(
      css.indexOf(':root, [data-theme="light"] {'),
      css.indexOf('@theme inline {'),
    )
    expect(root).toContain('--texture-opacity: 0.035;')
  })

  it('separa duração e curva do movimento, mesmo no texto irregular do json', () => {
    expect(css).toContain('--duration-fast: 150ms;')
    expect(css).toContain('--duration-base: 220ms;')
    expect(css).toContain('--duration-delight: 400ms;')
    expect(css).toContain('--ease-standard: cubic-bezier(.2,.8,.2,1);')
    expect(css).toContain('--ease-exit: cubic-bezier(.4,0,1,1);')
  })

  it('zera animações e transições com prefers-reduced-motion', () => {
    expect(css).toContain('@media (prefers-reduced-motion: reduce) {')
  })

  it('é determinístico', () => {
    expect(buildTokensCss(tokens)).toBe(css)
  })
})

describe('tokens.css versionado', () => {
  it('está em dia com o tokens.json (rode `pnpm tokens:build` se este teste falhar)', () => {
    expect(buildTokensCss(realTokens as Tokens)).toBe(versionedCss)
  })
})

// Guia, pág. 26 e D-054: o guia desenha texto de interface em 15, 13 e 11 px, que a escala original
// (40/32/24/20/18/16/14/12) não tinha.
describe('escala tipográfica do tokens.json', () => {
  const escala = (realTokens as Tokens).tipografia.escala
  const find = (token: string) => escala.find((e) => e.token === token)

  it.each([
    ['ui', 15, 22],
    ['ui-sm', 13, 18],
    ['ui-xs', 11, 14],
  ])('tem o token %s em %i/%i, sempre em sans', (token, px, lh) => {
    expect(find(token)).toMatchObject({ familia: 'sans', px, lh, mobile: `${px}/${lh}` })
  })

  it('gera o utilitário de texto de cada tamanho novo', () => {
    const generated = buildTokensCss(realTokens as Tokens)
    expect(generated).toContain('@utility text-ui {')
    expect(generated).toContain('@utility text-ui-sm {')
    expect(generated).toContain('@utility text-ui-xs {')
  })
})
