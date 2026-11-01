import type { Side } from '../api/guests'

export type Lens = 'casal' | 'minha'
export type SessionProfile = 'Noivo' | 'Noiva'

/**
 * Os lados que a lente mostra por padrão (F-CNV-07). `Casal` mostra todos. `Minha visão` mostra o
 * meu lado mais o `Comum`, e o outro lado fica um toque atrás (`includeOther`). `undefined` quer
 * dizer "todos". A lente muda o foco e nunca a autoria: ninguém perde acesso a nada.
 */
export function visibleSides({
  lens,
  profile,
  includeOther,
}: {
  lens: Lens
  profile: SessionProfile
  includeOther: boolean
}): readonly Side[] | undefined {
  if (lens === 'casal' || includeOther) return undefined
  return [profile, 'Comum']
}
