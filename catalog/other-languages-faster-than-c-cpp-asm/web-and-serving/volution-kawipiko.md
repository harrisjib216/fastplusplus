# kawipiko

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `AGPL-3.0-or-later` · 🟢 active

> Go static-site server that serves a prebuilt CDB archive from memory over fasthttp; author measured 1.22-1.34x NGINX request rate.

| | |
|---|---|
| **Beats** | NGINX (distribution package; configuration in the kawipiko examples/nginx folder), also darkhttpd |
| **Claimed result** | Hello World over loopback, 2 server threads, 2 wrk threads: kawipiko 106,698.89 / 100,296.65 / 95,628.34 / 53,548.52 req/s at 512 / 2048 / 4096 / 16384 connections (section 'Last updated in August 2018') vs NGinx 79,816.08 / 78,211.46 / 75,970.82 / 43,909.67 (section 'Last updated in August 2019'), 1.34x / 1.28x / 1.26x / 1.22x (derived from page data, pairing the two separately dated sections). OpenStreetMap tile run (one section, August 2019, i7 4770, 8 threads, 16384 connections, 2 minutes): kawipiko --archive-inmem 238,499.86 req/s, --archive-mmap 237,239.35, 8 processes mmap 248,266.83 vs NGinx 8 workers 188,255.32 (1.27x / 1.26x / 1.32x, derived); the author states \~25% more requests/s, \~29% lower average latency, \~40% lower p90 latency, \~25% less CPU per request, while NGinx used the least RAM and kawipiko about 1 GiB. The summary (December 2021) calls kawipiko 'at least on-par with NGinx'. |
| **Workload** | Static 'Hello World!' file served from a CDB archive held in memory (kawipiko) or from tmpfs (NGINX), wrk over loopback with keep-alive, 512 to 16384 connections; plus a 250k-file OpenStreetMap tile set at 16384 connections. |
| **Metric** | throughput |
| **Hardware** | Laptop with Intel Core i7 3667U (2 physical cores, 4 threads), 8 GiB RAM for the Hello World runs; desktop Intel Core i7 4770 (4 cores, 8 threads), 32 GiB for the tile run; wrk and server pinned to separate physical cores, tmpfs. |
| **Compiler and flags** | Go build of kawipiko (version and flags not stated); NGINX from distribution packages (version and build flags not stated); server run with --archive-inmem, --security-headers-disable and --timeout-disable. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Content pre-indexed in a CDB archive held in memory with a compact lookup (no per-request file system calls), on Go fasthttp; the README says the advantage grows for many small files accessed in random patterns. |
| **Adoption** | 397 stars |
| **Last commit** | 2026-08-15 |
| **Links** | [repository](https://github.com/volution/kawipiko) · [benchmark](https://raw.githubusercontent.com/volution/kawipiko/development/documentation/readme/benchmarks.rst) |

## Verdict

Author-run wrk over loopback with server and client pinned to separate physical cores, 'Hello World!' from tmpfs: kawipiko (2 threads, 2018 run) 106,699 / 100,297 / 95,628 / 53,549 req/s vs a distribution-package NGINX with 2 workers (2019 run) 79,816 / 78,211 / 75,971 / 43,910 req/s at 512 / 2048 / 4096 / 16384 connections on an i7-3667U laptop (1.22-1.34x across runs a year apart); the same-session OpenStreetMap tile run on an i7-4770 desktop gave 238,500 vs 188,255 req/s (1.27x) at 16384 connections. Go and NGINX versions and build flags are not stated.

## Use it when

- Self-hosting a static site or tile set made of many small files (the author's OpenStreetMap case: \~250k PNGs, median 103 bytes) where per-file syscalls and inode overhead dominate.
- Deployments that want atomic publish and rollback: build one archive in CI, swap it with rename, restart.
- Plain HTTP/1.1 or HTTPS over HTTP/1.1 behind a CDN or load balancer, where fasthttp's path is the fast one.
- Small static-only hosts (Linux, FreeBSD, OpenBSD, macOS) that want a single statically linked binary and no config files.

## Skip it when

- HTTP/2-heavy traffic: the author measured kawipiko's HTTP/2 (Go net/http) at about one sixth of its HTTP/1-over-TLS rate, while NGINX's HTTP/2 was close to its HTTP/1 rate.
- Content that changes often, needs per-client content negotiation (it sends the archive's encoding regardless of Accept-Encoding), custom headers, auth, proxying or more than 4 GiB / 16M resources.
- Workloads that need correct HTTP caching semantics: the fasthttp path sets NoDefaultDate, so responses carry no Date header (RFC 9110 requires one from origin servers with a clock), and no conditional-GET (304) or Range handling appears in the server source.
- Memory-tight hosts: the tile run used about 1 GiB RAM for kawipiko while NGINX used the least; --archive-inmem also copies the archive into each process.
- Strict latency targets at high connection counts: in the author's own Hello World rows NGINX had lower average and p99 latency at 2048 and 4096 connections.

## How it is fast

Every resource lives in one CDB file that is loaded into RAM (--archive-inmem) or memory-mapped (--archive-mmap), so a request does no open/read/close syscalls; optional in-RAM indexes (--index-paths, --index-data-meta, --index-data-content) remove even the CDB hash lookups. Response headers are stored precomputed in the archive and bodies are pre-compressed at build time, and the handler copies the request path into stack buffers and hands the archive bytes to fasthttp with SetBodyRaw, avoiding heap allocations. Duplicate files are stored once, which helped the OpenStreetMap tile run (about 250k tiles became about 100k entries).

## Compared with alternatives

Pick kawipiko for serving a fixed static site or tile set from one immutable archive; the HttpArena siblings (vanilla, zix, zeemo, tokio-uring and others) beat a custom NGINX handler module on synthetic dynamic endpoints and are frameworks rather than static servers, and cblt is the closer static-file sibling but its NGINX comparison is a Docker image under ab.

## Integration

| | |
|---|---|
| **Form** | static binary (kawipiko-server, kawipiko-archiver, all-in-one kawipiko); Go module source |
| **Dependencies** | fasthttp v1.40.0, a fork of colinmarc/cdb with mmap support (cipriancraciun/go-cdb-lib), andybalholm/brotli, go-zopfli, zeebo/blake3, bbolt (archiver cache), golang.org/x/sys |
| **Minimum toolchain** | Go 1.17 per go.mod (prebuilt v0.1.0 preview binaries for linux/freebsd/openbsd x86_64 and darwin x86_64/aarch64) |
| **Platforms** | Linux (main platform), FreeBSD, OpenBSD, macOS; x86-64 and arm64 builds |
| **Thread safety** | Read-only archive shared lock-free by all goroutines; scale with --threads per process or several --processes (use --archive-mmap then, since --archive-inmem copies the archive per process). |
| **Drop-in for the baseline** | partial — it replaces an NGINX static docroot only after archiving the site; GET-only, no per-request compression, no reload without restart, and different response headers (no Date, Server or Last-Modified). |

## Gotchas

- Harness flaw: the Hello World ratios pair kawipiko rows labelled August 2018 with NGINX rows labelled August 2019, and the NGINX config the page links (examples/nginx/nginx.conf) was first committed on 2021-12-23, two years after the NGINX runs, with non-default settings (sendfile off, tcp_nodelay off, open_file_cache max=2048, far below the \~250k tile files); the tile run's per-path wrk Lua script is loaded from a separate kawipiko-examples repo (scripts/benchmark.z-run) that returned 404 here, so neither comparison can be rerun as measured.
- The higher request rate comes with worse tails in the same table: at 2048 connections kawipiko averaged 45.42 ms (p99 417.40 ms) vs NGINX 27.11 ms (p99 126.97 ms); at 4096 connections p99 745.94 ms vs 339.05 ms, with 4,449 vs 187 requests past wrk's 1 s timeout dropped from the histogram. Those kawipiko rows are also internally inconsistent: the mean latency times the request count exceeds connections times duration by 2.2x and 2.1x (Little's law, derived from page data), which a one-request-per-connection wrk run cannot produce.
- The responses were not equivalent: kawipiko ran with --security-headers-disable and --timeout-disable and sends no Date, Server or Last-Modified headers, so wrk read about 169 bytes per response from kawipiko vs 263 from NGINX (derived from page data); the author says timeouts alone cost 10-15%.
- Request paths are not percent-decoded (a FIXME in sources/cmd/server/server.go), so URLs with escaped characters must match the archive keys literally; experimental QUIC/HTTP/3 and seccomp support were removed on 2026-08-15.

## Known shortcomings

- The 1.34x Hello World ratio pairs August 2018 kawipiko rows with August 2019 NGinx rows (cross-run); only the 1.27x tile run is same-session; timeouts and security headers off; more wrk timeouts than NGinx at 4096 connections; 2013-era CPUs; the author claims only 'at least on-par'.
- The linked nginx.conf was first committed 2021-12-23, two years after the 2019 NGINX runs, with non-default settings (sendfile off, tcp_nodelay off, open_file_cache max=2048 against about 250k tiles); the tile wrk Lua script in kawipiko-examples returns 404. At 2048 and 4096 connections NGINX had the better p99 (126.97 vs 417.40 ms; 339.05 vs 745.94 ms), and those kawipiko latency rows break Little's law by 2.2x/2.1x. Responses are not equivalent (no Date, Server or Last-Modified; 169 vs 263 bytes per response); paths are not percent-decoded (FIXME); QUIC and seccomp were removed 2026-08-15.

## Caveats and trade-offs

First-party, measured on 2013-era CPUs (i7 3667U laptop, i7 4770 desktop) with an older kawipiko version (the author says the current one is at least 10% more efficient). The Hello World kawipiko rows (August 2018) and NGinx rows (August 2019) are in separately dated sections, so the 1.22-1.34x ratios compare runs a year apart; only the tile run is a same-session comparison. kawipiko was requested at '/' and NGinx at '/index.txt' (the author chose the path he says favours NGinx). NGinx is a distribution package with an author-tuned config (examples/nginx); kawipiko ran with --archive-inmem, --security-headers-disable and --timeout-disable (the author says timeouts cost 10-15%). wrk reports socket errors for kawipiko at every row from 512 connections (timeouts 86 / 4,449 / 2,288 at 2048 / 4096 / 16384, versus NGinx 11 / 187 / 1,121) and in both tile runs (kawipiko 7,032 timeouts, NGinx 16,833). The tile CDB was deduplicated to \~100k of \~250k files, and the wrk command shown targets a single URL, so how the tile list was driven is not shown. The author says kawipiko over HTTP/2 is about 6x slower than its own HTTPS over HTTP/1, where NGinx is not. The author says the real advantage is deployment simplicity. The win comes from the CDB in-memory design on fasthttp, not from Go versus C codegen. [retier] The linked nginx.conf was first committed 2021-12-23, two years after the 2019 NGINX runs, with sendfile off, tcp_nodelay off and open_file_cache max=2048 against about 250k tiles; the tile wrk Lua script returns 404. At 2048 and 4096 connections NGINX had the better p99 (126.97 vs 417.40 ms; 339.05 vs 745.94 ms), and the kawipiko latency rows break Little's law by about 2x. Responses are not equivalent (no Date, Server or Last-Modified; 169 vs 263 bytes); QUIC and seccomp were removed 2026-08-15.

Serves only a prebuilt CDB archive, so content changes need a rebuild; HTTP/2 is about 6 times slower than its HTTP/1 path (Go net/http), where the author says NGINX is much better; kawipiko used about 1 GiB RAM in the tile run while NGINX used the least; AGPL licence.

## Maintenance

Single-author project, AGPL-3.0-or-later, 397 stars, last commits 2026-08-15 (removing QUIC and seccomp), dependencies pinned to 2022 versions (fasthttp v1.40.0, Go 1.17); the author reports it serving about 600k pages in production, but the benchmarks date from 2018-2019 and have not been rerun against current NGINX.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party wrk numbers in documentation/readme/benchmarks.rst match the record (kawipiko 106,698.89 / 100,296.65 / 95,628.34 / 53,548.52 vs NGinx 79,816.08 / 78,211.46 / 75,970.82 / 43,909.67; tiles 238,499.86 vs 188,255.32); kawipiko's Go version and flags and NGinx's version and build are not stated, so C.
- **Verifier notes:** Numbers match benchmarks.rst; tier C stands (first-party, Go and NGinx builds unstated). Shortcomings: the Hello World ratio pairs kawipiko rows from August 2018 with NGinx rows from August 2019 (cross-run), only the 1.27x tile run is same-session; timeouts and security headers disabled for kawipiko; more wrk timeouts for kawipiko than NGinx at 4096 connections; 2013-era CPUs, old version; the author calls it 'at least on-par'.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-52 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/volution/kawipiko/development/documentation/readme/benchmarks.rst>
  - <https://github.com/volution/kawipiko>
  - <https://github.com/volution/kawipiko/commits/development>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/volution/kawipiko/development/documentation/readme/benchmarks.rst>
  - <https://raw.githubusercontent.com/volution/kawipiko/development/documentation/readme/readme.rst>
  - <https://raw.githubusercontent.com/volution/kawipiko/development/documentation/readme/installation.rst>
  - <https://raw.githubusercontent.com/volution/kawipiko/development/documentation/manuals/server.txt>
  - <https://raw.githubusercontent.com/volution/kawipiko/development/sources/go.mod>
  - <https://raw.githubusercontent.com/volution/kawipiko/development/sources/cmd/server/server.go>
  - <https://raw.githubusercontent.com/volution/kawipiko/development/sources/cmd/server.go>
  - <https://raw.githubusercontent.com/volution/kawipiko/development/examples/nginx/nginx.conf>
  - <https://raw.githubusercontent.com/volution/kawipiko/development/scripts/benchmark.z-run>
  - <https://raw.githubusercontent.com/volution/kawipiko-examples/development/sources/wrk-paths-from-file.lua>
  - <https://github.com/volution/kawipiko>
  - <https://github.com/volution/kawipiko/tree/development/documentation/readme>
  - <https://github.com/volution/kawipiko/tree/development/examples/nginx>
  - <https://github.com/volution/kawipiko/tree/development/sources/lib/server>
  - <https://github.com/volution/kawipiko/tree/development/scripts>
  - <https://github.com/volution/kawipiko/commits/development/examples/nginx/nginx.conf>
  - <https://github.com/volution/kawipiko/commits/development>
  - <https://github.com/volution/kawipiko/issues?q=is%3Aissue>
  - <https://github.com/volution/kawipiko/issues/5>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/volution/kawipiko`) · [data/wave14/enrich/raw/github_com_volution_kawipiko.json](../../../data/wave14/enrich/raw/github_com_volution_kawipiko.json) (enrichment confidence 0.7)

</details>
