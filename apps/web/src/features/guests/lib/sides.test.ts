import { describe, expect, it } from 'vitest'
import { visibleSides } from './sides'

describe('lado visível pela lente (F-CNV-07)', () => {
  it('na lente Casal mostra todos os lados', () => {
    expect(visibleSides({ lens: 'casal', profile: 'Noivo', includeOther: false })).toBeUndefined()
    expect(visibleSides({ lens: 'casal', profile: 'Noiva', includeOther: false })).toBeUndefined()
  })

  it('na Minha visão do Noivo mostra o lado dele mais o Comum', () => {
    expect(visibleSides({ lens: 'minha', profile: 'Noivo', includeOther: false })).toEqual([
      'Noivo',
      'Comum',
    ])
  })

  it('na Minha visão da Noiva mostra o lado dela mais o Comum', () => {
    expect(visibleSides({ lens: 'minha', profile: 'Noiva', includeOther: false })).toEqual([
      'Noiva',
      'Comum',
    ])
  })

  it('o outro lado fica a um toque: com "mostrar também o outro lado" volta a mostrar todos', () => {
    expect(visibleSides({ lens: 'minha', profile: 'Noivo', includeOther: true })).toBeUndefined()
  })
})
