import type { QueryClient } from '@tanstack/react-query'
import {
  createRootRouteWithContext,
  createRoute,
  createRouter,
  lazyRouteComponent,
  notFound,
  Outlet,
  type RouterHistory,
  redirect,
  useNavigate,
} from '@tanstack/react-router'
import { AppShell } from '@/app/shell/app-shell'
import { RouteAnnouncer } from '@/app/shell/route-announcer'
import { AssistantPage } from '@/features/assistant'
import { validateGuestsSearch } from '@/features/guests/search'
import { LOGIN_PATH, LoginPage, meQueryOptions, safeDestination } from '@/features/identity'
import { validateScheduleSearch } from '@/features/schedule/search'
import { validatePlanningSearch } from '@/features/wedding/search'
import { queryClient } from '@/lib/query-client'
import { NotFoundPage } from './not-found'
import { redirectToLoginOnUnauthenticated } from './session-watch'

/** O que toda rota recebe: o cliente de dados, para as guardas consultarem a sessão. */
export interface RouterContext {
  queryClient: QueryClient
}

/** A lente fica na URL: ausente é `Casal`, `minha` é `Minha visão` (D-021). Qualquer outro valor vira `Casal`. */
export interface RootSearch {
  lente?: 'minha'
}

function RootLayout() {
  // O anúncio de troca de rota vale para toda página, inclusive a de entrada, que não tem a casca.
  return (
    <>
      <RouteAnnouncer />
      <Outlet />
    </>
  )
}

const rootRoute = createRootRouteWithContext<RouterContext>()({
  validateSearch: (search: Record<string, unknown>): RootSearch => ({
    lente: search.lente === 'minha' ? 'minha' : undefined,
  }),
  component: RootLayout,
})

/** Quem está na sessão, ou `null`. Um erro (de rede, por exemplo) conta como sem sessão. */
function currentUser(queryClient: QueryClient) {
  return queryClient.ensureQueryData(meQueryOptions).catch(() => null)
}

/** Divide `/x?y=1#z` no que o roteador entende. O caminho já passou por `safeDestination`. */
function locationOf(destination: string | undefined) {
  const url = new URL(destination ?? '/', 'http://altare.invalid')
  return {
    to: url.pathname,
    search: Object.fromEntries(url.searchParams),
    hash: url.hash.slice(1) || undefined,
  }
}

/** Layout sem caminho: tudo o que mora dentro da casca do app, atrás da guarda de sessão. */
const appRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: 'app',
  beforeLoad: async ({ context, location }) => {
    if (!(await currentUser(context.queryClient))) {
      throw redirect({ to: LOGIN_PATH, search: { destino: safeDestination(location.href) } })
    }
  },
  component: AppShell,
  notFoundComponent: NotFoundPage,
})

function LoginRoute() {
  const { destino } = loginRoute.useSearch()
  const navigate = useNavigate()
  // O destino é livre-texto vindo da URL; os tipos do roteador só conhecem as rotas de verdade.
  return <LoginPage onAuthenticated={() => void navigate(locationOf(destino) as never)} />
}

/** Fora da casca: quem ainda não entrou não vê navegação nem barra. */
const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: LOGIN_PATH,
  staticData: { title: 'Entrar' },
  validateSearch: (search: Record<string, unknown>): { destino?: string } => ({
    destino: safeDestination(search.destino),
  }),
  beforeLoad: async ({ context, search }) => {
    if (await currentUser(context.queryClient)) throw redirect(locationOf(search.destino) as never)
  },
  component: LoginRoute,
})

const area = (path: string, title: string | undefined) => ({
  getParentRoute: () => appRoute,
  path,
  staticData: { title },
})

const routeTree = rootRoute.addChildren([
  loginRoute,
  appRoute.addChildren([
    createRoute({
      ...area('/', 'Visão Geral'),
      component: lazyRouteComponent(() => import('@/features/overview'), 'OverviewPage'),
    }),
    createRoute({
      ...area('/planejamento', 'Planejamento & Caminhos'),
      // Aba, vista, filtros e categoria aberta moram na URL (design-system.md §10). O validador é
      // um módulo puro e pequeno; a feature em si continua carregada só quando a rota abre.
      validateSearch: validatePlanningSearch,
      component: lazyRouteComponent(() => import('@/features/wedding'), 'WeddingRoute'),
    }),
    createRoute({
      ...area('/cronograma', 'Cronograma & Dependências'),
      // O marco aberto mora na URL (design-system.md §10); o validador é um módulo puro e pequeno.
      validateSearch: validateScheduleSearch,
      component: lazyRouteComponent(() => import('@/features/schedule'), 'ScheduleRoute'),
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
      // O painel do núcleo mora na URL (design-system.md §10); o validador é um módulo puro e pequeno.
      validateSearch: validateGuestsSearch,
      component: lazyRouteComponent(() => import('@/features/guests'), 'GuestsRoute'),
    }),
    createRoute({
      ...area('/assistente', 'Assistente'),
      // Sem carregamento sob demanda: o ícone flutuante, na casca, já traz esta feature para o pacote principal.
      component: AssistantPage,
    }),
    createRoute({
      // Vitrine só em desenvolvimento (D-053, D-057). Na versão publicada a rota cai na página não
      // encontrada, e o Vite troca `import.meta.env.DEV` por `false` e descarta a vitrine do pacote.
      ...area('/design-system', import.meta.env.DEV ? 'Design System' : undefined),
      beforeLoad: () => {
        if (!import.meta.env.DEV) throw notFound()
      },
      component: import.meta.env.DEV
        ? lazyRouteComponent(() => import('@/app/design-system-page'), 'DesignSystemPage')
        : undefined,
    }),
    // Todo caminho desconhecido cai aqui, dentro da casca e atrás da guarda de sessão.
    createRoute({ getParentRoute: () => appRoute, path: '$', component: NotFoundPage }),
  ]),
])

export function createAppRouter({
  queryClient,
  history,
}: {
  queryClient: QueryClient
  history?: RouterHistory
}) {
  const router = createRouter({
    routeTree,
    history,
    context: { queryClient },
    defaultPreload: 'intent',
  })
  redirectToLoginOnUnauthenticated(queryClient, router)
  return router
}

export const router = createAppRouter({ queryClient })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
  interface StaticDataRouteOption {
    /** Título da página, usado no título do documento ao trocar de rota. */
    title?: string
  }
}
