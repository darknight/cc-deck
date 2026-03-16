---
name: spec
description: "Turn ideas into structured specs and execute them — conduct interviews to refine requirements, import existing plans, or run task lists via subagents. Use whenever starting a feature, planning implementation, or managing task execution."
argument-hint: '["idea" | @file | run @SPEC-*.md | import @plan-file.md]'
allowed-tools: Read, Write, AskUserQuestion, Glob, Bash(mkdir:*), Bash(date:*), Task, ExitPlanMode
---

## Quick Reference
```
/spec "idea"               # Start interview from idea description
/spec @file.md             # Start interview from file content
/spec run @SPEC-*.md       # Execute tasks in specified SPEC file
/spec import @plan.md      # Import Claude Code plan file to SPEC format
```

# Spec Skill - Requirements Refinement & Task Execution

Route to the appropriate mode based on `$ARGUMENTS`:

## Mode Routing

### 1. Run Mode
**Trigger**: `$ARGUMENTS` starts with `run`
**Example**: `run @SPEC-user-auth.md`
**Required**: Must specify a SPEC file. If not provided, prompt user to specify one.

### 2. Import Mode
**Trigger**: `$ARGUMENTS` starts with `import`
**Example**: `import @plan.md`
**Required**: Must specify a plan file to import.

### 3. Interview Mode (Default)
**Trigger**: All other cases
- `@file` - Start from file content
- Plain text - Start from idea description

---

## Mode 1: Interview Mode

### Input Handling
- **Idea mode**: Use text from `$ARGUMENTS` directly
- **File mode**: Read file content as starting point

### Interview Process

Conduct adaptive interviews using AskUserQuestion. No fixed rounds — continue until the user signals completion.

**Core Principles**:
- Ask 1-3 focused questions per round
- Dig deep rather than staying surface-level
- Challenge assumptions and explore alternatives
- Before each round, briefly summarize what has been collected so far

**Topic Areas to Explore** (adapt order and depth based on context):
- Problem definition and success criteria
- Target users and their needs
- Technical constraints and integration points
- User experience and interaction patterns
- Risks, tradeoffs, and scope boundaries
- Dependencies and open questions

### Slug Generation

Generate a short English slug: lowercase, hyphen-separated, 2-4 words (e.g., `user-auth`, `dark-mode`, `api-rate-limit`).

### Plan Mode Handling

If plan mode is currently active, call ExitPlanMode before generating the SPEC file. The spec interview process itself serves as the planning phase — the SPEC document is the deliverable, not a plan file.

### Output File

Ensure directory exists, then generate **SPEC-{slug}.md** using the template in `references/spec-template.md`. Adapt sections based on the interview — omit sections that are not relevant, expand those that are.

---

## Mode 2: Import Mode

Import a Claude Code plan file and convert it to SPEC format for subagent execution. This enables isolated execution of each task with fresh context, avoiding context window overflow.

### Execution Flow

1. **Read plan file** — Parse the specified file
2. **Extract content** — Title from first heading, background from pre-task text, tasks from checkbox/numbered items
3. **Generate slug** — Derive from title or ask user
4. **Convert to SPEC format** — Create SPEC-{slug}.md with requirements, task list, and empty execution log
5. **Save and confirm** — Write to `./plans/SPEC-{slug}.md` and show summary

### Task Conversion Rules

| Plan Format | SPEC Format |
|-------------|-------------|
| `- [ ] Task` | ⬜ Pending |
| `- [x] Task` | ✅ Completed |
| `1. Task` | ⬜ Pending |
| Nested items | Merged into Notes column |

---

## Mode 3: Run Mode

Execute tasks sequentially using subagents. Main context handles scheduling and progress tracking only.

### Execution Flow

#### Phase 1: Parse and Plan

1. **Locate SPEC file** — Must be specified in the command. If missing, prompt user.
2. **Parse tasks** — Extract all tasks, identify status (⬜/🔄/✅), count pending.
3. **Display execution plan** — Show task table with status. Ask user to confirm before proceeding.

#### Phase 2: Sequential Execution

For each pending task in order:

1. **Update status** — Change to 🔄, write file immediately.
2. **Execute via subagent** — Use Task tool with task description, acceptance criteria, and relevant spec context.
3. **Handle result**:
   - **Success**: Update to ✅, add timestamp, update progress count and `last-updated`
   - **Failure**: Keep as 🔄, stop execution immediately, display error report with recovery instructions
4. **Report progress** — Show completion status after each task.

### Error Handling

On failure, stop and report: which task failed, error details, current progress, and how to retry (`/spec run @SPEC-xxx.md` resumes from the failed task).

---

## Guidelines

### File Handling
- If file exists, ask user: Overwrite / Use new slug / Cancel
- Auto-create directory if it doesn't exist
- Single SPEC file contains both requirements and tasks

### Task Table Format
- Use table format for all tasks
- Status icons: ⬜ Pending | 🔄 In Progress | ✅ Completed
- Include acceptance criteria in Notes column
