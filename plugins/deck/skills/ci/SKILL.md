---
name: ci
description: Commit staged changes to git
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
---

## Quick Reference
```
/ci                 # Commit current changes to git
```

## Workflow

Follow these steps in order:

1. **Check status**: Run `git status` to identify staged, unstaged, and untracked files.

2. **Handle untracked files**: If there are untracked files, ask user if they want to add them to the commit. Provide options to add all, add none, or specify individual files to add.

3. **Run lint/format**: Run lint checking on the staged files. If necessary, format the changed code to make the lint check pass.

4. **Re-stage all changes**: After formatting, run `git add` on all previously staged files again so that formatting changes are included. This is critical — formatting may modify files that were already staged, and those modifications must be re-staged before committing.

5. **Commit**: Create the commit. Do NOT push to remote github.

## Rules

- The commit message must be in concise English.
