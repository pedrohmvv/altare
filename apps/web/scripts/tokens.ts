export interface Tokens {
  claro: { token: string; hex: string }[]
  apoio: Record<string, string>
  tipografia: {
    serif: { familia: string; fallback: string }
    sans: { familia: string; fallback: string }
    mono: { familia: string; fallback: string }
    escala: {
      token: string
      familia: 'serif' | 'sans' | 'mono'
      px: number
      lh: number
      mobile: string
      peso: number
    }[]
  }
  forma: {
    raios: Record<string, number>
    sombras: Record<string, string>
    textura_opacidade: number
  }
  movimento: { fast: string; base: string; delight: string }
}

// design-system.md §3.1 e §4: valores que o tokens.json não carrega.
const SCRIM = 'rgb(35 42 34 / .45)'
const EYEBROW_TRACKING = '.08em'
const DESKTOP_BREAKPOINT = '48rem'
// O Fontsource publica as fontes variáveis como "<Família> Variable".
const FONTSOURCE_VARIABLE_SUFFIX = ' Variable'

// Reserva de métrica (identity.md §4, guia pág. 29, D-054): enquanto a fonte carrega, uma fonte local de
// largura parecida assume o lugar com `size-adjust`, para o texto não saltar quando a troca acontece.
// Medido com fontTools: largura média das letras do português (ponderada pela frequência) de cada fonte
// contra a local; `ascent` e `descent` da fonte divididos pelo `size-adjust`, como a regra CSS exige.
const FALLBACK_FACES = {
  serif: { local: 'Georgia', sizeAdjust: 90.5, ascent: 81.2, descent: 29.3 },
  sans: { local: 'Arial', sizeAdjust: 106.2, ascent: 97.7, descent: 20.9 },
  mono: { local: 'Courier New', sizeAdjust: 100, ascent: 102, descent: 30 },
} as const

const rem = (px: number) => `${px / 16}rem`

function parseMobileSize(mobile: string): { px: number; lh: number } {
  const [px, lh] = mobile.split('/').map(Number)
  if (!px || !lh) {
    throw new Error(`Tamanho mobile inválido no tokens.json: "${mobile}"`)
  }
  return { px, lh }
}

function parseMotion(motion: Tokens['movimento']) {
  const duration = (text: string) => {
    const found = text.match(/^(\d+ms)/)
    if (!found?.[1]) throw new Error(`Duração inválida no tokens.json: "${text}"`)
    return found[1]
  }
  const easings = (text: string) => text.match(/cubic-bezier\([^)]*\)/g) ?? []
  const standard = easings(motion.fast)[0]
  const exit = easings(motion.base)[1]
  if (!standard || !exit) {
    throw new Error('Curvas de movimento ausentes em movimento.fast ou movimento.base')
  }
  return {
    fast: duration(motion.fast),
    base: duration(motion.base),
    delight: duration(motion.delight),
    standard,
    exit,
  }
}

function textUtility(entry: Tokens['tipografia']['escala'][number]): string {
  const mobile = parseMobileSize(entry.mobile)
  const lines = [
    `  font-family: var(--font-${entry.familia});`,
    `  font-size: ${rem(mobile.px)};`,
    `  line-height: ${rem(mobile.lh)};`,
    `  font-weight: ${entry.peso};`,
  ]
  if (entry.familia === 'mono') lines.push('  font-variant-numeric: tabular-nums;')
  if (entry.token === 'eyebrow') {
    lines.push('  text-transform: uppercase;', `  letter-spacing: ${EYEBROW_TRACKING};`)
  }
  if (mobile.px !== entry.px || mobile.lh !== entry.lh) {
    lines.push(
      `  @media (min-width: ${DESKTOP_BREAKPOINT}) {`,
      `    font-size: ${rem(entry.px)};`,
      `    line-height: ${rem(entry.lh)};`,
      '  }',
    )
  }
  return `@utility text-${entry.token} {\n${lines.join('\n')}\n}`
}

export function buildTokensCss(tokens: Tokens): string {
  const { claro, apoio, tipografia, forma, movimento } = tokens
  const primaryInk = apoio['primary-ink']
  if (!primaryInk) throw new Error('apoio.primary-ink ausente no tokens.json')
  const motion = parseMotion(movimento)
  const font = (key: 'serif' | 'sans' | 'mono') =>
    `  --font-${key}: "${tipografia[key].familia}${FONTSOURCE_VARIABLE_SUFFIX}", "${tipografia[key].familia}", "${tipografia[key].familia} Fallback", ${tipografia[key].fallback};`
  const fallbackFaces = (['serif', 'sans', 'mono'] as const).map((key) => {
    const face = FALLBACK_FACES[key]
    return [
      '@font-face {',
      `  font-family: "${tipografia[key].familia} Fallback";`,
      `  src: local("${face.local}");`,
      `  size-adjust: ${face.sizeAdjust}%;`,
      `  ascent-override: ${face.ascent}%;`,
      `  descent-override: ${face.descent}%;`,
      '  line-gap-override: 0%;',
      '}',
    ].join('\n')
  })

  const root = [
    ':root, [data-theme="light"] {',
    '  color-scheme: light;',
    ...claro.map((c) => `  --${c.token}: ${c.hex};`),
    `  --primary-ink: ${primaryInk};`,
    '  --focus-ring: var(--primary);',
    `  --scrim: ${SCRIM};`,
    `  --texture-opacity: ${forma.textura_opacidade};`,
    '}',
  ].join('\n')

  const colorNames = [...claro.map((c) => c.token), 'primary-ink', 'focus-ring', 'scrim']
  const theme = [
    '@theme inline {',
    '  --color-*: initial;',
    ...colorNames.map((name) => `  --color-${name}: var(--${name});`),
    font('serif'),
    font('sans'),
    font('mono'),
    ...Object.entries(forma.raios).map(([name, px]) => `  --radius-${name}: ${px}px;`),
    ...Object.entries(forma.sombras).map(([name, value]) => `  --shadow-${name}: ${value};`),
    `  --duration-fast: ${motion.fast};`,
    `  --duration-base: ${motion.base};`,
    `  --duration-delight: ${motion.delight};`,
    `  --ease-standard: ${motion.standard};`,
    `  --ease-exit: ${motion.exit};`,
    '}',
  ].join('\n')

  const reducedMotion = [
    '@media (prefers-reduced-motion: reduce) {',
    '  *, ::before, ::after {',
    '    animation-duration: 0.01ms !important;',
    '    animation-iteration-count: 1 !important;',
    '    transition-duration: 0.01ms !important;',
    '    scroll-behavior: auto !important;',
    '  }',
    '}',
  ].join('\n')

  const header =
    '/* Gerado de docs/design/identidade-visual/tokens.json por `pnpm tokens:build`. Não edite. */'

  return `${[header, root, ...fallbackFaces, theme, ...tipografia.escala.map(textUtility), reducedMotion].join('\n\n')}\n`
}
