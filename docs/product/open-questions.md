# Perguntas em Aberto (`open-questions.md`)

> **Status Global:** **Uma pergunta em aberto, que não bloqueia a v1** (`OQ-IA-001`, camada de IA; o item 1, a navegação, foi resolvido em `D-050`). Concepção de produto (`D-001` a `D-018`), stack (`D-020`, `D-021`), identidade visual e design system (`D-025`), caráter não confessional do produto (`D-026`), arquitetura (`D-027`) escopo enxuto do design system (`D-028`) e o detalhamento de features da v1 manual (`D-029` a `D-038`) estão fechados. A implementação do Nível 0 foi autorizada em `D-028`.

---

## Perguntas Abertas

### OQ-IA-001 — Assistente Conversacional: Navegação, Detalhamento e Infraestrutura (`D-042`)
- **Por que importa:** o assistente por linguagem natural (chat no módulo, ícone flutuante e WhatsApp) entra no Nível 5, mas algumas escolhas mudam a navegação e a hospedagem.
- **O que falta decidir:**
  1. ~~O módulo de chat é uma **8ª área** da navegação ou só o ícone flutuante e uma tela de histórico?~~ **Resolvido em `D-050`:** as duas coisas. A área **Assistente** é a 8ª da navegação e o **ícone flutuante** existe nas demais áreas; a casca nasce na etapa (d) do Bloco 0.2, e o chat de verdade segue no Bloco 5.3.
  2. Detalhamento de features do Nível 5 (o que o assistente faz em cada área, no mesmo formato de `docs/product/features/`).
  3. **Busca aproximada** de fornecedores pelo nome que funcione igual em SQLite e em PostgreSQL.
  4. **WhatsApp:** custo, conta do WhatsApp Business e aprovação de modelos. O *webhook* exige o app publicado na nuvem (`stack.md` §9).
  5. **Canto inferior direito, convivência com o "+ Registrar Rápido"** (`QuickAddFab`, `design-system.md` §9): até o Bloco 3.1 o assistente é o único dono do canto (`D-050`). Quando o `QuickAddFab` for construído, decidir como os dois convivem (ex.: o assistente dentro do menu "Novo"). **Gatilho: Bloco 3.1.**
- **Bloqueia:** o item 5 bloqueia o Bloco 3.1 (`QuickAddFab`); os itens 2 a 4, apenas o Bloco 5.3. Nada da v1 manual depende disso (`D-005`).

---

## Perguntas Resolvidas (Histórico Completo)

### Concepção de Produto e Design (Fases 1 a 5)
- ~~**OQ-001 — Validação do Conceito e do Corte de Escopo da v1**~~ $\rightarrow$ **Resolvida em `D-008` a `D-011`**.
- ~~**OQ-002 — Profundidade da Lista de Presentes na v1**~~ $\rightarrow$ **Resolvida em `D-006`** (Enxoval/casa nova + rascunho exportável/formatável para site externo ou convidados).
- ~~**OQ-003 — Comparação de Possibilidades para Cenários Macro no Marco Zero**~~ $\rightarrow$ **Resolvida em `D-007`** (Possibilidades em dois níveis: Cenários Macro + Propostas de Fornecedores).
- ~~**OQ-004 — Validação da Arquitetura de Informação e dos Fluxos da Experiência**~~ $\rightarrow$ **Resolvida em `D-014`**.
- ~~**OQ-005 — Escala de Avaliação Individual nas Possibilidades**~~ $\rightarrow$ **Resolvida em `D-012`** (Classificação qualitativa + Nota 1 a 5 + Comentário).
- ~~**OQ-006 — Canal Preferido para as Notificações Personalizadas**~~ $\rightarrow$ **Resolvida em `D-013`** (Painel In-App, Push mobile/web e WhatsApp).
- ~~**OQ-007 — Escolha da Personalidade Visual**~~ $\rightarrow$ **Resolvida em `D-016`** (Opção A — Editorial Acolhedor & Estruturado).
- ~~**OQ-008 — Confirmação Final de Congelamento do Conceito (Fase 5)**~~ $\rightarrow$ **Resolvida em `D-017`** (Conceito congelado pelo usuário).

### Marca e Produto (Pós-Congelamento)
- ~~**OQ-DS-001 — Aprovação da Identidade Visual do Altare e do Design System**~~ $\rightarrow$ **Resolvida em `D-025`** (guia completo, `identity.md` e `design-system.md` aprovados como propostos; sem assinatura verbal; `heart-handshake` só no selo de consenso).
- ~~**OQ-PROD-001 — Casamento Católico como Eixo do Escopo e do Cronograma**~~ $\rightarrow$ **Resolvida em `D-026`** (o produto não é só para casamentos católicos; o tipo de cerimônia é um dado do casal; nenhum roteiro fixo de uma tradição na v1; a cerimônia entra pelas categorias neutras do Mapa de Escopo, com marcos editáveis).

### Planejamento de Engenharia (Pós-Congelamento)
- ~~**OQ-ENG-005 — Aprovação do Detalhamento da Arquitetura**~~ $\rightarrow$ **Resolvida em `D-027`** (`docs/engineering/architecture.md` aprovada como está; implementação só quando o usuário pedir).
- ~~**OQ-ENG-001 — Stack, Hospedagem e Persistência**~~ $\rightarrow$ **Resolvida em `D-019`**, **parcialmente revista em `D-020`** (backend Python, SPA React, SQLite inicial, nuvem após o Nível 1, login individual).
- ~~**OQ-ENG-002 — Ordem de Construção da v1**~~ $\rightarrow$ **Resolvida em `D-018`** (Pirâmide de Blocos do Nível 0 ao Nível 5 sem datas ou prazos, documentada em `docs/engineering/roadmap.md`).
- ~~**OQ-ENG-003 — Aprovação do Detalhamento da Stack**~~ $\rightarrow$ **Resolvida em `D-021`** (`docs/engineering/stack.md` aprovada integralmente).
- ~~**OQ-ENG-004 — Impactos do Login Individual na Experiência**~~ $\rightarrow$ **Resolvida em `D-021`** (cada um avalia na própria sessão; avaliações visíveis de imediato; seletor com `Casal` e `Minha visão`).
