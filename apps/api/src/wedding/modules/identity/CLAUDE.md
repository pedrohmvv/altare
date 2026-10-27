# Módulo `identity`

> Regras gerais: leia `AGENTS.md` (raiz) e os docs abaixo. Este arquivo só traz o que é específico do módulo.

**Propósito:** é dono do usuário (Noivo e Noiva), da sessão e do login. Não é dono de papéis ou permissões por área: não há RBAC (`D-002`).

## Superfície pública
- `application/public.py`: `ResolveSession` (token da sessão → `Actor`) e `CurrentUser`.
- `domain/events.py`: nenhum evento.

Nada além disso pode ser importado por outro módulo (`architecture.md` §4; contrato 5 de §9).

## Invariantes
- `User.profile` é `Noivo` ou `Noiva`, nunca `Ambos`; um usuário por perfil, e o usuário é único sem diferenciar maiúsculas.
- O token da sessão nunca é guardado: só o SHA-256 dele (`D-059`).
- Senha errada e usuário inexistente dão o mesmo erro e o mesmo trabalho; ninguém descobre quais contas existem.
- Não há cadastro público: só a CLI cria usuário e troca senha.
- A autoria vem sempre do `Actor` montado da sessão, nunca de um campo do pedido.

## Dependências permitidas
- Não importa nenhum outro módulo.
- Camadas: domínio só usa a biblioteca padrão e o `shared_kernel` (`architecture.md` §2 e §9).
- Argon2 e as tabelas ficam em `infrastructure/`; `platform/http` só recebe um resolvedor de sessão injetado pelo `bootstrap`.

## Docs
- Features: sem doc de feature; o login é do Bloco 0.1 (`roadmap.md`).
- Decisões: `D-020`, `D-021`, `D-059`, `D-061`.
- Arquitetura e domínio: `docs/engineering/architecture.md` §10 e §12; `docs/engineering/stack.md` §3 e §6.
- Web: `apps/web/src/features/identity/`.

## Como testar
- `make test-api` e `make lint-api` na raiz.
- Domínio: pytest puro e Hypothesis. Aplicação: fakes das portas. Infraestrutura: SQLite real (`architecture.md` §9).
- Contratos de import: `import-linter` no `make lint-api`.
