import { screen, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { jsonResponse, mockApi } from '@/test/fake-api'
import { FAKE_NOIVO, renderRoute } from '@/test/render-route'

const AREAS = [
  ['/', 'O momento de vocês'],
  ['/planejamento', 'O rumo de vocês'],
  ['/cronograma', 'O que pode andar agora'],
  ['/possibilidades', 'Comparar propostas'],
  ['/orcamento', 'O orçamento de vocês'],
  ['/contatos', 'Quem vocês estão consultando'],
  ['/convidados', 'Quem estará com vocês'],
  ['/assistente', 'Conversem com o assistente'],
] as const

// Planejamento já tem conteúdo de verdade: lê as Definições Base, então a API falsa responde a elas.
const EMPTY_FIELD = { status: 'Em definição', note: null, version: 1 } as const
function planningApi() {
  return mockApi({
    'GET /api/v1/auth/me': jsonResponse(200, FAKE_NOIVO),
    'GET /api/v1/wedding/baseline': jsonResponse(200, {
      date: { ...EMPTY_FIELD, value: { kind: 'nenhuma' } },
      city: { ...EMPTY_FIELD, value: null },
      format: { ...EMPTY_FIELD, value: null },
      size: { ...EMPTY_FIELD, value: { minimum: null, maximum: null } },
      ceiling: { ...EMPTY_FIELD, value: { cents: null } },
      ceremony: { ...EMPTY_FIELD, value: { kinds: [], detail: null } },
    }),
  })
}

// As áreas que ainda são esqueleto: um estado vazio acolhedor e nenhuma ação.
const SKELETONS = AREAS.filter(([path]) => path !== '/planejamento')

describe('rotas das áreas', () => {
  it.each(AREAS)('%s mostra o título editorial da área como o único h1', async (path, title) => {
    await renderRoute(path, path === '/planejamento' ? { api: planningApi() } : {})

    expect(await screen.findByRole('heading', { level: 1, name: title })).toBeInTheDocument()
    expect(screen.getAllByRole('heading', { level: 1 })).toHaveLength(1)
  })

  it.each(SKELETONS)('%s mostra um estado vazio acolhedor, sem ação morta', async (path) => {
    await renderRoute(path)

    expect(await screen.findByRole('heading', { level: 2 })).toBeVisible()
    expect(within(screen.getByRole('main')).queryByRole('button')).not.toBeInTheDocument()
  })

  it('um caminho desconhecido mostra a página não encontrada com a saída para a Visão Geral', async () => {
    await renderRoute('/nao-existe')

    expect(
      await screen.findByRole('heading', { name: 'Não encontramos esta página' }),
    ).toBeVisible()
    expect(screen.getByRole('link', { name: 'Ir para a Visão Geral' })).toHaveAttribute('href', '/')
  })

  it('em desenvolvimento a rota /design-system abre a vitrine, fora da navegação', async () => {
    await renderRoute('/design-system')

    expect(await screen.findByRole('heading', { level: 1, name: 'Design System' })).toBeVisible()
  })
})

describe('vitrine só em desenvolvimento (D-053, D-057)', () => {
  afterEach(() => {
    vi.unstubAllEnvs()
  })

  it('em produção a rota /design-system não existe: cai na página não encontrada', async () => {
    vi.stubEnv('DEV', false)
    await renderRoute('/design-system')

    expect(
      await screen.findByRole('heading', { name: 'Não encontramos esta página' }),
    ).toBeVisible()
    expect(
      screen.queryByRole('heading', { level: 1, name: 'Design System' }),
    ).not.toBeInTheDocument()
  })
})

describe('lente na URL', () => {
  it('lê ?lente=minha', async () => {
    const router = await renderRoute('/cronograma?lente=minha')

    expect(router.state.matches.at(-1)?.search).toMatchObject({ lente: 'minha' })
  })

  it('sem o parâmetro, a lente é Casal (nenhum valor)', async () => {
    const router = await renderRoute('/cronograma')

    expect(router.state.matches.at(-1)?.search.lente).toBeUndefined()
  })

  it('um valor inválido cai em Casal', async () => {
    const router = await renderRoute('/cronograma?lente=banana')

    expect(router.state.matches.at(-1)?.search.lente).toBeUndefined()
  })
})
