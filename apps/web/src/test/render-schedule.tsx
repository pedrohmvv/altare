import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { vi } from 'vitest'
import { ToastProvider } from '@/components/ui/toast'
import { SchedulePage } from '@/features/schedule/pages/schedule-page'
import type { ScheduleSearch } from '@/features/schedule/search'
import { jsonResponse, mockApi } from './fake-api'
import { SCHEDULE } from './schedule-fixtures'

export const GET_SCHEDULE = 'GET /api/v1/schedule'
export const PUT_MILESTONE = (id: string) => `PUT /api/v1/schedule/milestones/${id}`
export const PUT_STATE = (id: string) => `PUT /api/v1/schedule/milestones/${id}/state`
export const PUT_DEPENDENCIES = (id: string) => `PUT /api/v1/schedule/milestones/${id}/dependencies`
export const DELETE_MILESTONE = (id: string) => `DELETE /api/v1/schedule/milestones/${id}`
export const RESTORE_MILESTONE = (id: string) => `POST /api/v1/schedule/milestones/${id}/restore`
export const POST_MILESTONE = 'POST /api/v1/schedule/milestones'
export const POST_PHASE = 'POST /api/v1/schedule/phases'
export const PUT_PHASE = (id: string) => `PUT /api/v1/schedule/phases/${id}`
export const PUT_PHASE_ORDER = 'PUT /api/v1/schedule/phases/order'

/** A URL do teste: o que a página pediu por último, para conferir o que ficou nela. */
export interface SearchProbe {
  current: ScheduleSearch
}

function Harness({ initial, probe }: { initial: ScheduleSearch; probe: SearchProbe }) {
  const [search, setSearch] = useState<ScheduleSearch>(initial)
  probe.current = search
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
  const probe: SearchProbe = { current: initial }
  render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <ToastProvider>
        <Harness initial={initial} probe={probe} />
      </ToastProvider>
    </QueryClientProvider>,
  )
  return { api, user: userEvent.setup(), probe }
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
