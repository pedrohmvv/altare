import { zodResolver } from '@hookform/resolvers/zod'
import { useQueryClient } from '@tanstack/react-query'
import { type ReactNode, useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogTrigger } from '@/components/ui/dialog'
import { type GuestList, guestKeys } from '../api/guests'
import { useCreateHousehold } from '../api/use-guest-mutations'
import { copy } from '../copy'
import { type FormAlertState, reportServerError } from '../lib/server-errors'
import {
  EMPTY_GUEST,
  EMPTY_HOUSEHOLD,
  type GuestFormValues,
  type HouseholdFormValues,
  householdSchema,
  makeGuestSchema,
  toGuestBody,
  toHouseholdBody,
} from '../schemas/guest-forms'
import { FormAlert } from './form-alert'
import { GuestFields } from './guest-fields'
import { GuestSequence } from './guest-sequence'
import { HouseholdFields } from './household-fields'

const labels = copy.forms.newHousehold

/**
 * Cria o núcleo com a primeira pessoa e, em seguida, continua aberto para as demais (F-CNV-01,
 * regra 3): é um fluxo contínuo, sem voltar à lista. Envolve a tela inteira, e os gatilhos
 * (`NewHouseholdTrigger`) ficam dentro dela: assim o diálogo não é desmontado quando a lista vazia
 * ganha o primeiro núcleo, e o foco volta ao gatilho que o abriu.
 */
export function NewHouseholdDialog({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false)
  const [created, setCreated] = useState<{ id: string; name: string } | null>(null)
  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next)
        if (!next) setCreated(null)
      }}
    >
      {children}
      <DialogContent
        title={created ? copy.forms.sequence.title(created.name) : labels.title}
        description={created ? copy.forms.sequence.description : labels.description}
      >
        {created ? (
          <GuestSequence householdId={created.id} onDone={() => setOpen(false)} />
        ) : (
          <CreateForm onCreated={setCreated} onCancel={() => setOpen(false)} />
        )}
      </DialogContent>
    </Dialog>
  )
}

function CreateForm({
  onCreated,
  onCancel,
}: {
  onCreated: (created: { id: string; name: string }) => void
  onCancel: () => void
}) {
  const create = useCreateHousehold()
  const queryClient = useQueryClient()
  const [alert, setAlert] = useState<FormAlertState | null>(null)
  const guestSchema = useMemo(() => makeGuestSchema({ nameRequired: true }), [])
  const householdForm = useForm<HouseholdFormValues>({
    resolver: zodResolver(householdSchema),
    mode: 'onTouched',
    defaultValues: EMPTY_HOUSEHOLD,
  })
  const guestForm = useForm<GuestFormValues>({
    resolver: zodResolver(guestSchema),
    mode: 'onTouched',
    defaultValues: EMPTY_GUEST,
  })

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    const householdOk = await householdForm.trigger(undefined, { shouldFocus: true })
    const guestOk = await guestForm.trigger(undefined, { shouldFocus: householdOk })
    if (!householdOk || !guestOk) return
    setAlert(null)
    const knownIds = new Set(
      queryClient.getQueryData<GuestList>(guestKeys.list)?.households.map((h) => h.id),
    )
    create.mutate(
      {
        household: toHouseholdBody(householdForm.getValues()),
        firstGuest: toGuestBody(guestForm.getValues()),
      },
      {
        onSuccess: (list) => {
          const made = list.households.find((household) => !knownIds.has(household.id))
          if (made) onCreated({ id: made.id, name: made.name })
          else onCancel()
        },
        onError: (error) => {
          const handled = reportServerError(error, householdForm.setError, {
            duplicate_household_name: 'name',
          })
          if (handled?.kind === 'error') {
            setAlert(
              reportServerError(error, guestForm.setError, {
                guest_name_required: 'name',
                invalid_phone: 'phone',
                invalid_email: 'email',
              }),
            )
          } else {
            setAlert(handled)
          }
        },
      },
    )
  }

  return (
    <form onSubmit={submit} noValidate className="flex flex-col gap-6">
      <section aria-label={labels.household} className="flex flex-col gap-3">
        <h3 className="text-body font-semibold text-ink">{labels.household}</h3>
        <HouseholdFields form={householdForm} />
      </section>
      <section aria-label={labels.firstGuest} className="flex flex-col gap-3">
        <h3 className="text-body font-semibold text-ink">{labels.firstGuest}</h3>
        <GuestFields form={guestForm} />
      </section>
      <FormAlert alert={alert} />
      <DialogFooter>
        <Button type="button" variant="ghost" onClick={onCancel}>
          {labels.cancel}
        </Button>
        <Button type="submit" loading={create.isPending}>
          {labels.create}
        </Button>
      </DialogFooter>
    </form>
  )
}

export function NewHouseholdTrigger() {
  return (
    <DialogTrigger asChild>
      <Button>{labels.button}</Button>
    </DialogTrigger>
  )
}
