# ltalloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Single-file source drop-in overriding operator new/delete; thread-local free lists speed up many small (&lt;256B) allocations vs CRT malloc.

| | |
|---|---|
| **Beats** | operator new/delete (CRT/C runtime malloc) |
| **Claimed result** | On Windows 10/i7-2600: \~2.6x faster than crt single-threaded (62,525,965 vs 23,853,865) and \~1.9x at 5 threads (27,333,887 vs 14,636,381) (derived from page data). On PS4: \~6.4x faster than crt single-threaded (28,571,429 vs 4,444,444) and \~44x at 4 threads (14,683,637 vs 332,095) (derived from page data). Units are not stated on the page (higher is better). |
| **Workload** | Same multi-threaded small-object alloc/dealloc stress test used in the smmalloc benchmark table (Windows/i7-2600 and PS4), comparing ltalloc's throughput against CRT malloc. |
| **Metric** | throughput |
| **Hardware** | Windows 10, Intel Core i7-2600; PlayStation 4 |
| **Adoption** | 174 stars |
| **Last commit** | 2026-04-10 |
| **Links** | [repository](https://github.com/r-lyeh-archived/ltalloc) · [benchmark](https://github.com/SergeyMakeev/smmalloc#performance) |

## Verdict

Third-party smmalloc README table (128-byte concurrent alloc/free stress test, compiler/flags/units unstated) shows ltalloc vs CRT malloc on Windows 10/i7-2600: \~62.5M vs \~23.9M ops at 1 thread (\~2.6x) and \~27.3M vs \~14.6M at 5 threads (\~1.9x); on PS4: \~28.6M vs \~4.4M at 1 thread (\~6.4x) and \~14.7M vs \~332K at 4 threads (\~44x). In that same table ltalloc trails rpmalloc, hoard, and smmalloc at every thread count. I confirmed these exact figures by reading the smmalloc README directly.

## Use it when

- Hot path is many small (&lt;256B) alloc/free calls, e.g. STL container churn, especially with a producer-consumer pattern where one thread allocates and another frees.
- You can add a single ltalloc.cc to the build and build with LTO (-flto/-ipo//GL) to get the compile-time size-class inlining benefit.
- You want a drop-in for global operator new/delete with no per-container allocator template changes.
- Target is Windows (MSVC) or Linux/macOS; ARM64/ARM64EC support was merged in April 2026 for those wanting arm64.
- You're fine manually reclaiming memory to the OS (via ltalloc_squeeze()) instead of relying on automatic trim.

## Skip it when

- You need memory returned to the OS automatically; small-block memory is only released when you explicitly call ltalloc_squeeze().
- You need allocator statistics/introspection - none is provided by design (no malloc_stats equivalent).
- Correctness matters more than raw throughput: open, unresolved issues report a segfault in ptrie_insert (#23), a realloc() hang/CPU-spin (#27), and chunk leaks (#30).
- You want an actively developed project: real bug-fix activity stopped in 2019; the only 2026 commit was an externally contributed ARM64 PR merge.
- Peak throughput vs. other allocators (not just CRT) matters: in the third-party smmalloc benchmark table, ltalloc trails smmalloc, rpmalloc, and hoard at both 1 and 5 threads on i7-2600.

## How it is fast

Each thread keeps a per-size-class free list (a TCMalloc-inspired thread cache) so alloc/free for blocks under 56KB is O(1) with, in the common case, a single conditional branch. Size-class selection is computed from constants only (no dynamic data), so with LTO/inlining enabled (-flto, /GL, -ipo) the compiler can inline the whole allocation path at the call site. Blocks are moved between the thread-local list and a shared central list in batches of up to 256 to bound cross-thread contention (at most one spin-lock per 256 ops), and chunks carry one 64-byte header per 64KB instead of a per-allocation header, cutting fragmentation.

## Compared with alternatives

Pick ltalloc over rpmalloc or smmalloc (same category, both also beat CRT malloc) only when you want the absolute smallest integration footprint - one .cc file, no build-system hookup - and can tolerate a project with no real bug-fix activity since 2019 and open segfault/hang reports; in the shared smmalloc benchmark table ltalloc is consistently slower than both rpmalloc and smmalloc, so neither is chosen for raw throughput.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (stdlib.h; optional &lt;new&gt;/&lt;limits&gt; only for the ltalloc.hpp STL-allocator wrapper) |
| **Minimum toolchain** | Compiles as C or C++ (no C++11 required); thread-local storage via compiler builtins (__thread / __declspec(thread)), not the C++11 thread_local keyword; LTO (-flto/-ipo//GL) recommended for full inlining benefit |
| **Platforms** | Windows (MSVC, AppVeyor CI) and Linux/macOS (Travis CI); ARM64/ARM64EC support merged April 2026; primarily x86/x86-64 |
| **Thread safety** | Almost lock-free per README: dedicated free list per thread per size class, at most one spin-lock per up to 256 alloc/free calls when refilling from the shared central list |
| **Drop-in for the baseline** | yes |

## Gotchas

- Full performance depends on LTO so the compiler can inline the compile-time size-class computation; without it you keep correctness but lose much of the speed edge.
- Memory for small blocks is never returned to the OS automatically; call ltalloc_squeeze() yourself (e.g. periodically from a background thread) to release it.
- No memory-usage statistics API exists by design; wrap in your own malloc if you need introspection.
- Several correctness bugs are open and unfixed as of the last commit (April 2026): segfault in ptrie_insert, realloc() hang, chunk leaks.

## Caveats and trade-offs

The main numbers come from the third-party smmalloc README table: compiler, flags, and units are unstated, the workload is not described on the page, and the current smmalloc perf code no longer benchmarks ltalloc. On the i7-2600 table, ltalloc trails rpmalloc, hoard, and smmalloc. The earlier caveat was wrong: ltalloc's own README FAQ does have a first-party results table, published as an image. That table covers 128-byte alloc/free from concurrent threads on several Windows/Linux machines, with the default allocator 6.21x-218.75x slower than ltalloc (i7 2600/Win7 single-thread: 16.0 vs 165.0 M ops/s per thread). The linked Xeon/Debian chart (googlecode) is dead. The repo has commits in 2026 and is not GitHub-archived or a fork.

Overrides global operator new/delete directly (not a std::allocator wrapper); best suited for many small (&lt;256B) allocations; peak performance relies on LTO/inlining of the size-class computation.

## Maintenance

GitHub marks the repo active (pushed April 2026, not archived) and it is not a fork, but real development stopped in 2019 - the only 2026 activity was merging one external ARM64/ARM64EC PR - and 8 issues remain open including unresolved crash/hang reports. BSD-3-Clause and a single source file, so it's cheap to vendor and pin even though upstream is effectively dormant.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The smmalloc README table compares ltalloc against crt (the default runtime malloc) on i7-2600/Windows 10 and PS4, but compiler, flags, and units are unstated. The smmalloc repo's current perf code no longer includes ltalloc. ltalloc's own README table is first-party with partial methodology. Both are C.
- **Verifier notes:** Numbers match the smmalloc table, but the record's ratios were not marked as derived, so they are now tagged. benchmark_url is left as smmalloc (text table). The ltalloc README table (https://i.imgur.com/fiR9C9M.png) is an alternative first-party source with larger ratios, but its flags are unstated and some ratios are &gt;50x.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/r-lyeh-archived/ltalloc>
  - <https://github.com/SergeyMakeev/smmalloc#performance>
  - <https://github.com/SergeyMakeev/smmalloc/blob/master/smmalloc_perf01.cpp>
  - <https://i.imgur.com/fiR9C9M.png>
  - <http://wiki.ltalloc.googlecode.com/hg/benchmark.png>
- **Sources the enricher read:**
  - <https://github.com/r-lyeh-archived/ltalloc>
  - <https://github.com/r-lyeh-archived/ltalloc/blob/master/ltalloc.h>
  - <https://github.com/r-lyeh-archived/ltalloc/blob/master/ltalloc.hpp>
  - <https://github.com/r-lyeh-archived/ltalloc/blob/master/ltalloc.cc>
  - <https://github.com/r-lyeh-archived/ltalloc/issues>
  - <https://github.com/r-lyeh-archived/ltalloc/issues/23>
  - <https://github.com/r-lyeh-archived/ltalloc/issues/27>
  - <https://github.com/r-lyeh-archived/ltalloc/commits/master>
  - <https://github.com/SergeyMakeev/smmalloc#performance>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/r-lyeh-archived/ltalloc`) · [data/wave1/enrich/raw/github_com_r_lyeh_archived_ltalloc.json](../../../data/wave1/enrich/raw/github_com_r_lyeh_archived_ltalloc.json) (enrichment confidence 0.45)

</details>
