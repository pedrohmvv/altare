import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { ensureOk } from '@/lib/api/errors'
import { meQueryOptions } from './me'

export function useLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async () => ensureOk(await api.POST('/api/v1/auth/logout')),
    // Já sem sessão: a guarda da próxima rota não pode achar que o usuário ainda está lá.
    onSuccess: () => queryClient.setQueryData(meQueryOptions.queryKey, null),
  })
}
