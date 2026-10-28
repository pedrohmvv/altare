import { vi } from 'vitest'

type Handler = Response | ((request: Request) => Response | Promise<Response>)

/** Rotas por "MÉTODO /caminho"; uma requisição sem tratador falha alto, em vez de ir à rede. */
export type FakeApiHandlers = Record<string, Handler>

export function jsonResponse(status: number, body?: unknown, headers: Record<string, string> = {}) {
  return new Response(body === undefined ? null : JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json', ...headers },
  })
}

export function problemResponse(
  status: number,
  code: string,
  extra: { title?: string; detail?: string; headers?: Record<string, string> } = {},
) {
  const body = {
    type: 'about:blank',
    title: extra.title ?? 'Título do problema',
    status,
    code,
    detail: extra.detail ?? 'Detalhe do problema.',
  }
  return jsonResponse(status, body, {
    'content-type': 'application/problem+json',
    ...extra.headers,
  })
}

export function mockApi(handlers: FakeApiHandlers = {}) {
  const calls: { method: string; path: string; body: unknown; request: Request }[] = []

  const fetchMock = vi.fn(async (request: Request) => {
    const path = new URL(request.url).pathname
    const text = await request.clone().text()
    calls.push({
      method: request.method,
      path,
      body: text ? JSON.parse(text) : undefined,
      request,
    })
    const handler = handlers[`${request.method} ${path}`]
    if (!handler) throw new Error(`Requisição sem tratador no teste: ${request.method} ${path}`)
    return typeof handler === 'function' ? handler(request) : handler.clone()
  })
  vi.stubGlobal('fetch', fetchMock)

  return {
    handlers,
    calls,
    fetchMock,
    callsTo: (route: string) => calls.filter((call) => `${call.method} ${call.path}` === route),
  }
}

export type FakeApi = ReturnType<typeof mockApi>
