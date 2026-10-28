import { describe, expect, it } from 'vitest'
import type { ScopeCategory, ScopeGroup } from '../api/scope'
import { filterGroups, groupByStatus, hasActiveFilters, highlightFor } from './scope-filters'

const EVAL = { priority: null, note: null, version: 1 } as const

function category(over: Partial<ScopeCategory> & { id: string; name: string }): ScopeCategory {
  return {
    group_id: 'g1',
    position: 0,
    origin: 'catalogo',
    hidden: false,
    visible: true,
    status: 'Em discussão',
    estimate_cents: null,
    discard_reason: null,
    noivo: EVAL,
    noiva: EVAL,
    alignment: { state: 'falta', missing: ['Noivo', 'Noiva'] },
    can_delete: false,
    version: 1,
    ...over,
  }
}

function group(
  over: Partial<ScopeGroup> & { id: string; categories: ScopeCategory[] },
): ScopeGroup {
  return {
    name: `Grupo ${over.id}`,
    position: 0,
    origin: 'catalogo',
    hidden: false,
    can_delete: false,
    version: 1,
    ...over,
  }
}

const GROUPS: ScopeGroup[] = [
  group({
    id: 'g1',
    categories: [
      category({ id: 'a', name: 'A Exemplo', status: 'Entra (Essencial)' }),
      category({
        id: 'b',
        name: 'B Exemplo',
        alignment: { state: 'divergem', missing: [] },
        noivo: { ...EVAL, priority: 'Quero muito' },
        noiva: { ...EVAL, priority: 'Dispenso' },
      }),
      category({ id: 'c', name: 'C Exemplo', hidden: true, visible: false }),
    ],
  }),
  group({
    id: 'g2',
    hidden: true,
    categories: [category({ id: 'd', name: 'D Exemplo', visible: false })],
  }),
  group({ id: 'g3', categories: [] }),
]

const ids = (groups: ScopeGroup[]) => groups.flatMap((g) => g.categories.map((c) => c.id))

describe('filterGroups', () => {
  it('sem filtros mostra só o que está visível e mantém o grupo vazio e visível', () => {
    const result = filterGroups(GROUPS, {}, 'Noivo')
    expect(ids(result)).toEqual(['a', 'b'])
    expect(result.map((g) => g.id)).toEqual(['g1', 'g3'])
  })

  it('mostrar ocultas traz as ocultas e os grupos ocultos', () => {
    const result = filterGroups(GROUPS, { ocultas: true }, 'Noivo')
    expect(ids(result)).toEqual(['a', 'b', 'c', 'd'])
    expect(result.map((g) => g.id)).toEqual(['g1', 'g2', 'g3'])
  })

  it('filtra por status e some com o grupo que ficou sem nada', () => {
    const result = filterGroups(GROUPS, { status: 'entra' }, 'Noivo')
    expect(ids(result)).toEqual(['a'])
    expect(result.map((g) => g.id)).toEqual(['g1'])
  })

  it('filtra por alinhamento', () => {
    expect(ids(filterGroups(GROUPS, { alinhamento: 'divergem' }, 'Noivo'))).toEqual(['b'])
    expect(ids(filterGroups(GROUPS, { alinhamento: 'falta' }, 'Noivo'))).toEqual(['a'])
  })

  it('"só o que falta eu avaliar" olha a prioridade do perfil da sessão', () => {
    expect(ids(filterGroups(GROUPS, { pendente: true }, 'Noivo'))).toEqual(['a'])
    // a Noiva já avaliou B, o Noivo também; A falta para os dois
    const sessao = filterGroups(GROUPS, { pendente: true }, 'Noiva')
    expect(ids(sessao)).toEqual(['a'])
  })

  it('combina os filtros: todos precisam valer', () => {
    expect(
      ids(filterGroups(GROUPS, { status: 'entra', alinhamento: 'divergem' }, 'Noivo')),
    ).toEqual([])
  })
})

describe('groupByStatus', () => {
  it('separa por status, na ordem dos quatro, mantendo a ordem de entrada', () => {
    const cats = filterGroups(GROUPS, { ocultas: true }, 'Noivo').flatMap((g) => g.categories)
    const result = groupByStatus(cats)
    expect(result.map((r) => r.status)).toEqual([
      'Em discussão',
      'Entra (Essencial)',
      'Talvez (Se couber)',
      'Fica de fora',
    ])
    expect(result[0]?.categories.map((c) => c.id)).toEqual(['b', 'c', 'd'])
    expect(result[1]?.categories.map((c) => c.id)).toEqual(['a'])
    expect(result[3]?.categories).toEqual([])
  })
})

describe('hasActiveFilters', () => {
  it('diz se algum filtro está ligado; mostrar ocultas não conta como filtro', () => {
    expect(hasActiveFilters({})).toBe(false)
    expect(hasActiveFilters({ ocultas: true })).toBe(false)
    expect(hasActiveFilters({ status: 'fora' })).toBe(true)
    expect(hasActiveFilters({ pendente: true })).toBe(true)
  })
})

describe('highlightFor (a lente destaca, nunca esconde)', () => {
  const [a, b] = GROUPS[0]?.categories ?? []

  it('Minha visão destaca o que falta a minha avaliação', () => {
    expect(a && highlightFor(a, 'minha', 'Noivo')).toBe('mine-missing')
    expect(b && highlightFor(b, 'minha', 'Noivo')).toBeNull()
    expect(b && highlightFor(b, 'minha', 'Noiva')).toBeNull()
  })

  it('Casal destaca o que diverge', () => {
    expect(b && highlightFor(b, 'casal', 'Noivo')).toBe('diverge')
    expect(a && highlightFor(a, 'casal', 'Noivo')).toBeNull()
  })

  it('o destaque de uma lente não aparece na outra', () => {
    expect(b && highlightFor(b, 'minha', 'Noivo')).toBeNull()
    expect(a && highlightFor(a, 'casal', 'Noiva')).toBeNull()
  })
})
