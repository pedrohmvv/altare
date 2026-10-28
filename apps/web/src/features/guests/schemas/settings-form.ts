import { z } from 'zod'
import type { GuestSettings } from '../api/guests'
import { copy } from '../copy'

const errors = copy.settings.errors

/** Tudo em texto, porque é o que o campo guarda; o `superRefine` confere e o corpo converte. */
const shape = z.object({
  certain: z.string().trim(),
  probable: z.string().trim(),
  phase2: z.string().trim(),
  exempt: z.string().trim(),
  paying: z.string().trim(),
})

export type SettingsFormValues = z.infer<typeof shape>
type Path = keyof SettingsFormValues

const isInt = (text: string, max: number) => /^\d{1,3}$/.test(text) && Number(text) <= max

export const settingsSchema = shape.superRefine((values, context) => {
  const report = (path: Path, message: string) =>
    context.addIssue({ code: 'custom', path: [path], message })

  const weights: [Path, string][] = [
    ['certain', values.certain],
    ['probable', values.probable],
    ['phase2', values.phase2],
  ]
  const filled = weights.filter(([, text]) => text !== '')
  if (filled.length > 0 && filled.length < weights.length) {
    for (const [path, text] of weights) if (text === '') report(path, errors.weightsTogether)
  }
  for (const [path, text] of filled) if (!isInt(text, 100)) report(path, errors.weight)

  for (const [path, text] of [
    ['exempt', values.exempt],
    ['paying', values.paying],
  ] as [Path, string][]) {
    if (text !== '' && !isInt(text, 17)) report(path, errors.age)
  }
  if (
    isInt(values.exempt, 17) &&
    isInt(values.paying, 17) &&
    Number(values.exempt) > Number(values.paying)
  ) {
    report('exempt', errors.order)
  }
})

const orEmpty = (value: number | null) => (value === null ? '' : String(value))

export function toSettingsFormValues(settings: GuestSettings): SettingsFormValues {
  return {
    certain: orEmpty(settings.weights?.certain_pct ?? null),
    probable: orEmpty(settings.weights?.probable_pct ?? null),
    phase2: orEmpty(settings.weights?.phase_2_pct ?? null),
    exempt: orEmpty(settings.exempt_until_age),
    paying: orEmpty(settings.paying_until_age),
  }
}

/** O corpo da API: os três pesos juntos ou nenhum, e vazio vira nulo. */
export function toSettingsBody(values: SettingsFormValues) {
  const hasWeights = values.certain !== ''
  return {
    weights: hasWeights
      ? {
          certain_pct: Number(values.certain),
          probable_pct: Number(values.probable),
          phase_2_pct: Number(values.phase2),
        }
      : null,
    exemptUntilAge: values.exempt === '' ? null : Number(values.exempt),
    payingUntilAge: values.paying === '' ? null : Number(values.paying),
  }
}
