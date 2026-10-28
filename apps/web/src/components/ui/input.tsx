import type { ComponentProps, ReactNode } from 'react'
import { cn } from '@/lib/cn'
import { Field } from './field'

export type InputProps = Omit<ComponentProps<'input'>, 'prefix' | 'id'> & {
  id?: string
  label: string
  hint?: string
  error?: string
  /** Texto fixo antes do valor (ex.: "R$"); fica fora do valor digitado. */
  prefix?: ReactNode
  /** Texto fixo depois do valor (ex.: "por pessoa"); fica fora do valor digitado. */
  suffix?: ReactNode
  /** Acrescenta classes ao `<input>` em si (o campo de dinheiro usa mono tabular). */
  inputClassName?: string
}

export function Input({
  id,
  label,
  hint,
  error,
  required,
  prefix,
  suffix,
  className,
  inputClassName,
  ...props
}: InputProps) {
  return (
    <Field
      label={label}
      hint={hint}
      error={error}
      required={required}
      id={id}
      className={className}
    >
      {(control) => {
        const prefixId = `${control.id}-prefix`
        const suffixId = `${control.id}-suffix`
        const describedBy = [
          control['aria-describedby'],
          prefix != null && prefixId,
          suffix != null && suffixId,
        ]
          .filter(Boolean)
          .join(' ')

        return (
          <div
            className={cn(
              'flex min-h-11 items-center gap-2 rounded-control border bg-surface px-3',
              'transition-colors duration-fast ease-standard',
              error ? 'border-attention-ink' : 'border-border-strong',
              'has-[input:focus-visible]:shadow-[0_0_0_2px_var(--focus-gap,var(--canvas)),0_0_0_4px_var(--focus-ring)]',
              'has-[input:disabled]:opacity-40',
            )}
          >
            {prefix != null && (
              <span id={prefixId} className="text-body-sm text-ink-muted">
                {prefix}
              </span>
            )}
            <input
              {...props}
              {...control}
              aria-describedby={describedBy || undefined}
              className={cn(
                'min-w-0 flex-1 bg-transparent py-2 text-body text-ink outline-none placeholder:text-ink-subtle focus-visible:shadow-none disabled:cursor-default',
                inputClassName,
              )}
            />
            {suffix != null && (
              <span id={suffixId} className="text-body-sm text-ink-muted">
                {suffix}
              </span>
            )}
          </div>
        )
      }}
    </Field>
  )
}
