import type { Responsible, Schedule, ScheduleMilestone, ScheduleTask } from '../api/schedule'
import type { ResponsibleSlug, ScheduleSearch, StateSlug } from '../search'

export type StateFilter = 'Bloqueado' | 'Destravado' | 'A fazer' | 'Em andamento' | 'Concluído'

export interface ScheduleFilters {
  responsible?: Responsible
  state?: StateFilter
  overdueOnly?: boolean
  tasksOnly?: boolean
}

export type Lens = 'casal' | 'minha'
export type SessionProfile = 'Noivo' | 'Noiva'

const RESPONSIBLES: Record<ResponsibleSlug, Responsible> = {
  noivo: 'Noivo',
  noiva: 'Noiva',
  ambos: 'Ambos',
}
const STATES: Record<StateSlug, StateFilter> = {
  bloqueado: 'Bloqueado',
  destravado: 'Destravado',
  'a-fazer': 'A fazer',
  'em-andamento': 'Em andamento',
  concluido: 'Concluído',
}

/** A URL guarda slugs; os filtros usam os valores da API. */
export function filtersFromSearch(search: ScheduleSearch): ScheduleFilters {
  return {
    responsible: search.responsavel ? RESPONSIBLES[search.responsavel] : undefined,
    state: search.estado ? STATES[search.estado] : undefined,
    overdueOnly: search.atrasados === true,
    tasksOnly: search.avulsas === true,
  }
}

export const hasActiveFilters = (filters: ScheduleFilters) =>
  Object.values(filters).some((value) => value !== undefined && value !== false)

export interface FilterContext {
  filters: ScheduleFilters
  /** A lente de visão: ausente é `casal`. */
  lens?: Lens
  /** Quem está na sessão; sem ele a lente `Minha visão` não tem de quem ser e não filtra. */
  profile?: SessionProfile
}

/**
 * A lente só vale com perfil e sem filtro explícito de responsável: o filtro explícito vence a
 * lente (D-080, resposta 1), e a tela diz isso em texto.
 */
export const lensApplies = ({ filters, lens, profile }: FilterContext) =>
  lens === 'minha' && profile !== undefined && filters.responsible === undefined

function matchesResponsible(responsible: Responsible, context: FilterContext): boolean {
  const { filters, profile } = context
  if (filters.responsible) return responsible === filters.responsible
  if (lensApplies(context)) return responsible === profile || responsible === 'Ambos'
  return true
}

function milestoneMatches(item: ScheduleMilestone, context: FilterContext): boolean {
  const { filters } = context
  if (filters.tasksOnly) return false
  if (!matchesResponsible(item.responsible, context)) return false
  if (filters.overdueOnly && !item.overdue) return false
  // `A fazer` é o estado da avulsa; o marco tem os quatro dele.
  if (filters.state && item.state !== filters.state) return false
  return true
}

function taskMatches(item: ScheduleTask, context: FilterContext): boolean {
  const { filters } = context
  if (!matchesResponsible(item.responsible, context)) return false
  if (filters.overdueOnly && !item.overdue) return false
  if (filters.state) {
    // `Concluído` (marco) é a `Concluída` da avulsa; `Bloqueado` e `Destravado` não existem nela.
    const state = item.state === 'Concluída' ? 'Concluído' : item.state
    if (state !== filters.state) return false
  }
  return true
}

export interface FilterResult {
  /** Os marcos que as listas mostram sob o filtro e a lente. */
  milestoneIds: ReadonlySet<string>
  taskIds: ReadonlySet<string>
  /** O "N" de "N de M itens". */
  shown: number
  /** O "M": tudo o que as listas mostram sem filtro (marcos ativos e avulsas). */
  total: number
  /** Algo estreita a lista: um filtro ou a lente `Minha visão` com perfil. */
  narrowed: boolean
}

/**
 * Escolhe o que mostrar, no navegador (D-080, resposta 1). Só decide a visibilidade: os bloqueios e
 * o progresso por fase continuam os do servidor, calculados sobre todos os itens. O arquivado já
 * não aparece em lista nenhuma e fica fora da conta.
 */
export function applyScheduleFilters(schedule: Schedule, context: FilterContext): FilterResult {
  const active = schedule.phases
    .flatMap((phase) => phase.milestones)
    .filter((milestone) => !milestone.archived)
  const milestoneIds = new Set(
    active.filter((item) => milestoneMatches(item, context)).map((item) => item.id),
  )
  const taskIds = new Set(
    schedule.tasks.filter((item) => taskMatches(item, context)).map((item) => item.id),
  )
  return {
    milestoneIds,
    taskIds,
    shown: milestoneIds.size + taskIds.size,
    total: active.length + schedule.tasks.length,
    narrowed: hasActiveFilters(context.filters) || lensApplies(context),
  }
}
