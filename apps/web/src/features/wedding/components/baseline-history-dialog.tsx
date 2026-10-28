import { useQuery } from '@tanstack/react-query'
import { Dialog, DialogContent } from '@/components/ui/dialog'
import { formatInstant } from '@/lib/date'
import { type BaselineChange, baselineChangesQueryOptions } from '../api/baseline'
import { copy } from '../copy'
import { describeValue } from '../lib/describe-value'

function changeLines(change: BaselineChange): string[] {
  const lines: string[] = []
  const before = describeValue(change.field, change.before.value)
  const after = describeValue(change.field, change.after.value)
  if (before !== after) {
    lines.push(`${before ?? copy.history.noValue} → ${after ?? copy.history.noValue}`)
  }
  if (change.before.status !== change.after.status) {
    lines.push(`${change.before.status} → ${change.after.status}`)
  }
  if (change.before.note !== change.after.note) {
    lines.push(
      change.after.note
        ? `${copy.history.noteLabel}: “${change.after.note}”`
        : `${copy.history.noteLabel}: ${copy.history.noValue}`,
    )
  }
  return lines
}

export function BaselineHistoryDialog({
  open,
  onOpenChange,
  onCloseAutoFocus,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onCloseAutoFocus?: (event: Event) => void
}) {
  const changes = useQuery({ ...baselineChangesQueryOptions, enabled: open })
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        title={copy.history.title}
        description={copy.history.description}
        onCloseAutoFocus={onCloseAutoFocus}
      >
        {changes.isError && <p className="text-body text-ink-muted">{copy.history.loadError}</p>}
        {changes.data?.length === 0 && (
          <p className="text-body text-ink-muted">{copy.history.empty}</p>
        )}
        {changes.data && changes.data.length > 0 && (
          <ul className="flex flex-col">
            {changes.data.map((change) => (
              <li key={change.id} className="border-t border-border py-3 first:border-t-0">
                <p className="text-ui-sm text-ink-muted">
                  {change.by} · {formatInstant(change.at)}
                </p>
                <p className="text-body font-medium text-ink">{copy.fields[change.field].label}</p>
                {changeLines(change).map((line) => (
                  <p key={line} className="text-body-sm text-ink-muted">
                    {line}
                  </p>
                ))}
              </li>
            ))}
          </ul>
        )}
      </DialogContent>
    </Dialog>
  )
}
