import {
  BookOpenIcon,
  ExternalLinkIcon,
  FileTextIcon,
  GitForkIcon,
} from "lucide-react";

import { displayName, runtimeLabel, type CatalogItem } from "@/catalog";
import { ItemBadges, RuntimeBadges } from "@/components/catalog-badges";
import { SourceIdentity } from "@/components/source-identity";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

function DetailBody({ item }: { item: CatalogItem }) {
  const links = [
    item.repositoryUrl && {
      detail: item.repositoryUrl.replace("https://github.com/", ""),
      icon: GitForkIcon,
      label: "GitHub repository",
      url: item.repositoryUrl,
    },
    item.skillsShUrl && {
      detail: item.skillsShUrl.replace("https://", ""),
      icon: BookOpenIcon,
      label: "skills.sh listing",
      url: item.skillsShUrl,
    },
    item.sourceUrl &&
      item.sourceUrl !== item.repositoryUrl && {
        detail: "Pinned source used by this catalog",
        icon: FileTextIcon,
        label: item.type === "skill" ? "SKILL.md source" : "Plugin source",
        url: item.sourceUrl,
      },
  ].filter(Boolean) as Array<{
    detail: string;
    icon: typeof GitForkIcon;
    label: string;
    url: string;
  }>;

  return (
    <div className="space-y-6">
      <div className="space-y-3">
        <ItemBadges item={item} />
        <p className="text-sm leading-6 text-muted-foreground">
          {item.description}
        </p>
      </div>

      <Separator />

      <dl className="grid grid-cols-[7rem_minmax(0,1fr)] gap-x-4 gap-y-4 text-sm">
        <dt className="text-muted-foreground">Works in</dt>
        <dd>
          <RuntimeBadges runtimes={item.runtimes} />
        </dd>
        <dt className="text-muted-foreground">Source</dt>
        <dd className="font-medium">{item.sourceLabel}</dd>
        <dt className="text-muted-foreground">Version</dt>
        <dd className="font-mono text-xs">
          {item.version === "Git" ? "Tracked from Git" : item.version}
        </dd>
        {item.contentHash && (
          <>
            <dt className="text-muted-foreground">Locked ref</dt>
            <dd className="break-all font-mono text-xs">
              {item.lockedRef || "Default branch snapshot"}
            </dd>
            <dt className="text-muted-foreground">Content hash</dt>
            <dd className="break-all font-mono text-xs">{item.contentHash}</dd>
          </>
        )}
        {item.type === "skill" && (
          <>
            <dt className="text-muted-foreground">Source check</dt>
            <dd>
              {item.freshness ? (
                <>
                  <span>{item.freshness.status}</span>
                  <span className="block text-xs text-muted-foreground">
                    {item.freshness.checkedAt}
                  </span>
                </>
              ) : (
                "Not checked on this machine"
              )}
            </dd>
          </>
        )}
        <dt className="text-muted-foreground">Availability</dt>
        <dd>
          {item.availability === "Global"
            ? "All repositories"
            : item.repository || "Project only"}
        </dd>
      </dl>

      {item.path && (
        <div className="space-y-2">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Managed from
          </h3>
          <code className="block [overflow-wrap:anywhere] rounded-md bg-muted px-3 py-2 font-mono text-xs leading-5">
            {item.path}
          </code>
        </div>
      )}

      {item.installations && item.installations.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Installations
          </h3>
          <div className="divide-y rounded-lg border">
            {item.installations.map((installation) => (
              <div
                key={`${installation.runtime}:${installation.pluginId}`}
                className="space-y-1 p-3"
              >
                <div className="flex items-center justify-between gap-3 text-sm">
                  <span className="font-medium">
                    {runtimeLabel(installation.runtime)}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {installation.delivery === "managed"
                      ? "Managed by Codex"
                      : installation.delivery === "runtime"
                        ? "Bundled"
                        : "Marketplace"}
                  </span>
                </div>
                <code className="block [overflow-wrap:anywhere] font-mono text-[11px] text-muted-foreground">
                  {installation.pluginId}
                </code>
              </div>
            ))}
          </div>
        </div>
      )}

      {links.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Official links
          </h3>
          <div className="grid gap-2">
            {links.map((link) => {
              const Icon = link.icon;
              return (
                <Button
                  key={link.label}
                  asChild
                  variant="outline"
                  className="h-auto min-h-12 justify-start gap-3 px-3 py-2 text-left"
                >
                  <a href={link.url} target="_blank" rel="noreferrer">
                    <Icon className="size-4 shrink-0 text-muted-foreground" />
                    <span className="min-w-0 flex-1">
                      <span className="block font-medium">{link.label}</span>
                      <span className="block truncate text-[11px] font-normal text-muted-foreground">
                        {link.detail}
                      </span>
                    </span>
                    <ExternalLinkIcon className="size-3.5 shrink-0 text-muted-foreground" />
                  </a>
                </Button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

export function DetailPanel({
  item,
  className,
}: {
  item: CatalogItem | null;
  className?: string;
}) {
  if (!item) return null;

  return (
    <aside
      className={cn("flex min-h-0 flex-col border-l bg-card", className)}
      aria-label="Capability details"
    >
      <div className="border-b p-6">
        <div className="flex items-start gap-3">
          <SourceIdentity item={item} size="lg" />
          <div className="min-w-0 pt-0.5">
            <p className="mb-1 text-xs font-medium text-muted-foreground">
              {item.sourceLabel}
            </p>
            <h2 className="text-xl font-semibold tracking-tight">
              {displayName(item)}
            </h2>
          </div>
        </div>
      </div>
      <ScrollArea className="min-h-0 flex-1">
        <div className="p-6">
          <DetailBody item={item} />
        </div>
      </ScrollArea>
    </aside>
  );
}

export function DetailSheet({
  item,
  onOpenChange,
  open,
}: {
  item: CatalogItem | null;
  onOpenChange: (open: boolean) => void;
  open: boolean;
}) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-[min(92vw,28rem)] sm:max-w-md">
        {item && (
          <>
            <SheetHeader className="border-b px-6 py-5 pr-12">
              <div className="flex items-start gap-3 text-left">
                <SourceIdentity item={item} size="lg" />
                <div className="min-w-0 pt-0.5">
                  <SheetTitle>{displayName(item)}</SheetTitle>
                  <SheetDescription>{item.sourceLabel}</SheetDescription>
                </div>
              </div>
            </SheetHeader>
            <ScrollArea className="min-h-0 flex-1">
              <div className="p-6">
                <DetailBody item={item} />
              </div>
            </ScrollArea>
          </>
        )}
      </SheetContent>
    </Sheet>
  );
}
