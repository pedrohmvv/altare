import { Sheet, SheetContent } from '@/components/ui/sheet'
import type { Guest, Household } from '../api/guests'
import { copy } from '../copy'
import { addressLines } from '../lib/address'
import { displayName } from '../lib/names'
import { summaryText } from '../lib/summary'
import { GuestStatusBadge } from './guest-badges'
import { WhatsAppButton } from './whatsapp-button'

export interface HouseholdSheetProps {
  household: Household
  open: boolean
  onOpenChange: (open: boolean) => void
  /** O painel abre pela URL, sem gatilho: quem abriu diz para onde o foco volta ao fechar. */
  onCloseAutoFocus?: (event: Event) => void
}

/** O detalhe do núcleo sem sair da lista (design-system.md §10, item 2). */
export function HouseholdSheet({
  household,
  open,
  onOpenChange,
  onCloseAutoFocus,
}: HouseholdSheetProps) {
  const lines = addressLines(household)
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        title={household.name}
        description={copy.sheet.description(household.side, summaryText(household.summary))}
        onCloseAutoFocus={onCloseAutoFocus}
      >
        <section aria-label={copy.sheet.people} className="flex flex-col gap-3">
          <h3 className="text-body font-semibold text-ink">{copy.sheet.people}</h3>
          <ul className="flex flex-col">
            {household.guests.map((guest) => (
              <GuestDetails key={guest.id} guest={guest} />
            ))}
          </ul>
        </section>
        <section aria-label={copy.sheet.address} className="flex flex-col gap-2">
          <h3 className="text-body font-semibold text-ink">{copy.sheet.address}</h3>
          {lines.length === 0 ? (
            <p className="text-body-sm text-ink-muted">{copy.sheet.noAddress}</p>
          ) : (
            <address className="text-body-sm text-ink not-italic">
              {lines.map((line) => (
                <span key={line} className="block">
                  {line}
                </span>
              ))}
            </address>
          )}
        </section>
        {household.note && (
          <section aria-label={copy.sheet.note} className="flex flex-col gap-2">
            <h3 className="text-body font-semibold text-ink">{copy.sheet.note}</h3>
            <p className="text-body-sm text-ink">{household.note}</p>
          </section>
        )}
      </SheetContent>
    </Sheet>
  )
}

function GuestDetails({ guest }: { guest: Guest }) {
  const name = displayName(guest)
  const facts = [
    copy.bands[guest.band],
    guest.age === null ? null : copy.sheet.age(guest.age),
    copy.probabilities[guest.probability],
  ].filter(Boolean)
  return (
    <li className="flex flex-col gap-2 border-t border-border py-3 first:border-t-0 first:pt-0">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-body font-medium text-ink">{name}</p>
        <GuestStatusBadge status={guest.status} />
      </div>
      {guest.name && guest.holder_name && (
        <p className="text-ui-sm text-ink-muted">{copy.companion.of(guest.holder_name)}</p>
      )}
      <p className="text-body-sm text-ink-muted">{facts.join(' · ')}</p>
      <dl className="flex flex-col gap-1 text-body-sm">
        {guest.decline_reason && (
          <Fact label={copy.sheet.declineReason} value={guest.decline_reason} />
        )}
        {guest.dietary_restriction && (
          <Fact label={copy.sheet.dietary} value={guest.dietary_restriction} />
        )}
        {guest.phone && <Fact label={copy.sheet.phone} value={guest.phone} />}
        {guest.email && <Fact label={copy.sheet.email} value={guest.email} />}
        {guest.note && <Fact label={copy.sheet.personNote} value={guest.note} />}
      </dl>
      <div>
        <WhatsAppButton url={guest.whatsapp_url} name={name} />
      </div>
    </li>
  )
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-wrap gap-x-2">
      <dt className="text-ink-muted">{label}:</dt>
      <dd className="text-ink">{value}</dd>
    </div>
  )
}
