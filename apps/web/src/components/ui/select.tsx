import { Check, ChevronDown } from 'lucide-react'
import { Select as RadixSelect } from 'radix-ui'
import type { Ref } from 'react'
import { cn } from '@/lib/cn'
import { Field } from './field'

export interface SelectOption {
  value: string
  label: string
  disabled?: boolean
  /** Nome do grupo sob o qual a opção aparece; opções sem grupo vêm primeiro, sem título. */
  group?: string
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
  /** O botão que abre a lista: o formulário o usa para levar o foco ao campo com erro. */
  ref?: Ref<HTMLButtonElement>
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
  ref,
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
            ref={ref}
            className={cn(
              'flex h-11 w-full items-center justify-between gap-2 rounded-control border bg-surface px-3',
              'text-left text-body text-ink transition-colors duration-fast ease-standard',
              'disabled:cursor-default disabled:opacity-40',
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
                {options
                  .filter((option) => option.group === undefined)
                  .map((option) => (
                    <SelectItem key={option.value} option={option} />
                  ))}
                {groupNames(options).map((name) => (
                  <RadixSelect.Group key={name}>
                    <RadixSelect.Label className="px-3 pt-2 pb-1 text-eyebrow text-ink-muted">
                      {name}
                    </RadixSelect.Label>
                    {options
                      .filter((option) => option.group === name)
                      .map((option) => (
                        <SelectItem key={option.value} option={option} />
                      ))}
                  </RadixSelect.Group>
                ))}
              </RadixSelect.Viewport>
            </RadixSelect.Content>
          </RadixSelect.Portal>
        </RadixSelect.Root>
      )}
    </Field>
  )
}

const groupNames = (options: SelectOption[]) => [
  ...new Set(options.flatMap((option) => (option.group === undefined ? [] : [option.group]))),
]

function SelectItem({ option }: { option: SelectOption }) {
  return (
    <RadixSelect.Item
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
  )
}
