#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v gitignore-tool >/dev/null 2>&1; then
  echo "[INFO] gitignore-tool no está instalado aún. Instalando en editable..."
  python3 -m pip install -e .
fi

rm -f demo_repo/.gitignore

echo
echo "========== 1) Estado inicial =========="
gitignore-tool list --repo ./demo_repo

echo
echo "========== 2) Agregar .env =========="
gitignore-tool add .env --repo ./demo_repo --verify

echo
echo "========== 3) Agregar logs/ =========="
gitignore-tool add logs --repo ./demo_repo --verify

echo
echo "========== 4) Mostrar .gitignore =========="
gitignore-tool list --repo ./demo_repo

echo
echo "========== 5) Doctor sobre logs/app.log =========="
gitignore-tool doctor logs/app.log --repo ./demo_repo

echo
echo "========== 6) Eliminar logs/ =========="
gitignore-tool remove logs/ --repo ./demo_repo

echo
echo "========== 7) Estado final =========="
gitignore-tool list --repo ./demo_repo

echo
echo "[OK] Demo automática completada"
echo "[INFO] Para probar modo interactivo manual: gitignore-tool browse --repo ./demo_repo"
