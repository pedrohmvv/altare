import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import type { components } from '@/lib/api/schema'
import {
  findMilestone,
  type LeftOut,
  type ManualState,
  type Responsible,
  SCHEDULE_WRITE_SCOPE,
  type Schedule,
  type ScheduleMilestone,
  scheduleKeys,
  type WindowUnit,
} from './schedule'

type MilestoneStateBody = components['schemas']['MilestoneStateIn']

/**
 * Toda escrita devolve o cronograma inteiro: vai direto para o cache, e nunca há pedaços de versões
 * diferentes na tela. O estado e o bloqueio de cada marco são derivados pela API, então nada aqui é
 * otimista: a tela só muda quando o servidor responde. Em erro, lê de novo.
 */
function useScheduleWrite<Vars>(send: (vars: Vars) => Promise<Schedule>) {
  const queryClient = useQueryClient()
  return useMutation({
    scope: SCHEDULE_WRITE_SCOPE,
    mutationFn: send,
    onSuccess: (schedule) => queryClient.setQueryData(scheduleKeys.all, schedule),
    onError: () => void queryClient.invalidateQueries({ queryKey: scheduleKeys.all }),
  })
}

/** O `PUT` é a substituição inteira dos campos editáveis: todos vão, os editados e os que ficaram. */
export const useUpdateMilestone = () =>
  useScheduleWrite(
    async (v: {
      milestoneId: string
      title: string
      phaseId: string
      categoryId: string | null
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
            title: v.title,
            phase_id: v.phaseId,
            category_id: v.categoryId,
            responsible: v.responsible,
            note: v.note,
            target_date: v.targetDate,
            version: v.version,
          },
        }),
      ),
  )

/** A janela inteira, em início, fim e unidade; vale em qualquer modo e em marco que não tinha janela. */
export const useUpdateMilestoneWindow = () =>
  useScheduleWrite(
    async (v: {
      milestoneId: string
      startBefore: number
      endBefore: number
      unit: WindowUnit
      /** A versão do marco que a tela viu. */
      version: number
    }) =>
      unwrap(
        await api.PUT('/api/v1/schedule/milestones/{milestone_id}/window', {
          params: { path: { milestone_id: v.milestoneId } },
          body: {
            start_before: v.startBefore,
            end_before: v.endBefore,
            unit: v.unit,
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
      /** A confirmação de concluir com itens do checklist em aberto; só vai quando é verdadeira. */
      ignoreOpenItems?: boolean
      version: number
    }) =>
      unwrap(
        await api.PUT('/api/v1/schedule/milestones/{milestone_id}/state', {
          params: { path: { milestone_id: v.milestoneId } },
          // O servidor assume `false` sem o campo: só a confirmação o leva, e o pedido comum não muda.
          body: {
            state: v.state,
            ignore_block: v.ignoreBlock,
            ...(v.ignoreOpenItems ? { ignore_open_items: true } : {}),
            version: v.version,
          } as MilestoneStateBody,
        }),
      ),
  )

export const useSetMilestoneDependencies = () =>
  useScheduleWrite(async (v: { milestoneId: string; dependsOn: string[]; version: number }) =>
    unwrap(
      await api.PUT('/api/v1/schedule/milestones/{milestone_id}/dependencies', {
        params: { path: { milestone_id: v.milestoneId } },
        body: { depends_on: v.dependsOn, version: v.version },
      }),
    ),
  )

export const useDeleteMilestone = () =>
  useScheduleWrite(async (v: { milestoneId: string; version: number }) =>
    unwrap(
      await api.DELETE('/api/v1/schedule/milestones/{milestone_id}', {
        params: { path: { milestone_id: v.milestoneId }, query: { version: v.version } },
      }),
    ),
  )

/** O que volta ao restaurar: o cronograma inteiro e as ligações que não puderam voltar. */
export interface Restored {
  schedule: Schedule
  leftOut: LeftOut[]
}

export function useRestoreMilestone() {
  const queryClient = useQueryClient()
  return useMutation({
    scope: SCHEDULE_WRITE_SCOPE,
    mutationFn: async (v: { milestoneId: string }): Promise<Restored> => {
      const restored = unwrap(
        await api.POST('/api/v1/schedule/milestones/{milestone_id}/restore', {
          params: { path: { milestone_id: v.milestoneId } },
        }),
      )
      return { schedule: restored.schedule, leftOut: restored.left_out }
    },
    onSuccess: ({ schedule }) => queryClient.setQueryData(scheduleKeys.all, schedule),
    onError: () => void queryClient.invalidateQueries({ queryKey: scheduleKeys.all }),
  })
}

/** O que volta ao criar: o cronograma inteiro e o marco criado, achado pelo id que a API devolve. */
export interface Created {
  schedule: Schedule
  /** `null` se o marco não está no cronograma devolvido (não deveria acontecer). */
  milestone: ScheduleMilestone | null
}

export function useCreateMilestone() {
  const queryClient = useQueryClient()
  return useMutation({
    scope: SCHEDULE_WRITE_SCOPE,
    mutationFn: async (v: {
      title: string
      phaseId: string
      responsible: Responsible
      categoryId: string | null
    }): Promise<Created> => {
      const created = unwrap(
        await api.POST('/api/v1/schedule/milestones', {
          body: {
            title: v.title,
            phase_id: v.phaseId,
            responsible: v.responsible,
            category_id: v.categoryId,
          },
        }),
      )
      return {
        schedule: created.schedule,
        milestone: findMilestone(created.schedule, created.milestone_id)?.milestone ?? null,
      }
    },
    onSuccess: ({ schedule }) => queryClient.setQueryData(scheduleKeys.all, schedule),
    onError: () => void queryClient.invalidateQueries({ queryKey: scheduleKeys.all }),
  })
}

export const useCreatePhase = () =>
  useScheduleWrite(async (v: { title: string }) =>
    unwrap(await api.POST('/api/v1/schedule/phases', { body: { title: v.title } })),
  )

export const useRenamePhase = () =>
  useScheduleWrite(async (v: { phaseId: string; title: string; version: number }) =>
    unwrap(
      await api.PUT('/api/v1/schedule/phases/{phase_id}', {
        params: { path: { phase_id: v.phaseId } },
        body: { title: v.title, version: v.version },
      }),
    ),
  )

export const useReorderPhases = () =>
  useScheduleWrite(async (v: { ids: string[] }) =>
    unwrap(await api.PUT('/api/v1/schedule/phases/order', { body: { ids: v.ids } })),
  )
