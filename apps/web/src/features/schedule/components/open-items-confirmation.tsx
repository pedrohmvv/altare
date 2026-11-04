import { Button } from '@/components/ui/button'
import { DialogContent, DialogFooter } from '@/components/ui/dialog'
import { copy } from '../copy'

const text = copy.confirm.openItems

export interface OpenItemsConfirmationProps {
  /** Quantos itens do checklist estão em aberto (sempre maior que zero). */
  openItems: number
  /** O que o marco ainda aguarda, quando está Bloqueado; a avulsa não tem. */
  waiting?: readonly string[]
  loading: boolean
  onCancel: () => void
  onConfirm: () => void
  onCloseAutoFocus: (event: Event) => void
}

/**
 * Concluir com itens do checklist em aberto (F-CRN-07, regra 5): um só diálogo, com as linhas que se
 * aplicam. Os itens não são alterados; no marco Bloqueado a mesma confirmação vale também para o
 * bloqueio.
 */
export function OpenItemsConfirmation({
  openItems,
  waiting = [],
  loading,
  onCancel,
  onConfirm,
  onCloseAutoFocus,
}: OpenItemsConfirmationProps) {
  return (
    <DialogContent
      title={text.title}
      description={text.count(openItems)}
      onCloseAutoFocus={onCloseAutoFocus}
    >
      <p className="text-body text-ink">{text.keep}</p>
      {waiting.length > 0 && (
        <div className="flex flex-col gap-1">
          <p className="text-body-sm text-ink-muted">{text.waiting}</p>
          <h3 className="text-body-sm font-semibold text-ink">{text.waitingLabel}</h3>
          <ul className="flex flex-col gap-1">
            {waiting.map((label) => (
              <li key={label} className="text-body text-ink">
                {label}
              </li>
            ))}
          </ul>
        </div>
      )}
      <DialogFooter>
        <Button variant="ghost" onClick={onCancel}>
          {copy.confirm.cancel}
        </Button>
        <Button onClick={onConfirm} loading={loading}>
          {text.confirm}
        </Button>
      </DialogFooter>
    </DialogContent>
  )
}
