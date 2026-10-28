import type { Household } from '../api/guests'
import { displayName } from '../lib/names'
import { summaryText } from '../lib/summary'
import { SideBadge } from './guest-badges'
import { InviteSummary } from './invite-summary'
import { StatusControl } from './status-control'
import { WhatsAppButton } from './whatsapp-button'

/**
 * No celular, um cartão por núcleo (F-CNV-07): o nome abre o painel (o botão cobre o cartão), e cada
 * pessoa mostra o status e o WhatsApp em um toque, acima da área que abre o painel.
 */
export function HouseholdCard({
  household,
  onOpen,
}: {
  household: Household
  onOpen: (householdId: string, opener: HTMLElement) => void
}) {
  return (
    <li className="relative flex flex-col gap-3 rounded-card border border-border bg-surface p-4 transition-colors duration-fast ease-standard hover:border-border-strong">
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-name text-ink">
          <button
            type="button"
            onClick={(event) => onOpen(household.id, event.currentTarget)}
            className="text-left after:absolute after:inset-0 after:rounded-card"
          >
            {household.name}
          </button>
        </h3>
        <SideBadge side={household.side} />
      </div>
      <p className="text-body-sm text-ink-muted">{summaryText(household.summary)}</p>
      <InviteSummary household={household} />
      <ul className="flex flex-col gap-3">
        {household.guests.map((guest) => {
          const name = displayName(guest)
          return (
            <li
              key={guest.id}
              className="flex flex-col gap-2 border-t border-border pt-3 first:border-t-0 first:pt-0"
            >
              <p className="text-body text-ink">{name}</p>
              <div className="flex flex-wrap items-center gap-2">
                <StatusControl guest={guest} name={name} />
                <WhatsAppButton url={guest.whatsapp_url} name={name} />
              </div>
            </li>
          )
        })}
      </ul>
    </li>
  )
}
