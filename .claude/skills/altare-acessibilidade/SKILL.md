---
name: altare-acessibilidade
description: >-
  Checklist manual WCAG 2.2 AA do Altare (o gate que substitui o axe, D-028): teclado, foco, nome
  acessível, contraste, toque, landmarks, reflow, movimento. Use ao concluir ou revisar qualquer
  componente, tela, formulário, diálogo ou tabela no apps/web, antes de pedir review.
---

# Acessibilidade do Altare

## Docs a consultar
- `docs/design/design-system.md` §7 (requisitos, a fonte deste checklist), §12 (como a verificação é feita) e §13 (gatilho do `axe`).
- `docs/design/identity.md` §3.4 (contrastes já auditados), §7 (ícones e estado) e §8 (movimento).
- `docs/engineering/stack.md` §7 (Biome, Playwright). Decisão: `D-028`.

## Princípios
1. **O alvo é WCAG 2.2 AA, nos dois temas.** Hoje só o claro existe; o escuro herda as regras quando entrar.
2. **Este checklist é o único gate.** `D-028` trocou o `axe` no CI por verificação manual para um app de duas pessoas. Sem uma passada manual por componente e por tela, nada impede a regressão.
3. **Cor nunca é o único sinal.** Todo estado semântico (consenso, atenção, bloqueado, pago) tem cor, ícone **e** texto completo. Vale também para o selo "Acima do teto".
4. **Use só pares de cor já auditados** (`identity.md` §3.4). Se um par novo for necessário, audite o contraste antes (texto 4,5:1; texto grande e componentes 3:1).
5. **Semântica antes de ARIA.** `<button>`, `<a>`, `<label>`, `<table>` resolvem quase tudo; ARIA só preenche o que o HTML não diz.

## Checklist por componente
- [ ] **Teclado:** alcanço e opero tudo com Tab, Shift+Tab, Enter, Espaço e setas onde couber; `Esc` fecha overlays; a ordem do foco segue a ordem visual.
- [ ] **Foco visível:** anel duplo (2 px `focus-ring` mais 2 px de espaçador na cor do fundo). Nunca `outline: none` sem substituto.
- [ ] **Nome acessível:** botão só de ícone tem `aria-label`; campo tem rótulo visível acima (placeholder não é rótulo); link faz sentido lido sozinho.
- [ ] **Estado em texto:** cor, ícone e texto juntos ("Aguardando avaliação da Noiva").
- [ ] **Alvo de toque** de pelo menos 44 × 44 px no mobile (`pointer: coarse`), com 8 px entre alvos; campo com no mínimo 16 px de fonte para o iOS não dar *zoom*.
- [ ] **Diálogo e gaveta:** foco entra ao abrir, fica preso dentro (Radix), volta ao gatilho ao fechar; título ligado por `aria-labelledby`.
- [ ] **Movimento:** com `prefers-reduced-motion`, as transições viram *fade* instantâneo; nada animado em *loop*.

## Checklist por tela
- [ ] `lang="pt-BR"`, *landmarks* (`nav`, `main`, `aside`) e *skip link* "Ir para o conteúdo" como primeiro elemento focável.
- [ ] Um `h1` por página (o `PageHeader`) e hierarquia de títulos sem pular nível.
- [ ] **Tabela:** `caption`, `th scope`, números à direita. A tabela comparativa rola **dentro do próprio contêiner** com a primeira coluna fixa, e esse contêiner é alcançável pelo teclado.
- [ ] **Formulário:** erro com ícone e texto ligado ao campo por `aria-describedby` e `aria-invalid`; ao enviar com erro, o foco vai ao primeiro campo inválido; obrigatoriedade escrita, não só asterisco.
- [ ] **Toast** em `aria-live="polite"`. Como ele some em 4 s, a ação que ele oferece ("Desfazer") também existe em outro lugar da tela.
- [ ] **Troca de rota na SPA:** ao navegar, o título do documento muda e o foco vai ao `h1`, para o leitor de tela anunciar a nova página.
- [ ] **Reflow:** sem rolagem horizontal em 320 px (exceto a tabela comparativa) e zoom de 200% sem perder conteúdo nem função.

## Como verificar (cerca de 5 minutos por tela)
1. Navegue **só com o teclado** do início ao fim da tarefa principal da tela.
2. Reduza a janela a 320 px de largura e aplique zoom de 200%.
3. Faça uma passada com leitor de tela (VoiceOver no macOS) pelo trecho que mudou: títulos, formulário, estados.
4. Ligue "reduzir movimento" no sistema e repita a interação animada.
5. Rode o `lint` (Biome) e confirme que o grupo `a11y` está ligado e sem supressões.
6. Registre o resultado numa linha no PR, por exemplo: `A11y: teclado ok, 320 px e zoom 200% ok, VoiceOver ok, reduzir movimento ok.`

## Biome
- As regras de acessibilidade do Biome ficam ligadas no `lint` (`design-system.md` §12). Corrija o código em vez de silenciar a regra; se a supressão for inevitável, escreva o motivo na mesma linha do `biome-ignore`.

## Bom / ruim
```tsx
// ruim: div clicável, ícone sem nome, erro só em cor
<div onClick={remover}><Trash2 /></div>
<input className="border-red-500" />

// bom: botão com nome, erro ligado ao campo com ícone e texto
<Button variant="ghost" size="icon" aria-label="Excluir fornecedor"><Trash2 /></Button>
<Input id="preco" aria-invalid aria-describedby="preco-erro" />
<p id="preco-erro"><CircleAlert /> Informe o preço base em reais.</p>
```

## Limites e vizinhas
- Esta skill é o checklist; `altare-frontend`, `altare-design`, `altare-ui-ux` e `altare-code-review` apontam para ela em vez de repeti-lo.
- Cores e tokens: `altare-design`. Fluxo e estados: `altare-ui-ux`. Implementação dos componentes: `altare-frontend`. Clareza das mensagens: `altare-conteudo-copy`.
- Estratégia geral de testes e gates: `altare-testes-qa`.

## Em aberto
- **Gatilho para reativar o `axe`** (E2E ou vitrine): regressões de acessibilidade recorrentes, ou o produto se abrir a outros casais (`D-002`, `D-028`). Até lá, não adicione o `axe` ao CI.
