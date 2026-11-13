import { LegalLayout } from "@/components/LegalLayout";

export default function PrivacyPage() {
  return (
    <LegalLayout
      title="Privacy"
      intro="Last updated November 2026."
      sections={[
        {
          id: "links",
          heading: "What we process",
          body: (
            <p>When you paste a link, the server uses that link to fetch public media information and, if you choose, to prepare a file. The link and the job status are kept only long enough to finish the download and to remove the temporary file.</p>
          ),
        },
        {
          id: "instagram",
          heading: "Instagram sign-in",
          body: (
            <p>
              If you sign in to Instagram, the password is sent once over HTTPS and is not written to disk or to the database. The server keeps an encrypted session in memory for this visit only. It is dropped when you sign out, when it expires, or when the server restarts. It is not shared with other visitors.
            </p>
          ),
        },
        {
          id: "logs",
          heading: "Logs and checks",
          body: (
            <>
              <p>The server may record the time of a request, the kind of error, and a shortened form of the network address. Full network addresses are not kept in the application log.</p>
              <p>If a robot check is turned on, that check is provided by Cloudflare Turnstile. Cloudflare receives the information needed to run that check.</p>
              <p>The pages are served over HTTPS. The download service is a separate server, also over HTTPS.</p>
            </>
          ),
        },
      ]}
    />
  );
}
