# Rayon

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT OR Apache-2.0` · 🟢 active

> Rust work-stealing data-parallelism crate (par_iter, join, scope); beats OpenMP only in fine-grained dynamic-schedule cells of a competitor's benchmark.

| | |
|---|---|
| **Beats** | OpenMP parallel for (C++ with static and dynamic scheduling) |
| **Claimed result** | Mixed, mostly OpenMP ahead. Rayon wins: N-body on the 24x Intel RPL Windows box, Rayon 151 / 151 us vs OpenMP 360 / 627 us (about 2.4x static, 4.2x dynamic, derived from page data); connected components with dynamic (one-vertex) scheduling, Rayon vs OpenMP GTEPS 6.5 vs 0.4 on 128x Intel SPR (about 16x, derived from page data), 6.2 vs 0.4 on 192x Graviton 5 (about 15x, derived from page data), 5.2 vs 0.1 on 24x Intel RPL (about 50x from rounded values, derived from page data); static connected components on 18x Apple M5 Pro 23.8 vs 23.0 (about 1.03x, derived from page data). Rayon loses: N-body on M5 Pro 222 / 339 us vs 115 / 137, on SPR 483 / 739 vs 115 / 226, on Graviton 5 490 / 580 vs 266 / 216; dynamic connected components on M5 Pro 14.6 vs 18.3 GTEPS; static connected components on SPR 8.5 vs 28.2, on Graviton 5 8.4 vs 53.9, on RPL 9.4 vs 11.4. |
| **Workload** | Fork Union README Performance section: N-body at 512 bodies on every logical core (microseconds per iteration, static / dynamic) and connected components by label propagation on a \~27M-edge R-MAT 'necklace' graph (GTEPS, 84 fork-join rounds per pass), one fixed 30-second window per cell, four machines. Rayon static is par_chunks_mut with one stripe per worker in N-body and plain par_iter_mut (Rayon's default adaptive splitting) in connected components; Rayon dynamic is par_iter_mut().with_max_len(1). OpenMP uses schedule(static) and schedule(dynamic, 1). |
| **Metric** | latency |
| **Hardware** | 18x Apple M5 Pro (macOS); 24x Intel RPL (Windows, also called a 24x i9 in the README); 128x Intel SPR (Linux); 192x AWS Graviton 5 (Linux); exact CPU SKUs not given |
| **Compiler and flags** | C++ side: Release build adds -O3 -march=native -mtune=native and -ffp-contract=off (scripts/CMakeLists.txt), no LTO; OpenMP is -fopenmp (libgomp) under GCC and Homebrew libomp under Clang/AppleClang (OpenMP is disabled for Clang without Homebrew). The compiler used for each machine is not stated; the README names MinGW-GCC for the 24x i9 (RPL) Windows box, and the macOS instructions use Homebrew LLVM clang plus libomp. N-body runs under numactl --interleave=all with OMP_PROC_BIND=spread OMP_PLACES=cores per the scripts/nbody.cpp header; connected-components cells run bare without pinning per the scripts/propagation.{cpp,rs} headers. Rust side: cargo build --release with RUSTFLAGS='-C target-cpu=native', profile opt-level 3, lto false, codegen-units 1, unchecked hot loops, rayon '1.11' requirement in Cargo.toml. |
| **Adoption** | 13.4k stars, 618 forks; rayon 1.12.0 published on crates.io 2026-04-14 |
| **Last commit** | 2026-08-28 |
| **Links** | [repository](https://github.com/rayon-rs/rayon) · [benchmark](https://github.com/ashvardanian/fork_union) |

## Verdict

The only Rayon-vs-OpenMP numbers are in the competing Fork Union README (four machines, every logical core, one 30-second window per cell, -O3 -march=native and target-cpu=native, compilers unnamed except MinGW-GCC on the Windows box): Rayon beats OpenMP when OpenMP uses schedule(dynamic, 1) on one-vertex connected-components claims (6.5 vs 0.4 GTEPS on 128x SPR, 6.2 vs 0.4 on 192x Graviton 5, 5.2 vs 0.1 on 24x RPL) and in N-body on the RPL Windows box (151 vs 360/627 us), and loses most other cells, by up to 6.4x on static connected components on Graviton 5. The Rust harness drives Rayon from the non-pool main thread through pool.install on every round, adding a global-injector push and a condition-variable wake that OpenMP's participating master thread does not pay, and its N-body OpenMP runs pinned (OMP_PROC_BIND=spread) while the Rayon pool is unpinned, so Rayon's dispatch figures are a pessimistic case rather than an idiomatic one.

## Use it when

- Rust code with irregular or recursive parallelism (divide and conquer, tree walks, parallel sort via par_sort_unstable) where dynamic load balancing matters more than per-dispatch latency.
- Coarse fork-join rounds (milliseconds of work each) where a dispatch cost in the tens to hundreds of microseconds is amortized and a one-line par_iter change is worth more than hand scheduling.
- Uneven per-item cost at high thread counts where a shared OpenMP schedule(dynamic, 1) queue collapses: in Fork Union's one-vertex connected-components cells Rayon kept 6.2-6.5 GTEPS against OpenMP's 0.4 on 128-192 threads.
- Projects that want compile-time data-race freedom from the type system rather than pragma discipline.

## Skip it when

- Many short fork-join rounds on many-core machines: in Fork Union's static connected components Rayon reached 8.5 GTEPS vs OpenMP 28.2 on 128x Intel SPR and 8.4 vs 53.9 on 192x Graviton 5, and N-body dispatch took 483 us vs 115 us on SPR.
- Regular, uniform loops that a static OpenMP schedule handles: Rayon has no fixed per-worker schedule, and issue #968 (open since 2022) reports about 20% slowdowns with non-power-of-two thread counts, suspected to come from even-halving splits overshooting to the next power of two.
- NUMA-sensitive, bandwidth-bound work: no built-in thread pinning or NUMA-local allocation (only start_handler/spawn_handler hooks you write yourself); issue #394, 'Communication costs are quadratic in the number of worker threads', is still open.
- Code that holds a Mutex or initializes a OnceLock across a parallel call: work stealing can re-enter the same lock on the same thread and deadlock (issue #592, open since 2018; #1251 hit it on a 192-thread Threadripper).
- C++ code bases: Rayon is Rust-only, so using it from C++ means an FFI boundary or a rewrite of the loop.

## How it is fast

Cilk-style work stealing: join(a, b) pushes b onto the caller's crossbeam-deque (Chase-Lev) and runs a, and idle workers steal from victims starting at a random index; join and parallel-iterator jobs live on the stack (StackJob), while scope/spawn heap-allocate one job per task. Parallel iterators use adaptive splitting: a Splitter starts with one split budget per thread, halves it on each split and resets it to the thread count whenever a piece is stolen, so work is only cut finer where stealing shows idle threads; with_min_len/with_max_len bound the grain. Idle workers yield for 32 rounds, then announce 'sleepy' through a jobs event counter and block on a condition variable (the sleep design from Rayon RFC #5).

## Compared with alternatives

Pick Rayon over chili or Spice when you need the full parallel-iterator API, scope/spawn and the existing ecosystem (chili lacks scope and spawn per Rayon issue #1235), accepting higher per-join overhead (chili's entry: 51.1 us vs 3.4 us for a 1023-node tree). For repeated flat fork-join loops on 100+ core machines, Fork Union or OpenMP's static schedule are faster per that same benchmark.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | rayon-core (crossbeam-deque, crossbeam-utils) and either; optional wasm_sync for the web_spin_lock feature |
| **Minimum toolchain** | rustc 1.80 for the published rayon 1.12.0 (crates.io rust_version); the main branch now declares rustc 1.85 and edition 2024 |
| **Platforms** | any Rust target with std threads; wasm32 targets without threads fall back to sequential execution unless wasm-bindgen-rayon is set up |
| **Thread safety** | Closures must be Send (and captured shared data Sync), so data races are compile errors; the global pool is process-wide and each rayon-core version carries its own global pool. |
| **Drop-in for the baseline** | partial — a one-line par_iter change for Rust loops, but not usable from C/C++ OpenMP code without FFI, and there is no static schedule equivalent |

## Gotchas

- Calling par_iter or ThreadPool::install from a thread outside the pool (such as main) injects the job into the global queue and blocks the caller on a Mutex/Condvar latch (in_worker_cold); for many short rounds, run the whole loop inside one install or build the pool with use_current_thread. Fork Union's harness pays this handoff on every round and every N-body half-step.
- A panic inside join or a parallel iterator propagates to the caller, but a panic in a spawned job aborts the process unless a panic_handler is set on the ThreadPoolBuilder.
- Idle workers spin through 32 thread::yield_now rounds before sleeping, which burns CPU between bursts of small work (closed issue #642, 'Rayon uses a lot of CPU when there's not a lot of work to do').
- Two rayon-core versions in one dependency graph mean two global thread pools competing for the same cores (rayon-core README).

## Known shortcomings

- Downgraded B to C: the only numbers come from the rival Fork Union README (competitor-run; no compiler named, CPUs given as families only). Rayon is slower than OpenMP in most cells, including dynamic connected components on M5 Pro (14.6 vs 18.3 GTEPS); its 15-50x wins come only from OpenMP's schedule(dynamic,1) queue collapse. nbody.cpp's header claims -ffast-math while the CMake file sets strict IEEE (-ffp-contract=off); connected-components cells run unpinned. A Rust library in a C++ thread-pool category.
- Fork Union harness calls pool.install from a non-worker thread every round and leaves Rayon unpinned while OpenMP is pinned (biased against Rayon)

## Caveats and trade-offs

Evidence is a side result of a competing library's benchmark: the README belongs to Fork Union (ForkUnion, Rust and C++), whose author promotes it as about 3-6x faster than OpenMP and 12-16x faster than Rayon, so the figures were not produced by the Rayon project. Rayon beats OpenMP only in a minority of cells; OpenMP's 'dynamic' columns use schedule(dynamic, 1), a one-vertex grain whose shared queue collapses at high thread counts (0.1-0.4 GTEPS, as the README itself explains), which is why the 15-50x Rayon wins appear; against OpenMP's static schedule Rayon is behind on most machines (up to 6.4x lower GTEPS on Graviton 5, derived from page data) and it also loses dynamic connected components on the M5 Pro. The one N-body win is on the Windows box where the README names MinGW-GCC, so the OpenMP runtime there is probably libgomp, not libomp. Fork Union's documentation disagrees on fast-math: the scripts/nbody.cpp and nbody.rs headers say the C++ build adds -ffast-math, while scripts/CMakeLists.txt says strict IEEE math is deliberate and adds only -ffp-contract=off; which build produced the tables is not stated. Rayon 'static' in connected components is plain par_iter_mut with adaptive splitting, not a fixed per-worker stripe as the doc comment says. Exact CPU models and compiler versions are not given, and the benchmark does not use the cited 'oneTBB parallel_for' or 'std::execution::par' baselines. Rayon's own repo has no comparison against OpenMP, TBB or std::execution::par: the README carries no numbers, PR #1156 (par_sort sync) says 'mostly the same or slightly better' with no figures, and rayon-demo prints sequential-vs-parallel speedups at run time without stored results. A search snippet (arXiv 2502.15536, NPB-Rust, page blocked and not opened) reports Rayon slower than C++ OpenMP on the NAS kernels; snippet only. [retier] Enricher: Fork Union's scripts/nbody.rs and propagation.rs call pool.install from the main thread, which is not a pool worker, on every round (twice per N-body iteration), taking the in_worker_cold path (global injector push plus a Mutex/Condvar LockLatch wait), while OpenMP's master thread joins the work; one install around the whole loop or use_current_thread is the idiomatic form. N-body OpenMP is pinned (OMP_PROC_BIND=spread) and the Rayon pool is not. So the Rayon numbers are pessimistic and its wins are not inflated. Minimum toolchain: published 1.12.0 declares rust_version 1.80; main's Cargo.toml says rustc 1.85, edition 2024. Gotchas: Mutex/OnceLock reentrancy deadlock (#592 open, #1251), slowdown with non-power-of-two thread counts (#968 open), quadratic stealing cost (#394 open), spawn panics abort without a panic_handler, 32 yield rounds before sleeping.

Rust-only (C++ projects must call it over FFI or rewrite the loop); par_iter is a one-line change and the API guarantees data-race freedom; dynamic splitting by default means no static schedule, so uniform loops pay stealing overhead and tiny per-item work can run slower than serial (forum reports, not opened).

## Maintenance

Actively maintained (rayon 1.12.0 published 2026-04-14, main branch commits through 2026-08-28), dual MIT/Apache-2.0, and one of the most-used Rust crates (about 149M downloads of 1.12.0 alone per crates.io).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification B, tier now C.
- **Tier reason:** The only Rayon-vs-OpenMP numbers are in the competing Fork Union README (benchmark code public in scripts/nbody.{cpp,rs} and scripts/propagation.{cpp,rs}, flags -O3 -march=native / target-cpu=native stated), but no compiler or version is named for the tables and CPUs are families only (Intel SPR, RPL, Apple M5 Pro, Graviton 5), so not A; a competitor library's README is not a well-known independent benchmark suite (precedent: TurboPFor README numbers run by a competitor's author were tiered C), and Rayon beats OpenMP only in a minority of cells.
- **Verifier notes:** All table numbers match the Fork Union README rows for Rayon and OpenMP; the record missed the M5 Pro dynamic connected-components loss and misattributed 'LLVM clang plus libomp' and '-ffast-math' as the general C++ build (CMake uses GCC libgomp or Homebrew libomp and states strict IEEE). Consider decision keep with shortcoming 'not faster than OpenMP in most cells'; Fork Union itself was tiered C in batch-44.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-68 (wave 11 book seed pass, 2026-10-24); enrichment (wave 11 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/rayon-rs/rayon>
  - <https://github.com/rayon-rs/rayon/commits/main>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/README.md>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/scripts/nbody.cpp>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/scripts/nbody.rs>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/scripts/propagation.cpp>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/scripts/propagation.rs>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/scripts/CMakeLists.txt>
  - <https://crates.io/api/v1/crates/rayon/versions?per_page=3>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/rayon-rs/rayon/HEAD/README.md>
  - <https://raw.githubusercontent.com/rayon-rs/rayon/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/rayon-rs/rayon/HEAD/FAQ.md>
  - <https://raw.githubusercontent.com/rayon-rs/rayon/HEAD/RELEASES.md>
  - <https://raw.githubusercontent.com/rayon-rs/rayon/HEAD/rayon-core/Cargo.toml>
  - <https://raw.githubusercontent.com/rayon-rs/rayon/HEAD/rayon-core/README.md>
  - <https://raw.githubusercontent.com/rayon-rs/rayon/HEAD/rayon-core/src/registry.rs>
  - <https://raw.githubusercontent.com/rayon-rs/rayon/HEAD/rayon-core/src/sleep/mod.rs>
  - <https://raw.githubusercontent.com/rayon-rs/rayon/HEAD/rayon-core/src/sleep/README.md>
  - <https://raw.githubusercontent.com/rayon-rs/rayon/HEAD/rayon-core/src/join/mod.rs>
  - <https://raw.githubusercontent.com/rayon-rs/rayon/HEAD/rayon-core/src/lib.rs>
  - <https://raw.githubusercontent.com/rayon-rs/rayon/HEAD/rayon-core/src/scope/mod.rs>
  - <https://raw.githubusercontent.com/rayon-rs/rayon/HEAD/rayon-core/src/latch.rs>
  - <https://raw.githubusercontent.com/rayon-rs/rayon/HEAD/rayon-core/src/thread_pool/mod.rs>
  - <https://raw.githubusercontent.com/rayon-rs/rayon/HEAD/src/iter/plumbing/mod.rs>
  - <https://raw.githubusercontent.com/rayon-rs/rayon/HEAD/src/iter/plumbing/README.md>
  - <https://crates.io/api/v1/crates/rayon/versions?per_page=3>
  - <https://github.com/rayon-rs/rayon/issues?q=is%3Aissue+label%3Aperformance>
  - <https://github.com/rayon-rs/rayon/issues?q=is%3Aissue+deadlock>
  - <https://github.com/rayon-rs/rayon/issues?q=is%3Aissue+cpu+usage+idle+spin>
  - <https://github.com/rayon-rs/rayon/issues/1251>
  - <https://github.com/rayon-rs/rayon/issues/1235>
  - <https://github.com/rayon-rs/rayon/issues/592>
  - <https://github.com/rayon-rs/rayon/issues/394>
  - <https://github.com/rayon-rs/rayon/issues/968>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/README.md>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/scripts/nbody.rs>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/scripts/nbody.cpp>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/scripts/propagation.rs>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/scripts/propagation.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/rayon-rs/rayon`) · [data/wave11/enrich/raw/github_com_rayon_rs_rayon.json](../../../data/wave11/enrich/raw/github_com_rayon_rs_rayon.json) (enrichment confidence 0.75)

</details>
