import { ApiError } from '@/lib/api/errors'

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
