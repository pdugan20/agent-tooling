import { useState } from "react";

import { Badge } from "@/components/ui/badge";
import type { CatalogItem, Runtime } from "@/catalog";
import { runtimeLabel } from "@/catalog";
import { brandIcons } from "@/components/source-identity";

const runtimeIcons: Record<Runtime, string> = {
  claude: brandIcons.claudecode,
  codex: brandIcons.openai,
};

function RuntimeIdentity({ runtime }: { runtime: Runtime }) {
  const [imageFailed, setImageFailed] = useState(false);
  const label = runtimeLabel(runtime);

  return (
    <span
      className="grid size-6 shrink-0 place-items-center overflow-hidden rounded-full border-2 border-background bg-background text-[8px] font-semibold shadow-xs"
      aria-label={label}
      title={label}
    >
      {imageFailed ? (
        <span aria-hidden="true">{label.slice(0, 2)}</span>
      ) : (
        <img
          src={runtimeIcons[runtime]}
          alt=""
          className="size-full object-contain p-0.5"
          loading="lazy"
          onError={() => setImageFailed(true)}
        />
      )}
    </span>
  );
}

export function RuntimeBadges({ runtimes }: { runtimes: Runtime[] }) {
  return (
    <div
      className="flex -space-x-1"
      aria-label={`Works in ${runtimes.map(runtimeLabel).join(" and ")}`}
    >
      {runtimes.map((runtime) => (
        <RuntimeIdentity key={runtime} runtime={runtime} />
      ))}
    </div>
  );
}

export function ItemBadges({
  item,
  compact = false,
}: {
  item: CatalogItem;
  compact?: boolean;
}) {
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      <Badge variant="secondary" className="capitalize">
        {item.type}
      </Badge>
      {!compact && (
        <Badge variant="outline">
          {item.availability === "Global"
            ? "All repos"
            : item.repository || "Project"}
        </Badge>
      )}
      {item.invocation && (
        <Badge
          variant={item.invocation === "Explicit" ? "outline" : "secondary"}
        >
          {item.invocation === "Automatic" ? "Auto-starts" : "Only when asked"}
        </Badge>
      )}
    </div>
  );
}
