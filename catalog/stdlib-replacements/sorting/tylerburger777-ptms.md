# PTMS (Parallel Tournament Merge Sort)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sorting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> OpenMP-task parallel merge sort for int arrays with AVX2/AVX-512 bitonic base cases; claims about 2.2x over tbb::parallel_sort.

| | |
|---|---|
| **Beats** | std::sort (1 thread) and tbb::parallel_sort |
| **Claimed result** | Median seconds: std::sort 0.300 (1.00x), tbb::parallel_sort 0.036 (8.30x), PTMS 0.0163 (about 18.4x versus std::sort; about 2.2x versus tbb::parallel_sort, derived from page data). On a Ryzen 7 7500F with AVX-512: median 0.0162 s at 12 threads. |
| **Workload** | Sorting 4,000,000 uniform random ints in [-1e6, 1e6] (fixed seed) with OpenMP tasks, parallel merging and AVX2/AVX-512 bitonic base cases; median of 600 timed runs after 400 warm-ups, with the input re-copied outside the timer before each run, at 16 threads on the 6900HX (AVX2 path, since that CPU lacks AVX-512). |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 6900HX (16 threads); AMD Ryzen 7 7500F (AVX-512, 12 threads) |
| **Compiler and flags** | Compiler not stated (README lists GCC 9+, Clang 10+, MSVC 2019+ via clang-cl). CMakeLists.txt defaults to a Release build and, for GCC/Clang, adds -O3 and -march=native (SIMD=AUTO) plus OpenMP with -std=c++17; MSVC gets /O2 with /arch:AVX2 or /arch:AVX512. |
| **Adoption** | 0 stars, 0 forks, 9 commits (all on 2026-10-10) |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/TylerBurger777/PTMS) · [benchmark](https://github.com/TylerBurger777/PTMS) |

## Verdict

On a Ryzen 9 6900HX (16 threads, AVX2 build; compiler unstated, CMake defaults to -O3 -march=native), sorting 4M uniform random ints in [-1e6, 1e6] took a median 0.0163 s versus 0.036 s for tbb::parallel_sort (about 2.2x, the like-for-like figure) and 0.300 s for single-thread std::sort (the headline 18.4x). Only the PTMS row comes from public code (median of 600 runs after 400 warm-ups, input recopied outside the timer); the baseline rows and the AVX-512 7500F figure (0.0162 s at 12 threads) have no published harness.

## Use it when

- Sorting millions of 32-bit ints on a multicore x86-64 machine where the code already links OpenMP and an extra n-int scratch buffer is affordable.
- Throughput-oriented batch sorts of uniform random int data at full core count, the only workload the author measured (4M ints, 16 threads, Ryzen 9 6900HX).
- As a compact (one \~480-line .cpp plus header) reference for combining OpenMP tasks, parallel binary-split merging and AVX2/AVX-512 bitonic base cases.

## Skip it when

- Any key type other than int (no 64-bit, float, key-value, struct or custom-comparator support); use IPS4o, vqsort or x86-simd-sort.
- Memory-constrained code: it needs a second n-int buffer, whereas IPS4o sorts in place.
- Production code that needs trust in the numbers: the repo appeared on 2026-10-10 (10 commits, 0 stars, no issues or releases), the std::sort and tbb::parallel_sort rows have no public harness, and there is no head-to-head against IPS4o or other parallel sorts.
- Arrays above 2^31-1 elements (n is int), or calls made from inside an existing OpenMP parallel region, where the nested region runs on one thread by default.
- Plain MSVC cl.exe builds: README says MSVC lacks #pragma omp taskgroup, so Windows needs clang-cl or MinGW GCC (the CI uses MinGW).

## How it is fast

The array is cut into P equal chunks (one OpenMP task each); each chunk's two halves are sorted by a sequential top-down merge sort that ping-pongs between the array and the scratch buffer to avoid copy-back, with optimal sorting networks (branchless min/max compare-exchange) for 4-7 elements and in-register bitonic sorting networks for 8 and 16 elements (AVX2 permutevar8x32 + min/max + blend; AVX-512 permutexvar + mask_blend). The resulting 2P runs are merged pairwise level by level as OpenMP tasks (a binary merge tree, not a loser/tournament tree despite the name), and each pairwise merge is itself parallelised by binary splitting (median of the larger run plus lower_bound in the other) down to 2048 elements or depth 5, so the final merge is not a serial bottleneck. Leaf merges use a branchless select loop.

## Compared with alternatives

IPS4o is the like-for-like parallel sibling (in-place, generic types, peer-reviewed benchmarks) and should be the default; vqsort and x86-simd-sort cover single-thread SIMD sorting for more key types. Pick PTMS only if you want a small, MIT, OpenMP-only int32 merge sort to vendor or study and can supply a scratch buffer; no comparison against IPS4o exists.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake target ptms_lib built from src/ptms.cpp); also usable as a source-drop of src/ptms.cpp, src/ptms_detail.h and include/ptms.h |
| **Dependencies** | OpenMP 4.5+ (tasks and taskgroup); CMake 3.15+ for the provided build |
| **Minimum toolchain** | C++17; GCC 9+, Clang 10+, or clang-cl from Visual Studio 2019+ (README); CI builds with ubuntu-latest g++, MSYS2 MinGW-w64 GCC and macOS Apple Clang + libomp |
| **Platforms** | x86-64 with AVX2 or AVX-512F for the SIMD base cases; scalar fallback (-DSIMD=SCALAR) on other targets, CI-tested on macOS arm64 in scalar mode only |
| **Thread safety** | Header: not thread-safe, do not call concurrently on overlapping data; each call opens its own OpenMP parallel region with P threads |
| **Drop-in for the baseline** | no |

## Gotchas

- sort_int silently returns without sorting when a or buf is null or buf == a; there is no error code or exception.
- The default CMake mode (SIMD=AUTO) adds -march=native globally, so binaries are not portable; when the compiler rejects -march=native it falls back to -mavx2, which breaks non-x86 builds unless -DSIMD=SCALAR is passed (the macOS CI job does this).
- Harness flaws behind the README numbers: benchmark/benchmark.cpp times only PTMS (no std::sort or TBB code, no TBB link), and it times the internal ptms::detail::sort_body inside an already-open parallel region rather than the public sort_int; its self-test checks copies of the 4-7 sorting networks, not the library's own or SIMD kernels (outputs are still compared with std::sort at four of the 600 timed runs). The 'cache-resident' label does not hold: 16 MB input plus 16 MB scratch against a 16 MB L3.
- No correctness bug found: I checked the 4-7 networks exhaustively with the 0-1 principle, emulated the AVX2 and AVX-512 bitonic sort/merge permutation and blend masks (exhaustive 0-1 inputs for the sorts, 20,000 random merges), and ran a sequential Python port of the whole pipeline for n = 4..199, 1000, 4097 and 10007 with P = 1..16 against sorted(); this is an emulation, not a native build. With 32 runs (16 threads) the merge tree has 5 levels, so every call ends with an extra full-array memcpy from the scratch buffer.

## Known shortcomings

- benchmark/benchmark.cpp times PTMS only, the std::sort and tbb::parallel_sort rows have no code and no TBB link; the timer runs sort_body inside an already-open OpenMP region; the 18.4x is 16 threads against 1, the fair figure is 2.2x against TBB; compiler unstated. Filed under sorting.
- Harness flaws: benchmark.cpp times only PTMS, with no std::sort or TBB code; the timer wraps the internal detail::sort_body inside an already-open parallel region; the self-test checks copies of the 4-7 networks, not the library or SIMD kernels; the 'cache-resident' label is false (32 MB working set vs 16 MB L3). No correctness bug found: the networks were checked exhaustively with the 0-1 principle, and the AVX2/AVX-512 bitonic kernels and a full pipeline port matched sorted() in a Python emulation (not a native run). sort_int silently skips sorting on a null or aliased buffer; AUTO mode adds -march=native and falls back to -mavx2 on non-x86.

## Caveats and trade-offs

The baseline rows cannot be reproduced. benchmark/benchmark.cpp times only PTMS, with no std::sort or tbb::parallel_sort code anywhere and no TBB link in CMakeLists.txt. The PTMS timer wraps ptms::detail::sort_body inside an OpenMP parallel region that is already open, with a preallocated scratch buffer, so it leaves out the parallel-region start-up the public ptms::sort_int pays on each call. The headline 18.4x compares 16 threads with one-thread std::sort; the like-for-like result is about 2.2x over tbb::parallel_sort (CITATION.cff says '\~2x on cache-resident data'). The 'cache-resident' label is doubtful: the 16 MB input plus a 16 MB scratch buffer is 32 MB on a CPU with 16 MB of L3. The same input is re-sorted 1000 times. One size, int keys only, compiler unstated; the Ryzen 7 7500F AVX-512 figure (0.0162 s at 12 threads) has no baseline numbers. The repo is brand new with no external verification, and the LICENSE and CITATION.cff say 2025 (author Andrey Afimov) although the first commit is 2026-10-10. It is a parallel sort more than a SIMD library and would fit the wave-1 sorting category, where std::sort is the listed baseline.

Int (sort_int) only, needs a caller-supplied scratch buffer, OpenMP tasks (MSVC needs clang-cl), AVX2 or AVX-512 base cases selectable with -DSIMD; benchmark program in the benchmark/ folder.

## Maintenance

Brand-new single-author project (10 commits, all on 2026-10-10, 0 stars, CI on Linux, Windows and macOS; LICENSE and CITATION.cff dated 2025), MIT-licensed and small enough to vendor, but unproven: no independent measurement and no public baseline harness.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README table names a CPU (Ryzen 9 6900HX) but the compiler is not stated, and the public benchmark/benchmark.cpp times only PTMS: the std::sort and tbb::parallel_sort rows have no public harness, so this is first-party with partial methodology.
- **Verifier notes:** The README numbers match (0.300 / 0.036 / 0.0163 s), but only the PTMS row comes from public code; the std::sort and TBB rows have no harness, and the PTMS timer excludes OpenMP team start-up. Consider category override to sorting (with domain override); baseline_in_list would then be true.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-78 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/TylerBurger777/PTMS>
  - <https://github.com/TylerBurger777/PTMS/commits>
  - <https://github.com/TylerBurger777/PTMS/tree/main/benchmark>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/README.md>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/benchmark/benchmark.cpp>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/src/ptms.cpp>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/CITATION.cff>
- **Sources the enricher read:**
  - <https://github.com/TylerBurger777/PTMS>
  - <https://github.com/TylerBurger777/PTMS/commits>
  - <https://github.com/TylerBurger777/PTMS/issues>
  - <https://github.com/TylerBurger777/PTMS/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/README.md>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/include/ptms.h>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/src/ptms.cpp>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/src/ptms_detail.h>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/benchmark/benchmark.cpp>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/tests/test_correctness.cpp>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/CITATION.cff>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/TylerBurger777/PTMS/HEAD/.github/workflows/release.yml>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/tylerburger777/ptms`) · [data/wave13/enrich/raw/github_com_tylerburger777_ptms.json](../../../data/wave13/enrich/raw/github_com_tylerburger777_ptms.json) (enrichment confidence 0.75)

</details>
