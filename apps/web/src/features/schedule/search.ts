/** Os slugs da URL são legíveis e estáveis; o rótulo em português é só da tela. */
export const RESPONSIBLE_SLUGS = ['noivo', 'noiva', 'ambos'] as const
export const STATE_SLUGS = [
  'bloqueado',
  'destravado',
  'a-fazer',
  'em-andamento',
  'concluido',
] as const

export type ResponsibleSlug = (typeof RESPONSIBLE_SLUGS)[number]
export type StateSlug = (typeof STATE_SLUGS)[number]

/**
 * O que a URL de `/cronograma` guarda (design-system §10): o marco ou a avulsa aberta no painel e
 * os filtros. A lente (`lente`) é do roteador raiz, e a busca por texto não existe aqui.
 */
export interface ScheduleSearch {
  /** O id do marco aberto no painel lateral. */
  marco?: string
  /** O id da avulsa aberta no painel lateral; nunca vem junto com `marco` (o marco vence). */
  avulsa?: string
  responsavel?: ResponsibleSlug
  estado?: StateSlug
  /** Só o que está atrasado (marcos e avulsas). */
  atrasados?: true
  /** Só as avulsas: esconde todas as fases. */
  avulsas?: true
}

const oneOf = <T extends string>(value: unknown, allowed: readonly T[]): T | undefined =>
  allowed.find((candidate) => candidate === value)

const isTrue = (value: unknown) => value === true || value === 'true'

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

/**
 * Valor desconhecido é descartado: um link velho ou editado à mão nunca quebra a página. Fica fora
 * da feature carregada sob demanda para o roteador poder importá-lo sem trazer a tela junto.
 */
export function validateScheduleSearch(search: Record<string, unknown>): ScheduleSearch {
  const result: ScheduleSearch = {}
  if (typeof search.marco === 'string' && UUID.test(search.marco)) result.marco = search.marco
  else if (typeof search.avulsa === 'string' && UUID.test(search.avulsa)) {
    result.avulsa = search.avulsa
  }
  const responsavel = oneOf(search.responsavel, RESPONSIBLE_SLUGS)
  const estado = oneOf(search.estado, STATE_SLUGS)
  if (responsavel) result.responsavel = responsavel
  if (estado) result.estado = estado
  if (isTrue(search.atrasados)) result.atrasados = true
  if (isTrue(search.avulsas)) result.avulsas = true
  return result
}
