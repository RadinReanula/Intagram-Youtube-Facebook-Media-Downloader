import type { ReactNode } from "react";

export function LegalLayout({
  title,
  intro,
  sections,
}: {
  title: string;
  intro: string;
  sections: { id: string; heading: string; body: ReactNode }[];
}) {
  return (
    <main className="mx-auto grid max-w-4xl gap-8 px-5 py-14 md:grid-cols-[180px_1fr] md:gap-10">
      <nav aria-label="On this page" className="flex gap-3 overflow-x-auto text-[0.8125rem] md:sticky md:top-24 md:flex-col md:self-start">
        {sections.map((section) => (
          <a key={section.id} href={`#${section.id}`} className="min-h-11 shrink-0 text-muted hover:text-ink md:min-h-0">
            {section.heading}
          </a>
        ))}
      </nav>
      <article className="rounded-[28px] border border-[var(--line)] bg-surface p-8 shadow-[var(--shadow)]">
        <h1 className="display text-[clamp(2.5rem,6vw,3.75rem)] leading-none">{title}</h1>
        <p className="mt-3 text-muted">{intro}</p>
        {sections.map((section) => (
          <section key={section.id} id={section.id} className="mt-7">
            <h2 className="display text-[1.625rem] leading-tight">{section.heading}</h2>
            <div className="mt-2 grid gap-3 text-muted">{section.body}</div>
          </section>
        ))}
      </article>
    </main>
  );
}
