# avx-512-sort (Bramas)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only AVX-512 quicksort with bitonic small-sort for int, double and int key/value arrays; paper claims 4x over GNU std::sort.

| | |
|---|---|
| **Beats** | std::sort (GNU C++ sort) and Intel IPP sort |
| **Claimed result** | About 4x faster than the GNU C++ sort and about 1.4x faster than the Intel IPP library on a Skylake Xeon (paper abstract, arXiv 1704.08579 / IJACSA 2017, seen in a search snippet only) |
| **Workload** | Paper-branch main.cpp timeAll: single-threaded sort (NewQuickSort512 V1-V5 QsSequential) of random int or double arrays (drand48()\*size) from 64 to 2^30 elements in x8 steps, 5 runs (min, max and mean recorded), against std::sort with a lambda less-than comparator and Intel IPP ippsSortRadixAscend (radix sort); a timeAll_pair variant covers int key/value pairs. |
| **Metric** | throughput |
| **Hardware** | Skylake Xeon (model not confirmed); Knights Landing in the older report |
| **Compiler and flags** | Paper-branch main.cpp header gives the Skylake build line: g++ -DNDEBUG -O3 -funroll-loops -faggressive-loop-optimizations -std=c++11 -mavx512f -mavx512cd -mavx512vl -mavx512bw -mavx512dq -fopenmp (an icpc -O3 -xCOMMON-AVX512 -xCORE-AVX512 -qopenmp alternative is also listed; -DUSE_IPP links IPP). Which compiler and version produced the paper's numbers is not confirmed (paper not opened). |
| **Adoption** | 29 stars; paper-linked; same algorithm family is credited by numpy/x86-simd-sort |
| **Last commit** | 2022-06-20 |
| **Links** | [repository](https://github.com/berenger-eu/avx-512-sort) · [benchmark](https://arxiv.org/abs/1704.08579) |

## Verdict

The IJACSA 2017 paper (arXiv 1704.08579, abstract seen in search snippets only) reports about 4x over GNU std::sort with a lambda less-than and about 1.4x over Intel IPP ippsSortRadixAscend on a Skylake Xeon whose model, like the compiler version, is not confirmed; the paper-branch harness behind it times single-threaded sorts of drand48()\*n int and double arrays from 64 to 2^30 elements in x8 steps, regenerating identical input for each algorithm and averaging 5 runs.

## Use it when

- Single-threaded sorting of large arrays of 32-bit int or double keys that are close to distinct (random data, IDs, measurements) on Intel AVX-512 hardware (Skylake-SP/X and later, or Knights Landing).
- Sorting int keys with an int payload stored in a separate array (struct-of-arrays layout) without packing pairs.
- As a small, MIT-licensed, readable reference for the AVX-512 compress-store partition plus bitonic-network design that later libraries (numpy/x86-simd-sort cites it) refined.
- Sorting many short arrays (up to 256 ints or 128 doubles) with SmallSort16V's branch-free networks.

## Skip it when

- Inputs with many duplicate keys: the &lt;= pivot partition sends every element equal to the pivot left, so an all-equal run shrinks by one element per level and the sort becomes O(n^2) (issue #1, closed 2022-03-27 without a code change; the author suggests an is_sorted pre-check, which does not help low-cardinality data that is not all equal).
- Doubles that may contain +infinity or NaN: the padding value DBL_MAX sorts below +inf, so +inf values in a leaf block whose length is not a multiple of 8 are overwritten with DBL_MAX, and NaN ordering is undefined (min/max and _CMP_LE_OQ semantics).
- Machines without AVX-512F (any AVX2-only x86, Arm): there is no fallback; the Arm SVE variant lives in a separate gitlab.inria.fr repository.
- Code that needs a comparator, iterators, 64-bit integer keys, stability or adversarial-input guarantees (no introsort fallback, median-of-three pivot only).
- New projects that want maintenance: numpy/x86-simd-sort and Highway vqsort are maintained successors covering more types and duplicate-heavy inputs.

## How it is fast

Quicksort whose partition step loads 512-bit vectors from both ends, compares them against a broadcast pivot into a mask, and writes the low and high lanes with masked compress-stores (_mm512_mask_compressstoreu), so partitioning is branch-free except for choosing which end to read next. Subarrays under 16 vectors (256 ints or 128 doubles) go to fully unrolled bitonic sorting networks built from permutexvar plus min/max, with the last partial vector padded with INT_MAX or DBL_MAX. The pivot is a scalar median of three; master's Sort corresponds to the paper branch's NewQuickSort512V5.

## Compared with alternatives

Pick it over WojciechMula/simd-sort when you need doubles or int key/value pairs as well as int32 keys from one header, and over jonicho/simd-radix-sort when you want a comparison-based in-place quicksort rather than an MSB radix sort; for anything new, numpy/x86-simd-sort (wave 1) is the maintained successor of this design.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for the sequential sort (immintrin.h); OpenMP and the bundled parallelInplace.hpp for the parallel variants |
| **Minimum toolchain** | C++11 (build lines use -std=c++11); GCC with -mavx512f -mavx512cd (plus -mavx512vl -mavx512bw -mavx512dq for Skylake) or icpc -xCORE-AVX512; CI used GCC 6 |
| **Platforms** | x86-64 with AVX-512F (Intel Knights Landing and Skylake were the targets); no non-AVX-512 path |
| **Thread safety** | not documented; the sequential functions keep no shared state, so concurrent calls on different arrays are independent by construction |
| **Drop-in for the baseline** | partial: replaces std::sort(p, p + n) for plain int or double arrays in ascending order only, with a different call (Sort512::Sort(p, n)) and without comparator, iterator, duplicate-heavy or special-float safety |

## Gotchas

- Sort512::Sort with IndexType size_t and size 0 computes right = size - 1 = SIZE_MAX, skips the small-sort branch and reads array[SIZE_MAX/2] while choosing the pivot (out-of-bounds read); the unit tests start at size 1. Guard empty inputs yourself.
- Duplicate-key and special-value pathologies above are not caught by the tests: sort512test.cpp only sorts power-of-two sizes up to 1024 filled with drand48()\*size values, and the benchmark (paper-branch timeAll, master sort512perf.cpp) uses the same near-distinct uniform random input, so the published speedups never exercise the O(n^2) duplicate case.
- SortOmpMerge and SortOmpParMerge need a power-of-two thread count, but the assert sits outside the parallel region where omp_get_num_threads() is 1 (and -DNDEBUG removes it); with 6 threads, thread 4 spins forever on done[1][3], a flag only a nonexistent thread 6 would set. Use SortOmpPartition or set OMP_NUM_THREADS to a power of two (at most 128).
- The README and header still name Sort512::SortOmp(), which no longer exists after the July 2020 strategy split; the master commit of 2022-06-20 changed signed-zero handling in the min/max networks after the paper's measurements.

## Known shortcomings

- The 4x vs std::sort and 1.4x vs Intel IPP figures exist only in a search snippet of the abstract (arXiv 1704.08579 unopened); the paper branch main.cpp has the full harness and build lines but no results; master code never re-benchmarked; -0/+0 fix 2022-06-20. x86-simd-sort cites it as ref [2].
- Enricher: O(n^2) on duplicate-heavy input (the &lt;= partition; issue #1 closed without a fix) and the benchmark uses only near-distinct drand48 data so the case is never measured; DBL_MAX padding in SmallSort16V overwrites +inf with DBL_MAX; Sort&lt;T,size_t&gt;(p,0) reads array[SIZE_MAX/2] out of bounds; SortOmpMerge deadlocks with non-power-of-two thread counts; the README names a SortOmp() that no longer exists; the paper is still snippet-only (HAL, datashare and arXiv blocked).

## Caveats and trade-offs

Snippet only: the IJACSA 2017 paper and arXiv 1704.08579 were unreachable (thesai.org, arxiv.org, ar5iv and gitlab.inria.fr fail DNS here), so the 4x and 1.4x abstract figures, the Skylake CPU model and the compiler version are unchecked. The 'paper' branch (LICENSE and a 1 MB main.cpp) holds the benchmark harness with build lines but no result tables; the measured code is the paper-branch NewQuickSort512 variants, while master ships a cleaned header library (sort512.hpp, sort512kv.hpp) that was not re-benchmarked, and a 2022-06-20 master commit ('Reverse min params to manage -0/+0') changed signed-zero handling after the paper. IJACSA is a low-selectivity open-access venue. Only AVX-512 (Skylake, earlier Knights Landing report) is covered. The algorithm is cited as reference [2] in numpy/x86-simd-sort (src/xss-common-qsort.h), which is already listed in wave 1 and is the maintained successor.

Header-only (sort512.hpp, sort512kv.hpp), AVX-512 only (KNL and Skylake-X flag sets), OpenMP parallel variant; an ARM SVE port is referenced on gitlab.inria.fr (not reachable here). Later libraries (x86-simd-sort, Highway vqsort) cover the same space.

## Maintenance

Abandoned since the 2022-06-20 signed-zero fix (29 stars, MIT, header-only and easy to vendor), but its duplicate-key quadratic case and +inf padding bug make it safe only for near-distinct finite keys.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The 4x over GNU std::sort and 1.4x over Intel IPP figures come only from the IJACSA 2017 / arXiv 1704.08579 abstract, seen in search snippets (arXiv, ar5iv, thesai.org and gitlab.inria.fr all fail DNS here); the repo's paper branch carries the full benchmark harness (main.cpp timeAll against std::sort and IPP) and build lines but no results, so tier C until the paper's tables, CPU model and compiler version are read.
- **Verifier notes:** Metadata confirmed (MIT, 29 stars, last commit 2022-06-20, abandoned). The record's statement that the paper branch has no numbers is right, but it does carry the full benchmark harness and build flags, so a B or A retier is possible once the IJACSA paper (CPU model, compiler) can be opened. baseline_in_list set to true because std::sort (libstdc++) is the C++ incumbent and a scalar C++ reference.
- **Fields the verifier corrected:** `benchmark_url`, `baseline_in_list`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-11 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/berenger-eu/avx-512-sort>
  - <https://github.com/berenger-eu/avx-512-sort/commits/master>
  - <https://github.com/berenger-eu/avx-512-sort/tree/paper>
  - <https://raw.githubusercontent.com/berenger-eu/avx-512-sort/master/README.md>
  - <https://raw.githubusercontent.com/berenger-eu/avx-512-sort/master/sort512perf.cpp>
  - <https://raw.githubusercontent.com/berenger-eu/avx-512-sort/paper/main.cpp>
  - <https://raw.githubusercontent.com/intel/x86-simd-sort/main/src/xss-common-qsort.h>
  - <https://github.com/numpy/x86-simd-sort/pull/96>
- **Sources the enricher read:**
  - <https://github.com/berenger-eu/avx-512-sort>
  - <https://github.com/berenger-eu/avx-512-sort/commits/master>
  - <https://github.com/berenger-eu/avx-512-sort/issues?q=is%3Aissue>
  - <https://github.com/berenger-eu/avx-512-sort/issues/1>
  - <https://raw.githubusercontent.com/berenger-eu/avx-512-sort/master/README.md>
  - <https://raw.githubusercontent.com/berenger-eu/avx-512-sort/42f6a71/README.md>
  - <https://raw.githubusercontent.com/berenger-eu/avx-512-sort/master/sort512.hpp>
  - <https://raw.githubusercontent.com/berenger-eu/avx-512-sort/master/sort512kv.hpp>
  - <https://raw.githubusercontent.com/berenger-eu/avx-512-sort/master/sort512perf.cpp>
  - <https://raw.githubusercontent.com/berenger-eu/avx-512-sort/master/sort512test.cpp>
  - <https://raw.githubusercontent.com/berenger-eu/avx-512-sort/master/LICENSE>
  - <https://raw.githubusercontent.com/berenger-eu/avx-512-sort/paper/main.cpp>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/berenger-eu/avx-512-sort`) · [data/wave13/enrich/raw/github_com_berenger_eu_avx_512_sort.json](../../../data/wave13/enrich/raw/github_com_berenger_eu_avx_512_sort.json) (enrichment confidence 0.75)

</details>
