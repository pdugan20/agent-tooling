import { SearchIcon, XIcon } from "lucide-react";
import type { RefObject } from "react";

import { defaultFilters, type CatalogFilters } from "@/catalog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

export function CatalogFiltersBar({
  className,
  filters,
  onChange,
  searchRef,
}: {
  className?: string;
  filters: CatalogFilters;
  onChange: (filters: CatalogFilters) => void;
  searchRef: RefObject<HTMLInputElement | null>;
}) {
  const hasFilters =
    filters.query ||
    filters.type !== "all" ||
    filters.runtime !== "all" ||
    filters.source !== "all";

  return (
    <div className={cn("flex flex-wrap items-center gap-2", className)}>
      <label className="relative min-w-56 flex-1">
        <span className="sr-only">Search catalog</span>
        <SearchIcon className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          ref={searchRef}
          type="search"
          value={filters.query}
          onChange={(event) =>
            onChange({ ...filters, query: event.target.value })
          }
          placeholder="Search capabilities…"
          className="pl-9"
        />
      </label>

      <Select
        value={filters.type}
        onValueChange={(type) =>
          onChange({ ...filters, type: type as CatalogFilters["type"] })
        }
      >
        <SelectTrigger aria-label="Filter by capability type" className="w-31">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All types</SelectItem>
          <SelectItem value="skill">Skills</SelectItem>
          <SelectItem value="plugin">Plugins</SelectItem>
        </SelectContent>
      </Select>

      <Select
        value={filters.runtime}
        onValueChange={(runtime) =>
          onChange({
            ...filters,
            runtime: runtime as CatalogFilters["runtime"],
          })
        }
      >
        <SelectTrigger aria-label="Filter by application" className="w-31">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All apps</SelectItem>
          <SelectItem value="both">Both apps</SelectItem>
          <SelectItem value="codex">Codex</SelectItem>
          <SelectItem value="claude">Claude</SelectItem>
        </SelectContent>
      </Select>

      <Select
        value={filters.source}
        onValueChange={(source) =>
          onChange({ ...filters, source: source as CatalogFilters["source"] })
        }
      >
        <SelectTrigger aria-label="Filter by source" className="w-36">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All sources</SelectItem>
          <SelectItem value="personal">Patrick</SelectItem>
          <SelectItem value="openai">OpenAI</SelectItem>
          <SelectItem value="anthropic">Anthropic</SelectItem>
          <SelectItem value="third-party">Third-party</SelectItem>
          <SelectItem value="repository">Repository</SelectItem>
        </SelectContent>
      </Select>

      {hasFilters && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onChange(defaultFilters)}
        >
          <XIcon />
          Clear
        </Button>
      )}
    </div>
  );
}
