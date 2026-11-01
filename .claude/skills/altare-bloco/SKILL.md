---
name: altare-bloco
description: >-
  Executar um bloco do roadmap com o time de agentes (altare-api-dev, altare-web-dev, altare-reviewer),
  com plano aprovado e quatro gates do usuário. Só manual: /altare-bloco 1.3. Não use para correção
  pontual nem para trabalho fora do roadmap.
disable-model-invocation: true
argument-hint: "[bloco, ex.: 1.3]"
---

# Executar um bloco com o time de agentes

A sessão principal orquestra e é dona dos gates; os subagents (`.claude/agents/`) implementam e revisam. Esta skill aponta para os documentos e não os copia (`D-039`): nunca fixe aqui o conteúdo de um bloco.

## Docs a consultar

- `docs/engineering/roadmap.md` (o bloco e seu critério de conclusão) e o mapa de features em `AGENTS.md` §4.
- `docs/product/decisions.md`: `D-066` e `D-071` (formato do plano em PRs), `D-070` e `D-076` (o E2E de fechamento) e as `D-xxx` que a feature citar.
- `AGENTS.md` §1 e §2 (nada de código sem o usuário pedir; fase e regras), `altare-git-fluxo`, `altare-commit`, `altare-pull-request`, `altare-docs-vivas`.

## 1. Entrada

`$ARGUMENTS` é o número do bloco. Ache o bloco em `roadmap.md` e a feature em `docs/product/features/`. Se o bloco não existir, já estiver concluído ou a feature não estiver aprovada, pare e diga.

## 2. Plano (plan mode)

1. Até 3 `Explore` em paralelo: a feature (campos, regras, critérios de aceite), as decisões `D-xxx` citadas e os módulos vizinhos que o bloco toca.
2. Produza a lista de PRs, por fatias verticais usáveis, no formato de `D-066` e `D-071`: nome da branch, escopo (`F-XXX-NN`), critérios de aceite verificáveis, o que fica fora. O último PR é o E2E e o fechamento (`D-070`).
3. **GATE 1:** o usuário aprova o plano. Só então o código começa.

## 3. Por PR, em sequência

1. Branch via `altare-git-fluxo`.
2. `altare-api-dev`, se houver backend.
3. `altare-web-dev`, se houver UI, já com os tipos gerados (`make api-types`) no diff.
4. **Você** reroda `make lint typecheck test` e lê o `git diff` real. O relatório do agente não prova nada.
5. Dois `altare-reviewer` **em paralelo**, com lentes diferentes: `corretude` sempre; mais `seguranca-lgpd` (dado de convidados, sessão, upload, exportação, log) ou `design-a11y` (UI), conforme o PR.
6. Triagem dos achados:
   - `bloqueia` com citação volta ao dev, **retomando o mesmo subagent** (`SendMessage`), e depois repete o passo 4;
   - `corrija` e `sugestão`: o usuário decide;
   - `bloqueia` sem arquivo:linha e regra violada vira `sugestão`.
7. **GATE 2:** o usuário vê o diff e os pareceres.
8. `/altare-commit` (**GATE 3**) e `/altare-pull-request` (**GATE 4**): o usuário as digita, porque ambas bloqueiam a invocação pelo modelo.
9. Com o OK do usuário, registre as `D-xxx` e a fase com `altare-docs-vivas`, na sessão principal.

## 4. Modelo de prompt de delegação

O subagent não vê a conversa. Todo prompt traz, nesta ordem:

```
Bloco e PR: <bloco> / PR <n> de <total>, branch <nome>
Feature: docs/product/features/<arquivo>.md, itens F-XXX-NN
Decisões: D-xxx, D-yyy
Critérios de aceite: <lista copiada do plano aprovado>
Fora do escopo (não toque): <arquivos, módulos, comportamentos>
Já decidido na conversa: <respostas do usuário que mudam o plano>
Formato do relatório: o de altare-<api|web>-dev (arquivos, testes, comandos com resultado real, desvios, decisões a registrar, perguntas)
As skills altare-* do seu papel já estão pré-carregadas: não as recarregue.
```

Para o reviewer: base (`develop`), feature, `D-xxx`, a lente e "sem rodar lint, typecheck nem testes".

## 5. Regras

- Subagents nunca commitam, nem fazem push ou PR, nem registram decisões.
- Em conflito vale o documento, depois a skill, depois o agente.
- Dúvida de produto que a feature não responde vai ao usuário (`AGENTS.md` §3), com proposta reversível. Não invente.
- O E2E do bloco é um PR final, como na `D-070`.
- O release (`develop → main` e a tag) é do usuário (`altare-git-fluxo`).
- Relatório de agente com gate vermelho ou desvio sem explicação volta ao agente antes de chegar ao usuário.

## Limites e vizinhas

- Uma correção pontual ou um PR avulso não usa esta skill: siga `altare-git-fluxo`.
- A pergunta "devo construir isto?" é de `altare-produto`.
