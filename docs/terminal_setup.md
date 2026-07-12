# Git Bash wieder hübsch machen

## Option 1: ohne zusätzliche Installation

Diese Variante ergänzt einen zweizeiligen farbigen Prompt mit:

- Benutzername
- aktuellem Ordner
- Git-Branch
- aktivem virtuellen Environment
- grünem oder rotem Statuspunkt

```bash
bash scripts/setup_terminal_pretty.sh
source ~/.bashrc
```

Die bestehende `.bashrc` wird vorher automatisch gesichert.

## Option 2: Starship

Starship installieren:

```bash
winget install --id Starship.Starship
```

Danach im Projektordner:

```bash
bash scripts/setup_terminal_starship.sh
source ~/.bashrc
```

Die offizielle Starship-Einrichtung für Bash verwendet ebenfalls:

```bash
eval "$(starship init bash)"
```

## Zurücksetzen

```bash
bash scripts/restore_terminal_prompt.sh
source ~/.bashrc
```

Die Backup-Dateien liegen im Home-Ordner und heißen zum Beispiel:

```text
~/.bashrc.modulehandbook-backup-20260712-123000
~/.bashrc.starship-backup-20260712-123000
```
