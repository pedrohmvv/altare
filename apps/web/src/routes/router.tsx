import {
  createRootRoute,
  createRoute,
  createRouter,
  lazyRouteComponent,
  type RouterHistory,
} from '@tanstack/react-router'
import { AppShell } from '@/app/shell/app-shell'
import { NotFoundPage } from './not-found'

/** A lente fica na URL: ausente é `Casal`, `minha` é `Minha visão` (D-021). Qualquer outro valor vira `Casal`. */
export interface RootSearch {
  lente?: 'minha'
}

const rootRoute = createRootRoute({
  validateSearch: (search: Record<string, unknown>): RootSearch => ({
    lente: search.lente === 'minha' ? 'minha' : undefined,
  }),
  component: AppShell,
  notFoundComponent: NotFoundPage,
})

const area = (path: string, title: string) => ({
  getParentRoute: () => rootRoute,
  path,
  staticData: { title },
})

const routeTree = rootRoute.addChildren([
  createRoute({
    ...area('/', 'Visão Geral'),
    component: lazyRouteComponent(() => import('@/features/overview'), 'OverviewPage'),
  }),
  createRoute({
    ...area('/planejamento', 'Planejamento & Caminhos'),
    component: lazyRouteComponent(() => import('@/features/wedding'), 'WeddingPage'),
  }),
  createRoute({
    ...area('/cronograma', 'Cronograma & Dependências'),
    component: lazyRouteComponent(() => import('@/features/schedule'), 'SchedulePage'),
  }),
  createRoute({
    ...area('/possibilidades', 'Possibilidades & Decisões'),
    component: lazyRouteComponent(() => import('@/features/possibilities'), 'PossibilitiesPage'),
  }),
  createRoute({
    ...area('/orcamento', 'Orçamento & Simulador'),
    component: lazyRouteComponent(() => import('@/features/budget'), 'BudgetPage'),
  }),
  createRoute({
    ...area('/contatos', 'Contatos & Fornecedores'),
    component: lazyRouteComponent(() => import('@/features/vendors'), 'VendorsPage'),
  }),
  createRoute({
    ...area('/convidados', 'Convidados, Enxoval & Dia D'),
    component: lazyRouteComponent(() => import('@/features/guests'), 'GuestsPage'),
  }),
  createRoute({
    ...area('/assistente', 'Assistente'),
    component: lazyRouteComponent(() => import('@/features/assistant'), 'AssistantPage'),
  }),
  createRoute({
    ...area('/design-system', 'Design System'),
    component: lazyRouteComponent(() => import('@/app/design-system-page'), 'DesignSystemPage'),
  }),
])

export function createAppRouter(history?: RouterHistory) {
  return createRouter({ routeTree, history, defaultPreload: 'intent' })
}

export const router = createAppRouter()

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
  interface StaticDataRouteOption {
    /** Título da página, usado no título do documento ao trocar de rota. */
    title?: string
  }
}
