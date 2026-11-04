import { z } from 'zod'
import type { ScheduleTask } from '../api/schedule'
import { copy } from '../copy'
import { isRealDay, MAX_NOTE, MAX_TITLE } from './milestone-form'

const errors = copy.form.errors

/** O formulário da avulsa (F-CRN-06): título, responsável, prazo (só data) e nota. */
export const taskSchema = z.object({
  title: z
    .string()
    .trim()
    .min(1, copy.task.form.titleRequired)
    .max(MAX_TITLE, errors.tooLong(MAX_TITLE)),
  responsible: z.enum(['Noivo', 'Noiva', 'Ambos']),
  target_date: z.string().refine((value) => value === '' || isRealDay(value), errors.targetInvalid),
  note: z.string().trim().max(MAX_NOTE, errors.tooLong(MAX_NOTE)),
})

export type TaskFormValues = z.infer<typeof taskSchema>

export function toTaskFormValues(task: ScheduleTask): TaskFormValues {
  return {
    title: task.title,
    responsible: task.responsible,
    target_date: task.target_date ?? '',
    note: task.note ?? '',
  }
}

/** Em branco vira ausência, como a API também faz. */
export function toTaskFields(values: TaskFormValues) {
  return {
    title: values.title.trim(),
    responsible: values.responsible,
    note: values.note.trim() === '' ? null : values.note.trim(),
    targetDate: values.target_date === '' ? null : values.target_date,
  }
}
