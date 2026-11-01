import { queryOptions } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import type { components } from '@/lib/api/schema'

type Schemas = components['schemas']
export type GuestList = Schemas['GuestListOut']
export type Household = Schemas['HouseholdOut']
export type Guest = Schemas['GuestOut']
export type GuestStatus = Schemas['GuestStatus']
export type AgeBand = Schemas['AgeBand']
export type Probability = Schemas['Probability']
export type Side = Schemas['Side']
export type GuestStatusChange = Schemas['GuestStatusChangeOut']
export type Headcount = Schemas['HeadcountOut']
export type BandCounts = Schemas['BandCountsOut']
export type GuestSettings = Schemas['GuestSettingsOut']

/** A ordem dos quatro status, a mesma do seletor. */
export const GUEST_STATUSES: readonly GuestStatus[] = [
  'Rascunho',
  'Convidado',
  'Confirmado',
  'Não irá',
]
export const AGE_BANDS: readonly AgeBand[] = ['Adulto', 'Criança pagante', 'Criança isenta']
export const PROBABILITIES: readonly Probability[] = ['Certeza', 'Provável', 'Fase 2']
export const SIDES: readonly Side[] = ['Noivo', 'Noiva', 'Comum']

export const guestKeys = {
  list: ['guests', 'list'] as const,
  history: (guestId: string) => ['guests', 'history', guestId] as const,
}

/**
 * Volta a ler quando a janela ganha foco: o que o outro mudou aparece na próxima leitura, sem
 * esperar um recarregamento (`D-021`). Não é tempo real, e a tela não promete que seja.
 */
export const guestListQueryOptions = queryOptions({
  queryKey: guestKeys.list,
  queryFn: async () => unwrap(await api.GET('/api/v1/guests')),
  refetchOnWindowFocus: true,
})

export const guestHistoryQueryOptions = (guestId: string) =>
  queryOptions({
    queryKey: guestKeys.history(guestId),
    queryFn: async () =>
      unwrap(
        await api.GET('/api/v1/guests/people/{guest_id}/history', {
          params: { path: { guest_id: guestId } },
        }),
      ),
  })
