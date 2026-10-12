# H2O

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> C HTTP/1, HTTP/2 and HTTP/3 web server and reverse proxy; 2016 charts show more req/s per core than nginx 1.9.

| | |
|---|---|
| **Beats** | nginx 1.7.9 (HTTP/1.1 local benchmark); nginx 1.9.10 in the later EC2 static-file chart |
| **Claimed result** | Static-file chart (612-byte file, 250 clients, req/s per core; bar heights read from the chart gridlines, so approximate): nginx 1.9.10 vs H2O 1.7.0-beta4 \~74K vs \~108K (HTTP/1.1, \~1.5x), \~45K vs \~79K (HTTP/1.1 TLS, \~1.7x), \~77K vs \~340K (HTTP/2 TLS, \~4.4x). Download-timings chart (labelled values, 8Mbps/100ms, H2O 1.5.0 HTTP/2 vs nginx 1.9.5 HTTP/1.1 / HTTP/2): load 2.96 vs 3.32/3.17 s (Chrome 45), 2.74 vs 3.01/2.82 s (Firefox 41), 2.97 vs 3.28/3.06 s (Safari iOS 9.0.1); first paint 1.74 vs 2.44/3.00 s (Chrome), 1.27 vs 1.48/1.83 s (Firefox), but on Safari 2.01 s vs 1.85/2.56 s, so H2O's first paint is slower than nginx HTTP/1.1 there. Ratios derived from page data. |
| **Workload** | 612-byte static file on two Amazon EC2 c3.8xlarge instances (server + client) in one placement group, 250 concurrent clients, wrk (HTTP/1) and h2load (HTTP/2), one worker per server (h2o num-threads: 1, nginx worker_processes 1), nginx open_file_cache enabled vs H2O's built-in open-file cache; plus first-paint/load times of an http2rulez.com fork in Chrome 45, Firefox 41 and Safari iOS 9.0.1 over a tc/netem-simulated 8Mbps/100ms link; plus an older reverse-proxy chart (h2o 0.9.0 vs nginx 1.7.7). |
| **Metric** | throughput |
| **Hardware** | Ubuntu 14.04 x86-64 in VMware Fusion 7.1.0 on OS X 10.9.5, MacBook Pro 15-inch Early 2013 (CPU model not stated); the later chart used two Amazon EC2 c3.8xlarge instances |
| **Adoption** | 11.5k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/h2o/h2o) · [benchmark](https://raw.githubusercontent.com/h2o/h2o/9ef1ad7/srcdoc/benchmarks.mt) |

## Verdict

Two 2015-2016 vendor charts, both from single-worker runs: a 612-byte static file with 250 clients (wrk for HTTP/1, h2load for HTTP/2) between two EC2 c3.8xlarge instances. Bar heights put nginx 1.9.10 vs H2O 1.7.0-beta4 at about 74K vs 108K (HTTP/1.1), 45K vs 79K (HTTP/1.1 TLS) and 77K vs 340K (HTTP/2 TLS) req/s per core. On an 8 Mbps/100 ms netem link, H2O 1.5.0 over HTTP/2 finished a test page 0.09-0.36 s sooner than nginx 1.9.5 and painted first sooner on Chrome 45 and Firefox 41, but not on Safari iOS 9.0.1 (2.01 s vs 1.85 s for nginx HTTP/1.1). No CPU model, compiler or build flags are given, and nginx ran with open_file_cache.

## Use it when

- Serving many small static files over HTTP/2 + TLS on one box: the vendor chart shows about 340K vs 77K req/s per core against nginx 1.9.10 for a 612-byte file
- HTTP/2 front ends for browsers on mobile or long-distance links, where priority handling and the TCP_NOTSENT_LOWAT latency tweak (Linux and macOS only) cut first-paint time
- An HTTP/3/QUIC-capable origin or proxy on x86-64 Linux, using quicly/picotls with GSO and the AVX2/VAES fusion AES-GCM engine
- C programs that need an embeddable HTTP/1-2-3 server library (libh2o) rather than a separate proxy process
- Request logic in a small embedded scripting language (mruby Rack handlers) instead of writing C modules

## Skip it when

- You depend on the nginx ecosystem (third-party modules, Lua/njs, existing nginx.conf, ops tooling): none of it transfers, and you must rewrite the config in H2O's YAML
- You need versioned, tagged releases: the project stopped cutting releases in April 2023 and treats every master commit as stable (the last tag is 'tag-no-more-releases'). You pin and track commits yourself
- Security-sensitive edges with no capacity to patch fast: GitHub lists 14 advisories, including 5 in 2026 (4 high: HTTP/2 state amplification, a QPACK stack overflow on musl, QUIC assertion failures and a heap overrun), plus HTTP/2 Rapid Reset (2023) and MadeYouReset (2025)
- Cold-storage file serving: file reads use pread/sendfile by default, which block the whole worker thread on a page-cache miss. Only file.io_uring (Linux, off by default) avoids that
- Platforms other than Linux: CI runs only on Ubuntu 24.04. macOS and FreeBSD are covered by packages, and kTLS, io_uring and zerocopy TLS work only on Linux

## How it is fast

Each worker thread (default: one per CPU) runs its own epoll/kqueue event loop (h2o_evloop). Requests are parsed with PicoHTTPParser, which has an SSE4.2 PCMPESTRI range-scan path, and short-lived objects come from per-thread memory pools and recycling allocators. The open-file cache is a khash + LRU table of file descriptors, with stat, ETag and Last-Modified strings, that is cleared at the end of every event-loop iteration: repeat hits in one iteration skip open/fstat, and replaced files are seen on the next iteration. For page-load time, H2O fully implements HTTP/2 dependency and weight prioritization and sends CSS/JS first for browsers that do not use dependency priorities. On high-RTT, small-cwnd links it also keeps unsent data small with TCP_NOTSENT_LOWAT and TCP_INFO, so a higher-priority response can go out sooner. Newer optional paths include the picotls 'fusion' AES-GCM engine for QUIC, kTLS or MSG_ZEROCOPY TLS, and io_uring file reads.

## Compared with alternatives

Pick H2O when you want a finished, config-driven nginx replacement for static files and reverse proxying with HTTP/2 prioritization and HTTP/3. Sogou Workflow, also catalogued against nginx, is a C++11 async task engine: you write server code on it, and its win is on small generated bodies. Lwan (catalogued as HTTP/1.1) and libevhtp suit embedding a lighter HTTP/1 server in your own program.

## Integration

| | |
|---|---|
| **Form** | static lib (libh2o, or shared with BUILD_SHARED_LIBS=ON) plus a standalone server binary; built from source with CMake |
| **Dependencies** | Required: CMake, pkg-config, OpenSSL 1.0.2+ (LibreSSL and BoringSSL also build) and zlib. Optional: libuv 1.0+ (libh2o libuv binding), wslay (WebSocket), brotli, liburing, libaegis, and ruby + bison for mruby. picotls, quicly, picohttpparser, mruby, libyaml and neverbleed are vendored under deps/ |
| **Minimum toolchain** | C99 (CMake adds -std=c99) with GCC or Clang; CMake 2.8.12 or newer; the Release build defaults to -O2 |
| **Platforms** | Linux (the only CI target), macOS and FreeBSD (packages; kqueue backend), SunOS handled in CMakeLists. The fusion AES-GCM engine needs x86-64 with AVX2/AES-NI/PCLMUL/VAES; other features are architecture-neutral C |
| **Thread safety** | Not documented as a guarantee. The design is shared-nothing: one h2o_context_t and event loop per worker thread, with h2o_multithread queues for cross-thread messages. libh2o users must keep each context on its own thread |
| **Drop-in for the baseline** | partial — it fills nginx's roles (static files, reverse proxy, FastCGI, TLS termination, HTTP/2 and HTTP/3) but uses its own YAML config, and nginx modules or directives are not supported |

## Gotchas

- The default build has no -msse4.2, so PicoHTTPParser's SSE4.2 path (#ifdef __SSE4_2__) is compiled out unless you pass it in CMAKE_C_FLAGS (for example -march=native)
- The open-file cache is emptied every event-loop iteration, and its capacity defaults to 2x http2-max-concurrent-requests-per-connection. It saves open(2) calls only within one iteration and is not a long-lived cache like nginx open_file_cache
- tcp-reuseport is OFF by default, so all worker threads accept from one shared listening socket. Turn it on to spread accepts across threads
- HTTP/3 is labelled experimental in the README, and most of the 2024-2026 advisories are in the QUIC/HTTP/3 and HTTP/2 code

## Known shortcomings

- The comparison page dates from 2016 (nginx 1.9.10, one worker each), with static-file numbers read off chart bars and no CPU, compiler or flags; on Safari iOS H2O's first paint (2.01 s) was slower than nginx over HTTP/1.1 (1.85 s).
- Benchmark is from 2015-2016 (H2O 1.5/1.7 vs nginx 1.9.x, one worker each), no CPU, compiler or flags; browser versions appear only in chart legends. The nginx config gist has no root directive in its TLS block (invalid as posted); an older chart ran nginx without open_file_cache. H2O's open-file cache holds file descriptors and is emptied every event-loop iteration, so it is not a memory-for-latency trade. No numbered release since 2019 (master is 'stable'). 14 security advisories, 5 from 2026 (4 high: HTTP/2 state amplification, QPACK stack overflow on musl, QUIC assertion failures, heap overrun), plus Rapid Reset and MadeYouReset. Default CMake build is -O2 without -msse4.2, so picohttpparser's SSE4.2 path is compiled out. File serving blocks a worker on page-cache misses unless file.io_uring (Linux, off by default) is enabled. CI on Ubuntu only; HTTP/3 still experimental.
- Re-found by the wave 5 seed backfill (w5-mine-i) with the project's own 2015 wrk run (h2o 0.9.0 vs nginx 1.7.9: 75,483 vs 37,289 and 59,673 vs 43,988 requests per second per core, commit 9ef1ad7 of srcdoc/benchmarks.mt; no compiler, flags or CPU; current docs use PNG charts); first-party, tier C either way.

## Caveats and trade-offs

First-party page. It was last changed in 2016 (benchmark update 2016-02-04, typo fix 2016-08-23), so it compares H2O 1.5/1.7 with nginx 1.9.x; the reverse-proxy chart (h2o 0.9.0 vs nginx 1.7.7) is called 'old' on the page. Static-file values exist only as bar heights, but the download-timing chart has labelled values. Single-worker runs only, so multi-core scaling is not shown. H2O is not faster everywhere: on Safari iOS its first paint (2.01 s) is slower than nginx HTTP/1.1 (1.85 s). No CPU model, compiler or build flags are stated for either server.

C server that can also be used as a library; HTTP/1.x, HTTP/2 and experimental HTTP/3. Smaller module and ecosystem surface than nginx; configuration is YAML.

## Maintenance

Active (last commit 2026-09-10, 11.5k stars, MIT) and production-grade, but it ships from master with no numbered releases since 2019's v2.2.6/v2.3.0-beta2 and has a steady flow of HTTP/2 and QUIC CVEs, so plan to track master closely.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party page with charts against nginx: static-file req/s per core (nginx 1.9.10 vs H2O 1.7.0-beta4) and labelled download timings (nginx 1.9.5 vs H2O 1.5.0). The server configs are public (gists kazuho/969bb99bae31d67e01c4 and def1e71281ed4ae07b95; one worker each). Only the instance type (c3.8xlarge) is given, with no CPU model, compiler or build flags, so it stays C.
- **Verifier notes:** Downgraded because the claim was overstated. 'First-paint sooner than nginx' fails for Safari against nginx HTTP/1.1, and the record wrongly said no numbers could be read (the download chart has labels). Tier C stands. Metadata checked: MIT, 11,546 stars, not archived, not a fork, last commit 2026-09-10 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** backfill w5-mine-i
- **Pages the verifier opened:**
  - <https://github.com/h2o/h2o>
  - <https://h2o.examp1e.net/benchmarks.html>
  - <https://h2o.examp1e.net/assets/staticfile612-nginx1910-h2o170.png>
  - <https://h2o.examp1e.net/assets/8mbps100msec-nginx195-h2o150.png>
  - <https://h2o.examp1e.net/assets/remotebench.png>
  - <https://gist.github.com/kazuho/969bb99bae31d67e01c4>
  - <https://gist.github.com/kazuho/def1e71281ed4ae07b95>
- **Sources the enricher read:**
  - <https://github.com/h2o/h2o>
  - <https://github.com/h2o/h2o/blob/master/README.md>
  - <https://h2o.examp1e.net/benchmarks.html>
  - <https://h2o.examp1e.net/assets/staticfile612-nginx1910-h2o170.png>
  - <https://h2o.examp1e.net/assets/8mbps100msec-nginx195-h2o150.png>
  - <https://h2o.examp1e.net/assets/remotebench.png>
  - <https://gist.github.com/kazuho/969bb99bae31d67e01c4>
  - <https://gist.github.com/kazuho/def1e71281ed4ae07b95>
  - <https://github.com/h2o/h2o/blob/master/srcdoc/benchmarks.mt>
  - <https://github.com/h2o/h2o/commits/master/srcdoc/benchmarks.mt>
  - <https://github.com/h2o/h2o/commit/9ef1ad73>
  - <https://github.com/h2o/h2o/blob/master/srcdoc/index.mt>
  - <https://github.com/h2o/h2o/blob/master/srcdoc/install.mt>
  - <https://github.com/h2o/h2o/blob/master/srcdoc/faq.mt>
  - <https://github.com/h2o/h2o/blob/master/srcdoc/configure/base_directives.mt>
  - <https://github.com/h2o/h2o/blob/master/srcdoc/configure/file_directives.mt>
  - <https://github.com/h2o/h2o/blob/master/srcdoc/configure/http2_directives.mt>
  - <https://github.com/h2o/h2o/blob/master/srcdoc/configure/http3_directives.mt>
  - <https://github.com/h2o/h2o/blob/master/CMakeLists.txt>
  - <https://github.com/h2o/h2o/blob/master/deps/picotls/cmake/fusion.cmake>
  - <https://github.com/h2o/h2o/blob/master/include/h2o.h>
  - <https://github.com/h2o/h2o/blob/master/include/h2o/filecache.h>
  - <https://github.com/h2o/h2o/blob/master/lib/common/filecache.c>
  - <https://github.com/h2o/h2o/blob/master/lib/core/util.c>
  - <https://github.com/h2o/h2o/blob/master/lib/core/context.c>
  - <https://github.com/h2o/h2o/blob/master/src/main.c>
  - <https://github.com/h2o/h2o/blob/master/deps/picohttpparser/picohttpparser.c>
  - <https://github.com/h2o/h2o/blob/master/.github/workflows/ci.yml>
  - <https://github.com/h2o/h2o/releases>
  - <https://github.com/h2o/h2o/security/advisories>
  - <https://github.com/h2o/h2o/issues/1091>
  - <https://github.com/h2o/h2o/issues/3534>
  - <https://github.com/h2o/h2o/issues/3535>
  - <https://github.com/h2o/h2o/issues?q=label%3Abug+is%3Aopen>
  - <https://github.com/h2o/h2o/issues?q=label%3Alibh2o+is%3Aopen>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/h2o/h2o`) · [data/wave5/enrich/raw/github_com_h2o_h2o.json](../../../data/wave5/enrich/raw/github_com_h2o_h2o.json) (enrichment confidence 0.78)

</details>
