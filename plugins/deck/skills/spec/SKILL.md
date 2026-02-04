---
name: spec
description: Interview to refine ideas into specs, then execute tasks with progress tracking
argument-hint: '["idea" | @file | run @SPEC-*.md | import @plan-file.md]'
allowed-tools: Read, Write, AskUserQuestion, Glob, Bash(mkdir:*), Bash(date:*), Task
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

Conduct adaptive interviews using AskUserQuestion. No fixed rounds - Claude determines the flow based on context.

**Core Principles**:
- Ask 1-3 focused questions per round
- Dig deep rather than staying surface-level
- Challenge assumptions and explore alternatives
- Continue until user signals completion ("enough", "that's all", "looks good")

**Cumulative Summary**:
Before each question round, provide a brief summary of information collected so far:

```
## Collected Information

**Problem**: {what we know about the problem}
**Users**: {target users identified}
**Technical**: {technical constraints/preferences}
**UX**: {user experience requirements}

Based on the above, I'd like to clarify...
```

**Topic Areas to Explore** (adapt order and depth based on context):
- Problem definition and success criteria
- Target users and their needs
- Technical constraints and integration points
- User experience and interaction patterns
- Risks, tradeoffs, and scope boundaries
- Dependencies and open questions

### Slug Generation

Generate a short English slug based on the requirements:
- Lowercase letters, hyphen-separated
- 2-4 words
- Examples: `user-auth`, `dark-mode`, `api-rate-limit`

### Output File

Ensure directory exists, then generate a single unified file:

**SPEC-{slug}.md** - Combined specification and task tracking:
```markdown
---
title: {Title}
slug: {slug}
created: {YYYY-MM-DD}
last-updated: {YYYY-MM-DD HH:MM}
status: draft
progress: 0/{N}
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

---

# Task List

## Progress Overview

| Status | Count |
|--------|-------|
| Total | {N} |
| Completed | 0 |
| Remaining | {N} |

## Tasks

### Phase 1: {Phase Name}

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1 | {Task description} | ⬜ | Acceptance: {criteria} |
| 2 | {Task description} | ⬜ | Acceptance: {criteria} |

### Phase 2: {Phase Name}

| # | Task | Status | Notes |
|---|------|--------|-------|
| 3 | {Task description} | ⬜ | Acceptance: {criteria} |
| 4 | {Task description} | ⬜ | Acceptance: {criteria} |

---

## Execution Log

{Execution notes will be appended here}
```

**Status Legend**:
- ⬜ Pending
- 🔄 In Progress
- ✅ Completed

---

## Mode 2: Import Mode

Import a Claude Code plan file and convert it to SPEC format for subagent execution.

### Purpose

Claude Code's built-in plan mode executes all tasks in the current session, which can overflow the context window. Import mode converts plan files to SPEC format, enabling execution via isolated subagents.

### Execution Flow

1. **Read plan file**
   - Parse the specified file (e.g., `import @plan.md`)
   - If no file specified, prompt user

2. **Extract content**
   - **Title**: From first `#` heading or filename
   - **Background**: Any text before the task list
   - **Tasks**: Parse checkbox items (`- [ ]` or `- [x]`)

3. **Generate slug**
   - Derive from title or ask user
   - Format: lowercase, hyphen-separated, 2-4 words

4. **Convert to SPEC format**
   - Create SPEC-{slug}.md with three sections:
     - Requirements (from background text)
     - Task List (converted to table format)
     - Execution Log (empty)

5. **Save and confirm**
   - Write to `./plans/SPEC-{slug}.md` (or custom --dir)
   - Show summary and next steps

### Plan File Formats Supported

**Format 1: Markdown checkboxes**
```markdown
# Feature Implementation

Some background context...

## Tasks
- [ ] Task one description
- [ ] Task two description
- [x] Already completed task
```

**Format 2: Numbered list**
```markdown
# Plan Title

1. First task
2. Second task
3. Third task
```

**Format 3: Mixed content**
```markdown
# Plan

## Background
Context and requirements...

## Implementation Steps
- [ ] Step 1: Do something
  - Detail about step 1
- [ ] Step 2: Do another thing
```

### Output Example

After `import @my-plan.md`:

```
## Import Complete

**Source**: my-plan.md
**Output**: ./plans/SPEC-my-feature.md

**Extracted**:
- Title: My Feature
- Tasks: 5 (0 completed, 5 pending)

**Next steps**:
- Review: Read the generated SPEC file
- Execute: /spec run @SPEC-my-feature.md
```

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

1. **Locate SPEC file**
   - File must be specified in the command (e.g., `run @SPEC-user-auth.md`)
   - If no file specified: Prompt user with message:
     ```
     Please specify a SPEC file to execute.
     Usage: /spec run @SPEC-{slug}.md
     ```

2. **Parse tasks**
   - Extract all tasks from the Task List section
   - Identify status of each task (⬜/🔄/✅)
   - Count pending tasks

3. **Display execution plan**
   ```
   ## Execution Plan

   **File**: SPEC-user-auth.md
   **Total Tasks**: 5
   **Already Completed**: 2
   **To Execute**: 3

   | Order | Task | Current Status |
   |-------|------|----------------|
   | 1 | Implement login API | ⬜ |
   | 2 | Add auth middleware | ⬜ |
   | 3 | Write unit tests | ⬜ |

   Proceed with execution? [Y/n]
   ```

#### Phase 2: Sequential Execution

For each pending task in order:

1. **Update status to in-progress**
   - Change task status to 🔄
   - Write file immediately

2. **Execute via subagent**
   - Use Task tool to create isolated subagent
   - Pass task description, acceptance criteria, and relevant spec context
   - Subagent prompt:
     ```
     Execute the following task:

     **Task**: {task_description}
     **Acceptance Criteria**: {acceptance_criteria}

     **Context from Spec**:
     {relevant_spec_sections}

     Complete this task and report the result.
     ```

3. **Handle result**
   - **On success**:
     - Update status to ✅
     - Add completion note with timestamp
     - Update progress count in frontmatter
     - Update `last-updated` timestamp
     - Proceed to next task
   - **On failure**:
     - Keep status as 🔄
     - Stop execution immediately
     - Display error report

4. **Report progress after each task**
   ```
   ## Progress Update

   Completed: Task 3 - Implement login API
   Progress: 3/5 tasks (60%)

   Moving to next task...
   ```

### Error Handling

On task failure, stop immediately and report:

```
## Execution Halted

**Failed Task**: Task 3 - Implement login API
**Status**: 🔄 (marked as in-progress)

**Error Details**:
{Error message from subagent}

**Current Progress**: 2/5 (40%)

**Recovery**:
- Fix the issue manually
- Run `/spec run @SPEC-xxx.md` again to retry from the failed task
```

### Completion Report

```
## Execution Complete

**File**: SPEC-user-auth.md
**Tasks Completed**: 5/5 (100%)

### Summary

| Task | Result |
|------|--------|
| Setup database schema | ✅ Created 3 migration files |
| Create user model | ✅ |
| Implement login API | ✅ Added JWT support |
| Add auth middleware | ✅ |
| Write unit tests | ✅ 12 tests passing |

SPEC file has been updated with completion status.
```

### Subagent Benefits

- **Fresh context**: Each task starts with clean state
- **Clear boundaries**: No accumulated pollution between tasks
- **Easier debugging**: Failures are isolated to specific tasks
- **Progress tracking**: Main context maintains overall view

---

## Important Guidelines

### Interview Principles
- Adapt questions based on context and previous answers
- Provide cumulative summary before each question round
- Ask deep, insightful questions - avoid surface-level ones
- No fixed number of rounds - continue until user is satisfied

### File Handling
- If file exists, ask user: Overwrite / Use new slug / Cancel
- Auto-create directory if it doesn't exist
- Single SPEC file contains both requirements and tasks

### Task Table Format
- Use table format for all tasks
- Status icons: ⬜ Pending | 🔄 In Progress | ✅ Completed
- Include acceptance criteria in Notes column
