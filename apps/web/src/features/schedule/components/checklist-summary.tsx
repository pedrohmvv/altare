import type { ChecklistProgress } from '../api/schedule'
import { copy } from '../copy'

/** O "Checklist: 2 de 5" do cartão e da linha (F-CRN-07), em texto; sem itens, não diz nada. */
export function ChecklistSummary({ progress }: { progress: ChecklistProgress }) {
  if (progress.total === 0) return null
  return (
    <span className="text-ui-sm text-ink-muted">
      {copy.checklist.summary(progress.done, progress.total)}
    </span>
  )
}
