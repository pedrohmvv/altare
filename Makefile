# Ponto de entrada das tarefas (stack.md §7). Só orquestra: a lógica mora nos scripts do pnpm.
.PHONY: dev build lint typecheck test tokens brand cursor-rules

dev:
	pnpm dev

build:
	pnpm build

lint:
	pnpm lint

typecheck:
	pnpm typecheck

test:
	pnpm test

tokens:
	pnpm --filter @altare/web tokens:build

brand:
	pnpm --filter @altare/web brand:build

cursor-rules:
	pnpm cursor:rules
