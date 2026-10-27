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
  forma: { raios: Record<string, number>; sombras: Record<string, string> }
  movimento: { fast: string; base: string; delight: string }
}

// design-system.md §3.1 e §4: valores que o tokens.json não carrega.
const SCRIM = 'rgb(35 42 34 / .45)'
const EYEBROW_TRACKING = '.08em'
const DESKTOP_BREAKPOINT = '48rem'

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
    `  --font-${key}: "${tipografia[key].familia}", ${tipografia[key].fallback};`

  const root = [
    ':root, [data-theme="light"] {',
    '  color-scheme: light;',
    ...claro.map((c) => `  --${c.token}: ${c.hex};`),
    `  --primary-ink: ${primaryInk};`,
    '  --focus-ring: var(--primary);',
    `  --scrim: ${SCRIM};`,
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

  return `${[header, root, theme, ...tipografia.escala.map(textUtility), reducedMotion].join('\n\n')}\n`
}
