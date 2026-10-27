import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

// Alturas do guia (págs. 30 e 31): ramo pequeno 64 px, ramo grande 112 px, arco simples 80 px.
const ILLUSTRATIONS = {
  ramo: { src: '/brand/ornamentos/ramo-pequeno.svg', className: 'h-16' },
  'ramo-grande': { src: '/brand/ornamentos/ramo-grande.svg', className: 'h-28' },
  arco: { src: '/brand/ornamentos/arco-simples.svg', className: 'h-20' },
} as const

export interface EmptyStateProps {
  title: string
  description?: string
  /** Uma única ação clara (identity.md §9). */
  action?: ReactNode
  /** Ornamento em linha de `public/brand/ornamentos/`, só decorativo. O ramo grande é o do 404. */
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
      <img
        src={ILLUSTRATIONS[illustration].src}
        alt=""
        className={ILLUSTRATIONS[illustration].className}
      />
      <Heading className="text-name text-ink">{title}</Heading>
      {description && <p className="max-w-[44ch] text-ui text-ink-muted">{description}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  )
}
