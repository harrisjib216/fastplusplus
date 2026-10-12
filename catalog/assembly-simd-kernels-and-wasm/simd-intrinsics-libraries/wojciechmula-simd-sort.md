# simd-sort (AVX2 and AVX-512F quicksort, Wojciech Mula)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🔴 abandoned

> Experimental AVX2/AVX-512F quicksorts for 32-bit keys; only Lemire's in-repo AVX2 variant beats std::sort on random data.

| | |
|---|---|
| **Beats** | std::sort (GCC toolchain; version not stated for the valid issue #8 run) |
| **Claimed result** | Repo results/ files (GCC 5.3.0, 2016) print AVX2 quicksort 1.91x vs std::sort at 1M 'random' uint32 on an i7-6700, but those runs sorted already-sorted data (harness bug: speed.cpp sorts input.pointer() in place; issues #7 and #8, open). Independent runs with a fixed harness on random input: issue #8 (bbqz007, 2022-01-22, Tiger Lake, CentOS 8, RDTSC cycles) measured the repo's qs::avx2::quicksort at 0.84x of std::sort at 1M, 0.91x at 10M and 0.92x at 20M (slower), with Daniel Lemire's 'AVX2 alt quicksort' in the same repo faster; issue #3 (simonlindholm, i5-4200U, g++ 5.4 -O3 -march=native, 20 sorts of 1e7) gives qs::avx2 19.476 s vs std::sort 20.209 s (about 1.04x), and rand() % 10 input takes over 10 minutes against 6.654 s (quadratic). |
| **Workload** | Sorting uint32_t arrays of 10k to 20M elements (random() keys, ascending, descending); speed.cpp reports the minimum of N iterations. Valid random-input numbers come only from the issue #8 run with the in-place sorting bug fixed. |
| **Metric** | throughput |
| **Hardware** | Issue #8 valid run: Intel Tiger Lake (model not stated), CentOS 8. Invalid repo results: i7-6700, i7-4770, Xeon Phi 7210. |
| **Compiler and flags** | Repo results files: GCC 5.3.0, Makefile -std=c++11 -mbmi2 -mavx2 (or -mavx512f) -O3 -DNDEBUG, but those runs are invalid (presorted data). Issue #8 fixed-harness run: compiler and flags not stated. |
| **Adoption** | 105 stars |
| **Last commit** | 2017-11-22 |
| **Links** | [repository](https://github.com/WojciechMula/simd-sort) · [benchmark](https://github.com/WojciechMula/simd-sort/issues/8) |

## Verdict

The repo's own results/ files (GCC 5.3.0 on i7-6700, i7-4770 and Xeon Phi 7210, 2016) are invalid because the harness re-sorted presorted data. With the harness fixed, a third party (issue #8, Tiger Lake, CentOS 8, compiler unstated, RDTSC minimum of N runs, random() keys) measured Lemire's AVX2 alt quicksort at 1.61x, 1.77x, 1.82x and 1.85x the speed of libstdc++ std::sort at 1M, 2M, 10M and 20M keys, the nodutch variant at 1.23x to 1.38x, and Mula's qs::avx2::quicksort at 0.84x to 0.92x (slower); an independent run in issue #3 (simonlindholm, i5-4200U, g++ 5.4 -std=c++11 -O3 -march=native, sum of 20 sorts of 1e7 keys) found qs::avx2::quicksort at 19.476 s against std::sort's 20.209 s on random input (about 1.04x, derived from page data) and over 10 minutes against 6.654 s on rand()%10.

## Use it when

- Studying or prototyping SIMD partition schemes: each variant is a few hundred lines of nearly plain C with intrinsics.
- Vendoring a small AVX2-only in-place sort for signed int32 arrays of roughly 10k to 20M elements, using avx2-altquicksort.h: 1.35x to 1.85x faster than std::sort on random keys in the issue #8 Tiger Lake run.
- As an extra contender when benchmarking your own 32-bit sort against std::sort, x86-simd-sort or Highway vqsort.
- Machines with AVX2 but no AVX-512 where adding a larger dependency is not an option and inputs are random rather than adversarial.

## Skip it when

- Production sorting: no introsort depth limit; qs::avx2::quicksort goes quadratic on few distinct keys (issue #1: about 9 s against under 1 s for other variants; issue #3: over 10 minutes against 6.654 s for std::sort on rand()%10 at n = 1e7), and HEAD's qs::avx512::quicksort and bmi2_quicksort take the first element as pivot, so sorted input recurses n deep (issue #4: hang, maintainer: stack runs out).
- uint32_t keys at or above 2^31: every SIMD compare is signed (vpcmpgtd, _mm512_cmp\*_epi32_mask); the Lemire and Nate variants return signed order, and qs::avx2 and qs::avx512 mix signed vector compares with unsigned scalar compares, so mixed-top-bit inputs come out unsorted (code reading; the tests never generate such keys because random() returns values below 2^31).
- Anything other than 32-bit integer keys on x86-64 with GCC or Clang: no 64-bit keys, floats, key-value pairs or comparators, no MSVC (GCC attributes and inline asm), no ARM, no runtime CPU dispatch.
- avx2-nate-quicksort.cpp ('Nate's variant'): out-of-bounds read crash at line 340 on 1M ascending keys (issue #4) and a non-terminating partition loop (issue #10, 2025); the BMI2 AVX-512 variant fails at 50M to 100M items (issue #2).
- When a maintained, faster SIMD sort is acceptable: x86-simd-sort and Highway vqsort (already catalogued) supersede this 2016-2017 code.

## How it is fast

Lemire's alt quicksort compares 8 keys with the pivot in one vpcmpgtd, turns the result into an 8-bit mask with movmskps, and loads a permutation from a 256-entry table so vpermd packs the 'not greater' lanes to the front; it then stores whole vectors and advances by the popcount, a branchless Lomuto-style vector partition. Mula's qs::avx2 partition loads one vector from each end, pairs misplaced lanes with ctz loops (align_masks) and swaps them in registers, with a scalar Hoare partition for the remainder. The AVX-512F versions use mask compares and a rank-based in-register sort (avx512_sortN_epi32: permutexvar broadcast, cmplt/cmpeq popcounts, masked move) for small partitions.

## Compared with alternatives

Rarely: Bramas's avx-512-sort (AVX-512 quicksort with bitonic small-array sorts, about 4x over GNU sort in its paper) and jonicho/simd-radix-sort (about 4.1x over std::sort on uniform int32 in its thesis) are better evidenced and more complete. Pick avx2-altquicksort.h only when you need a tiny AVX2-only (no AVX-512) in-place sort for signed int32 data and cannot take x86-simd-sort or vqsort.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond &lt;x86intrin.h&gt;; the headers expect FORCE_INLINE from common.h and scalar_partition_epi32 from partition.cpp, so copy those too |
| **Minimum toolchain** | GCC 5.3.0 or newer per the README; Makefile uses -std=c++11 -mbmi2 plus -mavx2 or -mavx512f and -O3 -DNDEBUG for the speed binary; Clang should work (GCC-style builtins), MSVC is not supported |
| **Platforms** | x86-64 only: AVX2 (the Makefile also passes -mbmi2) for the AVX2 variants, AVX-512F for the AVX-512 variants (the README suggests Intel SDE to run them without hardware) |
| **Thread safety** | not documented; most routines touch only the caller's buffer and read-only lookup tables, but Nate's variant partitions through a function-static tmp buffer (not reentrant) and WITH_RUNTIME_STATS builds update global counters |
| **Drop-in for the baseline** | partial — sorts a raw uint32_t buffer given inclusive int bounds instead of iterators, has no comparator, caps sizes at INT_MAX elements, and the fast Lemire variant gives signed int32 order |

## Gotchas

- Benchmark harness bug: speed.cpp's PerformanceTest::run memcpy's the input into tmp but sorts input.pointer() in place, so after std::sort's first iteration every timed run (and every later algorithm) sorts presorted data; the results/ 'random' rows are presorted-data times (issues #7 and #8, open). The same file gates the scalar 'quick sort' row on the -std-qsort flag instead of -quicksort, and the measured RDTSC overhead is printed but never subtracted.
- Signedness defect (code reading, not run): vector compares are signed _epi32 while partition.cpp's scalar fallback and the size-2 case compare as uint32_t, so qs::avx2::quicksort and the qs::avx512 sorts misorder arrays that mix keys below and above 2^31; the Lemire and Nate wrappers cast to int32_t and return signed order. The test program only uses random(), small ascending/descending values and random() % 10, so it cannot catch this.
- Out-of-bounds access (code reading): for partitions of 16 or fewer keys, qs::avx512::quicksort and popcnt_quicksort do an unmasked 64-byte _mm512_loadu_si512 and _mm512_storeu_si512 at array + i, so the last partition reads and rewrites up to 60 bytes past the end of the caller's buffer (same bytes written back, but undefined behaviour that can fault at a page boundary); pad buffers by 64 bytes if you use them.
- Worst cases are unguarded: middle-element or first-element pivots, no median-of-three, no depth limit and recursion on both sides, so adversarial, few-distinct or (for the AVX-512 variants) sorted inputs can be quadratic and exhaust the stack.

## Known shortcomings

- speed.cpp sorts the shared input in place (the tmp copy is unused), so the 'random' rows measured presorted data (random equals ascending within 1% on all 3 CPUs; open issues #7, #8); a fixed third-party run (issue #8, Tiger Lake, no compiler stated) has qs::avx2::quicksort at 0.84-0.92x std::sort (slower) while Lemire's avx2-altquicksort reaches 1.61-1.85x. Not faster on the corrected run.
- Harness bug confirmed: speed.cpp sorts input.pointer() in place, so the results/ files are presorted-data times. Code-reading defects (not run): all SIMD compares are signed (_epi32); the Lemire and Nate variants return signed int32 order; qs::avx2 and qs::avx512 mix signed vector compares with unsigned scalar ones, so keys at or above 2^31 come out misordered (tests use random() &lt; 2^31 and cannot catch it); AVX-512 partitions of 16 or fewer keys do unmasked 64-byte loadu/storeu, reading and rewriting up to 60 bytes past the buffer; the HEAD AVX-512 quicksort uses a first-element pivot; the scalar 'quick sort' row is gated on -std-qsort. Extra evidence: issue #3 (simonlindholm, i5-4200U, g++ 5.4 -O3 -march=native, 20 sorts of 1e7): qs::avx2 19.476 s vs std::sort 20.209 s (about 1.04x), and rand() % 10 takes over 10 minutes against 6.654 s (quadratic).

## Caveats and trade-offs

Harness bug: PerformanceTest::run copies the input to tmp and then sorts input.pointer() in place, and all algorithms share one InputData, so after std::sort's first iteration every timed run sorted presorted data; the results/ 'random' and 'ascending' rows are the same within 1% for every algorithm on Skylake, Haswell and Knights Landing (std::sort 12.3 ms for 1M 'random' keys on an i7-6700 is a presorted-data time). Reported in issue #7 (2021) and issue #8 (2022), both still open; the 2017 fix for issue #5 only corrected a t1/t2 typo in the gettimeofday branch. Once fixed, the headline AVX2 quicksort is slower than std::sort on random data; only Lemire's alternative AVX2 quicksort (a file in this repo that its own comment calls 'not meant to be fast as such') and the nodutch variant win. The AVX-512 implementation was fixed on 2017-01-28, after the September 2016 Knights Landing results. Open issue #10 (2025) reports a never-ending loop and access violation in avx2-nate-quicksort.cpp; open issue #2 reports the AVX512+BMI2 variant failing on large inputs. Research code (README: 'still unfinished'), last commit 2017-11-22; superseded by x86-simd-sort and Highway vqsort, which are already catalogued. [retier] Harness bug: PerformanceTest::run copies the input to tmp and then sorts input.pointer() in place, and all algorithms share one InputData, so after std::sort's first iteration every timed run sorted presorted data; the results/ 'random' and 'ascending' rows are the same within 1% for every algorithm (issues #7 and #8, open); the scalar 'quick sort' row is gated on -std-qsort. With the harness fixed, independent runs show the repo's AVX2 quicksort at about 0.84x-1.04x of std::sort on random uint32 and quadratic on few-distinct input; only Lemire's alt variant in the same repo is faster. Code-reading defects (not run): all SIMD compares are signed (_epi32) while partition.cpp's scalar fallback and the size-2 case compare as uint32_t, so qs::avx2 and the qs::avx512 sorts misorder arrays that mix keys below and above 2^31 (the Lemire and Nate wrappers return signed int32 order; tests use random() &lt; 2^31 and cannot catch it); for partitions of 16 or fewer keys the AVX-512 sorts do unmasked 64-byte loadu/storeu, reading and rewriting up to 60 bytes past the caller's buffer; middle- or first-element pivots with no median-of-three, no depth limit and recursion on both sides, so adversarial, few-distinct or (for AVX-512) sorted inputs can be quadratic and exhaust the stack.

x86 only; needs AVX2 or AVX-512F (and BMI2 for some variants); uint32_t keys only; no runtime dispatch; not stable; README calls the code unfinished.

## Maintenance

Abandoned since 2017-11-22 (the last commit only fixed a t1/t2 typo in the gettimeofday branch), BSD-2-Clause and small enough to vendor, but research code with an invalid benchmark harness, signed-compare and out-of-bounds defects found in code reading, and quadratic worst cases; the issue #3 run, which the verifier did not cite, confirms the headline AVX2 quicksort is only at parity with std::sort on random data and collapses on few distinct keys.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** The results/ files print the claimed ratios, but speed.cpp (both at the results commit 099ef75 of 2016-09-25 and at HEAD) memcpy's the input into tmp and then sorts the shared input buffer in place, so every repeat and every algorithm after std::sort's first iteration sorted already-sorted data: the 'random' rows match the 'ascending' rows within 1% on all three machines, and the bug is reported in open issues #7 and #8. The only valid random-input numbers are a third party's fixed-harness run in issue #8 (Tiger Lake, compiler and flags not stated, fix not published), which is tier C at most.
- **Verifier notes:** Downgrade A to C: the repo's own results are invalid evidence for random-input sorting (presorted data via the in-place harness bug, issues #7 and #8), and the claimed AVX2 quicksort is 0.84x to 0.92x of std::sort once fixed; keep the entry on the strength of the issue #8 third-party run where the in-repo Lemire AVX2 alt quicksort is 1.61x to 1.85x faster. If the orchestrator prefers, this fits the 'no valid measurement from the project' pattern; the issue #8 numbers are the only valid ones. BSD-2-Clause, 105 stars, abandoned (last commit 2017-11-22) confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-75 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/WojciechMula/simd-sort>
  - <https://github.com/WojciechMula/simd-sort/commits/master>
  - <https://github.com/WojciechMula/simd-sort/commits/master/speed.cpp>
  - <https://github.com/WojciechMula/simd-sort/commits/master/results>
  - <https://github.com/WojciechMula/simd-sort/commit/8067f42>
  - <https://github.com/WojciechMula/simd-sort/tree/master/results>
  - <https://github.com/WojciechMula/simd-sort/issues?q=is%3Aissue>
  - <https://github.com/WojciechMula/simd-sort/issues/5>
  - <https://github.com/WojciechMula/simd-sort/issues/7>
  - <https://github.com/WojciechMula/simd-sort/issues/8>
  - <https://github.com/WojciechMula/simd-sort/issues/10>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/README.rst>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/Makefile>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/speed.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/input_data.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/avx2-altquicksort.h>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/results/skylake-i7-6700-gcc5.3.0-avx2.txt>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/results/haswell-i7-4770-gcc5.3.0-avx2.txt>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/results/knights-landing-7210-gcc5.3.0-avx512f.txt>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/099ef75/speed.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/099ef75/gettime.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/099ef75/input_data.cpp>
- **Sources the enricher read:**
  - <https://github.com/WojciechMula/simd-sort>
  - <https://github.com/WojciechMula/simd-sort/commits/master>
  - <https://github.com/WojciechMula/simd-sort/issues?q=is%3Aissue>
  - <https://github.com/WojciechMula/simd-sort/issues/1>
  - <https://github.com/WojciechMula/simd-sort/issues/2>
  - <https://github.com/WojciechMula/simd-sort/issues/3>
  - <https://github.com/WojciechMula/simd-sort/issues/4>
  - <https://github.com/WojciechMula/simd-sort/issues/8>
  - <https://github.com/WojciechMula/simd-sort/issues/10>
  - <https://gist.github.com/simonlindholm/7f15e1c4d61813eeaa99ff71f1ada1a0>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/README.rst>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/Makefile>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/speed.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/test.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/input_data.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/rdtsc.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/gettime.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/common.h>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/cmdline.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/quicksort-all.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/quicksort.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/partition.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/avx2-partition.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/avx2-quicksort.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/avx2-altquicksort.h>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/avx2-nate-quicksort.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/avx2-natenodutch-quicksort.h>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/avx512-quicksort.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/avx512-partition.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/avx512-bmi2-partition.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/avx512-popcnt-partition.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/avx512-auxbuffer-partition.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/avx512-swap.cpp>
  - <https://raw.githubusercontent.com/WojciechMula/simd-sort/HEAD/avx512-sort-register.cpp>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/wojciechmula/simd-sort`) · [data/wave13/enrich/raw/github_com_wojciechmula_simd_sort.json](../../../data/wave13/enrich/raw/github_com_wojciechmula_simd_sort.json) (enrichment confidence 0.85)

</details>
