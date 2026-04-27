# Public API MCP Skills

White-label AI agent skills for commerce, membership, and community MCP workflows.

This folder is designed to be self-contained so it can be published as its own
GitHub repository. Users can install it through agent-tool plugin flows where
supported, or clone it and install the skill folders locally.

## What's Included

- `skills/` contains one portable skill package per directory.
- `skills.json` is the catalog manifest for discovery and marketplace indexing.
- Each skill includes a `SKILL.md` file and a `manifest.json` file.
- `plugin.json`, `gemini-extension.json`, and `package.json` expose the repo as
  a plugin/source package for compatible agent tools.
- `.claude-plugin/` and `.cursor-plugin/` contain generated plugin packages.
- `GEMINI.md`, `.gemini/GEMINI.md`, and `.github/instructions/` contain
  generated instruction bundles for Gemini CLI and VS Code/Copilot.
- `scripts/build.py` regenerates all plugin packaging from `skills/`.
- `scripts/install.py` installs skills for Claude Code, Cursor, Gemini CLI,
  VS Code/Copilot, or a custom skill directory.
- `scripts/validate.py` checks package structure and white-label constraints.

## Requirements

These skills assume the user's agent has access to an MCP server exposing the
tool names referenced by each skill, such as `shop_list_orders`,
`shop_list_products`, or `classic_create_push_broadcast`.

The skills do not require a specific MCP server URL. Configure the MCP server in
the target IDE, then install these skills as agent instructions.

## Install From GitHub

When an agent tool supports installing plugins or extensions directly from a
GitHub URL, use the URL of this repository after it has been published.

For Gemini CLI:

```bash
gemini extensions install https://github.com/<owner>/<repo>
```

For VS Code/Copilot, use the command palette action to install a chat plugin
from source, then paste this repository URL.

For local installation:

```bash
git clone <github-url>
cd public-api-mcp-skills
python scripts/install.py --target cursor
```

Install into multiple supported tools at once:

```bash
python scripts/install.py --target claude-code,cursor,gemini-cli --force
```

For a project-local install, pass the project root:

```bash
python scripts/install.py --target cursor,claude-code,gemini-cli,vscode --project /path/to/project
```

Supported targets:

- `claude-code`: copies skill packages to `~/.claude/skills`, or
  `<project>/.claude/skills` with `--project`.
- `cursor`: copies skill packages to `~/.cursor/skills`, or
  `<project>/.cursor/skills` with `--project`.
- `gemini-cli`: creates a Gemini CLI extension in
  `~/.gemini/extensions/public-api-mcp-skills`, or under
  `<project>/.gemini/extensions/` with `--project`.
- `vscode`: writes a Copilot instruction file to
  `<project>/.github/instructions/public-api-mcp-skills.instructions.md`.

For other IDEs, install the raw skill folders into any directory:

```bash
python scripts/install.py --target-dir /path/to/skills
```

For backwards compatibility, `--target /path/to/skills` also installs raw skill
folders into that directory. Each package is a directory containing a `SKILL.md`
file.

## Build Generated Plugin Files

The skill folders are the source of truth. After adding, removing, or renaming a
skill, regenerate the platform packaging:

```bash
python scripts/build.py
```

This updates:

- `.claude-plugin/skills/`
- `.cursor-plugin/skills/`
- `GEMINI.md`
- `.gemini/GEMINI.md`
- `.github/instructions/public-api-mcp-skills.instructions.md`
- `plugin.json`
- `gemini-extension.json`
- `package.json`

## Catalog Format

`skills.json` lists all packages:

```json
{
  "name": "public-api-mcp-skills",
  "version": "0.1.0",
  "skills_directory": "skills",
  "skills": [
    {
      "name": "shop-best-sellers",
      "path": "skills/shop-best-sellers/SKILL.md",
      "side_effects": "read-only",
      "required_mcp_tools": ["shop_list_orders", "shop_list_products"]
    }
  ]
}
```

Marketplaces can read this manifest to list skills, inspect required MCP tools,
and distinguish read-only skills from skills that can mutate data.

## Safety Model

Skills declare one of two side-effect levels in `manifest.json`:

- `read-only`: reports, audits, rankings, and diagnostics.
- `mutating`: creates, updates, grants, sends, or launches something.

Mutating skills must ask for explicit user confirmation before executing an
action through MCP tools.

## Publishing Checklist

Before publishing or tagging a release:

```bash
python scripts/validate.py
```

Then verify:

- Skill names are lowercase, hyphenated, and stable.
- No user-facing text contains private brand names or internal domains.
- Every skill states its required MCP tools.
- Mutating skills include explicit confirmation rules.
- The catalog version and release tag match.

## Versioning

Use semantic versions for the catalog:

- Patch: copy edits, documentation, wording clarifications.
- Minor: new skills or new optional fields.
- Major: renamed skills, removed skills, or incompatible manifest changes.
