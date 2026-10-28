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

  it('descarta valor desconhecido em vez de virar erro', () => {
    expect(validateGuestsSearch({ nucleo: 'qualquer-coisa', lixo: 'x' })).toEqual({})
    expect(validateGuestsSearch({ nucleo: 42 })).toEqual({})
  })

  it('a busca por nome nunca entra na URL', () => {
    expect(validateGuestsSearch({ busca: 'Convidado Exemplo' })).toEqual({})
  })
})
