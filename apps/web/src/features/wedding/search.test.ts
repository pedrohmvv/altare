import { describe, expect, it } from 'vitest'
import { validatePlanningSearch } from './search'

describe('validatePlanningSearch', () => {
  it('sem parâmetros não decide nada: a aba é a das Definições Base e a vista é por grupo', () => {
    expect(validatePlanningSearch({})).toEqual({})
  })

  it('aceita os valores conhecidos de cada parâmetro', () => {
    const id = '0190a1b2-c3d4-7e5f-8a9b-0c1d2e3f4a5b'
    expect(
      validatePlanningSearch({
        aba: 'escopo',
        vista: 'status',
        status: 'fora',
        alinhamento: 'divergem',
        pendente: true,
        ocultas: true,
        categoria: id,
      }),
    ).toEqual({
      aba: 'escopo',
      vista: 'status',
      status: 'fora',
      alinhamento: 'divergem',
      pendente: true,
      ocultas: true,
      categoria: id,
    })
  })

  it('descarta o que não conhece, sem quebrar a página', () => {
    expect(
      validatePlanningSearch({
        aba: 'outra',
        vista: 'grade',
        status: 'quase',
        alinhamento: 'tanto-faz',
        pendente: 'talvez',
        ocultas: 0,
        categoria: 'não é um id',
        lixo: 1,
      }),
    ).toEqual({})
  })

  it('aceita o booleano como texto, que é como chega de um link colado', () => {
    expect(validatePlanningSearch({ pendente: 'true', ocultas: 'false' })).toEqual({
      pendente: true,
    })
  })
})
