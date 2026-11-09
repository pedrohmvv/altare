import { useQueryClient } from '@tanstack/react-query'
import { useId, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Select } from '@/components/ui/select'
import { type Schedule, type ScheduleMilestone, scheduleKeys } from '../api/schedule'
import { useSetMilestoneDependencies } from '../api/use-milestone-mutations'
import { copy } from '../copy'
import { type AlertState, alertFromError } from '../lib/errors'
import { FormAlert } from './form-alert'

const labels = copy.sheet.links

const ALERTS = {
  conflict: labels.conflict,
  network: labels.network,
}

/**
 * Os marcos que ainda podem ser ligados: vivos, não arquivados, sem o próprio e sem os que já
 * estão ligados (F-CRN-03). Agrupados pela fase, na ordem do cronograma.
 */
function candidates(schedule: Schedule, milestone: ScheduleMilestone) {
  const linked = new Set(milestone.depends_on.map((dependency) => dependency.id))
  return schedule.phases.flatMap((phase) =>
    phase.milestones
      .filter((item) => !item.archived && item.id !== milestone.id && !linked.has(item.id))
      .map((item) => ({ value: item.id, label: item.title, group: phase.title })),
  )
}

/**
 * O "Depende de" do marco: remover cada ligação e adicionar outra. Cada mudança envia o conjunto
 * inteiro e a versão do marco; o ciclo e a auto-dependência são recusados pelo servidor, que diz o
 * caminho, e nada muda. O estado do marco (por exemplo, destravar) vem sempre da API.
 */
export function MilestoneDependencies({
  milestone,
  schedule,
}: {
  milestone: ScheduleMilestone
  schedule: Schedule
}) {
  const titleId = useId()
  // O botão que tinha o foco some ou se desabilita: o foco vai ao título da seção, que fica.
  const heading = useRef<HTMLHeadingElement>(null)
  const change = useSetMilestoneDependencies()
  const queryClient = useQueryClient()
  const [chosen, setChosen] = useState('')
  const [alert, setAlert] = useState<AlertState | null>(null)
  const [reloading, setReloading] = useState(false)
  const [done, setDone] = useState('')
  const options = candidates(schedule, milestone)

  function send(dependsOn: string[], message: string, onDone?: () => void) {
    setAlert(null)
    setDone('')
    change.mutate(
      { milestoneId: milestone.id, dependsOn, version: milestone.version },
      {
        onSuccess: () => {
          heading.current?.focus()
          setDone(message)
          onDone?.()
        },
        onError: (error) => setAlert(alertFromError(error, ALERTS)),
      },
    )
  }

  async function reload() {
    setReloading(true)
    await queryClient.refetchQueries({ queryKey: scheduleKeys.all })
    setReloading(false)
    setAlert(null)
  }

  const currentIds = milestone.depends_on.map((dependency) => dependency.id)

  return (
    <section aria-labelledby={titleId} className="flex flex-col gap-3">
      <h3 ref={heading} tabIndex={-1} id={titleId} className="text-body font-semibold text-ink">
        {labels.dependsOn}
      </h3>
      {milestone.depends_on.length === 0 ? (
        <p className="text-body-sm text-ink-muted">{labels.noDependsOn}</p>
      ) : (
        <ul aria-labelledby={titleId} className="flex flex-col gap-2">
          {milestone.depends_on.map((dependency) => (
            <li key={dependency.id} className="flex items-center justify-between gap-3">
              <span className="text-body text-ink">
                <span>{dependency.title}</span>{' '}
                <span className="text-body-sm text-ink-muted">
                  {dependency.resolved ? labels.resolved : labels.pending}
                </span>
              </span>
              <Button
                variant="ghost"
                size="sm"
                aria-label={labels.remove(dependency.title)}
                disabled={change.isPending}
                onClick={() =>
                  send(
                    currentIds.filter((id) => id !== dependency.id),
                    labels.removed,
                  )
                }
              >
                {labels.removeShort}
              </Button>
            </li>
          ))}
        </ul>
      )}
      {options.length === 0 ? (
        <p className="text-body-sm text-ink-muted">{labels.noCandidates}</p>
      ) : (
        <div className="flex flex-col gap-2">
          <Select
            label={labels.addLabel}
            placeholder={labels.addPlaceholder}
            options={options}
            value={chosen}
            onValueChange={setChosen}
            disabled={change.isPending}
          />
          <Button
            variant="secondary"
            className="self-start"
            disabled={chosen === ''}
            loading={change.isPending}
            onClick={() => send([...currentIds, chosen], labels.added, () => setChosen(''))}
          >
            {labels.add}
          </Button>
        </div>
      )}
      <FormAlert alert={alert} onReload={() => void reload()} reloading={reloading} />
      <p role="status" className="text-body-sm text-consensus-ink">
        {done}
      </p>
    </section>
  )
}
