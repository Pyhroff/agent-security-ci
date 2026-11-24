#!/usr/bin/env python3
"""Run the controlled scanner regression corpus and emit machine-readable metrics."""
from __future__ import annotations

import json
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark" / "latest.json"

# Keep this list aligned with the explicit clean/vulnerable fixture checks in
# .github/workflows/security-gate.yml.
CASES = [
    ("mcpaudit", "clean_mcp", True, ["mcpaudit", "scan", "--fail-on", "high", "--", "python", "toy_agent/clean/mcp_server.py"]),
    ("mcpaudit", "vulnerable_mcp", False, ["mcpaudit", "scan", "--fail-on", "high", "--", "python", "toy_agent/vulnerable/mcp_server.py"]),
    ("loopcheck", "clean_trace", True, ["loopcheck", "analyze", "toy_agent/clean/trace.json", "--fail-on", "medium"]),
    ("loopcheck", "vulnerable_trace", False, ["loopcheck", "analyze", "toy_agent/vulnerable/trace.json", "--fail-on", "medium"]),
    ("memsentry", "clean_memory", True, ["memsentry", "toy_agent/clean/memory.md", "--fail-on", "high"]),
    ("memsentry", "vulnerable_memory", False, ["memsentry", "toy_agent/vulnerable/memory.md", "--fail-on", "high"]),
    ("ragsentry", "clean_rag", True, ["ragsentry", "toy_agent/clean/rag_doc.md", "--fail-on", "high"]),
    ("ragsentry", "vulnerable_rag", False, ["ragsentry", "toy_agent/vulnerable/rag_doc.md", "--fail-on", "high"]),
    ("trainsentry", "clean_training", True, ["trainsentry", "toy_agent/clean/training_data.jsonl", "--fail-on", "high"]),
    ("trainsentry", "vulnerable_training", False, ["trainsentry", "toy_agent/vulnerable/training_data.jsonl", "--fail-on", "high"]),
    ("memsentry", "clean_goal_hijack_memory", True, ["memsentry", "toy_agent/clean/goal_hijack_memory.md", "--fail-on", "high"]),
    ("memsentry", "vulnerable_goal_hijack_memory", False, ["memsentry", "toy_agent/vulnerable/goal_hijack_memory.md", "--fail-on", "high"]),
    ("ragsentry", "clean_fake_remediation", True, ["ragsentry", "toy_agent/clean/fake_remediation_doc.md", "--fail-on", "high"]),
    ("ragsentry", "vulnerable_fake_remediation", False, ["ragsentry", "toy_agent/vulnerable/fake_remediation_doc.md", "--fail-on", "high"]),
    ("trainsentry", "clean_goal_hijack_training", True, ["trainsentry", "toy_agent/clean/goal_hijack_training.jsonl", "--fail-on", "high"]),
    ("trainsentry", "vulnerable_goal_hijack_training", False, ["trainsentry", "toy_agent/vulnerable/goal_hijack_training.jsonl", "--fail-on", "high"]),
    ("specprove", "clean_formal_protocols", True, ["specprove", "scan-py", "toy_agent/clean/protocol_handlers.py", "--fail-on-findings"]),
    ("specprove", "vulnerable_formal_protocols", False, ["specprove", "scan-py", "toy_agent/vulnerable/protocol_handlers.py", "--fail-on-findings"]),
]


def run(cmd: list[str]) -> tuple[int, str]:
    try:
        p = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        return p.returncode, p.stdout[-4000:]
    except OSError as exc:
        return 127, f"{type(exc).__name__}: {exc}"


def metrics(rows: list[dict]) -> dict:
    tp = sum((not r["expected_pass"]) and r["exit_code"] != 0 for r in rows)
    fn = sum((not r["expected_pass"]) and r["exit_code"] == 0 for r in rows)
    tn = sum(r["expected_pass"] and r["exit_code"] == 0 for r in rows)
    fp = sum(r["expected_pass"] and r["exit_code"] != 0 for r in rows)
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "cases": len(rows),
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": fp / (fp + tn) if fp + tn else 0.0,
        "contract_pass": all(r["contract_pass"] for r in rows),
    }


def main() -> None:
    rows = []
    for scanner, case, should_pass, cmd in CASES:
        code, output = run(cmd)
        contract_pass = (code == 0) == should_pass
        rows.append(
            {
                "scanner": scanner,
                "case": case,
                "expected_pass": should_pass,
                "exit_code": code,
                "contract_pass": contract_pass,
                "output_tail": output,
            }
        )

    by_scanner: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_scanner[row["scanner"]].append(row)

    report = {
        "benchmark": "agent-security-ci controlled regression corpus",
        "scope": "checked-in fixtures only; not a production detection claim",
        "corpus": {"total_cases": len(rows), "paired_cases": len(rows) // 2, "scanners": sorted(by_scanner)},
        "cases": rows,
        "confusion_matrix": {k: metrics(rows)[k] for k in ("tp", "fp", "tn", "fn")},
        "metrics": {k: metrics(rows)[k] for k in ("precision", "recall", "f1", "false_positive_rate")},
        "by_scanner": {scanner: metrics(scanner_rows) for scanner, scanner_rows in sorted(by_scanner.items())},
        "contract_pass": all(r["contract_pass"] for r in rows),
    }

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["contract_pass"] else 1)


if __name__ == "__main__":
    main()
