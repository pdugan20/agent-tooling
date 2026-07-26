---
name: execute-plan
description: Carry out an approved implementation plan while preserving existing work and reporting verified checkpoints. Use only when explicitly invoked with a plan or clear plan reference; do not trigger merely because a task has multiple steps.
---

# Execute Plan

1. Read the plan, applicable instructions, current diff, and repository state.
2. Flag only blockers or assumptions that would materially change the intended result.
3. Implement in coherent batches, keeping unrelated user changes intact.
4. Verify each batch at the narrowest useful level before proceeding.
5. Use strict TDD only when the plan or user explicitly requires it.
6. Stop before destructive actions, live mutations, deploys, pushes, or PR creation unless authorized.
7. Finish with the implemented outcome, verification evidence, remaining risks, and unexecuted plan items.

Do not require a worktree, branch, commit, or approval checkpoint unless repository state, risk, or the plan makes one necessary.
