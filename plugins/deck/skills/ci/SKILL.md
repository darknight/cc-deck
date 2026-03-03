---
name: ci
description: Commit changes to git with auto-formatting
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git diff:*), Bash(git commit:*), Bash(npm run:*), Bash(npx:*), Bash(pnpm:*), Bash(bun run:*), Bash(cargo fmt:*), Bash(cargo clippy:*)
---

## Quick Reference
```
/ci                 # Commit current changes to git
```

## Critical Constraint

This skill MUST produce EXACTLY ONE commit — never two. The single commit includes both the original code changes AND any formatting fixes. If you run `git commit` before the formatter runs, you have violated this constraint and there is no recovery.

## Workflow

Follow these steps strictly in order. Do NOT skip or reorder steps. Do NOT run `git commit` until Step 4.

### Step 1: Snapshot the working directory

Run `git status` to understand the current state. Note whether there are already-staged files ("Changes to be committed") or not. You will need this in Step 3.

**Do NOT run `git add` or `git commit` in this step.** Only observe.

### Step 2: Format all changed files

Run the project's lint/format tools on all modified tracked files (both staged and unstaged). Detect the formatter from project config:

- `package.json` with format/lint scripts → run the appropriate script
- `biome.json` / `biome.jsonc` → `npx biome check --write`
- `.prettierrc*` → `npx prettier --write`
- `Cargo.toml` → `cargo fmt`

If no formatter is detected, skip this step.

**Do NOT run `git add` or `git commit` in this step.** Only format files.

### Step 3: Stage changes

Based on what you observed in Step 1, follow exactly ONE of the two cases:

**Case A — Staged files already existed in Step 1** (status showed "Changes to be committed"):

The user deliberately staged files. Respect their choices:
1. Run `git diff --cached --name-only` to get the list of staged files.
2. Run `git add` on those same files again. This captures any formatting modifications made in Step 2.
3. Do NOT add any other files. Do NOT ask about untracked files.

**Case B — No staged files existed in Step 1** (status showed NO "Changes to be committed"):

1. Run `git add` on all modified tracked files (everything under "Changes not staged for commit").
2. If there are untracked files, ask the user how to handle them:
   - Add all untracked files
   - Add none of them
   - Specify which files to add

After staging, run `git status` to confirm there are staged changes. If nothing is staged, tell the user and stop.

**Do NOT run `git commit` in this step.** Only stage files.

### Step 4: Commit

Run `git diff --cached --stat` to review what will be committed, then create the commit. Do NOT push to remote.

## Rules

- **ONE COMMIT ONLY**: This skill must produce exactly one commit. Never create a second commit for any reason.
- The commit message must be in concise English.
- The commit message describes the code change purpose (e.g., `feat:`, `fix:`, `refactor:`), NOT the formatting. Even if the formatter modified files, do not use a `style:` prefix.
- Do NOT run `git commit` until Steps 1–3 are complete.
- Do NOT push to remote.

## Common Mistake

Do NOT follow this wrong order:
1. ~~Stage changes~~ → 2. ~~Commit~~ → 3. ~~Run formatter~~ → 4. ~~Commit formatting fixes~~

That creates two commits. Always format BEFORE staging and committing.
