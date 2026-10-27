import { createMemoryHistory, RouterProvider } from '@tanstack/react-router'
import { render } from '@testing-library/react'
import { Providers } from '@/app/providers'
import { createAppRouter } from '@/routes/router'

/** Monta o app inteiro numa rota, com histórico em memória, e espera as rotas carregarem. */
export async function renderRoute(path: string) {
  const router = createAppRouter(createMemoryHistory({ initialEntries: [path] }))
  await router.load()
  render(
    <Providers>
      <RouterProvider router={router} />
    </Providers>,
  )
  return router
}
