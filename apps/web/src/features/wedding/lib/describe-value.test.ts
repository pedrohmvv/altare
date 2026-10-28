import { describe, expect, it } from 'vitest'
import { describeValue } from './describe-value'

const NBSP = '\u00a0'

describe('describeValue', () => {
  it('data exata no formato de lista do guia', () => {
    expect(describeValue('date', { kind: 'exata', exact: '2027-05-01' })).toBe('1 mai 2027')
  })

  it('janela com e sem rótulo', () => {
    const janela = {
      kind: 'janela',
      window_start: { year: 2027, month: 3 },
      window_end: { year: 2027, month: 5 },
    } as const
    expect(describeValue('date', janela)).toBe('mar 2027 a mai 2027')
    expect(describeValue('date', { ...janela, label: 'outono' })).toBe(
      'mar 2027 a mai 2027 · outono',
    )
  })

  it('sem data, e qualquer campo vazio, não tem descrição', () => {
    expect(describeValue('date', { kind: 'nenhuma' })).toBeNull()
    expect(describeValue('city', null)).toBeNull()
    expect(describeValue('size', { minimum: null, maximum: null })).toBeNull()
    expect(describeValue('ceiling', { cents: null })).toBeNull()
    expect(describeValue('ceremony', { kinds: [], detail: null })).toBeNull()
  })

  it('texto, porte, teto e cerimônia', () => {
    expect(describeValue('city', 'Cidade Exemplo')).toBe('Cidade Exemplo')
    expect(describeValue('format', 'Formato Exemplo')).toBe('Formato Exemplo')
    expect(describeValue('size', { minimum: 80, maximum: 120 })).toBe('80 a 120 convidados')
    expect(describeValue('ceiling', { cents: 2_800_000 })).toBe(`R$${NBSP}28.000`)
    expect(describeValue('ceremony', { kinds: ['Civil', 'Religiosa'] })).toBe('Civil, Religiosa')
    expect(describeValue('ceremony', { kinds: ['Civil'], detail: 'detalhe' })).toBe(
      'Civil · detalhe',
    )
  })
})
