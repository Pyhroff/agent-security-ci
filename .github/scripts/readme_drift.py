#!/usr/bin/env python3
"""Conservative README drift detector.

Checks README links and common executable/file references without requiring
network access or credentials. The goal is actionable failures, not lint noise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

SKIP_SCHEMES = {"http", "https", "mailto", "tel"}
README_NAMES = {"README", "README.md", "README.rst", "README.txt"}

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
COMMAND_RE = re.compile(
    r"(?m)^\s*(?:\$\s*)?(?:python3?|bash|sh|zsh|ruby|node)\s+([A-Za-z0-9_./-]+)"
)
DIRECT_RE = re.compile(r"(?m)^\s*(?:\$\s*)?(\./[A-Za-z0-9_./-]+)")
BADGE_RE = re.compile(r"actions/workflows/([^/]+)/badge\.svg")


def local_target(readme: Path, raw: str) -> Path | None:
    raw = unquote(raw.strip().strip("<>"))
    parsed = urlparse(raw)
    if parsed.scheme in SKIP_SCHEMES or parsed.netloc:
        return None
    if raw.startswith("#") or raw.startswith("data:"):
        return None
    target = raw.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return None
    return (readme.parent / target).resolve()


def check_readme(readme: Path) -> list[str]:
    errors: list[str] = []
    text = readme.read_text(encoding="utf-8", errors="replace")

    for raw in LINK_RE.findall(text):
        target = local_target(readme, raw)
        if target is None:
            continue
        if not target.exists():
            errors.append(f"{readme}: broken local link -> {raw}")

    for rel in COMMAND_RE.findall(text) + DIRECT_RE.findall(text):
        target = (readme.parent / rel.lstrip("./")).resolve()
        if not target.exists():
            errors.append(f"{readme}: command references missing path -> {rel}")

    for workflow in BADGE_RE.findall(text):
        target = readme.parent / ".github" / "workflows" / workflow
        if not target.exists():
            errors.append(f"{readme}: workflow badge references missing workflow -> {workflow}")

    return errors


def main() -> int:
    readmes = sorted(
        p for p in Path(".").rglob("*")
        if p.is_file() and p.name in README_NAMES
        and not any(part.startswith(".git") or part in {"node_modules", ".venv", "venv"} for part in p.parts)
    )
    if not readmes:
        print("README drift: no README files found; nothing to check.")
        return 0

    errors: list[str] = []
    for readme in readmes:
        errors.extend(check_readme(readme))

    if errors:
        print("README DRIFT DETECTED")
        for error in errors:
            print(f"- {error}")
        print(f"\n{len(errors)} actionable issue(s).")
        return 1

    print(f"README drift check passed: {len(readmes)} README file(s) checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
