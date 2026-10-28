import { Outlet, useRouterState } from '@tanstack/react-router'
import { AssistantLauncher } from '@/features/assistant'
import { BottomNav } from './bottom-nav'
import { SidebarNav } from './sidebar-nav'
import { TopBar } from './top-bar'

/**
 * Casca do app: barra lateral (desktop) ou trilho (tablet), barra superior, conteúdo, barra inferior
 * (celular) e o ícone flutuante do Assistente. O conteúdo reserva 6 rem no fim (48 px do ícone mais
 * respiro) para o ícone nunca cobrir a última linha.
 */
export function AppShell() {
  // Na própria área Assistente o ícone seria redundante (D-050).
  const inAssistantArea = useRouterState({
    select: (state) => state.location.pathname === '/assistente',
  })

  return (
    <div className="min-h-dvh md:grid md:grid-cols-[4.5rem_minmax(0,1fr)] lg:grid-cols-[16rem_minmax(0,1fr)]">
      <a
        href="#conteudo"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:rounded-control focus:bg-primary focus:px-4 focus:py-2 focus:text-primary-ink"
      >
        Ir para o conteúdo
      </a>
      <SidebarNav />
      <div className="flex min-h-dvh min-w-0 flex-col">
        <TopBar />
        <main
          id="conteudo"
          className="mx-auto w-full max-w-[75rem] flex-1 px-4 pt-6 pb-[calc(var(--shell-bottom-offset)+6rem)] md:px-8.5 md:pt-9"
        >
          <Outlet />
        </main>
      </div>
      <BottomNav />
      {!inAssistantArea && <AssistantLauncher />}
    </div>
  )
}
