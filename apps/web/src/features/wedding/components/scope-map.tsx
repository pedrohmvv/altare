import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { EmptyState } from '@/components/ui/empty-state'
import { useMediaQuery } from '@/lib/use-media-query'
import { scopeMapQueryOptions } from '../api/scope'
import { copy } from '../copy'
import {
  filterGroups,
  groupByStatus,
  hasActiveFilters,
  highlightFor,
  type Lens,
  type SessionProfile,
} from '../lib/scope-filters'
import type { PlanningSearch } from '../search'
import { CategorySheet } from './category-sheet'
import { GroupsDialog } from './groups-dialog'
import { NewCategoryDialog } from './new-category-dialog'
import { ScopeCategoryCard } from './scope-category-card'
import { ScopeToolbar } from './scope-toolbar'

export interface ScopeMapProps {
  search: PlanningSearch
  onSearchChange: (patch: Partial<PlanningSearch>) => void
  /** Quem está na sessão: define o que é "o que falta eu avaliar". */
  profile: SessionProfile
  /** A lente de visão (`lente` na URL): ausente é `casal`. */
  lens?: Lens
}

/** O Mapa de Escopo (F-PLN-08): o que entra, o que talvez entre e o que fica de fora, com os filtros na URL. */
export function ScopeMap({ search, onSearchChange, profile, lens = 'casal' }: ScopeMapProps) {
  const query = useQuery(scopeMapQueryOptions)
  const wide = useMediaQuery('(min-width: 1024px)')
  // A última categoria aberta continua montada durante a animação de saída do painel.
  const [lastOpened, setLastOpened] = useState<string | undefined>(undefined)
  if (search.categoria && search.categoria !== lastOpened) setLastOpened(search.categoria)
  const [groupsOpen, setGroupsOpen] = useState(false)
  const [newCategoryOpen, setNewCategoryOpen] = useState(false)

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
      <>
        <Card>
          <EmptyState
            title={copy.scope.empty.title}
            description={copy.scope.empty.description}
            action={
              <Button variant="secondary" onClick={() => setGroupsOpen(true)}>
                {copy.scope.manage.manageGroups}
              </Button>
            }
          />
        </Card>
        <GroupsDialog groups={map.groups} open={groupsOpen} onOpenChange={setGroupsOpen} />
      </>
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
  const open = (categoryId: string) => onSearchChange({ categoria: categoryId })
  const owner = map.groups.find((group) =>
    group.categories.some((category) => category.id === (search.categoria ?? lastOpened)),
  )
  const sheetCategory = owner?.categories.find(
    (category) => category.id === (search.categoria ?? lastOpened),
  )
  const clear = () =>
    onSearchChange({ status: undefined, alinhamento: undefined, pendente: undefined })

  return (
    <div className="flex flex-col gap-8">
      <h2 className="sr-only">{copy.scope.title}</h2>
      {owner && sheetCategory && (
        <CategorySheet
          category={sheetCategory}
          groupName={owner.name}
          groups={map.groups.map((group) => ({ id: group.id, name: group.name }))}
          profile={profile}
          open={Boolean(search.categoria && sheetCategory)}
          onOpenChange={(isOpen) => !isOpen && onSearchChange({ categoria: undefined })}
        />
      )}
      <div className="flex flex-wrap gap-3">
        <Button onClick={() => setNewCategoryOpen(true)}>{copy.scope.manage.newCategory}</Button>
        <Button variant="secondary" onClick={() => setGroupsOpen(true)}>
          {copy.scope.manage.groups}
        </Button>
      </div>
      <NewCategoryDialog
        key={newCategoryOpen ? 'open' : 'closed'}
        groups={map.groups
          .filter((group) => !group.hidden)
          .map((group) => ({ id: group.id, name: group.name }))}
        open={newCategoryOpen}
        onOpenChange={setNewCategoryOpen}
      />
      <GroupsDialog groups={map.groups} open={groupsOpen} onOpenChange={setGroupsOpen} />
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
      ) : search.vista === 'status' && wide ? (
        <section aria-label={copy.scope.board.label} className="grid grid-cols-4 items-start gap-4">
          {groupByStatus(shown).map(({ status, categories }) => (
            <section
              key={status}
              aria-labelledby={`status-${status}`}
              className="flex flex-col gap-3 rounded-card bg-surface-muted p-3"
            >
              <h3 id={`status-${status}`} className="text-name text-ink">
                {status}
              </h3>
              {categories.length === 0 ? (
                <p className="text-body-sm text-ink-muted">{copy.scope.statusEmpty}</p>
              ) : (
                <ul className="flex flex-col gap-3">
                  {categories.map((category) => (
                    <ScopeCategoryCard
                      key={category.id}
                      category={category}
                      onOpen={open}
                      highlight={highlightFor(category, lens, profile)}
                    />
                  ))}
                </ul>
              )}
            </section>
          ))}
        </section>
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
                  <ScopeCategoryCard
                    key={category.id}
                    category={category}
                    onOpen={open}
                    highlight={highlightFor(category, lens, profile)}
                  />
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
                  <ScopeCategoryCard
                    key={category.id}
                    category={category}
                    onOpen={open}
                    highlight={highlightFor(category, lens, profile)}
                  />
                ))}
              </ul>
            )}
          </section>
        ))
      )}
    </div>
  )
}
