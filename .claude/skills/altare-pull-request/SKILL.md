---
name: altare-pull-request
description: >-
  Como abrir e descrever um pull request no Altare com gh: base develop (ou main em hotfix e release), título no padrão de commit, corpo em pt-BR com o que muda e por quê, decisões D-xxx, como testar e um checklist de gates, docs vivas, CLAUDE.md de módulo, acessibilidade e conferência com o guia de identidade (captura quando houver mudança visual), merge commit sem squash e o PR de volta para a develop quando for hotfix. Use quando o usuário pedir para abrir, criar ou subir um PR, fechar a branch, ou preparar a descrição de uma mudança para integração, mesmo que ele não diga pull request. NÃO use para decidir o nome da branch ou o fluxo de release (use altare-git-fluxo), para commitar (use altare-commit) nem para revisar o diff (use altare-code-review).
---

# Pull request

O PR é onde a intenção, as decisões e a prova de que funciona ficam juntas. Quem lê (o próprio autor, meses depois) precisa entender o porquê sem abrir o diff.

## Docs a consultar

- `docs/design/design-system.md` §15 (mapa guia → componente), para PR que muda UI.
- `docs/product/decisions.md` D-041 (bases e estratégia de merge) e D-040 (PR atômico entre API e web).
- `docs/engineering/stack.md` §7 (gates) e `AGENTS.md` §2, regra 5 (docs vivas).

## Regras

1. **Só abra o PR quando o usuário pedir.** Pedir commit não é pedir PR, e PR não implica `push` sem confirmação.
2. **Confira a base antes de criar:** `develop` para trabalho comum; **`main` para hotfix e para release** (`develop → main`). Base errada integra código não validado.
3. **Título no padrão de commit** (`altare-commit`): `tipo(escopo): descrição em pt-BR`.
4. **Corpo em pt-BR**, escrito para quem não viu a conversa.
5. **Merge commit, sem *squash*** (`gh pr merge --merge`), e só quando o usuário mandar integrar.
6. **Hotfix:** depois do PR para a `main`, abra também o PR da mesma branch para a `develop` (`altare-git-fluxo`).
7. **Rodapé de atribuição:** use o que a ferramenta em uso indicar.

## Modelo do corpo

```markdown
## O que muda e por quê
<2 a 5 linhas: o problema, a solução e o efeito para o casal ou para o código>

## Decisões
- D-0xx: <uma linha>   (ou "Nenhuma decisão nova")

## Como testar
1. <passo>  2. <passo>  <resultado esperado>

## Checklist
- [ ] Gates verdes (`altare-testes-qa`): Ruff, Pyright, import-linter, pytest, Biome, tsc, Vitest (inclui o gate de limites do frontend)
- [ ] Contrato OpenAPI e tipos regenerados, sem drift (se tocou a API)
- [ ] Docs vivas atualizadas: `decisions.md`, doc de feature, `AGENTS.md` se a fase mudou (`altare-docs-vivas`)
- [ ] `CLAUDE.md` criado ou atualizado, se há módulo novo
- [ ] Acessibilidade conferida manualmente (`altare-acessibilidade`), se tocou UI
- [ ] Comparado com o guia (mapa em `design-system.md` §15), com captura quando houver mudança visual; desvios com `D-xxx` (`altare-design`)
- [ ] Sem dados reais do casamento, segredos ou `data/`
```

Apague do checklist o que não se aplica e **diga por quê** quando um item bloqueante ficar de fora; item riscado em silêncio é o que o review deixa passar.

## Comando

```bash
git rev-parse --abbrev-ref HEAD     # confirme a branch de origem
gh pr create --base develop \
  --title "feat(budget): calcula o custo comparável com extras" \
  --body-file <arquivo-com-o-corpo>
```

Use `--body-file` (ou *heredoc*) em vez de `--fill`: o corpo precisa seguir o modelo. Para release, a base é `main` e o título descreve o que foi concluído (por exemplo `chore(release): conclui o Bloco 2.1`); a *tag* é criada depois do merge, conforme `altare-git-fluxo`.

## Checklist de abertura

- [ ] A branch foi publicada com autorização do usuário?
- [ ] A base é a correta (`develop`; `main` em hotfix ou release)?
- [ ] O título segue `tipo(escopo): descrição`?
- [ ] O corpo cita as decisões `D-xxx` e diz como testar?
- [ ] Mudança que cruza API e web está inteira neste PR (`D-040`)?

## Limites e vizinhas

- Branch, release, hotfix e estratégia de merge: `altare-git-fluxo`.
- Mensagens e plano de commits: `altare-commit`.
- Avaliar o diff: `altare-code-review`. Gates e o que cada um cobre: `altare-testes-qa`.
- Atualização das docs vivas: `altare-docs-vivas`.
