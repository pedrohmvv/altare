import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import { type ManualState, type Responsible, type Schedule, scheduleKeys } from './schedule'

/**
 * Toda escrita devolve o cronograma inteiro: vai direto para o cache, e nunca há pedaços de versões
 * diferentes na tela. O estado e o bloqueio de cada marco são derivados pela API, então nada aqui é
 * otimista: a tela só muda quando o servidor responde. Em erro, lê de novo.
 */
function useScheduleWrite<Vars>(send: (vars: Vars) => Promise<Schedule>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: send,
    onSuccess: (schedule) => queryClient.setQueryData(scheduleKeys.all, schedule),
    onError: () => void queryClient.invalidateQueries({ queryKey: scheduleKeys.all }),
  })
}

export const useUpdateMilestone = () =>
  useScheduleWrite(
    async (v: {
      milestoneId: string
      responsible: Responsible
      note: string | null
      targetDate: string | null
      /** A versão do marco que a tela viu. */
      version: number
    }) =>
      unwrap(
        await api.PUT('/api/v1/schedule/milestones/{milestone_id}', {
          params: { path: { milestone_id: v.milestoneId } },
          body: {
            responsible: v.responsible,
            note: v.note,
            target_date: v.targetDate,
            version: v.version,
          },
        }),
      ),
  )

export const useChangeMilestoneState = () =>
  useScheduleWrite(
    async (v: {
      milestoneId: string
      /** `null` reabre: o marco volta ao estado derivado. */
      state: ManualState | null
      ignoreBlock: boolean
      version: number
    }) =>
      unwrap(
        await api.PUT('/api/v1/schedule/milestones/{milestone_id}/state', {
          params: { path: { milestone_id: v.milestoneId } },
          body: { state: v.state, ignore_block: v.ignoreBlock, version: v.version },
        }),
      ),
  )
