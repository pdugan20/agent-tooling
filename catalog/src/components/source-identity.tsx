import { useState } from "react";

import type { CatalogItem } from "@/catalog";
import { cn } from "@/lib/utils";

export const brandIcons = {
  claudecode:
    "https://unpkg.com/@lobehub/icons-static-svg@1.94.0/icons/claudecode-color.svg",
  openai: "https://unpkg.com/@lobehub/icons-static-svg@1.94.0/icons/openai.svg",
} as const;

const sizes = {
  sm: "size-8 text-[10px]",
  md: "size-10 text-xs",
  lg: "size-12 text-sm",
} as const;

export function SourceIdentity({
  className,
  item,
  size = "md",
}: {
  className?: string;
  item: CatalogItem;
  size?: keyof typeof sizes;
}) {
  const [imageFailed, setImageFailed] = useState(false);
  const imageUrl = item.brand
    ? brandIcons[item.brand]
    : item.ownerAvatarUrl || undefined;
  const initials = item.sourceLabel
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();

  return (
    <span
      className={cn(
        "grid shrink-0 place-items-center overflow-hidden rounded-xl border bg-muted font-semibold text-muted-foreground shadow-xs",
        sizes[size],
        className,
      )}
      title={item.sourceLabel}
    >
      {imageUrl && !imageFailed ? (
        <img
          src={imageUrl}
          alt={`${item.sourceLabel} identity`}
          className={cn(
            "size-full",
            item.brand ? "object-contain p-1.5" : "object-cover",
          )}
          loading="lazy"
          referrerPolicy="no-referrer"
          onError={() => setImageFailed(true)}
        />
      ) : (
        <span aria-hidden="true">{initials || "?"}</span>
      )}
    </span>
  );
}
