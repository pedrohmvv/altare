/** O que a URL de `/planejamento` guarda: aba, vista, filtros e a categoria aberta (design-system §10). */
export const STATUS_SLUGS = ['discussao', 'entra', 'talvez', 'fora'] as const
export type StatusSlug = (typeof STATUS_SLUGS)[number]

export const ALIGNMENT_FILTERS = ['divergem', 'falta'] as const
export type AlignmentFilter = (typeof ALIGNMENT_FILTERS)[number]

export interface PlanningSearch {
  /** Ausente é a aba das Definições Base. */
  aba?: 'escopo'
  /** Ausente é a vista por grupo. */
  vista?: 'status'
  status?: StatusSlug
  alinhamento?: AlignmentFilter
  /** Só o que falta eu avaliar. */
  pendente?: true
  ocultas?: true
  /** O id da categoria aberta no painel lateral. */
  categoria?: string
}

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

function oneOf<T extends string>(value: unknown, allowed: readonly T[]): T | undefined {
  return allowed.find((candidate) => candidate === value)
}

const isTrue = (value: unknown) => value === true || value === 'true'

/** Valor desconhecido é descartado: um link velho ou editado à mão nunca quebra a página. */
export function validatePlanningSearch(search: Record<string, unknown>): PlanningSearch {
  const result: PlanningSearch = {}
  const aba = oneOf(search.aba, ['escopo'] as const)
  const vista = oneOf(search.vista, ['status'] as const)
  const status = oneOf(search.status, STATUS_SLUGS)
  const alinhamento = oneOf(search.alinhamento, ALIGNMENT_FILTERS)
  if (aba) result.aba = aba
  if (vista) result.vista = vista
  if (status) result.status = status
  if (alinhamento) result.alinhamento = alinhamento
  if (isTrue(search.pendente)) result.pendente = true
  if (isTrue(search.ocultas)) result.ocultas = true
  if (typeof search.categoria === 'string' && UUID.test(search.categoria)) {
    result.categoria = search.categoria
  }
  return result
}
