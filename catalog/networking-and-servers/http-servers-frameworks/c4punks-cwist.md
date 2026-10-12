# CWIST

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Plain-C17 web framework and app server; about 2.1-2.3x Go net/http's plaintext req/s in one independent suite run.

| | |
|---|---|
| **Beats** | Go net/http |
| **Claimed result** | the-benchmarker/web-frameworks data.json of 2026-09-24 (develop branch, commit f673364): CWIST 3.6 148,679 / 154,723 / 151,250 req/s at concurrency 64 / 256 / 512 vs Go net/http ('nethttp', label 1.22) 71,499 / 67,382 / 67,239 req/s, i.e. 2.08x / 2.30x / 2.25x (derived from page data) |
| **Workload** | the-benchmarker/web-frameworks run of 2026-09-24: `zrk --plain --closed` (closed loop over keep-alive connections, not oha), 15 s at each concurrency level 64/256/512. Each headline number is the average over the routes in .env (GET /, GET /user/0, POST /user; SQL avg in .tasks/db.rake), all hello-world handlers. The framework container is pinned to cores 0-3 (SERVER_CPUS) and the load generator to cores 4-15; CWIST's server_cpu_saturation was about 0.99 on about 3.95-3.98 cores at every level (server-bound by the suite's own probe). |
| **Metric** | throughput |
| **Hardware** | Single shared host per data.json: 16 CPUs (Etc.nprocessors), Linux 7.2.6-200.fc44.x86_64. The cpu_name 'M1 Eight-Core Processor' and memory 7,733,008 kB are hardcoded in .tasks/db.rake, not measured, so the CPU model is unknown; a comment in go/Dockerfile names an AMD Ryzen 7 5700U, not confirmed for this run. Server container limited to 4 cores (SERVER_CPUS=0-3), load generator on cores 4-15. |
| **Compiler and flags** | debian:trixie-slim + build-essential (Debian trixie default GCC is 14.2; the suite does not print the version). libcwist v3.6 is built with its own Makefile (`make -j$(nproc)`), whose GCC profile is `-Ofast -g -flto=auto -ffat-lto-objects -fno-plt -falign-*=32 -fno-semantic-interposition -fomit-frame-pointer -finline-functions -fstrict-aliasing -funroll-loops`, plus -fstack-protector-strong -D_FORTIFY_SOURCE=2 on Linux. The benchmark main.c is compiled with `gcc -O2` (c/cwist/config.yaml). Go side: golang:1.27 image, `go build -trimpath`, GOAMD64=v3. |
| **Adoption** | 15 stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/c4punks/CWIST) · [benchmark](https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json) |

## Verdict

Setup: the-benchmarker/web-frameworks run of 2026-09-24 (commit f673364), zrk closed-loop keep-alive load against empty or echo hello-world routes. The server was confined to 4 cores of a 16-CPU x86-64 Linux 7.2 host; the CPU model is unknown because the cpu_name field is hardcoded. Result: CWIST 3.6 (GCC -Ofast LTO build on Debian trixie, first-party-maintained entry app) averaged 148.7k/154.7k/151.2k req/s at 64/256/512 connections, against Go net/http (golang:1.27 image, GOAMD64=v3) at 71.5k/67.4k/67.2k req/s, which is 2.08-2.30x. Both servers were CPU-saturated, and neither had errors.

## Use it when

- You want a C (not C++) HTTP server with high plaintext keep-alive throughput per core, and you can pin its workers to dedicated cores.
- Many short, CPU-light handlers on Linux, where the io_uring reactor and prefork-per-core model pay off.
- Holding very large numbers of mostly idle connections (SSE, WebSocket, long-polling): the README reports 1M loopback connections at about 244 MB peak RSS in reactor mode.
- You need HTTP/3, WebTransport or post-quantum hybrid TLS in C without assembling lsquic, BoringSSL and routing yourself.
- You need to link existing C/C++ libraries into the request path with no FFI layer.

## Skip it when

- Production services that need API stability or a track record: the repo dates from January 2026, releases v3.1 to v3.7 shipped between August and September 2026, and the README says minor releases may change public APIs until 4.0.
- Latency-SLO work at low concurrency: in the same suite run, CWIST's p99 at 64 connections was about 8.6 ms against net/http's 3.1 ms, even though its median was far lower (0.11 ms against 0.72 ms).
- Blocking or slow handlers in the default reactor mode: the handler runs on the reactor thread, so a blocking handler stalls every connection on that worker.
- HTTPS-heavy or long-idle keep-alive workloads: the README says the async path covers cleartext HTTP/1.x only, HTTPS still uses the thread-pool model for the request phase, and idle keep-alive connections are not yet reaped by a timer.
- Windows targets: only Linux, macOS and BSD are documented.

## How it is fast

By default it pre-forks one worker process per online core. Each worker is pinned to a CPU and has its own SO_REUSEPORT listen socket, and each worker runs its own reactor. The reactor uses io_uring through raw syscalls (epoll or kqueue as fallback) as a readiness notifier: it arms one-shot IORING_OP_POLL_ADD and runs the handler synchronously on the woken thread, with no completion-queue hand-offs. An optional IORING_OP_RECV path is also available. Responses are serialized straight into a per-connection output buffer and flushed in batches, and request and response share one arena. Request-line and header scans use SSE2/AVX2/NEON byte search.

## Compared with alternatives

In the same 2026-09-24 suite run, CWIST 3.6 led Drogon 1.9 by about 1.15-1.18x and led Agoo-C by about 2x at 64 connections, but only by about 1.01x at 512. Pick it over those two when you want plain C with built-in HTTP/3, WebTransport and PQ TLS. Pick Drogon (C++) or Lwan when maturity and a longer track record matter more than the last 15%.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Vendored and built in-tree: BoringSSL, lsquic, libttak, SQLite3, cJSON, uriparser, cnats, multipart-parser-c. System libraries: zlib, zstd, brotli (libbrotlienc/libbrotlicommon). Optional: libnghttp2 (HTTP/2) and libcurl (RDBMS auto-mount probing). The link line also needs -lstdc++, and the suite build installs cmake. |
| **Minimum toolchain** | C17 (-std=c17); GCC or Clang, with a separate tcc profile in the Makefile. The suite built it with Debian trixie's default GCC. |
| **Platforms** | Linux (io_uring with epoll fallback), macOS and FreeBSD (kqueue). SIMD scans have SSE2/AVX2, NEON, RVV, AltiVec and MSA paths with a scalar fallback. The default Makefile passes no -march, so x86-64 builds use the SSE2 path. |
| **Thread safety** | Not documented as a contract. By default it forks one worker process per online core, so globals and in-process state are per worker and not shared. Within a worker, the classic mode (CWIST_C1M_MODE=0) runs one thread per connection, so handlers must be reentrant. |
| **Drop-in for the baseline** | no |

## Gotchas

- The docs and code disagree on the worker count. The README's env-var table says CWIST_WORKERS defaults to 1, but app.c defaults to the online core count; set CWIST_WORKERS explicitly.
- An on-by-default response cache, Big Dumb Reply, can replay GET responses. It keys on method and path only, and it learns a response once the handler takes more than 10 ms and returns identical bytes twice. Entries live up to 300 s or 100,000 hits. Only responses carrying Vary are skipped, so per-user GET routes that are slow need Vary. The app.h field comment says this cache is 'never replayed by HTTP dispatch', but app.c serves hits from it.
- The library build uses -Ofast with LTO; your own code is compiled with whatever flags you choose. Static linking pulls in each vendored component's license: Apache-2.0 for BoringSSL and cnats, BSD-3-Clause for uriparser and libttak.
- The issue tracker shows a run of fixed security bugs in 2026: WebSocket RFC 6455 violations and OOM DoS, JWT algorithm confusion, HTTP/2 'Made You Reset', and a non-rotating TLS session-ticket key. Treat the protocol stack as young code.

## Known shortcomings

- The \~2.1-2.3x over Go net/http is only for CWIST 3.6 on the-benchmarker's develop-branch data; runs with 3.4-3.5 (including master) show 1.04-1.08x. CWIST's lead developer maintains the suite entry, and its own README has it slightly behind Axum; the-benchmarker's CPU label and memory value are hardcoded, not measured, and each figure averages three routes. 15 stars.
- p99 worse than net/http at 64 connections (8.6 vs 3.1 ms) despite a lower median. A response cache ('Big Dumb Reply') is on by default and replays GET responses keyed on method+path once a handler is slow and deterministic; per-user GET routes need Vary. Docs contradict the code (CWIST_WORKERS default; cache replay). A blocking handler stalls its whole worker; HTTPS goes through a thread pool and idle keep-alive connections are not reaped. Weekly minor releases, API may break until 4.0, one lead developer; many 2026 security fixes (WebSocket DoS, JWT algorithm confusion, HTTP/2 Made You Reset, non-rotating TLS ticket key).

## Caveats and trade-offs

Single suite run: data.json is overwritten on every run, and the suite says results from different method revisions are not comparable. Earlier snapshots with CWIST 3.4-3.5 under the older zrk method show only a small lead over net/http. Master data.json of 2026-09-20 (CWIST 3.5): 101,254 / 89,553 / 87,455 vs 96,149 / 85,406 / 83,964 req/s (1.04x-1.05x). Snapshot of 2026-09-15 (CWIST 3.5): 142.8K / 120.9K / 119.0K vs 133.1K / 112.2K / 109.9K (\~1.07-1.08x). The suite entry (c/cwist/config.yaml, main.c) is maintained by CWIST's lead developer (gg582 authors its version bumps, and the file header says it is mirrored from CWIST's benchmarks/web-frameworks/), so the implementation is first-party-tuned, though the suite runs it. CWIST's own README benchmark has it slightly behind Rust Axum (117,184 vs 121,272 req/s). Very young project with a low star count (15) and no independent track record. It vendors BoringSSL, lsquic, SQLite, cJSON and others under their own licenses.

Very new/low-adoption project (15 stars); a large feature surface (HTTP/3, WebTransport, post-quantum crypto) for a project this young raises production-hardening questions.

## Maintenance

Very actively developed: roughly weekly minor releases, last commit 2026-09-25, v3.7 is already out while v3.6 was benchmarked. MIT-licensed with 15 stars, and effectively one lead developer (gg582, 327 commits). Usable via make install, Homebrew or pkg-config, but pin an exact tag.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (the-benchmarker/web-frameworks) runs CWIST and Go net/http on one host with public code (c/cwist/config.yaml, c/cwist/main.c, c/Dockerfile, go/nethttp/main.go, .tasks/config.rake) and flags visible in the build files. Not A: the CPU name in data.json is a string hardcoded in .tasks/db.rake, not a measured CPU model, and the GCC version is only implied by the debian:trixie-slim base image.
- **Verifier notes:** The record's numbers are on the develop-branch (default) data.json, commit f673364, not the master URL it cited; master (CWIST 3.5, older method) shows only a \~1.05x lead. benchmark_url is now pinned to that commit, and the load generator is corrected from oha to zrk --closed. The 2.1-2.3x lead appears in only one run and one CWIST version (3.6). Metadata verified: MIT, not a fork, not archived, 15 stars, last commit 2026-09-25 (active).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/c4punks/CWIST>
  - <https://github.com/c4punks/CWIST/blob/main/README.md>
  - <https://github.com/c4punks/CWIST/blob/main/LICENSE>
  - <https://github.com/c4punks/CWIST/blob/v3.6/Makefile>
  - <https://github.com/c4punks/CWIST/blob/main/Makefile>
  - <https://github.com/c4punks/CWIST/blob/main/benchmarks/webserver.json>
  - <https://github.com/c4punks/CWIST/commit/54044dab3871326e61b1d8ed2e5152064a79e31a>
  - <https://github.com/c4punks/CWIST/graphs/contributors>
  - <https://github.com/the-benchmarker/web-frameworks>
  - <https://github.com/the-benchmarker/web-frameworks/blob/master/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/master/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/develop/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/5d9db5685024f61b8f8c2c25dccd0a21e96dc5f3/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/8ae370ae89075281c056a138e57de25682d36e02/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/commits/develop/c/cwist>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/README.md>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/.env>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/collect.rake>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/db.rake>
  - <https://github.com/the-benchmarker/web-frameworks/blob/develop/c/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/develop/c/Dockerfile>
  - <https://github.com/the-benchmarker/web-frameworks/blob/develop/c/cwist/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/c/cwist/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/c/cwist/main.c>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/go/Dockerfile>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/go/nethttp/main.go>
- **Sources the enricher read:**
  - <https://github.com/c4punks/CWIST>
  - <https://github.com/c4punks/CWIST/blob/main/README.md>
  - <https://github.com/c4punks/CWIST/blob/main/Makefile>
  - <https://github.com/c4punks/CWIST/blob/main/src/net/http/simd_parser.h>
  - <https://github.com/c4punks/CWIST/blob/main/src/sys/io/reactor.c>
  - <https://github.com/c4punks/CWIST/blob/main/src/net/http/async_server.c>
  - <https://github.com/c4punks/CWIST/blob/main/src/net/http/http.c>
  - <https://github.com/c4punks/CWIST/blob/main/src/net/http/writer_fast.c>
  - <https://github.com/c4punks/CWIST/blob/main/src/sys/app/app.c>
  - <https://github.com/c4punks/CWIST/blob/main/src/sys/app/worker_affinity.h>
  - <https://github.com/c4punks/CWIST/blob/main/src/sys/app/big_dumb_reply.c>
  - <https://github.com/c4punks/CWIST/blob/main/include/cwist/sys/app/app.h>
  - <https://github.com/c4punks/CWIST/blob/main/include/cwist/sys/app/big_dumb_reply.h>
  - <https://github.com/c4punks/CWIST/blob/main/src/sys/sys_info.c>
  - <https://github.com/c4punks/CWIST/issues>
  - <https://github.com/c4punks/CWIST/releases>
  - <https://github.com/c4punks/CWIST/graphs/contributors>
  - <https://github.com/c4punks/CWIST/commits/main/src/sys/app/app.c>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/c/cwist/main.c>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/c/cwist/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/c4punks/cwist`) · [data/wave5/enrich/raw/github_com_c4punks_cwist.json](../../../data/wave5/enrich/raw/github_com_c4punks_cwist.json) (enrichment confidence 0.75)

</details>
