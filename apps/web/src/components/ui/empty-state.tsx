import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

const ILLUSTRATIONS = {
  ramo: '/brand/ornamentos/ramo-pequeno.svg',
  arco: '/brand/ornamentos/arco-simples.svg',
} as const

export interface EmptyStateProps {
  title: string
  description?: string
  /** Uma única ação clara (identity.md §9). */
  action?: ReactNode
  /** Ornamento em linha de `public/brand/ornamentos/`, só decorativo. */
  illustration?: keyof typeof ILLUSTRATIONS
  /** Nível do título, para respeitar a hierarquia da tela. */
  headingLevel?: 2 | 3 | 4
  className?: string
}

export function EmptyState({
  title,
  description,
  action,
  illustration = 'ramo',
  headingLevel = 2,
  className,
}: EmptyStateProps) {
  const Heading = `h${headingLevel}` as const

  return (
    <div className={cn('flex flex-col items-center gap-3 px-4 py-10 text-center', className)}>
      <img src={ILLUSTRATIONS[illustration]} alt="" className="h-20" />
      <Heading className="text-heading text-ink">{title}</Heading>
      {description && <p className="max-w-[44ch] text-body text-ink-muted">{description}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  )
}
