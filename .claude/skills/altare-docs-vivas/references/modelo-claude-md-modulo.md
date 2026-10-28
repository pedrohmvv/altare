# Modelo de `CLAUDE.md` de módulo

Salvar em `apps/api/src/wedding/modules/<módulo>/CLAUDE.md` no mesmo commit que cria a pasta (`D-039`). Máximo de 40 linhas. Substitua tudo entre `<>`. Apague o que não se aplica em vez de deixar vazio.

````markdown
# Módulo `<módulo>`

> Regras gerais: leia `AGENTS.md` (raiz) e os docs abaixo. Este arquivo só traz o que é específico do módulo.

**Propósito:** <o que o módulo é dono, em uma frase>. <O que ele não é dono, em uma frase.>

## Superfície pública
- `application/public.py`: <casos de uso e consultas que outros módulos podem chamar>.
- `domain/events.py`: <eventos que publica ou consome; catálogo em `docs/engineering/architecture.md` §6>.

Nada além disso pode ser importado por outro módulo (`architecture.md` §4; contrato 5 de §9).

## Invariantes
- <regra que nunca pode ser violada, com o ID da feature, ex.: `F-XXX-03`>.
- <regra de integridade que o domínio garante sem depender do banco>.

## Dependências permitidas
- Importa de: <módulos>, só via `application/public.py` ou `domain/events.py`.
- Não importa: entidades, tabelas nem repositórios de outro módulo.
- Camadas: domínio só usa a biblioteca padrão e o `shared_kernel` (`architecture.md` §2 e §9).

## Docs
- Features: `docs/product/features/<arquivo>.md` (`F-XXX-01` a `F-XXX-nn`).
- Decisões: `D-0xx`, `D-0xx`.
- Arquitetura e domínio: `docs/engineering/architecture.md` §<n>; `docs/engineering/stack.md` §<n>.
- Web: `apps/web/src/features/<módulo>/` (quando existir).

## Como testar
- `make test-api` e `make lint-api` na raiz (`stack.md` §7).
- Domínio: pytest puro. Aplicação: fakes das portas. Infraestrutura: SQLite real (`architecture.md` §9).
- Contratos de import: `import-linter` no `make lint`.
````

## Regras

1. Não repita regra geral (camadas, nomes, commits): ela vive em `AGENTS.md` e nas skills `altare-*`.
2. Invariantes são poucas e verificáveis. Se passa de 5, o módulo provavelmente deveria ser dividido.
3. Atualize o arquivo quando a superfície pública, uma invariante ou uma dependência mudar, no mesmo commit.
4. Os comandos de teste só deixam de ser "pendentes" quando existirem no `Makefile`.
