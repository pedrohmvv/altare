import { z } from 'zod'
import type { ScheduleMilestone } from '../api/schedule'
import { copy } from '../copy'

const errors = copy.form.errors

/** O limite da API para a nota, e os anos que ela aceita no prazo (módulo `schedule`). */
export const MAX_NOTE = 500
const MIN_YEAR = 2000
const MAX_YEAR = 2100

function isRealDay(value: string): boolean {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value)
  if (!match) return false
  const [year, month, day] = [Number(match[1]), Number(match[2]), Number(match[3])]
  if (year < MIN_YEAR || year > MAX_YEAR) return false
  const date = new Date(Date.UTC(year, month - 1, day))
  return date.getUTCMonth() === month - 1 && date.getUTCDate() === day
}

/** O formulário do marco (F-CRN-05): responsável, prazo (só data, pode ficar vazio) e nota. */
export const milestoneSchema = z.object({
  responsible: z.enum(['Noivo', 'Noiva', 'Ambos']),
  target_date: z.string().refine((value) => value === '' || isRealDay(value), errors.targetInvalid),
  note: z.string().trim().max(MAX_NOTE, errors.noteTooLong(MAX_NOTE)),
})

export type MilestoneFormValues = z.infer<typeof milestoneSchema>

export function toFormValues(milestone: ScheduleMilestone): MilestoneFormValues {
  return {
    responsible: milestone.responsible,
    target_date: milestone.target_date ?? '',
    note: milestone.note ?? '',
  }
}

/** Em branco vira ausência, como a API também faz. */
export function toUpdateFields(values: MilestoneFormValues) {
  return {
    responsible: values.responsible,
    note: values.note.trim() === '' ? null : values.note.trim(),
    targetDate: values.target_date === '' ? null : values.target_date,
  }
}
