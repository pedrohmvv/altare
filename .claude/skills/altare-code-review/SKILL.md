---
name: altare-code-review
description: >-
  Checklist de revisão de diff ou PR do Altare, por severidade (bloqueia, corrija, sugestão), somente
  leitura. Use ao revisar, dar parecer ou conferir um diff, branch ou PR, e antes de sugerir o merge
  de qualquer mudança.
---

# Code review

Revisar é ler a mudança contra as decisões já tomadas, não contra o gosto de quem revisa. O Altare tem dono único e dois usuários: o review existe para pegar o que o autor não enxerga (camada quebrada, centavo errado, dado vazado), não para renegociar estilo.

## Docs a consultar

- Se o diff toca `apps/web`: o mapa guia → componente (`docs/design/design-system.md` §15) e a página do guia correspondente.
- `AGENTS.md` §2 (regras inegociáveis) e `docs/product/decisions.md` (a decisão `D-xxx` que a mudança implementa ou contraria).
- O doc de feature da área (`docs/product/features/*.md`) para os critérios de aceite.
- `docs/engineering/architecture.md` §2 e §9, e `docs/engineering/stack.md` §4 e §7.

## Princípios

1. **Leia a intenção primeiro**: título, descrição do PR e `D-xxx` citado. Um diff correto para a intenção errada continua errado.
2. **Somente leitura por padrão.** Não edite código, não poste comentário no PR e não aprove sem o usuário pedir. O produto do review é o relatório.
3. **Cada achado traz arquivo e linha, o que está errado, por que importa e a correção.** Achado sem correção sugerida só passa ansiedade.
4. **Aponte a skill dona da regra** em vez de reexplicá-la, para a regra viver em um lugar só.
5. **Nada a corrigir é um resultado válido.** Não invente achado para parecer útil; diga o que conferiu.
6. **Não revise o que o gate já garante** (formatação, `import-linter`, tipos). Confira que o gate rodou verde.

## Checklist por severidade

### Bloqueia (não integra)

- UI sem conferência contra a página do guia, ou valor divergente sem decisão registrada (`altare-design`, "Fonte visual: o guia"; mapa em `design-system.md` §15). Peça a captura ao lado do PNG da página, ou o desvio em `decisions.md`.
- Import que quebra a regra de dependência ou atravessa módulo sem `public.py` (`altare-arquitetura`).
- Escrita de agente sem `ChangeProposal` e confirmação humana (`altare-agente-dados`, `D-008`).
- Autoria vinda do cliente em vez da sessão, ou rota sem autorização (`altare-seguranca-privacidade`, `altare-backend-api`).
- Dinheiro em `float`, ou regra numérica reimplementada no frontend (`altare-escrita-de-codigo`).
- Migration sem `downgrade`, enum nativo do banco, ou SQL específico de SQLite (`altare-banco-de-dados`).
- Segredo, `.env`, stack trace ou dado de terceiros no código, no log ou na resposta de erro.
- Dado real ou inventado do casamento no código, em teste ou em exemplo (`AGENTS.md` §2, regra 4).
- Comportamento novo sem teste, ou teste que nunca falhou (`altare-testes-qa`).
- Mudança de decisão registrada sem novo `D-xxx` (`altare-docs-vivas`).

### Corrija (antes do merge, salvo justificativa)

- Teste só do caminho feliz; regra com borda (arredondamento, zero convidados, parcela única) sem caso.
- Sinais de código de IA: comentário óbvio, abstração de um uso, `except` amplo, nome genérico (`altare-escrita-de-codigo`).
- Duplicação de regra entre camadas ou entre apps.
- Tela sem estado vazio, carregando ou erro, ou com texto fora do tom (`altare-ui-ux`, `altare-conteudo-copy`).
- Mudança de UI sem a verificação manual de acessibilidade (`altare-acessibilidade`).
- Contrato OpenAPI alterado sem tipos regenerados (`altare-monorepo`).
- Módulo novo sem `CLAUDE.md`, ou doc de feature e `AGENTS.md` desatualizados (`altare-docs-vivas`).
- Commit misturando intenções ou fora do padrão (`altare-commit`).

### Sugestão (não bloqueia)

- Nome mais claro, função que pode ficar menor, simplificação local.
- Melhoria de teste existente sem risco de regressão.

## Formato de saída

```
Revisão de <branch ou PR> (<n> arquivos, <n> commits) · intenção: <uma linha, com D-xxx>

Bloqueia
1. caminho/arquivo.py:42 · <o que está errado>
   Por quê: <consequência para o casal ou para o código>
   Correção: <ação concreta>  (regra em: altare-xxx)

Corrija
...
Sugestão
...
Conferido sem achados: <camadas, dinheiro, autoria, migrations, testes, a11y...>
Gates: <verdes / não rodados>
```

Se não houver achado, escreva "Nada a corrigir" e liste o que foi conferido. Uma lista vazia sem a seção "Conferido" não prova que alguém olhou.

## Bom / ruim

- Ruim: "Poderia usar um padrão Factory aqui." Bom: "`pricing.py:58` cria `PricingStrategyFactory` para uma única estratégia; remova e chame a função (`altare-escrita-de-codigo`, abstração especulativa)."
- Ruim: "Cuidado com segurança." Bom: "`router.py:31` lê `created_by` do corpo; a autoria vem da sessão (`altare-seguranca-privacidade`). Bloqueia."

## Limites e vizinhas

- Aqui se **avalia**; escrever e corrigir é `altare-escrita-de-codigo`.
- As regras de cada área moram nas skills citadas; o review só confere e aponta.
- Gates e cobertura: `altare-testes-qa`; execução no CI: `altare-devops`.
- Formato de commit e PR: `altare-commit` e `altare-pull-request`.
