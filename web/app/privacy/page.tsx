export default function PrivacyPage() {
  return (
    <main className="mx-auto grid max-w-3xl gap-4 px-5 py-12 text-[1.0625rem] leading-relaxed">
      <h1 className="display text-[clamp(2rem,4vw,2.75rem)]">Privacy Policy</h1>
      <p>This site does not ask you to create an account. It does not ask for, or store, a login for Instagram, Facebook or YouTube.</p>
      <p>When you paste a link, the server uses that link to fetch public media information and, if you choose, to prepare a file. The link and the job status are kept only long enough to finish the download and to remove the temporary file.</p>
      <p>The server may record the time of a request, the kind of error, and a shortened form of the network address. Full network addresses are not kept in the application log.</p>
      <p>If a robot check is turned on, that check is provided by Cloudflare Turnstile. Cloudflare receives the information needed to run that check.</p>
      <p>The pages are served over HTTPS. The download service is a separate server, also over HTTPS.</p>
    </main>
  );
}
