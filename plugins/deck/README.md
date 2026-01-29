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
| `/deck:plan` | Add a plan markdown file under `./plans` folder |
| `/deck:pickup <file>` | Pick up a task from a markdown file in `./plans` folder |
| `/deck:spec` | Interview user to refine a spec through in-depth Q&A |

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

### Save a Plan
```
/deck:plan
```
Saves your proposal to a `PLAN-*.md` file in the `./plans` folder.

### Pick up a task
```
/deck:pickup plans/PLAN-feature.md
```
Reads the specified task file and applies it to the current project.

### Refine a Spec
```
/deck:spec @docs/SPEC-feature.md
```
Interviews you in-depth about your spec using AskUserQuestion tool:
- Technical implementation details
- UI & UX considerations
- Edge cases, tradeoffs, and risks

Continue until the spec is complete, then writes the refined spec back to the file.

## Requirements

- [Claude Code CLI](https://github.com/anthropics/claude-code)
- [GitHub CLI (`gh`)](https://cli.github.com/) - for PR creation

## Credits

- The `/deck:spec` skill is inspired by [@trq212](https://x.com/trq212)'s [tweet](https://x.com/trq212/status/2005315275026260309) on spec-based development workflow with Claude Code.

## License

Apache-2.0
