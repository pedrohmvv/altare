import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogTrigger } from '@/components/ui/dialog'
import { copy } from '../copy'
import { GuestSequence } from './guest-sequence'

/** Acrescenta pessoas a um núcleo que já existe, em sequência (F-CNV-01, regra 3). */
export function AddGuestDialog({
  householdId,
  householdName,
}: {
  householdId: string
  householdName: string
}) {
  const [open, setOpen] = useState(false)
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="secondary" size="sm">
          {copy.forms.addGuest.button}
        </Button>
      </DialogTrigger>
      <DialogContent
        title={copy.forms.sequence.title(householdName)}
        description={copy.forms.sequence.description}
      >
        <GuestSequence householdId={householdId} onDone={() => setOpen(false)} />
      </DialogContent>
    </Dialog>
  )
}
