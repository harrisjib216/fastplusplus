# Fork Union

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++ (also C, Rust, Zig)` · `Apache-2.0` · 🟢 active

> NUMA-aware fork-join thread pool for C++/C/Rust/Zig with lower parallel-for dispatch latency than OpenMP, Rayon and Taskflow.

| | |
|---|---|
| **Beats** | OpenMP, Rayon, Taskflow |
| **Claimed result** | README headline: often \~3-6x faster than OpenMP and \~12-16x faster than Rayon and Taskflow per parallel-for dispatch. N-body at N=512, us per iteration, static/dynamic: 128x Intel SPR ForkUnion C++ 54/86, ForkUnion Rust 40/67, OpenMP 115/226, Rayon 483/739, Taskflow 666/694. Connected components, GTEPS: 192x Graviton 5 ForkUnion Rust 258.7/87.3, ForkUnion C++ 192.6/77.6, OpenMP 53.9/0.4, Rayon 8.4/6.2, Taskflow 53.0/0.4. |
| **Workload** | N-body parallel-for dispatch latency (512 bodies, all cores) and connected-components GTEPS on a 27M-edge graph, on Apple M5 Pro, Intel RPL, Intel SPR and AWS Graviton 5. |
| **Metric** | latency |
| **Hardware** | 18x Apple M5 Pro, 24x Intel RPL, 128x Intel SPR, 192x AWS Graviton 5 (exact CPU SKUs not named) |
| **Compiler and flags** | -O3 -march=native -ffast-math (C++ nbody), RUSTFLAGS=-C target-cpu=native (Rust), no LTO; runs use numactl --interleave=all and OMP_PROC_BIND=spread; compiler names and versions not stated for the tables |
| **Adoption** | 379 stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/ashvardanian/fork_union) · [benchmark](https://github.com/ashvardanian/fork_union) |

## Verdict

The author's N-body benchmark (N=512, all logical cores, 30 s fixed window, static/dynamic) shows ForkUnion C++ at 54/86 us per step against OpenMP 115/226, Rayon 483/739 and Taskflow 666/694 on 128x Intel SPR. Connected components on a \~27M-edge graph reach 192.6/77.6 GTEPS against OpenMP 53.9/0.4 on 192x Graviton 5. Builds use -O3 and target-cpu=native with no LTO (plus -ffast-math in the C++ binary); CPU SKUs and compiler versions are not named. Taskflow graphs are built once and re-run, so its numbers are dispatch cost, not graph construction.

## Use it when

- Frequent, short data-parallel loops or bulk-synchronous rounds where fork-join dispatch overhead is a large share of the time (for example N-body at N=512: 40-54 us per step on 128x Intel SPR against OpenMP 115 and Taskflow 666).
- Many-core and multi-socket servers (128-192 threads) where Rayon and Taskflow dispatch collapses and you want NUMA-pinned threads plus node-local memory.
- Fine-grained dynamic scheduling with very cheap items (one-vertex claims), where OpenMP schedule(dynamic,1) and Taskflow's DynamicPartitioner fell to 0.4 GTEPS in the author's connected-components run.
- Mixed-language codebases that need the same pool from C++, C99, Rust (forkunion crate) and Zig.
- Memory-constrained or no-exceptions environments: no allocations or exceptions on the dispatch path.

## Skip it when

- Task graphs, futures, async I/O, work that outlives its scope, or nested/recursive parallelism: banned by design; the README itself points to Taskflow, Tokio or oneTBB for those.
- Small desktop machines where the gap narrows or flips: on 24x Intel RPL Windows, Rayon roughly ties ForkUnion C++ in N-body (151/151 vs 148/143 us) and OpenMP static beats it in connected components (11.4 vs 10.0 GTEPS).
- Rayon-style parallel iterators and reductions outside Rust: that layer is Rust-only; C++ gets only the for_\* primitives.
- When you need independently reproduced numbers: all tables are author-run, and CPU SKUs and compiler versions are not named.
- Shared or oversubscribed machines where spin-waiting workers are unwelcome; timed hardware waits help, but the design is spin-based.

## How it is fast

Workers stay resident and are woken by bumping a shared fork_generation counter; the whole pool synchronizes on three atomics (stop, fork_generation, threads_to_sync) plus one private claim cursor per worker. The hot path makes no heap allocations, no syscalls and no CAS: dynamic scheduling uses per-worker fetch_add cursors that neighbours drain in coprime order, instead of Chase-Lev CAS deques. Hot variables are padded against false sharing (128-byte padding for the adjacent-line prefetcher is discussed). Idle workers wait with PAUSE/YIELD or with hardware timed waits (x86 UMONITOR/UMWAIT/TPAUSE, Arm WFET, RISC-V Zawrs) rather than futexes.

## Compared with alternatives

Pick it over citor, Weave or a work-stealing pool such as Thiefpool or ThunderBolt-HT when the workload is flat data-parallel loops on many-core or NUMA hardware and dispatch latency dominates; pick citor, Nowa, chili or Spice for recursive fork-join or task parallelism, which ForkUnion does not support.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the C++ header (NUMA and huge pages through kernel interfaces, no libnuma); the C API links a prebuilt static or shared library that needs the C++ runtime |
| **Minimum toolchain** | C++17 for the header (C++20 adds concepts and an atomic_ref waiter); C99 for the C ABI; CMake 3.21, Rust 1.84, Zig 0.16 |
| **Platforms** | Linux, FreeBSD, Windows, macOS, Android, iOS; x86-64, AArch64, RISC-V (big-endian 32-bit tested per README); NUMA memory placement only on Linux, FreeBSD and Windows |
| **Thread safety** | Dispatch is single-producer: a fork may be issued from one thread at a time, and terminate/try_spawn must not overlap running work; callbacks are noexcept. |
| **Drop-in for the baseline** | partial — it replaces `#pragma omp parallel for` loops and Taskflow for_each-style loops with an equivalent call, but through its own API and without nested parallelism or task graphs |

## Gotchas

- On caller_inclusive_k pools the calling thread owes one slice that runs only inside unsafe_join or the guard's join/destructor, so polling is_complete alone never completes; on exclusive pools work starts when the guard is constructed.
- The pool object should be declared alignas(fu::default_alignment_k), as in the README example, to keep its atomics off shared cache lines.
- The C++ benchmark binary adds -ffast-math (the Rust build cannot), and published runs use numactl --interleave=all with OMP_PROC_BIND=spread OMP_PLACES=cores; the record's '-O3 -march=native' omits these. The kernels are hand-reassociated so the language columns stay comparable.
- The repo is now published as ashvardanian/ForkUnion (v3.0.4, crate 'forkunion'); older docs and links use fork_union.

## Caveats and trade-offs

Author-run numbers. CPUs are given as families and core counts, not SKUs, and compiler versions are not stated. The latency win is dispatch overhead; on 24x Intel RPL Windows, OpenMP static beats ForkUnion C++ in connected components (11.4 vs 10.0 GTEPS) and Rayon roughly ties ForkUnion C++ in n-body (151/151 vs 148/143). The 3-6x OpenMP headline is the upper range: the C++ static cell on 128x SPR is 115 vs 54 us (about 2.1x, derived from page data).

Fork-join data-parallel loops, not general dynamic work stealing; spin-based workers with NUMA-aware compute domains; no allocations, syscalls or CAS on hot path. Targets OpenMP-style parallel-for rather than recursive tasks.

## Maintenance

Actively maintained (last commit 2026-10-02, v3.0.4), Apache-2.0, used by USearch, NumKong and StringZilla; header-only and easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification A, tier now C.
- **Tier reason:** Benchmark code is public (scripts/nbody.cpp, scripts/propagation.\*) and the flags are stated (-O3 -march=native, target-cpu=native, no LTO), but the README names no compiler or version for the result tables and gives the CPUs only as families ('128x Intel SPR', '24x Intel RPL'), not models. That makes these first-party numbers with partial methodology, so tier C, not A.
- **Verifier notes:** README tables match the record's numbers. The tier falls to C because compiler names, versions and CPU models are missing. Apache-2.0 license and 379 stars confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ashvardanian/fork_union>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/README.md>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/scripts/nbody.cpp>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/README.md>
  - <https://raw.githubusercontent.com/ashvardanian/fork_union/HEAD/scripts/nbody.cpp>
  - <https://github.com/ashvardanian/fork_union/issues?q=is%3Aissue+label%3Abug>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/ashvardanian/fork_union`) · [data/wave11/enrich/raw/github_com_ashvardanian_fork_union.json](../../../data/wave11/enrich/raw/github_com_ashvardanian_fork_union.json) (enrichment confidence 0.75)

</details>
