import importlib.util
import json
import os
import stat
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GATE_WORKFLOW = ROOT / ".github" / "workflows" / "security-gate.yml"


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


regression = _load("regression", "scripts/regression.py")
challenge = _load("challenge", "scripts/challenge.py")


def _row(expected_pass: bool, exit_code: int) -> dict:
    return {"expected_pass": expected_pass, "exit_code": exit_code, "contract_pass": (exit_code == 0) == expected_pass}


def _fixture_paths(cmd: list[str]) -> list[str]:
    return [arg for arg in cmd if arg.startswith("toy_agent/")]


# --- corpus integrity -------------------------------------------------------


@pytest.mark.parametrize("module", [regression, challenge], ids=["regression", "challenge"])
def test_every_referenced_fixture_exists(module):
    missing = [p for _, _, _, cmd in module.CASES for p in _fixture_paths(cmd) if not (ROOT / p).is_file()]
    assert missing == []


@pytest.mark.parametrize("module", [regression, challenge], ids=["regression", "challenge"])
def test_case_ids_are_unique(module):
    ids = [(scanner, case) for scanner, case, _, _ in module.CASES]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("module", [regression, challenge], ids=["regression", "challenge"])
def test_every_scanner_has_both_a_pass_and_a_block_case(module):
    expectations: dict[str, set[bool]] = {}
    for scanner, _, should_pass, _ in module.CASES:
        expectations.setdefault(scanner, set()).add(should_pass)
    assert {s: e for s, e in expectations.items() if e != {True, False}} == {}


def test_regression_fixtures_are_clean_vulnerable_pairs():
    for scanner, case, should_pass, cmd in regression.CASES:
        (path,) = _fixture_paths(cmd)
        assert path.startswith("toy_agent/clean/" if should_pass else "toy_agent/vulnerable/"), case
        twin = path.replace("/clean/", "/vulnerable/") if should_pass else path.replace("/vulnerable/", "/clean/")
        twin_cases = [c for s, c, p, cm in regression.CASES if s == scanner and p != should_pass and twin in cm]
        assert twin_cases, f"{case} has no paired case for {twin}"


def test_regression_cases_stay_aligned_with_security_gate_workflow():
    # regression.py says to keep CASES aligned with the explicit fixture checks in the gate workflow.
    workflow = GATE_WORKFLOW.read_text(encoding="utf-8")
    drifted = [case for _, case, _, cmd in regression.CASES if " ".join(cmd) not in workflow]
    assert drifted == []


# --- metrics -----------------------------------------------------------------


@pytest.mark.parametrize("module", [regression, challenge], ids=["regression", "challenge"])
def test_metrics_confusion_matrix(module):
    rows = [
        _row(False, 1),  # vulnerable, blocked -> TP
        _row(False, 1),  # TP
        _row(False, 0),  # vulnerable, passed -> FN
        _row(True, 0),  # clean, passed -> TN
        _row(True, 2),  # clean, blocked -> FP
    ]
    m = module.metrics(rows)
    assert (m["tp"], m["fp"], m["tn"], m["fn"]) == (2, 1, 1, 1)
    assert m["precision"] == pytest.approx(2 / 3)
    assert m["recall"] == pytest.approx(2 / 3)
    assert m["f1"] == pytest.approx(2 / 3)
    assert m["false_positive_rate"] == pytest.approx(0.5)
    assert m["cases"] == 5


def test_metrics_perfect_and_empty_corpora():
    perfect = regression.metrics([_row(False, 1), _row(True, 0)])
    assert (perfect["precision"], perfect["recall"], perfect["f1"], perfect["false_positive_rate"]) == (1.0, 1.0, 1.0, 0.0)
    assert perfect["contract_pass"] is True

    empty = regression.metrics([])
    assert (empty["precision"], empty["recall"], empty["false_positive_rate"]) == (1.0, 1.0, 0.0)


def test_metrics_reports_zero_f1_when_nothing_is_caught():
    m = regression.metrics([_row(False, 0), _row(True, 1)])
    assert (m["tp"], m["precision"], m["recall"], m["f1"]) == (0, 0.0, 0.0, 0.0)
    assert m["contract_pass"] is False


def test_run_reports_missing_executable_as_127():
    code, output = regression.run(["definitely-not-a-real-scanner-binary"])
    assert code == 127
    assert "FileNotFoundError" in output


# --- end to end with fake scanners -------------------------------------------


@pytest.fixture
def fake_scanners(tmp_path, monkeypatch):
    """Put a stub for every scanner on PATH that blocks any file under toy_agent/vulnerable/."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    script = "#!/bin/sh\nfor a in \"$@\"; do case \"$a\" in *toy_agent/vulnerable/*) echo blocked; exit 1;; esac; done\necho clean\n"
    for scanner in {cmd[0] for _, _, _, cmd in regression.CASES}:
        exe = bin_dir / scanner
        exe.write_text(script, encoding="utf-8")
        exe.chmod(exe.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    return bin_dir


@pytest.mark.skipif(os.name == "nt", reason="stub scanners are POSIX shell scripts")
def test_main_writes_passing_report_when_scanners_honour_contract(fake_scanners, tmp_path, monkeypatch):
    out = tmp_path / "latest.json"
    monkeypatch.setattr(regression, "OUT", out)

    with pytest.raises(SystemExit) as exit_info:
        regression.main()

    assert exit_info.value.code == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["contract_pass"] is True
    assert report["corpus"]["total_cases"] == len(regression.CASES)
    assert report["confusion_matrix"] == {"tp": len(regression.CASES) // 2, "fp": 0, "tn": len(regression.CASES) // 2, "fn": 0}
    assert set(report["by_scanner"]) == {s for s, _, _, _ in regression.CASES}


@pytest.mark.skipif(os.name == "nt", reason="stub scanners are POSIX shell scripts")
def test_main_fails_gate_when_a_scanner_misses_a_vulnerable_fixture(fake_scanners, tmp_path, monkeypatch):
    # memsentry stops detecting anything: its vulnerable fixtures now pass.
    (fake_scanners / "memsentry").write_text("#!/bin/sh\necho clean\n", encoding="utf-8")
    out = tmp_path / "latest.json"
    monkeypatch.setattr(regression, "OUT", out)

    with pytest.raises(SystemExit) as exit_info:
        regression.main()

    assert exit_info.value.code == 1
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["contract_pass"] is False
    assert report["by_scanner"]["memsentry"]["fn"] == 2
    assert report["by_scanner"]["ragsentry"]["contract_pass"] is True


@pytest.mark.skipif(os.name == "nt", reason="stub scanners are POSIX shell scripts")
def test_challenge_never_fails_even_on_misses(fake_scanners, tmp_path, monkeypatch, capsys):
    (fake_scanners / "mcpaudit").write_text("#!/bin/sh\necho clean\n", encoding="utf-8")
    out = tmp_path / "challenge.json"
    monkeypatch.setattr(challenge, "OUT", out)

    assert challenge.main() == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["by_scanner"]["mcpaudit"]["fn"] == 1
