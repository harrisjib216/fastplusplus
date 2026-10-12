# Lwan

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `GPL-2.0` · 🟢 active

> C HTTP/1.1 server and embeddable library; topped TechEmpower Round 10 JSON at \~5.8x Go net/http's throughput.

| | |
|---|---|
| **Beats** | Go net/http |
| **Claimed result** | TechEmpower Round 10, Peak (physical) JSON serialization: Lwan best 2,200,066 req/s (33,000,984 requests in 15 s at concurrency 256), ranked #1 of 145 JSON entries, vs the Go stdlib net/http entry 'go' best 379,662 req/s (5,694,930 requests in 15 s at concurrency 256), ranked #19, i.e. about 5.8x (derived from page data) |
| **Workload** | TechEmpower Framework Benchmarks Round 10 (April 2015) JSON-serialization test, 15 s runs at concurrency 8/16/32/64/128/256, Peak Hosting physical environment. Lwan at rev 49607add; the Go baseline is TFB's 'go' test (net/http + encoding/json, Go 1.4.2, GOMAXPROCS=NumCPU). |
| **Metric** | throughput |
| **Hardware** | Peak Hosting Dell R720 (listed as R720xd on the TFB results site) dual-Xeon E5 v2 servers with 40 hyperthreaded cores and 10 Gigabit Ethernet; exact CPU model not stated. |
| **Compiler and flags** | Lwan rev 49607add built with `cmake -DCMAKE_BUILD_TYPE=Release` and `make techempower` (TFB R10 frameworks/C/lwan/setup.sh); compiler and version not stated. Go baseline built with Go 1.4.2 (TFB R10 toolset/setup/linux/languages/go.sh). |
| **Adoption** | 6k stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/lpereira/lwan) · [benchmark](https://www.techempower.com/benchmarks/results/round10/peak.json) |

## Verdict

TechEmpower Round 10 (April 2015), Peak Hosting dual-Xeon E5 v2 servers (40 hyperthreads) over 10 GbE, JSON-serialization test: Lwan rev 49607add (CMake Release, compiler not stated) peaked at 2,200,066 req/s at 256 connections, #1 of 145, versus 379,662 req/s for TFB's Go 1.4.2 net/http + encoding/json entry (5.8x); the ratio was 1.7x at 8 connections. In the same round's plaintext test the gap was \~2.6x (2,075,046 vs 799,052 req/s, Lwan #7, far behind ULib's 6.9M), and Lwan's JSON handler then built a ccan/json DOM per request, so the win comes from the server core, not from JSON encoding.

## Use it when

- Small, CPU-cheap HTTP/1.1 responses (JSON, plaintext, cached small files) at high connection counts, where per-request server overhead dominates; in Round 10 its lead over Go net/http grew from 1.7x at 8 connections to 5.8x at 256.
- Linux x86-64 or aarch64 hosts where you build from source for the target CPU and want one pinned worker per core.
- Embedding an HTTP endpoint in a C program via liblwan without a C++ runtime or an external event library.
- Config-only static file or Lua serving: files under 16 KiB are mmap-cached with precompressed deflate/gzip/Brotli/zstd variants, and larger files go out via sendfile.
- A fast backend stub or load target for benchmarking proxies and gateways (the README lists Kong, KrakenD and Istio using it this way).

## Skip it when

- You need HTTP/2 or HTTP/3: Lwan is HTTP/1.x only (issue #17, open since 2014).
- You need production TLS: TLS is marked experimental, works only on Linux through kTLS (tls.ko plus mbedTLS), and supports TLSv1.2 only; the README suggests a separate terminator such as Hitch.
- Uploads without Content-Length or of large size: a request body with no Content-Length gets 400 (no chunked request bodies), POST/PUT bodies are capped at 40,960 bytes by default, and issue #218 (open) reports pipelined requests over 4 KB failing.
- An internet-facing edge that needs a hardened parser: September 2026 reports fixed request desynchronization via stale pipelined state (#381, #382), a WebSocket-FIN busy-spin that pinned a worker (#383), and an 8-byte out-of-bounds read in the SWAR URL decoder (#380); lost/stuck socket reports #348 and #353 remain open.
- Proprietary software that ships the binary: Lwan is GPL-2.0-or-later, so distributing a program linked with liblwan carries GPL obligations (the README notes that only serving over HTTP does not).

## How it is fast

One worker thread per online CPU, pinned using the sysfs thread_siblings topology, each with its own SO_REUSEPORT listening socket (with a CBPF steering filter where available) and its own edge-triggered epoll set; connection state lives in one preallocated array indexed by file descriptor. Every connection runs in a stackful coroutine switched by a hand-written x86-64/aarch64 swapcontext that skips floating-point registers and the signal mask, so handlers read like blocking code with no per-request thread or callback chain. The request parser dispatches on methods and headers by loading 2/4/8 bytes as integers (`STRING_SWITCH`), finds line ends with memchr/memmem, and decodes URLs with SSE/SWAR; idle keep-alive connections expire through a timeout queue driven by a timer wheel. Release builds add LTO and `-march=native`.

## Compared with alternatives

Pick Lwan over Drogon, Crow, Oat++, CWIST or Agoo-C when you want a pure-C HTTP/1.1 server with the widest measured margin over Go net/http (5.8x in TFB JSON versus \~1.5x for Crow in the catalog), and GPL plus no HTTP/2 is acceptable. If you need HTTP/2 or production TLS, Lwan is the wrong choice; look at H2O or a C++ framework instead.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (liblwan-static / liblwan.so with installed headers), or the standalone `lwan` server binary |
| **Dependencies** | Required: CMake 3.20+ (CMakeLists.txt; the README still says 2.8) and one of zlib, zlib-ng or libdeflate. Optional: Lua 5.4, Brotli, zstd, mbedTLS (kTLS), mimalloc/jemalloc/tcmalloc, SQLite and MariaDB client (samples only); libucontext on architectures other than x86-64/aarch64. |
| **Minimum toolchain** | C compiler that accepts -std=gnu11 (GCC or Clang; uses GNU extensions, inline assembly and linker sections) |
| **Platforms** | Linux x86-64 is primary (CI build, tests, static analysis, OSS-Fuzz); FreeBSD and OpenBSD x86-64 build (epoll emulated on kqueue); aarch64 has a native context switch; other CPUs fall back to libucontext, which fails on Apple Silicon macOS (issue #366). Windows not documented. |
| **Thread safety** | Fixed pool of worker threads (default one per online CPU); each connection's coroutine stays on one thread, so a handler runs single-threaded per request. A handler that blocks stalls every connection on that worker; use lwan_request_await_read/write or lwan_request_sleep to yield. Shared caches use locks (issue #53). Otherwise not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- The default CMake build type is Debug, which logs every request while holding a lock; benchmark only with -DCMAKE_BUILD_TYPE=Release.
- Release builds default to -march=native/-mtune=native (MTUNE_NATIVE=ON), so a binary can fail on other CPUs; pass -DMTUNE_NATIVE=OFF when packaging.
- Coroutine stacks are fixed-size (4x SIGSTKSZ, 8x with Brotli, page-rounded) and in release builds come from the heap with no guard page, so deep recursion or large stack buffers in handlers can silently overflow (see issue #130).
- At startup Lwan raises RLIMIT_NOFILE and preallocates max_file_descriptors (default 524288) x sizeof(struct lwan_connection); max_file_descriptors must be at least 10x threads. A crash when threads &lt; online CPUs was fixed only on 2026-09-18.

## Known shortcomings

- The evidence is TechEmpower Round 10 (2015, Go 1.4.2 baseline), about 5.8x on JSON; no recent independent rounds are cited. No compiler or exact CPU model stated.
- Evidence is TechEmpower Round 10 (April 2015, Go 1.4.2); the maintainer reported a big regression in later preview rounds (#291). The 5.8x is the 256-connection best case (1.7x at 8, 2.6x at 32); plaintext in the same round is \~2.6x. September 2026 fixed an out-of-bounds read in the URL decoder (#380), request desynchronization via stale pipelining state (#381, #382) and a WebSocket worker spin (#383); lost/stuck socket reports still open. HTTP/1.x only, TLS experimental (Linux, TLS 1.2), no chunked uploads, 40 KB default body cap, &gt;4 KB pipelined requests fail (#218). Default CMake build is Debug; Release uses -march=native; no coroutine stack guard page. GPL-2.0-or-later.

## Caveats and trade-offs

Round 10 dates from April 2015, on retired hardware, with Lwan rev 49607add and Go 1.4.2; not re-verified on current Lwan or current Go. The archived Round 10 blog post (live URL now returns 404) states that Lwan 'has taken the crown' in the Peak JSON test with a top score of 2.2M vs Round 9's 1.05M, and that Go is not in the Peak top-ten leaderboard. The ranking covers the JSON-serialization test only; ULib (C++) was a close second at 2,062,437 req/s.

Hand-written HTTP parser and coroutine-based design trade some safety/portability guarantees for speed; GPLv2 is more restrictive than nginx's license for some users.

## Maintenance

Active (last commit 2026-09-22; latest tag v0.7, June 2025; September 2026 security reports were fixed within days), GPL-2.0-or-later, built from source with CMake or pulled as GHCR container images and Alpine/Arch/NixOS packages.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** TechEmpower is a well-known independent suite with public test code (FrameworkBenchmarks tag R10: frameworks/C/lwan/setup.sh, frameworks/Go/go/src/hello/hello.go) and a Release build. Not A: the compiler version and exact CPU model (only 'dual-Xeon E5 v2') are not stated.
- **Verifier notes:** Blog claims verified on the archived post; benchmark_url moved to the official Round 10 Peak raw-results file (rendered at techempower.com/benchmarks/#section=data-r10&hw=ph&test=json), which carries both the Lwan and Go net/http numbers. Metadata (GPL-2.0, 6,037 stars, last commit 2026-09-22, not a fork) verified.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://web.archive.org/web/20230525035203/https://www.techempower.com/blog/2015/04/21/framework-benchmarks-round-10/>
  - <https://www.techempower.com/blog/2015/04/21/framework-benchmarks-round-10/>
  - <https://web.archive.org/web/2023/https://www.techempower.com/blog/2015/05/28/the-hardware-behind-the-results-of-framework-benchmarks-round-10/>
  - <https://www.techempower.com/benchmarks/>
  - <https://www.techempower.com/benchmarks/assets/index-rdjV3uRt.js>
  - <https://www.techempower.com/benchmarks/results/round10/peak.json>
  - <https://www.techempower.com/benchmarks/results/round10/ph.json>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/tree/R10/frameworks/C/lwan>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/blob/R10/frameworks/C/lwan/setup.sh>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/blob/R10/frameworks/C/lwan/install.sh>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/blob/R10/frameworks/C/lwan/benchmark_config>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/blob/R10/frameworks/Go/go/benchmark_config>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/blob/R10/frameworks/Go/go/src/hello/hello.go>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/blob/R10/toolset/setup/linux/languages/go.sh>
  - <https://github.com/lpereira/lwan>
- **Sources the enricher read:**
  - <https://github.com/lpereira/lwan>
  - <https://github.com/lpereira/lwan/blob/HEAD/README.md>
  - <https://github.com/lpereira/lwan/blob/HEAD/CMakeLists.txt>
  - <https://github.com/lpereira/lwan/blob/HEAD/src/lib/CMakeLists.txt>
  - <https://github.com/lpereira/lwan/blob/HEAD/src/lib/lwan.h>
  - <https://github.com/lpereira/lwan/blob/HEAD/src/lib/lwan.c>
  - <https://github.com/lpereira/lwan/blob/HEAD/src/lib/lwan-private.h>
  - <https://github.com/lpereira/lwan/blob/HEAD/src/lib/lwan-coro.c>
  - <https://github.com/lpereira/lwan/blob/HEAD/src/lib/lwan-thread.c>
  - <https://github.com/lpereira/lwan/blob/HEAD/src/lib/lwan-request.c>
  - <https://github.com/lpereira/lwan/blob/HEAD/src/lib/lwan-response.c>
  - <https://github.com/lpereira/lwan/blob/HEAD/src/lib/lwan-mod-serve-files.c>
  - <https://github.com/lpereira/lwan/blob/HEAD/src/samples/techempower/techempower.c>
  - <https://github.com/lpereira/lwan/blob/HEAD/src/samples/techempower/json.c>
  - <https://github.com/lpereira/lwan/commit/49607addb31879e2aa2b701317773674662315aa>
  - <https://github.com/lpereira/lwan/blob/49607addb31879e2aa2b701317773674662315aa/techempower/techempower.c>
  - <https://github.com/lpereira/lwan/blob/49607addb31879e2aa2b701317773674662315aa/techempower/json.c>
  - <https://github.com/lpereira/lwan/tags>
  - <https://github.com/lpereira/lwan/releases>
  - <https://github.com/lpereira/lwan/commits>
  - <https://github.com/lpereira/lwan/issues>
  - <https://github.com/lpereira/lwan/issues/17>
  - <https://github.com/lpereira/lwan/issues/205>
  - <https://github.com/lpereira/lwan/issues/218>
  - <https://github.com/lpereira/lwan/issues/290>
  - <https://github.com/lpereira/lwan/issues/291>
  - <https://github.com/lpereira/lwan/issues/348>
  - <https://github.com/lpereira/lwan/issues/353>
  - <https://github.com/lpereira/lwan/issues/366>
  - <https://github.com/lpereira/lwan/issues/380>
  - <https://github.com/lpereira/lwan/issues/381>
  - <https://github.com/lpereira/lwan/issues/382>
  - <https://github.com/lpereira/lwan/issues/383>
  - <https://www.techempower.com/benchmarks/results/round10/peak.json>
  - <https://github.com/TechEmpower/FrameworkBenchmarks/tree/master/frameworks/C/lwan>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=lwan>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/lpereira/lwan`) · [data/wave5/enrich/raw/github_com_lpereira_lwan.json](../../../data/wave5/enrich/raw/github_com_lpereira_lwan.json) (enrichment confidence 0.6)

</details>
