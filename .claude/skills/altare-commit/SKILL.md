---
name: altare-commit
description: >-
  Como commitar no Altare: commits atômicos por intenção, com plano mostrado e aprovado antes de executar, no formato Conventional Commits com tipo em inglês e descrição em pt-BR no presente (por exemplo docs(product) detalha as features da v1 manual), corpo em prosa citando as decisões D-xxx. É o único caminho de commit neste repositório (D-039). Use sempre que o usuário pedir para commitar, salvar as mudanças, fechar o trabalho, ou ao terminar um ciclo de mudanças antes do PR, mesmo que ele não diga commit. NÃO use para decidir branch, release ou hotfix (use altare-git-fluxo), para abrir o PR (use altare-pull-request) nem para merge, rebase ou revert, que o usuário conduz.
---

# Commits atômicos

Cada commit conta **uma intenção**, e o histórico lido em ordem conta a história do produto. Por isso o merge é feito sem *squash* (`D-041`): o valor dos commits só existe se eles forem pequenos e honestos.

## Docs a consultar

- `docs/product/decisions.md` D-039 e D-041; `git log` do próprio repositório como referência viva do estilo.
- `AGENTS.md` §2, regra 5 (documentação viva atualizada na mesma mudança).

## Formato

```
tipo(escopo): descrição no presente, em pt-BR, sem ponto final

Corpo em prosa, quebrado em ~72 colunas, explicando o que muda e por
que, e citando as decisões (D-029 a D-038).
```

- **Tipo em inglês:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `build`, `perf`.
- **Descrição em pt-BR, no presente** ("detalha", "reduz", "registra"), alvo de ~72 colunas na linha toda. O histórico real chega a 80 quando carrega `D-xxx`; evite passar disso.
- **Escopo:** nos docs, os já usados no repositório: `product`, `design`, `engineering`. No código, o módulo (`budget`, `guests`, `contracts`...) ou `api` e `web`. Para ferramental, `skills` ou `agents` (para o `AGENTS.md`).
- **Corpo:** prosa, sem lista de arquivos (o diff já mostra). Cite `D-xxx` quando a mudança implementa ou registra uma decisão.
- **Trailer de coautoria:** use o que a ferramenta em uso indicar. O histórico existente usa `Co-authored-by:`.

Exemplos reais do repositório:
`docs(product): detalha as features da v1 manual, área por área (D-029 a D-038)` ·
`docs(engineering): reduz o design system ao escopo enxuto (D-028)`.

## Fluxo

1. **Leia o estado:** `git status` e `git diff` (e `git diff --staged`). Identifique arquivos que não pertencem à mudança (`.env`, `data/`, binários, arquivos gerados fora de hora) e **não os inclua**.
2. **Agrupe por intenção.** Regras de agrupamento:
   - Código e o teste dele vão **juntos**, para todo commit deixar a suíte verde.
   - Migration, mapeamento e o código que depende dela vão juntos.
   - Arquivo gerado (tipos do OpenAPI, `tokens.css`) vai com a fonte que o gerou.
   - Documentação viva que registra a mudança (`D-xxx`, doc de feature, `AGENTS.md`) vai junto se for a mesma intenção; se for outra (ajuste de processo, por exemplo), vira commit `docs` separado.
   - Refatoração sem mudança de comportamento não se mistura com `feat` ou `fix`.
3. **Mostre o plano e espere aprovação.** Nada é commitado antes de o usuário aprovar:

```
Plano de commits (2)
1. feat(budget): calcula o custo comparável com extras em centavos
   arquivos: apps/api/src/wedding/modules/budget/domain/rules.py,
             apps/api/tests/budget/test_rules.py
2. docs(product): registra a regra de arredondamento (D-0xx)
   arquivos: docs/product/decisions.md
```

4. **Execute em sequência**, adicionando **arquivos por nome** (`git add <arquivos>`). Nunca `git add -A` ou `git add .` às cegas: levaria arquivo que o plano não previu.
5. **Se um hook falhar, corrija a causa e crie um commit novo.** Nunca use `--no-verify` nem `--amend` em commit já publicado.
6. **Confira com `git log --oneline` e `git status`** e reporte os hashes.

## Regras de segurança

- Não faça `commit` nem `push` sem o usuário pedir. Pedir commit **não** autoriza `push`.
- Nunca commite segredo, `.env` (só `.env.example`), base SQLite, upload de teste ou dado real do casamento.
- Não reescreva histórico compartilhado, nem faça merge, rebase ou revert sem o usuário conduzir.

## Bom / ruim

| Ruim | Bom |
| :--- | :--- |
| `feat: mudanças no orçamento` | `feat(budget): ativa um único cenário oficial por vez` |
| Um commit com migration, tela e ajuste de doc | Três commits, um por intenção |
| `fix: corrige bug.` (ponto, vago) | `fix(contracts): soma a última parcela sem perder centavos` |
| Mensagem em inglês na descrição | Descrição em pt-BR, tipo em inglês |

## Limites e vizinhas

- Em qual branch trabalhar e quando integrar: `altare-git-fluxo`. Abrir e descrever o PR: `altare-pull-request`.
- Gates que devem passar antes de commitar: `altare-testes-qa`.
- Como registrar `D-xxx` e atualizar docs: `altare-docs-vivas`.
