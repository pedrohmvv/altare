import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent } from '@/components/ui/sheet'
import { formatTableDay } from '@/lib/date'
import { type ScheduleTask, scheduleKeys } from '../api/schedule'
import { useDeleteTask } from '../api/use-task-mutations'
import { copy } from '../copy'
import { type AlertState, alertFromError } from '../lib/errors'
import { Checklist } from './checklist'
import { FormAlert } from './form-alert'
import { TaskOverdueBadge, TaskStateBadge } from './milestone-badges'
import { DeadlineDate, DeadlineDetails, taskDeadline } from './milestone-deadline'
import { TaskForm } from './task-form'
import { TaskStateActions } from './task-state-actions'

export interface DeletedTask {
  id: string
  title: string
}

export interface TaskSheetProps {
  task: ScheduleTask
  open: boolean
  onOpenChange: (open: boolean) => void
  /** Chamado quando a avulsa foi excluída: quem mostra a lista fecha o painel e oferece o Desfazer. */
  onDeleted: (deleted: DeletedTask) => void
  /** O painel abre pela URL, sem gatilho: quem abriu diz para onde o foco volta ao fechar. */
  onCloseAutoFocus?: (event: Event) => void
}

/**
 * O detalhe da avulsa sem sair da lista (design-system.md §10, item 2): lateral no computador e
 * folha inferior no celular. Não é o painel do marco: a avulsa não tem fase, categoria, janela nem
 * dependências. Estado, dados, checklist e exclusão; o formulário guarda a versão de quando abriu.
 */
export function TaskSheet({
  task,
  open,
  onOpenChange,
  onDeleted,
  onCloseAutoFocus,
}: TaskSheetProps) {
  const deadline = taskDeadline(task)
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        title={task.title}
        description={copy.task.sheet.description}
        onCloseAutoFocus={onCloseAutoFocus}
        // O foco entra no painel, não no primeiro botão de estado: um Enter a mais não conclui nada.
        onOpenAutoFocus={(event) => {
          event.preventDefault()
          ;(event.currentTarget as HTMLElement | null)?.focus()
        }}
      >
        <div className="flex flex-col gap-2">
          <div className="flex flex-wrap items-center gap-2">
            <TaskStateBadge state={task.state} />
            {task.overdue && <TaskOverdueBadge />}
          </div>
          <p className="flex items-start gap-2 text-body text-ink">
            <span className="text-ink-muted">{copy.task.sheet.deadline}</span>
            <span className="flex flex-col gap-0.5">
              <DeadlineDate milestone={deadline} format={formatTableDay} className="text-num" />
              <DeadlineDetails milestone={deadline} format={formatTableDay} showWindow={false} />
            </span>
          </p>
        </div>
        <TaskStateActions key={`state-${task.id}`} task={task} />
        <TaskForm key={`form-${task.id}`} task={task} />
        <Checklist
          key={`checklist-${task.id}`}
          owner={{ kind: 'tasks', id: task.id }}
          items={task.checklist}
          progress={task.checklist_progress}
        />
        <DeleteTask task={task} onDeleted={onDeleted} />
      </SheetContent>
    </Sheet>
  )
}

const DELETE_ALERTS = {
  conflict: copy.task.remove.conflict,
  network: copy.task.remove.network,
}

/** Excluir a avulsa não tem confirmação: não há dependentes e o aviso de 4 s oferece o Desfazer. */
function DeleteTask({
  task,
  onDeleted,
}: {
  task: ScheduleTask
  onDeleted: (deleted: DeletedTask) => void
}) {
  const remove = useDeleteTask()
  const queryClient = useQueryClient()
  const [alert, setAlert] = useState<AlertState | null>(null)
  const [reloading, setReloading] = useState(false)

  function submit() {
    setAlert(null)
    remove.mutate(
      { taskId: task.id, version: task.version },
      {
        onSuccess: () => onDeleted({ id: task.id, title: task.title }),
        onError: (error) => setAlert(alertFromError(error, DELETE_ALERTS)),
      },
    )
  }

  async function reload() {
    setReloading(true)
    await queryClient.refetchQueries({ queryKey: scheduleKeys.all })
    setReloading(false)
    setAlert(null)
  }

  return (
    <div className="flex flex-col gap-3">
      <Button
        variant="soft-destructive"
        className="shrink-0 self-start"
        onClick={submit}
        loading={remove.isPending}
      >
        {copy.task.remove.button}
      </Button>
      <FormAlert alert={alert} onReload={() => void reload()} reloading={reloading} />
    </div>
  )
}
