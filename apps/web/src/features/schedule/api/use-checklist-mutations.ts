import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import { type ChecklistOwner, SCHEDULE_WRITE_SCOPE, type Schedule, scheduleKeys } from './schedule'

/**
 * Cada escrita devolve o cronograma inteiro, que vai ao cache; nada é otimista. O escopo serial faz
 * a segunda escrita esperar a primeira (`SCHEDULE_WRITE_SCOPE`, o mesmo de todas as escritas do
 * cronograma).
 */
function useChecklistWrite<Vars>(send: (vars: Vars) => Promise<Schedule>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: send,
    scope: SCHEDULE_WRITE_SCOPE,
    onSuccess: (schedule) => queryClient.setQueryData(scheduleKeys.all, schedule),
    onError: () => void queryClient.invalidateQueries({ queryKey: scheduleKeys.all }),
  })
}

/** O servidor não devolve o id do item novo; a tela não precisa dele. */
export const useAddChecklistItem = () =>
  useChecklistWrite(async (v: { owner: ChecklistOwner; text: string }) =>
    unwrap(
      await api.POST('/api/v1/schedule/{owner_kind}/{owner_id}/checklist', {
        params: { path: { owner_kind: v.owner.kind, owner_id: v.owner.id } },
        body: { text: v.text },
      }),
    ),
  )

/** Marcar, desmarcar e editar o texto são o mesmo pedido: a substituição inteira do item. */
export const useUpdateChecklistItem = () =>
  useChecklistWrite(async (v: { itemId: string; text: string; done: boolean; version: number }) =>
    unwrap(
      await api.PUT('/api/v1/schedule/checklist/{item_id}', {
        params: { path: { item_id: v.itemId } },
        body: { text: v.text, done: v.done, version: v.version },
      }),
    ),
  )

/** A lista completa de ids na nova ordem; sem versão, sem 409. */
export const useReorderChecklist = () =>
  useChecklistWrite(async (v: { owner: ChecklistOwner; ids: string[] }) =>
    unwrap(
      await api.PUT('/api/v1/schedule/{owner_kind}/{owner_id}/checklist/order', {
        params: { path: { owner_kind: v.owner.kind, owner_id: v.owner.id } },
        body: { ids: v.ids },
      }),
    ),
  )

/** Remover é imediato e não se desfaz. */
export const useRemoveChecklistItem = () =>
  useChecklistWrite(async (v: { itemId: string; version: number }) =>
    unwrap(
      await api.DELETE('/api/v1/schedule/checklist/{item_id}', {
        params: { path: { item_id: v.itemId }, query: { version: v.version } },
      }),
    ),
  )
