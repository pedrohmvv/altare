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

const BASE = '/api/v1/wedding/scope'

/** Toda escrita devolve o mapa inteiro: vai direto para o cache. Valor do casamento não é otimista. */
function useScopeWrite<Vars>(send: (vars: Vars) => Promise<ScopeMap>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: send,
    onSuccess: (map) => queryClient.setQueryData(scopeKeys.map, map),
    onError: () => void queryClient.invalidateQueries({ queryKey: scopeKeys.map }),
  })
}

export const useCreateScopeGroup = () =>
  useScopeWrite(async (v: { name: string }) =>
    unwrap(await api.POST(`${BASE}/groups`, { body: { name: v.name } })),
  )

export const useRenameScopeGroup = () =>
  useScopeWrite(async (v: { groupId: string; name: string; version: number }) =>
    unwrap(
      await api.PUT('/api/v1/wedding/scope/groups/{group_id}', {
        params: { path: { group_id: v.groupId } },
        body: { name: v.name, version: v.version },
      }),
    ),
  )

export const useSetScopeGroupVisibility = () =>
  useScopeWrite(async (v: { groupId: string; hidden: boolean; version: number }) =>
    unwrap(
      await api.PUT('/api/v1/wedding/scope/groups/{group_id}/visibility', {
        params: { path: { group_id: v.groupId } },
        body: { hidden: v.hidden, version: v.version },
      }),
    ),
  )

export const useDeleteScopeGroup = () =>
  useScopeWrite(async (v: { groupId: string; version: number }) =>
    unwrap(
      await api.DELETE('/api/v1/wedding/scope/groups/{group_id}', {
        params: { path: { group_id: v.groupId }, query: { version: v.version } },
      }),
    ),
  )

export const useCreateScopeCategory = () =>
  useScopeWrite(async (v: { groupId: string; name: string; estimateCents: number | null }) =>
    unwrap(
      await api.POST('/api/v1/wedding/scope/categories', {
        body: { group_id: v.groupId, name: v.name, estimate_cents: v.estimateCents },
      }),
    ),
  )

export const useUpdateScopeCategory = () =>
  useScopeWrite(
    async (v: {
      categoryId: string
      name: string
      groupId: string
      estimateCents: number | null
      version: number
    }) =>
      unwrap(
        await api.PUT('/api/v1/wedding/scope/categories/{category_id}', {
          params: { path: { category_id: v.categoryId } },
          body: {
            name: v.name,
            group_id: v.groupId,
            estimate_cents: v.estimateCents,
            version: v.version,
          },
        }),
      ),
  )

export const useSetScopeCategoryVisibility = () =>
  useScopeWrite(async (v: { categoryId: string; hidden: boolean; version: number }) =>
    unwrap(
      await api.PUT('/api/v1/wedding/scope/categories/{category_id}/visibility', {
        params: { path: { category_id: v.categoryId } },
        body: { hidden: v.hidden, version: v.version },
      }),
    ),
  )

export const useDeleteScopeCategory = () =>
  useScopeWrite(async (v: { categoryId: string; version: number }) =>
    unwrap(
      await api.DELETE('/api/v1/wedding/scope/categories/{category_id}', {
        params: { path: { category_id: v.categoryId }, query: { version: v.version } },
      }),
    ),
  )
