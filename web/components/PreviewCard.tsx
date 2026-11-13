"use client";

import { motion, useReducedMotion } from "motion/react";
import { platformLabel } from "@/lib/detect";
import { formatDuration } from "@/lib/format";
import type { AnalyzeResult } from "@/lib/types";

const spring = { type: "spring" as const, bounce: 0, duration: 0.4 };
const COLORS: Record<string, string> = { youtube: "#e0382e", instagram: "#d6287b", facebook: "#2f6fe0" };

export function PreviewCard({ result }: { result: AnalyzeResult }) {
  const reduced = useReducedMotion();
  const duration = formatDuration(result.duration);
  const color = COLORS[result.platform];
  const meta = [result.uploader ? `By ${result.uploader}` : null, duration].filter(Boolean).join(", ");
  return (
    <motion.article
      layout
      initial={reduced ? { opacity: 0 } : { opacity: 0, y: 8, scale: 0.99 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={reduced ? { opacity: 0 } : { opacity: 0, y: 6 }}
      transition={reduced ? { duration: 0.2 } : spring}
      className="mb-4 rounded-[28px] border border-[var(--line)] bg-surface p-5 shadow-[var(--shadow)]"
    >
      <div className="grid items-center gap-4 sm:grid-cols-[150px_1fr]">
        {result.thumbnail ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={result.thumbnail} alt="" className="aspect-video w-full rounded-[18px] object-cover" referrerPolicy="no-referrer" />
        ) : (
          <div className="grid aspect-video place-items-center rounded-[18px] text-white" style={{ background: `linear-gradient(135deg, ${color}, color-mix(in srgb, ${color} 40%, white))` }}>
            <span className="display text-[1.75rem] italic">{platformLabel(result.platform)}</span>
          </div>
        )}
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-[var(--line)] bg-bg px-2.5 py-1 text-xs font-medium">
            <i className="h-1.5 w-1.5 rounded-full" style={{ background: color }} />
            {platformLabel(result.platform)} {result.media_type}
          </span>
          <h2 className="display mt-2 text-[1.625rem] leading-tight">{result.title || "Untitled"}</h2>
          <p className="mt-1 text-sm text-muted">{meta || "Public media"}</p>
        </div>
      </div>
    </motion.article>
  );
}

export function PreviewSkeleton() {
  return (
    <div className="mb-4 grid gap-4 rounded-[28px] border border-[var(--line)] bg-surface p-5 shadow-[var(--shadow)] sm:grid-cols-[132px_1fr]" aria-hidden="true">
      <div className="skel-block aspect-video" />
      <div className="grid content-center gap-2.5">
        <div className="skel-block h-5 w-24" />
        <div className="skel-block h-6 w-3/4" />
        <div className="skel-block h-3.5 w-1/2" />
      </div>
    </div>
  );
}
