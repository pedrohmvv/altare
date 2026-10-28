import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import { type GuestList, guestKeys } from './guests'

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
    onSuccess: (list) => queryClient.setQueryData(guestKeys.list, list),
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
