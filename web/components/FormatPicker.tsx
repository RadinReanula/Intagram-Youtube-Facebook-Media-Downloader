"use client";

import { motion, useReducedMotion } from "motion/react";
import { formatBytes } from "@/lib/format";
import type { FormatOption, MediaItem } from "@/lib/types";

const spring = { type: "spring" as const, bounce: 0, duration: 0.4 };

type Props = {
  items: MediaItem[];
  canDownloadAll: boolean;
  itemIndex: number;
  formatId: string | null;
  onItem: (index: number) => void;
  onFormat: (format: FormatOption) => void;
  onAll: () => void;
};

export function FormatPicker({ items, canDownloadAll, itemIndex, formatId, onItem, onFormat, onAll }: Props) {
  const reduced = useReducedMotion();
  const item = items.find((entry) => entry.index === itemIndex) ?? items[0];
  const selected = item?.formats.find((format) => format.id === formatId) ?? null;
  const transition = reduced ? { duration: 0.2 } : spring;

  return (
    <div className="grid gap-4">
      {items.length > 1 ? (
        <div className="grid gap-2">
          <p className="text-sm font-medium">Items</p>
          <div className="flex gap-2 overflow-x-auto pb-1">
            {items.map((entry) => (
              <button
                key={entry.index}
                type="button"
                onClick={() => onItem(entry.index)}
                className={`press h-10 shrink-0 rounded-full px-4 text-sm ${entry.index === item?.index ? "bg-text text-bg" : "bg-raised text-text"}`}
              >
                {entry.index + 1}. {entry.media_type}
              </button>
            ))}
          </div>
        </div>
      ) : null}

      <div className="grid gap-2" role="listbox" aria-label="Download options">
        {item?.formats.map((format) => {
          const active = format.id === formatId;
          const size = formatBytes(format.filesize);
          return (
            <button
              key={format.id}
              type="button"
              role="option"
              aria-selected={active}
              onClick={() => onFormat(format)}
              className={`press relative overflow-hidden rounded-2xl px-4 py-3 text-left ${active ? "text-white" : "bg-raised text-text"}`}
            >
              {active ? (
                <motion.span
                  layoutId="format-pill"
                  className="absolute inset-0 bg-accent"
                  transition={transition}
                />
              ) : null}
              <span className="relative z-10 flex items-baseline justify-between gap-3">
                <span className="font-medium">{format.label}</span>
                <span className={`text-sm ${active ? "text-white/80" : "text-muted"}`}>{size || format.ext.toUpperCase()}</span>
              </span>
            </button>
          );
        })}
      </div>

      {selected?.warning ? <p className="text-sm text-warning">{selected.warning}</p> : null}

      {canDownloadAll ? (
        <button type="button" onClick={onAll} className="press h-11 rounded-full bg-raised px-5 text-sm font-medium">
          Download all items
        </button>
      ) : null}
    </div>
  );
}
