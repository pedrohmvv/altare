import type { FieldPath, FieldValues, UseFormSetError } from 'react-hook-form'
import { ApiError } from '@/lib/api/errors'
import { copy } from '../copy'

export interface FormAlertState {
  kind: 'conflict' | 'error'
  text: string
}

/**
 * Para onde vai o erro da API: o `code` estável de máquina decide o campo, e o `detail` em
 * português é o texto. Conflito de versão e erro sem campo viram um aviso do formulário; falha de
 * rede mantém o que foi digitado.
 */
export function reportServerError<T extends FieldValues>(
  error: unknown,
  setError: UseFormSetError<T>,
  fieldByCode: Record<string, FieldPath<T>>,
): FormAlertState | null {
  if (!(error instanceof ApiError)) return { kind: 'error', text: copy.forms.errors.network }
  if (error.code === 'version_conflict') {
    return { kind: 'conflict', text: copy.forms.errors.conflict }
  }
  const field = fieldByCode[error.code]
  if (field) {
    setError(field, { message: error.message }, { shouldFocus: true })
    return null
  }
  return { kind: 'error', text: error.message }
}
