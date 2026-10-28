import { zodResolver } from '@hookform/resolvers/zod'
import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogTrigger } from '@/components/ui/dialog'
import { type GuestList, guestKeys, type Household } from '../api/guests'
import { useUpdateHousehold } from '../api/use-guest-mutations'
import { copy } from '../copy'
import { type FormAlertState, reportServerError } from '../lib/server-errors'
import {
  type HouseholdFormValues,
  householdSchema,
  toHouseholdBody,
  toHouseholdFormValues,
} from '../schemas/guest-forms'
import { FormAlert } from './form-alert'
import { HouseholdFields } from './household-fields'

const labels = copy.forms.editHousehold

/** Edita o nome, o lado, o endereço e a observação do núcleo (F-CNV-01). */
export function EditHouseholdDialog({ household }: { household: Household }) {
  const [open, setOpen] = useState(false)
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="secondary" size="sm">
          {labels.button}
        </Button>
      </DialogTrigger>
      <DialogContent title={labels.title} description={household.name}>
        <HouseholdEditor household={household} onDone={() => setOpen(false)} />
      </DialogContent>
    </Dialog>
  )
}

function HouseholdEditor({ household, onDone }: { household: Household; onDone: () => void }) {
  // A versão que a pessoa viu ao abrir é a que vai no pedido: se alguém mudou no meio, a API recusa
  // (409) em vez de deixar um sobrescrever o outro.
  const [opened, setOpened] = useState(household)
  const [alert, setAlert] = useState<FormAlertState | null>(null)
  const [reloading, setReloading] = useState(false)
  const update = useUpdateHousehold()
  const queryClient = useQueryClient()
  const form = useForm<HouseholdFormValues>({
    resolver: zodResolver(householdSchema),
    mode: 'onTouched',
    defaultValues: toHouseholdFormValues(opened),
  })

  const submit = form.handleSubmit((values) => {
    setAlert(null)
    update.mutate(
      { householdId: opened.id, household: toHouseholdBody(values), version: opened.version },
      {
        onSuccess: onDone,
        onError: (error) =>
          setAlert(reportServerError(error, form.setError, { duplicate_household_name: 'name' })),
      },
    )
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
    form.reset(toHouseholdFormValues(latest))
    setAlert(null)
  }

  return (
    <form onSubmit={submit} noValidate className="flex flex-col gap-6">
      <HouseholdFields form={form} />
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
