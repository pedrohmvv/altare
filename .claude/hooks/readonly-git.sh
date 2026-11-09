#!/bin/bash
# PreToolUse do altare-reviewer: só passa git de leitura, rg, ls e wc, sem encadear comandos.
CMD=$(jq -r '.tool_input.command // empty')
[ -z "$CMD" ] && exit 0

bloqueia() {
  echo "Bloqueado: o reviewer só roda git de leitura, rg, ls e wc, sem encadear comandos." >&2
  exit 2
}

# Quebra de linha, encadeamento, redirecionamento e substituição de comando.
case "$CMD" in *$'\n'* | *$'\r'*) bloqueia ;; esac
echo "$CMD" | grep -Eq '[;&|><`]|\$\(' && bloqueia
# Flags que escrevem em disco ou executam programa externo.
echo "$CMD" | grep -Eq -- '--output|--pre([= ]|$)|--ext-diff|--textconv' && bloqueia

# `git branch` só em modo de listagem: -D, -m e criação mudam o repositório.
if echo "$CMD" | grep -Eq '^git branch( +(--show-current|-a|-r|--list|-v|-vv))*$'; then exit 0; fi
if echo "$CMD" | grep -Eq '^git (diff|log|show|status|rev-parse|merge-base)( |$)'; then exit 0; fi
if echo "$CMD" | grep -Eq '^(rg|ls|wc)( |$)'; then exit 0; fi

bloqueia
