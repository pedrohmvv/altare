import { describe, expect, it } from 'vitest'
import { makeInviteSchema, todayInBrazil } from './invite-form'

const schema = makeInviteSchema('2026-10-28')
const issues = (result: { error?: { issues: { path: PropertyKey[]; message: string }[] } }) =>
  result.error?.issues.map((i) => `${i.path.join('.')}: ${i.message}`) ?? []

describe('formulário do envio do convite', () => {
  it('data de hoje ou passada e um dos cinco canais valem', () => {
    expect(schema.safeParse({ sent_on: '2026-10-28', channel: 'WhatsApp' }).success).toBe(true)
    expect(schema.safeParse({ sent_on: '2026-01-02', channel: 'Pessoalmente' }).success).toBe(true)
  })

  it('data vazia, futura ou fora do formato é recusada', () => {
    expect(issues(schema.safeParse({ sent_on: '', channel: 'Outro' }))).toEqual([
      'sent_on: Informem a data do envio.',
    ])
    expect(issues(schema.safeParse({ sent_on: '2026-10-29', channel: 'Outro' }))).toEqual([
      'sent_on: A data não pode ser futura.',
    ])
    expect(schema.safeParse({ sent_on: '28/10/2026', channel: 'Outro' }).success).toBe(false)
  })

  it('canal vazio ou desconhecido é recusado', () => {
    expect(issues(schema.safeParse({ sent_on: '2026-10-28', channel: '' }))).toEqual([
      'channel: Escolham o canal.',
    ])
    expect(schema.safeParse({ sent_on: '2026-10-28', channel: 'Telegrama' }).success).toBe(false)
  })

  it('hoje em Brasília: às 02h UTC ainda é o dia anterior', () => {
    expect(todayInBrazil(new Date('2026-10-28T02:00:00Z'))).toBe('2026-10-27')
    expect(todayInBrazil(new Date('2026-10-28T15:00:00Z'))).toBe('2026-10-28')
  })
})
