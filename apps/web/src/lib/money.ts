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

  return `${sign}R$${NBSP}${reais}${decimals}`
}
