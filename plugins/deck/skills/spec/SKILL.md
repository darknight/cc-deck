---
name: spec
description: Interview to refine ideas into specs, generate task lists, and execute with progress tracking
argument-hint: '["idea" | @file | apply @TASK-*.md | list | --dir path]'
allowed-tools: Read, Write, AskUserQuestion, Glob, Bash(mkdir:*), Bash(date:*)
---

## Quick Reference
```
/spec "idea"               # Start interview from idea description
/spec @file.md             # Start interview from file content
/spec apply @TASK-*.md     # Execute next task in task list
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
