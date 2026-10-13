# fastcpp::algo::sort / radix_sort (developer source)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only pdqsort-style quicksort and LSD radix sort; 2.3x libstdc++ std::sort on random int64, 6.6x sorted, loses nearly-sorted.

| | |
|---|---|
| **Beats** | std::sort |
| **Claimed result** | vs std::sort on 1M int64 (results/fastest.json rows, run 2026-09-04-algorithms): 6.63x already-sorted (1.418ms vs 9.403ms), 3.42x few-unique/8 values (6.147ms vs 20.996ms), 2.28x random (24.567ms vs 56.106ms). LOSES 0.93x on almost-sorted/1% swapped (derived from page data: 12.471ms vs 11.640ms; the page records this as std::sort winning 1.07x, 'about 7-10% across runs'). The other three patterns are not in fastest.json. Their exact values come from the message of commit 2fa7d3d, and README.md rounds them: 2.33x sorted+1% appended (README 2.3x), 1.71x sawtooth (README 1.7x), 1.55x reverse-sorted (README 1.6x; the fastest.json note gives 1.55-1.93x after the pivot fix). A pivot-arrangement fix is an internal before/after comparison, not against std::sort: 2.86x on 1M reverse-sorted (3.803ms vs 10.864ms); before the fix fastcpp was 0.55x vs std::sort. radix_sort vs std::sort on random uint64: peaks at 4.30x at n=16,384 (148.5us vs 638.6us) and drops to 2.06x at n=4,194,304, where fastcpp::algo::sort (140.5ms) beats radix (158.2ms). It LOSES around and below the n\~1024 crossover (0.92x at n=1024, 0.23x at n=64). |
| **Workload** | Sort 1M int64 elements across seven input patterns (random, already-sorted, reverse-sorted, almost-sorted with 1% swapped, few-unique/8 values, sawtooth, sorted+1% appended random), gcc 13.3.0 -O3 -march=native -std=c++23; separately, LSD radix_sort vs std::sort on random uint64 from n=64 to n=4,194,304. |
| **Metric** | latency |
| **Hardware** | Intel Xeon @ 2.10GHz, 4 cores (SSE4.2, AVX2, BMI2, AVX-512F/VL, PCLMULQDQ), Ubuntu 24.04, Linux 6.18, shared cloud VM |
| **Compiler and flags** | gcc 13.3.0, -O3 -march=native -std=c++23 (benchmarks force -O3 via fastcpp_bench_opt in root CMakeLists; run label 2026-09-04-algorithms) |
| **Adoption** | 0 stars (private repository, not publicly discoverable) |
| **Last commit** | 2026-09-04 |
| **Links** | private repository, not published yet |

## Verdict

On a 4-core 'Intel Xeon @ 2.10GHz' shared cloud VM with gcc 13.3 -O3 -march=native and libstdc++, the project's own bench_sort.cpp (minimum of 3 samples) timed fastcpp::algo::sort against std::sort on 1M int64: 6.63x on already-sorted input, 3.42x with 8 distinct values, 2.28x on random input and 0.93x (a loss) with 1% swapped; radix_sort against std::sort on random uint64 peaked at 4.30x (n=16,384) and fell to 0.23x at n=64. The appended/sawtooth/reverse ratios (2.33x/1.71x/1.55x) exist only in the commit message and README, not in results/fastest.json, and each timed body includes copying the source array, which pulls all ratios toward 1.

## Use it when

- You sort large arrays of int64 or other cheap-to-copy scalars with std::sort on gcc/libstdc++, and the input is often already sorted (6.63x at 1M), has few distinct values (3.42x with 8 values), or is a sorted array with \~1% new records appended (2.33x).
- Uniformly random 1M-element int64 sorts where you want a near drop-in with the same comparator contract: 2.28x over std::sort, and no extra memory.
- Random uint32/uint64/int32/int64/float/double keys in roughly the 1K-1M range where an extra n-key buffer is affordable: radix_sort measured 4.30x std::sort at 16,384 uint64 and 3.15x at 256K.
- Repeated sorts in a loop, passing radix_sort a reused scratch vector so that one of its two buffers is not reallocated on every call.
- You would rather vendor code than add a dependency. It is four MIT headers that use only the standard library.

## Skip it when

- Nearly sorted data with scattered displacements (1% of positions swapped): std::sort wins by 7-10% (0.93x). The 8-move sorted-run probe fails, and its cost is wasted.
- Move-only or expensive-to-copy element types. The small-sort networks and pivot selection copy-construct both elements on every compare-exchange, and only int64/uint64 were benchmarked.
- radix_sort below about 1K elements (0.23x at n=64, 0.92x at n=1024) or around 4M and above, where fastcpp::algo::sort beats it (140.5 ms vs 158.2 ms). Also not for sorting structs or records by key, for floats that may contain NaN, or when memory is tight (up to 2n extra keys).
- You need numbers for libc++, MSVC STL, clang, -O2 builds or non-x86 hardware. Only gcc 13.3/libstdc++ at -O3 -march=native on one shared Xeon VM was measured, and no one else has reproduced it.
- Adversarial or hostile input. Unlike pdqsort, there is no pattern-breaking shuffle after a lopsided partition, so it depends only on the heapsort fallback. The code is also young: one commit (2026-09-04) in a private, 0-star repo.

## How it is fast

sort is a pdqsort-style pattern-defeating quicksort whose partition is Edelkamp & Weiss BlockQuicksort: each 64-element block records the byte offsets of misplaced elements with an unconditional store plus a boolean increment and then swaps them in pairs, so no branch depends on the data. Pattern detection does the rest: a partition that finds its range already partitioned tries a bounded insertion sort (at most 8 moves per side) to finish in one pass, and a pivot equal to the element before the range triggers an equal-keys partition that drops the whole duplicate run. The supporting pieces are a ninther pivot above 128 elements, fixed sorting networks for n&lt;=8 (gcc 13 emits vpminsq/vpmaxsq with no conditional jumps), insertion sort up to 24 elements, and a heapsort fallback after 2\*log2(n) levels. radix_sort is an 8-bit-digit LSD radix sort that counts every digit's histogram in one read and skips any pass where all keys have the same digit.

## Compared with alternatives

No siblings catalogued yet. Against std::sort itself, use fastcpp::algo::sort for large scalar arrays that are random, sorted or few-valued, use radix_sort only for 1K-1M bare numeric keys, and keep std::sort for nearly-sorted data.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | None beyond the standard library. sort.hpp includes algo/sorting_network.hpp and core/macros.hpp, and radix_sort.hpp includes core/macros.hpp, so four headers under include/fastcpp/ cover both. Copy them instead of using add_subdirectory, because the fastcpp::fastcpp CMake target links all 10 vendored libraries (fmt, phmap, xsimd, simdjson, CRoaring, ...) and requires C++23. |
| **Minimum toolchain** | By inspection, sort.hpp and sorting_network.hpp need C++17 (structured bindings, inline constexpr). radix_sort.hpp needs C++20 (concepts, std::bit_cast). The project itself targets C++23; the README lists gcc 13+, clang 17+ and MSVC 19.35+. The commit reports tests passing on gcc 13.3, gcc 14.2 and clang 18.1 with -Werror. MSVC is not in CI. |
| **Platforms** | Portable C++ with no intrinsics in these headers. The branch-free behavior depends on the compiler emitting conditional moves or min/max, which was verified only for gcc 13 at -O3 -march=native on x86-64. Benchmarked only on x86-64 Linux. CI compiles test_sort and bench_sort on Linux gcc/clang and macOS clang, but runs test_sort only on Linux gcc -march=native and ASan/UBSan. |
| **Thread safety** | Not documented. Both are stateless functions over the caller's range, so concurrent calls on separate ranges are safe by construction. Do not share one radix_sort scratch vector between concurrent calls. |
| **Drop-in for the baseline** | partial — fastcpp::algo::sort matches std::sort's (first, last[, comp]) signature and unstable O(n log n) contract, but it is not constexpr, has no ranges or execution-policy overloads, and by code reading will not compile for move-only element types. radix_sort is not a drop-in: it takes pointers or a std::vector, supports six key types, and has no comparator. |

## Gotchas

- sorting_network.hpp's compare_exchange always copy-constructs and copy-assigns both elements (`const T lo = out_of_order ? b : a;`), whether or not they are out of order. Move-only types like std::unique_ptr should therefore not compile, and heap-owning types such as long std::string pay allocations in every small sort. The test commented 'Move-only, non-trivially-copyable' actually sorts std::string.
- radix_sort always allocates a fresh n-key buffer per call, even when you pass scratch (owned_b is unconditional). Without scratch it allocates two, so peak extra memory is 2n keys, although the header comment says 'one scratch buffer'.
- radix_sort specializes only the exact fixed-width typedefs, so types such as long long on Linux, or size_t/long on macOS (where uint64_t is unsigned long long), fail the radix_sortable concept at compile time. NaN is unsupported and unchecked, and -0.0 is placed before +0.0.
- The speedups come from -O3 -march=native builds (the repo forces -O3 for benchmarks). Branch-free codegen of the networks was verified by disassembly only on gcc 13, and the default RelWithDebInfo (-O2) build was not measured.

## Caveats and trade-offs

Developer source is a PRIVATE repo (private:developer-source, 0 stars, 0 forks), readable only via authenticated `gh api`. Private code is not 'public', so this is capped below tier A even though results/fastest.json's run metadata states the compiler, flags and CPU (verified against bench/bench_sort.cpp, root CMakeLists.txt fastcpp_bench_opt/-O3 and the 'release' preset with FASTCPP_NATIVE_ARCH=ON). The CPU string names no SKU (only 'Intel Xeon @ 2.10GHz'). The estimator is the minimum of 3 samples with a 50ms budget each. The run is labelled commit '7db44c2 + sorting', i.e. it was measured on a working tree before sorting commit 2fa7d3d. The 2.86x pivot-arrangement figure is a before/after measurement: the committed bench/bench_sort.cpp times only std::sort vs fastcpp::algo::sort vs radix_sort, so the old arrangement cannot be re-run from the repo. The sawtooth, reverse-sorted and appended ratios are not in results/fastest.json; they come from the commit message and README only. Only libstdc++/gcc was tested; there is no libc++ or MSVC STL comparison. The benchmark is first-party, written by the same project, and has not been independently reproduced. The repo's own results file says absolute times are not comparable across differently-timed runs on this shared cloud VM, so only within-row ratios are treated as meaningful.

Pattern-defeating quicksort loses to std::sort by \~7-10% on almost-sorted data (1% of positions swapped): the bounded sorted-run probe (at most 8 moves per side) fails once displacement exceeds that budget, so the wasted probe is pure overhead; wins on the other six tested patterns. radix_sort needs O(n) scratch memory, supports no custom comparator, and only works on key types decomposable into bytes; its advantage window is roughly n=1024..1M, and past \~4M it is slower than the project's own comparison sort.

## Maintenance

Active but brand new: the repo is private (private:developer-source, 0 stars) and MIT-licensed, the sorting code landed in one commit on 2026-09-04, and the four self-contained headers are easy to vendor for anyone with access; all 21 CI runs are red, but at that commit the failures come from unrelated targets (the xsimd bench_matmul build and a UBSan error in string/parse.hpp), and test_sort passed wherever it ran.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** results/fastest.json has sorting rows against std::sort (run 2026-09-04-algorithms: gcc 13.3.0, -O3 -march=native -std=c++23, 'Intel Xeon @ 2.10GHz' 4 cores), produced by bench/bench_sort.cpp. Compiler, flags and CPU are stated, but the repo is private so the benchmark code is not public, which rules out A. There is no paper or independent third-party suite, so it cannot be B. That leaves first-party numbers: C.
- **Verifier notes:** The main numbers check out exactly against fastest.json: 6.63/3.42/2.28/2.86/4.30 recompute from the page's ns values, and 0.93x is the inverse of the page's 1.07x std::sort win. The only precision fix is where 2.33x/1.71x/1.55x come from: the commit message and README, not benchmark_url. Metadata is confirmed via gh: MIT (spdx MIT), not a fork, not archived, private, 0 stars, last commit 2026-09-04 (active). The sort is a first-party pdqsort-style reimplementation crediting Edelkamp & Weiss BlockQuicksort; it is not a vendored copy of pdqsort.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - private:developer-source
  - private:developer-source/blob/main/results/fastest.json
  - private:developer-source/blob/main/bench/bench_sort.cpp
  - private:developer-source/blob/main/README.md
  - private:developer-source/blob/main/CMakeLists.txt
  - private:developer-source/blob/main/CMakePresets.json
  - private:developer-source/blob/main/bench/CMakeLists.txt
  - private:developer-source/blob/main/LICENSE
  - private:developer-source/blob/main/include/fastcpp/algo/sort.hpp
  - private:developer-source/blob/main/include/fastcpp/algo/radix_sort.hpp
  - private:developer-source/commit/2fa7d3df006a9e4bc58c863c651d5fefe721f9e3
- **Sources the enricher read:**
  - private:developer-source
  - private:developer-source/blob/main/README.md
  - private:developer-source/blob/main/include/fastcpp/algo/sort.hpp
  - private:developer-source/blob/main/include/fastcpp/algo/radix_sort.hpp
  - private:developer-source/blob/main/include/fastcpp/algo/sorting_network.hpp
  - private:developer-source/blob/main/include/fastcpp/core/macros.hpp
  - private:developer-source/blob/main/bench/bench_sort.cpp
  - private:developer-source/blob/main/bench/bench_harness.hpp
  - private:developer-source/blob/main/bench/CMakeLists.txt
  - private:developer-source/blob/main/tests/test_sort.cpp
  - private:developer-source/blob/main/results/fastest.json
  - private:developer-source/blob/main/CMakeLists.txt
  - private:developer-source/blob/main/CMakePresets.json
  - private:developer-source/blob/main/.github/workflows/ci.yml
  - private:developer-source/commit/2fa7d3df006a9e4bc58c863c651d5fefe721f9e3
  - private:developer-source/commits/main
  - private:developer-source/issues
  - private:developer-source/actions
  - private:developer-source/actions/runs/33828450197
- **Raw records:** [data/wave1-phf/verified.json](../../../data/wave1-phf/verified.json) (id `private:developer-source#sorting`) · [data/wave1-phf/enrich/raw/private_developer_source_sorting.json](../../../data/wave1-phf/enrich/raw/private_developer_source_sorting.json) (enrichment confidence 0.82)

</details>
