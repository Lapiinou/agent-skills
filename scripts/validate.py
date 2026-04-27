#!/usr/bin/env python3
"""Validate the portable skill catalog."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
CATALOG_NAME = "public-api-mcp-skills"
BANNED_PATTERNS = (
    re.compile(r"GoodBarber", re.IGNORECASE),
    re.compile(r"\bgb\b", re.IGNORECASE),
    re.compile(r"gb[-_]", re.IGNORECASE),
    re.compile(r"goodbarber\.", re.IGNORECASE),
)


def load_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        return {}

    data: dict[str, str] = {}
    lines = match.group(1).splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            index += 1
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value == "|":
            index += 1
            block: list[str] = []
            while index < len(lines) and (
                lines[index].startswith(" ") or not lines[index].strip()
            ):
                block.append(lines[index].lstrip())
                index += 1
            data[key] = "\n".join(block).strip()
            continue
        data[key] = value.strip("\"'")
        index += 1
    return data


def check_white_label(path: Path, errors: list[str]) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for pattern in BANNED_PATTERNS:
        if pattern.search(text):
            errors.append(f"{path.relative_to(ROOT)} contains banned brand text")
            return


def check_json_name(path: Path, expected_name: str, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"Missing {path.relative_to(ROOT)}")
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("name") != expected_name:
        errors.append(f"{path.relative_to(ROOT)} name should be {expected_name}")


def check_plugin_skills(plugin_dir: Path, catalog_names: set[str], errors: list[str]) -> None:
    skills_dir = plugin_dir / "skills"
    if not skills_dir.exists():
        errors.append(f"Missing {skills_dir.relative_to(ROOT)}")
        return

    plugin_names = {path.name for path in skills_dir.iterdir() if path.is_dir()}
    if plugin_names != catalog_names:
        missing = sorted(catalog_names - plugin_names)
        extra = sorted(plugin_names - catalog_names)
        if missing:
            errors.append(f"{skills_dir.relative_to(ROOT)} is missing: {', '.join(missing)}")
        if extra:
            errors.append(f"{skills_dir.relative_to(ROOT)} has unknown skills: {', '.join(extra)}")

    for skill_name in sorted(catalog_names & plugin_names):
        skill_file = skills_dir / skill_name / "SKILL.md"
        manifest_file = skills_dir / skill_name / "manifest.json"
        if not skill_file.exists():
            errors.append(f"{skill_file.relative_to(ROOT)} is missing")
        if not manifest_file.exists():
            errors.append(f"{manifest_file.relative_to(ROOT)} is missing")


def check_generated_packaging(catalog_names: set[str], errors: list[str]) -> None:
    check_json_name(ROOT / "plugin.json", CATALOG_NAME, errors)
    check_json_name(ROOT / "package.json", CATALOG_NAME, errors)
    check_json_name(ROOT / "gemini-extension.json", CATALOG_NAME, errors)
    check_json_name(ROOT / ".claude-plugin" / "plugin.json", CATALOG_NAME, errors)
    check_json_name(ROOT / ".cursor-plugin" / "plugin.json", CATALOG_NAME, errors)

    check_plugin_skills(ROOT / ".claude-plugin", catalog_names, errors)
    check_plugin_skills(ROOT / ".cursor-plugin", catalog_names, errors)

    gemini_context = ROOT / "GEMINI.md"
    gemini_project_context = ROOT / ".gemini" / "GEMINI.md"
    vscode_instructions = (
        ROOT / ".github" / "instructions" / f"{CATALOG_NAME}.instructions.md"
    )
    if not gemini_context.exists():
        errors.append(f"Missing {gemini_context.relative_to(ROOT)}")
    if not gemini_project_context.exists():
        errors.append(f"Missing {gemini_project_context.relative_to(ROOT)}")
    if not vscode_instructions.exists():
        errors.append(f"Missing {vscode_instructions.relative_to(ROOT)}")

    generated_paths = [
        ROOT / "plugin.json",
        ROOT / "package.json",
        ROOT / "gemini-extension.json",
        ROOT / ".claude-plugin" / "plugin.json",
        ROOT / ".cursor-plugin" / "plugin.json",
        gemini_context,
        gemini_project_context,
        vscode_instructions,
    ]
    for path in generated_paths:
        check_white_label(path, errors)


def main() -> int:
    errors: list[str] = []
    catalog_path = ROOT / "skills.json"
    skills_dir = ROOT / "skills"

    if not catalog_path.exists():
        errors.append("Missing skills.json")
    if not skills_dir.exists():
        errors.append("Missing skills/ directory")

    catalog = json.loads(catalog_path.read_text(encoding="utf-8")) if catalog_path.exists() else {}
    catalog_names = {skill.get("name") for skill in catalog.get("skills", [])}

    for skill_dir in sorted(path for path in skills_dir.iterdir() if path.is_dir()):
        skill_file = skill_dir / "SKILL.md"
        manifest_file = skill_dir / "manifest.json"
        if not skill_file.exists():
            errors.append(f"{skill_dir.relative_to(ROOT)} is missing SKILL.md")
            continue
        if not manifest_file.exists():
            errors.append(f"{skill_dir.relative_to(ROOT)} is missing manifest.json")
            continue

        frontmatter = load_frontmatter(skill_file)
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
        name = str(frontmatter.get("name") or "")

        if not NAME_PATTERN.match(name):
            errors.append(f"{skill_file.relative_to(ROOT)} has invalid skill name: {name}")
        if not str(frontmatter.get("description") or "").strip():
            errors.append(f"{skill_file.relative_to(ROOT)} is missing description")
        if manifest.get("name") != name:
            errors.append(f"{manifest_file.relative_to(ROOT)} name does not match SKILL.md")
        if name not in catalog_names:
            errors.append(f"{name} is missing from skills.json")
        if manifest.get("side_effects") not in {"read-only", "mutating"}:
            errors.append(f"{manifest_file.relative_to(ROOT)} has invalid side_effects")

        check_white_label(skill_file, errors)
        check_white_label(manifest_file, errors)

    check_white_label(catalog_path, errors)
    check_white_label(ROOT / "README.md", errors)
    check_generated_packaging(catalog_names, errors)

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validation passed for {len(catalog_names)} skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
