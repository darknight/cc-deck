---
name: spec
description: Interview to refine ideas into specs, generate task lists, and execute with progress tracking
argument-hint: '["idea" | @file | apply @TASK-*.md | run [@TASK-*.md] [--dry-run] | list | --dir path]'
allowed-tools: Read, Write, AskUserQuestion, Glob, Bash(mkdir:*), Bash(date:*), Task
---

## Quick Reference
```
/spec "idea"               # Start interview from idea description
/spec @file.md             # Start interview from file content
/spec apply @TASK-*.md     # Execute next task in task list
/spec run                  # Execute all tasks automatically (batch)
/spec run @TASK-*.md       # Execute all tasks in specific file
/spec run --dry-run        # Preview execution plan without running
/spec list                 # List all SPEC/TASK files with progress
/spec "idea" --dir ./docs  # Specify custom output directory
```

# Spec Skill - Requirements Refinement & Task Management

Route to the appropriate mode based on `$ARGUMENTS`:

## Mode Routing

### 1. Apply Mode
**Trigger**: `$ARGUMENTS` starts with `apply`
**Example**: `apply @TASK-user-auth.md`, `apply ./plans/TASK-xxx.md`

### 2. List Mode
**Trigger**: `$ARGUMENTS` equals `list`

### 3. File Interview Mode
**Trigger**: `$ARGUMENTS` starts with `@` or points to an existing file

### 4. Idea Interview Mode
**Trigger**: All other cases (plain text description)

### 5. Run Mode (Batch Execution)
**Trigger**: `$ARGUMENTS` starts with `run`
**Example**: `run`, `run @TASK-user-auth.md`, `run --dry-run`

### Parameter Parsing
- `--dir <path>`: Custom output directory, defaults to `./plans`
- Example: `/spec "idea" --dir ./docs/specs`

---

## Mode 1: Interview Mode

### Input Handling
- **Idea mode**: Use text from `$ARGUMENTS` directly
- **File mode**: Read file content as starting point

### Interview Process

Conduct in-depth interviews using AskUserQuestion, focusing on one topic per round:

**Round 1 - Core Requirements**
- What problem does this feature solve?
- Who are the target users?
- What are the success criteria?

**Round 2 - Technical Details**
- Any technical constraints or preferences?
- What existing systems need integration?
- Performance and security requirements?

**Round 3 - User Experience**
- How will users interact with this feature?
- Any UI/UX requirements?
- Error handling and edge cases?

**Round 4 - Risks & Tradeoffs**
- What are the potential risks?
- What tradeoffs are acceptable?
- What must be avoided?

**Subsequent Rounds**
- Dig deeper based on previous answers
- Challenge assumptions, explore alternatives
- No fixed number of rounds - continue until user says "enough" or "that's all"

### Slug Generation

Generate a short English slug based on the requirements:
- Lowercase letters, hyphen-separated
- 2-4 words
- Examples: `user-auth`, `dark-mode`, `api-rate-limit`

### Output Files

Ensure directory exists, then generate two files:

**SPEC-{slug}.md** - Requirements specification:
```markdown
---
title: {Title}
slug: {slug}
created: {YYYY-MM-DD}
status: draft
---

# {Title}

## Overview
{One paragraph describing the core purpose}

## Background
### Problem Statement
### Target Users
### Success Criteria

## Functional Requirements
### Core Features
### Non-functional Requirements

## Technical Design
### Architecture Overview
### Technology Choices
### Interface Design

## User Experience
### User Flow
### UI/UX Requirements

## Scope & Constraints
### In Scope
### Out of Scope
### Constraints

## Risks & Mitigation

## Dependencies

## Open Questions
```

**TASK-{slug}.md** - Task checklist:
```markdown
---
title: {Title}
slug: {slug}
spec: SPEC-{slug}.md
created: {YYYY-MM-DD}
last-updated: {YYYY-MM-DD HH:MM}
progress: 0/{N}
status: pending
---

# {Title} - Task List

> Related spec: [SPEC-{slug}.md](./SPEC-{slug}.md)

## Progress Overview

[░░░░░░░░░░] 0% (0/{N} tasks)

## Task List

### Phase 1: {Phase Name}

- [ ] **Task 1**: {Description}
  - Acceptance: {Completion criteria}

- [ ] **Task 2**: {Description}
  - Acceptance: {Completion criteria}

### Phase 2: {Phase Name}

...

## Execution Log

{Execution notes will be appended here}
```

---

## Mode 2: Apply Mode

### Execution Flow

1. **Read task file**
   - Parse YAML front matter
   - Identify all tasks and their status

2. **Select task**
   - Find the first incomplete `[ ]` task
   - If all complete, inform the user

3. **Execute task**
   - Perform the actual work as described
   - Mark as `[x]` when done

4. **Update file**
   - Update checkbox status
   - Update `progress` count
   - Update `last-updated` timestamp
   - Add completion note

### Update Format

```markdown
- [x] **Task 1**: Description
  - Acceptance: Completion criteria
  > Completed: 2024-01-15 14:30
```

### Progress Bar Update

```
[████░░░░░░] 40% (2/5 tasks)
```

---

## Mode 3: List Mode

### Execution Flow

1. Use Glob to search for `SPEC-*.md` and `TASK-*.md` in the directory
2. Read front matter from each TASK file
3. Display as table:

```markdown
| File | Title | Progress | Status | Last Updated |
|------|-------|----------|--------|--------------|
| TASK-user-auth.md | User Auth | 3/5 (60%) | in-progress | 2024-01-15 |
| TASK-dark-mode.md | Dark Mode | 5/5 (100%) | completed | 2024-01-14 |
```

---

## Mode 4: Run Mode (Batch Execution)

Execute all tasks in a TASK file automatically with isolated subagent per task.

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `@TASK-*.md` | Specific task file | Auto-discover in current directory |
| `--dry-run` | Preview plan without executing | false |

### Run vs Apply Comparison

| Feature | apply | run |
|---------|-------|-----|
| Scope | Single task | All tasks |
| Context | Accumulated | Fresh per task (subagent) |
| Error handling | Manual | Auto-stop + report |
| Use case | Review each step | Trusted batch processing |

### Execution Flow

#### Phase 1: Parse and Plan

1. **Read TASK file**
   - If no file specified, search for `TASK-*.md` in current directory
   - If multiple found, ask user to select

2. **Parse tasks**
   - Extract all tasks with their status
   - Identify dependencies (if `Depends:` field exists)
   - Build execution order (topological sort)

3. **Display execution plan**
   ```
   ## Execution Plan

   **File**: TASK-user-auth.md
   **Total Tasks**: 5
   **Already Completed**: 2
   **To Execute**: 3

   | Order | Task | Dependencies |
   |-------|------|--------------|
   | 1 | Implement login API | (task-2 ✅) |
   | 2 | Add auth middleware | (task-3) |
   | 3 | Write unit tests | (task-4) |

   Proceed with execution? [Y/n]
   ```

4. **If `--dry-run`**: Stop here after showing plan

#### Phase 2: Execute Loop

For each pending task in order:

1. **Pre-check**: Verify dependencies completed
2. **Display**: Show current task being executed
3. **Execute via subagent**:
   - Use Task tool to create isolated subagent
   - Pass full task description and acceptance criteria
   - Include relevant SPEC context
4. **Validate**: Check subagent result
5. **Update file immediately**:
   - Mark task as `[x]`
   - Add completion timestamp
   - Update `progress` in frontmatter
   - Update `last-updated` timestamp
6. **Report progress**: Show updated progress bar

### Progress Display

```
## Batch Execution Progress

[████░░░░░░] 40% (2/5 tasks)

| # | Task | Status |
|---|------|--------|
| 1 | Setup database schema | ✅ Done |
| 2 | Create user model | ✅ Done |
| 3 | Implement login API | 🔄 Running... |
| 4 | Add auth middleware | ⏳ Pending |
| 5 | Write unit tests | ⏳ Pending |

**Current Task**: Implement login API
```

### Error Handling

On task failure:

1. **Stop immediately** - Do not continue to next task
2. **Save state** - Update TASK file with current progress
3. **Display error report**:

```
## Execution Halted ❌

**Failed Task**: Task 3 - Implement login API
**Error Type**: Execution failure
**Details**:
[Error details from subagent]

**Current Progress**: 2/5 (40%)
**Completed**: Task 1, Task 2
**Pending**: Task 3, Task 4, Task 5

**Recovery Options**:
1. Fix the issue manually
2. Run `/spec run` again to continue from failed task
3. Use `/spec apply @TASK-xxx.md` to execute single task with more control
```

### Completion Report

```
## Execution Complete ✅

[██████████] 100% (5/5 tasks)

### Summary
- **Total Tasks**: 5
- **Completed**: 5
- **Failed**: 0

### Execution Log
| Task | Notes |
|------|-------|
| Setup database schema | Created 3 migration files |
| Create user model | - |
| Implement login API | Added JWT support |
| Add auth middleware | - |
| Write unit tests | 12 tests, all passing |

**TASK file updated**: TASK-user-auth.md
```

### Subagent Execution Details

When executing each task via Task tool:

1. **Create subagent prompt**:
   ```
   Execute the following task:

   **Task**: {task_description}
   **Acceptance Criteria**: {acceptance_criteria}
   **Related Spec**: {spec_content_summary}

   Complete this task and report the result.
   ```

2. **Subagent isolation benefits**:
   - Fresh context for each task
   - No accumulated state pollution
   - Clear task boundaries
   - Easier debugging on failure

---

## Important Guidelines

### Interview Principles
- Ask deep, insightful questions - avoid surface-level ones
- 1-3 related questions per round
- Adapt subsequent questions based on answers
- No preset number of rounds

### File Handling
- If file exists, ask user: Overwrite / Use new slug / Cancel
- Auto-create directory if it doesn't exist
- SPEC and TASK slugs must match
