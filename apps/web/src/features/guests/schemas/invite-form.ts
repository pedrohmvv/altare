import { z } from 'zod'
import { INVITE_CHANNELS } from '../api/guests'
import { copy } from '../copy'

const errors = copy.invite.errors

/** Hoje em Brasília, como `AAAA-MM-DD`: o dia que o convite pode ter como limite (F-CNV-05). */
export function todayInBrazil(now: Date = new Date()): string {
  return now.toLocaleDateString('sv-SE', { timeZone: 'America/Sao_Paulo' })
}

/** O formulário do envio: data e canal são obrigatórios e a data não passa de hoje. */
export const makeInviteSchema = (today: string) =>
  z.object({
    sent_on: z
      .string()
      .regex(/^\d{4}-\d{2}-\d{2}$/, errors.date)
      .refine((value) => value <= today, errors.future),
    channel: z.string().refine((value) => INVITE_CHANNELS.some((c) => c === value), errors.channel),
  })

export type InviteFormValues = z.infer<ReturnType<typeof makeInviteSchema>>
