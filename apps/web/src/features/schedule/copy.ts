import type { ManualState, MilestoneState, Responsible, TaskState } from './api/schedule'

export const copy = {
  eyebrow: 'Cronograma',
  title: 'O que pode andar agora',
  description: 'O que está Destravado e o que está Bloqueado por outra decisão.',
  list: {
    title: 'Marcos por fase e avulsas',
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
    tableLabel: 'Marcos por fase e avulsas',
    tableCaption: 'Fases do cronograma com os seus marcos, e as avulsas.',
    columns: {
      milestone: 'Marco ou avulsa',
      state: 'Estado',
      responsible: 'Responsável',
      target: 'Prazo-alvo',
    },
    noTarget: 'Sem prazo',
    emptyPhase: 'Nenhum marco ativo nesta fase.',
  },
  banner: {
    text: 'Sem data definida. Quando vocês definirem a data exata do casamento, as janelas e os prazos sugeridos aparecem aqui.',
    link: 'Definir a data em Definições Base',
  },
  countdown: {
    today: 'é hoje',
    left: (days: number) => (days === 1 ? 'falta 1 dia' : `faltam ${days} dias`),
    overdue: (days: number) => (days === 1 ? 'venceu há 1 dia' : `venceu há ${days} dias`),
  },
  deadline: {
    window: (start: string, end: string) => `Janela: ${start} a ${end}`,
    suggestion: 'sugestão genérica',
    manual: 'prazo definido por vocês',
  },
  window: {
    title: 'Janela',
    range: (start: number, end: number, unit: 'meses' | 'semanas') => {
      const word = start === 1 ? (unit === 'meses' ? 'mês' : 'semana') : unit
      return `de ${start} a ${end} ${word} antes da data`
    },
    calculated: (start: string, end: string) => `Datas calculadas: ${start} a ${end}`,
    suggestion: 'Sugestão genérica: ainda ninguém editou esta janela.',
    noWindow: 'Este marco ainda não tem janela.',
    define: 'Definir janela',
    cancelDefine: 'Cancelar',
    noDateWithRange: (range: string) =>
      `Janela ${range}. As datas aparecem quando vocês definirem a data exata do casamento.`,
    noDateNoWindow:
      'Este marco ainda não tem janela. Com a data exata definida, vocês podem criar uma.',
    start: 'Início',
    end: 'Fim',
    unit: 'Unidade',
    units: { meses: 'meses', semanas: 'semanas' },
    // Uma frase por unidade: "meses" é masculino e "semanas" é feminino.
    hints: {
      meses: 'Quantos meses antes da data do casamento.',
      semanas: 'Quantas semanas antes da data do casamento.',
    },
    save: 'Salvar janela',
    noChange: 'Mudem o início, o fim ou a unidade para salvar.',
    saved: 'Janela salva.',
    errors: {
      integer: (max: number) => `Informem um número inteiro de 0 a ${max}.`,
      max: (max: number, unit: 'meses' | 'semanas') => `Usem no máximo ${max} ${unit}.`,
      order: 'O início precisa ser maior ou igual ao fim (a janela começa antes de terminar).',
      conflict:
        'Este marco foi alterado em outra tela. Vejam a versão mais recente antes de salvar.',
      network: 'Não conseguimos salvar a janela agora. O que vocês escreveram continua aqui.',
    },
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
    deadline: 'Prazo-alvo:',
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
      unnamedCategory: 'Categoria sem nome',
      dependsOn: 'Depende de',
      noDependsOn: 'Não depende de nenhum marco.',
      resolved: 'resolvido',
      pending: 'pendente',
      unlocks: 'Libera',
      noUnlocks: 'Não libera nenhum marco.',
      remove: (title: string) => `Remover a dependência de ${title}`,
      removeShort: 'Remover',
      addLabel: 'Adicionar dependência',
      addPlaceholder: 'Escolham um marco',
      add: 'Adicionar',
      added: 'Dependência adicionada.',
      removed: 'Dependência removida.',
      noCandidates: 'Não há outro marco para ligar.',
      conflict:
        'Este marco foi alterado em outra tela. Vejam a versão mais recente e tentem de novo.',
      network: 'Não conseguimos salvar a dependência agora. Tentem de novo em instantes.',
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
    openItems: {
      title: 'Concluir com itens em aberto?',
      count: (open: number) =>
        open === 1
          ? 'Há 1 item em aberto no checklist.'
          : `Há ${open} itens em aberto no checklist.`,
      keep: 'Os itens continuam como estão.',
      waiting: 'Este marco também ainda está aguardando o que está abaixo.',
      waitingLabel: 'O que falta',
      confirm: 'Concluir mesmo assim',
      stale: 'Os itens do checklist mudaram. Tentem concluir de novo.',
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
    title: 'Dados do marco',
    titleLabel: 'Título',
    phase: 'Fase',
    category: 'Categoria',
    noCategory: 'Sem categoria',
    categoryHint:
      'A categoria liga o marco ao Mapa de Escopo e decide se o marco fica Bloqueado, Opcional ou arquivado, conforme o status dela.',
    responsible: 'Responsável',
    target: 'Prazo-alvo',
    targetHint: 'Só a data. Podem deixar em branco.',
    clearTarget: 'Tirar o prazo',
    backToSuggestion: 'Voltar à sugestão',
    suggestion: (date: string) => `Sugestão: ${date}`,
    blankUsesSuggestion: 'Em branco, vale a sugestão.',
    note: 'Nota',
    noteHint: 'Opcional. Até 500 caracteres.',
    save: 'Salvar alterações',
    saved: 'Alterações salvas.',
    reload: 'Ver a versão mais recente',
    errors: {
      titleRequired: 'Informem o título do marco.',
      tooLong: (max: number) => `Usem até ${max} caracteres.`,
      targetInvalid: 'Informem uma data válida, com dia, mês e ano.',

      conflict:
        'Este marco foi alterado em outra tela. Vejam a versão mais recente antes de salvar.',
      network: 'Não conseguimos salvar agora. O que vocês escreveram continua aqui.',
    },
  },
  header: {
    newMilestone: 'Novo marco',
    newTask: 'Nova avulsa',
    phases: 'Fases',
  },
  newMilestone: {
    inPhase: 'Novo marco nesta fase',
    inPhaseFor: (phase: string) => `Novo marco nesta fase: ${phase}`,
    title: 'Novo marco',
    description: 'O marco entra no fim da fase escolhida. Depois, vocês ligam as dependências.',
    submit: 'Criar marco',
    cancel: 'Cancelar',
    created: 'Marco criado',
    createdArchived: (title: string) =>
      `“${title}” foi criado, mas fica fora das listas porque a categoria ligada está fora do escopo.`,
    network: 'Não conseguimos criar o marco agora. O que vocês escreveram continua aqui.',
    conflict: 'O cronograma mudou em outra tela. Vejam a versão mais recente e tentem de novo.',
  },
  remove: {
    button: 'Excluir marco',
    title: (title: string) => `Excluir “${title}”?`,
    description: 'O marco sai do cronograma, mas fica guardado e pode ser restaurado.',
    dependentsTitle: 'Marcos que dependem dele',
    dependents: 'Estes marcos deixam de depender dele.',
    noDependents: 'Nenhum marco depende dele.',
    confirm: 'Excluir marco',
    cancel: 'Cancelar',
    done: 'Marco excluído',
    doneDescription: (title: string) => `“${title}” saiu do cronograma.`,
    undo: 'Desfazer',
    undoAlt: 'Desfazer a exclusão do marco',
    restored: 'Marco restaurado',
    leftOut: {
      title: 'Marco restaurado, com ressalvas',
      description: (links: readonly string[]) =>
        `Estas ligações não voltaram, porque fechariam um ciclo ou chegam a um marco excluído: ${links.join('; ')}.`,
      dependsOn: (title: string) => `depende de ${title}`,
      dependencyOf: (title: string) => `é dependência de ${title}`,
    },
    conflict:
      'Este marco foi alterado em outra tela. Vejam a versão mais recente e tentem de novo.',
    network: 'Não conseguimos excluir o marco agora. Tentem de novo em instantes.',
    restoreFailed: {
      title: 'Não conseguimos restaurar o marco agora.',
      description: 'O marco segue guardado e pode ser restaurado.',
      retry: 'Tentar de novo',
      retryAlt: 'Tentar restaurar o marco de novo',
    },
  },
  phases: {
    title: 'Fases do cronograma',
    description:
      'Renomeiem e reordenem as fases. Os marcos de cada uma acompanham o nome e a ordem.',
    listTitle: 'Ordem e nomes',
    save: 'Salvar',
    saveFor: (title: string) => `Salvar o nome da fase ${title}`,
    up: 'Subir',
    upFor: (title: string) => `Subir a fase ${title}`,
    down: 'Descer',
    downFor: (title: string) => `Descer a fase ${title}`,
    newTitle: 'Nova fase',
    newLabel: 'Nome da nova fase',
    add: 'Adicionar fase',
    renamed: 'Nome da fase salvo.',
    moved: 'Ordem das fases salva.',
    createdPhase: 'Fase criada.',
    errors: {
      titleRequired: 'Informem o nome da fase.',
      tooLong: (max: number) => `Usem até ${max} caracteres.`,
      conflict:
        'As fases foram alteradas em outra tela. Vejam a versão mais recente antes de salvar.',
      network: 'Não conseguimos salvar as fases agora. O que vocês escreveram continua aqui.',
    },
  },
  checklist: {
    title: 'Checklist',
    progress: (done: number, total: number) => `${done} de ${total}`,
    summary: (done: number, total: number) => `Checklist: ${done} de ${total}`,
    empty: 'Ainda sem itens. Quebrem o que falta em passos pequenos.',
    newLabel: 'Novo item',
    add: 'Adicionar item',
    textLabel: 'Texto do item',
    edit: 'Editar',
    editFor: (text: string) => `Editar o item ${text}`,
    save: 'Salvar',
    saveFor: (text: string) => `Salvar o item ${text}`,
    cancel: 'Cancelar',
    cancelFor: (text: string) => `Cancelar a edição do item ${text}`,
    up: 'Subir',
    upFor: (text: string) => `Subir o item ${text}`,
    down: 'Descer',
    downFor: (text: string) => `Descer o item ${text}`,
    remove: 'Remover',
    removeFor: (text: string) => `Remover o item ${text}`,
    added: 'Item adicionado.',
    saved: 'Item salvo.',
    removed: 'Item removido.',
    moved: 'Itens reordenados.',
    errors: {
      textRequired: 'Informem o texto do item.',
      tooLong: (max: number) => `Usem até ${max} caracteres.`,
      full: 'Cada lista vai até 50 itens.',
      conflict:
        'Este checklist foi alterado em outra tela. Vejam a versão mais recente e tentem de novo.',
      network: 'Não conseguimos salvar o checklist agora. O que vocês escreveram continua aqui.',
    },
  },
  task: {
    sectionTitle: 'Avulsas',
    empty: 'Ainda não há avulsas. Criem uma para o que não tem ordem, como “pesquisar alianças”.',
    states: {
      'A fazer': 'A fazer',
      'Em andamento': 'Em andamento',
      Concluída: 'Concluída',
    } satisfies Record<TaskState, string>,
    overdue: 'Atrasada',
    sheet: {
      description: 'Tarefa avulsa: fica fora das fases e das dependências.',
      deadline: 'Prazo:',
    },
    actions: {
      start: 'Marcar em andamento',
      done: 'Concluir',
      reopen: 'Reabrir',
    },
    done: {
      'Em andamento': 'Avulsa em andamento.',
      Concluída: 'Avulsa concluída.',
      reopened: 'Avulsa reaberta.',
    } satisfies Record<Exclude<TaskState, 'A fazer'> | 'reopened', string>,
    stateConflict:
      'Esta avulsa foi alterada em outra tela. Vejam a versão mais recente e tentem de novo.',
    stateNetwork: 'Não conseguimos mudar o estado agora. Tentem de novo em instantes.',
    form: {
      title: 'Dados da avulsa',
      target: 'Prazo',
      titleRequired: 'Informem o título da avulsa.',
      conflict:
        'Esta avulsa foi alterada em outra tela. Vejam a versão mais recente antes de salvar.',
    },
    create: {
      title: 'Nova avulsa',
      description: 'Para o que não tem ordem nem fase. Só o título é obrigatório.',
      submit: 'Criar avulsa',
      cancel: 'Cancelar',
      created: 'Avulsa criada.',
      network: 'Não conseguimos criar a avulsa agora. O que vocês escreveram continua aqui.',
    },
    remove: {
      button: 'Excluir avulsa',
      done: 'Avulsa excluída',
      doneDescription: (title: string) => `“${title}” saiu do cronograma.`,
      undo: 'Desfazer',
      undoAlt: 'Desfazer a exclusão da avulsa',
      restored: 'Avulsa restaurada',
      conflict:
        'Esta avulsa foi alterada em outra tela. Vejam a versão mais recente e tentem de novo.',
      network: 'Não conseguimos excluir a avulsa agora. Tentem de novo em instantes.',
      restoreFailed: {
        title: 'Não conseguimos restaurar a avulsa agora.',
        description: 'A avulsa segue guardada e pode ser restaurada.',
        retry: 'Tentar de novo',
        retryAlt: 'Tentar restaurar a avulsa de novo',
      },
    },
  },
  filters: {
    label: 'Filtros do cronograma',
    responsible: 'Responsável',
    state: 'Estado',
    overdue: 'Só atrasados',
    tasksOnly: 'Só avulsas',
    clear: 'Limpar filtros',
    count: (shown: number, total: number) => `${shown} de ${total} itens`,
    // O artigo vem junto de cada perfil: nada de montar o gênero por concatenação.
    lensNote: {
      Noivo: 'Minha visão: itens do Noivo e de Ambos.',
      Noiva: 'Minha visão: itens da Noiva e de Ambos.',
    },
    lensOverridden: 'Filtro de responsável ativo: a lente não se aplica.',
    noMatch: {
      title: 'Nenhum item com esses filtros.',
      lensTitle: 'Nada na Minha visão.',
      lensOnly: {
        Noivo: 'Na Minha visão aparecem só os itens do Noivo e os de Ambos.',
        Noiva: 'Na Minha visão aparecem só os itens da Noiva e os de Ambos.',
      },
      showCouple: 'Ver a Visão do Casal',
    },
  },
  nextSteps: {
    title: 'Meus próximos passos',
    empty: 'Nada seu pendente por agora.',
    showAll: (count: number) => `Ver todos (${count})`,
    showLess: 'Ver menos',
    kind: { milestone: 'Marco', task: 'Avulsa' },
  },
} as const
