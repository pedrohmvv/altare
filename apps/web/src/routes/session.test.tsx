import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { ApiError } from '@/lib/api/errors'
import { jsonResponse, mockApi, problemResponse } from '@/test/fake-api'
import { FAKE_NOIVO, renderRoute } from '@/test/render-route'

const ME = 'GET /api/v1/auth/me'
const LOGIN = 'POST /api/v1/auth/login'
const SENHA = 'senha-exemplo-12345'

const semSessao = () => ({ [ME]: problemResponse(401, 'unauthenticated') })

function entrouComoNoivo() {
  return mockApi({ ...semSessao(), [LOGIN]: jsonResponse(200, FAKE_NOIVO) })
}

describe('guarda de sessão', () => {
  it('sem sessão, qualquer área leva à tela de entrada, guardando o destino', async () => {
    const router = await renderRoute('/orcamento?lente=minha', { session: null })

    expect(
      await screen.findByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' }),
    ).toBeVisible()
    expect(router.state.location.pathname).toBe('/entrar')
    expect(router.state.location.search).toMatchObject({ destino: '/orcamento?lente=minha' })
  })

  it('a tela de entrada não tem a casca: sem navegação, sem barra superior', async () => {
    await renderRoute('/', { session: null })
    await screen.findByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' })

    expect(screen.queryByRole('navigation')).not.toBeInTheDocument()
    expect(screen.queryByRole('complementary')).not.toBeInTheDocument()
  })

  it('a tela de entrada tem título de documento próprio', async () => {
    await renderRoute('/', { session: null })
    await screen.findByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' })

    expect(document.title).toBe('Entrar · Altare')
  })

  it('com sessão, a casca abre normalmente', async () => {
    await renderRoute('/orcamento')

    expect(
      await screen.findByRole('heading', { level: 1, name: 'O orçamento de vocês' }),
    ).toBeVisible()
    expect(screen.getByRole('navigation', { name: 'Navegação principal' })).toBeVisible()
  })

  it('um caminho desconhecido, sem sessão, também leva à entrada', async () => {
    const router = await renderRoute('/nao-existe', { session: null })

    await screen.findByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' })
    expect(router.state.location.pathname).toBe('/entrar')
  })

  it('a vitrine de desenvolvimento também fica atrás da guarda', async () => {
    const router = await renderRoute('/design-system', { session: null })

    await screen.findByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' })
    expect(router.state.location.pathname).toBe('/entrar')
  })

  it('falha de rede ao consultar a sessão também leva à entrada', async () => {
    const api = mockApi({
      [ME]: () => {
        throw new TypeError('Failed to fetch')
      },
    })
    const router = await renderRoute('/', { api })

    await screen.findByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' })
    expect(router.state.location.pathname).toBe('/entrar')
  })

  it('consulta a sessão uma vez só, mesmo navegando entre áreas', async () => {
    const api = mockApi({ [ME]: jsonResponse(200, FAKE_NOIVO) })
    await renderRoute('/', { api })
    await screen.findByRole('heading', { level: 1, name: 'O momento de vocês' })

    await userEvent.click(screen.getByRole('link', { name: 'Orçamento & Simulador' }))
    await screen.findByRole('heading', { level: 1, name: 'O orçamento de vocês' })

    expect(api.callsTo(ME)).toHaveLength(1)
  })
})

describe('rota /entrar', () => {
  it('quem já tem sessão vai direto para o destino', async () => {
    const router = await renderRoute('/entrar?destino=/orcamento')

    expect(
      await screen.findByRole('heading', { level: 1, name: 'O orçamento de vocês' }),
    ).toBeVisible()
    expect(router.state.location.pathname).toBe('/orcamento')
  })

  it('quem já tem sessão e não pediu destino vai para a Visão Geral', async () => {
    const router = await renderRoute('/entrar')

    expect(
      await screen.findByRole('heading', { level: 1, name: 'O momento de vocês' }),
    ).toBeVisible()
    expect(router.state.location.pathname).toBe('/')
  })

  it.each([
    ['//evil.example', 'URL sem protocolo'],
    ['https://evil.example/', 'URL absoluta'],
    ['javascript:alert(1)', 'esquema perigoso'],
  ])('ignora o destino %s (%s)', async (destino) => {
    const router = await renderRoute(`/entrar?destino=${encodeURIComponent(destino)}`, {
      session: null,
    })

    await screen.findByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' })
    expect(router.state.location.search).not.toHaveProperty('destino')
  })

  it('entrar leva ao destino guardado, já na casca e com o foco no título', async () => {
    const user = userEvent.setup()
    const router = await renderRoute('/orcamento', { api: entrouComoNoivo() })
    await screen.findByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' })

    await user.type(screen.getByLabelText(/Usuário/), 'exemplo.noivo')
    await user.type(screen.getByLabelText(/Senha/), SENHA)
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    const titulo = await screen.findByRole('heading', { level: 1, name: 'O orçamento de vocês' })
    expect(router.state.location.pathname).toBe('/orcamento')
    expect(screen.getByRole('navigation', { name: 'Navegação principal' })).toBeVisible()
    await waitFor(() => expect(titulo).toHaveFocus())
  })

  it('entrar sem destino guardado leva à Visão Geral', async () => {
    const user = userEvent.setup()
    await renderRoute('/entrar', { api: entrouComoNoivo() })
    await screen.findByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' })

    await user.type(screen.getByLabelText(/Usuário/), 'exemplo.noivo')
    await user.type(screen.getByLabelText(/Senha/), SENHA)
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(
      await screen.findByRole('heading', { level: 1, name: 'O momento de vocês' }),
    ).toBeVisible()
  })

  it('depois de entrar, a guarda não consulta a sessão de novo: o login já a trouxe', async () => {
    const user = userEvent.setup()
    const api = entrouComoNoivo()
    await renderRoute('/orcamento', { api })
    await screen.findByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' })
    const consultasAntes = api.callsTo(ME).length

    await user.type(screen.getByLabelText(/Usuário/), 'exemplo.noivo')
    await user.type(screen.getByLabelText(/Senha/), SENHA)
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    await screen.findByRole('heading', { level: 1, name: 'O orçamento de vocês' })

    expect(api.callsTo(ME)).toHaveLength(consultasAntes)
  })
})

describe('sessão que vence com o app aberto', () => {
  it('um 401 em qualquer consulta leva à entrada, guardando onde a pessoa estava', async () => {
    const router = await renderRoute('/orcamento')
    await screen.findByRole('heading', { level: 1, name: 'O orçamento de vocês' })

    await router.options.context.queryClient
      .fetchQuery({
        queryKey: ['orcamento', 'cenarios'],
        queryFn: () => {
          throw new ApiError({ code: 'unauthenticated' }, new Response(null, { status: 401 }))
        },
      })
      .catch(() => undefined)

    await screen.findByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' })
    expect(router.state.location.pathname).toBe('/entrar')
    expect(router.state.location.search).toMatchObject({ destino: '/orcamento' })
  })

  it('um erro que não é 401 não derruba a sessão', async () => {
    const router = await renderRoute('/orcamento')
    await screen.findByRole('heading', { level: 1, name: 'O orçamento de vocês' })

    await router.options.context.queryClient
      .fetchQuery({
        queryKey: ['orcamento', 'cenarios'],
        queryFn: () => {
          throw new ApiError({ code: 'internal_error' }, new Response(null, { status: 500 }))
        },
      })
      .catch(() => undefined)

    expect(router.state.location.pathname).toBe('/orcamento')
  })
})
