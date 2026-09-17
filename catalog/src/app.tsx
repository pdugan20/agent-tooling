import { FlaskConicalIcon } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import {
  defaultFilters,
  filterItems,
  loadCatalogs,
  type CatalogFilters,
  type CatalogItem,
  type CatalogPayload,
  type CatalogScope,
} from "@/catalog";
import { DetailSheet } from "@/components/catalog-detail";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TooltipProvider } from "@/components/ui/tooltip";
import { LibraryVariant } from "@/variants/library";
import { WorkbenchVariant } from "@/variants/workbench";

type Variant = "workbench" | "library";

interface CatalogCollections {
  canonical: CatalogPayload;
  local: CatalogPayload;
}

function readVariant(): Variant {
  return new URLSearchParams(window.location.search).get("variant") ===
    "library"
    ? "library"
    : "workbench";
}

function readScope(): CatalogScope {
  return new URLSearchParams(window.location.search).get("runtime") === "local"
    ? "local"
    : "canonical";
}

function LoadingState() {
  return (
    <div className="grid flex-1 place-items-center">
      <div className="text-center">
        <div className="mx-auto size-8 animate-pulse rounded-lg bg-muted" />
        <p className="mt-3 text-sm text-muted-foreground">
          Loading the catalog…
        </p>
      </div>
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="grid flex-1 place-items-center p-6">
      <div className="max-w-md rounded-xl border bg-card p-6 text-center shadow-sm">
        <h1 className="font-semibold">The catalog could not load</h1>
        <p className="mt-2 text-sm text-muted-foreground">{message}</p>
      </div>
    </div>
  );
}

export function App() {
  const [collections, setCollections] = useState<CatalogCollections | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<CatalogFilters>(defaultFilters);
  const [scope, setScope] = useState<CatalogScope>(readScope);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [variant, setVariantState] = useState<Variant>(readVariant);
  const [, setLocationVersion] = useState(0);
  const searchRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let cancelled = false;
    loadCatalogs()
      .then((payloads) => {
        if (!cancelled) setCollections(payloads);
      })
      .catch((reason: unknown) => {
        if (!cancelled)
          setError(
            reason instanceof Error ? reason.message : "Unknown catalog error.",
          );
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const handleLocationChange = () => {
      setVariantState(readVariant());
      setScope(readScope());
      setFilters(defaultFilters);
      setSelectedId(null);
      setLocationVersion((version) => version + 1);
    };
    window.addEventListener("popstate", handleLocationChange);
    return () => window.removeEventListener("popstate", handleLocationChange);
  }, []);

  useEffect(() => {
    const focusSearch = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        searchRef.current?.focus();
      }
    };
    document.addEventListener("keydown", focusSearch);
    return () => document.removeEventListener("keydown", focusSearch);
  }, []);

  const activePayload = collections?.[scope] ?? null;
  const items = useMemo(
    () => (activePayload ? filterItems(activePayload.items, filters) : []),
    [activePayload, filters],
  );
  const selected =
    items.find((item) => item.id === selectedId) ??
    activePayload?.items.find((item) => item.id === selectedId) ??
    items[0] ??
    null;

  useEffect(() => {
    if (!selectedId && items[0]) setSelectedId(items[0].id);
    if (
      selectedId &&
      items.length > 0 &&
      !items.some((item) => item.id === selectedId)
    ) {
      setSelectedId(items[0].id);
    }
  }, [items, selectedId]);

  const setVariant = (nextVariant: string) => {
    const value = nextVariant as Variant;
    const url = new URL(window.location.href);
    url.searchParams.set("variant", value);
    window.history.replaceState({}, "", url);
    setVariantState(value);
  };

  const selectItem = (item: CatalogItem) => {
    setSelectedId(item.id);
    if (window.matchMedia("(max-width: 1279px)").matches) setDetailOpen(true);
  };

  const changeScope = (nextScope: CatalogScope) => {
    const url = new URL(window.location.href);
    if (nextScope === "local") url.searchParams.set("runtime", "local");
    else url.searchParams.delete("runtime");
    window.history.replaceState({}, "", url);
    setScope(nextScope);
    setFilters(defaultFilters);
    setSelectedId(null);
  };

  if (error) return <ErrorState message={error} />;

  return (
    <TooltipProvider>
      <div className="flex h-svh min-h-0 flex-col overflow-hidden">
        <header className="flex h-16 shrink-0 items-center justify-between gap-4 border-b bg-card px-4 sm:px-6">
          <div className="flex min-w-0 items-center gap-3">
            <div className="grid size-8 shrink-0 place-items-center rounded-lg bg-foreground text-xs font-bold text-background">
              A
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold">Agent Tooling</p>
              <p className="hidden truncate text-xs text-muted-foreground sm:block">
                Skills and plugins
              </p>
            </div>
            <Badge variant="outline" className="hidden gap-1.5 sm:flex">
              <FlaskConicalIcon />
              Exploration
            </Badge>
          </div>

          <Tabs value={variant} onValueChange={setVariant}>
            <TabsList aria-label="Catalog design variant">
              <TabsTrigger value="workbench">Workbench</TabsTrigger>
              <TabsTrigger value="library">Library</TabsTrigger>
            </TabsList>
          </Tabs>
        </header>

        {!collections || !activePayload ? (
          <LoadingState />
        ) : variant === "workbench" ? (
          <WorkbenchVariant
            activePayload={activePayload}
            canonicalCount={collections.canonical.items.length}
            filters={filters}
            items={items}
            localCount={collections.local.items.length}
            onFiltersChange={setFilters}
            onScopeChange={changeScope}
            onSelect={selectItem}
            scope={scope}
            searchRef={searchRef}
            selected={selected}
          />
        ) : (
          <LibraryVariant
            activePayload={activePayload}
            canonicalCount={collections.canonical.items.length}
            filters={filters}
            items={items}
            localCount={collections.local.items.length}
            onFiltersChange={setFilters}
            onScopeChange={changeScope}
            onSelect={selectItem}
            scope={scope}
            searchRef={searchRef}
            selected={selected}
          />
        )}

        <DetailSheet
          item={selected}
          open={detailOpen}
          onOpenChange={setDetailOpen}
        />
      </div>
    </TooltipProvider>
  );
}
