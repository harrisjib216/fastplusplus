# may

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust stackful-coroutine runtime with Go-style go! and blocking-style I/O; its may_minihttp demo beat pre-1.0 tokio_minihttp by \~15% req/s.

| | |
|---|---|
| **Beats** | Tokio, pre-1.0 (tokio-core 0.1 / tokio-proto 0.1 era, via tokio_minihttp) |
| **Claimed result** | \~15% higher requests/sec than tokio_minihttp (116,181.73 req/s vs 100,650.94 req/s; \~1.15x derived from page data) |
| **Workload** | Single-thread hello-world HTTP server, wrk -d10 -t1 -c200, may_minihttp (stackful coroutines on may) vs tokio_minihttp |
| **Metric** | throughput |
| **Hardware** | author's laptop, model unspecified |
| **Compiler and flags** | cargo run --example=hello-world --release; rustc version and flags not stated |
| **Adoption** | 2.4k stars; may_minihttp cited as "one of the fastest web frameworks" on the TechEmpower Framework Benchmark |
| **Last commit** | 2026-08-03 |
| **Links** | [repository](https://github.com/Xudong-Huang/may) · [benchmark](https://github.com/Xudong-Huang/may_minihttp) |

## Verdict

The author ran wrk (1 client thread, 200 connections, 10 s) against the hello-world servers of may_minihttp and tokio_minihttp with one server worker thread on an unspecified laptop: 116,182 vs 100,651 req/s (\~1.15x), with lower average latency (1.70 ms vs 1.98 ms) but higher max latency (20.17 ms vs 12.53 ms); the Tokio side is tokio-core/tokio-proto 0.1 on futures 0.1, and neither rustc version nor CPU is stated. Independent TechEmpower data is framework-vs-framework, not a clean Tokio comparison: in R22 may-minihttp beat hyper and axum but only matched Tokio-based actix-server and ntex-plt on plaintext, while in R23 it led hyper, axum, ntex-plt and xitca-web on plaintext, JSON and fortunes (derived from raw data).

## Use it when

- You want Go-style thread-per-connection code in Rust (blocking reads/writes, mutexes, channels) at event-loop cost, without async/await function colouring.
- HTTP/1.1 plaintext, JSON or Postgres-backed microservices where you control the whole stack: in TechEmpower Round 23 (Citrine, derived from raw data) may-minihttp ranked 1st of 518 on fortunes (1.33M rps), 2nd of 540 on JSON (3.10M vs hyper 2.89M, axum 2.71M) and 10th of 533 on network-bound plaintext (27.9M vs hyper 17.5M, axum 12.4M).
- Porting an existing threaded, blocking Rust server where an async rewrite is too costly: swap std::net/std::sync for may::net/may::sync and wrap per-connection work in go!.
- Many I/O-bound connections whose handlers need well under the 32 KiB default stack, on x86-64 or AArch64 Linux, macOS or Windows.

## Skip it when

- You depend on the Tokio ecosystem (hyper, axum, tonic, reqwest, sqlx): none of it runs on may's scheduler, and calling any thread-blocking API (std Mutex/Condvar, std::thread::sleep, blocking socket libraries) from a coroutine stalls the whole worker thread.
- Millions of mostly idle tasks: every coroutine reserves a fixed stack that never grows (the author says 1M coroutines need at least 4 GB), while Tokio futures are stackless.
- You need safe Rust to stay sound: touching thread-local storage across a yield is undefined behavior (libstd and C/C++ libraries use TLS), and open issue #109 argues go! hides the unsafe that spawn requires; the maintainer calls this intentional.
- Deep recursion, large stack frames or heavy FFI engines: stack overflow hits the guard page and kills the process, and a user in #109 reports V8 and JavaScriptCore code silently not running or segfaulting inside coroutines.
- Tail-latency-critical or thread-per-core designs: scheduling is cooperative (long CPU loops must call coroutine::yield_now()), there is no non-work-stealing mode and the author has no plan to add one (#90), and open issue #27 records much higher latency than Tokio in an early hyper port.

## How it is fast

Each coroutine runs on its own mmap'd stack (default 4K words = 32 KiB on 64-bit, with a PROT_NONE guard page) and switches through a hand-written assembly register swap from the generator crate, so a read that would block parks only the coroutine until epoll (Linux), kqueue (macOS/BSD) or IOCP (Windows) reports the socket ready, and the worker switches to the next ready coroutine. N worker threads (default num_cpus, pinned to cores by default) each run their own event loop with a local work-stealing queue, and finished coroutines are recycled through a pool (default capacity 1000). may_minihttp adds request batching: it reads all available bytes into a 32 KiB buffer, decodes every pipelined request with httparse, encodes all responses into one buffer and, on Unix, issues a single non-blocking write before waiting on the socket again.

## Compared with alternatives

Pick may over monoio when you want multi-threaded work stealing and blocking-style std-like code on Linux, macOS and Windows rather than thread-per-core io_uring with async/await (monoio's own echo benchmark shows a larger 1.86x edge over Tokio, but may_minihttp has the stronger independent TechEmpower record). Pick it over futures-based Tokio challengers such as exec-rs or Rain when you would rather avoid async entirely; for C++, PhotonLibOS is the closest stackful-coroutine analogue.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | generator (stackful context switch), may_queue, crossbeam, parking_lot, socket2, core_affinity, smallvec, num_cpus, log, cfg-if; nix + libc on Unix; windows-sys on Windows. may_minihttp adds bytes, httparse, httpdate, itoa, once_cell. |
| **Minimum toolchain** | Rust 2021 edition; may declares no rust-version, but its generator 0.8 dependency declares rust-version 1.73. README says stable, beta and nightly all work. |
| **Platforms** | x86_64 Linux/Windows/macOS and AArch64 Linux/macOS per the README (the generator crate also covers armv7, riscv64, loongarch64, ppc64le, s390x Linux, but may does not list them). I/O backends: epoll (Linux/Android), kqueue (macOS/BSD), IOCP (Windows). |
| **Thread safety** | README: all coroutine APIs are safe to call from multiple threads. Coroutines migrate between worker threads via work stealing, so thread-local storage is not stable across yields; use coroutine_local! instead. Use may::sync primitives, not std::sync blocking ones, inside coroutines. |
| **Drop-in for the baseline** | no |

## Gotchas

- go! wraps the unsafe coroutine::spawn in a hidden unsafe block, so safe-looking code can reach UB through TLS or FFI; call the unsafe spawn/Builder API directly if you want the unsafety visible.
- Stack size is set in words, not bytes (set_stack_size(0x400) = 8 KiB on 64-bit). An odd stack size makes may pre-fill the stack and print the real usage when the coroutine exits; use it to tune. Functions with big stack frames such as std::io::copy are called out as risks.
- may::config() (workers, stack size, pool capacity, worker pinning, poll timeout) takes effect only before the scheduler starts; workers are pinned to CPU cores by default (set_worker_pin(false) to turn it off).
- An I/O-ready coroutine keeps reading until the socket returns WouldBlock before it yields, which the author links to latency jitter under load (#27).

## Known shortcomings

- The only first-party number (\~1.15x, 116,182 vs 100,651 req/s) is against tokio_minihttp on tokio-core/futures 0.1, one worker on an unnamed laptop, no rustc version; the current example no longer sets one worker (default is num_cpus pinned workers). performace.md's Tokio 0.2 echo test is disowned by the author as old and unfair (#90); the request for a modern Tokio comparison (#72) has been open since 2019. TLS across a yield is UB (spawn is unsafe) and go! hides that unsafe block by design (#109); V8/JavaScriptCore code reportedly fails inside coroutines. Fixed 32 KiB stacks that don't grow (1M coroutines need 4+ GB); cooperative scheduling; no mode without work stealing (#90). Last crates.io releases lag master (may 0.3.51, 2025-05; may_minihttp 0.1.11, 2024-09).

## Caveats and trade-offs

First-party wrk benchmark on an unspecified laptop, single worker thread only, rustc version not stated. The baseline tokio_minihttp is built on tokio-core 0.1, tokio-proto 0.1 and futures 0.1, so the comparison is against pre-1.0 Tokio, not modern Tokio. In the independent TechEmpower R22 data (Citrine), may-minihttp beats Tokio-based hyper and axum, but Tokio-based actix-server and ntex-plt match or beat it on plaintext. may and may_minihttp are dual-licensed MIT OR Apache-2.0 (Cargo.toml 'MIT/Apache-2.0', both LICENSE files present).

Stackful coroutines (via generator crate) instead of Rust's native async/await; blocking-style API; must avoid calling thread-blocking syscalls directly and be careful with thread-local storage across coroutine yields.

## Maintenance

Maintained (commits through 2026-08-03; latest crates.io releases may 0.3.51 on 2025-05-13 and may_minihttp 0.1.11 on 2024-09-22) and dual MIT/Apache-2.0 on crates.io; RustSec lists no advisory for may itself and old ones for its may_queue and generator dependencies are patched, but the documented TLS hazard (#6) and the open go! soundness issue (#109) make it better suited to controlled services than to general-purpose libraries.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The may_minihttp README Performance section shows the author's own wrk runs (-d 10 -t 1 -c 200, one worker thread, 'my laptop'): tokio_minihttp 100650.94 req/s vs may_minihttp 116181.73 req/s. The example code is public, but there is no CPU model, no rustc version and no flags beyond --release, so this is C.
- **Verifier notes:** The numbers match the page exactly. Tier C stays: TechEmpower R22 rawData gives approximately (derived) may-minihttp 6.91M plaintext rps vs hyper 5.49M, axum 3.75M, actix-server 6.97M and ntex-plt 7.00M, and 1.205M json rps vs hyper 1.099M and actix-server 1.194M. That is framework against framework and not a clean win over Tokio, so I did not upgrade to B. The GitHub spdx is Apache-2.0, but the crate is dual-licensed, so I corrected the license.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `license`, `caveats`
- **Shortcomings recorded by:** TechEmpower Round 23 (framework vs framework, not a clean Tokio comparison; ranks derived from round23/ph.json raw data): may-minihttp ranked 1st of 518 on fortunes (1.33M rps), 2nd of 540 on JSON (3.10M vs hyper 2.89M) and 10th of 533 on plaintext (27.9M vs hyper 17.5M, ntex-plt 24.9M; plaintext looks network-bound). In Round 22 actix-server and ntex-plt matched it on plaintext.
- **Pages the verifier opened:**
  - <https://github.com/Xudong-Huang/may>
  - <https://github.com/Xudong-Huang/may_minihttp>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/Cargo.toml>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/Cargo.toml>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/examples/hello-world.rs>
  - <https://raw.githubusercontent.com/tokio-rs/tokio-minihttp/master/Cargo.toml>
  - <https://www.techempower.com/benchmarks/results/round22/ph.json>
- **Sources the enricher read:**
  - <https://github.com/Xudong-Huang/may>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/README.md>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/Cargo.toml>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/src/lib.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/src/config.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/src/scheduler.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/src/io/mod.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/src/io/event_loop.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/src/io/sys/unix/mod.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/src/io/sys/windows/mod.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/build.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/docs/may_caveat.md>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/docs/tune_stack_size.md>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/docs/CLS_instead_of_TLS.md>
  - <https://raw.githubusercontent.com/Xudong-Huang/may/master/performace.md>
  - <https://github.com/Xudong-Huang/may/commits/master.atom>
  - <https://github.com/Xudong-Huang/may/issues/6>
  - <https://github.com/Xudong-Huang/may/issues/27>
  - <https://github.com/Xudong-Huang/may/issues/29>
  - <https://github.com/Xudong-Huang/may/issues/72>
  - <https://github.com/Xudong-Huang/may/issues/90>
  - <https://github.com/Xudong-Huang/may/issues/109>
  - <https://github.com/Xudong-Huang/may/issues/114>
  - <https://github.com/Xudong-Huang/may_minihttp>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/README.md>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/Cargo.toml>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/examples/hello-world.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/src/lib.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/may_minihttp/master/src/http_server.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/generator-rs/master/README.md>
  - <https://raw.githubusercontent.com/Xudong-Huang/generator-rs/master/Cargo.toml>
  - <https://raw.githubusercontent.com/Xudong-Huang/generator-rs/master/src/detail/mod.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/generator-rs/master/src/detail/x86_64_unix.rs>
  - <https://raw.githubusercontent.com/Xudong-Huang/generator-rs/master/src/stack/unix.rs>
  - <https://www.techempower.com/benchmarks/results/round23/ph.json>
  - <https://crates.io/api/v1/crates/may>
  - <https://crates.io/api/v1/crates/may_minihttp>
  - <https://rustsec.org/packages/may.html>
  - <https://rustsec.org/packages/may_queue.html>
  - <https://rustsec.org/packages/generator.html>
  - <https://rustsec.org/advisories/RUSTSEC-2020-0111.html>
  - <https://rustsec.org/advisories/RUSTSEC-2019-0020.html>
  - <https://rustsec.org/advisories/RUSTSEC-2020-0151.html>
  - <https://hn.algolia.com/api/v1/search?query=Xudong-Huang%2Fmay&restrictSearchableAttributes=url>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/xudong-huang/may`) · [data/wave5/enrich/raw/github_com_xudong_huang_may.json](../../../data/wave5/enrich/raw/github_com_xudong_huang_may.json) (enrichment confidence 0.8)

</details>
