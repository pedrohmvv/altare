import { AlertDialog as RadixAlertDialog } from 'radix-ui'
import type { ComponentProps } from 'react'
import { cn } from '@/lib/cn'

export const AlertDialog = RadixAlertDialog.Root
export const AlertDialogTrigger = RadixAlertDialog.Trigger
/** O lado seguro: recebe o foco ao abrir e fecha sem agir. Use com `asChild` sobre um `Button`. */
export const AlertDialogCancel = RadixAlertDialog.Cancel

export type AlertDialogContentProps = Omit<
  ComponentProps<typeof RadixAlertDialog.Content>,
  'title' | 'aria-describedby'
> & {
  /** Nome da confirmação, lido pelo leitor de tela (`aria-labelledby`). */
  title: string
  /** A consequência, em uma frase: o que sai da lista e o que fica guardado. */
  description: string
  /**
   * A ação confirmada está no ar: o Esc não fecha, para o resultado (e um erro do servidor) ter onde
   * aparecer. Quem usa também desabilita o Cancelar com o mesmo estado.
   */
  pending?: boolean
}

/**
 * Confirmação de ação destrutiva (design-system.md §8, D-085): o mesmo desenho do `Dialog`, mas sem
 * o botão Fechar e sem fechar por clique fora; só o Cancelar, o Esc ou a própria ação a encerram.
 * O foco entra no Cancelar. O botão de confirmar é um `Button` comum, não `AlertDialog.Action`: ele
 * não fecha sozinho, para a tela mostrar a escrita pendente e um erro do servidor dentro do diálogo.
 */
export function AlertDialogContent({
  title,
  description,
  pending = false,
  onEscapeKeyDown,
  className,
  children,
  ...props
}: AlertDialogContentProps) {
  return (
    <RadixAlertDialog.Portal>
      <RadixAlertDialog.Overlay className="fixed inset-0 z-40 bg-scrim data-[state=closed]:animate-overlay-out data-[state=open]:animate-overlay-in" />
      <RadixAlertDialog.Content
        className={cn(
          'fixed inset-x-0 bottom-0 z-40 flex max-h-[85dvh] flex-col gap-4 overflow-y-auto',
          'rounded-t-card border border-border bg-surface p-5 shadow-nivel-2 [--focus-gap:var(--surface)]',
          'data-[state=closed]:animate-sheet-out data-[state=open]:animate-sheet-in',
          'md:inset-auto md:top-1/2 md:left-1/2 md:w-[calc(100%-2rem)] md:max-w-lg md:-translate-x-1/2 md:-translate-y-1/2',
          'md:rounded-card md:p-6 md:data-[state=closed]:animate-dialog-out md:data-[state=open]:animate-dialog-in',
          className,
        )}
        onEscapeKeyDown={(event) => {
          onEscapeKeyDown?.(event)
          if (pending) event.preventDefault()
        }}
        {...props}
      >
        <div className="flex flex-col gap-1">
          <RadixAlertDialog.Title className="text-heading text-ink">{title}</RadixAlertDialog.Title>
          <RadixAlertDialog.Description className="text-body text-ink-muted">
            {description}
          </RadixAlertDialog.Description>
        </div>
        {children}
      </RadixAlertDialog.Content>
    </RadixAlertDialog.Portal>
  )
}

export function AlertDialogFooter({ className, ...props }: ComponentProps<'div'>) {
  return (
    <div
      className={cn(
        'flex flex-col-reverse gap-3 max-md:*:w-full md:flex-row md:justify-end',
        className,
      )}
      {...props}
    />
  )
}
