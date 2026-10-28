import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import { type GuestList, type GuestStatus, guestKeys } from './guests'

type GuestBody = ReturnType<typeof import('../schemas/guest-forms').toGuestBody>
type HouseholdBody = ReturnType<typeof import('../schemas/guest-forms').toHouseholdBody>

/**
 * Toda escrita devolve a lista inteira: vai direto para o cache, e nunca há pedaços de versões
 * diferentes na tela. Os contadores, quando existirem, também são do servidor, então nada aqui é
 * otimista: o dado de convidado e o que se deriva dele só mudam quando a API responde.
 */
function useGuestWrite<Vars>(send: (vars: Vars) => Promise<GuestList>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: send,
    onSuccess: (list) => {
      queryClient.setQueryData(guestKeys.list, list)
      // O histórico de status de cada pessoa pode ter mudado; lê de novo só se alguém o abriu.
      void queryClient.invalidateQueries({ queryKey: ['guests', 'history'] })
    },
    onError: () => void queryClient.invalidateQueries({ queryKey: guestKeys.list }),
  })
}

export const useCreateHousehold = () =>
  useGuestWrite(async (v: { household: HouseholdBody; firstGuest: GuestBody }) =>
    unwrap(
      await api.POST('/api/v1/guests/households', {
        body: { household: v.household, first_guest: v.firstGuest },
      }),
    ),
  )

export const useUpdateHousehold = () =>
  useGuestWrite(async (v: { householdId: string; household: HouseholdBody; version: number }) =>
    unwrap(
      await api.PUT('/api/v1/guests/households/{household_id}', {
        params: { path: { household_id: v.householdId } },
        body: { ...v.household, version: v.version },
      }),
    ),
  )

export const useAddGuest = () =>
  useGuestWrite(async (v: { householdId: string; guest: GuestBody }) =>
    unwrap(
      await api.POST('/api/v1/guests/households/{household_id}/guests', {
        params: { path: { household_id: v.householdId } },
        body: v.guest,
      }),
    ),
  )

export const useAddCompanion = () =>
  useGuestWrite(async (v: { holderId: string }) =>
    unwrap(
      await api.POST('/api/v1/guests/people/{guest_id}/companion', {
        params: { path: { guest_id: v.holderId } },
        body: { name: null },
      }),
    ),
  )

export const useUpdateGuest = () =>
  useGuestWrite(
    async (v: {
      guestId: string
      guest: GuestBody
      declineReason: string | null
      version: number
    }) =>
      unwrap(
        await api.PUT('/api/v1/guests/people/{guest_id}', {
          params: { path: { guest_id: v.guestId } },
          body: { ...v.guest, decline_reason: v.declineReason, version: v.version },
        }),
      ),
  )

export const useChangeGuestStatus = () =>
  useGuestWrite(
    async (v: { guestId: string; status: GuestStatus; reason: string | null; version: number }) =>
      unwrap(
        await api.PUT('/api/v1/guests/people/{guest_id}/status', {
          params: { path: { guest_id: v.guestId } },
          body: { status: v.status, reason: v.reason, version: v.version },
        }),
      ),
  )

export const useMoveGuest = () =>
  useGuestWrite(async (v: { guestId: string; householdId: string; version: number }) =>
    unwrap(
      await api.PUT('/api/v1/guests/people/{guest_id}/household', {
        params: { path: { guest_id: v.guestId } },
        body: { household_id: v.householdId, version: v.version },
      }),
    ),
  )

export const useDeleteGuest = () =>
  useGuestWrite(
    async (v: { guestId: string; version: number; companion: 'delete' | 'keep' | null }) =>
      unwrap(
        await api.DELETE('/api/v1/guests/people/{guest_id}', {
          params: {
            path: { guest_id: v.guestId },
            query: { version: v.version, companion: v.companion },
          },
        }),
      ),
  )

export const useRestoreGuest = () =>
  useGuestWrite(async (v: { guestId: string }) =>
    unwrap(
      await api.POST('/api/v1/guests/people/{guest_id}/restore', {
        params: { path: { guest_id: v.guestId } },
      }),
    ),
  )

export const useDeleteHousehold = () =>
  useGuestWrite(async (v: { householdId: string; version: number }) =>
    unwrap(
      await api.DELETE('/api/v1/guests/households/{household_id}', {
        params: { path: { household_id: v.householdId }, query: { version: v.version } },
      }),
    ),
  )

export const useRestoreHousehold = () =>
  useGuestWrite(async (v: { householdId: string }) =>
    unwrap(
      await api.POST('/api/v1/guests/households/{household_id}/restore', {
        params: { path: { household_id: v.householdId } },
      }),
    ),
  )
