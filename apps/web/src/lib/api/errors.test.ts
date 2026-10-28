import { describe, expect, it } from 'vitest'
import { problemResponse } from '@/test/fake-api'
import { ApiError, ensureOk, unwrap } from './errors'

const PROBLEM = {
  type: 'about:blank',
  title: 'Muitas tentativas',
  status: 429,
  code: 'too_many_attempts',
  detail: 'Houve muitas tentativas de entrada.',
}

function response(status: number, headers: Record<string, string> = {}) {
  return new Response(null, { status, headers })
}

describe('ApiError', () => {
  it('guarda o code, o status e o detail do problema', () => {
    const erro = new ApiError(PROBLEM, response(429))
    expect(erro).toBeInstanceOf(Error)
    expect([erro.code, erro.status, erro.message]).toEqual([
      'too_many_attempts',
      429,
      'Houve muitas tentativas de entrada.',
    ])
  })

  it('lê o Retry-After em segundos', () => {
    expect(new ApiError(PROBLEM, response(429, { 'retry-after': '120' })).retryAfterSeconds).toBe(
      120,
    )
  })

  it.each([undefined, 'amanhã', ''])('ignora um Retry-After que não é número (%j)', (valor) => {
    const headers: Record<string, string> = valor === undefined ? {} : { 'retry-after': valor }
    expect(new ApiError(PROBLEM, response(429, headers)).retryAfterSeconds).toBeUndefined()
  })

  it('traz os erros por campo da validação', () => {
    const erro = new ApiError(
      {
        ...PROBLEM,
        status: 422,
        code: 'validation_error',
        errors: [{ field: 'username', message: 'x' }],
      },
      response(422),
    )
    expect(erro.fieldErrors).toEqual([{ field: 'username', message: 'x' }])
  })

  it('aguenta um corpo que não é problem+json, como a página de erro de um proxy', () => {
    const erro = new ApiError('<html>Bad Gateway</html>', response(502))
    expect([erro.code, erro.status, erro.fieldErrors]).toEqual(['http_error', 502, []])
    expect(erro.message).not.toContain('<html>')
  })
})

describe('unwrap e ensureOk', () => {
  it('devolve os dados quando deu certo', () => {
    expect(unwrap({ data: { ok: true }, response: response(200) })).toEqual({ ok: true })
  })

  it('levanta ApiError quando há erro', () => {
    expect(() => unwrap({ error: PROBLEM, response: response(429) })).toThrow(ApiError)
  })

  it('ensureOk aceita uma resposta sem corpo e levanta no erro', () => {
    expect(() => ensureOk({ response: response(204) })).not.toThrow()
    expect(() => ensureOk({ error: PROBLEM, response: response(403) })).toThrow(ApiError)
  })
})

describe('o fetch falso dos testes', () => {
  it('monta um problem+json com o media type certo', () => {
    expect(problemResponse(401, 'unauthenticated').headers.get('content-type')).toBe(
      'application/problem+json',
    )
  })
})
