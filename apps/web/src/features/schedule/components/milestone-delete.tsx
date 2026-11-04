import { useQueryClient } from '@tanstack/react-query'
import { useRef, useState } from 'react'
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogFooter,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { type ScheduleMilestone, scheduleKeys } from '../api/schedule'
import { useDeleteMilestone } from '../api/use-milestone-mutations'
import { copy } from '../copy'
import { type AlertState, alertFromError } from '../lib/errors'
import { FormAlert } from './form-alert'

const labels = copy.remove

const ALERTS = {
  conflict: labels.conflict,
  network: labels.network,
}

export interface DeletedMilestone {
  id: string
  title: string
}

/**
 * Excluir o marco (F-CRN-01, regra 3): a confirmação lista os dependentes, que deixam de depender
 * dele, e diz que o marco fica guardado. A exclusão é lógica; o Desfazer fica com quem mostra o
 * aviso, porque este painel fecha ao excluir (D-072, item 8).
 */
export function DeleteMilestone({
  milestone,
  onDeleted,
}: {
  milestone: ScheduleMilestone
  onDeleted: (deleted: DeletedMilestone) => void
}) {
  const remove = useDeleteMilestone()
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [alert, setAlert] = useState<AlertState | null>(null)
  const [reloading, setReloading] = useState(false)
  // Sem `AlertDialogTrigger` o Radix não devolve o foco: ao cancelar ele volta ao botão que abriu.
  const origin = useRef<HTMLButtonElement>(null)

  function close() {
    setOpen(false)
    setAlert(null)
  }

  function submit() {
    setAlert(null)
    remove.mutate(
      { milestoneId: milestone.id, version: milestone.version },
      {
        onSuccess: () => {
          close()
          onDeleted({ id: milestone.id, title: milestone.title })
        },
        onError: (error) => setAlert(alertFromError(error, ALERTS)),
      },
    )
  }

  async function reload() {
    setReloading(true)
    await queryClient.refetchQueries({ queryKey: scheduleKeys.all })
    setReloading(false)
    setAlert(null)
  }

  return (
    <>
      <Button
        ref={origin}
        variant="soft-destructive"
        className="shrink-0 self-start"
        onClick={() => setOpen(true)}
      >
        {labels.button}
      </Button>
      <AlertDialog open={open} onOpenChange={(next) => (next ? setOpen(true) : close())}>
        <AlertDialogContent
          title={labels.title(milestone.title)}
          description={labels.description}
          pending={remove.isPending}
          onCloseAutoFocus={(event) => {
            event.preventDefault()
            origin.current?.focus()
          }}
        >
          {milestone.unlocks.length === 0 ? (
            <p className="text-body text-ink">{labels.noDependents}</p>
          ) : (
            <div className="flex flex-col gap-1">
              <h3 className="text-body-sm font-semibold text-ink">{labels.dependentsTitle}</h3>
              <ul className="flex flex-col gap-1">
                {milestone.unlocks.map((unlocked) => (
                  <li key={unlocked.id} className="text-body text-ink">
                    {unlocked.title}
                  </li>
                ))}
              </ul>
              <p className="text-body-sm text-ink-muted">{labels.dependents}</p>
            </div>
          )}
          <FormAlert alert={alert} onReload={() => void reload()} reloading={reloading} />
          <AlertDialogFooter>
            <AlertDialogCancel asChild>
              <Button variant="ghost" disabled={remove.isPending}>
                {labels.cancel}
              </Button>
            </AlertDialogCancel>
            <Button variant="soft-destructive" onClick={submit} loading={remove.isPending}>
              {labels.confirm}
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
