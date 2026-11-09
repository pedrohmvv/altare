import { z } from 'zod'
import type { MilestoneWindow, WindowUnit } from '../api/schedule'
import { copy } from '../copy'

const errors = copy.window.errors

/** Os tetos da API (módulo `schedule`): 120 meses ou 520 semanas antes da data do casamento. */
export const MAX_WINDOW: Record<WindowUnit, number> = { meses: 120, semanas: 520 }

const WHOLE_NUMBER = /^\d+$/

/** O formulário do editor de janela (F-CRN-05, regra 5): início e fim em unidades antes da data. */
export const windowSchema = z
  .object({
    start_before: z.string(),
    end_before: z.string(),
    unit: z.enum(['meses', 'semanas']),
  })
  .superRefine((values, context) => {
    const max = MAX_WINDOW[values.unit]
    const parsed: Partial<Record<'start_before' | 'end_before', number>> = {}
    for (const path of ['start_before', 'end_before'] as const) {
      const text = values[path].trim()
      if (!WHOLE_NUMBER.test(text)) {
        context.addIssue({ code: 'custom', path: [path], message: errors.integer(max) })
      } else if (Number(text) > max) {
        context.addIssue({ code: 'custom', path: [path], message: errors.max(max, values.unit) })
      } else {
        parsed[path] = Number(text)
      }
    }
    // A ordem só se confere quando os dois números já valem: um erro por vez, no campo certo.
    const { start_before: start, end_before: end } = parsed
    if (start !== undefined && end !== undefined && start < end) {
      context.addIssue({ code: 'custom', path: ['start_before'], message: errors.order })
    }
  })

export type WindowFormValues = z.infer<typeof windowSchema>

/** Sem janela, o editor abre vazio e em meses, a unidade da sugestão genérica. */
export function toWindowFormValues(window: MilestoneWindow | null): WindowFormValues {
  return {
    start_before: window ? String(window.start_before) : '',
    end_before: window ? String(window.end_before) : '',
    unit: window?.unit ?? 'meses',
  }
}

/** O corpo do `PUT .../window` sem a versão: quem envia a põe. */
export function toWindowBody(values: WindowFormValues) {
  return {
    start_before: Number(values.start_before.trim()),
    end_before: Number(values.end_before.trim()),
    unit: values.unit,
  }
}
