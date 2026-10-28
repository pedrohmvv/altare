import { zodResolver } from '@hookform/resolvers/zod'
import { useQueryClient } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { type GuestList, guestKeys, type Household, INVITE_CHANNELS } from '../api/guests'
import { useRecordHouseholdInvite } from '../api/use-guest-mutations'
import { copy } from '../copy'
import { alertFromError, type FormAlertState } from '../lib/server-errors'
import { type InviteFormValues, makeInviteSchema, todayInBrazil } from '../schemas/invite-form'
import { FormAlert } from './form-alert'

const labels = copy.invite

/**
 * Registra ou edita o envio do convite do núcleo (F-CNV-05). Se há pessoas em `Rascunho`, o
 * sistema **oferece** movê-las para `Convidado`, com uma confirmação: nunca é automático, e quem
 * recusa mantém todos os status como estão.
 */
export function InviteDialog({ household }: { household: Household }) {
  const [open, setOpen] = useState(false)
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="secondary" size="sm">
          {household.invite_sent_on ? labels.edit : labels.record}
        </Button>
      </DialogTrigger>
      <DialogContent title={labels.title} description={labels.description}>
        <InviteEditor household={household} onDone={() => setOpen(false)} />
      </DialogContent>
    </Dialog>
  )
}

function InviteEditor({ household, onDone }: { household: Household; onDone: () => void }) {
  // A versão que a pessoa viu ao abrir é a que vai no pedido (409 se o outro mudou o núcleo).
  const [opened, setOpened] = useState(household)
  const [pending, setPending] = useState<InviteFormValues | null>(null)
  const [alert, setAlert] = useState<FormAlertState | null>(null)
  const [reloading, setReloading] = useState(false)
  const record = useRecordHouseholdInvite()
  const queryClient = useQueryClient()
  const today = todayInBrazil()
  const schema = useMemo(() => makeInviteSchema(today), [today])
  const form = useForm<InviteFormValues>({
    resolver: zodResolver(schema),
    mode: 'onTouched',
    defaultValues: {
      sent_on: opened.invite_sent_on ?? today,
      channel: opened.invite_channel ?? '',
    },
  })
  const { register, control, formState } = form
  const drafts = opened.guests.filter((guest) => guest.status === 'Rascunho').length

  function send(values: InviteFormValues, moveDrafts: boolean) {
    const channel = INVITE_CHANNELS.find((candidate) => candidate === values.channel)
    if (!channel) return
    setAlert(null)
    record.mutate(
      {
        householdId: opened.id,
        sentOn: values.sent_on,
        channel,
        moveDrafts,
        version: opened.version,
      },
      {
        onSuccess: onDone,
        onError: (error) => {
          setPending(null)
          setAlert(alertFromError(error))
        },
      },
    )
  }

  const submit = form.handleSubmit((values) => {
    if (drafts > 0) setPending(values)
    else send(values, false)
  })

  async function reload() {
    setReloading(true)
    await queryClient.refetchQueries({ queryKey: guestKeys.list })
    const latest = queryClient
      .getQueryData<GuestList>(guestKeys.list)
      ?.households.find((candidate) => candidate.id === opened.id)
    setReloading(false)
    if (!latest) return onDone()
    setOpened(latest)
    form.reset({
      sent_on: latest.invite_sent_on ?? today,
      channel: latest.invite_channel ?? '',
    })
    setAlert(null)
  }

  if (pending) {
    return (
      <div className="flex flex-col gap-4">
        <h3 className="text-body font-semibold text-ink">{labels.offer.title}</h3>
        <p className="text-body text-ink">{labels.offer.description(drafts)}</p>
        <FormAlert alert={alert} />
        <DialogFooter>
          <Button variant="ghost" onClick={() => send(pending, false)} disabled={record.isPending}>
            {labels.offer.keep}
          </Button>
          <Button onClick={() => send(pending, true)} loading={record.isPending}>
            {labels.offer.move}
          </Button>
        </DialogFooter>
      </div>
    )
  }

  return (
    <form onSubmit={submit} noValidate className="flex flex-col gap-4">
      <Input
        label={labels.date}
        hint={labels.dateHint}
        type="date"
        max={today}
        error={formState.errors.sent_on?.message}
        {...register('sent_on')}
      />
      <Controller
        control={control}
        name="channel"
        render={({ field }) => (
          <Select
            label={labels.channel}
            placeholder={labels.channelPlaceholder}
            options={INVITE_CHANNELS.map((channel) => ({ value: channel, label: channel }))}
            value={field.value}
            onValueChange={field.onChange}
            error={formState.errors.channel?.message}
          />
        )}
      />
      <FormAlert alert={alert} onReload={() => void reload()} reloading={reloading} />
      <DialogFooter>
        <Button type="button" variant="ghost" onClick={onDone}>
          {labels.cancel}
        </Button>
        <Button type="submit" loading={record.isPending}>
          {labels.save}
        </Button>
      </DialogFooter>
    </form>
  )
}
