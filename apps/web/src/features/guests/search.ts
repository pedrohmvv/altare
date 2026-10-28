/** Os slugs da URL são legíveis e estáveis; o rótulo em português é só da tela. */
export const SIDE_SLUGS = ['noivo', 'noiva', 'comum'] as const
export const BAND_SLUGS = ['adulto', 'pagante', 'isenta'] as const
export const PROBABILITY_SLUGS = ['certeza', 'provavel', 'fase2'] as const
export const STATUS_SLUGS = ['rascunho', 'convidado', 'confirmado', 'nao-ira'] as const

export type SideSlug = (typeof SIDE_SLUGS)[number]
export type BandSlug = (typeof BAND_SLUGS)[number]
export type ProbabilitySlug = (typeof PROBABILITY_SLUGS)[number]
export type StatusSlug = (typeof STATUS_SLUGS)[number]

/** O que a URL de `/convidados` guarda (design-system.md §10): os filtros e o núcleo aberto. */
export interface GuestsSearch {
  /** O id do núcleo cujo painel está aberto. */
  nucleo?: string
  lado?: SideSlug
  faixa?: BandSlug
  probabilidade?: ProbabilitySlug
  status?: StatusSlug
  /** Só os núcleos sem convite enviado. */
  semconvite?: true
  /** Só quem tem restrição alimentar. */
  restricao?: true
  /** Na lente `Minha visão`: mostrar também o outro lado. */
  outro?: true
}

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

const oneOf = <T extends string>(value: unknown, allowed: readonly T[]): T | undefined =>
  allowed.find((candidate) => candidate === value)

const isTrue = (value: unknown) => value === true || value === 'true'

/**
 * Valida o que veio da URL: valor desconhecido é descartado, nunca vira erro. Fica fora da feature
 * carregada sob demanda para o roteador poder importá-lo sem trazer a tela junto. A busca por nome
 * não entra na URL: ela guardaria dado de convidado no histórico e no log de quem serve a página.
 */
export function validateGuestsSearch(search: Record<string, unknown>): GuestsSearch {
  const result: GuestsSearch = {}
  if (typeof search.nucleo === 'string' && UUID.test(search.nucleo)) result.nucleo = search.nucleo
  const lado = oneOf(search.lado, SIDE_SLUGS)
  const faixa = oneOf(search.faixa, BAND_SLUGS)
  const probabilidade = oneOf(search.probabilidade, PROBABILITY_SLUGS)
  const status = oneOf(search.status, STATUS_SLUGS)
  if (lado) result.lado = lado
  if (faixa) result.faixa = faixa
  if (probabilidade) result.probabilidade = probabilidade
  if (status) result.status = status
  if (isTrue(search.semconvite)) result.semconvite = true
  if (isTrue(search.restricao)) result.restricao = true
  if (isTrue(search.outro)) result.outro = true
  return result
}
