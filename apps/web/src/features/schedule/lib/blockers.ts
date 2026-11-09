import type { ScheduleMilestone } from '../api/schedule'
import { copy } from '../copy'

/**
 * O que o marco aguarda, como a API entrega: os nomes dos marcos que faltam viram uma frase só
 * ("Aguardando: A, B") e o motivo da categoria já vem pronto, sem recalcular nada.
 */
export function waitingLines(milestone: Pick<ScheduleMilestone, 'blocked_by'>): string[] {
  const names = milestone.blocked_by.filter((b) => b.kind === 'milestone').map((b) => b.label)
  const reasons = milestone.blocked_by.filter((b) => b.kind === 'category').map((b) => b.label)
  return [...reasons, ...(names.length > 0 ? [copy.waiting.for(names)] : [])]
}
