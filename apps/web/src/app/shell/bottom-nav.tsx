import { Link, useRouterState } from '@tanstack/react-router'
import { Ellipsis } from 'lucide-react'
import { Dialog, DialogClose, DialogContent, DialogTrigger } from '@/components/ui/dialog'
import { SessionBlock } from '@/features/identity'
import { cn } from '@/lib/cn'
import { keepLens } from './keep-lens'
import { LensSwitcher } from './lens-switcher'
import { NAV_ITEMS } from './nav-config'

const BAR_ITEMS = NAV_ITEMS.flatMap((item) => (item.bar ? [{ ...item, bar: item.bar }] : []))
const MORE_ITEMS = NAV_ITEMS.filter((item) => !item.bar)

// Barra de 72 px do guia: ícone de 22 px e rótulo de 12 px; o destino atual fica oliva e em seminegrito.
const BAR_ITEM = cn(
  'group flex min-h-18 w-full flex-col items-center justify-center gap-1 px-1',
  'text-ink-muted transition-colors duration-fast ease-standard data-[status=active]:text-primary',
)
const BAR_LABEL = 'max-w-full truncate text-ui-xs group-data-[status=active]:font-semibold'

/** Barra inferior do celular: 4 destinos e "Mais", com a lente e as demais áreas (D-025, D-050). */
export function BottomNav() {
  const pathname = useRouterState({ select: (state) => state.location.pathname })
  const moreIsActive = MORE_ITEMS.some((item) => item.to === pathname)

  return (
    <nav
      aria-label="Navegação principal (celular)"
      className="fixed inset-x-0 bottom-0 z-20 border-t border-border bg-surface pb-[env(safe-area-inset-bottom)] md:hidden"
    >
      <ul className="grid grid-cols-5">
        {BAR_ITEMS.map((item) => {
          const Icon = item.bar.icon
          return (
            <li key={item.to}>
              <Link
                to={item.to}
                search={keepLens}
                activeOptions={{ exact: item.to === '/' }}
                aria-label={item.bar.name}
                className={BAR_ITEM}
              >
                <Icon aria-hidden className="size-5.5" />
                <span className={BAR_LABEL}>{item.bar.label}</span>
              </Link>
            </li>
          )
        })}
        <li>
          <Dialog>
            <DialogTrigger asChild>
              <button
                type="button"
                data-status={moreIsActive ? 'active' : undefined}
                className={BAR_ITEM}
              >
                <Ellipsis aria-hidden className="size-5.5" />
                <span className={BAR_LABEL}>Mais</span>
              </button>
            </DialogTrigger>
            <DialogContent title="Mais áreas">
              <div className="flex flex-col gap-2">
                <p className="text-eyebrow text-ink-muted">Lente de visão</p>
                <LensSwitcher />
              </div>
              <hr className="border-border" />
              <ul className="flex flex-col gap-1">
                {MORE_ITEMS.map((item) => {
                  const Icon = item.icon
                  return (
                    <li key={item.to}>
                      <DialogClose asChild>
                        <Link
                          to={item.to}
                          search={keepLens}
                          className="group flex min-h-11 items-center gap-3 rounded-control px-3 text-body font-medium text-ink hover:bg-surface-muted data-[status=active]:bg-surface-muted"
                        >
                          <Icon
                            aria-hidden
                            className="size-5 shrink-0 text-ink-muted group-data-[status=active]:text-primary"
                          />
                          {item.label}
                        </Link>
                      </DialogClose>
                    </li>
                  )
                })}
              </ul>
              <hr className="border-border" />
              <SessionBlock variant="sheet" />
            </DialogContent>
          </Dialog>
        </li>
      </ul>
    </nav>
  )
}
