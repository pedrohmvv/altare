import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

/** Botão de alternar em forma de pílula (`aria-pressed`): filtros e prioridades. */
export function Chip({
  pressed,
  onClick,
  disabled,
  children,
}: {
  pressed: boolean
  onClick: () => void
  disabled?: boolean
  children: ReactNode
}) {
  return (
    <button
      type="button"
      aria-pressed={pressed}
      disabled={disabled}
      onClick={onClick}
      className={cn(
        'inline-flex min-h-8 items-center rounded-pill border px-3 text-ui-sm font-medium pointer-coarse:min-h-11',
        'transition-colors duration-fast ease-standard disabled:opacity-40',
        pressed
          ? 'border-primary bg-primary text-primary-ink'
          : 'border-border-strong bg-surface text-ink hover:border-ink-muted',
      )}
    >
      {children}
    </button>
  )
}
