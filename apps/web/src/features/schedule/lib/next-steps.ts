import type { Responsible, Schedule } from '../api/schedule'

export interface NextStep {
  kind: 'milestone' | 'task'
  id: string
  title: string
  responsible: Responsible
  /** O prazo efetivo do marco ou o prazo da avulsa. */
  dueDate: string | null
  /** Os dias até o prazo, como o servidor os calculou: o navegador não sabe "hoje". */
  daysLeft: number | null
  overdue: boolean
}

/**
 * Os próximos passos de quem está na sessão (F-CRN-09): o que é seu ou de `Ambos` e pode andar
 * agora (marco Destravado ou Em andamento; avulsa A fazer ou Em andamento). Não segue a lente nem os
 * filtros. Ordem: atrasados primeiro (o prazo mais antigo antes), depois o prazo crescente, depois
 * os sem prazo; empate por título e por id.
 */
export function nextSteps(schedule: Schedule, profile: 'Noivo' | 'Noiva'): NextStep[] {
  const mine = (responsible: Responsible) => responsible === profile || responsible === 'Ambos'
  const steps: NextStep[] = [
    ...schedule.phases
      .flatMap((phase) => phase.milestones)
      .filter(
        (item) =>
          !item.archived &&
          mine(item.responsible) &&
          (item.state === 'Destravado' || item.state === 'Em andamento'),
      )
      .map((item) => ({
        kind: 'milestone' as const,
        id: item.id,
        title: item.title,
        responsible: item.responsible,
        dueDate: item.effective_target,
        daysLeft: item.days_left,
        overdue: item.overdue,
      })),
    ...schedule.tasks
      .filter(
        (item) =>
          mine(item.responsible) && (item.state === 'A fazer' || item.state === 'Em andamento'),
      )
      .map((item) => ({
        kind: 'task' as const,
        id: item.id,
        title: item.title,
        responsible: item.responsible,
        dueDate: item.target_date,
        daysLeft: item.days_left,
        overdue: item.overdue,
      })),
  ]
  return steps.sort(compareSteps)
}

function compareSteps(a: NextStep, b: NextStep): number {
  if (a.overdue !== b.overdue) return a.overdue ? -1 : 1
  if (a.dueDate !== b.dueDate) {
    if (a.dueDate === null) return 1
    if (b.dueDate === null) return -1
    return a.dueDate < b.dueDate ? -1 : 1
  }
  return a.title.localeCompare(b.title, 'pt-BR') || a.id.localeCompare(b.id)
}
