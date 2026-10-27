import { afterEach, describe, expect, expectTypeOf, it, vi } from 'vitest'
import { api, createApiClient, problemCode } from './client'
import type { components } from './schema'

type ProblemDetails = components['schemas']['ProblemDetails']

function json(status: number, body: unknown, contentType = 'application/json') {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': contentType },
  })
}

function stubFetch(response: Response) {
  // Um clone por chamada: o corpo de um Response só pode ser lido uma vez.
  const fetchMock = vi.fn(async (_request: Request) => response.clone())
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

function sentRequest(fetchMock: ReturnType<typeof stubFetch>): Request {
  const [request] = fetchMock.mock.calls[0] ?? []
  if (!request) throw new Error('nenhuma requisição foi enviada')
  return request
}

const CURRENT_USER = { user_id: 'u-1', username: 'exemplo.noivo', profile: 'Noivo' }
const LOGIN_BODY = { username: 'exemplo.noivo', password: 'senha-exemplo-12345' }

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('cliente da API', () => {
  it('envia o header anti-CSRF nos métodos que alteram dados', async () => {
    const fetchMock = stubFetch(json(200, CURRENT_USER))
    await api.POST('/api/v1/auth/login', { body: LOGIN_BODY })
    expect(sentRequest(fetchMock).headers.get('X-Altare-CSRF')).toBe('1')
  })

  it('envia o header também no logout, que não tem corpo', async () => {
    const fetchMock = stubFetch(new Response(null, { status: 204 }))
    await api.POST('/api/v1/auth/logout')
    expect(sentRequest(fetchMock).headers.get('X-Altare-CSRF')).toBe('1')
  })

  it('não envia o header em leitura', async () => {
    const fetchMock = stubFetch(json(200, CURRENT_USER))
    await api.GET('/api/v1/auth/me')
    expect(sentRequest(fetchMock).headers.has('X-Altare-CSRF')).toBe(false)
  })

  it('chama a mesma origem, com URL absoluta, e leva o cookie da sessão', async () => {
    const fetchMock = stubFetch(json(200, CURRENT_USER))
    await api.GET('/api/v1/auth/me')
    const request = sentRequest(fetchMock)
    expect(request.url).toBe(`${window.location.origin}/api/v1/auth/me`)
    expect(request.credentials).toBe('same-origin')
  })

  it('resolve o fetch na hora da chamada, para os testes poderem trocá-lo', async () => {
    const primeiro = stubFetch(json(200, CURRENT_USER))
    await api.GET('/api/v1/auth/me')
    const segundo = stubFetch(json(200, CURRENT_USER))
    await api.GET('/api/v1/auth/me')
    expect([primeiro.mock.calls.length, segundo.mock.calls.length]).toEqual([1, 1])
  })

  it('devolve os dados tipados quando dá certo', async () => {
    stubFetch(json(200, CURRENT_USER))
    const { data, error } = await api.GET('/api/v1/auth/me')
    expect(error).toBeUndefined()
    expect(data?.profile).toBe('Noivo')
    expectTypeOf(data).toEqualTypeOf<components['schemas']['CurrentUserOut'] | undefined>()
  })

  it('devolve o erro do problem+json tipado, para decidir pelo code', async () => {
    const problema: ProblemDetails = {
      type: 'about:blank',
      title: 'Usuário ou senha inválidos',
      status: 401,
      code: 'invalid_credentials',
      detail: 'Confira o usuário e a senha e tente de novo.',
    }
    stubFetch(json(401, problema, 'application/problem+json'))
    const { data, error } = await api.POST('/api/v1/auth/login', { body: LOGIN_BODY })
    expect(data).toBeUndefined()
    expect(error?.code).toBe('invalid_credentials')
    expect(problemCode(error)).toBe('invalid_credentials')
    expectTypeOf(error).toEqualTypeOf<ProblemDetails | undefined>()
  })

  it('deixa a falha de rede subir, para a tela tratar sem perder o que foi digitado', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        throw new TypeError('Failed to fetch')
      }),
    )
    await expect(api.GET('/api/v1/auth/me')).rejects.toThrow('Failed to fetch')
  })

  it('cada cliente criado tem o seu próprio middleware', async () => {
    const fetchMock = stubFetch(json(200, CURRENT_USER))
    await createApiClient().POST('/api/v1/auth/login', { body: LOGIN_BODY })
    await createApiClient().POST('/api/v1/auth/login', { body: LOGIN_BODY })
    const headers = fetchMock.mock.calls.map(([request]) => request.headers.get('X-Altare-CSRF'))
    expect(headers).toEqual(['1', '1'])
  })
})

describe('problemCode', () => {
  it('lê o code de um problema', () => {
    expect(problemCode({ code: 'version_conflict', status: 409 })).toBe('version_conflict')
  })

  it.each([undefined, null, 'texto', 42, {}, { code: 7 }])('devolve nada para %j', (valor) => {
    expect(problemCode(valor)).toBeUndefined()
  })
})
