from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_repo_has_readme():
    assert (REPO_ROOT / "README.md").exists()


def test_repo_has_gitignore():
    assert (REPO_ROOT / ".gitignore").exists()


def test_demo_repo_not_tracked():
    import subprocess
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=REPO_ROOT,
        capture_output=True, text=True, check=True
    ).stdout
    assert "demo_repo" not in tracked, "demo_repo está trackeado"


def test_cli_imports():
    from gitignore_tool.cli import main
    assert callable(main)
