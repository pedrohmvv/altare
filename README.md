# Altare

> *O altar no centro. A festa a serviço.*

O **Altare** é um app de planejamento de casamento para o casal, feito para o uso pessoal do autor e da noiva. Ele troca a planilha, a pasta de contratos e o grupo de mensagens por um só lugar onde as decisões, os convidados, o cronograma e o dinheiro conversam entre si.

O projeto é **pessoal**, não é um produto aberto a outros casais, e **não confessional**: o tipo de cerimônia (religiosa de qualquer tradição, civil ou simbólica) é um dado do casal, nunca uma suposição. O diretório e o repositório de origem se chamam `wedding-planner`.

## O que ele faz

O trabalho está organizado em uma pirâmide de blocos, do alicerce ao topo (`docs/engineering/roadmap.md`):

| Nível | Tema |
| :--- | :--- |
| 0 | Fundação: design system, login dos dois perfis, banco e arquivos |
| 1 | Base do casamento: definições, mapa de escopo, convidados e cronograma com dependências |
| 2 | Orçamento vivo, simulador de orçamentos em paralelo e comparador de cenários macro |
| 3 | Contatos e fornecedores, comparador de propostas, contratos e parcelas |
| 4 | Enxoval e lista de presentes, centro de comando e dossiê do dia D |
| 5 | Camada de IA: rascunhos com confirmação humana, revisão proativa e assistente conversacional |

Os Níveis 0 e 1 estão em construção ou concluídos; os seguintes estão especificados e aguardam a vez. A fase atual e o próximo passo ficam sempre em [`AGENTS.md`](./AGENTS.md) §1, que é a fonte de verdade do estado do projeto. Este README não repete esse estado para não envelhecer.

O app tem **dois logins individuais** (`Noivo` e `Noiva`). A autoria de cada alteração vem da sessão; o seletor de lente da interface só muda o recorte que cada um vê. Não há cadastro público.

## Stack

| Parte | Tecnologia |
| :--- | :--- |
| `apps/api` | Python 3.13, FastAPI, SQLAlchemy 2 (síncrono), Alembic, Pydantic v2, Typer, `uv` |
| `apps/web` | React 19, TypeScript, Vite, TanStack (Router e Query), React Hook Form e Zod, Tailwind v4, PWA instalável, `pnpm` |
| Dados | SQLite no início, com caminho para PostgreSQL ao ir para a nuvem; arquivos em disco local atrás de uma interface `FileStorage` |
| Qualidade | Ruff, Pyright, `import-linter`, pytest e Hypothesis; Biome, `tsc`, Vitest e Playwright; `pre-commit` e GitHub Actions |

A API é um monólito modular em camadas (domínio, aplicação, adaptadores e infraestrutura), com um módulo por área (`identity`, `files`, `wedding`, `guests`, `schedule`, e os próximos). O contrato OpenAPI gera os tipos do front, e o CI barra o *drift*. Detalhes em [`docs/engineering/stack.md`](./docs/engineering/stack.md) e [`docs/engineering/architecture.md`](./docs/engineering/architecture.md).

## Estrutura do repositório

```
apps/api/        API FastAPI (uv); módulos em src/wedding/modules/, migrations em migrations/
apps/web/        SPA/PWA React (pnpm); telas em src/features/, primitivos em src/components/ui/
tools/api-types/ Tipos TypeScript gerados do OpenAPI da API
docs/            Documentação viva de produto, design e engenharia
scripts/         Utilitários do repositório (CI, regras do Cursor)
data/            Banco e arquivos locais (fora do git)
.claude/         Skills, subagents e hooks do trabalho com o Claude Code
```

## Como rodar

**Pré-requisitos:** [`uv`](https://docs.astral.sh/uv/) com Python 3.13, Node 22.12 ou mais novo e `pnpm` 10.

```bash
# 1. Dependências
pnpm install
(cd apps/api && uv sync)

# 2. Banco local (SQLite em data/altare.db)
make migrate

# 3. Os dois logins do casal (a senha é pedida sem aparecer na tela)
(cd apps/api && uv run wedding create-user --profile Noivo --username <usuario>)
(cd apps/api && uv run wedding create-user --profile Noiva --username <usuario>)

# 4. API em 127.0.0.1:8000 e web com o proxy de /api
make dev
```

Abra o endereço que o Vite mostrar no terminal. `make dev` sobe a API com o cookie de sessão sem `Secure`, só para o desenvolvimento local.

Variáveis de ambiente da API (todas opcionais no desenvolvimento): `DATABASE_URL` (padrão `data/altare.db`), `FILES_DIR` (padrão `data/files`) e `SESSION_COOKIE_SECURE` (padrão `true`).

## Comandos

Tudo é chamado pelo `Makefile` na raiz, que só orquestra os scripts do `pnpm` e do `uv`.

| Comando | O que faz |
| :--- | :--- |
| `make dev` | API e web em desenvolvimento |
| `make lint` · `make typecheck` · `make test` | Os gates de qualidade das duas pontas (`-api` e `-web` rodam uma só) |
| `make e2e` | Testes de ponta a ponta com Playwright (build de produção e API de verdade) |
| `make build` | Build de produção do web |
| `make migrate` | Aplica as migrations do banco |
| `make api-types` | Exporta o OpenAPI e regenera os tipos do front |
| `make tokens` · `make brand` | Regeneram o `tokens.css` e os ativos de marca a partir do `tokens.json` |

Antes de abrir um PR, `make lint`, `make typecheck` e `make test` precisam estar verdes. O check `CI` é exigido na `develop` e na `main`.

## Fluxo de trabalho

O trabalho sai da `develop` em `<tipo>/<assunto>` e volta por PR com *merge commit*, sem *squash*. A `main` guarda o que está pronto e recebe release por PR da `develop`, com tag `vX.Y.Z`. Os commits seguem Conventional Commits, com o tipo em inglês e a descrição em português. As regras completas estão em [`AGENTS.md`](./AGENTS.md) e na decisão `D-041`.

## Documentação

Toda a documentação é viva e escrita em português. Cada decisão relevante fica registrada em [`docs/product/decisions.md`](./docs/product/decisions.md), com data, razão e alternativas rejeitadas.

| Para | Leia |
| :--- | :--- |
| Entender o produto | [`docs/product/vision.md`](./docs/product/vision.md), [`personas.md`](./docs/product/personas.md), [`jobs.md`](./docs/product/jobs.md) e [`scope.md`](./docs/product/scope.md) |
| Ver cada feature em detalhe | [`docs/product/features/`](./docs/product/features/) |
| Conhecer a identidade e o design system | [`docs/design/identity.md`](./docs/design/identity.md), [`docs/design/design-system.md`](./docs/design/design-system.md) e [`docs/design/identidade-visual/`](./docs/design/identidade-visual/) |
| Entender a engenharia | [`docs/engineering/README.md`](./docs/engineering/README.md), [`stack.md`](./docs/engineering/stack.md), [`architecture.md`](./docs/engineering/architecture.md) e [`roadmap.md`](./docs/engineering/roadmap.md) |
| Saber o que está em aberto | [`docs/product/open-questions.md`](./docs/product/open-questions.md) |

## Trabalhando com agentes de IA

O repositório tem um contrato operacional único e agnóstico de ferramenta em [`AGENTS.md`](./AGENTS.md), que o `CLAUDE.md` da raiz apenas aponta. As skills `altare-*` em `.claude/skills/` codificam as decisões já registradas, e o time de agentes em `.claude/agents/` executa um bloco do roadmap com plano aprovado, revisão independente e gates verdes.
