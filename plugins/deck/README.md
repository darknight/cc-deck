# cc-deck

A developer's skill deck for Claude Code - streamlined workflows for git commits, PRs, and task management.

## Installation

### Option 1: Marketplace (in Claude Code)

```
/plugin marketplace add darknight/cc-deck
/plugin install deck@cc-deck
```

### Option 2: CLI (in Terminal)

```bash
claude plugin marketplace add darknight/cc-deck
claude plugin install deck@cc-deck
```

### Option 3: Manual Installation

Clone and install locally:

```bash
git clone https://github.com/darknight/cc-deck.git
claude plugin add /path/to/cc-deck
```

## Skills

After installation, you can use the following skills with the `deck:` namespace:

| Skill | Description |
|-------|-------------|
| `/deck:ci` | Commit staged changes to git (runs lint, stages changes, commits) |
| `/deck:pr` | Create a GitHub PR (commit, push, and create PR with `gh` CLI) |
| `/deck:spec` | Interview to refine ideas into specs, generate task lists, and execute with progress tracking |

## Usage Examples

### Commit changes
```
/deck:ci
```
This will:
1. Run lint checks
2. Stage all tracked changes
3. Create a commit with a concise message

### Create a Pull Request
```
/deck:pr
```
This will:
1. Check if on `main` branch (creates new branch if needed)
2. Run lint checks
3. Commit changes
4. Push to remote
5. Create PR using `gh` CLI with Conventional Commits format

### Spec Workflow

#### Start from an idea
```
/deck:spec "implement user authentication"
```
Interviews you in-depth, then generates:
- `SPEC-user-auth.md` - detailed requirements spec
- `TASK-user-auth.md` - task list with progress tracking

#### Start from existing file
```
/deck:spec @docs/idea.md
```
Uses the file content as starting point for the interview.

#### Execute tasks with progress tracking
```
/deck:spec apply @TASK-user-auth.md
```
Picks up the next pending task, executes it, and automatically updates progress.

#### List all specs and tasks
```
/deck:spec list
```
Shows all SPEC and TASK files with their progress status.

#### Custom output directory
```
/deck:spec "my idea" --dir ./docs/specs
```
Saves generated files to the specified directory (default: `./plans`).

## Requirements

- [Claude Code CLI](https://github.com/anthropics/claude-code)
- [GitHub CLI (`gh`)](https://cli.github.com/) - for PR creation

## Credits

- The `/deck:spec` skill is inspired by [@trq212](https://x.com/trq212)'s [tweet](https://x.com/trq212/status/2005315275026260309) on spec-based development workflow with Claude Code.

## License

Apache-2.0
