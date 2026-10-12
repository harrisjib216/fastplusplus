# vectorized_find (AVX2 find experiments)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟡 stale

> Personal AVX2 experiment: a 2x-unrolled cmpeq/movemask find for int and float, about 3.2x std::find on 4096 L1-resident ints.

| | |
|---|---|
| **Beats** | std::find on a raw array and on std::vector (plus a naive loop) |
| **Claimed result** | README table (4096 int elements, target in the last slot, G-elements/s, rounded, compiler unstated): std::find on a raw array about 7.7 and on std::vector about 8.1 vs FIND_IntrinsicFind (AVX2 cmpeq + movemask, 2x unrolled) about 24.9, about 3.2x over raw-array std::find (derived from page data), and FIND_IntrinsicFloatFind about 25.3; naive loop about 4.6. The FIND_Intrinsic2Find row (about 49.7) and the compare_find row (about 32.2) are struck: both are full-array counts with no early exit (lower_bound semantics on sorted input, not std::find), Intrinsic2's reduction returns twice the sum of lanes 0-3 and ignores lanes 4-7 (4096 instead of 4095 on the benchmark input), and compare_find's counter starts at -1 (4094). The archived docs/perf_results/results.txt gives IntrinsicFind/4096 at 21.06 G/s, not about 24.9. |
| **Workload** | Worst-case search (target at the end) over 4096 int elements, Google Benchmark, billions of elements per second. |
| **Metric** | throughput |
| **Compiler and flags** | CMakeLists: GCC -mtune=native -march=native -mavx2 -Ofast -funroll-loops -ftree-vectorize; Clang -O3 -ffast-math ...; compiler used for the table not stated |
| **Adoption** | 0 stars |
| **Last commit** | 2025-09-29 |
| **Links** | [repository](https://github.com/sbstndb/vectorized_find) · [benchmark](https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/README.md) |

## Verdict

With Google Benchmark on an unnamed machine whose perf stat output shows 24 CPUs, an unstated compiler and standard library (CMake flags: GCC -Ofast -march=native -funroll-loops, or Clang -O3 -ffast-math), searching 4096 ints with the target in the last slot: the AVX2 intrinsic_find runs at \~24.9 G-elements/s against std::find at \~7.7 (raw pointer) and \~8.1 (std::vector), about 3.2x (derived from page data). The 49.7 G-elements/s Intrinsic2Find headline is a buggy full-array count, not a find, and is not a valid speedup.

## Use it when

- As a compact reading example of the cmpeq + movemask + ctz find idiom for 32-bit int or float on an AVX2 x86-64 machine.
- Repeated scans of short-to-medium unsorted int32 or float arrays (up to a few thousand elements, L1-resident, which is all the benchmark covers) when your toolchain is GCC with libstdc++, whose std::find for 4-byte types is scalar.
- As a starting harness for benchmarking your own find kernel; the Google Benchmark file is short and easy to extend.

## Skip it when

- Buffers whose length is not a multiple of 16: there is no tail loop, so intrinsic_find reads up to 15 elements past the end and can return an out-of-range index if that stray memory holds the target.
- With libc++ on Linux or with MSVC STL: libc++ routes std::find on 4-byte trivially comparable types to wmemchr (glibc has an AVX2 wmemchr) and MSVC STL dispatches to the vectorized __std_find_trivial_4, so the 3.2x baseline gap does not carry over; the repo never measured those standard libraries.
- Non-x86, pre-AVX2 CPUs or MSVC builds: it uses AVX2 intrinsics, the GCC/Clang-only __m256i_u type and __builtin_ctz, with no scalar fallback or runtime dispatch.
- Sorted lower_bound-style searches: the Intrinsic2Find and CompareFind variants look like that but return wrong counts (see gotchas); use std::lower_bound or a tested branchless search instead.
- Production code in general: no licence, no tests, 0 stars, int sizes rather than size_t, and only int and float overloads.

## How it is fast

It broadcasts the target with _mm256_set1_epi32 (or _mm256_set1_ps), loads two unaligned 256-bit chunks (16 elements) per iteration, compares with _mm256_cmpeq_epi32 (or _mm256_cmp_ps), collapses each comparison with movemask and finds the hit with __builtin_ctz; the 2x unroll was tuned on the author's CPU. That is one branch per 16 elements, against libstdc++'s std::find for int, which is a scalar `#pragma GCC unroll 4` loop (libstdc++ only switches to memchr for 1-byte types). The even faster Intrinsic2Find and CompareFind rows drop the early exit and count elements below the target over the whole array, which is a different algorithm, not a faster find.

## Compared with alternatives

FastArrayOps (komrad36) covers contains/find for 8- to 64-bit integers and float/double, reports about 12x on 32-bit ints and is the better source to copy; libhat and the Rust memchr crate cover byte-pattern and substring search. Pick vectorized_find only as a minimal, readable AVX2 int32/float find to study or adapt (after adding a tail loop). If you only need a faster std::find for int, moving to libc++ or MSVC STL gives a vectorized std::find with no new code.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the find functions; Google Benchmark (find_package(benchmark REQUIRED)) for the benchmark executable |
| **Minimum toolchain** | C++17 (CMAKE_CXX_STANDARD 17); CMakeLists requires CMake 3.24 although the README says 3.28; GCC or Clang with AVX2 support |
| **Platforms** | x86-64 with AVX2 only; the build uses -march=native -mavx2 |
| **Thread safety** | not documented; the functions only read the array and keep no shared state, so concurrent calls on read-only data are safe by inspection |
| **Drop-in for the baseline** | partial — different signature (int\* or float\*, int size, value), returns -1 instead of last on a miss, only int and float overloads, and the length must be a multiple of 16 to avoid over-reading |

## Gotchas

- Over-read: intrinsic_find always loads 16 elements per step with no tail loop. The benchmark itself bumps sizes 2 and 4 up to 8 and then reads 8 ints past an 8-int malloc at sizes 2, 4 and 8; it also counts 8 items processed for the 2- and 4-element cases, which inflates the small-size throughput rows of the intrinsic variants.
- The \~49.7 G-elements/s headline row (intrinsic2_find) is not a find. It counts elements below the target over the whole array (equal to lower_bound only on sorted input), and its reduction, _mm256_extract_epi32(sum,0) + _mm256_extract_epi32(sum,1) after two in-lane _mm256_hadd_epi32, returns twice the sum of lanes 0-3 and ignores lanes 4-7. On the benchmark input (4095 zeros, then the target) it returns 4096 instead of 4095. No benchmark checks the returned index, so the bug went unnoticed.
- compare_find (the \~32.2 G-elements/s row, which already beats the AVX2 find) is a branchless count with no early exit that GCC auto-vectorizes. Its counter starts at -1, so on the benchmark input it returns 4094 instead of 4095, off by one even as a lower_bound. Its worst-case speed says nothing about inputs where the target appears early.
- Harness limits: every row is a worst case on an all-zero array of at most 4096 ints (16 KiB, L1-resident) that is rescanned in a loop, and no result is validated. The std::find array is 64-byte aligned via aligned_alloc while the intrinsic arrays use malloc. The README's std::find and Intrinsic2 rows have no raw output in the repo, and the archived docs/perf_results/results.txt (older BM_ names) gives IntrinsicFind/4096 at 21.06 G/s, not \~24.9.

## Known shortcomings

- Real claim is IntrinsicFind about 3.2x std::find (24.9 vs 7.7, derived); the Intrinsic2Find 49.7 row is not a valid speedup (full-scan count with lower_bound semantics and a reduction bug returning twice the sum of lanes 0-3, 4096 instead of 4095); intrinsic_find reads past the buffer for sizes not divisible by 16; no CPU, compiler unstated; no licence (reference).
- Harness flaws: the \~49.7 G-elements/s Intrinsic2Find headline is a full-array count whose reduction returns 4096 instead of 4095; compare_find (the \~32.2 row) is off by one (counter starts at -1, returns 4094); intrinsic_find has no tail loop and over-reads, and the small-size rows count 8 items; nothing validates results; the 16 KiB array is L1-hot only. The 3.2x holds only against libstdc++'s scalar std::find (libc++ routes it to wmemchr, the MSVC STL to __std_find_trivial_4).

## Caveats and trade-offs

Personal experiment with no licence file and no hardware stated. The archived docs/perf_results/results.txt is an older run (BM_ names, no CPU header; perf stat files show 24 CPUs only) that has no std::find or Intrinsic2 rows and gives IntrinsicFind/4096 at 21.06 G/s and NaiveFind/4096 at 4.48 G/s, lower than the README's \~24.9; the README's std::find numbers have no raw output in the repo. intrinsic2_find (src/intrinsics/intrinsic_find.cpp) counts elements less than the target with no early exit (a lower_bound on sorted input, not std::find semantics) and its reduction returns _mm256_extract_epi32(sum,0)+_mm256_extract_epi32(sum,1), which is twice the sum of lanes 0-3 and ignores the upper 128-bit half; on the benchmark input (4095 zeros then the target) it returns 4096 instead of 4095. intrinsic_find has no tail loop: it always reads 16 elements per step, so sizes that are not a multiple of 16 read past the buffer (the benchmark rounds sizes 2 and 4 up to 8 and then reads 8 ints beyond the malloc). Both sides are compiled with -Ofast -march=native (GCC) or -O3 -ffast-math (Clang); the std::find side is compiled with the same flags, but which standard library was used is not stated. Numbers are rounded ('\~'). [retier] Personal experiment with no licence file and no hardware stated; the archived docs/perf_results/results.txt is an older run with different names and lower numbers, and the README's std::find rows have no raw output in the repo. Harness flaws: intrinsic_find always loads 16 elements per step with no tail loop, so the benchmark bumps sizes 2 and 4 up to 8, reads 8 ints past an 8-int malloc at sizes 2, 4 and 8, and counts 8 items processed for the 2- and 4-element cases (inflating the small-size rows); every row is a worst case on an all-zero 16 KiB L1-resident array rescanned in a loop; no result is validated; the std::find array is 64-byte aligned via aligned_alloc while the intrinsic arrays use malloc. The 3.2x holds only against libstdc++'s scalar std::find: libc++ routes int find to wmemchr and the MSVC STL to __std_find_trivial_4, both vectorised.

AVX2 only; fixed 4096-element size in the quoted table; Intrinsic2Find has lower_bound semantics on a sorted array rather than a plain find.

## Maintenance

Stale personal experiment (35 commits, last on 2025-09-29, 0 stars, no issues) with no licence file, so it is reference-only: learn the idiom, do not vendor the code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Google Benchmark code is public (src/benchmarks/benchmarks.cpp, std::find in src/cpp_stl/cpp_stl_find.cpp) and the README table compares against std::find on a raw array and on std::vector, but no CPU model is stated, the compiler used for the table is not named (CMakeLists.txt has separate GCC and Clang flag sets) and the README figures are rounded with no raw output for the std::find rows, so it falls short of A.
- **Verifier notes:** Real comparison against std::find; keep at C with the 3.2x IntrinsicFind figure as the claim. New finding: the headline 49.7 G-elements/s Intrinsic2Find row is a different algorithm (full-scan count, lower_bound semantics) whose horizontal reduction is buggy (returns 2x the lanes 0-3 count, 4096 instead of 4095 on the benchmark input), so the 6.5x figure must not be presented as a speedup; intrinsic_find over-reads for sizes not divisible by 16. Metadata checked: no licence (reference), 0 stars, 35 commits, last commit 2025-09-29 (stale), not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-113 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/README.md>
  - <https://github.com/sbstndb/vectorized_find>
  - <https://github.com/sbstndb/vectorized_find/commits>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/src/benchmarks/benchmarks.cpp>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/src/intrinsics/intrinsic_find.cpp>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/src/cpp_stl/cpp_stl_find.cpp>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/src/utils/utils.cpp>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/src/naive/naive_find.cpp>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/src/compare/compare_find.cpp>
  - <https://github.com/sbstndb/vectorized_find/tree/main/docs/perf_results>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/docs/perf_results/results.txt>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/docs/perf_results/intrinsic_perf.txt>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/docs/perf_results/naive_perf.txt>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/docs/perf_results/nobreak_perf.txt>
- **Sources the enricher read:**
  - <https://github.com/sbstndb/vectorized_find>
  - <https://github.com/sbstndb/vectorized_find/commits>
  - <https://github.com/sbstndb/vectorized_find/issues>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/README.md>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/main.cpp>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/src/benchmarks/benchmarks.cpp>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/src/benchmarks/benchmarks.hpp>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/src/intrinsics/intrinsic_find.cpp>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/src/intrinsics/intrinsic_find.hpp>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/src/cpp_stl/cpp_stl_find.cpp>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/src/cpp_stl/cpp_stl_find.hpp>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/src/utils/utils.cpp>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/src/naive/naive_find.cpp>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/src/compare/compare_find.cpp>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/docs/perf_results/results.txt>
  - <https://raw.githubusercontent.com/sbstndb/vectorized_find/HEAD/docs/perf_results/intrinsic_perf.txt>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/libcxx/include/__algorithm/find.h>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc%2B%2B-v3/include/bits/stl_algobase.h>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc%2B%2B-v3/include/bits/stl_algo.h>
  - <https://raw.githubusercontent.com/microsoft/STL/main/stl/inc/xutility>
  - <https://raw.githubusercontent.com/bminor/glibc/master/sysdeps/x86_64/multiarch/wmemchr-avx2.S>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/sbstndb/vectorized_find`) · [data/wave13/enrich/raw/github_com_sbstndb_vectorized_find.json](../../../data/wave13/enrich/raw/github_com_sbstndb_vectorized_find.json) (enrichment confidence 0.8)

</details>
