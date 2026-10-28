import { queryOptions } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import type { components } from '@/lib/api/schema'

export type CurrentUser = components['schemas']['CurrentUserOut']

export const identityKeys = {
  me: ['identity', 'me'] as const,
}

/**
 * Quem está na sessão: o usuário, ou `null` sem sessão (a resposta 401 é uma resposta esperada, não
 * uma falha). Qualquer outro erro, inclusive o de rede, sobe como exceção.
 */
export const meQueryOptions = queryOptions({
  queryKey: identityKeys.me,
  queryFn: async (): Promise<CurrentUser | null> => {
    const result = await api.GET('/api/v1/auth/me')
    if (result.response.status === 401) return null
    return unwrap(result)
  },
  staleTime: 5 * 60_000,
  // A guarda espera esta resposta para abrir uma tela: sem sessão ou sem rede, vai logo à entrada.
  retry: false,
})
