import { CircleAlert } from 'lucide-react'
import type { ScheduleMilestone } from '../api/schedule'
import { copy } from '../copy'
import { waitingLines } from '../lib/blockers'

/**
 * O que a API diz sobre o marco além do estado: o que ele aguarda (nomes ou o motivo da categoria)
 * e, no concluído, os predecessores ainda não resolvidos. Tudo em texto e com ícone; nada é
 * recalculado aqui (stack.md §5.1).
 */
export function MilestoneNotes({ milestone }: { milestone: ScheduleMilestone }) {
  const lines = waitingLines(milestone)
  const unresolved = milestone.warnings
    .filter((warning) => warning.kind === 'depends_on_unresolved')
    .map((warning) => warning.title)
  if (lines.length === 0 && unresolved.length === 0) return null
  return (
    <div className="flex flex-col gap-0.5">
      {lines.map((line) => (
        <p key={line} className="text-body-sm text-ink-muted">
          {line}
        </p>
      ))}
      {unresolved.length > 0 && (
        <p className="flex items-start gap-1.5 text-body-sm text-attention-ink">
          <CircleAlert aria-hidden className="mt-0.5 size-4 shrink-0" />
          {copy.warnings.doneBefore(unresolved)}
        </p>
      )}
    </div>
  )
}
