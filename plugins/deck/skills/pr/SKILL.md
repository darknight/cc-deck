---
name: pr
description: Create GitHub PR
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git push:*), Bash(gh:*)
---

## Quick Reference
```
/pr                 # Create GitHub PR (auto lint, commit, push)
```

Current changes are good enough, now you need to commit & create github PR.

First, you need to check current branch, if you find we are on the `main` branch, please checkout a new one.

If you see untracked files, please ignore them, you focus on changed files which are already tracked in git.

Then, you need to run lint checking to make sure the lint check pass. If necessary, format the changed code before committing the changes.

For the the commit message, it should be just one line, and do not add co-author info with any claude brand.

Then you should generate succinct pr description, it should be self-explained and easy to read and understand.

Last, you use `gh` cli to raise a PR on github with title following `Conventional Commits` pattern with above generated description.

Be aware that the base branch should be `main` by default.

In the end, show me the pr link.
