# poolSTL

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause OR BSL-1.0 OR MIT` · 🟡 stale

> Header-only thread-pool implementation of the C++17 parallel algorithms; about 5x over sequential and roughly on par with TBB-backed std::execution::par.

| | |
|---|---|
| **Beats** | std::execution::par (native C++17 parallel algorithms; backing runtime not stated) |
| **Claimed result** | Mixed against std::execution::par (GCC 13, M1 Pro): exclusive_scan 11.6 ms vs 19.8 ms (about 1.7x, derived from page data) vs sequential 33.7 ms; sort 112 ms vs 113 ms (parity), pluggable_sort with pdqsort 71.7 ms; for_each 18.7 vs 15.3 ms, transform 17.4 vs 15.3 ms, reduce 4.06 vs 3.38 ms, find_if at the 5th percentile 0.405 vs 0.230 ms (all slower); all_of 3.47 vs 3.45 ms (parity). About 5x faster than sequential on most algorithms. |
| **Workload** | Google Benchmark of parallel STL algorithms (all_of, find_if, for_each, sort, transform, exclusive_scan, reduce) on large arrays, poolstl::par versus std::execution::par and sequential. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Pro (6 performance + 2 efficiency cores) |
| **Compiler and flags** | GCC 13; flags not stated |
| **Adoption** | 38 stars |
| **Last commit** | 2024-06-03 |
| **Links** | [repository](https://github.com/alugowski/poolSTL) · [benchmark](https://raw.githubusercontent.com/alugowski/poolSTL/HEAD/README.md) |

## Verdict

Author's Google Benchmark run on an Apple M1 Pro (6P+2E) with GCC 13 (benchmark CMake Release flags -O3 -DNDEBUG; native par from libstdc++ linked to TBB when found) on 100M-int arrays (10M shuffled ints for sort) gives about 4-5x over sequential. Against std::execution::par it ties on all_of and sort, is 1.7x faster on exclusive_scan (11.6 vs 19.8 ms), and is 10-20% slower on for_each, transform and reduce.

## Use it when

- You need std::execution::par semantics on Apple Clang, libc++, Emscripten or old GCC, where native parallel algorithms are missing or need TBB.
- You want parallel for_each/transform/reduce over large random-access ranges (millions of elements) without linking TBB or OpenMP.
- Shipping a library that must build anywhere: single amalgamated header, C++11 minimum, CI on GCC 7+, Clang 5+, Apple Clang, MSVC, MinGW and Emscripten.
- Sorting large arrays of mostly distinct keys, especially with pluggable_sort plus pdqsort (71.7 ms vs 113 ms for TBB-backed std::sort(par) on 10M shuffled ints in the README run).
- Choosing parallel vs sequential at runtime by input size with par_if.

## Skip it when

- If native TBB-backed std::execution::par is available: in the author's own run poolSTL is slower on for_each (18.7 vs 15.3 ms), transform (17.4 vs 15.3), reduce (4.06 vs 3.38) and early-exit find_if (0.405 vs 0.230 ms), and wins only on exclusive_scan.
- Inputs with many duplicate keys: the 2-way quicksort partition (comp(x, pivot)) cannot split a run of equal keys, so the range falls back to one sequential std::sort; open issue #39 reports single-core sorting of a 40M mostly-zero vector.
- Nested parallelism or task graphs: the README forbids nested parallel calls and the pool has no dependencies or work stealing (see the sibling task schedulers instead).
- Non-random-access iterators (lists, input streams): not supported.
- Algorithms outside the implemented subset (no inclusive_scan, merge, unique and others); they are added on request.

## How it is fast

Plain static chunking: the range is split into about one chunk per pool thread (some algorithms use an extra split factor), each chunk becomes a std::future task, and results are combined on the calling thread. sort is a parallel quicksort that partitions with the middle element as pivot until leaves are about n/(2\*threads), then runs std::sort on each leaf; the first partitions also run 2-way parallel (partition_p2). A pairwise-merge mergesort variant also exists. Nothing is vectorised or work-stolen; the gain is ordinary multicore parallelism with low dependency cost.

## Compared with alternatives

Pick poolSTL when you want standard-algorithm syntax (std::sort, std::reduce with a policy) and portability without TBB. Fork Union, citor or dp::thread_pool are lower-overhead schedulers with their own APIs, better suited to fine-grained or nested parallelism, but none of them implement the std:: parallel algorithms.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (bundles alugowski/task-thread-pool); -lpthread on GCC/Clang 8 or older, -pthread on Emscripten |
| **Minimum toolchain** | C++11; C++17 for exclusive_scan, transform_reduce and the other C++17-only algorithms; CI on GCC 7+, Clang 5+, Apple Clang, MSVC, MinGW, Emscripten |
| **Platforms** | any platform with std::thread (Linux, macOS, Windows, WebAssembly via Emscripten) |
| **Thread safety** | Algorithms may be called concurrently on disjoint data through the shared default pool, which starts on first use; nested parallel calls are not supported. Concurrent calls sharing the pool were not separately documented. |
| **Drop-in for the baseline** | partial — same std:: algorithm calls with poolstl::par in place of std::execution::par (or a full alias via POOLSTL_STD_SUPPLEMENT), but only a subset of algorithms and random-access iterators only |

## Gotchas

- In the README Google Benchmark table the CPU column for poolstl::par (for example 0.044 ms for for_each) counts only the waiting caller thread, because work runs on pool threads; compare real_time.
- POOLSTL_STD_SUPPLEMENT is labelled 'USE AT YOUR OWN RISK! THIS IS A HACK!': it injects poolstl::par as std::execution::par when native support is missing, and POOLSTL_STD_SUPPLEMENT_NO_INCLUDE is needed to avoid pulling in &lt;execution&gt; (and its TBB link) where TBB is absent.
- Quicksort pivot is the middle element without median-of-3 or 3-way partitioning, so the parallel speedup depends on the key distribution (see issue #39).
- Open issue #40: building with GCC -Wshadow produces many warnings.

## Known shortcomings

- Sort falls back to one sequential std::sort on runs of equal keys: the 2-way quicksort partition with a middle-element pivot cannot split them (open issue 39). The README CPU column counts only the caller thread. Native par here is TBB-linked libstdc++.

## Caveats and trade-offs

Mostly parity or slower than native std::execution::par; wins only in exclusive_scan and when a pluggable sort is swapped in; single machine; which standard library and parallel backend implement std::execution::par on that machine is not stated; own results.

Header-only thread-pool backend for C++17 parallel algorithms for compilers without native support; random-access iterators only, no nested parallel calls.

## Maintenance

Stale since mid-2024 with two open issues, but triple-licensed (BSD-2-Clause, MIT or BSL-1.0), header-only and CI-tested on many toolchains, so safe to vendor as a portability fallback.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party Google Benchmark output in the README, from the public benchmark/ directory, with GCC 13 and an Apple M1 Pro, but no compiler flags stated, so not A.
- **Verifier notes:** Numbers match the README exactly. Its real value is as a dependency-free fallback where native std::execution::par is missing (Apple Clang, Emscripten); against native par it wins only in exclusive_scan and with a pluggable sort. baseline_stdlib set to libstdc++ because GCC 13 ships libstdc++ (whose par backend is TBB), inferred, not stated. Licenses, 38 stars and last commit 2024-06-03 (stale) confirmed on github.com.
- **Fields the verifier corrected:** `baseline_stdlib`, `claimed_speedup`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/alugowski/poolSTL/HEAD/README.md>
  - <https://github.com/alugowski/poolSTL>
  - <https://github.com/alugowski/poolSTL/commits>
- **Sources the enricher read:**
  - <https://github.com/alugowski/poolSTL>
  - <https://raw.githubusercontent.com/alugowski/poolSTL/HEAD/README.md>
  - <https://github.com/alugowski/poolSTL/tree/main/include/poolstl>
  - <https://github.com/alugowski/poolSTL/issues?q=is%3Aissue>
  - <https://github.com/alugowski/poolSTL/issues/39>
  - <https://raw.githubusercontent.com/alugowski/poolSTL/HEAD/include/poolstl/internal/ttp_impl.hpp>
  - <https://raw.githubusercontent.com/alugowski/poolSTL/HEAD/include/poolstl/internal/utils.hpp>
  - <https://raw.githubusercontent.com/alugowski/poolSTL/HEAD/include/poolstl/internal/thread_impl.hpp>
  - <https://raw.githubusercontent.com/alugowski/poolSTL/HEAD/include/poolstl/algorithm>
  - <https://github.com/alugowski/poolSTL/tree/main/benchmark>
  - <https://raw.githubusercontent.com/alugowski/poolSTL/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/alugowski/poolSTL/HEAD/benchmark/utils.hpp>
  - <https://raw.githubusercontent.com/alugowski/poolSTL/HEAD/benchmark/algorithm_bench.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/alugowski/poolstl`) · [data/wave11/enrich/raw/github_com_alugowski_poolstl.json](../../../data/wave11/enrich/raw/github_com_alugowski_poolstl.json) (enrichment confidence 0.8)

</details>
