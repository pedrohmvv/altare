const UNITS = ['B', 'KB', 'MB', 'GB'] as const
const NUMBER = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 })

/** O tamanho de um arquivo em pt-BR (`1,4 MB`), base 1024, com uma casa e o espaço que não quebra. */
export function formatBytes(bytes: number): string {
  if (!Number.isInteger(bytes) || bytes < 0) {
    throw new RangeError(`O tamanho deve ser um inteiro não negativo, mas veio ${bytes}`)
  }
  let value = bytes
  let unit = 0
  while (unit < UNITS.length - 1 && Math.round(value * 10) / 10 >= 1024) {
    value /= 1024
    unit += 1
  }
  return `${NUMBER.format(value)} ${UNITS[unit]}`
}
