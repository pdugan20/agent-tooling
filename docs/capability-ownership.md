# Capability ownership

Use this guide when an installed capability is useful but has no entry in the selected setup. Record its source,
consumer, and maintenance owner before deciding whether to adopt it. Availability across projects does not establish
that it should be a global default.

## Ownership records

| Record | What it owns |
| --- | --- |
| [`inventory/skill-ownership.json`](../inventory/skill-ownership.json) | Reviewed source evidence, proposed scope, and retention decisions for capabilities outside the selected lock |
| `skills-lock.json` | The standalone snapshots selected and installed by this repository |
| An organization's shared-workflow repository | Its shared skills, external dependencies, and adoption decisions |
| A product's capability guide and instructions | Skills needed only for that product, including exceptions to generic guidance |
| Private `~/.codex/local/skill-ownership.json` ledger | Machine paths, copied-skill hashes, installer state, repaired links, and preserved backups |

The ownership registry is a review ledger. Setup and the catalog do not read it as an installation manifest.
`retained-not-adopted` preserves an existing capability while its packaging and intended audience are evaluated.
`retained-recovery-not-selected` records a recovered dependency without adding it to the selected consumer lock.
`provider-selected-fallback-retained` records a provider-backed runtime with a separately tracked standalone fallback;
retired copies stay recoverable outside skill discovery.

## Evidence levels

- `exact-tree`: local file names and Git blob hashes matched the recorded upstream tree, including supporting files.
- `historical-entrypoint`: `SKILL.md` matched an older upstream revision; supporting-file integrity is a separate check.
- `upstream-family-identified-base-unresolved`: the upstream is identified, but the exact older or modified base is unresolved.
- `separate-global-lock-declaration-not-content-verification`: a different manager declares the source; this pass did not verify its bytes.
- `exact-git-tree-recovery`: files were restored from the recorded repository commit and checked against its Git blobs.

A comparison revision is not an installed-version claim. Repository-level license metadata is evidence to review
before redistribution, not a substitute for checking notices and any skill-specific license.

## Moving from retention to adoption

Keep generic source provenance here, work-specific decisions in their organization's repository, and machine
bindings private. Reuse an existing product guide or shared candidate inventory rather than creating another copy
of the skill's instructions. Record existing provider packages and overlapping workflows before adding a duplicate.

Adoption needs an identified owner and audience, a reviewed source and license, a reproducible install path, and
routing and behavior checks proportionate to the risk. Product-specific runner, data, deployment, and publication
rules remain authoritative. Preserve original files and evidence during any later move or retirement.

See [machine audits](maintenance.md#audit-a-machine) for inventory coverage and the
[documentation audit](documentation-audit.md) for the separate Codex-first setup work.
