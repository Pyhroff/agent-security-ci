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