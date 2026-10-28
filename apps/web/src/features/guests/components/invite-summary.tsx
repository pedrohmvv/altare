import { formatDay } from '@/lib/date'
import type { Household } from '../api/guests'
import { copy } from '../copy'

/** "Convite enviado em 20 out 2026 · WhatsApp"; núcleo sem envio não diz nada na lista (F-CNV-05). */
export function InviteSummary({ household }: { household: Household }) {
  if (household.invite_sent_on === null || household.invite_channel === null) return null
  return (
    <span className="text-body-sm text-ink-muted">
      {copy.invite.short(formatDay(household.invite_sent_on), household.invite_channel)}
    </span>
  )
}
