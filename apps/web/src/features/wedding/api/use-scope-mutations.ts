import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import { type Priority, type ScopeMap, type ScopeStatus, scopeKeys } from './scope'

interface StatusChange {
  categoryId: string
  status: ScopeStatus
  reason: string | null
  /** A versão que a tela está mostrando agora. */
  version: number
}

/**
 * Mudar o status é a única ação com atualização otimista (baixo risco, `altare-frontend`): a tela
 * troca na hora e volta ao que era se a API recusar. Vale o mapa que a API devolve, sempre.
 */
export function useChangeScopeStatus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (change: StatusChange) =>
      unwrap(
        await api.PUT('/api/v1/wedding/scope/categories/{category_id}/status', {
          params: { path: { category_id: change.categoryId } },
          body: { status: change.status, reason: change.reason, version: change.version },
        }),
      ),
    onMutate: async (change) => {
      await queryClient.cancelQueries({ queryKey: scopeKeys.map })
      const previous = queryClient.getQueryData<ScopeMap>(scopeKeys.map)
      if (previous) {
        queryClient.setQueryData<ScopeMap>(scopeKeys.map, {
          ...previous,
          groups: previous.groups.map((group) => ({
            ...group,
            categories: group.categories.map((category) =>
              category.id === change.categoryId ? { ...category, status: change.status } : category,
            ),
          })),
        })
      }
      return { previous }
    },
    onError: (_error, _change, context) => {
      if (context?.previous) queryClient.setQueryData(scopeKeys.map, context.previous)
      void queryClient.invalidateQueries({ queryKey: scopeKeys.map })
    },
    onSuccess: (map, change) => {
      queryClient.setQueryData(scopeKeys.map, map)
      void queryClient.invalidateQueries({ queryKey: scopeKeys.history(change.categoryId) })
    },
  })
}

interface EvaluationChange {
  categoryId: string
  priority: Priority | null
  note: string | null
  /** A versão da avaliação do perfil da sessão. */
  version: number
}

export function useSetMyEvaluation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (change: EvaluationChange) =>
      unwrap(
        await api.PUT('/api/v1/wedding/scope/categories/{category_id}/my-evaluation', {
          params: { path: { category_id: change.categoryId } },
          body: { priority: change.priority, note: change.note, version: change.version },
        }),
      ),
    onSuccess: (map) => queryClient.setQueryData(scopeKeys.map, map),
    onError: () => void queryClient.invalidateQueries({ queryKey: scopeKeys.map }),
  })
}
