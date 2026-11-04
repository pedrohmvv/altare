import { describe, expect, it } from 'vitest'
import { formatBytes } from './bytes'

// O espaço entre o número e a unidade não quebra a linha (identity.md §4).
const NBSP = ' '

describe('formatBytes', () => {
  it.each([
    [0, `0${NBSP}B`],
    [800, `800${NBSP}B`],
    [1024, `1${NBSP}KB`],
    [1536, `1,5${NBSP}KB`],
    [512 * 1024, `512${NBSP}KB`],
    [1_468_006, `1,4${NBSP}MB`],
    [20 * 1024 * 1024, `20${NBSP}MB`],
    [3 * 1024 * 1024 + 1, `3${NBSP}MB`],
  ])('formata %i bytes como %s, com vírgula decimal e uma casa', (bytes, expected) => {
    expect(formatBytes(bytes)).toBe(expected)
  })

  it('sobe de unidade quando o arredondamento chegaria a 1024', () => {
    expect(formatBytes(1024 * 1024 - 1)).toBe(`1${NBSP}MB`)
  })

  it('recusa tamanho negativo ou fracionário', () => {
    expect(() => formatBytes(-1)).toThrow(RangeError)
    expect(() => formatBytes(1.5)).toThrow(RangeError)
  })
})
