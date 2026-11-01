import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogTrigger } from '@/components/ui/dialog'
import { useToast } from '@/components/ui/toast'
import type { Household } from '../api/guests'
import { useDeleteHousehold, useRestoreHousehold } from '../api/use-guest-mutations'
import { copy } from '../copy'
import { alertFromError, type FormAlertState } from '../lib/server-errors'
import { FormAlert } from './form-alert'

const labels = copy.remove

/** Excluir o núcleo (F-CNV-01, regra 2): pede confirmação, é lógico e traz o Desfazer. */
export function DeleteHouseholdDialog({
  household,
  onDeleted,
}: {
  household: Household
  /** O painel do núcleo excluído não faz mais sentido: quem o abriu o fecha. */
  onDeleted: () => void
}) {
  const [open, setOpen] = useState(false)
  const [alert, setAlert] = useState<FormAlertState | null>(null)
  const remove = useDeleteHousehold()
  const restore = useRestoreHousehold()
  const { toast } = useToast()

  function submit() {
    setAlert(null)
    remove.mutate(
      { householdId: household.id, version: household.version },
      {
        onSuccess: () => {
          setOpen(false)
          onDeleted()
          toast({
            title: labels.householdDone(household.name),
            action: {
              label: labels.undo,
              altText: labels.undoAlt,
              onClick: () => restore.mutate({ householdId: household.id }),
            },
          })
        },
        onError: (error) => setAlert(alertFromError(error)),
      },
    )
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next)
        if (!next) setAlert(null)
      }}
    >
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm">
          {labels.householdButton}
        </Button>
      </DialogTrigger>
      <DialogContent
        title={labels.householdTitle(household.name)}
        description={labels.householdDescription(household.guests.length)}
      >
        <FormAlert alert={alert} />
        <DialogFooter>
          <Button variant="ghost" onClick={() => setOpen(false)}>
            {labels.cancel}
          </Button>
          <Button variant="soft-destructive" onClick={submit} loading={remove.isPending}>
            {labels.confirmHousehold}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
