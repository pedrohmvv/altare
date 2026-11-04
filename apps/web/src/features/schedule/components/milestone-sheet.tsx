import { useId } from 'react'
import { Sheet, SheetContent } from '@/components/ui/sheet'
import { formatTableDay } from '@/lib/date'
import type { Schedule, ScheduleMilestone, SchedulePhase } from '../api/schedule'
import { copy } from '../copy'
import { OptionalBadge, OverdueBadge, StateBadge } from './milestone-badges'
import { DeadlineDate, DeadlineDetails } from './milestone-deadline'
import { type DeletedMilestone, DeleteMilestone } from './milestone-delete'
import { MilestoneDependencies } from './milestone-dependencies'
import { MilestoneForm } from './milestone-form'
import { MilestoneNotes } from './milestone-notes'
import { MilestoneStateActions } from './milestone-state-actions'
import { MilestoneWindow } from './milestone-window'

export interface MilestoneSheetProps {
  milestone: ScheduleMilestone
  /** A fase em que o marco está agora. */
  phase: SchedulePhase
  /** O cronograma inteiro: as fases e as categorias que o formulário oferece. */
  schedule: Schedule
  open: boolean
  onOpenChange: (open: boolean) => void
  /** Chamado quando o marco foi excluído: quem mostra a lista fecha o painel e oferece o Desfazer. */
  onDeleted: (deleted: DeletedMilestone) => void
  /** O painel abre pela URL, sem gatilho: quem abriu diz para onde o foco volta ao fechar. */
  onCloseAutoFocus?: (event: Event) => void
}

/**
 * O detalhe do marco sem sair da lista (design-system.md §10, item 2): lateral no computador, folha
 * inferior no celular. As ações de estado são imediatas, cada uma com a versão que a tela mostra; o
 * formulário guarda a versão de quando abriu, para um conflito nunca virar sobrescrita silenciosa.
 */
export function MilestoneSheet({
  milestone,
  phase,
  schedule,
  open,
  onOpenChange,
  onDeleted,
  onCloseAutoFocus,
}: MilestoneSheetProps) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        title={milestone.title}
        description={copy.sheet.phase(phase.title)}
        onCloseAutoFocus={onCloseAutoFocus}
        // O foco entra no painel, não no primeiro botão de estado: um Enter a mais não conclui nada.
        onOpenAutoFocus={(event) => {
          event.preventDefault()
          ;(event.currentTarget as HTMLElement | null)?.focus()
        }}
      >
        <div className="flex flex-col gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <StateBadge state={milestone.state} />
            {milestone.overdue && <OverdueBadge />}
            {milestone.optional && <OptionalBadge />}
          </div>
          <p className="flex items-start gap-2 text-body text-ink">
            <span className="text-ink-muted">{copy.sheet.deadline}</span>
            <span className="flex flex-col gap-0.5">
              <DeadlineDate milestone={milestone} format={formatTableDay} className="text-num" />
              <DeadlineDetails milestone={milestone} format={formatTableDay} showWindow={false} />
              {milestone.window && milestone.target_date !== null && (
                <span className="text-body-sm text-ink-muted">{copy.deadline.manual}</span>
              )}
            </span>
          </p>
          <MilestoneNotes milestone={milestone} />
        </div>
        <MilestoneStateActions key={`state-${milestone.id}`} milestone={milestone} />
        <MilestoneForm
          key={`form-${milestone.id}`}
          milestone={milestone}
          phaseId={phase.id}
          phases={schedule.phases}
          categoryOptions={schedule.category_options}
        />
        <MilestoneWindow
          key={`window-${milestone.id}`}
          milestone={milestone}
          hasExactDate={schedule.has_exact_date}
        />
        <MilestoneDependencies
          key={`deps-${milestone.id}`}
          milestone={milestone}
          schedule={schedule}
        />
        <Unlocks milestone={milestone} />
        <DeleteMilestone milestone={milestone} onDeleted={onDeleted} />
      </SheetContent>
    </Sheet>
  )
}

/** O "Libera" é só leitura: quem muda a ligação é o marco que depende (F-CRN-03). */
function Unlocks({ milestone }: { milestone: ScheduleMilestone }) {
  const labels = copy.sheet.links
  const titleId = useId()
  return (
    <section aria-labelledby={titleId} className="flex flex-col gap-1">
      <h3 id={titleId} className="text-body font-semibold text-ink">
        {labels.unlocks}
      </h3>
      {milestone.unlocks.length === 0 ? (
        <p className="text-body-sm text-ink-muted">{labels.noUnlocks}</p>
      ) : (
        <ul aria-labelledby={titleId} className="flex flex-col gap-1">
          {milestone.unlocks.map((unlocked) => (
            <li key={unlocked.id} className="text-body text-ink">
              {unlocked.title}
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
