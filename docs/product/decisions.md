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
  6. **Tema claro + escuro ("Noite Oliva")** já no Nível 0, com `claro / escuro / sistema`. Refina `D-015`, que rejeitou apenas o *dark-mode estrito* (único tema escuro).
- **Razão:** Os agentes de IA aumentam a complexidade (propostas, confirmação, somente-leitura, múltiplos canais e provedores), e isso justifica portas e casos de uso explícitos; o histórico básico basta para dois usuários; as escolhas visuais mantêm a atmosfera editorial sem cair em ornamento kitsch (`D-016`).
- **O que ficou rejeitado:**
  - Monólito modular sem separação de domínio/infraestrutura (recomendação inicial do agente; o usuário preferiu Clean por causa dos agentes).
  - Trilha de auditoria completa e histórico mínimo sem autoria.
  - Ornamento nulo ou rico; cantos retos ou muito arredondados; tema exclusivamente claro.
- **Ajustes colaterais:** `stack.md` §3.1 substituída por `architecture.md`; eventos de domínio síncronos em processo passam a existir (antes "sem barramento de eventos"); `Profile` vira enum de domínio (não tabela); `import-linter` e `dependency-cruiser` entram no CI.
- **Pendente:** aprovação do detalhamento em `architecture.md` (`OQ-ENG-005`), `identity.md` e `design-system.md` (`OQ-DS-001`).

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
