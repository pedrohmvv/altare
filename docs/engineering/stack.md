# Stack Técnica Detalhada (`docs/engineering/stack.md`)

> **Status:** **APROVADA pelo usuário em 2026-10-26 (`D-021`, resolve `OQ-ENG-003`); parcialmente refinada por `D-022` (arquitetura em [`architecture.md`](./architecture.md), design em `docs/design/`).** As 5 decisões estruturais estão em `D-020`; o detalhamento abaixo é a stack oficial. Mudanças futuras exigem nova decisão registrada.
>
> Este documento **substitui parcialmente `D-019`** (que previa Next.js + Drizzle/Prisma + Supabase) e detalha a stack em nível granular.

---

## 1. Decisões Travadas (`D-020`)

| # | Tema | Decisão | Alternativas rejeitadas |
| :-- | :--- | :--- | :--- |
| 1 | Backend | **Python** (FastAPI) | Backend em Node/Next.js (`D-019` original) |
| 2 | Frontend | **React + TypeScript + Vite como SPA/PWA estática**, consumindo a API FastAPI | Next.js só como frontend (dois servidores, sem ganho de SSR); Python puro com HTMX (interações ricas e PWA mais trabalhosas) |
| 3 | Banco | **SQLite no início**, migração para PostgreSQL ao ir para a nuvem | PostgreSQL desde o dia 1 via Docker (recomendação do agente, não adotada — ver §5 para as mitigações) |
| 4 | Hospedagem | **Local nos Níveis 0 e 1**; nuvem (backend + Postgres gerenciado + storage S3-compatível) quando o Nível 1 estiver utilizável | Nuvem desde o Nível 0; servidor doméstico com Tailscale |
| 5 | Login e perfis | **Dois logins individuais** (`Noivo` e `Noiva`); autoria vem do login; o seletor alterna a *lente de visão* | Login único do casal com seletor autodeclarado |

---

## 2. Visão de Arquitetura

```
 Celular (PWA instalada)         Computador (navegador)
          \                         /
           \                       /
        ┌───────────────────────────────┐
        │  SPA React (apps/web)         │   build estático
        └──────────────┬────────────────┘
                       │ HTTPS · JSON · cookie de sessão (mesma origem)
        ┌──────────────▼────────────────┐
        │  FastAPI (apps/api)           │   monólito modular
        │  routers → services → rules   │
        ├───────────────┬───────────────┤
        │ SQLAlchemy 2  │ FileStorage   │   interface única
        └───────┬───────┴───────┬───────┘
                │               │
         SQLite (→ Postgres)   Disco local (→ S3-compatível)
```

Princípios que guiam as escolhas:
1. **Um único deploy unit:** em produção o FastAPI serve a SPA buildada e a API na **mesma origem** (cookies simples, sem CORS).
2. **Fonte única de cálculo:** toda regra de negócio numérica (orçamento, custo comparável, contagem ponderada de convidados, destravamento do cronograma) vive **só em Python**. O frontend exibe e pede recálculo; não reimplementa regra.
3. **Portabilidade por contrato:** nada no código assume SQLite nem disco local (`DATABASE_URL` e `STORAGE_BACKEND` por ambiente).
4. **Fluxo manual completo sem IA** (`D-005`); a IA (Nível 5) se acopla depois sobre o mesmo modelo, via estados de rascunho.
5. **Simplicidade proporcional:** 2 usuários, 1 casamento. Sem filas, cache distribuído, microsserviços ou multi-tenant (`D-002`).

---

## 3. Backend (`apps/api`)

| Camada | Escolha proposta | Por quê | Alternativa considerada |
| :--- | :--- | :--- | :--- |
| Linguagem / versão | **Python ≥ 3.12** (a mais recente suportada por todas as dependências no momento do setup) | Tipagem moderna, `uv` maduro | — |
| Gerência de projeto | **`uv`** (venv, lockfile, `uv run`) + `pyproject.toml` | Rápido, lock reprodutível, padrão atual | Poetry, pip-tools |
| Framework web | **FastAPI** + Uvicorn | OpenAPI automático (gera tipos do frontend), validação Pydantic, tipagem forte | Django (admin e ORM prontos, porém mais pesado e menos alinhado ao SPA), Litestar |
| Validação / config | **Pydantic v2** + `pydantic-settings` (`.env`) | Schemas de entrada/saída e config tipada | — |
| ORM | **SQLAlchemy 2.0** (estilo tipado `Mapped[...]`), **modo síncrono** | Maduro, funciona igual em SQLite e Postgres; síncrono evita complexidade de `aiosqlite` e é suficiente para 2 usuários | SQLModel (menos controle), Tortoise, SQLAlchemy async |
| Migrações | **Alembic** (`render_as_batch=True` para SQLite) | Padrão do SQLAlchemy; histórico versionado | — |
| Autenticação | **Própria e mínima**: `argon2-cffi`, **sessões server-side** em tabela, cookie `HttpOnly` + `SameSite=Lax` + `Secure` (em produção), proteção CSRF por header customizado, rate limit simples no login, **sem cadastro público** (usuários criados por comando CLI) | Só 2 contas; evita dependência de provedor externo e JWT em localStorage | `fastapi-users`, Supabase Auth, passkeys/WebAuthn (candidato a evolução futura) |
| Arquivos | Interface **`FileStorage`** com `LocalFileStorage` (disco, nome por hash SHA-256, fora da pasta pública, servido por endpoint autenticado) e `S3FileStorage` (`boto3`, compatível com R2/Backblaze/Supabase Storage S3) | Troca de backend sem mexer em regra de negócio | Armazenar blob no banco |
| Validação de upload | Tipo MIME + assinatura real do arquivo (PDF/imagem), limite de tamanho, hash para dedupe | Segurança básica | — |
| Exportações | **Excel (`.xlsx`) via `openpyxl`** como formato padrão e **CSV via stdlib `csv`** como opção (UTF-8 com BOM e `;`); texto formatado via template Jinja2 | Atende `D-006` e `D-030`. `openpyxl` é a única dependência extra, adotada porque o uso diário é em Excel | Só CSV (rejeitado em `D-030`) |
| CLI | **Typer** (`wedding create-user`, `wedding seed`, `wedding export-openapi`) | Operações administrativas sem endpoint público | — |
| Logs | `logging` padrão com formatação JSON em produção | Suficiente agora | structlog (futuro) |

### 3.1 Organização do código — **SUBSTITUÍDA por [`architecture.md`](./architecture.md) §4 (`D-022`)**

> O bloco abaixo é o desenho anterior (modular pragmático) e permanece apenas como histórico. Vale a Clean Architecture de `architecture.md`.

```
apps/api/src/wedding/
├─ core/            config, db (engine/session), security, money, storage, errors
├─ modules/
│  ├─ identity/     usuários, sessões, perfil (Noivo/Noiva)
│  ├─ wedding/      WeddingBaseline + ScopeCategory + avaliações de escopo
│  ├─ guests/       GuestHousehold, Guest, contadores
│  ├─ schedule/     Milestone/ScheduleTask + motor de dependências
│  ├─ budget/       BudgetScenario, BudgetCategoryLine, simulador
│  ├─ possibilities/ macro + propostas + custo comparável + avaliações + DecisionRecord
│  ├─ vendors/      Contact/Vendor, InteractionLog, NextStep
│  ├─ contracts/    Contract, PaymentInstallment
│  ├─ trousseau/    TrousseauGiftItem + exportações
│  ├─ dossier/      read-model do Dossiê do Dia D
│  └─ files/        metadados de anexos
└─ main.py, cli.py
```

Cada módulo segue: `models.py` (SQLAlchemy) · `schemas.py` (Pydantic) · `rules.py` (**funções puras** de domínio, 100% testáveis sem banco) · `service.py` (casos de uso + transação) · `router.py` (HTTP).

**Efeitos em cadeia:** valores como `Contratado` e `Realizado` passam a ser **derivados na leitura**; o que não pode ser derivado usa **eventos de domínio síncronos em processo** (`architecture.md` §5 e §6).

---

## 4. Convenções de Dados e Portabilidade SQLite → PostgreSQL

Como o SQLite foi a escolha (`D-020`), estas regras são **obrigatórias desde a primeira migração** para a troca futura ser mecânica:

1. **Dinheiro = inteiro em centavos** (`BIGINT`), nunca `float`. Helper `Money` em `core/money.py`; formatação `R$` apenas na borda (frontend). Cálculos *per capita* usam arredondamento definido e testado.
2. **Enums** como `VARCHAR` + `CHECK` (`native_enum=False`), nunca enum nativo do banco.
3. **`PRAGMA foreign_keys=ON`**, `journal_mode=WAL` e `busy_timeout` configurados na conexão SQLite.
4. **Timestamps em UTC** com `TypeDecorator` que preserva tz (SQLite descarta fuso); datas de vencimento e prazos como `DATE`; exibição em `America/Sao_Paulo`.
5. **IDs UUID** (v7 quando disponível na versão do Python/biblioteca; senão v4) — evita colisões ao migrar e não expõe contagem sequencial.
6. **Convenção de nomes de constraints** no `MetaData` (necessária para Alembic em batch mode).
7. **Sem SQL cru específico de SQLite**; JSON via tipo `JSON` do SQLAlchemy e sem consultas profundas dentro do JSON.
8. **Portão antes da nuvem:** a suíte de testes precisa passar também contra **PostgreSQL** (container efêmero) antes do primeiro deploy. Esse é o custo real de ter adiado o Postgres, e ele fica explícito no roadmap.
9. **Migração dos dados reais:** script único (SQLAlchemy lê SQLite → escreve Postgres) validado com contagem de linhas e somatório financeiro por tabela.

---

## 5. Frontend (`apps/web`)

| Camada | Escolha proposta | Por quê | Alternativa considerada |
| :--- | :--- | :--- | :--- |
| Linguagem | **TypeScript** `strict` | Contrato tipado com a API | — |
| Build / dev | **Vite** + **React 19** | SPA estática, HMR rápido | Next.js (rejeitado em `D-020`) |
| Gerenciador de pacotes | **pnpm** | Rápido e determinístico | npm |
| Roteamento | **TanStack Router** (rotas tipadas, search params tipados) | Filtros por perfil/categoria/cenário viram estado de URL tipado | React Router |
| Dados do servidor | **TanStack Query** | Cache, invalidação após mutações | SWR |
| Contrato da API | **`openapi-typescript` + `openapi-fetch`** (+ `openapi-react-query`) gerados do OpenAPI do FastAPI | Tipos nunca divergem; `make api-types` regenera; CI falha se houver drift | Orval, hey-api, tipos escritos à mão |
| Tabelas | **TanStack Table** | Comparador lado a lado, orçamento 4 colunas, convidados | AG Grid (pesado/licença) |
| Formulários | **React Hook Form** + **Zod** (validação de UX; a regra final é do backend) | Padrão estável | Formik |
| Estilo | **Tailwind CSS v4** com tokens em CSS variables (`@theme`) mapeados de `docs/design/visual-direction.md` | Tokens oficiais viram classes (`bg-canvas`, `text-ink`, `bg-olive`…) | CSS Modules |
| Componentes base | **shadcn/ui** (primitivos **Radix**, código copiado para o repo e re-estilizado ao padrão Editorial) | Acessibilidade pronta e controle total do visual; evita aparência genérica | Mantine/MUI (estilo difícil de dobrar à direção visual) |
| Gavetas / mobile | `vaul` (drawer) + Radix Dialog/Sheet | Painéis laterais no desktop, gavetas no celular (`visual-direction.md` §2) | — |
| Ícones | `lucide-react` | Leve e consistente | — |
| Datas | `date-fns` (locale `pt-BR`) | — | dayjs |
| Formatação monetária | `Intl.NumberFormat('pt-BR')` sobre centavos inteiros | Sem aritmética de float | — |
| Fontes (autohospedadas via Fontsource) | **Newsreader** (serifa), **Plus Jakarta Sans** (interface), **JetBrains Mono** (números, com `tabular-nums`) | Concretiza as referências de `D-015`/`D-016`; **aprovadas em `D-025`** | Instrument Serif / DM Sans / Geist Mono |
| PDFs | Início: visualização nativa (`<object>`/nova aba). Evolução: `react-pdf` (pdf.js) para o painel lateral no desktop e no iOS | Evita dependência pesada antes de ser necessária | — |
| PWA | **`vite-plugin-pwa`** (Workbox): manifesto, instalável, cache do *app shell* | `D-003` | — |
| Lint / format | **Biome** (um único binário para lint + format) + o gate de limites (`apps/web/src/architecture.test.ts`, `D-051`) para limites entre `features` (no lugar do `dependency-cruiser`, que não suporta o Node 25) | Menos configuração | ESLint + Prettier |
| Vitrine do Design System | Rota interna `/design-system` (tokens, tipografia, componentes, estados) | Cumpre o Bloco 0.2 sem o peso do Storybook | Storybook |

**Fronteira explícita do PWA na v1:** instalável e com *app shell* em cache; **sem modo offline de escrita** e sem sincronização offline de dados (não está no escopo aprovado). Se vocês quiserem consulta offline do último estado, isso vira nova decisão.

### 5.1 Onde mora cada cálculo
Simulador de orçamento, contadores de convidados, custo comparável e destravamento de cronograma são calculados **no backend**. O frontend chama endpoints de leitura/simulação com *debounce* ao editar premissas. Para 2 usuários a latência é irrelevante, e ganhamos **uma só implementação** das regras, testada em Python.

---

## 6. Identidade, Perfis e Sessão (consequência da decisão 5)

- Dois usuários criados por CLI, cada um vinculado a um `Profile` (`Noivo` ou `Noiva`). `Ambos` é um valor de responsabilidade/visão, não um login.
- **Autoria** de avaliações, interações, tarefas e comprovantes vem **sempre da sessão**, nunca de um campo enviado pelo cliente.
- **Seletor de lente** (barra superior): `Visão do Casal` · `Minha visão`. Ele altera foco e destaques, **não** a autoria.
- Questões de produto abertas por essa decisão: `OQ-ENG-004`.

---

## 7. Qualidade e Automação

| Item | Escolha proposta |
| :--- | :--- |
| Lint/format Python | **Ruff** (lint + format) |
| Tipos Python | **Pyright** (modo `standard`, endurecer gradualmente) |
| Arquitetura Python | **`import-linter`** com os contratos de `architecture.md` §9 |
| Testes backend | **pytest** + `httpx`/`TestClient`; regras puras testadas sem banco; **Hypothesis** para invariantes numéricas (orçamento, contadores, parcelas); banco de teste SQLite temporário |
| Testes frontend | **Vitest** + Testing Library (componentes e utilitários) |
| E2E | **Playwright** com projeto *desktop* e projeto *mobile* (viewport de celular). Entra com o login (restante do Bloco 0.1). Verificação automatizada com `axe` **adiada** (`D-028`); acessibilidade verificada manualmente + regras do Biome |
| Hooks locais | `pre-commit` (ruff, pyright, biome); **adiado até o `apps/api`** (`D-043`) |
| CI (quando houver remoto) | Pipeline com: lint, tipos, testes, build do web, **checagem de drift dos tipos OpenAPI** e, antes do deploy, testes contra PostgreSQL |
| Comandos | **Makefile** na raiz: `make dev`, `make test`, `make lint`, `make api-types`, `make migrate` |

---

## 8. Estrutura do Repositório

```
wedding-planner/
├─ apps/
│  ├─ api/     (Python — ver §3.1)
│  └─ web/     (React — src/app, routes, features/<modulo>, components/ui, lib, styles)
├─ data/       (gitignored: SQLite e uploads em desenvolvimento)
├─ docs/
├─ Makefile
├─ AGENTS.md · CLAUDE.md
```

**Desenvolvimento:** `make dev` sobe Uvicorn (`:8000`) e Vite (`:5173`) com *proxy* de `/api` → mesma origem, igual à produção.
**Produção:** imagem Docker multi-stage (build do web em Node → runtime Python que serve `/api` e os estáticos).

---

## 9. Caminho Local → Nuvem (a decidir só quando o Nível 1 estiver utilizável)

Restrição fixa desde já: tudo parametrizado por variáveis de ambiente (`DATABASE_URL`, `STORAGE_BACKEND`, `SECRET_KEY`, `ALLOWED_HOSTS`).

Candidatos a avaliar na hora (**não decididos**):
- **Aplicação:** Fly.io · Render · Railway (container único).
- **Postgres gerenciado:** Neon · Supabase (usado apenas como Postgres) · o do próprio provedor.
- **Arquivos:** Cloudflare R2 · Backblaze B2 · Supabase Storage (via API S3).

Supabase Auth e Vercel (de `D-019`) deixam de fazer parte do plano: o login é próprio e o deploy é de um container.

---

## 10. Adiado Conscientemente (cada item vira decisão própria no momento certo)

| Tema | Quando decidir | Candidatos iniciais |
| :--- | :--- | :--- |
| PDF do Dossiê do Dia D | Bloco 4.2 | CSS de impressão (zero dependência) vs. WeasyPrint no backend |
| Jobs agendados (lembretes, parcelas) | Bloco 5.2 | APScheduler in-process → fila (ARQ/Celery) só se necessário |
| Web Push | Bloco 5.2 | `pywebpush` + service worker do PWA |
| WhatsApp (envio de notificações no Bloco 5.2 e canal de entrada do assistente no Bloco 5.3, `D-042`) | Blocos 5.2 e 5.3 | API oficial do WhatsApp Business (exige conta e aprovação; custo a levantar); o *webhook* de entrada exige o app na nuvem |
| Camada de IA (extração, entrevista, revisor) | Bloco 5.1 | Provedor de LLM e biblioteca (saída estruturada com Pydantic); toda mutação via rascunho (`D-008`) |
| Observabilidade / erros | Antes do deploy | Sentry (plano gratuito) |
| Passkeys/WebAuthn | Após deploy | Evolução do login próprio |

---

## 11. O que Muda nos Blocos 0.1 e 0.2 (revisado)

**Bloco 0.1 — Fundação** *(executado em duas partes, `D-028`: primeiro só o item 1 na parte do `apps/web`, com Vite + React + TypeScript, Tailwind v4, Vitest, Biome e `tsc`; os demais itens em outra sessão)*
1. Monorepo `apps/api` + `apps/web`, Makefile, `uv`, `pnpm`, hooks e linters.
2. FastAPI com `core/` (config, DB SQLite com PRAGMAs, `Money`, `FileStorage` local, erros padronizados) + Alembic + primeira migração.
3. Modelo de domínio **inicial mínimo** do Nível 0: `User`, `Session`, `FileAsset` (`Profile` é enum de domínio — `architecture.md` §12), com o *mixin* de histórico básico e módulos `identity` e `files` nas 4 camadas. As demais entidades entram **junto de cada bloco que as usa** (evita modelar 10 objetos no escuro).
4. Login para os dois usuários (CLI de criação), logout, sessão e CSRF.
5. SPA com `openapi-fetch` + geração de tipos, roteamento, guarda de rota autenticada e **seletor de lente**.
6. PWA instalável (manifesto + *app shell*).

**Bloco 0.2 — Design System (enxuto, `D-028`)** — ordem de construção em `docs/design/design-system.md` §13
1. Tokens do **tema claro** gerados do `tokens.json` e mapeados em `@theme`, com nomes semânticos; fontes autohospedadas. Tema escuro adiado até o usuário pedir.
2. Ativos de marca copiados para `public/brand/`.
3. 15 primitivos shadcn/Radix re-estilizados: `Button`, `Input`, `Textarea`, `Select`, `Checkbox`, `Badge`, `Card`, `Dialog`, `Table`, `Tabs`, `Tooltip`, `Toast`, `EmptyState`, `PageHeader`, `Money`. Componentes de domínio e gaveta (`vaul`) nascem no bloco que os usa.
4. Casca de navegação das 8 áreas (as 7 de `D-025` mais o Assistente, `D-050`; desktop: lateral; mobile: barra inferior + "Mais") com seletor de lente, ícone flutuante do assistente e páginas-esqueleto. O "+ Registrar Rápido" entra no Bloco 3.1.
5. Rota `/design-system` **mínima**. Testes com Vitest + Testing Library; sem *snapshots* visuais e sem `axe` no CI.

**Critério de conclusão do Nível 0:** abrir no computador e no celular, entrar com o próprio login, alternar a lente e navegar pela estrutura visual pronta.

---

## 12. Riscos e *Trade-offs* Aceitos

| Risco / custo | Origem | Mitigação |
| :--- | :--- | :--- |
| Migrar SQLite → Postgres pode revelar diferenças tardias | `D-020` item 3 | Regras de §4 desde a 1ª migração + portão de testes em Postgres antes do deploy |
| Dois ecossistemas (Python + Node) | Itens 1 e 2 | Contrato único via OpenAPI gerado; `make` unifica comandos |
| Autenticação própria exige cuidado | Item 5 | Escopo mínimo (2 contas, sem cadastro público), `argon2`, sessões server-side, CSRF, testes dedicados |
| Cálculo só no servidor exige chamadas ao editar o simulador | §5.1 | *Debounce*; volume irrelevante para 2 usuários |
| Sem offline de escrita no celular | §5 | Fora do escopo aprovado; reavaliar se a rotina real pedir |
