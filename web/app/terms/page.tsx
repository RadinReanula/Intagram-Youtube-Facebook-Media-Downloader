import { LegalLayout } from "@/components/LegalLayout";

export default function TermsPage() {
  return (
    <LegalLayout
      title="Terms of use"
      intro="Last updated November 2026."
      sections={[
        {
          id: "scope",
          heading: "Scope",
          body: (
            <>
              <p>This site lets you save a copy of a public media file from a link you paste.</p>
              <p>Only download content you own or have permission to use. You are responsible for what you do with a file after you download it. Most videos, photos and music are protected by copyright.</p>
              <p>Playlists, channels, profiles, live streams and bulk downloads are not offered.</p>
            </>
          ),
        },
        {
          id: "accounts",
          heading: "Accounts",
          body: (
            <p>
              Public links work without an account. Instagram stories, and some Instagram posts, ask you to sign in with your own Instagram username and password for that visit. The password is used once to open a session and is not stored.
            </p>
          ),
        },
        {
          id: "files",
          heading: "Temporary files",
          body: (
            <p>The service is provided as available. Downloads can fail, and files are deleted from the server a short time after they are ready. Downloading may also be against the rules of the site the file came from.</p>
          ),
        },
      ]}
    />
  );
}
