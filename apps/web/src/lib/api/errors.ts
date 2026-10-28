import { problemCode } from './client'

const FALLBACK_DETAIL = 'Não foi possível concluir esta ação. Tente de novo em instantes.'

export interface FieldError {
  field: string
  message: string
}

/** A API respondeu, mas com um erro. Falha de rede é outra coisa: nela o `fetch` levanta TypeError. */
export class ApiError extends Error {
  readonly status: number
  /** `code` estável do problem+json; `http_error` quando o corpo não é um (um proxy, por exemplo). */
  readonly code: string
  readonly retryAfterSeconds: number | undefined
  readonly fieldErrors: FieldError[]

  constructor(error: unknown, response: Response) {
    super(detailOf(error))
    this.name = 'ApiError'
    this.status = response.status
    this.code = problemCode(error) ?? 'http_error'
    this.retryAfterSeconds = parseSeconds(response.headers.get('retry-after'))
    this.fieldErrors = fieldErrorsOf(error)
  }
}

function detailOf(error: unknown): string {
  if (typeof error === 'object' && error !== null && 'detail' in error) {
    if (typeof error.detail === 'string') return error.detail
  }
  return FALLBACK_DETAIL
}

function fieldErrorsOf(error: unknown): FieldError[] {
  if (typeof error !== 'object' || error === null || !('errors' in error)) return []
  if (!Array.isArray(error.errors)) return []
  return error.errors.filter(
    (item): item is FieldError =>
      typeof item?.field === 'string' && typeof item?.message === 'string',
  )
}

function parseSeconds(header: string | null): number | undefined {
  return header !== null && /^\d+$/.test(header) ? Number(header) : undefined
}

interface Result<Data> {
  data?: Data
  error?: unknown
  response: Response
}

/** Os dados de uma resposta; um erro da API vira `ApiError`. */
export function unwrap<Data>(result: Result<Data>): Data {
  if (result.error !== undefined) throw new ApiError(result.error, result.response)
  if (result.data === undefined) throw new Error('A API respondeu sem corpo')
  return result.data
}

/** Para respostas sem corpo (204): só confere que não houve erro. */
export function ensureOk(result: Omit<Result<never>, 'data'>): void {
  if (result.error !== undefined) throw new ApiError(result.error, result.response)
}
