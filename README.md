# agent-security-ci

[![CI](https://github.com/Pyhroff/agent-security-ci/actions/workflows/security-gate.yml/badge.svg)](https://github.com/Pyhroff/agent-security-ci/actions/workflows/security-gate.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Cross-repository regression infrastructure for the Pyhroff AI-security portfolio.**

## Purpose

A scanner's unit tests prove its own rules execute correctly.

`agent-security-ci` asks the harder question:

> **Do the scanners still work together after one of them changes?**

The harness exercises clean, vulnerable, and adversarial fixtures across the portfolio and acts as the integration/regression layer around [aisec-suite](https://github.com/Pyhroff/aisec-suite). The checked-in regression corpus is release-gating; the adversarial challenge corpus is deliberately non-gating so weaknesses are surfaced rather than hidden behind a green build.

## Covered systems

| Tool | Surface |
|---|---|
| mcpaudit | MCP poisoning and permission scope |
| memsentry | Persistent memory injection |
| ragsentry | RAG/document injection |
| trainsentry | Training-data poisoning |
| loopcheck | Agent-loop waste and thrashing |
| wormsentry | Package-worm behavior |
| adversagen | Adaptive adversarial regression experiments |

## What the gate catches

**Missed detection** — a planted vulnerable fixture stops triggering.

**False-positive regression** — a clean fixture starts triggering.

**Integration drift** — a scanner's CLI, schema, output, or dependency changes break downstream tooling.

## Regression corpus

`scripts/regression.py` runs 26 checked-in cases (13 clean / vulnerable pairs across mcpaudit, loopcheck, memsentry, ragsentry, trainsentry, specprove, weightspecter, tokenspecter, circuitshield and attestinfer) through the real scanner CLIs. A clean fixture must pass and its vulnerable twin must trip the configured severity gate; any mismatch fails CI. Each run writes precision, recall, F1, false-positive rate and per-case exit codes to `benchmark/latest.json` and the workflow summary.

These are **fixture-regression metrics**: the corpus is small, paired and written alongside the scanners, so a perfect score means "nothing regressed", not "the detectors are accurate". See `benchmark/README.md`.

## Adversarial challenge layer

`scripts/challenge.py` runs a non-gating 10-case corpus: one rephrased attack and one benign security-documentation control per scanner (mcpaudit, loopcheck, memsentry, ragsentry, trainsentry). It surfaces weaknesses without blocking releases.

| Run | Precision | Recall | F1 | FPR | TP / FP / TN / FN |
|---|---:|---:|---:|---:|---|
| First run (37658926358, commit 3affd73) | 0.200 | 0.200 | 0.200 | 0.800 | 1 / 4 / 1 / 4 |
| After hardening the five scanners | 1.000 | 1.000 | 1.000 | 0.000 | 5 / 0 / 5 / 0 |

The first run showed the scanners missed rephrased attacks and flagged quoted security guidance. The scanners were then changed to fix exactly those cases, so the second row measures that the observed failures were addressed; the challenge is now a development set, not a held-out test. Held-out evaluations of the detectors live in [aisec-suite's STUDY.md](https://github.com/Pyhroff/aisec-suite/blob/master/docs/STUDY.md).

## CI posture

Workflows use least-privilege permissions, bounded execution, stale-run cancellation, explicit failure states and actions pinned to commit SHAs (enforced by `action-ref-gate.yml`). The security gate installs the scanners from their repositories with a `TOOLS_PAT` repository secret and fails closed if it is missing; the harness's own tests (`tests.yml`) need no secrets.

## Relationship to aisec-suite

**aisec-suite** is the product-facing umbrella and CLI; **agent-security-ci** is the cross-scanner compatibility and regression harness around it.

## Development

```bash
python -m pip install pytest
python -m pytest -q tests        # harness tests with stub scanners (no private packages needed)
python scripts/regression.py     # needs the scanner CLIs installed
```

## License

MIT
