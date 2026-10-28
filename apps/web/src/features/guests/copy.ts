import type { AgeBand, GuestStatus, Probability, Side } from './api/guests'

export const copy = {
  eyebrow: 'Convidados',
  title: 'Quem estará com vocês',
  description: 'A lista de quem vem com vocês, por núcleo familiar.',
  list: {
    title: 'Lista de convidados',
    loading: 'Carregando a lista de convidados…',
    loadError: {
      title: 'Não conseguimos carregar a lista agora.',
      description: 'Confira a conexão e tente de novo.',
      retry: 'Tentar de novo',
    },
    empty: {
      title: 'Ainda sem convidados',
      description:
        'Comecem por um núcleo, uma família ou um grupo, e acrescentem as pessoas dele em sequência.',
    },
    tableLabel: 'Convidados por núcleo',
    tableCaption: 'Núcleos e pessoas da lista de convidados',
    columns: {
      name: 'Nome',
      band: 'Faixa',
      probability: 'Probabilidade',
      status: 'Status',
      contact: 'Contato',
    },
  },
  household: {
    open: (name: string) => `Abrir ${name}`,
    people: (count: number) => (count === 1 ? '1 pessoa' : `${count} pessoas`),
    summary: (total: number, confirmed: number) =>
      `${confirmed} de ${total} ${total === 1 ? 'confirmado' : 'confirmados'}`,
    declined: (count: number) => (count === 1 ? '1 não irá' : `${count} não irão`),
  },
  sides: { Noivo: 'Noivo', Noiva: 'Noiva', Comum: 'Comum' } satisfies Record<Side, string>,
  bands: {
    Adulto: 'Adulto',
    'Criança pagante': 'Criança pagante',
    'Criança isenta': 'Criança isenta',
  } satisfies Record<AgeBand, string>,
  probabilities: {
    Certeza: 'Certeza',
    Provável: 'Provável',
    'Fase 2': 'Fase 2',
  } satisfies Record<Probability, string>,
  statuses: {
    Rascunho: 'Rascunho',
    Convidado: 'Convidado',
    Confirmado: 'Confirmado',
    'Não irá': 'Não irá',
  } satisfies Record<GuestStatus, string>,
  companion: {
    of: (holder: string) => `Acompanhante de ${holder}`,
    unnamed: 'Acompanhante a confirmar',
  },
  whatsapp: {
    label: 'Abrir WhatsApp',
    for: (name: string) => `Abrir WhatsApp de ${name}`,
  },
  sheet: {
    description: (side: string, summary: string) => `Lado ${side.toLowerCase()} · ${summary}`,
    people: 'Pessoas',
    address: 'Endereço do núcleo',
    noAddress: 'Ainda sem endereço.',
    note: 'Observação',
    age: (years: number) => (years === 1 ? '1 ano' : `${years} anos`),
    dietary: 'Restrição alimentar',
    declineReason: 'Motivo',
    phone: 'Telefone',
    email: 'E-mail',
    personNote: 'Observação',
  },
} as const
