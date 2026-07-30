# Global and project scope

Use runtime availability—not the directory name printed by an installer—to decide whether a capability is global or project-scoped.

## Scope rules

| Put it globally when… | Put it in a repository when… |
| --- | --- |
| The guidance should behave the same in nearly every codebase. | It names project architecture, commands, endpoints, schemas, release lanes, or domain concepts. |
| It is a personal working preference, general design method, or reusable review workflow. | It needs to travel with the repository so another contributor or machine gets the same behavior. |
| A plugin supplies a broadly useful integration such as GitHub, Figma, Firebase, Sentry, or Vercel. | Only that project needs an upstream reference bundle, or the project must pin it independently. |

Global does not mean “unconditionally active.” Invocation policy is separate: a global skill can be explicit-only, and a project skill can be selected automatically for a request that clearly matches it.

## Global profile

`agent-tooling` manages ten shared skills. Although the official `skills` CLI calls the seven upstream snapshots project-scoped because their lockfile lives here, `bootstrap.sh` links all ten into each agent's home-directory skills location. Their effective runtime availability is therefore **all repositories**.

- Locally maintained: `code-native-ui-ideation`, `feature-delivery`, `production-hardening`.
- Upstream managed: `animation-vocabulary`, `apple-design`, `emil-design-eng`, `find-animation-opportunities`, `pick-ui-library`, `review-animations`, `swiftui-pro`.

The desired Codex and Claude plugin manifests are also user-level machine setup. Plugins can contribute their own skills and tools. Repository instructions decide how those global capabilities should be used locally; they should not duplicate the plugin files.

## Audited project profiles

| Repository | Project-scoped skills | Why they stay local |
| --- | --- | --- |
| `nextup-backend` | 20 NextUp-maintained backend, Firebase, recommendation, notification, testing, and deployment workflows | They encode NextUp schemas, scripts, operations, and safety boundaries. Notification sending remains explicit-only. |
| `nextup-ios-app` | 19 NextUp-maintained workflows plus locked `hig`, `swift-concurrency`, and `swift-testing` references | The local workflows encode the app's build, test, simulator, analytics, release, and documentation systems. The narrow upstream Apple profile is pinned only where it is useful. |
| `audiobook-ios` | Locked `hig`, `swift-concurrency`, and `swift-testing` references | The project benefits from the same narrow Apple reference profile while keeping iOS 18 availability constraints in its `AGENTS.md`. |
| `rewind` | `add-media`, `media-search`, `changelog-writer` | These name Rewind's live admin API, credentials, media domains, and documentation format. |
| `messenger` | None | Expo/React Native work uses the global design and delivery profile plus installed Expo and Figma capabilities. Project behavior lives in `AGENTS.md`. |
| `pat-portfolio` | None | React work uses the global design, animation, UI-library, and delivery profile. Project behavior lives in `AGENTS.md`. |
| `rss-feed-generator` | Locked `use-railway` skill | Railway operations apply only to this deployed service. The canonical Railway skill is shared by Codex and Claude through the project's `.agents/skills` source and Claude compatibility link; do not add Railway to either global plugin manifest. |

The full Apple Skills plugin is deliberately not installed. `swiftui-pro` remains global and primary; the two native apps pin only three factual/reference skills from `Prisma-Labs-Dev/apple-skills`. Upstream files remain unmodified so the official lock/update path continues to work.

## Persistence and machine setup

- Git-tracked `AGENTS.md`, `.agents/skills`, `.claude/skills` links, and `skills-lock.json` travel with a project.
- `agent-tooling` global sources travel through its Git repository and become active after `npm run bootstrap` on each machine. Claude paths use `$CLAUDE_CONFIG_DIR` when set and otherwise default to `~/.claude`.
- User-level plugin installations and product settings must be recreated by `npm run setup` or the plugin refresh commands.
- Project-scoped plugins belong in the consuming repository's tracked agent configuration and should be installed
  with the runtime's project scope. They must not be promoted to a user-level manifest for convenience.
- `.claude/settings.local.json`, OAuth sessions, secrets, API keys, simulator state, and toolchains are machine-local and do not sync through Git.

For upstream project skills, run `npx skills update -p -y` in that project, review the snapshot and lockfile diff, and run the project's verification. The current CLI does not document a read-only update check. Locally maintained project skills update with the application code.

The canonical browser catalog remains the portable global manifest. Its local “This Mac” snapshot can also index
project skills without committing machine paths: run
`npm run catalog:snapshot -- --repos-root /path/to/repositories`, then filter by availability or repository.
