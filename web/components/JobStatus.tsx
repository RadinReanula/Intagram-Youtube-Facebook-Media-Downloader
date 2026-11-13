"use client";

import { absoluteDownload } from "@/lib/api";
import { formatBytes } from "@/lib/format";
import type { JobView } from "@/lib/types";

export function JobStatus({ job, onCancel, cancelling }: { job: JobView; onCancel: () => void; cancelling: boolean }) {
  const scale = Math.max(0, Math.min(100, job.progress)) / 100;
  return (
    <section className="card grid gap-3 rounded-3xl p-5" aria-live="polite">
      {job.status === "queued" ? (
        <p>
          Waiting
          {job.position ? `. You are number ${job.position} in the queue.` : ". Your download will start soon."}
        </p>
      ) : null}
      {job.status === "processing" ? (
        <div className="grid gap-2">
          <p>Preparing your file{job.progress > 0 ? ` · ${Math.round(job.progress)}%` : ""}</p>
          <div className="h-1.5 overflow-hidden rounded-full bg-[var(--hairline)]">
            <div className="progress-fill h-full bg-accent" style={{ transform: `scaleX(${scale})` }} />
          </div>
        </div>
      ) : null}
      {job.status === "ready" && job.download_url ? (
        <div className="grid gap-3">
          <p className="text-ready">Ready{job.file_size ? ` · ${formatBytes(job.file_size)}` : ""}</p>
          <a
            href={absoluteDownload(job.download_url)}
            className="press inline-flex h-11 items-center justify-center rounded-full bg-accent px-5 text-sm font-medium text-white"
          >
            Download {job.file_name || "file"}
          </a>
        </div>
      ) : null}
      {job.status === "failed" ? <p className="text-failed">{job.error_message || "The download failed."}</p> : null}
      {job.status === "cancelled" ? <p className="text-muted">Download cancelled.</p> : null}
      {job.status === "queued" || job.status === "processing" ? (
        <button type="button" onClick={onCancel} disabled={cancelling} className="press h-10 justify-self-start rounded-full px-4 text-sm text-muted">
          Cancel
        </button>
      ) : null}
    </section>
  );
}
