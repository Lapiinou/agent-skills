#!/usr/bin/env python3
"""Install skill packages into supported agent tool directories."""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from pathlib import Path


CATALOG_NAME = "public-api-mcp-skills"
PRESET_TARGETS = ("claude-code", "cursor", "gemini-cli", "vscode")


@dataclass(frozen=True)
class InstallTarget:
    name: str
    directory: Path
    mode: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install MCP skill packages.")
    parser.add_argument(
        "--target",
        action="append",
        help=(
            "Install target. Use a preset "
            f"({', '.join(PRESET_TARGETS)}, all) or a directory path. "
            "May be passed more than once."
        ),
    )
    parser.add_argument(
        "--target-dir",
        help="Explicit directory for a single custom install target.",
    )
    parser.add_argument(
        "--project",
        help=(
            "Project root for project-local installs. For example, Cursor uses "
            "<project>/.cursor/skills and VS Code uses <project>/.github/instructions."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace existing skill directories with the same names.",
    )
    return parser.parse_args()


def skill_directories(source_dir: Path) -> list[Path]:
    return sorted(
        path for path in source_dir.iterdir() if path.is_dir() and (path / "SKILL.md").exists()
    )


def default_target(name: str, project_root: Path | None) -> InstallTarget:
    home = Path.home()

    if name == "claude-code":
        directory = project_root / ".claude" / "skills" if project_root else home / ".claude" / "skills"
        return InstallTarget(name=name, directory=directory, mode="skill-dirs")
    if name == "cursor":
        directory = project_root / ".cursor" / "skills" if project_root else home / ".cursor" / "skills"
        return InstallTarget(name=name, directory=directory, mode="skill-dirs")
    if name == "gemini-cli":
        directory = (
            project_root / ".gemini" / "extensions" / CATALOG_NAME
            if project_root
            else home / ".gemini" / "extensions" / CATALOG_NAME
        )
        return InstallTarget(name=name, directory=directory, mode="gemini-extension")
    if name == "vscode":
        if not project_root:
            raise SystemExit("--target vscode requires --project /path/to/project")
        return InstallTarget(
            name=name,
            directory=project_root / ".github" / "instructions",
            mode="vscode-instructions",
        )

    raise SystemExit(f"Unknown install target: {name}")


def resolve_targets(args: argparse.Namespace) -> list[InstallTarget]:
    project_root = Path(args.project).expanduser().resolve() if args.project else None

    if args.target_dir:
        if args.target:
            raise SystemExit("Use either --target or --target-dir, not both.")
        return [
            InstallTarget(
                name="custom",
                directory=Path(args.target_dir).expanduser().resolve(),
                mode="skill-dirs",
            )
        ]

    target_names = args.target or ["all"]
    resolved_names: list[str] = []
    for raw_target in target_names:
        for target in raw_target.split(","):
            target = target.strip()
            if not target:
                continue
            if target == "all":
                resolved_names.extend(PRESET_TARGETS)
            elif target in PRESET_TARGETS:
                resolved_names.append(target)
            else:
                return [
                    InstallTarget(
                        name="custom",
                        directory=Path(target).expanduser().resolve(),
                        mode="skill-dirs",
                    )
                ]

    targets: list[InstallTarget] = []
    seen: set[tuple[str, Path]] = set()
    for name in resolved_names:
        target = default_target(name, project_root)
        key = (target.mode, target.directory)
        if key not in seen:
            targets.append(target)
            seen.add(key)
    return targets


def copy_skill_dirs(source_dir: Path, target_dir: Path, force: bool) -> tuple[int, list[str]]:
    target_dir.mkdir(parents=True, exist_ok=True)
    installed = 0
    skipped: list[str] = []

    for skill_dir in skill_directories(source_dir):
        destination = target_dir / skill_dir.name
        if destination.exists():
            if not force:
                skipped.append(skill_dir.name)
                continue
            shutil.rmtree(destination)
        shutil.copytree(skill_dir, destination)
        installed += 1

    return installed, skipped


def build_instruction_body(source_dir: Path, heading: str) -> str:
    sections = [
        f"# {heading}",
        "",
        "Use these portable MCP skills when the user request matches a skill description.",
        "Each skill below is copied from its source `SKILL.md` package.",
    ]

    for skill_dir in skill_directories(source_dir):
        skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8").strip()
        sections.extend(["", f"## Skill: {skill_dir.name}", "", skill_text])

    return "\n".join(sections).rstrip() + "\n"


def install_gemini_extension(source_dir: Path, target_dir: Path, force: bool) -> tuple[int, list[str]]:
    if target_dir.exists():
        if not force:
            return 0, [target_dir.name]
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "name": CATALOG_NAME,
        "version": "0.1.0",
        "contextFileName": "GEMINI.md",
    }
    (target_dir / "gemini-extension.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    (target_dir / "GEMINI.md").write_text(
        build_instruction_body(source_dir, "Public API MCP Skills"),
        encoding="utf-8",
    )
    return 1, []


def install_vscode_instructions(source_dir: Path, target_dir: Path, force: bool) -> tuple[int, list[str]]:
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / f"{CATALOG_NAME}.instructions.md"
    if destination.exists() and not force:
        return 0, [destination.name]
    destination.write_text(
        build_instruction_body(source_dir, "Public API MCP Skills"),
        encoding="utf-8",
    )
    return 1, []


def install_target(source_dir: Path, target: InstallTarget, force: bool) -> tuple[int, list[str]]:
    if target.mode == "skill-dirs":
        return copy_skill_dirs(source_dir, target.directory, force)
    if target.mode == "gemini-extension":
        return install_gemini_extension(source_dir, target.directory, force)
    if target.mode == "vscode-instructions":
        return install_vscode_instructions(source_dir, target.directory, force)
    raise SystemExit(f"Unsupported install mode: {target.mode}")


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent.parent
    source_dir = root / "skills"

    if not source_dir.exists():
        raise SystemExit(f"Missing source directory: {source_dir}")

    for target in resolve_targets(args):
        installed, skipped = install_target(source_dir, target, args.force)
        print(f"[{target.name}] Installed {installed} item(s) into {target.directory}")
        if skipped:
            print(f"[{target.name}] Skipped existing items: " + ", ".join(skipped))
            print(f"[{target.name}] Re-run with --force to replace them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
