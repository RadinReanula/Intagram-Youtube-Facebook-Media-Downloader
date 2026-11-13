import Link from "next/link";
import { DownloadMark } from "@/components/icons/DownloadMark";
import { InstagramAccount } from "@/components/InstagramAccount";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-20 px-4 pt-3">
      <div className="nav-bar mx-auto flex max-w-5xl items-center gap-4 rounded-full border border-[var(--line)] bg-[color-mix(in_srgb,var(--surface)_72%,transparent)] px-2 py-1.5 pl-4 backdrop-blur-xl">
        <Link href="/" className="mr-auto flex min-h-11 items-center gap-2 text-sm font-semibold">
          <DownloadMark className="h-[18px] w-[18px]" play={false} />
          Media Downloader
        </Link>
        <Link href="/#how" className="hidden min-h-11 items-center px-1 text-[0.8125rem] text-muted hover:text-ink sm:inline-flex">
          How it works
        </Link>
        <Link href="/terms" className="hidden min-h-11 items-center px-1 text-[0.8125rem] text-muted hover:text-ink sm:inline-flex">
          Terms
        </Link>
        <Link href="/privacy" className="hidden min-h-11 items-center px-1 text-[0.8125rem] text-muted hover:text-ink md:inline-flex">
          Privacy
        </Link>
        <Link href="/takedown" className="inline-flex min-h-11 items-center rounded-full border border-[var(--line)] bg-surface px-4 text-[0.8125rem] font-medium shadow-[var(--shadow)]">
          Takedown
        </Link>
        <InstagramAccount />
      </div>
    </header>
  );
}
