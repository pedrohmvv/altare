import type { Household } from '../api/guests'

/** O endereço em linhas, só com o que foi preenchido; vazio devolve lista vazia. */
export function addressLines(household: Household): string[] {
  const street = [household.street, household.number].filter(Boolean).join(', ')
  const streetLine = [street, household.complement].filter(Boolean).join(' · ')
  const place = [household.district, household.city].filter(Boolean).join(' · ')
  const region = [household.state, household.postal_code].filter(Boolean).join(' · ')
  return [streetLine, place, region].filter((line) => line !== '')
}
