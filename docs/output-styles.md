# Output styles

An output style changes how the agent writes. It is part of the system prompt, so it
applies to every response in every session, with no invocation.

This is the difference that matters when you choose between a style and a skill:

| | Output style | Skill |
| --- | --- | --- |
| Applies | Every response, always | Only when invoked |
| Scope | Prose the agent writes | Whatever the skill does |
| Selected by | `outputStyle` in settings | A call, or a slash command |

A skill cannot make the agent write differently by default, because a skill runs only
when something calls it. If you want every answer to read a certain way, you need a
style.

## What is configured here

`global/output-styles/simple-english.md` holds the managed style.
`scripts/bootstrap.sh` links it into `<claude-config>/output-styles/`, and
`scripts/configure-claude.py` selects it with `outputStyle`. The selection is managed,
not defaulted: a stale value from an earlier release is replaced, so one machine cannot
keep writing in an old style.

## simple-english

The style applies ASD-STE100 Simplified Technical English: one meaning per word, active
voice, simple tenses, short sentences, small noun clusters, and no marketing adjectives.

It is adapted from [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish),
which measured it across 7 models and 8 writing tasks and reported 41 to 85 percent
fewer STE violations per 100 words. A blind pairwise judge preferred the style output in
45 of 56 pairs. That evaluation is the reason this source was chosen over the two other
STE implementations.

### The one local amendment

The upstream style bans `may`, `might`, and `could` outright. That rule is wrong for
this use, and the local copy carves them out.

A hedge carries the author's confidence, and confidence is content. "The request may
have failed" and "the request failed" are different claims. A length rule that deletes
the hedge does not shorten the sentence, it fabricates certainty the source never
stated. The amendment keeps those modals when they mark real uncertainty, and deletes
them only when they are padding ("this may potentially help to improve").

The failure it prevents is the most common way a well-intentioned plain-language rewrite
goes wrong, and it is documented in
[danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill), which states
the rule clearly even though its own packaging is a skill rather than a style.

## Changing the style

Edit `global/output-styles/simple-english.md`, or add a file beside it and change
`OUTPUT_STYLE` in `scripts/configure-claude.py`. Run `npm run bootstrap` to link it,
then start a new session. `/output-style` shows the current selection.
