import { CircleAlert } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { copy } from '../copy'
import type { FormAlertState } from '../lib/server-errors'

/**
 * O aviso do formulário, ligado a um erro da API. A região existe vazia desde o início: um aviso
 * que nasce já pronto não é anunciado pelo leitor de tela. Conflito de versão oferece ver a versão
 * mais recente, nunca sobrescreve.
 */
export function FormAlert({
  alert,
  onReload,
  reloading = false,
}: {
  alert: FormAlertState | null
  onReload?: () => void
  reloading?: boolean
}) {
  return (
    <div role="alert">
      {alert && (
        <div className="flex flex-col items-start gap-3 rounded-control bg-attention-bg px-3 py-2.5 text-body-sm text-attention-ink">
          <p className="flex items-start gap-2">
            <CircleAlert aria-hidden className="mt-0.5 size-4 shrink-0" />
            {alert.text}
          </p>
          {alert.kind === 'conflict' && onReload && (
            <Button
              type="button"
              variant="secondary"
              size="sm"
              disabled={reloading}
              onClick={onReload}
            >
              {copy.forms.reload}
            </Button>
          )}
        </div>
      )}
    </div>
  )
}
