import type {
  Attachment,
  ChecklistItem,
  Schedule,
  ScheduleMilestone,
  ScheduleTask,
} from '@/features/schedule/api/schedule'

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
  avulsaUm: '00000000-0000-4000-8000-0000000000b1',
  avulsaDois: '00000000-0000-4000-8000-0000000000b2',
  avulsaNova: '00000000-0000-4000-8000-0000000000b3',
  itemUm: '00000000-0000-4000-8000-0000000000d1',
  itemDois: '00000000-0000-4000-8000-0000000000d2',
  itemTres: '00000000-0000-4000-8000-0000000000d3',
  itemNovo: '00000000-0000-4000-8000-0000000000d4',
  anexoPdf: '00000000-0000-4000-8000-0000000000f4',
  anexoImagem: '00000000-0000-4000-8000-0000000000f5',
  anexoLink: '00000000-0000-4000-8000-0000000000f6',
  anexoNovo: '00000000-0000-4000-8000-0000000000f7',
  arquivoPdf: '00000000-0000-4000-8000-0000000000f8',
  arquivoImagem: '00000000-0000-4000-8000-0000000000f9',
  arquivoNovo: '00000000-0000-4000-8000-0000000000fa',
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
    checklist: [],
    checklist_progress: { done: 0, total: 0 },
    attachments: [],
    version: 1,
    ...over,
  } satisfies ScheduleMilestone
}

/** Um item de checklist, sem texto do casamento: os exemplos são rotulados como fictícios. */
export function checklistItem(over: Partial<ChecklistItem> & { id: string; text: string }) {
  return { done: false, position: 0, version: 1, ...over } satisfies ChecklistItem
}

/**
 * Um anexo de link de exemplo (`https://exemplo.test`), do Noivo, que o perfil da sessão pode remover.
 * Quem testa um arquivo passa `kind: 'file'` e o `file` (veja `pdfAttachment` e `imageAttachment`).
 */
export function attachment(over: Partial<Attachment> & { id: string }) {
  return {
    kind: 'link',
    title: null,
    comment: null,
    url: 'https://exemplo.test/pagina',
    domain: 'exemplo.test',
    file: null,
    by: 'Noivo',
    at: '2026-10-27T15:30:00Z',
    can_remove: true,
    ...over,
  } satisfies Attachment
}

/** Um PDF de exemplo anexado: o nome e o tamanho são cópias de quando foi anexado. */
export function pdfAttachment(over: Partial<Attachment> & { id: string } = { id: ID.anexoPdf }) {
  return attachment({
    kind: 'file',
    url: null,
    domain: null,
    file: {
      id: ID.arquivoPdf,
      name: 'contrato-exemplo.pdf',
      content_type: 'application/pdf',
      size_bytes: 1_468_006,
    },
    ...over,
  })
}

/** Uma imagem de exemplo anexada. */
export function imageAttachment(
  over: Partial<Attachment> & { id: string } = { id: ID.anexoImagem },
) {
  return attachment({
    kind: 'file',
    url: null,
    domain: null,
    file: {
      id: ID.arquivoImagem,
      name: 'planta-exemplo.png',
      content_type: 'image/png',
      size_bytes: 204_800,
    },
    ...over,
  })
}

/**
 * Uma avulsa com os padrões de uma recém-criada: A fazer, sem prazo, sem itens. O `checklist_progress`
 * acompanha os itens, como o servidor o calcularia.
 */
export function task(over: Partial<ScheduleTask> & { id: string; title: string }) {
  const checklist = over.checklist ?? []
  return {
    responsible: 'Ambos',
    note: null,
    target_date: null,
    state: 'A fazer',
    overdue: false,
    days_left: null,
    checklist,
    checklist_progress: {
      done: checklist.filter((item) => item.done).length,
      total: checklist.length,
    },
    attachments: [],
    version: 1,
    ...over,
  } satisfies ScheduleTask
}

/** Duas fases de exemplo, com um marco de cada situação que a tela precisa mostrar. */
export const SCHEDULE: Schedule = {
  has_exact_date: false,
  tasks: [],
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

/** O cronograma de exemplo com avulsas, no fim da lista, como a API as entrega. */
export function scheduleWithTasks(tasks: ScheduleTask[], base: Schedule = SCHEDULE): Schedule {
  return { ...base, tasks }
}

/** Duas avulsas de exemplo: uma Noiva com prazo vencido e itens, e uma Ambos, concluída. */
export function sampleTasks(): ScheduleTask[] {
  return [
    task({
      id: ID.avulsaUm,
      title: 'Avulsa Exemplo Atrasada',
      responsible: 'Noiva',
      target_date: '2020-01-15',
      overdue: true,
      days_left: -3,
      checklist: [
        checklistItem({ id: ID.itemUm, text: 'Item Exemplo Um', done: true, position: 0 }),
        checklistItem({ id: ID.itemDois, text: 'Item Exemplo Dois', position: 1 }),
        checklistItem({ id: ID.itemTres, text: 'Item Exemplo Três', position: 2 }),
      ],
    }),
    task({
      id: ID.avulsaDois,
      title: 'Avulsa Exemplo Concluída',
      state: 'Concluída',
    }),
  ]
}

/**
 * O cronograma com o checklist de um dono (marco ou avulsa) trocado, como a API o devolveria: o
 * "N de M" acompanha os itens. Os ids dos marcos e das avulsas não se confundem.
 */
export function scheduleWithChecklist(
  ownerId: string,
  checklist: ChecklistItem[],
  base: Schedule = SCHEDULE,
): Schedule {
  const checklist_progress = {
    done: checklist.filter((item) => item.done).length,
    total: checklist.length,
  }
  const change = { checklist, checklist_progress }
  return {
    ...base,
    tasks: base.tasks.map((item) => (item.id === ownerId ? { ...item, ...change } : item)),
    phases: base.phases.map((phase) => ({
      ...phase,
      milestones: phase.milestones.map((item) =>
        item.id === ownerId ? { ...item, ...change } : item,
      ),
    })),
  }
}

/**
 * O cronograma com os anexos de um dono (marco ou avulsa) trocados, como a API o devolveria. Os ids
 * dos marcos e das avulsas não se confundem.
 */
export function scheduleWithAttachments(
  ownerId: string,
  attachments: Attachment[],
  base: Schedule = SCHEDULE,
): Schedule {
  const change = { attachments }
  return {
    ...base,
    tasks: base.tasks.map((item) => (item.id === ownerId ? { ...item, ...change } : item)),
    phases: base.phases.map((phase) => ({
      ...phase,
      milestones: phase.milestones.map((item) =>
        item.id === ownerId ? { ...item, ...change } : item,
      ),
    })),
  }
}

/** Os anexos vivos de um dono, no cronograma dado. */
export function attachmentsOf(schedule: Schedule, ownerId: string): Attachment[] {
  const owner =
    schedule.tasks.find((item) => item.id === ownerId) ??
    schedule.phases.flatMap((phase) => phase.milestones).find((item) => item.id === ownerId)
  return owner?.attachments ?? []
}

/** Os itens vivos de um dono, no cronograma dado. */
export function checklistOf(schedule: Schedule, ownerId: string): ChecklistItem[] {
  const owner =
    schedule.tasks.find((item) => item.id === ownerId) ??
    schedule.phases.flatMap((phase) => phase.milestones).find((item) => item.id === ownerId)
  return owner?.checklist ?? []
}

/** Ids do cronograma de filtros: todos válidos como UUID, para a URL aceitá-los. */
export const FID = {
  mNoivo: '00000000-0000-4000-8000-0000000000e1',
  mNoiva: '00000000-0000-4000-8000-0000000000e2',
  mAmbosAtrasado: '00000000-0000-4000-8000-0000000000e3',
  mNoivaConcluido: '00000000-0000-4000-8000-0000000000e4',
  mNoivaArquivado: '00000000-0000-4000-8000-0000000000e5',
  tNoivo: '00000000-0000-4000-8000-0000000000e6',
  tNoivaAndamento: '00000000-0000-4000-8000-0000000000e7',
  tAmbosConcluida: '00000000-0000-4000-8000-0000000000e8',
  tNoivaAtrasada: '00000000-0000-4000-8000-0000000000e9',
} as const

/**
 * Um cronograma para filtros e lentes: marcos e avulsas de cada responsável, em cada estado, um
 * atrasado de cada tipo e um marco arquivado (que nunca entra em lista nenhuma). O progresso das
 * fases é o do servidor e não muda com filtro.
 */
export function scheduleForFilters(): Schedule {
  return {
    ...SCHEDULE,
    tasks: [
      task({ id: FID.tNoivo, title: 'Avulsa Exemplo do Noivo', responsible: 'Noivo' }),
      task({
        id: FID.tNoivaAndamento,
        title: 'Avulsa Exemplo da Noiva em Andamento',
        responsible: 'Noiva',
        state: 'Em andamento',
        target_date: '2027-03-01',
        days_left: 20,
      }),
      task({
        id: FID.tAmbosConcluida,
        title: 'Avulsa Exemplo de Ambos Concluída',
        responsible: 'Ambos',
        state: 'Concluída',
      }),
      task({
        id: FID.tNoivaAtrasada,
        title: 'Avulsa Exemplo da Noiva Atrasada',
        responsible: 'Noiva',
        target_date: '2020-01-15',
        days_left: -9,
        overdue: true,
      }),
    ],
    phases: [
      {
        id: ID.faseUm,
        title: 'Fase Exemplo Um',
        position: 0,
        version: 1,
        progress: { done: 0, total: 3 },
        milestones: [
          milestone({
            id: FID.mNoivo,
            title: 'Marco Exemplo do Noivo',
            position: 0,
            responsible: 'Noivo',
            state: 'Destravado',
          }),
          milestone({
            id: FID.mNoiva,
            title: 'Marco Exemplo da Noiva',
            position: 1,
            responsible: 'Noiva',
            state: 'Bloqueado',
            blocked_by: [
              { kind: 'milestone', milestone_id: FID.mNoivo, label: 'Marco Exemplo do Noivo' },
            ],
          }),
          milestone({
            id: FID.mAmbosAtrasado,
            title: 'Marco Exemplo de Ambos Atrasado',
            position: 2,
            responsible: 'Ambos',
            state: 'Em andamento',
            overdue: true,
            target_date: '2020-02-01',
            days_left: -5,
          }),
        ],
      },
      {
        id: ID.faseDois,
        title: 'Fase Exemplo Dois',
        position: 1,
        version: 2,
        progress: { done: 1, total: 1 },
        milestones: [
          milestone({
            id: FID.mNoivaConcluido,
            title: 'Marco Exemplo da Noiva Concluído',
            position: 0,
            responsible: 'Noiva',
            state: 'Concluído',
          }),
          milestone({
            id: FID.mNoivaArquivado,
            title: 'Marco Exemplo da Noiva Arquivado',
            position: 1,
            responsible: 'Noiva',
            state: 'Destravado',
            archived: true,
          }),
        ],
      },
    ],
  }
}
