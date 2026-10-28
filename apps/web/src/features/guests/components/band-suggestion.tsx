import { useState } from 'react'
import { Button } from '@/components/ui/button'
import type { Guest } from '../api/guests'
import { useUpdateGuest } from '../api/use-guest-mutations'
import { copy } from '../copy'
import { alertFromError, type FormAlertState } from '../lib/server-errors'
import { toGuestBody, toGuestFormValues } from '../schemas/guest-forms'
import { FormAlert } from './form-alert'

const labels = copy.suggestion

/**
 * A faixa que a idade sugere (F-CNV-03, regra 3): um aviso com um toque para aplicar e outro para
 * manter a faixa atual. Nunca muda a faixa sozinho. Aplicar "Adulto" tira a idade, que só vale para
 * criança.
 */
export function BandSuggestion({ guest, name }: { guest: Guest; name: string }) {
  const [dismissed, setDismissed] = useState(false)
  const [alert, setAlert] = useState<FormAlertState | null>(null)
  const update = useUpdateGuest()
  const band = guest.suggested_band
  if (band === null || guest.age === null || dismissed) return null

  function apply(target: NonNullable<Guest['suggested_band']>) {
    setAlert(null)
    const values = toGuestFormValues(guest)
    const body = toGuestBody({
      ...values,
      band: target,
      age: target === 'Adulto' ? '' : values.age,
    })
    update.mutate(
      {
        guestId: guest.id,
        guest: body,
        declineReason: guest.decline_reason,
        version: guest.version,
      },
      { onError: (error) => setAlert(alertFromError(error)) },
    )
  }

  return (
    <div className="flex flex-col gap-2 rounded-control bg-surface-muted px-3 py-2.5">
      <p className="text-body-sm text-ink">{labels.byAge(guest.age, copy.bands[band])}</p>
      <div className="flex flex-wrap gap-2">
        <Button
          size="sm"
          variant="secondary"
          aria-label={labels.applyFor(name, copy.bands[band])}
          loading={update.isPending}
          onClick={() => apply(band)}
        >
          {labels.apply}
        </Button>
        <Button
          size="sm"
          variant="ghost"
          aria-label={labels.keepFor(name)}
          onClick={() => setDismissed(true)}
        >
          {labels.keep}
        </Button>
      </div>
      <FormAlert alert={alert} />
    </div>
  )
}
