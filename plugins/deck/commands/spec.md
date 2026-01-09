---
allowed-tools: Read, AskUserQuestion, Write
description: interview user to refine a spec through in-depth Q&A
---

Read the spec file provided by the user (e.g., @docs/SPEC-*.md or any markdown file they reference).

Then interview the user in detail using the AskUserQuestion tool about:
- Technical implementation details
- UI & UX considerations
- Edge cases and concerns
- Tradeoffs and alternatives
- Dependencies and constraints
- Potential risks

Important guidelines:
- Ask non-obvious, insightful questions that dig deeper
- Avoid surface-level or generic questions
- Challenge assumptions when appropriate
- Explore implications of design decisions
- Continue interviewing until the spec is comprehensive and complete

After the interview is complete, update the spec file with all the refined details and decisions made during the conversation.
