#!/usr/bin/env bash
set -euo pipefail

BASHRC="$HOME/.bashrc"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$HOME/.bashrc.modulehandbook-backup-$STAMP"
START='# >>> modulehandbook pretty prompt >>>'
END='# <<< modulehandbook pretty prompt <<<'

mkdir -p "$HOME"
touch "$BASHRC"
cp "$BASHRC" "$BACKUP"

python - "$BASHRC" "$START" "$END" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
start = sys.argv[2]
end = sys.argv[3]
text = path.read_text(encoding="utf-8", errors="ignore")
while start in text and end in text:
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    text = before.rstrip() + "\n" + after.lstrip("\n")
path.write_text(text.rstrip() + "\n", encoding="utf-8")
PY

cat >> "$BASHRC" <<'BASHRC'

# >>> modulehandbook pretty prompt >>>
parse_git_branch() {
  git branch --show-current 2>/dev/null
}

modulehandbook_prompt() {
  local exit_code=$?
  local branch
  local venv
  branch="$(parse_git_branch)"
  venv=""
  if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    venv="$(basename "$VIRTUAL_ENV") "
  fi

  local status_color='\[\e[38;5;78m\]'
  if [[ $exit_code -ne 0 ]]; then
    status_color='\[\e[38;5;203m\]'
  fi

  PS1="${status_color}● \[\e[38;5;111m\]${venv}\[\e[38;5;147m\]\u \[\e[38;5;39m\]\W"
  if [[ -n "$branch" ]]; then
    PS1+=" \[\e[38;5;244m\](\[\e[38;5;177m\]$branch\[\e[38;5;244m\])"
  fi
  PS1+="\[\e[0m\]\n❯ "
}
PROMPT_COMMAND=modulehandbook_prompt

alias ll='ls -lah --color=auto'
alias gs='git status -sb'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline --decorate --graph -12'
alias act='source .venv/Scripts/activate'
# <<< modulehandbook pretty prompt <<<
BASHRC

printf 'Pretty prompt wurde eingerichtet.\n'
printf 'Backup: %s\n' "$BACKUP"
printf 'Jetzt ausführen: source ~/.bashrc\n'
