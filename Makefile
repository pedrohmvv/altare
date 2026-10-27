# Ponto de entrada das tarefas (stack.md §7). Só orquestra: a lógica mora nos scripts do pnpm e do uv.
.PHONY: dev dev-api dev-web build \
	lint lint-api lint-web typecheck typecheck-api typecheck-web test test-api test-web \
	migrate api-types tokens brand cursor-rules

API := apps/api
DATABASE_URL ?= sqlite:///$(CURDIR)/data/altare.db
export DATABASE_URL

dev:
	$(MAKE) -j2 dev-api dev-web

dev-api:
	cd $(API) && SESSION_COOKIE_SECURE=false uv run uvicorn wedding.main:app --reload --host 127.0.0.1 --port 8000

dev-web:
	pnpm dev

build:
	pnpm build

lint: lint-api lint-web

lint-api:
	cd $(API) && uv run ruff check . && uv run ruff format --check . && uv run lint-imports

lint-web:
	pnpm lint

typecheck: typecheck-api typecheck-web

typecheck-api:
	cd $(API) && uv run pyright

typecheck-web:
	pnpm typecheck

test: test-api test-web

test-api:
	cd $(API) && uv run pytest

test-web:
	pnpm test

migrate:
	cd $(API) && uv run alembic upgrade head

api-types:
	cd $(API) && uv run wedding export-openapi
	pnpm --filter @altare/api-types generate

tokens:
	pnpm --filter @altare/web tokens:build

brand:
	pnpm --filter @altare/web brand:build

cursor-rules:
	pnpm cursor:rules
