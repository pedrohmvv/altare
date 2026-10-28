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
