import {
  ArrowUpRightIcon,
  LaptopIcon,
  Layers3Icon,
  SearchIcon,
} from "lucide-react";
import type { RefObject } from "react";

import {
  categoryFor,
  displayName,
  formatSnapshotDate,
  libraryCategories,
  type CatalogFilters,
  type CatalogItem,
  type CatalogPayload,
  type CatalogScope,
  type LibraryCategory,
} from "@/catalog";
import { ItemBadges, RuntimeBadges } from "@/components/catalog-badges";
import { DetailPanel } from "@/components/catalog-detail";
import { CatalogFiltersBar } from "@/components/catalog-filters";
import { SourceIdentity } from "@/components/source-identity";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

function LibraryCard({
  item,
  onSelect,
  selected,
}: {
  item: CatalogItem;
  onSelect: (item: CatalogItem) => void;
  selected: boolean;
}) {
  return (
    <Card
      className={cn(
        "gap-4 py-5 transition-[border-color,box-shadow]",
        selected && "border-primary/35 shadow-md",
      )}
    >
      <CardHeader className="gap-3 px-5">
        <div className="flex items-start justify-between gap-3">
          <SourceIdentity item={item} />
          <ItemBadges item={item} compact />
        </div>
        <div>
          <CardTitle className="text-base leading-6">
            {displayName(item)}
          </CardTitle>
          <p className="mt-1 text-xs text-muted-foreground">
            {item.sourceLabel}
          </p>
        </div>
      </CardHeader>
      <CardContent className="px-5">
        <p className="line-clamp-3 min-h-15 text-sm leading-5 text-muted-foreground">
          {item.description}
        </p>
      </CardContent>
      <CardFooter className="justify-between gap-3 px-5">
        <RuntimeBadges runtimes={item.runtimes} />
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onSelect(item)}
          aria-label={`View ${displayName(item)}`}
        >
          View
          <ArrowUpRightIcon />
        </Button>
      </CardFooter>
    </Card>
  );
}

export function LibraryVariant({
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
  const selectedCategory = (new URLSearchParams(window.location.search).get(
    "category",
  ) || "All capabilities") as LibraryCategory;
  const safeCategory = libraryCategories.includes(selectedCategory)
    ? selectedCategory
    : "All capabilities";
  const snapshotDate = formatSnapshotDate(activePayload.generatedAt);
  const categoryCounts = Object.fromEntries(
    libraryCategories.map((category) => [
      category,
      category === "All capabilities"
        ? items.length
        : items.filter((item) => categoryFor(item) === category).length,
    ]),
  );
  const visible =
    safeCategory === "All capabilities"
      ? items
      : items.filter((item) => categoryFor(item) === safeCategory);

  const setCategory = (category: LibraryCategory) => {
    const url = new URL(window.location.href);
    if (category === "All capabilities") url.searchParams.delete("category");
    else url.searchParams.set("category", category);
    window.history.replaceState({}, "", url);
    window.dispatchEvent(new PopStateEvent("popstate"));
  };

  return (
    <main className="grid min-h-0 flex-1 grid-cols-1 xl:grid-cols-[minmax(0,1fr)_23rem]">
      <ScrollArea className="min-h-0 bg-background">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 sm:py-10">
          <section className="grid gap-8 border-b pb-8 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-end">
            <div className="max-w-2xl">
              <Badge
                variant="outline"
                className="mb-4 border-primary/20 bg-primary/5 text-primary"
              >
                Skill Library
              </Badge>
              <h1 className="text-3xl font-semibold tracking-[-0.035em] sm:text-4xl">
                Know what your agents can do.
              </h1>
              <p className="mt-3 max-w-xl text-base leading-7 text-muted-foreground">
                Browse the reusable instructions and integrations available
                across Codex and Claude, with provenance close at hand.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-2 sm:flex">
              <Button
                variant={scope === "canonical" ? "secondary" : "outline"}
                onClick={() => onScopeChange("canonical")}
              >
                <Layers3Icon />
                Our setup
                <Badge variant="outline" className="bg-background">
                  {canonicalCount}
                </Badge>
              </Button>
              <Button
                variant={scope === "local" ? "secondary" : "outline"}
                onClick={() => onScopeChange("local")}
              >
                <LaptopIcon />
                This Mac
                <Badge variant="outline" className="bg-background">
                  {localCount}
                </Badge>
              </Button>
            </div>
          </section>

          <div className="grid gap-8 pt-8 lg:grid-cols-[13rem_minmax(0,1fr)]">
            <aside className="hidden lg:block">
              <div className="sticky top-5 space-y-6">
                <div>
                  <p className="mb-2 px-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                    Collections
                  </p>
                  <nav
                    aria-label="Capability collections"
                    className="space-y-1"
                  >
                    {libraryCategories.map((category) => (
                      <Button
                        key={category}
                        variant={
                          safeCategory === category ? "secondary" : "ghost"
                        }
                        className="w-full justify-start"
                        onClick={() => setCategory(category)}
                      >
                        <span className="truncate">{category}</span>
                        <span className="ml-auto text-xs tabular-nums text-muted-foreground">
                          {categoryCounts[category]}
                        </span>
                      </Button>
                    ))}
                  </nav>
                </div>
                <div className="rounded-lg border bg-muted/30 p-4 text-xs leading-5 text-muted-foreground">
                  <p>
                    {activePayload.message ||
                      "The setup saved in this repository."}
                  </p>
                  {scope === "local" && snapshotDate && (
                    <p className="mt-2">Captured {snapshotDate}</p>
                  )}
                </div>
              </div>
            </aside>

            <section
              className="min-w-0 space-y-5"
              aria-labelledby="collection-title"
            >
              <div className="space-y-4">
                <div className="space-y-2 lg:hidden">
                  <label className="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                    Collection
                  </label>
                  <Select
                    value={safeCategory}
                    onValueChange={(category) =>
                      setCategory(category as LibraryCategory)
                    }
                  >
                    <SelectTrigger
                      aria-label="Choose a capability collection"
                      className="w-full"
                    >
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {libraryCategories.map((category) => (
                        <SelectItem key={category} value={category}>
                          {category} ({categoryCounts[category]})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-muted-foreground">
                    {scope === "local" && snapshotDate
                      ? `Snapshot from ${snapshotDate}`
                      : activePayload.message ||
                        "The setup saved in this repository."}
                  </p>
                </div>
                <div className="flex items-end justify-between gap-4">
                  <div>
                    <p className="text-xs font-medium text-primary">
                      {visible.length} capabilities
                    </p>
                    <h2
                      id="collection-title"
                      className="mt-1 text-xl font-semibold tracking-tight"
                    >
                      {safeCategory}
                    </h2>
                  </div>
                </div>
                <CatalogFiltersBar
                  filters={filters}
                  onChange={onFiltersChange}
                  searchRef={searchRef}
                />
              </div>

              {visible.length > 0 ? (
                <div className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-3">
                  {visible.map((item) => (
                    <LibraryCard
                      key={item.id}
                      item={item}
                      onSelect={onSelect}
                      selected={selected?.id === item.id}
                    />
                  ))}
                </div>
              ) : (
                <div className="grid min-h-72 place-items-center rounded-xl border border-dashed bg-muted/20 p-8 text-center">
                  <div>
                    <SearchIcon className="mx-auto size-5 text-muted-foreground" />
                    <h3 className="mt-3 text-sm font-semibold">
                      No capabilities found
                    </h3>
                    <p className="mt-1 max-w-sm text-sm text-muted-foreground">
                      {activePayload.items.length
                        ? "Try another collection or clear a filter."
                        : activePayload.message}
                    </p>
                  </div>
                </div>
              )}
            </section>
          </div>
        </div>
      </ScrollArea>

      <DetailPanel item={selected} className="hidden xl:flex" />
    </main>
  );
}
