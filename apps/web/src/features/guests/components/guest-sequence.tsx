import { zodResolver } from '@hookform/resolvers/zod'
import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { DialogFooter } from '@/components/ui/dialog'
import { guestListQueryOptions } from '../api/guests'
import { useAddGuest } from '../api/use-guest-mutations'
import { copy } from '../copy'
import { displayName } from '../lib/names'
import { type FormAlertState, reportServerError } from '../lib/server-errors'
import {
  EMPTY_GUEST,
  type GuestFormValues,
  makeGuestSchema,
  toGuestBody,
} from '../schemas/guest-forms'
import { FormAlert } from './form-alert'
import { GuestFields } from './guest-fields'

const labels = copy.forms.sequence

/**
 * O cadastro rápido (F-CNV-01, regra 3): o formulário da pessoa continua aberto depois de cada
 * inclusão, com o foco de volta ao nome, até quem cadastra concluir. Cada pessoa nova é anunciada.
 */
export function GuestSequence({
  householdId,
  onDone,
}: {
  householdId: string
  onDone: () => void
}) {
  const list = useQuery(guestListQueryOptions)
  const members =
    list.data?.households.find((household) => household.id === householdId)?.guests ?? []
  const add = useAddGuest()
  const [alert, setAlert] = useState<FormAlertState | null>(null)
  const [announcement, setAnnouncement] = useState('')
  const schema = useMemo(() => makeGuestSchema({ nameRequired: true }), [])
  const form = useForm<GuestFormValues>({
    resolver: zodResolver(schema),
    mode: 'onTouched',
    defaultValues: EMPTY_GUEST,
  })

  const submit = form.handleSubmit((values) => {
    setAlert(null)
    add.mutate(
      { householdId, guest: toGuestBody(values) },
      {
        onSuccess: () => {
          setAnnouncement(labels.added(values.name.trim()))
          form.reset(EMPTY_GUEST)
          // O botão de enviar estava ocupado e perdeu o foco: devolve-o ao nome depois da pintura.
          setTimeout(() => form.setFocus('name'), 0)
        },
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

  return (
    <form onSubmit={submit} noValidate className="flex flex-col gap-4">
      {members.length > 0 && (
        <section aria-label={labels.inside} className="flex flex-col gap-1">
          <h3 className="text-body font-medium text-ink">{labels.inside}</h3>
          <ul className="text-body-sm text-ink-muted">
            {members.map((member) => (
              <li key={member.id}>{displayName(member)}</li>
            ))}
          </ul>
        </section>
      )}
      <GuestFields form={form} />
      <FormAlert alert={alert} />
      <p role="status" className="text-body-sm text-consensus-ink">
        {announcement}
      </p>
      <DialogFooter>
        <Button type="button" variant="ghost" onClick={onDone}>
          {labels.done}
        </Button>
        <Button type="submit" loading={add.isPending}>
          {labels.add}
        </Button>
      </DialogFooter>
    </form>
  )
}
