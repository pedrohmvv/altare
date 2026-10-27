---
name: altare-devops
description: >-
  CI/CD, ambientes, deploy e custos do Altare: pipeline de gates, variáveis de ambiente, Docker,
  migração SQLite para PostgreSQL, backup. Use ao criar ou alterar CI, Dockerfile, variáveis de
  ambiente, deploy, hospedagem ou backup, ou ao estimar custo de infraestrutura.
---

# DevOps

O Altare é um app de duas pessoas e um casamento. A infraestrutura boa aqui é a mais simples que mantém os dados do casal seguros e o app no ar: **um container**, um banco, um bucket, sem filas, sem autoscaling e sem microsserviços (`stack.md` §2, princípio 5).

## Docs a consultar

- `docs/engineering/stack.md` §2 (visão e princípios), §4 (portabilidade e migração), §7 (CI), §8 (desenvolvimento e produção), §9 (caminho local para nuvem), §10 (adiado) e §12 (riscos).
- `docs/engineering/architecture.md` §9 (portão de portabilidade).
- `docs/product/decisions.md` D-020 (hospedagem local nos Níveis 0 e 1), D-038 item 4 (backup) e D-042 (WhatsApp exige nuvem).

## Princípios

1. **Tudo parametrizado por ambiente.** Nada no código assume SQLite nem disco local: `DATABASE_URL`, `STORAGE_BACKEND`, `SECRET_KEY`, `ALLOWED_HOSTS`. Trocar de ambiente é trocar variável, não código.
2. **Uma unidade de deploy, uma origem.** Em produção o FastAPI serve a API e a SPA buildada na **mesma origem**, o que dispensa CORS e simplifica o cookie de sessão.
3. **Segredo nunca no repositório.** `.env` e `.env.*` estão no `.gitignore` (exceto `.env.example`, que lista só os nomes). Valores vivem no provedor ou no cofre local.
4. **O CI é o gate.** O pipeline roda os gates definidos em `altare-testes-qa` e o merge só acontece com ele verde. Não crie gate novo aqui; proponha na skill dona.
5. **Local primeiro, nuvem quando o Nível 1 estiver utilizável** (D-020). Não contrate infraestrutura antes de haver o que hospedar.
6. **Backup não é funcionalidade do produto** (D-038, item 4): é requisito de implantação, tratado junto da hospedagem. A exportação de dados do casal (`F-CCD-10`) ajuda, mas **não substitui** backup do banco e dos arquivos.

## Pipeline de CI

O pipeline roda, nesta ordem lógica, com *path filters* conforme `altare-monorepo`:

1. API: Ruff, Pyright, `import-linter`, pytest (SQLite temporário).
2. Web: Biome, `tsc`, Vitest (inclui o gate de limites, `D-051`), build.
3. Contrato: regenerar tipos do OpenAPI e falhar se houver diff.
4. Antes do deploy: suíte de integração contra **PostgreSQL** em contêiner efêmero.
5. E2E com Playwright (desktop e mobile), quando o login existir.

O CI só vale com remoto configurado; o remoto existe (`github.com/pedrohmvv/altare`). O provedor é o GitHub Actions, e o workflow está em `.github/workflows/ci.yml` (`D-059`, `D-060`): jobs `changes`, `api`, `web` e o agregador `CI`, o único check a exigir na proteção das branches.

## Ambientes

| Ambiente | Banco | Arquivos | Notas |
| :--- | :--- | :--- | :--- |
| Desenvolvimento | SQLite em `data/` | disco local (`LocalFileStorage`) | `make dev` sobe Uvicorn (`:8000`) e Vite (`:5173`) com proxy de `/api` |
| Teste | SQLite temporário; Postgres efêmero no portão | temporário | Dados fictícios |
| Produção | PostgreSQL gerenciado | S3-compatível (`S3FileStorage`) | Cookie `Secure` ligado |

`data/` precisa estar no `.gitignore` (SQLite e uploads de desenvolvimento, `stack.md` §8).

## Docker e deploy

- **Imagem multi-stage:** estágio Node builda o `apps/web`; estágio final em Python serve `/api` e os estáticos. Sem Node no runtime.
- Rodar como usuário sem privilégio, sem segredo embutido na imagem, com `ALLOWED_HOSTS` explícito.
- Migrations Alembic rodam como passo do deploy **antes** de subir a nova versão, e uma migration que falha aborta o deploy.

## Migração SQLite para PostgreSQL

Script único (SQLAlchemy lê um e escreve no outro), executado só depois do portão em Postgres verde. A validação é **contagem de linhas e somatório financeiro por tabela** (`stack.md` §4, item 9): conferir só a contagem não pega valor trocado. Faça um ensaio em cópia antes de migrar os dados reais e guarde o SQLite original até o casal confirmar o app em produção.

## Custos

- Prefira planos gratuitos ou mínimos e **um** serviço de aplicação. Revise o custo mensal a cada mudança de infraestrutura e registre o provedor escolhido como `D-xxx` (`altare-docs-vivas`).
- Custo de LLM nasce no Nível 5 e é medido por `AgentRun` (`altare-engenharia-de-ia`). O WhatsApp pode ter custo próprio (`OQ-IA-001`).

## Checklist

- [ ] Nenhuma configuração de ambiente está fixa no código?
- [ ] Nenhum segredo no repositório, na imagem ou no log?
- [ ] O CI executa todos os gates de `altare-testes-qa` e bloqueia o merge?
- [ ] Antes do primeiro deploy: suíte em Postgres verde e ensaio de migração validado por contagem e somatório?
- [ ] Há backup do banco e dos arquivos, com restauração testada?

## Limites e vizinhas

- Quais gates existem e o que testar: `altare-testes-qa`.
- Estrutura do repo, Makefile, *path filters* e drift do OpenAPI: `altare-monorepo`.
- Auth, sessão, cookies, segredos e LGPD: `altare-seguranca-privacidade`.
- Tabelas e migrations em si: `altare-banco-de-dados`.

## Em aberto

- **Provedor de aplicação** (Fly.io, Render ou Railway), **Postgres gerenciado** (Neon, Supabase só como Postgres, ou o do provedor) e **storage S3-compatível** (Cloudflare R2, Backblaze B2 ou Supabase Storage): não decididos (`stack.md` §9). Decidir quando o Nível 1 estiver utilizável.
- **Observabilidade de erros (Sentry, plano gratuito)** antes do deploy; **jobs agendados**, **Web Push** e **WhatsApp** (`stack.md` §10).
- **Estratégia de backup e retenção:** depende da hospedagem (D-038).
