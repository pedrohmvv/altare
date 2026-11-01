import { copy } from '../copy'

/** "3 de 4 confirmados" e, se houver, "1 não irá" (F-CNV-04, regra 1): vem da API, só se escreve. */
export function summaryText(summary: {
  total: number
  confirmed: number
  declined: number
}): string {
  const base = copy.household.summary(summary.total, summary.confirmed)
  return summary.declined > 0 ? `${base} · ${copy.household.declined(summary.declined)}` : base
}
