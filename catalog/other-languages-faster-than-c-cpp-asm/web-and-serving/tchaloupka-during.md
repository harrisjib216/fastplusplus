# during (D io_uring wrapper)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `D` · `BSL-1.0` · 🟢 active

> Low-level D binding to Linux io_uring (no liburing); author's echo and HTTP microbenchmarks edge C liburing servers.

| | |
|---|---|
| **Beats** | C liburing echo server (MarkReedZ/mrloop) and C++ epoll echo server (methane/echoserver), both built with -O3; in the httpbench suite also the C liburing HTTP-reply server |
| **Claimed result** | echo_server README: during 131090 req/s vs C liburing server 95894 req/s vs C++ epoll server 45063 req/s (1.37x and 2.91x, derived from page data). httpbench README (separate harness, D port of the C liburing server, RPS from the tables): during/raw vs C io_uring raw is 41404 vs 37872 (2 clients), 86500 vs 75711 (8), 150752 vs 155627 (64), 221916 vs 185000 (128), 253256 vs 246812 (256), 2012380 vs 1898736 (256 clients, pipeline depth 10), i.e. 0.97x to 1.20x (derived from page data). |
| **Workload** | Single-threaded echo server, 50 clients, 512-byte messages, 10 s, best of 3, driven by haraldh/rust_echo_bench on loopback; second data set is a fixed-reply HTTP responder under wrk at 2 to 256 connections in tchaloupka/httpbench. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3700X 8-Core, Fedora 31 Linux 5.3.12 (echo_server README); httpbench: AMD Ryzen 7 3700X (8 cores, 16 threads) host, Fedora 36, kernel 5.17.9; server in a KVM VM with 2 pinned CPUs and load generator (wrk 4.1.0) in a KVM VM with 14 pinned CPUs, both Ubuntu 22.04 (bridged network) |
| **Compiler and flags** | during echo server: dub build -b release --compiler=ldc2, ldc2-1.18.0. Baselines: built with -O3 and no -g (compiler name and version not stated). httpbench D builds: ldc2 1.29.0 with --betterC --release -O3 --boundscheck=off --ffast-math --mcpu=native; C baseline gcc -Wall -O3 -D_GNU_SOURCE -luring (gcc version not stated, liburing cloned from axboe/liburing at build time). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | io_uring with provided buffers and fixed pre-registered io buffers (README design notes); the source does not explain why it beats the C liburing server. |
| **Adoption** | 37 stars |
| **Last commit** | 2026-10-09 |
| **Links** | [repository](https://github.com/tchaloupka/during) · [benchmark](https://github.com/tchaloupka/during/blob/master/examples/echo_server/README.md) |

## Verdict

In December 2019 the author measured a single-threaded during echo server at 131,090 req/s vs mrloop (C, liburing, -O3) 95,894 and methane's C++ epoll server 45,063 (rust_echo_bench, 50 clients, 512 B, 10 s, best of 3, Ryzen 7 3700X, Fedora 31 kernel 5.3.12, ldc2 1.18.0); these are different programs and a run one day earlier showed only 1.11x over epoll. In httpbench (Fedora 36 host, ldc2 1.29.0 vs gcc -O3, server in a 2-vCPU KVM guest, wrk 4.1.0) a D port of the C liburing HTTP responder ran at 0.97x to 1.20x of the C original in single 30 s runs.

## Use it when

- D code (LDC, DMD or GDC) on Linux that needs direct io_uring access in @nogc/nothrow or -betterC code without linking the C liburing.
- Building your own D event loop or runtime that wants recent io_uring features (provided-buffer rings, multishot accept/recv, SEND_ZC, NAPI, ring resize) with liburing-2.9-level coverage.
- Single-core socket responders or proxies where syscall count per request dominates and you can batch several SQEs per io_uring_enter, as the httpbench port does.
- Code that must choose a path at runtime by kernel version: Uring.probe() reports which opcodes the running kernel supports.

## Skip it when

- C or C++ projects: liburing is the native equivalent and during adds nothing algorithmic over it.
- When you want a server or a ready event loop: during has neither; the HttpArena siblings (libxev, tokio-uring, nginx-class C servers) are complete stacks.
- Non-Linux targets or old kernels: dub.sdl declares platforms "linux", most networking ops need 5.5 to 5.7+, and the httpbench io_uring servers refuse to start without FAST_POLL (5.7+).
- Containers or users with a low RLIMIT_MEMLOCK: every ring and registered buffer counts against memlock; the README warns the tests and the echo example can fail to initialise.
- Expecting the README's 2.9x echo speedup today: those numbers come from a 2019 kernel whose socket I/O path for io_uring no longer exists and were not re-measured.

## How it is fast

There is no new algorithm: speed comes from io_uring itself (one ring shared with the kernel, registered fixed buffers via IORING_REGISTER_BUFFERS, kernel-selected provided buffers, FAST_POLL, multishot ops) plus a wrapper with no hot-path overhead: put/putWith fill SQEs directly in the mapped ring, wait() skips io_uring_enter when completions are already queued, and nothing allocates. The echo example preallocates a registered buffer pool and swaps read/write buffers per client; the httpbench responder is a near line-by-line port of the C liburing server, so any gap there reflects the wrapper versus liburing plus compiler flags, not a different design.

## Compared with alternatives

The siblings are complete servers (HttpArena entries such as libxev, tokio-uring, nginx-class C servers) or the same author's D epoll port in httpbench; pick during only when you write D and want raw io_uring control without liburing, and pick libxev (Zig) or tokio-uring (Rust) when you want a ready io_uring event loop in those languages.

## Integration

| | |
|---|---|
| **Form** | dub package (source library, builds a static lib); optional Meson build |
| **Dependencies** | none at runtime (no liburing, druntime optional under betterC); the test runner uses silly and the echo example uses mempooled |
| **Minimum toolchain** | CI matrix DMD 2.091.1 and LDC 1.24.0 up to latest; CHANGELOG 0.5.0 says the suite passes on LDC 1.21+ (frontend 2.091+); betterC tests build with DMD 2.098 |
| **Platforms** | Linux only (CI on ubuntu-latest x86-64); features gated by the running kernel |
| **Thread safety** | not documented; Uring is a handle with a non-atomic reference count (refs++ in the copy constructor), so use one ring per thread |
| **Drop-in for the baseline** | partial — replaces liburing for D code (similar prep helpers and opcode coverage), not the C/C++ echo or HTTP servers it was compared with |

## Gotchas

- Harness flaw, echo numbers not reproducible: the first published echo results (commit e12d12c, 2019-12-07) were during 88,348 vs C++ epoll 79,820 req/s (1.11x); the next day's README-only commit acc79a4 ('benchmark update') reports epoll 45,063 (-44%) and during 131,090 (+48%) and adds mrloop, with app.d unchanged and only CI, Makefile and README commits in between. The 2.91x headline therefore swung from 1.11x between two of the author's own runs of the same code.
- Harness flaw, kernel artifact: on the stated kernel 5.3.12, io_prep_rw marks every socket READ_FIXED/WRITE_FIXED REQ_F_MUST_PUNT (sockets fail io_file_supports_async) and queues it on the io_ring-wq workqueue (max_active min(sq_entries-1, 2 x CPUs), 32 on the 16-thread 3700X); the echo server's accept()ed sockets are blocking (accept passes flags 0), so each pending read parks a kernel worker in recv. The 'single threaded' during server thus did its socket I/O on up to 32 kernel threads, while the C++ epoll baseline (edge-triggered, reads until EAGAIN, so at least read, read, write and epoll_wait per echo; its own Makefile uses -O2 -g) does every syscall on one thread and mrloop polls first (POLL_ADD, then READV, then WRITEV per echo). The comparison measures 2019 io_uring punting, not D or the wrapper, and does not carry over to 5.7+ kernels.
- The echo example is a benchmark toy: onWrite ignores the write result (short writes and errors are dropped), and a failed read's negative res is stored as lastRead and reused as the next write length.
- httpbench pairs are close to same-code but not same-build: the D port uses 1024-byte provided buffers vs C 2048 and adds --mcpu=native --ffast-math to ldc2 while gcc gets plain -O3; both abort on a partial request ('FIXME: partial request handling not implemented'), and each cell is one 30 s run on a 2-vCPU KVM guest, where the README also notes an io_uring regression from kernel 5.7.16.

## Known shortcomings

- Echo test (131,090 vs 95,894 vs 45,063 req/s) compares different programs in a 2019 first-party run with the baseline compiler unstated; the httpbench gap is within noise.
- Harness flaw 1: the README-only commit acc79a4 (2019-12-08) re-ran echo, moving epoll from 79,820 to 45,063 req/s and during from 88,348 to 131,090 with app.d and the library unchanged, so the ratio went from 1.11x to 2.91x on no code change. Harness flaw 2: Linux 5.3.12 punts every socket READ_FIXED/WRITE_FIXED to io-wq (REQ_F_MUST_PUNT, up to 32 workers on the 3700X), and the accepted sockets are blocking, so each pending read parks a kernel thread; the 'single-threaded' server ran multi-threaded in the kernel against a one-thread epoll baseline.

## Caveats and trade-offs

First-party numbers from the library author. The echo baselines are different programs, not ports: mrloop is a generic C event-loop library using liburing and methane/echoserver a generic C++ epoll echo server, whereas the during example uses a preallocated mempooled buffer pool registered with io_uring and swaps read/write buffers, so the echo comparison is not same-algorithm. The echo numbers date from 2019 (ldc2-1.18.0, Fedora 31, Linux 5.3.12), are best-of-3 on loopback with the load tool on the same machine, and the baselines' compiler and version are not stated (only -O3 without -g); the library has since been rewritten for Linux 6.x and released as 0.6.0 (2026-10-09) without new measurements. The httpbench rows compare a D port (dlang/during/raw/app.d) of the C liburing HTTP responder (c/io_uring/http_uring.c) with the same provided-buffer design (D uses 1024-byte buffers, C 2048): single 30 s runs per cell on a 2-vCPU server VM, D ahead in 5 of 6 cells (up to 1.20x at 128 clients) and 3% behind at 64 clients, within plausible single-run noise, and the D build adds --mcpu=native --ffast-math while the C build is plain -O3. The httpbench C README says the D variants exist to test performance issues of the during library, not to claim a win, and the during README makes no performance claim beyond pointing to the echo example. An echo server is a socket event loop rather than an HTTP server, so the category fits loosely. [retier] The README-only commit acc79a4 (2019-12-08) re-ran echo, moving epoll from 79,820 to 45,063 req/s and during from 88,348 to 131,090 with app.d and the library unchanged (ratio 1.11x to 2.91x on no code change). Linux 5.3.12 punts every socket READ_FIXED/WRITE_FIXED to io-wq (up to 32 workers on the 3700X) and the accepted sockets are blocking, so each pending read parks a kernel thread: the 'single-threaded' server ran multi-threaded in the kernel against a one-thread epoll baseline.

D library (druntime or betterC), Linux 5.7+ io_uring only; the echo example preallocates fixed io buffers registered with io_uring and can exceed the memlock limit; the library does not use liburing, so it reimplements the ring handling in D.

## Maintenance

Active (0.6.0 released 2026-10-09 with Linux 7.1-rc4 opcode parity, BSL-1.0, 37 stars) and usable as a dub dependency, but its only performance evidence is the 2019 echo run and the httpbench port, neither re-measured on the rewritten library, and the echo comparison is a kernel-punting artifact.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** examples/echo_server/README.md shows the author's own best-of-3 runs (131090 vs 95894 vs 45063 req/s) with the D compiler and CPU stated but the baselines' compiler only described as '-O3, no -g', so first-party with partial methodology: C. The httpbench rows match the README tables but are single 30 s runs with an unstated gcc version.
- **Retiered** C to D: Enricher: a README-only commit moved the echo ratio from 1.11x to 2.91x with no code change, and on the 5.3 kernel used every fixed-buffer socket op was punted to io-wq kernel threads against a one-thread epoll baseline; cross-run and asymmetric threading with no valid measurement: C to D.
- **Verifier notes:** Echo numbers (131090/95894/45063 req/s; 1.37x and 2.91x derived) and all six httpbench during-vs-C io_uring pairs verified. Metadata confirmed: BSL-1.0, 37 stars, last commit 2026-10-09 (release 0.6.0), active. baseline_in_list set true because both echo baselines and the httpbench C server are C/C++ at -O3, the wave's listed baseline; shortcomings: not same algorithm in the echo test, 2019-era first-party numbers, baseline compiler unstated, httpbench gap within noise.
- **Fields the verifier corrected:** `baseline_in_list`, `caveats`
- **Shortcomings recorded by:** verifier batch-91 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/tchaloupka/during>
  - <https://github.com/tchaloupka/during/commits/master>
  - <https://raw.githubusercontent.com/tchaloupka/during/HEAD/README.md>
  - <https://raw.githubusercontent.com/tchaloupka/during/HEAD/examples/echo_server/README.md>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/dlang/during/meta.json>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/dlang/during/raw/app.d>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/c/io_uring/Makefile>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/c/io_uring/meta.json>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/c/io_uring/http_uring.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/tchaloupka/during/HEAD/README.md>
  - <https://raw.githubusercontent.com/tchaloupka/during/HEAD/dub.sdl>
  - <https://raw.githubusercontent.com/tchaloupka/during/HEAD/Makefile>
  - <https://raw.githubusercontent.com/tchaloupka/during/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/tchaloupka/during/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tchaloupka/during/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/tchaloupka/during/HEAD/source/during/package.d>
  - <https://raw.githubusercontent.com/tchaloupka/during/HEAD/source/during/io_uring.d>
  - <https://raw.githubusercontent.com/tchaloupka/during/HEAD/examples/echo_server/README.md>
  - <https://raw.githubusercontent.com/tchaloupka/during/HEAD/examples/echo_server/source/app.d>
  - <https://raw.githubusercontent.com/tchaloupka/during/e12d12c/examples/echo_server/source/app.d>
  - <https://raw.githubusercontent.com/tchaloupka/during/e12d12c/examples/echo_server/README.md>
  - <https://raw.githubusercontent.com/tchaloupka/during/5385b3709092b3f9581d041247613df4a196d495/examples/echo_server/README.md>
  - <https://github.com/tchaloupka/during/commits/master/examples/echo_server/source/app.d>
  - <https://github.com/tchaloupka/during/commits/master/examples/echo_server/README.md>
  - <https://github.com/tchaloupka/during/commit/acc79a4e4eec43ac07e15a7714b3811f9bd4cf8a>
  - <https://github.com/tchaloupka/during/compare/e12d12c40c020bf2f957c510913cc4805e76f976...acc79a4e4eec43ac07e15a7714b3811f9bd4cf8a>
  - <https://github.com/tchaloupka/during/issues?q=is%3Aissue>
  - <https://github.com/tchaloupka/during/issues/3>
  - <https://github.com/tchaloupka/during/issues/9>
  - <https://github.com/tchaloupka/during/pull/9/files>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/c/README.md>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/dlang/during/meta.json>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/dlang/during/raw/app.d>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/c/io_uring/Makefile>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/c/io_uring/meta.json>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/c/io_uring/http_uring.c>
  - <https://github.com/MarkReedZ/mrloop>
  - <https://github.com/MarkReedZ/mrloop/commits/master>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/HEAD/README.md>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/HEAD/mrloop.c>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/HEAD/examples/echo_server.c>
  - <https://raw.githubusercontent.com/MarkReedZ/mrloop/HEAD/Makefile>
  - <https://github.com/methane/echoserver>
  - <https://raw.githubusercontent.com/methane/echoserver/HEAD/server_epoll.cpp>
  - <https://raw.githubusercontent.com/torvalds/linux/v5.3/fs/io_uring.c>
  - <https://raw.githubusercontent.com/gregkh/linux/v5.3.12/fs/io_uring.c>
  - <https://raw.githubusercontent.com/gregkh/linux/v5.3.12/net/socket.c>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/tchaloupka/during`) · [data/wave14/enrich/raw/github_com_tchaloupka_during.json](../../../data/wave14/enrich/raw/github_com_tchaloupka_during.json) (enrichment confidence 0.65)

</details>
