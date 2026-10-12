# epoll-httpd

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Small Linux-only C++17 static-file HTTP/1.1 server on raw epoll; \~1.4-1.6x single-worker nginx on 1-8 KB files.

| | |
|---|---|
| **Beats** | nginx |
| **Claimed result** | \~1.6x nginx headline (1KB file: 152,931 vs 96,792 req/s = 1.58x; index.html: 151,453 vs 82,510 = 1.84x; 8KB: 123,950 vs 89,014 = 1.39x; 64KB: parity at 0.94x); resident memory 4.1-5.2MB vs nginx's 10.4-10.5MB; across 4 repeated runs the 1KB ratio held 1.51x-1.67x and 8KB held 1.36x-1.42x (verbatim from README table, with author-documented run-to-run variance) |
| **Workload** | Static file serving over wrk (50 connections, 10s, server/client pinned to separate cores) for /index.html, 1KB, 8KB, and 64KB files, with nginx configured to match ehttpd's feature set (sendfile, keep-alive, open-file cache, no logging/gzip). |
| **Metric** | throughput |
| **Hardware** | Intel Xeon @ 2.10 GHz, 2 cores, Linux 6.18 (exact Xeon SKU not stated) |
| **Compiler and flags** | CMake Release, CMAKE_CXX_FLAGS_RELEASE="-O2 -DNDEBUG" (from CMakeLists.txt); compiler name/version (gcc vs clang) not pinned or stated |
| **Adoption** | 0 stars |
| **Last commit** | 2026-08-08 |
| **Links** | [repository](https://github.com/SapnilPatel/epoll-httpd) · [benchmark](https://github.com/SapnilPatel/epoll-httpd/blob/main/README.md) |

## Verdict

The author's bench/run.sh ran one ehttpd worker against one nginx worker (version not stated; sendfile, keep-alive and open-file cache on, logging and gzip off) on a 2-core Intel Xeon @ 2.10 GHz under Linux 6.18, with a single wrk thread at 50 connections for 10 s over loopback, and got 152,931 vs 96,792 req/s on 1 KB (1.58x; 1.51x-1.67x over four runs), 1.39x on 8 KB, 0.94x on 64 KB and under half nginx's RSS, built with -O2 -DNDEBUG on an unnamed compiler. The numbers are first-party, response headers were not equalized (ehttpd sends no Date header), and both of ehttpd's small-file rows sit near 151-153k req/s, which may mean the single wrk thread was close to its own limit.

## Use it when

- Serving a small set of hot, small (roughly 1-8 KB) static files over plain HTTP/1.1 on Linux, where per-request CPU cost is what limits you
- Behind a TLS-terminating load balancer or CDN, as a minimal static origin that needs only GET/HEAD, keep-alive and ETag revalidation
- Memory-constrained boxes or sidecars: the author measured 4.1-5.2 MB RSS under load vs 10.4-10.5 MB for single-worker nginx
- As a readable reference for a reactor-per-core epoll/SO_REUSEPORT/sendfile server: about 1,700 lines of C++ plus about 820 lines of tests, with design notes, and CI runs ASan and TSan jobs

## Skip it when

- Payloads of 64 KB and up: the author measured parity with nginx (0.94x-1.02x), so there is nothing to gain
- Anything beyond bare static files: no TLS, HTTP/2, request bodies (non-zero Content-Length gives 413, Transfer-Encoding gives 501), proxying, CGI, gzip, virtual hosts, access logs, IPv6 or non-Linux platforms
- Media or download serving: no Range requests (per the source) and only 14 file extensions get a MIME type; .mp4, .pdf, .xml, .woff and others go out as application/octet-stream
- Document roots larger than the page cache: open(), pread() and sendfile() run on the event-loop thread, so a cold disk read stalls every connection on that worker, and SO_REUSEPORT gives no work stealing
- Production use that needs a track record: 0 stars, no releases or tags, no issues filed, and all 13 commits were pushed together on 2026-08-08

## How it is fast

Each worker thread owns its own SO_REUSEPORT listener and edge-triggered epoll loop, so connections never cross threads and there are no locks (shared-nothing reactor-per-core). Bodies of 8 KB or less are pread into the response buffer and sent with the header in one send() call, which the author's threshold sweep measured at +44% at 1 KB and +26% at 8 KB over always using sendfile; larger bodies use sendfile(2). A per-worker open-file-descriptor cache (fstat revalidation on a 2 s TTL) removes open/fstat/close from hot requests, and a resumable byte-at-a-time parser records offsets and returns string_views, so parsing does no heap allocation.

## Compared with alternatives

Pick it over uhttp when you cannot rely on io_uring: uhttp needs liburing 2.5+ and C++20, while ehttpd needs only epoll and C++17; uhttp's benchmark is stronger, though (wrk on 6 cores, 3 interleaved runs, byte-matched headers, +40-54% vs tuned nginx). Pick H2O instead whenever you need a real server (HTTP/2, experimental HTTP/3, library mode); the framework siblings (Drogon, Crow, Lwan, Sogou Workflow) serve dynamic handlers, which ehttpd does not have at all.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond libc and pthreads; CMake 3.16+ to build; wrk and nginx only for the benchmark script |
| **Minimum toolchain** | C++17, CMake 3.16; CI builds with the gcc and clang on GitHub's ubuntu-latest image (versions not pinned) |
| **Platforms** | Linux only (epoll, sendfile, timerfd, eventfd, accept4, SO_REUSEPORT); IPv4 only |
| **Thread safety** | Shared-nothing: each worker thread owns its listener, connections, file cache and timer wheel, with no locks; README reports a clean ThreadSanitizer run and CI runs a TSan job |
| **Drop-in for the baseline** | partial — it replaces an nginx 'root + sendfile + keep-alive' static location only; nothing in an nginx config carries over, and TLS, Range, gzip, logging, proxying and virtual hosts are all missing |

## Gotchas

- The file cache revalidates by fstat() on the descriptor it already holds, so a file replaced by rename (atomic deploys) or deleted keeps being served from the old inode until eviction or restart; only in-place edits that change mtime (second granularity) or size are picked up
- Every worker binds with SO_REUSEPORT, so starting a second ehttpd on a port already in use does not fail; the kernel silently splits connections between the two processes (the author's integration test works around exactly this)
- The listening socket is registered level-triggered and accept_batch() just returns on EMFILE/ENFILE, so running out of file descriptors likely makes the worker spin in epoll_wait at full CPU until descriptors free up (read from the code, not tested)
- HTTP semantics are minimal: If-None-Match must equal the ETag string exactly (no list, W/ or \*), If-Modified-Since is ignored although Last-Modified is sent, responses carry no Date or Cache-Control header, a directory path without a trailing slash returns 403 instead of a redirect, and keep-alive connections close after 10,000 requests

## Known shortcomings

- First-party benchmark: nginx version and compiler not named; load from a single wrk thread, and ehttpd's small-file rows plateau near 151-153k req/s, so the client may be the limit; ehttpd sends no Date header, so responses are not equalized. Single push of 13 commits (2026-08-08), no releases or issues, 0 stars. The file cache rechecks by fstat on the held descriptor, so files replaced by rename or deleted keep being served until eviction. With SO_REUSEPORT a second instance binds silently and splits traffic. On EMFILE/ENFILE the level-triggered listener likely spins (from code reading). No Range, If-Modified-Since ignored, no Date/Cache-Control, 14 MIME types, directory without slash gets 403, GET/HEAD only. open/pread/sendfile block the event-loop thread. No TLS, HTTP/2, IPv6; Linux only; parity with nginx at 64 KB.

## Caveats and trade-offs

First-party benchmark (project's own bench/run.sh; numbers in README), so capped at Tier C despite disclosing CPU frequency, core count, kernel version, and multi-run variance; exact CPU model/SKU, compiler name/version and nginx version are not stated. Single-worker vs single-worker comparison on loopback (per-core efficiency, not multi-core scaling). Author flags the /index.html row as the least stable measurement (1.55x-2.90x across runs) because it is measured first in the loop before nginx settles; the 64 KB row is parity (0.94x-1.02x). Deliberately scoped: static files over HTTP/1.1 only, no TLS/HTTP/2, Linux only.

Static-file-only server: no TLS, no HTTP/2, no chunked request bodies, no CGI/reverse proxying, no compression, no virtual hosts, IPv4 only, Linux-only (epoll/sendfile/timerfd/eventfd/accept4). At 64KB payloads it reaches parity with nginx once the kernel's sendfile copy path dominates, so the win is specific to small-payload per-request overhead.

## Maintenance

MIT-licensed and small enough to vendor, but all 13 commits landed in one push on 2026-08-08 (one passing CI run), with no releases, issues, later commits or Hacker News mentions, so 'active' is unproven.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README table compares ehttpd against nginx (matched config in bench/nginx.conf, harness bench/run.sh) with every quoted rps, ratio, RSS and variance figure. Flags are known (-O2 -DNDEBUG), but the compiler is unnamed and the CPU is only 'Intel Xeon @ 2.10 GHz' with no SKU, so not A; first-party, so C.
- **Verifier notes:** Original benchmark_url (bench/run.sh) is the harness and holds no numbers; all claimed figures are verbatim in the README table and variance paragraph, so benchmark_url now points to README. Metadata (MIT, 0 stars, last commit 2026-08-08, not fork/archived) all check out.
- **Fields the verifier corrected:** `benchmark_url`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/SapnilPatel/epoll-httpd>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/bench/run.sh>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/README.md>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/CMakeLists.txt>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/bench/nginx.conf>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/.github/workflows/ci.yml>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/SapnilPatel/epoll-httpd>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/README.md>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/docs/DESIGN.md>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/CMakeLists.txt>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/bench/run.sh>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/bench/nginx.conf>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/bench/threshold.sh>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/.github/workflows/ci.yml>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/include/ehttpd/buffer.h>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/include/ehttpd/connection.h>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/include/ehttpd/file_cache.h>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/include/ehttpd/http.h>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/include/ehttpd/reactor.h>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/src/main.cc>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/src/connection.cc>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/src/reactor.cc>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/src/file_cache.cc>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/src/http.cc>
  - <https://github.com/SapnilPatel/epoll-httpd/commits/main>
  - <https://github.com/SapnilPatel/epoll-httpd/issues>
  - <https://github.com/SapnilPatel/epoll-httpd/actions>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/tests/test_integration.cc>
  - <https://github.com/SapnilPatel/epoll-httpd/blob/main/tests/test_parser.cc>
  - <https://github.com/h2o/h2o>
  - <https://github.com/SquiggleKernel/io_uring-http-benchmark>
  - <https://hn.algolia.com/api/v1/search?query=epoll-httpd&restrictSearchableAttributes=url,title>
  - <https://hn.algolia.com/api/v1/search?query=SapnilPatel>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/sapnilpatel/epoll-httpd`) · [data/wave5/enrich/raw/github_com_sapnilpatel_epoll_httpd.json](../../../data/wave5/enrich/raw/github_com_sapnilpatel_epoll_httpd.json) (enrichment confidence 0.8)

</details>
