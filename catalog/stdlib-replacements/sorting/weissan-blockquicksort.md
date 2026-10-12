# BlockQuicksort

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `GPL-3.0` · 🔴 abandoned

> In-place Quicksort using block-buffered Hoare partitioning to avoid branch mispredictions; \~88% more elements/s than GCC std::sort on random ints.

| | |
|---|---|
| **Beats** | std::sort |
| **Claimed result** | More than 80% more elements sorted per second than GCC's std::sort on random ints. Section 4: optimized BlockQuicksort needs \~45 ns/element vs 85 ns/element for std::sort at n=2^28 (+88%), and the duplicate-check variant is almost twice as fast on random ints in [0, sqrt n]. Figure 7 shows smaller but positive gains on Vector and Record for the BlockQS (mo-sqrt n, dc) variant. std::sort wins only on sorted or almost-sorted inputs. |
| **Workload** | Sorting arrays of random 32-bit ints, 10-dimensional double Vectors (Euclidean-norm comparator), and 21-field int Records, measured as elements sorted per second, against GCC's std::sort. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-2500K @ 3.30GHz, 4 cores, 32KB L1 i/d, 256KB L2/core, 6MB shared L3, 16GB RAM, Ubuntu 14.04.4 64-bit |
| **Compiler and flags** | GNU g++ 4.8.4, -O3 -march=native |
| **Adoption** | 40 stars; algorithm published in ACM Journal of Experimental Algorithmics (2019) and cited as the 'closest sequential competitor' baseline in the IPS4o paper |
| **Last commit** | 2021-11-29 |
| **Links** | [repository](https://github.com/weissan/BlockQuicksort) · [benchmark](https://drops.dagstuhl.de/opus/volltexte/2016/6389/pdf/LIPIcs-ESA-2016-38.pdf) |

## Verdict

On GCC 4.8.4 (-O3 -march=native) on an Intel Core i5-2500K (4 cores, Ubuntu 14.04.4), the optimized BlockQuicksort variant needs \~45 ns/element vs \~85 ns/element for the repo's bundled copy of GCC 4.7.2's std::sort at n=2^28 on random 32-bit ints (\~88% more elements sorted per second); smaller but still positive gains hold on 10-dim Vector and 21-field Record comparators for the mo-sqrt(n), duplicate-check variant, and std::sort wins on sorted/nearly-sorted input.

## Use it when

- Sorting large (n in the hundreds of millions) arrays of random 32-bit ints where per-element comparison is cheap and branch mispredictions dominate cost — the paper's largest reported gain (\~88%) is at n=2^28.
- Multi-field comparators (the paper's 10-dim Vector / 21-field Record benchmarks) where smaller but still positive gains hold for the mo-sqrt(n),dc variant.
- Batch/offline throughput-oriented sorts where an unstable, in-place sort is acceptable and you're willing to hand-integrate a research header into your own call sites.
- As a reference implementation or benchmarking baseline for new sequential sort research — it's already used as the 'closest sequential competitor' in the IPS4o paper.
- Random or otherwise non-sorted input distributions; the paper itself reports std::sort wins on sorted/nearly-sorted input.

## Skip it when

- Need stability (equal elements keep relative order) — not stable, no stable variant provided.
- Sorted or nearly-sorted input — the input record's own claim notes std::sort wins there.
- Want a true drop-in replacement for std::sort with no call-site changes — this exposes sort() under its own namespace, not an overload of std::sort.
- Production/commercial use needing an actively maintained, permissively-licensed dependency — repo abandoned since Nov 2021 with two issues open and unanswered since 2019, and it's GPL-3.0 (the branch-avoidance technique itself has since been reimplemented under more permissive licenses in pdqsort and PPQSort).
- Want to just include one clean header — mixing more than one \*.h++ interface file in the same translation unit causes duplicate-template-definition compile errors (open issue #6, unresolved).

## How it is fast

partition.h's hoare_block_partition_\* functions compare a BLOCKSIZE=128 chunk of elements against the pivot into small fixed-size index buffers first, then do the swaps in a second, branch-free loop, so the CPU's branch predictor never has to guess the per-element comparison outcome during the swap phase. Pivot selection samples a median of \~sqrt(n) elements (median.h), and the qsort_double_pivot_check main loop (quicksort.h) adds a check for duplicate-heavy partitions adapted from Elmasry/Katajainen/Stenmark's Tuned Quicksort, falling back to insertion sort/std::partial_sort at small sizes like libstdc++'s introsort.

## Compared with alternatives

Pick this over Boost.Sort/IPS4o/LearnedSort/etc. only when you specifically want the original peer-reviewed (ESA 2016 / JEA 2019) branch-avoidance partitioner — e.g. reproducing or benchmarking against it as IPS4o did — since the technique itself is now available in actively maintained, permissively-licensed form in pdqsort and PPQSort; for production sequential sorting prefer fluxsort or a pdqsort-family library instead of this abandoned GPL-3.0 repo.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none external; each \*.h++ variant needs matching repo-internal headers (quicksort.h, partition.h, median.h, insertionsort.h, rotations.h) included alongside it |
| **Minimum toolchain** | C++11 (repo makefile: g++ -O3 -std=c++11 -march=native; benchmarked with GCC 4.8.4) |
| **Platforms** | x86-64 only benchmarked (-march=native, Intel Core i5-2500K); portable C++11 templates with no explicit SIMD intrinsics observed — the branch-avoidance win depends on the compiler auto-vectorizing/optimizing the small fixed-size block-classification loop, so results are compiler- and arch-dependent |
| **Thread safety** | not documented — single-threaded algorithm; no shared/global mutable state visible in partition.h or quicksort.h (an unused #include &lt;future&gt; is the only concurrency-related trace found) |
| **Drop-in for the baseline** | partial — explain: same (begin, end, comparator) iterator signature as std::sort, but exposed as e.g. blocked_double_pivot_check_mosqrt::sort(...) rather than an overload of std::sort, so every call site must be edited; also unstable and in-place unlike std::stable_sort |

## Gotchas

- Including more than one \*.h++ interface header in the same translation unit triggers 'redefinition of template' errors from median.h (issue #6, open since 2019).
- Release-flag builds compile with -DNDEBUG, so the assert() sanity checks scattered through partition.h are stripped in the benchmarked configuration.
- The README recommends only blocked_double_pivot_check_mosqrt.h++ and blocked_simple.h++ out of \~40 header variants; a user asked in issue #5 (2019, still open) for clearer guidance on which variant to actually use.
- BLOCKSIZE (128) and pivot-sample-size constants are compile-time #defines tuned for the paper's int/Vector/Record types on one CPU; other key types or hardware may need retuning.

## Caveats and trade-offs

Repo unmaintained since Nov 2021; the std::sort compared against is a bundled copy of GCC 4.7.2's libstdc++ implementation (see paper footnote 3), not necessarily the std::sort of the g++ 4.8.4 compiler used to build the test; no libc++ or MSVC STL comparison.

In-place but not stable; block size (default 128) needs tuning per data type; branch-misprediction-avoidance technique now widely reused (e.g. pdqsort, PPQSort) under more permissive licenses than this repo's GPL-3.0.

## Maintenance

Abandoned since its last commit on 2021-11-29, with two open issues unanswered since 2019, but classified 'copyable' — the source is small enough to vendor directly if your project's license tolerates GPL-3.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The ESA 2016 paper (peer-reviewed) states g++ 4.8.4 -O3 -march=native and an Intel Core i5-2500K on Ubuntu 14.04.4. The repo holds the reproducible harness (driver.cpp plus makefile targets 'make timetest' / '&lt;alg&gt;.time', CXXFLAGS -O3 -std=c++11 -march=native) timing against the bundled GCC 4.7.2 std::sort copy (stl_gcc).
- **Verifier notes:** The claims, compiler, flags and hardware all match the paper; the old benchmark_url 301-redirects to https://drops.dagstuhl.de/storage/00lipics/lipics-vol057-esa2016/LIPIcs.ESA.2016.38/LIPIcs.ESA.2016.38.pdf and still works. Metadata verified: GPL-3.0, 40 stars, last commit 2021-11-29 (&gt;3 years, so abandoned), not archived, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`
- **Pages the verifier opened:**
  - <https://drops.dagstuhl.de/opus/volltexte/2016/6389/pdf/LIPIcs-ESA-2016-38.pdf>
  - <https://drops.dagstuhl.de/storage/00lipics/lipics-vol057-esa2016/LIPIcs.ESA.2016.38/LIPIcs.ESA.2016.38.pdf>
  - <https://github.com/weissan/BlockQuicksort>
- **Sources the enricher read:**
  - <https://github.com/weissan/BlockQuicksort>
  - <https://github.com/weissan/BlockQuicksort/blob/master/README.md>
  - <https://github.com/weissan/BlockQuicksort/blob/master/quicksort.h>
  - <https://github.com/weissan/BlockQuicksort/blob/master/partition.h>
  - <https://github.com/weissan/BlockQuicksort/blob/master/blocked_double_pivot_check_mosqrt.h++>
  - <https://github.com/weissan/BlockQuicksort/blob/master/makefile>
  - <https://github.com/weissan/BlockQuicksort/issues/5>
  - <https://github.com/weissan/BlockQuicksort/issues/6>
  - <https://github.com/weissan/BlockQuicksort/pulls?q=is%3Apr>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/weissan/blockquicksort`) · [data/wave1/enrich/raw/github_com_weissan_blockquicksort.json](../../../data/wave1/enrich/raw/github_com_weissan_blockquicksort.json) (enrichment confidence 0.83)

</details>
