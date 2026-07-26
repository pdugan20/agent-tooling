---
name: strict-tdd
description: Implement a feature, fix, or refactor with an explicit red-green-refactor test-driven cycle. Use only when the user explicitly invokes strict TDD; never trigger for visual exploration, prototypes, copy changes, or ordinary implementation where risk-based testing is sufficient.
---

# Strict TDD

For each observable behavior:

1. Identify the smallest useful test at the appropriate layer.
2. Write the test before changing production behavior.
3. Run it and confirm it fails for the intended reason, not because of setup noise.
4. Make the smallest production change that can satisfy the test.
5. Run the focused test and confirm it passes.
6. Refactor while keeping the focused suite green.
7. Repeat until the requested behavior is covered.

Finish by running the relevant broader suite and reporting the evidence. Do not create a worktree, branch, plan, or commit unless requested. If the codebase cannot support a meaningful failing test, stop and explain the concrete constraint instead of pretending the cycle occurred.
