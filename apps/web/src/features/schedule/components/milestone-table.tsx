import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { cn } from '@/lib/cn'
import { formatTableDay } from '@/lib/date'
import type { ScheduleMilestone, SchedulePhase, ScheduleTask } from '../api/schedule'
import { copy } from '../copy'
import { ChecklistSummary } from './checklist-summary'
import { OptionalBadge, OverdueBadge, StateBadge } from './milestone-badges'
import { MilestoneDeadline } from './milestone-deadline'
import { MilestoneNotes } from './milestone-notes'
import { PhaseHeader } from './phase-header'
import { TaskRowGroup } from './task-rows'

const columns = copy.list.columns

export interface ActivePhase {
  phase: SchedulePhase
  /** A posição da fase no cronograma inteiro, a partir de 1: não muda quando o filtro esconde fases. */
  number: number
  /** Só os marcos ativos: os arquivados não aparecem nas listas (F-CRN-04). */
  milestones: ScheduleMilestone[]
}

/**
 * No computador, a tabela densa com um grupo de linhas por fase (F-CRN-09): o cabeçalho do grupo
 * diz a fase e o progresso, e o painel lateral abre pelo nome do marco.
 */
export function MilestoneTable({
  phases,
  tasks,
  showTasks,
  onOpen,
  onOpenTask,
  onNewMilestone,
  onNewTask,
}: {
  phases: readonly ActivePhase[]
  /** As avulsas, em mais um grupo de linhas depois da última fase (F-CRN-06). */
  tasks: readonly ScheduleTask[]
  /** Sob filtro, o grupo some se nenhuma avulsa casa; sem filtro, aparece sempre (vazio, com a saída). */
  showTasks: boolean
  onOpen: (milestoneId: string, opener: HTMLElement) => void
  onOpenTask: (taskId: string, opener: HTMLElement) => void
  onNewMilestone: (phaseId: string, from: HTMLElement) => void
  onNewTask: (from: HTMLElement) => void
}) {
  return (
    <Table label={copy.list.tableLabel} density="compact">
      <TableCaption srOnly>{copy.list.tableCaption}</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>{columns.milestone}</TableHead>
          <TableHead>{columns.state}</TableHead>
          <TableHead>{columns.responsible}</TableHead>
          <TableHead numeric>{columns.target}</TableHead>
        </TableRow>
      </TableHeader>
      {phases.map(({ phase, milestones, number }) => (
        <TableBody key={phase.id}>
          <tr className="border-b border-border bg-surface-muted">
            <th scope="rowgroup" colSpan={4} className="px-4 py-2 text-left font-normal">
              <PhaseHeader
                variant="row"
                number={number}
                title={phase.title}
                done={phase.progress.done}
                total={phase.progress.total}
              />
            </th>
          </tr>
          {milestones.length === 0 && (
            <TableRow>
              <TableCell colSpan={4}>
                <div className="flex flex-wrap items-center gap-3">
                  <span className="text-ink-muted">{copy.list.emptyPhase}</span>
                  <Button
                    variant="secondary"
                    size="sm"
                    aria-label={copy.newMilestone.inPhaseFor(phase.title)}
                    onClick={(event) => onNewMilestone(phase.id, event.currentTarget)}
                  >
                    {copy.newMilestone.inPhase}
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          )}
          {milestones.map((milestone) => (
            <MilestoneRow key={milestone.id} milestone={milestone} onOpen={onOpen} />
          ))}
        </TableBody>
      ))}
      {showTasks && (
        <TaskRowGroup tasks={tasks} columns={4} onOpen={onOpenTask} onNewTask={onNewTask} />
      )}
    </Table>
  )
}

function MilestoneRow({
  milestone,
  onOpen,
}: {
  milestone: ScheduleMilestone
  onOpen: (milestoneId: string, opener: HTMLElement) => void
}) {
  return (
    <TableRow>
      <TableCell>
        <button
          type="button"
          data-milestone-id={milestone.id}
          onClick={(event) => onOpen(milestone.id, event.currentTarget)}
          className={cn(
            'rounded-control text-left text-ink hover:underline',
            milestone.state === 'Destravado' && 'font-semibold',
          )}
        >
          {milestone.title}
        </button>
        <div className="mt-0.5 flex flex-col gap-1">
          <MilestoneNotes milestone={milestone} />
          <ChecklistSummary progress={milestone.checklist_progress} />
          {milestone.optional && (
            <span>
              <OptionalBadge />
            </span>
          )}
        </div>
      </TableCell>
      <TableCell>
        <div className="flex flex-wrap items-center gap-1.5">
          <StateBadge state={milestone.state} />
          {milestone.overdue && <OverdueBadge />}
        </div>
      </TableCell>
      <TableCell>{copy.responsibles[milestone.responsible]}</TableCell>
      <TableCell numeric>
        <MilestoneDeadline milestone={milestone} format={formatTableDay} align="end" />
      </TableCell>
    </TableRow>
  )
}
