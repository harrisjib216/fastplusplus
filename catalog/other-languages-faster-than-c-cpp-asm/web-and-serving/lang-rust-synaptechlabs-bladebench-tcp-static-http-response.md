# bladebench Rust raw TCP server

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Web and serving](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT` · 🟡 stale

> Toy Rust std::net TCP server measured 1.21x faster than identical C++ and 1.5x than C; invalid comparison.

| | |
|---|---|
| **Beats** | the same minimal blocking TCP/HTTP server in C (gcc -O2) and C++ (g++ -O2) from the same repo |
| **Claimed result** | wrk 8 threads, 1000 connections, 10 s: Rust 49,388 req/s vs C++ 40,715 (1.21x, derived from page data) and C 32,976 (1.50x, derived), \~0 socket errors. |
| **Workload** | Single-threaded blocking accept loop that reads once, writes a fixed 'HTTP/1.1 200 OK' response and closes the connection, load-tested with wrk -t8 -c1000 -d10s over loopback. |
| **Metric** | throughput |
| **Compiler and flags** | Makefile: gcc -O2 blade_core.c, g++ -O2 blade_core.cpp, 'rustc blade_core.rs' with no -O or opt-level (an unoptimised debug build), and 'zig build-exe blade_core.zig' (Debug by default). No compiler versions. The C/C++ side is not -O3, and the optimisation levels are not matched. |
| **Kind** | language-level claim |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | no |
| **Adoption** | 0 stars, 1 commit |
| **Last commit** | 2025-07-12 |
| **Links** | [repository](https://github.com/Synaptechlabs/bladeBench) · [benchmark](https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/performance_summary.md) |

## Verdict

One wrk run each (8 threads, 1000 connections, 10 s, loopback, hardware and compiler versions not stated) against single-threaded accept/read/write/close servers gave Rust (plain rustc, unoptimised) 49,388 req/s, C++ (g++ -O2) 40,715 and C (gcc -O2) 32,976. The ratios (1.21x and 1.5x, derived from page data) are within the noise shown by the identical C and C++ servers, and the published error counts do not match how wrk counts server-side closes.

## Use it when

- As a 15-line example of a blocking std::net accept loop, for teaching or for a quick loopback smoke test.
- As a starting harness to redo the comparison properly: build with rustc -O (or cargo --release) and gcc/g++ -O3, add a 'Connection: close' header or read the full request, alternate the run order and repeat each run several times.
- Not as evidence for choosing Rust over C or C++ for a server; use the HttpArena entries for that.

## Skip it when

- Any production or benchmark use: one connection at a time, no request parsing, no keep-alive, no timeouts, and a panic (server exit) on any accept, read or write error because of unwrap().
- Quoting the 49,388 vs 40,715 vs 32,976 req/s figures: the C and C++ servers are the same code yet differ by 23%, and the ranking follows the order bench.sh ran them in.
- Comparing optimised code: the Makefile builds Rust with plain `rustc` (opt-level 0, debug assertions on) and Zig in Debug mode, against gcc and g++ at -O2.
- Learning async or multi-threaded Rust networking: the summary recommends 'Rust with async' for production, but no async server is in the repo.

## How it is fast

Nothing in the code is faster: all four servers make the same accept/read/write/close syscalls per connection, so the time goes to kernel TCP setup and teardown on loopback and to the wrk client. Rust's TcpListener::bind also sets SO_REUSEADDR and uses the same listen backlog of 128 as the C and C++ servers, which affects rebinding, not throughput. The 1.21x and 1.5x gaps are run-to-run and run-order noise, not codegen (see gotchas).

## Compared with alternatives

Never for performance: the HttpArena Rust tokio entry compares a real multi-core Rust HTTP/1.1 server against nginx and libreactorng built at -O3 on the same endpoints, while bladeBench is a single-threaded toy with an unoptimised Rust build.

## Integration

| | |
|---|---|
| **Form** | source-drop (one .rs file, built with rustc directly; no Cargo project) |
| **Dependencies** | none (Rust std only) |
| **Minimum toolchain** | not documented for Rust; README lists gcc, g++, rustc and zig 0.12.0+, and wrk for the benchmark |
| **Platforms** | Linux as run (C and C++ use netinet/in.h and unistd.h; the Rust version uses only std::net and is portable); hardware and kernel not documented |
| **Thread safety** | single-threaded blocking loop; one client at a time |
| **Drop-in for the baseline** | no |

## Gotchas

- Error column not from wrk: every server sends an HTTP/1.1 response with Content-Length and no 'Connection: close', so wrk keeps the connection alive, resets its parser and then sees the server's close as EOF at the start of the next response, which wrk.c counts as a read error (or a write error if its next request hits the reset first). The C, C++ and Rust runs should therefore each report roughly one socket error per request, yet performance_summary.md lists 0, 0 and \~0. The README promises 'detailed logs' there, but the file holds only a hand-made table, so the numbers cannot be checked against raw wrk output.
- Run order: bench.sh runs one 10 s wrk test per server in the fixed order C, C++, Rust, Zig, and req/s rises in exactly that order (32,976, 40,715, 49,388, 80,700). With one run each, a warm-up or order effect cannot be separated from the language, and the identical C and C++ servers differ by 23%.
- Zig row: the Zig server writes the response without ever reading the request and then closes, so the kernel resets connections with unread data; that, not a 'buffer overrun' as the summary says, fits the 701k write errors behind its 80,700 req/s. `zig build-exe blade_core.zig` outputs blade_core, not the blade_zig the README tells you to run, and the committed blade_core binary is that Zig server as a statically linked Debug build with debug info.
- Asymmetries: the Rust server binds 127.0.0.1 while C and C++ bind INADDR_ANY, Rust uses write_all where C and C++ make one write call, and the Rust binary is an unoptimised debug build; none of these is plausibly the cause of a 21-50% throughput difference in a syscall-bound loop.

## Known shortcomings

- Degenerate benchmark (tier D): Rust built with no -O against C/C++ at -O2, a syscall-bound accept/close loop, identical C and C++ servers 23% apart, single run. Last commit 2025-07-12, 0 stars.
- The error column is not what wrk reports: every server closes after a keep-alive HTTP/1.1 response without 'Connection: close', so wrk counts each close as a read or write error, yet performance_summary.md lists 0, 0 and \~0 for C, C++ and Rust; no raw logs are in the repo. Requests per second rise exactly in bench.sh run order (C, C++, Rust, Zig) with one run each. Zig never reads the request, so its errors come from connection resets, not a 'buffer overrun', and the committed blade_core binary is the Zig Debug build.

## Caveats and trade-offs

Not a valid language comparison. The Rust build has no optimisation flag while C and C++ use -O2. All four servers are the same single-threaded blocking loop (accept, one read, write a fixed 'HTTP/1.1 200 OK ... OK' response, close), so the time goes to kernel accept/close and the wrk client, not to language codegen. The C and C++ servers are functionally identical yet differ by 23% (32,976 vs 40,715 req/s), which shows the run-to-run noise exceeds the claimed Rust margin. There is one 10 s run per server and no repetitions, and CPU, kernel and compiler versions are not stated. Minor asymmetries: the Rust server binds 127.0.0.1 while C and C++ bind INADDR_ANY (wrk connects to 127.0.0.1 in every case); Rust uses write_all and unwrap() (a reset would abort the server) where C and C++ do a single write; C reads 1023 bytes and C++ 1024. The listen backlog is 128 in C, C++ and Rust std alike. The Zig row (80,700 req/s) came with 701k write errors. The repo has 0 stars and a single commit (2025-07-12). [retier] Enricher: the error column is not what wrk reports; every server closes after a keep-alive HTTP/1.1 response without 'Connection: close', so wrk counts each close as a read or write error, yet performance_summary.md lists 0, 0 and \~0 for C, C++ and Rust, and no raw logs are in the repo. Requests per second rise exactly in bench.sh run order (C, C++, Rust, Zig) with one run each. Zig never reads the request, so its errors come from connection resets, and the committed blade_core binary is the Zig Debug build.

Toy micro-benchmark, not a usable server library.

## Maintenance

One commit ('Initial Commit', 2025-07-12), 0 stars, MIT; abandoned toy code with no tests or raw benchmark logs, copyable only as an example of a blocking std::net loop, not as evidence of Rust out-running C or C++.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** The numbers are on performance_summary.md and in the README, but the benchmark is degenerate and gives no valid language measurement. The Rust binary is unoptimised (plain rustc, no -O), and each server is a single-threaded, syscall-bound accept/read/write/close loop. Each server got one 10 s wrk run with no hardware or compiler versions stated, and the byte-for-byte equivalent C and C++ servers differ by 23%. That is the degenerate-benchmark precedent (ThreadPool, hop) for D.
- **Verifier notes:** Downgraded C to D under the degenerate-benchmark precedent. It is kept rather than rejected because the numbers are real runs, not fabricated or a no-op. Shortcomings to record: Rust built without -O while C/C++ use -O2 (not -O3); the syscall-bound accept/close loop shows no language effect; identical C and C++ servers 23% apart; single 10 s run; no hardware or compiler versions; 0 stars, 1 commit, stale.
- **Fields the verifier corrected:** `last_commit`, `maintenance_status`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-18 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/performance_summary.md>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/README.md>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/blade_core.c>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/blade_core.cpp>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/blade_core.rs>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/bench.sh>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/std/src/sys/net/connection/socket/mod.rs>
  - <https://github.com/Synaptechlabs/bladeBench>
  - <https://github.com/Synaptechlabs/bladeBench/commits>
- **Sources the enricher read:**
  - <https://github.com/Synaptechlabs/bladeBench>
  - <https://github.com/Synaptechlabs/bladeBench/commits>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/README.md>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/performance_summary.md>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/Makefile>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/bench.sh>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/blade_core.c>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/blade_core.cpp>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/blade_core.rs>
  - <https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/blade_core.zig>
  - https://raw.githubusercontent.com/Synaptechlabs/bladeBench/HEAD/blade_core (committed binary, inspected with file and strings, not run)
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/std/src/sys/net/connection/socket/mod.rs>
  - <https://raw.githubusercontent.com/wg/wrk/master/src/wrk.c>
  - <https://raw.githubusercontent.com/wg/wrk/master/src/http_parser.c>
  - <https://raw.githubusercontent.com/wg/wrk/master/src/net.c>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:rust/synaptechlabs/bladebench#tcp-static-http-response`) · [data/wave14/enrich/raw/lang_rust_synaptechlabs_bladebench_tcp_static_http_response.json](../../../data/wave14/enrich/raw/lang_rust_synaptechlabs_bladebench_tcp_static_http_response.json) (enrichment confidence 0.75)

</details>
