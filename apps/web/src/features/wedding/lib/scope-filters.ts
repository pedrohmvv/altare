import type { ScopeCategory, ScopeGroup, ScopeStatus } from '../api/scope'
import { SCOPE_STATUSES } from '../api/scope'
import type { AlignmentFilter, StatusSlug } from '../search'

export interface ScopeFilters {
  status?: StatusSlug
  alinhamento?: AlignmentFilter
  /** Só o que falta eu avaliar. */
  pendente?: boolean
  /** Mostrar as ocultas: não é um filtro, é o contrário (traz mais). */
  ocultas?: boolean
}

export const STATUS_BY_SLUG: Record<StatusSlug, ScopeStatus> = {
  discussao: 'Em discussão',
  entra: 'Entra (Essencial)',
  talvez: 'Talvez (Se couber)',
  fora: 'Fica de fora',
}

export const SLUG_BY_STATUS: Record<ScopeStatus, StatusSlug> = {
  'Em discussão': 'discussao',
  'Entra (Essencial)': 'entra',
  'Talvez (Se couber)': 'talvez',
  'Fica de fora': 'fora',
}

export type SessionProfile = 'Noivo' | 'Noiva'

export const myEvaluation = (category: ScopeCategory, profile: SessionProfile) =>
  profile === 'Noivo' ? category.noivo : category.noiva

export const otherEvaluation = (category: ScopeCategory, profile: SessionProfile) =>
  profile === 'Noivo' ? category.noiva : category.noivo

export function hasActiveFilters(filters: ScopeFilters): boolean {
  return Boolean(filters.status || filters.alinhamento || filters.pendente)
}

function matches(category: ScopeCategory, filters: ScopeFilters, profile: SessionProfile) {
  if (!(filters.ocultas || category.visible)) return false
  if (filters.status && category.status !== STATUS_BY_SLUG[filters.status]) return false
  if (filters.alinhamento && category.alignment.state !== filters.alinhamento) return false
  if (filters.pendente && myEvaluation(category, profile).priority !== null) return false
  return true
}

/**
 * Aplica os filtros da URL aos dados que a API já calculou. Não calcula nada de negócio:
 * alinhamento, visibilidade e progresso vêm prontos. Com filtro ligado, o grupo que ficou sem
 * nenhuma frente some; sem filtro, o grupo vazio e visível continua (para receber a primeira).
 */
export function filterGroups(
  groups: readonly ScopeGroup[],
  filters: ScopeFilters,
  profile: SessionProfile,
): ScopeGroup[] {
  const filtering = hasActiveFilters(filters)
  return groups.flatMap((group) => {
    if (group.hidden && !filters.ocultas) return []
    const categories = group.categories.filter((c) => matches(c, filters, profile))
    if (categories.length === 0 && filtering) return []
    return [{ ...group, categories }]
  })
}

export function groupByStatus(categories: readonly ScopeCategory[]) {
  return SCOPE_STATUSES.map((status) => ({
    status,
    categories: categories.filter((category) => category.status === status),
  }))
}

export type Lens = 'casal' | 'minha'
export type Highlight = 'mine-missing' | 'diverge'

/**
 * O que a lente destaca (D-021): `Minha visão` o que falta a minha avaliação; `Casal` o que diverge.
 * Destacar nunca esconde, e o destaque sai em texto, nunca só em cor.
 */
export function highlightFor(
  category: ScopeCategory,
  lens: Lens,
  profile: SessionProfile,
): Highlight | null {
  if (lens === 'minha')
    return myEvaluation(category, profile).priority === null ? 'mine-missing' : null
  return category.alignment.state === 'divergem' ? 'diverge' : null
}
