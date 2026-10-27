# Cronograma de Desenvolvimento em Pirâmide (`docs/engineering/roadmap.md`)

> **Status:** Definido em `D-018` (2026-10-24).
> **Regra de estrutura:** Organização em **Pirâmide de Blocos** (dos mais básicos e fundacionais na base até os mais avançados no topo), **sem datas ou prazos fixos** — guiada exclusivamente por dependências técnicas e de uso real do casal.

---

## Visão da Pirâmide de Construção

Cada nível da pirâmide se apoia diretamente no nível inferior e entrega valor utilizável para você e sua noiva assim que é concluído:

```
                      /\
                     /  \
                    / N5 \       Nível 5: Topo — Camada de IA (Extração, Entrevista, Revisão Geral e Notificações)
                   /------\
                  /   N4   \     Nível 4: Fechamento da v1 — Enxoval/Presentes, Centro de Comando e Dossiê do Dia D
                 /----------\
                /     N3     \   Nível 3: Negociação e Fechamento — Contatos, Comparador de Propostas e Contratos/Parcelas
               /--------------\
              /       N2       \ Nível 2: Decisão Macro e Bolso — Simulador de Orçamentos em Paralelo e Cenários Macro
             /------------------\
            /         N1         \ Nível 1: Base do Casamento — Definições, Mapa de Escopo, Convidados e Cronograma
           /----------------------\
          /           N0           \ Nível 0: Fundação — Design System Editorial, Perfis (Noivo/Noiva) e Banco/Storage
         /--------------------------\
```

---

## Nível 0 — Fundação Técnica, Identidade do Casal e Design System
*O alicerce invisível e visual para que todas as telas seguintes já nasçam no padrão certo no computador e no celular.*

### Bloco 0.1 — Estrutura Base, Banco de Dados e Perfis (`Noivo` / `Noiva` / `Casal`)
- **O que é construído:**
  - Setup do monorepo (`apps/api` em Python/FastAPI + `apps/web` em React/Vite) com SPA responsiva (PWA instalável no celular e ampla no desktop) — *revisado em `D-020`*.
  - Banco SQLite com migrações (Alembic) e `FileStorage` local para anexos (PDFs). No Nível 0, modelam-se apenas `User`, `Session` e `FileAsset` (`Profile` é enum); as demais entidades entram junto do bloco que as usa.
  - **Login individual** do `Noivo` e da `Noiva` (sem cadastro público) e **Seletor de lente (`Visão do Casal` / `Minha visão`)** persistente no topo da aplicação. Arquitetura Clean pragmática com `import-linter` (`docs/engineering/architecture.md`) e detalhes em `docs/engineering/stack.md` §11.

### Bloco 0.2 — Design System "Editorial Acolhedor & Estruturado" (`D-015` + `D-016`)
- **O que é construído:**
  - **Tema claro e escuro ("Noite Oliva", `D-022`)** com alternador `claro / escuro / sistema`; marca **Altare** (wordmark, símbolo "A sobre a mensa" e ícones PWA, `D-023`), com ativos copiados de `docs/design/identidade-visual/` e `tokens.css` gerado do `tokens.json` (`D-024`); vitrine `/design-system` com testes `axe` e *snapshots* visuais (`docs/design/identity.md` e `docs/design/design-system.md`).
  - Tokens de cor oficiais: fundo Papel Areia (`#F9F5EC`), cartões Marfim Quente (`#FFFDF9`), blocos Champagne (`#F5EFE2`), bordas Amêndoa (`#DFD5C3`), primário Oliva Profundo (`#3A4B3C`) e destaque Terracota (`#B5563C`).
  - Hierarquia tipográfica configurada: Serifa Editorial (títulos e nomes de espaços/fornecedores), Sans-Serif (controles e leitura) e Monospace Tabular (todos os valores financeiros e notas).
  - Componentes base reutilizáveis: cartões editoriais, tabelas comparativas, badges de consenso/divergência e casca de navegação das 7 áreas (Desktop + Mobile).
- **Critério de conclusão do Nível 0:** Você e sua noiva conseguem abrir o app no computador e no celular, entrar com o próprio login, alternar a lente (`Casal` / `Minha visão`) e o tema claro/escuro, e navegar pela estrutura visual pronta.

---

## Nível 1 — Base da Pirâmide: Definição do Casamento, Convidados e Rota (Marco Zero)
*Os blocos fundamentais que não dependem de ter fornecedores nem orçamentos fechados e permitem sair imediatamente do marco zero.*

### Bloco 1.1 — Definições Base & Mapa de Escopo do Casamento
- **O que é construído:**
  - Painel de **Definições Base** (data/época, cidade/região, formato, porte e teto macro) com suporte ao estado `Em definição` ou `Definido`.
  - **Mapa de Escopo do Casamento:** catálogo de frentes de um casamento brasileiro onde o Noivo e a Noiva avaliam prioridades e classificam cada categoria como `Entra (Essencial)`, `Talvez (Se couber)`, `Em discussão` ou `Fica de fora` (com registro do motivo do descarte).

### Bloco 1.2 — Lista Nominal de Convidados (Por Núcleo Familiar)
- **O que é construído:**
  - Cadastro de convidados agrupados por **Núcleo/Família**, lado (`Noivo`, `Noiva`, `Comum`), faixa (`Adulto`, `Criança pagante`, `Criança isenta`), probabilidade (`Certeza/Essencial`, `Provável`, `Fase 2`) e status (`Rascunho`, `Convidado`, `Confirmado`, `Não irá`).
  - Motor de **Contagem em Tempo Real** (*Total Nominal*, *Estimado Ponderado* e *Confirmados*) pronto para alimentar os cálculos do orçamento.

### Bloco 1.3 — Cronograma com Dependências Explícitas
- **O que é construído:**
  - Marcos e tarefas distribuídos nas 5 fases lógicas do planejamento, com atribuição de responsável (`Noivo`, `Noiva`, `Ambos`).
  - Motor de **Dependências (Bloqueios)**: destaca visualmente o que está **Destravado para agir agora** vs. o que está **Bloqueado por uma decisão anterior**.
  - Suporte ao *Modo Sem Data* (ordem lógica pura) e *Modo Com Data* (janelas recomendadas e contagem regressiva).
- **Critério de conclusão do Nível 1:** Vocês já conseguem usar o produto para definir o que entra e o que fica de fora do casamento, montar a lista nominal de convidados e enxergar a sequência de decisões destravadas.

---

## Nível 2 — Inteligência Financeira e Caminhos Macro
*Conecta o escopo e o tamanho da lista de convidados do Nível 1 ao bolso do casal, permitindo decidir o formato do casamento com segurança.*

### Bloco 2.1 — Orçamento Vivo & Simulador de Múltiplos Orçamentos em Paralelo (`D-009`)
- **O que é construído:**
  - Estrutura de orçamento por categoria ativa com as 4 colunas (*Planejado/Teto*, *Estimado*, *Contratado*, *Realizado/Pago*) e cálculo automático para itens cobrados *por convidado* (conectado ao Bloco 1.2).
  - **Simulador de Múltiplos Orçamentos em Paralelo:** criação, clonagem e comparação lado a lado de cenários financeiros completos (ex.: *Cenário Praia* vs. *Cenário Campo* vs. *Cenário Enxuto*), variando número de convidados, tetos e categorias `Talvez`.
  - Ação para promover qualquer cenário simulado a **Orçamento Oficial Ativo**.

### Bloco 2.2 — Possibilidades Nível 1: Comparador de Cenários Macro (`D-007`)
- **O que é construído:**
  - Comparação estruturada de caminhos iniciais do casamento (formato, localidade, logística para convidados, prós e contras) vinculados aos cenários do Simulador de Orçamentos.
  - **Avaliação Individual Dupla (`Noivo` e `Noiva` — `D-012`)** (`Favorito`/`Gostei`/`Ressalvas`/`Descartaria` + Nota 1–5 + Comentário) e **Registro da Decisão Macro** (atualizando as Definições Base e destravando o Cronograma).
- **Critério de conclusão do Nível 2:** Vocês conseguem simular orçamentos completos lado a lado e decidir o caminho macro do casamento sabendo exatamente o impacto financeiro.

---

## Nível 3 — Relacionamento com Fornecedores, Comparação de Propostas e Contratos
*Com o escopo e o orçamento ativos, este nível cobre a rotina de ir ao mercado cotar, equalizar propostas em PDF, decidir e gerenciar os pagamentos.*

### Bloco 3.1 — Contatos & Fornecedores com Próximo Passo Único
- **O que é construído:**
  - Ficha completa de fornecedores/contatos vinculada às categorias do escopo, com atalho direto para abrir conversa no WhatsApp (`wa.me`), Instagram/site e upload de arquivos/PDFs.
  - Funil de status (`Para contatar` $\rightarrow$ `Contratado`/`Descartado`), linha do tempo de interações datada com autoria (`Noivo` ou `Noiva`) e destaque para o **Próximo Passo Único** (ação, data-alvo e responsável).

### Bloco 3.2 — Possibilidades Nível 2: Comparador de Propostas & Custo Comparável (`D-007`, `D-012`)
- **O que é construído:**
  - Cadastro de propostas de fornecedores (permitindo múltiplos pacotes do mesmo fornecedor) com anexo e visualização do PDF original.
  - **Normalizador de Custo Comparável:** adição de custos ocultos/adicionais obrigatórios (ex.: gerador, ECAD, rolha, horas extras, mobiliário extra) ao preço base para exibir o **Custo Total Real Comparável**.
  - **Quadro Comparativo Lado a Lado** por categoria + **Avaliação Individual Dupla (`Noivo` e `Noiva`)** com detector visual de consenso/divergência.
  - **Registro de Decisão por Categoria:** escolha da proposta vencedora com motivo da escolha e do descarte das demais, atualizando automaticamente a coluna *Contratado* do Orçamento e destravando os marcos dependentes no Cronograma.

### Bloco 3.3 — Contratos Assinados & Cronograma de Pagamentos (Parcelas)
- **O que é construído:**
  - Ficha do contrato fechado (PDF assinado, contato responsável para o Dia D e combinados operacionais críticos).
  - Gestão de **Parcelas / Desembolso Mensal** (sinal, parcelas intermediárias e quitação final, meio de pagamento, status `Pendente`/`Pago`, comprovante e pagador), alimentando automaticamente a coluna *Realizado (Pago)* do Orçamento.
- **Critério de conclusão do Nível 3:** Vocês substituem 100% das planilhas de cotação e pastas soltas de PDF, gerenciando fornecedores, comparativos de propostas e parcelas de contratos em um só lugar.

---

## Nível 4 — Fechamento da v1 Manual: Enxoval, Centro de Comando e Dossiê do Dia D
*Consolida os módulos complementares e a visão integrada de ponta a ponta da primeira versão.*

### Bloco 4.1 — Enxoval da Casa Nova & Lista de Presentes Exportável (`D-006`)
- **O que é construído:**
  - Gestão de itens da casa nova e cotas por cômodo/categoria, prioridade, valor estimado, link de referência, destino (`Pedir na lista` vs. `Comprar nós mesmos`), status (`Precisamos`, `Na lista`, `Já ganhamos`, `Já compramos`) e registro de quem presenteou.
  - **Módulo de Exportação e Formatação:** geração de arquivo CSV/planilha (para importar em sites externos de presentes) e geração de lista formatada limpa para envio direto aos convidados.

### Bloco 4.2 — Centro de Comando (Home Desktop & Mobile) + Dossiê do Dia D (`D-001`)
- **O que é construído:**
  - **Visão Geral (Home):** painel executivo do casal no computador e visão rápida de bolso no celular (decisões destravadas da vez, próximos passos com fornecedores, próximas parcelas, resumo do orçamento ativo e contagem de convidados).
  - **Dossiê do Dia D:** visão consolidada e exportável/imprimível para o(a) cerimonialista do dia, reunindo automaticamente todos os contratos fechados, responsáveis no dia, itens contratados, saldos a pagar no dia do evento, resumo de convidados e observações críticas.
- **Critério de conclusão do Nível 4 (Marco de Entrega da v1 Completa):** Todo o fluxo manual planejado para a v1 está 100% operacional do Marco Zero até a entrega ao(à) cerimonialista do dia.

---

## Nível 5 — Topo da Pirâmide: Camada de Inteligência Artificial (v1.1+)
*Construído sobre o fluxo manual já validado e populado, dividindo-se nos dois regimes da decisão `D-008`.*

### Bloco 5.1 — IA de Mutação Assistida (Rascunhos com Confirmação Humana Obrigatória)
- **O que é construído:**
  - **Extrator de Propostas de PDF e Texto de WhatsApp:** leitura automática de orçamentos enviados por fornecedores, preenchendo um rascunho revisável de `Possibilidade` (preço à vista/parcelado, itens inclusos e taxas ocultas detectadas).
  - **Equalizador de Assimetrias na Comparação:** análise cruzada das propostas de uma mesma categoria apontando o que um fornecedor inclui e o outro cobra à parte, sugerindo ajustes no Custo Comparável.
  - **Entrevista Guiada por IA para Rascunho Inicial (`D-010`):** fluxo conversacional sobre perfil, gosto e prioridades do Noivo e da Noiva para sugerir rascunhos de escopo, cenários macro e divisão de orçamento.

### Bloco 5.2 — IA Proativa e Somente-Leitura (Revisão Geral & Notificações Personalizadas — `D-008`, `D-013`)
- **O que é construído:**
  - **Revisor Geral do Planejamento:** auditoria completa e não-destrutiva do casamento (cruzando capacidade de espaço vs. lista de convidados, categorias essenciais sem cotação, desvios de orçamento e lacunas operacionais nos contratos para o Dia D).
  - **Motor de Notificações Personalizadas (`D-013`):** envio de lembretes, resumos e alertas direcionados individualmente ao `Noivo` e à `Noiva` via **Painel In-App**, **Notificações Push (Mobile/PWA)** e **WhatsApp**.
- **Critério de conclusão do Nível 5:** O produto passa a contar com um "assessor inteligente" completo que elimina digitação braçal de propostas e audita proativamente o planejamento do casal.
