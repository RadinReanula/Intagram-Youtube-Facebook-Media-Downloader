"use client";

import { motion, useReducedMotion } from "motion/react";
import type { JobView } from "@/lib/types";

export function JobIcon({ status, progress }: { status: JobView["status"]; progress: number }) {
  const reduced = useReducedMotion();
  if (status === "queued") {
    return (
      <span className="flex items-center gap-1" aria-hidden="true">
        {[0, 1, 2].map((dot) => (
          <motion.span
            key={dot}
            className="h-1.5 w-1.5 rounded-full bg-current"
            animate={reduced ? { opacity: 0.7 } : { opacity: [0.3, 1, 0.3] }}
            transition={reduced ? { duration: 0 } : { duration: 1.1, repeat: Infinity, delay: dot * 0.15 }}
          />
        ))}
      </span>
    );
  }
  if (status === "processing") {
    const turn = Math.max(8, Math.min(100, progress || 12));
    return (
      <svg viewBox="0 0 36 36" className="h-7 w-7" aria-hidden="true">
        <circle cx="18" cy="18" r="14" fill="none" stroke="currentColor" strokeOpacity="0.25" strokeWidth="3" />
        <motion.circle
          cx="18"
          cy="18"
          r="14"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          strokeDasharray={`${turn} 100`}
          animate={reduced ? undefined : { rotate: 360 }}
          transition={reduced ? undefined : { duration: 1.1, repeat: Infinity, ease: "linear" }}
          style={{ transformOrigin: "18px 18px" }}
        />
      </svg>
    );
  }
  if (status === "ready") {
    return (
      <svg viewBox="0 0 16 16" className="h-5 w-5" aria-hidden="true">
        <motion.path
          d="M3.2 8.2 6.3 11.2 12.8 4.6"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={reduced ? { pathLength: 1 } : { pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: reduced ? 0 : 0.4 }}
        />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 16 16" className="h-4 w-4" aria-hidden="true">
      <path d="M4 4 12 12M12 4 4 12" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
