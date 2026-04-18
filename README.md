# gitignore-tool

CLI instalable para crear, modificar y auditar `.gitignore` desde terminal.

## Qué incluye

- Navegación interactiva por archivos y directorios
- Alta de patrones en `.gitignore`
- Remoción de patrones
- Listado del contenido actual de `.gitignore`
- Verificación con `git check-ignore`
- Repo demo listo para probar
- Scripts de instalación y prueba

## Requisitos

- Linux recomendado
- Python 3.10+
- Git disponible en PATH

## Instalación rápida

```bash
cd gitignore_tool_fullzip
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
