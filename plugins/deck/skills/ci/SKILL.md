---
name: ci
description: "Commit code changes to git with auto-formatting and smart staging. Use this for any git commit workflow — handles formatter detection, selective staging, and commit message generation in a single atomic commit."
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git diff:*), Bash(git commit:*), Bash(npm run:*), Bash(npx:*), Bash(pnpm:*), Bash(bun run:*), Bash(cargo fmt:*), Bash(cargo clippy:*), Bash(yarn:*)
---

## Quick Reference
```
/ci                 # Commit current changes to git
```

## Workflow

Formatting is part of the code change, not a separate concern — format before staging so everything lands in one commit.

### Step 1: Snapshot the working directory

Run `git status` to understand the current state. Note whether there are already-staged files ("Changes to be committed") or not. You will need this in Step 3.

Only observe — do not stage or commit yet.

### Step 2: Format all changed files

Run the project's lint/format tools on all modified tracked files (both staged and unstaged). Detect the formatter from project config:

- `package.json` with format/lint scripts → run the appropriate script
- `biome.json` / `biome.jsonc` → `npx biome check --write`
- `.prettierrc*` → `npx prettier --write`
- `Cargo.toml` → `cargo fmt`

If no formatter is detected, skip this step. Do not stage or commit yet.

### Step 3: Stage changes

Based on what you observed in Step 1, follow exactly ONE of the two cases:

**Case A — Staged files already existed in Step 1** (status showed "Changes to be committed"):

The user deliberately staged files. Respect their choices:
1. Run `git diff --cached --name-only` to get the list of staged files.
2. Run `git add` on those same files again. This captures any formatting modifications made in Step 2.
3. Do not add any other files.

**Case B — No staged files existed in Step 1** (status showed NO "Changes to be committed"):

1. Run `git add` on all modified tracked files (everything under "Changes not staged for commit").
2. If there are untracked files, ask the user how to handle them:
   - Add all untracked files
   - Add none of them
   - Specify which files to add

After staging, run `git status` to confirm there are staged changes. If nothing is staged, tell the user and stop.

### Step 4: Commit

Run `git diff --cached --stat` to review what will be committed, then create the commit.

## Rules

- This skill produces exactly one commit — formatting and code changes together. Always format before staging.
- The commit message describes the code change purpose (e.g., `feat:`, `fix:`, `refactor:`), not the formatting.
- This skill handles commit only; pushing is the PR skill's job.
