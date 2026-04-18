#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m pip install -e .

echo "[OK] gitignore-tool instalado en modo editable"
echo "[INFO] Prueba rápida: gitignore-tool list --repo ./demo_repo"
