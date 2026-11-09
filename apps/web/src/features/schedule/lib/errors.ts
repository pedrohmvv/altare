import { ApiError } from '@/lib/api/errors'
import { copy } from '../copy'

export interface AlertState {
  kind: 'conflict' | 'blocked' | 'error'
  text: string
}

/** As frases da tela para o que a API sinaliza por `code` e para a falha de rede. */
export interface AlertTexts {
  conflict: string
  /** Só onde o servidor pode recusar por bloqueio (as ações de estado); senão vale o aviso de rede. */
  blocked?: string
  network: string
}

/**
 * O `code` estável decide o comportamento e o texto é da tela; só um erro sem decisão própria usa a
 * frase da API (`detail`), em português. Falha de rede (sem resposta) vira o aviso de rede.
 */
export function alertFromError(error: unknown, texts: AlertTexts): AlertState {
  if (!(error instanceof ApiError)) return { kind: 'error', text: texts.network }
  // A ordem das fases que a tela mandou já não é a do servidor: o mesmo remédio do conflito.
  if (error.code === 'invalid_phase_order') return { kind: 'conflict', text: error.message }
  if (error.code === 'version_conflict') return { kind: 'conflict', text: texts.conflict }
  if (error.code === 'milestone_blocked')
    return { kind: 'blocked', text: texts.blocked ?? texts.network }
  return { kind: 'error', text: error.message }
}

/**
 * O checklist tem os próprios sinais: o limite de 50 itens é fato dito (não há o que recarregar), e
 * uma ordem que já não é a do servidor tem o mesmo remédio do conflito de versão.
 */
export function checklistAlertFromError(error: unknown): AlertState {
  const texts = copy.checklist.errors
  if (error instanceof ApiError && error.code === 'checklist_full') {
    return { kind: 'error', text: texts.full }
  }
  if (error instanceof ApiError && error.code === 'invalid_checklist_order') {
    return { kind: 'conflict', text: texts.conflict }
  }
  return alertFromError(error, { conflict: texts.conflict, network: texts.network })
}

/** Os códigos da API que dizem que o problema está no arquivo escolhido, não no resto do formulário. */
const FILE_CODES = new Set([
  'unsupported_file_type',
  'file_too_large',
  'empty_file',
  'attachment_file_not_allowed',
])

/**
 * Onde um erro de anexo aparece: `url` e `file` ficam junto do campo (a API diz o motivo em `detail`);
 * o resto (título ou comentário longos, falha de rede) vai ao aviso da seção.
 */
export function attachmentFieldOf(error: unknown): 'url' | 'file' | null {
  if (!(error instanceof ApiError)) return null
  if (error.code === 'invalid_attachment_url') return 'url'
  return FILE_CODES.has(error.code) ? 'file' : null
}

/** Um erro de anexo sem campo próprio: a frase da API (`detail`), ou o aviso de rede. */
export function attachmentAlertFromError(
  error: unknown,
  network: string = copy.attachments.errors.network,
): AlertState {
  return { kind: 'error', text: error instanceof ApiError ? error.message : network }
}
