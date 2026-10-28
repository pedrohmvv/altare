import { ApiError } from '@/lib/api/errors'
import { copy } from '../copy'

/** A frase para quem errou: a da API, em português, quando ela respondeu; o aviso de rede quando não. */
export function scopeErrorText(error: unknown): { conflict: boolean; text: string } {
  if (error instanceof ApiError) {
    if (error.code === 'version_conflict') {
      return { conflict: true, text: copy.scope.manage.conflict }
    }
    return { conflict: false, text: error.message }
  }
  return { conflict: false, text: copy.scope.manage.network }
}
