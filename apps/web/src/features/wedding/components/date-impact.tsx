import { ArrowRight } from 'lucide-react'
import { formatTableDay } from '@/lib/date'
import type { DateImpactChange, DateImpact as DateImpactData } from '../api/use-date-impact'
import { copy } from '../copy'

const text = copy.confirm.preview

/** Quantos marcos a lista mostra: o resto vira "e mais N". */
const MAX_LISTED = 5

type Range = DateImpactChange['window_before']

function describeRange(range: Range): string {
  return range ? text.range(formatTableDay(range.start), formatTableDay(range.end)) : text.noWindow
}

/** Uma frase por transição de modo (`mode_before` → `mode_after`); sem mudança, o resumo é um só. */
function headline({ mode_before, mode_after, changes }: DateImpactData): string {
  if (changes.length === 0) return text.none
  if (mode_before === 'sem_data' && mode_after === 'com_data') return text.gain(changes.length)
  if (mode_before === 'com_data' && mode_after === 'sem_data') return text.lose(changes.length)
  return text.change(changes.length)
}

/**
 * O que a nova data faz no cronograma, resumido do que o servidor calculou (F-CRN-05, regra 4):
 * a frase por transição, os prazos de vocês que não mudam, os atrasos novos e uma lista curta. Sem
 * resposta, diz que está calculando; com erro, diz que não calculou e a confirmação segue valendo.
 * A região de status existe desde o início, para o resultado ser anunciado quando chegar.
 */
export function DateImpact({
  data,
  failed,
}: {
  data: DateImpactData | undefined
  failed: boolean
}) {
  return (
    <>
      <div role="status" className="flex flex-col gap-1">
        {failed ? <p>{text.failed}</p> : data ? <Summary data={data} /> : <p>{text.loading}</p>}
      </div>
      {!failed && data && data.changes.length > 0 && <ChangedMilestones changes={data.changes} />}
    </>
  )
}

function Summary({ data }: { data: DateImpactData }) {
  // Com a mesma data o servidor ainda devolve os prazos manuais: só vale dizê-los quando algo muda.
  const somethingChanges = data.changes.length > 0 || data.mode_before !== data.mode_after
  return (
    <>
      <p className="text-ink">{headline(data)}</p>
      {somethingChanges && data.manual_kept > 0 && <p>{text.manualKept(data.manual_kept)}</p>}
      {data.newly_overdue > 0 && <p>{text.newlyOverdue(data.newly_overdue)}</p>}
    </>
  )
}

function ChangedMilestones({ changes }: { changes: readonly DateImpactChange[] }) {
  const listed = changes.slice(0, MAX_LISTED)
  return (
    <div className="mt-2 flex flex-col gap-1">
      <ul aria-label={text.listLabel} className="flex flex-col gap-1.5">
        {listed.map((change) => (
          <li key={change.id} className="flex flex-col">
            <span className="text-ink">{change.title}</span>
            <span className="flex flex-wrap items-center gap-x-1.5 text-num-sm">
              <span>{describeRange(change.window_before)}</span>
              <ArrowRight aria-hidden className="size-4 shrink-0" />
              <span className="sr-only">{text.becomes}</span>
              <span>{describeRange(change.window_after)}</span>
            </span>
          </li>
        ))}
      </ul>
      {changes.length > MAX_LISTED && <p>{text.more(changes.length - MAX_LISTED)}</p>}
    </div>
  )
}
