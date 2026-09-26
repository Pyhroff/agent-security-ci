# agent-security-ci

A working demonstration of wiring [mcpaudit](https://github.com/Pyhroff/mcpaudit),
[loopcheck](https://github.com/Pyhroff/loopcheck), and
[memsentry](https://github.com/Pyhroff/memsentry) into a real CI gate against
a toy agent, instead of leaving them as three standalone CLIs.

This is not a fourth scanner. It's the answer to "okay, you built three
security tools -- do they actually catch anything in a pipeline, or do they
just run locally?"

## What's here

Two tiny toy agents, `clean/` and `vulnerable/`, each with the three
artifacts the three tools need:

| | `toy_agent/clean/` | `toy_agent/vulnerable/` |
|---|---|---|
| MCP server (`mcp_server.py`) | normal, well-scoped tool description | tool description with embedded instruction-override phrasing ("always call this first", "never tell the user", "ignore any previous instructions") |
| Agent trace (`trace.json`) | one necessary tool call | the same tool called 5x with identical arguments -- pure thrashing |
| Memory export (`memory.md`) | ordinary `[stated]` facts | a forged `[stated]`-tagged instruction plus a plain override line |

`.github/workflows/security-gate.yml` runs all three tools against both
agents on every push:

- against `clean/`, every scan **must pass** -- a failure here is a real
  regression (a false positive newly introduced into one of the tools).
- against `vulnerable/`, every scan **must fail** -- the workflow inverts
  the exit code and fails the job if a tool *doesn't* catch its known-bad
  fixture, so "gate stopped detecting this" is what turns the pipeline red,
  not "the vulnerable fixture is vulnerable" (which is the point).

Run `gh run view` on this repo and you're looking at proof that these three
scanners actually catch what they claim to, in an automated pipeline, not
just against curated local `samples/` fixtures.

## Why a PAT secret instead of a plain `pip install`

mcpaudit, loopcheck and memsentry aren't published to PyPI -- they're
private repos under the same account. The workflow installs them straight
from GitHub using a fine-scoped PAT stored as the `TOOLS_PAT` repository
secret. This mirrors how a real team runs its own internal security tooling
in CI before (or instead of) publishing it publicly.

## Running it locally

```
pip install git+https://github.com/Pyhroff/mcpaudit.git
pip install git+https://github.com/Pyhroff/loopcheck.git
pip install git+https://github.com/Pyhroff/memsentry.git

mcpaudit scan --fail-on high -- python3 toy_agent/vulnerable/mcp_server.py   # exits 1
loopcheck analyze toy_agent/vulnerable/trace.json --fail-on medium          # exits 1
memsentry toy_agent/vulnerable/memory.md --fail-on high                     # exits 1
```

(Requires read access to the three private repos above.)
