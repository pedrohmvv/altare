# Features: Centro de Comando e Dados do Casal (`features/centro-de-comando.md`)

> **Status:** **Aprovado pelo usuário em 2026-10-27** (`D-038`). Cobre a **Visão Geral** (Home) do **Bloco 4.2**, o **"+ Registrar Rápido"** e a **exportação dos dados do casal**. O **Dossiê do Dia D**, também do Bloco 4.2, está na parte Dossiê de `features/convidados-enxoval-e-dia-d.md`.
>
> **Onde aparece na tela:** área **Visão Geral (Centro de Comando)**, a primeira das 7 áreas (`experience.md` §3.1, item 1), no desktop e no celular. O "Registrar Rápido" fica na casca de navegação, e a exportação, no menu do usuário.
>
> **Fontes:** `docs/design/experience.md` (§3.1, §3.2), `docs/product/scope.md`, `docs/product/jobs.md`, `docs/engineering/architecture.md` §5 (derivar, não duplicar), todas as áreas já detalhadas em `docs/product/features/`, `D-013`, `D-028`, `D-038`.
>
> **Convenções:** `F-CCD-xx` identifica a feature. O Centro de Comando **não cria dados**: toda informação é **derivada** das outras áreas, calculada no backend e sempre com link para a origem. "Autor" é o usuário da sessão. Todo número do exemplo é **fictício**. Nada é presumido: sem dado, o cartão diz o que falta.

---

## Visão da Área

**Jobs atendidos:** visão geral do momento, J9 (acompanhar teto, estimado, contratado e realizado) e o dia a dia de próximos passos e pagamentos.

| Cartão | Fonte | Lente? |
| :--- | :--- | :--- |
| Contagem regressiva e Definições Base | `F-PLN-01` | Não |
| **Atenção agora** | Regras sobre todas as áreas (`F-CCD-03`) | Parcial |
| Meus próximos passos | Contatos, marcos e avulsas | Sim |
| Destravados agora | Cronograma | Sim |
| Agenda dos próximos 7 dias | Visitas, parcelas e prazos | Sim |
| Termômetro do orçamento | Orçamento Ativo | Não |
| Convidados | Contadores de convidados | Não |

---

## F-CCD-01 — Estrutura da Visão Geral

**Regras**
1. É uma **visão sobre os mesmos dados**, sem cópia nem cálculo próprio duplicado: cada cartão consome a interface pública do módulo de origem (`architecture.md`).
2. **Cada item leva à origem** já filtrado (contato, parcela, marco, proposta). Tudo o que filtra fica na **URL** (`D-021`).
3. **Lente** (`Casal` · `Minha visão`): nos cartões marcados "Sim" ou "Parcial", `Minha visão` mostra só os itens cujo **responsável** é o perfil da sessão **ou** `Ambos`; `Casal` mostra todos.
4. **Desktop:** painel amplo em colunas, com Atenção agora e Termômetro do orçamento em destaque.
5. **Mobile:** **cartões empilhados** na ordem *Atenção agora*, *Meus próximos passos*, *Agenda dos próximos 7 dias*, *Termômetro do orçamento*, *Convidados*, mais a busca rápida (`F-CTT-10`) e o "Registrar Rápido" (`F-CCD-08`). Sem rolagem horizontal em 320 px.
6. Cor nunca é o único sinal: ícone e texto sempre (`design-system.md` §3.3).
7. O painel de insights da **IA** (Revisor Geral) é da v1.1 e **não** existe aqui. "Atenção agora" é outra coisa: regras fixas e determinísticas.

**Critérios de aceite**
- Cada item de qualquer cartão abre a tela de origem já posicionada nele.
- Mudar a lente atualiza os cartões "Sim" sem recarregar a página.
- Em 320 px, nenhum cartão exige rolagem horizontal.

---

## F-CCD-02 — Contagem Regressiva e Definições Base

| Elemento | Regra |
| :--- | :--- |
| **Contagem regressiva** | Só com a data do casamento `Definida` (nível exato, `F-PLN-01`): "faltam 247 dias", com a data no `title`. Antes disso mostra o nível de definição ("época: mês e ano") ou "data ainda não definida" |
| **Progresso das Definições Base** | "N de M definidas" e quais seguem `Em definição`, com link para o painel (`F-PLN-01`) |
| **Mapa de Escopo** | "N categorias classificadas, M em discussão" (`F-PLN-08`) |

**Critérios de aceite**
- Com data exata em 12/06/2027 e hoje 27/10/2026, o cartão mostra a contagem correta em dias.
- Sem data, o cartão não mostra contagem alguma e diz "data ainda não definida".

---

## F-CCD-03 — "Atenção agora" (`D-038`)

**O que é:** a lista das pontas soltas do casamento, por **regras fixas** (sem IA, sem notificações). É a forma de a Home chamar a atenção sem push nem alerta (`D-013`).

| Ordem | Regra | Origem | Lente |
| :--- | :--- | :--- | :--- |
| 1 | **Parcela atrasada** | `F-CTR-04` | Responsável da parcela |
| 2 | **Próximo Passo de contato atrasado** | `F-CTT-05` | Responsável do passo |
| 3 | **Marco ou tarefa atrasados** | `F-CRN-03` | Responsável |
| 4 | **Falta a minha avaliação** em uma possibilidade (caminho macro ou proposta) | `F-POS-03`, `F-PRP-05` | Sempre o usuário da sessão |
| 5 | **Possibilidade em `Conversar juntos`** | `F-POS-04`, `F-PRP-05` | Não filtra |
| 6 | **Visita agendada que já passou** ("Foi realizada ou cancelada?") | `F-CTT-06` | Participantes |
| 7 | **Categoria `Entra (Essencial)` sem Planejado** no cenário ativo | `F-ORC-04` | Não filtra |
| 8 | **Contrato com parcelas que não somam o valor** ("faltam R$ X a programar" ou "acima") | `F-CTR-04` | Não filtra |
| 9 | **Contrato com pendências do Dossiê** | `F-CTR-03` | Não filtra |

**Regras**
1. Cada item mostra **ícone, texto direto e o link** para resolver. Exemplo: "Parcela 'Sinal' do Contrato Exemplo venceu em 10/03/2027".
2. Mostra os **5 primeiros** pela ordem acima (e, dentro da regra, pelo mais antigo), com "ver todas (N)", que abre a lista completa.
3. Não há "dispensar": o item some quando o motivo é resolvido. Tudo é derivado.
4. Sem pendências: "Tudo em dia".
5. Regras que dependem de uma área ainda não construída (`F-CTR-*`, `F-PRP-*`) só passam a existir quando a área existe.

**Critérios de aceite**
- Uma parcela `Pendente` vencida aparece em primeiro lugar, com ícone e texto.
- Resolver a pendência (marcar a parcela como paga) faz o item sumir sem recarregar.
- A regra 4 mostra só pendências do usuário da sessão, mesmo com a lente `Casal`.
- Com 7 pendências, a Home mostra 5 e "ver todas (7)".
- Sem pendências, mostra "Tudo em dia".

---

## F-CCD-04 — Meus Próximos Passos e Destravados Agora

**Meus próximos passos:** junta, numa lista só, os itens com responsável na lente:
- **Próximos Passos de contatos** (`F-CTT-05`).
- **Marcos** `Destravado` ou `Em andamento` (`F-CRN-03`).
- **Tarefas avulsas** pendentes (`F-CRN-06`).

**Regras**
1. Ordem: atrasados primeiro, depois por data-alvo mais próxima, depois sem data.
2. Cada linha mostra o tipo (contato, marco, avulsa), o texto, a data-alvo (com `Atrasado` em ícone e texto) e o responsável.
3. Mostra **8** itens, com "ver todos" levando à área de origem filtrada.

**Destravados agora:** os marcos `Destravado` (liberados, ainda sem início) pela lente, **até 5**, com o nome, o prazo-alvo e "ver cronograma". É a resposta a "o que podemos decidir agora?".

**Critérios de aceite**
- Com a `Noiva` logada e a lente `Minha visão`, só aparecem itens da `Noiva` e de `Ambos`.
- Um Próximo Passo de contato atrasado aparece primeiro, com ícone e texto.
- Um marco `Bloqueado` não aparece em "Destravados agora".

---

## F-CCD-05 — Agenda dos Próximos 7 Dias

**Conteúdo:** hoje e os 6 dias seguintes, agrupado por dia:
- **Visitas** `Agendadas`, com hora (`F-CTT-06`).
- **Parcelas** `Pendente` por vencimento (`F-CTR-04`).
- **Prazos-alvo** de marcos, avulsas e Próximos Passos (`F-CRN-05`, `F-CTT-05`).

**Regras**
1. O que já passou **não** entra (está em "Atenção agora").
2. A lente filtra pelo responsável (visitas, pelos participantes).
3. Cada item mostra o tipo por ícone e texto, e leva à origem.
4. Dia sem itens não é mostrado. Sem nenhum item: "Nada previsto para os próximos 7 dias".

**Critérios de aceite**
- Uma visita em 15/03/2027 às 14:00 aparece no dia 15/03 com "14:00".
- Uma parcela vencida ontem não aparece na agenda e aparece em "Atenção agora".

---

## F-CCD-06 — Termômetro do Orçamento

**Conteúdo (cenário ativo, `F-ORC-06`):** **Planejado · Estimado · Contratado · Realizado (Pago)**, mais **A pagar** e o **teto global** com a barra de uso (`F-ORC-05`, `F-ORC-07`).

**Regras**
1. Os valores são **os mesmos** da aba Orçamento Ativo: nenhum cálculo novo.
2. "—" nunca é lido como zero. Os avisos do cenário aparecem junto ("estimado incompleto", "N linhas sem estimativa").
3. **Sem cenário ativo:** o cartão mostra "Sem orçamento ativo" e a ação "Criar o primeiro cenário".
4. Links: "Abrir orçamento" e "Fluxo de pagamentos".
5. A lente **não** se aplica: o dinheiro é do casal.

**Critérios de aceite**
- Os totais do cartão são idênticos aos do Orçamento Ativo no mesmo instante.
- Sem cenário ativo, aparece a ação de criar o primeiro.
- Estimado com linhas sem valor mostra o aviso de incompleto.

---

## F-CCD-07 — Convidados

**Conteúdo:** **Total Nominal**, **Estimado Ponderado** e **Confirmados** (`F-CNV-06`), com o detalhamento por faixa e o link para a lista.

**Regras**
1. Sem pesos definidos, o Ponderado mostra "defina os pesos" (`F-CNV-06`), nunca um número presumido.
2. Lista vazia: "Nenhum convidado ainda", com a ação "Adicionar o primeiro núcleo".

**Critérios de aceite**
- Os contadores do cartão são idênticos aos da lista de convidados.
- Sem pesos, o Ponderado mostra a orientação e não um número.

---

## F-CCD-08 — "+ Registrar Rápido" (`D-038`)

**O que é:** o atalho para registrar algo em poucos toques, sem navegar até a área. No celular, o **botão flutuante** acima da barra inferior; no desktop, o menu **"Novo"** no cabeçalho.

| Ação | Faz | Origem |
| :--- | :--- | :--- |
| **Novo contato** | Captura rápida: nome e categoria | `F-CTT-01` |
| **Registrar interação** | Escolhe o fornecedor e abre o formulário | `F-CTT-04` |
| **Anexar arquivo ou foto** | Escolhe o destino (contato, proposta ou contrato) e abre a câmera ou a galeria | `F-CTT-07`, `F-PRP-04`, `F-CTR-02` |
| **Marcar parcela como paga** | Lista as parcelas pendentes mais próximas e abre o formulário de pagamento | `F-CTR-04` |
| **Nova tarefa avulsa** | Abre o formulário | `F-CRN-06` |
| **Avaliar** | Lista as possibilidades em que falta a **minha** avaliação | `F-POS-03`, `F-PRP-05` |
| **Registrar presente ou compra** | Escolhe o item da lista de enxoval | `F-ENX-03` |

**Regras**
1. Cada ação **reaproveita o formulário da área**. Não há regra nem validação duplicada.
2. Cada ação só aparece quando a área existe. O botão nasce com o Bloco 3.1 (`D-028`), com as ações disponíveis até ali, e ganha as demais conforme os blocos chegam.
3. Cada ação chega ao formulário em **no máximo 2 toques**. O botão tem alvo ≥ 44 px e rótulo acessível.
4. No desktop, o menu "Novo" tem as mesmas ações e abre numa janela de diálogo.

**Critérios de aceite**
- No celular, "Marcar parcela como paga" leva ao formulário com a data de hoje e o valor previsto em até 2 toques.
- "Anexar arquivo" abre a câmera ou a galeria.
- Uma ação cuja área ainda não existe não é exibida.

---

## F-CCD-09 — Casamento Novo (Estado Vazio)

**Regras**
1. Sem nenhum dado, a Visão Geral mostra **um primeiro passo** claro: "Comece pelas Definições Base", com o link, e os cartões vazios dizem o que falta e onde registrar.
2. **Nenhum dado é inventado** (`AGENTS.md` §2): sem data, sem convidados, sem orçamento, os cartões ficam vazios com a orientação.
3. Conforme o casal preenche, os cartões passam a mostrar conteúdo, sem configuração.

**Critérios de aceite**
- Um casamento recém-criado mostra o convite para as Definições Base e nenhum número.
- Preencher a primeira definição atualiza o cartão de progresso.

---

## F-CCD-10 — Exportar Todos os Dados do Casal (`D-038`)

**O que é:** um arquivo para o casal **guardar fora do Altare**. É a proteção dos dados enquanto não houver backup automático (fora da v1).

**Onde:** menu do usuário, "Dados do casal", ação "Exportar todos os dados".

**Conteúdo do arquivo `.zip`** (`altare-dados-AAAA-MM-DD.zip`):

| Item | Descrição |
| :--- | :--- |
| **`dados.json`** | Todos os dados do casamento, **com versão do formato** (`schema_version`): definições, escopo, convidados, cronograma, cenários, possibilidades e avaliações, decisões, contatos e interações, contratos e parcelas, enxoval, dados do Dossiê e versões entregues |
| **`arquivos/`** | Os arquivos anexados (PDFs, imagens, comprovantes), organizados por tipo e dono, com o nome original |
| **`LEIA-ME.txt`** | Em português: o que há no arquivo, a data de geração e como conferir |

**Regras**
1. **Qualquer um dos dois** pode exportar. O arquivo é gerado **sob demanda** no backend e o download é protegido por sessão.
2. Itens **excluídos de forma lógica** entram no `dados.json` com a marca `excluido`. Os arquivos removidos não entram.
3. **Nunca inclui** senhas, hashes, sessões ou segredos.
4. A tela mostra o **tamanho estimado** antes de gerar e avisa: "O arquivo contém dados pessoais de convidados e fornecedores. Guarde com cuidado."
5. Registra **data, hora e autor** da última exportação, exibidos na tela ("Última exportação: 27/10/2026, Noivo"). Isso não gera notificação nem lembrete.
6. A exportação serve para **guardar e conferir**. **Importar** o arquivo de volta fica para v1.1+.
7. Usa só a biblioteca padrão para o `.zip` (sem dependência nova).

**Critérios de aceite**
- O `.zip` abre no computador e tem `dados.json`, a pasta `arquivos/` e o `LEIA-ME.txt`.
- O `dados.json` traz `schema_version` e não contém nenhum campo de senha ou sessão.
- Um contrato com PDF assinado tem o arquivo na pasta `arquivos/` com o nome original.
- Um item excluído logicamente aparece com `excluido`.
- Sem sessão, o download é recusado.
- A tela mostra a data da última exportação depois que ela foi feita.

---

## Fora desta área (v1)
- **Painel de insights da IA, Revisor Geral e notificações personalizadas:** v1.1+ (`D-008`, `D-013`).
- **Notificações in-app, push e WhatsApp:** v1.1+. "Atenção agora" é uma lista na tela, sem aviso ativo.
- **Backup automático diário:** não é funcionalidade da v1. É requisito de implantação, a tratar quando a hospedagem for definida (`D-019`).
- **Importar o arquivo de dados de volta:** v1.1+.
- **Personalizar cartões** (ordem, esconder, redimensionar): não solicitado.
- **Cartões por perfil configuráveis:** a lente cobre o caso.
- **Gráficos de evolução e projeção contra poupança:** v1.1+ (`scope.md` §3).

## Pontos de atenção
1. **Risco enquanto não houver backup automático:** os dados do casal estão num único banco. O casal deve exportar com frequência (por exemplo, a cada decisão importante) até o backup automático existir. O arquivo é a única cópia fora do Altare.
2. **Validar em uso:** se "Atenção agora" ficar longa demais, ajustar o limite de 5 ou a ordem das regras (reversível).
3. **Validar em uso:** se o casal sentir falta de lembretes ativos, antecipar o canal in-app de `D-013`.
