import type { ScopeMap } from '@/features/wedding/api/scope'

export const EVAL = { priority: null, note: null, version: 1 } as const

export function cat(over: Record<string, unknown>) {
  return {
    group_id: 'g-a',
    position: 0,
    origin: 'catalogo',
    hidden: false,
    visible: true,
    status: 'Em discussão',
    estimate_cents: null,
    discard_reason: null,
    noivo: EVAL,
    noiva: EVAL,
    alignment: { state: 'falta', missing: ['Noivo', 'Noiva'] },
    can_delete: false,
    version: 1,
    ...over,
  }
}

export const MAP = {
  groups: [
    {
      id: 'g-a',
      name: 'Grupo Exemplo A',
      position: 0,
      origin: 'catalogo',
      hidden: false,
      can_delete: false,
      version: 1,
      categories: [
        cat({
          id: 'c-foto',
          name: 'Fotografia Exemplo',
          status: 'Entra (Essencial)',
          estimate_cents: 150_000,
          alignment: { state: 'divergem', missing: [] },
          noivo: { ...EVAL, priority: 'Quero muito' },
          noiva: { ...EVAL, priority: 'Dispenso' },
        }),
        cat({
          id: 'c-video',
          name: 'Vídeo Exemplo',
          position: 1,
          noivo: { ...EVAL, priority: 'Se couber' },
          alignment: { state: 'falta', missing: ['Noiva'] },
        }),
        cat({ id: 'c-oculta', name: 'Oculta Exemplo', position: 2, hidden: true, visible: false }),
      ],
    },
    {
      id: 'g-b',
      name: 'Grupo Exemplo B',
      position: 1,
      origin: 'casal',
      hidden: false,
      can_delete: false,
      version: 1,
      categories: [
        cat({
          id: 'c-buffet',
          group_id: 'g-b',
          name: 'Buffet Exemplo',
          status: 'Fica de fora',
          discard_reason: 'fora do teto',
          alignment: { state: 'alinhados', missing: [] },
          noivo: { ...EVAL, priority: 'Dispenso' },
          noiva: { ...EVAL, priority: 'Dispenso' },
        }),
      ],
    },
  ],
  progress: { classified: 2, total: 3 },
  totals: {
    essential_cents: 150_000,
    essential_without_estimate: 0,
    maybe_cents: 0,
    maybe_without_estimate: 2,
  },
} as unknown as ScopeMap
