export interface DesignViolation {
  rule: string
  file: string
  found: string
}

/** Arquivo de `src` (caminho `src/...`) e o seu código-fonte. */
export type Sources = Record<string, string>

// Cor em hex. O recuo à esquerda e o fim da palavra evitam âncoras e ids como `#conteudo`.
const HEX = /(?<![\w&])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})(?![\w-])/g
const COLOR_FUNCTION = /\b(?:rgba?|hsla?|hwb|oklch|oklab|lab|lch|color-mix)\(/g

// Classe arbitrária de cor, fonte, traço ou sombra: `bg-[…]`, `text-[15px]`, `font-[600]`. Classes de layout
// (`min-w-[36rem]`, `grid-cols-[…]`, `data-[…]`) ficam livres, e vale o que lê um token com `var(--…)`.
const ARBITRARY_CLASS =
  /(?<![\w-])(?:bg|text|border(?:-[xytrblse])?|ring(?:-offset)?|outline|fill|stroke|decoration|accent|caret|divide|from|via|to|shadow|inset-shadow|drop-shadow|font|leading|tracking)-\[([^\]\s]+)\]/g

// Propriedade de cor ou de fonte em `style={{ … }}` com texto solto; `var(--token)` é aceito.
const LOOSE_STYLE =
  /\b(?:color|backgroundColor|background|borderColor|borderTopColor|borderBottomColor|fill|stroke|boxShadow|fontSize|fontFamily|fontWeight|lineHeight|letterSpacing)\s*:\s*(['"`])(?!var\(--)([^'"`]*)\1/g

/**
 * Regras de design de `src` (design-system.md §12, D-055): cor, fonte e traço só entram por token.
 * Componentes usam classes de token (`bg-surface`, `text-ui`), e `#RRGGBB` mora só em `tokens.css`.
 */
export function checkDesignRules(sources: Sources): DesignViolation[] {
  const violations: DesignViolation[] = []

  for (const [file, source] of Object.entries(sources)) {
    const scan = (rule: string, pattern: RegExp, accept?: (match: RegExpMatchArray) => boolean) => {
      for (const match of source.matchAll(pattern)) {
        if (accept?.(match)) continue
        violations.push({ rule, file, found: match[0] })
      }
    }

    scan('sem-hex', HEX)
    scan('sem-cor-funcional', COLOR_FUNCTION)
    scan('classe-arbitraria-sem-token', ARBITRARY_CLASS, (match) =>
      (match[1] as string).includes('var(--'),
    )
    scan('style-com-valor-solto', LOOSE_STYLE)
  }

  return violations
}
