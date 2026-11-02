/** Data em tabela (`26/10/2026`), a partir de `AAAA-MM-DD`. */
export function formatTableDay(iso: string): string {
  const [year, month, day] = iso.split('-')
  return `${day}/${month}/${year}`
}
