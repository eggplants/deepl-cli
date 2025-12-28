#!/usr/bin/env bash

set -exo pipefail

if ! grep -q mise ~/.zshrc; then
  # shellcheck disable=SC2016
  echo 'eval "$(mise activate zsh)"' >> ~/.zshrc
fi

mise trust
mise install
mise generate git-pre-commit --write
eval "$(mise activate zsh)"

cat<<'A'>> ~/.zshrc
eval "$(uv generate-shell-completion zsh)"
eval "$(uvx --generate-shell-completion zsh)"
A

sed -i ~/.zshrc -e 's/^ZSH_THEME=.*/ZSH_THEME="refined"/'
