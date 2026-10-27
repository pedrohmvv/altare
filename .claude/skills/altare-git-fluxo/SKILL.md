---
name: altare-git-fluxo
description: >-
  Fluxo de branches do Altare (D-041): main recebe só o que foi validado, develop integra, e todo trabalho sai da develop em branches tipo/assunto; hotfix sai da main e volta para main e develop; release é um PR develop para main ao concluir um bloco ou nível, com tag; merge commit sem squash para preservar commits atômicos; rebase local antes do PR; proteção de branches. Use sempre que for criar, nomear ou integrar uma branch, abrir release, aplicar um hotfix, decidir estratégia de merge ou perguntar em qual branch trabalhar, mesmo que o usuário só diga vou começar uma feature. NÃO use para montar mensagens e planos de commit (use altare-commit) nem para abrir ou descrever o PR (use altare-pull-request).
---

# Fluxo de branches

`main` conta o que está pronto; `develop` conta o que está integrado. Separar as duas permite integrar com frequência sem declarar nada como concluído, e o merge sem *squash* mantém o histórico por intenção que `altare-commit` constrói.

## Docs a consultar

- `docs/product/decisions.md` D-041 (a decisão completa) e D-039.
- `docs/engineering/roadmap.md` (o que é um bloco ou nível concluído) e `AGENTS.md` §1 (fase atual).

## Modelo

```
trabalho:  develop ──▶ feat/xxx ──PR──▶ develop
release:   develop ──PR──▶ main ──▶ tag vX.Y.Z
hotfix:    main ──▶ hotfix/yyy ──PR──▶ main (tag)
                              └─PR──▶ develop
```

## Regras

1. **Trabalho sai da `develop`**, em `<tipo>/<assunto-curto>`: minúsculas e kebab-case, com o tipo igual ao do commit (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`). Ex.: `feat/orcamento-simulador`, `docs/detalhamento-features-v1`. Uma branch, uma intenção; o nome diz qual.
2. **Volta à `develop` por PR**, com *merge commit* (`--no-ff`). **Nunca *squash* nem *rebase and merge***: apagariam os commits atômicos.
3. **Rebase local antes do PR:** `git fetch && git rebase origin/develop` na branch de trabalho, para o PR chegar sem conflito. Rebase **só em branch que ninguém mais usa**. Se a branch já foi publicada, reescrever exige `--force-with-lease`: peça confirmação ao usuário antes.
4. **Release:** quando um **bloco ou nível do roadmap** estiver concluído e passar em todos os gates de `altare-testes-qa`, abra um PR `develop → main` (`altare-pull-request`). Depois do merge, crie a *tag* anotada `vMAJOR.MINOR.PATCH` na `main`. Não há branch `release/*`: com um desenvolvedor, a `develop` já é a candidata.
5. **Versão (confirmada em `D-059`):** `MINOR` sobe por bloco concluído, `PATCH` por hotfix, e `1.0.0` marca o fim do Nível 4 (v1 manual completa, `roadmap.md`). `v0.1.0` marca o Bloco 0.2 e o fechamento do Nível 0 será `v0.2.0`.
6. **Proteção** de `main` e `develop`: sem *push* direto, PR obrigatório, CI verde. Está ativa no GitHub desde 2026-10-27 (valores em `D-041`, item 6). Alterá-la, ou criar branch e tag no remoto, só com pedido do usuário.

## Hotfix, passo a passo

1. `git switch main && git pull`, depois `git switch -c hotfix/<assunto>`.
2. Reproduza o bug com um teste que falha (`altare-testes-qa`) e corrija o mínimo.
3. PR `hotfix/<assunto> → main`; após o merge, *tag* com `PATCH` incrementado.
4. **Volte a correção para a `develop`:** PR `hotfix/<assunto> → develop`, resolvendo conflitos. Sem este passo, o próximo release da `develop` apaga a correção.
5. Remova a branch de hotfix.

## Estado atual

A `develop` existe e está protegida desde 2026-10-27, criada a partir da `main` depois do merge do PR #1 (`D-041`, itens 6 e 7). Todo trabalho novo sai dela. Falta exigir os *status checks* na proteção, o que depende da CI existir (`altare-devops`).

## Checklist

- [ ] A branch sai da `develop` (ou da `main`, se for hotfix) e tem nome `<tipo>/<assunto>`?
- [ ] Atualizei com `rebase` local sem reescrever branch compartilhada?
- [ ] O merge será *merge commit*, sem *squash*?
- [ ] Release: bloco ou nível concluído, gates verdes, *tag* planejada?
- [ ] Hotfix: a correção também volta para a `develop`?

## Limites e vizinhas

- **Onde** e **quando** integrar é aqui. **Como** commitar: `altare-commit`. **Como** abrir e descrever o PR: `altare-pull-request`.
- Gates exigidos antes do merge: `altare-testes-qa`; execução no CI: `altare-devops`.
- Decisões novas de processo viram `D-xxx`: `altare-docs-vivas`.

## Em aberto

- **Esquema de versionamento** (item 5) não consta em D-041; confirmar com o usuário antes da primeira *tag*.
