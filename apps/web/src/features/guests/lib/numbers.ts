const PEOPLE = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 })

/**
 * Centésimos de pessoa (100 = uma pessoa) em texto: "3,7". Só formata; a conta e o arredondamento
 * para cima são do servidor (stack.md §5.1).
 */
export function formatPeople(hundredths: number): string {
  return PEOPLE.format(hundredths / 100)
}
