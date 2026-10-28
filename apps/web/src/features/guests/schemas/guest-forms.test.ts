import { describe, expect, it } from 'vitest'
import {
  EMPTY_GUEST,
  EMPTY_HOUSEHOLD,
  householdSchema,
  makeGuestSchema,
  toGuestBody,
  toHouseholdBody,
} from './guest-forms'

const household = (over = {}) => ({
  ...EMPTY_HOUSEHOLD,
  name: 'Família Exemplo',
  side: 'Comum',
  ...over,
})
const guest = (over = {}) => ({ ...EMPTY_GUEST, name: 'Convidado Exemplo A', ...over })
const issues = (result: { success: boolean; error?: { issues: { path: PropertyKey[] }[] } }) =>
  result.error?.issues.map((i) => i.path.join('.')) ?? []

describe('formulário do núcleo', () => {
  it('só o nome e o lado são obrigatórios', () => {
    expect(householdSchema.safeParse(household()).success).toBe(true)
    expect(issues(householdSchema.safeParse(household({ name: '  ', side: '' })))).toEqual([
      'name',
      'side',
    ])
  })

  it('confere o formato da UF e do CEP, e os limites de tamanho', () => {
    expect(
      householdSchema.safeParse(household({ state: 'sp', postal_code: '00000-000' })).success,
    ).toBe(true)
    expect(
      issues(householdSchema.safeParse(household({ state: 'SPX', postal_code: '123' }))),
    ).toEqual(['state', 'postal_code'])
    expect(householdSchema.safeParse(household({ name: 'x'.repeat(81) })).success).toBe(false)
  })

  it('vazio vira nulo no corpo da API e o resto é aparado', () => {
    expect(
      toHouseholdBody(
        household({ name: ' Família Exemplo ', street: '', city: ' Cidade Exemplo ' }),
      ),
    ).toEqual({
      name: 'Família Exemplo',
      side: 'Comum',
      street: null,
      number: null,
      complement: null,
      district: null,
      city: 'Cidade Exemplo',
      state: null,
      postal_code: null,
      note: null,
    })
  })
})

describe('formulário da pessoa', () => {
  const required = makeGuestSchema({ nameRequired: true })
  const optional = makeGuestSchema({ nameRequired: false })

  it('o nome é obrigatório, exceto no acompanhante', () => {
    expect(issues(required.safeParse(guest({ name: '' })))).toEqual(['name'])
    expect(optional.safeParse(guest({ name: '' })).success).toBe(true)
  })

  it('a idade só é conferida para criança e vai de 0 a 17', () => {
    expect(required.safeParse(guest({ band: 'Adulto', age: '40' })).success).toBe(true)
    expect(required.safeParse(guest({ band: 'Criança isenta', age: '17' })).success).toBe(true)
    expect(issues(required.safeParse(guest({ band: 'Criança isenta', age: '18' })))).toEqual([
      'age',
    ])
    expect(issues(required.safeParse(guest({ band: 'Criança pagante', age: 'x' })))).toEqual([
      'age',
    ])
  })

  it('o corpo manda idade só para criança e vazio como nulo', () => {
    expect(toGuestBody(guest({ band: 'Criança pagante', age: '9', phone: '' }))).toMatchObject({
      band: 'Criança pagante',
      age: 9,
      phone: null,
      name: 'Convidado Exemplo A',
    })
    expect(toGuestBody(guest({ band: 'Adulto', age: '9' })).age).toBeNull()
    expect(toGuestBody(guest({ name: '' })).name).toBeNull()
  })
})
