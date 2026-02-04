# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Language Preferences

- **Git-tracked files**: Must use English (code, comments, commit messages, documentation, SKILL.md, README.md, etc.)
- **Conversation and temporary files**: Prefer Chinese (SPEC-*.md, TASK-*.md, plans, session notes)

## Repository Overview

cc-deck is a collection of Claude Code plugins providing developer workflow automation and RSS management capabilities.

## Architecture

```
cc-deck/
├── plugins/
│   ├── deck/                    # Git workflow plugin
│   │   ├── .claude-plugin/      # Plugin metadata
│   │   └── skills/              # SKILL.md files define Claude behaviors
│   │       ├── ci/              # Git commit skill
│   │       ├── pr/              # GitHub PR creation skill
│   │       └── spec/            # Spec-based development workflow
│   └── freshrss/                # RSS reading assistant plugin
│       ├── .claude-plugin/      # Plugin metadata
│       └── skills/freshrss/     # Python CLI for FreshRSS API
│           ├── run.py           # CLI entry point
│           └── lib/             # Core modules
│               ├── client.py    # FreshRSS Google Reader API client
│               ├── credentials.py # System keychain integration
│               └── fetcher.py   # Article content fetcher (static/dynamic)
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
- Interview mode: Generate SPEC-{slug}.md and TASK-{slug}.md
- Apply mode: Execute single task from TASK file
- Run mode: Batch execute all tasks via subagents
- List mode: Show all spec/task files with progress

### freshrss Plugin

Python-based skill using `uv` for dependency management:
- Commands: `setup`, `unread`, `article`, `fetch`, `read`, `subs`
- Digest mode: Batch fetch full content for Claude summarization
- Credentials stored in system keychain (macOS: `security`, Linux: `secret-tool`)

Run commands from skill directory:
```bash
cd plugins/freshrss/skills/freshrss && uv run python run.py <command>
```

## Development

### Adding a New Skill

1. Create `plugins/<plugin>/skills/<skill>/SKILL.md`
2. Define YAML frontmatter with name, description, allowed-tools
3. Write instructions in markdown body
4. For Python skills, use `uv` for dependency management

### Plugin Installation (for users)

```bash
claude plugin marketplace add darknight/cc-deck
claude plugin install deck@cc-deck
claude plugin install freshrss@cc-deck
```

## Dependencies

- GitHub CLI (`gh`) - Required for PR creation
- Python 3.10+ with `uv` - For freshrss plugin
- Playwright with Chromium - For dynamic content fetching (optional)
