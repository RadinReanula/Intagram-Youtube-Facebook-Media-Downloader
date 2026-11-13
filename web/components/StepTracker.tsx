"use client";

import { StepCheck } from "@/components/icons/StepCheck";

const STEPS = ["Paste", "Choose", "Wait", "Download"];

export function StepTracker({ current }: { current: number }) {
  return (
    <ol className="my-8 flex list-none flex-wrap justify-center gap-1.5 p-0 text-[0.8125rem] text-muted" aria-label="Progress">
      {STEPS.map((label, index) => {
        const step = index + 1;
        const done = step < current;
        const active = step === current;
        return (
          <li
            key={label}
            className={`flex min-h-11 items-center gap-2 rounded-full pr-3 pl-1.5 ${active ? "bg-surface text-ink shadow-[var(--shadow)]" : ""}`}
          >
            <b className={`grid h-5 w-5 place-items-center rounded-full border text-[0.6875rem] ${done ? "border-transparent bg-ready text-bg" : active ? "border-transparent bg-accent text-on-accent" : "border-[var(--line)] bg-surface"}`}>
              {done ? <StepCheck /> : step}
            </b>
            {label}
          </li>
        );
      })}
    </ol>
  );
}
