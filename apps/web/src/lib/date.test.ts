import { describe, expect, it } from 'vitest'
import { formatDay, formatInstant, formatMonthYear, MONTHS } from './date'

describe('datas em pt-BR', () => {
  it('escreve o dia como na lista do guia: 26 out 2026', () => {
    expect(formatDay('2026-10-26')).toBe('26 out 2026')
    expect(formatDay('2027-05-01')).toBe('1 mai 2027')
  })

  it('escreve mês e ano abreviados', () => {
    expect(formatMonthYear(2027, 3)).toBe('mar 2027')
    expect(formatMonthYear(2027, 12)).toBe('dez 2027')
  })

  it('recusa data impossível em vez de inventar um texto', () => {
    expect(() => formatDay('2027-13-01')).toThrow(RangeError)
    expect(() => formatMonthYear(2027, 0)).toThrow(RangeError)
  })

  it('lista os doze meses por extenso, de 1 a 12', () => {
    expect(MONTHS).toHaveLength(12)
    expect(MONTHS[0]).toEqual({ value: '1', label: 'janeiro' })
    expect(MONTHS[11]).toEqual({ value: '12', label: 'dezembro' })
  })

  it('mostra o instante no horário de Brasília, onde vocês estão', () => {
    expect(formatInstant('2026-10-27T15:30:00Z')).toBe('27 out 2026, 12:30')
    // 02:00 UTC ainda é a noite do dia anterior em São Paulo.
    expect(formatInstant('2027-01-01T02:00:00Z')).toBe('31 dez 2026, 23:00')
  })
})
