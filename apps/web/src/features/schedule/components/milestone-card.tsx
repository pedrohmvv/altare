import { cn } from '@/lib/cn'
import { formatDay } from '@/lib/date'
import type { ScheduleMilestone } from '../api/schedule'
import { copy } from '../copy'
import { ChecklistSummary } from './checklist-summary'
import { OptionalBadge, OverdueBadge, StateBadge } from './milestone-badges'
import { DeadlineDate, DeadlineDetails } from './milestone-deadline'
import { MilestoneNotes } from './milestone-notes'

/**
 * No celular, um cartão por marco (F-CRN-09): o título abre o painel (o botão cobre o cartão). O que
 * está Destravado ganha o contorno em sálvia, além do selo com texto e ícone: cor nunca é o único sinal.
 */
export function MilestoneCard({
  milestone,
  onOpen,
}: {
  milestone: ScheduleMilestone
  onOpen: (milestoneId: string, opener: HTMLElement) => void
}) {
  return (
    <li
      className={cn(
        'relative flex flex-col gap-2 rounded-card border bg-surface p-4',
        'transition-colors duration-fast ease-standard hover:border-border-strong',
        milestone.state === 'Destravado' ? 'border-consensus-ink' : 'border-border',
      )}
    >
      <h3 className="text-name text-ink">
        <button
          type="button"
          data-milestone-id={milestone.id}
          onClick={(event) => onOpen(milestone.id, event.currentTarget)}
          className="text-left after:absolute after:inset-0 after:rounded-card"
        >
          {milestone.title}
        </button>
      </h3>
      <div className="flex flex-wrap items-center gap-2">
        <StateBadge state={milestone.state} />
        {milestone.overdue && <OverdueBadge />}
        {milestone.optional && <OptionalBadge />}
      </div>
      <MilestoneNotes milestone={milestone} />
      <ChecklistSummary progress={milestone.checklist_progress} />
      <div className="flex flex-col gap-1 text-body-sm text-ink-muted">
        <p className="flex flex-wrap items-center justify-between gap-x-3">
          <span>
            <span className="sr-only">{`${copy.list.columns.responsible}: `}</span>
            {copy.responsibles[milestone.responsible]}
          </span>
          <span className="text-num-sm">
            <DeadlineDate milestone={milestone} format={formatDay} srLabel />
          </span>
        </p>
        <DeadlineDetails milestone={milestone} format={formatDay} align="end" />
      </div>
    </li>
  )
}
