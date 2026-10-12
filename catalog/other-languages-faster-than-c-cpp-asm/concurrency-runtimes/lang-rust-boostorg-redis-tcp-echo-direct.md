# Tokio TCP echo server (Boost.Redis echo benchmark, vs libuv)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT` · 🟢 active

> Tokio's docs-example TCP echo server on the single-threaded runtime; one 2022 run took 30.7 s against 43.6 s for the libuv docs example.

| | |
|---|---|
| **Beats** | libuv TCP echo server (C, epoll event loop, libuv docs tcp-echo-server example); the table also holds a Boost.Asio C++20 coroutine echo server that is slightly faster than Tokio |
| **Claimed result** | Tokio 30.7 s vs libuv 43.6 s wall time for 1000 connections x 5000 echoes (about 1.42x less wall time, derived from page data); Boost.Asio (C++) 29.5 s is about 4% faster than Tokio (derived from page data). Each value is a single run; the Tokio value was recorded on 2022-07-16 after switching to a newer Tokio and the current_thread runtime (it was 42.2-43.2 s before), the libuv value by 2022-07-15. Go 35.6 s and Node.js 74.2 s are in the same table. |
| **Workload** | TCP echo server serving 1000 concurrent client connections on localhost (the Boost.Redis echo_server_client driver, benchmarks.tex comment 'time ./echo_server_client 1000 5000'); metric is the total wall-clock seconds the client run took against each server, one server per language/library, each written from that library's own docs example. |
| **Metric** | throughput |
| **Compiler and flags** | Tokio server: #[tokio::main(flavor = "current_thread")], tokio = { version = "1.0", features = ["full"] } (benchmarks/rust/echo_server_direct/Cargo.toml has no [profile] section); cargo build profile and rustc version not stated. libuv server: 'gcc echo_server_direct.c -luv -O2 -o echo_server_direct' (benchmarks/c/libuv/README.md), linked against an unstated system libuv build. Asio server/client: CMake target with C++20 (benchmarks/CMakeLists.txt), compiler and optimisation level not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 33.4k stars (tokio); suite repo boostorg/redis has 282 stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/tokio-rs/tokio) · [benchmark](https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/benchmarks.tex) |

## Verdict

One `time` run each of a single-threaded Boost.Asio client (1000 localhost connections x 5000 13-byte echoes) on the author's unnamed machine (localhost latency 0.07 ms) took 30.7 s against the Tokio 1.20.0 current_thread server and 43.6 s against the libuv docs example built with gcc -O2, about 1.42x less wall time (derived from page data). The Boost.Asio C++20 coroutine server took 29.5 s in a later run, Go 35.6 s and Node.js 74.2 s; no CPU, OS, rustc or libuv versions are given.

## Use it when

- New network services in Rust with many concurrent, mostly idle connections exchanging small messages, where one task per connection is the simplest correct design.
- Single-core or one-runtime-per-core deployments: the current_thread flavour is what produced the 30.7 s result; the default multi-thread runtime (tokio 0.2.25) took 42.2-43.2 s in the same harness.
- When the C alternative under consideration is a straightforward libuv callback server written from the docs, without buffer pooling or request reuse.
- As a sidecar or separate process next to C++ code when the team prefers Rust's ownership checks for network-facing parsing.

## Skip it when

- When C++ is an option: the Boost.Asio C++20 coroutine echo server in the same chart took 29.5 s (October 2022) against Tokio's 30.7 s, and the July 2022 Asio run was 31.1 s, so the two are within noise of one single-run chart.
- As proof that Rust or Tokio beats libuv: the libuv server allocates per message, was built with gcc -O2 against an unstated libuv, and was never revised, while the Tokio server was moved to a newer Tokio and the single-threaded runtime before its winning run.
- Inside an existing C or C++ event loop: Tokio needs its own runtime thread and an FFI boundary; nothing in the benchmark covers that.
- Handlers that block or burn CPU: on the current-thread scheduler every task shares one thread, so one blocking call stalls every connection, and in this harness the multi-thread runtime was slower, so moving off current_thread has a cost.
- Latency-SLO work: only total wall time for 5,000,000 round trips exists, with no percentiles.

## How it is fast

Each connection is an async fn compiled to a stackless state machine whose 1 KiB buffer lives inside the task, so an echo costs one read and one write syscall and no heap allocation. Sockets are registered once with mio, which uses edge-triggered epoll (EPOLLET), and a read that hits WouldBlock parks the task until the reactor wakes it. The current-thread scheduler runs every task on one thread, so there is no work-stealing or cross-thread wake-up; it polls the I/O driver every 61 scheduled tasks (event_interval default in runtime/builder.rs). The libuv baseline makes the same syscalls but, as the unmodified docs example, mallocs a 64 KiB read buffer on each read callback (libuv passes 64 \* 1024 as suggested_size) plus a write request per echo and frees both; how much of the 13 s gap that explains was never measured.

## Compared with alternatives

Against the Go net echo server from the same harness (35.6 s), Tokio took about 14% less wall time and gives explicit control of the runtime flavour, so pick it when you want Rust's ownership model and are fine with async code. The Tokio 1M-task peak-memory entry (214 MB against 606 MB for concurrencpp and 853 MB for Asio) is the stronger reason to choose Tokio over a C++ coroutine runtime; this echo result alone is directional.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | tokio (the benchmark enables features = ["full"]); tokio itself depends on mio for the OS event queue |
| **Minimum toolchain** | Rust 1.85 for current Tokio (README MSRV); the benchmark's Cargo.lock pins tokio 1.20.0 (edition 2021); the rustc version and cargo profile used for the run are not stated |
| **Platforms** | Linux (epoll), macOS and BSD (kqueue), Windows (IOCP) per the Tokio README; measured only on the author's unnamed localhost machine |
| **Thread safety** | current_thread runtime: all tasks are created and executed on the calling thread (runtime/mod.rs); the default multi-thread runtime is a work-stealing scheduler (README) |
| **Drop-in for the baseline** | no |

## Gotchas

- The doc page's 'code used' link for Tokio points to commit 3fb018c, whose server is tokio 0.2.25 with the default multi-thread #[tokio::main] and scored 42.2 s (comment) and 43.2 s (chart), not the ab68e8a tokio 1.20.0 current_thread server behind the 30.7 s bar (2022-07-16, 'Updates to a more recent Tokio version and uses single thread.'). The version bump and the runtime switch happened together, so their effects cannot be separated.
- The chart is a composite of single `time ./echo_server_client 1000 5000` runs from different dates: libuv 43.568 s by 2022-07-15, Tokio 2022-07-16, Go 2022-08-25, and Asio re-run at 29.5 s on 2022-10-07 after its server switched from io_context(1) to a typed executor with BOOST_ASIO_CONCURRENCY_HINT_UNSAFE_IO. On 2022-07-16 Tokio (30.7 s) was ahead of Asio (31.1 s); it was never re-run after Asio's tuning.
- The single-threaded Asio client catches each session's exception, prints 'Error:' to stderr and carries on; it never checks that all 5,000,000 echoes completed or that the echoed bytes match, so a run with failed sessions would look faster. No logs of the runs are in the repository.
- No hardware, OS, rustc version or cargo profile is given (the Cargo.toml has no [profile] section and no build command is documented), and the libuv build is gcc -O2 against a system libuv of unknown version; Tokio and Asio at about 30 s may both be capped by the single-threaded client on the same host (inferred, not measured).

## Known shortcomings

- The C++ matmul kernel indexes B[k][i] (a wrong product hidden by all-ones inputs), so the matmul win is invalid, and the "every thread count" claim is false at 8 threads; the C++ sort source is not committed (binary only, GCC 4.8.5, int against Rust u64) and the Rust sort numbers come from uncommitted older code; the only surviving win is the stable parallel sort at 100M on 12-16 threads, about 1.11-1.20x (derived from data/Data.xlsx); no licence (reference).
- The doc page's 'code used' link for Tokio points to commit 3fb018c, a tokio 0.2.25 multi-thread server that scored 42.2 / 43.2 s, not the ab68e8a tokio 1.20.0 current_thread server behind the 30.7 s bar; the version bump and the runtime switch happened in one commit, so their effects cannot be separated. The chart is a composite of runs on different days: the same-day Tokio 30.7 s beat Asio 31.1 s, Asio was later tuned (UNSAFE_IO hint, typed executor) to 29.5 s and Tokio was never re-run. The client never checks that all echoes completed, and no cargo profile, rustc version or hardware is stated.

## Caveats and trade-offs

Numbers are the pgfplots source (benchmarks.tex) of the chart on the Boost.Redis doc page 'Echo server benchmark' (doc/modules/ROOT/pages/benchmarks.adoc); the rendered PNG on boostorg.github.io was not viewed. The chart is a composite of single `time` runs recorded on different dates by the Boost.Redis (C++) author on 'my machine' (localhost latency 0.07 ms; no CPU model, OS, Go/Rust/compiler versions, no repetitions or variance): libuv 43.568 s was recorded by 2022-07-15 (commit 3fb018c) and never re-run; Tokio moved from 42.2 s/43.2 s to 30.7 s on 2022-07-16 after switching to a newer Tokio and the current_thread runtime; Go moved from 81.0 s to 35.6 s on 2022-08-25 (commit f11622e) after its server was rewritten from bufio ReadBytes line echo to a raw 1024-byte read loop with GOMAXPROCS(1); Asio was re-measured at 29.5 s on 2022-10-07. Unequal work: the libuv server is the unmodified libuv docs tcp-echo-server example, which mallocs a 64 KiB read buffer (libuv passes 64\*1024 as suggested_size, src/unix/stream.c) on every read callback and a write_req_t per echo and frees both after each write, while the Go, Tokio and Asio servers reuse one 1 KiB buffer per connection; the Go server was revised between runs, the libuv one never was. The libuv server is built per benchmarks/c/libuv/README.md with 'gcc echo_server_direct.c -luv -O2' (not -O3; system libuv build flags unknown). The load generator is the single-threaded Boost.Asio echo_server_client (1000 sessions x 5000 13-byte ping-pong messages) on the same host, which may set a floor near the Asio/Tokio results. All servers are single-threaded (Asio io_context with BOOST_ASIO_CONCURRENCY_HINT_UNSAFE_IO, Tokio current_thread, Go GOMAXPROCS(1), one libuv loop). The C++ Boost.Asio coroutine server in the same table is the fastest entry (29.5 s), so this is not a win over the best C++ result. The author gives no explanation for the gap beyond 'I expected Libuv to have similar performance to Asio and Tokio'. Measured in 2022 on a Tokio 1.x release of that time; the Tokio server binds 127.0.0.1 while the others bind 0.0.0.0 (no timing effect expected). [retier] Enricher correction: the doc page's 'code used' link for Tokio points to commit 3fb018c, a tokio 0.2.25 multi-thread server that scored 42.2 / 43.2 s, not the ab68e8a tokio 1.20.0 current_thread server behind the 30.7 s bar (2022-07-16); the version bump and the runtime switch happened in one commit. The chart is a composite of single runs on different days: the same-day Tokio 30.7 s beat Asio 31.1 s, Asio was later tuned (UNSAFE_IO hint, typed executor) to 29.5 s and Tokio was never re-run. The client never checks that all echoes completed; no cargo profile, rustc version or hardware is stated.

Rust async needs the Tokio runtime and a Rust toolchain; the benchmark deliberately uses the single-threaded Tokio runtime to match the single-threaded libuv loop. Calling it from C++ needs FFI or a separate process.

## Maintenance

Tokio is actively maintained (MIT, 33.4k stars, README install snippet shows 1.53.2) and the server is a copyable docs example, but the evidence is a 2022 single-run composite chart that the current doc page still shows and links to the older Tokio code, against an allocation-heavy C example, so it supports only a tier-D directional claim.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** Numbers are real (benchmarks.tex: Tokio 30.7 s, Libuv 43.6 s, Asio 29.5 s) and server code is public (benchmarks/rust/echo_server_direct/src/main.rs, benchmarks/c/libuv/echo_server_direct.c, benchmarks/cpp/asio/echo_server_client.cpp), but there is no CPU model, rustc version or cargo profile, each bar is one run from a different date (Tokio 2022-07-16 after a runtime switch, libuv by 2022-07-15), and the libuv side mallocs a 64 KiB read buffer and a write request per message at -O2 while Tokio reuses one 1 KiB buffer: crippled-baseline and cross-run precedents put the Tokio-over-libuv claim at D.
- **Verifier notes:** Downgrade C to D: Tokio only beats the unmodified libuv docs example (per-message 64 KiB malloc plus write-request malloc, -O2), recorded in a different single run, and loses to the C++ Asio server (29.5 s) in the same table. Shortcomings for decisions.json: composite single-run chart across July-October 2022, no hardware, versions or cargo profile, unequal buffer management, -O2 C build, single-threaded client may cap results.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-31 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/doc/modules/ROOT/pages/benchmarks.adoc>
  - <https://github.com/boostorg/redis/tree/develop/benchmarks>
  - <https://github.com/boostorg/redis/tree/develop/benchmarks/rust>
  - <https://github.com/boostorg/redis/tree/develop/benchmarks/c/libuv>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/c/libuv/README.md>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/c/libuv/echo_server_direct.c>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/rust/echo_server_direct/src/main.rs>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/rust/echo_server_direct/Cargo.toml>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/cpp/asio/echo_server_direct.cpp>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/cpp/asio/echo_server_client.cpp>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/CMakeLists.txt>
  - <https://github.com/boostorg/redis/commits/develop/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/boostorg/redis/3fb018ccc6138d310ac8b73540391cdd8f2fdad6/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/boostorg/redis/59b5d35672eb39aacbf6405946eb37600c0c60f6/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/boostorg/redis/ab68e8a31dd5f10a2b6ecfd6aec44bab71233aae/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/boostorg/redis/ba82c6cd8487eca9b3142f34c8ad7b2ff16548b1/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/libuv/libuv/v1.x/src/unix/stream.c>
  - <https://github.com/boostorg/redis>
  - <https://github.com/tokio-rs/tokio>
  - <https://github.com/tokio-rs/tokio/commits/master>
- **Sources the enricher read:**
  - <https://github.com/tokio-rs/tokio>
  - <https://raw.githubusercontent.com/tokio-rs/tokio/master/tokio/src/runtime/builder.rs>
  - <https://raw.githubusercontent.com/tokio-rs/tokio/master/tokio/src/runtime/mod.rs>
  - <https://raw.githubusercontent.com/tokio-rs/tokio/master/tokio/src/net/tcp/stream.rs>
  - <https://raw.githubusercontent.com/tokio-rs/mio/master/src/sys/unix/selector/epoll.rs>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/doc/modules/ROOT/pages/benchmarks.adoc>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/rust/echo_server_direct/src/main.rs>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/rust/echo_server_direct/Cargo.toml>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/rust/echo_server_direct/Cargo.lock>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/c/libuv/echo_server_direct.c>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/c/libuv/README.md>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/cpp/asio/echo_server_direct.cpp>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/cpp/asio/echo_server_client.cpp>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/boostorg/redis/develop/benchmarks/go/echo_server_direct.go>
  - <https://raw.githubusercontent.com/boostorg/redis/3fb018ccc6138d310ac8b73540391cdd8f2fdad6/benchmarks/rust/echo_server_direct/src/main.rs>
  - <https://raw.githubusercontent.com/boostorg/redis/3fb018ccc6138d310ac8b73540391cdd8f2fdad6/benchmarks/rust/echo_server_direct/Cargo.toml>
  - <https://raw.githubusercontent.com/boostorg/redis/3fb018ccc6138d310ac8b73540391cdd8f2fdad6/benchmarks/rust/echo_server_direct/Cargo.lock>
  - <https://raw.githubusercontent.com/boostorg/redis/3fb018ccc6138d310ac8b73540391cdd8f2fdad6/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/boostorg/redis/ab68e8a31dd5f10a2b6ecfd6aec44bab71233aae/benchmarks/rust/echo_server_direct/Cargo.lock>
  - <https://raw.githubusercontent.com/boostorg/redis/ab68e8a31dd5f10a2b6ecfd6aec44bab71233aae/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/boostorg/redis/ab68e8a31dd5f10a2b6ecfd6aec44bab71233aae/benchmarks/cpp/asio/echo_server_direct.cpp>
  - <https://raw.githubusercontent.com/boostorg/redis/ba82c6cd8487eca9b3142f34c8ad7b2ff16548b1/benchmarks/cpp/asio/echo_server_direct.cpp>
  - <https://raw.githubusercontent.com/boostorg/redis/ba82c6cd8487eca9b3142f34c8ad7b2ff16548b1/benchmarks/benchmarks.tex>
  - <https://github.com/boostorg/redis/commits/develop/benchmarks/rust>
  - <https://github.com/boostorg/redis/commits/develop/benchmarks/benchmarks.tex>
  - <https://raw.githubusercontent.com/libuv/libuv/v1.x/src/unix/stream.c>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:rust/boostorg/redis#tcp-echo-direct`) · [data/wave14/enrich/raw/lang_rust_boostorg_redis_tcp_echo_direct.json](../../../data/wave14/enrich/raw/lang_rust_boostorg_redis_tcp_echo_direct.json) (enrichment confidence 0.6)

</details>
