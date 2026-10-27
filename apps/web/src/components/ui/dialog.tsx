import { X } from 'lucide-react'
import { Dialog as RadixDialog } from 'radix-ui'
import type { ComponentProps } from 'react'
import { cn } from '@/lib/cn'
import { Button } from './button'

export const Dialog = RadixDialog.Root
export const DialogTrigger = RadixDialog.Trigger
export const DialogClose = RadixDialog.Close

export type DialogContentProps = Omit<ComponentProps<typeof RadixDialog.Content>, 'title'> & {
  /** Nome do diálogo, lido pelo leitor de tela (`aria-labelledby`). */
  title: string
  description?: string
}

/** Centralizado a partir de `md`; abaixo disso vira folha inferior (design-system.md §8). */
export function DialogContent({
  title,
  description,
  className,
  children,
  ...props
}: DialogContentProps) {
  return (
    <RadixDialog.Portal>
      <RadixDialog.Overlay className="fixed inset-0 z-40 bg-scrim data-[state=closed]:animate-overlay-out data-[state=open]:animate-overlay-in" />
      <RadixDialog.Content
        // Declarar `undefined` evita o aviso do Radix quando não há descrição; com ela, o Radix a liga sozinho.
        aria-describedby={undefined}
        className={cn(
          'fixed inset-x-0 bottom-0 z-40 flex max-h-[85dvh] flex-col gap-4 overflow-y-auto',
          'rounded-t-card border border-border bg-surface p-5 shadow-nivel-2 [--focus-gap:var(--surface)]',
          'data-[state=closed]:animate-sheet-out data-[state=open]:animate-sheet-in',
          'md:inset-auto md:top-1/2 md:left-1/2 md:w-[calc(100%-2rem)] md:max-w-lg md:-translate-x-1/2 md:-translate-y-1/2',
          'md:rounded-card md:p-6 md:data-[state=closed]:animate-dialog-out md:data-[state=open]:animate-dialog-in',
          className,
        )}
        {...props}
      >
        <div className="flex flex-col gap-1 pr-10">
          <RadixDialog.Title className="text-heading text-ink">{title}</RadixDialog.Title>
          {description && (
            <RadixDialog.Description className="text-body text-ink-muted">
              {description}
            </RadixDialog.Description>
          )}
        </div>
        {children}
        <RadixDialog.Close asChild>
          <Button
            variant="ghost"
            size="icon"
            aria-label="Fechar"
            className="absolute top-3 right-3"
          >
            <X aria-hidden />
          </Button>
        </RadixDialog.Close>
      </RadixDialog.Content>
    </RadixDialog.Portal>
  )
}

export function DialogFooter({ className, ...props }: ComponentProps<'div'>) {
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
