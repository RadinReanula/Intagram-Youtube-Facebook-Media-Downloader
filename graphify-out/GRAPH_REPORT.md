# Graph Report - Media_Downloader  (2026-11-13)

## Corpus Check
- 86 files · ~16,906 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 487 nodes · 977 edges · 34 communities (26 shown, 8 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 203 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b1b27a97`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

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
- page.tsx
- page.tsx
- page.tsx
- next.config.ts
- next-env.d.ts
- postcss.config.mjs
- test_auth.py
- __init__.py

## God Nodes (most connected - your core abstractions)
1. `get_settings()` - 33 edges
2. `ApiError` - 28 edges
3. `JobStore` - 26 edges
4. `SessionStore` - 21 edges
5. `create_download()` - 19 edges
6. `Settings` - 17 edges
7. `run_download()` - 16 edges
8. `compilerOptions` - 16 edges
9. `analyze_url()` - 15 edges
10. `unsupported()` - 14 edges

## Surprising Connections (you probably didn't know these)
- `_enable()` --calls--> `reset_pending()`  [INFERRED]
  api/tests/test_auth.py → api/app/auth/instagram.py
- `test_ytdlp_errors_map_to_plain_codes()` --calls--> `map_ytdlp_error()`  [INFERRED]
  api/tests/test_security.py → api/app/platforms/ytdlp.py
- `session_dir()` --calls--> `get_settings()`  [INFERRED]
  api/app/auth/cookies.py → api/app/config.py
- `lifespan()` --calls--> `session_dir()`  [INFERRED]
  api/app/main.py → api/app/auth/cookies.py
- `run_download()` --calls--> `job_cookie_path()`  [INFERRED]
  api/app/jobs/runner.py → api/app/auth/cookies.py

## Import Cycles
- None detected.

## Communities (34 total, 8 thin omitted)

### Community 0 - "Downloader.tsx"
Cohesion: 0.07
Nodes (49): Downloader(), ErrorNotice(), FormatPicker(), Props, spring, JobIcon(), StepCheck(), InstagramAccount() (+41 more)

### Community 1 - "models.py"
Cohesion: 0.08
Nodes (30): AnalyzeRequest, AnalyzeResult, FormatOption, JobCreate, JobView, MediaItem, BaseModel, Platform (+22 more)

### Community 2 - "errors.py"
Cohesion: 0.15
Nodes (22): blocked(), limit_exceeded(), _largest(), _link_or_copy(), _merge_streams(), Path, Pick the finished media files. A zip is only for a multi-item download., run_download() (+14 more)

### Community 3 - "get_settings"
Cohesion: 0.11
Nodes (20): get_settings(), _load_settings(), Limits and paths. Change them in the environment, not in code., set_settings(), Settings, directory_size(), ensure_capacity(), Path (+12 more)

### Community 4 - "devDependencies"
Cohesion: 0.06
Nodes (32): motion, next, postcss, react, react-dom, tailwindcss, @tailwindcss/postcss, @tanstack/react-query (+24 more)

### Community 5 - "JobStore"
Cohesion: 0.13
Nodes (13): Any, cleanup_loop(), cleanup_once(), datetime, Path, _remove_empty(), _remove_stale_work(), iso() (+5 more)

### Community 6 - "ApiError"
Cohesion: 0.09
Nodes (44): ApiError, busy(), invalid_link(), login_required(), not_found(), private_content(), Exception, unsupported() (+36 more)

### Community 7 - "compilerOptions"
Cohesion: 0.07
Nodes (28): ./*, dom, dom.iterable, esnext, next-env.d.ts, .next/types/**/*.ts, node_modules, **/*.ts (+20 more)

### Community 8 - "main.py"
Cohesion: 0.20
Nodes (18): configure_logging(), RedactIpFilter, truncate_ip(), access_log(), api_error_handler(), create_app(), guard_errors(), lifespan() (+10 more)

### Community 9 - "create_download"
Cohesion: 0.15
Nodes (23): _client(), _login_sync(), PendingLogin, _purge(), reset_pending(), _settings(), sign_in(), sign_out() (+15 more)

### Community 10 - "TtlCache"
Cohesion: 0.22
Nodes (3): TtlCache, get_metadata_cache(), client()

### Community 12 - "layout.tsx"
Cohesion: 0.20
Nodes (6): instrument, metadata, DownloadMark(), Providers(), SiteFooter(), SiteHeader()

### Community 13 - "Media Downloader"
Cohesion: 0.33
Nodes (5): Deploy the API on Debian, Deploy the site on Vercel, Local development, Media Downloader, Scope

### Community 14 - "probe_links.py"
Cohesion: 0.60
Nodes (4): main(), probe(), Metadata-only extraction probe. Does not download media files.  Run from the r, ytdlp()

### Community 19 - "page.tsx"
Cohesion: 0.20
Nodes (6): public_state(), Request, session_hash(), SessionRecord, SessionStore, Fernet

### Community 20 - "page.tsx"
Cohesion: 0.21
Nodes (11): clear_session_files(), discard_cookie(), discard_job_cookie(), job_cookie_path(), Path, session_dir(), temporary_cookie(), write_cookie_file() (+3 more)

### Community 31 - "test_auth.py"
Cohesion: 0.61
Nodes (8): _enable(), _headers(), _ok(), test_login_cookie_and_log_hygiene(), test_login_rate_limit(), test_origin_is_required(), test_sessions_do_not_share_jobs_or_cache(), test_user_agent_and_idle_expiry()

## Knowledge Gaps
- **61 isolated node(s):** `install.sh script`, `measure_host.sh script`, `instrument`, `metadata`, `spring` (+56 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `get_settings` to `models.py`, `errors.py`, `ApiError`, `main.py`, `create_download`, `page.tsx`, `page.tsx`, `test_auth.py`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `JobStore` connect `JobStore` to `main.py`, `errors.py`, `page.tsx`, `ApiError`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `ApiError` connect `ApiError` to `errors.py`, `get_settings`, `main.py`, `create_download`, `page.tsx`, `page.tsx`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `get_settings()` (e.g. with `session_dir()` and `assert_origin()`) actually correct?**
  _`get_settings()` has 30 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `ApiError` (e.g. with `_login_sync()` and `PendingLogin`) actually correct?**
  _`ApiError` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `JobStore` (e.g. with `JobManager` and `lifespan()`) actually correct?**
  _`JobStore` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `SessionStore` (e.g. with `Settings` and `ApiError`) actually correct?**
  _`SessionStore` has 2 INFERRED edges - model-reasoned connections that need verification._