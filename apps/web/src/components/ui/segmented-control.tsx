import { ToggleGroup } from 'radix-ui'
import { useState } from 'react'
import { cn } from '@/lib/cn'

export interface SegmentedControlOption {
  value: string
  label: string
  disabled?: boolean
}

export interface SegmentedControlProps {
  /** Nome do grupo, lido pelo leitor de tela. */
  'aria-label': string
  /** De 2 a 5 opções (design-system.md §8). */
  options: SegmentedControlOption[]
  value?: string
  defaultValue?: string
  onValueChange?: (value: string) => void
  className?: string
}

/** Escolha exclusiva entre poucas opções, sempre com uma selecionada (a lente de visão, por exemplo). */
export function SegmentedControl({
  options,
  value,
  defaultValue,
  onValueChange,
  className,
  ...props
}: SegmentedControlProps) {
  const [inner, setInner] = useState(defaultValue ?? '')
  const current = value ?? inner

  return (
    <ToggleGroup.Root
      type="single"
      value={current}
      onValueChange={(next) => {
        // O Radix devolve vazio ao clicar na opção já marcada; aqui sempre há uma escolhida.
        if (!next) return
        setInner(next)
        onValueChange?.(next)
      }}
      // Como no seletor de lente do guia: trilho afundado e a opção ativa em marfim, com hairline.
      className={cn(
        'inline-grid auto-cols-fr grid-flow-col gap-0.5 rounded-thumb bg-surface-sunken p-0.75',
        className,
      )}
      {...props}
    >
      {options.map((option) => (
        <ToggleGroup.Item
          key={option.value}
          value={option.value}
          disabled={option.disabled}
          className={cn(
            'inline-flex h-7 items-center justify-center rounded-control border border-transparent px-4',
            'text-body-sm font-medium whitespace-nowrap text-ink-muted transition-colors duration-fast ease-standard',
            'pointer-coarse:min-h-11 hover:text-ink disabled:cursor-default disabled:opacity-40',
            'data-[state=on]:border-border data-[state=on]:bg-surface data-[state=on]:font-semibold data-[state=on]:text-ink',
          )}
        >
          {option.label}
        </ToggleGroup.Item>
      ))}
    </ToggleGroup.Root>
  )
}
