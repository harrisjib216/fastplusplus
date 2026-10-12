# swenson/sort (sort.h)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> Single C89 header that macro-generates type-specialised quick, heap, tim, merge and shell sorts that beat libc qsort.

| | |
|---|---|
| **Beats** | qsort (C standard library) |
| **Claimed result** | demo.c output on a 2014-era MacBook Pro, 10,000 int64_t: quick sort 579 us vs stdlib qsort 1285 us (about 2.2x, derived from page data); heap sort 592, in-place merge sort 903, merge sort 999, tim sort 1005, shell sort 1054, sqrt sort 1095 and grail sort 1220 us are also below qsort's 1285 us; binary insertion (13,443 us) and selection sort (127,176 us) are far slower; stdlib mergesort 1299 us and heapsort 2109 us are slower than qsort. |
| **Workload** | Sorting 10,000 random int64_t values (lrand48) once per routine with demo.c, timed with gettimeofday, against libc qsort with a function-pointer comparator. |
| **Metric** | throughput |
| **Hardware** | 2014-era MacBook Pro (CPU model unstated) |
| **Compiler and flags** | Unstated for the README numbers. The Makefile default is CFLAGS ?= -O3 -g -Wall -std=c89 -pedantic -Wno-long-long -Wno-format with CC ?= gcc, which may differ from the README run. |
| **Adoption** | 476 stars, 88 forks |
| **Last commit** | 2024-02-13 |
| **Links** | [repository](https://github.com/swenson/sort) · [benchmark](https://github.com/swenson/sort) |

## Verdict

The README table is one run of demo.c sorting 10,000 lrand48 int64_t values on an unnamed 2014-era MacBook Pro with macOS libc qsort as the baseline: quick sort 579 us and heap sort 592 us vs qsort 1285 us (about 2.2x, derived from page data); compiler and flags are not stated (the Makefile at that commit used CFLAGS = -O3 -g -Wall -std=c89 with CC ?= gcc). The table is unchanged since commit 47934fc (May 4, 2014), so it measured the old quick sort (middle-element pivot, two recursive calls, binary insertion below 16, no depth limit; the version behind the stack overflow in issue #62), not the 2019 median-of-5/heap-fallback/sorting-network quick sort that ships now.

## Use it when

- C code (C89 plus stdint.h and long long) that sorts arrays of one primitive or struct type through qsort and can accept a compile-time comparator macro.
- You want several algorithms behind one header: timsort for partially ordered data or expensive comparisons, heap sort for O(1) extra memory with an n log n worst case, quick sort for random data.
- Stable sorting without an O(n) buffer: in-place grail sort and sqrt sort from sort_extra.h.
- Builds that must not link a library: everything is in the header, and SORT_DEF static removes unused routines (issue #86 reported about 30 kB per instantiated type at -Oz without it).

## Skip it when

- C++ code: std::sort already inlines the comparator, and no measurement against std::sort, pdqsort or any other modern sort exists (issue #85 asking for a std::sort comparison has been open since February 2023).
- When you need current performance evidence: the only published table is a single 2014 run of code that has since been replaced.
- Full-range int64 keys or floating-point keys with the README's subtraction comparator: comparator results are truncated to int inside quick sort, binary insertion and in-place merge, so the output can be unsorted (see gotchas); keep the default '&lt;'-based SORT_CMP.
- Programs that cannot tolerate exit() on allocation failure (tim sort) or arrays above INT_MAX elements with the sort_extra.h routines, which use int lengths (issue #89).
- Non-trivially-copyable C++ types unless SORT_SAFE_CPY is defined to 1; the default copies with memcpy/memmove and allocates with malloc.

## How it is fast

The win over qsort is compile-time specialisation: SORT_CMP and SORT_SWAP expand inline on SORT_TYPE, so there is no indirect comparator call and no byte-wise generic swap per step. The current quick sort is introsort-like: median-of-5 pivot (two nested median-of-three), Lomuto partition with an all-equal early exit, recursion on the smaller side and a loop on the larger, a switch to heap sort after about lg N partition rounds, and optimal sorting networks (BITONIC_SORT_2..16) for ranges of 16 or fewer. Tim sort detects runs, extends them to minrun with binary insertion and merges through a buffer of min(A,B) elements; galloping was reverted in 2020.

## Compared with alternatives

Pick it over pdqsort, crumsort or fluxsort when you need a C89 header with a menu of algorithms, including in-place stable grail/sqrt sort and timsort, instantiated per type by macros. For raw speed on primitive keys the catalogued siblings (pdqsort, crumsort, Highway vqsort) carry newer and much stronger benchmarks, while this entry's only numbers are from 2014.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C standard library headers stdlib.h, stdio.h, string.h, stdint.h) |
| **Minimum toolchain** | C89 with stdint.h and long long (Makefile builds with -std=c89 -pedantic -Wno-long-long); CI builds with gcc 10-13 and clang 13-15 on Ubuntu 22.04, the default compiler on macOS, and MSVC (stresstest only); also compiles as C++. |
| **Platforms** | any; uses __builtin_clzll when the compiler has it and a portable fallback otherwise |
| **Thread safety** | Not documented. The code keeps no mutable global state (only a const shell-gap table), so concurrent calls on different arrays are safe from code reading; tim sort and merge sort malloc/realloc a buffer on every call. |
| **Drop-in for the baseline** | partial — replaces qsort only after rewriting each call to a generated typed function (NAME_quick_sort(arr, n)) with the comparator expressed as a SORT_CMP macro; there is no qsort-compatible void\* entry point, and quick, heap, shell and in-place merge sort are not stable. |

## Gotchas

- Comparator results are stored in an int (int cmp in QUICK_SORT_PARTITION, const int val in BINARY_INSERTION_FIND, int cv in the in-place merge), so the README's own example '#define SORT_CMP(x, y) ((x) - (y))' on int64_t is wrong beyond overflow: differences wider than 32 bits truncate, e.g. keys that are multiples of 2^32 all compare equal, and for more than 16 of them the partition's all-equal shortcut returns without sorting the range. With double keys a subtraction comparator truncates differences below 1.0 to 0 (the README only warns of 'stability problems'). Found by code reading, not executed; demo, benchmark and stresstest only sort lrand48 values below 2^31, so nothing in the repo exercises it.
- MEDIAN has a copy-paste bug: in the a &gt;= b branch it computes 'AC' as SORT_CMP(dst[a], dst[b]) instead of dst[a] vs dst[c], so for the ordering b &lt; a &lt; c it returns c, the maximum. Output stays correct but pivot quality drops on random data; open PR #84 (December 2022, unmerged) rewrites MEDIAN and reports 4-25% faster quick sort.
- Allocation failure: tim sort prints to stderr and calls exit(1); merge sort does not check the malloc result. In C++ SORT_SAFE_CPY defaults to 0, so classes are moved with memcpy unless you define it to 1.
- The bundled tests cannot fail CI on a wrong result: stresstest's run_tests returns 0 even after printing FAILED, so main never returns 1; verify() checks only order, not that the output is a permutation; and the Windows job passes /DDSET_SORT_EXTRA, which defines DSET_SORT_EXTRA, so the sort_extra.h routines are never built there. The current demo.c and benchmark.c also override SORT_CSWAP with branchless MIN/MAX on int64, a tuning the README usage section does not mention.

## Known shortcomings

- One 10,000-element run with compiler and CPU unstated, qsort called through a function pointer (macOS libc), numbers from older code; not compared against std::sort.
- Enricher: the README table is unchanged since commit 47934fc (2014-05-04) and timed the old middle-pivot quick sort without a depth limit (the issue #62 stack-overflow version); the shipping 2019 median-of-5/heap-fallback quick sort has never been re-benchmarked. Comparator results are stored in an int, so the README's own ((x) - (y)) int64 example truncates differences wider than 32 bits and double keys with a subtraction comparator truncate differences below 1.0 to 0; the MEDIAN else branch compares the wrong elements (open PR #84); the stress test returns 0 on FAILED, so CI cannot fail on unsorted output.

## Caveats and trade-offs

The README table comes from one run (RUNS is 1 in demo.c, timed with gettimeofday at microsecond resolution) of one 10,000-element lrand48 array on an unnamed 2014 laptop, with compiler and flags unstated. The baseline is C qsort calling through a function pointer (and, since the stdlib heapsort and mergesort rows are compiled only on non-Linux, non-Cygwin platforms, macOS/BSD libc qsort), not std::sort or an inlined-comparator sort, so the gap measures comparator inlining more than algorithm quality; qsort is also not in the sorting category's baseline list. The demo uses the subtraction comparator (x - y), safe here only because lrand48 values are non-negative. The table predates later code changes (gallop revert 2020, binary-insertion small sorts 2021, grail and sqrt sort moved to sort_extra.h in 2024), so it reflects older code. Only quick sort, heap sort and in-place merge sort show a clear win; the README itself says results depend on the machine and data. benchmark.c in the repo (100,000 elements, timed loops) is more careful but no results from it are published. [retier] One 10,000-element lrand48 int64 run on a 2014 MacBook Pro with compiler and flags unstated, qsort called through a function pointer (macOS libc), not compared against std::sort. The table is unchanged since commit 47934fc (2014-05-04) and timed the old middle-pivot quick sort with no depth limit (the issue #62 stack-overflow version); the shipping 2019 median-of-5/heap-fallback/sorting-network quick sort has never been re-benchmarked. Comparator results are stored in an int (partition, binary insertion find, in-place merge), so the README's own ((x) - (y)) int64 example truncates differences wider than 32 bits (with more than 16 multiples of 2^32 the all-equal shortcut leaves the range unsorted) and double keys with a subtraction comparator truncate differences below 1.0 to 0; the MEDIAN else branch compares dst[a] with dst[b] instead of dst[c] (pivot quality only, open PR #84); the stress test returns 0 on FAILED; demo and benchmark override SORT_CSWAP with branchless MIN/MAX; tim sort exits on OOM.

Single C89 header that generates type-specialised routines through #define SORT_TYPE, SORT_NAME and SORT_CMP, so each instantiation adds code size. Comparator inlining is the source of the win over qsort. Includes stable options (timsort, merge sort, grail sort, sqrt sort). Not a C++ std::sort drop-in. The default demo comparator (x - y) is unsafe for integers whose difference can overflow.

## Maintenance

Stale (last commit February 13, 2024; issues #62, #85 and #89 and PR #84 unanswered) but MIT-licensed, a single dependency-free header with CI on gcc, clang and MSVC, and easy to vendor if you keep the default comparator.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table from the repo's demo.c (public code) against libc qsort, but compiler, flags and CPU model for the run are unstated (only '2014-era MacBook Pro'), so it is first-party with partial methodology.
- **Verifier notes:** README numbers match the record; metadata confirmed on github.com (476 stars, 88 forks, MIT, not a fork, last commit 2024-02-13 'Add GitHub Actions (#88)', so stale). Baseline is C qsort rather than a listed std:: facility, so baseline_in_list is corrected to false.
- **Fields the verifier corrected:** `baseline_in_list`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party README (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/swenson/sort>
  - <https://github.com/swenson/sort/commits>
  - <https://raw.githubusercontent.com/swenson/sort/HEAD/README.md>
  - <https://raw.githubusercontent.com/swenson/sort/HEAD/demo.c>
  - <https://raw.githubusercontent.com/swenson/sort/HEAD/Makefile>
  - <https://raw.githubusercontent.com/swenson/sort/HEAD/benchmark.c>
- **Sources the enricher read:**
  - <https://github.com/swenson/sort>
  - <https://github.com/swenson/sort/commits>
  - <https://github.com/swenson/sort/commits/HEAD/README.md>
  - <https://github.com/swenson/sort/issues?q=is%3Aissue>
  - <https://github.com/swenson/sort/issues/62>
  - <https://github.com/swenson/sort/issues/85>
  - <https://github.com/swenson/sort/issues/86>
  - <https://github.com/swenson/sort/issues/89>
  - <https://github.com/swenson/sort/issues/39>
  - <https://github.com/swenson/sort/pulls?q=is%3Apr>
  - <https://github.com/swenson/sort/pull/63>
  - <https://github.com/swenson/sort/pull/84>
  - <https://github.com/swenson/sort/pull/84/files>
  - <https://raw.githubusercontent.com/swenson/sort/HEAD/README.md>
  - <https://raw.githubusercontent.com/swenson/sort/HEAD/sort.h>
  - <https://raw.githubusercontent.com/swenson/sort/HEAD/sort_extra.h>
  - <https://raw.githubusercontent.com/swenson/sort/HEAD/demo.c>
  - <https://raw.githubusercontent.com/swenson/sort/HEAD/benchmark.c>
  - <https://raw.githubusercontent.com/swenson/sort/HEAD/stresstest.c>
  - <https://raw.githubusercontent.com/swenson/sort/HEAD/multidemo.c>
  - <https://raw.githubusercontent.com/swenson/sort/HEAD/Makefile>
  - <https://raw.githubusercontent.com/swenson/sort/HEAD/.github/workflows/test.yml>
  - <https://raw.githubusercontent.com/swenson/sort/47934fc724f14795ce9f1a11e04703b37ece6614/README.md>
  - <https://raw.githubusercontent.com/swenson/sort/47934fc724f14795ce9f1a11e04703b37ece6614/demo.c>
  - <https://raw.githubusercontent.com/swenson/sort/47934fc724f14795ce9f1a11e04703b37ece6614/sort.h>
  - <https://raw.githubusercontent.com/swenson/sort/47934fc724f14795ce9f1a11e04703b37ece6614/Makefile>
  - <https://raw.githubusercontent.com/swenson/sort/8a036f197c5b155bf19380df608fd1ca2cc54fba/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/swenson/sort`) · [data/wave1/enrich/raw/github_com_swenson_sort.json](../../../data/wave1/enrich/raw/github_com_swenson_sort.json) (enrichment confidence 0.8)

</details>
