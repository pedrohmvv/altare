import { CircleAlert } from 'lucide-react'
import { type ReactNode, useId } from 'react'
import { cn } from '@/lib/cn'

export interface FieldControlProps {
  id: string
  'aria-describedby'?: string
  'aria-invalid'?: true
  'aria-required'?: true
}

export interface FieldProps {
  label: string
  hint?: string
  error?: string
  required?: boolean
  id?: string
  className?: string
  /** Recebe os atributos que ligam o controle ao rótulo, à ajuda e ao erro. */
  children: (control: FieldControlProps) => ReactNode
}

/** Rótulo acima, ajuda e erro ligados ao controle (design-system.md §10, item 1). */
export function Field({ label, hint, error, required, id, className, children }: FieldProps) {
  const generatedId = useId()
  const controlId = id ?? generatedId
  const hintId = `${controlId}-hint`
  const errorId = `${controlId}-error`
  const describedBy = [hint && hintId, error && errorId].filter(Boolean).join(' ')

  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      <label htmlFor={controlId} className="text-body-sm font-semibold text-ink">
        {label}
        {required && ' '}
        {required && <span className="font-normal text-ink-muted">(obrigatório)</span>}
      </label>
      {children({
        id: controlId,
        'aria-describedby': describedBy || undefined,
        'aria-invalid': error ? true : undefined,
        'aria-required': required ? true : undefined,
      })}
      {hint && (
        <p id={hintId} className="text-body-sm text-ink-muted">
          {hint}
        </p>
      )}
      {error && (
        <p id={errorId} className="flex items-start gap-1.5 text-body-sm text-attention-ink">
          <CircleAlert aria-hidden className="mt-0.5 size-4 shrink-0" />
          {error}
        </p>
      )}
    </div>
  )
}
