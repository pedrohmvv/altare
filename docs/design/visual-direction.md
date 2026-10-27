# Direção Visual (`visual-direction.md`)

> **Status:** Aprovado na **Fase 4 (Direção Visual)** em 2026-10-24 (decisões `D-015` e `D-016`).

---

## 1. Personalidade Visual: Editorial Acolhedor & Estruturado (`D-016`)

A interface combina a **atmosfera de um caderno/revista autoral de casamento contemporâneo** com o **rigor analítico de uma ferramenta moderna de decisão e finanças**:

- **Sensação Tátil de Papel Quente:** Em vez de fundos brancos frios ou cinzas corporativos, a aplicação vive sobre uma superfície de **papel creme/areia perceptível (`#F9F5EC`)**, com cartões em **marfim quente (`#FFFDF9`)** e divisórias amendoadas (`#DFD5C3`).
- **Identidade Editorial nos Protagonistas:** Os títulos de página, os nomes dos cenários macro e os **nomes dos espaços e fornecedores dentro dos cartões** usam tipografia com **serifa clássica/editorial**, reforçando que o casal está construindo a história do próprio casamento.
- **Rigor Estrutural nos Dados:** Dentro de cada cartão ou tabela, as métricas financeiras (*Preço de capa*, *Extras*, *Custo comparável*, *Planejado vs. Contratado*) e as notas do casal (`4,8 / 5`) usam tipografia **monoespaçada/tabular** sobre blocos em tom champagne/areia (`#F5EFE2`), garantindo leitura rápida e comparação exata.

> **Extensão `D-022` (2026-10-26):** a identidade é detalhada em [`identity.md`](./identity.md) e o sistema de componentes em [`design-system.md`](./design-system.md). Passa a existir um **tema escuro opcional ("Noite Oliva")** — o que `D-015` rejeitou foi o *dark-mode estrito*, não um tema escuro alternativo. Extensões de token (`border-strong`, `ink-subtle`, `primary-hover`) e a regra de texto terracota pequeno (`accent-ink`) nasceram da auditoria de contraste.

### O que a Direção Visual Evita Explicitamente:
- **Não é um ERP/planilha corporativa fria:** Sem azul bancário, cinza hospitalar ou cara de software contábil.
- **Não é um portal de casamento kitsch/ornamental:** Sem fontes cursivas ilegíveis, laços decorativos, excesso de sombras ou rosa/dourado saturado que canse a vista.

---

## 2. Princípios de Interface e Densidade de Informação

1. **Calma Visual em Dados Densos:** Orçamentos em paralelo e comparativos de 3 a 5 fornecedores exibem muitos números. A interface usa espaçamento generoso, caixas de resumo em tom areia (`#F5EFE2`) e alinhamento tabular rigoroso, abrindo detalhes extensos (como leitura de PDFs e histórico completo) em painéis laterais ou gavetas.
2. **Consenso e Divergência sem Ansiedade:** Nas comparações entre `Noivo` e `Noiva`, o acordo visual (*"Consenso Favorito"*) aparece em verde-oliva/sálvia suave (`#E4ECE4` com texto `#2B422E`), enquanto divergências (*"Conversar juntos"*) ou alertas de custo extra aparecem em terracota suave (`#F6E6E0` com texto `#8A3C27`) — sempre como convite ao diálogo, nunca como "erro vermelho".
3. **Custo Real Comparável em Primeiro Plano:** O **Custo Total Comparável** (preço base + custos extras obrigatórios) recebe destaque pelo **tamanho e pelo mono** (`ink`, 24 px), enquanto os **custos extras** que o compõem aparecem em terracota escuro (`#98442D`) com ícone e sinal `+`, como na aplicação "Comparar propostas" do guia (págs. 34 e 40, `D-054`), impedindo que um preço de capa artificialmente baixo engane o casal.
4. **Dupla Postura (Desktop Confortável vs. Mobile Focado — `D-003`):**
   - **No Computador:** Layout multi-colunas para planejar juntos, comparar propostas e cenários de orçamento lado a lado e visualizar dependências do cronograma.
   - **No Celular:** Cartões verticais escaneáveis com alvos de toque amplos (mínimo 44px), priorizando o *Próximo Passo*, o *Custo Comparável* e o atalho direto para abrir conversa no WhatsApp.

---

## 3. Sistema de Cores Oficial (`D-015` + `D-016`)

| Papel Semântico | Nome do Tom | Hex Oficial | Onde é aplicado |
| :--- | :--- | :--- | :--- |
| **Fundo Principal (Canvas)** | Papel Areia | `#F9F5EC` | Fundo geral da aplicação (sensação acolhedora de caderno/editorial). |
| **Superfície de Cartão / Tabela** | Marfim Quente | `#FFFDF9` | Cartões de possibilidades, linhas de orçamento, fichas de fornecedores. |
| **Superfície Secundária (Agrupamento)** | Champagne / Areia Escura | `#F5EFE2` / `#EFE7D6` | Blocos internos de preço comparável, cabeçalhos de tabela e tags editoriais. |
| **Bordas e Divisórias** | Amêndoa Suave | `#DFD5C3` / `#E2D9C8` | Contornos de cartões, caixas de avaliação do casal e linhas divisórias. |
| **Texto Primário** | Carvão Oliva | `#232A22` | Títulos em serifa, nomes de fornecedores e textos principais (alto contraste). |
| **Texto Secundário / Apoio** | Musgo Acinzentado | `#5C6158` | Subtítulos, categorias, datas e observações secundárias. |
| **Cor Primária / Estrutura & Consenso** | Oliva Profundo | `#3A4B3C` | Botões primários, abas ativas, marcos concluídos e orçamento oficial ativo. |
| **Superfície de Consenso / Sucesso** | Sálvia Suave | `#E4ECE4` (texto `#2B422E`) | Selo *"Consenso Favorito"*, itens dentro do teto do orçamento e parcelas quitadas. |
| **Cor de Destaque / Custo Real & Atenção** | Terracota | `#B5563C` / `#98442D` | Custos extras do Custo Total Comparável, alertas de custo, divergências para conversar e próximos passos urgentes. |
| **Superfície de Atenção / Divergência** | Argila Clara | `#F6E6E0` (texto `#8A3C27`) | Selos de atenção (*"1 extra pendente"*, *"Avaliações divergentes"*, *"Acima do teto"*). |

---

## 4. Tipografia e Hierarquia (`D-015` + `D-016`)

> **Fontes definitivas (`D-025`):** Newsreader, Plus Jakarta Sans e JetBrains Mono. As demais citadas abaixo são as referências originais de `D-015`/`D-016` e não são mais candidatas.

1. **Família Editorial (`Serif`) — Títulos e Protagonistas:**
   - *Referências de fonte:* `Instrument Serif`, `Newsreader`, `Playfair Display` ou `Lora` (com fallback `Georgia, serif`).
   - *Onde usar:*
     - Títulos das 7 áreas principais e cabeçalho do casamento;
     - **Nomes dos espaços, fornecedores e cenários macro dentro dos cartões**;
     - Tags de destaque editorial (em itálico suave) e cabeçalhos do Dossiê do Dia D.
2. **Família de Interface (`Sans-Serif`) — Estrutura, Leitura e Controles:**
   - *Referências de fonte:* `Plus Jakarta Sans`, `DM Sans` ou `Inter`.
   - *Onde usar:* Navegação, botões, filtros, rótulos de formulários, descrições de itens inclusos/exclusos, comentários do Noivo e da Noiva e linha do tempo de contatos.
3. **Família Numérica (`Tabular / Monospace`) — Orçamento, Comparação e Notas:**
   - *Referências de fonte:* `JetBrains Mono` ou `Geist Mono` com `font-variant-numeric: tabular-nums`.
   - *Onde usar:* Todos os valores monetários (`R$ 28.000`, `+ R$ 4.800`, `R$ 32.800`), colunas do Simulador de Orçamentos, contagens de convidados e notas individuais (`4,8 / 5`).

---

## 5. Tom de Voz e Microcopy (`D-015`)

- **Personalidade verbal:** Parceiro calmo, organizado e direto. Fala com o casal (`vocês`) ou com o perfil ativo (`Noivo` / `Noiva`).
- **Exemplos de aplicação:**
  - *Próximo passo na Home:* `"Próximo passo de vocês: confirmar se a taxa do ECAD entra no contrato até sexta-feira."`
  - *Comparação de Orçamento:* `"Este espaço fica R$ 2.200 abaixo do teto planejado no Cenário Campo."`
  - *Divergência de avaliação:* `"Vocês avaliaram esta opção de forma diferente (Noivo: Favorito · Noiva: Com ressalvas). Vale conversar antes da visita."`
  - *Botões de ação:* Verbos diretos e claros (`"Registrar decisão"`, `"Adicionar custo extra"`, `"Promover a orçamento oficial"`, `"Exportar lista de presentes"`).
