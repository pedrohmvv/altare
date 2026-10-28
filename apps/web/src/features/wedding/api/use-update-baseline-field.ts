import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import type { BaselineUpdate } from '../schemas/baseline-form'
import { weddingKeys } from './baseline'

const BASE = '/api/v1/wedding/baseline'

async function send(update: BaselineUpdate) {
  switch (update.key) {
    case 'date':
      return unwrap(await api.PUT(`${BASE}/date`, { body: update.body }))
    case 'city':
      return unwrap(await api.PUT(`${BASE}/city`, { body: update.body }))
    case 'format':
      return unwrap(await api.PUT(`${BASE}/format`, { body: update.body }))
    case 'size':
      return unwrap(await api.PUT(`${BASE}/size`, { body: update.body }))
    case 'ceiling':
      return unwrap(await api.PUT(`${BASE}/ceiling`, { body: update.body }))
    case 'ceremony':
      return unwrap(await api.PUT(`${BASE}/ceremony`, { body: update.body }))
  }
}

/**
 * A resposta é o quadro inteiro, já com as versões novas: vai direto para o cache. Valor do casamento
 * não é otimista; a tela só muda depois que a API aceitou.
 */
export function useUpdateBaselineField() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: send,
    onSuccess: (baseline) => {
      queryClient.setQueryData(weddingKeys.baseline, baseline)
      void queryClient.invalidateQueries({ queryKey: weddingKeys.changes })
    },
  })
}
