import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent } from '@/components/ui/sheet'
import { formatDay } from '@/lib/date'
import type { Guest, Household } from '../api/guests'
import {
  useAddCompanion,
  useClearHouseholdInvite,
  useRestoreGuest,
} from '../api/use-guest-mutations'
import { copy } from '../copy'
import { addressLines } from '../lib/address'
import { displayName } from '../lib/names'
import { summaryText } from '../lib/summary'
import { AddGuestDialog } from './add-guest-dialog'
import { BandSuggestion } from './band-suggestion'
import { DeleteGuestDialog } from './delete-guest-dialog'
import { DeleteHouseholdDialog } from './delete-household-dialog'
import { EditGuestDialog } from './edit-guest-dialog'
import { EditHouseholdDialog } from './edit-household-dialog'
import { GuestHistory } from './guest-history'
import { InviteDialog } from './invite-dialog'
import { MoveGuestDialog } from './move-guest-dialog'
import { StatusControl } from './status-control'
import { WhatsAppButton } from './whatsapp-button'

export interface HouseholdSheetProps {
  household: Household
  /** Os outros núcleos, para onde uma pessoa pode ir. */
  others: readonly Pick<Household, 'id' | 'name'>[]
  open: boolean
  onOpenChange: (open: boolean) => void
  /** O painel abre pela URL, sem gatilho: quem abriu diz para onde o foco volta ao fechar. */
  onCloseAutoFocus?: (event: Event) => void
}

/** O detalhe do núcleo sem sair da lista (design-system.md §10, item 2). */
export function HouseholdSheet({
  household,
  others,
  open,
  onOpenChange,
  onCloseAutoFocus,
}: HouseholdSheetProps) {
  const lines = addressLines(household)
  const [removed, setRemoved] = useState<{ guestId: string; name: string } | null>(null)
  return (
    <Sheet
      open={open}
      onOpenChange={(next) => {
        if (!next) setRemoved(null)
        onOpenChange(next)
      }}
    >
      <SheetContent
        title={household.name}
        description={copy.sheet.description(household.side, summaryText(household.summary))}
        onCloseAutoFocus={onCloseAutoFocus}
      >
        <div className="flex flex-wrap gap-3">
          <EditHouseholdDialog household={household} />
          <AddGuestDialog householdId={household.id} householdName={household.name} />
          <DeleteHouseholdDialog household={household} onDeleted={() => onOpenChange(false)} />
        </div>
        <RemovedNotice removed={removed} onDone={() => setRemoved(null)} />
        <section aria-label={copy.sheet.people} className="flex flex-col gap-3">
          <h3 className="text-body font-semibold text-ink">{copy.sheet.people}</h3>
          <ul className="flex flex-col">
            {household.guests.map((guest) => (
              <GuestDetails
                key={guest.id}
                guest={guest}
                companion={household.guests.find((other) => other.companion_of_id === guest.id)}
                others={others}
                onRemoved={setRemoved}
              />
            ))}
          </ul>
        </section>
        <InviteSection household={household} />
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

function GuestDetails({
  guest,
  companion,
  others,
  onRemoved,
}: {
  guest: Guest
  companion?: Guest
  others: readonly Pick<Household, 'id' | 'name'>[]
  onRemoved: (removed: { guestId: string; name: string }) => void
}) {
  const name = displayName(guest)
  const addCompanion = useAddCompanion()
  const facts = [
    copy.bands[guest.band],
    guest.age === null ? null : copy.sheet.age(guest.age),
    copy.probabilities[guest.probability],
  ].filter(Boolean)
  return (
    <li className="flex flex-col gap-2 border-t border-border py-3 first:border-t-0 first:pt-0">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-body font-medium text-ink">{name}</p>
        <StatusControl guest={guest} name={name} />
      </div>
      {guest.name && guest.holder_name && (
        <p className="text-ui-sm text-ink-muted">{copy.companion.of(guest.holder_name)}</p>
      )}
      <p className="text-body-sm text-ink-muted">{facts.join(' · ')}</p>
      <BandSuggestion guest={guest} name={name} />
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
      <div className="flex flex-wrap items-center gap-2">
        <WhatsAppButton url={guest.whatsapp_url} name={name} />
        <EditGuestDialog guest={guest} />
        {guest.companion_of_id === null && !companion && (
          <Button
            variant="ghost"
            size="sm"
            loading={addCompanion.isPending}
            onClick={() => addCompanion.mutate({ holderId: guest.id })}
          >
            {copy.forms.addCompanion.button}
          </Button>
        )}
        <MoveGuestDialog guest={guest} destinations={others} />
        <DeleteGuestDialog guest={guest} companion={companion} onRemoved={onRemoved} />
      </div>
      <GuestHistory guestId={guest.id} />
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

/** O aviso de exclusão com o Desfazer, dentro do painel: fica até a pessoa agir ou fechar o painel. */
function RemovedNotice({
  removed,
  onDone,
}: {
  removed: { guestId: string; name: string } | null
  onDone: () => void
}) {
  const restore = useRestoreGuest()
  return (
    <div role="status">
      {removed && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-control bg-surface-muted px-3 py-2.5 text-body-sm text-ink">
          <p>{copy.remove.guestDone(removed.name)}</p>
          <Button
            variant="secondary"
            size="sm"
            loading={restore.isPending}
            onClick={() => restore.mutate({ guestId: removed.guestId }, { onSuccess: onDone })}
          >
            {copy.remove.undo}
          </Button>
        </div>
      )}
    </div>
  )
}

/** O convite do núcleo (F-CNV-05): quando e como foi enviado, ou que ainda não foi. */
function InviteSection({ household }: { household: Household }) {
  const clear = useClearHouseholdInvite()
  const sent = household.invite_sent_on !== null && household.invite_channel !== null
  return (
    <section aria-label={copy.invite.section} className="flex flex-col gap-2">
      <h3 className="text-body font-semibold text-ink">{copy.invite.section}</h3>
      <p className="text-body-sm text-ink">
        {sent && household.invite_sent_on && household.invite_channel
          ? copy.invite.sent(formatDay(household.invite_sent_on), household.invite_channel)
          : copy.invite.notSent}
      </p>
      <div className="flex flex-wrap gap-2">
        <InviteDialog household={household} />
        {sent && (
          <Button
            variant="ghost"
            size="sm"
            loading={clear.isPending}
            onClick={() => clear.mutate({ householdId: household.id, version: household.version })}
          >
            {copy.invite.clear}
          </Button>
        )}
      </div>
    </section>
  )
}
