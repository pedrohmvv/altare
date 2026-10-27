# AGENTS.md — Contrato Operacional do Repositório

Este arquivo é a **fonte única de verdade operacional** para qualquer agente de IA (Cursor, Claude Code, Codex ou outro) que trabalhe neste repositório.

---

## 1. Estado Atual do Projeto

- **Nome do produto:** **Altare** (`D-023`, 2026-10-27). Princípio de marca: *"O altar no centro. A festa a serviço."* O diretório/repositório continua `wedding-planner`.
- **Fase atual:** `Implementação — Nível 0: Design System enxuto (Passo 0 e plano das etapas aprovados em 2026-10-27; **PAUSADO**, retoma na Etapa 0, a base do `apps/web`)` *(Fases 1 a 5 e `D-001` a `D-018` aprovadas em 2026-10-24; stack em `D-020`/`D-021` e arquitetura/identidade/design system em `D-022`, em 2026-10-26; nome em `D-023`, pacote de identidade visual em `D-024`, identidade + design system **aprovados** em `D-025`, produto não confessional em `D-026` e arquitetura **aprovada** em `D-027`, em 2026-10-27; implementação **autorizada** e design system **enxuto** em `D-028`, em 2026-10-27)*
- **Status de código/arquitetura:** **NENHUM CÓDIGO GERADO AINDA.** Implementação autorizada em `D-028`, começando pelo `apps/web` mínimo do Bloco 0.1 (monorepo pnpm, Vite + React + TypeScript, Tailwind v4, Vitest, Biome e `tsc`) e pelo **Bloco 0.2 enxuto**: tokens do tema claro gerados do `tokens.json`, ativos de marca copiados, 15 primitivos, casca de navegação com seletor de lente e 7 áreas-esqueleto, e vitrine `/design-system` mínima. Etapas: (a) tokens e fontes → (b) ativos de marca → (c) primitivos → (d) casca e esqueletos → (e) vitrine, cada uma validada com lint, *typecheck* e testes antes da seguinte. **Fora desta sessão:** API, banco, login e PWA. **Adiados com gatilho** (`D-028`): tema escuro, componentes de domínio, *snapshots* visuais, `axe` automatizado, script anti-*hex*, impressão. Stack (`docs/engineering/stack.md`), arquitetura (`docs/engineering/architecture.md`, `D-027`), identidade e design system (`D-025`, reduzido por `D-028`) aprovados. Em paralelo, o **detalhamento de features por área** está em andamento (`D-029`): `docs/product/features/planejamento-e-caminhos.md` está **aprovado**; `docs/product/features/convidados-enxoval-e-dia-d.md` (parte Convidados, `D-030`) está **aprovada**; `docs/product/features/cronograma.md` (`D-031`) está **aprovado**; `docs/product/features/orcamento-e-simulador.md` (`D-032`) está **aprovado**; `docs/product/features/possibilidades-e-decisoes.md` (`D-033`) está **aprovado**; `docs/product/features/contatos.md` (Bloco 3.1, `D-034`) está **aprovado**; `docs/product/features/propostas-por-categoria.md` (Bloco 3.2, `D-035`) está **aprovado**; `docs/product/features/contratos-e-parcelas.md` (Bloco 3.3, `D-036`) está **aprovado**; a parte Enxoval de `docs/product/features/convidados-enxoval-e-dia-d.md` (Bloco 4.1, `D-037`) está **aprovada**; `docs/product/features/centro-de-comando.md` e a parte Dossiê de `docs/product/features/convidados-enxoval-e-dia-d.md` (Bloco 4.2, `D-038`) estão **aprovados**: o **detalhamento de features da v1 manual (Níveis 1 a 4) está concluído** (`D-029` a `D-038`). Restam, fora da v1, a camada de IA (Nível 5) e o plano de implantação e backup. Não há perguntas em aberto.
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
3. **Comece pela Etapa 0** (monorepo pnpm e `apps/web` com Vite, React 19, TypeScript, Tailwind v4, Vitest, Biome e `tsc`; scripts `lint`, `typecheck` e `test` verdes) e siga as etapas (a) a (e) do **Bloco 0.2 enxuto** (`D-028`), uma de cada vez, só avançando com lint, *typecheck* e testes verdes. O detalhamento de features da v1 manual (`D-029` a `D-038`) está **concluído**; consulte `docs/product/features/` ao construir cada bloco. Valores de marca vêm só de `docs/design/identidade-visual/tokens.json`; o `tokens.css` é gerado, nunca editado à mão. Componentes de domínio só nascem no bloco que os usa.

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
