# Features: Cronograma & Dependências (`features/cronograma.md`)

> **Status:** **Aprovado pelo usuário em 2026-10-27** (`D-031`). Cobre o **Bloco 1.3**, que roda em 7 PRs (`D-080`); o PR 1, marcos, bloqueios e estados (`F-CRN-02`, `03` e `04`, parte da `01` e da `09`), foi implementado em `D-081`, e o PR 2, a edição de marcos, dependências e fases (`F-CRN-01` completa; `F-CRN-03`, regra 2), em `D-082`.
>
> **Fontes:** `docs/product/scope.md` §2, `docs/design/experience.md` (objeto 4), `docs/product/jobs.md` (J4, J5), `features/planejamento-e-caminhos.md` (F-PLN-01, F-PLN-07), `D-026`, `D-031`.
>
> **Convenções:** `F-CRN-xx` identifica a feature; `Cxx` identifica um marco do catálogo inicial. Nenhum dado do casamento é presumido (`AGENTS.md` §2): o catálogo é um **modelo genérico**, e tudo nele é editável.

---

## Visão da Área

**Jobs atendidos:** J4 (entender a sequência e o que trava o quê) e J5 (acompanhar marcos, prazos e responsáveis).

**Ideia central:** o cronograma responde "o que podemos fazer agora e quem faz". Mostra o que está **Destravado**, o que está **Bloqueado** e por quê, sem Gantt corporativo (`scope.md` §2).

**Dois tipos de item:**

| Tipo | Para que serve | Tem dependências, fase e categoria? |
| :--- | :--- | :--- |
| **Marco** | Decisão ou entrega do planejamento (ex.: "Fechar o Espaço") | Sim |
| **Tarefa avulsa** | Coisa solta (ex.: "pesquisar alianças") | Não |

---

## F-CRN-01 — Fases e Marcos

**Fase:** título e ordem. O catálogo traz as 5 fases aprovadas; o casal pode **renomear, reordenar e criar** fases.

**Marco**

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Título** | Texto, obrigatório | — |
| **Fase** | Uma das fases | Pode mudar de fase |
| **Responsável** | `Noivo` · `Noiva` · `Ambos` | Obrigatório. Padrão `Ambos` |
| **Categoria de escopo** | Uma categoria, opcional | Liga o marco ao Mapa de Escopo (F-CRN-04). O casal escolhe entre as categorias visíveis; a já ligada que ficou oculta continua escolhida (`D-082`) |
| **Prazo-alvo** | Data, opcional | Ver F-CRN-05 |
| **Janela** | Início e fim, em "antes da data", com unidade `meses` ou `semanas` | Só com Modo Com Data (F-CRN-05) |
| **Estado** | Ver F-CRN-03 | — |
| **Nota** | Texto livre | — |
| **Dependências** | Lista de outros marcos | F-CRN-03 |
| **Checklist** | Subtarefas | F-CRN-07 |
| **Anexos e links** | Arquivos e URLs | F-CRN-08 |

**Regras**
1. O casal pode **criar, renomear, mover de fase e excluir** marcos, e alterar dependências (`D-031`). A exclusão é lógica e recuperável (`architecture.md` §10).
2. Qualquer dos dois edita. A autoria fica no histórico básico.
3. Excluir um marco que tem dependentes pede confirmação **listando os dependentes**. As dependências do excluído são removidas; os dependentes mantêm as demais. Restaurar traz de volta as que saíram junto com ele, exceto a que hoje fecharia um ciclo e a que tem a outra ponta excluída; a tela diz quais ficaram de fora (`D-082`).
4. O catálogo inicial (F-CRN-02) é uma **semente**: depois de criado, os marcos são dados do casal.

**Critérios de aceite**
- Criar um marco sem título é bloqueado.
- Excluir um marco com dois dependentes mostra os dois nomes antes de confirmar, e a restauração traz de volta o marco e suas dependências.
- Renomear uma fase não perde nenhum marco dela.

---

## F-CRN-02 — Catálogo Inicial de Marcos

**O que é:** o modelo de cronograma que o Altare cria junto com o casamento, já ligado às categorias do Mapa de Escopo e com as dependências. Os nomes são **neutros** (`D-026`): não há roteiro fixo de nenhuma tradição.

> **Janelas sugeridas:** são **valores genéricos propostos pelo Altare**, rotulados "sugestão genérica" na tela até alguém editá-los. **Não são dados do seu casamento.** Revisem à vontade.

| ID | Fase | Marco | Categoria | Depende de | Janela sugerida (antes da data) |
| :-- | :--- | :--- | :--- | :--- | :--- |
| C01 | 1 Marco Zero | Classificar o Mapa de Escopo | — | — | sem janela |
| C02 | 1 | Montar a lista preliminar de convidados | — | — | sem janela |
| C03 | 1 | Definir o teto macro e simular orçamentos | — | C01, C02 | sem janela |
| C04 | 1 | Escolher o caminho macro (formato e região) | — | C03 | sem janela |
| C05 | 2 Contrato Âncora | Definir a data (ou janela de datas) | — | C04 | sem janela |
| C06 | 2 | Fechar o Espaço | Espaço | C05 | 14 a 10 meses |
| C07 | 3 Fornecedores Essenciais | Fechar o Buffet | Buffet | C06 | 12 a 8 meses |
| C08 | 3 | Fechar a Fotografia | Fotografia | C06 | 12 a 8 meses |
| C09 | 3 | Fechar o Vídeo | Vídeo | C06 | 12 a 8 meses |
| C10 | 3 | Fechar o Cerimonial do dia | Cerimonial do dia | C06 | 10 a 7 meses |
| C11 | 3 | Fechar a Música | Música | C06 | 10 a 6 meses |
| C12 | 3 | Organizar a cerimônia civil | Cerimônia civil | C05 | 6 a 3 meses |
| C13 | 3 | Organizar a cerimônia religiosa ou simbólica | Cerimônia religiosa ou simbólica | C05 | 12 a 6 meses *(varia muito)* |
| C14 | 4 Identidade, Complementares e Convidados | Fechar Decoração e flores | Decoração e flores | C06 | 9 a 5 meses |
| C15 | 4 | Fechar Iluminação e som | Iluminação e som | C06 | 8 a 5 meses |
| C16 | 4 | Fechar Bebidas e bar | Bebidas e bar | C07 | 8 a 5 meses |
| C17 | 4 | Fechar Bolo e doces | Bolo e doces | C07 | 6 a 3 meses |
| C18 | 4 | Definir os trajes | Trajes | C05 | 10 a 5 meses |
| C19 | 4 | Contratar a beleza | Beleza (noivos) | C18 | 6 a 3 meses |
| C20 | 4 | Convites e papelaria | Convites e papelaria | C02, C06 | 7 a 4 meses |
| C21 | 4 | Lembrancinhas | Lembrancinhas | C06 | 5 a 3 meses |
| C22 | 4 | Montar o enxoval e a lista de presentes | — | C05 | 6 a 3 meses |
| C23 | 4 | Planejar a lua de mel | Lua de mel | C05 | 8 a 3 meses |
| C24 | 4 | Reservar a noite de núpcias | Noite de núpcias | C06 | 4 a 2 meses |
| C25 | 5 Reta Final | Enviar os convites | — | C20 | 4 a 2 meses |
| C26 | 5 | Confirmar as presenças | — | C25 | 2 a 1 meses |
| C27 | 5 | Degustações e provas finais | — | C07, C18 | 2 a 1 meses |
| C28 | 5 | Quitar os contratos | — | C26 | 4 a 1 semanas |
| C29 | 5 | Entregar o Dossiê ao cerimonialista | — | C10, C26 | 4 a 2 semanas |

**Regras**
1. Cada marco do catálogo guarda a **chave da categoria**, não o nome: renomear a categoria não quebra a ligação.
2. Marcos ligados a categorias `Fica de fora` ou ocultas nascem arquivados (F-CRN-04).
3. A responsabilidade inicial é `Ambos` em todos; o casal distribui.

**Critérios de aceite**
- Num casamento recém-criado, aparecem os 29 marcos nas 5 fases, todos com responsável `Ambos` e nenhum prazo preenchido.
- Com todas as categorias ainda `Em discussão`, todos os marcos ligados a categorias aparecem `Bloqueado` com o motivo "Aguardando classificar a categoria no Mapa de Escopo". Depois de classificá-las, C06, C12 e C13 passam a aguardar "Definir a data (ou janela de datas)", e C07 a C11 aguardam "Fechar o Espaço".
- Cada janela sugerida mostra o rótulo "sugestão genérica" até ser editada.

---

## F-CRN-03 — Dependências e Estados

**Estados**

| Estado | Como surge | Quem muda |
| :--- | :--- | :--- |
| `Bloqueado` | **Derivado**: há uma dependência pendente ou a categoria ligada está `Em discussão` | Ninguém: é calculado |
| `Destravado` | **Derivado**: nada pendente | Ninguém: é calculado |
| `Em andamento` | Marcado pelo casal | Qualquer um |
| `Concluído` | Marcado pelo casal (ou pela decisão, ver regra 6) | Qualquer um |
| `Atrasado` | **Sinalizador derivado**: prazo-alvo anterior a hoje e não `Concluído` | Ninguém |

**Regras**
1. Uma dependência "A depende de B" está **resolvida** quando B está `Concluído`, **arquivado** (categoria `Fica de fora`) ou **opcional** (categoria `Talvez`).
2. O sistema **impede ciclos** ao criar uma dependência, com mensagem acionável.
3. Um marco `Bloqueado` mostra **"Aguardando: …"** com os nomes do que falta. No celular, a lista abre em folha inferior.
4. Marcar `Em andamento` ou `Concluído` em um marco que **aguarda algo** (uma dependência não resolvida ou a categoria `Em discussão`) é **permitido com confirmação** ("ignorar o bloqueio"), qualquer que seja a marca de partida (inclusive voltar de `Concluído` para `Em andamento`); a escolha fica registrada. A vida real é paralela (`D-081`).
5. **Reabrir** um marco `Concluído` bloqueia de novo os dependentes que ainda não estão concluídos e **avisa** os que já estão concluídos ("Concluído antes de: …"), sem alterá-los. O aviso vale para todo marco `Concluído` com predecessor não resolvido, tenha o predecessor sido reaberto ou nunca concluído (o marco foi concluído ignorando o bloqueio): o estado é derivado e o sistema não guarda a diferença. Marcos arquivados (`Fica de fora`) não aparecem em "Libera" (`D-081`).
6. **Conclusão por decisão:** quando existir o Registro de Decisão macro (Bloco 2.2, `D-033`), o marco "Escolher o caminho macro" (C04) fica `Concluído` automaticamente; quando existir o Registro de Decisão da categoria (Bloco 3.2) **ou um contrato direto na categoria** (Bloco 3.3, `D-036`), o marco "Fechar …" correspondente também. **Até lá, a conclusão é manual.**
7. Estados e bloqueios são calculados **no backend**, derivados na leitura (`architecture.md` §3).

**Critérios de aceite**
- Concluir C06 muda C07 a C11, C14, C15, C21 e C24 de `Bloqueado` para `Destravado` (se as categorias não estiverem `Em discussão`) sem digitação. C20 só destrava se C02 também estiver concluído.
- Criar uma dependência que fecha um ciclo é recusada, mostrando o caminho do ciclo.
- Marcar `Concluído` (ou `Em andamento`) um marco que aguarda algo exige confirmação e registra "ignorou o bloqueio".
- Um marco com prazo ontem e estado `Destravado` aparece `Atrasado`; ao concluir, o sinalizador some.

---

## F-CRN-04 — Ligação com o Mapa de Escopo

Concretiza `F-PLN-07` para o cronograma.

| Status da categoria ligada | Efeito no marco |
| :--- | :--- |
| `Entra (Essencial)` | Marco **ativo** |
| `Talvez (Se couber)` | Marco **opcional**: aparece com a etiqueta "Opcional" e **não bloqueia** dependentes |
| `Em discussão` | Marco **`Bloqueado`**, com o motivo "Aguardando classificar a categoria no Mapa de Escopo" |
| `Fica de fora` | Marco **arquivado**: sai das listas ativas e **não bloqueia** dependentes |

**Regras**
1. Voltar uma categoria a `Entra` restaura o marco e seu histórico.
2. Marcos **sem categoria** (como C25) seguem só as dependências.
3. Categoria **oculta** (F-PLN-02) conta como `Fica de fora` para esta finalidade.

**Critérios de aceite**
- Marcar Fotografia como `Fica de fora` arquiva C08; marcos que dependiam dele ficam sem bloqueio por causa dele.
- Marcar Música como `Talvez` mostra C11 com "Opcional", e C29 (que depende de C10) não é afetado.
- Reabrir Fotografia restaura C08 no estado em que estava.

---

## F-CRN-05 — Responsável, Prazo e Modos Sem/Com Data

**Modo Sem Data** (a data exata do casamento ainda não foi definida em `F-PLN-01`): o cronograma funciona **só pela ordem lógica**. Janelas sugeridas não são calculadas. O casal pode, mesmo assim, definir um prazo-alvo manual em qualquer marco.

**Modo Com Data** (data exata `Definida`):
1. Cada marco com janela recebe **datas calculadas**: início = data − "início antes"; fim = data − "fim antes". Meses respeitam o fim do mês (31 → 30 ou 28/29).
2. O **prazo-alvo padrão** é o **fim da janela**. Um prazo digitado à mão **prevalece**, e há um botão "voltar à sugestão".
3. Mostra contagem regressiva em linguagem direta ("faltam 12 dias") com a data exata no `title`/tooltip.
4. **Mudar a data do casamento** recalcula as janelas dos marcos **não editados à mão** e mostra, antes de confirmar, a lista do que muda ("7 marcos mudam de janela"). Marcos com prazo manual não mudam.
5. O casal pode editar a janela de um marco (início, fim e unidade).
6. **Voltar ao Modo Sem Data** (data deixa de ser `Definida`) mantém prazos manuais e apaga as datas calculadas.

**Regras gerais**
- Responsável: `Noivo`, `Noiva` ou `Ambos`; editável por qualquer um.
- Prazos são datas (`DATE`); sem horário (`D-031`).
- Janela vencida e não concluída = `Atrasado` (F-CRN-03).

**Critérios de aceite** *(data fictícia de teste: 12/06/2027)*
- "Fechar o Espaço" (14 a 10 meses) mostra janela 12/04/2026 a 12/08/2026, e o prazo-alvo é 12/08/2026.
- Digitar um prazo manual de 30/07/2026 o torna o prazo-alvo; "voltar à sugestão" restaura 12/08/2026.
- Mudar a data para 12/07/2027 lista os marcos afetados antes de confirmar e mantém o de prazo manual.
- Data em 31/05 com "fim 3 meses antes" resulta em 28/02 (ou 29/02 em ano bissexto).
- Sem data exata, nenhum marco mostra janela calculada, e a tela diz "Sem data definida".

---

## F-CRN-06 — Tarefas Avulsas (`D-031`)

**O que é:** tarefas livres que não pertencem ao fluxo de dependências.

| Campo | Tipo | Regras |
| :--- | :--- | :--- |
| **Título** | Texto, obrigatório | — |
| **Responsável** | `Noivo` · `Noiva` · `Ambos` | Padrão: quem criou |
| **Prazo** | Data, opcional | — |
| **Estado** | `A fazer` · `Em andamento` · `Concluída` | — |
| **Nota, checklist, anexos** | Como no marco | F-CRN-07 e F-CRN-08 |

**Regras**
1. **Sem fase, sem categoria e sem dependências.**
2. Aparecem em uma seção "Avulsas", na visão de calendário e nos "meus próximos passos".
3. `Atrasada` é derivada como nos marcos (prazo vencido e não concluída).

**Critérios de aceite**
- Criar "pesquisar alianças" com responsável `Noiva` e sem prazo a mostra na seção "Avulsas" e na lente `Minha visão` da Noiva.
- Uma avulsa não aparece em nenhuma lista de bloqueios.

---

## F-CRN-07 — Checklist de Subtarefas (`D-031`)

**Regras**
1. Vale para **marcos e tarefas avulsas**.
2. Cada item tem texto, "feito" e ordem. Pode adicionar, reordenar, editar e remover.
3. Mostra o progresso ("2 de 5").
4. **Não altera** o estado do marco nem as dependências.
5. Concluir um marco com itens abertos pede confirmação ("há 3 itens em aberto"), e a pessoa pode concluir mesmo assim.

**Critérios de aceite**
- Marcar 2 de 5 itens mostra "2 de 5" no cartão e na lista.
- Concluir o marco com itens abertos pede confirmação e preserva os itens.

---

## F-CRN-08 — Anexos e Links (`D-031`)

**Regras**
1. Vale para marcos e avulsas, com os mesmos controles de `F-PLN-06`: **arquivo** (PDF ou imagem, via `FileStorage`, com validação de tipo real e tamanho) ou **link** (domínio visível, sem leitura automática da página).
2. Título e comentário opcionais. Autor mostrado como rótulo (`Noivo`/`Noiva`).
3. Qualquer um adiciona. **Só o autor** remove o seu, de forma lógica e recuperável.
4. No celular, o envio abre a câmera ou a galeria.

**Critérios de aceite**
- Anexar um PDF de um marco o mostra na lista com nome e tamanho.
- Um arquivo com extensão trocada (não é PDF real) é recusado.

---

## F-CRN-09 — Visões, Filtros e Lentes

**Aba "Por fase" (padrão)**

| Recurso | Comportamento |
| :--- | :--- |
| **Estrutura** | Uma seção por fase, com título, progresso ("4 de 6 concluídos", sem contar arquivados) e os marcos |
| **Foco padrão** | Destaca o que está **Destravado agora**; `Bloqueado` aparece com "Aguardando: …" |
| **Filtros** | Responsável (`Noivo`/`Noiva`/`Ambos`), estado, "só atrasados", "só avulsas". Estado na **URL** |
| **Lente `Casal`** | Todos os itens |
| **Lente `Minha visão`** | Itens em que sou responsável **ou** `Ambos` |
| **Detalhe** | Painel lateral (desktop) ou folha inferior (mobile) com campos, **"Depende de"**, **"Libera"**, checklist e anexos |

**Desktop:** seções de fase com tabela densa e painel lateral. **Mobile:** lista de cartões, com a seção "Meus próximos passos" no topo (itens `Destravado` ou `Em andamento` sob minha responsabilidade, ordenados por prazo).

**Critérios de aceite**
- Aplicar "Atrasados" altera a URL, e o botão voltar do navegador desfaz o filtro.
- Com a Noiva em `Minha visão`, aparecem itens dela e de `Ambos`, mas não os do Noivo.
- O painel de um marco lista de quais marcos ele depende e quais ele libera.
- Em 320 px, nenhuma linha exige rolagem horizontal.

---

## F-CRN-10 — Calendário Mensal (`D-031`)

**Aba "Calendário" (ao lado de "Por fase")**

| Recurso | Comportamento |
| :--- | :--- |
| **Conteúdo** | Itens (marcos e avulsas) pelo **prazo-alvo**. A janela não é desenhada; o marco aparece no dia do seu prazo. **Visitas `Agendadas` a fornecedores** (`F-CTT-06`, `D-034`) aparecem no dia da visita, com a hora, como itens somente leitura que abrem a ficha do contato |
| **Navegação** | Mês anterior/próximo e "hoje" |
| **Filtros e lentes** | Os mesmos de `F-CRN-09` |
| **Sem prazo** | Lista lateral/inferior "Sem prazo", para não os perder |
| **Desktop** | Grade mensal com os itens nos dias; clicar abre o detalhe |
| **Mobile** | Grade compacta com marcadores por dia e a lista do dia selecionado logo abaixo |

**Regras**
1. É uma **visão** sobre os mesmos dados, sem cópia.
2. Cor nunca é o único sinal: atrasados trazem ícone e texto.
3. A data do casamento, quando `Definida`, aparece destacada.

**Critérios de aceite**
- Um marco com prazo 12/08/2026 aparece no dia 12/08/2026 da grade.
- Itens sem prazo aparecem em "Sem prazo" e não na grade.
- No celular, tocar em um dia lista seus itens abaixo da grade.

---

## Fora desta área (v1)
- **Sincronização com Google/Apple Calendar:** v1.1+.
- **Notificações e lembretes** (in-app, push, WhatsApp): v1.1+ (`D-013`).
- **Gantt, horas e recorrência:** fora do produto.
- **Horário em tarefas:** fora da v1 (só data). A única exceção é a **visita a fornecedor** (`F-CTT-06`), que tem hora mas não é uma tarefa.
- **Roteiro do Dia D minuto a minuto:** v1.1+ (`scope.md` §7).
- **Roteiro fixo de uma tradição religiosa:** fora do produto (`D-026`).

## Pontos a validar em uso
1. As **janelas sugeridas** do catálogo (F-CRN-02) são genéricas e devem ser revisadas por vocês na primeira vez que a data for definida.
2. A regra de que `Em discussão` **bloqueia** o marco (F-CRN-04) pode parecer rígida: reavaliar depois de usar o Mapa de Escopo de verdade.
3. O calendário no celular (F-CRN-10): validar a legibilidade da grade compacta em tela de 320 px.
