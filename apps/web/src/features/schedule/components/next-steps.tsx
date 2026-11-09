import { CircleAlert } from 'lucide-react'
import { useId, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatDay } from '@/lib/date'
import { copy } from '../copy'
import type { NextStep } from '../lib/next-steps'
import { DeadlineDate, DeadlineDetails, taskDeadline } from './milestone-deadline'

const text = copy.nextSteps
/** O que a lista mostra antes de "Ver todos". */
export const NEXT_STEPS_LIMIT = 8

export interface NextStepsProps {
  steps: readonly NextStep[]
  onOpen: (step: NextStep, opener: HTMLElement) => void
}

/**
 * Os próximos passos de quem está na sessão (F-CRN-09), no topo da lista do celular: sempre "eu ou
 * Ambos", sem seguir a lente nem os filtros. O prazo e a contagem vêm do servidor; o atraso tem
 * ícone e texto. Até 8, e "Ver todos" expande no lugar.
 */
export function NextSteps({ steps, onOpen }: NextStepsProps) {
  const titleId = useId()
  const [expanded, setExpanded] = useState(false)
  const shown = expanded ? steps : steps.slice(0, NEXT_STEPS_LIMIT)
  return (
    <section aria-labelledby={titleId} className="flex flex-col gap-3">
      <h2 id={titleId} className="text-name text-ink">
        {text.title}
      </h2>
      {steps.length === 0 ? (
        <p className="text-body-sm text-ink-muted">{text.empty}</p>
      ) : (
        <ul className="grid gap-3">
          {shown.map((step) => (
            <NextStepRow key={`${step.kind}-${step.id}`} step={step} onOpen={onOpen} />
          ))}
        </ul>
      )}
      {steps.length > NEXT_STEPS_LIMIT && (
        <Button
          variant="ghost"
          size="sm"
          className="self-start"
          aria-expanded={expanded}
          onClick={() => setExpanded((value) => !value)}
        >
          {expanded ? text.showLess : text.showAll(steps.length)}
        </Button>
      )}
    </section>
  )
}

function NextStepRow({
  step,
  onOpen,
}: {
  step: NextStep
  onOpen: (step: NextStep, opener: HTMLElement) => void
}) {
  const deadline = taskDeadline({ target_date: step.dueDate, days_left: step.daysLeft })
  return (
    <li className="relative flex flex-col gap-1.5 rounded-card border border-border bg-surface p-4 transition-colors duration-fast ease-standard hover:border-border-strong">
      <button
        type="button"
        data-next-step-id={step.id}
        aria-label={`${text.kind[step.kind]}: ${step.title}`}
        onClick={(event) => onOpen(step, event.currentTarget)}
        className="flex flex-col items-start gap-0.5 text-left after:absolute after:inset-0 after:rounded-card"
      >
        <span className="text-eyebrow text-ink-muted">{text.kind[step.kind]}</span>
        <span className="text-name text-ink">{step.title}</span>
      </button>
      {step.overdue && (
        <span>
          <Badge variant="attention" icon={<CircleAlert />}>
            {step.kind === 'task' ? copy.task.overdue : copy.overdue}
          </Badge>
        </span>
      )}
      <div className="flex flex-col gap-1 text-body-sm text-ink-muted">
        <p className="flex flex-wrap items-center justify-between gap-x-3">
          <span>
            <span className="sr-only">{`${copy.list.columns.responsible}: `}</span>
            {copy.responsibles[step.responsible]}
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
