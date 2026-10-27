---
name: altare-design
description: >-
  Identidade visual e design system do Altare, com o guia de identidade como fonte visual (mapa guia → componente em design-system.md §15): tokens (tokens.json é a fonte única, tokens.css é gerado), tipografia, cor semântica, ornamento sutil, ícones, movimento, os 15 primitivos do escopo enxuto (D-028) e a regra de sacralidade discreta e não confessional. Use sempre que for criar, alterar, conferir ou comparar a aparência de qualquer componente, tela, página, estado vazio, barra, cartão, botão, campo, selo ou ícone no apps/web, escolher cor, fonte, tamanho, espaçamento, ícone ou ilustração, adicionar primitivo, mexer em marca ou logo, ou quando aparecer um valor de cor ou fonte escrito à mão, mesmo que o pedido seja só 'deixa isso mais bonito', 'ajusta o espaçamento', 'cria a tela de X' ou 'muda a cor do botão', sem citar o guia. NÃO use para estrutura de código e estado (use altare-frontend), fluxos e estados de tela (use altare-ui-ux), checklist de acessibilidade (use altare-acessibilidade) ou texto da interface (use altare-conteudo-copy).
---

# Design do Altare

## Docs a consultar
- **`docs/design/design-system.md` §15, o mapa guia → componente**: a página do guia que define cada componente e tela. Comece por ele.
- `docs/design/identity.md` (a marca e o porquê): §1.3 sacralidade discreta, §3 cor, §4 tipografia, §6 ornamento, §7 ícones, §8 movimento.
- `docs/design/design-system.md`: §1 princípios, §3.3 regras de cor, §8 e §9 inventário (referência), §12 governança, §13 ordem e adiamentos.
- `docs/design/identidade-visual/`: `tokens.json` (valores), `componentes/INDEX.md` (ativos exportados), `build/` (pipeline).
- `docs/design/visual-direction.md` §1 e §2 (personalidade e densidade). Decisões: `D-025`, `D-026`, `D-028`.

## Fonte visual: o guia
O guia de identidade (`docs/design/identidade-visual/`, aprovado em `D-024` e `D-025`) é a referência de **composição e medidas** de tudo que se desenha. O texto de `design-system.md` resume; quando diverge do guia, o guia vence e o texto é corrigido, com decisão registrada. Antes de implementar ou alterar qualquer UI:
1. **Ache o componente ou a tela no mapa** (`design-system.md` §15): ele diz a página, o arquivo e as linhas de medida.
2. **Abra o PNG da página** (`componentes/paginas/pagina-NN-*.png`, ou o de `aplicacoes/` e `elementos/`). Olhe a imagem; não confie só na descrição.
3. **Leia a medida** na função indicada de `build/componentes.py` (e em `medidas.json`); valores de marca vêm do `tokens.json`. Não estime a olho.
4. **Só então implemente**, com classes de token. Tamanho que o guia usa e a escala não tem não vira valor solto: vira token (`D-054`).
5. **Ao terminar, compare** o resultado com o PNG (suba o app e capture, skill `run`) e registre cada desvio em `decisions.md`. Estado que o guia não desenha: proponha no espírito dele e peça aprovação (`AGENTS.md` §3).

## Princípios
1. **`tokens.json` é a única fonte de valores.** `apps/web/src/styles/tokens.css` é **gerado** por script e nunca editado à mão; um teste do Vitest falha se estiver desatualizado. Para mudar um valor: edite o `tokens.json`, regenere o guia (`uv run build.py`; `--marca` regenera os logos) e o `tokens.css`. Os arquivos gerados do pacote (PDF, HTML, PNG, SVG de `componentes/`) não se editam.
2. **Só token em componente.** `#RRGGBB` só existe em `tokens.css` e nos SVGs de marca; componente usa classe de token (`bg-surface`, `text-ink`, `text-ui`, `border-border-strong`). O teste `design-rules.test.ts` (`D-055`) falha com *hex*, cor funcional, classe arbitrária de cor, fonte, traço ou sombra sem `var(--…)` e valor solto de cor ou fonte em `style`.
3. **Nomes semânticos, não literais** (`canvas`, `surface`, `ink`, `primary`, `consensus-*`, `attention-*`). É o que deixa o tema escuro entrar depois sem retrabalho.
4. **Só o tema claro por enquanto** (`data-theme="light"` fixo). O escuro "Noite Oliva" está especificado, mas não se implementa alternador, script anti-*flash* nem bloco `dark` até o usuário pedir (`D-028`).
5. **Regras de cor** (`design-system.md` §3.3):
   - Texto pequeno terracota usa `text-accent-ink`; `bg-accent` só em preenchimento, ícone e texto grande.
   - Controle interativo usa `border-border-strong`; `border-border` é só divisória.
   - `consensus-*` é acordo, dentro do teto, parcela paga. `attention-*` é divergência, extra pendente, acima do teto e erro. **Nunca vermelho**: o erro é um convite, não um alarme.
   - **Sem cor por perfil.** `Noivo` e `Noiva` se distinguem por rótulo e inicial.
6. **Três famílias, três papéis** (`identity.md` §4): serifa para título e nome de espaço, fornecedor e cenário; sans para interface; mono tabular para todo número que o casal compara. Nunca serifa em botão, rótulo de formulário ou cabeçalho de tabela.
7. **Primitivos: só os 15 de `D-028`** (`Button`, `Input`, `Textarea`, `Select`, `Checkbox`, `Badge`, `Card`, `Dialog`, `Table`, `Tabs`, `Tooltip`, `Toast`, `EmptyState`, `PageHeader`, `Money`). Os demais nascem quando a primeira tela que os usa for construída; componente de domínio nasce no bloco que o usa.
   - Primitivo recebe só *props*: sem regra de negócio, sem API, sem importar de `features`.
   - Variantes por `cva` e `cn()`, não por cópia. Nenhum shadcn "de fábrica": tudo re-estilizado.
   - Estados mínimos: default, hover, focus-visible, active, disabled, loading (quando couber) e error (campos).
   - `Money` é primitivo (`components/ui`), um formatador puro de centavos.
8. **Calma visual.** Plano com *hairline* em vez de sombra; sombra só em overlay (popover, diálogo, gaveta). Raios: `control` 6, `card` 10. Respiro generoso.
9. **Sacralidade discreta, sem religião literal** (`identity.md` §1.3, `D-026`). Ela aparece em proporção, silêncio, serifa clássica, *hairline*, arco e luz suave. Não aparece como cruz, pomba, cálice, vitral, aliança, laço, dourado saturado, brilho ou confete. O latim existe só no nome.
10. **Ornamento Sutil** (`identity.md` §6): arco e ramo em linha só em login, estados vazios, 404 e Dossiê. Os SVGs vêm de `identidade-visual/fonte/ornamentos/` e ativos de marca são **copiados** para `apps/web/public/brand/`, nunca redesenhados. Sem foto decorativa.
11. **Ícones Lucide** (traço 1,5 px) com mapa semântico fixo (`identity.md` §7), sempre com texto. `heart-handshake` é restrito ao selo de consenso.
12. **Movimento calmo:** 150 ms e 220 ms, um único momento de deleite (selo de decisão registrada, 400 ms). Proibido *bounce*, *parallax*, animação em *loop* e confete. Respeite `prefers-reduced-motion`.
13. **Dados de exemplo** na vitrine e nos testes são fictícios e rotulados ("Espaço Exemplo"); nunca dados do casamento (`AGENTS.md` §2).

## Checklist (componente ou mudança visual)
- [ ] Achei a linha no mapa (§15), abri o PNG da página e li a medida em `componentes.py`.
- [ ] Comparei o resultado com a página do guia; cada desvio tem `D-xxx` e o mapa foi atualizado.
- [ ] Nenhum *hex*, `px` de cor ou fonte escrita à mão; só classes de token.
- [ ] Cor semântica certa (acordo e atenção) e nada em vermelho.
- [ ] Famílias tipográficas nos papéis certos; número comparado em mono tabular.
- [ ] Estados mínimos implementados e visíveis na vitrine `/design-system`.
- [ ] Desktop e mobile (alvo de toque, altura de controle `lg` no mobile).
- [ ] Nenhum símbolo religioso literal; ornamento só nos lugares previstos.
- [ ] Passei pelo checklist de `altare-acessibilidade`.
- [ ] Se mudei valor de marca: editei o `tokens.json` e regenerei.

## Bom / ruim
```tsx
// ruim: hex, vermelho, serifa em botão, sombra em cartão
<button className="bg-[#3A4B3C] font-serif">Salvar</button>
<div className="shadow-lg text-red-600">Acima do teto</div>

// bom: tokens, argila com ícone e texto, plano com hairline (o Card já traz a borda)
<Button variant="primary">Registrar decisão</Button>
<Badge variant="attention"><CircleAlert /> Acima do teto</Badge>
<Card />
```

## Limites e vizinhas
- Como o componente é organizado e usa estado: `altare-frontend`. Como a tela se comporta e o que cada estado comunica: `altare-ui-ux`.
- Palavras e formatos de texto: `altare-conteudo-copy`. Foco, contraste e teclado: `altare-acessibilidade`.
- Mudança de identidade (marca, paleta, fonte) é decisão registrada: `altare-docs-vivas`.

## Em aberto
- Tema escuro: adiado com gatilho "quando o usuário pedir" (`D-028`).
- Demais primitivos e componentes de domínio: nascem com a primeira tela que os usa.
