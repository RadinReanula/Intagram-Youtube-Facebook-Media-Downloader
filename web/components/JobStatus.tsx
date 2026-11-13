"use client";

import { absoluteDownload } from "@/lib/api";
import { JobIcon } from "@/components/icons/JobIcon";
import { formatBytes } from "@/lib/format";
import type { JobView } from "@/lib/types";

const TONE: Record<JobView["status"], string> = {
  queued: "bg-[var(--queued-bg)] text-queued",
  processing: "bg-[var(--warn-bg)] text-warning",
  ready: "bg-[var(--ready-bg)] text-ready",
  failed: "bg-[var(--fail-bg)] text-failed",
  cancelled: "bg-[var(--fail-bg)] text-failed",
};

export function JobStatus({ job, onCancel, onReset, cancelling }: { job: JobView; onCancel: () => void; onReset: () => void; cancelling: boolean }) {
  const scale = Math.max(0.04, Math.min(1, (job.progress || 8) / 100));
  const size = formatBytes(job.file_size);
  return (
    <section className="mb-4 rounded-[28px] border border-[var(--line)] bg-surface p-5 shadow-[var(--shadow)]" aria-live="polite">
      <div className="flex items-center gap-4">
        <div className={`grid h-12 w-12 shrink-0 place-items-center rounded-2xl ${TONE[job.status]}`}>
          <JobIcon status={job.status} progress={job.progress} />
        </div>
        <div className="min-w-0 flex-1">
          {job.status === "queued" ? (
            <>
              <strong className="block text-[0.9375rem]">You’re in line</strong>
              <small className="text-[0.8125rem] text-muted">{job.position ? `Place ${job.position}. Processing starts as soon as the server is free.` : "Processing starts as soon as the server is free."}</small>
              <div className="mt-2.5 h-2 overflow-hidden rounded-full bg-[var(--line)]">
                <div className="pulse-bar h-full w-full rounded-full bg-queued opacity-40" />
              </div>
            </>
          ) : null}
          {job.status === "processing" ? (
            <>
              <strong className="block text-[0.9375rem]">Preparing your file{job.progress > 0 ? `, ${Math.round(job.progress)}%` : ""}</strong>
              <small className="text-[0.8125rem] text-muted">This can take a minute for longer videos.</small>
              <div className="mt-2.5 h-2 overflow-hidden rounded-full bg-[var(--line)]" role="progressbar" aria-valuenow={Math.round(job.progress)} aria-valuemin={0} aria-valuemax={100}>
                <div className="progress-fill h-full w-full rounded-full bg-accent" style={{ transform: `scaleX(${scale})` }} />
              </div>
            </>
          ) : null}
          {job.status === "ready" ? (
            <>
              <strong className="block text-[0.9375rem]">Ready to download</strong>
              <small className="text-[0.8125rem] text-muted">
                {(job.file_name || "File") + (size ? `, ${size}` : "")}. Available for a limited time, then it’s deleted.
              </small>
            </>
          ) : null}
          {job.status === "failed" ? (
            <>
              <strong className="block text-[0.9375rem]">The download failed</strong>
              <small className="text-[0.8125rem] text-muted">{job.error_message || "Try another format or a different link."}</small>
            </>
          ) : null}
          {job.status === "cancelled" ? (
            <>
              <strong className="block text-[0.9375rem]">Cancelled</strong>
              <small className="text-[0.8125rem] text-muted">Nothing was saved. Pick a format to start again.</small>
            </>
          ) : null}
        </div>
      </div>
      {job.status === "ready" && job.download_url ? (
        <div className="mt-4 flex flex-wrap gap-2.5">
          <a href={absoluteDownload(job.download_url)} className="press inline-flex min-h-11 flex-1 items-center justify-center rounded-full bg-accent px-5 text-sm font-semibold text-on-accent">
            Download file
          </a>
          <button type="button" onClick={onReset} className="min-h-11 rounded-full border border-[var(--line)] px-5 text-sm font-medium">
            Save another
          </button>
        </div>
      ) : null}
      {job.status === "queued" || job.status === "processing" ? (
        <div className="mt-4">
          <button type="button" onClick={onCancel} disabled={cancelling} className="min-h-11 rounded-full border border-[var(--line)] px-5 text-sm font-medium">
            Cancel
          </button>
        </div>
      ) : null}
    </section>
  );
}
