import { describe, expect, it } from 'vitest'
import { toWindowBody, toWindowFormValues, windowSchema } from './window-form'

const valid = { start_before: '14', end_before: '10', unit: 'meses' }
const issues = (input: object) => {
  const result = windowSchema.safeParse(input)
  return result.success ? [] : result.error.issues.map((i) => [i.path.join('.'), i.message])
}

describe('o editor de janela (F-CRN-05, regra 5)', () => {
  it('aceita início maior que o fim, em meses', () => {
    expect(issues(valid)).toEqual([])
  })

  it('aceita início igual ao fim e o dia do casamento (0 e 0)', () => {
    expect(issues({ ...valid, start_before: '3', end_before: '3' })).toEqual([])
    expect(issues({ ...valid, start_before: '0', end_before: '0' })).toEqual([])
  })

  it('exige número inteiro: vazio, decimal, negativo e letras são recusados no campo', () => {
    const integer = 'Informem um número inteiro de 0 a 120.'
    expect(issues({ ...valid, start_before: '' })).toEqual([['start_before', integer]])
    expect(issues({ ...valid, end_before: '1,5' })).toEqual([['end_before', integer]])
    expect(issues({ ...valid, end_before: '1.5' })).toEqual([['end_before', integer]])
    expect(issues({ ...valid, end_before: '-1' })).toEqual([['end_before', integer]])
    expect(issues({ ...valid, start_before: 'dez' })).toEqual([['start_before', integer]])
  })

  it('recusa o início que vem depois do fim, no campo do início', () => {
    expect(issues({ ...valid, start_before: '3', end_before: '10' })).toEqual([
      [
        'start_before',
        'O início precisa ser maior ou igual ao fim (a janela começa antes de terminar).',
      ],
    ])
  })

  it('o teto é 120 meses', () => {
    expect(issues({ ...valid, start_before: '120' })).toEqual([])
    expect(issues({ ...valid, start_before: '121' })).toEqual([
      ['start_before', 'Usem no máximo 120 meses.'],
    ])
  })

  it('o teto é 520 semanas, e o mesmo número que passa em semanas não passa em meses', () => {
    expect(issues({ start_before: '130', end_before: '10', unit: 'semanas' })).toEqual([])
    expect(issues({ start_before: '520', end_before: '10', unit: 'semanas' })).toEqual([])
    expect(issues({ start_before: '521', end_before: '10', unit: 'semanas' })).toEqual([
      ['start_before', 'Usem no máximo 520 semanas.'],
    ])
    expect(issues({ start_before: '130', end_before: '10', unit: 'meses' })).toEqual([
      ['start_before', 'Usem no máximo 120 meses.'],
    ])
  })

  it('só o fim acima do teto é recusado no campo do fim', () => {
    expect(issues({ start_before: '120', end_before: '130', unit: 'meses' })).toEqual([
      ['end_before', 'Usem no máximo 120 meses.'],
    ])
  })
})

describe('da janela da API para o formulário e de volta', () => {
  it('abre com os deslocamentos da janela como texto', () => {
    expect(
      toWindowFormValues({ start_before: 14, end_before: 10, unit: 'meses', is_suggestion: true }),
    ).toEqual(valid)
  })

  it('sem janela, abre vazio e em meses', () => {
    expect(toWindowFormValues(null)).toEqual({ start_before: '', end_before: '', unit: 'meses' })
  })

  it('envia números inteiros, sem a versão (quem envia a põe)', () => {
    expect(toWindowBody({ start_before: ' 14 ', end_before: '10', unit: 'semanas' })).toEqual({
      start_before: 14,
      end_before: 10,
      unit: 'semanas',
    })
  })
})
