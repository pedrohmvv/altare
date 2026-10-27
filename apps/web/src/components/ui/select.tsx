import { Check, ChevronDown } from 'lucide-react'
import { Select as RadixSelect } from 'radix-ui'
import { cn } from '@/lib/cn'
import { Field } from './field'

export interface SelectOption {
  value: string
  label: string
  disabled?: boolean
}

export interface SelectProps {
  label: string
  options: SelectOption[]
  /** Texto mostrado enquanto nada foi escolhido. */
  placeholder?: string
  hint?: string
  error?: string
  required?: boolean
  disabled?: boolean
  value?: string
  defaultValue?: string
  onValueChange?: (value: string) => void
  name?: string
  id?: string
  className?: string
}

/** Lista de opções própria do app (Radix Select), com teclado e leitor de tela (D-047). */
export function Select({
  label,
  options,
  placeholder,
  hint,
  error,
  required,
  disabled,
  id,
  className,
  ...root
}: SelectProps) {
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
        <RadixSelect.Root {...root} disabled={disabled} required={required}>
          <RadixSelect.Trigger
            {...control}
            className={cn(
              'flex h-10 w-full items-center justify-between gap-2 rounded-control border bg-surface px-3',
              'text-left text-body text-ink transition-colors duration-fast ease-standard',
              'max-md:h-12 pointer-coarse:min-h-11 disabled:cursor-default disabled:opacity-40',
              'data-[placeholder]:text-ink-subtle',
              error ? 'border-attention-ink' : 'border-border-strong',
            )}
          >
            <RadixSelect.Value placeholder={placeholder} />
            <RadixSelect.Icon asChild>
              <ChevronDown aria-hidden className="size-5 shrink-0 text-ink-muted" />
            </RadixSelect.Icon>
          </RadixSelect.Trigger>
          <RadixSelect.Portal>
            <RadixSelect.Content
              position="popper"
              sideOffset={4}
              className={cn(
                'z-50 max-h-(--radix-select-content-available-height) w-(--radix-select-trigger-width)',
                'overflow-hidden rounded-card border border-border bg-surface shadow-nivel-1',
                '[--focus-gap:var(--surface)]',
              )}
            >
              <RadixSelect.Viewport className="p-1">
                {options.map((option) => (
                  <RadixSelect.Item
                    key={option.value}
                    value={option.value}
                    disabled={option.disabled}
                    className={cn(
                      'flex min-h-9 cursor-default items-center justify-between gap-2 rounded-control px-3 py-2',
                      'text-body text-ink outline-none pointer-coarse:min-h-11',
                      'data-[highlighted]:bg-surface-muted data-[state=checked]:font-medium',
                      'data-[disabled]:opacity-40',
                    )}
                  >
                    <RadixSelect.ItemText>{option.label}</RadixSelect.ItemText>
                    <RadixSelect.ItemIndicator>
                      <Check aria-hidden className="size-4 text-primary" />
                    </RadixSelect.ItemIndicator>
                  </RadixSelect.Item>
                ))}
              </RadixSelect.Viewport>
            </RadixSelect.Content>
          </RadixSelect.Portal>
        </RadixSelect.Root>
      )}
    </Field>
  )
}
