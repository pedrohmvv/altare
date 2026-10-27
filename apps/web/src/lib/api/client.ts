import createClient, { type Middleware } from 'openapi-fetch'
import type { paths } from './schema'

const CSRF_HEADER = 'X-Altare-CSRF'
const MUTATING_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])

/** A API exige o header em todo método que altera dados; sem ele, 403 `csrf_missing`. */
const csrf: Middleware = {
  onRequest({ request }) {
    if (MUTATING_METHODS.has(request.method)) request.headers.set(CSRF_HEADER, '1')
    return request
  },
}

export function createApiClient() {
  const client = createClient<paths>({
    baseUrl: window.location.origin,
    credentials: 'same-origin',
    // Resolvido na hora da chamada: um `fetch` guardado na criação não aceitaria o dos testes.
    fetch: (request) => globalThis.fetch(request),
  })
  client.use(csrf)
  return client
}

export const api = createApiClient()

/** O `code` estável de um `problem+json`, para decidir o comportamento sem ler a mensagem. */
export function problemCode(error: unknown): string | undefined {
  if (typeof error === 'object' && error !== null && 'code' in error) {
    return typeof error.code === 'string' ? error.code : undefined
  }
  return undefined
}
