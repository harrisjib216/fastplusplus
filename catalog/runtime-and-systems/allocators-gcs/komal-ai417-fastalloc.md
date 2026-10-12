# FastAlloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Thread-caching slab allocator (C++17) that beats glibc malloc on small mixed-size alloc/free pairs and returns memory aggressively.

| | |
|---|---|
| **Beats** | glibc malloc, jemalloc 5.3.0, mimalloc 2.1.7 |
| **Claimed result** | Wins 20/33 throughput cells vs glibc, 21/33 vs jemalloc, 12/33 vs mimalloc. Vs glibc: small-mixed 1.24-1.51x, random 1-4096 B up to 2.98x, ramp 1.54-1.94x. Large-block cycles 6.8-14.6x faster than jemalloc and 4.6-9.2x faster than mimalloc. Retains 16.0 MB vs 46.7/171.8/552.2 MB (glibc/jemalloc/mimalloc) after purging 1M objects. Loses on realloc-grow (0.28x vs glibc), thread-churn vs glibc (0.48-0.62x), bulk 1M alloc+free (0.63-0.77x vs glibc), churn vs jemalloc/mimalloc (0.55-0.75x) and ramp vs mimalloc (0.36-0.51x). |
| **Workload** | 11 Larson/mimalloc-bench style workloads x 1/2/4 threads, one allocator per process via LD_PRELOAD, median of 5, plus Google Benchmark micro suites and a 1M-object free-and-purge RSS test. |
| **Metric** | throughput |
| **Hardware** | 2-vCPU x86-64 VM (Intel Xeon, model not stated), 4 GB RAM, Debian 13; T=4 is 2x oversubscribed; glibc 2.41 |
| **Compiler and flags** | GCC 14.2, -O3 -march=native + LTO (CMake Release), CMake 4.4 |
| **Adoption** | 3 stars |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/Komal-ai417/FastAlloc) · [benchmark](https://github.com/Komal-ai417/FastAlloc/blob/main/docs/performance_report.md) |

## Verdict

The author's bench_suite (11 Larson/mimalloc-bench style workloads at 1, 2 and 4 threads, median of 5, one allocator per process, both sides called through the same function pointers) on a 2-vCPU Intel Xeon VM, GCC 14.2 -O3 -march=native + LTO, Debian 13, shows FastAlloc winning 20/33 cells vs glibc 2.41, 21/33 vs jemalloc 5.3.0 and 12/33 vs mimalloc 2.1.7. The report says contended cells are noisy and that the win/loss pattern, not the multipliers, should be quoted.

## Use it when

- C++ services dominated by small (16 B to 4 KB) mixed-size new/delete pairs, where the report shows 1.16-2.98x over glibc 2.41 at 1-4 threads
- Repeated large-block (8 KB+) alloc/free cycles, measured 4.6-14.6x faster than jemalloc 5.3.0 and mimalloc 2.1.7 because spans are recycled from a userspace cache
- Programs that need to hand memory back after a load spike and can call fast_alloc_purge() explicitly
- Code that wants an allocator-level debug mode (canaries, poisoning, leak dump) switchable at build time

## Skip it when

- realloc-heavy growth patterns: 0.28x vs glibc, which grows its heap top in place
- Steady constant-live-set churn or ramp-up against mimalloc or jemalloc (0.36-0.75x), and thread spawn/exit storms against glibc (0.48-0.62x)
- Bulk free of millions of objects at once: free phase 185 ms vs 64 ms for glibc on 1M objects
- When you need a process-wide malloc replacement for C libraries: there is no malloc/free interposition, only new/delete
- Production use that needs a track record: 3 stars, single author, no releases, all numbers from one 2-vCPU VM

## How it is fast

Per-thread TLS bins (pthread keys on Linux, FLS on Windows) serve 512 size classes in 16-byte steps up to 8 KB without locks; misses refill in adaptive batches (16 blocks, doubling) from 16 striped global arenas of 64-128 KB slabs. Cross-thread frees go to lock-free MPSC pending queues per arena, which later refills consume directly. Blocks above 8 KB use a best-fit, splitting page-span cache (2 MB per bin, 64 MB global) carved from 4 MB mappings released with madvise(MADV_DONTNEED), so large-block cycles stay in userspace; large realloc uses mremap.

## Compared with alternatives

Pick it over v8malloc or mem++ when you want a C++17 static library with an explicit purge call and a built-in debug mode, and your workload is small-object pairs or large-block cycles; for constant-live-set churn or ramp workloads mimalloc remains faster per this repo's own matrix, and fast-alloc (NotKeira) is the simpler choice if you only need fixed pools or stack arenas.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none for the library (Google Test and Google Benchmark are fetched via CMake FetchContent for tests and benchmarks only) |
| **Minimum toolchain** | C++17, CMake; tested with GCC 14.2, Clang and MSVC in CI |
| **Platforms** | Linux and Windows on x86-64 (span pool and mremap paths are Linux-only); other architectures not documented |
| **Thread safety** | Thread-safe; cross-thread free via lock-free MPSC queues, verified under ThreadSanitizer in CI per the README |
| **Drop-in for the baseline** | partial — global operator new/delete can be overridden with FAST_ALLOC_OVERRIDE_NEW (sized delete forwards to fast_free_sized), but malloc/free are not exported, so C callers need source changes to call FastAlloc::fast_malloc |

## Gotchas

- The memory-retention headline (16.0 MB vs 171.8/552.2 MB for jemalloc/mimalloc after purge) is not like-for-like: bench_suite.cpp calls fast_alloc_purge() for FastAlloc but only malloc_trim(0) for the LD_PRELOADed allocators, never jemalloc's arena purge mallctl or mi_collect, and measures immediately, before their decay timers run.
- Every small block carries a 16-byte header (USER_OFFSET = 16) and classes step by 16 B, so RSS/live was 1.08 vs glibc 0.78 in the report; calloc zeroes the whole rounded block (Calloc/10B 11.9x slower than glibc).
- Freeing a pointer FastAlloc did not allocate (for example memory from a C library's malloc) is undefined behaviour in release builds; only FASTALLOC_DEBUG detects it.
- The override covers plain and sized new/delete only; aligned (std::align_val_t) new/delete are not overridden and go to the system allocator.

## Known shortcomings

- Harness flaw: bench_suite.cpp run_overhead calls fast_alloc_purge() for FastAlloc but only malloc_trim(0) for the LD_PRELOADed jemalloc and mimalloc (no arena purge mallctl, no mi_collect) and measures right away, so '16.0 MB vs 171.8/552.2 MB retained after purge' is not like for like; the throughput cells are fair. Not a malloc drop-in: no malloc/free symbols exported, only a namespaced API plus an optional new/delete override (aligned new not covered); 16 B header per block.

## Caveats and trade-offs

First-party numbers on a 2-vCPU VM with CPU model missing, T=4 oversubscribed; the report itself warns contended cells are noisy and to quote the win/loss pattern, not individual multipliers. Does not beat mimalloc overall (12/33 cells). Raw results are gitignored, so only the summary report is public. Very new repo (3 stars, last commit 'Restore repository to a2a342b6 baseline' on 2026-10-02). In-process gbench ratios up to 50-285x are page-fault artifacts per the author.

Per-thread caches with 16 arenas; global new/delete override via macro; Windows and Linux; debug instrumentation mode.

## Maintenance

Active as of the 2026-10-02 commits (100 commits, last one 'Restore repository to a2a342b6 baseline'), MIT-licensed and small enough to vendor, but a 3-star single-author project with raw results gitignored.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Public harness (benchmarks/benchsuite/bench_compare.py, bench_suite) with GCC 14.2 -O3 -march=native + LTO stated in docs/performance_report.md, but the hardware is only '2 vCPU x86-64 VM (Intel Xeon)' with no CPU model, so it falls short of A; first-party, so C.
- **Verifier notes:** MIT LICENSE file confirmed. Numbers checked in docs/performance_report.md and README; they match the record apart from the large-block range split (jemalloc 6.8-14.6x, mimalloc 4.6-9.2x).
- **Fields the verifier corrected:** `benchmark_url`, `compiler_and_flags`, `hardware`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/Komal-ai417/FastAlloc>
  - <https://github.com/Komal-ai417/FastAlloc/blob/main/docs/performance_report.md>
  - <https://raw.githubusercontent.com/Komal-ai417/FastAlloc/HEAD/LICENSE>
  - <https://github.com/Komal-ai417/FastAlloc/commits>
- **Sources the enricher read:**
  - <https://github.com/Komal-ai417/FastAlloc>
  - <https://github.com/Komal-ai417/FastAlloc/commits/main>
  - <https://github.com/Komal-ai417/FastAlloc/tree/main/benchmarks/benchsuite>
  - <https://github.com/Komal-ai417/FastAlloc/tree/main/src>
  - <https://github.com/Komal-ai417/FastAlloc/tree/main/include>
  - <https://raw.githubusercontent.com/Komal-ai417/FastAlloc/HEAD/README.md>
  - <https://raw.githubusercontent.com/Komal-ai417/FastAlloc/HEAD/docs/performance_report.md>
  - <https://raw.githubusercontent.com/Komal-ai417/FastAlloc/HEAD/docs/api_reference.md>
  - <https://raw.githubusercontent.com/Komal-ai417/FastAlloc/HEAD/include/fast_alloc.h>
  - <https://raw.githubusercontent.com/Komal-ai417/FastAlloc/HEAD/src/fast_alloc.cpp>
  - <https://raw.githubusercontent.com/Komal-ai417/FastAlloc/HEAD/src/fast_alloc_config.h>
  - <https://raw.githubusercontent.com/Komal-ai417/FastAlloc/HEAD/src/tls_cache.cpp>
  - <https://raw.githubusercontent.com/Komal-ai417/FastAlloc/HEAD/src/global_heap.cpp>
  - <https://raw.githubusercontent.com/Komal-ai417/FastAlloc/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Komal-ai417/FastAlloc/HEAD/benchmarks/benchsuite/bench_suite.cpp>
  - <https://raw.githubusercontent.com/Komal-ai417/FastAlloc/HEAD/benchmarks/benchsuite/run_matrix.sh>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/komal-ai417/fastalloc`) · [data/wave11/enrich/raw/github_com_komal_ai417_fastalloc.json](../../../data/wave11/enrich/raw/github_com_komal_ai417_fastalloc.json) (enrichment confidence 0.75)

</details>
