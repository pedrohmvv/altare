import { Link } from '@tanstack/react-router'
import { Tooltip } from '@/components/ui/tooltip'
import { SessionBlock } from '@/features/identity'
import { cn } from '@/lib/cn'
import { useMediaQuery } from '@/lib/use-media-query'
import { keepLens } from './keep-lens'
import { DESIGN_SYSTEM_ITEM, NAV_ITEMS, type NavItem } from './nav-config'

const AREAS = NAV_ITEMS.filter((item) => item.group === 'areas')
const ASSISTANT = NAV_ITEMS.filter((item) => item.group === 'assistant')

// Medidas do guia de identidade: itens de 40 px a cada 46 px, ícone de 20 px e rótulo de 12 px.
function SidebarLink({ item, withTooltip }: { item: NavItem; withTooltip: boolean }) {
  const Icon = item.icon
  const link = (
    <Link
      to={item.to}
      search={keepLens}
      activeOptions={{ exact: item.to === '/' }}
      className={cn(
        'group flex h-10 items-center justify-center gap-2.5 rounded-control px-3.5 pointer-coarse:min-h-11 lg:justify-start lg:pr-1.5',
        'text-eyebrow font-medium whitespace-nowrap normal-case tracking-normal text-ink-muted transition-colors duration-fast ease-standard',
        'hover:bg-surface-muted hover:text-ink',
        'data-[status=active]:bg-surface-muted data-[status=active]:font-semibold data-[status=active]:text-ink',
      )}
    >
      <Icon aria-hidden className="size-5 shrink-0 group-data-[status=active]:text-primary" />
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
    <aside className="sticky top-0 hidden h-dvh flex-col border-r border-border bg-surface px-4 pt-8.25 pb-6 md:flex">
      <Link
        to="/"
        search={keepLens}
        aria-label="Altare, ir para a Visão Geral"
        className="flex items-center justify-center rounded-control lg:justify-start lg:px-3"
      >
        <img
          src="/brand/logo/altare-wordmark-oliva.svg"
          alt=""
          className="hidden h-7.25 lg:block"
        />
        <img src="/brand/logo/altare-simbolo-oliva.svg" alt="" className="h-7 lg:hidden" />
      </Link>
      <nav aria-label="Navegação principal" className="mt-9.5 flex flex-1 flex-col">
        <ul className="flex flex-col gap-1.5">
          {AREAS.map((item) => (
            <li key={item.to}>
              <SidebarLink item={item} withTooltip={!isWide} />
            </li>
          ))}
        </ul>
        <hr className="my-4 border-border" />
        <ul className="flex flex-col gap-1.5">
          {ASSISTANT.map((item) => (
            <li key={item.to}>
              <SidebarLink item={item} withTooltip={!isWide} />
            </li>
          ))}
        </ul>
      </nav>
      {/* O pé da barra (pág. 38 do guia): uma *hairline* e a sessão individual. */}
      <div className="flex flex-col gap-1.5 border-t border-border pt-3">
        {/* Só em desenvolvimento: um atalho discreto para ver os primitivos (D-053). */}
        {import.meta.env.DEV && <SidebarLink item={DESIGN_SYSTEM_ITEM} withTooltip={!isWide} />}
        <SessionBlock variant={isWide ? 'sidebar' : 'rail'} />
      </div>
    </aside>
  )
}
