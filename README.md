# agent-security-ci

A working demonstration of wiring [mcpaudit](https://github.com/Pyhroff/mcpaudit),
[loopcheck](https://github.com/Pyhroff/loopcheck),
[memsentry](https://github.com/Pyhroff/memsentry),
[ragsentry](https://github.com/Pyhroff/ragsentry), and
[trainsentry](https://github.com/Pyhroff/trainsentry) into a real CI gate
against a toy agent, instead of leaving them as five standalone CLIs — plus
a regression check for [adversagen](https://github.com/Pyhroff/adversagen),
the red-team counterpart that adversarially tests three of them for real.

This is not a sixth scanner. It's the answer to "okay, you built five
security tools -- do they actually catch anything in a pipeline, or do they
just run locally?"

## What's here

Two tiny toy agents, `clean/` and `vulnerable/`, each with the artifacts
the five tools need:

| | `toy_agent/clean/` | `toy_agent/vulnerable/` |
|---|---|---|
| MCP server (`mcp_server.py`) | normal, well-scoped tool description | tool description with embedded instruction-override phrasing ("always call this first", "never tell the user", "ignore any previous instructions") |
| Agent trace (`trace.json`) | one necessary tool call | the same tool called 5x with identical arguments -- pure thrashing |
| Memory export (`memory.md`) | ordinary `[stated]` facts | a forged `[stated]`-tagged instruction plus a plain override line |
| RAG document (`rag_doc.md`) | ordinary returns-policy text | a `[SYSTEM NOTE]`-tagged instruction-override + biased-recommendation injection |
| Training data (`training_data.jsonl`) | 15 ordinary arithmetic Q&A records | one completion rewritten as a standing instruction |

`.github/workflows/security-gate.yml` runs all five tools against both
agents on every push:

- against `clean/`, every scan **must pass** -- a failure here is a real
  regression (a false positive newly introduced into one of the tools).
- against `vulnerable/`, every scan **must fail** -- the workflow inverts
  the exit code and fails the job if a tool *doesn't* catch its known-bad
  fixture, so "gate stopped detecting this" is what turns the pipeline red,
  not "the vulnerable fixture is vulnerable" (which is the point).

Run `gh run view` on this repo and you're looking at proof that these five
scanners actually catch what they claim to, in an automated pipeline, not
just against curated local `samples/` fixtures.

## The adversagen regression stage

The last job step clones `adversagen` (the adaptive attack-payload
generator that adversarially tests mcpaudit/memsentry/ragsentry for real,
via its `RealScannerDefender`) and runs its own test suite. This isn't
redundant with adversagen's own repo having its own CI -- it catches a
*cross-repo* regression that adversagen's own tests, run in isolation,
never would: if a future change to mcpaudit/memsentry/ragsentry (a CLI
flag rename, an exit-code change, an output-format change) breaks how
adversagen actually calls them, **this job goes red**, because it's
installing this pipeline's exact current versions of all three scanners
alongside adversagen's tests, not whatever version adversagen's own CI
happened to pin. That's the kind of integration break a single repo's
own test suite structurally cannot see.

## Why a PAT secret instead of a plain `pip install`

None of these six repos are published to PyPI -- they're private repos
under the same account. The workflow installs them straight from GitHub
using a fine-scoped PAT stored as the `TOOLS_PAT` repository secret. This
mirrors how a real team runs its own internal security tooling in CI
before (or instead of) publishing it publicly.

## Running it locally

```
pip install git+https://github.com/Pyhroff/mcpaudit.git
pip install git+https://github.com/Pyhroff/loopcheck.git
pip install git+https://github.com/Pyhroff/memsentry.git
pip install git+https://github.com/Pyhroff/ragsentry.git
pip install git+https://github.com/Pyhroff/trainsentry.git

mcpaudit scan --fail-on high -- python3 toy_agent/vulnerable/mcp_server.py     # exits 1
loopcheck analyze toy_agent/vulnerable/trace.json --fail-on medium            # exits 1
memsentry toy_agent/vulnerable/memory.md --fail-on high                      # exits 1
ragsentry toy_agent/vulnerable/rag_doc.md --fail-on high                     # exits 1
trainsentry toy_agent/vulnerable/training_data.jsonl --fail-on high          # exits 1
```

(Requires read access to the private repos above.)
