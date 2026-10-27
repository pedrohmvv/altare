import { useMatches, useRouterState } from '@tanstack/react-router'
import { useEffect, useRef } from 'react'

const APP_NAME = 'Altare'

/**
 * Numa SPA o leitor de tela não anuncia a troca de página. Ao mudar de rota, muda o título do
 * documento e leva o foco ao título da página (altare-acessibilidade). Mudar só a lente não conta.
 */
export function RouteAnnouncer() {
  const title = useMatches({ select: (matches) => matches.at(-1)?.staticData.title })
  // Só muda depois que a rota (e a página carregada sob demanda) terminou de resolver.
  const pathname = useRouterState({ select: (state) => state.resolvedLocation?.pathname })
  const lastPathname = useRef<string | undefined>(undefined)

  useEffect(() => {
    if (pathname === undefined) return
    document.title = `${title ?? 'Página não encontrada'} · ${APP_NAME}`
    // Na primeira página o foco fica onde o navegador o pôs.
    if (lastPathname.current !== undefined && lastPathname.current !== pathname) {
      document.querySelector<HTMLElement>('main h1')?.focus()
    }
    lastPathname.current = pathname
  }, [pathname, title])

  return null
}
