import type { ComponentProps } from 'react'
import { cn } from '@/lib/cn'
import { Field } from './field'

export type TextareaProps = Omit<ComponentProps<'textarea'>, 'id'> & {
  id?: string
  label: string
  hint?: string
  error?: string
}

export function Textarea({ id, label, hint, error, required, className, ...props }: TextareaProps) {
  return (
    <Field
      label={label}
      hint={hint}
      error={error}
      required={required}
      id={id}
      className={className}
    >
      {(control) => (
        <textarea
          rows={4}
          {...props}
          {...control}
          className={cn(
            'min-h-24 resize-y rounded-control border bg-surface px-3 py-2 text-body text-ink',
            'transition-colors duration-fast ease-standard placeholder:text-ink-subtle',
            'disabled:cursor-default disabled:opacity-40',
            error ? 'border-attention-ink' : 'border-border-strong',
          )}
        />
      )}
    </Field>
  )
}
