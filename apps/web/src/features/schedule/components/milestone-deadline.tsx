import { cn } from '@/lib/cn'
import type { ScheduleMilestone } from '../api/schedule'
import { copy } from '../copy'
import { countdownText } from '../lib/countdown'

interface DeadlineParts {
  milestone: ScheduleMilestone
  /** O formato da data: `dd/mm/aaaa` na tabela e no painel, `26 out 2026` no cartão. */
  format: (iso: string) => string
}

export interface MilestoneDeadlineProps extends DeadlineParts {
  /** A janela calculada, em linha própria; o painel a mostra na seção "Janela". */
  showWindow?: boolean
  /** O nome da coluna para o leitor de tela, onde a tabela não o repete. */
  srLabel?: boolean
  align?: 'start' | 'end'
}

/** O prazo que vale: o manual ou, sem ele, o fim da janela; "Sem prazo" se não há nenhum dos dois. */
export function DeadlineDate({
  milestone,
  format,
  srLabel = false,
  className,
}: DeadlineParts & { srLabel?: boolean; className?: string }) {
  return (
    <span className={className}>
      {srLabel && <span className="sr-only">{`${copy.list.columns.target}: `}</span>}
      {milestone.effective_target ? format(milestone.effective_target) : copy.list.noTarget}
    </span>
  )
}

/**
 * A contagem regressiva e a janela calculada. Tudo vem pronto da API: o navegador não sabe "hoje"
 * nem soma datas (stack.md §5.1). A contagem é texto visível; a data exata vai no `title`, nunca só
 * nele.
 */
export function DeadlineDetails({
  milestone,
  format,
  showWindow = true,
  align = 'start',
}: DeadlineParts & { showWindow?: boolean; align?: 'start' | 'end' }) {
  const countdown = countdownText(milestone.days_left)
  const tags: string[] = []
  if (milestone.window?.is_suggestion) tags.push(copy.deadline.suggestion)
  if (milestone.target_date !== null) tags.push(copy.deadline.manual)
  const range =
    showWindow && milestone.window_start && milestone.window_end
      ? { start: milestone.window_start, end: milestone.window_end }
      : null
  if (!countdown && !range) return null

  return (
    <span className={cn('flex flex-col gap-0.5', align === 'end' && 'items-end text-right')}>
      {countdown && (
        <span
          className="text-body-sm text-ink-muted"
          title={milestone.effective_target ? format(milestone.effective_target) : undefined}
        >
          {countdown}
        </span>
      )}
      {range && (
        <span className="text-ui-sm text-ink-muted">
          <span>{copy.deadline.window(format(range.start), format(range.end))}</span>
          {tags.map((tag) => (
            <span key={tag}>
              <span aria-hidden>{' · '}</span>
              <span>{tag}</span>
            </span>
          ))}
        </span>
      )}
    </span>
  )
}

/** O prazo, a contagem e a janela, empilhados: a coluna da tabela e o resumo do painel. */
export function MilestoneDeadline({
  milestone,
  format,
  showWindow = true,
  srLabel = false,
  align = 'start',
}: MilestoneDeadlineProps) {
  return (
    <span className={cn('flex flex-col gap-0.5', align === 'end' && 'items-end text-right')}>
      <DeadlineDate milestone={milestone} format={format} srLabel={srLabel} />
      <DeadlineDetails
        milestone={milestone}
        format={format}
        showWindow={showWindow}
        align={align}
      />
    </span>
  )
}
