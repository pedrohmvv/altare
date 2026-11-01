import { describe, expect, it } from 'vitest'
import { guest, household } from '@/test/guest-fixtures'
import { countGuests, filterHouseholds, normalizeText, visibleGuestIds } from './guest-filters'

const LISTA = [
  household({
    id: 'n-silva',
    name: 'Família Silva Exemplo',
    side: 'Noivo',
    invite_sent_on: '2026-10-20',
    invite_channel: 'WhatsApp',
    guests: [
      guest({
        id: 'a',
        household_id: 'n-silva',
        name: 'Maria da Silva Exemplo',
        status: 'Confirmado',
      }),
      guest({
        id: 'b',
        household_id: 'n-silva',
        name: 'João Exemplo',
        band: 'Criança pagante',
        age: 9,
        probability: 'Certeza',
        dietary_restriction: 'Sem lactose',
      }),
    ],
  }),
  household({
    id: 'n-souza',
    name: 'Família Souza Exemplo',
    side: 'Noiva',
    guests: [
      guest({ id: 'c', household_id: 'n-souza', name: 'Ana Silva Exemplo', status: 'Não irá' }),
      guest({ id: 'd', household_id: 'n-souza', name: 'Lúcia Exemplo', probability: 'Fase 2' }),
    ],
  }),
  household({
    id: 'n-comum',
    name: 'Amigos Exemplo',
    side: 'Comum',
    guests: [guest({ id: 'e', household_id: 'n-comum', name: 'Pedro Exemplo' })],
  }),
]

const ids = (households: ReturnType<typeof filterHouseholds>) =>
  households.flatMap((h) => h.guests.map((g) => g.id))

describe('normalizeText', () => {
  it('ignora caixa, acento e espaços repetidos', () => {
    expect(normalizeText('  Família   SILVA ')).toBe('familia silva')
    expect(normalizeText('Lúcia')).toBe(normalizeText('lucia'))
  })
})

describe('busca (F-CNV-07)', () => {
  it('"silva" encontra o núcleo Família Silva e a Maria da Silva', () => {
    const result = filterHouseholds(LISTA, {}, 'silva')

    expect(result.map((h) => h.id)).toEqual(['n-silva', 'n-souza'])
    // O nome do núcleo bate: todos os dele entram. Em Souza, só quem tem Silva no nome.
    expect(ids(result)).toEqual(['a', 'b', 'c'])
  })

  it('não diferencia maiúsculas nem acentos', () => {
    expect(ids(filterHouseholds(LISTA, {}, 'LUCIA'))).toEqual(['d'])
  })

  it('sem texto não filtra nada', () => {
    expect(ids(filterHouseholds(LISTA, {}, '  '))).toEqual(['a', 'b', 'c', 'd', 'e'])
  })
})

describe('filtros (F-CNV-07)', () => {
  it('lado filtra o núcleo', () => {
    expect(filterHouseholds(LISTA, { side: 'Noiva' }, '').map((h) => h.id)).toEqual(['n-souza'])
  })

  it('faixa, probabilidade e status filtram as pessoas e escondem o núcleo sem ninguém', () => {
    expect(ids(filterHouseholds(LISTA, { band: 'Criança pagante' }, ''))).toEqual(['b'])
    expect(ids(filterHouseholds(LISTA, { probability: 'Fase 2' }, ''))).toEqual(['d'])
    expect(filterHouseholds(LISTA, { status: 'Confirmado' }, '').map((h) => h.id)).toEqual([
      'n-silva',
    ])
  })

  it('convite não enviado lista só os núcleos sem data', () => {
    // F-CNV-05
    expect(filterHouseholds(LISTA, { withoutInvite: true }, '').map((h) => h.id)).toEqual([
      'n-souza',
      'n-comum',
    ])
  })

  it('com restrição alimentar lista só quem tem uma', () => {
    expect(ids(filterHouseholds(LISTA, { withDietary: true }, ''))).toEqual(['b'])
  })

  it('os filtros se combinam', () => {
    const result = filterHouseholds(LISTA, { side: 'Noivo', status: 'Confirmado' }, 'silva')

    expect(ids(result)).toEqual(['a'])
  })

  it('o resumo do núcleo continua o real, mesmo com a pessoa escondida', () => {
    const [silva] = filterHouseholds(LISTA, { status: 'Confirmado' }, '')

    expect(silva?.guests).toHaveLength(1)
    expect(silva?.summary.total).toBe(2)
  })
})

describe('lente (F-CNV-07)', () => {
  it('só os lados visíveis aparecem; um filtro de lado explícito vence a lente', () => {
    expect(filterHouseholds(LISTA, {}, '', ['Noivo', 'Comum']).map((h) => h.id)).toEqual([
      'n-silva',
      'n-comum',
    ])
    expect(filterHouseholds(LISTA, { side: 'Noiva' }, '', undefined).map((h) => h.id)).toEqual([
      'n-souza',
    ])
  })
})

describe('contagem e exportação', () => {
  it('conta as pessoas visíveis e entrega os ids na ordem da lista', () => {
    const result = filterHouseholds(LISTA, { side: 'Noivo' }, '')

    expect(countGuests(result)).toBe(2)
    expect(visibleGuestIds(result)).toEqual(['a', 'b'])
    expect(countGuests(LISTA)).toBe(5)
  })

  it('o filtro nunca inventa nem repete uma pessoa', () => {
    for (const filters of [{}, { side: 'Noivo' as const }, { status: 'Rascunho' as const }]) {
      const all = visibleGuestIds(LISTA)
      const part = visibleGuestIds(filterHouseholds(LISTA, filters, ''))
      expect(new Set(part).size).toBe(part.length)
      expect(part.every((id) => all.includes(id))).toBe(true)
    }
  })
})
