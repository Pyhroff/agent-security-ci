# Cross-Repository Benchmark Contract

`agent-security-ci` is the integration layer for the portfolio's specialist scanners.

## Contract

1. Clean fixtures must exit successfully under their configured severity gate.
2. Known-vulnerable fixtures must produce a non-zero gate result.
3. Every fixture is deterministic and harmless.
4. Scanner CLI or output-schema changes that break the harness fail CI.
5. Benchmark metrics describe only the checked-in corpus.

## Metrics

The benchmark runner emits a confusion matrix plus precision, recall, F1 and false-positive rate. These values are regression signals, not production efficacy claims.

## Evidence chain

Threat hypothesis → fixture → scanner invocation → expected outcome → measured result → regression decision.

The benchmark should grow with new attack surfaces rather than replacing specialist unit tests.