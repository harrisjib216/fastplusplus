# quadsort

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `Unlicense` · 🟡 stale

> Stable branchless bottom-up adaptive merge sort in C, beating std::stable_sort on random and partially ordered arrays.

| | |
|---|---|
| **Beats** | std::stable_sort |
| **Claimed result** | \~2.4x faster than std::stable_sort (g++ 7.5 libstdc++) on random arrays of 513-1024 32-bit ints: best 0.005664s vs 0.013871s (weighted benchmark, 50 samples). Across random arrays of 1-4096 items the gain is \~2.0-4.9x. The README's 100,000-element per-distribution data table labels its rows 'fluxsort', not quadsort, although the bar graph says quadsort. That table shows \~4.1x for ascending saw and \~5.5x for pipe organ, and \~15-16x only for fully ascending or descending input. It is slower than std::stable_sort on bit reversal, which the graph also shows for quadsort. The earlier '\~16x ascending-saw / \~10x pipe-organ' figures are not supported. |
| **Workload** | From the wolfsort bench.c: std::stable_sort vs quadsort vs timsort on 100,000 elements (32/64/128-bit) across 11 distributions (random, random%100, ascending, ascending saw, pipe organ, descending, descending saw, random tail, random half, ascending tiles, bit reversal), 100 samples with best and average reported. A second run covers random arrays of 1-4096 32-bit items (weighted repetitions, 50 samples). |
| **Metric** | throughput |
| **Compiler and flags** | g++ -O3 -w -fpermissive (GCC 7.5.0, WSL2/Ubuntu 18.04); a separate run used clang -O3 (clang 10) |
| **Adoption** | 2204 stars |
| **Last commit** | 2024-07-27 |
| **Links** | [repository](https://github.com/scandum/quadsort) · [benchmark](https://github.com/scandum/quadsort#benchmark-quadsort-vs-stdstable_sort-vs-timsort) |

## Verdict

On WSL2/Ubuntu 18.04 with g++ 7.5.0 (-O3 -w -fpermissive), the author's own wolfsort bench.c measured quadsort at 0.005664s vs std::stable_sort's 0.013871s (best-of-50) sorting weighted random arrays of 513-1024 32-bit ints, about 2.4x, with roughly 2.0-4.9x across the full 1-4096 item weighted sweep; no CPU model is stated. The README's larger 100,000-element, 11-distribution table (\~4-16x claims) is mislabeled 'fluxsort' in its row data despite a 'quadsort' bar-graph caption, so those bigger numbers cannot be confidently attributed to quadsort itself.

## Use it when

- Large arrays (100K+) of primitives on gcc/x86 where std::stable_sort's overhead is measured to be a bottleneck
- Partially ordered input (ascending/descending runs, sawtooth, pipe-organ patterns) where the run-detecting analyzer pays off most
- C codebases already built around qsort-style comparators, or C++ call sites that can pass contiguous arrays of PODs
- Fixed-width 32/64-bit integer arrays, via quadsort_prim, to skip comparator call overhead entirely
- Projects fine vendoring a small, unlicensed (public-domain) header/source pair instead of linking a library

## Skip it when

- Call sites that need std::stable_sort's actual iterator/comparator signature over arbitrary containers, not just contiguous arrays
- Bit-reversal-ordered input: the vendor's own benchmark table shows quadsort slower than std::stable_sort there
- Building with clang instead of gcc: author states the branchless merge/small-sort routines run 2-3x slower under clang
- Need current, independently reproduced numbers: last commit 2024-07-27 ('stale'), sole benchmark is first-party with no CPU stated, and the README's big 100,000-element per-distribution table is mislabeled 'fluxsort' even though its graph is captioned 'quadsort'
- Memory-constrained sorts expecting an in-place win: quadsort still needs an O(n) auxiliary swap buffer, same as std::stable_sort

## How it is fast

An 8-element analyzer detects ascending or descending runs using a 4-comparison bitmask trick, cutting branch mispredictions to about 0.2 per 8 elements versus \~3.2 for naive comparisons, and exits with pre-sorted 8-element blocks. Small blocks are combined with branchless swap and 'parity merge' macros, then merged bottom-up with a single reusable O(n) swap buffer (like std::stable_sort's own auxiliary buffer) instead of per-level allocation. The branchless macros are written as GCC-style conditional stores on gcc and as ternary expressions on clang, so codegen and speed differ by compiler.

## Compared with alternatives

Pick quadsort over the same author's fluxsort when you specifically want the mergesort half without fluxsort's quicksort partitioning (fluxsort itself is the faster average-case hybrid per the vendor's own comparisons); pick quadsort over BlockQuicksort, Boost.Sort/spreadsort, IPS4o, LearnedSort, or x86-simd-sort specifically when stability is required, since those all target unstable std::sort rather than std::stable_sort.

## Integration

| | |
|---|---|
| **Form** | header-only (quadsort.h #includes quadsort.c internally; single #include "quadsort.h" is enough) |
| **Dependencies** | none (stdlib.h, stdio.h, assert.h, errno.h, float.h, string.h only) |
| **Minimum toolchain** | plain C (no C99/C11-specific features observed); README benchmarks used GCC 7.5.0 and clang 10 with -O3; the C++ bench harness needed -fpermissive to compile the C header as C++ |
| **Platforms** | any target with a C compiler; portable C with no SIMD intrinsics, but branchless codegen and measured speed are tuned for gcc/x86 (2-3x slower merge/small-sort routines under clang per the author) |
| **Thread safety** | not documented (single-threaded implementation; no mention of thread safety or reentrancy in README or headers) |
| **Drop-in for the baseline** | partial — explain: quadsort takes a qsort-style (array, nmemb, size, cmp) signature, not std::stable_sort's (first, last, comp) iterator interface, so C++ call sites need an adapter and are limited to contiguous arrays of PODs, not arbitrary containers/iterators |

## Gotchas

- QUAD_CACHE (default 262144) gates performance for pointer/struct sorts via quadsort_size; the header comments say it needs tuning for large arrays and L3 cache size
- Branchless macros branch on the __clang__ define, so gcc and clang run genuinely different code paths for the same source, not just different optimizer output
- quadsort and quadsort_size malloc their own O(n) swap buffer internally with no custom-allocator hook, and assert() on malloc failure rather than returning an error code
- A user-filed correctness question about cross_merge's tail pointer possibly running past the block's tail (issue #20) is closed but its resolution isn't confirmed in the visible thread

## Caveats and trade-offs

First-party benchmark (the author's wolfsort suite, src/bench.c), not independently replicated. The CPU/hardware is never stated, only WSL2/Ubuntu 18.04 with GCC 7.5.0 (dated). The README's 100,000-element data table is mislabeled 'fluxsort' while its graph says quadsort, so per-distribution numbers for quadsort itself are unreliable. Quadsort is slower than std::stable_sort on bit-reversal input. It is C code, usable from C++ via its header.

Stable, needs O(n) swap buffer like std::stable_sort; branchless design is tuned for GCC on x86 — author notes a 2-3x slowdown for the branchless merge/small-sort routines when compiled with clang instead of gcc.

## Maintenance

Maintenance is stale (last commit 2024-07-27, no recent activity) but the code is Unlicense (public domain) and a small, single header/source pair, cheap to vendor and freeze indefinitely.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The author's own benchmark code (src/bench.c, from the wolfsort suite) calls std::stable_sort directly, and the compiler and flags are stated (g++ 7.5.0 -O3 -w -fpermissive). The CPU is never stated, so it cannot be A. There is no paper or independent suite (for example, the cpp-sort benchmarks do not include quadsort), so B does not apply.
- **Verifier notes:** The 1024-item 2.4x figure is verified. The partially-ordered claims (16x/10x) were wrong and came from a table the README labels 'fluxsort'. Tier goes from B to C (first-party, no hardware stated). Metadata is confirmed: Unlicense, 2204 stars, last commit 2024-07-27, 'stale'.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/scandum/quadsort>
  - <https://github.com/scandum/quadsort#benchmarks>
  - <https://github.com/scandum/quadsort/blob/master/src/bench.c>
  - <https://github.com/scandum/quadsort/blob/master/images/graph1.png>
  - <https://github.com/Morwenn/cpp-sort/wiki/Benchmarks>
- **Sources the enricher read:**
  - <https://github.com/scandum/quadsort>
  - <https://github.com/scandum/quadsort#benchmark-quadsort-vs-stdstable_sort-vs-timsort>
  - <https://github.com/scandum/quadsort/blob/master/README.md>
  - <https://github.com/scandum/quadsort/blob/master/src/quadsort.h>
  - <https://github.com/scandum/quadsort/blob/master/src/quadsort.c>
  - <https://github.com/scandum/quadsort/blob/master/src/bench.c>
  - <https://github.com/scandum/quadsort/issues>
  - <https://github.com/scandum/quadsort/issues/14>
  - <https://github.com/scandum/quadsort/issues/20>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/scandum/quadsort`) · [data/wave1/enrich/raw/github_com_scandum_quadsort.json](../../../data/wave1/enrich/raw/github_com_scandum_quadsort.json) (enrichment confidence 0.75)

</details>
