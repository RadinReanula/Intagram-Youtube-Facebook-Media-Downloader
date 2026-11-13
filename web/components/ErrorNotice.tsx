import type { ErrorCopy } from "@/lib/messages";

export function ErrorNotice({ copy }: { copy: ErrorCopy }) {
  return (
    <div role="alert" className="mb-4 rounded-[20px] bg-[var(--fail-bg)] px-4 py-3.5 text-sm text-failed">
      <strong className="block font-semibold">{copy.title}</strong>
      <span className="text-ink/80">{copy.detail}</span>
    </div>
  );
}
