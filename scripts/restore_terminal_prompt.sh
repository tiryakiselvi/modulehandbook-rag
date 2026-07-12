#!/usr/bin/env bash
set -euo pipefail

BASHRC="$HOME/.bashrc"
[[ -f "$BASHRC" ]] || exit 0

python - "$BASHRC" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8", errors="ignore")
blocks = [
    ('# >>> modulehandbook pretty prompt >>>', '# <<< modulehandbook pretty prompt <<<'),
    ('# >>> modulehandbook starship >>>', '# <<< modulehandbook starship <<<'),
]
for start, end in blocks:
    while start in text and end in text:
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        text = before.rstrip() + "\n" + after.lstrip("\n")
path.write_text(text.rstrip() + "\n", encoding="utf-8")
PY

echo 'Die von diesem Projekt ergänzten Prompt-Blöcke wurden entfernt.'
echo 'Jetzt ausführen: source ~/.bashrc'
