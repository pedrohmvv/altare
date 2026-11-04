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
export type ScheduleTask = Schemas['TaskOut']
export type TaskState = Schemas['TaskState']
export type ChecklistItem = Schemas['ChecklistItemOut']
export type ChecklistProgress = Schemas['ChecklistProgressOut']
export type CategoryOption = Schemas['CategoryOptionOut']
export type LeftOut = Schemas['LeftOutOut']
export type MilestoneWindow = Schemas['MilestoneWindowOut']
export type WindowUnit = Schemas['WindowUnit']

/** As três escolhas de responsável, na ordem em que o casal as lê. */
export const RESPONSIBLES: readonly Responsible[] = ['Noivo', 'Noiva', 'Ambos']

/**
 * Um só escopo para toda escrita do cronograma: o TanStack as roda uma depois da outra. Toda resposta
 * é o cronograma inteiro; se duas saíssem juntas, a resposta velha poderia chegar por último e cobrir
 * a nova no cache, ou a segunda levar uma versão de antes da primeira.
 */
export const SCHEDULE_WRITE_SCOPE = { id: 'schedule-write' } as const

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

/** A avulsa pelo id, nos dados do cronograma inteiro: nunca numa lista filtrada. */
export function findTask(schedule: Schedule | undefined, id: string): ScheduleTask | undefined {
  return schedule?.tasks.find((item) => item.id === id)
}

/** De quem é um checklist: o marco ou a avulsa; é o trecho do caminho da API. */
export type ChecklistOwner = { kind: 'milestones' | 'tasks'; id: string }

/**
 * O servidor não devolve o id da avulsa criada: ele se acha pela diferença entre os ids de antes e
 * de depois. Só vale se for exatamente um; senão `null`, e a tela não abre nada.
 */
export function newTaskId(before: readonly string[], after: Schedule): string | null {
  const known = new Set(before)
  const added = after.tasks.filter((item) => !known.has(item.id))
  return added.length === 1 ? (added[0]?.id ?? null) : null
}
