import { Link } from '@tanstack/react-router'
import { Tooltip } from '@/components/ui/tooltip'
import { cn } from '@/lib/cn'
import { useMediaQuery } from '@/lib/use-media-query'
import { keepLens } from './keep-lens'
import { NAV_ITEMS, type NavItem } from './nav-config'

const AREAS = NAV_ITEMS.filter((item) => item.group === 'areas')
const ASSISTANT = NAV_ITEMS.filter((item) => item.group === 'assistant')

function SidebarLink({ item, withTooltip }: { item: NavItem; withTooltip: boolean }) {
  const Icon = item.icon
  const link = (
    <Link
      to={item.to}
      search={keepLens}
      activeOptions={{ exact: item.to === '/' }}
      className={cn(
        'flex min-h-11 items-center justify-center gap-3 rounded-control px-3 lg:justify-start',
        'text-body font-medium text-ink-muted transition-colors duration-fast ease-standard',
        'hover:bg-surface-muted hover:text-ink data-[status=active]:bg-surface-muted data-[status=active]:text-ink',
      )}
    >
      <Icon aria-hidden className="size-6 shrink-0" />
      {/* No trilho do tablet só o ícone aparece; o nome continua para o leitor de tela. */}
      <span className="sr-only lg:not-sr-only">{item.label}</span>
    </Link>
  )

  // A dica só faz falta no trilho: na barra larga o nome já está visível.
  return withTooltip ? (
    <Tooltip content={item.label} side="right">
      {link}
    </Tooltip>
  ) : (
    link
  )
}

/** Barra lateral no desktop (256 px) e trilho de ícones no tablet (72 px); some no celular. */
export function SidebarNav() {
  const isWide = useMediaQuery('(min-width: 1024px)')

  return (
    <aside className="sticky top-0 hidden h-dvh flex-col gap-6 border-r border-border bg-surface px-3 py-5 md:flex">
      <Link
        to="/"
        search={keepLens}
        aria-label="Altare, ir para a Visão Geral"
        className="flex h-10 items-center justify-center rounded-control lg:justify-start lg:px-3"
      >
        <img src="/brand/logo/altare-wordmark-oliva.svg" alt="" className="hidden h-7 lg:block" />
        <img src="/brand/logo/altare-simbolo-oliva.svg" alt="" className="h-8 lg:hidden" />
      </Link>
      <nav aria-label="Navegação principal" className="flex flex-1 flex-col">
        <ul className="flex flex-col gap-1">
          {AREAS.map((item) => (
            <li key={item.to}>
              <SidebarLink item={item} withTooltip={!isWide} />
            </li>
          ))}
        </ul>
        <hr className="my-3 border-border" />
        <ul className="flex flex-col gap-1">
          {ASSISTANT.map((item) => (
            <li key={item.to}>
              <SidebarLink item={item} withTooltip={!isWide} />
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  )
}
