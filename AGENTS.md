# AGENTS.md — Contrato Operacional do Repositório

Este arquivo é a **fonte única de verdade operacional** para qualquer agente de IA (Cursor, Claude Code, Codex ou outro) que trabalhe neste repositório.

---

## 1. Estado Atual do Projeto

- **Nome do produto:** **Altare** (`D-023`, 2026-10-27). Princípio de marca: *"O altar no centro. A festa a serviço."* O diretório/repositório continua `wedding-planner`.
- **Fase atual:** `Implementação — Nível 0: Design System enxuto (Etapa 0, a base do `apps/web`, e Bloco 0.2 etapas (a), tokens e fontes, e (b), ativos de marca, **concluídas** em 2026-10-27, `D-043` a `D-045`; etapa (c), os 15 primitivos, **concluída** (`D-046` a `D-049`); etapa (d), casca de navegação com **8 áreas, incluindo o Assistente (`D-050`)**, **em andamento em 2 lotes**: lote 1, casca e rotas, **feito** (`D-051`) e **alinhado ao guia de identidade** (`D-052`, `D-054`); lote 2, ícone flutuante do assistente (desenho decidido em `D-054`, item 11), a fazer; depois a etapa (e), vitrine, já com tokens, tipografia e os estados dos primitivos)` *(Fases 1 a 5 e `D-001` a `D-018` aprovadas em 2026-10-24; stack em `D-020`/`D-021` e arquitetura/identidade/design system em `D-022`, em 2026-10-26; nome em `D-023`, pacote de identidade visual em `D-024`, identidade + design system **aprovados** em `D-025`, produto não confessional em `D-026` e arquitetura **aprovada** em `D-027`, em 2026-10-27; implementação **autorizada** e design system **enxuto** em `D-028`; skills de projeto, monorepo, fluxo de branches e assistente conversacional em `D-039` a `D-042`, em 2026-10-27; base do `apps/web` em `D-043`, tokens e fontes em `D-044`, ativos de marca em `D-045` e primitivos em `D-046` a `D-049` e Assistente na navegação em `D-050` e casca de navegação em `D-051` a `D-053`; auditoria e alinhamento do `apps/web` ao guia em `D-054`)*
- **Status de código/arquitetura:** **Só o `apps/web` existe, agora com rotas e a casca de navegação (8 áreas, lente na URL)** (`D-043` a `D-053`): monorepo pnpm, Vite + React 19 + TypeScript, Tailwind v4, Vitest e Biome, com `lint`, `typecheck`, `test` e `build` verdes; `tokens.css` gerado do `tokens.json` (`make tokens`), fontes autohospedadas, `cn()` e os ativos de marca em `public/brand/` (`make brand`, favicon e ícone do app ligados no `index.html`). Primitivos em `components/ui`: campos (`Button`, `Input`, `Textarea`, `Select` com lista própria, `Checkbox`, mais o `Field` interno) exibição (`Money`, `Badge`, `Card`, `Table`, `PageHeader`, `EmptyState`) e sobreposições (`Dialog`, `Tabs`, `Tooltip`, `Toast` com `useToast`): **os 15 primitivos existem**, com a vitrine `/design-system` em construção (`src/app/Conferencia.tsx` e `src/app/tokens-showcase.tsx`: cores, tipografia, os 16 primitivos com variantes e estados), que um teste exige completa. Sem os demais primitivos, rotas, API, banco ou login. Implementação autorizada em `D-028`, que começou pelo `apps/web` mínimo do Bloco 0.1 (monorepo pnpm, Vite + React + TypeScript, Tailwind v4, Vitest, Biome e `tsc`) e pelo **Bloco 0.2 enxuto**: tokens do tema claro gerados do `tokens.json`, ativos de marca copiados, 15 primitivos, casca de navegação com seletor de lente e 8 áreas-esqueleto (as 7 de `D-025` e o Assistente, `D-050`), e vitrine `/design-system` mínima. Etapas: (a) tokens e fontes → (b) ativos de marca → (c) primitivos → (d) casca e esqueletos → (e) vitrine, cada uma validada com lint, *typecheck* e testes antes da seguinte. **Fora desta sessão:** API, banco, login e PWA. **Adiados com gatilho** (`D-028`): tema escuro, componentes de domínio, *snapshots* visuais, `axe` automatizado, script anti-*hex*, impressão. Stack (`docs/engineering/stack.md`), arquitetura (`docs/engineering/architecture.md`, `D-027`), identidade e design system (`D-025`, reduzido por `D-028`) aprovados. Em paralelo, o **detalhamento de features por área** está em andamento (`D-029`): `docs/product/features/planejamento-e-caminhos.md` está **aprovado**; `docs/product/features/convidados-enxoval-e-dia-d.md` (parte Convidados, `D-030`) está **aprovada**; `docs/product/features/cronograma.md` (`D-031`) está **aprovado**; `docs/product/features/orcamento-e-simulador.md` (`D-032`) está **aprovado**; `docs/product/features/possibilidades-e-decisoes.md` (`D-033`) está **aprovado**; `docs/product/features/contatos.md` (Bloco 3.1, `D-034`) está **aprovado**; `docs/product/features/propostas-por-categoria.md` (Bloco 3.2, `D-035`) está **aprovado**; `docs/product/features/contratos-e-parcelas.md` (Bloco 3.3, `D-036`) está **aprovado**; a parte Enxoval de `docs/product/features/convidados-enxoval-e-dia-d.md` (Bloco 4.1, `D-037`) está **aprovada**; `docs/product/features/centro-de-comando.md` e a parte Dossiê de `docs/product/features/convidados-enxoval-e-dia-d.md` (Bloco 4.2, `D-038`) estão **aprovados**: o **detalhamento de features da v1 manual (Níveis 1 a 4) está concluído** (`D-029` a `D-038`). Restam, fora da v1, a camada de IA (Nível 5, com o assistente conversacional de `D-042`) e o plano de implantação e backup. Há **uma pergunta em aberto, que não bloqueia a v1** (`OQ-IA-001`). Em 2026-10-27 também foram criadas as **skills de projeto** `altare-*` (`D-039`), o monorepo sem *submodules* (`D-040`) e o fluxo de branches (`D-041`): ver §5.
- **Premissa de produto (`D-026`):** o Altare **não é só para casamentos católicos**, embora o autor seja católico. Produto e marca são não confessionais; o tipo de cerimônia (religiosa de qualquer tradição, civil ou simbólica) é um dado do casal, nunca presumido. Nenhum roteiro fixo de uma tradição na v1.

### Fases de Concepção (100% Concluídas)
1. **Entrevista** *(Concluída)* — Entender o casal, o momento do planejamento, o que já existe e o que mais dói hoje.
2. **Conceito** *(Concluída e Aprovada)* — Fechar problema, para quem é, o que faz, o que não faz, escopo (v1 vs. depois vs. fora) e como se diferencia de planilha, pasta e grupo de mensagens.
3. **Experiência** *(Concluída e Aprovada)* — Definir a jornada do casal, a arquitetura de informação, os objetos do produto e os fluxos principais.
4. **Direção visual** *(Concluída e Aprovada)* — Definir personalidade (`Editorial Acolhedor & Estruturado`), princípios de interface, cor, tipografia e tom (sem tela de alta fidelidade).
5. **Congelamento** *(Concluída e Aprovada em `D-017`)* — Conceito, stack (`D-019`) e pirâmide de desenvolvimento (`D-018`) confirmados pelo usuário.

### Como Retomar na Próxima Sessão
1. Leia `docs/engineering/README.md`, `docs/engineering/stack.md`, `docs/engineering/roadmap.md` e `docs/design/design-system.md` §12 e §13.
2. Respeite a stack (`docs/engineering/stack.md`), a arquitetura (`docs/engineering/architecture.md`) e o design (`docs/design/identity.md`, `docs/design/design-system.md`) aprovados; qualquer desvio exige nova decisão registrada.
3. A **Etapa 0** (`D-043`) e as **etapas (a), (b) e (c) do Bloco 0.2** (`D-044` a `D-049`) estão concluídas (rode `make lint`, `make typecheck` e `make test` para conferir). **Comece pela etapa (d) do Bloco 0.2 enxuto** (`D-028`, casca de navegação e as 8 áreas-esqueleto, incluindo o Assistente e o ícone flutuante, `D-050`) e siga até a (e), uma de cada vez, só avançando com lint, *typecheck* e testes verdes. O detalhamento de features da v1 manual (`D-029` a `D-038`) está **concluído**; consulte `docs/product/features/` ao construir cada bloco. Valores de marca vêm só de `docs/design/identidade-visual/tokens.json`; o `tokens.css` é gerado, nunca editado à mão. Componentes de domínio só nascem no bloco que os usa.

---

## 2. Regras Inegociáveis de Condução

1. **Proibido codar antes do Congelamento (Fase 5):** Não crie código de aplicação, banco de dados, protótipos de código ou definições de stack técnica enquanto a Fase 5 não estiver formalmente aprovada.
2. **Não avançar de fase com bloqueios abertos:** Não avance para a próxima fase enquanto as perguntas que bloqueiam a fase atual estiverem sem resposta em `docs/product/open-questions.md`.
3. **Perguntas em lotes curtos e acionáveis:** Pergunte apenas o que muda uma decisão de produto, design ou escopo. Quando o usuário não souber, registre a lacuna em `docs/product/open-questions.md` e siga com uma proposta explícita e reversível.
4. **Premissas fixas de contexto:**
   - **Uso inicial:** Pessoal, exclusivo do noivo (autor do projeto) e de sua noiva. Qualquer expansão para outros casais (SaaS/multi-tenant) é **hipótese futura**, nunca premissa de projeto.
   - **Geografia e cultura:** Casamento no **Brasil** (terminologias locais como assessoria/cerimonialista do dia, buffet, espaço, cartório, parcelas/sinal, PIX/boleto, etc.).
   - **Proibido inventar dados do casamento:** Nunca invente data, cidade, orçamento total, número de convidados nem estilo do casamento. Trate esses dados como variáveis em aberto que o próprio produto ajudará o casal a definir.
5. **Manutenção da documentação viva:**
   - A cada decisão tomada, atualize os arquivos afetados **na mesma resposta**.
   - Toda decisão relevante deve ser registrada em `docs/product/decisions.md` com data, motivação e alternativas rejeitadas.
   - Não reescreva documentos estáveis sem explicitar ao usuário o que mudou e por quê.
   - Ao final de cada sessão/turno, atualize a fase atual neste `AGENTS.md`, registre decisões novas e mantenha `docs/product/open-questions.md` limpo e acionável.

---

## 3. O que o Agente Pode Decidir vs. O que Precisa Perguntar

### O agente PODE propor/decidir autonomamente (com registro explícito):
- Estruturação interna dos documentos e organização de tabelas/fluxos.
- Propostas de decomposição de *Jobs to be Done*, objetos de domínio e estados de itens, desde que alinhadas às respostas do usuário.
- Sugestões de automações de IA para a fase pós-fluxo manual, respeitando a distinção da decisão `D-008`: **mutações de dados** exigem confirmação humana explícita; **ações somente-leitura/proativas** (como revisão geral do planejamento e envio de notificações personalizadas) podem rodar autonomamente sem alterar os dados do casamento.

### O agente PRECISA perguntar / confirmar com o usuário:
- O que entra na primeira versão (v1) vs. o que fica para depois (v1.1 / v2) vs. o que fica de fora.
- Mudanças nas fronteiras do produto (novos módulos ou corte de módulos existentes).
- Decisões de modelo mental na Experiência (Fase 3) e escolhas estéticas na Direção Visual (Fase 4).
- Passagem de uma fase para a seguinte e o Congelamento final (Fase 5).

---

## 4. Mapa da Documentação (`docs/`)

Todos os documentos de produto e design devem ser mantidos em **português**:

- `docs/product/vision.md` — Problema, usuários, proposta de valor, diferenciação (vs. planilha, pasta e WhatsApp) e não-objetivos.
- `docs/product/personas.md` — O casal (noivo e noiva com perfis distintos) e papéis secundários/externos (como o cerimonialista do dia).
- `docs/product/jobs.md` — Trabalhos a realizar (*Jobs to be Done*) e em que momento da jornada aparecem.
- `docs/product/scope.md` — Mapeamento por território: trabalho do casal, o que entra na v1 (agora), o que entra depois e o que fica de fora.
- `docs/product/decisions.md` — Log cronológico de decisões: decisão, data, razão e o que foi rejeitado.
- `docs/product/open-questions.md` — Perguntas em aberto, por que importam e qual fase/decisão bloqueiam.
- `docs/design/experience.md` — Jornada do casal, arquitetura de informação, objetos do produto e fluxos principais *(Fase 3)*.
- `docs/design/visual-direction.md` — Personalidade, princípios de interface, cor, tipografia e tom *(Fase 4)*.
- `docs/engineering/README.md` — Especificação de engenharia pós-congelamento (modelo de domínio, resumo da stack e design tokens).
- `docs/engineering/stack.md` — Stack técnica detalhada e granular (backend, frontend, dados, auth, qualidade, estrutura do repo, adiamentos e riscos), revisada em `D-020`.
- `docs/engineering/architecture.md` — Arquitetura Clean pragmática (camadas, estrutura, eventos, agentes de IA, API, qualidade, frontend, mapa de domínio e estados), `D-022`.
- `docs/design/identity.md` — **Identidade visual oficial do Altare** (nome, princípio, sacralidade discreta, marca, cor, contraste, tema escuro, tipografia, ornamento, ícones, movimento, estados), `D-022` e `D-023`. Regras da marca (o porquê).
- `docs/design/identidade-visual/` — **Pacote da identidade (brand book, `D-024`)**: `tokens.json` (fonte única dos valores), guia de 43 páginas (`altare-identidade-visual.pdf`/`.html`), logos-mestre em `fonte/`, componentes exportados com `componentes/INDEX.md` e o pipeline `build/` (`uv run build.py`; `--marca` regenera os logos). Ao mudar um valor de marca, edite o `tokens.json` e regenere; nunca edite os arquivos gerados à mão.
- `docs/design/design-system.md` — Design System (tokens, escala, layout, acessibilidade, componentes primitivos e de domínio, padrões, governança e ordem do Bloco 0.2), `D-022`.
- `docs/product/features/` — **Detalhamento de features, um arquivo por área** (`D-029`): campos, regras, estados e critérios de aceite, na ordem da pirâmide. Prevalece sobre `scope.md` onde houver diferença. Aprovado: `planejamento-e-caminhos.md` (Bloco 1.1). Aprovado: `convidados-enxoval-e-dia-d.md` (parte Convidados, Bloco 1.2, `D-030`). Aprovado: `cronograma.md` (Bloco 1.3, `D-031`). Aprovado: `orcamento-e-simulador.md` (Bloco 2.1, `D-032`). Aprovado: `possibilidades-e-decisoes.md` (Bloco 2.2, `D-033`). Aprovado: `contatos.md` (Bloco 3.1, `D-034`). Aprovado: `propostas-por-categoria.md` (Bloco 3.2, `D-035`). Aprovado: `contratos-e-parcelas.md` (Bloco 3.3, `D-036`). Aprovado: parte Enxoval de `convidados-enxoval-e-dia-d.md` (Bloco 4.1, `D-037`). Aprovado: `centro-de-comando.md` e parte Dossiê (Bloco 4.2, `D-038`). **Detalhamento da v1 manual concluído.**
- `docs/engineering/roadmap.md` — Cronograma de desenvolvimento em Pirâmide de Blocos (do Nível 0 fundacional ao Nível 5 de IA, sem datas ou prazos).

---

## 5. Skills do Projeto (`.claude/skills/`, `D-039`)

As skills `altare-*` codificam as decisões já registradas em `docs/`; elas **apontam** para os documentos e não os copiam. Em caso de conflito, vale o documento e a skill é corrigida. Cada `SKILL.md` declara quando usar, quando não usar e qual skill vizinha cobre o resto.

**Precedência (`D-039`):** o Altare é um projeto pessoal. Neste repositório, as skills `altare-*` **substituem** as instruções globais do usuário que mandam aplicar padrões da Dharma (`dharma-standards`, `dharma-sdd`, `dharma-tdd`, `dharma-commit`, `dharma-commit-push-pr`, `dharma-create-pr` e `dharma-code-review*`). Para commit, branch e PR, use sempre `altare-commit`, `altare-git-fluxo` e `altare-pull-request`.

**`CLAUDE.md` por módulo:** todo módulo de `docs/engineering/architecture.md` §4 tem um `CLAUDE.md` curto na própria pasta (propósito, superfície pública, invariantes, dependências permitidas, links de feature e como testar), apontando para este arquivo e para `docs/`. **Módulo novo nasce com `CLAUDE.md`**; o modelo está em `altare-docs-vivas`. O `CLAUDE.md` da raiz não recebe regras.

| Área | Skill | Propósito |
| :--- | :--- | :--- |
| Engenharia | `altare-arquitetura` | Camadas, limites entre módulos, quando criar porta ou abstração, eventos, registro de decisão |
| | `altare-backend-api` | FastAPI: rotas, `problem+json`, bloqueio otimista, DTOs, autoria vinda da sessão |
| | `altare-banco-de-dados` | Tabelas, migrations, índices, integridade e portabilidade SQLite → PostgreSQL |
| | `altare-agente-dados` | Tools do assistente = casos de uso, escrita via `ChangeProposal`, schema legível por agente, três canais (`D-042`) |
| | `altare-engenharia-de-ia` | Agentes, prompts, evals, custo e latência, guardrails (`D-008`), observabilidade |
| | `altare-escrita-de-codigo` | Código limpo e modular; sinais de código de IA a evitar |
| | `altare-frontend` | Estrutura de `features/` e `components/`, estado, performance, testes de componente |
| | `altare-monorepo` | `apps/api` + `apps/web` sem *submodules* (`D-040`), tarefas na raiz, contrato OpenAPI e *drift* |
| Qualidade | `altare-testes-qa` | Pirâmide de testes, TDD, Ruff, Pyright, Biome, `tsc` e quais gates bloqueiam |
| | `altare-code-review` | Checklist de revisão de diff do projeto |
| | `altare-seguranca-privacidade` | LGPD, dados de casal e convidados, autenticação, segredos |
| | `altare-acessibilidade` | Checklist manual WCAG 2.2 AA (o gate que substitui o `axe` adiado, `D-028`) |
| | `altare-devops` | CI/CD, ambientes, deploy, migração para nuvem e custos |
| Produto e design | `altare-produto` | Critérios de produto bom, priorização na pirâmide, validação em uso |
| | `altare-analytics-metricas` | North Star, funil e métricas derivadas do próprio banco |
| | `altare-gtm-pricing` | **Dormente**: só se o usuário explorar abrir para outros casais (`D-002`) |
| | `altare-design` | Tokens, identidade e design system enxuto |
| | `altare-ui-ux` | Fluxos, heurísticas, onboarding, estados vazio e de erro |
| | `altare-conteudo-copy` | Tom de voz e textos em pt-BR |
| Fluxo de trabalho | `altare-git-fluxo` | `main ← develop ← feature`, hotfix e release (`D-041`) |
| | `altare-commit` | Commits atômicos com plano aprovado, Conventional Commits em pt-BR |
| | `altare-pull-request` | PR com `gh`, base `develop` (ou `main` no hotfix) |
| | `altare-docs-vivas` | Registrar decisões e features, manter a fase e os modelos de documento |
