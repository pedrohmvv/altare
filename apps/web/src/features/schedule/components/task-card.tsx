import { useId } from 'react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/cn'
import { formatDay } from '@/lib/date'
import type { ScheduleTask } from '../api/schedule'
import { copy } from '../copy'
import { ChecklistSummary } from './checklist-summary'
import { TaskOverdueBadge, TaskStateBadge } from './milestone-badges'
import { DeadlineDate, DeadlineDetails, taskDeadline } from './milestone-deadline'

/**
 * No celular, um cartão por avulsa (F-CRN-06), no mesmo desenho do cartão de marco, sem fase nem
 * dependências: o título abre o painel (o botão cobre o cartão).
 */
export function TaskCard({
  task,
  onOpen,
}: {
  task: ScheduleTask
  onOpen: (taskId: string, opener: HTMLElement) => void
}) {
  const deadline = taskDeadline(task)
  return (
    <li
      className={cn(
        'relative flex flex-col gap-2 rounded-card border border-border bg-surface p-4',
        'transition-colors duration-fast ease-standard hover:border-border-strong',
      )}
    >
      <h3 className="text-name text-ink">
        <button
          type="button"
          data-task-id={task.id}
          onClick={(event) => onOpen(task.id, event.currentTarget)}
          className="text-left after:absolute after:inset-0 after:rounded-card"
        >
          {task.title}
        </button>
      </h3>
      <div className="flex flex-wrap items-center gap-2">
        <TaskStateBadge state={task.state} />
        {task.overdue && <TaskOverdueBadge />}
      </div>
      <ChecklistSummary progress={task.checklist_progress} />
      <div className="flex flex-col gap-1 text-body-sm text-ink-muted">
        <p className="flex flex-wrap items-center justify-between gap-x-3">
          <span>
            <span className="sr-only">{`${copy.list.columns.responsible}: `}</span>
            {copy.responsibles[task.responsible]}
          </span>
          <span className="text-num-sm">
            <DeadlineDate milestone={deadline} format={formatDay} srLabel />
          </span>
        </p>
        <DeadlineDetails milestone={deadline} format={formatDay} align="end" />
      </div>
    </li>
  )
}

/** O que a seção "Avulsas" diz quando ainda não há nenhuma, com a saída (Nova avulsa). */
export function EmptyTasks({ onNewTask }: { onNewTask: (from: HTMLElement) => void }) {
  return (
    <div className="flex flex-col items-start gap-2">
      <p className="text-body-sm text-ink-muted">{copy.task.empty}</p>
      <Button variant="secondary" size="sm" onClick={(event) => onNewTask(event.currentTarget)}>
        {copy.header.newTask}
      </Button>
    </div>
  )
}

/** No celular, a seção "Avulsas" depois da última fase: um cartão por avulsa, na ordem do servidor. */
export function TaskCards({
  tasks,
  onOpen,
  onNewTask,
}: {
  tasks: readonly ScheduleTask[]
  onOpen: (taskId: string, opener: HTMLElement) => void
  onNewTask: (from: HTMLElement) => void
}) {
  const titleId = useId()
  return (
    <section aria-labelledby={titleId} className="flex flex-col gap-3">
      <h2 id={titleId} className="text-name text-ink">
        {copy.task.sectionTitle}
      </h2>
      {tasks.length === 0 ? (
        <EmptyTasks onNewTask={onNewTask} />
      ) : (
        <ul className="grid gap-3">
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} onOpen={onOpen} />
          ))}
        </ul>
      )}
    </section>
  )
}
