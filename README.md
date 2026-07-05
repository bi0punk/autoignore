# gitignore-tool

[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![CI](https://github.com/drbash/autoignore/actions/workflows/ci.yml/badge.svg)](https://github.com/drbash/autoignore/actions)

CLI interactiva instalable para crear, modificar y auditar archivos `.gitignore` desde la terminal.

## Contenido

- [Características](#caracter%C3%ADsticas)
- [Stack](#stack)
- [Estructura](#estructura)
- [Requisitos](#requisitos)
- [Instalación](#instalaci%C3%B3n)
- [Uso](#uso)
- [Tests](#tests)
- [Configuración](#configuraci%C3%B3n)
- [CI/CD](#cicd)
- [Demo rápida](#demo-r%C3%A1pida)
- [Nota sobre Git](#nota-importante-sobre-git)
- [Flujo recomendado](#flujo-recomendado)
- [Limitaciones / Roadmap](#limitaciones--roadmap)
- [Licencia](#licencia)

## Características

- **Navegación interactiva** por archivos y directorios
- **Alta de patrones** en `.gitignore`
- **Remoción de patrones** exactos
- **Listado** del contenido actual de `.gitignore`
- **Verificación** con `git check-ignore`
- **Modo no interactivo** para scripting
- **Repo demo** listo para probar

## Stack

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.10+ |
| CLI | `argparse` (stdlib) |
| Interacción | `rich` para menús interactivos |
| Testing | pytest |

## Estructura

```
autoignore/
├── src/
│   └── gitignore_tool/
│       ├── __init__.py
│       └── cli.py              # CLI principal
├── scripts/
│   └── demo_run.sh             # Script de demo
├── demo_repo/                  # Repositorio de prueba
├── tests/
├── .env.example
├── .github/workflows/ci.yml
├── pyproject.toml
└── README.md
```

## Requisitos

- Linux recomendado
- Python 3.10+
- Git disponible en PATH

## Instalación

```bash
git clone https://github.com/drbash/autoignore.git
cd autoignore
python3 -m pip install -e .
```

## Uso

### Navegación interactiva

```bash
gitignore-tool browse --repo ./demo_repo
```

### Agregar una ruta directamente

```bash
gitignore-tool add .env --repo ./demo_repo
gitignore-tool add logs/ --repo ./demo_repo
```

### Listar reglas actuales

```bash
gitignore-tool list --repo ./demo_repo
```

### Eliminar una regla exacta

```bash
gitignore-tool remove logs/ --repo ./demo_repo
```

### Verificar una ruta con Git

```bash
gitignore-tool doctor logs/app.log --repo ./demo_repo
```

## Tests

```bash
pip install pytest
pytest tests/ -v
```

## Configuración

Variables de entorno (ver `.env.example`):

| Variable | Default | Descripción |
|---|---|---|
| `GIT_REPO_PATH` | `.` | Ruta al repositorio objetivo |

## CI/CD

GitHub Actions ejecuta lint (Ruff) y tests (pytest) en cada push/PR a main/master.

## Demo rápida

```bash
chmod +x scripts/demo_run.sh
./scripts/demo_run.sh
```

## Nota importante sobre Git

Si un archivo ya estaba trackeado por Git, agregarlo a `.gitignore` no basta. Debes sacarlo del índice:

```bash
git rm --cached ruta/al/archivo
```

## Flujo recomendado

1. Instalar en editable
2. Probar con `demo_repo`
3. Ejecutar sobre un repositorio real
4. Extender plantillas o reglas por stack si lo necesitas

## Limitaciones / Roadmap

- [x] Navegación interactiva + comandos directos
- [x] Verificación con `git check-ignore`
- [ ] Plantillas por lenguaje/stack (Python, Node, etc.)
- [ ] Soporte para `.gitignore` global
- [ ] Autocompletado en shell
- [ ] Generación de `.gitignore` desde cero con wizard

## Licencia

MIT
