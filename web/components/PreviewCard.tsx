"use client";

import { motion, useReducedMotion } from "motion/react";
import { PlatformBadge } from "@/components/PlatformBadge";
import { formatDuration } from "@/lib/format";
import type { AnalyzeResult } from "@/lib/types";

const spring = { type: "spring" as const, bounce: 0, duration: 0.4 };

export function PreviewCard({ result }: { result: AnalyzeResult }) {
  const reduced = useReducedMotion();
  const duration = formatDuration(result.duration);
  return (
    <motion.article
      layout
      initial={reduced ? { opacity: 0 } : { opacity: 0, scale: 0.96, filter: "blur(12px)" }}
      animate={reduced ? { opacity: 1 } : { opacity: 1, scale: 1, filter: "blur(0px)" }}
      exit={reduced ? { opacity: 0 } : { opacity: 0, scale: 0.98, filter: "blur(8px)" }}
      transition={reduced ? { duration: 0.2 } : spring}
      style={{ transformOrigin: "top center" }}
      className="card overflow-hidden rounded-3xl"
    >
      {result.thumbnail ? (
        // Thumbnails come from the source platform and change host often.
        // eslint-disable-next-line @next/next/no-img-element
        <img src={result.thumbnail} alt="" className="aspect-video w-full object-cover" referrerPolicy="no-referrer" />
      ) : null}
      <div className="grid gap-3 p-5">
        <PlatformBadge detection={{ platform: result.platform, mediaType: result.media_type }} />
        <h2 className="text-xl leading-tight font-semibold tracking-[-0.02em]">{result.title || "Untitled"}</h2>
        <p className="text-sm text-muted">
          {[result.uploader, duration].filter(Boolean).join(" · ") || "Public media"}
        </p>
      </div>
    </motion.article>
  );
}
