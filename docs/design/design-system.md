# Design System (`docs/design/design-system.md`)

> **Produto:** **Altare** (`D-023`). Identidade oficial em `docs/design/identity.md`.
>
> **Status:** **Aprovado pelo usuário em 2026-10-27 (`D-025`)**. Linguagem de forma (cantos moderados) e tema claro + escuro em `D-022` (2026-10-26). Mudanças a partir daqui exigem nova decisão registrada.
>
> **Escopo enxuto (`D-028`, 2026-10-27):** design system proporcional a um app pessoal de duas pessoas. O Bloco 0.2 constrói **tema claro, 15 primitivos, casca de navegação e uma vitrine mínima** (§13). §8 e §9 continuam como **inventário de referência**: o restante nasce no bloco que o usa. Tema escuro, *snapshots* visuais, `axe` automatizado, script anti-*hex* e impressão foram **adiados com gatilho** (§13).
>
> Implementa `docs/design/visual-direction.md` e `docs/design/identity.md` (cores, fontes, marca, ornamento) em tokens, componentes e padrões. Este documento é a **especificação do Bloco 0.2** do roadmap.

---

## 1. Princípios do Design System

1. **Tokens primeiro:** nenhum valor de cor, espaçamento, raio ou tipografia é escrito direto em componentes; tudo vem de tokens.
2. **Primitivos neutros, componentes de domínio opinativos:** `components/ui` não conhece o produto (inclui `Money`, formatador puro, `D-028`); `components/domain` fala a língua do casal (`RatingPair`, `ConsensusBadge`).
3. **Dupla postura nativa (`D-003`):** todo componente nasce com comportamento **desktop** e **mobile** definidos (alvos de toque ≥ 44 px, gaveta lateral vs. folha inferior).
4. **Acessível por padrão:** WCAG 2.2 AA; foco visível; cor nunca é o único sinal.
5. **Calma visual:** hairlines em vez de sombras; espaçamento generoso; sem ruído decorativo.
6. **Um só lugar para cada coisa:** um componente por conceito; variantes por *props*, não por cópia.

---

## 2. Arquitetura do Design System

```
Tokens (CSS variables)  →  Primitivos UI (shadcn/Radix re-estilizados)  →  Componentes de Domínio  →  Padrões de Página
 styles/tokens.css          components/ui/*                                  components/domain/*        features/*/pages
```

- **Distribuição:** dentro do repositório (`apps/web/src/components`), **não** como pacote publicado (uso pessoal, `D-002`).
- **Base:** shadcn/ui (código copiado) sobre Radix, **totalmente re-estilizado** com os tokens. Nenhum componente é usado "de fábrica".
- **Acesso à vitrine:** `/design-system` não está no menu aprovado; em desenvolvimento há um link discreto no pé da barra lateral, ausente na versão publicada (`D-053`).
- **Vitrine:** rota interna `/design-system` **mínima** (tokens, tipografia e cada primitivo com variantes e estados, no tema claro). Cresce junto com os componentes (`D-028`).
- **Dados de exemplo:** a vitrine e os testes usam **dados claramente fictícios e rotulados** ("Espaço Exemplo", "Fornecedor Exemplo"). Nunca dados reais ou inventados do casamento (`AGENTS.md`).

---

## 3. Tokens e Tema

### 3.1 Nomenclatura (semântica, não literal)
Valores de cada papel (claro e escuro) estão em `docs/design/identity.md` §3.3. Os tokens são expostos como variáveis CSS e mapeados ao Tailwind v4.

> **Nível 0 (`D-028`):** o gerador emite **só o bloco claro** (`:root, [data-theme="light"]`). O bloco `[data-theme="dark"]` abaixo é a especificação para quando o tema escuro for pedido; como os componentes usam apenas nomes semânticos, ele entra sem retrabalho.

```css
/* styles/tokens.css */
:root, [data-theme="light"] {
  color-scheme: light;
  --canvas: #F9F5EC;   --surface: #FFFDF9;  --surface-muted: #F5EFE2;  --surface-sunken: #EFE7D6;
  --border: #DFD5C3;   --border-strong: #8F846F;
  --ink: #232A22;      --ink-muted: #5C6158; --ink-subtle: #6F7367;
  --primary: #3A4B3C;  --primary-hover: #2F3E31; --primary-ink: #FFFDF9;
  --consensus-bg: #E4ECE4; --consensus-ink: #2B422E;
  --accent: #B5563C;   --accent-ink: #98442D;
  --attention-bg: #F6E6E0; --attention-ink: #8A3C27;
  --focus-ring: #3A4B3C; --scrim: rgb(35 42 34 / .45);
}
[data-theme="dark"] {
  color-scheme: dark;
  --canvas: #151A15;   --surface: #1C231C;  --surface-muted: #252E25;  --surface-sunken: #2E382D;
  --border: #3A4439;   --border-strong: #6B7868;
  --ink: #F1ECDF;      --ink-muted: #B3B7A8; --ink-subtle: #9AA08F;
  --primary: #B7CDB0;  --primary-hover: #C9DBC3; --primary-ink: #151A15;
  --consensus-bg: #22332A; --consensus-ink: #C3DCC3;
  --accent: #C8664A;   --accent-ink: #E69A80;
  --attention-bg: #3B231C; --attention-ink: #F2BBA8;
  --focus-ring: #B7CDB0; --scrim: rgb(0 0 0 / .60);
}

@theme inline {            /* Tailwind v4: expõe como bg-canvas, text-ink, border-border-strong… */
  --color-canvas: var(--canvas);        --color-surface: var(--surface);
  --color-surface-muted: var(--surface-muted); --color-surface-sunken: var(--surface-sunken);
  --color-border: var(--border);        --color-border-strong: var(--border-strong);
  --color-ink: var(--ink);              --color-ink-muted: var(--ink-muted); --color-ink-subtle: var(--ink-subtle);
  --color-primary: var(--primary);      --color-primary-hover: var(--primary-hover); --color-primary-ink: var(--primary-ink);
  --color-consensus-bg: var(--consensus-bg); --color-consensus-ink: var(--consensus-ink);
  --color-accent: var(--accent);        --color-accent-ink: var(--accent-ink);
  --color-attention-bg: var(--attention-bg); --color-attention-ink: var(--attention-ink);
  --font-serif: "Newsreader", Georgia, serif;
  --font-sans:  "Plus Jakarta Sans", system-ui, sans-serif;
  --font-mono:  "JetBrains Mono", ui-monospace, monospace;
}
```

### 3.2 Mecanismo de tema (claro / escuro / sistema)
> **Adiado (`D-028`), gatilho: quando o usuário pedir.** No Nível 0 o `<html>` recebe `data-theme="light"` fixo e não há alternador. A especificação abaixo vale quando o escuro entrar.

- Atributo **`data-theme`** no `<html>`; três modos do usuário: `claro`, `escuro`, `sistema` (padrão).
- **Script inline mínimo no `index.html`** lê `localStorage.theme` e `prefers-color-scheme` **antes da primeira pintura** (evita *flash* de tema errado).
- Alternador no **menu do usuário**; preferência salva **por dispositivo** (`localStorage`). Persistir por usuário no servidor fica como evolução.
- Atualizar `<meta name="theme-color">` a cada troca.
- Textura de papel e sombras de overlay aplicadas só no claro (`[data-theme="light"]`).

### 3.3 Regras de uso de cor em componentes
- Texto pequeno terracota = `text-accent-ink`. `bg-accent` apenas em preenchimentos, ícones e textos grandes.
- Controles interativos usam `border-border-strong`; `border-border` é só divisória.
- `consensus-*` = acordo, dentro do teto, parcela paga. `attention-*` = divergência, extra pendente, acima do teto, erro. **Nunca vermelho.**
- Sem cor por perfil: `Noivo` e `Noiva` se distinguem por **rótulo** (§9.1).

---

## 4. Tipografia (escala)

| Token | Família | Tamanho/entrelinha (desktop → mobile) | Peso | Uso |
| :--- | :--- | :--- | :---: | :--- |
| `display` | Serifa | 40/48 → 32/40 | 500 | Título de página e do Dossiê |
| `title` | Serifa | 32/40 → 28/36 | 500 | Título de seção principal |
| `heading` | Serifa | 24/32 → 22/30 | 500 | Subseções, cabeçalho de cenário |
| `name` | Serifa | 20/28 | 500 | **Nome de espaço/fornecedor/cenário em cartões** |
| `body-lg` | Sans | 18/28 | 400 | Introduções |
| `body` | Sans | 16/24 | 400/500 | Texto e controles (**mínimo 16 px em campos no mobile**, evita *zoom* do iOS) |
| `body-sm` | Sans | 14/20 | 400/500 | Metadados, tabelas densas |
| `eyebrow` | Sans | 12/16, maiúsculas, `tracking .08em` | 600 | Rótulo acima de títulos |
| `num-xl` | Mono | 24/32 | 500 | Totais em `StatBlock` |
| `num-lg` | Mono | 20/28 | 500 | Custo comparável em cartões |
| `num` | Mono | 16/24 | 400 | Valores em linhas |
| `num-sm` | Mono | 14/20 | 400 | Valores em tabelas densas |

Todo token mono aplica `font-variant-numeric: tabular-nums`. Largura máxima de leitura de texto corrido: **68 caracteres**.

---

## 5. Espaço, Forma, Profundidade e Layout

| Categoria | Valores |
| :--- | :--- |
| **Espaçamento** (base 4 px) | `1`=4 · `2`=8 · `3`=12 · `4`=16 · `5`=20 · `6`=24 · `8`=32 · `10`=40 · `12`=48 · `16`=64 |
| **Raios** (`D-022` — cantos moderados) | `control`=6 px (botões, campos, badges retangulares) · `card`=10 px (cartões, overlays, gavetas) · `thumb`=8 px (miniaturas) · `pill`=9999 (chips e avatares) |
| **Bordas** | `1px solid border` (divisória) · `1px solid border-strong` (controle) · foco: anel duplo (§7) |
| **Profundidade** | Nível 0: **plano + hairline** (cartões, tabelas) · Nível 1 (popover/menu): `0 4px 16px rgb(35 42 34/.08)` + hairline · Nível 2 (diálogo/gaveta): `0 12px 32px rgb(35 42 34/.12)`. **Escuro: sem sombra**; profundidade por degraus de `surface` |
| **Z-index** | `sticky`=10 · `nav`=20 · `drawer`=30 · `modal`=40 · `popover`=50 · `toast`=60 |
| **Breakpoints** | `sm` 640 · `md` 768 · `lg` 1024 · `xl` 1280 · `2xl` 1536 |
| **Alturas de controle** | `sm` 32 (denso, desktop) · `md` 40 (padrão desktop) · `lg` 48 (padrão mobile). Com `pointer: coarse`, nenhum alvo < 44 px |

### Casca do aplicativo (shell)
| Faixa | Layout |
| :--- | :--- |
| **≥ 1024 (desktop)** | Barra lateral fixa de 256 px (marca, 7 áreas e, separado por uma hairline ao fim, o **Assistente**, `D-050`) + barra superior (título da área, **seletor de lente**, menu do usuário) + conteúdo (máx. 1200 px; tabelas comparativas usam largura total) |
| **768–1023 (tablet)** | Barra lateral recolhida em trilho de ícones (72 px) |
| **< 768 (mobile)** | Barra superior compacta + **barra inferior** com 4 destinos + "Mais" + botão flutuante **"+ Registrar Rápido"** (Bloco 3.1). O **ícone flutuante do assistente** fica acima da barra inferior; a convivência dos dois é a `OQ-IA-001`, item 5 |

---

## 6. Movimento (tokens)

| Token | Valor |
| :--- | :--- |
| `motion-fast` | 150 ms, `cubic-bezier(.2,.8,.2,1)` |
| `motion-base` | 220 ms, `cubic-bezier(.2,.8,.2,1)` (entrada) / `cubic-bezier(.4,0,1,1)` (saída) |
| `motion-delight` | 400 ms, apenas no selo de "decisão registrada" |
| `prefers-reduced-motion` | Todas as transições viram *fade* instantâneo (≤ 1 ms) |

---

## 7. Acessibilidade (requisitos)

1. **WCAG 2.2 AA** em todas as telas, nos dois temas. Contrastes auditados em `identity.md` §3.4.
2. **Foco visível:** anel duplo — 2 px `focus-ring` + 2 px de espaçador na cor do fundo (`canvas`/`surface`). Nunca `outline: none` sem substituto.
3. **Teclado completo:** tabelas navegáveis, menus e diálogos com *trap* de foco (Radix), `Esc` fecha overlays, atalhos documentados.
4. **Semântica:** `lang="pt-BR"`, *landmarks* (`nav`, `main`, `aside`), *skip link* "Ir para o conteúdo", tabelas com `caption`, `th scope`.
5. **Anúncios:** *toasts* em `aria-live="polite"`; erros de formulário ligados por `aria-describedby`.
6. **Alvos de toque ≥ 44 × 44 px** no mobile; espaçamento mínimo de 8 px entre alvos.
7. **Reflow:** sem rolagem horizontal até 320 px (exceto tabela comparativa, que rola dentro do próprio contêiner com primeira coluna fixa). Zoom de 200% sem perda.
8. **Cor + ícone + texto** para qualquer estado semântico.
9. **Verificação (`D-028`):** **manual** (teclado, foco visível, contraste) a cada componente e tela, mais as regras de acessibilidade do **Biome** no lint. `axe` automatizado está adiado (gatilho em §13). Os requisitos acima continuam valendo como critério de revisão.

---

## 8. Inventário de Componentes Primitivos (`components/ui`)

Estados mínimos de todo componente interativo: *default · hover · focus-visible · active · disabled · loading (quando aplicável) · error (campos)*.

**Inventário de referência.** No Bloco 0.2 entram só `Button`, `Input`, `Textarea`, `Select`, `Checkbox`, `Badge`, `Card`, `Dialog`, `Table`, `Tabs`, `Tooltip`, `Toast`, `EmptyState`, `PageHeader` e `Money` (§9) (`D-028`). Os demais nascem quando a primeira tela que os usa for construída.

| Componente | Variantes / API | Notas |
| :--- | :--- | :--- |
| **Button** | `primary` · `secondary` (contorno `border-strong`) · `ghost` · `soft-destructive` (argila) · `link`; tamanhos `sm/md/lg/icon`; `loading` | Verbo direto no rótulo ("Registrar decisão"). Botão só-ícone exige `aria-label` |
| **Input / Textarea** | Rótulo **acima**, ajuda, erro com ícone; `prefix`/`suffix` | Placeholder em `ink-subtle`, nunca substitui rótulo. O mecanismo comum (rótulo, ajuda, erro, `aria-describedby`) é o `Field` interno (`D-046`) |
| **Select / Combobox** | Pesquisável (fornecedores, categorias) | No mobile abre como folha inferior. **No Bloco 0.2 o `Select` é o Radix Select estilizado, com a lista aberta pelo app** (`D-047`, que revisa o `Select` nativo de `D-046`); a versão pesquisável é o `Combobox`, adiado |
| **Checkbox · Radio · Switch** | Com rótulo clicável | Alvo 44 px no mobile |
| **SegmentedControl** | 2–5 opções | Base do seletor de lente e das classificações |
| **Tabs** | Horizontal; no mobile rolável | Abas das áreas (ex.: Orçamento Ativo / Simulador / Pagamentos) |
| **Badge** | `neutral` · `consensus` · `attention` · `primary` · `outline`; com ícone | Selos "Consenso Favorito", "1 extra pendente", "Acima do teto" |
| **Tag editorial** | Itálico serifa, `surface-muted` | Etiquetas de categoria/estilo |
| **Avatar** | Inicial em `pill` `surface-sunken` | Sem cor por perfil |
| **Card** | `default` · `interactive` (hover com `border-strong`) · `muted` | Plano, sem sombra, raio `card` |
| **Table** | Densidade `comfortable`/`compact`; cabeçalho sticky; **primeira coluna fixa** opcional; números à direita | Cabeçalho em `surface-muted`, sans 12 px |
| **Dialog / AlertDialog** | Centralizado desktop, folha inferior mobile | AlertDialog para ações destrutivas, explicando o que fica salvo |
| **Sheet / Drawer** | **Lateral direita (desktop)**, **folha inferior (mobile)** | Detalhes, histórico, PDF, formulários rápidos |
| **Popover · Tooltip · DropdownMenu** | Radix | Tooltip nunca é a única fonte de informação crítica |
| **Toast** | `success` · `attention` · `info`; 4 s; ação opcional "Desfazer" | Posição: topo-direita (desktop), acima da barra inferior (mobile) |
| **Skeleton · Progress** | `surface-muted` | Sem *spinner* de tela cheia |
| **Separator · ScrollArea · Accordion** | Hairline 1 px | — |
| **EmptyState** | Ilustração botânica pequena + título + descrição + 1 ação | Texto acolhedor |
| **PageHeader** | Eyebrow + título serifa + apoio + ações + hairline | Padrão de `identity.md` §5 |

---

## 9. Componentes de Domínio (`components/domain`)

**Nenhum componente de domínio é construído no Bloco 0.2** (`D-028`). Esta tabela é a especificação de referência: cada componente **nasce no bloco que o usa**, como componente puro (só *props*, sem API nem regra de negócio). Duas exceções de lugar: **`Money` vive em `components/ui`** (formatador puro, construído no Bloco 0.2) e o **seletor de lente** faz parte da casca de navegação (§13).

| Componente | Responsabilidade | Detalhes de especificação |
| :--- | :--- | :--- |
| **`Money`** | Exibir valores em centavos | Mono tabular, `R$` + U+00A0, vírgula decimal. `precision`: `auto` (sem centavos se inteiro, em cartões e resumos) · `always` (tabelas financeiras, parcelas) · ~~`none`~~ (não construído: nenhuma tela o pede e arredondar na exibição faria o total divergir das linhas, `D-048`). `tone`: `default` · `comparable` (`accent-ink`, destaque do custo real) · `muted` · `positive` (dentro do teto) · `attention`. `signed` mostra `+`/`−` (extras e diferenças) |
| **`MoneyInput`** | Entrada de valor | Máscara pt-BR, armazena **centavos inteiros**, alinhado à direita, mono; nunca `float` |
| **`ProfileChip`** | Mostrar autoria/responsável | Avatar com inicial + rótulo `Noivo`/`Noiva`; **`Ambos`** = dois avatares sobrepostos. Sem cor por perfil |
| **`ProfileLensSwitcher`** | Alternar `Visão do Casal` / `Minha visão` | `SegmentedControl` na barra superior; estado persistido em URL/preferência |
| **`ConsensusBadge`** | Indicador de alinhamento do casal (`D-012`) | Estados: *Consenso Favorito* (sálvia, `heart-handshake`) · *Conversar juntos* (argila, `messages-square`) · *Ambos descartariam* (neutro) · *Aguardando avaliação* (neutro, mostra quem falta) |
| **`RatingPair`** | Avaliação individual dupla | Duas colunas (`Noivo`, `Noiva`): classificação em `SegmentedControl` (`Favorito`/`Gostei`/`Com ressalvas`/`Descartaria`) + nota **1–5 em botões numéricos mono** (não estrelas) + comentário. Edita apenas a coluna do usuário logado; a do outro é leitura (`D-021`) |
| **`ComparableCostBreakdown`** | Normalizador de custo comparável | Linhas: Preço de capa · `+` extras (cada um com rótulo e `Money signed`) · linha total em `Money tone="comparable"` + selo "1 extra pendente" quando aplicável. Mostra a mensagem do tom de voz (ex.: "abaixo/acima do teto") |
| **`ComparisonTable`** | Quadro lado a lado (3–5 colunas) | Colunas ≥ 280 px, primeira coluna fixa; linha "Custo real comparável" em destaque; linha de `RatingPair` resumido; realce de "Menor custo real" com `Badge consensus`; mobile vira cartões empilhados com abas deslizantes |
| **`NextStepCard`** | Próximo Passo Único | Ação, data-alvo (mono), `ProfileChip` responsável; urgente = `accent-ink` + `circle-arrow-right` |
| **`DependencyStatus`** | Cronograma | `Destravado` (sálvia, `lock-open`) / `Bloqueado` (neutro, `lock`) com *popover* "Aguardando: …" |
| **`ScenarioColumn`** | Simulador de orçamentos | Cabeçalho serifa, selo "Oficial/Ativo" (`badge-check`), totais Planejado/Estimado, custo por convidado, folga/estouro (`positive`/`attention`) |
| **`BudgetRow`** | Linha de orçamento de 4 colunas | Planejado · Estimado · Contratado · Realizado em mono; barra de uso sobre o teto (sálvia dentro; argila acima) |
| **`GuestCounters`** | Contadores de convidados | Três `StatBlock`: Total nominal · Estimado ponderado · Confirmados |
| **`InstallmentRow`** | Parcela | Vencimento, `Money`, meio de pagamento, `Badge` (Pendente/Pago), comprovante, pagador |
| **`FileAttachment`** | Anexo | Ícone, nome, tamanho (mono), abrir/baixar; suporta visualização no `Sheet` |
| **`WhatsAppButton`** | Abrir conversa | Link `https://wa.me/55…` normalizando telefone brasileiro; rótulo "Abrir WhatsApp"; alvo ≥ 44 px |
| **`QuickAddFab`** | "+ Registrar Rápido" (mobile) | Botão flutuante primário acima da barra inferior; abre `Sheet` com atalhos (novo contato, nota, anexar PDF) |
| **`PhaseHeader`** | Fase do cronograma | Eyebrow "Fase N" + título serifa + progresso mono |
| **`DecisionSeal`** | Momento de deleite | Selo sálvia com `check` (`motion-delight`) |

---

## 10. Padrões de Interface

1. **Formulários:** rótulo acima; ajuda abaixo; obrigatoriedade escrita ("obrigatório") em vez de asterisco; validação **ao sair do campo** e ao enviar; erro em argila com ícone e texto acionável; botão primário à direita no desktop, largura total no mobile; salvar não perde dados em erro.
2. **Detalhe lateral:** informações extensas (PDF, histórico, avaliação) abrem em `Sheet` lateral no desktop e folha inferior no mobile, **sem sair da lista**.
3. **Tabela comparativa:** primeira coluna fixa, cabeçalho fixo, rolagem horizontal contida; ordenação por custo comparável; destaque de divergências com `attention`.
4. **Filtros:** *chips* + estado na URL (compartilhável, volta do navegador funciona).
5. **Confirmações destrutivas:** `AlertDialog` explicando consequência e que o registro fica recuperável (exclusão lógica).
6. **Feedback:** *toast* para sucesso/ação reversível; erro persistente inline; ação com "Desfazer" quando segura.
7. **Estados vazios, carregando e erro:** conforme `identity.md` §9.
8. **Atalhos de teclado (desktop):** `g` + letra navega às áreas, `n` novo item, `/` busca (documentados na vitrine; opcionais na v1).

### 10.1 Navegação (aprovada em `D-025`, §14 item 1; Assistente acrescentado em `D-050`; ícones e celular conforme o guia em `D-052`)
| Posição | Desktop (barra lateral) | Ícone (Lucide) | Mobile (barra inferior) | Ícone no mobile |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Visão Geral | `layout-dashboard` | **Início** | `house` |
| 2 | Planejamento & Caminhos | `map` | **Possib.** (Possibilidades) | `scale` |
| 3 | Cronograma & Dependências | `calendar` | **Orçam.** (Orçamento) | `wallet` |
| 4 | Possibilidades & Decisões | `scale` | **Contatos** | `users` |
| 5 | Orçamento & Simulador | `wallet` | **Mais** → folha com a lente de visão, Planejamento, Cronograma, Convidados/Enxoval/Dia D e Assistente | `ellipsis` |
| 6 | Contatos & Fornecedores | `users` | — | — |
| 7 | Convidados, Enxoval & Dia D | `gift` | — | — |
| 8 | **Assistente** (separado por hairline; `D-050`) | `message-square-text` | Dentro de "Mais" | — |

Medidas do guia de identidade (aplicação "Visão Geral no desktop" e "Mobile"): barra lateral com itens de 40 px a cada 46 px, ícone de 20 px e rótulo de 12 px, ativo com fundo `surface-muted`, ícone `primary` e rótulo em seminegrito; barra superior de 72 px; barra inferior de 72 px, ícone de 22 px e rótulo de 12 px, ativo em `primary` e seminegrito. Os rótulos abreviados ("Possib.", "Orçam.") têm o nome completo para o leitor de tela. O ícone do Assistente, que não existe no guia, evita `message-circle` (WhatsApp) e `messages-square` (divergência).

Racional: no celular o casal consulta próximo passo, compara opções, abre WhatsApp e confere saldo (`D-003`); áreas de planejamento profundo ficam em "Mais" e continuam completas no desktop.

---

## 11. Conteúdo, Formatação e Microcopy

- Idioma único **pt-BR**; textos centralizados em constantes por feature (sem biblioteca de i18n).
- Tom conforme `visual-direction.md` §5 ("vocês", direto, acionável); botões com **verbo**.
- Formatos: `R$ 28.000` (resumos) · `R$ 28.000,00` (parcelas/pagamentos) · `4,8 / 5` · datas `26 out 2026` em listas e `26/10/2026` em tabelas · prazos relativos ("em 3 dias") com a data exata no `title`/tooltip.
- Estados em texto sempre completos ("Aguardando avaliação da Noiva"), nunca só ícone.

---

## 12. Implementação, Governança e Qualidade (enxuta, `D-028`)

| Item | Regra |
| :--- | :--- |
| **Fonte única de tokens** | `docs/design/identidade-visual/tokens.json` (`D-024`); `apps/web/src/styles/tokens.css` é **gerado** por script a partir dele e **nunca editado à mão**. Mudar um token = editar o `tokens.json`, regenerar o guia e o `tokens.css`. Um teste do Vitest falha se o `tokens.css` estiver desatualizado |
| **Tema** | Só o **claro** no Nível 0, com nomes semânticos e `data-theme="light"` no `<html>`. Escuro adiado (§13) |
| **Sem *hex* em componentes** | **Convenção documentada**: `#RRGGBB` só em `tokens.css` e nos SVGs de marca; componentes usam classes de token (`bg-surface`, `text-ink`). Sem script de CI por enquanto (gatilho em §13) |
| **Componentes puros** | Só recebem *props*: sem regra de negócio, sem chamada de API, sem acesso a `features` (`architecture.md` §11) |
| **Utilitário de classes** | `cn()` (`clsx` + `tailwind-merge`) e `cva` (`class-variance-authority`) para variantes |
| **Vitrine `/design-system`** | **Mínima**: tokens (cores com função), tipografia e cada primitivo com variantes e estados, no tema claro, legível em desktop e mobile. Ganha seções conforme os componentes surgem |
| **Testes** | Vitest + Testing Library para comportamento (variantes, estados, teclado onde houver lógica) e para a navegação da casca. **Sem *snapshots* visuais e sem `axe` no CI** |
| **Acessibilidade** | Verificação **manual** (teclado, foco, contraste) + regras de acessibilidade do Biome no lint (§7) |
| **Dados de exemplo** | Claramente fictícios e rotulados ("Espaço Exemplo"); nunca dados do casamento (`AGENTS.md`) |
| **Ativos de marca** | `apps/web/public/brand/`, **copiados** de `docs/design/identidade-visual/` (logos-mestre de `fonte/`, favicon de `componentes/favicon/`, ícones de `componentes/app-icon/`, ornamentos de `fonte/ornamentos/`); nada é redesenhado no app (ver `identity.md` §2.6). A cópia é gerada por `make brand` (`D-045`) e um teste falha se divergir do pacote |

---

## 13. Ordem de Construção do Bloco 0.2 (enxuta, `D-028`)

Pré-requisito: a parte do Bloco 0.1 que faz o `apps/web` existir (monorepo pnpm, Vite + React + TypeScript, Tailwind v4, Vitest, Biome e `tsc`). Cada etapa só começa com lint, *typecheck* e testes passando na anterior.

1. **Tokens e fontes:** `tokens.css` gerado do `tokens.json` (tema claro), mapeado em `@theme`; fontes autohospedadas (Fontsource); `cn()` e `cva`.
2. **Ativos de marca:** copiar do pacote `docs/design/identidade-visual/` para `public/brand/`; favicon e ícones no `index.html`.
3. **Primitivos (15), concluída em 2026-10-27 (`D-049`):** `Button`, `Input`, `Textarea`, `Select`, `Checkbox`, `Badge`, `Card`, `Dialog`, `Table`, `Tabs`, `Tooltip`, `Toast`, `EmptyState`, `PageHeader`, `Money` (mono tabular).
4. **Casca de navegação e esqueletos:** barra lateral (desktop), trilho de ícones (tablet), barra superior com o **seletor de lente** (`Casal` / `Minha visão`), barra inferior com 4 destinos + "Mais" (mobile, conforme §10.1) e as **8 áreas** (as 7 de `D-025` e o Assistente, `D-050`) como páginas-esqueleto com `EmptyState`. **Lote 1 (casca, rotas e seletor de lente) feito em `D-051`; o ícone flutuante do assistente é o lote 2.**
5. **Vitrine `/design-system`:** tokens, tipografia e cada primitivo com variantes e estados.

**Adiado, com gatilho para retomar:**

| Item | Gatilho |
| :--- | :--- |
| Tema escuro "Noite Oliva" (§3.1), alternador `claro / escuro / sistema` e script anti-*flash* (§3.2) | Quando o usuário pedir |
| Regressão visual por *snapshots* | Se houver regressões visuais recorrentes |
| `axe` automatizado (E2E ou vitrine) | Se houver regressões de acessibilidade recorrentes ou o produto se abrir a outros casais (`D-002`) |
| Script de CI/`pre-commit` contra *hex* | Se aparecer *hex* em componente mais de uma vez na revisão |
| Impressão (`@media print`, tokens de papel) | Bloco 4.2 (Dossiê do Dia D): **gatilho atingido no detalhamento** (`D-038`, `F-DOS-08`); entra na construção do Bloco 4.2 |
| Demais primitivos de §8 (`Radio`, `Switch`, `SegmentedControl`, `Avatar`, `Separator`, `Sheet`, `Popover`, `DropdownMenu`, `AlertDialog`, `Combobox`, `Tag`, `Skeleton`, `Progress`, `Accordion`, `ScrollArea`) e `MoneyInput` | Quando a primeira tela que o usa for construída |
| Componentes de domínio de §9 | No bloco que os usa |
| `QuickAddFab` ("+ Registrar Rápido") | Primeiro bloco com algo para registrar rápido (Bloco 3.1) |
| Menu do usuário | Com o login (restante do Bloco 0.1) |
| E2E de navegação com Playwright | Com o login (restante do Bloco 0.1) |

**Critério de conclusão do Bloco 0.2:** a vitrine mostra tokens, tipografia e todos os primitivos listados com variantes e estados, no tema claro, em desktop e mobile; as 7 áreas são navegáveis como esqueletos; o app segue a identidade do Altare.

---

## 14. Pontos Aprovados (`OQ-DS-001`, resolvida em `D-025`)
1. Navegação mobile: 4 destinos + "Mais" + botão flutuante (§10.1).
2. **Sem cor por perfil**; distinção por rótulo e inicial (§3.3, §9).
3. Nota 1–5 como **botões numéricos em mono** (não estrelas) no `RatingPair`.
4. Formatação monetária: sem centavos em resumos, com centavos em parcelas/pagamentos (§11).
5. Tema escuro **Noite Oliva** e alternador `claro / escuro / sistema` por dispositivo (§3.2). *(Construção adiada em `D-028` até o usuário pedir.)*
6. Escala tipográfica (§4) e alturas de controle (§5).
