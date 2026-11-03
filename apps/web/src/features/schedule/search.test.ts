import { describe, expect, it } from 'vitest'
import { validateScheduleSearch } from './search'

describe('validateScheduleSearch', () => {
  it('sem parâmetros não decide nada', () => {
    expect(validateScheduleSearch({})).toEqual({})
  })

  it('aceita o marco aberto, que é um id', () => {
    const id = '0190a1b2-c3d4-7e5f-8a9b-0c1d2e3f4a5b'
    expect(validateScheduleSearch({ marco: id })).toEqual({ marco: id })
  })

  it('descarta o marco que não é um id, sem quebrar a página', () => {
    expect(validateScheduleSearch({ marco: 'não é um id' })).toEqual({})
    expect(validateScheduleSearch({ marco: 42 })).toEqual({})
    expect(validateScheduleSearch({ marco: '' })).toEqual({})
  })

  it('descarta o que não conhece, inclusive a aba, que ainda não existe', () => {
    expect(validateScheduleSearch({ aba: 'calendario', lixo: 1, estado: 'concluido' })).toEqual({})
  })
})
