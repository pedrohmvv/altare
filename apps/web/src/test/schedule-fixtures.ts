import type { Schedule, ScheduleMilestone } from '@/features/schedule/api/schedule'

/** Ids fixos e válidos como UUID: a URL só aceita este formato. */
export const ID = {
  concluido: '00000000-0000-4000-8000-000000000001',
  destravado: '00000000-0000-4000-8000-000000000002',
  bloqueado: '00000000-0000-4000-8000-000000000003',
  arquivado: '00000000-0000-4000-8000-000000000004',
  categoria: '00000000-0000-4000-8000-000000000005',
  opcional: '00000000-0000-4000-8000-000000000006',
  aviso: '00000000-0000-4000-8000-000000000007',
  andamento: '00000000-0000-4000-8000-000000000008',
} as const

export function milestone(over: Partial<ScheduleMilestone> & { id: string; title: string }) {
  return {
    position: 0,
    responsible: 'Ambos',
    note: null,
    target_date: null,
    state: 'Destravado',
    optional: false,
    archived: false,
    overdue: false,
    blocked_by: [],
    depends_on: [],
    unlocks: [],
    warnings: [],
    category: null,
    version: 1,
    ...over,
  } satisfies ScheduleMilestone
}

/** Duas fases de exemplo, com um marco de cada situação que a tela precisa mostrar. */
export const SCHEDULE: Schedule = {
  has_exact_date: false,
  phases: [
    {
      id: 'f-1',
      title: 'Fase Exemplo Um',
      position: 0,
      progress: { done: 1, total: 3 },
      milestones: [
        milestone({
          id: ID.concluido,
          title: 'Marco Exemplo Concluído',
          position: 0,
          state: 'Concluído',
          unlocks: [{ id: ID.destravado, title: 'Marco Exemplo Destravado' }],
        }),
        milestone({
          id: ID.destravado,
          title: 'Marco Exemplo Destravado',
          position: 1,
          responsible: 'Noiva',
          target_date: '2027-03-15',
          note: 'Nota de exemplo.',
          category: { id: 'c-espaco', name: 'Espaço Exemplo' },
          depends_on: [{ id: ID.concluido, title: 'Marco Exemplo Concluído', resolved: true }],
          unlocks: [{ id: ID.bloqueado, title: 'Marco Exemplo Bloqueado' }],
        }),
        milestone({
          id: ID.bloqueado,
          title: 'Marco Exemplo Bloqueado',
          position: 2,
          state: 'Bloqueado',
          blocked_by: [
            { kind: 'milestone', milestone_id: ID.destravado, label: 'Marco Exemplo Destravado' },
          ],
          depends_on: [{ id: ID.destravado, title: 'Marco Exemplo Destravado', resolved: false }],
        }),
        milestone({
          id: ID.arquivado,
          title: 'Marco Exemplo Arquivado',
          position: 3,
          archived: true,
        }),
      ],
    },
    {
      id: 'f-2',
      title: 'Fase Exemplo Dois',
      position: 1,
      progress: { done: 1, total: 4 },
      milestones: [
        milestone({
          id: ID.categoria,
          title: 'Marco Exemplo da Categoria',
          position: 0,
          state: 'Bloqueado',
          category: { id: 'c-buffet', name: 'Buffet Exemplo' },
          blocked_by: [
            {
              kind: 'category',
              milestone_id: null,
              label: 'Aguardando classificar a categoria no Mapa de Escopo',
            },
          ],
        }),
        milestone({
          id: ID.opcional,
          title: 'Marco Exemplo Opcional',
          position: 1,
          optional: true,
          overdue: true,
          target_date: '2020-01-15',
        }),
        milestone({
          id: ID.aviso,
          title: 'Marco Exemplo com Aviso',
          position: 2,
          state: 'Concluído',
          warnings: [
            {
              kind: 'depends_on_unresolved',
              milestone_id: ID.bloqueado,
              title: 'Marco Exemplo Bloqueado',
            },
            {
              kind: 'depends_on_unresolved',
              milestone_id: ID.categoria,
              title: 'Marco Exemplo da Categoria',
            },
          ],
        }),
        milestone({
          id: ID.andamento,
          title: 'Marco Exemplo em Andamento',
          position: 3,
          state: 'Em andamento',
          blocked_by: [
            { kind: 'milestone', milestone_id: ID.bloqueado, label: 'Marco Exemplo Bloqueado' },
          ],
        }),
      ],
    },
  ],
}

/** O cronograma de exemplo com uma mudança num marco, como a API devolveria depois de uma escrita. */
export function scheduleWith(id: string, change: Partial<ScheduleMilestone>): Schedule {
  return {
    ...SCHEDULE,
    phases: SCHEDULE.phases.map((phase) => ({
      ...phase,
      milestones: phase.milestones.map((item) => (item.id === id ? { ...item, ...change } : item)),
    })),
  }
}
