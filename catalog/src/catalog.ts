export type Runtime = "codex" | "claude";
export type CapabilityType = "skill" | "plugin";
export type CatalogScope = "canonical" | "local";

export interface Installation {
  delivery: "managed" | "marketplace" | "runtime";
  path?: string;
  pluginId: string;
  runtime: Runtime;
  state?: string;
  version?: string;
}

export interface CatalogItem {
  availability: "Global" | "Project";
  brand?: "openai" | "claudecode" | null;
  description: string;
  displayName?: string;
  featured: number;
  id: string;
  installations?: Installation[];
  invocation?: "Automatic" | "Explicit" | null;
  name: string;
  ownerAvatarUrl?: string | null;
  path?: string;
  pathHref?: string | null;
  pluginIds?: string[];
  repository?: string;
  repositoryUrl?: string | null;
  runtimes: Runtime[];
  source: "personal" | "openai" | "anthropic" | "third-party" | "repository";
  sourceLabel: string;
  sourceUrl?: string | null;
  state: string;
  skillsShUrl?: string | null;
  type: CapabilityType;
  version: string;
  lockedRef?: string | null;
  contentHash?: string;
  freshness?: { checkedAt: string; status: string; upstreamCommit?: string };
}

export interface CatalogPayload {
  generatedAt?: string;
  items: CatalogItem[];
  message?: string;
  schemaVersion: number;
}

export interface CatalogFilters {
  query: string;
  runtime: "all" | "both" | Runtime;
  source: "all" | CatalogItem["source"];
  type: "all" | CapabilityType;
}

export const defaultFilters: CatalogFilters = {
  query: "",
  runtime: "all",
  source: "all",
  type: "all",
};

const baseUrl = import.meta.env.BASE_URL;

async function readPayload(file: string): Promise<CatalogPayload | null> {
  const response = await fetch(`${baseUrl}${file}`, { cache: "no-store" });
  if (!response.ok) return null;
  return (await response.json()) as CatalogPayload;
}

export async function loadCatalogs() {
  const [canonical, local, localPlaceholder, freshness] = await Promise.all([
    readPayload("data.json"),
    readPayload("runtime-data.local.json"),
    readPayload("runtime-data.json"),
    fetch(`${baseUrl}skill-freshness.local.json`, { cache: "no-store" })
      .then(async (response) =>
        response.ok && response.headers.get("content-type")?.includes("json")
          ? ((await response.json()) as {
              checkedAt: string;
              results: Array<{
                name: string;
                status: string;
                upstreamCommit?: string;
              }>;
            })
          : null,
      )
      .catch(() => null),
  ]);

  if (!canonical) throw new Error("Could not load the canonical catalog.");

  if (freshness) {
    for (const item of canonical.items) {
      const result = freshness.results.find(
        (result) => item.type === "skill" && result.name === item.name,
      );
      if (result)
        item.freshness = {
          checkedAt: freshness.checkedAt,
          status: result.status,
          upstreamCommit: result.upstreamCommit,
        };
    }
  }

  return {
    canonical,
    local: local ??
      localPlaceholder ?? {
        items: [],
        message: "Run npm run catalog:snapshot to inspect this computer.",
        schemaVersion: canonical.schemaVersion,
      },
  };
}

export function displayName(item: CatalogItem) {
  return item.displayName || item.name;
}

export function filterItems(items: CatalogItem[], filters: CatalogFilters) {
  const query = filters.query.trim().toLowerCase();

  return items
    .filter((item) => {
      const haystack = [
        item.name,
        item.displayName,
        item.description,
        item.sourceLabel,
        item.sourceUrl,
        item.repositoryUrl,
        item.skillsShUrl,
        item.invocation,
        item.state,
        item.version,
        item.repository,
        ...(item.pluginIds ?? []),
        ...(item.installations ?? []).flatMap((installation) => [
          installation.pluginId,
          installation.runtime,
          installation.delivery,
          installation.state,
          installation.version,
        ]),
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      const runtimeMatches =
        filters.runtime === "all" ||
        (filters.runtime === "both"
          ? item.runtimes.includes("codex") && item.runtimes.includes("claude")
          : item.runtimes.includes(filters.runtime));

      return (
        (!query || haystack.includes(query)) &&
        (filters.type === "all" || item.type === filters.type) &&
        (filters.source === "all" || item.source === filters.source) &&
        runtimeMatches
      );
    })
    .sort(
      (first, second) =>
        first.featured - second.featured ||
        displayName(first).localeCompare(displayName(second)),
    );
}

export const libraryCategories = [
  "All capabilities",
  "Build & deliver",
  "Interface craft",
  "Documentation",
  "Platforms & services",
  "Agent workflow",
] as const;

export type LibraryCategory = (typeof libraryCategories)[number];

export function categoryFor(item: CatalogItem): LibraryCategory {
  const text =
    `${item.name} ${item.displayName ?? ""} ${item.description}`.toLowerCase();

  if (
    /mintlify|document|presentation|writing|changelog|reference|docs/.test(text)
  ) {
    return "Documentation";
  }
  if (/ui|design|animation|swiftui|typography|interface|figma/.test(text)) {
    return "Interface craft";
  }
  if (
    /firebase|cloudflare|vercel|expo|xcode|sentry|github|slack|supabase|hosting|browser/.test(
      text,
    )
  ) {
    return "Platforms & services";
  }
  if (/feature|bootstrap|delivery|repository|deploy|build/.test(text)) {
    return "Build & deliver";
  }
  return "Agent workflow";
}

export function formatSnapshotDate(value?: string) {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) return null;
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function runtimeLabel(runtime: Runtime) {
  return runtime === "codex" ? "Codex" : "Claude";
}
