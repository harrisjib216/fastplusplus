# monoio

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Thread-per-core Rust async runtime on io_uring (epoll/kqueue fallback); \~1.9x Tokio's peak echo QPS on 4 cores.

| | |
|---|---|
| **Beats** | epoll (via Tokio's mio-based reactor) |
| **Claimed result** | 4-core server, 1KB messages, peak QPS: Monoio 810,075 vs Tokio (epoll) 434,565 (\~1.86x, derived from page data) and vs Glommio (io_uring) 603,016 (\~1.34x, derived from page data). At 16 cores with 100B messages, Monoio peaks at 2,802,033 vs Tokio 917,419 (\~3.05x, derived from page data). |
| **Workload** | Extreme-performance TCP test on ByteDance production network: fixed number of client connections against 4 server cores / 16 client cores, 1KB messages, comparing io_uring (Monoio), io_uring (Glommio) and epoll (Tokio) runtimes |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 5118 @ 2.30GHz, Intel X710 10GbE SFP+ NIC, Linux 5.15.4-arch1-1; client and server on separate physical machines on the ByteDance production network |
| **Compiler and flags** | rust nightly-2021-11-26; cargo release build (target/release) with [profile.release] lto = true, debug = false, overflow-checks = false (monoio-rs/monoio-benchmark Cargo.toml) |
| **Adoption** | 5.1k stars |
| **Last commit** | 2026-05-29 |
| **Links** | [repository](https://github.com/monoio-rs/monoio) · [benchmark](https://github.com/monoio-rs/monoio/blob/master/.github/resources/benchmark/raw_data.txt) |

## Verdict

This is the maintainers' 2021 ping-pong echo benchmark: rust nightly-2021-11-26 release build with LTO, Linux 5.15.4, a Xeon Gold 5118 server with an X710 10GbE NIC, and the client on a separate machine. With 1 KiB messages on 4 server cores, Monoio peaked at 810,075 QPS against 434,565 for Tokio's multi-thread epoll runtime (1.86x) and 603,016 for Glommio. With 100 B messages on 16 cores it reached 2,802,033 against 917,419. Tokio ran as one unpinned work-stealing runtime with a single accept loop, while Monoio ran one pinned io_uring runtime per core with its own SO_REUSEPORT listener, so the numbers compare runtime architecture plus io_uring rather than io_uring against raw epoll; at 1 core the lead is \~1.15x.

## Use it when

- Linux 5.6+ servers with many concurrent connections per core, such as L4/L7 proxies, gateways and RPC front ends, where peak QPS or CPU per request matters. In the maintainers' echo test the lead over Tokio grows with core count: \~1.15x at 1 core, \~1.9x at 4 and \~3x at 16.
- Work that shards evenly across cores (NGINX-style), where per-connection state never needs to leave its thread and you want Rc/RefCell instead of Arc/Mutex.
- Fixed-load services where CPU headroom matters. At 384k QPS on 4 cores with 250 connections per core, Monoio used \~232% CPU against Tokio's \~390%.
- Teams that develop on macOS or older kernels and deploy on io_uring Linux. The default FusionDriver probes io_uring opcode support at startup and otherwise falls back to epoll/kqueue with the same code (MONOIO_FORCE_LEGACY_DRIVER=1 forces the fallback).

## Skip it when

- Unbalanced or bursty per-connection load. There is no work stealing, and the README warns this can make it slower than Tokio because cores sit idle.
- Low concurrency on a single core. In the project's own data Tokio had higher QPS up to 480 connections on 1 core (for example 166,938 vs 160,157 at 400 connections) and lower latency at 80 connections per core under fixed load, because io_uring submission latency is higher than epoll's.
- Code built mainly on the Tokio ecosystem (tokio::spawn, tokio::sync, reqwest, tonic). Those crates need the poll-io feature (epoll readiness layered over io_uring) or monoio-compat (an extra buffer copy), and both give up most of the io_uring gain on those paths.
- Windows, musl or Android targets. Windows is experimental (open issues #274, #403), 0.2.4 fails to compile for musl (#349), and there is an open Android build failure (#324).
- Mixed CPU-heavy or blocking work. spawn_blocking needs the `sync` feature and by default runs on the calling thread (BlockingStrategy::ExecuteLocal), which stalls that core's I/O loop.

## How it is fast

It uses completion-based I/O through io_uring. Reads and writes are pushed as SQEs and only submitted when the thread runs out of ready tasks, in one io_uring_enter call (submit_and_wait). Tokio's reactor instead does an epoll_wait and then one read/write syscall per ready socket. The thread-per-core scheduler keeps its state in thread-local Rc/UnsafeCell plus a local VecDeque task queue with no work stealing, so the hot path has no atomics or cross-thread locks. TcpListener sets SO_REUSEPORT by default, so each core accepts its own connections. Because the I/O API takes buffer ownership, the kernel can write straight into user buffers; the project's comparison doc says Glommio copies data at this point for compatibility.

## Compared with alternatives

Pick Monoio for a general-purpose Rust network server that wants io_uring throughput from a full runtime (sockets, files, timers, and hyper/h2 via poll-io); PhotonLibOS is the nearest C++ equivalent. aquatic's own io_uring-vs-mio/epoll comparison shows only \~1.11x, so remember that Monoio's 2-3x multi-core lead over Tokio mixes io_uring with thread-per-core scheduling.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | io-uring 0.6 (Linux), mio 0.8 (legacy epoll/kqueue driver), libc, socket2, bytes, pin-project-lite, rustc-hash, memchr, auto-const-array; optional: tokio (poll-io / tokio-compat), flume + threadpool + once_cell (sync), nix (utils: CPU pinning), tracing (debug), ctrlc (signal) |
| **Minimum toolchain** | Rust 1.75 per the README; Cargo.toml sets no rust-version, and CI runs both stable and nightly. The opt-in `unstable` feature needs nightly. The io_uring driver needs Linux 5.6+; splice needs 5.7+, unlinkat/renameat 5.11+, mkdirat/symlinkat 5.15+. Wait-with-timeout uses ext_arg on 5.11+ and a TimeoutOp fallback otherwise. |
| **Platforms** | Linux (io_uring or epoll) and macOS (kqueue). CI builds x86_64, aarch64, armv7, riscv64, s390x and loongarch64 Linux plus x86_64/aarch64 macOS. Windows support is experimental. |
| **Thread safety** | Thread-per-core: the runtime, tasks and I/O objects stay on the thread that created them, and spawn does not require Send. Cross-thread wakers and channels need the `sync` feature, which adds an eventfd and a waker channel. To scale, start one runtime per thread, either with the worker_threads macro option or with your own threads plus utils::bind_to_cpu_set. |
| **Drop-in for the baseline** | partial — it replaces Tokio as the runtime but has its own I/O API (buffer-ownership AsyncReadRent/AsyncWriteRent, monoio::spawn without a Send bound). Tokio's AsyncRead/AsyncWrite are available three ways: through `poll-io` (TcpStreamPoll, epoll over io_uring), through monoio-compat (extra copy, and you must call flush/shutdown explicitly), or with the legacy-only driver via `tokio-compat` at no overhead. |

## Gotchas

- io_uring needs locked memory. With the common 64 KiB memlock default, reads and writes can fail with os error 105 'No buffer space available'. Raise memlock to at least 512 or unlimited. Ring entries default to 1024 (minimum 256); the in-flight op slab starts at 10x entries.
- Dropping an in-flight I/O future does not reliably cancel it. The async-cancel feature queues a CancelOp, but the read may still complete and its data is then lost, for example in select!{read, timeout}. Keep the future alive, or use cancelable_read with a Canceller and check for ECANCELED (125).
- A panic inside a spawned task kills the runtime thread; unlike Tokio it is not caught (issue #314). Timer APIs panic unless enable_timer() or timer_enabled = true is set.
- TcpListener::bind turns on SO_REUSEPORT and SO_REUSEADDR by default, so a second process can quietly share the port; use bind_with_config to disable this. The `zero-copy` feature (MSG_ZEROCOPY) is documented as unstable and possibly slower.

## Known shortcomings

- Thread-per-core io_uring runtime: tasks are not Send and are not work-stolen, so it is not a drop-in for Tokio. Benchmark is from 2021 (rust nightly-2021-11-26). Repository moved from bytedance to monoio-rs.
- Confounded benchmark: Tokio ran one work-stealing runtime with a single accept loop and no pinning, while monoio ran one pinned io_uring runtime per core with SO_REUSEPORT, so the 1.9-3x measures thread-per-core scheduling plus io_uring; at 1 core the lead is only \~1.15x, and Tokio wins at low concurrency. Last crates.io release 0.2.4 (2024-08); fixes only on master; a panic in a spawned task kills the runtime thread (#314).

## Caveats and trade-offs

First-party benchmark by the Monoio maintainers, run in late 2021 on Linux 5.15. The benchmark code (monoio-rs/monoio-benchmark) and the raw numbers are public. The docs say that with 1 core and few connections, Tokio has lower latency and higher throughput than Monoio. The comparison is between runtimes (Tokio's mio/epoll reactor) and not raw epoll. The GitHub repo moved from bytedance/monoio to monoio-rs/monoio (the old URL redirects). The benchmark repo's workspace takes monoio from git and uses a nightly rust-toolchain, so a re-run today would not use the 2021 versions exactly.

Thread-per-core, non-Send/Sync design (values do not escape thread on await); at very low connection counts on a single core, Monoio's io_uring submission latency is higher than Tokio's epoll path, so Tokio wins that narrow case

## Maintenance

Active but slow to ship: the repo is now github.com/monoio-rs/monoio (moved from bytedance/monoio) with commits through 2026-05-29, but the last crates.io release is still 0.2.4 from August 2024 (\~1.58M downloads), so fixes made since then are only on git master, and open issue #398 asks whether the project is still maintained. It is MIT OR Apache-2.0 and usable as a crate today.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C to A. The raw_data.txt page lists the per-run Tokio, Glommio and Monoio QPS, with Tokio 4C(1K) at 434565, Glommio at 603016 and Monoio at 810075. The page and docs/en/benchmark.md give the CPU (Xeon Gold 5118), the kernel and the compiler (rust nightly-2021-11-26). The benchmark code is public in monoio-rs/monoio-benchmark (monoio-server/, tokio-server/, glommio-server/, client/), and its Cargo.toml [profile.release] sets lto = true and the README runs target/release binaries, so the flags are stated too.
- **Verifier notes:** All claimed numbers match raw_data.txt exactly. The license is dual MIT OR Apache-2.0: monoio/Cargo.toml says so and both LICENSE-MIT and LICENSE-APACHE exist, although the GitHub API reports only Apache-2.0. The repo moved to the monoio-rs org; consider updating repo_url to https://github.com/monoio-rs/monoio. Stars 5117, last commit 2026-05-29, not archived, not a fork.
- **Fields the verifier corrected:** `license`, `benchmark_url`, `compiler_and_flags`, `hardware`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/bytedance/monoio>
  - <https://github.com/bytedance/monoio/blob/master/.github/resources/benchmark/raw_data.txt>
  - <https://github.com/monoio-rs/monoio>
  - <https://github.com/monoio-rs/monoio/blob/master/.github/resources/benchmark/raw_data.txt>
  - <https://github.com/monoio-rs/monoio/blob/master/docs/en/benchmark.md>
  - <https://github.com/monoio-rs/monoio/blob/master/README.md>
  - <https://github.com/monoio-rs/monoio/blob/master/monoio/Cargo.toml>
  - <https://github.com/monoio-rs/monoio-benchmark>
  - <https://github.com/monoio-rs/monoio-benchmark/blob/master/README.md>
  - <https://github.com/monoio-rs/monoio-benchmark/blob/master/Cargo.toml>
  - <https://github.com/monoio-rs/monoio-benchmark/blob/master/rust-toolchain>
  - <https://github.com/monoio-rs/monoio-benchmark/blob/master/tokio-server/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/monoio-rs/monoio>
  - <https://github.com/monoio-rs/monoio/blob/master/README.md>
  - <https://github.com/monoio-rs/monoio/blob/master/Cargo.toml>
  - <https://github.com/monoio-rs/monoio/blob/master/monoio/Cargo.toml>
  - <https://github.com/monoio-rs/monoio/blob/master/.github/resources/benchmark/raw_data.txt>
  - <https://github.com/monoio-rs/monoio/blob/master/.github/workflows/ci.yml>
  - <https://github.com/monoio-rs/monoio/blob/master/docs/en/benchmark.md>
  - <https://github.com/monoio-rs/monoio/blob/master/docs/en/platform-support.md>
  - <https://github.com/monoio-rs/monoio/blob/master/docs/en/memlock.md>
  - <https://github.com/monoio-rs/monoio/blob/master/docs/en/comparing-with-others.md>
  - <https://github.com/monoio-rs/monoio/blob/master/docs/en/why-async-rent.md>
  - <https://github.com/monoio-rs/monoio/blob/master/docs/en/compatiable-with-tokio-eco.md>
  - <https://github.com/monoio-rs/monoio/blob/master/docs/en/use-legacy-driver.md>
  - <https://github.com/monoio-rs/monoio/blob/master/docs/en/poll-io.md>
  - <https://github.com/monoio-rs/monoio/blob/master/docs/en/io-cancel.md>
  - <https://github.com/monoio-rs/monoio/blob/master/docs/en/configuration.md>
  - <https://github.com/monoio-rs/monoio/blob/master/monoio/src/driver/uring/mod.rs>
  - <https://github.com/monoio-rs/monoio/blob/master/monoio/src/runtime.rs>
  - <https://github.com/monoio-rs/monoio/blob/master/monoio/src/scheduler.rs>
  - <https://github.com/monoio-rs/monoio/blob/master/monoio/src/builder.rs>
  - <https://github.com/monoio-rs/monoio/blob/master/monoio/src/lib.rs>
  - <https://github.com/monoio-rs/monoio/blob/master/monoio/src/utils/uring_detect.rs>
  - <https://github.com/monoio-rs/monoio/blob/master/monoio/src/net/listener_config.rs>
  - <https://github.com/monoio-rs/monoio/blob/master/monoio/src/net/tcp/listener.rs>
  - <https://github.com/monoio-rs/monoio/commits/master>
  - <https://github.com/monoio-rs/monoio/releases>
  - <https://github.com/monoio-rs/monoio/issues>
  - <https://github.com/monoio-rs/monoio/issues/398>
  - <https://github.com/monoio-rs/monoio/issues/378>
  - <https://github.com/monoio-rs/monoio/issues/349>
  - <https://github.com/monoio-rs/monoio/issues/241>
  - <https://github.com/monoio-rs/monoio/issues/314>
  - <https://github.com/monoio-rs/monoio/issues/400>
  - <https://crates.io/api/v1/crates/monoio>
  - <https://github.com/monoio-rs/monoio-benchmark>
  - <https://github.com/monoio-rs/monoio-benchmark/blob/master/tokio-server/src/main.rs>
  - <https://github.com/monoio-rs/monoio-benchmark/blob/master/monoio-server/src/main.rs>
  - <https://github.com/monoio-rs/monoio-benchmark/blob/master/config/src/lib.rs>
  - <https://github.com/rustsec/advisory-db/tree/main/crates/monoio>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/bytedance/monoio`) · [data/wave5/enrich/raw/github_com_bytedance_monoio.json](../../../data/wave5/enrich/raw/github_com_bytedance_monoio.json) (enrichment confidence 0.8)

</details>
