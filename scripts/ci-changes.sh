#!/usr/bin/env bash
# Diz quais gates do CI precisam rodar, pelos arquivos que mudaram (altare-monorepo, D-059).
# Uso: scripts/ci-changes.sh <base> <head>   ->   api=true|false e web=true|false
# Sem base utilizável, roda tudo: errar para mais é seguro, errar para menos deixa passar.
set -euo pipefail

base="${1:-}"
head="${2:-HEAD}"

run_all() {
  echo "api=true"
  echo "web=true"
  exit 0
}

if [[ -z "$base" || "$base" =~ ^0+$ ]]; then
  run_all
fi

files="$(git diff --name-only "$base" "$head")" || run_all

api=false
web=false
while IFS= read -r file; do
  case "$file" in
    Makefile | .github/* | pnpm-workspace.yaml | scripts/ci-changes.sh | apps/api/openapi.json)
      api=true
      web=true
      ;;
    apps/api/*)
      api=true
      ;;
    apps/web/* | docs/design/identidade-visual/tokens.json | package.json | pnpm-lock.yaml | biome.json)
      web=true
      ;;
  esac
done <<< "$files"

echo "api=$api"
echo "web=$web"
