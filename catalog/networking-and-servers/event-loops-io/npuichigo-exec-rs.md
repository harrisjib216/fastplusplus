# exec-rs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [Event loops and async I/O](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `no license` · 🟢 active

> Rust port of C++ P2300 senders/receivers with a mio event loop; its single-threaded echo server beats Tokio 10-26% (self-reported).

| | |
|---|---|
| **Beats** | Tokio |
| **Claimed result** | 10-26% higher req/s than Tokio across concurrency levels (e.g. 135,157 req/s vs 107,333 req/s at 500 connections "heavy" load) |
| **Workload** | Single-threaded TCP echo server (exec_echo example on the P2300-style sender/receiver design vs the tokio_echo example): Light (50 connections), Medium (200), Heavy (500) and Large (4KB payload; connection count not stated) |
| **Metric** | throughput |
| **Adoption** | 26 stars |
| **Last commit** | 2026-01-31 |
| **Links** | [repository](https://github.com/npuichigo/exec-rs) · [benchmark](https://github.com/npuichigo/exec-rs#benchmark-results) |

## Verdict

The top-level README table compares a single-threaded exec_echo (mio loop) with Tokio's multi-thread runtime at worker_threads(1). Results were 114,723 vs 104,601 req/s (50 connections), 130,694 vs 114,478 (200), 135,157 vs 107,333 (500) and 100,321 vs 85,745 (4 KB), which is +10% to +26%. benchmark.sh shows the load came from haraldh/rust_echo_bench on 127.0.0.1: one blocking client thread per connection, 128 B messages, 10 s, with 'Large' being 100 connections of 4096 B. No CPU, OS, rustc version or run count is given. The script launches a nonexistent 'exec_echo_async' example, and the example directory's own README (Linux 5.15) reports only +4-7% single-threaded and parity at 4 threads.

## Use it when

- Studying or prototyping P2300/stdexec-style sender pipelines in Rust: then/let_value/when_all/bulk, stop tokens, and async scopes.
- Research on how the sender/receiver design compares with Future-based runtimes on allocations and scheduling overhead, since operation states are exposed and kept inline.
- A single-threaded, Unix-only TCP request/response loop with trivial per-connection work, where you will re-run the echo benchmark on your own hardware before trusting the gap.
- Reading material for porting C++ std::execution code (stdexec, uring_exec) to Rust or comparing the two.

## Skip it when

- Production services. There is no LICENSE file, CI or issue history, the repo has 30 commits and 0 forks, and the author's commit messages describe the January 2026 rewrite as 'Brand new version with vibe coding'.
- Multi-core servers. IoContext is single-threaded, and the repo's own examples/echo_server/README.md reports Tokio and exec-rs as 'nearly identical' at 4 threads (3,714k vs 3,703k at 500 connections).
- Anything beyond plain TCP: there is no TLS, UDP, DNS, file I/O or I/O-integrated timers, and no ecosystem (hyper, tonic, reqwest). Nested when_all and the merge/transform_each sequence senders are listed as incomplete.
- Windows. Sockets are registered with the poller only under cfg(unix).
- async/await codebases. Handlers become nested closures that clone Arcs: the exec echo example is 105 lines against 51 for the Tokio one.

## How it is fast

The echo result comes from a small single-threaded reactor. IoContext::run_one polls mio (epoll/kqueue) and runs readiness callbacks inline on the same thread, so the hot path has no work-stealing scheduler, task wakers or cross-thread handoff. Each read or write is tried directly on the non-blocking socket first. Only on WouldBlock does it store a boxed completion in a per-token HashMap. repeat_effect_until keeps each iteration's operation state inline and uses a thread-local trampoline to bound recursion. The Tokio baseline is not a current_thread runtime: it is Tokio's multi-thread scheduler with worker_threads(1), with the accept loop running inside block_on.

## Compared with alternatives

Pick exec-rs only if you want P2300 sender/receiver semantics in Rust specifically; uring_exec is the more serious C++ equivalent (P2300-style over io_uring). If you just need to beat Tokio, monoio (thread-per-core io_uring, about 1.86x Tokio at 4 cores in its own benchmark) and ringline are far more complete.

## Integration

| | |
|---|---|
| **Form** | crate (git dependency only; not published on crates.io under this name) |
| **Dependencies** | pin-project-lite 0.2, parking_lot 0.12, crossbeam-channel 0.5, wait_on_address 0.1, mio 1 (os-poll, os-ext, net); tokio is a dev-dependency only |
| **Minimum toolchain** | Rust 2021 edition; no rust-version declared. IoContext::spawn uses associated-type-bound syntax (Sender&lt;Completions: ...&gt;), which implies Rust 1.79+ (inferred). |
| **Platforms** | The core sender/scheduler code is plain Rust. Networking is Unix-only: Linux (epoll) and macOS/BSD (kqueue) through mio, because socket registration is behind cfg(unix). There is no CI, so no platform has been tested. |
| **Thread safety** | IoContext is single-threaded. Its poll handle, socket map and pending-op map are RefCells behind `unsafe impl Send + Sync`. Only the atomic intrusive task queue and the mio Waker are safe to use from other threads (through IoContextScheduler). StaticThreadPool and SingleThreadContext are for cross-thread compute. |
| **Drop-in for the baseline** | no |

## Gotchas

- The README's `exec-rs = "0.1"` resolves on crates.io to an unrelated crate (robinfriedli/exec-rs, task-execution utilities, versions 0.1.0-0.2.0). Use a git dependency instead. Cargo.toml's repository field also points to the wrong place (github.com/yuchao/exec-rs).
- I/O senders make one non-blocking syscall per readiness event. A spurious wakeup completes with a WouldBlock error instead of retrying, and repeat_effect/repeat_effect_until stop on error, so one spurious wakeup can end the accept loop or a connection.
- async_send_from does a single write and the echo example ignores the byte count, so partial writes are silently dropped (Tokio's echo uses write_all). IoContext keeps one pending op per socket token, so a concurrent read and write on one socket overwrite each other.
- Resource handling is loose. TcpStream has no Drop impl and deregister_socket is never called in the net module, so socket-map entries build up per connection. IoContext::spawn deliberately leaks the operation ('For now, we leak it'). The README calls StaticThreadPool work-stealing, but it is one shared crossbeam bounded channel.

## Known shortcomings

- Contradicted inside the repo: the top README claims 10-26% over Tokio, but examples/echo_server/README.md (Linux 5.15) reports +4-7% single-threaded and near-identical at 4 threads (3,714k vs 3,703k req/s). Not like-for-like: Tokio runs the multi-thread scheduler with worker_threads(1) and write_all, while exec-rs does one write and drops partial writes. benchmark.sh (rust_echo_bench, loopback, 128 B) gives no CPU, OS, rustc or run count and launches a nonexistent example. The README's exec-rs = "0.1" pulls an unrelated crates.io crate; this project is unpublished and Cargo.toml's repository points elsewhere. No LICENSE or CI; 'vibe coding' rewrite in 2026-01, idle since. Code bugs: spurious wakeups return WouldBlock and end accept loops or connections; one pending operation per socket (concurrent read and write overwrite each other); closed sockets never removed; spawn leaks the operation; heavy unsafe Send/Sync over RefCell. Unix TCP only; the 'work-stealing' pool is a single shared channel.

## Caveats and trade-offs

The README and Cargo.toml declare Apache-2.0, but the repository has no LICENSE file and GitHub detects no license, so treat it as reference only. No hardware, compiler or load-generator details are given for the benchmark. Single-threaded mode only.

Implements the C++ P2300 std::execution proposal's sender/receiver model in Rust; several features (nested when_all, some sequence senders) are incomplete.

## Maintenance

The last commit was 2026-01-31, about 8 months ago, so 'active' is generous. The current code is a January 2026 rewrite. README and Cargo.toml say Apache-2.0 but the repo has no LICENSE file, so read it for reference and do not take it as a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README 'Benchmark Results' table compares exec-rs directly against a Tokio echo server (examples tokio_echo vs exec_echo) and supports the claimed 10-26% (104,601/114,478/107,333/85,745 vs 114,723/130,694/135,157/100,321 req/s). No hardware, compiler, load generator or run methodology is given, so this is first-party evidence without methodology.
- **Verifier notes:** Numbers match the README exactly. baseline_in_list is now false: Tokio is not in the event-loops incumbent list (libuv/libevent/epoll/io_uring) and not in known_list.txt. Metadata checked: 26 stars, last commit 2026-01-31 (active), no license detected, and LICENSE, LICENSE-APACHE and LICENSE.md all return 404.
- **Fields the verifier corrected:** `baseline_in_list`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/npuichigo/exec-rs>
  - <https://github.com/npuichigo/exec-rs#benchmark-results>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/README.md>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/Cargo.toml>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/npuichigo/exec-rs>
  - <https://github.com/npuichigo/exec-rs/tree/master>
  - <https://github.com/npuichigo/exec-rs/tree/master/src>
  - <https://github.com/npuichigo/exec-rs/tree/master/src/net>
  - <https://github.com/npuichigo/exec-rs/tree/master/src/scope>
  - <https://github.com/npuichigo/exec-rs/tree/master/src/adaptors>
  - <https://github.com/npuichigo/exec-rs/tree/master/src/util>
  - <https://github.com/npuichigo/exec-rs/tree/master/src/schedulers>
  - <https://github.com/npuichigo/exec-rs/tree/master/src/future>
  - <https://github.com/npuichigo/exec-rs/tree/master/examples>
  - <https://github.com/npuichigo/exec-rs/tree/master/examples/echo_server>
  - <https://github.com/npuichigo/exec-rs/commits/master.atom>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/README.md>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/Cargo.toml>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/src/lib.rs>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/src/net/mod.rs>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/src/net/io_context.rs>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/src/net/operations.rs>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/src/net/socket.rs>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/src/net/buffer.rs>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/src/adaptors/repeat.rs>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/src/scope/async_scope.rs>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/src/schedulers/thread_pool.rs>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/src/schedulers/trampoline.rs>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/src/util/intrusive_queue.rs>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/src/consumers/start_detached.rs>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/src/future/mod.rs>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/examples/echo_server/tokio_echo.rs>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/examples/echo_server/exec_echo.rs>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/examples/echo_server/README.md>
  - <https://raw.githubusercontent.com/npuichigo/exec-rs/master/examples/echo_server/benchmark.sh>
  - <https://raw.githubusercontent.com/haraldh/rust_echo_bench/master/README.md>
  - <https://raw.githubusercontent.com/haraldh/rust_echo_bench/master/src/main.rs>
  - <https://crates.io/api/v1/crates/exec-rs>
  - <https://crates.io/api/v1/crates?q=p2300&per_page=10>
  - <https://hn.algolia.com/api/v1/search?query=exec-rs%20P2300&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=npuichigo>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/npuichigo/exec-rs`) · [data/wave5/enrich/raw/github_com_npuichigo_exec_rs.json](../../../data/wave5/enrich/raw/github_com_npuichigo_exec_rs.json) (enrichment confidence 0.35)

</details>
