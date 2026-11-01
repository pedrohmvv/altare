import type { Guest, GuestList, Household } from '@/features/guests/api/guests'

type Counts = GuestList['headcount']['total_nominal']

export function guest(over: Partial<Guest> = {}): Guest {
  return {
    id: 'p-a',
    household_id: 'n-a',
    name: 'Convidado Exemplo A',
    companion_of_id: null,
    holder_name: null,
    band: 'Adulto',
    age: null,
    suggested_band: null,
    probability: 'Provável',
    status: 'Rascunho',
    decline_reason: null,
    dietary_restriction: null,
    note: null,
    phone: null,
    whatsapp_url: null,
    email: null,
    version: 1,
    ...over,
  }
}

export function household(over: Partial<Household> = {}): Household {
  const guests = over.guests ?? [guest()]
  return {
    id: 'n-a',
    name: 'Família Exemplo',
    side: 'Comum',
    street: null,
    number: null,
    complement: null,
    district: null,
    city: null,
    state: null,
    postal_code: null,
    note: null,
    summary: {
      total: guests.length,
      confirmed: guests.filter((g) => g.status === 'Confirmado').length,
      invited: guests.filter((g) => g.status === 'Convidado').length,
      draft: guests.filter((g) => g.status === 'Rascunho').length,
      declined: guests.filter((g) => g.status === 'Não irá').length,
    },
    version: 1,
    ...over,
    guests,
  }
}

const counts = (guests: Guest[]): Counts => {
  const adults = guests.filter((g) => g.band === 'Adulto').length
  const paying = guests.filter((g) => g.band === 'Criança pagante').length
  const exempt = guests.filter((g) => g.band === 'Criança isenta').length
  return { adults, paying_children: paying, exempt_children: exempt, total: guests.length }
}

/**
 * Uma lista completa a partir dos núcleos: os contadores saem de uma contagem simples (sem pesos, o
 * ponderado é nulo) e as configurações vêm vazias, como o servidor as devolve no começo.
 */
export function listOf(
  households: Household[],
  settings: Partial<GuestList['settings']> = {},
): GuestList {
  const everyone = households.flatMap((h) => h.guests)
  const attending = everyone.filter((g) => g.status !== 'Não irá')
  return {
    households,
    headcount: {
      total_nominal: counts(attending),
      confirmed: counts(attending.filter((g) => g.status === 'Confirmado')),
      not_attending: counts(everyone.filter((g) => g.status === 'Não irá')),
      certain_or_confirmed: counts(
        attending.filter((g) => g.probability === 'Certeza' || g.status === 'Confirmado'),
      ),
      weighted_adults_hundredths: null,
      weighted_paying_children_hundredths: null,
      weighted_rounded_up: null,
    },
    settings: {
      weights: null,
      exempt_until_age: null,
      paying_until_age: null,
      version: 1,
      ...settings,
    },
  }
}

/** Uma lista de exemplo com dois núcleos, um acompanhante sem nome e um celular com WhatsApp. */
export const LIST: GuestList = listOf([
  household({
    id: 'n-a',
    name: 'Família Exemplo',
    side: 'Noivo',
    street: 'Rua Exemplo',
    number: '100',
    city: 'Cidade Exemplo',
    state: 'SP',
    postal_code: '00000-000',
    note: 'Convite impresso.',
    guests: [
      guest({
        id: 'p-a',
        name: 'Convidado Exemplo A',
        status: 'Confirmado',
        phone: '(11) 91234-5678',
        whatsapp_url: 'https://wa.me/5511912345678',
        email: 'convidado@exemplo.invalid',
        dietary_restriction: 'Sem lactose',
      }),
      guest({
        id: 'p-b',
        name: null,
        companion_of_id: 'p-a',
        holder_name: 'Convidado Exemplo A',
      }),
      guest({
        id: 'p-c',
        name: 'Convidado Exemplo C',
        band: 'Criança pagante',
        age: 9,
        probability: 'Certeza',
        status: 'Não irá',
        decline_reason: 'Viagem',
      }),
    ],
  }),
  household({
    id: 'n-b',
    name: 'Outra Família Exemplo',
    side: 'Noiva',
    guests: [
      guest({
        id: 'p-d',
        household_id: 'n-b',
        name: 'Convidado Exemplo D',
        phone: '(11) 3456-7890',
      }),
    ],
  }),
])
