"use client";

import { motion, useReducedMotion } from "motion/react";

export function StepCheck() {
  const reduced = useReducedMotion();
  if (reduced) {
    return (
      <svg viewBox="0 0 16 16" className="h-3 w-3" aria-hidden="true">
        <path d="M3.5 8.2 6.4 11 12.5 4.8" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 16 16" className="h-3 w-3" aria-hidden="true">
      <motion.path
        d="M3.5 8.2 6.4 11 12.5 4.8"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ duration: 0.35, ease: "easeOut" }}
      />
    </svg>
  );
}
