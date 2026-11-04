import { describe, expect, it } from 'vitest'
import { milestone } from '@/test/schedule-fixtures'
import { milestoneSchema, NO_CATEGORY, toFormValues, toUpdateFields } from './milestone-form'

const valid = {
  title: 'Marco Exemplo',
  phase_id: 'fase-1',
  category_id: NO_CATEGORY,
  responsible: 'Ambos',
  target_date: '',
  note: '',
}
const issues = (input: object) => {
  const result = milestoneSchema.safeParse(input)
  return result.success ? [] : result.error.issues.map((issue) => issue.message)
}

describe('formulário do marco (F-CRN-05)', () => {
  it('aceita responsável, prazo e nota em branco', () => {
    expect(issues(valid)).toEqual([])
  })

  it('aceita uma data de verdade e recusa uma que não existe', () => {
    expect(issues({ ...valid, target_date: '2027-02-28' })).toEqual([])
    expect(issues({ ...valid, target_date: '2027-02-30' })).toEqual([
      'Informem uma data válida, com dia, mês e ano.',
    ])
  })

  it('recusa um ano fora do que a API aceita', () => {
    expect(issues({ ...valid, target_date: '1999-12-31' })).toHaveLength(1)
    expect(issues({ ...valid, target_date: '2101-01-01' })).toHaveLength(1)
  })

  it('a nota passa até 500 caracteres, depois de aparada', () => {
    expect(issues({ ...valid, note: `  ${'a'.repeat(500)}  ` })).toEqual([])
    expect(issues({ ...valid, note: 'a'.repeat(501) })).toEqual(['Usem até 500 caracteres.'])
  })

  it('recusa um responsável que não existe', () => {
    expect(issues({ ...valid, responsible: 'Padrinho' })).toHaveLength(1)
  })

  it('o título é obrigatório, aparado, e vai até 120 caracteres', () => {
    expect(issues({ ...valid, title: '   ' })).toEqual(['Informem o título do marco.'])
    expect(issues({ ...valid, title: `  ${'a'.repeat(120)} ` })).toEqual([])
    expect(issues({ ...valid, title: 'a'.repeat(121) })).toEqual(['Usem até 120 caracteres.'])
  })

  it('a fase é obrigatória', () => {
    expect(issues({ ...valid, phase_id: '' })).toHaveLength(1)
  })

  it('vai e volta do marco: sem categoria, prazo e nota viram campos vazios, e o contrário', () => {
    const item = milestone({ id: 'm', title: 'Marco Exemplo' })
    expect(toFormValues(item, 'fase-1')).toEqual(valid)
    expect(
      toFormValues(
        milestone({ id: 'm', title: 'Marco Exemplo', category: { id: 'c1', name: 'X' } }),
        'fase-1',
      ).category_id,
    ).toBe('c1')
    expect(
      toUpdateFields({
        ...valid,
        title: '  Outro  ',
        responsible: 'Noiva',
        target_date: '',
        note: '  ',
      }),
    ).toEqual({
      title: 'Outro',
      phaseId: 'fase-1',
      categoryId: null,
      responsible: 'Noiva',
      note: null,
      targetDate: null,
    })
    expect(
      toUpdateFields({
        ...valid,
        category_id: 'c1',
        responsible: 'Noivo',
        target_date: '2027-05-01',
        note: ' oi ',
      }),
    ).toEqual({
      title: 'Marco Exemplo',
      phaseId: 'fase-1',
      categoryId: 'c1',
      responsible: 'Noivo',
      note: 'oi',
      targetDate: '2027-05-01',
    })
  })
})
