# Skill visibility and invocation

Two independent gates decide whether an agent can start a skill. Confusing them costs
real time, because the symptom is identical: the agent does not use the skill.

## Gate 1: `skillOverrides` in Claude settings

Four values, set per skill:

| Value | Agent sees it | Agent can start it | User can start it |
| --- | --- | --- | --- |
| `on` | yes | yes | yes |
| `name-only` | name only | yes | yes |
| `user-invocable-only` | **no** | no | yes |
| `off` | no | no | no |

The important row is `user-invocable-only`. It does not mean "ask the user first". It
means the skill is **invisible to the agent**. The agent cannot propose it, because it
does not know the skill exists.

Measured 2026-08-17: a repository held 23 skills on disk with exactly one set to
`user-invocable-only`. That skill was the only one absent from the agent's listing.

## Gate 2: `disable-model-invocation` in the skill's own frontmatter

A skill author can set `disable-model-invocation: true` in `SKILL.md`. This reserves the
skill for explicit user invocation.

**`skillOverrides` cannot override it.** Measured 2026-08-17: twelve skills were set to
`on`. The eight without the frontmatter flag appeared. The four with it did not:
`grill-with-docs`, `to-tickets`, `wayfinder`, and `setup-matt-pocock-skills`, all from
`mattpocock/skills`.

Calling such a skill returns an explicit refusal:

```
Skill to-tickets cannot be used with Skill tool due to disable-model-invocation.
Ask the user to run /to-tickets themselves.
```

The block sits below the permission layer. There is no prompt to approve, so an approval
hook cannot reach it.

## What this means in practice

Making a frontmatter-gated skill agent-invocable requires editing the upstream author's
`SKILL.md`. Those files are hash-locked in `skills-lock.json`, so editing one means
carrying a fork patch and fighting `npx skills update` from then on. For a skill that
publishes issues to a real tracker, "a human types the command" is a defensible bar.
Prefer leaving it.

The cost of the gate is not that the work cannot happen. It is that an **invisible skill
gets silently substituted** rather than skipped: an agent that cannot see the tool
hand-rolls an equivalent and does not mention it. That happened on 2026-08-17, when a
ticket named `xcode-build-benchmark`, the agent could not start it, and it benchmarked by
hand without saying so.

The fix is the rule in `global/AGENTS.md`: when a ticket, plan, or doc requires an action
from a skill the agent cannot invoke, it must stop and ask, and must not substitute a
hand-rolled equivalent.

That rule applies when the named skill still has work to do. It does not make every
downstream implementation step another invocation of the planning skill. Keep these
surfaces distinct:

- `wayfinder` owns creating and resolving a decision map;
- `to-tickets` owns publishing tracer-bullet tickets and their blocking edges; and
- the repository's ordinary delivery cycle owns implementing already-decided work.

If a map or ticket has already established a finite implementation batch, one explicit
owner approval can authorize the agent to work through that batch without asking for the
planning skill again after every item. The agent must keep the batch in the same active
work session where the skill's own instructions require that, and must not claim the
skill ran during ordinary implementation. A new invocation is needed only when the next
step actually changes the map, publishes tracker state, or otherwise requires the gated
skill to act.

## Open decision: the explicit-only sets

Two lists in this repository make skills invisible rather than owner-approved:

- `config/superpowers.json` -> `explicitOnlySkills`
- `EXPLICIT_PERSONAL_SKILLS` in `scripts/configure-claude.py` (`review-animations`)

Both use the fork patch or `user-invocable-only`, so the agent cannot see or propose
them. That is why the owner has to remember to run `/superpowers:writing-plans` at the
right moment, instead of the agent proposing a plan document when one is due.

The alternative is visibility plus an approval prompt: the agent proposes, the user
approves each run. A consuming repository has already shipped that pattern with a
`PreToolUse` hook and a checked-in list of owner-approved skills. Whether to adopt it
here is an open decision, not an oversight.
