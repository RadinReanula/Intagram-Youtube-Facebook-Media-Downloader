# Extraction spike

Recorded on 13 November 2026 from the development machine (Windows, 8 CPUs, about 25 GB free on the working disk). The Debian VPS was not available in this session, so CPU, RAM, disk and bandwidth on the server still need `spike/measure_host.sh` before the concurrency default is tightened. The probe does not download media files. It only asks yt-dlp for metadata. yt-dlp 2026.10.26. No cookies and no login were used.

| Platform | Sample | Result | Time |
| --- | --- | --- | --- |
| YouTube video | `watch?v=jNQXAC9IVRw` | Title, uploader, duration, thumbnail, video and audio formats | 143 s, then 21 s on the next YouTube link |
| YouTube short URL | `shorts/aqz-KE-bpKQ` | Metadata returned. This particular short URL is a 10 minute film, so the short pattern is recognised separately from the media itself | 21 s |
| Instagram reel and post | `C8Q3p0sR0aA` | Empty media response. yt-dlp asked for a login | 14–18 s |
| Instagram story | `/stories/instagram/` | Explicit login required | 11 s |
| Facebook video and reel | Facebook's own "How to Share With Just Friends" | Title, uploader and duration returned. The listed formats had no video or audio codec, so a real download of this sample may still fail | 9–11 s |

Decision for the first release:

- YouTube video, short, and audio metadata work without a login.
- Instagram stories are not offered. They require a login, and the service does not store or send cookies.
- Other Instagram links stay in the product, with a plain error when the platform demands a login. The sample post and reel were not readable without one.
- Facebook public video metadata can be read. Treat a result that has a duration as video even when the codec fields are empty.
- The first YouTube lookup was far slower than the 5 second goal. Later lookups were closer. Keep the analyse timeout generous, and set the reverse-proxy read timeout to at least 300 seconds.

Run `spike/measure_host.sh` on the VPS and keep `MAX_CONCURRENT_JOBS` at 1 until that measurement says there is spare CPU and RAM.
