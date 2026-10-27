import { cva } from 'class-variance-authority'
import type { ComponentProps, ReactNode } from 'react'
import { cn } from '@/lib/cn'

const badgeVariants = cva(
  'inline-flex items-center gap-1.5 rounded-control px-2 py-0.5 text-body-sm font-medium [&_svg]:size-4 [&_svg]:shrink-0',
  {
    variants: {
      variant: {
        neutral: 'bg-surface-sunken text-ink',
        consensus: 'bg-consensus-bg text-consensus-ink',
        attention: 'bg-attention-bg text-attention-ink',
        primary: 'bg-primary text-primary-ink',
        outline: 'border border-border-strong text-ink',
      },
    },
    defaultVariants: { variant: 'neutral' },
  },
)

type CommonProps = ComponentProps<'span'>

/** Consenso e atenção exigem ícone: cor nunca é o único sinal (identity.md §7). */
type SemanticBadgeProps = CommonProps & {
  variant: 'consensus' | 'attention'
  icon: ReactNode
}
type PlainBadgeProps = CommonProps & {
  variant?: 'neutral' | 'primary' | 'outline'
  icon?: ReactNode
}

export type BadgeProps = SemanticBadgeProps | PlainBadgeProps

export function Badge({ variant, icon, className, children, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props}>
      {icon != null && <span aria-hidden>{icon}</span>}
      {children}
    </span>
  )
}
