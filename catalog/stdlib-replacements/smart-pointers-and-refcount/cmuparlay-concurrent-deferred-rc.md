# CDRC atomic_weak_ptr (concurrent_deferred_rc)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Smart pointers and reference counting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only C++20 lock-free atomic weak/shared pointers, beating a commercial atomic&lt;weak_ptr&gt; implementation under contention.

| | |
|---|---|
| **Beats** | just::thread's atomic&lt;weak_ptr&gt; (commercial third-party implementation of the C++20 std::atomic&lt;std::weak_ptr&gt; interface) |
| **Claimed result** | CDRC atomic weak pointers vs just::thread: 4.2x faster at P=8 and 10x faster at P=192 (paper Sec. 5.2). At P=1 (off-plot), the paper says the hand-tuned 'original' manual-reclamation queue is 4.5x faster than CDRC and 67x faster than just::thread, which puts CDRC \~15x ahead of just::thread at P=1 (derived from page data: 67/4.5). Versus the manual original, CDRC is 4.5x slower at P=1, 19% slower at P=8, and 33% slower at P=192. |
| **Workload** | Ramalethe & Correia lock-free concurrent doubly-linked queue using atomic weak back-pointers; P threads repeatedly pop-then-reinsert an element, P = 1 to 192, on a 4-socket 72-core machine |
| **Metric** | throughput |
| **Hardware** | 4-socket 72-core machine, 4x Intel Xeon E7-8867 v4 @ 2.4GHz, 2-way hyperthreading, 45MB L3 cache, 1TB RAM |
| **Compiler and flags** | GCC 9.2.1, -O3 |
| **Adoption** | 174 stars |
| **Last commit** | 2022-07-03 |
| **Links** | [repository](https://github.com/cmuparlay/concurrent_deferred_rc) · [benchmark](https://arxiv.org/pdf/2204.05985) |

## Verdict

PLDI '22 paper Sec. 5.2/Fig. 12: on a 4-socket 72-core machine (4x Xeon E7-8867 v4, GCC 9.2.1 -O3), in a lock-free doubly-linked queue benchmark using atomic weak back-pointers (pop-then-reinsert, P=1-192 threads), CDRC's atomic_weak_ptr beat just::thread's atomic&lt;weak_ptr&gt; by 4.2x at P=8 and 10x at P=192, with CDRC's margin over just::thread at P=1 around 15x (derived, not the paper's often-cited 67x figure, which is the hand-tuned manual-reclamation baseline vs just::thread). CDRC itself trails that manual-reclamation queue by 4.5x at P=1, 19% at P=8, and 33% at P=192.

## Use it when

- Lock-free concurrent data structures (queues, stacks, structures with back-pointers) that need atomic weak pointers, at medium-to-high thread counts where the paper shows the advantage growing (4.2x at P=8, 10x at P=192 on a 72-core/4-socket box)
- You are currently bottlenecked on a commercial or hand-rolled atomic&lt;weak_ptr&gt;-style implementation (e.g. just::thread) under contention
- You can target a C++20-concepts-capable compiler (GCC 9+, Clang 13+, AppleClang, or MSVC 19, all green in CI) and restructure pointer usage around cdrc's own types
- You want to tune the throughput/memory tradeoff by swapping reclamation backends (hazard pointers vs EBR vs IBR vs Hyaline) for the same pointer API
- A research or experimental system where vendoring a small, unmaintained, MIT header-only library is acceptable

## Skip it when

- You need a true drop-in replacement for std::shared_ptr/std::weak_ptr/std::atomic&lt;weak_ptr&gt; with no code changes — cdrc's types are similarly shaped but distinct and require rewriting the pointer hierarchy
- Single-threaded or low-contention (P=1) hot paths: the paper's own data has CDRC 4.5x slower than a hand-tuned manual-reclamation queue at P=1, and non-default backends add explicit per-scope guard overhead
- Memory-constrained environments — EBR and Hyaline backends trade higher memory for throughput, and the library documents higher memory use than manual reclamation when oversubscribed
- You need dynamic_cast on managed pointers or easy debuggability of the managed object's storage — issue #6 (dynamic cast) is open, and issues #3/#4 flag the type-erased char-array storage as hard to inspect
- You need active upstream support — no commits since 2022-07-03, 5 open issues, 2 open unmerged PRs

## How it is fast

Uses 'concurrent deferred reference counting': reference-count updates are decoupled from object reclamation, which is handed to a pluggable safe-memory-reclamation backend (hazard pointers by default, or epoch-based/interval-based/Hyaline reclamation) bounding per-operation reclamation overhead. The snapshot_ptr/weak_snapshot_ptr types read the current object without incrementing the shared reference count, cutting atomic RMW traffic on hot traversal paths versus always producing a fully counted handle.

## Compared with alternatives

The only same-category sibling that is actually concurrency-focused is observable_unique_ptr/observer_ptr (oup), which targets single-threaded non-owning observers, not atomic weak pointers. Pick CDRC over oup when you need thread-safe, lock-free atomic&lt;weak_ptr&gt;-style pointers for lock-free concurrent data structures; pick oup instead for single-threaded ownership/observer tracking where a full shared_ptr/weak_ptr pair is overkill.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the library itself; benchmarks additionally need CMake 3.5+, Boost (program_options), hwloc, jemalloc, Python3+Matplotlib, and optionally Folly or just::thread |
| **Minimum toolchain** | C++20 (uses concepts); CI builds and tests pass on GCC 9, GCC 11, Clang 13, AppleClang, and MSVC 19 |
| **Platforms** | Linux, macOS, Windows for the library (all three run in CI); benchmarks are Linux-only (require NUMA policy support) |
| **Thread safety** | atomic_rc_ptr/atomic_weak_ptr are lock-free (is_always_lock_free() == true) and safe for concurrent load/store/CAS; rc_ptr/weak_ptr are safe to read/copy concurrently as long as no thread races a writer; snapshot_ptr/weak_snapshot_ptr are for single-thread-local use only and must not outlive the guard (for non-default backends) that created them |
| **Drop-in for the baseline** | partial — explain: operation shapes (load/store/compare_and_swap/compare_exchange_weak) match std::atomic&lt;weak_ptr&gt;-style APIs like just::thread's, but adopting it means switching the whole pointer hierarchy to cdrc::rc_ptr/atomic_rc_ptr/weak_ptr, and non-default reclamation backends require wrapping accesses in explicit guard objects |

## Gotchas

- Default backend is hazard pointers (moderate throughput, low memory); switching to EBR or Hyaline for higher throughput requires wrapping every potentially concurrent access in an epoch_guard/hyaline_guard, and holding a guard too long delays reclamation
- atomic_rc_ptr and atomic_weak_ptr have deleted copy and move constructors/assignment — they must be used in place (e.g. as class members), not stored by value in containers
- Internal counted-object storage is a raw char array (type-erased); two long-open issues (#3 'getValue' typo, #4 debuggability) flag this as awkward to inspect in a debugger
- dynamic_cast on managed pointers is not supported and is an open, unresolved request (issue #6) as of the last commit

## Caveats and trade-offs

The paper's 67x figure at P=1 is the manual 'original' implementation vs just::thread, not CDRC vs just::thread; CDRC's own P=1 margin is \~15x (derived). The baseline is just::thread, a commercial library of atomic shared and weak pointers, not libstdc++/libc++/MSVC STL atomic&lt;weak_ptr&gt;. The paper's separate 2x-3x throughput claim is against earlier concurrent reference-counting implementations, not std::shared_ptr. The last commit on the default branch is 2022-07-03 (the repo shows a push on 2024-02-18).

Requires a C++20-concepts-capable compiler; full benchmark reproduction needs jemalloc + NUMA-aware setup; library is research-grade (from the CDRC/acquire-retire papers), not a drop-in std::shared_ptr replacement, and uses more memory than manual reclamation in oversubscribed scenarios.

## Maintenance

Abandoned: no commits since 2022-07-03 despite a later recorded repo push (no new commits found); MIT-licensed, small and header-only enough to vendor, and CI still builds/tests green on GCC 9/11, Clang 13, AppleClang, and MSVC 19, but 5 issues and 2 PRs have sat open since 2022.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now A.
- **Tier reason:** PLDI '22 paper, Sec. 5.2 and Fig. 12. It states GCC 9.2.1 -O3, 4x Intel Xeon E7-8867 v4, jemalloc, and numactl -i all. The benchmark code is public in the repo (benchmarks/bench_queue.cpp, which has the weak_ptr_queue, jss_queue, and CRDoubleLinkQueue variants). The tier stays A; the verdict is downgrade only because the claim was overstated.
- **Verifier notes:** Downgrade because the record credited CDRC with the paper's 67x figure, which belongs to the manual baseline. Its claim that CDRC is 19-33% slower 'over the same range' was also wrong at P=1 (4.5x slower there). Tier A still holds: PLDI '22 paper, full setup stated, benchmark code in the repo. Metadata checks out: MIT, 174 stars, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2204.05985>
  - <https://github.com/cmuparlay/concurrent_deferred_rc>
  - <https://github.com/cmuparlay/concurrent_deferred_rc/blob/master/benchmarks/README.md>
  - <https://github.com/cmuparlay/concurrent_deferred_rc/blob/master/benchmarks/bench_queue.cpp>
- **Sources the enricher read:**
  - <https://github.com/cmuparlay/concurrent_deferred_rc>
  - <https://github.com/cmuparlay/concurrent_deferred_rc/blob/master/README.md>
  - <https://github.com/cmuparlay/concurrent_deferred_rc/blob/master/benchmarks/README.md>
  - <https://github.com/cmuparlay/concurrent_deferred_rc/blob/master/include/cdrc/atomic_weak_ptr.h>
  - <https://github.com/cmuparlay/concurrent_deferred_rc/blob/master/.github/workflows/build.yml>
  - <https://github.com/cmuparlay/concurrent_deferred_rc/blob/master/LICENSE>
  - <https://github.com/cmuparlay/concurrent_deferred_rc/issues>
  - <https://arxiv.org/pdf/2204.05985>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/cmuparlay/concurrent_deferred_rc`) · [data/wave1/enrich/raw/github_com_cmuparlay_concurrent_deferred_rc.json](../../../data/wave1/enrich/raw/github_com_cmuparlay_concurrent_deferred_rc.json) (enrichment confidence 0.85)

</details>
