import { queryOptions } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import type { components } from '@/lib/api/schema'

type Schemas = components['schemas']
export type ScopeMap = Schemas['ScopeMapOut']
export type ScopeGroup = Schemas['GroupOut']
export type ScopeCategory = Schemas['CategoryOut']
export type ScopeStatus = Schemas['ScopeStatus']
export type Priority = Schemas['Priority']
export type StatusChange = Schemas['StatusChangeOut']
export type ScopeReference = Schemas['ReferenceOut']

/** A ordem dos quatro status, a mesma das colunas do quadro. */
export const SCOPE_STATUSES: readonly ScopeStatus[] = [
  'Em discussão',
  'Entra (Essencial)',
  'Talvez (Se couber)',
  'Fica de fora',
]

export const scopeKeys = {
  map: ['wedding', 'scope'] as const,
  history: (categoryId: string) => ['wedding', 'scope', 'history', categoryId] as const,
  references: (categoryId: string) => ['wedding', 'scope', 'references', categoryId] as const,
}

/**
 * Volta a ler quando a janela ganha foco: o que o outro avaliou aparece na próxima leitura, sem
 * esperar um recarregamento (`D-021`). Não é tempo real, e a tela não promete que seja.
 */
export const scopeMapQueryOptions = queryOptions({
  queryKey: scopeKeys.map,
  queryFn: async () => unwrap(await api.GET('/api/v1/wedding/scope')),
  refetchOnWindowFocus: true,
})

export const scopeHistoryQueryOptions = (categoryId: string) =>
  queryOptions({
    queryKey: scopeKeys.history(categoryId),
    queryFn: async () =>
      unwrap(
        await api.GET('/api/v1/wedding/scope/categories/{category_id}/history', {
          params: { path: { category_id: categoryId } },
        }),
      ),
  })

export const scopeReferencesQueryOptions = (categoryId: string) =>
  queryOptions({
    queryKey: scopeKeys.references(categoryId),
    queryFn: async () =>
      unwrap(
        await api.GET('/api/v1/wedding/scope/categories/{category_id}/references', {
          params: { path: { category_id: categoryId } },
        }),
      ),
  })
