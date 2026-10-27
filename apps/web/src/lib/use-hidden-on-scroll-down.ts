import { useEffect, useState } from 'react'

/**
 * `true` enquanto a página rola para baixo e `false` ao rolar para cima ou no topo. Movimentos menores
 * que `threshold` px não contam, para o elemento não piscar com a tremida do dedo.
 */
export function useHiddenOnScrollDown(threshold = 12): boolean {
  const [hidden, setHidden] = useState(false)

  useEffect(() => {
    let last = window.scrollY
    const onScroll = () => {
      const y = window.scrollY
      if (y <= 0) {
        last = 0
        setHidden(false)
      } else if (Math.abs(y - last) >= threshold) {
        setHidden(y > last)
        last = y
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [threshold])

  return hidden
}
