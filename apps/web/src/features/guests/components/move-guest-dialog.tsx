import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogTrigger } from '@/components/ui/dialog'
import { Select } from '@/components/ui/select'
import type { Guest, Household } from '../api/guests'
import { useMoveGuest } from '../api/use-guest-mutations'
import { copy } from '../copy'
import { displayName } from '../lib/names'
import { alertFromError, type FormAlertState } from '../lib/server-errors'
import { FormAlert } from './form-alert'

const labels = copy.move

/** Mover entre núcleos (F-CNV-01, regra 1). O acompanhante vai junto e não se move sozinho. */
export function MoveGuestDialog({
  guest,
  destinations,
}: {
  guest: Guest
  destinations: readonly Pick<Household, 'id' | 'name'>[]
}) {
  const [open, setOpen] = useState(false)
  const [destination, setDestination] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [alert, setAlert] = useState<FormAlertState | null>(null)
  const move = useMoveGuest()
  const name = displayName(guest)

  if (guest.companion_of_id !== null) {
    return <p className="text-ui-sm text-ink-muted">{labels.companionHint}</p>
  }
  if (destinations.length === 0) return null

  function submit() {
    if (destination === '') {
      setError(labels.needsDestination)
      return
    }
    setError(null)
    setAlert(null)
    move.mutate(
      { guestId: guest.id, householdId: destination, version: guest.version },
      { onSuccess: () => setOpen(false), onError: (e) => setAlert(alertFromError(e)) },
    )
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next)
        if (!next) {
          setDestination('')
          setError(null)
          setAlert(null)
        }
      }}
    >
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" aria-label={`${labels.button}: ${name}`}>
          {labels.button}
        </Button>
      </DialogTrigger>
      <DialogContent title={labels.title} description={labels.description(name)}>
        <Select
          label={labels.destination}
          placeholder={labels.placeholder}
          options={destinations.map((household) => ({
            value: household.id,
            label: household.name,
          }))}
          value={destination}
          onValueChange={setDestination}
          error={error ?? undefined}
        />
        <FormAlert alert={alert} />
        <DialogFooter>
          <Button variant="ghost" onClick={() => setOpen(false)}>
            {copy.forms.cancel}
          </Button>
          <Button onClick={submit} loading={move.isPending}>
            {labels.confirm}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
