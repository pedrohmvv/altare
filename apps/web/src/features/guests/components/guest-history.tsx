import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { formatInstant } from '@/lib/date'
import { guestHistoryQueryOptions } from '../api/guests'
import { copy } from '../copy'

const labels = copy.history

/** O histórico de status de uma pessoa (F-CNV-04, regra 4): quem mudou, quando e de qual para qual. */
export function GuestHistory({ guestId }: { guestId: string }) {
  const [open, setOpen] = useState(false)
  const history = useQuery({ ...guestHistoryQueryOptions(guestId), enabled: open })
  return (
    <div className="flex flex-col gap-2">
      <Button
        variant="ghost"
        size="sm"
        aria-expanded={open}
        className="self-start"
        onClick={() => setOpen((current) => !current)}
      >
        {open ? labels.hide : labels.button}
      </Button>
      {open && (
        <section aria-label={labels.title} className="flex flex-col gap-1">
          {history.isError && <p className="text-body-sm text-ink-muted">{labels.loadError}</p>}
          {history.data?.length === 0 && (
            <p className="text-body-sm text-ink-muted">{labels.empty}</p>
          )}
          {history.data && history.data.length > 0 && (
            <ul className="flex flex-col">
              {history.data.map((change) => (
                <li key={change.id} className="border-t border-border py-2 first:border-t-0">
                  <p className="text-ui-sm text-ink-muted">
                    {change.profile} · {formatInstant(change.changed_at)}
                  </p>
                  <p className="text-body-sm text-ink">
                    {labels.change(change.from_status, change.to_status)}
                  </p>
                  {change.reason && (
                    <p className="text-body-sm text-ink-muted">{labels.reason(change.reason)}</p>
                  )}
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </div>
  )
}
