import { cva } from 'class-variance-authority'
import type { ComponentProps, ReactNode } from 'react'
import { cn } from '@/lib/cn'

const badgeVariants = cva(
  'inline-flex min-h-6.5 items-center gap-1.5 rounded-pill px-2.5 text-ui-sm font-semibold [&_svg]:size-3.5 [&_svg]:shrink-0',
  {
    variants: {
      variant: {
        neutral: 'bg-surface-sunken text-ink-muted',
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
