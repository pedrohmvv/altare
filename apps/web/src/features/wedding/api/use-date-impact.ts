import { queryOptions, useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import type { components } from '@/lib/api/schema'
import { weddingKeys } from './baseline'

/** O que mudaria no cronograma com a data hipotética; o servidor calcula, a tela só resume. */
export type DateImpact = components['schemas']['DatePreviewOut']
export type DateImpactChange = components['schemas']['DateChangeOut']

/**
 * Somente leitura (`GET /schedule/date-preview`): `exact` ausente é o cenário Sem Data. Sempre
 * recalcula (o cronograma pode ter mudado desde a última vez) e não repete a tentativa: a prévia é
 * um auxílio, e quem confirma não espera por ela.
 */
export const dateImpactQueryOptions = (exact: string | undefined) =>
  queryOptions({
    queryKey: weddingKeys.datePreview(exact),
    queryFn: async () =>
      unwrap(await api.GET('/api/v1/schedule/date-preview', { params: { query: { exact } } })),
    staleTime: 0,
    gcTime: 0,
    retry: false,
  })

/** A consulta só roda enquanto a tela de confirmação está aberta (`enabled`). */
export function useDateImpact(exact: string | undefined, enabled: boolean) {
  return useQuery({ ...dateImpactQueryOptions(exact), enabled })
}
