# Guia de Engenharia Pós-Congelamento (`docs/engineering/README.md`)

> **Status:** **CONCEITO CONGELADO (`D-017` em 2026-10-24).**
>
> Este documento consolida tudo o que foi decidido nas Fases 1 a 5 em `docs/product/` e `docs/design/` para orientar a arquitetura de software e a implementação, sem inventar premissas fora do que foi acordado.

---

## 1. Diretrizes Gerais para a Implementação

1. **Escopo Pessoal do Casal (`D-002`):** O sistema é construído para uso real de um único casamento com dois perfis nomeados (`Noivo` e `Noiva`), além da visão combinada (`Casal / Ambos`). Não adicionar complexidade multi-tenant/SaaS na v1.
2. **Zero Dados Hardcoded do Casamento:** Data, cidade, formato, número de convidados e teto de orçamento são entidades configuráveis que começam no estado `Em definição` e evoluem para `Definido`.
3. **Postura Responsiva Dupla (`D-003`):**
   - **Desktop-first para decisão conjunta:** Tabelas comparativas multi-colunas, simulador de múltiplos orçamentos em paralelo e visualização lateral de PDFs.
   - **Mobile-first para consulta e captura rápida:** Cartões verticais de leitura rápida, foco em *Próximo Passo*, link direto `wa.me` para WhatsApp, upload rápido de PDF e registro de avaliação individual.
4. **Fluxo Manual 100% Completo na v1 (`D-005`):** Nenhum fluxo da v1 pode depender de LLM/IA para funcionar. A camada de IA (v1.1) deve se acoplar sobre o mesmo modelo de dados.

---

## 2. Entidades de Domínio que o Banco de Dados / Estado Deve Suportar

Conforme especificado em `docs/design/experience.md`, o modelo de dados deve implementar 10 objetos centrais:

1. **`Profile` (`Noivo`, `Noiva`, `Ambos`):** Autoria de registros, responsabilidade sobre tarefas/próximos passos/parcelas e avaliações individuais.
2. **`WeddingBaseline` & `ScopeCategory`:**
   - Variáveis base do casamento (`Em definição` vs. `Definido`).
   - Categorias do casamento com status `Entra (Essencial)`, `Talvez (Se couber)`, `Em discussão` ou `Fica de fora` (com motivo registrado e avaliação de prioridade do Noivo e da Noiva).
3. **`BudgetScenario` & `BudgetCategoryLine` (`D-009`):**
   - Suporte a **múltiplos cenários completos de orçamento em paralelo** (ex.: *Cenário Praia*, *Cenário Campo*, *Cenário Cidade*), onde exatamente um pode ser marcado como `Oficial / Ativo` (promovível/trocável a qualquer momento).
   - Quatro métricas por categoria e no consolidado: `Planejado (Teto)`, `Estimado`, `Contratado` e `Realizado (Pago)`.
   - Suporte a linhas de custo fixo ou custo variável *per capita* (multiplicado automaticamente pela contagem do cenário ou da `GuestList`).
4. **`Milestone` & `ScheduleTask` (Cronograma com Dependências):**
   - Organizados em 5 fases lógicas, funcionando tanto em *Modo Sem Data* (puramente por grafo de dependência) quanto em *Modo Com Data* (com prazos e contagem regressiva).
   - Relação de dependência explícita (`dependsOn`): destaca o que está `Destravado` vs. `Bloqueado`.
5. **`Contact` / `Vendor` & `InteractionLog`:**
   - Ficha do fornecedor/pessoa, status no funil (`Para contatar` $\rightarrow$ `Contratado`/`Descartado`), anexos (PDFs/links), linha do tempo datada com autoria e campo obrigatório/destacado de **`NextStep` (Próximo Passo Único)** com ação, data-alvo e responsável.
6. **`Possibility` (Dois Níveis — `D-007`) & `ComparableCostItem`:**
   - Nível 1: `MacroScenario` (caminhos macro no marco zero, vinculáveis a um `BudgetScenario`).
   - Nível 2: `VendorProposal` (propostas de fornecedores por `ScopeCategory`).
   - **Normalizador de Custo Comparável:** `Preço Base` + $\sum$ `Custos Extras/Ocultos Necessários` (gerador, ECAD, rolha, horas extras, etc.) = `Custo Total Real Comparável`.
   - **Avaliação Dupla (`D-012`):** Para `Noivo` e para `Noiva` separadamente: classificação (`Favorito`, `Gostei`, `Com ressalvas`, `Descartaria`) + nota numérica (`1 a 5`) + comentário livre.
7. **`DecisionRecord`:**
   - Registra a escolha de uma `Possibilidade` e o descarte das concorrentes com **Motivo da Escolha** e **Motivo do Descarte**.
   - Dispara efeitos em cadeia: atualiza a coluna `Contratado` da categoria no orçamento ativo, destrava dependências do cronograma e alimenta o `Dossiê do Dia D`.
8. **`Contract` & `PaymentInstallment` (Parcelas):**
   - PDF do contrato assinado, responsável no Dia D, combinados operacionais críticos e lista de parcelas (vencimento, valor, meio de pagamento, status `Pendente`/`Pago`, comprovante e pagador).
9. **`GuestHousehold` (Núcleo Familiar) & `Guest`:**
   - Agrupamento por família/núcleo, lado (`Noivo`, `Noiva`, `Comum`), faixa (`Adulto`, `Criança pagante`, `Criança isenta`), probabilidade (`Certeza`, `Provável`, `Fase 2`) e status (`Rascunho`, `Convidado`, `Confirmado`, `Não irá`).
   - Cálculo em tempo real de *Total Nominal*, *Estimado Ponderado* e *Confirmados*.
10. **`TrousseauGiftItem` (Enxoval & Lista de Presentes — `D-006`):**
    - Cômodo/categoria, descrição, prioridade, valor estimado, link de referência, destino (`Pedir na lista` vs. `Comprar nós mesmos`), status (`Precisamos`, `Na lista`, `Já ganhamos`, `Já compramos`) e quem presenteou.
    - Exportadores nativos para **CSV/Planilha** (para importar em sites externos) e **Texto/Visão Formatada** (para envio direto aos convidados).

> **Visão Consolidada `DayOfDossier` (Dossiê do Dia D — `D-001`):** Projeção/relatório vivo (exportável/imprimível) agregando todos os contratos fechados, contatos do dia, itens contratados, saldos a pagar no dia do evento, resumo de convidados e observações para o(a) cerimonialista do dia.

---

## 3. Pontos de Extensão para a Camada de IA (v1.1 — `D-005`, `D-008`, `D-010`, `D-013`)

A arquitetura deve prever dois padrões distintos de integração de IA para a fase pós-v1:

1. **Mutação Assistida (Sempre via Rascunho + Confirmação Humana Explícita):**
   - *Entrevista Guiada por IA (`D-010`):* gera payload de proposta de `ScopeCategory` + `MacroScenario` + `BudgetScenario` em estado de prévia (`draft`), aplicando no banco somente após aprovação do usuário.
   - *Extrator de PDF/WhatsApp e Equalizador de Comparação:* gera prévia de `Possibility` e `ComparableCostItem` para revisão humana antes da persistência.
2. **Execução Proativa / Somente-Leitura (`D-008` + `D-013`):**
   - *Revisor Geral do Planejamento:* job de leitura que cruza `GuestList`, `BudgetScenario`, `ScopeCategory`, `Contract` e `ScheduleTask` gerando alertas/diagnósticos sem alterar registros do casamento.
   - *Notificações Personalizadas:* dispatcher preparado para entregar avisos direcionados ao `Noivo` e à `Noiva` via **Painel In-App**, **Web Push (PWA/Mobile)** e **WhatsApp**.

---

## 4. Tokens de Design System (`D-015` + `D-016` — Editorial Acolhedor & Estruturado)

- **Superfícies:** Canvas Papel Areia (`#F9F5EC`), Cartões Marfim Quente (`#FFFDF9`), Agrupamento Champagne (`#F5EFE2` / `#EFE7D6`), Bordas Amêndoa (`#DFD5C3`).
- **Textos:** Primário Carvão Oliva (`#232A22`), Secundário Musgo (`#5C6158`).
- **Acentos e Semântica:** Primário Oliva Profundo (`#3A4B3C`), Consenso/Sucesso Sálvia (`#E4ECE4` / `#2B422E`), Destaque/Custo Comparável Terracota (`#B5563C` / `#98442D`), Atenção/Divergência Argila Clara (`#F6E6E0` / `#8A3C27`).
- **Tipografia:**
  - `--font-serif` (ex.: *Instrument Serif* / *Newsreader* / *Playfair Display*) em títulos de página e nomes de espaços/fornecedores/cenários nos cartões;
  - `--font-sans` (ex.: *Plus Jakarta Sans* / *DM Sans*) na interface, tabelas e controles;
  - `--font-mono` com `font-variant-numeric: tabular-nums` (ex.: *JetBrains Mono* / *Geist Mono*) em todos os valores de orçamento, custo comparável e notas.

---

## 5. Stack Técnica & Estratégia de Persistência (`D-019` revista por `D-020`)

> **A stack detalhada e granular está em [`docs/engineering/stack.md`](./stack.md).** O texto original de `D-019` (Next.js + Drizzle/Prisma + Supabase + Vercel) foi **parcialmente substituído em 2026-10-26**.

Resumo das decisões travadas em `D-020`:

1. **Backend:** Python (FastAPI + SQLAlchemy 2 + Alembic), monólito modular.
2. **Frontend:** React + TypeScript + Vite como **SPA/PWA estática** (instalável no celular, ampla no desktop), com tipos gerados do OpenAPI da API.
3. **Dados e arquivos (Local $\rightarrow$ Nuvem):** **SQLite local** + PDFs em disco nos Níveis 0 e 1, atrás de uma interface `FileStorage`; migração para **PostgreSQL gerenciado + storage S3-compatível** quando o Nível 1 estiver utilizável (com regras de portabilidade e portão de testes em Postgres — `stack.md` §4).
4. **Perfis de acesso:** **dois logins individuais** (`Noivo` e `Noiva`); o seletor de perfil alterna a *lente de visão* (`Visão do Casal` / `Minha visão`) e a autoria vem sempre da sessão.

> **Arquitetura:** Clean Architecture pragmática em [`architecture.md`](./architecture.md) (`D-022`). **Design:** [`identity.md`](../design/identity.md) e [`design-system.md`](../design/design-system.md).

---

## 6. Ordem de Construção (Pirâmide de Blocos — `D-018`)

O cronograma lógico de construção (sem datas e prazos, organizado dos blocos mais básicos na base até os mais avançados no topo) está aprovado e documentado em **[`docs/engineering/roadmap.md`](./roadmap.md)**.

- **Ponto de partida da próxima sessão de implementação:** `Nível 0 — Fundação Técnica, Identidade do Casal e Design System` (`Bloco 0.1` e `Bloco 0.2`).
