#!/usr/bin/env python3
"""Generate plugin-first packaging from the canonical skills directory."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
CATALOG_PATH = ROOT / "skills.json"
CATALOG_NAME = "public-api-mcp-skills"
DISPLAY_NAME = "Public API MCP Skills"


def load_catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def skill_directories() -> list[Path]:
    return sorted(
        path for path in SKILLS_DIR.iterdir() if path.is_dir() and (path / "SKILL.md").exists()
    )


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def clean_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_skills(destination: Path) -> None:
    clean_directory(destination)
    for skill_dir in skill_directories():
        shutil.copytree(skill_dir, destination / skill_dir.name)


def build_instruction_body(catalog: dict, heading: str) -> str:
    sections = [
        f"# {heading}",
        "",
        catalog.get("description", ""),
        "",
        "Use these portable MCP skills when the user request matches a skill description.",
        "Each skill below is copied from its source `SKILL.md` package.",
    ]

    for skill_dir in skill_directories():
        skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8").strip()
        sections.extend(["", f"## Skill: {skill_dir.name}", "", skill_text])

    return "\n".join(sections).rstrip() + "\n"


def plugin_manifest(catalog: dict, plugin_type: str) -> dict:
    return {
        "name": CATALOG_NAME,
        "displayName": DISPLAY_NAME,
        "version": catalog.get("version", "0.1.0"),
        "description": catalog.get("description", ""),
        "type": plugin_type,
        "skills": "skills",
    }


def build_claude_plugin(catalog: dict) -> None:
    plugin_dir = ROOT / ".claude-plugin"
    clean_directory(plugin_dir)
    write_json(plugin_dir / "plugin.json", plugin_manifest(catalog, "claude-code"))
    copy_skills(plugin_dir / "skills")


def build_cursor_plugin(catalog: dict) -> None:
    plugin_dir = ROOT / ".cursor-plugin"
    clean_directory(plugin_dir)
    write_json(plugin_dir / "plugin.json", plugin_manifest(catalog, "cursor"))
    copy_skills(plugin_dir / "skills")


def build_gemini_extension(catalog: dict) -> None:
    write_json(
        ROOT / "gemini-extension.json",
        {
            "name": CATALOG_NAME,
            "version": catalog.get("version", "0.1.0"),
            "contextFileName": "GEMINI.md",
        },
    )
    gemini_body = build_instruction_body(catalog, DISPLAY_NAME)
    (ROOT / "GEMINI.md").write_text(gemini_body, encoding="utf-8")
    gemini_dir = ROOT / ".gemini"
    gemini_dir.mkdir(parents=True, exist_ok=True)
    (gemini_dir / "GEMINI.md").write_text(gemini_body, encoding="utf-8")


def build_vscode_instructions(catalog: dict) -> None:
    instructions_dir = ROOT / ".github" / "instructions"
    instructions_dir.mkdir(parents=True, exist_ok=True)
    (instructions_dir / f"{CATALOG_NAME}.instructions.md").write_text(
        build_instruction_body(catalog, DISPLAY_NAME),
        encoding="utf-8",
    )


def build_root_manifests(catalog: dict) -> None:
    write_json(
        ROOT / "plugin.json",
        {
            "name": CATALOG_NAME,
            "displayName": DISPLAY_NAME,
            "version": catalog.get("version", "0.1.0"),
            "description": catalog.get("description", ""),
            "skills": "skills",
            "platforms": ["claude-code", "cursor", "gemini-cli", "vscode"],
        },
    )
    write_json(
        ROOT / "package.json",
        {
            "name": CATALOG_NAME,
            "version": catalog.get("version", "0.1.0"),
            "description": catalog.get("description", ""),
            "private": True,
            "scripts": {
                "build": "python scripts/build.py",
                "validate": "python scripts/validate.py",
            },
            "keywords": ["agent-skills", "claude-code", "cursor", "gemini-cli", "vscode"],
            "license": "MIT",
        },
    )


def main() -> int:
    if not SKILLS_DIR.exists():
        raise SystemExit(f"Missing source directory: {SKILLS_DIR}")
    if not CATALOG_PATH.exists():
        raise SystemExit(f"Missing catalog: {CATALOG_PATH}")

    catalog = load_catalog()
    build_root_manifests(catalog)
    build_claude_plugin(catalog)
    build_cursor_plugin(catalog)
    build_gemini_extension(catalog)
    build_vscode_instructions(catalog)

    print(f"Built plugin packaging for {len(skill_directories())} skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
