import { useState } from 'react'
import { formatMoneyPlain, parseMoney } from '@/lib/money'
import { Input, type InputProps } from './input'

export type MoneyInputProps = Omit<
  InputProps,
  'value' | 'defaultValue' | 'onChange' | 'type' | 'prefix' | 'suffix' | 'inputMode'
> & {
  /** Valor em centavos inteiros; `null` é campo vazio, nunca zero. */
  value: number | null
  onValueChange: (cents: number | null) => void
  /** O que o campo diz quando o texto não é um valor; um `error` de fora vence. */
  unreadableMessage?: string
}

const toText = (cents: number | null) => (cents === null ? '' : formatMoneyPlain(cents))

/**
 * Campo de dinheiro (design-system.md §9): a pessoa digita reais com máscara pt-BR e quem usa o
 * componente só enxerga centavos inteiros. Texto que não dá para ler vira `null` e um erro, em vez
 * de um número adivinhado.
 */
export function MoneyInput({
  value,
  onValueChange,
  error,
  unreadableMessage = 'Informe o valor em reais, como 28.000,00.',
  onBlur,
  ...props
}: MoneyInputProps) {
  const [text, setText] = useState(() => toText(value))
  const [seen, setSeen] = useState(value)

  // O valor mudou por fora (restaurar o formulário): o texto o acompanha, menos quando já o diz.
  if (value !== seen) {
    setSeen(value)
    if (value !== parseMoney(text)) setText(toText(value))
  }

  const unreadable = text.trim() !== '' && parseMoney(text) === null

  return (
    <Input
      {...props}
      prefix="R$"
      inputMode="decimal"
      autoComplete="off"
      inputClassName="font-mono tabular-nums"
      value={text}
      error={error ?? (unreadable ? unreadableMessage : undefined)}
      onChange={(event) => {
        const next = event.target.value
        const cents = parseMoney(next)
        setText(next)
        setSeen(cents)
        onValueChange(cents)
      }}
      onBlur={(event) => {
        const cents = parseMoney(text)
        if (cents !== null) setText(formatMoneyPlain(cents))
        onBlur?.(event)
      }}
    />
  )
}
