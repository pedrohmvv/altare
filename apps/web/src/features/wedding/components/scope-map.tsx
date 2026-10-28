import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { EmptyState } from '@/components/ui/empty-state'
import { scopeMapQueryOptions } from '../api/scope'
import { copy } from '../copy'
import {
  filterGroups,
  groupByStatus,
  hasActiveFilters,
  type SessionProfile,
} from '../lib/scope-filters'
import type { PlanningSearch } from '../search'
import { ScopeCategoryCard } from './scope-category-card'
import { ScopeToolbar } from './scope-toolbar'

export interface ScopeMapProps {
  search: PlanningSearch
  onSearchChange: (patch: Partial<PlanningSearch>) => void
  /** Quem está na sessão: define o que é "o que falta eu avaliar". */
  profile: SessionProfile
}

/** O Mapa de Escopo (F-PLN-08): o que entra, o que talvez entre e o que fica de fora, com os filtros na URL. */
export function ScopeMap({ search, onSearchChange, profile }: ScopeMapProps) {
  const query = useQuery(scopeMapQueryOptions)

  if (query.isPending) {
    return (
      <Card aria-busy>
        <p className="text-body-sm text-ink-muted">{copy.scope.loading}</p>
        <div aria-hidden className="mt-4 flex flex-col gap-3">
          <div className="h-3 w-2/3 rounded-pill bg-surface-sunken" />
          <div className="h-3 w-1/2 rounded-pill bg-surface-sunken" />
          <div className="h-16 rounded-card bg-surface-sunken" />
        </div>
      </Card>
    )
  }
  if (query.isError) {
    return (
      <Card>
        <p className="text-body font-medium text-ink">{copy.scope.loadError.title}</p>
        <p className="text-body-sm text-ink-muted">{copy.scope.loadError.description}</p>
        <Button variant="secondary" className="mt-3" onClick={() => void query.refetch()}>
          {copy.scope.loadError.retry}
        </Button>
      </Card>
    )
  }

  const map = query.data
  if (map.groups.every((group) => group.categories.length === 0)) {
    return (
      <Card>
        <EmptyState title={copy.scope.empty.title} description={copy.scope.empty.description} />
      </Card>
    )
  }

  const filters = {
    status: search.status,
    alinhamento: search.alinhamento,
    pendente: search.pendente,
    ocultas: search.ocultas,
  }
  const groups = filterGroups(map.groups, filters, profile)
  const shown = groups.flatMap((group) => group.categories)
  const clear = () =>
    onSearchChange({ status: undefined, alinhamento: undefined, pendente: undefined })

  return (
    <div className="flex flex-col gap-8">
      <h2 className="sr-only">{copy.scope.title}</h2>
      <ScopeToolbar map={map} search={search} onSearchChange={onSearchChange} />

      {shown.length === 0 && hasActiveFilters(filters) ? (
        <Card>
          <EmptyState
            title={copy.scope.noMatch.title}
            description={copy.scope.noMatch.description}
            action={
              <Button variant="secondary" onClick={clear}>
                {copy.scope.noMatch.clear}
              </Button>
            }
          />
        </Card>
      ) : search.vista === 'status' ? (
        groupByStatus(shown).map(({ status, categories }) => (
          <section
            key={status}
            aria-labelledby={`status-${status}`}
            className="flex flex-col gap-3"
          >
            <h3 id={`status-${status}`} className="text-heading text-ink">
              {status}
            </h3>
            {categories.length === 0 ? (
              <p className="text-body-sm text-ink-muted">{copy.scope.statusEmpty}</p>
            ) : (
              <ul className="grid gap-3 md:grid-cols-2">
                {categories.map((category) => (
                  <ScopeCategoryCard key={category.id} category={category} />
                ))}
              </ul>
            )}
          </section>
        ))
      ) : (
        groups.map((group) => (
          <section
            key={group.id}
            aria-labelledby={`group-${group.id}`}
            className="flex flex-col gap-3"
          >
            <div className="flex items-center gap-3">
              <h3 id={`group-${group.id}`} className="text-heading text-ink">
                {group.name}
              </h3>
              {group.hidden && <Badge variant="outline">{copy.scope.card.hiddenGroup}</Badge>}
            </div>
            {group.categories.length === 0 ? (
              <p className="text-body-sm text-ink-muted">{copy.scope.groupEmpty}</p>
            ) : (
              <ul className="grid gap-3 md:grid-cols-2">
                {group.categories.map((category) => (
                  <ScopeCategoryCard key={category.id} category={category} />
                ))}
              </ul>
            )}
          </section>
        ))
      )}
    </div>
  )
}
