# Ponto de entrada das tarefas (stack.md §7). Só orquestra: a lógica mora nos scripts do pnpm.
.PHONY: dev build lint typecheck test

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
