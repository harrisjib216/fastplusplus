# Ultra-Sort (SIMD sorting DSL for AVX2 and AVX-512)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> 2018 course-project AVX-512/AVX2 bitonic merge sort for power-of-two numeric arrays; 7.7x std::sort on 1M 32-bit ints in its own report.

| | |
|---|---|
| **Beats** | std::sort (also std::stable_sort, ips4o::sort, pdqsort) |
| **Claimed result** | Project report Table 4 (1M elements, 32-bit int, single core, Xeon Silver 4114): avx512::sort 0.010364 s vs std::sort 0.080234 s (Table 2 states 7.741558x); same table: ips4o 0.035442 s, pdqsort 0.036089 s, avx256::sort 0.019070 s. Table 7 (1024 elements, 32-bit int): 5.689899x std::sort. At the report's '10M' rows (actually 2^24 = 16.8M elements) avx512::sort is only about 1.9x std::sort and sequential ips4o beats it on 7 of 8 settings (32-bit int 0.0755 s vs 0.284 s, derived from page data). Report: 'best-cast speedup of 8x on single-core and 17x on multicore AVX512' (multicore numbers shown only in a figure). |
| **Workload** | gtest cases in test/avx512/simd_sort_test.cpp sort uniform random values from [-10000, 10000] (LO/HI in test/include/test_util.h, so 1M inputs hold heavy duplicates); each algorithm is timed once per case with currentSeconds() on a copy of the same input; the checked-in NNUM is 65536, so the report's 1M (2^20), 1024 and 10M runs required editing it; N must be a power of 2. Settings: 32/64-bit int and float keys and key-value pairs, single core via OMP_NUM_THREADS=1. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Silver 4114 at 2.20 GHz, 40 logical CPUs, L3 14080 KB (Skylake-SP, AVX-512) |
| **Compiler and flags** | Report: 'compile with flag -O3 -flto'; CMakeLists: -g -O3 -flto -Wall -march=native -fopenmp; compiler vendor and version not stated |
| **Adoption** | 31 stars |
| **Last commit** | 2019-01-11 |
| **Links** | [repository](https://github.com/PatwinchIR/ultra-sort) · [benchmark](https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/reports/ProjectReport.pdf) |

## Verdict

In the authors' gtest harness on a Xeon Silver 4114 (Skylake-SP), built with -O3 -flto -march=native by an unnamed compiler and standard library, one thread, one timed run each: 2^20 32-bit ints from [-10000, 10000] sorted in 10.4 ms by avx512::sort vs 80.2 ms for std::sort (7.7x), 36.1 ms for pdqsort and 35.4 ms for sequential ips4o. The gain shrinks to 1.9x std::sort at 2^24 elements, where ips4o is 3.8x faster than avx512::sort, and 64-bit key-value sorts lose to std::sort at both sizes.

## Use it when

- Studying or porting a compact AVX-512 bitonic sort-and-merge implementation, including masked key-value networks; the report explains each building block
- Sorting power-of-two batches of plain 32-bit ints or floats that already sit in 64-byte-aligned buffers on an AVX-512 x86-64 machine, where the report shows 5.7x (1024 elements) to 7.7x (2^20 elements) over std::sort
- Experiments where a data-oblivious, branch-free sort is wanted, since the network does the same work whatever the input order
- As a baseline to compare a newer SIMD sort against, not as a production dependency

## Skip it when

- Arbitrary sizes: N must be a power of two and the code only asserts N % 256 == 0, so other sizes read and write past the end (issue #1, open since 2018, reports reads past a 2,000,000-float array)
- Large arrays: in the report's own 2^24-element ('10M') AVX-512 table it is only 1.9x std::sort on 32-bit ints, slower than std::sort on 64-bit ints, 32-bit and 64-bit int key-value pairs and 64-bit float pairs, and sequential ips4o beats it on 7 of 8 settings (32-bit ints 0.0755 s vs 0.284 s)
- 64-bit key-value pairs: slower than std::sort at 2^20 (0.107 s vs 0.085 s for int64 pairs) and far behind ips4o
- Production code: unmaintained since May 2018 (later commits only added a licence), leaks a full-size buffer on every call, needs -march=native at build time with no runtime CPU dispatch, and has no NaN handling documented for float keys
- Records or custom comparators: only built-in numeric keys, ascending order, one key column

## How it is fast

Phase 1 loads 16 ZMM registers (a 256-element block of 32-bit keys, or 8 registers of 64-bit keys), runs a branch-free bitonic sorting network across registers with vector min/max, then an in-register 16x16 transpose leaves sorted runs of 16 (8 for 64-bit). Phase 2 runs log2(N/16) out-of-place merge passes, each merging two runs a register at a time with an in-register bitonic merge network into a ping-pong buffer (the Chhugani et al. / Kim et al. 2009, Balkesen 2013 and Inoue 2015 approach the report cites). Key-value pairs use masked compares on the key lanes and blends that move each value with its key; 32-bit int pairs are packed into one int64 and sorted as int64. The merge-pass loop carries an OpenMP parallel for, which is the multicore mode.

## Compared with alternatives

Pick Highway vqsort or numpy/x86-simd-sort for real AVX-512 sorting: they take any length, dispatch at run time and are maintained; pick IPS4o for large or duplicate-heavy inputs, which beat Ultra-Sort at 2^24 in Ultra-Sort's own report. Ultra-Sort is only the better choice as a small, readable reference for bitonic merge networks and masked key-value sorting.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | OpenMP (omp.h is included by common.h; code is built with -fopenmp); GoogleTest, ips4o and pdqsort only for the bundled tests |
| **Minimum toolchain** | C++14 (CMAKE_CXX_STANDARD 14), CMake 3.5, a GCC- or Clang-style compiler providing x86intrin.h and -march=native; tested compiler and version not documented |
| **Platforms** | x86-64 only: AVX-512F for avx512::SIMDSort, AVX2 for avx2::SIMDSort, selected at compile time by __AVX512F__/__AVX2__ |
| **Thread safety** | not documented; no global mutable state, but every merge pass opens an OpenMP parallel region, so the README tells users to set OMP_NUM_THREADS=1 for single-core use |
| **Drop-in for the baseline** | no |

## Gotchas

- Pointer-swapping API: MergeRuns swaps the caller's pointer with an internal posix_memalign buffer after each pass, so when the pass count is odd (int64 or double at 2^20: 17 passes; at the default test size 65536: 13) the caller's pointer comes back pointing at a new buffer, the original memory holds the second-to-last pass and is no longer referenced; the other buffer is never freed, so every call leaks N elements (key-value paths leak two buffers of 2N)
- Loads and stores dereference __m512i pointers directly, which compiles to aligned moves: input must be 64-byte aligned (the tests use posix_memalign through aligned_init) or the program faults; the harness then releases these buffers with delete, which is undefined behaviour
- Min/max, load/store and network helpers are ordinary functions in separate .cpp files, so the measured speed depends on -flto inlining them across translation units, as in the report's -O3 -flto build
- Benchmark harness: single-shot currentSeconds() timings with inputs seeded from std::random_device; integer inputs are drawn from only 20,001 values ([-10000, 10000]), which flatters duplicate-aware comparison sorts at 2^24 (std::sort 0.545 s on ints vs 1.76 s on floats) and makes the 1M-int win the best case; the report's '10M' rows are actually 2^24 = 16.8M elements

## Known shortcomings

- No compiler name, single-shot timings on inputs from [-10000,10000]; the report tables have copy errors (identical IPC tables, Table 3 vs 4 conflict); slower than std::sort on 64-bit key-value, ips4o wins 3 of 8 settings; the 17x multicore claim has no table. Filed under sorting.
- Harness flaws in the code: MergeRuns swaps the caller's pointer each pass, so an odd pass count (int64 and double at 2^20: 17 passes; 65536: 13) returns a new buffer and orphans the caller's array; one N buffer leaks per call (two for key-value); loads are aligned-only; non-power-of-two N reads and writes out of bounds (issue #1, open since 2018). The report's '10M' rows are 2^24: there avx512::sort is only 1.9x std::sort and sequential ips4o beats it on 7 of 8 settings (32-bit int 0.0755 s vs 0.284 s); int inputs have only 20,001 distinct values. Abandoned since May 2018.

## Caveats and trade-offs

Course-project report, not peer reviewed; README speedup chart is an image. Compiler name and version missing (CMakeLists: -g -O3 -flto -Wall -march=native -fopenmp), and the std library tested is not named. Single-shot timings with no repetition. The report's tables contain copy errors: Table 1 (1M IPC) and Table 6 (1024 IPC) are identical, Table 4 gives avx256 and avx512 the same 64-bit int time (0.028105 s) while Table 2 gives them 1.48x and 2.93x, and Table 3's 1M 32-bit key-value times (avx512 0.0337 s slower than avx256 0.0201 s) contradict Table 4 (0.0337 vs 0.0681). Gains are uneven: at 1M the 64-bit key-value int sort (0.106933 s) and 64-bit key-value float sort (0.107151 s) are slower than std::sort (0.085000 s, 0.099286 s), and ips4o (sequential) beats avx512::sort on 3 of 8 settings at 1M (64-bit key-value int 0.044091 s, 32-bit key-value float 0.042667 s, 64-bit key-value float 0.049526 s); in the 10M AVX2 table avx256::sort is only 1.5x std::sort while ips4o is 7.4x. The 17x multicore claim has no table. Harness frees posix_memalign buffers (aligned_init in src/common.cpp) with delete, which is undefined behaviour, and seeds inputs from std::random_device, so runs are not repeatable. Fits wave 1's sorting category better than simd-intrinsics-libraries. [retier] Course-project report, not peer reviewed; README speedup chart is an image; compiler name and version missing (CMakeLists: -g -O3 -flto -Wall -march=native -fopenmp) and the std library is not named; single-shot timings with no repetition, inputs seeded from std::random_device, integer inputs drawn from only 20,001 values ([-10000, 10000]), which flatters duplicate-aware comparison sorts at 2^24 and makes the 1M-int win the best case. The report's tables contain copy errors (Tables 1 and 6 identical; Table 4 gives avx256 and avx512 the same 64-bit int time; Table 3 contradicts Table 4). Code defects: MergeRuns swaps the caller's pointer with an internal posix_memalign buffer after each pass, so with an odd pass count (int64 or double at 2^20: 17 passes; at 65536: 13) the caller's pointer comes back pointing at a new buffer and the original array is orphaned, and every call leaks N elements (two buffers of 2N for key-value); loads and stores dereference __m512i pointers directly (64-byte alignment required or the program faults; the harness frees posix_memalign buffers with delete); non-power-of-two N reads and writes out of bounds (issue #1, open since 2018); the measured speed depends on -flto inlining helpers across translation units. Abandoned since May 2018.

x86-64 AVX2 or AVX-512 only; element count must be a power of two (README); built for course-project scale, no NUMA support; single-thread SIMD sort, optional OpenMP multicore.

## Maintenance

Abandoned: last code commit May 2018 (licence added January 2019), issue #1 about out-of-bounds reads for non-power-of-two sizes still open; MIT-licensed and small enough to vendor for study, but the pointer-swapping, leaking API and missing size checks rule it out for production use without rework.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Course-project report (CMU 15-618, not peer reviewed) with benchmark code in test/avx512/simd_sort_test.cpp, flags (-O3 -flto; CMakeLists adds -march=native -fopenmp) and CPU (Xeon Silver 4114), but no compiler name or version, so first-party C, one step short of A.
- **Verifier notes:** Every number in the record appears in the report PDF. Shortcomings: course project with no compiler version, single-shot timings on a 20001-value domain, table copy errors, slower than std::sort for 64-bit key-value pairs and behind ips4o on 3 of 8 settings at 1M, multicore 17x unsupported by tables, abandoned since 2019. Metadata checked: MIT, 31 stars, last commit 2019-01-11, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-112 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/reports/ProjectReport.pdf>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/README.md>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/test/avx512/simd_sort_test.cpp>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/test/include/test_util.h>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/analysis/analysis.py>
  - <https://github.com/PatwinchIR/ultra-sort>
  - <https://github.com/PatwinchIR/ultra-sort/commits>
  - <https://github.com/PatwinchIR/ultra-sort/tree/master/test>
  - <https://github.com/PatwinchIR/ultra-sort/tree/master/test/avx512>
  - <https://github.com/PatwinchIR/ultra-sort/tree/master/src>
  - <https://github.com/PatwinchIR/ultra-sort/tree/master/analysis>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/src/common.cpp>
- **Sources the enricher read:**
  - <https://github.com/PatwinchIR/ultra-sort>
  - <https://github.com/PatwinchIR/ultra-sort/commits/master>
  - <https://github.com/PatwinchIR/ultra-sort/issues?q=is%3Aissue>
  - <https://github.com/PatwinchIR/ultra-sort/issues/1>
  - <https://github.com/PatwinchIR/ultra-sort/tree/master/src>
  - <https://github.com/PatwinchIR/ultra-sort/tree/master/src/avx512>
  - <https://github.com/PatwinchIR/ultra-sort/tree/master/src/include/avx512>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/README.md>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/reports/ProjectReport.pdf>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/src/common.cpp>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/src/include/common.h>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/src/include/avx512/simd_sort.h>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/src/include/avx512/utils.h>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/src/avx512/simd_sort.cpp>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/src/avx512/merge_util.cpp>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/src/avx512/sort_util.cpp>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/src/avx512/utils.cpp>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/src/include/avx256/simd_sort.h>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/src/avx256/simd_sort.cpp>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/src/avx256/utils.cpp>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/test/avx512/simd_sort_test.cpp>
  - <https://raw.githubusercontent.com/PatwinchIR/ultra-sort/HEAD/test/include/test_util.h>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/patwinchir/ultra-sort`) · [data/wave13/enrich/raw/github_com_patwinchir_ultra_sort.json](../../../data/wave13/enrich/raw/github_com_patwinchir_ultra_sort.json) (enrichment confidence 0.82)

</details>
