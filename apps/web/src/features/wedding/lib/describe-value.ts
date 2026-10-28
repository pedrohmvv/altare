import type { components } from '@/lib/api/schema'
import { formatDay, formatMonthYear } from '@/lib/date'
import { formatMoney } from '@/lib/money'
import type { BaselineKey } from '../api/baseline'

type Schemas = components['schemas']

/** O valor de um campo como a API o devolve: cada chave tem o seu formato. */
export type ValueOut =
  | Schemas['DateValueSchema']
  | Schemas['SizeValueSchema']
  | Schemas['CeilingValueSchema']
  | Schemas['CeremonyValueSchema']
  | string
  | null
  | undefined

function isObject(value: ValueOut): value is Exclude<ValueOut, string | null | undefined> {
  return typeof value === 'object' && value !== null
}

function describeDate(value: Schemas['DateValueSchema']): string | null {
  if (value.kind === 'exata' && value.exact) return formatDay(value.exact)
  if (value.kind === 'janela' && value.window_start && value.window_end) {
    const range = `${formatMonthYear(value.window_start.year, value.window_start.month)} a ${formatMonthYear(value.window_end.year, value.window_end.month)}`
    return value.label ? `${range} · ${value.label}` : range
  }
  return null
}

/** O valor em uma linha de texto, ou `null` quando o campo está vazio. */
export function describeValue(key: BaselineKey, value: ValueOut): string | null {
  if (value === null || value === undefined) return null
  switch (key) {
    case 'date':
      return isObject(value) && 'kind' in value ? describeDate(value) : null
    case 'city':
    case 'format':
      return typeof value === 'string' ? value : null
    case 'size':
      if (!isObject(value) || !('minimum' in value)) return null
      return value.minimum !== null && value.minimum !== undefined && value.maximum
        ? `${value.minimum} a ${value.maximum} convidados`
        : null
    case 'ceiling':
      if (!isObject(value) || !('cents' in value)) return null
      return value.cents === null || value.cents === undefined ? null : formatMoney(value.cents)
    case 'ceremony': {
      if (!isObject(value) || !('kinds' in value) || !value.kinds?.length) return null
      return value.detail ? `${value.kinds.join(', ')} · ${value.detail}` : value.kinds.join(', ')
    }
  }
}
