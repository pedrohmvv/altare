import { zodResolver } from '@hookform/resolvers/zod'
import { useQueryClient } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogTrigger } from '@/components/ui/dialog'
import { type Guest, type GuestList, guestKeys } from '../api/guests'
import { useUpdateGuest } from '../api/use-guest-mutations'
import { copy } from '../copy'
import { displayName } from '../lib/names'
import { type FormAlertState, reportServerError } from '../lib/server-errors'
import {
  type GuestFormValues,
  makeGuestSchema,
  toDeclineReason,
  toGuestBody,
  toGuestFormValues,
} from '../schemas/guest-forms'
import { FormAlert } from './form-alert'
import { GuestFields } from './guest-fields'

const labels = copy.forms.editGuest

/** Edita uma pessoa; o nome só pode ficar vazio no acompanhante a confirmar (F-CNV-02). */
export function EditGuestDialog({ guest }: { guest: Guest }) {
  const [open, setOpen] = useState(false)
  const name = displayName(guest)
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" aria-label={labels.button(name)}>
          {labels.short}
        </Button>
      </DialogTrigger>
      <DialogContent title={labels.title} description={name}>
        <GuestEditor guest={guest} onDone={() => setOpen(false)} />
      </DialogContent>
    </Dialog>
  )
}

function GuestEditor({ guest, onDone }: { guest: Guest; onDone: () => void }) {
  const [opened, setOpened] = useState(guest)
  const [alert, setAlert] = useState<FormAlertState | null>(null)
  const [reloading, setReloading] = useState(false)
  const update = useUpdateGuest()
  const queryClient = useQueryClient()
  const companion = opened.companion_of_id !== null
  const schema = useMemo(() => makeGuestSchema({ nameRequired: !companion }), [companion])
  const form = useForm<GuestFormValues>({
    resolver: zodResolver(schema),
    mode: 'onTouched',
    defaultValues: toGuestFormValues(opened),
  })

  const submit = form.handleSubmit((values) => {
    setAlert(null)
    update.mutate(
      {
        guestId: opened.id,
        guest: toGuestBody(values),
        declineReason: opened.status === 'Não irá' ? toDeclineReason(values) : null,
        version: opened.version,
      },
      {
        onSuccess: onDone,
        onError: (error) =>
          setAlert(
            reportServerError(error, form.setError, {
              guest_name_required: 'name',
              invalid_phone: 'phone',
              invalid_email: 'email',
            }),
          ),
      },
    )
  })

  async function reload() {
    setReloading(true)
    await queryClient.refetchQueries({ queryKey: guestKeys.list })
    const latest = queryClient
      .getQueryData<GuestList>(guestKeys.list)
      ?.households.flatMap((household) => household.guests)
      .find((candidate) => candidate.id === opened.id)
    setReloading(false)
    if (!latest) return onDone()
    setOpened(latest)
    form.reset(toGuestFormValues(latest))
    setAlert(null)
  }

  return (
    <form onSubmit={submit} noValidate className="flex flex-col gap-6">
      <GuestFields
        form={form}
        companion={companion}
        showDeclineReason={opened.status === 'Não irá'}
      />
      <FormAlert alert={alert} onReload={() => void reload()} reloading={reloading} />
      <DialogFooter>
        <Button type="button" variant="ghost" onClick={onDone}>
          {copy.forms.cancel}
        </Button>
        <Button type="submit" loading={update.isPending}>
          {labels.save}
        </Button>
      </DialogFooter>
    </form>
  )
}
