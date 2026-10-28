import { X } from 'lucide-react'
import { Dialog as RadixDialog } from 'radix-ui'
import type { ComponentProps } from 'react'
import { cn } from '@/lib/cn'
import { Button } from './button'

export const Sheet = RadixDialog.Root
export const SheetTrigger = RadixDialog.Trigger
export const SheetClose = RadixDialog.Close

export type SheetContentProps = Omit<ComponentProps<typeof RadixDialog.Content>, 'title'> & {
  /** Nome do painel, lido pelo leitor de tela (`aria-labelledby`). */
  title: string
  description?: string
}

/**
 * Detalhe sem sair da lista (design-system.md §10, item 2): gaveta lateral à direita a partir de
 * `md` e folha inferior abaixo disso, só com CSS. Fica na camada `drawer` (z-30), abaixo de diálogo,
 * popover e aviso, que abrem de dentro dela. É modal: o foco fica preso e volta ao gatilho.
 */
export function SheetContent({
  title,
  description,
  className,
  children,
  ...props
}: SheetContentProps) {
  return (
    <RadixDialog.Portal>
      <RadixDialog.Overlay className="fixed inset-0 z-30 bg-scrim data-[state=closed]:animate-overlay-out data-[state=open]:animate-overlay-in" />
      <RadixDialog.Content
        // Declarar `undefined` evita o aviso do Radix quando não há descrição.
        aria-describedby={undefined}
        className={cn(
          'fixed inset-x-0 bottom-0 z-30 flex max-h-[85dvh] flex-col gap-5 overflow-y-auto',
          'rounded-t-card border border-border bg-surface p-5 shadow-nivel-2 [--focus-gap:var(--surface)]',
          'data-[state=closed]:animate-sheet-out data-[state=open]:animate-sheet-in',
          'md:inset-x-auto md:inset-y-0 md:right-0 md:max-h-none md:w-[28rem] md:max-w-[calc(100vw-2rem)]',
          'md:rounded-t-none md:rounded-l-card md:border-y-0 md:border-r-0 md:p-6',
          'md:data-[state=closed]:animate-sheet-side-out md:data-[state=open]:animate-sheet-side-in',
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
