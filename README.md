# cc-deck

A developer's command deck for Claude Code - streamlined workflows for git commits, PRs, and task management.

## Installation

### Manual Installation

Clone this repository and install as a Claude Code plugin:

```bash
git clone https://github.com/anthropics/cc-deck.git
claude plugin add /path/to/cc-deck
```

Or install directly from a local directory:

```bash
claude plugin add /path/to/cc-deck
```

## Commands

After installation, you can use the following commands with the `ccdeck:` namespace:

| Command | Description |
|---------|-------------|
| `/ccdeck:ci` | Commit staged changes to git (runs lint, stages changes, commits) |
| `/ccdeck:pr` | Create a GitHub PR (commit, push, and create PR with `gh` CLI) |
| `/ccdeck:plan` | Add a plan markdown file under `./docs` folder |
| `/ccdeck:pickup <file>` | Pick up a task from a markdown file in `./docs` folder |

## Usage Examples

### Commit changes
```
/ccdeck:ci
```
This will:
1. Run lint checks
2. Stage all tracked changes
3. Create a commit with a concise message

### Create a Pull Request
```
/ccdeck:pr
```
This will:
1. Check if on `main` branch (creates new branch if needed)
2. Run lint checks
3. Commit changes
4. Push to remote
5. Create PR using `gh` CLI with Conventional Commits format

### Save a Plan
```
/ccdeck:plan
```
Saves your proposal to a `PLAN-*.md` file in the `./docs` folder.

### Pick up a task
```
/ccdeck:pickup docs/PLAN-feature.md
```
Reads the specified task file and applies it to the current project.

## Requirements

- [Claude Code CLI](https://github.com/anthropics/claude-code)
- [GitHub CLI (`gh`)](https://cli.github.com/) - for PR creation

## License

MIT
