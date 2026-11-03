import { useId } from 'react'
import { Sheet, SheetContent } from '@/components/ui/sheet'
import type { ScheduleMilestone } from '../api/schedule'
import { copy } from '../copy'
import { OptionalBadge, OverdueBadge, StateBadge } from './milestone-badges'
import { MilestoneForm } from './milestone-form'
import { MilestoneNotes } from './milestone-notes'
import { MilestoneStateActions } from './milestone-state-actions'

export interface MilestoneSheetProps {
  milestone: ScheduleMilestone
  phaseTitle: string
  open: boolean
  onOpenChange: (open: boolean) => void
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
  phaseTitle,
  open,
  onOpenChange,
  onCloseAutoFocus,
}: MilestoneSheetProps) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        title={milestone.title}
        description={copy.sheet.phase(phaseTitle)}
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
          <MilestoneNotes milestone={milestone} />
        </div>
        <MilestoneStateActions key={`state-${milestone.id}`} milestone={milestone} />
        <MilestoneForm key={`form-${milestone.id}`} milestone={milestone} />
        <Links milestone={milestone} />
      </SheetContent>
    </Sheet>
  )
}

function Links({ milestone }: { milestone: ScheduleMilestone }) {
  const labels = copy.sheet.links
  const dependsOnId = useId()
  const unlocksId = useId()
  const category = milestone.category
  return (
    <section aria-label={labels.title} className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <h3 className="text-body font-semibold text-ink">{labels.category}</h3>
        <p className="text-body text-ink">
          {category ? (category.name ?? labels.unnamedCategory) : labels.noCategory}
        </p>
      </div>
      <div className="flex flex-col gap-1">
        <h3 id={dependsOnId} className="text-body font-semibold text-ink">
          {labels.dependsOn}
        </h3>
        {milestone.depends_on.length === 0 ? (
          <p className="text-body-sm text-ink-muted">{labels.noDependsOn}</p>
        ) : (
          <ul aria-labelledby={dependsOnId} className="flex flex-col gap-1">
            {milestone.depends_on.map((dependency) => (
              <li key={dependency.id} className="text-body text-ink">
                <span>{dependency.title}</span>{' '}
                <span className="text-body-sm text-ink-muted">
                  {dependency.resolved ? labels.resolved : labels.pending}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="flex flex-col gap-1">
        <h3 id={unlocksId} className="text-body font-semibold text-ink">
          {labels.unlocks}
        </h3>
        {milestone.unlocks.length === 0 ? (
          <p className="text-body-sm text-ink-muted">{labels.noUnlocks}</p>
        ) : (
          <ul aria-labelledby={unlocksId} className="flex flex-col gap-1">
            {milestone.unlocks.map((unlocked) => (
              <li key={unlocked.id} className="text-body text-ink">
                {unlocked.title}
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
