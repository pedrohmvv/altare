import { queryOptions } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import type { components } from '@/lib/api/schema'

type Schemas = components['schemas']
export type Schedule = Schemas['ScheduleOut']
export type SchedulePhase = Schemas['PhaseOut']
export type ScheduleMilestone = Schemas['MilestoneOut']
export type MilestoneState = Schemas['MilestoneState']
export type ManualState = Schemas['ManualState']
export type Responsible = Schemas['ProfileKind']
export type CategoryOption = Schemas['CategoryOptionOut']
export type LeftOut = Schemas['LeftOutOut']
export type MilestoneWindow = Schemas['MilestoneWindowOut']
export type WindowUnit = Schemas['WindowUnit']

/** As três escolhas de responsável, na ordem em que o casal as lê. */
export const RESPONSIBLES: readonly Responsible[] = ['Noivo', 'Noiva', 'Ambos']

export const scheduleKeys = {
  all: ['schedule'] as const,
}

/**
 * Volta a ler quando a janela ganha foco: o que o outro marcou aparece na próxima leitura, sem
 * esperar um recarregamento. Não é tempo real, e a tela não promete que seja.
 */
export const scheduleQueryOptions = queryOptions({
  queryKey: scheduleKeys.all,
  queryFn: async () => unwrap(await api.GET('/api/v1/schedule')),
  refetchOnWindowFocus: true,
})

/** O marco com a fase em que está: o `MilestoneOut` não traz o id da fase, quem o contém sabe. */
export function findMilestone(
  schedule: Schedule | undefined,
  id: string,
): { milestone: ScheduleMilestone; phase: SchedulePhase } | undefined {
  for (const phase of schedule?.phases ?? []) {
    const milestone = phase.milestones.find((item) => item.id === id)
    if (milestone) return { milestone, phase }
  }
  return undefined
}
