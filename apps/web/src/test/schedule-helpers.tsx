import { screen, waitFor, within } from '@testing-library/react'
import type {
  ChecklistItem,
  Schedule,
  ScheduleMilestone,
  ScheduleTask,
} from '@/features/schedule/api/schedule'
import { jsonResponse } from './fake-api'
import type { renderSchedule } from './render-schedule'
import { checklistOf, SCHEDULE, scheduleWith, scheduleWithChecklist } from './schedule-fixtures'

type Renderer = ReturnType<typeof renderSchedule>

/** A API falsa com memória: a leitura devolve o que a última escrita deixou, como o servidor faria. */
export function memory(initial: Schedule = SCHEDULE) {
  const state = { schedule: initial }
  return {
    state,
    get: () => jsonResponse(200, state.schedule),
    /** Uma escrita que troca o cronograma inteiro pelo que o teste manda. */
    set: (next: Schedule | ((current: Schedule) => Schedule)) => () => {
      state.schedule = typeof next === 'function' ? next(state.schedule) : next
      return jsonResponse(200, state.schedule)
    },
    /** O POST de criar marco: o cronograma novo e o id do marco criado, aninhados. */
    created: (next: Schedule, milestoneId: string) => () => {
      state.schedule = next
      return jsonResponse(201, { schedule: next, milestone_id: milestoneId })
    },
    /** A escrita de uma avulsa: troca os campos dela e devolve o cronograma inteiro. */
    writeTask: (id: string, change: (item: ScheduleTask) => Partial<ScheduleTask>) => () => {
      state.schedule = {
        ...state.schedule,
        tasks: state.schedule.tasks.map((item) =>
          item.id === id ? { ...item, ...change(item) } : item,
        ),
      }
      return jsonResponse(200, state.schedule)
    },
    /** Uma avulsa nova no fim da lista; o servidor devolve só o cronograma, sem o id. */
    addTask: (item: ScheduleTask) => () => {
      state.schedule = { ...state.schedule, tasks: [...state.schedule.tasks, item] }
      return jsonResponse(201, state.schedule)
    },
    /** A escrita do checklist de um dono: recebe os itens de agora e devolve os de depois. */
    writeChecklist:
      (ownerId: string, change: (items: ChecklistItem[]) => ChecklistItem[]) => () => {
        state.schedule = scheduleWithChecklist(
          ownerId,
          change(checklistOf(state.schedule, ownerId)),
          state.schedule,
        )
        return jsonResponse(200, state.schedule)
      },
    write: (id: string, change: (item: ScheduleMilestone) => Partial<ScheduleMilestone>) => () => {
      state.schedule = scheduleWith(
        id,
        {
          ...change(
            state.schedule.phases.flatMap((p) => p.milestones).find((m) => m.id === id) as never,
          ),
        },
        state.schedule,
      )
      return jsonResponse(200, state.schedule)
    },
  }
}

/** Há mais de uma região de aviso no painel; esta é a que já tem um aviso. */
export async function activeAlert(container: HTMLElement) {
  return waitFor(() => {
    const filled = within(container)
      .getAllByRole('alert')
      .find((region) => region.textContent !== '')
    if (!filled) throw new Error('Nenhum aviso ainda')
    return filled
  })
}

/** Abre o painel do marco pelo botão da lista e devolve o painel. */
export async function openMilestone(user: Renderer['user'], name: string) {
  await user.click(await screen.findByRole('button', { name }))
  return screen.findByRole('dialog', { name })
}
