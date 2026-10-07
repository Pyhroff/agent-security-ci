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


## Adversarial challenge corpus

`challenge.py` runs ten held-out-style cases: five semantically malicious variants and five benign security-context controls. The malicious variants preserve the underlying threat while changing wording or structure; the benign controls deliberately contain security terminology without making it an instruction to the agent.

The challenge layer is **non-gating**. This is intentional: a miss should become visible as evidence for scanner hardening rather than being converted into an arbitrary release failure. Results are written to `benchmark/challenge.json` and summarized in GitHub Actions.

Interpret challenge metrics as exploratory regression evidence, not a representative evaluation set. The corpus is small, hand-authored, and designed to probe known failure modes.

## Measured challenge result

The first challenge run used 10 hand-authored cases (five rephrased malicious variants and five benign security-context controls). The real scanner CLIs produced **TP=1, FP=4, TN=1, FN=4**, yielding **precision=0.200, recall=0.200, F1=0.200, FPR=0.800**.

| Scanner | TP | FP | TN | FN | Precision | Recall | F1 | FPR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| mcpaudit | 0 | 1 | 0 | 1 | 0.000 | 0.000 | 0.000 | 1.000 |
| loopcheck | 1 | 1 | 0 | 0 | 0.500 | 1.000 | 0.667 | 1.000 |
| memsentry | 0 | 1 | 0 | 1 | 0.000 | 0.000 | 0.000 | 1.000 |
| ragsentry | 0 | 1 | 0 | 1 | 0.000 | 0.000 | 0.000 | 1.000 |
| trainsentry | 0 | 0 | 1 | 1 | 1.000 | 0.000 | 0.000 | 0.000 |
| **Overall** | **1** | **4** | **1** | **4** | **0.200** | **0.200** | **0.200** | **0.800** |

### What this exposed

- **mcpaudit:** a semantically equivalent poisoned tool description evaded the current pattern match, while a benign security description containing words such as “override” triggered a finding.
- **loopcheck:** the rephrased repeated-call attack was detected, but a benign two-call verification flow was treated as wasteful. The current rule needs stronger progress/context semantics before a repeated call is considered a defect.
- **memsentry:** rephrased memory injection evaded detection, while explanatory security text containing an injection phrase was treated as an instruction.
- **ragsentry:** the same semantic-vs-literal limitation appeared in retrieved-document detection.
- **trainsentry:** the benign control passed, but the rephrased poisoning variant evaded detection.

These are hypotheses for scanner hardening, not claims about general-world performance. The corpus is intentionally small and should grow into a held-out suite with multiple independent variants per threat class.


## Post-hardening rerun

The scanner hardening changes identified by the first challenge run have now landed in `mcpaudit`, `memsentry`, `ragsentry`, `trainsentry`, and `loopcheck`. The next gate run executes this same challenge corpus against those updated default branches; the original 0.20/0.20 result above is retained as the baseline for comparison.


## Final gap fix rerun

`ragsentry` received one additional targeted fix for the remaining “disregard previous guidance” variant. The next umbrella run will validate the complete challenge corpus against that revision.
