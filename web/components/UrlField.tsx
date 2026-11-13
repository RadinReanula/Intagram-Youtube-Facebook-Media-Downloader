"use client";

import { useState } from "react";
import { detectLink, platformLabel } from "@/lib/detect";

const COLORS: Record<string, string> = {
  youtube: "#e0382e",
  instagram: "#d6287b",
  facebook: "#2f6fe0",
};

const SAMPLE = "https://www.youtube.com/watch?v=jNQXAC9IVRw";

type Props = {
  onSubmit: (url: string) => void;
  busy: boolean;
};

export function UrlField({ onSubmit, busy }: Props) {
  const [value, setValue] = useState("");
  const detection = detectLink(value);
  const color = detection ? COLORS[detection.platform] : undefined;

  return (
    <div>
      <form
        className="mx-auto flex max-w-xl items-center gap-1 rounded-full border border-[var(--line)] bg-surface p-1.5 shadow-[var(--shadow)] focus-within:outline focus-within:outline-2 focus-within:outline-offset-2 focus-within:outline-accent"
        onSubmit={(event) => {
          event.preventDefault();
          const url = value.trim();
          if (!url || busy) return;
          onSubmit(url);
        }}
      >
        <div className={`flex h-11 items-center gap-2 border-r border-[var(--line)] px-3 text-[0.8125rem] font-medium ${detection ? "text-ink" : "text-muted"}`} aria-live="polite">
          <b className="h-2.5 w-2.5 rounded-full" style={{ background: color || "var(--line)" }} />
          <span className="hidden sm:inline">{detection ? platformLabel(detection.platform) : "Platform"}</span>
        </div>
        <input
          id="media-url"
          name="url"
          type="url"
          inputMode="url"
          autoCapitalize="none"
          autoCorrect="off"
          spellCheck={false}
          placeholder="Paste a public link"
          aria-label="Media link"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          className="h-11 min-w-0 flex-1 border-0 bg-transparent px-2 text-[0.9375rem] outline-none"
        />
        <button
          type="submit"
          disabled={busy || value.trim().length === 0}
          className="press h-11 shrink-0 rounded-full bg-accent px-5 text-sm font-semibold text-on-accent disabled:cursor-not-allowed disabled:opacity-45"
        >
          {busy ? "Checking" : "Analyse"}
        </button>
      </form>
      <div className="mt-4 flex flex-wrap justify-center gap-2">
        <span className="rounded-full border border-[var(--line)] bg-surface px-3.5 py-2 text-xs font-medium">Public content only</span>
        <span className="rounded-full border border-[var(--line)] bg-surface px-3.5 py-2 text-xs font-medium">No playlists or channels</span>
        <span className="rounded-full border border-[var(--line)] bg-surface px-3.5 py-2 text-xs font-medium">Files are temporary</span>
        <button
          type="button"
          className="min-h-11 rounded-full border border-ink bg-surface px-3.5 text-xs font-medium"
          onClick={() => setValue(SAMPLE)}
        >
          Try a sample link
        </button>
      </div>
    </div>
  );
}
