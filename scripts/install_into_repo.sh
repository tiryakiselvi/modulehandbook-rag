#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Verwendung: bash scripts/install_into_repo.sh /pfad/zum/modulehandbook-rag"
  exit 1
fi

SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$1"

if [[ ! -d "$TARGET" ]]; then
  echo "Zielordner existiert nicht: $TARGET"
  exit 1
fi

cp -R "$SOURCE_ROOT"/. "$TARGET"/
echo "Dateien wurden nach $TARGET kopiert."
echo "Wechsle jetzt in den Zielordner und prüfe git status."
