import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

export interface PageHeaderProps {
  /** Título da página: o único `h1` da tela. */
  title: string
  /** Rótulo acima do título (identity.md §5). */
  eyebrow?: string
  /** Linha de apoio abaixo do título. */
  description?: string
  /** Ações da página, à direita no desktop e abaixo no celular. */
  actions?: ReactNode
  className?: string
}

/** Cabeçalho editorial: rótulo, título em serifa, apoio, ações e uma hairline (identity.md §5). */
export function PageHeader({ title, eyebrow, description, actions, className }: PageHeaderProps) {
  return (
    <header
      className={cn(
        'flex flex-col gap-4 border-b border-border pb-6 md:flex-row md:items-end md:justify-between',
        className,
      )}
    >
      <div className="flex min-w-0 flex-col gap-1">
        {eyebrow && <p className="text-eyebrow text-ink-muted">{eyebrow}</p>}
        <h1 className="text-display text-ink">{title}</h1>
        {description && <p className="max-w-[68ch] text-body text-ink-muted">{description}</p>}
      </div>
      {actions && <div className="flex flex-wrap items-center gap-3">{actions}</div>}
    </header>
  )
}
