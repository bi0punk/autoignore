#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v gitignore-tool >/dev/null 2>&1; then
  echo "[INFO] gitignore-tool no está instalado aún. Instalando en editable..."
  python3 -m pip install -e .
fi

rm -f demo_repo/.gitignore

echo "[INFO] Ejecutando demo interactiva automatizada"
echo "[INFO] Flujo: seleccionar logs/ -> ignorar -> no verificar -> imprimir .gitignore -> salir"

printf '3\ni\nn\np\nq\n' | gitignore-tool browse --repo ./demo_repo
