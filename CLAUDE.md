# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Language Preferences

- **Git-tracked files**: Must use English (code, comments, commit messages, documentation, SKILL.md, README.md, etc.)
- **Conversation and temporary files**: Prefer Chinese (SPEC-*.md, TASK-*.md, plans, session notes)

## Repository Overview

cc-deck is a collection of Claude Code plugins providing developer workflow automation capabilities.

## Architecture

```
cc-deck/
├── plugins/
│   └── deck/                    # Git workflow plugin
│       ├── .claude-plugin/      # Plugin metadata
│       └── skills/              # SKILL.md files define Claude behaviors
│           ├── ci/              # Git commit skill
│           ├── pr/              # GitHub PR creation skill
│           └── spec/            # Spec-based development workflow
```

### Plugin Structure

Each plugin follows Claude Code's plugin format:
- `.claude-plugin/plugin.json` - Plugin metadata (name, version, description)
- `skills/<name>/SKILL.md` - Skill definition with YAML frontmatter and instructions

### Skill Definition Format

SKILL.md files use YAML frontmatter:
```yaml
---
name: skill-name
description: Brief description
argument-hint: 'usage hints'
allowed-tools: Tool1, Tool2, Bash(cmd:*)
---
```

The `allowed-tools` field restricts which tools the skill can use. Bash patterns like `Bash(git:*)` allow specific command prefixes.

## Plugin Details

### deck Plugin

Markdown-only skills that orchestrate git/GitHub workflows:
- `/deck:ci` - Commit with lint checking (no push)
- `/deck:pr` - Full PR workflow (lint, commit, push, create PR via `gh`)
- `/deck:spec` - Spec-based development with interview → spec → task list → execution

Spec skill modes:
- Interview mode: Generate SPEC-{slug}.md
- Import mode: Convert Claude Code plan files to SPEC format
- Run mode: Batch execute all tasks via subagents

## Development

### Adding a New Skill

1. Create `plugins/<plugin>/skills/<skill>/SKILL.md`
2. Define YAML frontmatter with name, description, allowed-tools
3. Write instructions in markdown body
4. Skills can include `references/` directories for templates and supporting files

### Version Management

- When modifying plugin content (skills, code, or config), bump the version in the corresponding `.claude-plugin/plugin.json`
- Follow semver: patch for fixes, minor for new features/enhancements, major for breaking changes

### Adding or Removing a Plugin

When adding or removing a plugin, update **all** registry and documentation files:
- `.claude-plugin/marketplace.json` — the marketplace plugin registry (controls what users see during installation)
- `README.md` — plugin table and installation instructions
- `CLAUDE.md` — architecture diagram and plugin details

### Plugin Installation (for users)

```bash
claude plugin marketplace add darknight/cc-deck
claude plugin install deck@cc-deck
```

## Dependencies

- GitHub CLI (`gh`) - Required for PR creation
