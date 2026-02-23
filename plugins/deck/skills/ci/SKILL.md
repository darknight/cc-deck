---
name: ci
description: Commit staged changes to git
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git diff:*), Bash(git commit:*), Bash(npm run:*), Bash(npx:*), Bash(pnpm:*), Bash(bun run:*), Bash(cargo fmt:*), Bash(cargo clippy:*)
---

## Quick Reference
```
/ci                 # Commit current changes to git
```

## Workflow

Follow these steps strictly in order:

1. **Check status**: Run `git status` to identify staged, unstaged, and untracked files.

2. **Handle untracked files**: If there are untracked files, ask user if they want to add them to the commit. Provide options to add all, add none, or specify individual files to add.

3. **Format and re-stage**: Run lint/format tools on the staged files. After formatting, you MUST immediately run `git add` on every file that was formatted. Never skip this — formatting modifies files that were already staged, and those modifications will be lost from the commit if not re-staged.

4. **Verify staging**: Run `git diff` (without --cached) to check for unstaged changes. If any output appears, those changes are NOT yet staged — run `git add` on them before proceeding. Only continue when `git diff` produces no output.

5. **Commit**: Create the commit. Do NOT push to remote.

## Rules

- The commit message must be in concise English.
