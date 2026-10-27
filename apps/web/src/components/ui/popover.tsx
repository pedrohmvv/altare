import { X } from 'lucide-react'
import { Popover as RadixPopover } from 'radix-ui'
import { type ComponentProps, useId } from 'react'
import { cn } from '@/lib/cn'
import { Button } from './button'

export const Popover = RadixPopover.Root
export const PopoverTrigger = RadixPopover.Trigger
export const PopoverAnchor = RadixPopover.Anchor
export const PopoverClose = RadixPopover.Close

export type PopoverContentProps = Omit<ComponentProps<typeof RadixPopover.Content>, 'title'> & {
  /** Nome do cartão, lido pelo leitor de tela (`aria-labelledby`). */
  title: string
  description?: string
}

/**
 * Cartão ancorado no gatilho, nível 1 de profundidade do guia (pág. 32: Marfim, *hairline*, raio 10 e
 * sombra suave). Não é modal: não escurece nem trava a página. Esc, o botão Fechar e o clique fora o
 * fecham, e o foco volta ao gatilho.
 */
export function PopoverContent({
  title,
  description,
  className,
  children,
  side = 'top',
  align = 'end',
  sideOffset = 8,
  collisionPadding = 16,
  ...props
}: PopoverContentProps) {
  const titleId = useId()
  const descriptionId = useId()

  return (
    <RadixPopover.Portal>
      <RadixPopover.Content
        side={side}
        align={align}
        sideOffset={sideOffset}
        collisionPadding={collisionPadding}
        aria-labelledby={titleId}
        aria-describedby={description ? descriptionId : undefined}
        className={cn(
          'z-50 flex w-[min(22rem,calc(100vw-2rem))] origin-(--radix-popover-content-transform-origin) flex-col gap-3',
          'rounded-card border border-border bg-surface p-5 shadow-nivel-1 [--focus-gap:var(--surface)]',
          'data-[state=closed]:animate-dialog-out data-[state=open]:animate-dialog-in',
          className,
        )}
        {...props}
      >
        <div className="flex flex-col gap-1 pr-8">
          <p id={titleId} className="text-name text-ink">
            {title}
          </p>
          {description && (
            <p id={descriptionId} className="text-body text-ink-muted">
              {description}
            </p>
          )}
        </div>
        {children}
        <RadixPopover.Close asChild>
          <Button
            variant="ghost"
            size="icon"
            aria-label="Fechar"
            className="absolute top-2 right-2"
          >
            <X aria-hidden />
          </Button>
        </RadixPopover.Close>
      </RadixPopover.Content>
    </RadixPopover.Portal>
  )
}
