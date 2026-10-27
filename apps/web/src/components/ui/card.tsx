import { cva } from 'class-variance-authority'
import { Slot } from 'radix-ui'
import type { ComponentProps } from 'react'
import { cn } from '@/lib/cn'

// Plano, com hairline e sem sombra (identity.md §5); o anel de foco usa o fundo do cartão como espaçador.
const cardVariants = cva('rounded-card border p-5 max-md:p-4', {
  variants: {
    variant: {
      default: 'border-border bg-surface [--focus-gap:var(--surface)]',
      interactive: [
        'border-border bg-surface [--focus-gap:var(--surface)]',
        'transition-colors duration-fast ease-standard hover:border-border-strong',
      ],
      muted: 'border-border bg-surface-muted [--focus-gap:var(--surface-muted)]',
    },
  },
  defaultVariants: { variant: 'default' },
})

export type CardProps = ComponentProps<'div'> & {
  variant?: 'default' | 'interactive' | 'muted'
  /** Aplica o estilo ao único filho (por exemplo, um link que torna o cartão clicável). */
  asChild?: boolean
}

export function Card({ variant, asChild = false, className, ...props }: CardProps) {
  const Component = asChild ? Slot.Root : 'div'
  return <Component className={cn(cardVariants({ variant }), className)} {...props} />
}
