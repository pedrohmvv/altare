import { queryOptions } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import type { components } from '@/lib/api/schema'

export type Baseline = components['schemas']['BaselineOut']
export type BaselineKey = keyof Baseline
export type BaselineChange = components['schemas']['BaselineChangeOut']
export type DefinitionStatus = components['schemas']['DefinitionStatus']

/** A ordem em que as definições aparecem (F-PLN-01). */
export const BASELINE_KEYS: readonly BaselineKey[] = [
  'date',
  'city',
  'format',
  'size',
  'ceiling',
  'ceremony',
]

export const weddingKeys = {
  baseline: ['wedding', 'baseline'] as const,
  changes: ['wedding', 'baseline', 'changes'] as const,
}

export const baselineQueryOptions = queryOptions({
  queryKey: weddingKeys.baseline,
  queryFn: async () => unwrap(await api.GET('/api/v1/wedding/baseline')),
})

export const baselineChangesQueryOptions = queryOptions({
  queryKey: weddingKeys.changes,
  queryFn: async () => unwrap(await api.GET('/api/v1/wedding/baseline/changes')),
})
