---
name: pr
description: Create GitHub PR
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git diff:*), Bash(git commit:*), Bash(git push:*), Bash(git checkout:*), Bash(gh:*), Bash(npm run:*), Bash(npx:*), Bash(pnpm:*), Bash(bun run:*), Bash(cargo fmt:*), Bash(cargo clippy:*)
---

## Quick Reference
```
/pr                 # Create GitHub PR (auto lint, commit, push)
```

## Workflow

Follow these steps strictly in order:

1. **Check branch**: If on `main`, checkout a new branch.

2. **Check status**: Run `git status`. Ignore untracked files — focus on tracked changes only.

3. **Format and re-stage**: Run lint/format tools on the changed files. After formatting, you MUST immediately run `git add` on every file that was formatted. Never skip this — formatting modifies files that were already staged, and those modifications will be lost from the commit if not re-staged.

4. **Verify staging**: Run `git diff` (without --cached) to check for unstaged changes. If any output appears, run `git add` on them. Only continue when `git diff` produces no output.

5. **Commit**: Create the commit. One-line message, no co-author info.

6. **Create PR**: Generate a succinct, self-explanatory PR description. Use `gh` cli to create the PR with title following `Conventional Commits` pattern. Base branch is `main`.

7. **Show PR link**: Display the PR URL.
