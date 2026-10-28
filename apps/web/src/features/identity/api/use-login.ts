import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import { meQueryOptions } from './me'

export interface Credentials {
  username: string
  password: string
}

export function useLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (credentials: Credentials) =>
      unwrap(await api.POST('/api/v1/auth/login', { body: credentials })),
    onSuccess: (user) => {
      // Troca de usuário no mesmo computador: nada do usuário anterior pode ficar no cache.
      queryClient.getQueryCache().clear()
      queryClient.setQueryData(meQueryOptions.queryKey, user)
    },
  })
}
