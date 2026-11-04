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
  novo: '00000000-0000-4000-8000-000000000009',
  faseUm: '00000000-0000-4000-8000-0000000000f1',
  faseDois: '00000000-0000-4000-8000-0000000000f2',
  faseVazia: '00000000-0000-4000-8000-0000000000f3',
  espaco: '00000000-0000-4000-8000-0000000000c1',
  buffet: '00000000-0000-4000-8000-0000000000c2',
  musica: '00000000-0000-4000-8000-0000000000c3',
  janelaSugerida: '00000000-0000-4000-8000-0000000000a1',
  janelaEditada: '00000000-0000-4000-8000-0000000000a2',
  prazoManual: '00000000-0000-4000-8000-0000000000a3',
  atrasadoComJanela: '00000000-0000-4000-8000-0000000000a4',
  semJanela: '00000000-0000-4000-8000-0000000000a5',
  semPrazo: '00000000-0000-4000-8000-0000000000a6',
} as const

/**
 * Um marco com os padrões do Modo Sem Data: sem janela, sem prazo calculado e sem contagem. O prazo
 * efetivo acompanha o manual, como a API faz quando não há janela. Quem testa o Modo Com Data
 * passa os campos derivados que o servidor calcularia (`window`, `window_start`, `days_left`...).
 */
export function milestone(over: Partial<ScheduleMilestone> & { id: string; title: string }) {
  return {
    position: 0,
    responsible: 'Ambos',
    note: null,
    target_date: null,
    window: null,
    window_start: null,
    window_end: null,
    effective_target: over.target_date ?? null,
    days_left: null,
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
  category_options: [
    { id: ID.espaco, name: 'Espaço Exemplo' },
    { id: ID.buffet, name: 'Buffet Exemplo' },
    { id: ID.musica, name: 'Música Exemplo' },
  ],
  phases: [
    {
      id: ID.faseUm,
      title: 'Fase Exemplo Um',
      position: 0,
      version: 1,
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
          category: { id: ID.espaco, name: 'Espaço Exemplo' },
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
      id: ID.faseDois,
      title: 'Fase Exemplo Dois',
      position: 1,
      version: 2,
      progress: { done: 1, total: 4 },
      milestones: [
        milestone({
          id: ID.categoria,
          title: 'Marco Exemplo da Categoria',
          position: 0,
          state: 'Bloqueado',
          category: { id: ID.buffet, name: 'Buffet Exemplo' },
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
export function scheduleWith(
  id: string,
  change: Partial<ScheduleMilestone>,
  base: Schedule = SCHEDULE,
): Schedule {
  return {
    ...base,
    phases: base.phases.map((phase) => ({
      ...phase,
      milestones: phase.milestones.map((item) => (item.id === id ? { ...item, ...change } : item)),
    })),
  }
}

/** O cronograma de exemplo com uma fase a mais, sem marco nenhum. */
export function scheduleWithEmptyPhase(): Schedule {
  return {
    ...SCHEDULE,
    phases: [
      ...SCHEDULE.phases,
      {
        id: ID.faseVazia,
        title: 'Fase Exemplo Três',
        position: 2,
        version: 3,
        progress: { done: 0, total: 0 },
        milestones: [],
      },
    ],
  }
}

/** O cronograma de exemplo com um marco novo no fim de uma fase, como a API o devolveria. */
export function scheduleWithNewMilestone(
  phaseId: string,
  item: Partial<ScheduleMilestone> & { id: string; title: string },
  base: Schedule = SCHEDULE,
): Schedule {
  return {
    ...base,
    phases: base.phases.map((phase) =>
      phase.id === phaseId
        ? { ...phase, milestones: [...phase.milestones, milestone({ ...item, position: 99 })] }
        : phase,
    ),
  }
}

/** O cronograma com o marco levado para o fim de outra fase, como a API o devolveria ao mover. */
export function scheduleWithMoved(
  id: string,
  toPhaseId: string,
  change: Partial<ScheduleMilestone> = {},
  base: Schedule = SCHEDULE,
): Schedule {
  const moved = base.phases.flatMap((phase) => phase.milestones).find((item) => item.id === id)
  if (!moved) throw new Error(`Marco de exemplo inexistente: ${id}`)
  return {
    ...base,
    phases: base.phases.map((phase) => ({
      ...phase,
      milestones:
        phase.id === toPhaseId
          ? [...phase.milestones.filter((item) => item.id !== id), { ...moved, ...change }]
          : phase.milestones.filter((item) => item.id !== id),
    })),
  }
}

/**
 * O Modo Com Data (data fictícia de teste: 12/06/2027), com os valores que a API calcularia: janela
 * sugerida com contagem de 12 dias, janela editada, prazo manual com janela, atrasado com janela de
 * 3 dias atrás e um marco sem janela e sem prazo. Os rótulos de data vêm prontos, sem calcular nada.
 */
export function scheduleComData(): Schedule {
  const suggested = {
    start_before: 14,
    end_before: 10,
    unit: 'meses',
    is_suggestion: true,
  } as const
  const calculated = {
    window_start: '2026-04-12',
    window_end: '2026-08-12',
  } as const
  return {
    ...SCHEDULE,
    has_exact_date: true,
    phases: [
      {
        id: ID.faseUm,
        title: 'Fase Exemplo Um',
        position: 0,
        version: 1,
        progress: { done: 0, total: 6 },
        milestones: [
          milestone({
            id: ID.janelaSugerida,
            title: 'Marco Exemplo com Janela Sugerida',
            position: 0,
            window: suggested,
            ...calculated,
            effective_target: '2026-08-12',
            days_left: 12,
          }),
          milestone({
            id: ID.janelaEditada,
            title: 'Marco Exemplo com Janela Editada',
            position: 1,
            window: { start_before: 8, end_before: 4, unit: 'semanas', is_suggestion: false },
            window_start: '2027-04-17',
            window_end: '2027-05-15',
            effective_target: '2027-05-15',
            days_left: 1,
          }),
          milestone({
            id: ID.prazoManual,
            title: 'Marco Exemplo com Prazo Manual',
            position: 2,
            window: suggested,
            ...calculated,
            target_date: '2026-07-30',
            effective_target: '2026-07-30',
            days_left: 0,
          }),
          milestone({
            id: ID.atrasadoComJanela,
            title: 'Marco Exemplo Atrasado com Janela',
            position: 3,
            overdue: true,
            window: { start_before: 12, end_before: 10, unit: 'meses', is_suggestion: true },
            window_start: '2026-06-12',
            window_end: '2026-08-12',
            effective_target: '2026-08-12',
            days_left: -3,
          }),
          milestone({ id: ID.semJanela, title: 'Marco Exemplo sem Janela', position: 4 }),
          milestone({
            id: ID.semPrazo,
            title: 'Marco Exemplo Concluído com Janela',
            position: 5,
            state: 'Concluído',
            window: suggested,
            ...calculated,
            effective_target: '2026-08-12',
          }),
        ],
      },
    ],
  }
}
