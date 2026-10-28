import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { jsonResponse, mockApi, problemResponse } from '@/test/fake-api'
import { LoginPage } from './login-page'

const USER = { user_id: 'u-1', username: 'exemplo.noivo', profile: 'Noivo' }
const LOGIN = 'POST /api/v1/auth/login'

function renderPage(handlers = {}, onAuthenticated = vi.fn()) {
  const api = mockApi({ [LOGIN]: jsonResponse(200, USER), ...handlers })
  render(
    <QueryClientProvider
      client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
    >
      <LoginPage onAuthenticated={onAuthenticated} />
    </QueryClientProvider>,
  )
  return { api, onAuthenticated, user: userEvent.setup() }
}

async function fill(user: ReturnType<typeof userEvent.setup>, username: string, password: string) {
  if (username) await user.type(screen.getByLabelText(/Usuário/), username)
  if (password) await user.type(screen.getByLabelText(/Senha/), password)
}

describe('LoginPage: conteúdo (guia, pág. 37)', () => {
  it('traz a saudação como o único h1, o apoio, os campos, o botão e a nota', () => {
    renderPage()
    expect(screen.getByRole('heading', { level: 1, name: 'Bem-vindos ao Altare.' })).toBeVisible()
    expect(screen.getByText('Entre com o seu usuário.')).toBeVisible()
    expect(screen.getByLabelText(/Usuário/)).toHaveAttribute('placeholder', 'noivo ou noiva')
    expect(screen.getByRole('button', { name: 'Entrar' })).toBeVisible()
    expect(screen.getByText('Acesso exclusivo do casal.')).toBeVisible()
  })

  it('está dentro de um main, para o anúncio de rota achar o h1', () => {
    renderPage()
    expect(screen.getByRole('main')).toContainElement(screen.getByRole('heading', { level: 1 }))
  })

  it('usa os atributos que deixam o navegador e o gerenciador de senhas ajudarem', () => {
    renderPage()
    const usuario = screen.getByLabelText(/Usuário/)
    const senha = screen.getByLabelText(/Senha/)
    expect(usuario).toHaveAttribute('autocomplete', 'username')
    expect(usuario).toHaveAttribute('autocapitalize', 'none')
    expect(senha).toHaveAttribute('type', 'password')
    expect(senha).toHaveAttribute('autocomplete', 'current-password')
  })

  it('mostra a marca uma vez, com nome, e deixa o arco e o ramo mudos', () => {
    renderPage()
    expect(screen.getAllByRole('img', { name: 'Altare' })).toHaveLength(1)
    const imagens = document.querySelectorAll('img')
    const decorativas = [...imagens].filter((img) => img.getAttribute('alt') === '')
    expect(decorativas).toHaveLength(2)
  })

  it('tem uma região de alerta vazia desde o início, para o aviso ser anunciado', () => {
    renderPage()
    expect(screen.getByRole('alert')).toBeEmptyDOMElement()
  })
})

describe('LoginPage: preenchimento', () => {
  it('pede o que falta, com o erro ligado ao campo, e leva o foco ao primeiro inválido', async () => {
    const { api, user } = renderPage()
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    const usuario = screen.getByLabelText(/Usuário/)
    expect(await screen.findByText('Informe o usuário.')).toBeVisible()
    expect(screen.getByText('Informe a senha.')).toBeVisible()
    expect(usuario).toHaveAttribute('aria-invalid', 'true')
    expect(usuario).toHaveAccessibleDescription('Informe o usuário.')
    expect(usuario).toHaveFocus()
    expect(api.callsTo(LOGIN)).toHaveLength(0)
  })

  it('avisa ao sair do campo vazio, sem esperar o envio', async () => {
    const { user } = renderPage()
    await user.click(screen.getByLabelText(/Usuário/))
    await user.tab()
    expect(await screen.findByText('Informe o usuário.')).toBeVisible()
  })

  it('trata espaços como vazio no usuário', async () => {
    const { user } = renderPage()
    await fill(user, '   ', 'senha-exemplo-12345')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(await screen.findByText('Informe o usuário.')).toBeVisible()
  })
})

describe('LoginPage: entrada', () => {
  it('envia o usuário e a senha e avisa quem chamou', async () => {
    const { api, onAuthenticated, user } = renderPage()
    await fill(user, 'exemplo.noivo', 'senha-exemplo-12345')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    await waitFor(() => expect(onAuthenticated).toHaveBeenCalledTimes(1))
    expect(api.callsTo(LOGIN)[0]?.body).toEqual({
      username: 'exemplo.noivo',
      password: 'senha-exemplo-12345',
    })
    expect(api.callsTo(LOGIN)[0]?.request.headers.get('X-Altare-CSRF')).toBe('1')
  })

  it('entra também com Enter no campo de senha', async () => {
    const { onAuthenticated, user } = renderPage()
    await fill(user, 'exemplo.noivo', 'senha-exemplo-12345')
    await user.keyboard('{Enter}')
    await waitFor(() => expect(onAuthenticated).toHaveBeenCalled())
  })

  it('bloqueia o botão e o marca como ocupado enquanto espera a resposta', async () => {
    let responder: (resposta: Response) => void = () => {}
    const espera = new Promise<Response>((resolve) => {
      responder = resolve
    })
    const { user } = renderPage({ [LOGIN]: () => espera })
    await fill(user, 'exemplo.noivo', 'senha-exemplo-12345')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    const botao = await screen.findByRole('button', { name: 'Entrar' })
    expect(botao).toBeDisabled()
    expect(botao).toHaveAttribute('aria-busy', 'true')
    responder(jsonResponse(200, USER))
  })
})

describe('LoginPage: erros, pelo code e não pelo texto', () => {
  it('senha errada: mostra o detalhe do servidor, guarda o usuário e leva o foco à senha vazia', async () => {
    const { onAuthenticated, user } = renderPage({
      [LOGIN]: problemResponse(401, 'invalid_credentials', {
        detail: 'Confira o usuário e a senha e tente de novo.',
      }),
    })
    await fill(user, 'exemplo.noivo', 'senha-errada-123')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Confira o usuário e a senha e tente de novo.',
    )
    expect(screen.getByLabelText(/Usuário/)).toHaveValue('exemplo.noivo')
    expect(screen.getByLabelText(/Senha/)).toHaveValue('')
    expect(screen.getByLabelText(/Senha/)).toHaveFocus()
    expect(onAuthenticated).not.toHaveBeenCalled()
  })

  it.each([
    [900, '15 minutos'],
    [60, '1 minuto'],
    [61, '2 minutos'],
    [1, '1 minuto'],
  ])('muitas tentativas com espera de %is: diz "%s"', async (segundos, texto) => {
    const { user } = renderPage({
      [LOGIN]: problemResponse(429, 'too_many_attempts', {
        headers: { 'retry-after': String(segundos) },
      }),
    })
    await fill(user, 'exemplo.noivo', 'senha-exemplo-12345')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent(`em ${texto}`)
    expect(screen.getByLabelText(/Usuário/)).toHaveValue('exemplo.noivo')
  })

  it('muitas tentativas sem Retry-After usa o detalhe do servidor', async () => {
    const { user } = renderPage({
      [LOGIN]: problemResponse(429, 'too_many_attempts', { detail: 'Aguarde alguns minutos.' }),
    })
    await fill(user, 'exemplo.noivo', 'senha-exemplo-12345')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Aguarde alguns minutos.')
  })

  it('falha de rede: avisa com calma e NÃO apaga o que foi digitado', async () => {
    const { user } = renderPage({
      [LOGIN]: () => {
        throw new TypeError('Failed to fetch')
      },
    })
    await fill(user, 'exemplo.noivo', 'senha-exemplo-12345')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Não conseguimos falar com o servidor',
    )
    expect(screen.getByLabelText(/Usuário/)).toHaveValue('exemplo.noivo')
    expect(screen.getByLabelText(/Senha/)).toHaveValue('senha-exemplo-12345')
    expect(screen.getByRole('button', { name: 'Entrar' })).toBeEnabled()
  })

  it('erro por campo do servidor vai para o campo certo', async () => {
    const { user } = renderPage({
      [LOGIN]: jsonResponse(
        422,
        {
          type: 'about:blank',
          title: 'Dados inválidos',
          status: 422,
          code: 'validation_error',
          detail: 'Alguns campos precisam de ajuste.',
          errors: [{ field: 'password', message: 'Valor inválido.' }],
        },
        { 'content-type': 'application/problem+json' },
      ),
    })
    await fill(user, 'exemplo.noivo', 'senha-exemplo-12345')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(await screen.findByText('Valor inválido.')).toBeVisible()
    expect(screen.getByLabelText(/Senha/)).toHaveAttribute('aria-invalid', 'true')
  })

  it('erro inesperado do servidor mostra o detalhe dele, sem jargão técnico', async () => {
    const { user } = renderPage({
      [LOGIN]: problemResponse(500, 'internal_error', { detail: 'Algo deu errado do nosso lado.' }),
    })
    await fill(user, 'exemplo.noivo', 'senha-exemplo-12345')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Algo deu errado do nosso lado.')
  })

  it('resposta que nem é problem+json cai no texto padrão da tela', async () => {
    const { user } = renderPage({
      [LOGIN]: new Response('<html>Bad Gateway</html>', {
        status: 502,
        headers: { 'content-type': 'text/html' },
      }),
    })
    await fill(user, 'exemplo.noivo', 'senha-exemplo-12345')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Não foi possível concluir esta ação',
    )
  })

  it('depois de um erro, uma nova tentativa que dá certo limpa o aviso', async () => {
    const { api, onAuthenticated, user } = renderPage({
      [LOGIN]: problemResponse(401, 'invalid_credentials', { detail: 'Confira os dados.' }),
    })
    await fill(user, 'exemplo.noivo', 'errada-errada-1')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Confira os dados.')
    api.handlers[LOGIN] = jsonResponse(200, USER)
    await user.type(screen.getByLabelText(/Senha/), 'senha-exemplo-12345')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))
    await waitFor(() => expect(onAuthenticated).toHaveBeenCalled())
    expect(screen.getByRole('alert')).toBeEmptyDOMElement()
  })
})
