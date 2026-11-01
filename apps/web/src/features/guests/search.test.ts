import { describe, expect, it } from 'vitest'
import { validateGuestsSearch } from './search'

const ID = '0192f4e0-7c1a-7b3e-8f21-3d6a9b1c4e55'

describe('validateGuestsSearch', () => {
  it('sem parâmetros devolve vazio', () => {
    expect(validateGuestsSearch({})).toEqual({})
  })

  it('guarda o núcleo aberto quando é um UUID', () => {
    expect(validateGuestsSearch({ nucleo: ID })).toEqual({ nucleo: ID })
  })

  it('guarda os filtros conhecidos', () => {
    expect(
      validateGuestsSearch({
        lado: 'noiva',
        faixa: 'pagante',
        probabilidade: 'fase2',
        status: 'nao-ira',
        semconvite: true,
        restricao: 'true',
        outro: true,
      }),
    ).toEqual({
      lado: 'noiva',
      faixa: 'pagante',
      probabilidade: 'fase2',
      status: 'nao-ira',
      semconvite: true,
      restricao: true,
      outro: true,
    })
  })

  it('descarta valor desconhecido em vez de virar erro', () => {
    expect(
      validateGuestsSearch({
        nucleo: 'qualquer-coisa',
        lado: 'banana',
        faixa: 42,
        status: 'Confirmado',
        semconvite: 'false',
        lixo: 'x',
      }),
    ).toEqual({})
  })

  it('a busca por nome nunca entra na URL', () => {
    expect(validateGuestsSearch({ busca: 'Convidado Exemplo', q: 'silva' })).toEqual({})
  })
})
