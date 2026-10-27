import { act, renderHook } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import { useHiddenOnScrollDown } from './use-hidden-on-scroll-down'

function scrollTo(y: number) {
  act(() => {
    Object.defineProperty(window, 'scrollY', { value: y, configurable: true })
    window.dispatchEvent(new Event('scroll'))
  })
}

afterEach(() => scrollTo(0))

describe('useHiddenOnScrollDown', () => {
  it('começa visível, no topo da página', () => {
    const { result } = renderHook(() => useHiddenOnScrollDown())
    expect(result.current).toBe(false)
  })

  it('esconde ao rolar para baixo e volta ao rolar para cima', () => {
    const { result } = renderHook(() => useHiddenOnScrollDown())

    scrollTo(200)
    expect(result.current).toBe(true)

    scrollTo(150)
    expect(result.current).toBe(false)
  })

  it('ignora tremidas menores que o limite, para não piscar', () => {
    const { result } = renderHook(() => useHiddenOnScrollDown(24))

    scrollTo(10)
    scrollTo(20)
    expect(result.current).toBe(false)

    scrollTo(300)
    expect(result.current).toBe(true)

    scrollTo(290)
    scrollTo(285)
    expect(result.current).toBe(true)
  })

  it('volta a aparecer ao chegar ao topo', () => {
    const { result } = renderHook(() => useHiddenOnScrollDown())

    scrollTo(400)
    expect(result.current).toBe(true)

    scrollTo(0)
    expect(result.current).toBe(false)
  })
})
