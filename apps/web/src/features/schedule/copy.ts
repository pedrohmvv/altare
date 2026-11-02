import type { ManualState, MilestoneState, Responsible } from './api/schedule'

export const copy = {
  eyebrow: 'Cronograma',
  title: 'O que pode andar agora',
  description: 'O que está Destravado e o que está Bloqueado por outra decisão.',
  list: {
    title: 'Marcos por fase',
    loading: 'Carregando o cronograma…',
    loadError: {
      title: 'Não conseguimos carregar o cronograma agora.',
      description: 'Confiram a conexão e tentem de novo.',
      retry: 'Tentar de novo',
    },
    empty: {
      title: 'Ainda sem marcos',
      description: 'Quando houver marcos, vocês veem aqui o que pode andar agora.',
    },
    tableLabel: 'Marcos por fase',
    tableCaption: 'Fases do cronograma e os marcos de cada uma',
    columns: {
      milestone: 'Marco',
      state: 'Estado',
      responsible: 'Responsável',
      target: 'Prazo-alvo',
    },
    noTarget: 'Sem prazo',
    emptyPhase: 'Nenhum marco ativo nesta fase.',
  },
  phase: {
    label: (number: number) => `Fase ${number}`,
    progress: (done: number, total: number) =>
      `${done} de ${total} ${total === 1 ? 'concluído' : 'concluídos'}`,
  },
  states: {
    Bloqueado: 'Bloqueado',
    Destravado: 'Destravado',
    'Em andamento': 'Em andamento',
    Concluído: 'Concluído',
  } satisfies Record<MilestoneState, string>,
  overdue: 'Atrasado',
  optional: 'Opcional',
  waiting: {
    for: (names: readonly string[]) => `Aguardando: ${names.join(', ')}`,
  },
  warnings: {
    doneBefore: (titles: readonly string[]) => `Concluído antes de: ${titles.join(', ')}`,
  },
  responsibles: {
    Noivo: 'Noivo',
    Noiva: 'Noiva',
    Ambos: 'Ambos',
  } satisfies Record<Responsible, string>,
  sheet: {
    phase: (title: string) => `Fase: ${title}`,
    stateTitle: 'Estado',
    actions: {
      start: 'Marcar em andamento',
      done: 'Concluir',
      reopen: 'Reabrir',
    },
    done: {
      'Em andamento': 'Marco marcado em andamento.',
      Concluído: 'Marco concluído.',
      reopened: 'Marco reaberto.',
    } satisfies Record<ManualState | 'reopened', string>,
    stateConflict:
      'Este marco foi alterado em outra tela. Vejam a versão mais recente e tentem de novo.',
    stateNetwork: 'Não conseguimos mudar o estado agora. Tentem de novo em instantes.',
    stateBlocked: 'Este marco passou a aguardar outra coisa. Vejam o que falta e tentem de novo.',
    links: {
      title: 'Ligações',
      category: 'Categoria ligada',
      noCategory: 'Sem categoria ligada',
      unnamedCategory: 'Categoria sem nome',
      dependsOn: 'Depende de',
      noDependsOn: 'Não depende de nenhum marco.',
      resolved: 'resolvido',
      pending: 'pendente',
      unlocks: 'Libera',
      noUnlocks: 'Não libera nenhum marco.',
    },
  },
  confirm: {
    cancel: 'Cancelar',
    ignoreBlock: {
      title: 'Ignorar o bloqueio?',
      description:
        'Este marco ainda está aguardando o que está abaixo. Vocês podem seguir mesmo assim: a escolha fica registrada.',
      waitingLabel: 'O que falta',
      start: 'Marcar em andamento mesmo assim',
      done: 'Concluir mesmo assim',
    },
    reopen: {
      title: 'Reabrir este marco?',
      description:
        'Os marcos abaixo dependem deste. Os que ainda não foram concluídos podem voltar a ficar bloqueados. Os já concluídos ficam como estão, com um aviso.',
      unlocksLabel: 'Libera',
      confirm: 'Reabrir marco',
    },
  },
  form: {
    title: 'Responsável, prazo e nota',
    responsible: 'Responsável',
    target: 'Prazo-alvo',
    targetHint: 'Só a data. Podem deixar em branco.',
    clearTarget: 'Tirar o prazo',
    note: 'Nota',
    noteHint: 'Opcional. Até 500 caracteres.',
    save: 'Salvar alterações',
    saved: 'Alterações salvas.',
    reload: 'Ver a versão mais recente',
    errors: {
      targetInvalid: 'Informem uma data válida, com dia, mês e ano.',
      noteTooLong: (max: number) => `Usem até ${max} caracteres.`,
      conflict:
        'Este marco foi alterado em outra tela. Vejam a versão mais recente antes de salvar.',
      network: 'Não conseguimos salvar agora. O que vocês escreveram continua aqui.',
    },
  },
} as const
