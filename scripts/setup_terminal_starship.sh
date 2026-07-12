#!/usr/bin/env bash
set -euo pipefail

if ! command -v starship >/dev/null 2>&1 && ! command -v starship.exe >/dev/null 2>&1; then
  echo 'Starship ist noch nicht installiert.'
  echo 'In PowerShell oder Git Bash ausführen:'
  echo 'winget install --id Starship.Starship'
  exit 1
fi

BASHRC="$HOME/.bashrc"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$HOME/.bashrc.starship-backup-$STAMP"
START='# >>> modulehandbook starship >>>'
END='# <<< modulehandbook starship <<<'
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$HOME/.config"
touch "$BASHRC"
cp "$BASHRC" "$BACKUP"
cp "$SCRIPT_DIR/starship.toml" "$HOME/.config/starship.toml"

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

# >>> modulehandbook starship >>>
eval "$(starship init bash)"
# <<< modulehandbook starship <<<
BASHRC

printf 'Starship wurde für Git Bash eingerichtet.\n'
printf 'Backup: %s\n' "$BACKUP"
printf 'Jetzt ausführen: source ~/.bashrc\n'
