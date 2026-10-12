# Tokio (1M concurrent tasks, peak memory)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Concurrency runtimes](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust's work-stealing async runtime; 1M sleeping tasks used 2.8x less peak memory than concurrencpp and 4x less than Asio.

| | |
|---|---|
| **Beats** | Asio C++20 coroutines (awaitable tasks) and concurrencpp |
| **Claimed result** | Peak memory at 1M tasks: tokio 214,136 KB, concurrencpp 605,972 KB, Asio 853,144 KB (about 2.8x and 4.0x less, derived from page data); at 100k tasks: 23,824 vs 61,460 vs 86,652 KB; at 10k: 6,908 vs 7,840 vs 10,244 KB. At 1 task tokio is the largest (3,092 KB vs Asio 1,668 KB). Libunifex hangs at 100k and 1M. |
| **Workload** | Spawn N concurrent async tasks that wait on a timer and measure peak memory (port of the Rust '1 million concurrent tasks' memory benchmark to C++ coroutine libraries). |
| **Metric** | memory |
| **Hardware** | Intel i7-8550U (8 threads, about 1.99 GHz), 8 GB RAM, WSL Ubuntu 20.04.6 on Windows 10 |
| **Compiler and flags** | C++20, CMAKE_BUILD_TYPE Release set in CMakeLists.txt (-O3 -DNDEBUG with GCC or Clang), compiler not named; Asio and concurrencpp fetched by FetchContent with no GIT_TAG (default-branch HEAD at build time, June 2023), libunifex GIT_TAG main; tokio_bench built by 'cargo build --release' from CMakeLists.txt (opt-level 3), tokio 1.28.2 per Cargo.lock, #[tokio::main] multi-thread runtime. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 33.4k stars (tokio); benchmark repo has 4 stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/tokio-rs/tokio) · [benchmark](https://github.com/Xavorim/cpp_tasks_bench) |

## Verdict

Peak RSS from /usr/bin/time for N tasks each awaiting a 10 s timer, all alive at once, on an Intel i7-8550U (8 GB, WSL Ubuntu 20.04): tokio 1.28.2 (cargo --release) used 214,136 KB at 1M tasks versus 605,972 KB for concurrencpp and 853,144 KB for Asio (C++20 Release builds, compiler not named, libraries at June 2023 HEAD), about 2.8x and 4.0x less. Libunifex hung at 100k and above, and tokio was the largest at 1 task.

## Use it when

- Rust services that keep hundreds of thousands to millions of mostly idle tasks alive at once (connections waiting on I/O or timers), where per-task memory dominates.
- Network servers and clients that want a multi-core work-stealing scheduler with no hand-written thread-to-io_context mapping.
- Memory-constrained hosts running a large fan-out of timers or sleeps, since each sleep lives inside its task allocation.
- Teams that can put the concurrent part of a system in Rust and talk to C++ over a socket or FFI boundary.

## Skip it when

- Small task counts: at 1 task tokio had the largest footprint (3,092 KB vs Asio 1,668 KB), and only at 10k tasks did it pull ahead (6,908 vs concurrencpp 7,840 and Asio 10,244 KB).
- When throughput rather than memory is the goal: the catalogue's own echo-server sibling shows Boost.Asio C++20 coroutines slightly faster than Tokio.
- CPU-bound or blocking work inside tasks: a task only yields at .await, so long computations stall a core thread; the crate docs route such code to spawn_blocking or a separate pool.
- In-process use from a C++ codebase: it is a Rust crate with no C ABI, so integration means FFI glue or a separate process.
- Wasm targets: only the sync, macros, io-util, rt and time features build there, 'full' fails to compile and timers can panic.

## How it is fast

Rust compiles each async fn into a stackless state machine whose size is fixed at compile time, and tokio::spawn moves that future into one heap block (the task Cell) together with its header, scheduler handle, task id and trailer. tokio::time::sleep keeps its timer entry inline in the future (an intrusive timer registered in a hierarchical timing wheel of 6 levels with 64 slots), so in tokio 1.28.2 a sleeping task is a single allocation with no separate stack or timer object. That is about 216 bytes per task in this run, against about 619 for concurrencpp and 872 for Asio (derived from page data as (RSS at 1M minus RSS at 1 task) / 1M, 1 KB = 1024 bytes).

## Compared with alternatives

Pick this entry when the deciding factor is the memory cost of very many concurrent tasks: the Tokio echo-server sibling covers throughput, where Asio is slightly ahead. GHC lightweight threads and Go goroutines are measured against OS threads or a pthread-based ring rather than C++ coroutine libraries, so this is the only sibling that compares stackless tasks with C++20 coroutine runtimes.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | pin-project-lite; optional per feature: mio, bytes, parking_lot, socket2, libc, signal-hook-registry, windows-sys, tokio-macros |
| **Minimum toolchain** | Rust 1.85 on master (README: 1.54 onward); the 1.53.x LTS line needs Rust 1.71; the benchmark used tokio 1.28.2 |
| **Platforms** | Linux, Windows, Android (API 21), macOS, iOS and FreeBSD guaranteed; other mio platforms best effort; Wasm limited |
| **Thread safety** | tokio::spawn on the default multi-thread runtime requires Send + 'static futures and moves tasks between worker threads; spawn_local and the current-thread runtime cover !Send futures. |
| **Drop-in for the baseline** | no |

## Gotchas

- The measured version predates task padding: PR #5809 (merged 2023-06-21, after the 1.28.2 release the benchmark locked) makes the task Cell repr(align(128)) on x86-64, aarch64 and powerpc64 to avoid false sharing, so on current tokio each task allocation is rounded up to a multiple of 128 bytes. Per-task memory today is probably above the about 216 bytes seen here. Not re-measured, and the change is not in the changelog.
- Peak RSS mixes fixed runtime cost with per-task cost. Tokio's multi-thread runtime starts one core thread per CPU (8 on this i7-8550U), while the Asio program runs everything on the main thread and concurrencpp uses one worker_thread_executor plus its timer_queue. The slope between the 1-task and 1M-task rows is the fairer comparison, and it still favours tokio about 2.9x over concurrencpp and 4x over Asio (derived).
- The C++ programs are one design each and were not tuned: every Asio task builds its own asio::steady_timer inside an awaitable frame launched by co_spawn, and every concurrencpp task copies two shared_ptrs into its frame and makes its own delay object. Shared timers or custom frame allocators were not tried, the C++ library versions were unpinned (fetched at HEAD in June 2023) and the compiler is not named.
- Single unreported-count runs of /usr/bin/time under WSL Ubuntu 20.04 on a laptop, memory only (no spawn time or wake latency), from a 4-star one-person repo; the tokio project itself makes no C++ comparison.

## Known shortcomings

- Memory-only comparison (1M tasks: Tokio 214 MB vs Asio 853 MB, concurrencpp 606 MB) from a 4-star 2023 hobby repo (Xavorim/cpp_tasks_bench) with the C++ compiler unnamed and C++ libraries unpinned; Tokio is larger at 1 task.
- A later raw copy (HttpArena raw tokio HTTP/1.1 server) shares the repo URL; the verified concurrency-runtimes identity is kept by override and the HttpArena rows live under lang:rust/mda2av/httparena#baseline-4096.
- The harness is logically fair and the per-task slope still favours tokio (about 216 vs 619 vs 872 bytes, derived), but the measured tokio 1.28.2 predates PR #5809 (2023-06-21), which aligns the task Cell to 128 bytes on x86-64, so current per-task memory is probably higher (not re-measured, not in the changelog). Peak RSS mixes a fixed cost: tokio runs 8 worker threads while Asio runs 1 thread; the C++ programs are untuned and their versions unpinned.

## Caveats and trade-offs

Independent hobby replication (4 stars, 6 commits all on 2023-06-24) of the pkolaczk 'How Much Memory Do You Need to Run 1 Million Concurrent Tasks?' benchmark, not the tokio authors' work; the README notes the original methodology was criticised. Memory only (peak RSS from /usr/bin/time), no timing; run count not stated; WSL Ubuntu 20.04 on a laptop i7-8550U with 8 GB. C++ compiler unnamed and Asio/concurrencpp versions unpinned. Workloads match logically (N tasks each awaiting a 10 s timer, all alive at once), but the C++ programs differ in structure: Asio builds a vector of N lazily-started awaitables and then co_spawns each on one io_context thread; concurrencpp copies two shared_ptrs into every coroutine frame and uses one worker_thread_executor plus its timer_queue; tokio spawns each task on the default multi-thread runtime and keeps the JoinHandles. Tokio is the largest at 1 task (3,092 KB vs Asio 1,668 KB) and only pulls ahead from 10k tasks. Libunifex hangs at 100k and 1M. The tokio repo itself makes no comparison to C++ runtimes. [retier] The measured tokio 1.28.2 predates PR #5809 (2023-06-21), which aligns the task Cell to 128 bytes on x86-64, so current per-task memory is probably higher (not re-measured). Peak RSS mixes a fixed cost: tokio runs 8 worker threads while Asio runs 1; the per-task slope is about 216 vs 619 vs 872 bytes (derived). The C++ programs are untuned and their versions unpinned.

Tokio tasks are stackless futures sized by the compiler, so memory is small per task but not free of heap allocation per spawn; the C++ libraries allocate a coroutine frame per task. The result is about memory only, not throughput or latency.

## Maintenance

Tokio is very active (MIT, 33.4k stars, monthly minor releases, LTS lines 1.51.x to March 2027 and 1.53.x to September 2027); the evidence is a one-off June 2023 hobby benchmark against tokio 1.28.2, and current tokio's 128-byte task alignment may narrow the measured gap.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Xavorim/cpp_tasks_bench README lists the exact peak-RSS figures (/usr/bin/time) for tokio, concurrencpp, Asio and libunifex at 1, 10k, 100k and 1M tasks on an i7-8550U under WSL; code is public (asio_bench/main.cpp, concurrencpp_bench/main.cpp, tokio_bench/src/main.rs) and CMakeLists.txt fixes Release and cargo --release, but the C++ compiler is not named and the C++ libraries are unpinned, so not A; a 4-star one-person repo is not a well-known independent suite, so C.
- **Verifier notes:** Confirm at C: numbers match the benchmark README exactly (1M tasks: tokio 214,136 KB vs concurrencpp 605,972 KB and Asio 853,144 KB, about 2.8x and 4.0x less, derived); same -O3-equivalent Release builds per CMakeLists.txt; tokio metadata (MIT, 33.4k stars, last commit 2026-10-11) checks out. Shortcomings to record: one-person 2023 hobby benchmark, compiler unnamed, unpinned C++ library versions, memory-only single-run figures on WSL, tokio larger at 1 task, library-level not language-level claim.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-01 (wave 14); orchestrator (wave 14 merge); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/Xavorim/cpp_tasks_bench>
  - <https://github.com/Xavorim/cpp_tasks_bench/commits/main>
  - <https://github.com/Xavorim/cpp_tasks_bench/tree/main/asio_bench>
  - <https://github.com/Xavorim/cpp_tasks_bench/tree/main/tokio_bench>
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/asio_bench/main.cpp>
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/concurrencpp_bench/main.cpp>
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/unifex_bench/main.cpp>
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/tokio_bench/src/main.rs>
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/tokio_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/tokio_bench/Cargo.lock>
  - <https://github.com/tokio-rs/tokio>
  - <https://github.com/tokio-rs/tokio/commits/master>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/asio_bench/main.cpp>
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/concurrencpp_bench/main.cpp>
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/unifex_bench/main.cpp>
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/tokio_bench/src/main.rs>
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/tokio_bench/Cargo.toml>
  - <https://raw.githubusercontent.com/Xavorim/cpp_tasks_bench/HEAD/tokio_bench/Cargo.lock>
  - <https://raw.githubusercontent.com/tokio-rs/tokio/HEAD/README.md>
  - <https://raw.githubusercontent.com/tokio-rs/tokio/HEAD/tokio/Cargo.toml>
  - <https://raw.githubusercontent.com/tokio-rs/tokio/HEAD/tokio/CHANGELOG.md>
  - <https://raw.githubusercontent.com/tokio-rs/tokio/HEAD/tokio/src/lib.rs>
  - <https://raw.githubusercontent.com/tokio-rs/tokio/HEAD/tokio/src/runtime/task/core.rs>
  - <https://raw.githubusercontent.com/tokio-rs/tokio/tokio-1.28.2/tokio/src/runtime/task/core.rs>
  - <https://raw.githubusercontent.com/tokio-rs/tokio/tokio-1.28.2/tokio/src/runtime/time/entry.rs>
  - <https://raw.githubusercontent.com/tokio-rs/tokio/tokio-1.28.2/tokio/src/runtime/time/wheel/mod.rs>
  - <https://github.com/tokio-rs/tokio/commits/master/tokio/src/runtime/task/core.rs>
  - <https://github.com/tokio-rs/tokio/commit/2e62374>
  - https://raw.githubusercontent.com/chriskohlhoff/asio/HEAD/asio/include/asio/impl/co_spawn.hpp (404)
  - https://github.com/chriskohlhoff/asio/blob/master/asio/include/asio/impl/co_spawn.hpp (503)
  - https://docs.rs/tokio/latest/tokio/index.html (blocked)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/tokio-rs/tokio`) · [data/wave14/enrich/raw/github_com_tokio_rs_tokio.json](../../../data/wave14/enrich/raw/github_com_tokio_rs_tokio.json) (enrichment confidence 0.7)

</details>
