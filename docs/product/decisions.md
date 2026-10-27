# Registro de Decisões (`decisions.md`)

> Histórico cronológico de decisões de produto, design e escopo, registrando o porquê e as alternativas rejeitadas.

---

## D-001 — Papel do Produto: Substituto Estrutural de uma Assessoria de Planejamento + Hand-off para Cerimonialista do Dia
- **Data:** 2026-10-24
- **Fase:** Fase 1 (Entrevista) $\rightarrow$ Fase 2 (Conceito)
- **Decisão:** O produto deve guiar o casal do marco zero até a véspera do casamento assumindo o papel organizacional de uma assessoria de planejamento (escopo, ordem de decisões com dependências, comparação de propostas e controle financeiro) e gerar, ao final, um **Dossiê do Dia D** para passagem de bastão ao(à) cerimonialista do dia.
- **Razão:** O casal decidiu ter cerimonialista apenas para o dia do evento, sem assessoria durante a preparação. Essa é a motivação central para a criação do projeto.
- **O que ficou rejeitado:**
  - Tratar o produto apenas como um repositório passivo de notas/planilhas sem inteligência de sequência e dependências.
  - Criar um módulo multi-usuário para assessores operarem o sistema durante toda a preparação.

---

## D-002 — Modelo de Identidade: Dois Perfis Distintos (Noivo e Noiva)
- **Data:** 2026-10-24
- **Fase:** Fase 1 (Entrevista) $\rightarrow$ Fase 2 (Conceito)
- **Decisão:** O sistema terá dois perfis individuais (`Noivo` e `Noiva`) operando sobre o mesmo casamento, permitindo autoria em registros, atribuição de responsabilidades (`Noivo`, `Noiva`, `Ambos`) e avaliação individual de possibilidades antes da decisão conjunta.
- **Razão:** Ambos participam ativamente das decisões; separar as percepções individuais de cada um ajuda a identificar onde já existe consenso e onde é preciso conversar, além de dar clareza sobre quem ficou responsável por cada próximo passo.
- **O que ficou rejeitado:**
  - Conta única anônima ("casal") sem distinção de quem cadastrou, avaliou ou assumiu uma pendência.
  - Sistema complexo de permissões/RBAC corporativo.

---

## D-003 — Dispositivos e Contexto de Uso: Desktop para Planejar Juntos, Mobile para Consulta Rápida
- **Data:** 2026-10-24
- **Fase:** Fase 1 (Entrevista) $\rightarrow$ Fase 2 (Conceito)
- **Decisão:** A interface deve ser projetada de forma responsiva com **duas posturas complementares**:
  1. **Desktop (tela ampla):** Otimizado para sessões de planejamento conjunto do casal (comparação lado a lado de propostas, visão completa de orçamento, dependências do cronograma e gestão da lista de convidados).
  2. **Mobile (tela vertical):** Otimizado para consultas rápidas no dia a dia (ver próximo passo, checar dados de um fornecedor, consultar orçamento ou registrar uma nota rápida).
- **Razão:** Reflete a rotina real informada pelo usuário ("Computador para planejar juntos com calma, celular para ver coisas rápidas").
- **O que ficou rejeitado:**
  - Aplicação exclusiva para desktop (ruim para consulta de rua/WhatsApp).
  - Aplicação mobile-only (ruim para comparar propostas densas lado a lado).

---

## D-004 — Fronteira com Convidados, Presentes e Site Público
- **Data:** 2026-10-24
- **Fase:** Fase 1 (Entrevista) $\rightarrow$ Fase 2 (Conceito)
- **Decisão:**
  - **Entra na v1:** Lista nominal de convidados (conectada ao dimensionamento do casamento e orçamento) e gestão interna da lista de presentes.
  - **Fica de fora:** Site público dos noivos, RSVP aberto ao público na web e vitrine/checkout público de presentes.
- **Razão:** A lista nominal de convidados é fundamental desde o início para dimensionar o casamento e o orçamento; a lista de presentes faz sentido como organização interna do casal, mas um site público foge do problema central (gestão e decisão interna do casal).
- **O que ficou rejeitado:**
  - Deixar a lista nominal de convidados para depois (trabalhando apenas com um número solto na v1).
  - Construir construtor de site público para convidados.

---

## D-005 — Estratégia de IA: Fluxo Manual 100% Sólido na v1; IA na v1.1 com Confirmação Humana Obrigatória
- **Data:** 2026-10-24
- **Fase:** Fase 1 (Entrevista) $\rightarrow$ Fase 2 (Conceito)
- **Decisão:** A primeira versão (v1) será 100% manual e completa (permitindo anexar PDFs e links às propostas/contatos). As automações de IA (extração estruturada de PDFs de orçamento e textos de WhatsApp, equalização de itens inclusos/exclusos) entram na etapa imediatamente seguinte (v1.1), depois do modelo de dados e fluxo manual estarem validados, sempre exigindo confirmação explícita do usuário antes de gravar dados.
- **Razão:** Garante que o modelo mental e os fluxos do produto fiquem claros e confiáveis antes de automatizar a entrada, evitando que erros de extração da IA comprometam a confiança nos números do casamento.
- **O que ficou rejeitado:**
  - Bloquear a v1 esperando pipeline de OCR/LLM perfeito para PDFs.
  - Automações de IA que criam ou alteram orçamentos/decisões sem revisão prévia do usuário.

---

## D-006 — Papel Duplo da Lista de Presentes / Enxoval na v1
- **Data:** 2026-10-24
- **Fase:** Fase 2 (Conceito)
- **Decisão:** O módulo de Lista de Presentes na v1 terá papel duplo:
  1. **Controle de Enxoval / Casa Nova:** gerenciar o que o casal precisa para a casa (prioridade, preço estimado, links de referência, o que já compraram e o que já ganharam).
  2. **Rascunho Exportável para Convidados / Site Externo:** servir como base estruturada para exportar/cadastrar em um site externo de presentes ou gerar uma versão formatada para enviar diretamente aos convidados.
- **Razão:** O casal não quer construir um site público próprio dentro do produto, mas precisa tanto organizar a montagem da casa quanto preparar/exportar a lista que será compartilhada com os convidados.
- **O que ficou rejeitado:**
  - Lista restrita apenas a controle interno sem capacidade de formatação/exportação para convidados.
  - E-commerce público próprio com checkout integrado.

---

## D-007 — Possibilidades em Dois Níveis: Cenários Macro (Marco Zero) e Propostas de Fornecedores
- **Data:** 2026-10-24
- **Fase:** Fase 2 (Conceito)
- **Decisão:** O mecanismo de **Possibilidades** (alternativas em aberto $\rightarrow$ comparação lado a lado $\rightarrow$ avaliação do Noivo e da Noiva $\rightarrow$ decisão registrada com motivo) funcionará em dois níveis:
  1. **Nível Macro (Caminhos/Formatos do Casamento):** comparar cenários de largada (ex.: *Casar na praia vs. no campo vs. na cidade/restaurante*, ou diferentes cidades/portes) com prós, contras, impacto estimado no orçamento e implicações logísticas.
  2. **Nível de Categoria (Propostas de Fornecedores):** comparar orçamentos e pacotes específicos dentro de cada categoria (Espaço A vs. Espaço B, Buffet X vs. Buffet Y).
- **Razão:** Como o casal está no marco zero, as primeiras decisões difíceis acontecem antes mesmo de cotar fornecedores específicos. Usar a mesma estrutura de comparação e registro de decisão evita que essa definição inicial fique solta em conversas.
- **O que ficou rejeitado:**
  - Restringir Possibilidades apenas a cotações de fornecedores quando o formato do casamento já estivesse fechado.

---

## D-008 — Governança de IA: Confirmação Obrigatória para Alteração de Dados vs. Autonomia para Revisão e Notificações
- **Data:** 2026-10-24
- **Fase:** Fase 2 (Conceito)
- **Decisão:** Refinamento de `D-005`. A atuação da IA (a partir da v1.1) divide-se em dois regimes:
  1. **Ações que criam ou alteram dados do casamento (Mutação):** NUNCA acontecem no escuro. Toda extração de PDF/WhatsApp, rascunho inicial de casamento ou ajuste de comparativo exige revisão e confirmação explícita do usuário antes de salvar.
  2. **Ações analíticas, de revisão e comunicação interna (Somente-leitura / Proativas):** A IA PODE atuar autonomamente para fazer **revisão geral de tudo** (auditar coerência entre orçamento, cronograma, contratos e convidados sem alterar registros) e **enviar notificações personalizadas** para o Noivo e para a Noiva (lembretes inteligentes, alertas de dependências destravadas, resumos de pendências).
- **Razão:** Impedir que a IA corrompa dados ou tome decisões pelo casal, sem abrir mão do valor de ter um "assessor inteligente" que revisa o todo proativamente e avisa cada um do que precisa de atenção.
- **O que ficou rejeitado:**
  - Proibir qualquer execução em background da IA (o que impediria revisões contínuas e notificações personalizadas).
  - Permitir que a IA altere valores de orçamento, escopo ou decisões automaticamente sem confirmação.

---

## D-009 — Simulador de Múltiplos Orçamentos Completos em Paralelo Entra na v1
- **Data:** 2026-10-24
- **Fase:** Fase 2 (Conceito)
- **Decisão:** O **Simulador de Múltiplos Orçamentos Completos em Paralelo** passa a fazer parte da **v1 (Agora)**, e não de versões futuras. O casal poderá criar e comparar cenários completos de orçamento em paralelo (ex.: *"Orçamento Cenário Praia - 120 pessoas"* vs. *"Orçamento Cenário Campo - 180 pessoas"* vs. *"Orçamento Enxuto"*), ajustando tetos, categorias ativas e premissas de convidados em cada um antes de definir (ou enquanto evolui) o orçamento oficial ativo.
- **Razão:** Como o casal está no marco zero e ainda vai decidir caminhos macro do casamento, poder simular orçamentos completos lado a lado já na v1 é essencial para tomar as decisões fundacionais com segurança financeira.
- **O que ficou rejeitado:**
  - Adiar o simulador de múltiplos orçamentos em paralelo para a v1.1+.

---

## D-010 — Entrevistas Guiadas por IA para Gerar Rascunho Inicial do Casamento (Perfil e Gosto dos Noivos)
- **Data:** 2026-10-24
- **Fase:** Fase 2 (Conceito)
- **Decisão:** Em vez de descartar qualquer ferramenta de descoberta de estilo, entra no escopo (na camada de IA — v1.1) a funcionalidade de **Entrevistas Guiadas por IA**: caso o casal queira ajuda para sair do zero (ou refinar o alinhamento), a IA conduz uma entrevista conversacional com o Noivo e a Noiva sobre o perfil, gostos, prioridades e restrições de cada um, gerando como saída uma proposta de rascunho do casamento (sugestão de escopo do que entra/fica de fora, cenários macro e distribuição sugerida de orçamento) para confirmação do casal.
- **Razão:** Testes estáticos de revista são inúteis, mas uma entrevista inteligente baseada no perfil e gosto real dos noivos acelera a criação do rascunho inicial do casamento.
- **O que ficou rejeitado:**
  - Quizzes estáticos/genéricos de múltipla escolha.
  - Descartar completamente o apoio guiado para descobrir o formato/rascunho do casamento.

---

## D-011 — Fechamento e Aprovação da Fase 2 (Conceito e Escopo)
- **Data:** 2026-10-24
- **Fase:** Fase 2 (Conceito) $\rightarrow$ Fase 3 (Experiência)
- **Decisão:** Conceito e corte de escopo (v1 vs. futuro vs. fora) formalmente aprovados pelo usuário após inclusão de `D-008`, `D-009` e `D-010`. Projeto avança para a **Fase 3 (Experiência)**.
- **Razão:** Todas as perguntas bloqueadoras das Fases 1 e 2 foram respondidas e documentadas.
- **O que ficou rejeitado:** N/A.

---

## D-012 — Modelo de Avaliação Individual nas Possibilidades: Classificação Qualitativa + Nota (1 a 5) + Comentário
- **Data:** 2026-10-24
- **Fase:** Fase 3 (Experiência)
- **Decisão:** Em cada `Possibilidade` (seja um cenário macro ou uma proposta de fornecedor), tanto o `Noivo` quanto a `Noiva` terão três campos de avaliação individual:
  1. **Classificação rápida:** `Favorito`, `Gostei`, `Com ressalvas` ou `Descartaria`.
  2. **Nota numérica:** escala de `1 a 5`.
  3. **Comentário livre:** impressões, pontos de atenção e percepções pessoais.
- **Razão:** Combina leitura visual instantânea de consenso/divergência (pelos selos qualitativos) com desempate objetivo (pela nota de 1 a 5) e contexto subjetivo (pelo comentário).
- **O que ficou rejeitado:**
  - Apenas nota numérica fria sem selo de intenção (`Favorito` / `Descartaria`).
  - Matrizes pesadas de múltiplos subcritérios obrigatórios que deixariam o preenchimento lento.

---

## D-013 — Canais de Notificações Personalizadas e Alertas da IA: In-App, Push (Celular/Web) e WhatsApp
- **Data:** 2026-10-24
- **Fase:** Fase 3 (Experiência)
- **Decisão:** As notificações personalizadas e alertas do Revisor Geral de IA (`D-008`, previstos para a v1.1+) terão três canais de entrega mapeados na arquitetura:
  1. **Painel In-App** (centro de notificações e diagnóstico dentro do próprio produto).
  2. **Notificações Push (Mobile / PWA / Navegador)** para lembretes rápidos no celular.
  3. **WhatsApp** para resumos personalizados, lembretes de próximos passos com fornecedores e avisos de vencimento de parcelas.
- **Razão:** O casal usa celular para acompanhamento rápido no dia a dia e já concentra a rotina de comunicação no WhatsApp; E-mail foi descartado como canal prioritário.
- **O que ficou rejeitado:**
  - E-mail como canal principal de notificação.

---

## D-014 — Fechamento e Aprovação da Fase 3 (Experiência)
- **Data:** 2026-10-24
- **Fase:** Fase 3 (Experiência) $\rightarrow$ Fase 4 (Direção Visual)
- **Decisão:** Jornada ponta a ponta, modelo de 10 objetos de domínio, arquitetura de 7 áreas (com postura Desktop vs. Mobile e seletor de perfil `Casal`/`Noivo`/`Noiva`) e os 8 fluxos principais aprovados pelo usuário. Projeto avança para a **Fase 4 (Direção Visual)**.
- **Razão:** Todas as questões da Fase 3 (`OQ-004`, `OQ-005` e `OQ-006`) foram definidas.
- **O que ficou rejeitado:** N/A.

---

## D-015 — Paleta, Tipografia e Tom de Voz da Direção Visual
- **Data:** 2026-10-24
- **Fase:** Fase 4 (Direção Visual)
- **Decisão:**
  1. **Paleta e Atmosfera:** Tons naturais e quentes (fundo creme/areia/alabastro suave, verde-oliva/sálvia escuro para estrutura e ações primárias, terracota/argila para destaques/alertas de atenção e champagne/pedra clara para superfícies secundárias).
  2. **Tipografia Mista Editorial:** Títulos com serifa elegante (trazendo identidade de casamento) + corpo de interface e controles em sans-serif limpa + números tabulares/monoespaçados alinhados para valores de orçamento e comparativos.
  3. **Tom de Voz:** Parceiro calmo e direto — acolhedor, fala com o casal ("vocês"), reduz a ansiedade de planejar sem assessoria e vai direto ao ponto acionável.
- **Razão:** Evita tanto a frieza de um ERP corporativo quanto o excesso de ornamento de portais tradicionais de casamento, mantendo alta legibilidade para sessões longas de planejamento.
- **O que ficou rejeitado:**
  - Paleta fria/corporativa (azul/cinza puro) ou dark-mode estrito.
  - Tipografia 100% ornamental (ruim para tabelas de orçamento) ou 100% técnica sem identidade.
  - Microcopy robótico/técnico demais.

---

## D-016 — Personalidade Visual: Editorial Acolhedor & Estruturado (Opção A)
- **Data:** 2026-10-24
- **Fase:** Fase 4 (Direção Visual) $\rightarrow$ Fase 5 (Congelamento)
- **Decisão:** A personalidade visual oficial do produto é **Editorial Acolhedor & Estruturado (Opção A)**:
  - Fundo principal em tom de **papel creme/areia perceptível (`#F9F5EC`)**, cartões em **marfim quente (`#FFFDF9`)** com bordas amendoadas (`#DFD5C3`) e caixas de agrupamento em **champagne/areia (`#F5EFE2` / `#EFE7D6`)**.
  - A **fonte com serifa** aparece tanto nos títulos de páginas/seções quanto nos **nomes dos espaços, fornecedores e cenários dentro dos cartões**, dando a sensação de um caderno/revista autoral do casamento, enquanto os controles são em *sans-serif* e os valores financeiros em fonte *monoespaçada/tabular*.
- **Razão:** Traz identidade afetiva e autoral de casamento sem abrir mão da precisão estrutural e financeira nas tabelas e comparativos.
- **O que ficou rejeitado:**
  - Opção B (*Clean, Moderno & Aesthetic* 100% branco/alabastro com cartões apenas em sans-serif).
  - Opção C (Híbrido que restringia a serifa apenas ao título do topo da página).

---

## D-017 — Congelamento do Conceito (Fase 5 Concluída)
- **Data:** 2026-10-24
- **Fase:** Fase 5 (Congelamento)
- **Decisão:** O usuário confirmou formalmente o congelamento do conceito (`vision.md`, `personas.md`, `jobs.md`, `scope.md`, `experience.md` e `visual-direction.md`). A fase de concepção está encerrada e a documentação passa a orientar a engenharia em `docs/engineering/README.md` e a implementação da v1.
- **Razão:** Todos os critérios de pronto da fase de concepção foram atingidos sem ambiguidades.
- **O que ficou rejeitado:** N/A.

---

## D-018 — Estratégia de Desenvolvimento em Pirâmide de Blocos (Sem Datas ou Prazos)
- **Data:** 2026-10-24
- **Fase:** Pós-Congelamento (Planejamento de Engenharia)
- **Decisão:** A construção do produto seguirá uma **Pirâmide de Blocos** documentada em `docs/engineering/roadmap.md`, partindo dos blocos mais básicos e fundacionais (Nível 0: Fundação e Design System; Nível 1: Escopo, Convidados e Cronograma; Nível 2: Simulador de Orçamentos e Cenários Macro; Nível 3: Contatos, Comparador de Propostas e Contratos/Parcelas; Nível 4: Enxoval, Centro de Comando e Dossiê do Dia D) até os mais avançados (Nível 5: Camada de IA v1.1+), **sem datas ou prazos fixos**, orientada apenas pela ordem de dependência técnica e de valor para o casal.
- **Razão:** Permite construir sobre alicerces sólidos e entregar módulos utilizáveis pelo casal desde os primeiros blocos, sem pressão artificial de calendário.
- **O que ficou rejeitado:**
  - Construir tudo em um único bloco monolítico ("big bang") antes de poder usar.
  - Cronograma de engenharia amarrado a datas arbitrárias.

---

## D-019 — Stack Técnica e Estratégia de Persistência/Hospedagem (Local-First $\rightarrow$ Cloud PWA)
- **Status:** **Parcialmente substituída por `D-020` (2026-10-26)** — backend, frontend, autenticação, banco-alvo e hospedagem foram redefinidos. Mantidos: local-first, SQLite no início, PWA e armazenamento local de PDFs no início.
- **Data:** 2026-10-24
- **Fase:** Pós-Congelamento (Planejamento de Engenharia)
- **Decisão:**
  1. **Aplicação Full-Stack & PWA:** `Next.js (App Router + TypeScript + Tailwind CSS)` com manifesto PWA (acesso amplo no navegador do computador e instalável na tela inicial do celular).
  2. **ORM e Banco de Dados:** `Drizzle ORM` (ou `Prisma`), iniciando o desenvolvimento dos primeiros blocos com **SQLite local + armazenamento local de PDFs** (para velocidade máxima e zero burocracia inicial) e preparado para migração transparente para **Supabase (PostgreSQL + Supabase Storage privado + Supabase Auth)** e deploy na **Vercel** quando o casal quiser sincronizar entre computador e celulares na nuvem.
- **Razão:** Une rapidez para começar a construir localmente sem depender de configuração de nuvem no dia 1 com um caminho direto e gratuito para sincronização web/mobile quando necessário.
- **O que ficou rejeitado:**
  - Arquiteturas pesadas com múltiplos microsserviços separados.
  - Bloquear o início do código esperando provisionamento de infraestrutura externa.

---

## D-020 — Revisão da Stack: Backend Python, SPA React, SQLite Inicial, Login Individual e Nuvem Após o Nível 1
- **Data:** 2026-10-26
- **Fase:** Pós-Congelamento (Planejamento de Engenharia) — revisão parcial de `D-019`
- **Decisão:**
  1. **Backend em Python** (FastAPI, SQLAlchemy 2, Alembic), em monólito modular.
  2. **Frontend:** React + TypeScript + Vite como **SPA/PWA estática**, consumindo a API FastAPI com tipos gerados do OpenAPI. Em produção, o FastAPI serve API e estáticos na mesma origem.
  3. **Banco:** **SQLite no início**, migrando para PostgreSQL ao ir para a nuvem, com regras de portabilidade obrigatórias desde a primeira migração e um portão de testes em PostgreSQL antes do primeiro deploy (`docs/engineering/stack.md` §4).
  4. **Hospedagem:** 100% local nos Níveis 0 e 1; nuvem (container + Postgres gerenciado + storage S3-compatível) quando o Nível 1 estiver utilizável. Supabase Auth e Vercel saem do plano.
  5. **Perfis e login:** **dois logins individuais** (`Noivo` e `Noiva`); a autoria de avaliações, interações e tarefas vem da sessão; o seletor de perfil passa a alternar a *lente de visão* (`Casal` / `Minha visão`), não a autoria.
- **Razão:** O usuário quer backend em Python. Com backend próprio, o Next.js perde o sentido (app privado, sem SEO, SSR exigiria um servidor Node adicional) e a SPA reduz a superfície de deploy. O login individual preserva a integridade das avaliações independentes (`D-012`). SQLite e nuvem tardia mantêm o início sem atrito (`D-019`).
- **O que ficou rejeitado:**
  - Next.js como frontend com FastAPI separado (dois servidores sem ganho de SSR).
  - Frontend Python puro (HTMX): interações ricas do comparador/simulador e PWA ficam mais trabalhosas.
  - PostgreSQL desde o dia 1 via Docker (recomendado pelo agente; o usuário preferiu SQLite — risco mitigado em `stack.md` §4 e §12).
  - Nuvem desde o Nível 0 e servidor doméstico com Tailscale.
  - Login único do casal com seletor autodeclarado.
- **Pendente:** *(resolvido em `D-021`)* detalhamento granular da stack e impactos do login individual na experiência.

---

## D-021 — Aprovação da Stack Detalhada e Ajuste da Semântica do Seletor de Perfil
- **Data:** 2026-10-26
- **Fase:** Pós-Congelamento (Planejamento de Engenharia) → Implementação
- **Decisão:**
  1. **Stack detalhada aprovada integralmente** conforme `docs/engineering/stack.md` (resolve `OQ-ENG-003`), incluindo: `uv`, FastAPI, SQLAlchemy 2 síncrono, Alembic, autenticação própria com sessões server-side, Typer; Vite + React 19, TanStack Router/Query/Table, `openapi-typescript` + `openapi-fetch`, Tailwind v4 + shadcn/ui, Biome, `vite-plugin-pwa`; fontes Newsreader + Plus Jakarta Sans + JetBrains Mono; cálculos de negócio somente no backend; modelagem incremental (Nível 0 modela apenas `User`, `Session`, `Profile`, `FileAsset`); PWA sem offline de escrita na v1.
  2. **Login individual (resolve `OQ-ENG-004` pelas propostas padrão, aceitas junto com a aprovação):**
     - Cada um avalia na **própria sessão**; no computador compartilhado, a troca de usuário é rápida (senha).
     - Avaliações são **visíveis ao outro imediatamente** (avaliação cega fica como opção futura).
     - O seletor de lente tem apenas **`Visão do Casal`** e **`Minha visão`** (não há visão do outro perfil).
- **Razão:** Mantém a integridade das avaliações independentes (`D-012`) sem adicionar atrito de produto nem funcionalidades não pedidas.
- **O que ficou rejeitado:**
  - Avaliação cega por padrão; visão somente-leitura do perfil do outro; autoria escolhida manualmente.
- **Observação:** A aceitação de `OQ-ENG-004` foi inferida da aprovação geral da proposta; o usuário pode reverter a qualquer momento.

---

## D-022 — Arquitetura Clean Pragmática, Histórico Básico, Marca Paramétrica, Ornamento Sutil, Cantos Moderados e Tema Claro + Escuro
- **Data:** 2026-10-26
- **Fase:** Pós-Congelamento (Planejamento de Engenharia e Design)
- **Decisão:**
  1. **Arquitetura do backend: Clean Architecture** (Domínio → Aplicação/Casos de Uso → Adaptadores → Infraestrutura), proposta pelo usuário por causa dos **fluxos de agentes de IA** (Nível 5). Aplicada de forma **pragmática**: agentes como adaptador de entrada sobre os mesmos casos de uso; mutação por agente só via `ChangeProposal` aprovada por humano; agentes proativos só com portas de consulta; entidades ricas apenas onde há regra; consultas fora do domínio (CQRS leve); mapeamento imperativo do SQLAlchemy; contratos verificados com `import-linter`. "Service" deixa de ser camada (substituído por casos de uso e serviços de domínio puros).
  2. **Histórico de alterações: básico** — `created/updated_at`, `created/updated_by`, exclusão lógica (`deleted_at/by`) e `version` (bloqueio otimista). Trilha completa de auditoria fica fora do escopo atual.
  3. **Marca paramétrica:** nome de trabalho neutro e monograma do casal por configuração futura (nenhum nome/iniciais inventados). *(Nome de trabalho `Wedding Planner` e símbolo "&" substituídos por `D-023`.)*
  4. **Ornamento sutil:** textura de papel quase imperceptível, hairlines e ilustração botânica em linha apenas em login, estados vazios e Dossiê.
  5. **Linguagem de forma:** cantos moderados (6–10 px), cartões planos com hairline, sem sombras em cartões.
  6. **Tema claro + escuro ("Noite Oliva")** já no Nível 0, com `claro / escuro / sistema`. Refina `D-015`, que rejeitou apenas o *dark-mode estrito* (único tema escuro). *(Construção do tema escuro adiada em `D-028`; a paleta continua aprovada.)*
- **Razão:** Os agentes de IA aumentam a complexidade (propostas, confirmação, somente-leitura, múltiplos canais e provedores), e isso justifica portas e casos de uso explícitos; o histórico básico basta para dois usuários; as escolhas visuais mantêm a atmosfera editorial sem cair em ornamento kitsch (`D-016`).
- **O que ficou rejeitado:**
  - Monólito modular sem separação de domínio/infraestrutura (recomendação inicial do agente; o usuário preferiu Clean por causa dos agentes).
  - Trilha de auditoria completa e histórico mínimo sem autoria.
  - Ornamento nulo ou rico; cantos retos ou muito arredondados; tema exclusivamente claro.
- **Ajustes colaterais:** `stack.md` §3.1 substituída por `architecture.md`; eventos de domínio síncronos em processo passam a existir (antes "sem barramento de eventos"); `Profile` vira enum de domínio (não tabela); `import-linter` e `dependency-cruiser` entram no CI.
- **Pendente:** *(resolvido em `D-025` e `D-027`)* aprovação do detalhamento em `architecture.md` (`OQ-ENG-005`), `identity.md` e `design-system.md` (`OQ-DS-001`).

---

## D-023 — Nome do Produto: **Altare**; Princípio "O Altar no Centro, a Festa a Serviço"; Sacralidade Discreta
- **Data:** 2026-10-27
- **Fase:** Pós-Congelamento (Identidade de Marca)
- **Decisão:**
  1. O produto se chama **Altare** (latim/italiano *altare*, "altar"). A escolha foi do usuário ("Eu escolho e aprovo"), a partir de entrevista de perfil e duas rodadas de candidatos. Substitui o nome de trabalho `Wedding Planner` (que permanece apenas como nome do repositório/pasta).
  2. **Princípio de marca e produto: "O altar no centro. A festa a serviço."** A centralidade do matrimônio (cerimônia religiosa católica, informada pelo Noivo) orienta o produto, mesmo que a ferramenta seja um planejador com foco na festa. *(Esclarecido em `D-026`: o produto não é só para casamentos católicos; o centro é o compromisso, em qualquer tipo de cerimônia.)*
  3. **Sacralidade discreta:** sagrado e beleza como atmosfera (proporção, silêncio, luz, serifa, arco), **sem** símbolos religiosos literais, **sem** cara de "igrejinha" ou devocional; latim apenas no nome; interface 100% em português.
  4. **Marca visual:** wordmark `Altare` em Newsreader 500 e símbolo proposto **"A sobre a mensa"** (letra A assentada sobre uma lâmina que representa a mesa do altar). Detalhes e medidas em `docs/design/identity.md` (documento-fonte da marca). Substitui a proposta anterior do símbolo "&".
- **Perfil levantado na entrevista (base das escolhas):** católico tradicional, missa na forma ordinária (sem rito extraordinário disponível na Paraíba), devoção a São João Paulo II, São Josemaria Escrivá, São Paulo e São Padre Pio; aprecia o canto gregoriano e o latim por **sacralidade e beleza**; quer nome que não seja explícito sobre casamento, sem trocadilhos, sem clichês românticos, sem nome de casal, sem inglês óbvio, sem cara de startup genérica, sem acentos; tom elegante, sóbrio e levemente irreverente; evoca clareza, tempo e caminho.
- **Razão:** O altar é o centro do casamento católico e nomeia o lugar, não a instituição. É curto o bastante para marca, sóbrio, belo e sem trocadilho. Reflete a hierarquia que o usuário descreveu: o sacramento no centro, a festa em ordem a serviço dele.
- **Riscos assumidos pelo usuário:**
  - Existe a *Altare Cerimonial* (assessoria de casamentos em Juiz de Fora/MG) e os domínios `altare.{com,app,com.br,co,io}` já estão registrados (checagem de DNS, indicativa).
  - "Altar" como objeto concreto pode ser lido como loja de artigos religiosos ou espaço de eventos; mitigado pela regra de sacralidade discreta e pelo uso do nome sem símbolos religiosos.
  - **Reavaliação obrigatória** do nome e busca formal no INPI se houver qualquer passo para uso público/SaaS (`D-002`).
- **O que ficou rejeitado:**
  - **Votum** (voto/consentimento: recomendação do agente por teologia e por evitar colisão de categoria; colide com uma empresa de tecnologia e um app de enquetes).
  - Candidatos de metáfora de obra e instrumentos (Aresta, Prumo, Compasso, Andante etc.), de vocabulário litúrgico/arquitetônico (Arras, Neuma, Adro, Decoro, Condigno, Dossel, Coro, Introito) e as demais alternativas das rodadas de entrevista.
  - Nomes que mencionam explicitamente casamento, trocadilhos, clichês românticos, junção de nomes do casal e termos devocionais (nome de Deus, "Fiat", "Domine", títulos de obras de São Josemaria).
- **Pendente:** aprovação do restante da identidade em `docs/design/identity.md` (`OQ-DS-001`) e validação do eixo católico no escopo (`OQ-PROD-001`).

---

## D-024 — Pacote Completo de Identidade Visual (Brand Book) em `docs/design/identidade-visual/`
- **Data:** 2026-10-27
- **Fase:** Pós-Congelamento (Identidade de Marca)
- **Pedido do usuário:** "Não quero apenas isso como documento de identidade visual. […] Quero nesse nível de detalhe, mas mantenha organizado dentro daqui", tomando como referência a pasta `identidade-visual/` do repositório de design da Paso.
- **Decisão:**
  1. A identidade do Altare passa a ter um **pacote completo**: guia de 43 páginas (`altare-identidade-visual.pdf` + `.html`), logos-mestre em SVG, componentes exportados em SVG + PNG com índice (`componentes/INDEX.md`), PNG de cada página, favicon, ícone do app e ornamentos.
  2. **`tokens.json` é a fonte única dos valores** (cores claras e escuras, versões da marca, geometria, mínimos, ícone do app, escala tipográfica, forma e movimento). O guia é **gerado** por um pipeline reprodutível (`build/`, `uv run build.py`; `--marca` regenera os logos-mestre). Matrizes de contraste e fichas de cor são calculadas, nunca digitadas.
  3. Os logos-mestre saem dos **contornos reais da Newsreader** (peso 500, `opsz` 72, kerning via HarfBuzz), sem redesenho manual.
  4. **Refinamentos de marca** `[PROPOSTA]`, sujeitos a `OQ-DS-001`:
     - grade modular (1 m = H/20): lâmina de 27 × 1 m (antes 0,052 H, agora 0,05 H) e folga de 2 m;
     - **versão pequena** (lâmina de 2 m) para 16 a 23 px e favicon;
     - **seis versões de cor** (oliva, carvão, preto, marfim, sálvia, branco);
     - mínimos revistos: símbolo de 24 px (16 px só na versão pequena), vertical de 96 px e equivalentes em mm;
     - regra métrica do lockup vertical (2,6 × e espaço de 1 versal);
     - favicon com versal de 43% do lado;
     - seis ornamentos desenhados (três arcos e três ramos);
     - dez usos incorretos ilustrados.
  5. `docs/design/identity.md` continua sendo o **documento das regras** (o porquê). O pacote é a especificação visual e os arquivos (o como). `docs/design/brand/` (prévia de uma imagem só) foi **removida**, porque o pacote a substitui.
  6. As telas de exemplo do guia **não mostram nenhum dado do casamento**: usam "Em definição" e "[a definir]", e os fornecedores fictícios levam o selo "conteúdo ilustrativo".
- **Razão:** o usuário pediu nível de detalhe de brand book profissional. Gerar tudo a partir de tokens e fontes reais evita divergência entre documento, assets e o futuro código (Bloco 0.2 copia os assets e gera `tokens.css` do mesmo `tokens.json`).
- **O que ficou rejeitado:**
  - Manter a identidade só em Markdown com uma prévia, que era insuficiente para o pedido.
  - Desenhar o guia à mão em ferramenta visual (Figma etc.), que não é reprodutível e se desalinha dos tokens.
  - Copiar a estrutura de pastas inteira da Paso fora de `docs/design/`, o que contraria o "mantenha organizado dentro daqui".
- **Pendente:** *(resolvido em `D-025`)* aprovação visual do pacote em `OQ-DS-001`.

---

## D-025 — Aprovação da Identidade Visual do Altare e do Design System
- **Data:** 2026-10-27
- **Fase:** Pós-Congelamento (Identidade de Marca)
- **Decisão:** O usuário aprovou ("Aprovo.") o guia completo (`D-024`), `docs/design/identity.md` e `docs/design/design-system.md`. Fica resolvida a `OQ-DS-001`, com todos os itens na **proposta padrão**:
  - o pacote como formato oficial, com a versão pequena do símbolo, as seis versões de cor, os mínimos revistos e os seis ornamentos;
  - o símbolo "A sobre a mensa", sem lockup lado a lado;
  - a assinatura formal `ALTARE`;
  - arco de volta perfeita e ramo de oliveira como os únicos motivos;
  - a sacralidade discreta;
  - as fontes Newsreader, Plus Jakarta Sans e JetBrains Mono;
  - a paleta escura Noite Oliva e as extensões `border-strong`, `ink-subtle` e `primary-hover`;
  - texto terracota pequeno sempre em `accent-ink`;
  - na navegação mobile, 4 destinos + "Mais" + botão flutuante;
  - nenhuma cor por perfil;
  - nota de 1 a 5 em botões numéricos;
  - a formatação monetária;
  - a escala tipográfica e as alturas de controle.
- **Escolhas abertas resolvidas pela proposta padrão (reversíveis):** **nenhuma assinatura verbal** (`identity.md` §1.5); **`heart-handshake` mantido**, restrito ao selo de consenso (`handshake` fica como alternativa registrada).
- **Razão:** aprovação explícita do usuário após a revisão do guia de 43 páginas.
- **O que ficou rejeitado:** reabrir o símbolo ou a paleta. Não houve contraproposta.
- **Cuidados pós-aprovação (não bloqueiam o Nível 0):**
  - mostrar o guia à Noiva;
  - refinar à mão o kerning do wordmark e o *hinting* do favicon a 16 px;
  - testar a impressão real do Dossiê em P&B;
  - fazer a busca no INPI antes de qualquer uso público.

---

## D-026 — O Altare Não É Só para Casamentos Católicos (Produto Não Confessional)
- **Data:** 2026-10-27
- **Fase:** Pós-Congelamento (Produto e Marca)
- **Esclarecimento do usuário:** "Não é apenas para casamentos católicos, apesar de eu ser católico."
- **Decisão:**
  1. **Produto e marca são não confessionais.** O princípio "O altar no centro. A festa a serviço." continua valendo. Lê-se "altar" no sentido amplo de "subir ao altar", o lugar do compromisso, seja a cerimônia religiosa de qualquer tradição, civil ou simbólica. A fé católica do autor é a **origem** do nome, não uma premissa do produto.
  2. **O tipo de cerimônia é um dado do casal** (como data, cidade e estilo): nunca é presumido nem inventado.
  3. **Escopo da v1 inalterado:** a cerimônia entra pelas categorias neutras que já estavam no Mapa de Escopo (`scope.md`: "cerimônia civil" e "cerimônia religiosa/simbólica"), com etapas e marcos criados e editados pelo casal. **Nenhum roteiro fixo de uma tradição** (ex.: processo paroquial) entra na v1. Modelos prontos por tradição, se um dia forem desejados, exigem nova decisão.
  4. Termos de uma tradição específica (paróquia, celebrante, rito) não aparecem na interface nem nos exemplos, a não ser quando cadastrados pelo próprio casal.
  5. A identidade aprovada em `D-025` já é compatível com isso (sacralidade discreta, sem símbolos religiosos). Só mudaram os textos que citavam o casamento católico como centro (`identity.md` §1.1, §1.3 e §1.4, `vision.md` §6 e a página "Altare, o nome" do guia).
- **Resolve:** `OQ-PROD-001`. A pergunta sobre a Noiva considerar a cerimônia religiosa o centro deixa de bloquear o escopo, porque o produto não depende dessa resposta.
- **Razão:** evita embutir uma confissão num produto que deve servir ao casal tal como ele é e mantém aberta, sem virar premissa, a hipótese futura de outros casais (`D-002`).
- **O que ficou rejeitado:**
  - Trilha católica fixa (curso de noivos, processo matrimonial) na v1.
  - Seletor de "religião do casal" com fluxos diferentes por tradição, porque adiciona complexidade sem necessidade na v1.
  - Trocar o nome. "Altar" funciona fora do contexto católico ("subir ao altar").
- **Premissas mantidas:** uso inicial pessoal do Noivo e da Noiva (`D-002`); expansão para outros casais segue como hipótese futura.

---

## D-027 — Aprovação da Arquitetura; Início da Implementação Adiado por Escolha do Usuário
- **Data:** 2026-10-27
- **Fase:** Pós-Congelamento (Pronto para Implementação)
- **Decisão:**
  1. O usuário aprovou `docs/engineering/architecture.md` como está ("Eu aprovo"). Fica resolvida a `OQ-ENG-005`, com todos os itens na proposta padrão:
     - limites pragmáticos de §3;
     - eventos síncronos em processo;
     - agentes como adaptador de entrada + `ChangeProposal`;
     - "derivar, não duplicar";
     - convenções de API e erros;
     - contratos `import-linter`/`dependency-cruiser`;
     - `Profile` como enum.
  2. **Nenhum arquivo de implementação será criado por enquanto** ("mas não quero criar nada de arquivos ainda"). O Nível 0 (Bloco 0.1) está **desbloqueado, mas só começa quando o usuário pedir explicitamente**.
- **Razão:** aprovação explícita do usuário. O momento de começar a construir é escolha dele.
- **O que ficou rejeitado:** iniciar o Bloco 0.1 automaticamente após a última aprovação.

---

## D-028 — Design System Enxuto, Proporcional a um App Pessoal de Duas Pessoas; Início da Implementação
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Pedido do usuário:** "Autorizo o início da implementação (D-027). Quero construir o Design System do Altare em versão enxuta, proporcional a um app pessoal de duas pessoas (D-002), e não a um produto com times e governança."
- **Motivação:** o Altare é de uso pessoal, para duas pessoas (`D-002`). A especificação aprovada em `D-025` (`design-system.md` §12 e §13) previa governança de design system completo: ~45 componentes antes da primeira tela, `axe` e *snapshots* visuais no CI, script anti-*hex* e tema escuro e impressão já no Nível 0. Para dois usuários, isso é custo de manutenção sem retorno.
- **Decisão:**
  1. **Implementação autorizada.** Esta sessão cobre o Bloco 0.1 **só no necessário para o `apps/web` existir** (monorepo, pnpm, Vite + React + TypeScript, Tailwind v4, Vitest, lint e *typecheck* com Biome e `tsc`) e o Bloco 0.2 enxuto. API, banco, login e PWA ficam para outra sessão.
  2. **O Design System continua sendo o lugar único** que centraliza e padroniza os componentes: cada tela importa o que já existe (ex.: `<Button variant="primary">`) em vez de recriar estilos. O que ele contém no Nível 0:
     - **Tokens:** `tokens.json` → `tokens.css` **gerado** (nunca editado à mão), mapeado no Tailwind v4 (`@theme`). **Só o tema claro**, com nomes semânticos (`canvas`, `surface`, `ink`, `primary`…) e `data-theme="light"` no `<html>`, para o escuro entrar depois sem retrabalho. Fontes autohospedadas (Fontsource).
     - **15 primitivos** em `components/ui` (shadcn/Radix re-estilizados, nenhum "de fábrica"): `Button`, `Input`, `Textarea`, `Select`, `Checkbox`, `Badge`, `Card`, `Dialog`, `Table`, `Tabs`, `Tooltip`, `Toast`, `EmptyState`, `PageHeader` e `Money`.
     - **Casca de navegação** desktop e mobile, com o seletor de lente (`Casal` / `Minha visão`) e as 7 áreas como páginas-esqueleto com `EmptyState`.
     - **Vitrine mínima** em `/design-system`: tokens, tipografia e cada primitivo com variantes e estados.
     - **Ativos de marca** copiados de `docs/design/identidade-visual/` para `apps/web/public/brand/`, sem redesenho.
  3. **`Money` passa a ser primitivo** (`components/ui`), e não componente de domínio como em `design-system.md` §9: é um formatador puro de centavos em pt-BR, sem conhecimento do casamento.
  4. **Nenhum componente de domínio agora.** `ConsensusBadge`, `ProfileChip`, `ComparisonTable`, `NextStepCard` e os demais nascem no bloco que os usa, com as *props* puras de `design-system.md` §9.
  5. **Regras:** componentes só recebem *props* (sem regra de negócio nem chamada de API); sem *hex* em componentes, como **convenção documentada** e sem script; dados de exemplo claramente fictícios ("Espaço Exemplo"); acessibilidade verificada **manualmente** (teclado, foco, contraste), com as regras de acessibilidade do Biome ligadas no lint, que já é a ferramenta da stack.
  6. **Critério de pronto do Bloco 0.2:** a vitrine mostra tokens, tipografia e todos os primitivos listados com variantes e estados, no tema claro, em desktop e mobile; as 7 áreas são navegáveis como esqueletos; o app segue a identidade do Altare.
- **Adiado, com gatilho para retomar:**

  | Item | Gatilho |
  | :--- | :--- |
  | Tema escuro "Noite Oliva", alternador `claro / escuro / sistema` e script anti-*flash* (paleta continua aprovada no `tokens.json`) | Quando o usuário pedir |
  | Testes de regressão visual (*snapshots*) | Se houver regressões visuais recorrentes |
  | `axe` automatizado (E2E ou vitrine) | Se houver regressões de acessibilidade recorrentes ou o produto se abrir a outros casais (`D-002`) |
  | Script de CI/`pre-commit` contra *hex* fora de `tokens.css` | Se aparecer *hex* em componente mais de uma vez na revisão |
  | Impressão (`@media print` e tokens de papel) | Bloco 4.2 (Dossiê do Dia D) |
  | Demais primitivos (`Radio`, `Switch`, `SegmentedControl`, `Avatar`, `Separator`, `Sheet`/gaveta, `Popover`, `DropdownMenu`, `AlertDialog`, `Combobox`, `Tag`, `Skeleton`, `Progress`, `Accordion`, `ScrollArea`, `MoneyInput`) | Quando a primeira tela que o usa for construída |
  | Componentes de domínio (`design-system.md` §9) | No bloco que os usa |
  | Botão flutuante "+ Registrar Rápido" (`QuickAddFab`) | No primeiro bloco com algo para registrar rápido (Bloco 3.1) |
  | Menu do usuário na barra superior | Com o login (restante do Bloco 0.1) |
  | E2E de navegação com Playwright (desktop e mobile) | Com o login (restante do Bloco 0.1). Até lá, a navegação é testada com Vitest e Testing Library |

- **O que ficou rejeitado:**
  - Manter o escopo integral do Bloco 0.2 (~45 componentes, `axe` e *snapshots* visuais no CI, script anti-*hex* no CI, tema escuro e impressão no Nível 0).
  - Eliminar o Design System e usar shadcn "de fábrica": perde a identidade e a consistência.
  - Figma, Storybook e pacote npm privado (`D-020`; a distribuição é dentro do repositório).
  - `eslint-plugin-jsx-a11y` (citado num rascunho anterior desta decisão): a stack usa Biome, que já traz regras de acessibilidade.
- **Inalterado:** identidade, paleta clara e escura, tipografia, tokens e o inventário de componentes **como especificação de referência** (`design-system.md` §8 e §9). Mudou só **quando** cada coisa é construída e **quanto** de verificação a acompanha.
- **Aprovado (2026-10-27):** o Passo 0 (registro desta decisão e das docs) e o **plano das etapas 0, (a) a (e)**, com "Ok" do usuário. **Implementação pausada** a pedido do usuário, para retomar em outro dia, a partir da **Etapa 0** (base do `apps/web`). Nenhum código foi gerado até aqui.

---

## D-029 — Definição Detalhada de Features, Área por Área; Revisão do Escopo do Bloco 1.1
- **Data:** 2026-10-27
- **Fase:** Pós-Congelamento (Detalhamento de Produto, em paralelo ao Passo 0 de `D-028`)
- **Pedido do usuário:** "Eu quero definir detalhadamente quais features o projeto terá." Respostas: **revisar o escopo** (adicionar, cortar ou mover features, e não só detalhar), **um arquivo por área** e **ordem da pirâmide** do roadmap.
- **Decisão:**
  1. **Formato:** o detalhamento vive em `docs/product/features/`, **um arquivo por área** (as 7 áreas de `experience.md` §3.1). Cada feature tem ID (`F-<ÁREA>-xx`), campos, regras, estados e critérios de aceite, e indica o bloco do roadmap. Cada feature só é considerada definitiva quando o usuário aprova o arquivo da área.
  2. **Ordem:** a da pirâmide (`roadmap.md`). Primeira área em detalhamento: **Planejamento & Caminhos, Bloco 1.1** (`features/planejamento-e-caminhos.md`).
  3. **Itens adicionados à v1 no Bloco 1.1** (escopo revisado em `scope.md` §1):
     - **Tipo de cerimônia** como campo das Definições Base (religiosa, civil, simbólica ou mais de uma), concretizando `D-026`.
     - **Referências e inspirações por categoria** (links e imagens), sem leitura automática de páginas.
     - **Estimativa inicial de valor por categoria** no Mapa de Escopo, lida depois pelo orçamento (coluna *Estimado*) sem cópia.
     - **Nota livre por categoria**, por perfil.
  4. **Quem muda o status conjunto de uma categoria:** **qualquer um dos dois**, com a mudança registrada no histórico com autor, data e status anterior. Confirmação conjunta foi rejeitada por atrito, dado que são duas pessoas que conversam.
  5. **Escala de prioridade individual:** três níveis (`Quero muito`, `Se couber`, `Dispenso`). A prioridade informa a conversa e não altera o status conjunto.
- **Razão:** o escopo aprovado em `D-008` a `D-011` já cobria os territórios, mas só em nível de capacidade. O detalhamento por feature permite revisar o escopo com precisão antes de construir cada bloco, e o usuário preferiu rever por área e na ordem em que o produto será construído.
- **O que ficou rejeitado:**
  - Catálogo único de features: arquivo grande demais para revisar de uma vez.
  - Só histórias de usuário, sem campos: não fecha as regras que o banco e a API precisam.
  - Aprovação conjunta para mudar o status de categoria: mais atrito sem ganho para duas pessoas.
  - Escala de prioridade igual aos quatro status do Mapa: confunde voto individual com decisão conjunta.
- **Aprovado:** `features/planejamento-e-caminhos.md` (Bloco 1.1), aprovado pelo usuário em 2026-10-27 ("Aprovo."), incluindo as escolhas feitas sem pergunta (data em três níveis, catálogo inicial, referências sem leitura automática, estimativa lida pelo orçamento).
- **Pendente:** detalhamento da próxima área na pirâmide, **Convidados (Bloco 1.2)**.

---

## D-030 — Detalhamento de Convidados (Bloco 1.2); Exportação em Excel com CSV como Opção
- **Data:** 2026-10-27
- **Fase:** Pós-Congelamento (Detalhamento de Produto)
- **Decisão (escopo revisado de `scope.md` §6, Convidados; detalhamento em `features/convidados-enxoval-e-dia-d.md`):**
  1. **Estimado Ponderado por pesos:** três percentuais editáveis por probabilidade (`Certeza`, `Provável`, `Fase 2`), **vazios até o casal definir** (nenhum peso presumido). Confirmado conta 100%. Crianças isentas e `Não irá` ficam fora da base de custo.
  2. **Campos extras do convidado:** restrição alimentar e observação; telefone/WhatsApp e e-mail; **acompanhante (+1)** como pessoa a confirmar, sem nome; **idade da criança**. No núcleo: **endereço postal** para convite impresso.
  3. **Idade da criança sugere a faixa, sem alterá-la sozinha.** Os limites de idade são definidos pelo casal e começam vazios, porque a cobrança depende de cada fornecedor.
  4. **Convite enviado por núcleo** (data e canal), com oferta, nunca automática, de mover `Rascunho` para `Convidado`.
  5. **Motivo ou anotação opcional** ao marcar `Não irá`.
  6. **Exportação da lista em Excel (`.xlsx`) como padrão e CSV como opção** (CSV com UTF-8 BOM e `;`, para o Excel pt-BR). O mesmo padrão vale para a exportação do Enxoval e da Lista de Presentes (`D-006`).
  7. **Importação de planilha não entra na v1** (permanece em v1.1+).
- **Desvio da stack (registrado, `stack.md` §3 e §12):** `stack.md` previa exportações "CSV via stdlib, sem dependência extra". Gerar `.xlsx` exige uma biblioteca; adota-se **`openpyxl`** no backend (Python, madura, só escrita). Custo: uma dependência a mais em `apps/api`; o CSV continua na stdlib. Reavaliar apenas se a manutenção pesar.
- **Razão:** o usuário usa Excel no dia a dia; CSV exige passos extras de importação e problemas de acentuação. Os pesos editáveis e vazios evitam inventar uma regra que só o casal conhece.
- **O que ficou rejeitado:**
  - Apenas CSV, como previa a stack.
  - Pesos fixos pré-definidos (ex.: 100/70/30): presumiriam uma regra do casal.
  - Mudar a faixa automaticamente pela idade: errada para fornecedores com regras diferentes.
  - Convite enviado por pessoa: mais trabalho para um ato que é por família.
  - Importação de planilha na v1: não solicitada.
- **Aprovado:** `features/convidados-enxoval-e-dia-d.md`, parte Convidados, pelo usuário em 2026-10-27 ("aprovo"), incluindo `openpyxl` e as escolhas feitas sem pergunta (Confirmado conta 100%, idade só sugere a faixa, convite oferece mover status, lente `Minha visão` mostra o meu lado mais `Comum`).
- **Pendente:** detalhamento do **Cronograma (Bloco 1.3)**.

---

## D-031 — Detalhamento do Cronograma (Bloco 1.3); Catálogo Inicial Editável, Janelas Sugeridas e Extras
- **Data:** 2026-10-27
- **Fase:** Pós-Congelamento (Detalhamento de Produto)
- **Decisão (escopo revisado de `scope.md` §2; detalhamento em `features/cronograma.md`):**
  1. **Catálogo inicial de 29 marcos** nas 5 fases, ligado às categorias do Mapa de Escopo e já com as dependências, com **nomes neutros** (`D-026`). É uma semente: depois de criado, tudo é dado do casal.
  2. **Edição total:** o casal cria, renomeia, move e exclui marcos e fases e altera dependências (o sistema impede ciclos; exclusão lógica).
  3. **Janelas sugeridas** relativas à data do casamento ("N meses ou semanas antes"), como valores iniciais **editáveis e rotulados "sugestão genérica"**. Não são dados do casamento. O prazo-alvo padrão é o fim da janela, e um prazo manual prevalece.
  4. **Extras na v1:** **tarefas avulsas** (sem fase, categoria nem dependência), **checklist de subtarefas**, **anexos e links** (reaproveitando o `FileStorage` e o padrão de `F-PLN-06`) e **calendário mensal** como segunda visão.
  5. **Estados:** `Bloqueado` e `Destravado` derivados; `Em andamento` e `Concluído` marcados pelo casal; `Atrasado` como sinalizador derivado. Marcar andamento ou conclusão em item bloqueado é permitido com confirmação, e fica registrado.
  6. **Resolução de dependência:** concluído, **arquivado** (categoria `Fica de fora`) ou **opcional** (`Talvez`) não bloqueiam.
  7. **Refinamento de `F-PLN-07` (aprovado):** categoria `Em discussão` passa a **bloquear** seus marcos com o motivo "Aguardando classificar a categoria no Mapa de Escopo", em vez de não ter efeito. Sem isso, nada ficaria bloqueado no início e o cronograma perderia o sentido. `features/planejamento-e-caminhos.md` foi ajustado.
  8. **Conclusão por decisão** (Bloco 3.2): o marco "Fechar …" será concluído automaticamente quando houver o Registro de Decisão; até lá é manual.
  9. **Só data, sem horário**, em prazos e tarefas.
- **Razão:** o escopo aprovado definia fases, dependências e modos, mas não o modelo de marcos nem a edição. Partir de um catálogo editável reduz o trabalho inicial sem impor um roteiro, e as janelas sugeridas evitam um cronograma vazio quando a data for definida.
- **O que ficou rejeitado:**
  - Cronograma vazio ou só com marcos âncora: transfere ao casal o trabalho de montar do zero.
  - Estrutura fixa: não acompanha a realidade de cada casamento.
  - Janelas vazias: o modo com data perderia valor.
  - Horário em tarefas e recorrência: não pedidos, e aproximam do Gantt que `scope.md` exclui.
  - Marco com categoria `Em discussão` sem efeito: tira o sentido do bloqueio.
- **Aprovado:** `features/cronograma.md` pelo usuário em 2026-10-27 ("Aprovo"), incluindo o refinamento de `F-PLN-07` (`Em discussão` bloqueia) e as janelas sugeridas do catálogo.
- **Pendente:** detalhamento de **Orçamento & Simulador (Bloco 2.1)**.

---

## D-032 — Detalhamento do Orçamento e do Simulador (Bloco 2.1)
- **Data:** 2026-10-27
- **Fase:** Pós-Congelamento (Detalhamento de Produto)
- **Decisão (escopo revisado de `scope.md` §3; detalhamento em `features/orcamento-e-simulador.md`):**
  1. **Base de convidados por cenário**, com quatro opções: Estimado Ponderado, Total Nominal sem isentos, só Certeza e Confirmados, ou número manual. **Isentos e `Não irá` ficam sempre fora da base de custo.**
  2. **Arredondamento para cima** da quantidade usada em custos por pessoa (`quantidade = ⌈adultos + crianças pagantes × fator⌉`), de modo que a contagem fracionária nunca subestima o custo. Resolve o ponto pendente de `F-CNV-06`.
  3. **Fator da criança pagante por linha** (percentual, vazio conta 100%), porque cada fornecedor cobra de um jeito.
  4. **Linhas derivadas do Mapa de Escopo** (derivar, não duplicar): `Entra` sempre incluída; `Talvez` ligada ou desligada por cenário (nasce desligada); `Em discussão` fora dos totais; `Fica de fora` oculta, com valores guardados para uma eventual reabertura.
  5. **Estimado:** em linhas `Fixo`, lê a estimativa da categoria (`F-PLN-05`) e pode ser **sobrescrito por cenário** (com "voltar ao valor da categoria"); em linhas `Por pessoa`, é preço por pessoa × quantidade, e a estimativa da categoria só aparece como referência. Vazio não é zero e é sinalizado. Resolve o ponto pendente de `F-PLN-05`.
  6. **Contratado e Realizado são fatos do casamento, não do cenário:** só aparecem no cenário **ativo**, derivados de contratos e parcelas (Blocos 3.2 e 3.3), com "—" até lá. Cenários em simulação têm só Planejado e Estimado.
  7. **Cenário ativo:** o primeiro criado vira ativo; no máximo um; o ativo não pode ser excluído enquanto houver outros; promover pede confirmação e é registrado.
  8. **Extras na v1:** **reserva para imprevistos** (percentual por cenário, vazio até definir, mostrada à parte), **indicador visual de uso do teto** por categoria (sálvia dentro, argila acima, sempre com ícone e texto) e **exportação em Excel com CSV como opção** (padrão de `D-030`).
  9. **Comparativo** de 2 a 4 cenários, somente leitura, com seleção na URL e selo "Menor total com reserva" apenas entre cenários completos.
- **Razão:** o escopo aprovado definia as quatro colunas e o simulador, mas não onde moram os fatos financeiros, como se contam as pessoas nem como se arredonda. Separar fatos (contratado e pago) de hipóteses (cenários) evita que simular altere o que realmente foi gasto, e as sobrescritas explícitas mantêm a regra "derivar, não duplicar".
- **O que ficou rejeitado:**
  - Número manual como única base de convidados: desliga o orçamento da lista.
  - Arredondamento exato da contagem ponderada: pode subestimar o custo.
  - Criança pagante sempre como pessoa inteira: não representa os fornecedores que cobram metade.
  - Contratado e Realizado por cenário: duplicaria fatos e confundiria simulação com realidade.
  - Linhas copiadas para cada cenário: ficariam desatualizadas quando o escopo mudasse.
  - Nota por linha de categoria: não solicitada.
- **Aprovado:** `features/orcamento-e-simulador.md` pelo usuário em 2026-10-27 ("Aprovo"), incluindo as escolhas feitas sem pergunta (Contratado e Realizado só no ativo, primeiro cenário vira ativo, `Talvez` nasce desligada, comparativo somente leitura).
- **Pendente:** detalhamento de **Possibilidades (Bloco 2.2)**.

---

## D-033 — Detalhamento de Possibilidades Macro, Avaliação Dupla e Decisão (Bloco 2.2)
- **Data:** 2026-10-27
- **Fase:** Pós-Congelamento (Detalhamento de Produto)
- **Decisão (escopo revisado de `scope.md` §5; detalhamento em `features/possibilidades-e-decisoes.md`):**
  1. **Modelo compartilhado** entre os Blocos 2.2 e 3.2: `Possibilidade` (tipo `Macro` agora, `Proposta` depois), `Avaliação` (um perfil × uma possibilidade), **selo de consenso derivado** e `Decisão registrada`.
  2. **Os Caminhos Macro aparecem na aba "Definições Base & Caminhos Macro" da área Planejamento** (`experience.md` §3.1); a área Possibilidades & Decisões recebe as propostas no Bloco 3.2.
  3. **Custo do caminho derivado do cenário vinculado** (um cenário por caminho, no máximo), sem digitação. Sem vínculo, não há valor monetário; há ações para vincular ou criar um cenário.
  4. **Registro de decisão com efeitos sugeridos e confirmados campo a campo:** preencher Formato, Região e Porte nas Definições Base como `Definido` (marcados só os campos ainda `Em definição`); **oferecer** promover o cenário vinculado a Ativo (desmarcado por padrão); concluir o marco "Escolher o caminho macro" automaticamente.
  5. **Selo de consenso:** `Consenso Favorito` quando os dois avaliam `Favorito` ou `Gostei`; `Ambos descartariam` quando os dois avaliam `Descartaria`; `Aguardando avaliação` quando falta uma; qualquer outra combinação é `Conversar juntos`. **A nota de 1 a 5 só informa** e não entra na regra. A classificação é obrigatória; nota e comentário são opcionais.
  6. **Decisão reversível:** reabrir volta todos a `Em análise`, mantém os motivos no histórico e reabre o marco; valores já aplicados não são revertidos sozinhos. Motivo da escolha e de cada descarte são obrigatórios.
  7. **Campos do caminho:** nome, descrição, formato, região, porte, prós e contras em listas, **logística como texto livre** e **referências** (links e imagens, como `F-PLN-06`). Sem campos estruturados de logística, época nem anexos (a seleção do usuário combinou "Nenhum" e "Referências"; interpretada como só referências).
  8. **Comparação** de 2 a 5 caminhos, com seleção na URL.
- **Ajuste em arquivo aprovado:** `features/cronograma.md` (`F-CRN-03`, regra 6) passa a prever a conclusão automática do marco "Escolher o caminho macro" pela decisão macro do Bloco 2.2, e não só dos marcos "Fechar …" pelo Bloco 3.2.
- **Razão:** o escopo definia os dois níveis de possibilidades, mas não como o consenso é calculado nem o que a decisão altera. Derivar custo e selo evita duplicar dado, e os efeitos confirmados mantêm o controle com o casal sem remover o trabalho de repetir a digitação.
- **O que ficou rejeitado:**
  - Registrar a decisão sem nenhum efeito (obrigaria a repetir tudo à mão).
  - Aplicar os efeitos sem confirmação (poderia sobrescrever Definições Base já decididas).
  - Consenso só com `Favorito` dos dois: rigidez que esconderia alinhamentos positivos.
  - Nota 1 a 5 na regra do selo: mistura duas escalas.
  - Votação cega: contraria `D-021`.
  - Custo digitado no caminho: duplicaria o cenário.
- **Aprovado:** `features/possibilidades-e-decisoes.md` pelo usuário em 2026-10-27 ("Aprovo."), incluindo a interpretação de "Nenhum" + "Referências" como só referências, o ajuste em `F-CRN-03` e as escolhas feitas sem pergunta (promover cenário desmarcado por padrão, avaliação editável após a decisão, um cenário por caminho).
- **Pendente:** detalhamento de **Contatos (Bloco 3.1)**.

---

## D-034 — Detalhamento de Contatos, Visitas e Busca Global (Bloco 3.1)
- **Data:** 2026-10-27
- **Fase:** Pós-Congelamento (Detalhamento de Produto)
- **Decisão (escopo revisado de `scope.md` §4; detalhamento em `features/contatos.md`):**
  1. **Dois tipos de contato:** `Fornecedor` (com funil, Próximo Passo, interações e visitas) e `Pessoa` (indicação, familiar, contato do local; sem funil, Próximo Passo, interações nem visitas). Ambos aceitam arquivos e links e aparecem na mesma lista, com filtro por tipo.
  2. **Funil de 6 estados**, confirmado: `Para contatar` → `Aguardando orçamento` → `Orçamento recebido` → `Em negociação / Visita` → `Contratado` · `Descartado`. Transição livre entre quaisquer estados. Cada mudança gera entrada do sistema na linha do tempo. **Motivo do descarte opcional**; descartar remove o Próximo Passo e reativar é permitido.
  3. **`Contratado` manual até o Bloco 3.2** e **derivado da decisão por categoria** depois disso. O caso de fornecedor com várias categorias fica para o Bloco 3.2.
  4. **Próximo Passo Único** (ação, data-alvo, responsável): concluir cria uma interação e pede o próximo passo. `Atrasado` é derivado.
  5. **Visitas agendadas com data e hora** (estados `Agendada`, `Realizada`, `Cancelada`), aparecendo no calendário do Cronograma como itens somente leitura. **Marcar `Realizada` cria a interação `Visita`.** A hora é exclusiva da visita: marcos e tarefas continuam só com data (`D-031`).
  6. **Aviso de duplicidade** por telefone, e-mail e Instagram normalizados, **sem bloquear** ("Salvar mesmo assim"). Sem comparação por nome.
  7. **Busca global do app** no cabeçalho: contatos, arquivos (por nome ou título), categorias, convidados, marcos, caminhos macro e cenários, e cresce com as áreas seguintes. Busca por trecho, sem acento nem caixa, sem busca no conteúdo de PDFs, ignora a lente.
  8. **Captura rápida:** nome e categoria bastam para criar um fornecedor. **"Quem atende"** é um campo de texto livre.
  9. **Lista** em tabela (desktop) e cartões (celular), visão **Por status** sem arrastar, filtros na URL e ordenação com o Próximo Passo atrasado no topo.
- **Ajuste em arquivo aprovado:** `features/cronograma.md` (`F-CRN-10` e "Fora desta área") passa a prever as visitas a fornecedores no calendário, como a única exceção ao "só data".
- **Ajuste em `architecture.md`:** o estado do funil de `Contact` deixa de ser "a confirmar".
- **Razão:** o escopo definia os campos e o funil, mas deixava aberto o conjunto de estados, o que acontece ao concluir um passo e como a visita (que tem hora) convive com um calendário só de datas. A busca global estava registrada como lacuna transversal e o Bloco 3.1 é o primeiro com volume de itens que a justifique.
- **O que ficou rejeitado:**
  - Funil de 4 estados e funil editável: o de 6 do escopo já cobre a conversa real, e a edição de etapas aumenta a configuração sem ganho para duas pessoas.
  - Várias pessoas de contato por fornecedor: um campo de texto livre atende ao caso sem uma segunda entidade.
  - Indicador de "parado há N dias": o Próximo Passo e o filtro de atrasados cobrem o caso.
  - Bloquear contatos duplicados: há fornecedores legítimos com o mesmo telefone.
  - Motivo de descarte obrigatório: o contato é um registro de conversa, não uma decisão entre alternativas (que já exige motivo em `D-033`).
  - Arrastar cartões entre colunas: pior em teclado e leitor de tela, e o menu resolve.
  - Horário nas tarefas do cronograma: `D-031` mantém só data.
- **Aprovado:** `features/contatos.md` pelo usuário em 2026-10-27 ("Aprovo, prossiga."), incluindo o ajuste em `F-CRN-10` e em `architecture.md`.
- **Pendente:** detalhamento de **Possibilidades por Categoria (Bloco 3.2)**.

---

## D-035 — Detalhamento de Propostas por Categoria, Custo Comparável e Decisão (Bloco 3.2)
- **Data:** 2026-10-27
- **Fase:** Pós-Congelamento (Detalhamento de Produto)
- **Decisão (escopo revisado de `scope.md` §5; detalhamento em `features/propostas-por-categoria.md`):**
  1. **Proposta** é um pacote de um fornecedor para uma categoria, tipo `Proposta` do modelo compartilhado de `D-033`. Um fornecedor pode ter vários pacotes, e há "duplicar como novo pacote". Reaproveita **avaliação dupla, selo de consenso e registro de decisão** de `F-POS-03` a `F-POS-05`.
  2. **Preço base em dois modos:** Valor total ou Preço por pessoa. No modo por pessoa, a quantidade é a do **cenário ativo** (`F-ORC-03`, arredondada para cima), lida sem cópia. A proposta pode ter fator próprio da criança pagante; vazio lê o da linha da categoria. Sem base, o total é "—" e nenhum número é presumido.
  3. **Normalizador de Custo Comparável:** **Custo Total Real Comparável** = preço base + extras `Necessário`. Cada extra é `Fixo` ou `Por pessoa`, e os `Opcional` aparecem à parte. Exibe também o **custo por convidado equivalente**.
  4. **Condições de pagamento em texto livre.** As parcelas só nascem no contrato (Bloco 3.3).
  5. **Estimado não é alimentado por propostas.** O cenário ativo mostra só uma **faixa de referência** (menor a maior custo comparável em análise). Cada proposta exibe a **situação frente ao teto** da categoria (`F-ORC-07`).
  6. **Quadro lado a lado** de 2 a 5 propostas da mesma categoria, **sem eleger a "melhor"**, com painel lateral de PDF no desktop e cartões com abas no celular.
  7. **Uma decisão por categoria** (sem várias vencedoras). Pode-se decidir com **uma única proposta**. Motivos obrigatórios para a escolha e para cada descarte, com avisos de avaliação faltando, acima do teto e total sem valor.
  8. **Efeitos da decisão:** **Contratado** derivado no Orçamento Ativo (recalculado até haver contrato; o contrato do Bloco 3.3 prevalecerá); marco "Fechar …" concluído; fornecedor `Contratado` derivado (basta uma proposta escolhida, com chips por categoria); oferta **desmarcada** de descartar os fornecedores sem outra proposta ativa. O Estimado fica intacto.
  9. **Reabrir a decisão:** descartadas pela decisão voltam a `Em análise`, marco reaberto, Contratado volta a "—", fornecedor volta ao status anterior e motivos ficam no histórico.
  10. **Coerência:** categoria com decisão não vai para `Fica de fora` nem `Em discussão`, e não recebe propostas novas sem reabrir. Um fornecedor com propostas não é excluído antes disso. Descarte individual de proposta com motivo obrigatório.
  11. **Transição:** na entrega do bloco, fornecedores marcados à mão como `Contratado` voltam a `Em negociação / Visita`, com nota na linha do tempo.
- **Ajustes em arquivos aprovados:** `orcamento-e-simulador.md` (Estimado não alimentado por propostas, Contratado derivado de `F-PRP-08`, pontos a validar); `contatos.md` (`F-CTT-01`, `F-CTT-03`, `F-CTT-07`, pontos de atenção; nova aba Propostas); `planejamento-e-caminhos.md` (`F-PLN-07`, regra 3).
- **Razão:** o escopo previa o Normalizador e a decisão por categoria, mas deixava abertas a quantidade dos custos por pessoa, a relação com o Estimado, o efeito sobre o fornecedor e o Contratado, e a reabertura. Derivar totais e Contratado evita duplicar dado e mantém o controle com o casal.
- **O que ficou rejeitado:**
  - Alimentar o Estimado com as propostas (mistura valor planejado com cotação e sobrescreveria um valor do casal).
  - Botão "usar como Estimado" por proposta: duas fontes para o mesmo número.
  - Várias propostas vencedoras por categoria: categorias separadas já resolvem e mantêm o Contratado simples.
  - Condições de pagamento estruturadas na proposta: duplicariam as parcelas do contrato (Bloco 3.3).
  - Destacar a "melhor" proposta automaticamente: tiraria a decisão do casal.
  - Validade da proposta e histórico de revisões de preço: não solicitados.
  - Aplicar o descarte de fornecedores sem confirmação: o fornecedor pode ter outras categorias ou voltar à conversa.
- **Aprovado:** `features/propostas-por-categoria.md` pelo usuário em 2026-10-27 ("Aprovo"), incluindo os ajustes em `orcamento-e-simulador.md`, `contatos.md` e `planejamento-e-caminhos.md`.
- **Pendente:** detalhamento de **Contratos & Parcelas (Bloco 3.3)**.

---

## D-036 — Detalhamento de Contratos, Parcelas e Fluxo de Pagamentos (Bloco 3.3)
- **Data:** 2026-10-27
- **Fase:** Pós-Congelamento (Detalhamento de Produto)
- **Decisão (escopo revisado de `scope.md` §3; detalhamento em `features/contratos-e-parcelas.md`):**
  1. **Contrato nasce de duas formas:** **por decisão** (criado automaticamente com a decisão da categoria, `Aguardando assinatura`) e **direto** (sem proposta, para alianças, roupas e compras em loja; fornecedor opcional, com "favorecido" em texto livre quando não há contato).
  2. **Contratado conta desde a criação** (`Aguardando assinatura` e `Assinado` somam; `Cancelado` não). É a **soma** dos contratos da categoria e substitui o Contratado derivado da proposta de `D-035`.
  3. **Valor fechado é fato:** copiado **uma vez** do custo comparável e editável; a tela mostra "difere do comparável em R$ X". Sem registro de aditivos e sem campo de política de cancelamento.
  4. **Cancelar contrato por decisão é reabrir a decisão** (ação única). Contrato com parcela `Pago` não pode ser cancelado nem excluído. Reembolsos e multas ficam fora da v1.
  5. **Dados do Dia D no contrato** (responsável no dia, itens contratados copiados da proposta, combinados críticos e PDF assinado). O Dossiê só lê esses campos. **Pendências do Dossiê** são derivadas e não bloqueiam.
  6. **Parcela:** descrição, vencimento (**data** ou **"no dia do evento"**), valor previsto, meio, responsável. Ao pagar: data, **valor pago (pode diferir do previsto)**, quem pagou (`Noivo`, `Noiva` ou `Conta Conjunta`) e comprovante opcional. **`Atrasada` é derivada.**
  7. **Assistente de plano de pagamento** (sinal, parcelas iguais e quitação), com pré-visualização, centavos residuais na **última** parcela e ajuste manual depois. Gerar de novo só substitui as `Pendente`.
  8. **Fluxo de Pagamentos** (aba 3 do Orçamento): lista por mês e calendário, filtros e lente pelo responsável da parcela, marcar `Pago` direto da lista, **exportação em Excel com CSV como opção**. Projeção de poupança e alertas ficam em v1.1+.
  9. **Orçamento Ativo:** **Realizado** = soma dos valores efetivamente pagos; indicador derivado **"A pagar"** (Contratado − Realizado); o **saldo da categoria não muda**. Contratado e Realizado de categoria `Talvez` com linha desligada aparecem e somam.
  10. **Lista de Contratos** como aba da área Possibilidades & Decisões, com selo derivado `Quitado` e progresso de pagamento.
  11. **Contrato direto com fornecedor** o marca `Contratado` (derivado) e conclui o marco "Fechar …" da categoria.
- **Ajustes em arquivos aprovados:** `propostas-por-categoria.md` (`F-PRP-08`: decisão cria o contrato, reabrir cancela o contrato e é recusado com parcela paga; pontos de atenção resolvidos); `orcamento-e-simulador.md` (`F-ORC-06`, fora de escopo e pontos a validar); `contatos.md` (`F-CTT-01`, `F-CTT-03`); `planejamento-e-caminhos.md` (`F-PLN-07`, regra 3); `cronograma.md` (`F-CRN-03`, regra 6); `experience.md` (aba Contratos); `architecture.md` (estados de `Contract` e `PaymentInstallment`).
- **Razão:** o escopo previa parcelas e a coluna Realizado, mas deixava abertos quando o contrato existe, quando conta no orçamento, como o pagamento real difere do previsto e como cobrir o que não passa por cotação. Tratar o contrato como fato e derivar Contratado, Realizado e "A pagar" evita duplicar dado.
- **O que ficou rejeitado:**
  - Exigir decisão para todo contrato: não cobriria compras sem fornecedor ou cotação.
  - Contratado só depois da assinatura: esconderia compromissos já assumidos do orçamento.
  - Valor pago sempre igual ao previsto: obrigaria a falsear juros, descontos e multas.
  - Gerar parcelas só à mão: lento para contratos de muitas parcelas.
  - Campo de política de cancelamento e registro de aditivos: não solicitados.
  - Bloquear o contrato quando as parcelas não somam o valor: a vida real tem acertos futuros, então só avisa.
  - Alterar o saldo da categoria com o que já foi pago: pago não muda quanto cabe no teto.
  - Reembolso e multa na v1: o casal ajusta o valor do contrato ao que foi efetivamente devido.
- **Aprovado:** `features/contratos-e-parcelas.md` pelo usuário em 2026-10-27 ("aprovo"), incluindo os ajustes nos arquivos já aprovados.
- **Pendente:** detalhamento de **Enxoval e Lista de Presentes (Bloco 4.1)**.

---

## D-037 — Detalhamento de Enxoval e Lista de Presentes (Bloco 4.1)
- **Data:** 2026-10-27
- **Fase:** Pós-Congelamento (Detalhamento de Produto)
- **Decisão (escopo revisado de `scope.md` §6, Enxoval; detalhamento na parte Enxoval de `features/convidados-enxoval-e-dia-d.md`):**
  1. **Grupos** (cômodos e categorias) com **sugestões iniciais editáveis** (Cozinha, Quarto, Sala, Banheiro, Área de serviço, Eletros e eletrônicos, Lua de mel), arquiváveis, nunca excluídos com itens.
  2. **Item (por unidade) e Cota (valor em dinheiro)** na mesma lista. Item com quantidade desejada, valor unitário opcional, link, loja, **imagem opcional** e prioridade `Essencial`, `Desejável` ou `Se sobrar`. Cota com valor-alvo e destino sempre `Pedir na lista`.
  3. **Quantidade e recebimentos:** cada presente ou compra é um **registro** (origem, quantidade, data, valor opcional, quem presenteou). Cota recebe **contribuições** em dinheiro. **Excedentes** são permitidos e mostrados como "a mais".
  4. **Status derivado:** `Precisamos` · `Na lista de presentes` · `Em andamento` · `Já ganhamos` · `Já compramos` · `Completo` (misto). Totais derivados: estimado da lista, ganho, gasto do casal, falta conseguir e progresso. Valor vazio nunca é zero.
  5. **Quem presenteou:** convidado ou núcleo da lista (guardando o nome no momento, sem alterar a lista de convidados) ou texto livre.
  6. **O enxoval é separado do Orçamento do casamento:** os totais da subárea **não alimentam** orçamento nem cenários. O que se paga a um fornecedor do casamento sem proposta continua no **Contrato direto** (`D-036`).
  7. **Exportação para site externo** em **Excel (padrão) e CSV (opção)**, sobre os filtros, sem dados de convidados, com a visão pronta "Para a lista". Depois do download, o Altare **oferece** (desmarcado) marcar os itens exportados como "Na lista".
  8. **Lista formatada para convidados** em **texto limpo para copiar e colar** (estilo WhatsApp) ou baixar em `.txt`, com mensagem inicial opcional e vazia, **valores desligados por padrão** e links ligados. Não inclui itens completos nem dados de quem presenteou.
- **Razão:** o escopo previa os campos e a exportação, mas deixava abertos o que acontece com quantidades maiores que 1, o encaixe das cotas de lua de mel, a relação com o Orçamento e o formato da lista para convidados. Derivar status e totais dos registros evita um status editável que diverge da realidade.
- **O que ficou rejeitado:**
  - Item unitário com status único e campo "quem presenteou": não representa 12 pratos nem cotas com várias contribuições.
  - Integrar o enxoval ao Orçamento do casamento por uma categoria "Enxoval": mistura a casa nova com o evento e distorce teto, cenários e comparações.
  - Lista formatada em PDF ou página imprimível: a impressão depende do Bloco 4.2 (`design-system.md` §13).
  - "Agradecimento enviado" por presente e visão "quem deu o quê": não solicitados.
  - Leitura automática de preço e foto a partir do link: sem *scraping*.
  - Escrever uma mensagem padrão na lista aos convidados: o texto é do casal.
  - Responsável por item e lente por perfil: não solicitados.
- **Aprovado:** parte Enxoval de `features/convidados-enxoval-e-dia-d.md` pelo usuário em 2026-10-27 ("aprovo"), incluindo o rótulo derivado `Completo` e o ajuste em `contratos-e-parcelas.md`.
- **Pendente:** detalhamento de **Centro de Comando e Dossiê do Dia D (Bloco 4.2)**.

---

## D-038 — Detalhamento do Centro de Comando, Dossiê do Dia D e Exportação dos Dados (Bloco 4.2)
- **Data:** 2026-10-27
- **Fase:** Pós-Congelamento (Detalhamento de Produto)
- **Decisão (detalhamento em `features/centro-de-comando.md` e na parte Dossiê de `features/convidados-enxoval-e-dia-d.md`):**
  1. **Centro de Comando como visão derivada, sem dados próprios:** contagem regressiva e Definições Base, **"Atenção agora"**, meus próximos passos e destravados, agenda de 7 dias, termômetro do orçamento e convidados. A lente filtra os cartões pessoais.
  2. **"Atenção agora" por 9 regras fixas e determinísticas** (parcela atrasada, passo e marco atrasados, avaliação que falta a mim, `Conversar juntos`, visita passada, categoria essencial sem teto, contrato com saldo a programar, contrato com pendências do Dossiê). **Sem IA e sem notificação ativa:** é uma lista na tela. Mostra 5 com "ver todas".
  3. **"+ Registrar Rápido":** botão no celular e menu "Novo" no desktop, com ações que **reaproveitam os formulários das áreas**, no máximo 2 toques para abrir cada formulário. Nasce no Bloco 3.1 (`D-028`) e ganha ações conforme os blocos chegam.
  4. **Exportar todos os dados do casal:** `.zip` com `dados.json` (versionado), `arquivos/` e `LEIA-ME.txt`, gerado sob demanda, sem senhas nem sessões, com a data da última exportação. **Importação de volta fica para v1.1+.** **Backup automático não entra como funcionalidade da v1:** é requisito de implantação a tratar com a hospedagem (`D-019`), e o risco enquanto isso fica registrado.
  5. **Dossiê como visão viva, sem digitar de novo:** quadro do evento, fornecedores contratados (por contrato, com responsável no dia, itens, combinados e PDF), pagamentos (a pagar no dia e resumo das demais), convidados (contagens e restrições alimentares, sem contatos) e itens físicos.
  6. **Dados novos do Dossiê:** **Local do evento** (texto), **horários-chave** (lista curta de até 12, não é o roteiro minuto a minuto), **checklist de itens físicos** (lista começa vazia) e **versões entregues**.
  7. **Versões entregues:** cópia datada, imutável, com "o que mudou desde a última entrega" (antes → depois).
  8. **Impressão pelo navegador** (A4 retrato, tokens de papel, sem controles, fichas sem quebra), **sem PDF gerado no servidor** e sem dependência nova. O valor dos contratos vem **desligado** por padrão no Dossiê.
  9. **Pendências do Dossiê** só em tela, não bloqueiam e não saem na impressão.
- **Ajustes em arquivos aprovados:** `architecture.md` (o módulo `dossier` deixa de ser "somente consultas" e ganha escrita pequena); `design-system.md` §13 (gatilho de impressão atingido); `convidados-enxoval-e-dia-d.md` (cabeçalho e fora de escopo).
- **Razão:** o escopo previa a Home e o Dossiê como consolidações, mas deixava em aberto onde ficam o local e os horários do evento, o checklist de itens físicos (previsto só na experiência), a forma de saída do documento e a proteção dos dados do casal, que não aparecia em nenhum documento. Manter tudo derivado evita um segundo cadastro.
- **O que ficou rejeitado:**
  - Notificações ativas (in-app, push e WhatsApp) na v1: `D-013` as mantém em v1.1+.
  - Roteiro minuto a minuto agora: v1.1+.
  - PDF gerado no servidor: exigiria biblioteca nova sem ganho proporcional a um documento para duas pessoas.
  - Backup automático como tela do produto: é infraestrutura, tratada na implantação.
  - Observações gerais livres no Dossiê: os combinados por contrato cobrem o caso.
  - Dossiê editável como documento próprio: duplicaria dados e ficaria desatualizado.
  - Mostrar contatos de convidados no Dossiê: dados de terceiros desnecessários ao hand-off.
  - Home configurável (ordem e esconder cartões): não solicitada.
- **Aprovado:** `features/centro-de-comando.md` e a parte Dossiê de `features/convidados-enxoval-e-dia-d.md` pelo usuário em 2026-10-27 ("aprovo"). **O detalhamento da v1 manual (Níveis 1 a 4) está concluído.**
- **Escolhido pelo usuário:** retomar a implementação do Nível 0 (`D-028`). O Passo 0 e o plano foram aprovados e a sessão foi **pausada** antes do primeiro código.
- **Pendente (sem urgência):** detalhar a camada de IA do Nível 5 (v1.1+) e planejar implantação, hospedagem e backup automático.

---

## D-039 — Skills de Projeto do Altare, Precedência sobre as Instruções Globais e `CLAUDE.md` por Módulo
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0 (ferramental de agentes)
- **Pedido do usuário:** criar um conjunto de skills de projeto em `.claude/skills/`, uma por área de trabalho, para um projeto **pessoal e não Dharma**, sem aplicar padrões da Dharma.
- **Decisão:**
  1. **23 skills** em `.claude/skills/altare-<nome>/SKILL.md`, em português, nomes em kebab-case com prefixo `altare-`, indexadas em `AGENTS.md` §5. Áreas: arquitetura, backend-api, banco-de-dados, agente-dados, engenharia-de-ia, seguranca-privacidade, escrita-de-codigo, code-review, testes-qa, devops, monorepo, frontend, design, ui-ux, acessibilidade, conteudo-copy, produto, analytics-metricas, gtm-pricing, git-fluxo, commit, pull-request e docs-vivas.
  2. **Fonte de verdade inalterada:** `AGENTS.md` e `docs/`. As skills **apontam** para os docs e não os copiam; havendo conflito, vale o doc e a skill é corrigida.
  3. **Precedência:** neste repositório, as skills `altare-*` **substituem** as instruções globais do usuário baseadas em padrões da Dharma (`dharma-standards`, `dharma-sdd`, `dharma-tdd`, `dharma-commit`, `dharma-commit-push-pr`, `dharma-create-pr` e `dharma-code-review*`). O Altare é projeto pessoal.
  4. **`CLAUDE.md` por módulo:** cada módulo da arquitetura (`architecture.md` §4) tem um `CLAUDE.md` curto na própria pasta (propósito, superfície pública, invariantes, dependências permitidas, links de feature e como testar), que aponta para `AGENTS.md` e `docs/` sem repetir regras gerais. **Módulo novo nasce com `CLAUDE.md`.** Vale para os módulos do **backend** (`architecture.md` §4); a pasta da *feature* correspondente no `apps/web` é apenas linkada nele. O modelo fica em `altare-docs-vivas`; os arquivos são criados quando cada módulo for criado.
  5. **Acessibilidade vira skill própria**, porque `D-028` trocou o `axe` automatizado por verificação manual: o checklist manual passa a ser o único gate e precisa de um dono único.
  6. **`altare-gtm-pricing` é dormente:** só se aplica se o usuário explorar a hipótese de outros casais (`D-002`).
  7. **Decisões ficam em `decisions.md`** (formato `D-xxx`); não há pasta de ADRs separada.
- **Razão:** o `CLAUDE.md` global manda aplicar padrões de um projeto de empresa, o que não vale para um app pessoal de duas pessoas. Sem skills próprias, cada sessão redescobre as convenções que os docs já decidiram.
- **O que ficou rejeitado:**
  - Regras operacionais no `CLAUDE.md` raiz: ele deve apenas apontar para `AGENTS.md`.
  - Uma skill única e grande: dilui o gatilho e o contexto carregado.
  - Acessibilidade diluída em Frontend, UI/UX, Design e Code review: o mesmo checklist apareceria em quatro lugares.
  - Pasta de ADRs: `decisions.md` já cumpre o papel.
  - Ciclo de avaliações quantitativas das skills: custo desproporcional para 23 skills de uso pessoal. Cada `description` foi otimizada para disparo, sem *evals*.

---

## D-040 — Monorepo Sem Git Submodules
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Decisão:**
  1. `apps/api` (Python) e `apps/web` (React) vivem **no mesmo repositório**, como já previsto em `stack.md` §8. **Git submodules não são usados.**
  2. Uma mudança que atravessa API e web (rota nova e tela que a usa) é **um único PR**, com commits atômicos por intenção, validado pela CI inteira.
  3. A única ponte entre os apps é o **contrato OpenAPI**: `apps/web` não importa código de `apps/api` nem o contrário. Os tipos TypeScript são gerados do OpenAPI e a CI falha se houver *drift* (`stack.md` §7).
  4. **Pacotes compartilhados** (`packages/`) só nascem quando houver um segundo consumidor real; hoje não há nenhum.
  5. Tarefas e scripts na raiz (`Makefile`, `pnpm` workspace e `uv`) e CI com *path filters*, detalhados em `altare-monorepo`.
- **Razão:** com submodules, uma mudança de contrato viraria dois PRs em repositórios diferentes, sem commit atômico e com a CI de um lado sem enxergar o outro. Para dois usuários e uma só pessoa desenvolvendo, o custo não se paga.
- **O que ficou rejeitado:**
  - Git submodules para `apps/api` e `apps/web`: quebra a atomicidade entre API e web.
  - Dois repositórios independentes: mesmo problema, com versionamento de contrato à parte.
  - Pasta `packages/` criada de antemão "para o futuro": abstração especulativa.

---

## D-041 — Fluxo de Branches: `main ← develop ← feature`, com Hotfix e Release
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Decisão:**
  1. **`main`** guarda só o que foi concluído e validado (cada merge nela é uma *release* e leva *tag*). **`develop`** é a linha de integração. Todo trabalho sai da `develop` em uma branch de trabalho e volta por PR.
  2. **Nomes:** `<tipo>/<assunto-curto>` em minúsculas e kebab-case, com o tipo igual ao de commit (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`). Exemplo: `feat/orcamento-simulador`, `docs/detalhamento-features-v1`.
  3. **Hotfix:** `hotfix/<assunto>` sai da **`main`**, volta para a `main` (nova *tag*) **e também para a `develop`**, para a correção não se perder.
  4. **Release:** abre-se um PR `develop → main` quando um **bloco ou nível do roadmap** é concluído e passa em todos os gates de `altare-testes-qa`; a *tag* segue `vMAJOR.MINOR.PATCH`. Não há branch `release/*`: com uma pessoa desenvolvendo, a `develop` já é a candidata a release.
  5. **Estratégia de merge:** *merge commit* (sem *squash* e sem *rebase and merge*), para **preservar os commits atômicos** e o histórico por intenção. Antes do PR, a branch de trabalho se atualiza com a `develop` por *rebase* local (nunca em branch já compartilhada).
  6. **Proteção** de `main` e `develop`: sem *push* direto, PR obrigatório e CI verde. Aplicada no GitHub em 2026-10-27, a pedido do usuário: PR obrigatório (0 aprovações, porque uma pessoa não aprova o próprio PR), vale também para administradores, sem *force push* e sem exclusão da branch. **Falta exigir os *status checks* da CI**, que entram quando o pipeline existir (`altare-devops`).
  7. **Transição (concluída em 2026-10-27):** o PR #1 (`docs/detalhamento-features-v1`) foi integrado na `main` e a `develop` foi criada a partir dela. O repositório é privado; o GitHub aceitou a proteção no plano atual.
  8. Detalhes em `altare-git-fluxo`, `altare-commit` e `altare-pull-request`.
- **Razão:** separa o que está integrado do que está validado, e o merge sem *squash* mantém a promessa de commits atômicos feitos com `altare-commit`.
- **O que ficou rejeitado:**
  - *Trunk-based* só com `main`: o usuário pediu uma linha de integração separada.
  - *Squash merge*: apaga os commits atômicos.
  - Branch `release/*` fixa: cerimônia sem ganho para um desenvolvedor.
  - Git Flow completo com `support/*`: sem várias versões em produção, não há para quê.

---

## D-042 — Assistente Conversacional do Altare (Chat no Módulo, Ícone Flutuante e WhatsApp); Nível 5
- **Data:** 2026-10-27
- **Fase:** Pós-Congelamento (Produto, Camada de IA)
- **Pedido do usuário:** "quase tudo no produto possa ser feito por linguagem natural, só dentro do projeto", por três canais: módulo de chatbot, ícone fixo no canto inferior direito dos outros módulos que expande para um chat, e WhatsApp. Pensar como um servidor MCP próprio do Altare.
- **Decisão:**
  1. **Um só núcleo, três canais finos.** Um servidor de *tools* do Altare expõe **casos de uso da camada de aplicação** (nunca SQL direto) e os canais são adaptadores de entrada sobre ele: (a) **módulo de chat** (tela própria), (b) **ícone flutuante** no canto inferior direito das demais áreas, que expande para o chat com o contexto da tela, (c) **WhatsApp**.
  2. **Mesma autorização da API:** o agente age com `Actor(kind="agent", on_behalf_of=Noivo|Noiva)` (`architecture.md` §7). No WhatsApp, o número é **vinculado** a um dos dois usuários; número desconhecido não recebe dados.
  3. **Leitura livre, escrita sempre por proposta (`D-008`):** consultas respondem direto; qualquer mutação vira `ChangeProposal` com prévia e só é aplicada após confirmação humana explícita, também no WhatsApp (confirmação por resposta ou botão).
  4. **Schema legível por agente:** nomes autoexplicativos, enums fechados, descrições nas tabelas e colunas, *views* de leitura e chaves de busca aproximada (achar um fornecedor pelo nome parecido). Detalhado em `altare-agente-dados`.
  5. **Nível 5, depois do fluxo manual:** entra como Bloco 5.3 do roadmap. Nada da v1 depende dele (`D-005`).
  6. **Coerência com os não-objetivos (`vision.md` §5):** o WhatsApp aqui é o canal **entre o casal e o Altare**. O Altare continua sem enviar mensagem a fornecedores e sem ler conversas privadas do casal (`scope.md` §4, fora do escopo).
- **Razão:** a arquitetura já trata o agente como "mais um adaptador de entrada" (`D-027`). Tornar a linguagem natural um canal, e não uma segunda aplicação, evita duplicar regra e mantém a confirmação humana como conceito da camada de aplicação.
- **O que ficou rejeitado:**
  - Agente que acessa o banco ou executa SQL: contorna autorização, regras e histórico.
  - Escrita direta por agente, mesmo "de baixo risco": viola `D-008`.
  - Três implementações independentes, uma por canal.
  - Agente falando com fornecedores pelo WhatsApp: contraria o não-objetivo "não é um mensageiro".
- **Em aberto (`OQ-IA-001`, sem bloquear a v1):** lugar do módulo de chat na navegação, detalhamento do Nível 5, busca aproximada portátil entre SQLite e Postgres e custo e conta da API do WhatsApp (o *webhook* exige o app na nuvem) e a convivência do ícone flutuante com o "+ Registrar Rápido" no canto inferior direito.

---

## D-043 — Etapa 0: Base do `apps/web` Construída, com Hooks e Verificação de Limites Adiados
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Pedido do usuário:** gerar o plano do scaffold da Etapa 0 e executá-lo (`D-028`).
- **Decisão:**
  1. **Escopo entregue:** monorepo pnpm (sem `packages/` e sem *submodules*, `D-040`), `apps/web` com Vite, React 19, TypeScript `strict`, Tailwind v4 (plugin do Vite), Vitest com Testing Library e Biome (regras de acessibilidade incluídas). Scripts `lint`, `typecheck`, `test`, `build` e `dev`, expostos na raiz e no `Makefile`, que só orquestra o pnpm. Gates verdes: Biome, `tsc`, Vitest e `vite build`.
  2. **Versões fixadas pelo `pnpm-lock.yaml`:** React 19.3, Vite 8.3, TypeScript 7.0, Tailwind 4.3, Vitest 5.0 e Biome 2.6 (esta em versão exata). Tudo compatível na instalação, sem recuo para TypeScript 5.x.
  3. **`pre-commit` adiado** para o `apps/api`: só o Biome rodaria hoje, e Ruff, Pyright e `import-linter` dependem do backend. Fecha o item "hooks" que `altare-testes-qa` deixava para a Etapa 0.1.
  4. **`dependency-cruiser` adiado** para a primeira `feature` (Bloco 1.1): ainda não há `features/` para cobrar. As regras de `architecture.md` §11 valem desde já por revisão.
  5. **Fora da Etapa 0, por pertencerem à etapa seguinte:** roteamento, TanStack Query, formulários, Radix/shadcn, fontes, `tokens.css`, ativos de marca, PWA e cliente OpenAPI.
  6. **Um `biome.json` na raiz**, com escopo em `apps/web`; o Python usará Ruff.
  7. **Próximo passo:** Bloco 0.2, etapa (a): `tokens.css` gerado do `tokens.json`, fontes autohospedadas, `cn()` e `cva` (`design-system.md` §13).
- **Razão:** entregar só o necessário para o `apps/web` existir, com gates reais, antes de qualquer tela (`D-028`).
- **O que ficou rejeitado:**
  - Criar `pre-commit` e `dependency-cruiser` já: configurações sem nada para verificar, que envelhecem sem uso.
  - Criar pastas vazias de `routes/`, `features/` e `components/ui`: o git não as rastreia e cada uma nasce com o primeiro arquivo.
  - Recuar para TypeScript 5.x por precaução: a instalação e os quatro gates passaram com a 7.0.

---

## D-044 — Bloco 0.2, Etapa (a): Tokens Gerados, Fontes e `cn()`
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Pedido do usuário:** aprovou o escopo da etapa (a) com seis pontos de revisão (derivados, paleta padrão do Tailwind, escala no gerador, `tailwind-merge`, conferência visual) e mandou planejar e executar.
- **Decisão:**
  1. **`tokens.css` é gerado** por `apps/web/scripts/tokens.ts` (TypeScript, rodado com `tsx`) a partir de `docs/design/identidade-visual/tokens.json`: `pnpm tokens:build` ou `make tokens`. Um teste do Vitest falha se o arquivo versionado estiver defasado (`design-system.md` §12).
  2. **Derivados fora do `tokens.json`**, em constantes nomeadas no gerador: `focus-ring` (`var(--primary)`), `scrim` (`rgb(35 42 34 / .45)`), `primary-ink` (de `apoio`), `letter-spacing` do `eyebrow` (`.08em`) e o ponto de troca mobile/desktop (`48rem`). O JSON e o guia de 43 páginas não foram alterados.
  3. **Paleta padrão do Tailwind zerada** (`--color-*: initial`): só existem as cores semânticas, o que impõe "nunca vermelho" e "sem *hex* em componente" pela ferramenta.
  4. **Escala de texto como `@utility`** (`text-display`, `text-body-sm`, `text-num-lg`…), cada uma com família, tamanho mobile, peso e entrelinha, e o tamanho desktop em `@media`; os `num-*` levam `tabular-nums` e o `eyebrow` caixa-alta. Escolhido no lugar de `--text-*` do tema porque o Tailwind não carrega a família por ali. Raios, sombras, durações e curvas saem como variáveis do tema; `prefers-reduced-motion` zera animações e transições.
  5. **Fontes autohospedadas** pelo Fontsource (Newsreader com itálico, Plus Jakarta Sans e JetBrains Mono, variáveis). As famílias do Fontsource têm o sufixo ` Variable`, listado antes do nome da marca em `--font-*`.
  6. **`cn()`** (`clsx` + `tailwind-merge`) lê cores, raios, sombras e a escala de texto do `tokens.json`. O merge padrão descartava `text-ink` ao ver `text-body-sm` e não conhecia `rounded-card`. `class-variance-authority` está instalado para a etapa (c).
  7. **Base global:** `data-theme="light"` no `<html>`, `body` com `bg-canvas text-ink text-body` e foco visível em anel duplo. O Biome passa a aceitar as diretivas do Tailwind. O `App` mostra as três famílias só para conferência visual, até a vitrine da etapa (e).
- **Razão:** deixar as etapas (b) a (e) usarem só classes de token, com o gerador como única fonte e a defasagem barrada por teste.
- **O que ficou rejeitado:**
  - Acrescentar `focus-ring` e `scrim` ao `tokens.json`: obrigaria a regenerar o guia inteiro por dois valores derivados.
  - Manter a paleta padrão do Tailwind: `bg-red-600` ficaria a um *autocomplete* de distância.
  - Escrever à mão a lista de tokens do `cn()`: criaria uma segunda verdade que diverge da primeira.
  - `?raw` no teste de defasagem: o Vitest devolve string vazia para CSS e o teste passaria sem testar nada.

---

## D-045 — Bloco 0.2, Etapa (b): Ativos de Marca Copiados para o `apps/web`
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Pedido do usuário:** planejar e executar a etapa (b) do Bloco 0.2 (`D-028`).
- **Decisão:**
  1. **`apps/web/public/brand/` é cópia derivada** do pacote `docs/design/identidade-visual/`, gerada por `make brand` (`apps/web/scripts/build-brand.ts`, com o plano em `scripts/brand.ts`). Nada é redesenhado (`identity.md` §2.6). Um teste do Vitest falha se o conteúdo divergir do pacote ou se sobrar ou faltar arquivo.
  2. **O que se copia:** os 30 logos-mestre SVG (`fonte/`, 5 peças × 6 cores) em `logo/`, os 6 ornamentos em `ornamentos/`, o favicon (SVG, `.ico` e PNG 16/32/48) e o ícone do app (SVG e PNG 180/192/512). Os 30 logos entram de uma vez, mesmo os que a interface ainda não usa (`salvia` para o escuro, `preto` e `carvao` para o Dossiê), para a regra não mudar a cada etapa (~190 KB estáticos).
  3. **O que não se copia:** PNG dos logos (servem a documentos), ícone de 1024 px (loja de apps), favicons PNG 192 e 512 (o ícone do app cobre) e o restante de `componentes/` (guia, usos incorretos, paletas). Se um arquivo esperado faltar no pacote, o script falha em voz alta.
  4. **`index.html`:** favicon SVG com `.ico` de reserva, `apple-touch-icon` de 180 px e `theme-color` `#F9F5EC`, do tema claro. Um teste exige que cada link aponte para arquivo existente e que a cor seja a de `tokens.json` (`marca.app_icon.theme_color_claro`). A variante escura acompanha o tema escuro (adiado, `D-028`).
  5. **Biome ignora `public/brand`:** a cópia é derivada, como o `tokens.css`, e as regras de acessibilidade do Biome não se aplicam a SVG de marca editado fora do app.
  6. **Adiados:** o manifesto (vem com o PWA, restante do Bloco 0.1) e o componente `Logo` (nasce na casca de navegação, etapa (d)).
- **Razão:** dar ao app a marca oficial sem segunda fonte de verdade: o pacote continua sendo o único lugar onde ela muda, e o teste barra a cópia defasada.
- **O que ficou rejeitado:**
  - Copiar só os logos usados hoje: obrigaria a revisitar o script a cada tela nova.
  - Importar os SVGs do pacote direto em `src/`: o app passaria a depender de um caminho em `docs/` para renderizar.
  - Criar o manifesto e o `Logo` agora: dependem de decisões do PWA e da casca.

---

## D-046 — Bloco 0.2, Etapa (c): Abordagem dos 15 Primitivos, em 3 Lotes; Lote 1 (Campos)
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Pedido do usuário:** plano detalhado da etapa (c), quebrado em lotes, e execução (`D-028`).
- **Decisão:**
  1. **Três lotes, um PR cada:** (1) campos: `Button`, `Input`, `Textarea`, `Select`, `Checkbox`; (2) exibição: `Badge`, `Card`, `Table`, `Money`, `PageHeader`, `EmptyState`; (3) sobreposições: `Dialog`, `Tabs`, `Tooltip`, `Toast`. Este registro vale para a etapa inteira; o lote 1 está feito.
  2. **`radix-ui` unificado** (`import { Checkbox } from 'radix-ui'`) em vez de um pacote por componente, e `lucide-react` para os ícones (`identity.md` §7).
  3. **`Select` é o `<select>` nativo estilizado**, não o Radix Select: o celular abre o seletor do sistema, teclado e leitor de tela vêm de graça e o jsdom testa bem. A versão pesquisável e a "folha inferior" são do `Combobox`, adiado em `D-028`. Desvio consciente de "Radix re-estilizado".
  4. **`Toast` com Radix Toast** (região `aria-live="polite"`, 4 s, ação "Desfazer" opcional) e uma API mínima `useToast()`; sem `sonner`.
  5. **`Field` interno** (`components/ui/field.tsx`): rótulo acima, ajuda, erro com ícone, "obrigatório" escrito no rótulo e `aria-describedby` e `aria-invalid` ligados ao controle. Reusado por `Input`, `Textarea` e `Select`; não é um 16º primitivo da vitrine.
  6. **Convenções:** sem `forwardRef` (React 19), importação direta por arquivo e sem *barrel*; só classes de token; botão só de ícone **exige `aria-label` no tipo**, verificado pelo `tsc`; o `Button` tem `type="button"` por padrão; o `Money` (lote 2) é um formatador puro em `lib/money.ts` que só aceita inteiros em centavos.
  7. **Testes:** por papel e teclado (`getByRole`, `user-event`), escritos antes do código; o `setup.ts` limpa o DOM entre casos (com `globals: false` o Testing Library não o faz sozinho) e traz um *stub* de `ResizeObserver` para o jsdom.
  8. **Página de conferência provisória** (`src/app/Conferencia.tsx`) mostra os primitivos de cada lote para conferência com `make dev`; a vitrine `/design-system` a substitui na etapa (e).
  9. **Foco:** o anel duplo usa o espaçador `--focus-gap` (padrão `canvas`); `Card` e `Dialog` o redefinem para `surface`.
  10. **Acessibilidade:** teclado, nomes e `aria-*` são cobertos por teste; 320 px, zoom de 200%, leitor de tela e "reduzir movimento" seguem a checklist manual de `altare-acessibilidade`, a cargo do usuário em cada PR.
- **Ajustes em arquivos aprovados:** `design-system.md` §8 (notas sobre o `Select` nativo e o `Field`).
- **Razão:** dividir a maior etapa do Bloco 0.2 em entregas revisáveis, com o mecanismo de campos acessível definido uma vez.
- **O que ficou rejeitado:**
  - Radix Select no Bloco 0.2: custo de teste e de mobile sem ganho antes de existir lista pesquisável.
  - Um pacote Radix por componente: mais dependências para o mesmo resultado.
  - `sonner` para os *toasts*: segunda biblioteca de acessibilidade a conferir.
  - Rótulo e erro repetidos em cada campo: três cópias do mesmo `aria-describedby`.

---

## D-047 — `Select` com Lista Própria do App (Revisa o Item 3 de `D-046`)
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Pedido do usuário:** ao conferir o lote 1, viu que o `Select` abria o seletor do sistema (macOS) e queria que a lista de opções fosse do próprio app, com a identidade do Altare.
- **Decisão:**
  1. **O `Select` passa a ser o Radix Select estilizado** (`radix-ui`), com a lista aberta pelo app: superfície `surface` com *hairline* e sombra de nível 1, opção realçada em `surface-muted`, marca de escolhida em `primary`, opção desabilitada a 40%, alvo de 44 px no toque. Teclado (Enter abre, setas navegam, Enter escolhe, Esc fecha) e leitor de tela vêm do Radix.
  2. **API:** os filhos `<option>` dão lugar à prop `options` (`{ value, label, disabled? }`), e `onValueChange` substitui `onChange`. `value` não pode ser vazio; o *placeholder* é o texto da prop `placeholder`.
  3. **Testes:** o `setup.ts` ganha polyfills de `hasPointerCapture`, `setPointerCapture`, `releasePointerCapture` e `scrollIntoView`, que o jsdom não tem.
  4. **Continua adiado** o `Combobox` pesquisável e a "folha inferior" no celular (`D-028`, `design-system.md` §8).
- **Ajustes em arquivos aprovados:** `design-system.md` §8 (linha de `Select / Combobox`). O item 3 de `D-046` fica como histórico; vale esta decisão.
- **Razão:** a lista do sistema ignora a tipografia, a cor e os cantos do Altare, e destoava do restante dos campos.
- **O que ficou rejeitado:**
  - Manter o `<select>` nativo: seletor do sistema, fora da identidade, rejeitado pelo usuário.
  - Escrever a lista do zero, sem Radix: perderia o teclado, o foco e a semântica de `listbox` prontos.
  - Antecipar o `Combobox` pesquisável: não há lista longa para pesquisar antes do Bloco 3.1.

---

## D-048 — Etapa (c), Lote 2 (Exibição): `Money` sem o Modo `none` e Convenção de Classes de Texto
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Pedido do usuário:** perguntou em que caso de uso o `Money` precisaria arredondar e, sem caso concreto, preferiu **tirar o modo `none`**.
- **Decisão:**
  1. **`Money` tem só `precision` `auto` e `always`.** O modo `none` de `design-system.md` §9 não foi construído: nenhuma feature o usa, o `auto` já cobre os resumos ("sem centavos se inteiro", §14, item 4) e arredondar na exibição faria um total divergir da soma das linhas, que o casal confere à mão. Se uma tela futura precisar de um resumo sem centavos, a regra de arredondamento se decide naquele momento. As regras de arredondamento de cálculo (`F-ORC-03`, `F-CTR`) continuam só no backend.
  2. **Formatador puro `lib/money.ts`:** só inteiros seguros de centavos (qualquer outra coisa lança `RangeError`), `R$` + U+00A0, milhares com ponto, vírgula decimal, menos tipográfico (U+2212) nos negativos e `+` apenas com `signed`, nunca no zero.
  3. **`Badge`:** as variantes `consensus` e `attention` **exigem `icon` no tipo**, verificado pelo `tsc`, para a cor nunca ser o único sinal.
  4. **`Table`:** região rolável com `section` nomeada e focável por teclado (única supressão do Biome do lote, com o motivo na linha); cabeçalho de coluna fixo no topo, primeira coluna fixa opcional e duas densidades. A densidade chega às células **por contexto**, não por variantes de grupo.
  5. **Convenção:** as classes de texto do Altare (`text-body`, `text-eyebrow`, `text-num-*`…) definem família, tamanho, peso e entrelinha. Uma **variante** do Tailwind (`group-data-…:`, `md:`) que as use sobrescreve família e peso, porque as variantes vêm depois no CSS. Componentes escolhem a classe de texto em código (por *prop* ou contexto) e deixam a variante para tamanho e posição. A ordem entre `text-*` e utilitários do Tailwind (`font-medium`, `normal-case`) foi conferida no CSS gerado, não é garantida pelo Tailwind.
  6. **`PageHeader`** traz o único `h1` da tela; o `App` provisório já o usa.
- **Ajustes em arquivos aprovados:** `design-system.md` §9 (linha do `Money`, `none` riscado).
- **Razão:** manter o `Money` pequeno e sem arredondamento de exibição até haver um caso real, e registrar a armadilha das classes de texto antes de os próximos componentes repetirem o erro.
- **O que ficou rejeitado:**
  - `none` arredondando ao real mais próximo: risco de total divergente das parcelas.
  - `none` truncando: subestima valores e também diverge da soma.
  - Variantes `group-data` para a densidade da `Table`: sobrescreviam o estilo do cabeçalho e o mono das células.

---

## D-049 — Etapa (c) Concluída: Lote 3 (Sobreposições) e Balanço dos 15 Primitivos
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Pedido do usuário:** plano e execução do lote 3 da etapa (c) (`D-028`, `D-046`).
- **Decisão:**
  1. **Etapa (c) concluída:** os 15 primitivos de `components/ui` existem: `Button`, `Input`, `Textarea`, `Select`, `Checkbox` (lote 1, `D-046`, `D-047`), `Badge`, `Card`, `Table`, `Money`, `PageHeader`, `EmptyState` (lote 2, `D-048`) e `Dialog`, `Tabs`, `Tooltip`, `Toast` (lote 3), mais o `Field` interno e o formatador `lib/money.ts`.
  2. **Desvios da especificação de referência (§8 e §9), todos registrados:** `Select` com a lista do próprio app em vez do `<select>` nativo (`D-047`, revisa `D-046`); `Money` sem o modo `none` (`D-048`).
  3. **`Dialog`:** exige `title` no tipo (nome acessível) e tem o botão "Fechar" sempre; é centralizado a partir de `md` e **folha inferior** abaixo disso. `AlertDialog`, `Sheet`/gaveta lateral e `Popover` seguem adiados.
  4. **Movimento:** `@keyframes` e `@utility` em `src/styles/index.css` (`animate-overlay-*`, `animate-sheet-*`, `animate-dialog-*`, `animate-toast-*`), com `--duration-base` e as curvas `--ease-standard` (entrada) e `--ease-exit` (saída); `prefers-reduced-motion` segue zerando tudo em `tokens.css`. Sem *bounce*, *parallax* nem animação em *loop* (exceto o indicador de carregamento do `Button`).
  5. **`Tooltip`** inclui o provedor, atraso de 300 ms, aparece em hover e foco, some com Esc e ao afastar o ponteiro; o gatilho precisa ter nome acessível.
  6. **`Toast`:** `ToastProvider` e `useToast()`; 4 s; anúncio `aria-live="polite"` (o Radix o renderiza num `<span role="status">` oculto, fora da região visível); pausa ao passar o mouse ou focar; **`action.altText` obrigatório no tipo**; tons `success`, `attention` e `info` com cor, ícone e texto; topo à direita no desktop e base no celular, com a variável `--shell-bottom-offset` para a futura barra inferior. O `ToastProvider` envolve o `App`.
  7. **`Tabs`:** ativação por setas, `Home` e `End`, lista rolável no celular e anel de foco **interno** (o contêiner rolável cortaria o externo).
  8. **Acessibilidade:** cobertos por teste teclado, nomes, papéis e `aria-*` de todos os primitivos; **pendentes da passada manual do usuário** (`altare-acessibilidade`): 320 px e zoom de 200%, leitor de tela, "reduzir movimento" e alvo de 44 px em tela de toque, em cada lote. O que depende de layout e de animação reais fica fora do alcance do jsdom.
  9. **Próximo:** etapa (d), casca de navegação com seletor de lente e as 7 áreas-esqueleto; depois a (e), vitrine `/design-system`, que apaga a página de conferência provisória.
- **Ajustes em arquivos aprovados:** `design-system.md` §13 (etapa (c) marcada como concluída).
- **Razão:** fechar a etapa com o registro dos desvios e das pendências manuais, para a casca e a vitrine partirem de um conjunto completo e conhecido.
- **O que ficou rejeitado:**
  - Antecipar `AlertDialog`, `Sheet` e `Popover`: nenhuma tela do Nível 0 os usa (`D-028`).
  - `sonner` para as notificações: segunda biblioteca de acessibilidade a conferir, sem ganho sobre o Radix Toast.
  - Limite de fila de notificações: sem caso real ainda.

---

## D-050 — Assistente como 8ª Área da Navegação e Ícone Flutuante, Já na Casca (Resolve o Item 1 de `OQ-IA-001`)
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0 (etapa (d) do Bloco 0.2)
- **Pedido do usuário:** ao planejar a casca de navegação, o usuário decidiu que o assistente entra **já na casca**: "Incluir a área \"Assistente\", e o ícone flutuante."
- **Decisão:**
  1. **A navegação tem 8 áreas:** as 7 de `D-025` e o **Assistente** (o "módulo de chat" de `D-042`). No desktop e no tablet fica **ao fim da lista, separado das demais por uma *hairline***; no celular a barra inferior continua com 4 destinos mais "Mais", e o Assistente entra dentro de "Mais".
  2. **O ícone flutuante do assistente** fica no canto inferior direito das demais áreas, **recolhido por padrão, nunca abre sozinho e nunca cobre o conteúdo principal**; fica **oculto na própria área Assistente** (seria redundante). No celular fica acima da barra inferior.
  3. **Só a casca nasce agora.** A área Assistente é uma página-esqueleto como as outras, e o ícone abre um painel provisório que diz, com calma e sem prometer prazo, que o assistente ainda não está disponível. O chat de verdade (mensagens, campo de texto, prévia de `ChangeProposal` com Confirmar e Rejeitar) é do Bloco 5.3 (`D-008`, `D-042`).
  4. **Item 5 da `OQ-IA-001` (canto compartilhado com o "+ Registrar Rápido") continua aberto, com gatilho no Bloco 3.1:** até lá o assistente é o único dono do canto; ao construir o `QuickAddFab`, decide-se como convivem (ex.: o assistente dentro do menu "Novo"). Os itens 2 a 4 seguem para o Bloco 5.3.
  5. **Ícone da área:** `message-square-text` (Lucide), que evita `message-circle` (WhatsApp) e `messages-square` (divergência), os dois reservados em `identity.md` §7. Os ícones das demais áreas estão em `design-system.md` §10.1.
- **Ajustes em arquivos aprovados:** `experience.md` §3.1 (8ª área); `design-system.md` §5 e §10.1 (barra lateral, "Mais" e tabela de ícones); `roadmap.md` (Blocos 0.2 e 5.3); `stack.md` §11 (item 4); `open-questions.md` (item 1 resolvido, item 5 com gatilho); skills `altare-ui-ux`, `altare-frontend`, `altare-agente-dados` e `altare-engenharia-de-ia` (a regra "não nasce antes do Bloco 5.3, nem como placeholder" passa a valer só para o chat, não para a casca).
- **Razão:** o usuário quer o assistente visível na estrutura do app desde o início, para a navegação e o canto inferior direito nascerem já contando com ele, em vez de serem refeitos no Nível 5.
- **O que ficou rejeitado:**
  - Manter a `OQ-IA-001` inteira em aberto e construir só as 7 áreas (recomendação do agente): o usuário preferiu decidir agora.
  - Só o ícone flutuante, sem área própria: não dá lugar ao histórico e à tela do módulo de chat de `D-042`.
  - Só a 8ª área, sem o ícone: perde o acesso ao assistente com o contexto da tela atual.

---

## D-051 — Etapa (d), Lote 1: Roteador, Casca de Navegação e Seletor de Lente
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Pedido do usuário:** plano e execução da etapa (d) do Bloco 0.2, em 2 lotes (`D-028`, `D-050`).
- **Decisão:**
  1. **TanStack Router em modo *code-based*** (árvore escrita à mão em `src/routes/router.tsx`, sem plugin nem arquivo gerado), com rotas tipadas, página carregada sob demanda por rota (cada área vira um *chunk*) e `defaultPreload: 'intent'`. O modo por arquivos exigiria o plugin e um `routeTree.gen.ts` conferido contra defasagem, cerimônia desproporcional para 10 rotas (`stack.md` §2, princípio 5); migrar depois é mecânico.
  2. **URLs em pt-BR:** `/`, `/planejamento`, `/cronograma`, `/possibilidades`, `/orcamento`, `/contatos`, `/convidados`, `/assistente`, mais `/design-system`, que mantém a página de conferência provisória **fora da navegação** até a etapa (e). Uma rota desconhecida mostra "Não encontramos esta página" com a saída para a Visão Geral.
  3. **A lente fica na URL:** `?lente=minha` (ausente é `Casal`), validada na rota raiz (qualquer outro valor vira `Casal`) e preservada pelos links da navegação. Sem `localStorage`: a preferência por usuário vem com o login. **O efeito real de "Minha visão" depende do login e das features**; hoje só o estado e o seletor existem.
  4. **Casca em `src/app/shell/`:** `nav-config.ts` é a fonte única das 8 áreas (ordem, nome, ícone, posição na barra inferior). Responsivo por **CSS**: ≥ 1024 barra lateral de 256 px; 768 a 1023 trilho de 72 px (o nome fica `sr-only`); < 768 barra superior compacta e barra inferior com 4 destinos mais "Mais", cuja folha é o `Dialog` abaixo de `md`. O conteúdo tem no máximo 1200 px. O hook `useMediaQuery` só decide se as dicas do trilho aparecem (na barra larga o nome já está visível).
  5. **Espaço da barra inferior:** a variável `--shell-bottom-offset` (4 rem mais a *safe area* no celular, 0 acima de `md`) fica em `:root`, em `index.css`, para o `Toast` (fora da casca) e o conteúdo a lerem.
  6. **Novo primitivo `SegmentedControl`** (Radix `ToggleGroup`, `radiogroup` com itens `radio`): sempre com uma opção marcada, Tab entra na selecionada, setas movem o foco e Espaço escolhe. É o primeiro dos "demais primitivos" de `design-system.md` §8 a ser pedido por uma tela (`D-028`).
  7. **Nome curto "Opções" na barra inferior do celular** para a área Possibilidades & Decisões: "Possibilidades" não cabe em ~70 px por destino (5 colunas em 390 px) em nenhum tamanho legível. Na barra lateral e na folha "Mais" vale o nome completo. **Desvio consciente de `design-system.md` §10.1 ("Possibilidades")**, reversível trocando uma linha de `nav-config.ts`.
  8. **Acessibilidade da casca:** link "Ir para o conteúdo" como primeiro foco; `header`, dois `nav` com nomes distintos ("Navegação principal" e "(celular)"), `aside` e `main#conteudo`; `aria-current="page"` na área ativa, mais uma faixa no destino atual da barra inferior (a cor não é o único sinal). **Ao trocar de área**, o título do documento vira "Área · Altare" e o foco vai ao `h1`, que ganhou `tabIndex={-1}`; a primeira página e a troca só da lente não movem o foco.
  9. **Textos dos esqueletos** em `features/<módulo>/copy.ts`, no tom de `altare-conteudo-copy`, tirados de `experience.md` §3.1, **sem botão de ação** (nada funciona ainda): exceção consciente à regra "estado vazio com uma ação". A revisão do texto é do usuário no PR.
  10. **Gate de limites próprio no lugar do `dependency-cruiser`:** o gatilho de `D-043` (a primeira `feature`) ocorreu, mas o `dependency-cruiser` **não suporta o Node 25** em uso (só as versões LTS: 22, 24 e 26 em diante). As mesmas regras viraram `apps/web/scripts/architecture.ts`, testado em `src/architecture.test.ts` e rodado pelo `make test`: `components/ui` não importa `features` nem `lib/api`; uma feature só importa outra pelo `index.ts`; features não importam `app` nem `routes`; sem ciclos (imports só de tipo não contam). Conferido com violações reais, depois removidas. **Reavaliar ao adotar um Node LTS.**
  11. **Ícones de navegação** (Lucide, 24 px, traço 1,5): `house`, `compass`, `calendar-days`, `columns-3`, `wallet`, `contact`, `users` e `message-square-text` (Assistente), em `design-system.md` §10.1.
  12. **Acessibilidade e layout:** teclado, nomes, `aria-current`, lente e navegação cobertos por teste; **pendentes da passada manual do usuário** (`altare-acessibilidade`): os 3 tamanhos de tela, o trilho e a barra inferior reais, 320 px e zoom de 200%, leitor de tela e "reduzir movimento". O jsdom não carrega o CSS, então não prova nenhum *breakpoint*.
  13. **Próximo:** lote 2, o ícone flutuante do assistente (`D-050`), e depois a etapa (e), a vitrine.
- **Ajustes em arquivos aprovados:** `stack.md` §7 e `architecture.md` §9, §13 e §14 (o gate de limites no lugar do `dependency-cruiser`); `design-system.md` §13; skills `altare-testes-qa`, `altare-frontend`, `altare-devops`, `altare-pull-request` e `altare-escrita-de-codigo` (referência ao gate).
- **Razão:** dar ao `apps/web` a estrutura que as áreas vão ocupar, com a navegação e a lente prontas e acessíveis, e manter os limites entre camadas verificados por máquina desde a primeira `feature`.
- **O que ficou rejeitado:**
  - Roteamento por arquivos com plugin e `routeTree.gen.ts`: cerimônia sem ganho para 10 rotas.
  - `localStorage` para a lente: o estado vai na URL, compartilhável, e a preferência por usuário vem com o login.
  - Truncar "Possibilidades" na barra inferior: rótulo cortado deixaria o destino ilegível.
  - Instalar outro Node só para rodar o `dependency-cruiser`: mudaria o ambiente do usuário sem ele pedir.
  - Esperar o Bloco 1.1 para ter limites verificados: a primeira feature já chegou.

---

## D-052 — Casca de Navegação Alinhada ao Guia de Identidade (Revisa os Itens 7 e 11 de `D-051`)
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Pedido do usuário:** ao comparar a casca com a aplicação "Visão Geral no desktop" do guia (`altare-identidade-visual.pdf`, gerada por `build/componentes.py`), apontou que o espaçamento e as opções do canto superior direito estavam diferentes.
- **Decisão:**
  1. **O guia é a referência visual da casca** (aprovado em `D-025`), com as medidas lidas do próprio gerador: barra lateral com itens de 40 px a cada 46 px, ícone de 20 px, rótulo de 12 px, ativo em `surface-muted` com ícone `primary` e rótulo em seminegrito; marca de 26 px; barra superior de 72 px com o título em `ink` seminegrito; conteúdo com recuo de 34 px.
  2. **Ícones das áreas voltam aos do guia:** `layout-dashboard`, `map`, `calendar`, `scale`, `wallet`, `users` e `gift`; no celular, `house`, `scale`, `wallet`, `users` e `ellipsis`. Os ícones escolhidos em `D-050`/`D-051` (`house`, `compass`, `calendar-days`, `columns-3`, `contact`) foram um erro do agente, que não conferiu o guia. O Assistente, ausente do guia, segue com `message-square-text`.
  3. **Seletor de lente como no guia:** trilho `surface-sunken` com a opção ativa em `surface`, contornada por *hairline* e em seminegrito (não mais oliva cheio), com os rótulos **"Visão do Casal"** e "Minha visão". É o novo visual do primitivo `SegmentedControl`.
  4. **Celular como no guia:** barra de 72 px, ícone de 22 px, rótulo de 12 px, ativo em `primary` e seminegrito (sem a faixa superior), **rótulos abreviados "Possib." e "Orçam."** (o leitor de tela lê "Possibilidades" e "Orçamento", que contêm o texto visível) e a **ordem do guia: Início, Possib., Orçam., Contatos, Mais**. Isso substitui o nome "Opções" de `D-051` (item 7) e diverge da ordem de `design-system.md` §10.1, que foi atualizado. O guia não mostra a lente no celular, então ela vai para o topo da folha "Mais".
  5. **Textura de papel** sobre o canvas no tema claro (`identity.md` §6), com a opacidade do `tokens.json` (`--texture-opacity`, gerada), num pseudo-elemento fixo abaixo do conteúdo, desligada em impressão e com transparência reduzida.
  6. **Tamanhos fora da escala:** o guia usa 15 px no título da barra superior, 13 px no seletor e 11 px nos rótulos do celular; o app usa os tokens mais próximos (16, 14 e 12 px), porque só classes de token entram nos componentes.
  7. **Fica para o login:** o bloco "Noivo · sessão individual" no pé da barra lateral. O selo "conteúdo ilustrativo" é marcação do guia, não da interface.
- **Ajustes em arquivos aprovados:** `design-system.md` §10.1 (tabela com os ícones e o celular do guia e as medidas).
- **Razão:** a casca é a primeira tela que o casal vê, e o guia aprovado já define como ela deve parecer; divergir dele sem decisão contraria `AGENTS.md` §1.
- **O que ficou rejeitado:**
  - Manter os ícones e o nome "Opções" escolhidos pelo agente: contrariam o guia aprovado.
  - Manter a ordem de §10.1 no celular (Contatos antes de Orçamento): o usuário pediu fidelidade ao guia.
  - Valores de 15, 13 e 11 px escritos à mão: quebrariam a regra de só usar tokens; se a diferença incomodar, o caminho é acrescentar o tamanho ao `tokens.json`.

---

## D-053 — Atalho Discreto para o Design System, só em Desenvolvimento
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Pedido do usuário:** "Inclua uma forma não tão invasiva de visualizar o design system", depois de a página de conferência sair da raiz para `/design-system` e ficar sem link.
- **Decisão:**
  1. **Um link "Design system" no pé da barra lateral**, separado do menu por uma *hairline*, **visível só com `import.meta.env.DEV`** (`make dev`). O Vite o remove do *build* de produção, conferido no pacote gerado. Vale também para o trilho do tablet, onde mostra só o ícone (`palette`) com dica.
  2. **Não faz parte das 8 áreas** (`NAV_ITEMS`) nem do `nav` principal; é um item à parte, `DESIGN_SYSTEM_ITEM`. A navegação aprovada (`D-025`, `D-050`) fica intacta na versão publicada, e o celular não ganha o atalho.
  3. **Etapa (e):** a vitrine definitiva herda a rota e o atalho; se o casal precisar vê-la na versão publicada, é decisão nova.
- **Ajustes em arquivos aprovados:** `design-system.md` §2 (nota sobre o acesso à vitrine).
- **Razão:** o catálogo é ferramenta de quem desenvolve; um link só em desenvolvimento o deixa a um clique sem poluir a navegação do casal nem exigir mudança de produto.
- **O que ficou rejeitado:**
  - Link permanente no menu: altera a navegação aprovada e mostra ao casal uma ferramenta de desenvolvimento.
  - Atalho de teclado escondido: ninguém o descobre, e um atalho global precisaria de decisão sobre conflitos (`design-system.md` §10, item 8).
  - Item na folha "Mais" do celular: o desenvolvimento dos primitivos é feito no desktop.

---

## D-054 — Auditoria do `apps/web` contra o Guia de Identidade: Tamanhos 15, 13 e 11 px, Alturas de Campo e Alinhamento dos Primitivos e da Casca (Revisa o Item 6 de `D-052`)
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Pedido do usuário:** auditar tudo o que existe no `apps/web` (15 primitivos, vitrine, casca, esqueletos, tokens, tipografia, ícones, movimento, textura) contra o guia de identidade visual e corrigir o que divergir, porque a casca e os primitivos nasceram sem conferência com as páginas de aplicação do guia (`D-052`).
- **Método:** hierarquia de verdade explícita (1. `tokens.json`, valores; 2. o guia, composição e medidas, lidas em `build/componentes.py` e `medidas.json`; 3. `identity.md`; 4. `design-system.md`, onde diverge o guia vence; 5. o código nunca é fonte). Cada item foi classificado em A (guia claro, corrigir), B (ambíguo ou fora da escala, decisão do usuário), C (guia não cobre) ou D (já decidido); capturas do app em 1440, 768, 390 e 320 px foram comparadas com os PNGs do guia. Resultado: 17 itens A, 7 B, 4 C e 12 D; tokens, marca, cores semânticas, foco, superfícies, movimento e as medidas da casca já estavam conformes.
- **Decisão:**
  1. **Três tamanhos entram no `tokens.json`** (revisa o item 6 de `D-052`): `ui` 15/22 (botões, linhas de cartão e descrições de estado), `ui-sm` 13/18 (selos, lente) e `ui-xs` 11/14 (rótulo da barra inferior). Os 12,5 px do guia viram 13 e o título de 38 px fica em `display` (40). O guia (página 26) e o `tokens.css` foram regenerados; os SVGs de componentes cujo desenho não mudou foram restaurados, porque o subconjunto de fonte embutido muda de bytes a cada execução do pipeline.
  2. **Alturas de controle como no guia:** campos (`Input`, `Select`) com **44 px** em qualquer tela, botão `md` com 40 px no desktop e **44 px no celular** (antes 48); `lg` segue em 48. Revisa `design-system.md` §5 (`D-025`).
  3. **Tipografia:** a Newsreader passa a carregar o eixo óptico (`opsz.css`, +74 KB no arquivo latin), como a fonte do guia; *preload* da Newsreader 400 e da Plus Jakarta Sans 400 no `index.html`; reservas de métrica `"<Família> Fallback"` com `size-adjust`, `ascent-override` e `descent-override` medidos com `fontTools` (Georgia 90,5%, Arial 106,2%, Courier New 100%), geradas no `tokens.css` (`identity.md` §4, guia pág. 29).
  4. **Ícones:** todo ícone Lucide com traço de **1,5 px que não escala** (`LucideProvider` com `strokeWidth` 1,5 e `nonScalingStroke` em `providers.tsx`), porque os tamanhos vêm de classes CSS e `absoluteStrokeWidth` mede pela prop `size`. Antes valia o padrão 2 (guia pág. 33).
  5. **Primitivos:** `Button` em seminegrito, 15 px, e `ghost` em `ink-muted`; rótulo de campo em seminegrito; `Badge` em **pílula** de 26 px, 13 px, seminegrito, neutro em `ink-muted`; `EmptyState` com ramo de 64 px, título `name` e opção `ramo-grande` (a do 404, pág. 31); `Toast` com título em seminegrito; `SegmentedControl` em 13 px; `Tooltip` no **nível 1** da pág. 32 (Marfim, *hairline*, sombra suave) no lugar do escuro; `Table` com `isolate`, para o canto fixo não passar por cima da barra superior; **`Money` com espaço depois do sinal** (`+ R$ 1.200,00`, `− R$ 3.100`).
  6. **Casca:** *wordmark* de 29 px de altura (versal de 26 px) e símbolo de 27 px no celular, com as posições do guia; rótulos da barra lateral numa linha só; barra inferior com rótulos de `ui-xs`; ícones da folha "Mais" em `ink-muted` e o ativo em `primary`; as páginas-esqueleto com o estado vazio dentro de um `Card`.
  7. **Títulos editoriais nas 8 áreas** (padrão das págs. 38 a 40): o rótulo nomeia a área e o `h1` diz o que a página é; o título do documento e a barra superior seguem com o nome da área. Visão Geral usa o texto exato do guia ("O momento de vocês"). As outras sete são textos propostos e aprovados nesta decisão:

     | Área | Rótulo | Título (h1) |
     | :--- | :--- | :--- |
     | Visão Geral | Visão geral | O momento de vocês |
     | Planejamento & Caminhos | Planejamento | O rumo de vocês |
     | Cronograma & Dependências | Cronograma | O que pode andar agora |
     | Possibilidades & Decisões | Possibilidades | Comparar propostas |
     | Orçamento & Simulador | Orçamento | O orçamento de vocês |
     | Contatos & Fornecedores | Contatos | Quem vocês estão consultando |
     | Convidados, Enxoval & Dia D | Convidados | Quem estará com vocês |
     | Assistente | Assistente | Conversem com o assistente |

  8. **Custo comparável como no guia** (págs. 34 e 40): o total sai em `ink`, mono de 24 px, e a terracota fica só nos custos extras, com ícone e sinal `+`. Corrige `design-system.md` §9 e `visual-direction.md` §2.3 e §3. O tom `comparable` do `Money` passa a ser o dos extras.
  9. **Vitrine `/design-system`:** ganha as seções Cores (as 17 do `tokens.json`, com a função) e Tipografia (a escala inteira, com a amostra), o `SegmentedControl` e os estados que faltavam (carregando e desabilitado em todas as variantes do botão, `Textarea`, `Select` e `Checkbox` desabilitados, aba desabilitada, ramo grande). Um teste falha se um arquivo de `components/ui` não aparecer na vitrine.
  10. **Desvios aceitos, registrados:** cabeçalho de `Table` com fundo `surface-muted` e linha em sans (o guia, pág. 28, é a linha de orçamento, componente de domínio, revista quando o `BudgetRow` nascer); `Toast` com raio de 10 px e *hairline* (precisa se separar do conteúdo, nível 1); barra superior opaca, sem a textura de 3,5% (evita o conteúdo aparecer por baixo ao rolar); `Dialog`, `Tabs`, `Checkbox`, lista do `Select`, folha "Mais" e tom `info` do `Toast` aprovados como estão, por não terem página no guia; lupa do celular (pág. 39) adiada até a busca global do Bloco 3.1 (`D-034`); rótulo de 11 px na barra inferior por fidelidade ao guia, abaixo dos 12 px da escala anterior.
  11. **Ícone flutuante do Assistente** (lote 2 da etapa (d), `D-050`), que o guia não mostra: **pílula secundária de 48 px** com `message-square-text` e o texto "Assistente" (`surface`, borda `border-strong`, sombra de nível 1), no canto inferior direito e acima da barra inferior no celular, para ficar mais calma que o "Registrar" primário da pág. 39. A construção segue como lote 2.
- **Ajustes em arquivos aprovados:** `tokens.json` (três tamanhos) e o guia regenerado (HTML, PDF, página 26); `design-system.md` §4 (escala), §5 (raios e alturas), §8 (`Badge`) e §9 (`Money` e `ComparableCostBreakdown`); `visual-direction.md` §2.3 e §3 (custo comparável).
- **Razão:** o guia foi aprovado em `D-024` e `D-025`, e o app divergia dele em detalhes que o casal vê todo dia: traço dos ícones, peso dos títulos, quebra de linha na barra lateral, forma dos selos e alturas. Corrigir por medida lida do gerador do guia, e não a olho, evita repetir o `D-052`.
- **O que ficou rejeitado:**
  - Aproximar 15, 13 e 11 px dos tokens existentes: o usuário preferiu acrescentar os tamanhos para ficar fiel ao desenho do guia.
  - Manter campos de 40 px e botões de 48 px no celular: o guia mostra 44 px nos dois.
  - `absoluteStrokeWidth` do Lucide: mede pela prop `size`, e aqui o tamanho vem de classes.
  - Manter o título de cada área igual ao nome dela: repete a barra superior e destoa das páginas do guia.
  - Manter o total comparável em terracota: o guia reserva a terracota aos extras.
  - Reabrir o regenerar dos 53 SVGs de componentes sem mudança de desenho: só enchia o diff de ruído.
- **Pendente (do usuário):** a passada manual de `altare-acessibilidade` (teclado, zoom de 200%, VoiceOver e "reduzir movimento"); o reflow de 320 px sem rolagem horizontal foi verificado por script nas 10 rotas.

---

## D-055 — O Guia de Identidade como Referência Obrigatória do Front: Mapa guia → Componente, Regra nas Skills e Teste de Regras de Design (Revisa o Gatilho do Script Anti-*hex* de `D-028`)
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Pedido do usuário:** garantir que, de agora em diante, qualquer trabalho de front seja feito com o guia de identidade como referência obrigatória, ajustando a documentação para agentes e os gates de revisão, para o próximo agente não precisar ouvir o usuário reclamar para consultar o guia.
- **Causa (da auditoria de `D-054`):** nenhuma skill nem doc mandava abrir as páginas de **aplicação** do guia (32 a 42) antes de construir; `altare-design` citava a pasta só para tokens e pipeline, e `altare-frontend`, `altare-ui-ux` e `altare-code-review` nem a citavam. Os primitivos (`D-046` a `D-049`) saíram do texto de `design-system.md`, sem conferência, e a casca nasceu diferente do guia (`D-052`). A auditoria achou 17 divergências corrigíveis.
- **Decisão:**
  1. **Mapa guia → componente** em `design-system.md` §15, fora da pasta gerada do guia (que o pipeline sobrescreve): uma tabela com cada componente, tela ou padrão do app, a página do guia (PNG e SVG de aplicação), as linhas de `build/componentes.py` com as medidas e o estado (conforme, desvio com `D-xxx`, sem página ou pendente). É o índice único para o qual as skills apontam, com a hierarquia de verdade explícita (1. `tokens.json`; 2. o guia; 3. `identity.md`; 4. `design-system.md`; 5. o código nunca é fonte).
  2. **Definição de pronto de UI** (`design-system.md` §12): todo componente ou tela só está pronto depois de **comparado com a página do guia**, com cada divergência registrada.
  3. **`AGENTS.md`:** regra inegociável nova em §2 (item 6, curta) e um passo obrigatório em "Como Retomar" (item 4: achar a linha no mapa, abrir o PNG, ler a medida, comparar ao terminar). O `CLAUDE.md` da raiz continua sem regras, só apontando.
  4. **Skills,** que apontam para o mapa e não copiam o conteúdo: `altare-design` ganha a seção "Fonte visual: o guia", antes dos princípios, com o fluxo (ache a página no mapa, abra o PNG, leia a medida em `componentes.py`, só então implemente, compare ao terminar); `altare-frontend` e `altare-ui-ux` (fluxo e estados contra as págs. 34, 35, 37 a 40 e 42) remetem a ele; `altare-code-review` passa a **bloquear** "UI sem conferência contra a página do guia, ou valor divergente sem decisão registrada"; `altare-pull-request` ganha o item "comparado com o guia, com captura quando houver mudança visual". As `description` de `altare-design`, `altare-frontend` e `altare-ui-ux` passam a disparar em pedidos de UI e visual mesmo sem a palavra "guia" ("ajusta o espaçamento", "cria a tela de X").
  5. **Teste de regras de design ativado, revisando o gatilho de `D-028`** (`apps/web/scripts/design-rules.ts`, `src/design-rules.test.ts`, rodado pelo `make test`): falha com *hex*, `rgb()`/`hsl()` e afins literais, classe arbitrária de cor, fonte, traço ou sombra que não leia um token com `var(--…)` (`bg-[…]`, `text-[15px]`, `font-[600]`) e valor solto de cor ou fonte em `style`. Layout arbitrário (`min-w-[36rem]`, `grid-cols-[…]`, `calc()`) segue livre. Avaliação que levou à ativação: o código tinha **0 *hex*** e só valores arbitrários de layout, de modo que o gatilho de `D-028` ("*hex* mais de uma vez") não disparou, mas o risco real mostrado por `D-054` é o desvio de valor sem *hex* (`text-[15px]` seria a saída fácil para o que acabou virando token). Custo: um teste de milissegundos, sem infraestrutura. O gate foi conferido com violações reais, depois desfeitas. `D-028` fica como histórico.
  6. **Limite assumido:** o teste barra valor solto, mas **não prova que a composição bate com o guia**. Isso continua sendo a conferência com o mapa (itens 1 a 4) e o bloqueio da revisão.
- **Ajustes em arquivos aprovados:** `design-system.md` §12 (linha "Só token em componentes", definição de pronto), §13 (gatilho cumprido), cabeçalho e §15 (novo mapa); `AGENTS.md` §1, §2, §4 e "Como Retomar"; `roadmap.md` (Bloco 0.2); skills `altare-design`, `altare-frontend`, `altare-ui-ux`, `altare-code-review`, `altare-pull-request` e `altare-testes-qa` (tabela de gates). A ordem das etapas do roadmap não muda.
- **Razão:** o guia foi aprovado, mas só valia se alguém o abrisse. Um mapa único, uma regra curta e um bloqueio na revisão põem a conferência no caminho de quem constrói e de quem revisa, e o teste tira da memória a regra "só token".
- **O que ficou rejeitado:**
  - Copiar as medidas do guia para as skills: criaria uma segunda verdade que diverge da primeira (`AGENTS.md` §5: skills apontam).
  - Colocar o mapa dentro da pasta do guia: o pipeline (`uv run build.py`) a sobrescreve.
  - Regra no `CLAUDE.md` da raiz: `AGENTS.md` é a fonte única das regras operacionais.
  - *Snapshots* visuais contra os PNGs do guia: continuam adiados (`D-028`), por custo e sem o gatilho de regressões recorrentes.
  - Manter o script anti-*hex* adiado: o risco não é o *hex*, e o teste custa quase nada.
  - Proibir todo valor arbitrário, inclusive de layout: obrigaria tokens de espaço sem ganho para o casal.
- **Pendente:** o mapa precisa de manutenção na mesma mudança que constrói um componente novo, e as linhas de `componentes.py` que ele cita acompanham o guia se ele for regenerado.

---

## D-056 — Etapa (d), Lote 2: Ícone Flutuante do Assistente, Cartão Provisório e o Primitivo `Popover` (Conclui o Item 11 de `D-054`)
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Pedido do usuário:** construir o lote 2 da etapa (d), o ícone flutuante do Assistente (`D-050`), com o desenho de `D-054` (item 11). O guia não desenha esse elemento nem o seu painel; as duas escolhas abaixo foram feitas pelo usuário com recomendação do agente (`AGENTS.md` §3).
- **Conferência com o guia (`AGENTS.md` §1, item 4):** pág. 39 (o "Registrar" flutuante: 144 × 48 px, 16 px da borda direita e 16 px acima da barra de 72 px, `build_mobile` `:963`) para posição e geometria; pág. 32 (`build_superficies` `:611-628`) para o raio `pill`, a borda `border-strong` do controle e a sombra de nível 1 (popover). Capturas do app em 1440, 768, 390 e 320 px comparadas com as duas páginas: a pílula mede 146 × 48 px (o texto "Assistente" é mais largo que "Registrar"), fica a 16 px da borda e da barra no celular e a 34 px da borda e 24 px do pé no desktop.
- **Decisão:**
  1. **Pílula secundária de 48 px** (o `Button` `secondary` `lg` com raio `pill` e sombra nível 1) com `message-square-text` e o texto "Assistente", em `features/assistant/components/assistant-launcher.tsx`. Monta na casca (`AppShell`), **oculta na própria área `/assistente`** e visível nas demais rotas, inclusive `/design-system` e a página não encontrada. **Nunca abre sozinha.** No celular fica a `--shell-bottom-offset` mais 1 rem do pé, ou seja, acima da barra inferior.
  2. **Recolhe ao rolar para baixo e volta ao rolar para cima ou no topo** (escolha do usuário, para a pílula nunca cobrir o que se lê em tela curta). Hook `useHiddenOnScrollDown` em `lib/` (limite de 12 px contra tremida). O recolhimento é **só visual** (opacidade e 16 px de deslocamento em 220 ms, que o `prefers-reduced-motion` zera): a pílula continua na ordem de Tab e no leitor de tela, e **reaparece quando recebe foco** por teclado, para ninguém a perder. Com o cartão aberto ela fica à vista. Conferido no Chrome: opacidade 0, sem clique e deslocada ao rolar; opacidade 1 e clicável com foco.
  3. **O conteúdo reserva 6 rem no fim** (`pb` de `--shell-bottom-offset` mais 6 rem, antes 2 rem) para o ícone nunca cobrir a última linha ao fim da rolagem (medido nos 4 tamanhos: sem sobreposição).
  4. **Painel provisório como cartão ancorado no canto** (escolha do usuário, entre o diálogo central e o cartão): título "O assistente ainda não está disponível" e duas frases calmas, sem prometer prazo, que explicam que a inteligência chega depois das áreas manuais e que, até lá, tudo continua nas áreas do Altare. Textos em `features/assistant/copy.ts`. Sem campo de texto, sem botão de enviar e sem simular chat; o chat de verdade segue no Bloco 5.3 (`D-008`, `D-042`).
  5. **Novo primitivo `Popover`** (`components/ui/popover.tsx`, Radix), o primeiro dos "demais primitivos" de §8 pedido por esta tela (`D-028`): cartão ancorado no gatilho, **nível 1 de profundidade da pág. 32** (Marfim, *hairline*, raio 10, sombra suave), **não modal** (não escurece nem trava a página), com título (`aria-labelledby`), descrição opcional (`aria-describedby`), botão Fechar com nome, Esc e clique fora para fechar, foco para dentro ao abrir e de volta ao gatilho ao fechar. Entra na vitrine (o teste de completude exige) e no mapa §15.
  6. **A feature do assistente deixa de ser carregada sob demanda:** a casca já a importa, então o `chunk` próprio da página não existia mais e o build avisava `INEFFECTIVE_DYNAMIC_IMPORT`. A rota `/assistente` importa `AssistantPage` direto (a página tem 0,6 kB). As demais áreas seguem sob demanda.
  7. **Desvios do guia, registrados:** a pílula é **secundária** (o "Registrar" da pág. 39 é primário), para ficar mais calma, e **se recolhe ao rolar** (o guia não mostra a flutuante em movimento). O cartão não tem página no guia: segue o nível 1 da pág. 32.
  8. **Convivência com o "+ Registrar Rápido" segue a `OQ-IA-001`, item 5** (gatilho no Bloco 3.1): até lá o assistente é o dono do canto.
- **Ajustes em arquivos aprovados:** `design-system.md` (§8 `Popover`, §13 etapa (d) e lista de primitivos adiados, §15 linha do ícone e nova linha do `Popover`); `AGENTS.md` §1 e "Como Retomar"; `roadmap.md` (Bloco 0.2).
- **Razão:** dar ao assistente o seu lugar na casca desde já (`D-050`), no espírito calmo do guia e sem cobrir o que o casal lê, e criar só o primitivo que a tela pede, com a conferência feita contra as páginas 32 e 39.
- **O que ficou rejeitado:**
  - Diálogo central como painel (recomendado pelo agente): o usuário preferiu o cartão no canto, mais próximo do chat futuro.
  - Manter a pílula fixa mesmo cobrindo texto em tela curta (recomendado pelo agente): o usuário preferiu recolher ao rolar.
  - Recolher com `visibility: hidden` ou `tabindex="-1"`: tiraria o assistente do teclado e do leitor de tela enquanto a página está rolada.
  - Pílula primária como o "Registrar" do guia: disputaria a atenção com a ação principal do Bloco 3.1.
  - Esconder a pílula também na vitrine e na página não encontrada: não há razão, e a vitrine é onde ela se confere.
- **Pendente (do usuário):** a passada manual de `altare-acessibilidade` no ícone e no cartão (Tab até a pílula com a página rolada, Esc, VoiceOver, zoom de 200%, "reduzir movimento"); o jsdom não prova layout nem animação. **Pendente de desenho:** o `Toast` no celular ocupa a mesma faixa do pé e pode cobrir a pílula por 4 s; revisar quando a primeira notificação real existir.

---

## D-057 — Etapa (e): Vitrine `/design-system` Definitiva, Só em Desenvolvimento, e Conclusão do Bloco 0.2 (Revisa o Item 3 de `D-053`)
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0
- **Pedido do usuário:** concluir a vitrine `/design-system` como definitiva (nome e rótulo ainda provisórios), conferir o critério de conclusão do Bloco 0.2 (`design-system.md` §13) e decidir se ela aparece na versão publicada. Resposta do usuário, com recomendação do agente: **só em desenvolvimento**.
- **Fato que motivou a escolha:** em `D-053` só o **link** do menu era exclusivo de desenvolvimento; a **rota** `/design-system` existia em qualquer *build*, então abria na versão publicada a quem digitasse a URL, sem ninguém ter decidido isso.
- **Decisão:**
  1. **A vitrine só existe em desenvolvimento, rota e link** (revisa o item 3 de `D-053`). Na versão publicada a rota `/design-system` cai na página não encontrada (`beforeLoad` com `notFound()`), e, como o Vite troca `import.meta.env.DEV` por `false`, o `import()` da vitrine é descartado do pacote: conferido no *build*, que não tem mais o *chunk* `design-system` nem nenhuma de suas cadeias de texto. Um teste cobre a rota em produção (`routes.test.tsx`) e o já existente cobre o link (`app-shell.test.tsx`).
  2. **Nome e cabeçalho definitivos:** o arquivo `Conferencia.tsx` virou `primitives-showcase.tsx` (`PrimitivesShowcase`); o rótulo "Exemplo · conferência" virou **"Vitrine · dados de exemplo"** e a descrição provisória ("Espaço Exemplo A · texto de interface") virou "Cores, tipografia e os componentes do Altare, com variantes e estados. Os exemplos são fictícios." (a regra de rotular dados de exemplo, `AGENTS.md` §2, continua cumprida). Um teste exige o cabeçalho e que a palavra "conferência" não volte. **Texto proposto pelo agente, para revisão do usuário no PR** (`altare-conteudo-copy`).
  3. **Critério de conclusão do Bloco 0.2 (`design-system.md` §13) conferido** com captura em 1440, 768, 390 e 320 px: a vitrine mostra as 17 cores com a função, a escala tipográfica inteira e os 17 primitivos (os 15 de `D-028`, mais `SegmentedControl`, de `D-051`, e `Popover`, de `D-056`) com variantes e estados visíveis (botão em 5 variantes e 3 tamanhos, mais ícone, carregando e desabilitado; campos com erro e desabilitado; os 5 tons de `Money`; 3 cartões; 2 densidades de tabela; 3 estados vazios; diálogo, cartão, abas, dica e as 4 notificações); **sem rolagem horizontal em nenhum dos 4 tamanhos** (medido) e sem elemento fora da largura; as 8 áreas navegáveis como esqueletos (testes de rota); o app segue a identidade (`design-rules.test.ts`; no mapa §15 não sobra componente do Bloco 0.2 pendente, só o login, que é do restante do Bloco 0.1). O que é estado vivo (hover, ativo, foco, tooltip, cartão e diálogo abertos) se confere interagindo, como a própria vitrine diz.
  4. **Bloco 0.2 concluído** (etapas (a) a (e), `D-043` a `D-057`). **O Nível 0 do `apps/web` está fechado;** o que resta do Bloco 0.1 (API, banco, login e PWA) segue **fora de escopo até o usuário pedir** (`D-028`).
  5. **Limite assumido:** o teste de completude garante que cada **arquivo** de `components/ui` aparece na vitrine, não que cada **variante** apareça; isso é conferência visual (item 3). Vale revisar se um primitivo ganhar variante nova.
- **Ajustes em arquivos aprovados:** `design-system.md` (§2 acesso e vitrine, §12, §13 etapa 5 e critério, que dizia 7 áreas e agora diz 8); `roadmap.md` (Bloco 0.2); `AGENTS.md` §1 e "Como Retomar".
- **Razão:** a vitrine é ferramenta de quem desenvolve; deixá-la só em desenvolvimento, sem rota na versão publicada, fecha uma exposição que ninguém decidiu, não pesa no pacote do casal e dispensa manter dois estados da página. O critério do Bloco 0.2 foi conferido por medida e captura, não por inspeção do código.
- **O que ficou rejeitado:**
  - Manter a rota aberta por URL, sem link (como estava): exposição não decidida de uma ferramenta de desenvolvimento.
  - Vitrine visível com link no menu: muda a navegação aprovada (`D-025`, `D-050`) e mostra ao casal uma ferramenta que não é para ele.
  - Esconder só o link e manter o *chunk* no pacote: peso morto na versão publicada.
  - Um teste que exige cada variante na vitrine: custo de manutenção alto para um app de duas pessoas; a conferência visual por tamanho cobre.
- **Pendente (do usuário):** a passada manual de `altare-acessibilidade` sobre o Nível 0 (teclado, zoom de 200%, VoiceOver e "reduzir movimento": casca, primitivos, ícone e cartão do Assistente e a vitrine), que o jsdom não prova; e a revisão do texto do cabeçalho da vitrine. **Em aberto para decisão do usuário:** abrir o release `develop → main` do Bloco 0.2 (`altare-git-fluxo`, regra 4), que depende do esquema de versionamento ainda não confirmado.

---

## D-058 — Vitrine `/design-system`: Catálogo da Identidade (Arranjos, Arco, Ramo, Ícones, Favicon e Ícone do App, Dossiê) e Índice em Duas Partes
- **Data:** 2026-10-27
- **Fase:** Implementação — Nível 0 (pós-Bloco 0.2)
- **Pedido do usuário:** o guia (`altare-identidade-visual.pdf`) tem seções que a vitrine não mostrava: "Quatro arranjos, nenhum lado a lado", "O arco de volta perfeita", "O ramo de oliveira", "Ícones com significado fixo", "Favicon e ícone do app" e "Dossiê do Dia D". Pediu-as **em formato de catálogo**, não de apresentação. (O pedido dizia 3 seções, mas listava 6; as 6 foram feitas.)
- **Conferência com o guia (`AGENTS.md` §1, item 4):** páginas 12, 30, 31, 33, 36 e 42, abertas em PNG, e as medidas e os textos lidos em `build/componentes.py` (`build_lockups` `:226`, `build_arco` `:555`, `build_ramo` `:577`, `build_iconografia` `:643-661`, `build_favicon_app` `:784-819`, `build_dossie` `:1055-1103`). Capturas do app em 1440, 768, 390 e 320 px comparadas com as páginas: sem rolagem horizontal, sem imagem quebrada, âncora do índice a 96 px do topo (abaixo da barra de 72 px).
- **Decisão:**
  1. **Seis seções novas** em `src/app/identity-showcase.tsx`, todas com os **ativos reais** de `public/brand` (nada redesenhado) e os valores do `tokens.json` (traço de 1,25 px, opacidade de 70%, raio do favicon de 22%, versal de 43% e de 40%, nome e valor do Musgo e da Amêndoa Forte), e cada uma citando a página do guia de origem: **Arranjos da marca** (os 4 arranjos, uso e arquivo, e o aviso de que não existe lockup horizontal), **Arco** (simples, duplo e arcada, com proporção, traço, cor e leitura), **Ramo de oliveira** (grande, pequeno e faixa, com desenho, traço, cor e limite), **Ícones com significado fixo** (os 12 ícones do mapa de `identity.md` §7, com a cor semântica e o nome no Lucide, e os tamanhos de 16, 20 e 24 px), **Favicon e ícone do app** (aba clara, favicon em 16, 32, 48, 64 e 96 px, e o ícone do app como entregue e como o sistema o exibe) e **Dossiê do Dia D**.
  2. **Dossiê: peças reais e as 6 regras de impressão, sem montar o documento** (escolha do usuário, com recomendação do agente): assinatura formal, *hairline*, rótulo e arcada, mais as 6 regras da pág. 42 e o aviso de que **o documento nasce no Bloco 4.2** (`F-DOS`). Não há folha A4 nem campos "[a definir]": seria antecipar componente de domínio (`D-028`).
  3. **Mesma página, com índice em duas partes** (escolha do usuário, com recomendação do agente): "Identidade" (Cores, Tipografia e as 6 novas) e "Componentes" (as 8 de antes), com um `nav` "Índice da vitrine" no topo (`showcase-index.tsx`). Um teste exige que o índice liste toda seção da página, na ordem, e que cada link leve ao título certo. Uma regra de CSS (`scroll-margin-top`) impede o título de parar sob a barra superior fixa.
  4. **Desvios do guia, registrados:** (a) a **aba escura** da pág. 36 fica de fora, porque o tema escuro está adiado (`D-028`) e a regra de só usar token proíbe cor solta; (b) o **celular com a grade de apps** da pág. 36 vira o par "como entregue" e "como o sistema exibe", que mostra a mesma regra (quadrado cheio, o sistema arredonda) sem fundo de cor solta; (c) os **nomes de arquivo** saem em `ink-muted`, não em `ink-subtle` como no desenho, porque `ink-subtle` só é aprovado sobre Marfim (`identity.md` §3.4); (d) os **títulos** são nomes de catálogo ("Arco", não "O arco de volta perfeita"), com a página do guia no subtítulo; (e) as **seis versões de cor** da marca (pág. 14) não entram: não foram pedidas.
  5. **Teste:** `identity-showcase.test.tsx` cobre cada seção (nomes, arquivos, ícones, tamanhos e percentuais), que todo ativo de marca mostrado existe em `public/brand` e que toda imagem tem texto alternativo. O teste de regras de design (`D-055`) acusou um falso positivo (um campo `color:` numa lista de dados, que não é `style`); o campo foi renomeado para `tone` em vez de afrouxar a regra.
- **Ajustes em arquivos aprovados:** `design-system.md` (§2 vitrine, §12, §15 com a linha do catálogo); `AGENTS.md` §1; `roadmap.md` (Bloco 0.2).
- **Razão:** o catálogo é o lugar onde quem constrói confere os ativos e as regras da identidade sem abrir um PDF de 25 MB; usar os ativos e os valores reais evita uma segunda versão deles.
- **O que ficou rejeitado:**
  - Montar a folha A4 do Dossiê com campos "[a definir]": antecipa o Bloco 4.2.
  - Copiar a página do Dossiê do guia como imagem: exigiria copiar mais um arquivo gerado (~290 KB) e estender o `make brand` por uma figura de referência.
  - Rota separada `/design-system/marca`: outra rota só de desenvolvimento e mais um caso de teste de produção.
  - Reproduzir a aba escura com cor solta: quebra a regra de só token (`D-055`) por um tema que não existe ainda.
- **Pendente (do usuário):** a passada manual de `altare-acessibilidade` na vitrine (a navegação por âncoras do índice, o foco e o zoom de 200%) e a revisão dos textos do catálogo, que são do guia, com os subtítulos de origem propostos pelo agente.
