# simd-radix-sort (SIMD MSB radix sort with separate key and payload streams)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟡 stale

> AVX-512 in-place binary MSB radix sort for any arithmetic key plus payload arrays; about 2.7-4.1x std::sort on random keys.

| | |
|---|---|
| **Beats** | std::sort (STLSort in the thesis); thesis also compares Intel IPP Radix Sort, Bramas AVX-512 quicksort, Blacher AVX2 quicksort and Moeller's SIMD radix sort |
| **Claimed result** | Thesis Figure 8.16 (int32, Uniform): RadixSIMD 10.16 ns/element vs STLSort 41.87 ns/element (about 4.1x, derived from page data). Figure 8.17 (int32-int32): 11.19 vs 41.94 ns/element (about 3.7x, derived). Figure 8.18 (double, Gaussian): 16.33 vs 44.71 ns/element (about 2.7x, derived). Not the fastest: on int32 Uniform IPPRadix 5.55, BramasSort 3.62 and BlacherSort 2.45 ns/element are all faster than RadixSIMD. |
| **Workload** | Sorting 2^18 elements, time per element, int32 keys with uniform distribution (also int32 key plus int32 payload, and double keys with Gaussian distribution), AVX-512 build. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-12700K at 5 GHz, 32 GB RAM, Manjaro Linux kernel 5.17.15 (AVX-512 enabled; thesis notes Intel does not officially support AVX-512 on Alder Lake) |
| **Compiler and flags** | gcc 12.1.0 (thesis section 7.4); thesis-time Makefile at commit f5ec7f9 (2022-07-14): -std=c++17 -O3 -mavx512f -mavx512bw -mavx512dq -mavx512vl -mavx512vbmi2 with always_inline functions; the current Makefile is -std=c++20 -O3 -mavx512f -mavx512bw -mavx512dq -mavx512vl -mavx512vbmi -mavx512vbmi2 and describes code refactored in December 2023 (54eced8 removed always_inline; radixSort.hpp created 2024-03-12) that was never re-measured. |
| **Adoption** | 15 stars |
| **Last commit** | 2025-01-31 |
| **Links** | [repository](https://github.com/jonicho/simd-radix-sort) · [benchmark](https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/BachelorsThesis_JonasKeller.pdf) |

## Verdict

Keller's July 2022 Bielefeld bachelor's thesis sorted 2^18 uniformly random int32 keys in 10.16 ns/element vs 41.87 for std::sort, which is libstdc++ from gcc 12.1.0 over key-only-compared structs. That is about 4.1x, derived from page data, on an i7-12700K at 5 GHz with AVX-512 enabled. int32+int32 payload measured 11.19 vs 41.94 (about 3.7x) and Gaussian doubles 16.33 vs 44.71 (about 2.7x). Each figure is a CPU-time average of 16 runs with conversions excluded, and the faster IPP, Bramas and Blacher sorts were measured in the same runs.

## Use it when

- Large arrays (around 2^18 elements and up) of uniformly random or Gaussian keys on AVX-512 VBMI2 hardware (Ice Lake and later Xeons, Zen 4/5). The thesis measured int32 at 10.16 vs 41.87 ns/element and float at 11.3 vs 45.43 against std::sort.
- Sorting a key column with one or more payload columns kept in separate arrays (row-id permutations, SoA data), without packing them into structs first. int32 key plus int32 payload: 11.19 vs 41.94 ns/element.
- Narrow keys: uint8 0.5 vs 23.62 ns/element and int16 8.06 vs 41.23 ns/element (uniform, 2^18 elements).
- Key types, payload counts or a descending order that the faster SIMD quicksorts in the thesis do not support. The Bramas sort takes only int/double with at most one same-type payload, and the Blacher sort only int32 with no payload.
- Memory-tight code that cannot afford the O(n) auxiliary buffer of an LSD radix sort, since this sort runs in place.

## Skip it when

- Presorted, reverse-sorted or almost-sorted input, or constant/two-valued keys with payloads or double keys. In appendix B it is slower than std::sort in 19 of 56 cases, for example double Zero 14.37 vs 4.77 and int32 ReverseSorted 5.56 vs 3.02 ns/element.
- When you need the fastest int32/double sort. In the same thesis the Blacher AVX2 quicksort (2.45), the Bramas AVX-512 sort (3.62) and Intel IPP radix sort (5.55) all beat its 10.16 ns/element on int32, and the README itself points to Intel x86-simd-sort as the equally generic alternative.
- Portable binaries or machines without AVX-512 VBMI/VBMI2. There is no scalar fallback and no runtime dispatch, and that excludes Skylake-SP/Cascade Lake Xeons and consumer Alder Lake/Raptor Lake parts with AVX-512 fused off.
- Code that needs std::sort semantics: comparators, iterators, a stable order, or parallel sorting. The sort is single-threaded only; multithreading is listed as future work in thesis section 9.2.5.
- Production use that expects maintenance. It is a 2022 bachelor's-thesis project with 15 stars, no issues ever filed and no releases.

## How it is fast

It is a radix exchange sort (binary MSB radix sort): it recursively partitions the range in place on one key bit at a time, from the most significant bit down, and needs no histogram or scatter buffer. Each partition pass loads 512-bit vectors, tests the bit with a mask-producing test instruction, and writes the 0-bit and 1-bit lanes to the left and right ends with AVX-512 masked compress stores (Bramas-style in-place partition with one cached vector). Every payload array is compress-stored with the same mask, so keys stay dense in registers; when a payload is wider than the key, wider vectors are emulated with several zmm registers. The sign bit and float ordering are handled by flipping the partition direction, and subranges of 16 elements or fewer finish with insertion sort.

## Compared with alternatives

Pick it over avx-512-sort (Bramas) or simd-sort (Mula) when you need key types or layouts they lack: 8/16/64-bit or unsigned integers, float, several payload arrays, or a descending order. For ascending int32/double with at most one same-type payload, Bramas' sort was 2.8x faster in this same thesis (3.62 vs 10.16 ns/element on int32).

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (intrinsics headers only; the benchmark harness optionally uses Intel IPP and vendored Bramas, Blacher and Moeller sorts) |
| **Minimum toolchain** | C++20 (std::bit_cast); GCC with -mavx512f -mavx512bw -mavx512dq -mavx512vl -mavx512vbmi -mavx512vbmi2 per the README (the thesis used gcc 12.1.0); the Makefile also handles clang; MSVC not documented |
| **Platforms** | x86-64 with AVX-512 F/BW/DQ/VL/VBMI/VBMI2 required; POSIX headers (uses ssize_t from sys/types.h) |
| **Thread safety** | not documented; free functions with no global state, so separate arrays can presumably be sorted concurrently, but there is no parallel mode |
| **Drop-in for the baseline** | partial: it sorts the same data but takes (count, key pointer, payload pointers...) instead of iterators and a comparator, only orders arithmetic keys by value (ascending or descending), and is not stable |

## Gotchas

- Cost grows with key width on low-entropy input. Each recursion level is a full SIMD pass on one bit and shared prefix bits are not skipped, so constant or two-valued keys walk all 32 or 64 bits. That is why the Zero, ZeroOne and sorted cases with payloads or double keys lose to std::sort.
- The whole header is wrapped in #ifdef __AVX512F__. Building without the flags makes sort() disappear (a compile error, not a fallback), and a binary built with them faults with an illegal instruction on CPUs lacking VBMI/VBMI2. The thesis machine was an i7-12700K with AVX-512 enabled in the BIOS, which Intel later fused off.
- The measured code is not the shipped header. The thesis numbers come from the 2022-07-14 code (commit f5ec7f9, Makefile -std=c++17 -O3 -mavx512f -mavx512bw -mavx512dq -mavx512vl -mavx512vbmi2, with always_inline functions). The code was refactored in Dec 2023, including commit 54eced8 'Remove always_inline attribute from functions', C++20 and std::bit_cast, and radixSort.hpp was created on 2024-03-12. Nothing was re-measured, so the record's compiler_and_flags line describes the current Makefile, not the thesis build.
- Harness detail (no bug behind the headline numbers found). Each figure averages max(1, 2^22/n) runs (16 at 2^18) after max(1, 2^18/n) warmups (1), not 2^18/n runs. Every dataset defaults to seed time(NULL), so runs generated in the same second sort identical keys even though the thesis says each run gets a new data set. The AoS/SoA conversion is excluded from timing for all methods, and std::sort compares keys only, so the comparison is fair. The perf harness checks only sortedness, and the test program checks key presence but not multiplicity (thesis section 7.6). Floats are tested only with finite values (no NaN, infinity or -0.0).

## Known shortcomings

- Loses to std::sort in 19 of 56 appendix B cases (sorted, reverse-sorted, almost-sorted and some Zero/ZeroOne inputs); IPP, Bramas and Blacher sorts are faster; the Makefile was edited after the thesis (src/perf-thesis.cpp, gcc 12.1.0, i7-12700K, -O3 AVX-512).
- No bug behind the headline numbers; the harness is fair (layout conversion excluded for all methods, std::sort compares keys only). The thesis was built from commit f5ec7f9 (2022-07-14) with -std=c++17 -O3 -mavx512f -mavx512bw -mavx512dq -mavx512vl -mavx512vbmi2 (no VBMI); the code was refactored in December 2023 (54eced8 removed always_inline) and the header created 2024-03-12, never re-measured. Runs average max(1, 2^22/n) iterations (16 at 2^18) after one warm-up; seed time(NULL) gives identical keys across runs in the same second; the appendix's 19 of 56 losses to std::sort are confirmed. Requires VBMI2 (no Skylake-SP or Cascade Lake).

## Caveats and trade-offs

Bachelor's thesis benchmark (not peer reviewed) with the author's own harness (src/perf-thesis.cpp with src/sort_methods.hpp; results written to /tmp). STLSort is std::sort over DataElement structs with std::less; libstdc++ is implied by gcc 12.1.0 on Manjaro, not stated. The Makefile was edited after the thesis (commit 'Add warnings in Makefile', 2023-12-15), so the thesis-time flags are inferred from the current file. Timing uses CLOCK_PROCESS_CPUTIME_ID, averaged over max(1, 2^18/n) runs after warmup runs. The perf harness only checks sortedness (a separate test program checks keys and payloads). The cross-algorithm comparison covers only 2^18 elements. Not faster everywhere: in appendix B RadixSIMD is slower than std::sort in 19 of 56 key/distribution cases, including sorted, reverse-sorted and almost-sorted inputs for int32, int32-int32, float, float-int32 and double, and Zero/ZeroOne inputs with payloads or double keys (for example double Zero 14.37 vs 4.77 ns/element and int32 ReverseSorted 5.56 vs 3.02 ns/element). It is also slower than IPPRadix, BramasSort and BlacherSort on the headline cases; the thesis says most of its time is spent in the comparison sorter. The README says a quicksort variant performed about the same and was not published as a paper, and points to Intel x86-simd-sort as an equally generic alternative. AVX-512 is required (the i7-12700K had it enabled in the BIOS). The IPP rows need the proprietary Intel IPP library. [retier] Bachelor's thesis benchmark (not peer reviewed) with the author's own harness (src/perf-thesis.cpp with src/sort_methods.hpp). The measured code is the 2022-07-14 commit f5ec7f9, not the shipped header (refactored December 2023, never re-measured). STLSort is std::sort over DataElement structs with std::less (libstdc++ implied by gcc 12.1.0 on Manjaro). Each figure averages max(1, 2^22/n) runs (16 at 2^18) after max(1, 2^18/n) warm-ups, timed with CLOCK_PROCESS_CPUTIME_ID; every dataset defaults to seed time(NULL), so runs in the same second sort identical keys. AoS/SoA conversion is excluded for all methods and std::sort compares keys only, so the comparison is fair; the perf harness checks only sortedness and the test program checks key presence but not multiplicity. The cross-algorithm comparison covers only 2^18 elements. Not faster everywhere: in appendix B RadixSIMD loses to std::sort in 19 of 56 key/distribution cases (sorted, reverse-sorted, almost-sorted, Zero and ZeroOne inputs with payloads or double keys) because every recursion level is a full SIMD pass on one bit and shared prefix bits are not skipped; it is slower than IPPRadix, BramasSort and BlacherSort on the headline cases. The header is wrapped in #ifdef __AVX512F__ and needs VBMI2 (no Skylake-SP or Cascade Lake); the thesis i7-12700K had AVX-512 enabled in the BIOS, which Intel later fused off.

x86-64 only and needs AVX-512 F/BW/DQ/VL/VBMI/VBMI2 (the single header must be compiled with those flags); C++20; generic over key and payload types; sorts keys and payload streams separately.

## Maintenance

Stale student project (thesis 2022, single header 2024-03-12, last commit 2025-01-31 adding thesis sources) under MIT and small enough to vendor; its benchmark is a sound same-harness comparison, but it was run on the 2022 code rather than the refactored header now shipped.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The thesis PDF in the repo compares RadixSIMD against STLSort, which src/sort_methods.hpp (SortMethodSTLSort) implements as std::sort with std::less, driven by src/perf-thesis.cpp. It states gcc 12.1.0 and an Intel Core i7-12700K at 5 GHz (section 7.4), and the Makefile gives -std=c++20 -O3 plus the AVX-512 flags, so code, compiler, flags and CPU model are all public.
- **Verifier notes:** The headline numbers in Figures 8.16, 8.17 and 8.18 match the thesis exactly (10.16 vs 41.87, 11.19 vs 41.94 and 16.33 vs 44.71 ns/element). Shortcoming to record: RadixSIMD loses to std::sort on presorted and reverse-sorted inputs and on several constant-key cases (19 of 56 appendix B cases), and on the headline cases it is slower than IPP, Bramas and Blacher sorts. MIT, 15 stars, last commit 2025-01-31 (stale), and not already listed (the catalog lists x86-simd-sort, vxsort and berenger-eu/avx-512-sort separately).
- **Fields the verifier corrected:** `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier batch-109 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/BachelorsThesis_JonasKeller.pdf>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/README.md>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/Makefile>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/src/perf-thesis.cpp>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/src/sort_methods.hpp>
  - <https://github.com/jonicho/simd-radix-sort>
  - <https://github.com/jonicho/simd-radix-sort/commits>
  - <https://github.com/jonicho/simd-radix-sort/tree/main>
- **Sources the enricher read:**
  - <https://github.com/jonicho/simd-radix-sort>
  - <https://github.com/jonicho/simd-radix-sort/commits/main>
  - <https://github.com/jonicho/simd-radix-sort/issues?q=is%3Aissue>
  - <https://github.com/jonicho/simd-radix-sort/tree/f5ec7f988a0a7648bb54dadb3ebc26ce5a0e1d00>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/README.md>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/Makefile>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/radixSort.hpp>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/src/perf-thesis.cpp>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/src/perf.hpp>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/src/sort_methods.hpp>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/src/data.hpp>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/src/common.hpp>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/src/radix_sort.hpp>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/src/cmp_sorters.hpp>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/src/test.cpp>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/src/ipp_radix.hpp>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/HEAD/BachelorsThesis_JonasKeller.pdf>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/f5ec7f988a0a7648bb54dadb3ebc26ce5a0e1d00/Makefile>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/f5ec7f988a0a7648bb54dadb3ebc26ce5a0e1d00/perf.cpp>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/f5ec7f988a0a7648bb54dadb3ebc26ce5a0e1d00/radixSort.hpp>
  - <https://raw.githubusercontent.com/jonicho/simd-radix-sort/f5ec7f988a0a7648bb54dadb3ebc26ce5a0e1d00/lib/data.hpp>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/jonicho/simd-radix-sort`) · [data/wave13/enrich/raw/github_com_jonicho_simd_radix_sort.json](../../../data/wave13/enrich/raw/github_com_jonicho_simd_radix_sort.json) (enrichment confidence 0.86)

</details>
