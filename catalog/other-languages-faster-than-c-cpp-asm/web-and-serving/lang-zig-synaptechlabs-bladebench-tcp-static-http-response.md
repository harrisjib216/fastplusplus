# bladebench Zig raw TCP server

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Zig` · `MIT` · 🟡 stale

> 47-line Zig blocking TCP responder whose 2x wrk lead over C/C++ comes from skipping the request read, not codegen.

| | |
|---|---|
| **Beats** | the same minimal blocking TCP/HTTP server in C (gcc -O2) and C++ (g++ -O2) from the same repo |
| **Claimed result** | wrk -t8 -c1000 -d10s on loopback (first-party, single run): Zig 80,700 req/s vs C++ 40,715 (1.98x, derived from page data) and C 32,976 (2.45x, derived from page data); the same table marks the Zig row '701k write errors (buffer overrun)' and the C/C++ rows 0 errors. Not a like-for-like measurement (the Zig server skips the request read). |
| **Workload** | Single-threaded blocking accept loop that reads once, writes a fixed 'HTTP/1.1 200 OK' response and closes the connection, load-tested with wrk -t8 -c1000 -d10s over loopback. |
| **Metric** | throughput |
| **Compiler and flags** | Makefile: gcc -O2 and g++ -O2 for C and C++; 'zig build-exe blade_core.zig' with no optimize flag (default Debug mode, Zig 0.12 per source banner). Not -O3 and not matched. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | no |
| **Adoption** | 0 stars, 0 forks, 1 commit ('Initial Commit', 2025-07-12) |
| **Last commit** | 2025-07-12 |
| **Links** | [repository](https://github.com/Synaptechlabs/bladeBench) · [benchmark](https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/performance_summary.md) |

## Verdict

One first-party wrk run (-t8 -c1000 -d10s, loopback, hardware and versions not stated) gave the Zig Debug build 80,700 req/s against 40,715 for g++ -O2 C++ and 32,976 for gcc -O2 C (1.98x and 2.45x, derived from page data), with 701k write errors on the Zig row only; the Zig server skips the request read, so the lead reflects less work and reset connections rather than faster code.

## Use it when

- As a 47-line example of raw std.posix socket calls (socket, setsockopt, bind, listen, accept, write) in Zig 0.12, before std.posix was reshuffled in later releases.
- As a cautionary benchmark case: a responder that answers before reading the request inflates wrk req/s and produces reset connections.
- Not for any production or comparative use; the repo publishes no harness that measures equal work.

## Skip it when

- As evidence that Zig beats C or C++ on networking: the Zig server does less work (no read), is built in Debug against gcc/g++ -O2, and the run reports 701k write errors against 0 for C and C++.
- As an HTTP server of any kind: it ignores the request entirely, sends no Connection: close header although it closes after every reply, and serves one connection at a time.
- Under load you care about: every write or accept error is propagated with try out of main, so one failed syscall ends the process.
- On later Zig releases: the code targets Zig 0.12 std.posix and std.io.getStdOut APIs (the banner and README say 0.12.0+); it is not tested on anything newer.

## How it is fast

It is not faster at the same work. The Zig loop writes the response the moment accept returns and never waits for the client's request, so each connection costs accept, write and close; the C/C++ loops add a blocking read() that waits for wrk's request before they can write and accept the next connection. In a single-threaded blocking server that saved wait per connection, not Zig code generation (the Zig binary is an unoptimised Debug build), explains the 80,700 vs 40,715/32,976 req/s gap. Closing a socket with the request still unread makes the kernel reset the connection, which fits the 701k wrk write errors, about 0.87 per completed response (derived from page data: 80,700 req/s x 10 s = 807k).

## Compared with alternatives

Never as a server: zix (Zig HTTP server) and libxev (Zig event loop) have HttpArena rows against nginx, h2o and Drogon on a shared harness; the bladebench Rust row shares this repo's harness and its Debug/-O2 mismatch but at least reads the request, so neither bladebench row is a language comparison.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (Zig standard library only); benchmarking needs wrk |
| **Minimum toolchain** | Zig 0.12.0 (source banner; the repo commits zig-linux-x86_64-0.12.0.tar.xz and a binary linked by LLD 17.0.6) |
| **Platforms** | Linux x86-64 as published (POSIX sockets; other targets not documented) |
| **Thread safety** | single-threaded blocking accept loop; no shared state |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: blade_core.zig never reads the request, while blade_core.c and blade_core.cpp read() once before writing; under a single-threaded blocking loop this removes a wait per connection and makes the close abortive, so the req/s column compares different work.
- Build mismatch: the Makefile's blade_zig target runs a bare 'zig build-exe blade_core.zig' (Debug mode), which writes a binary named blade_core, not blade_zig as README and bench instructions say; the committed blade_core binary is a 2.25 MB statically linked ELF with debug info and runtime-safety symbols, i.e. the Debug build, against gcc -O2 and g++ -O2 (Rust is plain rustc, also unoptimised).
- No raw wrk output is in the repo although the README points to performance_summary.md for 'detailed logs'; it holds only the summary table, so the 0-error C/C++ rows and the 701k Zig write errors cannot be checked. No CPU, kernel, compiler or wrk versions, single run, servers on different ports, and only the Zig server sets SO_REUSEADDR.
- Every connection is closed after one reply while wrk -c1000 expects keep-alive, so all four rows mostly measure TCP connect and teardown on loopback with a 128-entry listen backlog against 1000 connections.

## Known shortcomings

- No valid measurement (tier D): the Zig server never reads the request and closes it unread (701k write errors), a Debug build against -O2 C/C++, no hardware (dp::thread_pool and fc_malloc precedent). Last commit 2025-07-12, 0 stars.
- blade_core.zig never reads the request and replies straight after accept, so the single-threaded loop skips the wait for wrk's request; the 701k write errors are about 0.87 per completed response (derived). The committed blade_core binary is the Zig build, a 2.25 MB static ELF with debug info and runtime-safety symbols (LLD 17.0.6), so a Debug build was timed against -O2; the Makefile emits blade_core, not blade_zig. The Zig server exits on any write or accept error (`try` out of main), and the README promises detailed logs but no raw wrk output is in the repo.

## Caveats and trade-offs

Not a valid language comparison. blade_core.zig accepts, writes the fixed response and closes without ever reading the request, whereas blade_core.c and blade_core.cpp read() once before writing; closing a socket with unread data makes the kernel reset the connection, which fits the 701k write errors the page reports for Zig (the page blames a 'buffer overrun'), so the Zig row measures less work and an abortive close rather than codegen. The Makefile builds Zig with a bare 'zig build-exe blade_core.zig' (Debug mode, Zig 0.12 per the source banner) and Rust with plain rustc (no -O), against gcc -O2 / g++ -O2 for C and C++; none is -O3. Each server is a single-threaded blocking accept loop that closes every connection, while wrk keeps HTTP/1.1 keep-alive and must reconnect after every response, so throughput is dominated by connection setup and teardown. Ports differ (8080, 8081, 8083) and only the Zig server sets SO_REUSEADDR. CPU, kernel, compiler and wrk versions are not stated; single run. The C and C++ servers are functionally identical yet differ by 23% (32,976 vs 40,715), which shows the noise. The README itself recommends 'Zig (if tuned)'. One commit, 0 stars. [retier] Enricher: the committed blade_core binary is the Zig build, a 2.25 MB static ELF with debug info and runtime-safety symbols (LLD 17.0.6), so a Debug build was timed against -O2; the Makefile emits blade_core, not blade_zig. The 701k write errors are about 0.87 per completed response (derived); the Zig server exits on any write or accept error, and no raw wrk output is in the repo.

Toy micro-benchmark, not a usable server library.

## Maintenance

Single 'Initial Commit' on 2025-07-12, 0 stars, 0 issues, MIT; stale toy benchmark that also commits a built binary and the Zig 0.12.0 toolchain tarball, useful only as a small socket example.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** performance_summary.md and README carry the wrk table (Zig 80,700, C++ 40,715, C 32,976 req/s) from public code (blade_core.{c,cpp,zig}, bench.sh, Makefile), but the measurement is not valid as a comparison: blade_core.zig never calls read() and closes with the request unread, while blade_core.c/.cpp read first, and the Zig row carries 701k write errors; under the no-valid-measurement precedent (dp::thread_pool, fc_malloc) this goes to D. No CPU, kernel or compiler versions are stated either, so it could not be A.
- **Verifier notes:** Downgrade C to D: the faster side does less work (no read of the request) and aborts connections, the Zig build is Debug against -O2 C/C++, and no hardware is stated; keep as a flagged entry with these shortcomings (an orchestrator could also treat it as invalid evidence of the 'faster side skips the work' kind, but the keep-and-document precedents for timed-but-incomplete work went to D). Repo is MIT, 0 stars, one commit dated 2025-07-12 (stale).
- **Fields the verifier corrected:** `last_commit`, `maintenance_status`, `stars_or_usage`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-19 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/performance_summary.md>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/README.md>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/blade_core.c>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/blade_core.cpp>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/blade_core.zig>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/bench.sh>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/LICENSE>
  - <https://github.com/Synaptechlabs/bladeBench>
  - <https://github.com/Synaptechlabs/bladeBench/commits>
- **Sources the enricher read:**
  - <https://github.com/Synaptechlabs/bladeBench>
  - <https://github.com/Synaptechlabs/bladeBench/commits>
  - <https://github.com/Synaptechlabs/bladeBench/issues>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/README.md>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/performance_summary.md>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/blade_core.c>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/blade_core.cpp>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/blade_core.zig>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/blade_core.rs>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/bench.sh>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/blade_core>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:zig/synaptechlabs/bladebench#tcp-static-http-response`) · [data/wave14/enrich/raw/lang_zig_synaptechlabs_bladebench_tcp_static_http_response.json](../../../data/wave14/enrich/raw/lang_zig_synaptechlabs_bladebench_tcp_static_http_response.json) (enrichment confidence 0.85)

</details>
