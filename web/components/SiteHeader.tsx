import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="scroll-edge material material-edge">
      <div className="mx-auto flex h-14 max-w-3xl items-center px-5">
        <Link href="/" className="text-[1.0625rem] font-semibold tracking-[-0.01em]">
          Media Downloader
        </Link>
      </div>
    </header>
  );
}
