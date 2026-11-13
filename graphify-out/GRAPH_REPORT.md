# Graph Report - Media_Downloader  (2026-11-13)

## Corpus Check
- 73 files · ~12,068 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 386 nodes · 704 edges · 31 communities (25 shown, 6 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 137 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Downloader.tsx
- models.py
- errors.py
- get_settings
- devDependencies
- JobStore
- ApiError
- compilerOptions
- main.py
- create_download
- TtlCache
- layout.tsx
- Media Downloader
- probe_links.py
- install.sh
- measure_host.sh
- SPIKE.md
- next.config.ts
- next-env.d.ts
- postcss.config.mjs

## God Nodes (most connected - your core abstractions)
1. `JobStore` - 26 edges
2. `get_settings()` - 22 edges
3. `ApiError` - 19 edges
4. `compilerOptions` - 16 edges
5. `run_download()` - 15 edges
6. `create_download()` - 15 edges
7. `Settings` - 14 edges
8. `unsupported()` - 13 edges
9. `analyze_url()` - 13 edges
10. `create_app()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `test_ytdlp_errors_map_to_plain_codes()` --calls--> `map_ytdlp_error()`  [INFERRED]
  api/tests/test_security.py → api/app/platforms/ytdlp.py
- `run_download()` --calls--> `get_settings()`  [INFERRED]
  api/app/jobs/runner.py → api/app/config.py
- `create_app()` --calls--> `get_settings()`  [INFERRED]
  api/app/main.py → api/app/config.py
- `lifespan()` --calls--> `get_settings()`  [INFERRED]
  api/app/main.py → api/app/config.py
- `social_items()` --calls--> `get_settings()`  [INFERRED]
  api/app/platforms/social.py → api/app/config.py

## Import Cycles
- None detected.

## Communities (31 total, 6 thin omitted)

### Community 0 - "Downloader.tsx"
Cohesion: 0.09
Nodes (33): Downloader(), ErrorNotice(), FormatPicker(), Props, spring, JobStatus(), PlatformBadge(), PreviewCard() (+25 more)

### Community 1 - "models.py"
Cohesion: 0.08
Nodes (30): AnalyzeRequest, AnalyzeResult, FormatOption, JobCreate, JobView, MediaItem, Platform, MediaItem (+22 more)

### Community 2 - "errors.py"
Cohesion: 0.10
Nodes (27): blocked(), limit_exceeded(), private_content(), JobManager, _largest(), _link_or_copy(), _merge_streams(), Path (+19 more)

### Community 3 - "get_settings"
Cohesion: 0.10
Nodes (24): get_settings(), _load_settings(), Limits and paths. Change them in the environment, not in code., set_settings(), Settings, busy(), invalid_link(), directory_size() (+16 more)

### Community 4 - "devDependencies"
Cohesion: 0.06
Nodes (32): motion, next, postcss, react, react-dom, tailwindcss, @tailwindcss/postcss, @tanstack/react-query (+24 more)

### Community 5 - "JobStore"
Cohesion: 0.13
Nodes (13): Any, cleanup_loop(), cleanup_once(), datetime, Path, _remove_empty(), _remove_stale_work(), iso() (+5 more)

### Community 6 - "ApiError"
Cohesion: 0.13
Nodes (24): ApiError, Exception, unsupported(), detect(), Detection, _facebook(), _instagram(), _youtube() (+16 more)

### Community 7 - "compilerOptions"
Cohesion: 0.07
Nodes (28): ./*, dom, dom.iterable, esnext, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+20 more)

### Community 8 - "main.py"
Cohesion: 0.20
Nodes (17): configure_logging(), RedactIpFilter, truncate_ip(), access_log(), api_error_handler(), create_app(), lifespan(), Exception (+9 more)

### Community 9 - "create_download"
Cohesion: 0.27
Nodes (12): not_found(), cancel_job(), create_job(), download_job(), JobView, Request, read_job(), create_download() (+4 more)

### Community 10 - "TtlCache"
Cohesion: 0.22
Nodes (3): TtlCache, get_metadata_cache(), client()

### Community 12 - "layout.tsx"
Cohesion: 0.31
Nodes (4): metadata, Providers(), SiteFooter(), SiteHeader()

### Community 13 - "Media Downloader"
Cohesion: 0.33
Nodes (5): Deploy the API on Debian, Deploy the site on Vercel, Local development, Media Downloader, Scope

### Community 14 - "probe_links.py"
Cohesion: 0.60
Nodes (4): main(), probe(), Metadata-only extraction probe. Does not download media files.  Run from the r, ytdlp()

## Knowledge Gaps
- **55 isolated node(s):** `install.sh script`, `measure_host.sh script`, `metadata`, `spring`, `Props` (+50 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `get_settings` to `models.py`, `errors.py`, `ApiError`, `main.py`, `create_download`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `JobStore` connect `JobStore` to `main.py`, `create_download`, `errors.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `run_download()` connect `errors.py` to `get_settings`, `JobStore`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `JobStore` (e.g. with `JobManager` and `lifespan()`) actually correct?**
  _`JobStore` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `get_settings()` (e.g. with `.__init__()` and `._worker()`) actually correct?**
  _`get_settings()` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `ApiError` (e.g. with `JobManager` and `api_error_handler()`) actually correct?**
  _`ApiError` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `run_download()` (e.g. with `._worker()` and `get_settings()`) actually correct?**
  _`run_download()` has 10 INFERRED edges - model-reasoned connections that need verification._