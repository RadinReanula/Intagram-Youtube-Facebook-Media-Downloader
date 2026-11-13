"use client";

import { useState } from "react";
import { detectLink, type Detection } from "@/lib/detect";
import { PlatformBadge } from "@/components/PlatformBadge";

type Props = {
  onSubmit: (url: string) => void;
  busy: boolean;
};

export function UrlField({ onSubmit, busy }: Props) {
  const [value, setValue] = useState("");
  const detection: Detection | null = detectLink(value);

  return (
    <form
      className="grid gap-3"
      onSubmit={(event) => {
        event.preventDefault();
        const url = value.trim();
        if (!url || busy) return;
        onSubmit(url);
      }}
    >
      <label className="grid gap-2 text-sm font-medium" htmlFor="media-url">
        Media link
        <input
          id="media-url"
          name="url"
          type="url"
          inputMode="url"
          autoCapitalize="none"
          autoCorrect="off"
          spellCheck={false}
          placeholder="Paste a public link"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          className="field h-12 rounded-2xl px-4 text-base font-normal outline-none focus-visible:ring-2 focus-visible:ring-accent"
        />
      </label>
      <div className="flex items-center justify-between gap-3">
        <div className="min-h-7">{detection ? <PlatformBadge detection={detection} /> : null}</div>
        <button
          type="submit"
          disabled={busy || value.trim().length === 0}
          className="press h-11 rounded-full bg-accent px-5 text-sm font-medium text-white enabled:hover:bg-[var(--accent-pressed)] disabled:opacity-40"
        >
          {busy ? "Checking" : "Analyse"}
        </button>
      </div>
    </form>
  );
}
