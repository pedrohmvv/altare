export interface FormatMoneyOptions {
  /** `auto` omite os centavos quando são zero; `always` os mostra sempre (parcelas e pagamentos). */
  precision?: 'auto' | 'always'
  /** Mostra `+` nos positivos (extras e diferenças). O zero nunca leva sinal. */
  signed?: boolean
}

const NBSP = ' '
const MINUS = '−'

/**
 * Formata um valor em centavos inteiros como `R$ 1.234,56` (design-system.md §9 e §11).
 * Aceita só inteiros seguros: dinheiro nunca é `float` (stack.md §4).
 */
export function formatMoney(
  cents: number,
  { precision = 'auto', signed = false }: FormatMoneyOptions = {},
): string {
  if (!Number.isSafeInteger(cents)) {
    throw new RangeError(`O valor deve ser um inteiro de centavos, mas veio ${cents}`)
  }

  const abs = Math.abs(cents)
  const reais = String(Math.trunc(abs / 100)).replace(/\B(?=(\d{3})+(?!\d))/g, '.')
  const rest = abs % 100
  const decimals = precision === 'always' || rest !== 0 ? `,${String(rest).padStart(2, '0')}` : ''
  const sign = cents < 0 ? MINUS : signed && cents > 0 ? '+' : ''

  return `${sign && `${sign}${NBSP}`}R$${NBSP}${reais}${decimals}`
}

/** Reais com ponto de milhar e vírgula nos centavos: `28.000`, `28.000,00`, `28000,5`. */
const MONEY_PATTERN = /^(\d+|\d{1,3}(?:\.\d{3})+)(?:,(\d{1,2}))?$/

/**
 * Lê o que a pessoa digitou ("R$ 28.000,00") como centavos inteiros, ou `null` quando não dá para
 * ter certeza. No Brasil o ponto separa milhar: `28.5` não vira 28,50, é recusado em vez de adivinhado.
 */
export function parseMoney(text: string): number | null {
  const cleaned = text.replace(/R\$/g, '').replace(/[\s ]/g, '')
  const match = MONEY_PATTERN.exec(cleaned)
  if (!match) return null
  const reais = Number((match[1] ?? '').replaceAll('.', ''))
  const cents = Number((match[2] ?? '').padEnd(2, '0'))
  const total = reais * 100 + cents
  return Number.isSafeInteger(total) ? total : null
}

/** O número como vai no campo de entrada, sem o `R$` (que é o prefixo do campo): `28.000,00`. */
export function formatMoneyPlain(cents: number): string {
  return formatMoney(cents, { precision: 'always' }).replace(/^R\$ /, '')
}
