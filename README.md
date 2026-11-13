# Media Downloader

Paste a public YouTube, Instagram or Facebook link, choose a format, and download the file.

The site is a Next.js app meant for Vercel. Downloading and conversion run on your Debian VPS, behind a reverse proxy, as a systemd service. Nothing heavy runs on Vercel.

## Local development

API:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r api\requirements.txt
.\.venv\Scripts\python -m pip install -U yt-dlp
$env:YTDLP_PATH = "$pwd\.venv\Scripts\yt-dlp.exe"
$env:DOWNLOAD_SIGNING_SECRET = "local-dev-secret"
$env:ADMIN_TOKEN = "local-dev-admin"
cd api
..\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

Web, in another terminal:

```powershell
cd web
copy .env.example .env.local
npm install
npm run dev
```

Open http://localhost:3000. The API is http://127.0.0.1:8000.

Tests:

```powershell
cd api
..\.venv\Scripts\python -m pytest
```

## Deploy the API on Debian

Docker is not used. From a checkout on the VPS:

```sh
sudo sh deploy/install.sh
```

Then edit `/etc/media-downloader.env`:

- `ADMIN_TOKEN` and `DOWNLOAD_SIGNING_SECRET` must be long random strings.
- `CORS_ORIGINS` must be the site origin. The site and the API have to share a parent domain, such as `example.com` and `api.example.com`, or the Instagram session cookie will not be kept. A `*.vercel.app` site with the API on another host will not stay signed in.
- `TURNSTILE_SECRET` if you turn on the robot check.
- `ENABLE_INSTAGRAM_LOGIN=true` and `COOKIE_SECURE=true` only when you want per-visit Instagram sign-in. It is off by default. Instagram may challenge or lock sign-ins from a data-centre address.
- `MAX_CONCURRENT_JOBS`, duration, file size and rate limit are read from this file. Restart the service after a change.

Resource caps live in `deploy/media-downloader.service` (`CPUQuota`, `MemoryMax`, `TasksMax`, `Nice`, idle I/O). Adjust them to the VPS, then `systemctl daemon-reload` and restart.

TLS: add `deploy/Caddyfile.snippet` or `deploy/nginx.snippet` to the proxy that already serves the machine, for a name such as `api.example.com`.

yt-dlp updates weekly through `ytdlp-update.timer`.

Before choosing the default concurrency, run `sh spike/measure_host.sh` on the VPS and `python spike/probe_links.py` for a metadata-only check of public links.

## Deploy the site on Vercel

Import this repository, set the root directory to `web`, and set:

- `NEXT_PUBLIC_API_URL` to `https://api.example.com`
- `NEXT_PUBLIC_TURNSTILE_SITE_KEY` if the API has `TURNSTILE_SECRET`
- `NEXT_PUBLIC_CONTACT_EMAIL` for the takedown page

## Scope

Public single videos, reels and posts work without an account. Instagram stories need the optional per-visit Instagram sign-in, which stays on the server and is not shared between visitors. No playlists or live streams. FFmpeg, installed by the Debian setup, combines separate video and audio into one MP4 and makes the MP3. See the Terms, Privacy and takedown pages in the site.
