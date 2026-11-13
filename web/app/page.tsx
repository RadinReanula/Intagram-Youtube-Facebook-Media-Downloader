import { Downloader } from "@/components/Downloader";
import { DownloadMark } from "@/components/icons/DownloadMark";

export default function HomePage() {
  return (
    <main className="mx-auto max-w-3xl px-5">
      <section className="px-2 pt-16 pb-6 text-center">
        <h1 className="display mx-auto max-w-[12em] text-[clamp(2.6rem,8vw,5rem)] leading-[0.98]">
          Save a public{" "}
          <span className="inline-flex translate-y-[-0.06em] items-center gap-2 rounded-full bg-surface px-2 py-1 align-middle text-[0.28em] font-medium tracking-normal text-ink shadow-[var(--shadow)]" style={{ fontFamily: "system-ui, sans-serif" }}>
            <span className="flex" aria-hidden="true">
              <i className="h-[2.2em] w-[2.2em] rounded-full border-2 border-surface bg-[#e0382e]" />
              <i className="-ml-[0.7em] h-[2.2em] w-[2.2em] rounded-full border-2 border-surface bg-[#d6287b]" />
              <i className="-ml-[0.7em] h-[2.2em] w-[2.2em] rounded-full border-2 border-surface bg-[#2f6fe0]" />
            </span>
            3 sites
          </span>{" "}
          video, quietly, from{" "}
          <span className="inline-flex h-[0.78em] w-[0.78em] translate-y-[-0.06em] items-center justify-center rounded-full bg-surface align-middle text-ink shadow-[var(--shadow)]">
            <DownloadMark className="h-[0.42em] w-[0.42em]" />
          </span>{" "}
          one link.
        </h1>
        <p className="mx-auto mt-6 max-w-[34em] text-[0.9375rem] text-muted">
          Paste a single public video, reel or post from YouTube, Instagram or Facebook. Stories ask you to sign in to your own Instagram account for this visit only.
        </p>
      </section>
      <Downloader />
      <p id="how" className="mx-auto mt-2 mb-8 max-w-[34em] text-center text-[0.9375rem] text-muted">
        Paste a link, we check it, you pick a format, and a server prepares the file. Busy servers show a place in line, and nothing is saved on your device until you download.
      </p>
    </main>
  );
}
