# 🧪 agent-security-ci

<div align="center">

**Cross-repository regression infrastructure for the Pyhroff AI-security portfolio.**

[![CI](https://github.com/Pyhroff/agent-security-ci/actions/workflows/security-gate.yml/badge.svg)](https://github.com/Pyhroff/agent-security-ci/actions/workflows/security-gate.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

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

## CI posture

Hardened workflows use least-privilege permissions, bounded execution, stale-run cancellation, explicit failure states, and immutable action references where enabled.

Private cross-repository actions require repository-level Actions access to be configured explicitly. The gate does not use personal access tokens or silently bypass inaccessible dependencies.

## Measured regression snapshot

The latest GitHub Actions benchmark executes 16 checked-in cases (8 clean/vulnerable pairs) through the real scanner CLIs.

| Metric | Result |
|---|---:|
| Precision | 1.000 |
| Recall | 1.000 |
| F1 | 1.000 |
| False-positive rate | 0.000 |
| TP / FP / TN / FN | 8 / 0 / 8 / 0 |

These figures are **fixture-regression metrics only**. They are not production detection claims; the corpus is intentionally small and paired. See `benchmark/README.md` for the methodology and measured per-scanner breakdown.

## Relationship to aisec-suite

**aisec-suite** = product-facing umbrella and common CLI.

**agent-security-ci** = compatibility and regression harness.

## Development

```bash
python -m pytest -q
```

## License

MIT


## Adversarial challenge layer

Every gate run also executes a 10-case challenge corpus containing:

- rephrased variants of known attack patterns, testing robustness beyond canonical wording;
- benign security-context controls containing attack terminology as documentation, testing false-positive resistance.

Challenge metrics are published to the workflow summary and `benchmark/challenge.json`, but **do not fail the release gate**. A challenge miss is a signal to expand scanner tests or improve detection logic, not evidence that the scanner is production-ready.
