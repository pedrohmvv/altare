import { useSyncExternalStore } from 'react'

/** Acompanha uma media query no JS. Sem `matchMedia` (jsdom, SSR) devolve `false`. */
export function useMediaQuery(query: string): boolean {
  return useSyncExternalStore(
    (notify) => {
      const media = window.matchMedia?.(query)
      media?.addEventListener('change', notify)
      return () => media?.removeEventListener('change', notify)
    },
    () => window.matchMedia?.(query).matches ?? false,
    () => false,
  )
}
