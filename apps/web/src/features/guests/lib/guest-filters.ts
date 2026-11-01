import type { AgeBand, GuestStatus, Household, Probability, Side } from '../api/guests'
import type { BandSlug, GuestsSearch, ProbabilitySlug, SideSlug, StatusSlug } from '../search'

export interface GuestFilters {
  side?: Side
  band?: AgeBand
  probability?: Probability
  status?: GuestStatus
  withoutInvite?: boolean
  withDietary?: boolean
}

const SIDES: Record<SideSlug, Side> = { noivo: 'Noivo', noiva: 'Noiva', comum: 'Comum' }
const BANDS: Record<BandSlug, AgeBand> = {
  adulto: 'Adulto',
  pagante: 'Criança pagante',
  isenta: 'Criança isenta',
}
const PROBABILITIES: Record<ProbabilitySlug, Probability> = {
  certeza: 'Certeza',
  provavel: 'Provável',
  fase2: 'Fase 2',
}
const STATUSES: Record<StatusSlug, GuestStatus> = {
  rascunho: 'Rascunho',
  convidado: 'Convidado',
  confirmado: 'Confirmado',
  'nao-ira': 'Não irá',
}

/** A URL guarda slugs; os filtros usam os valores da API. */
export function filtersFromSearch(search: GuestsSearch): GuestFilters {
  return {
    side: search.lado ? SIDES[search.lado] : undefined,
    band: search.faixa ? BANDS[search.faixa] : undefined,
    probability: search.probabilidade ? PROBABILITIES[search.probabilidade] : undefined,
    status: search.status ? STATUSES[search.status] : undefined,
    withoutInvite: search.semconvite === true,
    withDietary: search.restricao === true,
  }
}

export const hasActiveFilters = (filters: GuestFilters) =>
  Object.values(filters).some((value) => value !== undefined && value !== false)

/** Sem diferenciar caixa, acento nem espaços repetidos (F-CNV-07). */
export function normalizeText(text: string): string {
  return text
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)
    .join(' ')
}

/**
 * Aplica a busca, os filtros e a lente sobre a lista inteira (F-CNV-07). O filtro de **lado** e o
 * de **convite** valem para o núcleo; faixa, probabilidade, status e restrição valem para cada
 * pessoa, e o núcleo sem ninguém que sobre some. Se o nome do núcleo bate com a busca, todas as
 * pessoas dele entram; senão, só as que batem. O resumo do núcleo continua o real: a tela mostra
 * "N de M pessoas" à parte. É só escolha do que mostrar; nenhum número de negócio nasce aqui.
 */
export function filterHouseholds(
  households: readonly Household[],
  filters: GuestFilters,
  query: string,
  sides?: readonly Side[],
): Household[] {
  const text = normalizeText(query)
  const result: Household[] = []
  for (const household of households) {
    if (sides && !filters.side && !sides.includes(household.side)) continue
    if (filters.side && household.side !== filters.side) continue
    if (filters.withoutInvite && household.invite_sent_on !== null) continue
    const householdMatches = text === '' || normalizeText(household.name).includes(text)
    const guests = household.guests.filter(
      (guest) =>
        (householdMatches || normalizeText(guest.name ?? '').includes(text)) &&
        (!filters.band || guest.band === filters.band) &&
        (!filters.probability || guest.probability === filters.probability) &&
        (!filters.status || guest.status === filters.status) &&
        (!filters.withDietary || (guest.dietary_restriction ?? '').trim() !== ''),
    )
    if (guests.length > 0) result.push({ ...household, guests })
  }
  return result
}

export const countGuests = (households: readonly Household[]) =>
  households.reduce((sum, household) => sum + household.guests.length, 0)

/** Os ids das pessoas que estão na tela, na ordem da lista: é o que a exportação leva (F-CNV-08). */
export const visibleGuestIds = (households: readonly Household[]) =>
  households.flatMap((household) => household.guests.map((guest) => guest.id))
