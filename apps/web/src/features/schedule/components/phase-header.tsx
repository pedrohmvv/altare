import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/cn'
import { copy } from '../copy'

export interface PhaseHeaderProps {
  /** A posição da fase na ordem do cronograma, a partir de 1. */
  number: number
  title: string
  /** Quantos marcos ativos estão concluídos, e quantos há (a API não conta os arquivados). */
  done: number
  total: number
  /** No celular a fase é um título de seção, com a barra; na tabela é o texto do grupo de linhas. */
  variant: 'section' | 'row'
  titleId?: string
}

/** Rótulo "Fase N", o título em serifa e o progresso por escrito (design-system.md §9, `PhaseHeader`). */
export function PhaseHeader({ number, title, done, total, variant, titleId }: PhaseHeaderProps) {
  const progress = copy.phase.progress(done, total)
  const Title = variant === 'section' ? 'h2' : 'span'
  return (
    <div
      className={cn(
        'flex flex-col gap-1',
        variant === 'row' && 'sm:flex-row sm:flex-wrap sm:items-end sm:gap-x-4',
      )}
    >
      <div className="flex flex-col gap-0.5">
        <span className="text-eyebrow text-ink-muted">{copy.phase.label(number)}</span>
        <Title id={titleId} className="text-name text-ink">
          {title}
        </Title>
      </div>
      {variant === 'section' ? (
        <Progress value={done} max={total} label={progress} />
      ) : (
        <span className="text-num-sm text-ink-muted">{progress}</span>
      )}
    </div>
  )
}
