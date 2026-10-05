# 🧪 agent-security-ci

<div align="center">

**Cross-repository regression infrastructure for the Pyhroff AI-security portfolio.**

[![CI](https://github.com/Pyhroff/agent-security-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/Pyhroff/agent-security-ci/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

## Purpose

A scanner's unit tests prove its own rules execute correctly.

`agent-security-ci` asks the harder question:

> **Do the scanners still work together after one of them changes?**

The harness exercises clean, vulnerable, and adversarial fixtures across the portfolio and acts as the integration/regression layer around [aisec-suite](https://github.com/Pyhroff/aisec-suite).

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

Private cross-repository jobs require an appropriate read-only repository credential. Missing credentials are treated as infrastructure/configuration failures, never as a reason to bypass a security gate.

## Relationship to aisec-suite

**aisec-suite** = product-facing umbrella and common CLI.

**agent-security-ci** = compatibility and regression harness.

The two layers intentionally solve different problems.

## Development

```bash
python -m pytest -q
```

## License

MIT
