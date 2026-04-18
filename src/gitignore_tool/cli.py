#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

IGNORE_ALWAYS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
COMMENT_HEADER = "# Archivo generado/actualizado por gitignore-tool"


@dataclass
class RepoContext:
    repo_root: Path
    gitignore_path: Path


def print_header(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def log_info(message: str) -> None:
    print(f"[INFO] {message}")


def log_ok(message: str) -> None:
    print(f"[OK] {message}")


def log_warn(message: str) -> None:
    print(f"[WARN] {message}")


def log_error(message: str) -> None:
    print(f"[ERROR] {message}")


def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def find_git_root(start: Path) -> Optional[Path]:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if is_git_repo(candidate):
            return candidate
    return None


def resolve_repo(repo_arg: Optional[str]) -> RepoContext:
    start_path = Path(repo_arg).expanduser().resolve() if repo_arg else Path.cwd()
    repo_root = find_git_root(start_path)
    if repo_root is None:
        raise SystemExit(
            "[ERROR] No se encontró un repositorio Git desde la ruta indicada. "
            "Usa --repo /ruta/al/repo o entra a un repo válido."
        )
    return RepoContext(repo_root=repo_root, gitignore_path=repo_root / ".gitignore")


def ensure_gitignore_exists(path: Path) -> None:
    if not path.exists():
        path.write_text(COMMENT_HEADER + "\n", encoding="utf-8")


def read_gitignore_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def normalized_existing_patterns(lines: Iterable[str]) -> set[str]:
    items: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        items.add(stripped)
    return items


def list_entries(path: Path) -> List[Path]:
    entries: List[Path] = []
    try:
        for entry in path.iterdir():
            if entry.name in IGNORE_ALWAYS:
                continue
            entries.append(entry)
    except PermissionError:
        log_warn(f"Sin permisos para leer: {path}")
        return []
    entries.sort(key=lambda p: (not p.is_dir(), p.name.lower()))
    return entries


def to_gitignore_pattern(repo_root: Path, target: Path) -> str:
    target = target.resolve()
    rel = target.relative_to(repo_root.resolve())
    rel_str = rel.as_posix()
    if target.is_dir() and not rel_str.endswith("/"):
        rel_str += "/"
    return rel_str


def append_pattern_to_gitignore(gitignore_path: Path, pattern: str) -> bool:
    ensure_gitignore_exists(gitignore_path)
    lines = read_gitignore_lines(gitignore_path)
    existing = normalized_existing_patterns(lines)
    if pattern in existing:
        return False
    with gitignore_path.open("a", encoding="utf-8") as handler:
        if lines and lines[-1].strip() != "":
            handler.write("\n")
        handler.write(pattern + "\n")
    return True


def remove_pattern_from_gitignore(gitignore_path: Path, pattern: str) -> bool:
    if not gitignore_path.exists():
        return False
    lines = read_gitignore_lines(gitignore_path)
    new_lines: List[str] = []
    removed = False
    for line in lines:
        if line.strip() == pattern:
            removed = True
            continue
        new_lines.append(line)
    if removed:
        gitignore_path.write_text("\n".join(new_lines).rstrip() + "\n", encoding="utf-8")
    return removed


def is_git_available() -> bool:
    try:
        subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False


def git_check_ignore(repo_root: Path, rel_path: str) -> tuple[bool, str]:
    if not is_git_available():
        return False, "Git no está disponible en PATH"
    result = subprocess.run(
        ["git", "-C", str(repo_root), "check-ignore", "-v", rel_path],
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout or result.stderr or "").strip()
    return result.returncode == 0, output


def git_is_tracked(repo_root: Path, rel_path: str) -> bool:
    if not is_git_available():
        return False
    result = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "--error-unmatch", rel_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def print_gitignore_contents(gitignore_path: Path) -> None:
    lines = read_gitignore_lines(gitignore_path)
    print_header(f"Contenido de {gitignore_path}")
    if not lines:
        print("(vacío o no existe)")
        return
    for idx, line in enumerate(lines, start=1):
        print(f"{idx:>3}: {line}")


def verify_target(repo_root: Path, target: Path) -> None:
    rel = target.resolve().relative_to(repo_root.resolve()).as_posix()
    ignored, output = git_check_ignore(repo_root, rel)
    tracked = git_is_tracked(repo_root, rel)

    if ignored:
        log_ok(f"Git confirma que la ruta está siendo ignorada: {rel}")
        if output:
            print(output)
    else:
        log_warn(f"Git no confirmó ignore para: {rel}")
        if output:
            print(output)

    if tracked:
        log_warn("La ruta ya estaba trackeada por Git. El .gitignore no la sacará del índice.")
        print(f'       Ejecuta: git -C "{repo_root}" rm --cached "{rel}"')


def path_inside_repo(repo_root: Path, raw_path: str) -> Path:
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    candidate = candidate.resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise SystemExit(f"[ERROR] La ruta está fuera del repositorio: {candidate}") from exc
    return candidate


def prompt_choice(prompt: str, valid: set[str]) -> str:
    while True:
        value = input(prompt).strip().lower()
        if value in valid:
            return value
        log_error(f"Opción inválida. Válidas: {', '.join(sorted(valid))}")


def render_entries(current_path: Path, entries: List[Path], repo_root: Path) -> None:
    print_header(f"Navegando: {current_path}")
    print(f"Repo root: {repo_root}\n")
    print("Entradas disponibles:\n")
    if not entries:
        print("  (directorio vacío o sin permisos)")
    for idx, entry in enumerate(entries, start=1):
        rel = entry.relative_to(repo_root)
        kind = "[DIR]" if entry.is_dir() else "[FILE]"
        print(f"  {idx:>3}. {kind:<6} {rel}")
    print("\nComandos:")
    print("  número        -> seleccionar entrada")
    print("  cd <n>        -> entrar a directorio")
    print("  up            -> subir un nivel")
    print("  ls            -> refrescar")
    print("  p             -> imprimir .gitignore")
    print("  q             -> salir")


def interactive_browser(ctx: RepoContext) -> None:
    current_path = ctx.repo_root
    while True:
        entries = list_entries(current_path)
        render_entries(current_path, entries, ctx.repo_root)
        raw = input("\n> ").strip()

        if raw.lower() == "q":
            log_info("Saliendo.")
            return
        if raw.lower() == "ls":
            continue
        if raw.lower() == "p":
            print_gitignore_contents(ctx.gitignore_path)
            continue
        if raw.lower() == "up":
            if current_path == ctx.repo_root:
                log_info("Ya estás en la raíz del repositorio.")
            else:
                current_path = current_path.parent
            continue
        if raw.lower().startswith("cd "):
            parts = raw.split(maxsplit=1)
            if len(parts) != 2 or not parts[1].isdigit():
                log_error("Uso correcto: cd <n>")
                continue
            idx = int(parts[1]) - 1
            if idx < 0 or idx >= len(entries):
                log_error("Índice fuera de rango.")
                continue
            selected = entries[idx]
            if not selected.is_dir():
                log_error("Esa entrada no es un directorio.")
                continue
            current_path = selected
            continue
        if raw.isdigit():
            idx = int(raw) - 1
            if idx < 0 or idx >= len(entries):
                log_error("Índice fuera de rango.")
                continue
            selected = entries[idx]
            if selected.is_dir():
                print(f"\nHas seleccionado el directorio: {selected.relative_to(ctx.repo_root)}")
                action = prompt_choice("¿Qué deseas hacer? [i]gnorar / [e]ntrar / [c]ancelar: ", {"i", "e", "c"})
                if action == "e":
                    current_path = selected
                    continue
                if action == "c":
                    continue
            pattern = to_gitignore_pattern(ctx.repo_root, selected)
            added = append_pattern_to_gitignore(ctx.gitignore_path, pattern)
            if added:
                log_ok(f"Patrón agregado a .gitignore: {pattern}")
            else:
                log_info(f"El patrón ya existía en .gitignore: {pattern}")
            verify = prompt_choice("¿Verificar con git check-ignore? [s/n]: ", {"s", "n"})
            if verify == "s":
                verify_target(ctx.repo_root, selected)
            continue
        log_error("Comando no reconocido.")


def cmd_browse(args: argparse.Namespace) -> int:
    ctx = resolve_repo(args.repo)
    print_header("gitignore-tool | modo interactivo")
    log_info(f"Repositorio detectado: {ctx.repo_root}")
    if ctx.gitignore_path.exists():
        log_info(f"Usando .gitignore existente: {ctx.gitignore_path}")
    else:
        log_info(f"Se creará .gitignore en: {ctx.gitignore_path}")
    interactive_browser(ctx)
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    ctx = resolve_repo(args.repo)
    target = path_inside_repo(ctx.repo_root, args.path)
    if not target.exists():
        raise SystemExit(f"[ERROR] La ruta no existe dentro del repo: {target}")
    pattern = to_gitignore_pattern(ctx.repo_root, target)
    added = append_pattern_to_gitignore(ctx.gitignore_path, pattern)
    if added:
        log_ok(f"Patrón agregado: {pattern}")
    else:
        log_info(f"El patrón ya existía: {pattern}")
    if args.verify:
        verify_target(ctx.repo_root, target)
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    ctx = resolve_repo(args.repo)
    removed = remove_pattern_from_gitignore(ctx.gitignore_path, args.pattern)
    if removed:
        log_ok(f"Patrón eliminado: {args.pattern}")
    else:
        log_warn(f"No se encontró el patrón exacto en .gitignore: {args.pattern}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    ctx = resolve_repo(args.repo)
    print_gitignore_contents(ctx.gitignore_path)
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    ctx = resolve_repo(args.repo)
    target = path_inside_repo(ctx.repo_root, args.path)
    if not target.exists():
        raise SystemExit(f"[ERROR] La ruta no existe dentro del repo: {target}")
    print_header("gitignore-tool | doctor")
    print(f"Ruta analizada: {target}\n")
    verify_target(ctx.repo_root, target)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gitignore-tool",
        description="CLI interactiva y no interactiva para gestionar .gitignore",
    )
    subparsers = parser.add_subparsers(dest="command")

    browse = subparsers.add_parser("browse", help="Navegación interactiva")
    browse.add_argument("--repo", type=str, default=None, help="Ruta al repositorio Git")
    browse.set_defaults(func=cmd_browse)

    add = subparsers.add_parser("add", help="Agregar una ruta al .gitignore")
    add.add_argument("path", type=str, help="Ruta de archivo o directorio relativa al repo")
    add.add_argument("--repo", type=str, default=None, help="Ruta al repositorio Git")
    add.add_argument("--verify", action="store_true", help="Verifica la ruta con git check-ignore")
    add.set_defaults(func=cmd_add)

    remove = subparsers.add_parser("remove", help="Eliminar un patrón exacto del .gitignore")
    remove.add_argument("pattern", type=str, help="Patrón exacto a eliminar")
    remove.add_argument("--repo", type=str, default=None, help="Ruta al repositorio Git")
    remove.set_defaults(func=cmd_remove)

    list_cmd = subparsers.add_parser("list", help="Mostrar contenido del .gitignore")
    list_cmd.add_argument("--repo", type=str, default=None, help="Ruta al repositorio Git")
    list_cmd.set_defaults(func=cmd_list)

    doctor = subparsers.add_parser("doctor", help="Verificar si una ruta está siendo ignorada")
    doctor.add_argument("path", type=str, help="Ruta de archivo o directorio relativa al repo")
    doctor.add_argument("--repo", type=str, default=None, help="Ruta al repositorio Git")
    doctor.set_defaults(func=cmd_doctor)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        args = parser.parse_args(["browse"])

    try:
        exit_code = args.func(args)
    except KeyboardInterrupt:
        print("\n[INFO] Interrumpido por el usuario.")
        raise SystemExit(130)
    except BrokenPipeError:
        raise SystemExit(1)

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
