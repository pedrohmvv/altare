import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api/client'
import { unwrap } from '@/lib/api/errors'
import {
  type Responsible,
  SCHEDULE_WRITE_SCOPE,
  type Schedule,
  scheduleKeys,
  type TaskState,
} from './schedule'

/**
 * As escritas das avulsas seguem a regra das do marco: a resposta é o cronograma inteiro, vai direto
 * para o cache, e nada é otimista. Em erro, lê de novo.
 */
function useTaskWrite<Vars>(send: (vars: Vars) => Promise<Schedule>) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: send,
    scope: SCHEDULE_WRITE_SCOPE,
    onSuccess: (schedule) => queryClient.setQueryData(scheduleKeys.all, schedule),
    onError: () => void queryClient.invalidateQueries({ queryKey: scheduleKeys.all }),
  })
}

/**
 * O servidor não devolve o id da avulsa nova: quem chama acha o id comparando os ids de antes e de
 * depois (`newTaskId`). O responsável vai sempre: a tela o preenche com o perfil da sessão.
 */
export const useCreateTask = () =>
  useTaskWrite(
    async (v: {
      title: string
      responsible: Responsible
      note: string | null
      targetDate: string | null
    }) =>
      unwrap(
        await api.POST('/api/v1/schedule/tasks', {
          body: {
            title: v.title,
            responsible: v.responsible,
            note: v.note,
            target_date: v.targetDate,
          },
        }),
      ),
  )

/** O `PUT` é a substituição inteira dos campos editáveis. */
export const useUpdateTask = () =>
  useTaskWrite(
    async (v: {
      taskId: string
      title: string
      responsible: Responsible
      note: string | null
      targetDate: string | null
      /** A versão da avulsa que a tela viu. */
      version: number
    }) =>
      unwrap(
        await api.PUT('/api/v1/schedule/tasks/{task_id}', {
          params: { path: { task_id: v.taskId } },
          body: {
            title: v.title,
            responsible: v.responsible,
            note: v.note,
            target_date: v.targetDate,
            version: v.version,
          },
        }),
      ),
  )

export const useChangeTaskState = () =>
  useTaskWrite(
    async (v: { taskId: string; state: TaskState; ignoreOpenItems: boolean; version: number }) =>
      unwrap(
        await api.PUT('/api/v1/schedule/tasks/{task_id}/state', {
          params: { path: { task_id: v.taskId } },
          body: { state: v.state, ignore_open_items: v.ignoreOpenItems, version: v.version },
        }),
      ),
  )

export const useDeleteTask = () =>
  useTaskWrite(async (v: { taskId: string; version: number }) =>
    unwrap(
      await api.DELETE('/api/v1/schedule/tasks/{task_id}', {
        params: { path: { task_id: v.taskId }, query: { version: v.version } },
      }),
    ),
  )

export const useRestoreTask = () =>
  useTaskWrite(async (v: { taskId: string }) =>
    unwrap(
      await api.POST('/api/v1/schedule/tasks/{task_id}/restore', {
        params: { path: { task_id: v.taskId } },
      }),
    ),
  )
