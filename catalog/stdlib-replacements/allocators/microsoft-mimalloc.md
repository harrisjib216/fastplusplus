# mimalloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> General-purpose malloc drop-in replacement using sharded per-thread free lists; beats jemalloc/tcmalloc on multi-threaded workloads.

| | |
|---|---|
| **Beats** | jemalloc |
| **Claimed result** | sh6bench: mimalloc "more than 2.5x faster than jemalloc"; larsonN: "quite a bit faster than tcmalloc and jemalloc"; cfrac: "just a tad faster than tcmalloc and jemalloc"; leanN (Lean compiling its own standard library): "a 13% speedup over tcmalloc", which the README extrapolates to "1.6x faster than tcmalloc" if Lean spends 20% of its time in the allocator; xmalloc-testN: mimalloc "outperforms others by a very large margin"; sh8bench: adding object migration makes tcmalloc "10x slower than before" (a tcmalloc-vs-itself remark, not a mimalloc ratio) |
| **Workload** | mimalloc-bench suite (cfrac, leanN Lean theorem-prover self-build, redis, larsonN, mstressN, rptestN, alloc-test, sh6bench/sh8bench, xmalloc-testN, cache-scratch) run on a 16-core AMD 5950x and a 36-core (2x18) Intel Xeon c5.18xlarge |
| **Metric** | throughput |
| **Hardware** | 16-core AMD Ryzen 5950x (Zen3) 3.4GHz/4.9GHz boost, 32GiB 3600MHz RAM, Ubuntu 20.04, glibc 2.31; also reported on a 36-core 2x18-core Intel Xeon Cascade Lake (AWS c5.18xlarge), 144GiB RAM |
| **Compiler and flags** | GCC 9.3.0 (AMD 5950x run) / Clang 10.0.0 (Xeon c5.18xlarge run); the companion mimalloc-bench build scripts (github.com/daanx/mimalloc-bench, build-bench-env.sh) use CFLAGS/CXXFLAGS='-march=native' plus per-allocator -O2/-O3 |
| **Adoption** | 13.4k stars; used in Azure, Bing, Unreal Engine, Death Stranding PC, SPAdes |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/microsoft/mimalloc) · [benchmark](https://github.com/microsoft/mimalloc#performance) |

## Verdict

mimalloc's own README Performance section runs the public mimalloc-bench suite (glibc 2.31, GCC 9.3.0/Clang 10.0.0, on a 16-core AMD 5950x and a 36-core Xeon c5.18xlarge) and states in prose that mimalloc is 'more than 2.5x faster than jemalloc' (5.2.1) on sh6bench, 'quite a bit faster' than jemalloc/tcmalloc on larsonN, and 13% faster than tcmalloc (2.8.1) on the leanN Lean self-build workload.

## Use it when

- Multi-threaded server workloads with producer/consumer or cross-thread free patterns (allocate on one thread, free on another)
- Want a small (\~10k LOC), portable allocator to vendor/port to less-common platforms (Haiku, WASM, various BSDs, MUSL, riscV)
- Want built-in, production-usable overflow/double-free detection (guarded mode with sampling, or full secure mode) without swapping allocators for debug builds
- C++ code that can override global new/delete and wants first-class heaps for bulk-allocate/bulk-destroy object arenas
- Long-running services where reduced steady-state RSS from eager purge matters more than avoiding purge syscall overhead

## Skip it when

- Need mature allocation-profiling/heap-diff tooling; mimalloc offers stats/ETW/verbose output, not an equivalent to jemalloc's jeprof
- Single-threaded, allocation-light workloads (README's own cfrac/redis benchmarks show mimalloc roughly ties jemalloc/tcmalloc there)
- Code that forks() while using large/huge OS pages -- copy-on-write duplicates the whole 1GiB/2MiB page on first write post-fork, which can spike memory
- Statically overriding malloc in a codebase you don't fully control -- README warns mixing pointers across heaps can occur unless every source uses mimalloc-override.h
- Teams that specifically need decades of hardening at extreme single-vendor scale (e.g. Google-internal), where gperftools/Google TCMalloc has the longer track record

## How it is fast

Each \~64KiB 'mimalloc page' (one size class) uses free-list sharding, and within a page mimalloc keeps two lists per size class: a thread-local free list for same-thread frees and a separate lock-free 'remote free' list for cross-thread frees, so freeing from another thread is a single CAS with no coordination -- this is what wins on cross-thread-free benchmarks like larsonN and xmalloc-testN. It also does eager page purging (decommit/reset OS pages once a shard empties) to cut RSS, and v3 adds true first-class heaps that can allocate from any thread and be destroyed in bulk instead of freeing objects individually.

## Compared with alternatives

Pick mimalloc over jemalloc when you want a much smaller (\~10k LOC), easily-vendored codebase with broader OS/arch ports (Haiku, WASM, BSD, MUSL, riscV) and built-in guard-page/secure modes, at the cost of jemalloc's more mature profiling tooling. Pick it over snmalloc when you need that platform breadth more than snmalloc's extreme many-thread producer/consumer throughput, and over gperftools/Google TCMalloc when first-class heaps and lower baseline memory overhead matter more than TCMalloc's longer production track record at large single-vendor scale.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib \| source-drop (single src/static.c + mimalloc.o) |
| **Dependencies** | none (uses only mmap/VirtualAlloc) |
| **Minimum toolchain** | CMake &gt;=3.18 to build the library (CMAKE_C_STANDARD 11 / CXX_STANDARD 17 internally); consumers just need a C or C++ compiler and mimalloc.h |
| **Platforms** | x86-64 (opts to -march=haswell/AVX2 by default), arm64 (armv8.1, armv8.3 on Apple silicon), riscV (rv64gcb_zacas); Windows (incl. ARM64EC, UWP, Xbox), Linux, macOS, various BSDs, Haiku, MUSL, WASM |
| **Thread safety** | thread-safe; per-page free lists are split into a thread-local free list and a separate cross-thread 'remote free' list resolved with a single CAS, so concurrent free from other threads needs no locking |
| **Drop-in for the baseline** | yes |

## Gotchas

- Static override via mimalloc-override.h only works reliably if ALL sources in the program are rebuilt with it; otherwise pointers from different heaps can mix and corrupt memory
- mimalloc-new-delete.h (C++ new/delete override) must be included in exactly one source file, not every file
- -DMI_SECURE=FULL (guard page after every 64KiB page) is explicitly 'not recommended in general' -- costs more and can hit Linux's max VMA count on large heaps
- Large/huge OS pages plus fork(): copy-on-write duplicates the entire 1GiB/2MiB page on first write in the child, which can balloon memory use

## Caveats and trade-offs

The chart data (SVG bar charts in doc/bench-2021/) also includes glibc 2.31 as a tested allocator and mimalloc leads it in almost every benchmark, but the exact glibc-specific numbers are only rendered as vector-graphic bars, not extractable as page text, so per the hard rule that every claimed_speedup number must appear as text on the page, glibc is not used as the cited baseline here -- jemalloc/tcmalloc are used since those specific ratios are quoted in prose. README itself flags the 2021-01-30 data as dated: "many of these allocators have improved over time as well. YMMV."

secure-mode build (guard pages, encrypted free lists) costs \~10% avg perf penalty; eager purge/decommit trades some memory-release syscall overhead for lower steady-state RSS; not every benchmark favors it (cfrac/redis roughly tie jemalloc/tcmalloc)

## Maintenance

Actively maintained: latest release v3.5.3 on 2026-09-16 with commits through 2026-09-17; MIT licensed and small enough to vendor as a single source file (src/static.c), consistent with its 'copyable' usability rating.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification A, tier now A.
- **Tier reason:** README Performance section runs the public, automated mimalloc-bench suite (github.com/daanx/mimalloc-bench: bench.sh, build-bench-env.sh, which sets CFLAGS/CXXFLAGS='-march=native') against jemalloc 5.2.1, tcmalloc 2.8.1 and glibc 2.31, stating GCC 9.3.0 / Clang 10.0.0 and CPU models (AMD 5950x, Xeon Cascade Lake c5.18xlarge). The '2.5x faster than jemalloc' sh6bench figure is verbatim prose.
- **Verifier notes:** Numbers verified verbatim in README (Performance section, 'Last update: 2021-01-30', with a 2026-09-01 'YMMV' note). Removed the unsupported '(mimalloc does not regress)' parenthetical and added the larsonN/cfrac prose; only the sh6bench ratio is a numeric claim vs the jemalloc baseline, leanN is vs tcmalloc. The flags come from the current mimalloc-bench build script, which may differ from the one used in 2021. SVG charts are glyph paths with no extractable glibc numbers, so the caveat is accurate.
- **Fields the verifier corrected:** `claimed_speedup`
- **Shortcomings recorded by:** developer source's allocator selection put mimalloc at about 1.5x glibc malloc on allocate/free churn and about 6x on bulk free (approximate figures, no per-row table published), the same order as jemalloc's measured 2.71x via LD_PRELOAD on the committed churn benchmark. It was not vendored because swapping the allocator with LD_PRELOAD gets that gain without a source dependency. (developer source, private repo; selection measurement cited in docs/allocators.md and results/fastest.json row allocator_churn, run 2026-09-03-third-party)
- **Pages the verifier opened:**
  - <https://github.com/microsoft/mimalloc#performance>
  - <https://github.com/microsoft/mimalloc>
  - <https://github.com/microsoft/mimalloc/blob/main3/doc/bench-2021/bench-amd5950x-2021-01-30-a.svg>
  - <https://github.com/daanx/mimalloc-bench>
  - <https://github.com/daanx/mimalloc-bench/blob/master/build-bench-env.sh>
- **Sources the enricher read:**
  - <https://github.com/microsoft/mimalloc>
  - <https://github.com/microsoft/mimalloc#performance>
  - <https://github.com/microsoft/mimalloc/blob/main/CMakeLists.txt>
  - <https://github.com/microsoft/mimalloc/issues/1105>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/microsoft/mimalloc`) · [data/wave0-seed/enrich/raw/github_com_microsoft_mimalloc.json](../../../data/wave0-seed/enrich/raw/github_com_microsoft_mimalloc.json) (enrichment confidence 0.8)

</details>
