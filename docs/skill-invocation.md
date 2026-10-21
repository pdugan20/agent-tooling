# Skill visibility and invocation

Codex is the primary harness. Use its invocation controls even when the selected model is Claude.
Installation, visibility, invocation policy, and authorization to perform an action are separate concerns.

## Codex invocation policy

Codex can select a skill from its description or use one explicitly named by the user. Its initial skill list has a
context budget: descriptions can be shortened, and a sufficiently large collection can omit entries with a warning.
Front-load trigger conditions and boundaries. An on-disk file alone does not prove that the active chat can use it.
[Official skill guidance](https://learn.chatgpt.com/docs/build-skills)

Use `agents/openai.yaml` in the canonical skill source for Codex-specific policy:

```yaml
policy:
  allow_implicit_invocation: false
```

This disables implicit selection while retaining explicit invocation. It is different from disabling the skill
through `[[skills.config]]` with `enabled = false`, which this repo uses for unwanted or duplicate entrypoints.
Codex detects local skill changes automatically; restart if discovery is stale. Restart after changing skill
configuration in `config.toml`. [Official metadata and overrides](https://learn.chatgpt.com/docs/build-skills#optional-metadata)

For this setup, the current session's available-skills catalog is authoritative. Follow Codex's trigger rules for
listed skills. Do not reinterpret Claude's `disable-model-invocation` frontmatter as a Codex refusal.
Do not modify locked snapshots to change policy; update their canonical source or use a supported runtime override.

## Personal workflow boundaries

`global/AGENTS.md` defines which workflows need an explicit request. `config/superpowers.json` records the fork's
explicit-only and automatic groups. Preserve those boundaries when changing metadata or packaging.
An explicit skill invocation does not independently authorize publishing, deployment, or live-data mutation.

When a required named skill is unavailable, stop and ask the owner to run or restore it. Do not silently substitute
a hand-written workflow. Check installation, profile, disabled paths, collisions, and discovery before claiming a
capability is absent from the machine.

A historical skill mention does not require reinvocation for every downstream step. Once a decision map or ticket
establishes an approved finite batch, ordinary implementation can continue within that authorization.
Invoke the planning or tracker skill again when it must change the artifact it owns. See the shared agreement.

## Optional Claude Code compatibility

The following observations were measured in Claude on 2026-08-17. They explain retained configuration; recheck them
against the active Claude version before changing compatibility policy. They are not Codex controls.

| Claude `skillOverrides` value | Observed visibility and invocation |
| --- | --- |
| `on` | Visible and agent-invocable, subject to frontmatter |
| `name-only` | Name visible and agent-invocable, subject to frontmatter |
| `user-invocable-only` | Hidden from the agent; user invocation available |
| `off` | Hidden and disabled |

In that measurement, `disable-model-invocation: true` in `SKILL.md` prevented agent invocation even with the setting
`on`. A runtime refusal at that gate was not an approval prompt. Preserve the upstream snapshot rather than patching
it locally to bypass the restriction.

This repo sets Claude's `review-animations` override to `user-invocable-only`. The configured Superpowers fork also
contains Claude-specific invocation controls. Their visibility effects must be evaluated in Claude separately from
Codex's `allow_implicit_invocation`. This documentation update does not introduce a new approval-hook workflow.
