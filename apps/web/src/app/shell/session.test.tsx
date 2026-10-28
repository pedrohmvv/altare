import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { identityKeys } from '@/features/identity'
import { jsonResponse, mockApi, problemResponse } from '@/test/fake-api'
import { FAKE_NOIVO, renderRoute } from '@/test/render-route'

const ME = 'GET /api/v1/auth/me'
const LOGOUT = 'POST /api/v1/auth/logout'
const NOIVA = { ...FAKE_NOIVO, profile: 'Noiva' as const, username: 'exemplo.noiva' }

function api(overrides = {}) {
  return mockApi({
    [ME]: jsonResponse(200, FAKE_NOIVO),
    [LOGOUT]: new Response(null, { status: 204 }),
    ...overrides,
  })
}

/** O jsdom não tem `matchMedia`; com ele a casca mostra a barra larga em vez do trilho. */
function viewportWide() {
  vi.stubGlobal('matchMedia', (query: string) => ({
    matches: true,
    media: query,
    addEventListener() {},
    removeEventListener() {},
  }))
}

const aside = () => within(screen.getByRole('complementary'))

describe('bloco de sessão na barra lateral larga (guia, pág. 38)', () => {
  it('mostra o perfil e "sessão individual" no pé, como o desenho do guia', async () => {
    viewportWide()
    await renderRoute('/', { api: api() })
    await screen.findByRole('heading', { level: 1, name: 'O momento de vocês' })

    const bloco = aside().getByRole('button', { name: /Noivo.*sessão individual/ })
    expect(bloco).toBeVisible()
    expect(within(bloco).getByText('Noivo')).toBeVisible()
    expect(within(bloco).getByText('sessão individual')).toBeVisible()
  })

  it('mostra Noiva quando é a Noiva que está na sessão', async () => {
    viewportWide()
    await renderRoute('/', { api: api({ [ME]: jsonResponse(200, NOIVA) }) })
    await screen.findByRole('heading', { level: 1, name: 'O momento de vocês' })

    expect(aside().getByRole('button', { name: /Noiva.*sessão individual/ })).toBeVisible()
  })

  it('abre um cartão com o perfil e o botão Sair, e o Esc o fecha devolvendo o foco', async () => {
    viewportWide()
    const user = userEvent.setup()
    await renderRoute('/', { api: api() })
    await screen.findByRole('heading', { level: 1, name: 'O momento de vocês' })
    const bloco = aside().getByRole('button', { name: /Noivo.*sessão individual/ })

    await user.click(bloco)
    const cartao = await screen.findByRole('dialog', { name: 'Noivo' })
    expect(within(cartao).getByRole('button', { name: 'Sair' })).toBeVisible()

    await user.keyboard('{Escape}')
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(bloco).toHaveFocus()
  })

  it('é alcançável e operável só com o teclado', async () => {
    viewportWide()
    const user = userEvent.setup()
    await renderRoute('/', { api: api() })
    await screen.findByRole('heading', { level: 1, name: 'O momento de vocês' })
    const bloco = aside().getByRole('button', { name: /Noivo.*sessão individual/ })

    bloco.focus()
    await user.keyboard('{Enter}')
    expect(await screen.findByRole('dialog', { name: 'Noivo' })).toBeVisible()
  })

  it('Sair encerra a sessão no servidor, vai para a entrada e esquece os dados da sessão', async () => {
    viewportWide()
    const user = userEvent.setup()
    const fake = api()
    const router = await renderRoute('/orcamento', { api: fake })
    await screen.findByRole('heading', { level: 1, name: 'O orçamento de vocês' })

    await user.click(aside().getByRole('button', { name: /Noivo.*sessão individual/ }))
    await user.click(await screen.findByRole('button', { name: 'Sair' }))

    expect(
      await screen.findByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' }),
    ).toBeVisible()
    expect(router.state.location.pathname).toBe('/entrar')
    expect(fake.callsTo(LOGOUT)).toHaveLength(1)
    expect(fake.callsTo(LOGOUT)[0]?.request.headers.get('X-Altare-CSRF')).toBe('1')
    expect(router.options.context.queryClient.getQueryData(identityKeys.me)).toBeUndefined()
  })

  it('depois de sair, voltar a uma área leva à entrada e não à tela anterior', async () => {
    viewportWide()
    const user = userEvent.setup()
    const fake = api()
    const router = await renderRoute('/orcamento', { api: fake })
    await screen.findByRole('heading', { level: 1, name: 'O orçamento de vocês' })
    await user.click(aside().getByRole('button', { name: /Noivo.*sessão individual/ }))
    await user.click(await screen.findByRole('button', { name: 'Sair' }))
    await screen.findByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' })

    fake.handlers[ME] = problemResponse(401, 'unauthenticated')
    await router.navigate({ to: '/contatos' })

    expect(
      await screen.findByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' }),
    ).toBeVisible()
  })

  it('se não conseguir sair, avisa com calma, fica na tela e deixa tentar de novo', async () => {
    viewportWide()
    const user = userEvent.setup()
    const fake = api({ [LOGOUT]: problemResponse(500, 'internal_error') })
    const router = await renderRoute('/orcamento', { api: fake })
    await screen.findByRole('heading', { level: 1, name: 'O orçamento de vocês' })
    await user.click(aside().getByRole('button', { name: /Noivo.*sessão individual/ }))

    await user.click(await screen.findByRole('button', { name: 'Sair' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Não foi possível sair agora')
    expect(router.state.location.pathname).toBe('/orcamento')
    expect(screen.getByRole('button', { name: 'Sair' })).toBeEnabled()
  })

  it('enquanto espera o servidor, o botão fica ocupado', async () => {
    viewportWide()
    const user = userEvent.setup()
    let responder: (resposta: Response) => void = () => {}
    const espera = new Promise<Response>((resolve) => {
      responder = resolve
    })
    await renderRoute('/', { api: api({ [LOGOUT]: () => espera }) })
    await screen.findByRole('heading', { level: 1, name: 'O momento de vocês' })
    await user.click(aside().getByRole('button', { name: /Noivo.*sessão individual/ }))

    await user.click(await screen.findByRole('button', { name: 'Sair' }))

    expect(await screen.findByRole('button', { name: 'Sair' })).toHaveAttribute('aria-busy', 'true')
    responder(new Response(null, { status: 204 }))
  })
})

describe('bloco de sessão no trilho do tablet', () => {
  it('vira um botão de ícone com o perfil e a sessão no nome', async () => {
    await renderRoute('/', { api: api() })
    await screen.findByRole('heading', { level: 1, name: 'O momento de vocês' })

    expect(aside().getByRole('button', { name: 'Noivo, sessão individual' })).toBeVisible()
  })

  it('abre o mesmo cartão, com o Sair', async () => {
    const user = userEvent.setup()
    await renderRoute('/', { api: api() })
    await screen.findByRole('heading', { level: 1, name: 'O momento de vocês' })

    await user.click(aside().getByRole('button', { name: 'Noivo, sessão individual' }))

    const cartao = await screen.findByRole('dialog', { name: 'Noivo' })
    expect(within(cartao).getByRole('button', { name: 'Sair' })).toBeVisible()
  })
})

describe('bloco de sessão na folha "Mais" do celular', () => {
  it('mostra o perfil e o botão Sair dentro da folha, sem um segundo cartão', async () => {
    const user = userEvent.setup()
    await renderRoute('/', { api: api() })
    await screen.findByRole('heading', { level: 1, name: 'O momento de vocês' })
    const barra = within(screen.getByRole('navigation', { name: 'Navegação principal (celular)' }))

    await user.click(barra.getByRole('button', { name: 'Mais' }))

    const folha = await screen.findByRole('dialog', { name: 'Mais áreas' })
    expect(within(folha).getByText('Noivo')).toBeVisible()
    expect(within(folha).getByText('sessão individual')).toBeVisible()
    expect(within(folha).getByRole('button', { name: 'Sair' })).toBeVisible()
  })

  it('Sair, na folha, encerra a sessão e leva à entrada', async () => {
    const user = userEvent.setup()
    const fake = api()
    await renderRoute('/', { api: fake })
    await screen.findByRole('heading', { level: 1, name: 'O momento de vocês' })
    const barra = within(screen.getByRole('navigation', { name: 'Navegação principal (celular)' }))
    await user.click(barra.getByRole('button', { name: 'Mais' }))

    await user.click(
      within(await screen.findByRole('dialog', { name: 'Mais áreas' })).getByRole('button', {
        name: 'Sair',
      }),
    )

    expect(
      await screen.findByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' }),
    ).toBeVisible()
    expect(fake.callsTo(LOGOUT)).toHaveLength(1)
  })
})
