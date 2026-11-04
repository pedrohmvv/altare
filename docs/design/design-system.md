# Design System (`docs/design/design-system.md`)

> **Produto:** **Altare** (`D-023`). Identidade oficial em `docs/design/identity.md`.
>
> **Status:** **Aprovado pelo usuário em 2026-10-27 (`D-025`)**. Linguagem de forma (cantos moderados) e tema claro + escuro em `D-022` (2026-10-26). Mudanças a partir daqui exigem nova decisão registrada.
>
> **Escopo enxuto (`D-028`, 2026-10-27):** design system proporcional a um app pessoal de duas pessoas. O Bloco 0.2 constrói **tema claro, 15 primitivos, casca de navegação e uma vitrine mínima** (§13). §8 e §9 continuam como **inventário de referência**: o restante nasce no bloco que o usa. Tema escuro, *snapshots* visuais, `axe` automatizado e impressão foram **adiados com gatilho** (§13); o script anti-*hex* foi ativado como teste de regras de design em `D-055` (§12).
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
- **Acesso à vitrine:** `/design-system` não está no menu aprovado e **só existe em desenvolvimento** (`D-053`, `D-057`): há um link discreto no pé da barra lateral, e a rota e o link somem da versão publicada, onde a URL cai na página não encontrada.
- **Vitrine:** rota interna `/design-system`, **definitiva** desde `D-057` (tokens, tipografia e cada primitivo com variantes e estados, no tema claro), com o **catálogo da identidade** (arranjos da marca, arco, ramo, ícones, favicon e ícone do app e as peças do Dossiê, `D-058`) e um índice em duas partes, Identidade e Componentes. Cresce junto com os componentes (`D-028`).
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
- Alternador no **cartão da sessão** (`D-061`) ou onde o usuário decidir quando o tema escuro entrar; preferência salva **por dispositivo** (`localStorage`). Persistir por usuário no servidor fica como evolução.
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
| `ui` | Sans | 15/22 | 400/600 | Botões, linhas de cartão e descrições de estado (`D-054`) |
| `body-sm` | Sans | 14/20 | 400/500 | Metadados, tabelas densas |
| `ui-sm` | Sans | 13/18 | 400/600 | Selos, lente de visão e rótulos de apoio (`D-054`) |
| `eyebrow` | Sans | 12/16, maiúsculas, `tracking .08em` | 600 | Rótulo acima de títulos |
| `ui-xs` | Sans | 11/14 | 500/600 | Rótulo da barra inferior no celular (`D-054`) |
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
| **Raios** (`D-022` — cantos moderados) | `control`=6 px (botões, campos) · `card`=10 px (cartões, overlays, gavetas) · `thumb`=8 px (miniaturas) · `pill`=9999 (selos/badges, chips e avatares, `D-054`) |
| **Bordas** | `1px solid border` (divisória) · `1px solid border-strong` (controle) · foco: anel duplo (§7) |
| **Profundidade** | Nível 0: **plano + hairline** (cartões, tabelas) · Nível 1 (popover/menu): `0 4px 16px rgb(35 42 34/.08)` + hairline · Nível 2 (diálogo/gaveta): `0 12px 32px rgb(35 42 34/.12)`. **Escuro: sem sombra**; profundidade por degraus de `surface` |
| **Z-index** | `sticky`=10 · `nav`=20 · `drawer`=30 · `modal`=40 · `popover`=50 · `toast`=60 |
| **Breakpoints** | `sm` 640 · `md` 768 · `lg` 1024 · `xl` 1280 · `2xl` 1536 |
| **Alturas de controle** | **Botão:** `sm` 32 (denso, desktop) · `md` 40 (padrão; **44 no celular**) · `lg` 48. **Campos** (`Input`, `Select`): **44 em qualquer tela**, como no guia (`D-054`, revisa `D-025`). Com `pointer: coarse`, nenhum alvo < 44 px |

### Casca do aplicativo (shell)
| Faixa | Layout |
| :--- | :--- |
| **≥ 1024 (desktop)** | Barra lateral fixa de 256 px (marca, 7 áreas e, separado por uma hairline ao fim, o **Assistente**, `D-050`) + barra superior (título da área e **seletor de lente**; a sessão fica no pé da barra lateral, `D-061`) + conteúdo (máx. 1200 px; tabelas comparativas usam largura total) |
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
| **Chip** | Pílula de escolha com `aria-pressed` (apertado = `primary`; solto = `surface` com `border-strong`); `disabled`; sem variantes | Filtro de lista (`D-068`, `D-074`, `D-084`): estado na URL, cada filtro empurra uma entrada de histórico; 44 px no toque e 8 px entre chips. Sobe para `components/ui` no terceiro uso (`D-084`) |
| **Tabs** | Horizontal; no mobile rolável | Abas das áreas (ex.: Orçamento Ativo / Simulador / Pagamentos) |
| **Badge** | `neutral` (`surface-sunken` com `ink-muted`) · `consensus` · `attention` · `primary` · `outline`; com ícone | **Pílula** de 26 px, 13 px em seminegrito, como os selos do guia (págs. 34 e 38 a 40). Selos "Consenso Favorito", "1 extra pendente", "Acima do teto" |
| **Tag editorial** | Itálico serifa, `surface-muted` | Etiquetas de categoria/estilo |
| **Avatar** | Inicial em `pill` `surface-sunken` | Sem cor por perfil |
| **Card** | `default` · `interactive` (hover com `border-strong`) · `muted` | Plano, sem sombra, raio `card` |
| **Table** | Densidade `comfortable`/`compact`; cabeçalho sticky; **primeira coluna fixa** opcional; números à direita | Cabeçalho em `surface-muted`, sans 12 px |
| **Dialog / AlertDialog** | Centralizado desktop, folha inferior mobile | AlertDialog para ações destrutivas, explicando o que fica salvo. **`AlertDialog` existe desde `D-085`** (Radix): mesmo desenho e camada do `Dialog`, mas **sem o botão Fechar** e sem fechar por clique fora; o foco entra no Cancelar; o Esc fecha; confirmar é um `Button` comum (não fecha sozinho: a tela mostra a escrita pendente e o erro do servidor dentro do diálogo); a prop `pending` bloqueia o Esc com a escrita no ar (quem usa desabilita o Cancelar com o mesmo estado); o destrutivo é `soft-destructive` (argila, nunca vermelho) |
| **Sheet / Drawer** | **Lateral direita (desktop)**, **folha inferior (mobile)** | Detalhes, histórico, PDF, formulários rápidos |
| **Popover · Tooltip · DropdownMenu** | Radix. **`Popover` existe desde `D-056`**: cartão ancorado, nível 1 da pág. 32, não modal, com título, descrição opcional e Fechar | Tooltip nunca é a única fonte de informação crítica |
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
| **`Money`** | Exibir valores em centavos | Mono tabular, `R$` + U+00A0, vírgula decimal. `precision`: `auto` (sem centavos se inteiro, em cartões e resumos) · `always` (tabelas financeiras, parcelas) · ~~`none`~~ (não construído: nenhuma tela o pede e arredondar na exibição faria o total divergir das linhas, `D-048`). `tone`: `default` · `comparable` (`accent-ink`, para os custos extras, `+ R$`; o total comparável usa `default` em `num-xl`, `D-054`) · `muted` · `positive` (dentro do teto) · `attention`. `signed` mostra `+`/`−` (extras e diferenças); o sinal vem **separado do `R$` por espaço não separável** (`+ R$ 1.200,00`, guia págs. 28 e 34) |
| **`MoneyInput`** | Entrada de valor | Máscara pt-BR, armazena **centavos inteiros**, alinhado à direita, mono; nunca `float` |
| **`ProfileChip`** | Mostrar autoria/responsável | Avatar com inicial + rótulo `Noivo`/`Noiva`; **`Ambos`** = dois avatares sobrepostos. Sem cor por perfil |
| **`ProfileLensSwitcher`** | Alternar `Visão do Casal` / `Minha visão` | `SegmentedControl` na barra superior; estado persistido em URL/preferência |
| **`ConsensusBadge`** | Indicador de alinhamento do casal (`D-012`) | Estados: *Consenso Favorito* (sálvia, `heart-handshake`) · *Conversar juntos* (argila, `messages-square`) · *Ambos descartariam* (neutro) · *Aguardando avaliação* (neutro, mostra quem falta) |
| **`RatingPair`** | Avaliação individual dupla | Duas colunas (`Noivo`, `Noiva`): classificação em `SegmentedControl` (`Favorito`/`Gostei`/`Com ressalvas`/`Descartaria`) + nota **1–5 em botões numéricos mono** (não estrelas) + comentário. Edita apenas a coluna do usuário logado; a do outro é leitura (`D-021`) |
| **`ComparableCostBreakdown`** | Normalizador de custo comparável | Linhas: Preço de capa · `+` extras (cada um com rótulo e `Money signed`) · linha total em `Money` `default`, `num-xl`, sobre `surface-muted` (a terracota fica só nos extras, guia págs. 34 e 40, `D-054`) + selo "1 extra pendente" quando aplicável. Mostra a mensagem do tom de voz (ex.: "abaixo/acima do teto") |
| **`ComparisonTable`** | Quadro lado a lado (3–5 colunas) | Colunas ≥ 280 px, primeira coluna fixa; linha "Custo real comparável" em destaque; linha de `RatingPair` resumido; realce de "Menor custo real" com `Badge consensus`; mobile vira cartões empilhados com abas deslizantes |
| **`NextStepCard`** | Próximo Passo Único | Ação, data-alvo (mono), `ProfileChip` responsável; urgente = `accent-ink` + `circle-arrow-right` |
| **`DependencyStatus`** | Cronograma | `Destravado` (sálvia, `lock-open`) / `Bloqueado` (neutro, `lock`), com o motivo "Aguardando: …" em **texto visível** abaixo do título (revisto em `D-081`: um *popover* esconderia a informação do teclado e do toque, e o §8 diz que o `Tooltip` nunca é a única fonte) |
| **`ScenarioColumn`** | Simulador de orçamentos | Cabeçalho serifa, selo "Oficial/Ativo" (`badge-check`), totais Planejado/Estimado, custo por convidado, folga/estouro (`positive`/`attention`) |
| **`BudgetRow`** | Linha de orçamento de 4 colunas | Planejado · Estimado · Contratado · Realizado em mono; barra de uso sobre o teto (sálvia dentro; argila acima) |
| **`GuestCounters`** | Contadores de convidados | Três `StatBlock`: Total nominal · Estimado ponderado · Confirmados |
| **`InstallmentRow`** | Parcela | Vencimento, `Money`, meio de pagamento, `Badge` (Pendente/Pago), comprovante, pagador |
| **`FileAttachment`** | Anexo | Ícone, nome, tamanho (mono), abrir/baixar; suporta visualização no `Sheet`. **Hoje** vive em `features/schedule/components/attachments.tsx` (`D-085`), como o `WhatsAppButton` em `features/guests`: sobe para `components/domain` quando um segundo bloco usar; ainda sem visualização (abre em outra aba) |
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
| **Só token em componentes** | `#RRGGBB` só em `tokens.css` e nos SVGs de marca; componentes usam classes de token (`bg-surface`, `text-ink`, `text-ui`). **Um teste do Vitest (`src/design-rules.test.ts`, `scripts/design-rules.ts`, `D-055`) falha** com *hex*, `rgb()`/`hsl()` literal, classe arbitrária de cor, fonte, traço ou sombra sem `var(--…)` e valor solto de cor ou fonte em `style`. Layout arbitrário (`min-w-[36rem]`, `grid-cols-[…]`) segue livre |
| **Definição de pronto (UI)** | Todo componente ou tela do `apps/web` só está pronto quando foi **comparado com a página do guia** que o define (§15: abrir o PNG, ler a medida em `build/componentes.py`) e **cada divergência está registrada** em `decisions.md`. Vale também para estados que o guia não mostra: o espírito do guia, com a decisão registrada |
| **Componentes puros** | Só recebem *props*: sem regra de negócio, sem chamada de API, sem acesso a `features` (`architecture.md` §11) |
| **Utilitário de classes** | `cn()` (`clsx` + `tailwind-merge`) e `cva` (`class-variance-authority`) para variantes |
| **Vitrine `/design-system`** | **Definitiva** (`D-057`), só em desenvolvimento: tokens (cores com função), tipografia, o catálogo da identidade (`D-058`) e cada primitivo com variantes e estados, no tema claro, legível em desktop e mobile. Ganha seções conforme os componentes surgem; um teste exige que cada arquivo de `components/ui` apareça nela |
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
4. **Casca de navegação e esqueletos:** barra lateral (desktop), trilho de ícones (tablet), barra superior com o **seletor de lente** (`Casal` / `Minha visão`), barra inferior com 4 destinos + "Mais" (mobile, conforme §10.1) e as **8 áreas** (as 7 de `D-025` e o Assistente, `D-050`) como páginas-esqueleto com `EmptyState`. **Lote 1 (casca, rotas e seletor de lente) feito em `D-051`; lote 2, o ícone flutuante do assistente, feito em `D-056`.**
5. **Vitrine `/design-system`:** tokens, tipografia e cada primitivo com variantes e estados. **Concluída em `D-057`, só em desenvolvimento.**

**Adiado, com gatilho para retomar:**

| Item | Gatilho |
| :--- | :--- |
| Tema escuro "Noite Oliva" (§3.1), alternador `claro / escuro / sistema` e script anti-*flash* (§3.2) | Quando o usuário pedir |
| Regressão visual por *snapshots* | Se houver regressões visuais recorrentes |
| `axe` automatizado (E2E ou vitrine) | Se houver regressões de acessibilidade recorrentes ou o produto se abrir a outros casais (`D-002`) |
| ~~Script de CI/`pre-commit` contra *hex*~~ | **Ativado em `D-055`**, como teste do Vitest e com escopo mais largo (cor, fonte, traço e sombra), sem esperar o gatilho (§12) |
| Impressão (`@media print`, tokens de papel) | Bloco 4.2 (Dossiê do Dia D): **gatilho atingido no detalhamento** (`D-038`, `F-DOS-08`); entra na construção do Bloco 4.2 |
| Demais primitivos de §8 (`Radio`, `Switch`, `Avatar`, `Separator`, `DropdownMenu`, `Combobox`, `Tag`, `Skeleton`, `Accordion`, `ScrollArea`); `MoneyInput` nasceu no Bloco 1.1 (`D-067`), e `Sheet` e `Progress` também (`D-068`); `AlertDialog` nasceu no Bloco 1.3 (`D-085`) | Quando a primeira tela que o usa for construída |
| Componentes de domínio de §9 | No bloco que os usa |
| `QuickAddFab` ("+ Registrar Rápido") | Primeiro bloco com algo para registrar rápido (Bloco 3.1) |
| Menu do usuário | **Resolvido em `D-061`**: não há menu na barra superior; a sessão fica no pé da barra lateral, no trilho e na folha "Mais" |
| E2E de navegação com Playwright | Com o login (restante do Bloco 0.1) |

**Critério de conclusão do Bloco 0.2:** a vitrine mostra tokens, tipografia e todos os primitivos listados com variantes e estados, no tema claro, em desktop e mobile; as 8 áreas são navegáveis como esqueletos; o app segue a identidade do Altare. **Conferido e cumprido em `D-057`.**

---

## 14. Pontos Aprovados (`OQ-DS-001`, resolvida em `D-025`)
1. Navegação mobile: 4 destinos + "Mais" + botão flutuante (§10.1).
2. **Sem cor por perfil**; distinção por rótulo e inicial (§3.3, §9).
3. Nota 1–5 como **botões numéricos em mono** (não estrelas) no `RatingPair`.
4. Formatação monetária: sem centavos em resumos, com centavos em parcelas/pagamentos (§11).
5. Tema escuro **Noite Oliva** e alternador `claro / escuro / sistema` por dispositivo (§3.2). *(Construção adiada em `D-028` até o usuário pedir.)*
6. Escala tipográfica (§4) e alturas de controle (§5).

---

## 15. Mapa guia → componente (`D-055`)

O **guia de identidade** (`docs/design/identidade-visual/`, aprovado em `D-024` e `D-025`) é a referência de composição e medidas de tudo que o `apps/web` desenha. Este mapa é o **índice único**: para construir ou alterar um componente, uma tela ou um padrão, ache a linha, **abra a página e o PNG**, leia a medida na função de `build/componentes.py` e só então implemente. As skills `altare-design`, `altare-frontend`, `altare-ui-ux`, `altare-code-review` e `altare-pull-request` apontam para cá.

**Hierarquia de verdade:** (1) `tokens.json`, os valores; (2) o guia, composição e medidas; (3) `identity.md`, o porquê da marca; (4) este documento, inventário e governança (onde diverge do guia, o guia vence e este texto é corrigido, com registro em `decisions.md`); (5) o código nunca é fonte.

**Onde estão as páginas:** PNG de cada página em `identidade-visual/componentes/paginas/pagina-NN-*.png`; aplicações em `componentes/aplicacoes/` e elementos em `componentes/elementos/` (SVG e PNG); medidas exatas em `build/componentes.py` (linhas abaixo) e `build/medidas.json`. Os arquivos de `componentes/` são gerados: leia, nunca edite. O guia desenha em 15, 13 e 11 px, que o app tem como `ui`, `ui-sm` e `ui-xs` (`D-054`). **Estados que o guia não desenha** (hover, ativo, desabilitado, carregando, erro): sigam o espírito dele, com decisão registrada se houver dúvida.

**Estado:** **conforme** (conferido em `D-054`, com captura), **desvio** (registrado em `D-xxx`), **sem página** (não há desenho no guia; aprovado no espírito da pág. 32) ou **pendente** (nasce no bloco que o usa, `D-028`).

| Componente, tela ou padrão | Página(s) | Arquivo do guia | Medidas em `build/componentes.py` | Estado |
| :--- | :--- | :--- | :--- | :--- |
| Tokens de cor (claro) | 20, 22, 24 | `cores/paleta-clara`, `pagina-20-paleta-clara` | `build_paletas` `:402-431`; valores em `tokens.json` | Conforme (teste do `tokens.css`) |
| Tema escuro | 21, 23, 41 | `cores/paleta-escura`, `aplicacoes/tema-escuro` | `_visao_geral(D, …)` `:848-928` | Pendente (adiado, `D-028`) |
| Famílias e escala tipográfica | 25, 26, 27 | `tipografia/familias`, `hierarquia`, `especime` | `build_familias` `:437`, `build_hierarquia` `:463`; escala em `tokens.json` | Conforme (`D-054`) |
| Números e formatos pt-BR | 28 | `tipografia/numeros` | `build_numeros` `:506-551` | Conforme (`D-054`: sinal separado do `R$`) |
| Regras de texto (serifa, carregamento) | 29 | página 29 | `documento.py` `tipografia()` `:268-289` | Conforme (`D-054`: `opsz`, *preload*, reservas) |
| Superfícies: textura, raios, linhas, profundidade | 32 | `elementos/superficies` | `build_superficies` `:599-633` (cantos `:611-613`, sombras `:620-628`), `textura` `:98` | Conforme |
| Ícones e traço | 33 | `elementos/iconografia` | `build_iconografia` `:643-661`, `ICONES` `:635` | Conforme (`D-054`: 1,5 px que não escala) |
| Ornamentos (arco, ramo) | 30, 31 | `elementos/arco`, `elementos/ramo` | `build_arco` `:555`, `build_ramo` `:577` | Conforme (SVGs copiados) |
| Movimento | 35 | `elementos/estados-e-movimento` | `build_estados` `:727-761` (tokens `:752-758`) | Conforme |
| `Button` | 34, 39 | `elementos/interface`, `aplicacoes/mobile` | `button` `:54-71` (40 px, raio 6, 15 px seminegrito), variantes `:666-672`; celular 44 px `:958` | Conforme (`D-054`) |
| `Input`, `Textarea`, `Select`, `Field` | 34, 37 | `elementos/interface`, `aplicacoes/tela-de-login` | campo 44 px, borda `border-strong`, foco em anel duplo `:673-679`; login `:830-834` | Conforme (`D-054`); lista do `Select` sem página (`D-047`) |
| `Checkbox`, `Tabs`, `Dialog`, folha "Mais" | 32 | `elementos/superficies` | raios e níveis `:611-613`, `:620-628` | Sem página (aprovado, `D-054`) |
| `AlertDialog` (confirmação destrutiva) | 32, 35 | `elementos/superficies`, `elementos/estados-e-movimento` | diálogo, raios e nível 2 `:611-628`, botão `:664-672` | Sem página (`D-085`): o desenho do diálogo da pág. 32 (nível 2, `rounded-card`, folha inferior no celular, centralizado a partir de `md`), sem o botão Fechar; Cancelar à esquerda do destrutivo (que vem por último e, no celular, em cima: `flex-col-reverse`), `soft-destructive` em argila; o foco entra no Cancelar; usado em excluir núcleo, excluir marco e remover anexo |
| `SegmentedControl` (lente de visão) | 34, 38 | `elementos/interface`, `aplicacoes/visao-geral` | trilho 34 px, ativo 28 px com *hairline* `:687-689`, `:868-870` | Conforme (`D-052`, `D-054`) |
| `Badge` (selos) | 34, 38–40 | `elementos/interface`, `aplicacoes/*` | `chip` `:43-52` (pílula, 26 a 30 px, 13 px); selos `:691-700` | Conforme (`D-054`); selos de domínio pendentes |
| `Card` | 32, 38 | `aplicacoes/visao-geral` | `card` `:30`, `cartao` `:879-884` (raio 10, *hairline*, título em serifa 20) | Conforme |
| `Table` | 28, 40 | `tipografia/numeros`, `aplicacoes/comparador` | `:506-551`, `build_comparador` `:1003-1053` | Desvio: cabeçalho com fundo e linha em sans (`D-054`, item 10) |
| `Money` | 28, 34, 40 | `tipografia/numeros`, `elementos/interface` | `:513-551`, valor comparável `:713-718` | Conforme (`D-054`) |
| `Toast` | 35 | `elementos/estados-e-movimento` | `:742-749` (Sálvia, ícone, 4 s) | Desvio: raio 10 e *hairline* (`D-054`, item 10) |
| `Tooltip` | 32 | `elementos/superficies` | nível 1 `:620-628` | Conforme (`D-054`) |
| `EmptyState` e páginas-esqueleto | 30, 31, 35, 38 | `elementos/estados-e-movimento`, `elementos/ramo` | vazio `:730-736` (ramo 160 × 64, título 20 px, 1 ação) | Conforme (`D-054`) |
| 404 | 31 | `elementos/ramo` | ramo grande 300 × 112 `:577-597` | Conforme (`D-054`) |
| `PageHeader` | 38, 40 | `aplicacoes/visao-geral` | rótulo, título serifa, apoio e *hairline* `:874-877` | Conforme (`D-054`) |
| Casca: barra lateral e trilho | 38 | `aplicacoes/visao-geral` | `_visao_geral` `:848-872`, `AREAS` `:843` (itens 40 a cada 46, ícone 20, rótulo 12) | Conforme (`D-052`, `D-054`); trilho sem página (`D-051`) |
| Casca: barra superior | 38 | `aplicacoes/visao-geral` | `:866-871` (72 px) | Conforme (`D-052`); barra opaca (`D-054`, item 10) |
| Casca: barra inferior (celular) | 39 | `aplicacoes/mobile` | `:964-968` (72 px, ícone 22, rótulo 11) | Conforme (`D-052`, `D-054`); lupa adiada |
| Marca na casca e favicon | 12, 13, 16, 17, 36 | `construcao/*`, `aplicacoes/favicon-e-icone-de-app` | `build_lockups` `:226`, `build_favicon_app` `:784-819`; `medidas.json` | Conforme (`D-045`, `D-054`) |
| Ícone flutuante do Assistente | 33, 39 | (não desenhado) | texto sempre com ícone `:635-661`; "Registrar" `:963` (144 × 48, 16 px da borda e da barra) | Desvio: pílula secundária que se recolhe ao rolar (`D-054` item 11, `D-056`) |
| `Popover` (cartão do Assistente) | 32 | `elementos/superficies` | nível 1 `:620-628`, raio `card` `:611-613` | Conforme (`D-056`); sem página para o cartão em si |
| Avaliação dupla, `RatingPair` | 34, 39, 40 | `elementos/interface`, `aplicacoes/mobile` | `:703-712`, `:987-994` | Pendente (Bloco 2.2) |
| Comparador de propostas | 40 | `aplicacoes/comparador` | `build_comparador` `:1003-1053` | Pendente (Bloco 3.2) |
| `QuickAddFab` ("Registrar") | 39 | `aplicacoes/mobile` | `:963` | Pendente (Bloco 3.1) |
| Catálogo da identidade na vitrine | 12, 30, 31, 33, 36, 42 | `construcao/lockups`, `elementos/arco`, `elementos/ramo`, `elementos/iconografia`, `aplicacoes/favicon-e-icone-de-app`, `aplicacoes/dossie-do-dia-d` | `build_lockups` `:226`, `build_arco` `:555`, `build_ramo` `:577`, `build_iconografia` `:643-661`, `build_favicon_app` `:784-819`, `build_dossie` `:1055-1103` | Desvio: sem a aba escura nem a grade de apps; Dossiê só com as peças e as regras (`D-058`) |
| Login | 37 | `aplicacoes/tela-de-login` | `build_login` `:821-841` | Conforme (`D-061`); campo de 44 e botão de 48 com texto 15 pelos primitivos (`D-054`), ramo pequeno, aviso de erro em argila, sem arco nem ramo no celular |
| Sessão: pé da barra lateral, trilho e folha "Mais" | 38 | `aplicacoes/visao-geral` | `_visao_geral` `:863-864` | Conforme com desvios (`D-061`): o bloco virou botão com seta e abre o cartão com o Sair; ícone no trilho; a folha "Mais" termina com a sessão |
| `MoneyInput` | 34 | `elementos/interface` | campo com prefixo `R$` em mono `:673-679`; valor `:713-718` | Conforme (`D-067`); máscara e centavos sem página |
| Definições Base (painel) | 38 | `aplicacoes/visao-geral` | `cartao` `:879-884`, linha `:886-893` (rótulo 15, selo `Em definição`, *hairline*) | Desvio (`D-067`): linha-botão com valor e seta, `Definido` em sálvia com `check`, edição em `Dialog` (folha no celular) |
| `Sheet` (painel lateral) | 32 | `elementos/superficies` | gaveta no nível 2 `:620-628`, raio `card` `:611-613`; entra a 220 ms (`build_estados` `:752-758`) | Sem página (`D-068`): lateral à direita a partir de `md`, folha inferior abaixo; modal, `z-30` |
| `Progress` | 35, 38 | `elementos/estados-e-movimento`, `aplicacoes/visao-geral` | trilho em `surface-sunken` e preenchimento primário; número sempre por escrito | Sem página (`D-068`) |
| Mapa de Escopo (lista, quadro, filtros e painel) | 34, 35, 38, 39, 40 | `elementos/interface`, `elementos/estados-e-movimento`, `aplicacoes/*` | cartão `:879-884`, selos `:691-700`, aviso em argila `:742-749`, colunas de cartões `build_comparador` `:1003-1053` | Desvio (`D-068`): selos de alinhamento próprios (`circle-check`, `messages-square`), *chips* de filtro, nome-botão no cartão, quadro de 4 colunas a partir de 1024 px, status só pelo painel |
| Referências da frente (lista, miniaturas e formulários) | 34, 35, 39 | `elementos/interface`, `elementos/estados-e-movimento`, `aplicacoes/mobile` | campo 44 px `:673-679`, cartão `:879-884`, anexo com ícone e nome `:987-994` | Sem página (`D-069`): miniatura 80 px que abre o arquivo, link com domínio, `input` de arquivo nativo; no celular abre a câmera ou a galeria |
| Anexos do cronograma (lista, formulários e remover) | 34, 35, 39 | `elementos/interface`, `elementos/estados-e-movimento`, `aplicacoes/mobile` | campo 44 px `:673-679`, cartão `:879-884`, anexo com ícone, nome e clipe `:987-994` | Sem página (`D-085`): uma linha-cartão por anexo com ícone de 20 px (`file-text` para PDF, `image` para imagem, `paperclip` para link), título (ou o nome do arquivo, ou o domínio), tamanho em mono tabular (`1,4 MB`), comentário, e `Noivo · 27 out 2026, 12:30`; **sem miniatura e sem visualizador**: arquivo e link abrem em outra aba, e o link só é `<a>` se for http ou https; os formulários "Adicionar arquivo" e "Adicionar link" aparecem na própria seção (campo nativo de arquivo sem `capture`, título e comentário com a dica "Opcional."); "Remover" só para o autor, com o nome do anexo no botão e confirmação em `AlertDialog` que diz que sai da lista e o registro fica guardado (sem Desfazer); o foco vai ao título "Anexos" depois de anexar ou remover; **desvio**: o guia desenha o clipe à direita da linha, aqui o lugar é do botão Remover |
| Lista de convidados (tabela agrupada, cartões e painel do núcleo) | 34, 38, 39 | `elementos/interface`, `aplicacoes/visao-geral`, `aplicacoes/mobile` | cartão `:879-884`, linha com *hairline* `:886-893`, cartão no celular `:954-958` | Sem página (`D-072`): tabela com cabeçalho de grupo por núcleo no computador e cartão por núcleo no celular, nome-botão que abre o painel, lado em selo `outline`, `Não irá` neutro com `circle-minus` |
| `WhatsAppButton` ("Abrir WhatsApp") | 34, 39 | `elementos/interface`, `aplicacoes/mobile` | botão primário `:669`; no cartão do celular, secundário de 44 px `:958`; no detalhe, primário de 28 px `:982` | Conforme com desvio (`D-072`): variante `secondary` pequena nas linhas; só existe para celular válido; fica em `features/guests` até um segundo bloco usá-lo |
| Status em um toque (selo-botão com `Popover`) | 34, 35 | `elementos/interface`, `elementos/estados-e-movimento` | selos `:691-700` | Sem página (`D-072`): o selo é o botão e abre um cartão com os quatro status; `Não irá` pede o motivo opcional |
| Contadores da lista (`GuestCounters`, três blocos) | 34, 38 | `elementos/interface`, `aplicacoes/visao-geral` | cartão `:879-884`, valor em mono `:713-718`, rótulo em caixa alta pequena `eyebrow` | Sem página (`D-073`): três blocos com `text-num-xl`, detalhe por faixa e os Não irão à parte; o ponderado sem pesos diz "defina os pesos" em vez de um número |
| Pesos e idades das crianças (diálogo) | 32, 34 | `elementos/superficies`, `elementos/interface` | campo 44 px `:673-679`, diálogo `:611-628` | Sem página (`D-073`): campos com sufixo `%` e `anos`, abre vazio; no celular é folha inferior |
| Faixa sugerida pela idade (aviso com Aplicar) | 34, 35 | `elementos/interface`, `elementos/estados-e-movimento` | botões `:664-672`, aviso `:742-749` | Sem página (`D-073`): fundo `surface-muted`, texto completo e dois botões; nunca muda a faixa sozinho |
| Busca e filtros da lista (campo, chips e "N de M pessoas") | 34, 35, 38 | `elementos/interface`, `elementos/estados-e-movimento` | campo 44 px `:673-679`, selos `:691-700`, lente `:686-690` | Desvio (`D-074`): chips `aria-pressed` como os do Mapa (hoje o `Chip` de `components/ui`, `D-084`), grupos em `fieldset` com legenda, a lente `Minha visão` em texto e o outro lado a um toque |
| Convite por núcleo (seção, diálogo e a oferta de mover) | 32, 34, 35 | `elementos/superficies`, `elementos/interface` | campo `:673-679`, diálogo `:611-628` | Sem página (`D-074`): data e canal em um diálogo (folha no celular); a oferta é uma segunda etapa do mesmo diálogo com duas saídas |
| Exportar a lista (botão, formato, tamanho e aviso de cuidado) | 32, 34, 35 | `elementos/superficies`, `elementos/interface` | diálogo `:611-628` | Sem página (`D-075`): o mesmo diálogo (folha no celular) com o seletor segmentado de formato, a contagem da tela e o aviso de cuidado em texto; "Gerando o arquivo…" numa região de status e o erro no próprio diálogo |
| Cronograma "Por fase" (tabela por fase, cartões e foco no `Destravado`) | 34, 38, 39, 40 | `elementos/interface`, `aplicacoes/visao-geral`, `aplicacoes/mobile`, `aplicacoes/comparador` | selos `:691-700`, cartão `:879-884`, linha `:886-893`, cartão no celular `:954-958`, tabela `build_comparador` `:1003-1053` | Sem página (`D-081`): uma só tabela com `tbody` por fase no computador (título da fase em `th scope=rowgroup`, mais um `h2` só para leitor de tela) e um cartão por marco no celular; o motivo do bloqueio em texto abaixo do título; o `Destravado` com contorno `consensus-ink` no cartão e título em negrito na tabela (destaque proposto: o guia só desenha o selo); responsável em texto simples, sem `ProfileChip`; datas `15/03/2027` na tabela e `15 jan 2027` no cartão |
| `DependencyStatus` (selos de estado do marco) | 34 | `elementos/interface` | selos `:691-700` | Desvio (`D-081`): `Destravado` sálvia com `lock-open`, `Bloqueado` neutro com `lock`, `Em andamento` `outline` com `circle-dot`, `Concluído` sálvia com `circle-check`, `Atrasado` argila com `circle-alert`, `Opcional` `outline` sem ícone; o motivo vai em texto, não em `Popover` |
| `PhaseHeader` | 38, 40 | `aplicacoes/visao-geral`, `aplicacoes/comparador` | eyebrow, título em serifa e *hairline* `:874-877`, tabela `:1003-1053` | Desvio (`D-081`): eyebrow "Fase N" (a posição de exibição, não um campo), título em serifa e progresso em mono na tabela; no celular, o `Progress` com barra e o rótulo em sans (o guia não desenha a barra) |
| Detalhe do marco (`Sheet` com estado, formulário e confirmações) | 32, 34, 35 | `elementos/superficies`, `elementos/interface`, `elementos/estados-e-movimento` | gaveta e diálogo `:611-628`, campo 44 px `:673-679`, aviso `:742-749` | Sem página (`D-081`): painel lateral no computador e folha inferior no celular, aberto pela URL (`?marco=`); estado, responsável, prazo e nota; "ignorar o bloqueio" e "reabrir" em `Dialog` com a lista do que falta ou do que volta a ficar bloqueado; o feedback é uma região de status dentro do painel (sem `Toast`); o foco vai ao painel ao abrir, ao título "Estado" depois de mudar o estado e ao botão de origem se a confirmação é cancelada |
| Edição do cronograma (Novo marco, Fases, dependências e exclusão com Desfazer) | 32, 34, 35 | `elementos/superficies`, `elementos/interface`, `elementos/estados-e-movimento` | diálogo e gaveta `:611-628`, campo 44 px `:673-679`, botão `:664-672`, aviso `:742-749` | Sem página (`D-082`): os diálogos de Novo marco e de Fases (centralizados no computador, folha inferior no celular); a linha de fase com campo, Salvar, Subir e Descer, empilhada no celular, sem arrastar; "Excluir marco" em `soft-destructive` (argila, nunca vermelho) com a confirmação que lista os dependentes; o erro de ciclo em região de alerta com o caminho; a confirmação de excluir marco migrou para `AlertDialog` no PR 5 (`D-085`), com o foco devolvido ao botão de origem; o "ignorar o bloqueio", o "reabrir" e os itens em aberto seguem em `Dialog`, porque oferecem uma escolha e não uma exclusão |
| `Select` com grupos de opções | 34 | `elementos/interface` | campo 44 px, lista própria `:673-679` | Sem página (`D-082`): a opção pode trazer `group` (rótulo de grupo com `role="group"`, itens de 44 px no toque, o que não tem grupo vem primeiro); o `Select` repassa o `ref` ao botão que abre a lista |
| Prazo, janela e contagem do cronograma (tabela, cartão e painel) | 34, 38, 39, 40 | `elementos/interface`, `aplicacoes/visao-geral`, `aplicacoes/mobile`, `aplicacoes/comparador` | selos `:691-700`, cartão `:879-884`, valor em mono `:713-718`, tabela `build_comparador` `:1003-1053` | Sem página (`D-083`): o prazo efetivo (data **como dado** em mono, também no painel) e, na segunda linha, a janela calculada em `text-ui-sm` com "sugestão genérica" e "prazo definido por vocês"; a contagem ("faltam N dias", "venceu há N dias") em texto, com a data exata no `title` e também visível; no cartão, alinhados à direita junto da data; data **dentro de frase** ("Janela: …", "Sugestão: …") em sans; os separadores ` · ` em `aria-hidden` |
| Aviso "Sem data definida" | 35, 38 | `elementos/estados-e-movimento`, `aplicacoes/visao-geral` | aviso `:742-749`, cartão `:879-884` | Sem página (`D-083`): `Card` `muted` com o ícone `calendar-clock`, texto calmo e o link para as Definições Base; vale também com a data só em janela `Definida` |
| Seção "Janela" do painel do marco (editor, "Definir janela", "Voltar à sugestão") | 34 | `elementos/interface` | campo 44 px `:673-679`, botão `:664-672` | Sem página (`D-083`): a frase "de X a Y meses antes da data", as datas calculadas, o editor de três campos (início, fim, unidade) com a dica por unidade ligada por `aria-describedby`, "Salvar janela" desligado com o motivo em texto; só em Modo Com Data; o foco vai ao título "Janela" depois de salvar |
| Prévia da mudança de data (no diálogo de Definições Base) | 32, 34, 35 | `elementos/superficies`, `elementos/interface`, `elementos/estados-e-movimento` | diálogo `:611-628`, aviso `:742-749`, valor em mono `:713-718` | Desvio (`D-083`): o resumo por transição, até 5 marcos ("antes → depois" em mono, com "para" só para leitor de tela) e "e mais N marcos"; "Calculando…" e a falha honesta em região de status; o **rodapé fixo** no celular (abaixo de 768 px, borda superior e fundo `surface`); o foco vai ao título da confirmação |
| Avulsas (seção, cartões e `TaskSheet`) | 34, 38, 39, 40 | `elementos/interface`, `aplicacoes/visao-geral`, `aplicacoes/mobile`, `aplicacoes/comparador` | selos `:691-700`, cartão `:879-884`, linha `:886-893`, cartão no celular `:954-958`, campo 44 px `:673-679`, gaveta e diálogo `:611-628` | Sem página (`D-084`): no computador, um `tbody` com `th scope=rowgroup` "Avulsas" na mesma tabela (cabeçalho "Marco ou avulsa"); no celular, uma `section` com `h2` e cartões; o painel é um `TaskSheet` próprio (sem fase, categoria, janela nem dependências), aberto por `?avulsa=`; selos `A fazer` (ícone `circle`, neutro), `Em andamento` (`outline` com `circle-dot`), `Concluída` (sálvia, `circle-check`) e `Atrasada` (argila, `circle-alert`); excluir sem confirmação, com aviso de 4 s e "Desfazer" |
| Checklist (marco e avulsa) | 34 | `elementos/interface` | campo 44 px `:673-679`, botão `:664-672` | Sem página (`D-084`): "N de M" em texto (no painel e como "Checklist: N de M" nas linhas e cartões); cada item é uma caixa nomeada pelo texto, com "Editar o item X" (troca por campo, Salvar e Cancelar), Subir, Descer (o foco acompanha o item) e "Remover o item X" imediato; "Novo item" mantém o foco no campo; 8 px entre os alvos; sem arrastar (`D-068`, item 10) |
| Barra de filtros e lente do cronograma | 34, 35, 38 | `elementos/interface`, `elementos/estados-e-movimento`, `aplicacoes/visao-geral` | campo 44 px `:673-679`, selos `:691-700`, lente `:686-690` | Desvio (`D-084`): o padrão de Convidados (`fieldset` com legenda e chips de escolha única), com `Responsável`, `Estado`, "Só atrasados" e "Só avulsas"; a lente `Minha visão` filtra para "eu ou `Ambos`" e o filtro explícito de responsável a vence (a nota diz isso em texto); "N de M itens" em região de status; "Limpar filtros" só com filtro explícito; o estado vazio só pela lente oferece "Ver a Visão do Casal" |
| "Meus próximos passos" (celular) | 34, 39 | `elementos/interface`, `aplicacoes/mobile` | cartão no celular `:954-958`, selos `:691-700` | Sem página (`D-084`): `section` com `h2` no topo, só no celular, uma linha-botão por item com o tipo ("Marco"/"Avulsa") em texto, o prazo e a contagem, "Atrasado/Atrasada" com ícone e o responsável; até 8 e "Ver todos (N)" com `aria-expanded`; sempre "eu ou `Ambos`", sem depender da lente |
| Dossiê do Dia D (impressão) | 42 | `aplicacoes/dossie-do-dia-d` | `build_dossie` `:1055-1103` | Pendente (Bloco 4.2) |

**Manutenção:** componente ou tela nova entra no mapa **na mesma mudança** que a constrói; um desvio novo ganha `D-xxx` e a linha passa a "Desvio". Se o guia for regenerado (`uv run build.py`), confira as linhas citadas, que acompanham `componentes.py`.
