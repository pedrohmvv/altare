import { useQuery } from '@tanstack/react-query'
import { useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { EmptyState } from '@/components/ui/empty-state'
import { useMediaQuery } from '@/lib/use-media-query'
import { type ScheduleMilestone, type SchedulePhase, scheduleQueryOptions } from '../api/schedule'
import { copy } from '../copy'
import type { ScheduleSearch } from '../search'
import { MilestoneCard } from './milestone-card'
import { MilestoneSheet } from './milestone-sheet'
import { type ActivePhase, MilestoneTable } from './milestone-table'
import { PhaseHeader } from './phase-header'

export interface ScheduleListProps {
  search: ScheduleSearch
  onSearchChange: (patch: Partial<ScheduleSearch>) => void
}

/** Os marcos ativos de cada fase: o arquivado sai das listas (F-CRN-04). */
function activePhases(phases: readonly SchedulePhase[]): ActivePhase[] {
  return phases.map((phase) => ({
    phase,
    milestones: phase.milestones.filter((milestone) => !milestone.archived),
  }))
}

/** O cronograma por fase (F-CRN-09): tabela densa no computador, cartões no celular. */
export function ScheduleList({ search, onSearchChange }: ScheduleListProps) {
  const query = useQuery(scheduleQueryOptions)
  const wide = useMediaQuery('(min-width: 768px)')
  // O último marco aberto continua montado durante a animação de saída do painel. Quem abriu o
  // painel recebe o foco de volta ao fechá-lo (o Radix só o faz com um gatilho).
  const opener = useRef<HTMLElement | null>(null)
  const [lastOpened, setLastOpened] = useState<string | undefined>(undefined)
  if (search.marco && search.marco !== lastOpened) setLastOpened(search.marco)

  if (query.isPending) {
    return (
      <Card aria-busy>
        <p className="text-body-sm text-ink-muted">{copy.list.loading}</p>
        <div aria-hidden className="mt-4 flex flex-col gap-3">
          <div className="h-3 w-2/3 rounded-pill bg-surface-sunken" />
          <div className="h-3 w-1/2 rounded-pill bg-surface-sunken" />
          <div className="h-16 rounded-card bg-surface-sunken" />
        </div>
      </Card>
    )
  }
  if (query.isError) {
    return (
      <Card>
        <p className="text-body font-medium text-ink">{copy.list.loadError.title}</p>
        <p className="text-body-sm text-ink-muted">{copy.list.loadError.description}</p>
        <Button variant="secondary" className="mt-3" onClick={() => void query.refetch()}>
          {copy.list.loadError.retry}
        </Button>
      </Card>
    )
  }

  const phases = activePhases(query.data.phases)
  if (phases.length === 0) {
    return (
      <Card>
        <EmptyState title={copy.list.empty.title} description={copy.list.empty.description} />
      </Card>
    )
  }

  const open = (milestoneId: string, from: HTMLElement) => {
    opener.current = from
    onSearchChange({ marco: milestoneId })
  }
  const sheetId = search.marco ?? lastOpened
  const owner = phases.find(({ milestones }) => milestones.some((item) => item.id === sheetId))
  const sheetMilestone: ScheduleMilestone | undefined = owner?.milestones.find(
    (item) => item.id === sheetId,
  )

  return (
    <div className="flex flex-col gap-8">
      {owner && sheetMilestone && (
        <MilestoneSheet
          milestone={sheetMilestone}
          phaseTitle={owner.phase.title}
          open={Boolean(search.marco)}
          onOpenChange={(isOpen) => !isOpen && onSearchChange({ marco: undefined })}
          onCloseAutoFocus={(event) => {
            event.preventDefault()
            // Aberto pela URL não há gatilho: o foco cai no botão do próprio marco, ou no título.
            const fallback =
              document.querySelector<HTMLElement>(`[data-milestone-id="${sheetMilestone.id}"]`) ??
              document.querySelector<HTMLElement>('h1')
            ;(opener.current ?? fallback)?.focus()
            opener.current = null
          }}
        />
      )}
      {wide ? (
        <>
          <h2 className="sr-only">{copy.list.title}</h2>
          <MilestoneTable phases={phases} onOpen={open} />
        </>
      ) : (
        phases.map(({ phase, milestones }, index) => (
          <section
            key={phase.id}
            aria-labelledby={`phase-${phase.id}`}
            className="flex flex-col gap-3"
          >
            <PhaseHeader
              variant="section"
              number={index + 1}
              title={phase.title}
              done={phase.progress.done}
              total={phase.progress.total}
              titleId={`phase-${phase.id}`}
            />
            {milestones.length === 0 ? (
              <p className="text-body-sm text-ink-muted">{copy.list.emptyPhase}</p>
            ) : (
              <ul className="grid gap-3">
                {milestones.map((milestone) => (
                  <MilestoneCard key={milestone.id} milestone={milestone} onOpen={open} />
                ))}
              </ul>
            )}
          </section>
        ))
      )}
    </div>
  )
}
