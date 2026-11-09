import { useQuery } from '@tanstack/react-query'
import { useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { EmptyState } from '@/components/ui/empty-state'
import { type ToastOptions, useToast } from '@/components/ui/toast'
import { useMediaQuery } from '@/lib/use-media-query'
import {
  findTask,
  type LeftOut,
  type ScheduleMilestone,
  type SchedulePhase,
  scheduleQueryOptions,
} from '../api/schedule'
import { useRestoreMilestone } from '../api/use-milestone-mutations'
import { useRestoreTask } from '../api/use-task-mutations'
import { copy } from '../copy'
import { type NextStep, nextSteps } from '../lib/next-steps'
import {
  applyScheduleFilters,
  filtersFromSearch,
  hasActiveFilters,
  type Lens,
  type SessionProfile,
} from '../lib/schedule-filters'
import type { ScheduleSearch } from '../search'
import { MilestoneCard } from './milestone-card'
import type { DeletedMilestone } from './milestone-delete'
import { MilestoneSheet } from './milestone-sheet'
import { type ActivePhase, MilestoneTable } from './milestone-table'
import { NextSteps } from './next-steps'
import { PhaseHeader } from './phase-header'
import { ScheduleToolbar } from './schedule-toolbar'
import { TaskCards } from './task-card'
import { type DeletedTask, TaskSheet } from './task-sheet'

export interface ScheduleListProps {
  search: ScheduleSearch
  onSearchChange: (patch: Partial<ScheduleSearch>) => void
  /** Pede o diálogo de novo marco; a fase de origem vai junto, e o botão para devolver o foco. */
  onNewMilestone: (phaseId: string, from: HTMLElement) => void
  /** Pede o diálogo de nova avulsa, com o botão para devolver o foco. */
  onNewTask: (from: HTMLElement) => void
  /** A lente de visão: ausente é `casal`. Filtra no navegador, só com `profile`. */
  lens?: Lens
  /** Quem está na sessão: define o "meu" da lente e de "Meus próximos passos". */
  profile?: SessionProfile
  /** Tira a lente `Minha visão` (a página não conhece o roteador: quem a montou muda a URL). */
  onShowCouple?: () => void
}

/** Os marcos ativos de cada fase: o arquivado sai das listas (F-CRN-04). */
function activePhases(phases: readonly SchedulePhase[]): ActivePhase[] {
  return phases.map((phase, index) => ({
    phase,
    number: index + 1,
    milestones: phase.milestones.filter((milestone) => !milestone.archived),
  }))
}

/** O cronograma por fase (F-CRN-09): tabela densa no computador, cartões no celular. */
export function ScheduleList({
  search,
  onSearchChange,
  onNewMilestone,
  onNewTask,
  lens = 'casal',
  profile,
  onShowCouple,
}: ScheduleListProps) {
  const query = useQuery(scheduleQueryOptions)
  const { toast } = useToast()
  const restore = useRestoreMilestone()
  const restoreTask = useRestoreTask()
  const wide = useMediaQuery('(min-width: 768px)')
  // O último marco aberto continua montado durante a animação de saída do painel. Quem abriu o
  // painel recebe o foco de volta ao fechá-lo (o Radix só o faz com um gatilho).
  const opener = useRef<HTMLElement | null>(null)
  const [lastOpened, setLastOpened] = useState<string | undefined>(undefined)
  if (search.marco && search.marco !== lastOpened) setLastOpened(search.marco)
  const [lastOpenedTask, setLastOpenedTask] = useState<string | undefined>(undefined)
  if (search.avulsa && search.avulsa !== lastOpenedTask) setLastOpenedTask(search.avulsa)

  // O aviso de exclusão mora aqui, e não no painel, porque o painel fecha ao excluir (D-072, item 8).
  function handleDeleted(deleted: DeletedMilestone) {
    onSearchChange({ marco: undefined })
    opener.current = null
    toast({
      title: copy.remove.done,
      description: copy.remove.doneDescription(deleted.title),
      action: {
        label: copy.remove.undo,
        altText: copy.remove.undoAlt,
        onClick: () => restoreDeleted(deleted.id),
      },
    })
  }

  // Se a restauração falha, o aviso diz que o marco segue guardado e oferece a mesma ação de novo.
  function restoreDeleted(milestoneId: string) {
    restore.mutate(
      { milestoneId },
      {
        onSuccess: ({ leftOut }) => toast(restoredToast(leftOut)),
        onError: () =>
          toast({
            title: copy.remove.restoreFailed.title,
            description: copy.remove.restoreFailed.description,
            tone: 'attention',
            action: {
              label: copy.remove.restoreFailed.retry,
              altText: copy.remove.restoreFailed.retryAlt,
              onClick: () => restoreDeleted(milestoneId),
            },
          }),
      },
    )
  }

  // O aviso de exclusão da avulsa também mora aqui. Se a restauração falha, oferece a mesma ação.
  function handleTaskDeleted(deleted: DeletedTask) {
    onSearchChange({ avulsa: undefined })
    opener.current = null
    toast({
      title: copy.task.remove.done,
      description: copy.task.remove.doneDescription(deleted.title),
      action: {
        label: copy.task.remove.undo,
        altText: copy.task.remove.undoAlt,
        onClick: () => restoreDeletedTask(deleted.id),
      },
    })
  }

  function restoreDeletedTask(taskId: string) {
    restoreTask.mutate(
      { taskId },
      {
        onSuccess: () => toast({ title: copy.task.remove.restored, tone: 'success' }),
        onError: () =>
          toast({
            title: copy.task.remove.restoreFailed.title,
            description: copy.task.remove.restoreFailed.description,
            tone: 'attention',
            action: {
              label: copy.task.remove.restoreFailed.retry,
              altText: copy.task.remove.restoreFailed.retryAlt,
              onClick: () => restoreDeletedTask(taskId),
            },
          }),
      },
    )
  }

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

  const allPhases = activePhases(query.data.phases)
  if (allPhases.length === 0) {
    return (
      <Card>
        <EmptyState title={copy.list.empty.title} description={copy.list.empty.description} />
      </Card>
    )
  }

  // Abrir um painel limpa a chave do outro: nunca há dois na URL.
  const open = (milestoneId: string, from: HTMLElement) => {
    opener.current = from
    onSearchChange({ marco: milestoneId, avulsa: undefined })
  }
  const openTask = (taskId: string, from: HTMLElement) => {
    opener.current = from
    onSearchChange({ avulsa: taskId, marco: undefined })
  }
  const openStep = (step: NextStep, from: HTMLElement) =>
    step.kind === 'milestone' ? open(step.id, from) : openTask(step.id, from)

  // O filtro e a lente só escolhem o que mostrar (D-080): o progresso e os bloqueios são os do servidor.
  const filters = filtersFromSearch(search)
  const result = applyScheduleFilters(query.data, { filters, lens, profile })
  const phases = result.narrowed
    ? allPhases
        .map((entry) => ({
          ...entry,
          milestones: entry.milestones.filter((item) => result.milestoneIds.has(item.id)),
        }))
        .filter((entry) => entry.milestones.length > 0)
    : allPhases
  const tasks = result.narrowed
    ? query.data.tasks.filter((item) => result.taskIds.has(item.id))
    : query.data.tasks
  // O estado vazio some quando a lente sai: o foco vai ao título da página, um alvo que fica.
  const showCouple = () => {
    onShowCouple?.()
    document.querySelector<HTMLElement>('h1')?.focus()
  }
  const nothingShown = result.narrowed && phases.length === 0 && tasks.length === 0
  const steps = profile ? nextSteps(query.data, profile) : null
  const sheetTask = findTask(query.data, search.avulsa ?? lastOpenedTask ?? '')
  const sheetId = search.marco ?? lastOpened
  // Os painéis abrem pelos dados inteiros: o filtro nunca esconde o que a URL pede.
  const owner = allPhases.find(({ milestones }) => milestones.some((item) => item.id === sheetId))
  const sheetMilestone: ScheduleMilestone | undefined = owner?.milestones.find(
    (item) => item.id === sheetId,
  )

  return (
    <div className="flex flex-col gap-8">
      {owner && sheetMilestone && (
        <MilestoneSheet
          milestone={sheetMilestone}
          phase={owner.phase}
          schedule={query.data}
          open={Boolean(search.marco)}
          onOpenChange={(isOpen) => !isOpen && onSearchChange({ marco: undefined })}
          onDeleted={handleDeleted}
          onCloseAutoFocus={(event) => {
            event.preventDefault()
            // Aberto pela URL não há gatilho: o foco cai no botão do próprio marco, ou no título.
            const fallback =
              document.querySelector<HTMLElement>(`[data-milestone-id="${sheetMilestone.id}"]`) ??
              document.querySelector<HTMLElement>('h1')
            ;(opener.current?.isConnected ? opener.current : fallback)?.focus()
            opener.current = null
          }}
        />
      )}
      {sheetTask && (
        <TaskSheet
          task={sheetTask}
          open={Boolean(search.avulsa)}
          onOpenChange={(isOpen) => !isOpen && onSearchChange({ avulsa: undefined })}
          onDeleted={handleTaskDeleted}
          onCloseAutoFocus={(event) => {
            event.preventDefault()
            // Aberta pela URL não há gatilho: o foco cai no botão da própria avulsa, ou no título.
            const fallback =
              document.querySelector<HTMLElement>(`[data-task-id="${sheetTask.id}"]`) ??
              document.querySelector<HTMLElement>('h1')
            ;(opener.current?.isConnected ? opener.current : fallback)?.focus()
            opener.current = null
          }}
        />
      )}
      {!wide && steps && <NextSteps steps={steps} onOpen={openStep} />}
      <ScheduleToolbar
        search={search}
        onSearchChange={onSearchChange}
        lens={lens}
        profile={profile}
        count={result.narrowed ? { shown: result.shown, total: result.total } : null}
      />
      {nothingShown ? (
        <Card>
          <EmptyState
            title={
              hasActiveFilters(filters)
                ? copy.filters.noMatch.title
                : copy.filters.noMatch.lensTitle
            }
            description={
              !hasActiveFilters(filters) && profile
                ? copy.filters.noMatch.lensOnly[profile]
                : undefined
            }
            action={
              hasActiveFilters(filters) ? (
                <Button
                  variant="secondary"
                  onClick={() =>
                    onSearchChange({
                      responsavel: undefined,
                      estado: undefined,
                      atrasados: undefined,
                      avulsas: undefined,
                    })
                  }
                >
                  {copy.filters.clear}
                </Button>
              ) : onShowCouple ? (
                <Button variant="secondary" onClick={showCouple}>
                  {copy.filters.noMatch.showCouple}
                </Button>
              ) : undefined
            }
          />
        </Card>
      ) : wide ? (
        <>
          <h2 className="sr-only">{copy.list.title}</h2>
          <MilestoneTable
            phases={phases}
            tasks={tasks}
            showTasks={!result.narrowed || tasks.length > 0}
            onOpen={open}
            onOpenTask={openTask}
            onNewMilestone={onNewMilestone}
            onNewTask={onNewTask}
          />
        </>
      ) : (
        <>
          {phases.map(({ phase, milestones, number }) => (
            <section
              key={phase.id}
              aria-labelledby={`phase-${phase.id}`}
              className="flex flex-col gap-3"
            >
              <PhaseHeader
                variant="section"
                number={number}
                title={phase.title}
                done={phase.progress.done}
                total={phase.progress.total}
                titleId={`phase-${phase.id}`}
              />
              {milestones.length === 0 ? (
                <div className="flex flex-col items-start gap-2">
                  <p className="text-body-sm text-ink-muted">{copy.list.emptyPhase}</p>
                  <Button
                    variant="secondary"
                    size="sm"
                    aria-label={copy.newMilestone.inPhaseFor(phase.title)}
                    onClick={(event) => onNewMilestone(phase.id, event.currentTarget)}
                  >
                    {copy.newMilestone.inPhase}
                  </Button>
                </div>
              ) : (
                <ul className="grid gap-3">
                  {milestones.map((milestone) => (
                    <MilestoneCard key={milestone.id} milestone={milestone} onOpen={open} />
                  ))}
                </ul>
              )}
            </section>
          ))}
          {(!result.narrowed || tasks.length > 0) && (
            <TaskCards tasks={tasks} onOpen={openTask} onNewTask={onNewTask} />
          )}
        </>
      )}
    </div>
  )
}

/** O aviso de depois de restaurar: se alguma ligação não voltou, diz quais e em que sentido. */
function restoredToast(leftOut: readonly LeftOut[]): ToastOptions {
  if (leftOut.length === 0) return { title: copy.remove.restored, tone: 'success' }
  const text = copy.remove.leftOut
  return {
    title: text.title,
    description: text.description(
      leftOut.map((link) =>
        link.direction === 'depends_on'
          ? text.dependsOn(link.title)
          : text.dependencyOf(link.title),
      ),
    ),
    tone: 'attention',
  }
}
