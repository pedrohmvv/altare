import { useQuery } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { PageHeader } from '@/components/ui/page-header'
import { useToast } from '@/components/ui/toast'
import { scheduleQueryOptions } from '../api/schedule'
import type { Created } from '../api/use-milestone-mutations'
import { NewMilestoneDialog } from '../components/new-milestone-dialog'
import { NewTaskDialog } from '../components/new-task-dialog'
import { NoDateBanner, type PlanningLink } from '../components/no-date-banner'
import { PhasesDialog } from '../components/phases-dialog'
import { ScheduleList } from '../components/schedule-list'
import { copy } from '../copy'
import type { ScheduleSearch } from '../search'

export interface SchedulePageProps {
  /** O que a URL guarda: o marco aberto no painel lateral. */
  search: ScheduleSearch
  /** Pede uma mudança na URL; `undefined` num campo o tira. */
  onSearchChange: (patch: Partial<ScheduleSearch>) => void
  /** O link do aviso "Sem data definida" para as Definições Base; a rota o liga ao roteador. */
  planningLink?: PlanningLink
  /** O perfil da sessão: o responsável padrão de uma avulsa nova. Sem ele, a página não o conhece. */
  profile?: 'Noivo' | 'Noiva'
  /** A lente da sessão: `minha` filtra no navegador, só com `profile` (D-080, resposta 1). */
  lens?: 'casal' | 'minha'
  /** Tira a lente da URL: a rota o liga ao roteador; a página continua sem conhecê-lo. */
  onShowCouple?: () => void
}

/** A página não conhece o roteador: recebe a URL e devolve o que quer mudar, e assim se testa sem ele. */
export function SchedulePage({
  search,
  onSearchChange,
  planningLink,
  profile,
  lens,
  onShowCouple,
}: SchedulePageProps) {
  const query = useQuery(scheduleQueryOptions)
  const { toast } = useToast()
  const [newMilestone, setNewMilestone] = useState<{ phaseId?: string } | null>(null)
  // Os diálogos não têm `DialogTrigger`: a tela guarda o botão que abriu para devolver o foco.
  const origin = useRef<HTMLElement | null>(null)
  const created = useRef(false)
  const [phasesOpen, setPhasesOpen] = useState(false)
  const [newTaskOpen, setNewTaskOpen] = useState(false)
  const schedule = query.data

  function askNewMilestone(phaseId: string | undefined, from: HTMLElement) {
    origin.current = from
    created.current = false
    setNewMilestone({ phaseId })
  }

  function askPhases(from: HTMLElement) {
    origin.current = from
    setPhasesOpen(true)
  }

  function askNewTask(from: HTMLElement) {
    origin.current = from
    created.current = false
    setNewTaskOpen(true)
  }

  function handleTaskCreated({ taskId }: { taskId: string | null }) {
    setNewTaskOpen(false)
    // Sem exatamente um id novo não há painel para abrir: o aviso diz que a avulsa foi criada.
    if (taskId === null) return toast({ title: copy.task.create.created, tone: 'success' })
    created.current = true
    onSearchChange({ avulsa: taskId, marco: undefined })
  }

  function handleCreated({ milestone }: Created) {
    created.current = true
    setNewMilestone(null)
    if (milestone && !milestone.archived) {
      return onSearchChange({ marco: milestone.id, avulsa: undefined })
    }
    // Sem painel para abrir: o marco nasceu fora das listas (arquivado) e o aviso explica por quê.
    toast(
      milestone
        ? {
            title: copy.newMilestone.created,
            description: copy.newMilestone.createdArchived(milestone.title),
            tone: 'attention',
          }
        : { title: copy.newMilestone.created, tone: 'success' },
    )
  }

  return (
    <>
      <PageHeader
        eyebrow={copy.eyebrow}
        title={copy.title}
        description={copy.description}
        actions={
          schedule && (
            <>
              <Button onClick={(event) => askNewMilestone(undefined, event.currentTarget)}>
                <Plus aria-hidden />
                {copy.header.newMilestone}
              </Button>
              <Button variant="secondary" onClick={(event) => askNewTask(event.currentTarget)}>
                <Plus aria-hidden />
                {copy.header.newTask}
              </Button>
              <Button variant="secondary" onClick={(event) => askPhases(event.currentTarget)}>
                {copy.header.phases}
              </Button>
            </>
          )
        }
      />
      {schedule && !schedule.has_exact_date && (
        <div className="mt-6">
          <NoDateBanner planningLink={planningLink} />
        </div>
      )}
      <div className="mt-10">
        <ScheduleList
          search={search}
          onSearchChange={onSearchChange}
          onNewMilestone={askNewMilestone}
          onNewTask={askNewTask}
          lens={lens}
          profile={profile}
          onShowCouple={onShowCouple}
        />
      </div>
      {schedule && (
        <PhasesDialog
          open={phasesOpen}
          onOpenChange={setPhasesOpen}
          phases={schedule.phases}
          onCloseAutoFocus={(event) => {
            event.preventDefault()
            origin.current?.focus()
          }}
        />
      )}
      {schedule && (
        <NewMilestoneDialog
          open={newMilestone !== null}
          onOpenChange={(open) => !open && setNewMilestone(null)}
          schedule={schedule}
          phaseId={newMilestone?.phaseId}
          onCreated={handleCreated}
          onCloseAutoFocus={(event) => {
            // Criado, o foco é do painel do marco; senão volta ao botão de origem.
            event.preventDefault()
            if (!created.current) origin.current?.focus()
            created.current = false
          }}
        />
      )}
      {schedule && (
        <NewTaskDialog
          open={newTaskOpen}
          onOpenChange={(open) => !open && setNewTaskOpen(false)}
          taskIds={schedule.tasks.map((task) => task.id)}
          profile={profile}
          onCreated={handleTaskCreated}
          onCloseAutoFocus={(event) => {
            // Criada e achada, o foco é do painel da avulsa; senão volta ao botão de origem.
            event.preventDefault()
            if (!created.current) origin.current?.focus()
            created.current = false
          }}
        />
      )}
    </>
  )
}
