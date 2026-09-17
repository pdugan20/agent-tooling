import {
  BoxIcon,
  CheckCircle2Icon,
  CircleDotIcon,
  Layers3Icon,
  LaptopIcon,
  PanelLeftIcon,
} from "lucide-react";
import type { RefObject } from "react";

import {
  displayName,
  formatSnapshotDate,
  runtimeLabel,
  type CatalogFilters,
  type CatalogItem,
  type CatalogPayload,
  type CatalogScope,
} from "@/catalog";
import { ItemBadges, RuntimeBadges } from "@/components/catalog-badges";
import { DetailPanel } from "@/components/catalog-detail";
import { CatalogFiltersBar } from "@/components/catalog-filters";
import { SourceIdentity } from "@/components/source-identity";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

function Metric({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof BoxIcon;
  label: string;
  value: number;
}) {
  return (
    <div className="flex min-w-0 flex-col items-start gap-1 rounded-lg border bg-card px-3 py-3 shadow-xs sm:flex-row sm:items-center sm:gap-3 sm:px-4">
      <div className="hidden size-8 shrink-0 place-items-center rounded-md bg-muted text-muted-foreground sm:grid">
        <Icon className="size-4" />
      </div>
      <div className="min-w-0">
        <div className="text-lg font-semibold tabular-nums leading-none">
          {value}
        </div>
        <div className="mt-1 text-xs leading-4 text-muted-foreground">
          {label}
        </div>
      </div>
    </div>
  );
}

function WorkbenchSidebar({
  activePayload,
  canonicalCount,
  localCount,
  onScopeChange,
  scope,
}: {
  activePayload: CatalogPayload;
  canonicalCount: number;
  localCount: number;
  onScopeChange: (scope: CatalogScope) => void;
  scope: CatalogScope;
}) {
  const snapshotDate = formatSnapshotDate(activePayload.generatedAt);

  return (
    <aside className="hidden min-h-0 flex-col border-r bg-muted/25 lg:flex">
      <div className="p-4">
        <p className="mb-2 px-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
          Inventory
        </p>
        <nav aria-label="Inventory source" className="space-y-1">
          <Button
            variant={scope === "canonical" ? "secondary" : "ghost"}
            className="w-full justify-start"
            onClick={() => onScopeChange("canonical")}
          >
            <Layers3Icon />
            Our setup
            <Badge variant="outline" className="ml-auto bg-background">
              {canonicalCount}
            </Badge>
          </Button>
          <Button
            variant={scope === "local" ? "secondary" : "ghost"}
            className="w-full justify-start"
            onClick={() => onScopeChange("local")}
          >
            <LaptopIcon />
            This Mac
            <Badge variant="outline" className="ml-auto bg-background">
              {localCount}
            </Badge>
          </Button>
        </nav>
      </div>

      <Separator />

      <div className="space-y-4 p-6 text-xs text-muted-foreground">
        <div className="flex items-start gap-2">
          <CheckCircle2Icon className="mt-0.5 size-3.5 shrink-0 text-emerald-600" />
          <p>
            {activePayload.message ||
              "Canonical configuration saved in this repository."}
          </p>
        </div>
        {scope === "local" && snapshotDate && (
          <div className="flex items-start gap-2">
            <CircleDotIcon className="mt-0.5 size-3.5 shrink-0" />
            <p>Snapshot from {snapshotDate}</p>
          </div>
        )}
      </div>
    </aside>
  );
}

function EmptyResults({ message }: { message: string }) {
  return (
    <div className="grid min-h-72 place-items-center p-8 text-center">
      <div>
        <div className="mx-auto mb-3 grid size-10 place-items-center rounded-lg border bg-muted/40">
          <PanelLeftIcon className="size-4 text-muted-foreground" />
        </div>
        <h2 className="text-sm font-semibold">Nothing to show</h2>
        <p className="mt-1 max-w-sm text-sm text-muted-foreground">{message}</p>
      </div>
    </div>
  );
}

function WorkbenchTable({
  items,
  onSelect,
  selectedId,
}: {
  items: CatalogItem[];
  onSelect: (item: CatalogItem) => void;
  selectedId?: string;
}) {
  return (
    <>
      <div className="hidden overflow-hidden rounded-lg border bg-card md:block">
        <Table>
          <TableHeader>
            <TableRow className="bg-muted/35 hover:bg-muted/35">
              <TableHead>Capability</TableHead>
              <TableHead className="w-35">Works in</TableHead>
              <TableHead className="w-38">Source</TableHead>
              <TableHead className="w-32">Invocation</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((item) => (
              <TableRow
                key={item.id}
                data-state={selectedId === item.id ? "selected" : undefined}
              >
                <TableCell className="max-w-0 py-3">
                  <button
                    type="button"
                    onClick={() => onSelect(item)}
                    className="flex w-full items-start gap-3 rounded-md text-left outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  >
                    <SourceIdentity item={item} size="sm" />
                    <span className="min-w-0 flex-1">
                      <span className="flex items-center gap-2">
                        <span className="truncate text-sm font-medium">
                          {displayName(item)}
                        </span>
                        <Badge
                          variant="secondary"
                          className="shrink-0 capitalize"
                        >
                          {item.type}
                        </Badge>
                      </span>
                      <span className="mt-1 block truncate text-xs text-muted-foreground">
                        {item.description}
                      </span>
                    </span>
                  </button>
                </TableCell>
                <TableCell>
                  <RuntimeBadges runtimes={item.runtimes} />
                </TableCell>
                <TableCell className="truncate text-xs text-muted-foreground">
                  {item.sourceLabel}
                </TableCell>
                <TableCell className="text-xs text-muted-foreground">
                  {item.invocation === "Automatic"
                    ? "Auto-starts"
                    : item.invocation === "Explicit"
                      ? "Only when asked"
                      : "Plugin"}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <div className="divide-y overflow-hidden rounded-lg border bg-card md:hidden">
        {items.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => onSelect(item)}
            className={cn(
              "block w-full space-y-3 p-4 text-left outline-none transition-colors hover:bg-muted/50 focus-visible:bg-muted focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ring",
              selectedId === item.id && "bg-muted/60",
            )}
          >
            <div className="flex items-start gap-3">
              <SourceIdentity item={item} size="sm" />
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-3">
                  <span className="font-medium">{displayName(item)}</span>
                  <ItemBadges item={item} compact />
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  {item.sourceLabel}
                </p>
              </div>
            </div>
            <p className="line-clamp-2 text-xs leading-5 text-muted-foreground">
              {item.description}
            </p>
            <RuntimeBadges runtimes={item.runtimes} />
          </button>
        ))}
      </div>
    </>
  );
}

export function WorkbenchVariant({
  activePayload,
  canonicalCount,
  filters,
  items,
  localCount,
  onFiltersChange,
  onScopeChange,
  onSelect,
  scope,
  searchRef,
  selected,
}: {
  activePayload: CatalogPayload;
  canonicalCount: number;
  filters: CatalogFilters;
  items: CatalogItem[];
  localCount: number;
  onFiltersChange: (filters: CatalogFilters) => void;
  onScopeChange: (scope: CatalogScope) => void;
  onSelect: (item: CatalogItem) => void;
  scope: CatalogScope;
  searchRef: RefObject<HTMLInputElement | null>;
  selected: CatalogItem | null;
}) {
  const skills = items.filter((item) => item.type === "skill").length;
  const plugins = items.filter((item) => item.type === "plugin").length;
  const shared = items.filter((item) => item.runtimes.length === 2).length;

  return (
    <main className="grid min-h-0 flex-1 grid-cols-1 lg:grid-cols-[15rem_minmax(0,1fr)] xl:grid-cols-[15rem_minmax(0,1fr)_22rem]">
      <WorkbenchSidebar
        activePayload={activePayload}
        canonicalCount={canonicalCount}
        localCount={localCount}
        onScopeChange={onScopeChange}
        scope={scope}
      />

      <ScrollArea className="min-h-0 bg-background">
        <div className="mx-auto max-w-6xl space-y-5 p-4 sm:p-6">
          <div className="flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
                Workbench
              </p>
              <h1 className="mt-1 text-2xl font-semibold tracking-tight">
                Capability inventory
              </h1>
              <p className="mt-1 text-sm text-muted-foreground">
                Scan, filter, and inspect the setup without leaving the table.
              </p>
            </div>
            <div className="flex gap-2 lg:hidden">
              <Button
                size="sm"
                variant={scope === "canonical" ? "secondary" : "outline"}
                onClick={() => onScopeChange("canonical")}
              >
                Our setup
              </Button>
              <Button
                size="sm"
                variant={scope === "local" ? "secondary" : "outline"}
                onClick={() => onScopeChange("local")}
              >
                This Mac
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2">
            <Metric icon={BoxIcon} label="Skills" value={skills} />
            <Metric icon={Layers3Icon} label="Plugins" value={plugins} />
            <Metric
              icon={CheckCircle2Icon}
              label="Work in both"
              value={shared}
            />
          </div>

          <div className="sticky top-0 z-20 -mx-2 border-y bg-background/95 px-2 py-3 backdrop-blur supports-[backdrop-filter]:bg-background/80">
            <CatalogFiltersBar
              filters={filters}
              onChange={onFiltersChange}
              searchRef={searchRef}
            />
          </div>

          <div
            className="flex items-center justify-between text-xs text-muted-foreground"
            aria-live="polite"
          >
            <span>{items.length} capabilities</span>
            <span>
              {scope === "canonical"
                ? "Repository source of truth"
                : activePayload.message}
            </span>
          </div>

          {items.length ? (
            <WorkbenchTable
              items={items}
              onSelect={onSelect}
              selectedId={selected?.id}
            />
          ) : (
            <EmptyResults
              message={
                activePayload.items.length
                  ? "Try clearing a filter or using a broader search."
                  : activePayload.message || "No capabilities were found."
              }
            />
          )}
        </div>
      </ScrollArea>

      <DetailPanel item={selected} className="hidden xl:flex" />
    </main>
  );
}
