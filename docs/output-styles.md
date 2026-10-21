# Writing style by harness

## Codex

Put persistent writing preferences in the shared `global/AGENTS.md` when they should apply across projects.
Project-specific preferences belong in that project's instructions. Codex loads those instructions without a skill
invocation. [Official instruction guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

A writing skill can guide a particular documentation task. It does not replace persistent instructions for every
response. This repository does not install a Codex equivalent of Claude's `simple-english` output style, and selecting
a Claude model through Codex does not activate Claude Code's style settings.

## Optional Claude Code style

`global/output-styles/simple-english.md` is a Claude Code output style. Bootstrap links it into the active Claude
profile's `output-styles/` directory, and `scripts/configure-claude.py` selects it with `outputStyle`.
The configurator replaces a stale selection. This mechanism applies to Claude Code sessions.

The text is adapted from [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish). Its local amendment retains
`may`, `might`, and `could` when they express uncertainty. Removing those words must not turn an uncertain claim
into a factual assertion. Read the managed file for the complete writing guidance.

To change the Claude style, edit the canonical style or add another file and update `OUTPUT_STYLE` in the configurator.
`npm run bootstrap:claude` applies the Claude links and selection; restart Claude afterward. Default bootstrap configures Codex.
Use `/output-style` in Claude to inspect the selected style.

Claude's `outputStyles` declaration does not transfer to Codex plugin packaging.
[Official compatibility guidance](https://developers.openai.com/plugins/guides/submit-claude-plugin)
