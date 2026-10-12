# nghttp2 (nghttpx HTTP/2 proxy)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `MIT` · 🟢 active

> C HTTP/2 framing library (curl's HTTP/2 backend) plus nghttpx, an HTTP/3/2/1.1 TLS-terminating reverse proxy; weak evidence against ATS.

| | |
|---|---|
| **Beats** | Apache Traffic Server (ATS) as HTTP/2 terminating reverse proxy |
| **Claimed result** | Peak system CPU utilization under the same traffic load: ATS 18%, nghttpx 15%; idle process CPU ATS 0.5%, nghttpx 0%; idle system CPU ATS 7%, nghttpx 6.5%. No throughput or latency comparison seen. |
| **Workload** | Yahoo engineer's HTTP/2 benchmarking of ATS vs nghttpx (h2load clients), both terminating HTTP/2 and proxying requests, 3 large image objects (60 KB to 200 KB) per connection, same number of threads, logs on, no OCSP stapling, no ATS cache; metric was server CPU utilization at the same traffic load. |
| **Metric** | other |
| **Adoption** | 5.1k stars; libnghttp2 is the HTTP/2 backend of curl and many servers |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/nghttp2/nghttp2) · [benchmark](https://cwiki.apache.org/confluence/download/attachments/56066455/Benchmarking%20for%20HTTP-2.pdf?version=1&modificationDate=1447792756000&api=v2) |

## Verdict

Nothing was verified: the only comparison, Yahoo's 2015 'Benchmarking for HTTP/2' deck (h2load, 3 images of 60-200 KB per connection, same thread count, ATS cache off), reportedly shows 15% vs 18% peak system CPU at equal load for nghttpx vs ATS, but cwiki.apache.org failed DNS resolution here and search excerpts stop before the results; hardware, versions and flags are unknown. The project's own wiki (ServerBenchmarkRoundH210, March 2014) measured nghttpd, not nghttpx, at 76,338 req/s vs nginx (listed as '1.15.11', likely 1.5.11) speaking SPDY/3.1 at 49,566 req/s (1.54x, derived from page data) on one core of an i7-4600U with h2load -n100000 -c100 -m100 and a 612-byte file, a cross-protocol first-party run whose author says it does 'not justify anything'.

## Use it when

- You need a mature, widely deployed HTTP/2 framing engine to embed in a C or C++ server or client that already owns its event loop (it is the HTTP/2 layer behind curl).
- You want a standalone TLS terminator in front of HTTP/1.1 backends that adds HTTP/2 and experimental HTTP/3 on the frontend, with backend HTTP/2 per host/path pattern.
- You need a secure (TLS) HTTP/2 forward proxy in front of Squid or ATS, which nghttpx supports with --http2-proxy.
- You benchmark HTTP/1.1, HTTP/2 or HTTP/3 servers: h2load from the same repo is the usual tool and now reports median, p95 and p99 latency and JSON output (v1.69.0).

## Skip it when

- You want a measured throughput or latency win over nginx, H2O or ATS: no current like-for-like number exists; the ATS comparison is CPU utilisation only (15% vs 18% peak system CPU, unverified) from 2015.
- You need caching, ESI or full CDN features: nghttpx is a proxy without a cache, unlike ATS.
- You want a complete server from the library alone: libnghttp2 has no HTTP/1, no TLS and no sockets, so you write the I/O and HTTP/1 glue yourself.
- macOS deployments of the apps: the README says nghttpd, nghttpx and h2load may crash with threads on Mac OS X and suggests --disable-threads; Windows gets the library via CMake/MSVC but the apps only under Cygwin.
- Toolchains older than g++ 14 or clang++ 19 when you need the applications: since v1.70.0 the C++ parts require C++23 (the C library still builds with C99).

## How it is fast

The library does no I/O and no thread synchronisation, so the caller batches reads and writes on its own loop. HPACK Huffman decoding walks a precomputed finite-state table four bits at a time (the Hirschberg-Lelewer prefix-code method cited in lib/nghttp2_hd_huffman.c), the encoder packs codes into a 64-bit accumulator and stores four bytes at once, static-table header names are resolved by a generated switch on name length (lookup_token), and the encoder's dynamic table is indexed by a 128-bucket hash map. nghttpx runs one libev event loop per worker thread with pooled fixed-size memory chunks (src/memchunk.h) and a block allocator for per-stream strings (src/allocator.h), plus TLS session tickets, dynamic record sizing and an eBPF program that steers QUIC datagrams to the right SO_REUSEPORT socket.

## Compared with alternatives

Pick nghttpx over H2O or Pingora when you want an off-the-shelf HTTP/3 + HTTP/2 TLS terminator or secure forward proxy that needs configuration rather than code, or pick libnghttp2 when you need an embeddable HTTP/2 engine for your own loop; H2O has the stronger published numbers (against nginx) and Pingora documents large CPU savings over nginx at Cloudflare, while nghttp2 has no current speed comparison of its own.

## Integration

| | |
|---|---|
| **Form** | shared lib or static lib (libnghttp2, autotools or CMake; --enable-lib-only) plus standalone binaries (nghttpx, nghttpd, nghttp, h2load) |
| **Dependencies** | libnghttp2: none at runtime (pkg-config to build). nghttpx and tools: OpenSSL &gt;= 1.1.1 or wolfSSL &gt;= 5.7.0, LibreSSL &gt;= 3.8.1, aws-lc &gt;= 1.19.0 or BoringSSL; libev &gt;= 4.11; zlib &gt;= 1.2.3; c-ares &gt;= 1.7.5; optional jemalloc (recommended), ngtcp2 &gt;= 1.23.0 and nghttp3 &gt;= 1.17.0 for HTTP/3, libbpf, libsystemd, mruby, libbrotli, neverbleed |
| **Minimum toolchain** | Library: C99 (gcc 4.8 adequate). Applications: C++23 (g++ &gt;= 14, clang++ &gt;= 19 per README, v1.70.0) |
| **Platforms** | Library: any C99 platform including Windows (CMake/MSVC). Applications: Linux and other Unix; Windows via Cygwin only; macOS may need --disable-threads; eBPF QUIC steering needs libbpf |
| **Thread safety** | Library: any number of nghttp2_session objects, but one session must be used by a single thread at a time; never call send/recv functions from inside callbacks. nghttpx: N worker threads (-n, default 1) each with its own libev loop, plus a separate main process. |
| **Drop-in for the baseline** | no |

## Gotchas

- nghttpx defaults to one worker thread (-n 1); set --workers explicitly before comparing it with ATS or nginx, which the Yahoo test did by matching thread counts.
- Since 1.57.0 the HTTP/2 Rapid Reset mitigation rate-limits incoming RST_STREAM: a client that resets every stream after its response was throttled to about 33 requests/s (issue #1984); servers can raise it with nghttp2_option_set_stream_reset_rate_limit(). v1.69.0 also raised the default glitch rate limit 10x.
- Flow-control stalls are the application's job: with the default 65535-byte window and 16384-byte frames, an uploader that does not coalesce buffers degenerates into 1-byte DATA frames (issue #1722, 100 MB upload 38 s over HTTP/2 vs 0.33 s over HTTP/1.1); the maintainer declined a library change and the fix went into curl (#8965).
- Security advisories: HTTP/2 Rapid Reset and a memory leak (2023), unbounded CONTINUATION frames (2024), and CVE-2026-27135 (assertion-failure DoS in &lt;= 1.68.0 when PRIORITY_UPDATE, ALTSVC or extension frames are enabled; fixed in 1.68.1). Stay on current releases.

## Known shortcomings

- Downgraded C to D: the Yahoo PDF (cwiki.apache.org) is blocked and search excerpts stop before the results, so the ATS 18% vs nghttpx 15% system-CPU figure is unconfirmed; the metric is CPU at fixed load, not speed. Kept as notable (5.1k stars, curl backend).
- Enricher: the Yahoo ATS deck stays unreachable (cwiki.apache.org blocked), so the nghttpx claim is CPU-only and unverified (D). The only other numbers, the project wiki ServerBenchmarkRoundH210 (Tsujikawa, March 2014), measure nghttpd not nghttpx: 76,338 vs 49,566 req/s against nginx speaking SPDY/3.1 on one core of an i7-4600U, cross-protocol and first-party, with the nginx config on port 18443 while h2load targets 8443. nghttpx defaults to -n 1 worker; the Rapid Reset limit since 1.57.0 throttles clients that reset every stream to about 33 req/s (#1984); CVE-2026-27135 (&lt;= 1.68.0, fixed 1.68.1); apps need C++23 since v1.70.0.

## Caveats and trade-offs

Unverified, snippet only: the PDF ('Benchmarking for HTTP/2' by Kit Chan, Kenny Peng and Nora Shoemaker of Yahoo, Apache wiki attachments 56066455 and 62696116) could not be opened (cwiki.apache.org and cwiki-test.apache.org blocked), and the verifier's WebSearch excerpts of the deck stop before any CPU utilization or nghttpx results, so the ATS 18% vs nghttpx 15% peak system CPU figures (and the idle figures) are not confirmed by any source opened. Even if correct, they measure CPU utilization at fixed load, not requests per second or latency, a 3-percentage-point efficiency difference against a 2015-era ATS HTTP/2 implementation; hardware, versions and flags unknown. The nghttp2 README's own h2load example (129658 req/s on localhost) is a tool demo with no comparison. An Apache wiki note (snippet only) calls the 2015 ATS HTTP/2 code 50% slower than its HTTPS path and suggests ATS learn from nghttpx's data structures, which is directional only. Kept because nghttp2 is widely used (libnghttp2 is curl's HTTP/2 backend), not because a speed win is shown.

Evidence is for the nghttpx proxy application in the nghttp2 repo, not the libnghttp2 framing library. The library is a callback-based C API with no I/O of its own.

## Maintenance

Actively maintained (last commit 2026-10-03, v1.70.0 on 2026-07-29), MIT-licensed with regular releases and a documented security process, so safe to depend on; the speed claim is directional only (tier D), and the only other numbers found are a 2014 first-party nghttpd vs nginx-SPDY run whose nginx config listens on 18443 while h2load targets 8443.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now D.
- **Tier reason:** The only comparison source (Yahoo's 'Benchmarking for HTTP/2' PDF on cwiki.apache.org) is unreachable here (cwiki.apache.org and cwiki-test.apache.org both refused by the egress proxy), and two WebSearch queries returned excerpts that stop before any CPU or nghttpx results, so no number in the record could be verified; the repo itself has no comparative benchmark.
- **Verifier notes:** No number could be verified: the PDF host is blocked and search excerpts end before the results, so the entry falls to tier D (if the PDF is opened from another environment and the CPU figures hold, it could return to C or B as a measurement by the baseline's own maintainers at Yahoo). Shortcomings: unverifiable snippet-only evidence, CPU-utilization metric rather than throughput, 2015-era baseline, no comparison in the repo. Metadata checked: MIT, 5.1k stars, not a GitHub fork (historically derived from spdylay), last commit 2026-10-03, active.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-78 (wave 5); enricher w5 pair-030
- **Pages the verifier opened:**
  - <https://github.com/nghttp2/nghttp2>
  - <https://github.com/nghttp2/nghttp2/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/nghttp2/nghttp2/HEAD/README.rst>
  - <https://raw.githubusercontent.com/nghttp2/nghttp2/HEAD/doc/programmers-guide.rst>
  - <https://raw.githubusercontent.com/nghttp2/nghttp2/HEAD/doc/sources/nghttpx-howto.rst>
  - <https://raw.githubusercontent.com/nghttp2/nghttp2/HEAD/doc/nghttpx.1.rst>
  - <https://raw.githubusercontent.com/nghttp2/nghttp2/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/nghttp2/nghttp2/HEAD/lib/nghttp2_hd.c>
  - <https://raw.githubusercontent.com/nghttp2/nghttp2/HEAD/lib/nghttp2_hd.h>
  - <https://raw.githubusercontent.com/nghttp2/nghttp2/HEAD/lib/nghttp2_hd_huffman.c>
  - <https://raw.githubusercontent.com/nghttp2/nghttp2/HEAD/lib/includes/nghttp2/nghttp2.h>
  - <https://raw.githubusercontent.com/nghttp2/nghttp2/HEAD/src/memchunk.h>
  - <https://raw.githubusercontent.com/nghttp2/nghttp2/HEAD/src/shrpx_worker.h>
  - <https://raw.githubusercontent.com/nghttp2/nghttp2/HEAD/src/allocator.h>
  - <https://github.com/nghttp2/nghttp2/security>
  - <https://github.com/nghttp2/nghttp2/security/advisories/GHSA-6933-cjhr-5qg6>
  - <https://github.com/nghttp2/nghttp2/releases>
  - <https://github.com/nghttp2/nghttp2/commits>
  - <https://github.com/nghttp2/nghttp2/issues?q=is%3Aissue+performance>
  - <https://github.com/nghttp2/nghttp2/issues/1984>
  - <https://github.com/nghttp2/nghttp2/issues/1722>
  - <https://github.com/nghttp2/nghttp2/wiki>
  - <https://github.com/nghttp2/nghttp2/wiki/ServerBenchmarkRoundH210>
  - <https://github.com/nshoemaker/nghttp2/wiki/ServerBenchmarkRoundH210>
  - https://cwiki.apache.org/confluence/download/attachments/56066455/Benchmarking%20for%20HTTP-2.pdf?version=1&modificationDate=1447792756000&api=v2 (failed: getaddrinfo ENOTFOUND)
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/nghttp2/nghttp2`) · [data/wave5/enrich/raw/github_com_nghttp2_nghttp2.json](../../../data/wave5/enrich/raw/github_com_nghttp2_nghttp2.json) (enrichment confidence 0.45)

</details>
