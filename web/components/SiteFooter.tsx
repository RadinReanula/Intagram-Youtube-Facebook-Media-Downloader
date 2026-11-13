import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="mx-auto flex max-w-3xl flex-wrap gap-x-5 gap-y-2 px-5 py-10 text-sm text-muted">
      <Link href="/terms">Terms of Use</Link>
      <Link href="/privacy">Privacy Policy</Link>
      <Link href="/takedown">Copyright and takedown</Link>
    </footer>
  );
}
