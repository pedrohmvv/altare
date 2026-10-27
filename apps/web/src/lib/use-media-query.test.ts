import { act, renderHook } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { useMediaQuery } from './use-media-query'

type Listener = () => void

function stubMatchMedia(initial: boolean) {
  let matches = initial
  const listeners = new Set<Listener>()
  const mql = {
    get matches() {
      return matches
    },
    addEventListener: (_: string, listener: Listener) => listeners.add(listener),
    removeEventListener: (_: string, listener: Listener) => listeners.delete(listener),
  }
  vi.stubGlobal('matchMedia', () => mql)
  return {
    set(next: boolean) {
      matches = next
      for (const listener of listeners) listener()
    },
    listeners,
  }
}

describe('useMediaQuery', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('devolve se a consulta corresponde agora', () => {
    stubMatchMedia(true)

    const { result } = renderHook(() => useMediaQuery('(min-width: 1024px)'))

    expect(result.current).toBe(true)
  })

  it('acompanha as mudanças da consulta', () => {
    const media = stubMatchMedia(false)
    const { result } = renderHook(() => useMediaQuery('(min-width: 1024px)'))
    expect(result.current).toBe(false)

    act(() => media.set(true))

    expect(result.current).toBe(true)
  })

  it('para de ouvir ao desmontar', () => {
    const media = stubMatchMedia(false)
    const { unmount } = renderHook(() => useMediaQuery('(min-width: 1024px)'))
    expect(media.listeners.size).toBe(1)

    unmount()

    expect(media.listeners.size).toBe(0)
  })

  it('sem matchMedia (jsdom) devolve false', () => {
    vi.stubGlobal('matchMedia', undefined)

    const { result } = renderHook(() => useMediaQuery('(min-width: 1024px)'))

    expect(result.current).toBe(false)
  })
})
