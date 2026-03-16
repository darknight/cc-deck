---
name: pr
description: "Create a GitHub pull request — pushes the current branch and opens a PR with auto-generated title and description. Use for any PR creation, branch submission, or code review request."
allowed-tools: Bash(git status:*), Bash(git log:*), Bash(git push:*), Bash(git branch:*), Bash(git diff:*), Bash(gh:*)
---

## Quick Reference
```
/pr                 # Create GitHub PR from current branch
```

## Workflow

### Step 1: Check branch

Run `git branch --show-current`. If on `main`, tell the user they cannot create a PR from the main branch and stop.

Run `git log main..HEAD --oneline` to check for commits ahead of main. If there are no commits AND the working directory is clean, tell the user there is nothing to create a PR for and stop.

### Step 2: Check working directory

Run `git status` to check if the working directory is clean.

- **Clean**: Proceed to Step 3.
- **Dirty** (any staged, unstaged, or untracked changes): Ask the user:
  1. Commit changes first — suggest using `/ci`, then stop and let the user run it.
  2. Ignore local changes and continue creating the PR based on existing commits only.

### Step 3: Push and create PR

1. Run `git push -u origin HEAD` to push the branch.
2. Run `git log main..HEAD` to analyze all commits on this branch. Generate a succinct, self-explanatory PR description from them.
3. Run `gh pr create` with a title following `Conventional Commits` pattern. Base branch is `main`.

### Step 4: Request review agents

After the PR is created, automatically request code review from available review agents:

1. Run `gh pr edit --add-reviewer @copilot` to request Copilot code review.
2. If the command succeeds, note that Copilot review has been requested.
3. If it fails (e.g., Copilot not available for the repo), skip silently and continue.

### Step 5: Show result

Display the PR URL to the user, along with the review request status.

## Rules

- This skill only creates PRs. It does not format, stage, or commit code.
- The PR title must follow Conventional Commits pattern (e.g., `feat:`, `fix:`, `refactor:`).
- If a PR already exists for this branch, display the existing PR URL instead of creating a new one.
