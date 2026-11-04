import { describe, expect, it } from 'vitest'
import { countdownText } from './countdown'

describe('contagem regressiva em linguagem direta (F-CRN-05, regra 3)', () => {
  it('diz quantos dias faltam, no plural', () => {
    expect(countdownText(12)).toBe('faltam 12 dias')
    expect(countdownText(2)).toBe('faltam 2 dias')
  })

  it('com um dia, usa o singular', () => {
    expect(countdownText(1)).toBe('falta 1 dia')
  })

  it('no dia, diz que é hoje', () => {
    expect(countdownText(0)).toBe('é hoje')
  })

  it('passado o prazo, diz há quantos dias venceu', () => {
    expect(countdownText(-3)).toBe('venceu há 3 dias')
    expect(countdownText(-1)).toBe('venceu há 1 dia')
  })

  it('sem prazo, concluído ou arquivado (nulo), não diz nada', () => {
    expect(countdownText(null)).toBeNull()
  })
})
