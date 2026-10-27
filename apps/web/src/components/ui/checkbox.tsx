import { Check, Minus } from 'lucide-react'
import { Checkbox as RadixCheckbox } from 'radix-ui'
import { useId } from 'react'
import { cn } from '@/lib/cn'

export interface CheckboxProps {
  label: string
  checked?: boolean | 'indeterminate'
  defaultChecked?: boolean
  onCheckedChange?: (checked: boolean | 'indeterminate') => void
  disabled?: boolean
  id?: string
  className?: string
}

export function Checkbox({ label, id, className, disabled, ...props }: CheckboxProps) {
  const generatedId = useId()
  const controlId = id ?? generatedId

  return (
    <div className={cn('flex items-center gap-3 pointer-coarse:min-h-11', className)}>
      <RadixCheckbox.Root
        {...props}
        id={controlId}
        disabled={disabled}
        className={cn(
          'group flex size-5 shrink-0 items-center justify-center rounded-control border border-border-strong bg-surface',
          'text-primary-ink transition-colors duration-fast ease-standard',
          'data-[state=checked]:border-primary data-[state=checked]:bg-primary',
          'data-[state=indeterminate]:border-primary data-[state=indeterminate]:bg-primary',
          'disabled:opacity-40',
        )}
      >
        <RadixCheckbox.Indicator>
          <Check aria-hidden className="size-4 group-data-[state=indeterminate]:hidden" />
          <Minus aria-hidden className="hidden size-4 group-data-[state=indeterminate]:block" />
        </RadixCheckbox.Indicator>
      </RadixCheckbox.Root>
      <label
        htmlFor={controlId}
        className={cn('text-body text-ink', disabled && 'cursor-default opacity-40')}
      >
        {label}
      </label>
    </div>
  )
}
