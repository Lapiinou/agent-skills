#!/usr/bin/env python3
"""Install skill packages into an IDE skill directory."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install MCP skill packages.")
    parser.add_argument(
        "--target",
        required=True,
        help="Directory where skill packages should be installed.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing skill directories with the same names.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent.parent
    source_dir = root / "skills"
    target_dir = Path(args.target).expanduser().resolve()

    if not source_dir.exists():
        raise SystemExit(f"Missing source directory: {source_dir}")

    target_dir.mkdir(parents=True, exist_ok=True)
    installed = 0
    skipped: list[str] = []

    for skill_dir in sorted(path for path in source_dir.iterdir() if path.is_dir()):
        if not (skill_dir / "SKILL.md").exists():
            continue
        destination = target_dir / skill_dir.name
        if destination.exists():
            if not args.force:
                skipped.append(skill_dir.name)
                continue
            shutil.rmtree(destination)
        shutil.copytree(skill_dir, destination)
        installed += 1

    print(f"Installed {installed} skill(s) into {target_dir}")
    if skipped:
        print("Skipped existing skills: " + ", ".join(skipped))
        print("Re-run with --force to replace them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
