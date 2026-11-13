const contact = process.env.NEXT_PUBLIC_CONTACT_EMAIL || "takedown@example.com";

export default function TakedownPage() {
  return (
    <main className="mx-auto grid max-w-3xl gap-4 px-5 py-12 text-[1.0625rem] leading-relaxed">
      <h1 className="display text-[clamp(2rem,4vw,2.75rem)]">Copyright and takedown</h1>
      <p>If you believe a file prepared by this site infringes your copyright, write to us and we will review it.</p>
      <p>
        Email{" "}
        <a className="text-accent" href={`mailto:${contact}`}>
          {contact}
        </a>
        . Include the page or link, what you own, and how to reach you.
      </p>
      <p>Valid requests are acted on. Temporary files are already deleted automatically a short time after a download finishes.</p>
    </main>
  );
}
