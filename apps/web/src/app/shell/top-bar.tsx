import { Link, useMatches } from '@tanstack/react-router'
import { keepLens } from './keep-lens'
import { LensSwitcher } from './lens-switcher'

/** Título da área e seletor de lente. O menu do usuário entra com o login (D-028). */
export function TopBar() {
  const title = useMatches({ select: (matches) => matches.at(-1)?.staticData.title })

  return (
    <header className="sticky top-0 z-20 flex min-h-14 items-center justify-between gap-3 border-b border-border bg-canvas px-4 md:px-8">
      <div className="flex min-w-0 items-center gap-3">
        <Link
          to="/"
          search={keepLens}
          aria-label="Altare, ir para a Visão Geral"
          className="md:hidden"
        >
          <img src="/brand/logo/altare-simbolo-oliva.svg" alt="" className="h-8" />
        </Link>
        <p className="truncate text-body-sm text-ink-muted">{title}</p>
      </div>
      <LensSwitcher />
    </header>
  )
}
