import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("readme_drift", ROOT / ".github" / "scripts" / "readme_drift.py")
readme_drift = importlib.util.module_from_spec(spec)
spec.loader.exec_module(readme_drift)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("guide", encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "run.py").write_text("", encoding="utf-8")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("", encoding="utf-8")
    return tmp_path


def _check(repo: Path, text: str) -> list[str]:
    readme = repo / "README.md"
    readme.write_text(text, encoding="utf-8")
    return readme_drift.check_readme(readme)


def test_valid_readme_has_no_errors(repo):
    text = (
        "[guide](docs/guide.md) [anchor](#usage) [site](https://example.com) [mail](mailto:a@b.c)\n"
        "[guide section](docs/guide.md#part)\n"
        "![ci](https://github.com/o/r/actions/workflows/ci.yml/badge.svg)\n"
        "    python scripts/run.py\n"
        "    python -m pytest\n"
    )
    assert _check(repo, text) == []


def test_broken_local_link_is_reported(repo):
    errors = _check(repo, "[missing](docs/nope.md)\n")
    assert len(errors) == 1 and "broken local link -> docs/nope.md" in errors[0]


def test_missing_command_path_is_reported(repo):
    errors = _check(repo, "    $ python scripts/gone.py --flag\n")
    assert len(errors) == 1 and "command references missing path -> scripts/gone.py" in errors[0]


def test_direct_executable_reference_is_checked(repo):
    assert any("missing path -> ./build.sh" in e for e in _check(repo, "./build.sh\n"))


def test_badge_for_missing_workflow_is_reported(repo):
    errors = _check(repo, "![x](https://github.com/o/r/actions/workflows/deleted.yml/badge.svg)\n")
    assert errors == [f"{repo / 'README.md'}: workflow badge references missing workflow -> deleted.yml"]


def test_main_exit_codes(repo, capsys):
    (repo / "README.md").write_text("[ok](docs/guide.md)\n", encoding="utf-8")
    assert readme_drift.main() == 0
    (repo / "README.md").write_text("[bad](docs/missing.md)\n", encoding="utf-8")
    assert readme_drift.main() == 1
    assert "README DRIFT DETECTED" in capsys.readouterr().out


def test_this_repository_readme_has_no_drift(monkeypatch):
    monkeypatch.chdir(ROOT)
    assert readme_drift.check_readme(ROOT / "README.md") == []
