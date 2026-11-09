import { ApiError } from '@/lib/api/errors'
import type { ChecklistProgress } from '../api/schedule'

/** Quantos itens do checklist ainda estão em aberto, a partir do "N de M" que a API entrega. */
export function openItemsCount(progress: ChecklistProgress): number {
  return Math.max(progress.total - progress.done, 0)
}

/** O servidor recusou concluir porque há itens em aberto que a tela não via: o dado era velho. */
export function isOpenItemsError(error: unknown): boolean {
  return error instanceof ApiError && error.code === 'checklist_open_items'
}
