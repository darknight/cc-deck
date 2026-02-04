---
name: ci
description: Commit staged changes to git
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*)
---

## Quick Reference
```
/ci                 # Commit current changes to git
```

If there are untracked files, ask user if they want to add them to the commit.
You should provide options to add all, add none, or specify individual files to add.

You need to run lint checking to make sure the lint check pass. If necessary, format the changed code before committing the changes.

Then you add all changed files as staged changes.

You should commit changes only, do NOT push to remote github.

The commit message should be short, succinct.

The commit author should be current github user, do not co-author with anthropic or claude code.
