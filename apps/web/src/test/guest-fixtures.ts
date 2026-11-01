import type { Guest, GuestList, Household } from '@/features/guests/api/guests'

export function guest(over: Partial<Guest> = {}): Guest {
  return {
    id: 'p-a',
    household_id: 'n-a',
    name: 'Convidado Exemplo A',
    companion_of_id: null,
    holder_name: null,
    band: 'Adulto',
    age: null,
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

/** Uma lista de exemplo com dois núcleos, um acompanhante sem nome e um celular com WhatsApp. */
export const LIST: GuestList = {
  households: [
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
  ],
}
