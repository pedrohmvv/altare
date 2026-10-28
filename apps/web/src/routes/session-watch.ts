import type { QueryClient } from '@tanstack/react-query'
import type { AnyRouter } from '@tanstack/react-router'
import { identityKeys, LOGIN_PATH, meQueryOptions, safeDestination } from '@/features/identity'
import { ApiError } from '@/lib/api/errors'

/**
 * A sessão pode vencer com o app aberto. Quando qualquer consulta recebe 401, a pessoa vai para a
 * entrada, guardando onde estava, em vez de ficar numa tela que só mostra erros.
 */
export function redirectToLoginOnUnauthenticated(queryClient: QueryClient, router: AnyRouter) {
  return queryClient.getQueryCache().subscribe((event) => {
    if (event.type !== 'updated' || event.action.type !== 'error') return
    const { error } = event.action
    if (!(error instanceof ApiError) || error.status !== 401) return
    // A consulta da própria sessão trata o 401 sozinha: sem sessão é uma resposta, não uma falha.
    if (event.query.queryKey[0] === identityKeys.me[0]) return

    queryClient.setQueryData(meQueryOptions.queryKey, null)
    void router.navigate({
      to: LOGIN_PATH,
      search: { destino: safeDestination(router.state.location.href) },
    })
  })
}
