# Software Architecture with C++ 2E: binary search (std::ranges::lower_bound) versus linear scan (std::ranges::find) in a sorted vector

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Searching](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Book benchmark: std::ranges::lower_bound beats std::ranges::find on a sorted vector&lt;int&gt;, O(log n) against a linear scan.

| | |
|---|---|
| **Beats** | std::ranges::find (linear scan) on a sorted std::vector&lt;int&gt; |
| **Claimed result** | Book sample run (relayed via seed lead, not on a repo page): binary search 24.2 ns versus linear search 471 ns for the 2137 needle in 10M elements; with the needle at the end of 10M elements about 24 ns versus 2.8 ms. Ratios (derived from the relayed numbers): about 19x and about 117,000x. |
| **Workload** | Google Benchmark of std::ranges::lower_bound against std::ranges::find on a sorted std::vector&lt;int&gt; holding 0..n-1: main_1 and main_2 look up the constant value 2137 in 10M elements; main_3 looks up 2137 in sizes 1e3 to 1e7 (x10 steps); main_4 looks up needles n/8, n/2, n-1 (last element) and n+1 (absent, larger than every element) in vectors of 1e3, 1e5 and 1e7 elements. The same benchmark also exists as Catch2 and nanobench/doctest variants. |
| **Metric** | latency |
| **Hardware** | Book run reported only as a 20-thread 2022 MHz CPU with 48 KiB L1d and 24 MiB L3 (Google Benchmark context block, relayed via lead); no CPU model. |
| **Compiler and flags** | Repo README for Chapter13 requires a Conan profile of GCC 15, gnu20, libstdc++11 and a CMake Release build (CMAKE_BUILD_TYPE=Release, so CMake's default GCC Release flags, normally -O3 -DNDEBUG, which the repo does not spell out); targets set cxx_std_20 (Google Benchmark 1.9.4 via Conan, benchmark_1..4) or cxx_std_23 (Catch2 3.12.0 and nanobench 4.3.11 variants). The compiler and flags of the book's actual run are not stated. |
| **Adoption** | 74 stars, 22 forks; Packt companion repository of the book Software Architecture with C++, 2nd ed. |
| **Last commit** | 2026-09-27 |
| **Links** | [repository](https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E) · [benchmark](https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/blob/main/Chapter13/microbenchmarking/benchmark/main_4.cpp) |

## Verdict

The repo carries only benchmark source; the numbers are the book's own run relayed by the seed lead: std::ranges::lower_bound 24.2 ns versus std::ranges::find 471 ns for needle 2137 in a 10M-element sorted vector&lt;int&gt; (about 19x, with find stopping after 2,138 elements), and about 24 ns versus 2.8 ms with the needle at the end (about 117,000x, derived from the relayed numbers). Compiler, flags and CPU model are not stated (the Google Benchmark context shows only 20 threads at 2022 MHz, 48 KiB L1d and 24 MiB L3); the repo's own build is a GCC 15/libstdc++ CMake Release build via Conan.

## Use it when

- You keep a std::vector (or another random-access range) sorted and still look values up with std::find or a hand-written loop: switching to std::ranges::lower_bound plus an equality check is a zero-dependency change.
- Read-mostly data built once or in batches and searched many times, such as a sorted table of IDs or timestamps.
- Arrays from about a thousand elements up (the smallest size this benchmark covers); with the needle at the end of 10M elements the book's run puts lower_bound near 24 ns against 2.8 ms for find.
- Range queries (first element not less than x), which find cannot answer.

## Skip it when

- Unsorted data, or data that changes between lookups: inserting into a sorted vector costs O(n) and sorting first costs O(n log n), which a handful of finds will not repay.
- Very small arrays: the sweep starts at 1,000 elements, so it does not locate the size below which a linear scan wins; measure at your size.
- Random lookups into large arrays where std::lower_bound itself is the bottleneck: this harness repeats one needle and so hides cache misses and branch mispredictions; a branchless or Eytzinger-layout search (see siblings) targets that case.
- Hits that sit near the front of the array: a scan that stops early is cheap (in main_1 to main_3, find stops after 2,138 elements whatever the vector size).

## How it is fast

Binary search halves the candidate range at each comparison, so a 10M-element vector needs about 24 probes where std::ranges::find compares every element up to the match. The harness repeats one needle on one vector, so those probes stay in cache and the branches follow the same path every iteration; the book's 24 ns figure is that warm best case. Nothing beyond the textbook algorithm is used: the stock std::ranges::lower_bound, no branchless loop, prefetching or Eytzinger layout.

## Compared with alternatives

Pick plain std::ranges::lower_bound when you are still scanning sorted data linearly and want the zero-dependency fix; move to sb_lower_bound, FastBinarySearch or the developer-source branchless/Eytzinger lower_bound when std::lower_bound itself shows up in profiles on random lookups into large arrays, a case this warm-cache benchmark never measures.

## Integration

| | |
|---|---|
| **Form** | header-only (C++ standard library &lt;algorithm&gt; and &lt;ranges&gt;; the repo sample itself is a source-drop benchmark) |
| **Dependencies** | none for the technique; the benchmarks need Google Benchmark 1.9.4, or Catch2 3.12.0, or nanobench 4.3.11 with doctest 2.4.12 (all via Conan 2) |
| **Minimum toolchain** | C++20 for std::ranges (Google Benchmark targets use cxx_std_20, the Catch2 and nanobench targets cxx_std_23); the repo lists GCC 15, Clang 20 or MSVC 19.44/19.50, CMake 3.28 and Conan 2, and says GCC 14, Clang 19 and MSVC 19.44 build some but not all examples |
| **Platforms** | any (portable standard C++); the Chapter13 README says the examples are developed on Linux and tested on macOS and Windows |
| **Thread safety** | Not documented in the repo; both calls are non-mutating algorithms over a range that is not modified, so concurrent lookups on an unchanging vector need no locking. |
| **Drop-in for the baseline** | partial — lower_bound needs a range sorted by the same ordering and returns the first element not less than the needle, so a hit needs an extra \*it == needle check (or std::ranges::binary_search for a bool); find works on unsorted data and returns end() only when the value is absent. |

## Gotchas

- main_1 to main_3 fix the needle at 2137, so for vectors of 10,000 elements and more std::ranges::find always stops at index 2137: the linear series in main_3 is flat from 1e4 to 1e7, and the book's 471 ns versus 24.2 ns (about 19x) is a 2,138-element scan against a 24-probe search, not a scan of 10M elements. Only main_4's needles (n/8, n/2, n-1 and the absent n+1) scale with the vector size.
- Every iteration searches the same needle in the same vector, so the binary-search probes stay cached and its branch pattern repeats; random needles over the 40 MB array would cost more per lookup, and no variant measures that.
- The nanobench_doctest variant (main_4) builds the vector inside the timed lambda, so at 10M elements it mostly times allocating and filling 40 MB rather than the search; the Google Benchmark and Catch2 variants build it outside the timed region.
- main_4 passes the needle as int64_t (state.range) against a vector&lt;int&gt;, and the Catch2 helper narrows a size_t needle to int; harmless at these values, but needle and element types differ from a typical lookup.

## Known shortcomings

- Textbook algorithm comparison (O(log n) against O(n)), not a library win; warm cache with the same needle every iteration; the nanobench variant times vector construction; book numbers first-party, no CPU or flags in the repo.

## Caveats and trade-offs

The printed numbers are the book's own sample run, relayed through the seed lead; they are not on any repo page (the repo carries the benchmark source only, no result files), so they could not be checked against a page. The comparison is an algorithmic-complexity truism (logarithmic versus linear on sorted data), not a faster implementation of the same algorithm; the speedup grows with n by construction. Both sides are the C++ standard library, so the stdlib under test (libstdc++ per the repo's GCC 15 Conan profile) is not stated for the book's run. Each benchmark repeats the same needle on the same vector, so the about 23 probes of the binary search stay in cache and the 24 ns figure is a warm-cache best case; a random-needle lookup in a 40 MB array would be bound by cache misses. Tier C: first-party book run, compiler, flags and CPU model are unstated (the Google Benchmark context block reports only 20 threads at 2022 MHz, 48 KiB L1d, 24 MiB L3) and the repo holds code only. In the Google Benchmark and Catch2 variants the vector is built outside the timed region; the nanobench_doctest variant builds the vector inside the timed lambda (main_4), so it times construction as well as the search. The same benchmark is written three times (Google Benchmark, Catch2, nanobench with doctest) and only the Google Benchmark numbers are given in the book. Repo files opened: Chapter13/microbenchmarking/benchmark/main_1..4.cpp and CMakeLists.txt, catch2/main_4.cpp, nanobench_doctest/main_4.cpp, Chapter13/conanfile.py, CMakeLists.txt and README.md.

Binary search needs sorted input and random access (O(log n) versus O(n)); for tiny vectors a linear scan can win because of branch prediction and cache locality, which the 1000-element points in benchmark_3 and benchmark_4 are meant to show. Not a library: a std algorithm choice.

## Maintenance

Active Packt companion repository (last commit 2026-09-27, mostly README edits; CI builds only Chapter10/customer, not these benchmarks), MIT-licensed; there is nothing to vendor because the technique is the standard library call itself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter13/microbenchmarking/benchmark/main_1.cpp to main_4.cpp time std::ranges::lower_bound against std::ranges::find on a sorted std::vector&lt;int&gt; with Google Benchmark, but the repo holds code only and the 24.2 ns versus 471 ns figures are the book's run (relayed by the lead) with compiler and flags unstated and no CPU model, so first-party tier C.
- **Verifier notes:** Source matches the record; nanobench variant does time vector construction (confirmed). Workload corrected: main_4's last needle is n+1 (absent value), not one past the last position; main_3 size sweep added. Added warm-cache caveat (same needle every iteration). Metadata confirmed: MIT, 74 stars, last commit 2026-09-27.
- **Fields the verifier corrected:** `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-101 (book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E>
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/commits/main>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/conanfile.py>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/README.md>
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/blob/main/Chapter13/microbenchmarking/benchmark/main_4.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/microbenchmarking/benchmark/main_1.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/microbenchmarking/benchmark/main_2.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/microbenchmarking/benchmark/main_3.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/microbenchmarking/benchmark/main_4.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/microbenchmarking/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/microbenchmarking/catch2/main_4.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/microbenchmarking/nanobench_doctest/main_4.cpp>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E>
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/issues>
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/commits/main>
  - <https://github.com/PacktPublishing/Software-Architecture-with-Cpp-2E/tree/main/.github/workflows>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/.github/workflows/github-ci.yml>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/conanfile.py>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/microbenchmarking/benchmark/main_1.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/microbenchmarking/benchmark/main_2.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/microbenchmarking/benchmark/main_3.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/microbenchmarking/benchmark/main_4.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/microbenchmarking/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/microbenchmarking/catch2/main_4.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/microbenchmarking/catch2/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/microbenchmarking/nanobench_doctest/main_4.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Software-Architecture-with-Cpp-2E/HEAD/Chapter13/microbenchmarking/nanobench_doctest/CMakeLists.txt>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `paper:book-software-architecture-with-cpp-2e-binary-search-vs-linear-scan`) · [data/wave12/enrich/raw/paper_book_software_architecture_with_cpp_2e_binary_search_vs_linear_scan.json](../../../data/wave12/enrich/raw/paper_book_software_architecture_with_cpp_2e_binary_search_vs_linear_scan.json) (enrichment confidence 0.6)

</details>
