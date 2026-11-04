import { z } from 'zod'
import { copy } from '../copy'

/** O limite da API para o texto de um item do checklist. */
export const MAX_ITEM_TEXT = 200

const errors = copy.checklist.errors

/** O texto de um item (F-CRN-07): obrigatório, aparado, até 200 caracteres. */
export const checklistTextSchema = z.object({
  text: z
    .string()
    .trim()
    .min(1, errors.textRequired)
    .max(MAX_ITEM_TEXT, errors.tooLong(MAX_ITEM_TEXT)),
})

export type ChecklistTextValues = z.infer<typeof checklistTextSchema>
