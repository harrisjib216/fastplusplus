# chili

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟡 stale

> Rust port of Spice: heartbeat-scheduled fork-join join() with far lower per-join overhead than rayon::join on fine-grained recursion.

| | |
|---|---|
| **Beats** | Rayon (rayon::join) |
| **Claimed result** | Ryzen 7 4800HS 8 cores: 1023 nodes 3.4 us vs Rayon 51.1 us; 16.7M nodes 13.6 ms vs 58.1 ms; 134M nodes 101.8 ms vs 497.2 ms. Apple M1: 1023 nodes 3.5 us vs 29.2 us; 16.7M nodes 11.2 ms vs 40.5 ms; 67.1M nodes 44.3 ms vs 167.1 ms. At 1023 nodes chili is slower than the sequential baseline (1.8 us, x0.53 on Ryzen; 1.6 us, x0.46 on M1). |
| **Workload** | Summing a balanced binary tree via fork-join at 1023 to 134M nodes. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 7 4800HS (8 cores), Apple M1 (8 cores) |
| **Adoption** | 721 stars |
| **Last commit** | 2025-05-01 |
| **Links** | [repository](https://github.com/dragostis/chili) · [benchmark](https://github.com/dragostis/chili) |

## Verdict

First-party divan benchmarks summing a balanced binary tree of u64 nodes: on a Ryzen 7 4800HS (8 cores), 13.6 ms vs 58.1 ms for rayon::join at 16.7M nodes and 101.8 ms vs 497.2 ms at 134M nodes; on an Apple M1, 11.2 ms vs 40.5 ms at 16.7M nodes; at 1K nodes chili beats Rayon (3.4 us vs 51.1 us) but is about 2x slower than sequential code. Rust version and flags are not stated, and Rayon is called from outside its pool.

## Use it when

- Deep recursive divide-and-conquer with very cheap leaves where you cannot easily pick a grain size (tree sums, recursive slice splits); the README's 16.7M-node tree sum runs in 13.6 ms vs 58.1 ms for rayon::join on a Ryzen 7 4800HS.
- Code where rayon::join overhead dominates and you only need binary fork-join, not parallel iterators.
- Workloads where single-thread overhead matters: the README reports about 2x the sequential time at 1K nodes, roughly flat from 1 to 8 threads.
- Pure-Rust projects that accept a small crate with unsafe internals (MIT OR Apache-2.0, no runtime dependencies).

## Skip it when

- Small inputs where sequential code wins: at 1023 nodes chili is 0.53x (Ryzen) and 0.46x (M1) of the sequential baseline.
- Long-running or blocking leaf work without inner joins: work is only shared at join points, so a thread stuck in a long leaf never offers its queued jobs (open issue #33, 'Why is heartbeat not preemptive?').
- Code that needs Rayon's ecosystem (par_iter, scope, spawn, install, rayon-core compatibility); spawn(fn) (#20) and rayon-core compatibility (#12) are open requests.
- Many-core machines with high share rates: every shared job goes through one global Mutex&lt;LockContext&gt;, and there is no published scaling data beyond 8 cores.
- Production code that needs a clean soundness record: open issue #39 (June 2026) reports that Receiver::recv calls thread::park() once and then reads the result under a SAFETY comment, although park can return spuriously, so the value may be read before the sender has written it.

## How it is fast

Heartbeat scheduling (Acar et al., the Spice design): join pushes the left job on a thread-local queue and runs the right closure directly. Only when a heartbeat flag, set by a dedicated timer thread every heartbeat_interval, is seen does the thread move its oldest queued job to a shared, mutex-protected BTreeMap that idle workers take from. The heartbeat flag is checked only on every 64th join, or when the local queue holds fewer than 3 jobs; other joins run both closures sequentially. So almost every join costs a few stack operations, with no atomic deque operations or wakeups.

## Compared with alternatives

Pick chili over Spice when you are in Rust rather than Zig, since it is the same heartbeat design; pick it over Fork Union or Weave when the work is irregular recursive fork-join rather than flat parallel-for loops; the C++ deepsea-inria/heartbeat prototype is the research reference for the same idea.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | none (divan and rayon are dev-dependencies for benches) |
| **Minimum toolchain** | Rust 2021 edition; uses std::num::NonZero (stable since Rust 1.79) |
| **Platforms** | any std platform (std threads, Mutex, Condvar, park/unpark); benchmarked on x86-64 (Ryzen 7 4800HS) and aarch64 (Apple M1) |
| **Thread safety** | Scope is per-thread (&mut); multiple threads can each create their own scope on one pool (concurrent_scopes test with 128 threads); panics in a stolen job are carried back and resumed on the joining thread |
| **Drop-in for the baseline** | partial — join closures take &mut Scope and need a Scope from a ThreadPool, so rayon::join call sites must be rewritten; no par_iter or scope/spawn |

## Gotchas

- The pool spawns available_parallelism - 1 workers plus a heartbeat thread; the calling thread is the remaining worker. Issue #21 (heartbeat thread using too much CPU while idle) was fixed in March 2025.
- Sequential fallback order: join_seq runs b before a, so side effects in the two closures can happen in either order. The doc comment says the heartbeat check is skipped 'every 16 calls' but the code uses 64.
- The README's overhead table gives the 1023-node baseline as 1.8 ns where the main table gives 1.8 us, and the 134M-node (Ryzen) and 67M-node (M1) rows are not in benches/overhead.rs, which only runs 10 and 24 layers (1023 and 16,777,215 nodes).
- In benches/overhead.rs the Rayon variant calls rayon::join from the divan bench thread, outside any Rayon pool, so each iteration pays Rayon's cold inject-and-wait path; this inflates Rayon's small-tree time (51.1 us at 1023 nodes) compared with calling from inside pool.install.

## Known shortcomings

- Open issue 39: Receiver::recv calls park() once, so a spurious wakeup can read the value early (unsoundness, not on the benchmark path). The bench calls rayon::join outside the Rayon pool (cold inject), which inflates the Rayon 1K-node figure of 51.1 us; the 134M/67M rows are not in benches/overhead.rs; the README overhead table says 1.8 ns where the main table says 1.8 us. Rust, not C++.

## Caveats and trade-offs

Single synthetic tree-sum benchmark; compiler and flags not stated; Rust port of Spice. At 1K nodes both chili and Rayon are slower than the single-threaded baseline (chili x0.53 / x0.46), so the win over Rayon there is overhead reduction, not a speedup over sequential code. Found via HN thread 'Show HN: Chili' title only (thread blocked).

Heartbeat scheduling, join-only API; no parallel iterators or scopes.

## Maintenance

Stale since May 2025 (crate 0.2.1, 721 stars) and has an open unsoundness report (#39), but it is small, dual MIT/Apache-2.0, and its core is about 1,100 lines of Rust that you can audit or vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Benchmarks tables compare chili against rayon::join and a sequential baseline on a balanced-tree sum, with CPU models stated and bench code in the repo (Cargo.toml [[bench]] overhead, divan + rayon dev-deps), but no compiler version or flags are given, so first-party C.
- **Verifier notes:** Numbers match the README. License MIT OR Apache-2.0 confirmed via Cargo.toml plus LICENSE-MIT and LICENSE-APACHE files (no plain LICENSE). Last commit 2025-05-01, 721 stars confirmed on github.com.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/dragostis/chili/HEAD/README.md>
  - <https://raw.githubusercontent.com/dragostis/chili/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/dragostis/chili/HEAD/LICENSE-MIT>
  - <https://raw.githubusercontent.com/dragostis/chili/HEAD/LICENSE-APACHE>
  - <https://github.com/dragostis/chili/commits>
- **Sources the enricher read:**
  - <https://github.com/dragostis/chili>
  - <https://raw.githubusercontent.com/dragostis/chili/HEAD/README.md>
  - <https://raw.githubusercontent.com/dragostis/chili/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/dragostis/chili/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/dragostis/chili/HEAD/src/job.rs>
  - <https://raw.githubusercontent.com/dragostis/chili/HEAD/benches/overhead.rs>
  - <https://github.com/dragostis/chili/issues?q=is%3Aissue>
  - <https://github.com/dragostis/chili/issues/39>
  - <https://github.com/dragostis/chili/issues/33>
  - <https://github.com/dragostis/chili/issues/8>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/dragostis/chili`) · [data/wave11/enrich/raw/github_com_dragostis_chili.json](../../../data/wave11/enrich/raw/github_com_dragostis_chili.json) (enrichment confidence 0.75)

</details>
