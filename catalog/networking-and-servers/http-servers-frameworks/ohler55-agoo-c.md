# Agoo-C

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [HTTP servers and frameworks](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🔴 abandoned

> Small C HTTP/1.1 and GraphQL server library built on Ruby Agoo's C core; \~2.1x Go net/http at 256+ connections.

| | |
|---|---|
| **Beats** | Go net/http |
| **Claimed result** | the-benchmarker/web-frameworks data.json of 2026-09-24 (develop branch, commit f673364): agoo-c 0.7 (release v0.7.3) 74,974 / 141,394 / 149,193 req/s at concurrency 64 / 256 / 512 vs Go net/http ('nethttp', label 1.22) 71,499 / 67,382 / 67,239 req/s, i.e. 1.05x / 2.10x / 2.22x (derived from page data) |
| **Workload** | the-benchmarker/web-frameworks run of 2026-09-24: `zrk --plain --closed` (closed loop over keep-alive connections, not oha), 15 s at each concurrency level 64/256/512. Each headline number is the average over the routes in .env (GET /, GET /user/0, POST /user; SQL avg in .tasks/db.rake), all hello-world handlers. The framework container is pinned to cores 0-3 (SERVER_CPUS) and the load generator to cores 4-15. |
| **Metric** | throughput |
| **Hardware** | Single shared host per data.json: 16 CPUs (Etc.nprocessors), Linux 7.2.6-200.fc44.x86_64. The cpu_name 'M1 Eight-Core Processor' and memory 7,733,008 kB are hardcoded in .tasks/db.rake, not measured, so the CPU model is unknown; a comment in go/Dockerfile names an AMD Ryzen 7 5700U, not confirmed for this run. Server container limited to 4 cores (SERVER_CPUS=0-3), load generator on cores 4-15. |
| **Compiler and flags** | debian:trixie-slim + build-essential (Debian trixie default GCC is 14.2; the suite does not print the version). libagoo v0.7.3 is built with a plain `cd agoo-c/src && make`, which without build=release selects the debug flags `-g -Og -std=gnu11` (agoo-c src/Makefile). The benchmark app simple.c is compiled with `-O3 -std=gnu11` (c/agoo-c/Makefile). Go side: golang:1.27 image, `go build -trimpath`, GOAMD64=v3. |
| **Adoption** | 153 stars |
| **Last commit** | 2020-12-16 |
| **Links** | [repository](https://github.com/ohler55/agoo-c) · [benchmark](https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json) |

## Verdict

This is one the-benchmarker/web-frameworks run (develop-branch data.json, commit f673364, 2026-09-24) with zrk closed-loop keep-alive load averaged over GET /, GET /user/0 and POST /user. agoo-c v0.7.3 (library built with debug flags -g -Og, app with -O3, Debian trixie GCC) served 74,974 / 141,394 / 149,193 req/s at 64 / 256 / 512 connections. Go net/http (label 1.22, golang:1.27 image) served 71,499 / 67,382 / 67,239, making agoo-c 1.05x / 2.10x / 2.22x. The server was pinned to 4 cores of an unidentified 16-CPU x86-64 host running Linux 7.2, with the load generator on the other 12. At c=64 agoo-c used only 58% of its 4 cores, below the suite's 75% server-bound threshold, so that point does not measure the framework cleanly.

## Use it when

- A C program on Linux or macOS that needs an embedded HTTP/1.1 endpoint for trusted, internal traffic, with many keep-alive connections (256+, where it measured 2.1-2.2x Go net/http on 4 server cores)
- Handlers cheap enough to run inline on IO threads as 'quick' hooks, ideally returning constant or precomputed responses that can be ref-counted and reused
- You want a GraphQL endpoint (SDL schema, queries, mutations, introspection) from plain C with only pthread and libm as dependencies
- A few routes plus a small set of static files, which it serves from an in-memory cache that re-stats files every 5 s
- Studying or forking a compact accept-thread, IO-loop and ring-queue server design (37 .c files)

## Skip it when

- Internet-facing or untrusted clients. Content-Length is parsed with strtoul and added to the header length without an overflow check (the same pattern is reported as a heap overflow in Ruby Agoo issue #139). The GraphQL evaluator has no depth limit or fragment-cycle check (CVE-2022-30288, fixed upstream in Ruby Agoo 2.14.3, not here). There have been no commits since 2020-12-16.
- Low concurrency: at 64 connections it was only 1.05x net/http and had a higher median latency (0.95 vs 0.72 ms)
- You need HTTP/2 (issue #12, promised for early 2020 but never shipped), chunked request bodies, PATCH, headers over 8 KB, or strict HTTP header handling
- Windows, or any project that needs a maintained dependency with security fixes. For those, use a maintained sibling; for Agoo's core specifically, the Ruby gem (v2.15.15, 2026) is the maintained home.
- C++ codebases wanting an object API: it has only a C API with one process-wide agoo_server global, a blocking agoo_start that installs its own signal handlers, and agoo_respond calls exit() when out of memory

## How it is fast

A listener thread accepts connections, sets TCP_NODELAY and passes them through a fixed-size ring queue (atomic head/tail with a pipe for wakeups) to a pool of connection-loop threads. The pool size is online CPUs times agoo_io_loop_ratio (default 0.5; the benchmark app sets 1.0), and each thread runs its own poll() readiness loop. Hooks registered as 'quick' run inline on the IO thread, skipping the hop to eval threads. Responses are pre-serialized byte buffers with atomic reference counts, so a constant response can be built once and shared, and each loop recycles response objects from a free list. Parsing is minimal: strstr to find the end of the headers, a switch on the method's first letter, a linear list of glob routes, and a single malloc'd copy of the message with pointer slices into it instead of a header table. Pipelined requests are handled in a loop.

## Compared with alternatives

In the same 2026-09-24 run, CWIST (C) beat agoo-c at every concurrency: 148,679 vs 74,974 req/s at c=64, and roughly level at 512 (151,250 vs 149,193). Drogon led at c=64 (126,432) but trailed by 5-13% at 256/512 (134,984 / 131,608 vs 141,394 / 149,193). Pick agoo-c only if you want its built-in GraphQL server in a tiny C library and can accept an unmaintained 2019 core behind a trusted boundary.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | pthread, libm; OpenSSL optional (make SSL=true, but the Makefile only looks under /usr/local/opt/openssl or /usr/local/openssl) |
| **Minimum toolchain** | C11 with &lt;stdatomic.h&gt; (README: 'A C11 compiler or gcc-7'); the Makefile uses -std=gnu11 on Linux and -std=c11 on macOS |
| **Platforms** | Linux and macOS only (the Makefile branches on uname; code uses POSIX poll, pipe and pthreads). CPU architecture requirements are not documented. |
| **Thread safety** | Handlers run concurrently. Quick hooks run on the IO-loop threads and other hooks on agoo_server.thread_cnt eval threads, so handlers must be thread-safe. Server state is a single process-wide global, so there is one server per process. |
| **Drop-in for the baseline** | no |

## Gotchas

- agoo_init zeroes agoo_server.thread_cnt, and the examples always set it to 1 (this is not documented). With 0, no eval threads start, so non-quick hooks and the GraphQL routes (registered non-quick) are queued but never run. The eval queue has 1024 slots, and a push spins while it is full.
- A plain `make` builds the library with debug flags (-g -Og). Use the top-level `make release` for -O3; the benchmark used the debug build. The Makefile never defines HAVE_SYS_EPOLL_H or PLATFORM_LINUX, so the Linux build uses the poll() path (10 ms max wait) and skips TCP_QUICKACK, even though the vendored code supports both.
- Parser limits: headers must fit in 8 KB or you get 431. POST and PUT require a Content-Length or you get 411, and header lookup is a case-sensitive strncmp, so a lowercase 'content-length:' also gets 411. Only GET, POST, PUT, DELETE, HEAD, OPTIONS and CONNECT are accepted; anything else gets 400. The keep-alive idle timeout is hard-coded at 10 s.
- The OpenSSL branch for /usr/local/openssl sets `CFLAGS= -DHAVE_OPENSSL_SSL_H`, which overwrites the other flags instead of appending, and neither branch finds a distro OpenSSL under /usr/include. Expect to edit the Makefile to get TLS.

## Known shortcomings

- The 2.1-2.2x over Go net/http is from the-benchmarker's develop-branch data with libagoo built in debug mode (-g -Og); master data shows 0.99-1.45x and older runs had it slower than net/http; the-benchmarker's CPU label and memory value are hardcoded, not measured, and each figure averages three routes. Abandoned since 2020-12.
- Vendors a 2019 snapshot of Ruby Agoo's C core: con.c has the unchecked Content-Length arithmetic that Ruby Agoo #139 (open) reports as a heap overflow, and gqleval.c lacks the GraphQL depth/fragment-cycle fix for CVE-2022-30288 (disputed; fixed in Ruby Agoo 2.14.3). The benchmark understates it: besides the -g -Og build, the Makefile never defines HAVE_SYS_EPOLL_H or PLATFORM_LINUX, so Linux builds use poll() with a 10 ms wait and skip TCP_QUICKACK. agoo_init zeroes thread_cnt, so non-quick hooks never run unless the caller sets it. Case-sensitive header lookup (lowercase content-length gets 411), no chunked request bodies, 8 KB header cap, no PATCH, no HTTP/2. OpenSSL build branch overwrites CFLAGS. CWIST beat it at every concurrency in the same run.

## Caveats and trade-offs

Single suite run: data.json is overwritten on every run, and the suite says results from different method revisions are not comparable. At concurrency 64 agoo-c's server_cpu_saturation was only 0.58 (2.34 of 4 cores), below the suite's 75% server-bound threshold, so the c=64 figure is not a clean framework number; at 256/512 it was 0.99. Earlier snapshots vary widely. Master data.json of 2026-09-20 (older zrk method, no core pinning) shows 95,173 / 124,024 / 114,466 vs nethttp 96,149 / 85,406 / 83,964 req/s (0.99x / 1.45x / 1.36x). Under the pre-September oha method (a new connection per request, June-August 2026) agoo-c recorded only \~1.3-2.0K req/s vs nethttp \~2.1-26K, so it was slower there. The suite builds libagoo in its default debug mode (-g -Og), which likely understates agoo-c. The tested release v0.7.3 dates from 2019-11-10, and there are no commits since 2020-12-16.

Unmaintained since \~2020; C API only, so C++ use requires wrapping; only roughly ties Go net/http at the lowest tested concurrency.

## Maintenance

Abandoned: the last commit is 2020-12-16 and the last tag v0.7.3 is from 2019-11-10. It is MIT-licensed and about 450 KB of C, so it can be vendored, but it carries a 2019 snapshot of Ruby Agoo's core without the later upstream crash and security fixes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent suite (the-benchmarker/web-frameworks) with public code (c/agoo-c/config.yaml, c/agoo-c/Makefile, c/agoo-c/simple.c, c/Dockerfile, go/nethttp/main.go, .tasks/config.rake) and build flags derivable from it. Not A: the CPU name in data.json is a string hardcoded in .tasks/db.rake, not a measured CPU model, and the GCC version is only implied by the debian:trixie-slim base image.
- **Verifier notes:** The record's numbers are on the develop-branch (default) data.json, commit f673364, not the master URL it cited; master currently shows only 0.99x-1.45x. benchmark_url is now pinned to that commit, and the load generator is corrected from oha to zrk --closed. The odd c=64 dip is explained by the suite's own saturation probe (server only 58% busy). Metadata verified: MIT, not a fork, not archived, 153 stars, last commit 2020-12-16 (abandoned).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ohler55/agoo-c>
  - <https://github.com/ohler55/agoo-c/blob/develop/README.md>
  - <https://github.com/ohler55/agoo-c/blob/develop/LICENSE>
  - <https://github.com/ohler55/agoo-c/tags>
  - <https://github.com/ohler55/agoo-c/blob/v0.7.3/src/Makefile>
  - <https://github.com/the-benchmarker/web-frameworks>
  - <https://github.com/the-benchmarker/web-frameworks/blob/master/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/master/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/develop/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/commits/master/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/README.md>
  - <https://github.com/the-benchmarker/web-frameworks/blob/master/README.md>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/.env>
  - <https://github.com/the-benchmarker/web-frameworks/blob/master/.env>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/run.sh>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/collect.rake>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/.tasks/db.rake>
  - <https://github.com/the-benchmarker/web-frameworks/blob/develop/c/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/develop/c/Dockerfile>
  - <https://github.com/the-benchmarker/web-frameworks/blob/develop/c/agoo-c/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/c/agoo-c/Makefile>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/c/agoo-c/simple.c>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/go/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/go/Dockerfile>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/go/nethttp/main.go>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/go/nethttp/config.yaml>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/4e8a2e9b0b0ff07c8ea844bccbd4fb6a55676602/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/2dffd2559e4baf8b28e6fa53df9669fcc439a760/data.json>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/0fccb1d5a502432d76dc1364ab6babf709ef1380/data.json>
- **Sources the enricher read:**
  - <https://github.com/ohler55/agoo-c>
  - <https://github.com/ohler55/agoo-c/blob/develop/README.md>
  - <https://github.com/ohler55/agoo-c/blob/develop/CHANGELOG.md>
  - <https://github.com/ohler55/agoo-c/blob/develop/Makefile>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/Makefile>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/Makefile>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo.h>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo.c>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/server.h>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/server.c>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/con.h>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/con.c>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/queue.h>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/queue.c>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/ready.c>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/hook.h>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/hook.c>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/req.h>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/res.c>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/text.c>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/page.c>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/http.c>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/upgraded.c>
  - <https://github.com/ohler55/agoo-c/blob/develop/src/agoo/gqleval.c>
  - <https://github.com/ohler55/agoo-c/blob/develop/scripts/update_from_agoo.sh>
  - <https://github.com/ohler55/agoo-c/blob/develop/example/simple/main.c>
  - <https://github.com/ohler55/agoo-c/blob/develop/example/simple/Makefile>
  - <https://github.com/ohler55/agoo-c/blob/develop/example/graphql/simple/main.c>
  - <https://github.com/ohler55/agoo-c/blob/develop/example/graphql/simple/Makefile>
  - <https://github.com/ohler55/agoo-c/issues?q=is%3Aissue>
  - <https://github.com/ohler55/agoo-c/issues/2>
  - <https://github.com/ohler55/agoo-c/issues/9>
  - <https://github.com/ohler55/agoo-c/issues/10>
  - <https://github.com/ohler55/agoo-c/issues/12>
  - <https://github.com/ohler55/agoo-c/pulls?q=is%3Apr>
  - <https://github.com/ohler55/agoo-c/commits/develop>
  - <https://github.com/ohler55/agoo-c/tags>
  - <https://github.com/ohler55/agoo>
  - <https://github.com/ohler55/agoo/tags>
  - <https://github.com/ohler55/agoo/blob/develop/ext/agoo/extconf.rb>
  - <https://github.com/ohler55/agoo/blob/develop/CHANGELOG.md>
  - <https://github.com/ohler55/agoo/issues/109>
  - <https://github.com/ohler55/agoo/issues/139>
  - <https://github.com/ohler55/agoo/issues/140>
  - <https://github.com/advisories/GHSA-h385-52j6-9984>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2022-30288>
  - <https://raw.githubusercontent.com/the-benchmarker/web-frameworks/f673364fb30748e5bb8e57319ec2772bc872f78a/data.json>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/c/agoo-c/simple.c>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/c/agoo-c/Makefile>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/c/agoo-c/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/c/config.yaml>
  - <https://github.com/the-benchmarker/web-frameworks/blob/f673364fb30748e5bb8e57319ec2772bc872f78a/c/Dockerfile>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/ohler55/agoo-c`) · [data/wave5/enrich/raw/github_com_ohler55_agoo_c.json](../../../data/wave5/enrich/raw/github_com_ohler55_agoo_c.json) (enrichment confidence 0.75)

</details>
