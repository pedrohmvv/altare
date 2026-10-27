# AGENTS.md — Contrato Operacional do Repositório

Este arquivo é a **fonte única de verdade operacional** para qualquer agente de IA (Cursor, Claude Code, Codex ou outro) que trabalhe neste repositório.

---

## 1. Estado Atual do Projeto

- **Nome do produto:** **Altare** (`D-023`, 2026-10-27). Princípio de marca: *"O altar no centro. A festa a serviço."* O diretório/repositório continua `wedding-planner`.
- **Fase atual:** `Detalhamento de Arquitetura e Design System (Pré-Implementação)` *(Fases 1 a 5 e `D-001` a `D-018` aprovadas em 2026-10-24; stack em `D-020`/`D-021` e arquitetura/identidade/design system em `D-022`, em 2026-10-26; nome em `D-023`, pacote de identidade visual em `D-024`, identidade + design system **aprovados** em `D-025` e produto não confessional em `D-026`, em 2026-10-27)*
- **Status de código/arquitetura:** **NENHUM CÓDIGO GERADO AINDA.** Stack aprovada (`docs/engineering/stack.md`). Identidade visual (`docs/design/identity.md` + `docs/design/identidade-visual/`) e design system (`docs/design/design-system.md`) **aprovados** (`D-025`). Falta apenas `OQ-ENG-005` (`docs/engineering/architecture.md`); só após resolvida, iniciar o **Nível 0 — Bloco 0.1** (`docs/engineering/roadmap.md`).
- **Premissa de produto (`D-026`):** o Altare **não é só para casamentos católicos**, embora o autor seja católico. Produto e marca são não confessionais; o tipo de cerimônia (religiosa de qualquer tradição, civil ou simbólica) é um dado do casal, nunca presumido. Nenhum roteiro fixo de uma tradição na v1.

### Fases de Concepção (100% Concluídas)
1. **Entrevista** *(Concluída)* — Entender o casal, o momento do planejamento, o que já existe e o que mais dói hoje.
2. **Conceito** *(Concluída e Aprovada)* — Fechar problema, para quem é, o que faz, o que não faz, escopo (v1 vs. depois vs. fora) e como se diferencia de planilha, pasta e grupo de mensagens.
3. **Experiência** *(Concluída e Aprovada)* — Definir a jornada do casal, a arquitetura de informação, os objetos do produto e os fluxos principais.
4. **Direção visual** *(Concluída e Aprovada)* — Definir personalidade (`Editorial Acolhedor & Estruturado`), princípios de interface, cor, tipografia e tom (sem tela de alta fidelidade).
5. **Congelamento** *(Concluída e Aprovada em `D-017`)* — Conceito, stack (`D-019`) e pirâmide de desenvolvimento (`D-018`) confirmados pelo usuário.

### Como Retomar na Próxima Sessão
Quando o usuário pedir para começar a construir:
1. Leia `docs/engineering/README.md`, `docs/engineering/stack.md` e `docs/engineering/roadmap.md`.
2. Respeite a stack (`docs/engineering/stack.md`), a arquitetura (`docs/engineering/architecture.md`) e o design (`docs/design/identity.md`, `docs/design/design-system.md`) aprovados; qualquer desvio exige nova decisão registrada.
3. Inicie pelo **Nível 0 — Fundação Técnica, Identidade do Casal e Design System** (`Bloco 0.1` e `Bloco 0.2`), respeitando rigorosamente os tokens de `docs/design/visual-direction.md` e o modelo de domínio de `docs/design/experience.md`.

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
- `docs/engineering/roadmap.md` — Cronograma de desenvolvimento em Pirâmide de Blocos (do Nível 0 fundacional ao Nível 5 de IA, sem datas ou prazos).
