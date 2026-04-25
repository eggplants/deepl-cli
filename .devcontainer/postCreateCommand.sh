#!/usr/bin/env zsh

set -exo pipefail

mise trust
mise install
mise generate git-pre-commit --write
eval "$(mise activate zsh)"

cat<<'A'>> ~/.zshrc
eval "$(mise activate zsh)"

eval "$(mise completion zsh)"
eval "$(uv generate-shell-completion zsh)"
eval "$(uvx --generate-shell-completion zsh)"

autoload -U compinit
compinit -i
A

sed -i ~/.zshrc -e 's/^ZSH_THEME=.*/ZSH_THEME="refined"/'
