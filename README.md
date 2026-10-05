# agent-security-ci

Cross-repository CI harness for the Pyhroff AI-agent security tooling suite.

The repository exercises the scanners against known-good and known-bad fixtures and runs adversarial regression tests. A failing gate therefore signals a false-positive regression, missed detection, integration break, or environment problem.

## Covered tools

| Tool | Surface |
|---|---|
| mcpaudit | MCP tool poisoning and scope checks |
| loopcheck | agent-loop waste and thrashing |
| memsentry | memory injection |
| ragsentry | RAG/document injection |
| trainsentry | training-data poisoning |
| adversagen | adaptive adversarial regression testing |

## Test model

Clean fixtures must remain below the CI threshold. Vulnerable fixtures must produce a blocking result. Capability-specific fixtures independently exercise newer detector categories.

## Security properties

The workflow uses least-privilege contents read permissions, cancels stale runs, bounds execution time, verifies scanner CLIs, fails closed on missed detections, and tests cross-repository compatibility through adversagen.

## Local reproduction

The CI environment expects `TOOLS_PAT` with read access to the private scanner repositories.

```bash
export TOOLS_PAT=...
for repo in mcpaudit loopcheck memsentry ragsentry trainsentry; do
  pip install "git+https://x-access-token:$TOOLS_PAT@github.com/Pyhroff/$repo.git"
done
```

The purpose of this repository is integration: the individual scanners answer whether an artifact looks unsafe; this repository answers whether they still work together after one of them changes.

## License

MIT
