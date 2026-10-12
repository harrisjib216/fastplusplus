# D (LDC, betterC) port of the C epoll raw HTTP responder (httpbench)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `D` · `Unlicense` · 🔴 abandoned

> Single-file betterC D port of a C epoll 'Hello, World!' HTTP responder; matches the gcc -O3 original within 10%.

| | |
|---|---|
| **Beats** | the C epoll raw HTTP responder in the same suite (c/epoll/http_epoll.c, gcc -O3), same fixed 'Hello, World!' reply, prefork over 2 CPUs |
| **Claimed result** | No claim in the README; the tables show parity. Level-triggered D vs C RPS: 43752 vs 39886 (2 clients), 93942 vs 88906 (8), 176532 vs 187141 (64), 232039 vs 226433 (128), 276433 vs 261440 (256), 2075254 vs 2132917 (pipelined); edge-triggered D vs C: 43096 vs 39911, 86692 vs 85850, 166672 vs 173116, 234975 vs 216984, 261737 vs 258486, 1938169 vs 2005563. Ratios 0.94x to 1.10x (derived from page data); D ahead in 8 of 10 non-pipelined cells (behind at 64 clients) and about 3% behind in both pipelined cells. |
| **Workload** | Fixed-response HTTP/1.1 keep-alive responder (no parsing, no routing) under wrk for 30 s at 2, 8, 64, 128 and 256 connections, plus 256 connections with pipeline depth 10; level-triggered and edge-triggered variants, prefork over 2 pinned CPUs. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3700X (8 cores, 16 threads) host, Fedora 36, kernel 5.17.9; server in a KVM VM with 2 pinned CPUs and load generator (wrk 4.1.0) in a KVM VM with 14 pinned CPUs, both Ubuntu 22.04 (bridged network) |
| **Compiler and flags** | D: ldc2 1.29.0 via dub, DFLAGS '--betterC' from dlang/epoll/meta.json with the runner default '--release -O3 --boundscheck=off --ffast-math --mcpu=native' appended (_suite/runner.d applyDefaultBuildEnv); C: gcc -Wall -O3 -D_GNU_SOURCE (plus -D EDGE for the edge variant) from c/epoll/Makefile, gcc version not stated (build-essential in an unpinned debian:testing Docker image, _suite/Dockerfile). |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | no |
| **Adoption** | 19 stars |
| **Last commit** | 2022-05-30 |
| **Links** | [repository](https://github.com/tchaloupka/httpbench) · [benchmark](https://github.com/tchaloupka/httpbench/blob/master/README.md) |

## Verdict

In tchaloupka/httpbench (2022), wrk 4.1.0 ran in a 14-vCPU KVM guest and the servers in a 2-vCPU KVM guest on a Ryzen 7 3700X host. The LDC 1.29.0 betterC port served 43,752, 93,942, 176,532, 232,039 and 276,433 req/s level-triggered at 2, 8, 64, 128 and 256 connections, against 39,886, 88,906, 187,141, 226,433 and 261,440 for the gcc -O3 C original. With pipeline depth 10 it served 2,075,254 against 2,132,917. Both send identical 192-byte responses (BPS/RPS), and the ratios of 0.94x to 1.10x are parity within single-run noise.

## Use it when

- As a reference ceiling for epoll servers on your own machine: run it next to a framework to see how much the framework costs over raw syscalls.
- As evidence that betterC D compiled with LDC runs syscall-bound event-loop code as fast as gcc -O3 C, with no GC or druntime.
- As a starting point for a fixed-reply Linux endpoint (health check, load-balancer probe) where every request gets the same bytes.
- To compare level-triggered and edge-triggered epoll: both variants come from one file via --d-version=EdgeTriggered.

## Skip it when

- Any real HTTP service: it parses nothing, has no routing or request bodies, and aborts on a partial request.
- Expecting D to beat C: the tables show parity (0.94x to 1.10x in single runs), with D behind at 64 connections and about 3% behind when pipelined.
- Non-Linux platforms: it depends on epoll and accept4.
- Processes with more than 511 open descriptors: clients live in a 512-slot array indexed by fd and the runner builds with --boundscheck=off, so a higher fd writes out of bounds.
- Slow clients or large replies: send()'s return value is ignored, so a short write silently truncates the response stream.

## How it is fast

It uses the same machinery as the C original. prefork.d launches one process per CPU, each with its own SO_REUSEPORT listener. Sockets are non-blocking, multiplexed with epoll (level- or edge-triggered) and set to TCP_NODELAY. A send buffer pre-filled with 512 copies of the response lets a pipelined batch of N requests go out in one send() of N x 192 bytes, with no allocation per request. betterC drops druntime and the GC, so the D binary is libc calls and syscalls, effectively the same program as the C version. The D port also keeps per-client buffers inline in an fd-indexed static array and takes up to 256 events per epoll_wait (C: 128).

## Compared with alternatives

The siblings are deployable servers (the HttpArena entries, nginx-class proxies) or the same author's during io_uring wrapper. This one is a measuring stick, not a server. In the same httpbench tables it edged during raw (PF) and the C io_uring raw server at every connection count (for example 276,433 vs 253,256 and 246,812 req/s at 256), so use it to bound what D on epoll can reach. Use bladebench's Rust and Zig raw-socket rows for the same kind of comparison in those languages.

## Integration

| | |
|---|---|
| **Form** | source-drop (one D file run as a dub single-file package: dub build --single app.d) |
| **Dependencies** | none beyond libc and Linux headers via druntime's core.sys bindings (betterC, no Phobos) |
| **Minimum toolchain** | ldc2 1.29.0 as measured (uses ldc.intrinsics.llvm_expect under LDC, a no-op fallback otherwise); C baseline built with gcc -O3, version unstated |
| **Platforms** | Linux only (epoll, accept4); measured on x86-64 with --mcpu=native |
| **Thread safety** | single-threaded process; scales by running one process per CPU (prefork.d) with SO_REUSEPORT |
| **Drop-in for the baseline** | partial: same protocol behaviour and listen port as the C responder for well-formed keep-alive requests, but it hard-codes port 8080 instead of reading it from argv, and it aborts where the C version waits for the rest of a partial request |

## Gotchas

- Harness flaw: the port differs from the C original on error paths. On any read that holds no complete request, or ends with a partial one, D hits assert(0), which kills that worker; C keeps buffering. D ignores send()'s return; C exits on a short send. D uses inline 2048-byte buffers in a 512-slot array; C mallocs 4096 bytes per accept (never freed) in a 2048-slot array. prefork.d does not restart dead workers, and runner.d parses only wrk's Non-2xx line, not 'Socket errors'. So a worker crash would show up only as lower RPS, never as an error count.
- Harness flaw: each cell is one 30 s wrk run (no -b best-of option) after a 3 s warm-up, against a 2-vCPU KVM guest. With prefork, each process binds its own SO_REUSEPORT socket, so at 2 and 8 connections the kernel's hash decides how connections split across the two workers. That split can differ between the C and D runs, which is enough to explain the 2-client (1.10x) and 8-client (1.06x) leads. The stated test command covers only 8, 64, 128 and 256 connections; the 2-client table's command is not given.
- Flags are unmatched: runner.d appends --release -O3 --boundscheck=off --ffast-math --mcpu=native to D's --betterC, while the C Makefile uses plain gcc -Wall -O3. The gcc version is not recorded: the Dockerfile uses unpinned debian:testing build-essential, and the measured service VM ran Ubuntu 22.04.
- Toy request counter, shared with the C version (whose comment calls it 'unusable in real servers'): after a \r that does not start \r\n\r\n it skips ahead 5 bytes. A final header line of one or two characters therefore hides the request terminator. That is harmless for wrk's fixed request and wrong for real clients.

## Known shortcomings

- Parity, not a win: 0.94-1.10x in single 30 s runs; flags unmatched (the D build adds --mcpu=native --ffast-math); the D port differs from the C program (epoll batch 256 vs 128, inline buffers); gcc version unstated.
- The port differs from C on error paths: assert(0) kills a worker on a partial request, the send() return is ignored, and the 512-slot fd array runs with --boundscheck=off; prefork.d never restarts dead workers, and runner.d parses only wrk's Non-2xx count, not 'Socket errors', so a crash shows only as lower RPS. Single 30 s runs; the SO_REUSEPORT hash splits 2 or 8 connections unevenly per run, enough to explain D's 1.10x/1.06x leads. The toy request counter skips 5 bytes after a non-separator \r (shared with C). Parity, not a win.

## Caveats and trade-offs

This is a parity data point, not a win: counting the 10 non-pipelined cells, D is ahead in 8 and behind in 2 (64 clients, both variants) by at most 10%, and about 3% behind in both pipelined cells (0.97x); single 30 s runs with no variance reported, so the differences are probably noise. The D build adds --mcpu=native and --ffast-math while the C build is plain -O3 without -march=native, so the flags are not matched (likely irrelevant for a syscall-bound loop). The C file is frevib's epoll echo server slightly modified; the D file is a near line-by-line port calling the same libc functions, but it is not identical: epoll_wait takes 256 events per call in D versus 128 in C, D keeps each client's 2048-byte buffer inline in a static array while C mallocs a 4096-byte buffer on every accept, and D skips C's send-length checks and partial-request handling (asserts instead). The suite's own C README says the D variants exist to test performance issues of the during library, and the main README presents the C servers as the reference ceiling, so neither source claims D is faster. Benchmark code, flags, ldc2 1.29.0 and the CPU are public; only the gcc version is missing. Unlicense is a public-domain dedication with no patent grant. Last commit 2022-05-30. [retier] The port differs from C on error paths (assert(0) kills a worker on a partial request, the send() return is ignored, 512-slot fd array with --boundscheck=off); prefork.d never restarts dead workers and runner.d parses only wrk's Non-2xx count, so a crash shows only as lower RPS. Single 30 s runs; the SO_REUSEPORT hash splits 2 or 8 connections unevenly per run, enough to explain D's 1.10x/1.06x leads.

betterC @nogc D, i.e. D used as a C replacement without druntime, GC or exceptions; a micro benchmark that does not parse HTTP, so it says nothing about a real server.

## Maintenance

Abandoned since 2022-05-30 (19 stars, 4 forks, 89 commits, Unlicense, so copyable with no attribution); nothing has been re-measured since ldc2 1.29.0 and kernel 5.15, and it is a benchmark fixture rather than a maintained component.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** All twelve D-vs-C RPS pairs match the README multi-core and pipelining tables, and the code (_suite/runner.d, c/epoll/http_epoll.c with c/epoll/Makefile, dlang/epoll/app.d with dlang/epoll/meta.json), both flag sets, ldc2 1.29.0 and the Ryzen 7 3700X host are public; it falls short of A only because the gcc version is unstated (unpinned debian:testing build-essential image). Kept at C because the result is parity from single 30 s runs (0.94x to 1.10x), not a demonstrated win.
- **Verifier notes:** Numbers verified exactly against README.md tables; workload, hardware, license (Unlicense), stars (19) and last commit (2022-05-30, abandoned) confirmed. Shortcomings to record: parity not a win, single runs, unmatched flags (D --mcpu=native --ffast-math only), D port differs in epoll batch size and buffer handling, gcc version unstated.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-91 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/tchaloupka/httpbench>
  - <https://github.com/tchaloupka/httpbench/commits/master>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/_suite/runner.d>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/_suite/Dockerfile>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/c/README.md>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/c/epoll/Makefile>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/c/epoll/meta.json>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/c/epoll/http_epoll.c>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/dlang/epoll/meta.json>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/dlang/epoll/app.d>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/tchaloupka/httpbench>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/dlang/epoll/app.d>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/dlang/epoll/meta.json>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/c/epoll/http_epoll.c>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/c/epoll/Makefile>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/c/epoll/meta.json>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/c/README.md>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/_suite/runner.d>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/_suite/prefork.d>
  - <https://raw.githubusercontent.com/tchaloupka/httpbench/HEAD/_suite/Dockerfile>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:d/tchaloupka/httpbench#raw-epoll-http-responder`) · [data/wave14/enrich/raw/lang_d_tchaloupka_httpbench_raw_epoll_http_responder.json](../../../data/wave14/enrich/raw/lang_d_tchaloupka_httpbench_raw_epoll_http_responder.json) (enrichment confidence 0.65)

</details>
