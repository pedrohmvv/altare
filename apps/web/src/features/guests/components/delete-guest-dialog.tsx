import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogTrigger } from '@/components/ui/dialog'
import { SegmentedControl } from '@/components/ui/segmented-control'
import type { Guest } from '../api/guests'
import { useDeleteGuest } from '../api/use-guest-mutations'
import { copy } from '../copy'
import { displayName } from '../lib/names'
import { alertFromError, type FormAlertState } from '../lib/server-errors'
import { FormAlert } from './form-alert'

const labels = copy.remove

/**
 * Excluir uma pessoa (F-CNV-01): a exclusão é lógica, então o diálogo diz que fica recuperável. Quem
 * tem acompanhante escolhe o que fazer com ele (F-CNV-02). Quem abriu o painel mostra o Desfazer
 * dentro dele: um aviso fora do painel modal ficaria escondido do leitor de tela e do teclado.
 */
export function DeleteGuestDialog({
  guest,
  companion,
  onRemoved,
}: {
  guest: Guest
  companion?: Guest
  onRemoved: (removed: { guestId: string; name: string }) => void
}) {
  const [open, setOpen] = useState(false)
  const [choice, setChoice] = useState<'delete' | 'keep'>('delete')
  const [alert, setAlert] = useState<FormAlertState | null>(null)
  const remove = useDeleteGuest()
  const name = displayName(guest)
  const canKeep = companion?.name != null

  function submit() {
    setAlert(null)
    remove.mutate(
      {
        guestId: guest.id,
        version: guest.version,
        companion: companion ? (canKeep ? choice : 'delete') : null,
      },
      {
        onSuccess: () => {
          setOpen(false)
          onRemoved({ guestId: guest.id, name })
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
        <Button variant="ghost" size="sm" aria-label={`${labels.guestButton}: ${name}`}>
          {labels.guestButton}
        </Button>
      </DialogTrigger>
      <DialogContent title={labels.guestTitle(name)} description={labels.guestDescription}>
        {companion && (
          <div className="flex flex-col gap-2">
            <SegmentedControl
              aria-label={labels.companionLabel}
              value={canKeep ? choice : 'delete'}
              onValueChange={(value) => setChoice(value === 'keep' ? 'keep' : 'delete')}
              options={[
                { value: 'delete', label: labels.deleteBoth },
                {
                  value: 'keep',
                  label: labels.keepCompanion(companion.name),
                  disabled: !canKeep,
                },
              ]}
            />
            {!canKeep && <p className="text-body-sm text-ink-muted">{labels.keepNeedsName}</p>}
          </div>
        )}
        <FormAlert alert={alert} />
        <DialogFooter>
          <Button variant="ghost" onClick={() => setOpen(false)}>
            {labels.cancel}
          </Button>
          <Button variant="soft-destructive" onClick={submit} loading={remove.isPending}>
            {labels.confirmGuest}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
