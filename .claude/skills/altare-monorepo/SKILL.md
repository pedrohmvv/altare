---
name: altare-monorepo
description: >-
  Estrutura e disciplina do monorepo do Altare: apps/api (Python, uv) e apps/web (React, pnpm), Makefile e scripts na raiz, regra de dependência entre os apps (só pelo contrato OpenAPI), geração de tipos TypeScript com checagem de drift, arquivos gerados que nunca se editam à mão, packages/ só com segundo consumidor real, CI com path filters e a decisão D-040 de não usar git submodules, para que API e web mudem em PRs e commits atômicos. Use sempre que for criar ou mexer em pastas de topo, Makefile, workspace pnpm, pyproject, geração de tipos do OpenAPI, ou ao fazer uma mudança que atravessa API e web, mesmo que o usuário não fale em monorepo. NÃO use para hospedagem, Docker e deploy (use altare-devops), para camadas internas de um módulo (use altare-arquitetura) nem para rotas e erros HTTP (use altare-backend-api).
---

# Monorepo

Uma rota nova e a tela que a usa mudam juntas. No mesmo repositório elas entram em **um PR**, com a CI enxergando as duas pontas. Com submódulos seriam dois PRs, sem commit atômico e com a CI de um lado cega ao outro (`D-040`).

## Docs a consultar

- `docs/engineering/stack.md` §2 (visão), §5 (contrato da API e tipos gerados), §7 (CI e comandos) e §8 (estrutura do repositório).
- `docs/engineering/architecture.md` §4 (backend), §9 (snapshot do OpenAPI) e §11 (frontend).
- `docs/product/decisions.md` D-040 e D-028 (ordem: `apps/web` primeiro; API, banco e login depois).
- `docs/design/design-system.md` §12 (`tokens.css` é gerado).

## Estrutura

```
wedding-planner/
├─ apps/api/     Python: pyproject.toml e uv.lock próprios
├─ apps/web/     React: pnpm
├─ data/         gitignored (SQLite e uploads de desenvolvimento)
├─ docs/
├─ Makefile      ponto de entrada de todas as tarefas
└─ AGENTS.md · CLAUDE.md
```

**Estado atual:** `apps/web` e `apps/api` existem (esqueleto da API em `D-060`); os alvos do Makefile crescem junto, sem stub: `make api-types` só entra com o PR 2 do Bloco 0.1.

## Princípios

1. **Sem git submodules** (`D-040`). Não proponha, não adicione e remova se aparecer.
2. **Os apps só se falam pelo OpenAPI.** `apps/web` não importa código de `apps/api` e o contrário também não. Enum, nome de campo e formato de erro chegam ao web pelos tipos gerados; copiar a lista de valores de um enum para o TypeScript cria a segunda verdade que o contrato existe para evitar.
3. **Tarefas na raiz via `make`:** `make dev`, `make lint`, `make typecheck`, `make test` (com variantes `-api` e `-web`), `make migrate` e, a partir do PR 2, `make api-types` (`stack.md` §7). O Makefile só orquestra (`uv run`, `pnpm`); lógica não mora nele.
4. **`packages/` só nasce com o segundo consumidor real.** Hoje não há nenhum. O `tokens.json` fica em `docs/design/identidade-visual/` e um script gera o `tokens.css`; isso não é motivo para criar pacote.
5. **Arquivo gerado nunca se edita à mão:** `apps/web/src/styles/tokens.css` (de `tokens.json`) e os tipos do OpenAPI. Mude a fonte e regenere; o CI falha se o gerado divergir.
6. **Contrato e tipos andam no mesmo commit.** Quem altera uma rota ou schema regenera os tipos (`make api-types`) no commit que muda o contrato. A tela que consome vem no commit seguinte do **mesmo PR**.

## Contrato OpenAPI para tipos TypeScript

1. O backend exporta o OpenAPI (`wedding export-openapi`, CLI Typer, `stack.md` §3), com `operationId` estável por rota.
2. `openapi-typescript` gera os tipos; `openapi-fetch` e `openapi-react-query` os consomem no web.
3. **Checagem de drift:** o CI roda `make api-types` e falha se `git diff` não estiver vazio. Um teste de adaptador também guarda o *snapshot* do OpenAPI (`architecture.md` §9).
4. **Caminhos (`D-059`):** o artefato versionado é `apps/api/openapi.json` e os tipos gerados ficam em `apps/web/src/lib/api/schema.d.ts`.

## CI com *path filters*

| Filtro de caminho | Roda |
| :--- | :--- |
| `apps/api/**` | gates do backend **e a checagem de drift** |
| `apps/web/**`, artefato do OpenAPI e `docs/design/identidade-visual/tokens.json` | gates do frontend |
| `Makefile`, arquivos de CI, `pnpm-workspace.yaml` | tudo |

O filtro vive em `scripts/ci-changes.sh` (shell, sem ação de terceiros) e o workflow em `.github/workflows/ci.yml` (`D-060`).

**Ressalva:** uma mudança em `apps/api/**` que altera o contrato **também precisa rodar o web**, porque o tipo gerado mudou. O drift check no job da API pega o esquecimento de regenerar, e o artefato versionado dispara o job do web. Se o provedor tratar job pulado por filtro como pendente e travar o merge, use um job final agregador. O pipeline em si é de `altare-devops`.

## Checklist

- [ ] A mudança que cruza API e web está em um só PR, com commits por intenção?
- [ ] Os tipos do OpenAPI foram regenerados e o `git diff` do gerado está limpo?
- [ ] Nada foi importado de um app no outro, nem enum copiado à mão?
- [ ] Nenhum arquivo gerado foi editado manualmente?
- [ ] `packages/` ou submódulo não foi criado sem necessidade?
- [ ] O alvo novo do Makefile só orquestra comando?

## Limites e vizinhas

- Pipeline, ambientes e deploy: `altare-devops`. Gates e testes: `altare-testes-qa`.
- Camadas dentro do backend e do frontend: `altare-arquitetura` e `altare-frontend`.
- Convenções de rota, `operationId` e erros: `altare-backend-api`.
- Fluxo de branches, commits e PR: `altare-git-fluxo`, `altare-commit` e `altare-pull-request`.

## Em aberto

- Nada em aberto: o caminho do OpenAPI e o provedor de CI (GitHub Actions) foram definidos em `D-059`.
