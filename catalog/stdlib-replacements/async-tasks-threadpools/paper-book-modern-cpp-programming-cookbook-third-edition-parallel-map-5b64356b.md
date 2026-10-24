# Modern C++ Programming Cookbook 3rd ed.: parallel map and fold with std::thread

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Async tasks and thread pools](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Book recipe running std::transform and std::accumulate on one std::thread per hardware thread; about 2.2x at 50M ints.

| | |
|---|---|
| **Beats** | Sequential std::transform and std::accumulate |
| **Claimed result** | Book-reported (relayed via the seed lead; no numbers anywhere in the repository): at 50,000,000 ints map 27457 us parallel vs 60049 us sequential (about 2.2x, derived from the relayed book figures), fold 19075 us vs 41374 us (about 2.2x, derived). Parallel is faster only above roughly 2 million elements; below that the thread start-up cost loses. |
| **Workload** | Chapter08/recipe_8_09.h test_mapreduce_threads: in-place map (i+i) and fold (sum into long long) over a std::vector&lt;int&gt; of 10,000 to 50,000,000 elements, one thread per hardware thread, timed with a microsecond chrono perf_timer, single run per size. |
| **Metric** | throughput |
| **Hardware** | Windows 64-bit, Intel Core i7 with 4 physical and 8 logical cores (per the book; exact model not stated) |
| **Adoption** | 170 stars (Packt book companion repository) |
| **Last commit** | 2024-02-28 |
| **Links** | [repository](https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition) · [benchmark](https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/blob/main/Chapter08/recipe_8_09.h) |

## Verdict

The book (relayed via the seed lead; no numbers anywhere in the repo) reports one run at 50,000,000 ints: map 27,457 us parallel against 60,049 us for std::transform and fold 19,075 us against 41,374 us for std::accumulate into long long, about 2.2x each (derived), on 64-bit Windows with an Intel Core i7 of 4 cores and 8 threads; compiler, flags and exact CPU are not stated. The same book's std::async recipe reports a different sequential fold time (58,689 us) for the same 50M elements, so the run-to-run spread is about as large as the gain.

## Use it when

- A one-off parallel transform or reduction over millions of elements in a contiguous container, in a codebase that cannot rely on std::execution::par (for example libstdc++ without TBB, or libc++ builds where the parallel algorithms are not available).
- Teaching or prototyping: the code shows the whole fork-join pattern (chunk, spawn, join, combine) in one screen.
- Calls that are rare and large (the book places the break-even near 2 million ints), so creating and joining N threads per call is a small share of the time.
- Per-element work heavier than one add, where the loop is compute-bound and can scale closer to the core count than the memory-bound 2.2x reported here.

## Skip it when

- Frequent or small calls: every call creates and joins hardware_concurrency() threads; a persistent pool (BS::thread_pool, dispenso, Taskflow) or std::execution::par amortises that cost.
- Code that can throw: an exception escaping a worker calls std::terminate, and a std::system_error from std::thread construction partway through the loop destroys still-joinable threads, which also terminates.
- Stateful or move-sensitive functors: every worker evaluates std::forward&lt;F&gt;(f) on the same object, so an rvalue functor is moved from concurrently by several threads (a data race for any functor holding state such as a std::function or a captured container).
- Non-associative operations, or floating-point sums that must match the sequential result bit for bit: the fold regroups the reduction by chunk.
- Nested or concurrent use from several threads: each call spawns a full set of threads with no shared scheduler, so the machine is oversubscribed.

## How it is fast

Static data-parallel chunking (fork-join): the range is cut into hardware_concurrency() equal contiguous slices, each slice runs the ordinary sequential algorithm on its own std::thread, and the fold combines the per-thread partial results with one more std::accumulate after join. Nothing about the per-element work changes, so the gain is bounded by the core count and, for loops this light (one add per int), by memory bandwidth; counting 4 bytes read and 4 written per element, the relayed book figures put the parallel map near 15 GB/s against about 7 GB/s sequential (derived). Ranges of 10,000 elements or fewer skip the threads and call the sequential algorithm.

## Compared with alternatives

Pick it over the std::async sibling (recipe 8.10) only if you want plain threads and accept std::terminate on errors; that version's fold collects partial sums through futures that rethrow worker exceptions and it adds a recursive variant. For anything long-lived prefer std::execution::par (recipe 8.11 in the same repo), or a reusable pool such as BS::thread_pool or dispenso, which avoid creating threads on every call.

## Integration

| | |
|---|---|
| **Form** | source-drop (two function templates in one header of a book sample) |
| **Dependencies** | none (standard library only: &lt;thread&gt;, &lt;algorithm&gt;, &lt;numeric&gt;) |
| **Minimum toolchain** | C++17 for the code itself (std::invoke in the timer, C++14 std::plus&lt;&gt;); the repo builds with /std:c++latest or -std=c++2a and the README lists VC++ 2022 17.7, GCC 14 and Clang 19 |
| **Platforms** | any platform with std::thread; the repo's CMake is set up for Windows (top-level add_subdirectory uses lowercase chapterNN while the folders are ChapterNN, so configuring fails on case-sensitive file systems; issue #7, open) |
| **Thread safety** | Not documented. Each call is self-contained, but the caller must not touch the range during the call, and the functor is shared (and forwarded) across all worker threads. |
| **Drop-in for the baseline** | partial — same iterator-pair shape as std::transform/std::accumulate, but map is in place only, there is no execution-policy or output-iterator overload, and the operator must be associative |

## Gotchas

- std::thread::hardware_concurrency() may return 0 when the value is not computable, and the code divides the range size by it with no check (division by zero).
- The header is not self-contained for copying: it uses std::vector, std::setw and std::invoke without including &lt;vector&gt;, &lt;iomanip&gt; or &lt;functional&gt; (main.cpp's earlier includes cover it), and get_no_of_threads, test_mapreduce_threads and execute are non-inline functions defined in a header, so including it in two translation units breaks the link.
- Harness: one run per size, sequential always first, no warm-up or repetitions; the sums and vectors are consumed only by assert, so in an NDEBUG build the sequential timings are open to dead-code elimination while the thread-spawning parallel calls are not (a bias against the parallel side, not toward it). Thread creation and join are inside the parallel timing, and both sides work on freshly copied vectors, which is fair.
- Build configuration behind the book figures is not stated: the CMake files add no optimisation flag for any compiler (GCC and Clang get -g only), and the README's Visual Studio 2022 command generates a Win32 (32-bit) solution, while the book's machine is described as 64-bit Windows.

## Known shortcomings

- Book numbers only; the Chapter08 CMake adds no optimisation flags; inputs up to 10000 elements fall back to sequential. The harness is fair (fresh copies on both sides, thread start-up timed). Stale (last commit 2024-02-28).
- Enricher: data race on a forwarded stateful functor, division by zero when hardware_concurrency() is 0, sequential side may be dead-code-eliminated in NDEBUG builds, top-level CMake fails on Linux (issue #7).

## Caveats and trade-offs

The timing numbers are the book's own (quoted in the seed lead); the repository carries the benchmark program but no results file, so the numbers do not appear on the benchmark_url page and the ratios could not be checked against it. First-party book measurement, tier C: one run per size (the book itself notes run-to-run variation), compiler, optimisation flags and exact CPU not stated for this recipe; the repository's top-level CMakeLists adds only '/EHc /std:c++latest' for MSVC and '-std=c++2a -fexceptions -g -Wall' for GCC and Clang, so GCC and Clang builds through that file carry no optimisation flag. The baseline is single-threaded, so the gain is thread count (8 logical on 4 cores) and not a better algorithm; both loops are probably memory-bound, which would cap the gain well below the thread count. The sequential fold figure differs between this recipe (41374 us) and the std::async recipe (58689 us) for the same 50M elements, a spread as large as some of the claimed gains. Technique is an idiom, not a library: std::reduce or std::transform with std::execution::par (recipe 8.11) does the same job. [verifier] By reading the source (not compiled or run here): Chapter08/CMakeLists.txt adds no flags either, and the README lists VC++ 2022 17.7, GCC 14 and Clang 19 as tested toolchains, not the one used for the timings. Inputs at or below 10,000 elements fall back to the sequential algorithm inside parallel_map/parallel_fold. Both sides time freshly copied vectors (pages already touched) and thread creation and join sit inside the parallel timing, which is fair. [retier] Enricher: hardware_concurrency() can return 0 (division by zero); every worker calls std::forward&lt;F&gt;(f) on the same functor, so a stateful rvalue functor is moved from concurrently (data race); a worker throw or a std::thread constructor throw ends in std::terminate. One run per size with the sequential version always first; results feed only assert, so an NDEBUG build can eliminate the sequential work (bias against the parallel version). CMake gives GCC/Clang only -g; the README's VS2022 line uses -A Win32 (32-bit); the top-level add_subdirectory(chapterNN) does not match the ChapterNN folders, so configure fails on Linux (issue #7, open, no reply).

Hand-rolled chunking: splits the range into hardware_concurrency() equal parts, one std::thread each, no thread pool, no exception propagation (an exception in a worker calls std::terminate), threshold of 10,000 elements below which it falls back to the sequential algorithm. parallel_fold needs an associative operator and starts each partial sum from R{}. Needs random-access iterators. Up to hardware_concurrency extra threads per call.

## Maintenance

Stale MIT-licensed Packt companion repo (10 commits, code last changed 2024-02-23, README 2024-02-28; 7 issues with no maintainer replies), small enough to copy, but the parallel algorithms in &lt;execution&gt; are the maintained route.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter08/recipe_8_09.h is public code that times sequential std::transform/std::accumulate against parallel_map/parallel_fold on hardware_concurrency std::thread chunks, sizes 10,000 to 50,000,000, one run each with a microsecond chrono timer, but the repo has no results and no stated flags or CPU; the figures exist only in the book (first-party), so C.
- **Verifier notes:** Code matches the record (sizes list does include 50,000,000 here); tier C stands, only small caveat addenda. Same repo and recipe family as the std::async record; folding the two is an orchestrator call. Metadata confirmed on github.com: MIT, 170 stars, not fork or archived, last commit 2024-02-28 (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-85 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/blob/main/Chapter08/recipe_8_09.h>
  - <https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition>
  - <https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/commits/main>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/main/Chapter08/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/main/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/main/Chapter08/recipe_8_09.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/main/Chapter08/recipe_8_10.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/main/Chapter08/recipe_8_11.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/main/Chapter08/main.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/main/Chapter08/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/main/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/main/include/features.h>
  - <https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition>
  - <https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/commits/main>
  - <https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/issues?q=is%3Aissue>
  - <https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/issues/7>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-modern-cpp-programming-cookbook-third-edition-parallel-map-fold-std-thread`) · [data/wave1/enrich/raw/paper_book_modern_cpp_programming_cookbook_third_edition_parallel_map_fold_std_thread.json](../../../data/wave1/enrich/raw/paper_book_modern_cpp_programming_cookbook_third_edition_parallel_map_fold_std_thread.json) (enrichment confidence 0.65)

</details>
