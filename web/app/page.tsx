import { Downloader } from "@/components/Downloader";

export default function HomePage() {
  return (
    <main className="mx-auto grid max-w-3xl gap-8 px-5 py-12">
      <div className="grid gap-3">
        <h1 className="display">Save a public video</h1>
        <p className="max-w-xl text-lg text-muted">Paste a link from YouTube, Instagram or Facebook. We show what it is, then you choose a file. Stories are not supported.</p>
      </div>
      <Downloader />
    </main>
  );
}
