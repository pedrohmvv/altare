import { cva } from 'class-variance-authority'
import type { ComponentProps } from 'react'
import { cn } from '@/lib/cn'
import { type FormatMoneyOptions, formatMoney } from '@/lib/money'

const moneyVariants = cva('font-mono tabular-nums', {
  variants: {
    tone: {
      default: '',
      comparable: 'text-accent-ink',
      muted: 'text-ink-muted',
      positive: 'text-consensus-ink',
      attention: 'text-attention-ink',
    },
  },
  defaultVariants: { tone: 'default' },
})

export type MoneyProps = Omit<ComponentProps<'span'>, 'children'> &
  FormatMoneyOptions & {
    /** Valor em centavos inteiros (nunca `float`). */
    cents: number
    /** `comparable` destaca os custos extras (terracota); `positive` e `attention` marcam teto e estouro. */
    tone?: 'default' | 'comparable' | 'muted' | 'positive' | 'attention'
  }

/** Exibe dinheiro em mono tabular. O tamanho vem do contexto (`text-num`, `text-num-lg`…). */
export function Money({ cents, precision, signed, tone, className, ...props }: MoneyProps) {
  return (
    <span className={cn(moneyVariants({ tone }), className)} {...props}>
      {formatMoney(cents, { precision, signed })}
    </span>
  )
}
