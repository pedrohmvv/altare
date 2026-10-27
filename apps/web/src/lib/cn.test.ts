import { describe, expect, it } from 'vitest'
import { cn } from './cn'

describe('cn', () => {
  it('junta classes e descarta valores vazios', () => {
    expect(cn('flex', false, undefined, null, 'gap-2', ['p-4'], { hidden: false })).toBe(
      'flex gap-2 p-4',
    )
  })

  it('mantém só a última classe quando duas do Tailwind conflitam', () => {
    expect(cn('px-2', 'px-4')).toBe('px-4')
  })

  it('trata cores semânticas como cor: a última de cada propriedade vence', () => {
    expect(cn('bg-surface', 'bg-canvas')).toBe('bg-canvas')
    expect(cn('text-ink', 'text-ink-muted')).toBe('text-ink-muted')
    expect(cn('border-border', 'border-border-strong')).toBe('border-border-strong')
  })

  it('não confunde cor de texto com tamanho de texto do Altare', () => {
    expect(cn('text-ink', 'text-body-sm')).toBe('text-ink text-body-sm')
    expect(cn('text-body-sm', 'text-ink')).toBe('text-body-sm text-ink')
  })

  it('mantém só o último tamanho de texto entre os tokens da escala', () => {
    expect(cn('text-body', 'text-body-sm')).toBe('text-body-sm')
    expect(cn('text-display', 'text-num-xl')).toBe('text-num-xl')
  })

  it('resolve conflito entre raios e sombras dos tokens', () => {
    expect(cn('rounded-card', 'rounded-control')).toBe('rounded-control')
    expect(cn('shadow-nivel-1', 'shadow-nivel-2')).toBe('shadow-nivel-2')
  })
})
