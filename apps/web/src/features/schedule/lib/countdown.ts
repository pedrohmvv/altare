import { copy } from '../copy'

/**
 * A contagem regressiva em linguagem direta, a partir dos dias que a API calculou: o navegador não
 * sabe "hoje" nem soma datas (stack.md §5.1). Nulo é concluído, arquivado ou sem prazo: sem contagem.
 */
export function countdownText(daysLeft: number | null): string | null {
  if (daysLeft === null) return null
  if (daysLeft === 0) return copy.countdown.today
  return daysLeft > 0 ? copy.countdown.left(daysLeft) : copy.countdown.overdue(-daysLeft)
}
