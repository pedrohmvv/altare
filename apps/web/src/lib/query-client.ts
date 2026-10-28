import { QueryClient } from '@tanstack/react-query'
import { ApiError } from '@/lib/api/errors'

export function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Só uma falha de rede merece nova tentativa: se a API respondeu, repetir não muda a resposta.
        retry: (failureCount, error) => !(error instanceof ApiError) && failureCount < 2,
        refetchOnWindowFocus: false,
      },
    },
  })
}

/** O cliente do app. Os testes criam o seu, para um não enxergar o cache do outro. */
export const queryClient = createQueryClient()
