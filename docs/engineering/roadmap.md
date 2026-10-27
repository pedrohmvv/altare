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
- **Execução em duas partes (`D-028`):** primeiro, só o necessário para o `apps/web` existir (monorepo pnpm, Vite + React + TypeScript, Tailwind v4, Vitest, Biome e `tsc`), junto com o Bloco 0.2. Depois, em outra sessão, API, banco, login, PWA e o E2E com Playwright. O plano dessa segunda parte, em 4 PRs (esqueleto da API e CI; login; `files`; PWA e E2E), está em `D-059`; o PR 1 está feito (`D-060`).

### Bloco 0.2 — Design System "Editorial Acolhedor & Estruturado", versão enxuta (`D-015` + `D-016` + `D-028`)
- **O que é construído** (ordem e detalhes em `docs/design/design-system.md` §13):
  - **Tokens do tema claro**: `tokens.css` gerado do `tokens.json` (`D-024`), mapeado no Tailwind v4, com nomes semânticos prontos para o escuro entrar depois. Fontes autohospedadas: Serifa Editorial (títulos e nomes de espaços/fornecedores), Sans-Serif (controles e leitura) e Monospace Tabular (valores financeiros e notas).
  - **Marca Altare** (wordmark, símbolo "A sobre a mensa", favicon e ícones, `D-023`), copiada de `docs/design/identidade-visual/` para `public/brand/`, sem redesenho.
  - **15 primitivos** re-estilizados: `Button`, `Input`, `Textarea`, `Select`, `Checkbox`, `Badge`, `Card`, `Dialog`, `Table`, `Tabs`, `Tooltip`, `Toast`, `EmptyState`, `PageHeader` e `Money`.
  - **Casca de navegação** desktop e mobile, com seletor de lente (`Casal` / `Minha visão`) e as **8 áreas** (as 7 de `D-025` e o **Assistente**, `D-050`) como páginas-esqueleto, mais o ícone flutuante do assistente.
  - **Vitrine `/design-system`**: tokens, tipografia, o catálogo da identidade (`D-058`) e cada primitivo com variantes e estados, só em desenvolvimento (`D-057`). Acessibilidade verificada manualmente.
  - **Teste de regras de design** (`D-055`): barra cor, fonte e traço soltos em `src`; o mapa guia → componente (`design-system.md` §15) orientou as etapas (d), com o lote 2 feito em `D-056`, e (e).
  - **Não entram agora:** componentes de domínio (nascem no bloco que os usa), tema escuro, *snapshots* visuais, `axe` automatizado e impressão. Cada item tem gatilho registrado em `D-028`.
- **Critério de conclusão do Bloco 0.2:** a vitrine mostra tokens, tipografia e todos os primitivos com variantes e estados, no tema claro, em desktop e mobile; as 8 áreas são navegáveis como esqueletos; o app segue a identidade do Altare. **Cumprido em `D-057` (2026-10-27): o Bloco 0.2 está concluído.**
- **Critério de conclusão do Nível 0:** Você e sua noiva conseguem abrir o app no computador e no celular, entrar com o próprio login, alternar a lente (`Casal` / `Minha visão`) e navegar pela estrutura visual pronta. *(O alternador de tema saiu do critério em `D-028`; volta quando o tema escuro for pedido.)*

---

## Nível 1 — Base da Pirâmide: Definição do Casamento, Convidados e Rota (Marco Zero)
*Os blocos fundamentais que não dependem de ter fornecedores nem orçamentos fechados e permitem sair imediatamente do marco zero.*

### Bloco 1.1 — Definições Base & Mapa de Escopo do Casamento
- **O que é construído:**
  - Painel de **Definições Base** (data/época, cidade/região, formato, porte e teto macro) com suporte ao estado `Em definição` ou `Definido`.
  - **Mapa de Escopo do Casamento:** catálogo de frentes de um casamento brasileiro onde o Noivo e a Noiva avaliam prioridades e classificam cada categoria como `Entra (Essencial)`, `Talvez (Se couber)`, `Em discussão` ou `Fica de fora` (com registro do motivo do descarte).
  - *(Revisado em `D-029`; especificação em `docs/product/features/planejamento-e-caminhos.md`)* Definições Base com **tipo de cerimônia**; no Mapa de Escopo, prioridade individual em 3 níveis, **estimativa inicial**, **nota** e **referências** (links e imagens) por categoria.

### Bloco 1.2 — Lista Nominal de Convidados (Por Núcleo Familiar)
- **O que é construído:**
  - Cadastro de convidados agrupados por **Núcleo/Família**, lado (`Noivo`, `Noiva`, `Comum`), faixa (`Adulto`, `Criança pagante`, `Criança isenta`), probabilidade (`Certeza/Essencial`, `Provável`, `Fase 2`) e status (`Rascunho`, `Convidado`, `Confirmado`, `Não irá`).
  - Motor de **Contagem em Tempo Real** (*Total Nominal*, *Estimado Ponderado* e *Confirmados*) pronto para alimentar os cálculos do orçamento.
  - *(Revisado em `D-030`; especificação em `docs/product/features/convidados-enxoval-e-dia-d.md`)* Pesos editáveis por probabilidade, acompanhante (+1), idade da criança, contatos e endereço do núcleo, convite enviado por núcleo e **exportação em Excel/CSV** (dependência `openpyxl` no backend).

### Bloco 1.3 — Cronograma com Dependências Explícitas
- **O que é construído:**
  - Marcos e tarefas distribuídos nas 5 fases lógicas do planejamento, com atribuição de responsável (`Noivo`, `Noiva`, `Ambos`).
  - Motor de **Dependências (Bloqueios)**: destaca visualmente o que está **Destravado para agir agora** vs. o que está **Bloqueado por uma decisão anterior**.
  - Suporte ao *Modo Sem Data* (ordem lógica pura) e *Modo Com Data* (janelas recomendadas e contagem regressiva).
  - *(Revisado em `D-031`; especificação em `docs/product/features/cronograma.md`)* Catálogo inicial editável de 29 marcos, tarefas avulsas, checklist, anexos e links, e visão de calendário mensal.
- **Critério de conclusão do Nível 1:** Vocês já conseguem usar o produto para definir o que entra e o que fica de fora do casamento, montar a lista nominal de convidados e enxergar a sequência de decisões destravadas.

---

## Nível 2 — Inteligência Financeira e Caminhos Macro
*Conecta o escopo e o tamanho da lista de convidados do Nível 1 ao bolso do casal, permitindo decidir o formato do casamento com segurança.*

### Bloco 2.1 — Orçamento Vivo & Simulador de Múltiplos Orçamentos em Paralelo (`D-009`)
- **O que é construído:**
  - Estrutura de orçamento por categoria ativa com as 4 colunas (*Planejado/Teto*, *Estimado*, *Contratado*, *Realizado/Pago*) e cálculo automático para itens cobrados *por convidado* (conectado ao Bloco 1.2).
  - **Simulador de Múltiplos Orçamentos em Paralelo:** criação, clonagem e comparação lado a lado de cenários financeiros completos (ex.: *Cenário Praia* vs. *Cenário Campo* vs. *Cenário Enxuto*), variando número de convidados, tetos e categorias `Talvez`.
  - Ação para promover qualquer cenário simulado a **Orçamento Oficial Ativo**.
  - *(Revisado em `D-032`; especificação em `docs/product/features/orcamento-e-simulador.md`)* Base de convidados por cenário, fator da criança pagante, reserva para imprevistos, indicador de uso do teto e exportação em Excel/CSV. Contratado e Realizado são derivados e só chegam nos Blocos 3.2 e 3.3.

### Bloco 2.2 — Possibilidades Nível 1: Comparador de Cenários Macro (`D-007`)
- **O que é construído:**
  - Comparação estruturada de caminhos iniciais do casamento (formato, localidade, logística para convidados, prós e contras) vinculados aos cenários do Simulador de Orçamentos.
  - **Avaliação Individual Dupla (`Noivo` e `Noiva` — `D-012`)** (`Favorito`/`Gostei`/`Ressalvas`/`Descartaria` + Nota 1–5 + Comentário) e **Registro da Decisão Macro** (atualizando as Definições Base e destravando o Cronograma).
- *(Revisado em `D-033`; especificação em `docs/product/features/possibilidades-e-decisoes.md`)* O modelo de avaliação dupla, selo de consenso e decisão registrada é genérico e reaproveitado no Bloco 3.2.
- **Critério de conclusão do Nível 2:** Vocês conseguem simular orçamentos completos lado a lado e decidir o caminho macro do casamento sabendo exatamente o impacto financeiro.

---

## Nível 3 — Relacionamento com Fornecedores, Comparação de Propostas e Contratos
*Com o escopo e o orçamento ativos, este nível cobre a rotina de ir ao mercado cotar, equalizar propostas em PDF, decidir e gerenciar os pagamentos.*

### Bloco 3.1 — Contatos & Fornecedores com Próximo Passo Único
- **O que é construído:**
  - Ficha completa de fornecedores/contatos vinculada às categorias do escopo, com atalho direto para abrir conversa no WhatsApp (`wa.me`), Instagram/site e upload de arquivos/PDFs.
  - Funil de status (`Para contatar` $\rightarrow$ `Contratado`/`Descartado`), linha do tempo de interações datada com autoria (`Noivo` ou `Noiva`) e destaque para o **Próximo Passo Único** (ação, data-alvo e responsável).
  - *(Revisado em `D-034`; especificação em `docs/product/features/contatos.md`)* Tipos Fornecedor e Pessoa, visitas agendadas com data e hora no calendário do Cronograma, aviso de duplicidade e **busca global do app** (que cresce com as áreas seguintes).

### Bloco 3.2 — Possibilidades Nível 2: Comparador de Propostas & Custo Comparável (`D-007`, `D-012`)
- **O que é construído:**
  - Cadastro de propostas de fornecedores (permitindo múltiplos pacotes do mesmo fornecedor) com anexo e visualização do PDF original.
  - **Normalizador de Custo Comparável:** adição de custos ocultos/adicionais obrigatórios (ex.: gerador, ECAD, rolha, horas extras, mobiliário extra) ao preço base para exibir o **Custo Total Real Comparável**.
  - **Quadro Comparativo Lado a Lado** por categoria + **Avaliação Individual Dupla (`Noivo` e `Noiva`)** com detector visual de consenso/divergência.
  - **Registro de Decisão por Categoria:** escolha da proposta vencedora com motivo da escolha e do descarte das demais, atualizando automaticamente a coluna *Contratado* do Orçamento e destravando os marcos dependentes no Cronograma.
  - *(Revisado em `D-035`; especificação em `docs/product/features/propostas-por-categoria.md`)* Preço por pessoa ou total, custo por convidado equivalente, faixa de referência no Orçamento Ativo (sem alimentar o Estimado), uma decisão por categoria, reabertura da decisão e `Contratado` do fornecedor derivado.

### Bloco 3.3 — Contratos Assinados & Cronograma de Pagamentos (Parcelas)
- **O que é construído:**
  - Ficha do contrato fechado (PDF assinado, contato responsável para o Dia D e combinados operacionais críticos).
  - Gestão de **Parcelas / Desembolso Mensal** (sinal, parcelas intermediárias e quitação final, meio de pagamento, status `Pendente`/`Pago`, comprovante e pagador), alimentando automaticamente a coluna *Realizado (Pago)* do Orçamento.
- *(Revisado em `D-036`; especificação em `docs/product/features/contratos-e-parcelas.md`)* Contrato por decisão ou direto, dados do Dia D no contrato, assistente de plano de pagamento, Fluxo de Pagamentos (lista e calendário) com exportação Excel/CSV e o indicador "A pagar".
- **Critério de conclusão do Nível 3:** Vocês substituem 100% das planilhas de cotação e pastas soltas de PDF, gerenciando fornecedores, comparativos de propostas e parcelas de contratos em um só lugar.

---

## Nível 4 — Fechamento da v1 Manual: Enxoval, Centro de Comando e Dossiê do Dia D
*Consolida os módulos complementares e a visão integrada de ponta a ponta da primeira versão.*

### Bloco 4.1 — Enxoval da Casa Nova & Lista de Presentes Exportável (`D-006`)
- **O que é construído:**
  - Gestão de itens da casa nova e cotas por cômodo/categoria, prioridade, valor estimado, link de referência, destino (`Pedir na lista` vs. `Comprar nós mesmos`), status (`Precisamos`, `Na lista`, `Já ganhamos`, `Já compramos`) e registro de quem presenteou.
  - **Módulo de Exportação e Formatação:** geração de arquivo CSV/planilha (para importar em sites externos de presentes) e geração de lista formatada limpa para envio direto aos convidados.
  - *(Revisado em `D-037`; especificação na parte Enxoval de `docs/product/features/convidados-enxoval-e-dia-d.md`)* Cotas em dinheiro, recebimentos com quantidade (status e totais derivados), enxoval separado do Orçamento e lista formatada em texto para copiar e colar.

### Bloco 4.2 — Centro de Comando (Home Desktop & Mobile) + Dossiê do Dia D (`D-001`)
- **O que é construído:**
  - **Visão Geral (Home):** painel executivo do casal no computador e visão rápida de bolso no celular (decisões destravadas da vez, próximos passos com fornecedores, próximas parcelas, resumo do orçamento ativo e contagem de convidados).
  - **Dossiê do Dia D:** visão consolidada e exportável/imprimível para o(a) cerimonialista do dia, reunindo automaticamente todos os contratos fechados, responsáveis no dia, itens contratados, saldos a pagar no dia do evento, resumo de convidados e observações críticas.
- *(Revisado em `D-038`; especificação em `docs/product/features/centro-de-comando.md` e na parte Dossiê de `docs/product/features/convidados-enxoval-e-dia-d.md`)* Home com "Atenção agora" (regras fixas), "+ Registrar Rápido", exportação de todos os dados do casal, Dossiê com checklist de itens físicos, versões entregues e impressão pelo navegador.
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
### Bloco 5.3 — Assistente Conversacional (`D-042`)
- **O que é construído:**
  - **Servidor de *tools* do Altare:** cada *tool* chama um caso de uso da camada de aplicação, com a mesma autorização da API; escritas só por `ChangeProposal` (`D-008`).
  - **Três canais finos sobre o mesmo núcleo:** módulo de chat, ícone flutuante no canto inferior direito das demais áreas e WhatsApp (número vinculado a um dos dois usuários). **A área Assistente e o ícone flutuante já existem como casca desde o Bloco 0.2 (`D-050`); aqui entra o chat.**
  - **Schema legível por agente:** descrições em tabelas e colunas, *views* de leitura e busca aproximada. Pendências em `OQ-IA-001`.
- **Critério de conclusão do Nível 5:** O produto passa a contar com um "assessor inteligente" completo que elimina digitação braçal de propostas e audita proativamente o planejamento do casal.
