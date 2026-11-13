"use client";

import { motion, useReducedMotion } from "motion/react";

export function DownloadMark({ play = true, className = "h-[1em] w-[1em]" }: { play?: boolean; className?: string }) {
  const reduced = useReducedMotion();
  const drop = reduced || !play ? { y: 0 } : { y: [-4, 0] };
  return (
    <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden="true">
      <motion.g initial={false} animate={drop} transition={{ type: "spring", bounce: 0, duration: 0.45 }}>
        <path d="M10 3v10" />
        <path d="M5.5 9 10 13.5 14.5 9" />
      </motion.g>
      <path d="M4 17h12" />
    </svg>
  );
}
