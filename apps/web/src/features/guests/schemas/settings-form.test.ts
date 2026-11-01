import { describe, expect, it } from 'vitest'
import { settingsSchema, toSettingsBody, toSettingsFormValues } from './settings-form'

const empty = { certain: '', probable: '', phase2: '', exempt: '', paying: '' }
const issues = (result: { error?: { issues: { path: PropertyKey[] }[] } }) =>
  result.error?.issues.map((issue) => issue.path.join('.')) ?? []

describe('formulário de pesos e idades', () => {
  it('tudo em branco vale: nada é presumido', () => {
    expect(settingsSchema.safeParse(empty).success).toBe(true)
    expect(toSettingsBody(empty)).toEqual({
      weights: null,
      exemptUntilAge: null,
      payingUntilAge: null,
    })
  })

  it('os três pesos andam juntos: faltando um, o erro aponta quem falta', () => {
    const result = settingsSchema.safeParse({ ...empty, certain: '100', probable: '70' })

    expect(issues(result)).toEqual(['phase2'])
  })

  it('cada peso é um inteiro de 0 a 100', () => {
    const full = { ...empty, certain: '100', probable: '70', phase2: '30' }
    expect(settingsSchema.safeParse(full).success).toBe(true)
    expect(issues(settingsSchema.safeParse({ ...full, probable: '101' }))).toEqual(['probable'])
    expect(issues(settingsSchema.safeParse({ ...full, phase2: '7,5' }))).toEqual(['phase2'])
    expect(settingsSchema.safeParse({ ...full, certain: '0' }).success).toBe(true)
  })

  it('as idades vão de 0 a 17 e a isenta não passa da pagante', () => {
    expect(settingsSchema.safeParse({ ...empty, exempt: '5', paying: '12' }).success).toBe(true)
    expect(issues(settingsSchema.safeParse({ ...empty, exempt: '18' }))).toEqual(['exempt'])
    expect(issues(settingsSchema.safeParse({ ...empty, exempt: '8', paying: '5' }))).toEqual([
      'exempt',
    ])
    expect(settingsSchema.safeParse({ ...empty, paying: '5', exempt: '5' }).success).toBe(true)
  })

  it('o corpo manda os pesos como objeto inteiro e as idades como número', () => {
    expect(
      toSettingsBody({ certain: '100', probable: '70', phase2: '30', exempt: '5', paying: '' }),
    ).toEqual({
      weights: { certain_pct: 100, probable_pct: 70, phase_2_pct: 30 },
      exemptUntilAge: 5,
      payingUntilAge: null,
    })
  })

  it('abre com o que já está definido', () => {
    expect(
      toSettingsFormValues({
        weights: { certain_pct: 100, probable_pct: 70, phase_2_pct: 30 },
        exempt_until_age: null,
        paying_until_age: 12,
        version: 2,
      }),
    ).toEqual({ certain: '100', probable: '70', phase2: '30', exempt: '', paying: '12' })
  })
})
