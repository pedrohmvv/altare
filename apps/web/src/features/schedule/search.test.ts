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

  it('aceita a avulsa aberta, que é um id (F-CRN-06)', () => {
    const id = '0190a1b2-c3d4-7e5f-8a9b-0c1d2e3f4a5b'
    expect(validateScheduleSearch({ avulsa: id })).toEqual({ avulsa: id })
  })

  it('descarta a avulsa que não é um id, sem quebrar a página', () => {
    expect(validateScheduleSearch({ avulsa: 'não é um id' })).toEqual({})
    expect(validateScheduleSearch({ avulsa: 7 })).toEqual({})
  })

  it('com marco e avulsa juntos, o marco vence e a avulsa é descartada', () => {
    const marco = '0190a1b2-c3d4-7e5f-8a9b-0c1d2e3f4a5b'
    const avulsa = '0190a1b2-c3d4-7e5f-8a9b-0c1d2e3f4a5c'
    expect(validateScheduleSearch({ marco, avulsa })).toEqual({ marco })
  })

  it('descarta o que não conhece, inclusive a aba, que ainda não existe', () => {
    expect(validateScheduleSearch({ aba: 'calendario', lixo: 1, estado: 'lixo' })).toEqual({})
  })

  it('aceita os filtros conhecidos, como slugs legíveis', () => {
    expect(
      validateScheduleSearch({
        responsavel: 'noiva',
        estado: 'em-andamento',
        atrasados: true,
        avulsas: 'true',
      }),
    ).toEqual({ responsavel: 'noiva', estado: 'em-andamento', atrasados: true, avulsas: true })
  })

  it('descarta o filtro de valor desconhecido, sem quebrar a página', () => {
    expect(
      validateScheduleSearch({
        responsavel: 'comum',
        estado: 'quase',
        atrasados: 'talvez',
        avulsas: 0,
      }),
    ).toEqual({})
  })

  it('os filtros convivem com o painel aberto', () => {
    const marco = '0190a1b2-c3d4-7e5f-8a9b-0c1d2e3f4a5b'
    expect(validateScheduleSearch({ marco, estado: 'bloqueado' })).toEqual({
      marco,
      estado: 'bloqueado',
    })
  })

  it('não há busca por texto, nem a lente (que é do roteador raiz)', () => {
    expect(validateScheduleSearch({ busca: 'x', q: 'x', lente: 'minha' })).toEqual({})
  })
})
