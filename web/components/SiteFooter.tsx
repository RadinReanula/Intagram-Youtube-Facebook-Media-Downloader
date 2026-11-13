import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="mx-auto flex max-w-3xl flex-wrap justify-center gap-x-5 gap-y-2 px-5 pt-10 pb-8 text-[0.8125rem] text-muted">
      <Link href="/terms" className="min-h-11 content-center hover:text-ink hover:underline">
        Terms of use
      </Link>
      <Link href="/privacy" className="min-h-11 content-center hover:text-ink hover:underline">
        Privacy
      </Link>
      <Link href="/takedown" className="min-h-11 content-center hover:text-ink hover:underline">
        Copyright and takedown
      </Link>
      <span className="content-center">You are responsible for the content you save.</span>
    </footer>
  );
}
