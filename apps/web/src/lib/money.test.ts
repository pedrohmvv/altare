import { describe, expect, it } from 'vitest'
import { formatMoney } from './money'

const NBSP = ' '
const MINUS = '−'

describe('formatMoney', () => {
  it('em auto, valor inteiro de reais sai sem centavos', () => {
    expect(formatMoney(2_800_000)).toBe(`R$${NBSP}28.000`)
  })

  it('em auto, valor com centavos mostra os dois dígitos', () => {
    expect(formatMoney(123_456)).toBe(`R$${NBSP}1.234,56`)
    expect(formatMoney(100_050)).toBe(`R$${NBSP}1.000,50`)
  })

  it('em always, mostra os centavos mesmo quando zerados', () => {
    expect(formatMoney(2_800_000, { precision: 'always' })).toBe(`R$${NBSP}28.000,00`)
  })

  it('usa o espaço não separável depois do R$ para a quebra de linha não separar o símbolo', () => {
    expect(formatMoney(100)).toContain(`R$${NBSP}`)
    expect(formatMoney(100)).not.toContain('R$ ')
  })

  it('formata zero e centavos soltos', () => {
    expect(formatMoney(0)).toBe(`R$${NBSP}0`)
    expect(formatMoney(0, { precision: 'always' })).toBe(`R$${NBSP}0,00`)
    expect(formatMoney(5)).toBe(`R$${NBSP}0,05`)
    expect(formatMoney(99)).toBe(`R$${NBSP}0,99`)
    expect(formatMoney(100)).toBe(`R$${NBSP}1`)
  })

  it('agrupa os milhares com ponto em valores grandes', () => {
    expect(formatMoney(12_345_678_900)).toBe(`R$${NBSP}123.456.789`)
    expect(formatMoney(100_000_000, { precision: 'always' })).toBe(`R$${NBSP}1.000.000,00`)
  })

  it('escreve o negativo com o sinal de menos tipográfico, afastado do R$', () => {
    expect(formatMoney(-125_000, { precision: 'always' })).toBe(`${MINUS}${NBSP}R$${NBSP}1.250,00`)
    expect(formatMoney(-150)).toBe(`${MINUS}${NBSP}R$${NBSP}1,50`)
  })

  // Guia, págs. 28 e 34 (identity.md §1.4): "+ R$ 1.200,00", com espaço depois do sinal.
  it('com signed mostra + e − e deixa o zero sem sinal', () => {
    expect(formatMoney(125_000, { signed: true, precision: 'always' })).toBe(
      `+${NBSP}R$${NBSP}1.250,00`,
    )
    expect(formatMoney(-125_000, { signed: true, precision: 'always' })).toBe(
      `${MINUS}${NBSP}R$${NBSP}1.250,00`,
    )
    expect(formatMoney(0, { signed: true })).toBe(`R$${NBSP}0`)
    expect(formatMoney(-0, { signed: true })).toBe(`R$${NBSP}0`)
  })

  it('recusa o que não é um inteiro de centavos', () => {
    expect(() => formatMoney(1.5)).toThrow(RangeError)
    expect(() => formatMoney(Number.NaN)).toThrow(RangeError)
    expect(() => formatMoney(Number.POSITIVE_INFINITY)).toThrow(RangeError)
    expect(() => formatMoney(2 ** 53)).toThrow(RangeError)
  })

  it('em always, os dígitos formatados reconstroem exatamente os centavos', () => {
    let seed = 20_261_027
    for (let i = 0; i < 500; i++) {
      seed = (seed * 1_103_515_245 + 12_345) % 2_147_483_648
      const cents = (seed % 2_000_000_000) * (i % 2 === 0 ? 1 : -1)
      const digits = formatMoney(cents, { precision: 'always' }).replace(/\D/g, '')

      expect(Number(digits)).toBe(Math.abs(cents))
    }
  })
})
