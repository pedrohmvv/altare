import { Link, useMatches } from '@tanstack/react-router'
import { keepLens } from './keep-lens'
import { LensSwitcher } from './lens-switcher'

/**
 * Título da área e seletor de lente, com 72 px no desktop (guia de identidade). No celular a lente
 * fica na folha "Mais". Não há menu do usuário aqui, como no guia: a sessão fica no pé da barra
 * lateral e na folha "Mais" (D-061).
 */
export function TopBar() {
  const title = useMatches({ select: (matches) => matches.at(-1)?.staticData.title })

  return (
    <header className="sticky top-0 z-20 flex h-14 items-center justify-between gap-3 border-b border-border bg-canvas px-4 md:h-18 md:px-8.5">
      <div className="flex min-w-0 items-center gap-3">
        <Link
          to="/"
          search={keepLens}
          aria-label="Altare, ir para a Visão Geral"
          className="md:hidden"
        >
          <img src="/brand/logo/altare-simbolo-oliva.svg" alt="" className="h-6.75" />
        </Link>
        <p className="truncate text-body font-semibold text-ink">{title}</p>
      </div>
      <div className="hidden md:block">
        <LensSwitcher />
      </div>
    </header>
  )
}
