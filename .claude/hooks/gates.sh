#!/bin/bash
# Stop do altare-api-dev e do altare-web-dev (o Claude Code o converte em SubagentStop).
# Uso: gates.sh api | web | all (padrão). Exit 2 devolve a saída ao agente e o impede de encerrar.
INPUT=$(cat)
# Uma segunda tentativa só: se o hook já forçou a continuar, não prende o agente num laço.
[ "$(jq -r '.stop_hook_active // false' <<<"$INPUT")" = "true" ] && exit 0

cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}" || exit 0

case "${1:-all}" in
  api) read -ra ALVOS <<<"lint-api typecheck-api test-api" ;;
  web) read -ra ALVOS <<<"lint-web typecheck-web test-web" ;;
  all) read -ra ALVOS <<<"lint typecheck test" ;;
  *) echo "gates.sh: escopo desconhecido '$1' (use api, web ou all)." >&2; exit 1 ;;
esac

# Sem mudança em código, não há o que provar: o agente só devolveu uma pergunta ou um relatório.
[ -z "$(git status --porcelain -- apps tools Makefile)" ] && exit 0

if ! OUT=$(make -k "${ALVOS[@]}" 2>&1); then
  { echo "Gates vermelhos (${ALVOS[*]}). Corrija antes de encerrar. Fim da saída:"; tail -n 40 <<<"$OUT"; } >&2
  exit 2
fi
exit 0
