# ThunderBolt-HT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> C++20 dependency-aware work-stealing task runtime that measures \~1.5x lower per-task cost than Taskflow 3.7 on a 4-core laptop.

| | |
|---|---|
| **Beats** | Taskflow v3.7.0 (explicit tasks and for_each) |
| **Claimed result** | Per-task cost 286 ns vs Taskflow explicit tasks 451 ns (about 1.6x, derived from page data); under shuffled leg order the README states \~1.5x (237-261 ns vs Taskflow 355-390 ns across two runs); earlier fixed-order run 597-633 ns vs 643 ns. Partitioned parallel_for beat taskflow_for_each at every task count, 7-19% faster in two runs. Stress frame graph after the per-stage claiming fix: 0.162 vs 0.195 ms/tick (README: \~1.19x faster than Taskflow); full_mixed 0.102 ms/tick, stated 1.27x faster. |
| **Workload** | Per-task scheduling cost via granularity regression (fixed work split into more tasks), partitioned parallel_for throughput, and a game-simulation frame graph, 20 interleaved repetitions median. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-10310U (4 cores, 8 threads, 15 W laptop CPU), per docs/RESULTS.md |
| **Compiler and flags** | MSVC 14.51.36231, Release, /fp:precise; full flags in thunderbolt/cmake/ThunderboltCompilerFlags.cmake |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/ankitlinkesh/ThunderBolt-HT) · [benchmark](https://github.com/ankitlinkesh/ThunderBolt-HT) |

## Verdict

On an Intel Core i5-10310U (4 cores/8 threads, 15 W, \~1600 MHz sustained) with MSVC 14.51 C++20 Release, the project's own interleaved, median-of-20 harness measured 286 ns per task against 451 ns for Taskflow 3.7.0 explicit tasks (237-261 vs 355-390 ns under shuffled leg order), a partitioned parallel_for 1-19% faster than taskflow_for_each depending on task count, and a 10-stage simulation frame graph at 0.162 vs 0.195 ms/tick. The frame-graph win came from coarsening the engine's own task submission, and StandardRuntime reaches 0.196 ms/tick on the same scene; after chain fusion the margin over Taskflow is about 1.15x.

## Use it when

- Frame-graph style workloads (game or simulation ticks) with explicit inter-stage dependencies, priorities and many small tasks per frame on a desktop or laptop CPU with 8 or fewer hardware threads.
- You want explicit-task fork-join where per-task submission cost matters (thousands of tasks per call), and a measured \~1.5x lower marginal per-task cost than Taskflow explicit tasks is relevant.
- Element-wise parallel loops (out[i] depends only on i) where a chunk-claiming parallel_for with a caller-chosen grain is enough.
- Research or teaching: the repo documents its A/B harness (interleaved, shuffled leg order, median and IQR), its refuted hypotheses and its own measurement bugs, so it can serve as a reference for benchmarking schedulers.

## Skip it when

- Production use where maturity matters: 0 stars, version 0.1.0, written and measured largely by an AI agent per its README, and TSan found three data races in the dispatch path only recently (fixed).
- Reductions or other order-sensitive combines: parallel_for has no reduce, and the docs say a reduction over dynamically claimed chunks is unsafe under its determinism rule.
- Many-core servers or NUMA machines: every measurement stops at 8 workers on one 4-core/8-thread laptop part; scaling beyond that is not measured.
- When you need TBB, OpenMP or Rayon comparisons: oneTBB was deliberately never benchmarked, only Taskflow 3.7.0 and the project's own StandardRuntime.
- Ecosystem needs (concurrent containers, flow graphs, GPU tasks, task cancellation): not documented as features.

## How it is fast

Per-worker Arora-Blumofe-Plaxton (ABP) deques, one per priority, with randomized (xorshift64) victim selection and batched draining of a global injection queue. Most of the measured per-task gain came from removing cache-line contention: hot global counters were sharded and padded, which roughly halved per-task cost. A per-thread task-slot cache (64 slots per lock acquisition) and in-place construction of the task body in its pool slot cut it further. parallel_for spawns at most one task per worker, and each task claims grain-sized chunks from a shared atomic cursor (fetch_add) instead of submitting one task per chunk.

## Compared with alternatives

Pick it over nexus or dpuyda/scheduling when you want dependency edges, priority deques and a documented, reproducible A/B harness in a CMake package (find_package, vcpkg overlay, Conan); pick Fork Union for minimum-overhead parallel-for dispatch, or citor or Taskflow itself when you need results on many-core hardware.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at build time beyond Threads (Taskflow 3.7.0 is fetched only for benchmark targets with -DTHUNDERBOLT_REFERENCE_RUNTIMES=ON) |
| **Minimum toolchain** | C++20 (concepts in public headers), CMake 3.25+; MSVC is the reference toolchain, GCC and Clang presets exist for Linux |
| **Platforms** | Windows x64 (reference, SSE2 baseline, no /arch:AVX2) and Linux with GCC or Clang (CI on both); other platforms not documented |
| **Thread safety** | submit() is documented thread-safe and callable from inside a running task; calling wait_all() from inside a task can never return (listed in the project's own defect table). |
| **Drop-in for the baseline** | no |

## Gotchas

- Do not call wait_all() from inside a task: the project lists this as a case that never returns.
- parallel_for grain is a caller decision with no automatic selection; grain=1 lost to Taskflow's for_each in the project's own test because every claim paid a contended fetch_add.
- Externally submitted tasks go through a locked global injection queue and cost roughly 2x more per task than tasks spawned from inside a root task; the headline per-task numbers use the fork-join submission mode.
- Some result files in docs/results predate the shuffled-leg-order harness fix and were taken with fixed leg order, which the README says biased readings (Taskflow explicit read 836 vs 319 ns depending on its predecessor leg).

## Caveats and trade-offs

Baseline is Taskflow, not TBB, OpenMP or Rayon. Laptop CPU model unstated (4-core/8-thread 15 W). Self-reported, README only; result JSONs in docs/results not opened. README itself notes a fixed-leg-order harness flaw (Taskflow explicit read 836 vs 319 ns depending on predecessor) and that result files in docs/results predating the fix used fixed order. The earlier 'stress 0.195 vs 0.206, no change' line is superseded by the later frame-graph fix (0.162 vs 0.195); the frame-graph win comes from coarser tasks per stage in shared engine code, and StandardRuntime gets 0.196 on the same scene. 0 stars; README says some runs were done 'by the agent that built them' (agent-built code and measurements).

Dependency-aware task runtime with priority deques; mobile-class hardware with clock drift, authors use interleaved A/B.

## Maintenance

Very active (last commit 2026-09-30) single-author, agent-built Apache-2.0 project at version 0.1.0 with CI on Windows and Linux; small enough to vendor, but treat it as experimental.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now A.
- **Tier reason:** README reports first-party interleaved A/B runs against Taskflow v3.7.0 (granularity regression, partitioned parallel_for, stress frame graph) with benchmark code in the repo, but the CPU model is not named (only a 4-core/8-thread 15 W laptop part), so it falls short of A.
- **Retiered** C to A: Enricher read docs/RESULTS.md: it names the CPU (Intel Core i5-10310U) and the toolchain (MSVC 14.51.36231, /fp:precise), the flags are in thunderbolt/cmake/ThunderboltCompilerFlags.cmake and the harness is public, so the C-to-A rule (code, compiler, flags, CPU model all public) holds. The project itself fixed an earlier Taskflow timed-region bias (2.4x down to 1.44x); the frame-graph margin over Taskflow after chain fusion is about 1.15x.
- **Verifier notes:** Metadata checked on github.com: Apache-2.0, not a fork, 0 stars, 53 commits, last commit 2026-09-30. Claim corrected to the README's latest numbers; tier C stands.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`, `hardware`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/ankitlinkesh/ThunderBolt-HT/HEAD/README.md>
  - <https://github.com/ankitlinkesh/ThunderBolt-HT>
  - <https://github.com/ankitlinkesh/ThunderBolt-HT/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ankitlinkesh/ThunderBolt-HT/HEAD/README.md>
  - <https://raw.githubusercontent.com/ankitlinkesh/ThunderBolt-HT/HEAD/docs/RESULTS.md>
  - <https://raw.githubusercontent.com/ankitlinkesh/ThunderBolt-HT/HEAD/thunderbolt/api/ITaskRuntime.hpp>
  - <https://raw.githubusercontent.com/ankitlinkesh/ThunderBolt-HT/HEAD/thunderbolt/runtime/ThunderboltRuntime.hpp>
  - <https://raw.githubusercontent.com/ankitlinkesh/ThunderBolt-HT/HEAD/thunderbolt/CMakeLists.txt>
  - <https://raw.githubusercontent.com/ankitlinkesh/ThunderBolt-HT/HEAD/thunderbolt/cmake/ThunderboltCompilerFlags.cmake>
  - <https://raw.githubusercontent.com/ankitlinkesh/ThunderBolt-HT/HEAD/CMakePresets.json>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/ankitlinkesh/thunderbolt-ht`) · [data/wave11/enrich/raw/github_com_ankitlinkesh_thunderbolt_ht.json](../../../data/wave11/enrich/raw/github_com_ankitlinkesh_thunderbolt_ht.json) (enrichment confidence 0.65)

</details>
