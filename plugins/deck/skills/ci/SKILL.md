---
name: ci
description: Commit changes to git with auto-formatting
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git diff:*), Bash(git commit:*), Bash(npm run:*), Bash(npx:*), Bash(pnpm:*), Bash(bun run:*), Bash(cargo fmt:*), Bash(cargo clippy:*)
---

## Quick Reference
```
/ci                 # Commit current changes to git
```

## Workflow

Follow these steps strictly in order. Do NOT skip or reorder steps.

### Step 1: Format all changed files

Run the project's lint/format tools on all modified tracked files (both staged and unstaged). Detect the formatter from project config:

- `package.json` with format/lint scripts → run the appropriate script
- `biome.json` / `biome.jsonc` → `npx biome check --write`
- `.prettierrc*` → `npx prettier --write`
- `Cargo.toml` → `cargo fmt`

If no formatter is detected, skip this step.

**Do NOT run `git add` in this step.** Only format files.

### Step 2: Check status and stage

Run `git status` and follow exactly ONE of the two cases:

**Case A — Staged files already exist** (output shows "Changes to be committed"):

The user deliberately staged files. Respect their choices:
1. Run `git diff --cached --name-only` to get the list of staged files.
2. Run `git add` on those same files again. This captures any formatting modifications made in Step 1.
3. Do NOT add any other files. Do NOT ask about untracked files.

**Case B — No staged files** (output shows NO "Changes to be committed"):

1. Run `git add` on all modified tracked files (everything under "Changes not staged for commit").
2. If there are untracked files, ask the user how to handle them:
   - Add all untracked files
   - Add none of them
   - Specify which files to add

### Step 3: Pre-commit check

Run `git status` to confirm there are staged changes. If nothing is staged, tell the user and stop.

### Step 4: Commit

Run `git diff --cached --stat` to review what will be committed, then create the commit. Do NOT push to remote.

## Rules

- The commit message must be in concise English.
