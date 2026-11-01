import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Textarea } from '@/components/ui/textarea'
import { GUEST_STATUSES, type Guest, type GuestStatus, guestKeys } from '../api/guests'
import { useChangeGuestStatus } from '../api/use-guest-mutations'
import { copy } from '../copy'
import { alertFromError, type FormAlertState } from '../lib/server-errors'
import { FormAlert } from './form-alert'
import { GuestStatusBadge } from './guest-badges'

/**
 * O status em um toque (F-CNV-04): o selo é o botão e abre um cartão com os quatro status, de
 * qualquer um para qualquer outro. `Não irá` pergunta o motivo, que é opcional. Nada é otimista: o
 * servidor recalcula os contadores, e a tela só muda quando ele responde.
 */
export function StatusControl({ guest, name }: { guest: Guest; name: string }) {
  const [open, setOpen] = useState(false)
  const [asking, setAsking] = useState(false)
  const [reason, setReason] = useState('')
  const [alert, setAlert] = useState<FormAlertState | null>(null)
  const [reloading, setReloading] = useState(false)
  const change = useChangeGuestStatus()
  const queryClient = useQueryClient()

  function close() {
    setOpen(false)
    setAsking(false)
    setReason('')
    setAlert(null)
  }

  function send(status: GuestStatus, why: string | null) {
    setAlert(null)
    change.mutate(
      { guestId: guest.id, status, reason: why, version: guest.version },
      { onSuccess: close, onError: (error) => setAlert(alertFromError(error)) },
    )
  }

  function choose(status: GuestStatus) {
    if (status === guest.status) return
    if (status === 'Não irá') {
      setAsking(true)
      return
    }
    send(status, null)
  }

  async function reload() {
    setReloading(true)
    await queryClient.refetchQueries({ queryKey: guestKeys.list })
    setReloading(false)
    setAlert(null)
  }

  return (
    <Popover open={open} onOpenChange={(next) => (next ? setOpen(true) : close())}>
      <PopoverTrigger asChild>
        <button
          type="button"
          aria-label={copy.status.change(name, guest.status)}
          className="relative z-10 rounded-pill"
        >
          <GuestStatusBadge status={guest.status} />
        </button>
      </PopoverTrigger>
      <PopoverContent title={copy.status.title(name)} side="bottom" align="start">
        <div className="flex flex-col gap-2">
          {GUEST_STATUSES.map((status) => (
            <Button
              key={status}
              variant={status === guest.status ? 'primary' : 'secondary'}
              aria-pressed={status === guest.status}
              disabled={change.isPending}
              onClick={() => choose(status)}
            >
              {copy.statuses[status]}
            </Button>
          ))}
        </div>
        {asking && (
          <div className="flex flex-col gap-3">
            <Textarea
              label={copy.status.reasonLabel}
              hint={copy.status.reasonHint}
              rows={3}
              value={reason}
              onChange={(event) => setReason(event.target.value)}
            />
            <div className="flex flex-wrap gap-3">
              <Button
                onClick={() => send('Não irá', reason.trim() === '' ? null : reason.trim())}
                loading={change.isPending}
              >
                {copy.status.confirm}
              </Button>
              <Button variant="ghost" onClick={() => setAsking(false)}>
                {copy.status.back}
              </Button>
            </div>
          </div>
        )}
        <FormAlert alert={alert} onReload={() => void reload()} reloading={reloading} />
      </PopoverContent>
    </Popover>
  )
}
