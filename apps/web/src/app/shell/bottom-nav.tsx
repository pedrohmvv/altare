import { Link, useRouterState } from '@tanstack/react-router'
import { Ellipsis } from 'lucide-react'
import { Dialog, DialogClose, DialogContent, DialogTrigger } from '@/components/ui/dialog'
import { cn } from '@/lib/cn'
import { keepLens } from './keep-lens'
import { NAV_ITEMS } from './nav-config'

const BAR_ITEMS = NAV_ITEMS.filter((item) => item.placement === 'bar')
const MORE_ITEMS = NAV_ITEMS.filter((item) => item.placement === 'more')

// A faixa superior marca o destino atual além da cor (cor nunca é o único sinal).
const BAR_ITEM = cn(
  'flex min-h-16 w-full flex-col items-center justify-center gap-1 border-t-2 border-transparent px-1',
  'text-ink-muted transition-colors duration-fast ease-standard',
  'data-[status=active]:border-primary data-[status=active]:text-ink',
)
const BAR_LABEL = 'max-w-full truncate text-eyebrow normal-case tracking-normal'

/** Barra inferior do celular: 4 destinos e "Mais", com a folha das demais áreas (D-025, D-050). */
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
          const Icon = item.icon
          return (
            <li key={item.to}>
              <Link
                to={item.to}
                search={keepLens}
                activeOptions={{ exact: item.to === '/' }}
                className={BAR_ITEM}
              >
                <Icon aria-hidden className="size-6" />
                <span className={BAR_LABEL}>{item.shortLabel}</span>
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
                <Ellipsis aria-hidden className="size-6" />
                <span className={BAR_LABEL}>Mais</span>
              </button>
            </DialogTrigger>
            <DialogContent title="Mais áreas">
              <ul className="flex flex-col gap-1">
                {MORE_ITEMS.map((item) => {
                  const Icon = item.icon
                  return (
                    <li key={item.to}>
                      <DialogClose asChild>
                        <Link
                          to={item.to}
                          search={keepLens}
                          className="flex min-h-11 items-center gap-3 rounded-control px-3 text-body font-medium text-ink hover:bg-surface-muted data-[status=active]:bg-surface-muted"
                        >
                          <Icon aria-hidden className="size-6 shrink-0" />
                          {item.label}
                        </Link>
                      </DialogClose>
                    </li>
                  )
                })}
              </ul>
            </DialogContent>
          </Dialog>
        </li>
      </ul>
    </nav>
  )
}
