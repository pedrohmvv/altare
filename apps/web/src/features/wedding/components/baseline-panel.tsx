import { useQuery } from '@tanstack/react-query'
import { ChevronRight, History } from 'lucide-react'
import { type ReactNode, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { cn } from '@/lib/cn'
import { BASELINE_KEYS, type BaselineKey, baselineQueryOptions } from '../api/baseline'
import { copy } from '../copy'
import { describeValue } from '../lib/describe-value'
import { BaselineFieldDialog } from './baseline-field-dialog'
import { BaselineHistoryDialog } from './baseline-history-dialog'
import { DefinitionBadge } from './definition-badge'

/**
 * As variáveis estruturais do casamento (F-PLN-01). O guia só desenha este cartão na pág. 38
 * (título em serifa, uma linha por variável, selo à direita e *hairline* entre as linhas); aqui
 * cada linha é um botão que abre a edição (`D-067`).
 */
export function BaselinePanel() {
  const baseline = useQuery(baselineQueryOptions)
  const [editing, setEditing] = useState<BaselineKey | null>(null)
  // A definição aberta continua montada durante a animação de saída do diálogo.
  const [lastEdited, setLastEdited] = useState<BaselineKey>('date')
  const [historyOpen, setHistoryOpen] = useState(false)
  // Quem abriu o diálogo recebe o foco de volta ao fechá-lo.
  const opener = useRef<HTMLElement | null>(null)
  const returnFocus = (event: Event) => {
    event.preventDefault()
    opener.current?.focus()
  }

  if (baseline.isPending) return <PanelMessage busy>{copy.panel.loading}</PanelMessage>
  if (baseline.isError) {
    return (
      <PanelMessage>
        <p className="text-body font-medium text-ink">{copy.panel.loadError.title}</p>
        <p className="text-body-sm text-ink-muted">{copy.panel.loadError.description}</p>
        <Button variant="secondary" className="mt-3" onClick={() => void baseline.refetch()}>
          {copy.panel.loadError.retry}
        </Button>
      </PanelMessage>
    )
  }

  const data = baseline.data
  return (
    <Card asChild>
      <section aria-labelledby="baseline-title">
        <h2 id="baseline-title" className="text-heading text-ink">
          {copy.panel.title}
        </h2>
        <p className="mt-1 text-body-sm text-ink-muted">{copy.panel.intro}</p>

        <ul className="mt-4">
          {BASELINE_KEYS.map((key) => {
            const value = describeValue(key, data[key].value)
            return (
              <li key={key} className="border-t border-border first:border-t-0">
                <button
                  type="button"
                  aria-haspopup="dialog"
                  onClick={(event) => {
                    opener.current = event.currentTarget
                    setLastEdited(key)
                    setEditing(key)
                  }}
                  className={cn(
                    'flex min-h-14 w-full items-center justify-between gap-4 rounded-control py-2 text-left',
                    'transition-colors duration-fast ease-standard hover:bg-surface-muted',
                  )}
                >
                  <span className="flex min-w-0 flex-col">
                    <span className="text-ui font-medium text-ink">{copy.fields[key].label}</span>
                    <span className="truncate text-body-sm text-ink-muted">
                      {value ?? copy.panel.empty}
                    </span>
                  </span>
                  <span className="flex shrink-0 items-center gap-2">
                    <DefinitionBadge status={data[key].status} />
                    <ChevronRight aria-hidden className="size-4 text-ink-subtle" />
                  </span>
                </button>
              </li>
            )
          })}
        </ul>

        <div className="mt-3 flex justify-end">
          <Button
            variant="ghost"
            size="sm"
            onClick={(event) => {
              opener.current = event.currentTarget
              setHistoryOpen(true)
            }}
          >
            <History aria-hidden /> {copy.panel.history}
          </Button>
        </div>

        <BaselineFieldDialog
          fieldKey={lastEdited}
          open={editing !== null}
          onOpenChange={(open) => !open && setEditing(null)}
          baseline={data}
          onCloseAutoFocus={returnFocus}
        />
        <BaselineHistoryDialog
          open={historyOpen}
          onOpenChange={setHistoryOpen}
          onCloseAutoFocus={returnFocus}
        />
      </section>
    </Card>
  )
}

function PanelMessage({ busy = false, children }: { busy?: boolean; children: ReactNode }) {
  return (
    <Card aria-busy={busy}>
      <h2 className="text-heading text-ink">{copy.panel.title}</h2>
      <div className="mt-3 flex flex-col items-start text-body-sm text-ink-muted">{children}</div>
    </Card>
  )
}
