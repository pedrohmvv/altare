import { zodResolver } from '@hookform/resolvers/zod'
import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogTrigger } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { type GuestList, type GuestSettings, guestKeys } from '../api/guests'
import { useUpdateGuestSettings } from '../api/use-guest-mutations'
import { copy } from '../copy'
import { type FormAlertState, reportServerError } from '../lib/server-errors'
import {
  type SettingsFormValues,
  settingsSchema,
  toSettingsBody,
  toSettingsFormValues,
} from '../schemas/settings-form'
import { FormAlert } from './form-alert'

const labels = copy.settings

/** Os pesos por probabilidade e os limites de idade (F-CNV-03 e F-CNV-06): decisões do casal. */
export function GuestSettingsDialog({
  settings,
  trigger,
}: {
  settings: GuestSettings
  trigger: React.ReactNode
}) {
  const [open, setOpen] = useState(false)
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent title={labels.title} description={labels.description}>
        <SettingsEditor settings={settings} onDone={() => setOpen(false)} />
      </DialogContent>
    </Dialog>
  )
}

function SettingsEditor({ settings, onDone }: { settings: GuestSettings; onDone: () => void }) {
  // A versão que a pessoa viu ao abrir é a que vai no pedido: se o outro mudou no meio, a API
  // recusa (409) em vez de deixar um sobrescrever o outro.
  const [opened, setOpened] = useState(settings)
  const [alert, setAlert] = useState<FormAlertState | null>(null)
  const [reloading, setReloading] = useState(false)
  const update = useUpdateGuestSettings()
  const queryClient = useQueryClient()
  const form = useForm<SettingsFormValues>({
    resolver: zodResolver(settingsSchema),
    mode: 'onTouched',
    defaultValues: toSettingsFormValues(opened),
  })
  const { register, formState } = form
  const errors = formState.errors

  const submit = form.handleSubmit((values) => {
    setAlert(null)
    update.mutate(
      { ...toSettingsBody(values), version: opened.version },
      {
        onSuccess: onDone,
        onError: (error) => setAlert(reportServerError(error, form.setError, {})),
      },
    )
  })

  async function reload() {
    setReloading(true)
    await queryClient.refetchQueries({ queryKey: guestKeys.list })
    const latest = queryClient.getQueryData<GuestList>(guestKeys.list)?.settings
    setReloading(false)
    if (!latest) return onDone()
    setOpened(latest)
    form.reset(toSettingsFormValues(latest))
    setAlert(null)
  }

  return (
    <form onSubmit={submit} noValidate className="flex flex-col gap-6">
      <fieldset className="flex flex-col gap-4">
        <legend className="text-body font-medium text-ink">{labels.weightsLegend}</legend>
        <p className="-mt-2 text-body-sm text-ink-muted">{labels.weightsHint}</p>
        <div className="grid gap-4 sm:grid-cols-3">
          <Input
            label={labels.certain}
            suffix={labels.percent}
            inputMode="numeric"
            autoComplete="off"
            error={errors.certain?.message}
            {...register('certain')}
          />
          <Input
            label={labels.probable}
            suffix={labels.percent}
            inputMode="numeric"
            autoComplete="off"
            error={errors.probable?.message}
            {...register('probable')}
          />
          <Input
            label={labels.phase2}
            suffix={labels.percent}
            inputMode="numeric"
            autoComplete="off"
            error={errors.phase2?.message}
            {...register('phase2')}
          />
        </div>
      </fieldset>
      <fieldset className="flex flex-col gap-4">
        <legend className="text-body font-medium text-ink">{labels.agesLegend}</legend>
        <p className="-mt-2 text-body-sm text-ink-muted">{labels.agesHint}</p>
        <div className="grid gap-4 sm:grid-cols-2">
          <Input
            label={labels.exempt}
            suffix={labels.years}
            inputMode="numeric"
            autoComplete="off"
            error={errors.exempt?.message}
            {...register('exempt')}
          />
          <Input
            label={labels.paying}
            suffix={labels.years}
            inputMode="numeric"
            autoComplete="off"
            error={errors.paying?.message}
            {...register('paying')}
          />
        </div>
      </fieldset>
      <FormAlert alert={alert} onReload={() => void reload()} reloading={reloading} />
      <DialogFooter>
        <Button type="button" variant="ghost" onClick={onDone}>
          {labels.cancel}
        </Button>
        <Button type="submit" loading={update.isPending}>
          {labels.save}
        </Button>
      </DialogFooter>
    </form>
  )
}
