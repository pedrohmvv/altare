import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { vi } from 'vitest'
import { SchedulePage } from '@/features/schedule/pages/schedule-page'
import type { ScheduleSearch } from '@/features/schedule/search'
import { jsonResponse, mockApi } from './fake-api'
import { SCHEDULE } from './schedule-fixtures'

export const GET_SCHEDULE = 'GET /api/v1/schedule'
export const PUT_MILESTONE = (id: string) => `PUT /api/v1/schedule/milestones/${id}`
export const PUT_STATE = (id: string) => `PUT /api/v1/schedule/milestones/${id}/state`

function Harness({ initial }: { initial: ScheduleSearch }) {
  const [search, setSearch] = useState<ScheduleSearch>(initial)
  return (
    <SchedulePage
      search={search}
      onSearchChange={(patch) =>
        setSearch((previous) => {
          const next: Record<string, unknown> = { ...previous, ...patch }
          for (const key of Object.keys(next)) if (next[key] === undefined) delete next[key]
          return next as ScheduleSearch
        })
      }
    />
  )
}

/** A página do cronograma com a URL guardada em estado e a API falsa. */
export function renderSchedule(
  handlers: Parameters<typeof mockApi>[0] = {},
  initial: ScheduleSearch = {},
) {
  const api = mockApi({ [GET_SCHEDULE]: jsonResponse(200, SCHEDULE), ...handlers })
  render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <Harness initial={initial} />
    </QueryClientProvider>,
  )
  return { api, user: userEvent.setup() }
}

/** Faz o `matchMedia` responder que a tela é larga: a tabela no lugar dos cartões. */
export function stubWideScreen() {
  vi.stubGlobal('matchMedia', (query: string) => ({
    matches: true,
    media: query,
    addEventListener() {},
    removeEventListener() {},
  }))
}
