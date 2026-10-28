import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { vi } from 'vitest'
import { ToastProvider } from '@/components/ui/toast'
import { GuestsPage } from '@/features/guests/pages/guests-page'
import type { GuestsSearch } from '@/features/guests/search'
import { jsonResponse, mockApi } from './fake-api'
import { LIST } from './guest-fixtures'

export const GET_GUESTS = 'GET /api/v1/guests'

function Harness({
  initial,
  profile,
  lens,
}: {
  initial: GuestsSearch
  profile: 'Noivo' | 'Noiva'
  lens: 'casal' | 'minha'
}) {
  const [search, setSearch] = useState<GuestsSearch>(initial)
  return (
    <GuestsPage
      search={search}
      profile={profile}
      lens={lens}
      onSearchChange={(patch) =>
        setSearch((previous) => {
          const next: Record<string, unknown> = { ...previous, ...patch }
          for (const key of Object.keys(next)) if (next[key] === undefined) delete next[key]
          return next as GuestsSearch
        })
      }
    />
  )
}

/** A página de convidados com a URL guardada em estado e a API falsa. */
export function renderGuests(
  handlers: Parameters<typeof mockApi>[0] = {},
  initial: GuestsSearch = {},
  session: { profile?: 'Noivo' | 'Noiva'; lens?: 'casal' | 'minha' } = {},
) {
  const api = mockApi({ [GET_GUESTS]: jsonResponse(200, LIST), ...handlers })
  render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <ToastProvider>
        <Harness
          initial={initial}
          profile={session.profile ?? 'Noivo'}
          lens={session.lens ?? 'casal'}
        />
      </ToastProvider>
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
