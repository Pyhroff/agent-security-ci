# Controlled Regression Benchmark

This corpus is the integration contract for the Pyhroff AI-security scanners.

## What it measures

Paired clean and known-vulnerable fixtures are executed through the real scanner CLIs. Clean fixtures must pass; vulnerable fixtures must trigger their configured severity gate.

The runner records TP, FP, TN, FN, precision, recall, F1, false-positive rate, and per-case exit codes.

Run:

    python scripts/regression.py

Results are written to `benchmark/latest.json`.

## Boundary

These metrics describe only the checked-in regression corpus. They are not claims about real-world prevalence, coverage, or exploitability.

The benchmark answers a narrower engineering question: did a scanner change preserve the security behavior we already expect?

## Adding cases

Every new fixture should have a threat hypothesis, expected behavior, deterministic execution, and a benign counterpart where practical. Keep all fixtures harmless and review benchmark changes like production security code.
## Latest measured snapshot

The GitHub Actions run for commit `29d6f7a` executed all 16 checked-in cases (8 clean/vulnerable pairs) through the real scanner CLIs.

| Scanner | Cases | Precision | Recall | F1 | FPR |
|---|---:|---:|---:|---:|---:|
| mcpaudit | 2 | 1.000 | 1.000 | 1.000 | 0.000 |
| loopcheck | 2 | 1.000 | 1.000 | 1.000 | 0.000 |
| memsentry | 4 | 1.000 | 1.000 | 1.000 | 0.000 |
| ragsentry | 4 | 1.000 | 1.000 | 1.000 | 0.000 |
| trainsentry | 4 | 1.000 | 1.000 | 1.000 | 0.000 |
| **Overall** | **16** | **1.000** | **1.000** | **1.000** | **0.000** |

Confusion matrix: **TP=8, FP=0, TN=8, FN=0**.

**Interpretation:** this is a regression-contract result over a small, deliberately paired fixture corpus. It demonstrates that the current scanner behavior satisfies these checked-in expectations; it does **not** establish production-world precision, recall, coverage, or exploitability. The next benchmark expansion should add held-out and adversarially varied cases before making broader claims.
