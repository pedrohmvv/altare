import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { jsonResponse, mockApi } from '@/test/fake-api'
import { LIST, listOf } from '@/test/guest-fixtures'
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
      size: { ...EMPTY_FIELD, value: { minimum: null, maximum: null }, guest_count: 0 },
      ceiling: { ...EMPTY_FIELD, value: { cents: null } },
      ceremony: { ...EMPTY_FIELD, value: { kinds: [], detail: null } },
    }),
  })
}

// Convidados já tem conteúdo de verdade: lê a lista, então a API falsa responde a ela.
function guestsApi() {
  return mockApi({
    'GET /api/v1/auth/me': jsonResponse(200, FAKE_NOIVO),
    'GET /api/v1/guests': jsonResponse(200, listOf([])),
  })
}

const WITH_CONTENT = ['/planejamento', '/convidados']

// As áreas que ainda são esqueleto: um estado vazio acolhedor e nenhuma ação.
const SKELETONS = AREAS.filter(([path]) => !WITH_CONTENT.includes(path))

describe('rotas das áreas', () => {
  it.each(AREAS)('%s mostra o título editorial da área como o único h1', async (path, title) => {
    const api =
      path === '/planejamento' ? planningApi() : path === '/convidados' ? guestsApi() : undefined
    await renderRoute(path, api ? { api } : {})

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

  it('os filtros de Convidados moram na URL, o voltar os desfaz e a busca nunca vai para ela (F-CNV-07)', async () => {
    const api = mockApi({
      'GET /api/v1/auth/me': jsonResponse(200, FAKE_NOIVO),
      'GET /api/v1/guests': jsonResponse(200, LIST),
    })
    const router = await renderRoute('/convidados?lente=minha', { api })
    const chip = await screen.findByRole('button', { name: 'Confirmado' }, { timeout: 4000 })

    await userEvent.click(chip)
    expect(router.state.location.search).toMatchObject({ status: 'confirmado', lente: 'minha' })
    expect(chip).toHaveAttribute('aria-pressed', 'true')

    await userEvent.type(screen.getByRole('searchbox', { name: 'Buscar por nome' }), 'silva')
    expect(Object.keys(router.state.location.search)).toEqual(
      expect.not.arrayContaining(['busca', 'q', 'query']),
    )
    expect(JSON.stringify(router.state.location.search)).not.toContain('silva')

    router.history.back()
    await waitFor(() => expect(router.state.location.search).not.toHaveProperty('status'))
    expect(await screen.findByRole('button', { name: 'Confirmado' })).toHaveAttribute(
      'aria-pressed',
      'false',
    )
  })

  it('os filtros do Mapa de Escopo moram na URL e o botão voltar os desfaz (F-PLN-08)', async () => {
    const api = planningApi()
    api.handlers['GET /api/v1/wedding/scope'] = jsonResponse(200, {
      groups: [
        {
          id: 'g1',
          name: 'Grupo Exemplo',
          position: 0,
          origin: 'casal',
          hidden: false,
          can_delete: false,
          version: 1,
          categories: [
            {
              id: '0190a1b2-c3d4-7e5f-8a9b-0c1d2e3f4a5b',
              group_id: 'g1',
              name: 'Fotografia Exemplo',
              position: 0,
              origin: 'casal',
              hidden: false,
              visible: true,
              status: 'Em discussão',
              estimate_cents: null,
              discard_reason: null,
              noivo: { priority: null, note: null, version: 1 },
              noiva: { priority: null, note: null, version: 1 },
              alignment: { state: 'falta', missing: ['Noivo', 'Noiva'] },
              can_delete: true,
              version: 1,
            },
          ],
        },
      ],
      progress: { classified: 0, total: 1 },
      totals: {
        essential_cents: 0,
        essential_without_estimate: 0,
        maybe_cents: 0,
        maybe_without_estimate: 0,
      },
    })
    const router = await renderRoute('/planejamento?aba=escopo&lente=minha', { api })
    const chip = await screen.findByRole('button', { name: 'Fica de fora' }, { timeout: 4000 })
    await userEvent.click(chip)
    expect(router.state.location.search).toMatchObject({
      aba: 'escopo',
      status: 'fora',
      lente: 'minha',
    })
    expect(chip).toHaveAttribute('aria-pressed', 'true')

    router.history.back()
    await waitFor(() => expect(router.state.location.search).not.toHaveProperty('status'))
    expect(await screen.findByRole('button', { name: 'Fica de fora' })).toHaveAttribute(
      'aria-pressed',
      'false',
    )
  })

  it('um parâmetro inválido na URL é ignorado, e a página abre normalmente', async () => {
    await renderRoute('/planejamento?aba=lixo&status=quase', { api: planningApi() })
    expect(await screen.findByRole('heading', { level: 1, name: 'O rumo de vocês' })).toBeVisible()
    expect(screen.getByRole('tab', { name: 'Definições Base' })).toHaveAttribute(
      'aria-selected',
      'true',
    )
  })
})
