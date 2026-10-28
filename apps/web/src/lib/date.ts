const SHORT_MONTHS = [
  'jan',
  'fev',
  'mar',
  'abr',
  'mai',
  'jun',
  'jul',
  'ago',
  'set',
  'out',
  'nov',
  'dez',
] as const

const MONTH_NAMES = [
  'janeiro',
  'fevereiro',
  'março',
  'abril',
  'maio',
  'junho',
  'julho',
  'agosto',
  'setembro',
  'outubro',
  'novembro',
  'dezembro',
] as const

/** Os doze meses, no formato das opções do `Select`; o valor é o número do mês, de 1 a 12. */
export const MONTHS = MONTH_NAMES.map((label, index) => ({ value: String(index + 1), label }))

/** `mar 2027`. */
export function formatMonthYear(year: number, month: number): string {
  if (!Number.isInteger(month) || month < 1 || month > 12) {
    throw new RangeError(`O mês deve ir de 1 a 12, mas veio ${month}`)
  }
  return `${SHORT_MONTHS[month - 1]} ${year}`
}

/** Data em lista, como no guia (`26 out 2026`), a partir de `AAAA-MM-DD`. */
export function formatDay(iso: string): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso)
  const year = Number(match?.[1])
  const month = Number(match?.[2])
  const day = Number(match?.[3])
  if (!match || month < 1 || month > 12 || day < 1 || day > 31) {
    throw new RangeError(`Data inválida: ${iso}`)
  }
  return `${day} ${SHORT_MONTHS[month - 1]} ${year}`
}

const SAO_PAULO = new Intl.DateTimeFormat('pt-BR', {
  timeZone: 'America/Sao_Paulo',
  year: 'numeric',
  month: 'numeric',
  day: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  hourCycle: 'h23',
})

/** Um instante (ISO-8601, em UTC) no horário de Brasília: `27 out 2026, 12:30`. */
export function formatInstant(iso: string): string {
  const parts = Object.fromEntries(
    SAO_PAULO.formatToParts(new Date(iso)).map((part) => [part.type, part.value]),
  )
  return `${parts.day} ${SHORT_MONTHS[Number(parts.month) - 1]} ${parts.year}, ${parts.hour}:${parts.minute}`
}
