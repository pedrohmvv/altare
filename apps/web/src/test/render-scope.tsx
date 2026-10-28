import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { ScopeMap } from '@/features/wedding/components/scope-map'
import type { PlanningSearch } from '@/features/wedding/search'
import { jsonResponse, mockApi } from './fake-api'
import { MAP } from './scope-fixtures'

const GET = 'GET /api/v1/wedding/scope'

function Harness({ initial, profile }: { initial: PlanningSearch; profile: 'Noivo' | 'Noiva' }) {
  const [search, setSearch] = useState<PlanningSearch>(initial)
  return (
    <ScopeMap
      search={search}
      profile={profile}
      onSearchChange={(patch) =>
        setSearch((prev) => {
          const next: Record<string, unknown> = { ...prev, ...patch }
          for (const key of Object.keys(next)) if (next[key] === undefined) delete next[key]
          return next as PlanningSearch
        })
      }
    />
  )
}

/** O Mapa de Escopo inteiro com a URL guardada em estado, e a API falsa. */
export function renderScope(
  handlers: Parameters<typeof mockApi>[0] = {},
  initial: PlanningSearch = {},
  profile: 'Noivo' | 'Noiva' = 'Noivo',
) {
  const api = mockApi({ [GET]: jsonResponse(200, MAP), ...handlers })
  render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <Harness initial={initial} profile={profile} />
    </QueryClientProvider>,
  )
  return { api, user: userEvent.setup() }
}

/** O mapa de exemplo com uma mudança numa categoria. */
export function mapWithCategory(id: string, change: Record<string, unknown>) {
  return {
    ...MAP,
    groups: MAP.groups.map((g) => ({
      ...g,
      categories: g.categories.map((c) => (c.id === id ? { ...c, ...change } : c)),
    })),
  }
}

/** O mapa de exemplo com um grupo do casal, vazio, que pode ser excluído. */
export function mapWithEmptyGroup() {
  return {
    ...MAP,
    groups: [
      ...MAP.groups,
      {
        id: 'g-vazio',
        name: 'Vazio Exemplo',
        position: 2,
        origin: 'casal',
        hidden: false,
        can_delete: true,
        version: 3,
        categories: [],
      },
    ],
  }
}
