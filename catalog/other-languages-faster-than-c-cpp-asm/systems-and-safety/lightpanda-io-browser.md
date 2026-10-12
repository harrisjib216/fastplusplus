# Lightpanda

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `AGPL-3.0` · 🟢 active

> Zig headless browser (V8 JS, no rendering) for CDP automation; vendor crawl 9.7x faster, 16x less memory than headless Chrome.

| | |
|---|---|
| **Beats** | Headless Google Chrome 143 (Chromium, C++) driven over CDP |
| **Claimed result** | README: '16x lighter and 9x faster than Chromium'. Its table is labelled '(100 pages)', but its numbers (123MB vs 2GB, 5s vs 46s) match the BENCHMARKS.md 25-way rows: Lightpanda 25 processes 4.81 s, 123.0M versus Chrome 25 tabs 46.70 s, 2.0G (about 9.7x faster, 16x less memory, derived from page data). Other rows from the same table: 1 process versus 1 tab, 51.68 s, 27.2M versus 1:22.83, 1.3G (1.6x faster, derived from page data). 100 processes versus 100 tabs, 5.23 s, 410.2M versus 1:09.37, 4.2G (about 13x, derived from page data). Best versus best is 4.81 s versus 45.62 s for Chrome at 10 tabs (about 9.5x, derived from page data). Campfire page, 100 local loads via Puppeteer: average 16 ms versus 185 ms (total 1,698 ms versus 18,551 ms, about 11x), peak memory 21.2M versus 402.1M, peak CPU 4.6% versus 158.6%. |
| **Workload** | Crawler: a Go chromedp program crawls the Amiibo demo site (933 URLs) over the live internet. Chrome runs 1-100 tabs in one browser, while Lightpanda runs 1-100 separate processes (--fork --lpd-path), because Lightpanda cannot open multiple tabs. Each configuration ran once with /usr/bin/time -v, and smem PSS and ps CPU were sampled every 100 ms (watch -n0.1) for peak memory. Campfire: a homemade fake e-commerce page that loads two JSON XHRs, served locally, loaded 100 times via Puppeteer over CDP. |
| **Metric** | latency and memory |
| **Hardware** | AWS m5.xlarge (x86_64), fresh Ubuntu install, per BENCHMARKS.md; the CPU model appears only in a neofetch screenshot that was not read. The README calls the same crawler benchmark an m5.large. |
| **Compiler and flags** | Lightpanda commit 7b1f157cf8ccbdded7db6ab47e94577495ee87e4. The build mode is not stated; the README says Zig 0.15.2 and the Campfire section points to the nightly release binary. The baseline is the official Google Chrome binary, 143.0.7499.169 for the crawler and 143.0.7499.109 for Campfire, started with --headless=new --remote-debugging-port=9222 (crawler also --user-data-dir=/tmp/bench_chrome). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Source gives no language mechanism; README only says it is built from scratch for AI agents and automation (the speed comes from doing less work than a rendering browser). |
| **Adoption** | 36.3k stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/lightpanda-io/browser) · [benchmark](https://github.com/lightpanda-io/demo/blob/main/BENCHMARKS.md) |

## Verdict

Vendor-run in January 2026 on one AWS m5.xlarge: a Go chromedp crawler fetched the 933-page Amiibo demo site over the internet, and 25 Lightpanda processes (commit 7b1f157) took 4.81 s at 123 MB peak PSS versus 46.70 s and 2.0 GB for headless Chrome 143 with 25 tabs; one process versus one tab was 51.68 s vs 82.83 s (1.6x, derived from page data). A local Campfire page loaded 100 times through Puppeteer averaged 16 ms vs 185 ms, with Chrome also fetching CSS and images that Lightpanda skips by default.

## Use it when

- Crawling or scraping pages whose DOM is filled by JavaScript (XHR or fetch), when you need the DOM after scripts run and never need pixels.
- Dense automation fleets where Chrome's memory is the limit: the vendor table shows 27.2 MB peak PSS for one Lightpanda process against 1.3 GB for Chrome with one tab.
- One short-lived browser per worker or task: the vendor crawler forks one Lightpanda process per worker, with startup inside the timed region, and still finished first.
- LLM-agent and MCP pipelines that want page text as Markdown or DOM dumps (`fetch --dump markdown`, `lightpanda mcp`).
- Linux (glibc) or macOS on x86-64 or aarch64, from the nightly binaries or the Docker image.

## Skip it when

- Screenshots, visual regression, PDF fidelity or anything needing computed styles or geometry: there is no rendering engine, and `--dump png/pdf` is a text-only rendering.
- Sites outside its Web API and CDP coverage: the vendor built a homemade benchmark page because Lightpanda 'is not yet fully compliant', and anti-bot widgets such as Cloudflare Turnstile fail (issue #1869).
- Scripts that open several browser contexts or pages on one connection: issue #882 ('multi contexts and multi pages is not supported', open since July 2025); the benchmark itself ran N processes instead of N tabs.
- Proprietary products that embed it or offer it as a network service without meeting AGPL-3.0 terms; contributions require a CLA.
- musl (Alpine), Android or native Windows: no binaries for them (Windows only through WSL2).

## How it is fast

It skips most of what headless Chrome still does: no style, layout, paint or compositing, no GPU process and no per-site renderer processes, and `serve` by default fetches no images, stylesheets, iframes or workers (LoadResources defaults to all false in src/Config.zig). One small process holds the DOM and a V8 isolate, and release builds embed a V8 startup snapshot and are built ReleaseFast with a linker orderfile (.github/workflows/release.yml). JavaScript runs on the same V8 engine as Chrome, so the gain comes from doing less work in a lighter process model, not from Zig code generation.

## Compared with alternatives

No other headless browser is catalogued; the Zig siblings (ziggit, zroar, zipir) are unrelated tools. Pick Lightpanda only when you need page JavaScript executed into a DOM at high density and can do without rendering. It is not evidence that Zig beats C++, because both browsers run V8.

## Integration

| | |
|---|---|
| **Form** | standalone binary (CDP, WebDriver BiDi and MCP servers, fetch CLI); no embeddable library API documented |
| **Dependencies** | V8 (prebuilt archive from lightpanda-io/zig-v8-fork), libcurl, html5ever (Rust); building needs Rust, clang, make, pkg-config and glib dev headers |
| **Minimum toolchain** | Zig 0.15.2 exactly (README), plus a Rust toolchain for html5ever |
| **Platforms** | Linux x86-64 and aarch64 (glibc only), macOS x86-64 and aarch64; Windows only through WSL2; no musl or Android build |
| **Thread safety** | One browser context and page per session (issue #882); scale with processes. Current serve accepts up to 16 CDP connections by default (cdp_max_connections), and the MCP HTTP mode documents independent sessions per connection; per-connection CDP isolation is not documented. |
| **Drop-in for the baseline** | partial: Puppeteer, Playwright and chromedp scripts connect over the CDP websocket unchanged, but only a subset of CDP and Web APIs exists, nothing is rendered, and multi-context or multi-page scripts fail (#882) |

## Gotchas

- Harness asymmetry in the vendor benchmark beyond 'no rendering': Lightpanda's serve loads no images or stylesheets by default (src/Config.zig LoadResources), while Chrome does. In the Campfire test, Puppeteer's page.goto waits for the load event, which in Chrome includes style.css and the logo, cart and loading images from the local server; Lightpanda skips them. Chrome's Campfire loop also creates a fresh browser context and page every iteration, so the 185 ms vs 16 ms mixes context and renderer-process creation with page work. In the crawl, the sampled Amiibo page (03000502.json) sets an img src to a PNG on raw.githubusercontent.com that only Chrome downloads.
- The published numbers (BENCHMARKS.md commits of 2026-01-19 to 2026-01-26) were taken with crawler f2f0a8a, whose dispatch loop offered queued URLs only right after a result arrived; later commits fixed an infinite loop (7b56aae, 2026-03-27) and a deadlock (2767600, 2026-08-21). The old loop could leave pool workers idle for both browsers, and the flat curves (Lightpanda 4.81 s at 25 processes vs 5.23 s at 100; Chrome 45.6-46.7 s from 5 to 25 tabs) fit a dispatch or network ceiling rather than browser saturation. That is not proven, but the scaling rows are not clean browser-throughput numbers.
- The README headline table says '100 pages' and m5.large, but its 5 s / 123 MB vs 46 s / 2 GB are the 25-way rows of the 933-page crawl on m5.xlarge; one process versus one tab is only 1.6x faster (51.68 s vs 82.83 s). There is one run per configuration over the live internet, the Lightpanda build mode is not stated, and the CPU sampler's `ps aux | grep lightpanda` also counts the crawler process in fork mode (its command line contains ../../lightpanda).
- Usage telemetry is on by default (set LIGHTPANDA_DISABLE_TELEMETRY=true); there are no versioned releases, only a rolling nightly build.

## Known shortcomings

- Vendor benchmark with unequal work (no rendering engine); JavaScript runs on the same C++ V8 as Chrome, so no Zig effect; the one-to-one run is only 1.6x (51.68 vs 82.83 s) while the README 9x uses 25-way rows under a "(100 pages)" label; instances m5.xlarge vs m5.large; poor category fit.
- Harness flaw: serve loads no images or CSS by default (src/Config.zig LoadResources all false) while Chrome loads style.css plus images before Campfire's load event and makes a fresh context per run; each Amiibo page sets a PNG on raw.githubusercontent.com that only Chrome downloads. The numbers come from crawler f2f0a8a (2026-01-19), later fixed for an infinite loop (7b56aae, 2026-03-27) and a deadlock (2767600, 2026-08-21); the old dispatch could idle workers for both browsers, so the scaling rows are suspect.

## Caveats and trade-offs

Vendor benchmark (Lightpanda sells a cloud service), so first-party. The two browsers do unequal work: Lightpanda has 'No graphical rendering engine' (README), so it skips style, layout, paint, compositing and Chrome's GPU and renderer processes. The JavaScript runs on V8 (C++) in both browsers; Lightpanda also uses libcurl (C) for HTTP and html5ever (Rust) for HTML parsing. So the gap comes from doing less work, not from Zig codegen. The authors chose a homemade page because Lightpanda 'is not yet fully compliant'. The crawler fetches pages over the internet, so its single-process runs are network-bound (6-11% CPU). The concurrency models differ (N processes versus N tabs). There is one run per configuration with no variance. The README's '(100 pages)' label does not match the 25-way rows its numbers come from. The summary table has a typo (1:09:37 for 1:09.37). The instance size is m5.xlarge in BENCHMARKS.md but m5.large in the README. No independent reproduction was found; a Wavect write-up (WebSearch, snippet only) notes it was not reproduced. The category is a poor fit for a language-level claim. [retier] serve loads no images or CSS by default (src/Config.zig LoadResources all false) while Chrome loads style.css plus images before Campfire's load event and makes a fresh context per run; each Amiibo page sets a PNG on raw.githubusercontent.com that only Chrome downloads. The numbers come from crawler f2f0a8a (2026-01-19), later fixed for an infinite loop (7b56aae) and a deadlock (2767600); the old dispatch could idle workers for both browsers, so the scaling rows are suspect.

A new browser written from scratch for automation, not a Chromium fork; it is not a full rendering browser, so page-compatibility and Web API coverage are narrower. AGPL-3.0 licence.

## Maintenance

Very active (36.3k stars, 10,489 commits, 65 open issues, rolling nightly builds, no versioned releases); AGPL-3.0 with a CLA, fine as a standalone service binary but copyleft for embedding. The headline speedup is vendor-measured on unequal work (no rendering, no image or CSS loading) with a crawler later fixed for an infinite loop and a deadlock.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** BENCHMARKS.md in lightpanda-io/demo is the vendor's own benchmark against headless Chrome 143. The code is public (chromedp/crawler, puppeteer/cdp.js), and it gives the Lightpanda commit and the Chrome versions. The Lightpanda build mode is not stated and the CPU model appears only in a neofetch image. The company sells the product, so vendor evidence is C. WebSearch found no independent reproduction.
- **Verifier notes:** Numbers are accurate to BENCHMARKS.md. The README '9x/16x' pairs the 25-process Lightpanda run with the 25-tab Chrome run, while one-to-one it is only 1.6x faster (51.68 s vs 82.83 s). Shortcomings to record: vendor benchmark; unequal work (no rendering engine); JS on the same C++ V8 engine, so no Zig-versus-C++ effect; a network-bound single run; mismatched instance size and labels; Lightpanda not fully web-compliant. Metadata is confirmed: AGPL-3.0, 36.3k stars, last commit 2026-10-11. Out of scope for the wave's language-level framing, but kept per the keep-and-document rule; the orchestrator may want a category override.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-14 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/lightpanda-io/demo/blob/main/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/lightpanda-io/demo/main/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/lightpanda-io/browser/main/README.md>
  - <https://github.com/lightpanda-io/browser>
  - <https://github.com/lightpanda-io/browser/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/lightpanda-io/browser/main/README.md>
  - <https://raw.githubusercontent.com/lightpanda-io/demo/main/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/lightpanda-io/demo/main/README.md>
  - <https://raw.githubusercontent.com/lightpanda-io/demo/main/chromedp/crawler/main.go>
  - <https://raw.githubusercontent.com/lightpanda-io/demo/f2f0a8a/chromedp/crawler/main.go>
  - <https://raw.githubusercontent.com/lightpanda-io/demo/main/puppeteer/cdp.js>
  - <https://raw.githubusercontent.com/lightpanda-io/demo/main/puppeteer/helpers.js>
  - <https://raw.githubusercontent.com/lightpanda-io/demo/main/public/amiibo/index.html>
  - <https://raw.githubusercontent.com/lightpanda-io/demo/main/public/amiibo/load.js>
  - <https://raw.githubusercontent.com/lightpanda-io/demo/main/public/amiibo/03000502.json>
  - <https://raw.githubusercontent.com/lightpanda-io/demo/main/public/campfire-commerce/index.html>
  - <https://raw.githubusercontent.com/lightpanda-io/browser/main/src/Config.zig>
  - <https://raw.githubusercontent.com/lightpanda-io/browser/main/Makefile>
  - <https://raw.githubusercontent.com/lightpanda-io/browser/main/.github/workflows/release.yml>
  - <https://github.com/lightpanda-io/demo/commits/main/chromedp/crawler/main.go>
  - <https://github.com/lightpanda-io/demo/commits/main/BENCHMARKS.md>
  - <https://github.com/lightpanda-io/browser>
  - <https://github.com/lightpanda-io/browser/issues?q=is%3Aissue+is%3Aopen+crash>
  - <https://github.com/lightpanda-io/browser/issues/882>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/lightpanda-io/browser`) · [data/wave14/enrich/raw/github_com_lightpanda_io_browser.json](../../../data/wave14/enrich/raw/github_com_lightpanda_io_browser.json) (enrichment confidence 0.7)

</details>
