import { createMemoryHistory, RouterProvider } from '@tanstack/react-router'
import { render } from '@testing-library/react'
import { Providers } from '@/app/providers'
import type { CurrentUser } from '@/features/identity'
import { createQueryClient } from '@/lib/query-client'
import { createAppRouter } from '@/routes/router'
import { type FakeApi, jsonResponse, mockApi, problemResponse } from './fake-api'

export const FAKE_NOIVO: CurrentUser = {
  user_id: '00000000-0000-0000-0000-000000000001',
  username: 'exemplo.noivo',
  profile: 'Noivo',
}

interface RenderRouteOptions {
  /** Quem está na sessão; `null` simula alguém sem sessão. Padrão: o Noivo de exemplo. */
  session?: CurrentUser | null
  /** Um `fetch` falso já montado pelo teste, no lugar do padrão (que só responde ao /me). */
  api?: FakeApi
}

/** Monta o app inteiro numa rota, com histórico em memória, e espera as rotas carregarem. */
export async function renderRoute(path: string, options: RenderRouteOptions = {}) {
  const { session = FAKE_NOIVO } = options
  if (!options.api) {
    mockApi({
      'GET /api/v1/auth/me': session
        ? jsonResponse(200, session)
        : problemResponse(401, 'unauthenticated'),
    })
  }
  const queryClient = createQueryClient()
  const router = createAppRouter({
    queryClient,
    history: createMemoryHistory({ initialEntries: [path] }),
  })
  await router.load()
  render(
    <Providers queryClient={queryClient}>
      <RouterProvider router={router} />
    </Providers>,
  )
  return router
}
