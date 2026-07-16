from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_HEADINGS = ["## Scope", "## Standards"]


def validate_agent_file(path: Path) -> list[str]:
    content = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for heading in REQUIRED_HEADINGS:
        if heading not in content:
            errors.append(f"{path}: missing heading {heading}")
    return errors


def main() -> int:
    agent_dir = Path(".claude/agents")
    if not agent_dir.exists():
        print("No agent directory found; skipping validation.")
        return 0

    errors: list[str] = []
    for file_path in sorted(agent_dir.glob("*.md")):
        errors.extend(validate_agent_file(file_path))

    if errors:
        for error in errors:
            print(error)
        return 1

    print("Agent scope definitions look valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
