import { TableBody, TableCell, TableRow } from '@/components/ui/table'
import { formatTableDay } from '@/lib/date'
import type { ScheduleTask } from '../api/schedule'
import { copy } from '../copy'
import { ChecklistSummary } from './checklist-summary'
import { TaskOverdueBadge, TaskStateBadge } from './milestone-badges'
import { DeadlineDate, DeadlineDetails, taskDeadline } from './milestone-deadline'
import { EmptyTasks } from './task-card'

/**
 * No computador, as avulsas são mais um grupo de linhas da mesma tabela (F-CRN-06), depois da última
 * fase: o cabeçalho do grupo é "Avulsas" e as colunas são as do marco.
 */
export function TaskRowGroup({
  tasks,
  columns,
  onOpen,
  onNewTask,
}: {
  tasks: readonly ScheduleTask[]
  /** Quantas colunas a tabela tem: o cabeçalho do grupo ocupa todas. */
  columns: number
  onOpen: (taskId: string, opener: HTMLElement) => void
  onNewTask: (from: HTMLElement) => void
}) {
  return (
    <TableBody>
      <tr className="border-b border-border bg-surface-muted">
        <th scope="rowgroup" colSpan={columns} className="px-4 py-2 text-left font-normal">
          <span className="text-name text-ink">{copy.task.sectionTitle}</span>
        </th>
      </tr>
      {tasks.length === 0 && (
        <TableRow>
          <TableCell colSpan={columns}>
            <EmptyTasks onNewTask={onNewTask} />
          </TableCell>
        </TableRow>
      )}
      {tasks.map((task) => (
        <TaskRow key={task.id} task={task} onOpen={onOpen} />
      ))}
    </TableBody>
  )
}

function TaskRow({
  task,
  onOpen,
}: {
  task: ScheduleTask
  onOpen: (taskId: string, opener: HTMLElement) => void
}) {
  const deadline = taskDeadline(task)
  return (
    <TableRow>
      <TableCell>
        <button
          type="button"
          data-task-id={task.id}
          onClick={(event) => onOpen(task.id, event.currentTarget)}
          className="rounded-control text-left text-ink hover:underline"
        >
          {task.title}
        </button>
        <div className="mt-0.5 flex flex-col gap-1">
          <ChecklistSummary progress={task.checklist_progress} />
        </div>
      </TableCell>
      <TableCell>
        <div className="flex flex-wrap items-center gap-1.5">
          <TaskStateBadge state={task.state} />
          {task.overdue && <TaskOverdueBadge />}
        </div>
      </TableCell>
      <TableCell>{copy.responsibles[task.responsible]}</TableCell>
      <TableCell numeric>
        <span className="flex flex-col items-end gap-0.5 text-right">
          <DeadlineDate milestone={deadline} format={formatTableDay} />
          <DeadlineDetails milestone={deadline} format={formatTableDay} align="end" />
        </span>
      </TableCell>
    </TableRow>
  )
}
