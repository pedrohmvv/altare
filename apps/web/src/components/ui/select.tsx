import { ChevronDown } from 'lucide-react'
import type { ComponentProps } from 'react'
import { cn } from '@/lib/cn'
import { Field } from './field'

export type SelectProps = Omit<ComponentProps<'select'>, 'id'> & {
  id?: string
  label: string
  hint?: string
  error?: string
  /** Primeira opção, desabilitada, mostrada enquanto nada foi escolhido. */
  placeholder?: string
}

/** `<select>` nativo estilizado: o celular abre o seletor do sistema (D-046). */
export function Select({
  id,
  label,
  hint,
  error,
  required,
  placeholder,
  className,
  children,
  value,
  defaultValue,
  ...props
}: SelectProps) {
  const startsOnPlaceholder =
    placeholder != null && value === undefined && defaultValue === undefined

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
        <div className="relative">
          <select
            {...props}
            {...control}
            value={value}
            defaultValue={startsOnPlaceholder ? '' : defaultValue}
            className={cn(
              'h-10 w-full appearance-none rounded-control border bg-surface pr-10 pl-3 text-body text-ink',
              'transition-colors duration-fast ease-standard max-md:h-12 pointer-coarse:min-h-11',
              'disabled:cursor-default disabled:opacity-40',
              error ? 'border-attention-ink' : 'border-border-strong',
            )}
          >
            {placeholder != null && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {children}
          </select>
          <ChevronDown
            aria-hidden
            className="pointer-events-none absolute top-1/2 right-3 size-5 -translate-y-1/2 text-ink-muted"
          />
        </div>
      )}
    </Field>
  )
}
