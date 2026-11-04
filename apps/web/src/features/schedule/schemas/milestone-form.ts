import { z } from 'zod'
import type { ScheduleMilestone } from '../api/schedule'
import { copy } from '../copy'

const errors = copy.form.errors

/** Os limites da API (módulo `schedule`): título do marco, nota e os anos que o prazo aceita. */
export const MAX_TITLE = 120
export const MAX_NOTE = 500
const MIN_YEAR = 2000
const MAX_YEAR = 2100

/** O `Select` não aceita valor vazio: "sem categoria" tem um valor que nenhum id de categoria tem. */
export const NO_CATEGORY = 'sem-categoria'

function isRealDay(value: string): boolean {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value)
  if (!match) return false
  const [year, month, day] = [Number(match[1]), Number(match[2]), Number(match[3])]
  if (year < MIN_YEAR || year > MAX_YEAR) return false
  const date = new Date(Date.UTC(year, month - 1, day))
  return date.getUTCMonth() === month - 1 && date.getUTCDate() === day
}

export const milestoneTitleField = z
  .string()
  .trim()
  .min(1, errors.titleRequired)
  .max(MAX_TITLE, errors.tooLong(MAX_TITLE))

/** O formulário do marco (F-CRN-01, F-CRN-05): título, fase, categoria, responsável, prazo e nota. */
export const milestoneSchema = z.object({
  title: milestoneTitleField,
  phase_id: z.string().min(1),
  category_id: z.string().min(1),
  responsible: z.enum(['Noivo', 'Noiva', 'Ambos']),
  target_date: z.string().refine((value) => value === '' || isRealDay(value), errors.targetInvalid),
  note: z.string().trim().max(MAX_NOTE, errors.tooLong(MAX_NOTE)),
})

export type MilestoneFormValues = z.infer<typeof milestoneSchema>

export function toFormValues(milestone: ScheduleMilestone, phaseId: string): MilestoneFormValues {
  return {
    title: milestone.title,
    phase_id: phaseId,
    category_id: milestone.category?.id ?? NO_CATEGORY,
    responsible: milestone.responsible,
    target_date: milestone.target_date ?? '',
    note: milestone.note ?? '',
  }
}

/** Em branco vira ausência, como a API também faz; o `PUT` leva o marco inteiro. */
export function toUpdateFields(values: MilestoneFormValues) {
  return {
    title: values.title.trim(),
    phaseId: values.phase_id,
    categoryId: values.category_id === NO_CATEGORY ? null : values.category_id,
    responsible: values.responsible,
    note: values.note.trim() === '' ? null : values.note.trim(),
    targetDate: values.target_date === '' ? null : values.target_date,
  }
}

/** O formulário de um marco novo (F-CRN-01): título obrigatório, fase, responsável e categoria. */
export const newMilestoneSchema = z.object({
  title: milestoneTitleField,
  phase_id: z.string().min(1),
  responsible: z.enum(['Noivo', 'Noiva', 'Ambos']),
  category_id: z.string().min(1),
})

export type NewMilestoneFormValues = z.infer<typeof newMilestoneSchema>

/** O limite da API para o nome de uma fase. */
export const MAX_PHASE_TITLE = 60

/** O nome de uma fase (F-CRN-01): obrigatório, aparado, até 60 caracteres. */
export const phaseTitleSchema = z.object({
  title: z
    .string()
    .trim()
    .min(1, copy.phases.errors.titleRequired)
    .max(MAX_PHASE_TITLE, copy.phases.errors.tooLong(MAX_PHASE_TITLE)),
})

export type PhaseTitleValues = z.infer<typeof phaseTitleSchema>
