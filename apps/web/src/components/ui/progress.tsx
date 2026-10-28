import { Progress as RadixProgress } from 'radix-ui'
import { useId } from 'react'
import { cn } from '@/lib/cn'

export interface ProgressProps {
  value: number
  max: number
  /** O texto do progresso ("3 de 18 categorias classificadas"): fica visível e dá o nome à barra. */
  label: string
  className?: string
}

/** Quanto já foi feito, sempre com o número por escrito: a barra sozinha nunca diz o estado. */
export function Progress({ value, max, label, className }: ProgressProps) {
  const labelId = useId()
  const share = max > 0 ? Math.min(Math.max(value / max, 0), 1) : 0

  return (
    <div className={cn('flex flex-col gap-2', className)}>
      <p id={labelId} className="text-body-sm text-ink">
        {label}
      </p>
      <RadixProgress.Root
        value={Math.max(value, 0)}
        max={Math.max(max, 1)}
        aria-labelledby={labelId}
        className="h-2 w-full overflow-hidden rounded-pill bg-surface-sunken"
      >
        <RadixProgress.Indicator
          className="h-full rounded-pill bg-primary transition-[width] duration-base ease-standard"
          style={{ width: `${share * 100}%` }}
        />
      </RadixProgress.Root>
    </div>
  )
}
