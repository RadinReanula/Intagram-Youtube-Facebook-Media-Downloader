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
  starting: boolean;
  onItem: (index: number) => void;
  onFormat: (format: FormatOption) => void;
  onAll: () => void;
  onStart: () => void;
};

export function FormatPicker({ items, canDownloadAll, itemIndex, formatId, starting, onItem, onFormat, onAll, onStart }: Props) {
  const reduced = useReducedMotion();
  const item = items.find((entry) => entry.index === itemIndex) ?? items[0];
  const selected = item?.formats.find((format) => format.id === formatId) ?? null;
  const blocked = !selected || selected.over_limit || starting;

  return (
    <section className="mb-4 rounded-[28px] border border-[var(--line)] bg-surface p-5 shadow-[var(--shadow)]">
      {items.length > 1 ? (
        <>
          <div className="mb-2.5 flex items-baseline justify-between text-sm font-semibold">
            Items
            <small className="text-xs font-normal text-muted">{items.length} in this post</small>
          </div>
          <div className="mb-4 flex gap-2.5 overflow-x-auto pb-2">
            {items.map((entry) => {
              const active = entry.index === item?.index;
              return (
                <button
                  key={entry.index}
                  type="button"
                  aria-pressed={active}
                  onClick={() => onItem(entry.index)}
                  className={`w-[132px] shrink-0 rounded-[18px] border bg-bg p-2 text-left ${active ? "border-accent shadow-[0_0_0_2px_var(--accent)]" : "border-[var(--line)]"}`}
                >
                  {entry.thumbnail ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={entry.thumbnail} alt="" className="mb-1.5 aspect-square w-full rounded-xl object-cover" referrerPolicy="no-referrer" />
                  ) : (
                    <i className="mb-1.5 block aspect-square rounded-xl bg-[var(--m2)]" />
                  )}
                  <span className="block text-xs font-medium">{entry.title || `${entry.media_type} ${entry.index + 1}`}</span>
                </button>
              );
            })}
          </div>
        </>
      ) : null}

      <div className="mb-2.5 flex items-baseline justify-between text-sm font-semibold">
        Format
        <small className="text-xs font-normal text-muted">Pick one to continue</small>
      </div>
      <div className="grid gap-2" role="listbox" aria-label="Formats">
        {item?.formats.map((format) => {
          const active = format.id === formatId;
          const size = formatBytes(format.filesize);
          return (
            <button
              key={format.id}
              type="button"
              role="option"
              aria-selected={active}
              aria-disabled={format.over_limit}
              onClick={() => onFormat(format)}
              className={`relative grid grid-cols-[auto_1fr_auto] items-center gap-x-3 gap-y-1 rounded-[18px] border px-3.5 py-3 text-left ${active ? "border-accent bg-surface shadow-[0_0_0_2px_var(--accent)]" : "border-[var(--line)] bg-bg"} ${format.over_limit ? "cursor-not-allowed opacity-70" : ""}`}
            >
              {active && !reduced ? (
                <motion.span layoutId="format-ring" className="pointer-events-none absolute inset-0 rounded-[18px]" transition={spring} />
              ) : null}
              <span className={`rounded-full px-2 py-0.5 text-[0.6875rem] font-semibold capitalize ${format.kind === "audio" ? "bg-[var(--ready-bg)] text-ready" : format.kind === "image" ? "bg-[var(--warn-bg)] text-warning" : "bg-[var(--queued-bg)] text-queued"}`}>
                {format.kind}
              </span>
              <span className="text-sm font-medium">{format.label}</span>
              <span className="text-[0.8125rem] text-muted">{size || format.ext.toUpperCase()}</span>
              {format.warning ? <span className="col-span-2 col-start-2 rounded-[10px] bg-[var(--warn-bg)] px-2.5 py-1.5 text-xs text-warning">{format.warning}</span> : null}
            </button>
          );
        })}
      </div>
      <div className="mt-4 flex flex-wrap gap-2.5">
        {canDownloadAll ? (
          <button type="button" onClick={onAll} className="min-h-11 rounded-full border border-[var(--line)] px-5 text-sm font-medium">
            Download all items
          </button>
        ) : null}
        <button
          type="button"
          disabled={blocked}
          onClick={onStart}
          className="press min-h-11 min-w-[180px] flex-1 rounded-full bg-accent px-6 text-sm font-semibold text-on-accent disabled:cursor-not-allowed disabled:opacity-45"
        >
          {starting ? "Starting" : selected?.over_limit ? "Over the limit" : "Start download"}
        </button>
      </div>
    </section>
  );
}
