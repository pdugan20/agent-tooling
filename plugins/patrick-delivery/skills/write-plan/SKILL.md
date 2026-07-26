---
name: write-plan
description: Create a focused, executable implementation plan from approved requirements or a selected design. Use only when explicitly invoked to plan substantial work; do not trigger for small UI iterations, exploratory changes, or requests to implement immediately.
---

# Write Plan

1. Inspect the relevant repository state, instruction files, architecture, and existing tests.
2. State the goal, boundaries, assumptions, and unresolved decisions.
3. Divide work into ordered, independently verifiable steps.
4. Name concrete files or subsystems when evidence supports them.
5. Attach proportional verification to each risky step and a final acceptance check.
6. Call out production mutations, migrations, deploys, or user decisions that require approval.

Return the plan without implementing it. Avoid speculative rewrites, mandatory test-first steps, branch creation, or commit choreography unless the request requires them.
