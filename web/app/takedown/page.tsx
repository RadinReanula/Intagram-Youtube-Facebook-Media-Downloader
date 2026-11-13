import { LegalLayout } from "@/components/LegalLayout";

const contact = process.env.NEXT_PUBLIC_CONTACT_EMAIL || "takedown@example.com";

export default function TakedownPage() {
  return (
    <LegalLayout
      title="Copyright and takedown"
      intro="Last updated November 2026."
      sections={[
        {
          id: "report",
          heading: "Reporting content",
          body: (
            <p>
              If you believe a file prepared by this site infringes your copyright, email{" "}
              <a className="text-accent underline" href={`mailto:${contact}`}>
                {contact}
              </a>
              . Include the page or link, what you own, and how to reach you.
            </p>
          ),
        },
        {
          id: "next",
          heading: "What happens next",
          body: <p>Valid requests are acted on. Temporary files are already deleted automatically a short time after a download finishes.</p>,
        },
      ]}
    />
  );
}
