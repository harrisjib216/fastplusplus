# Modern C++ Programming Cookbook 3rd ed.: parallel map and fold with std::async tasks

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Async tasks and thread pools](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Cookbook recipe: chunked parallel map and fold with std::async tasks, beating sequential std::transform and std::accumulate on large vectors.

| | |
|---|---|
| **Beats** | Sequential std::transform and std::accumulate (the std::thread version is a second reference) |
| **Claimed result** | Book-reported (relayed via the seed lead; no numbers anywhere in the repository; the shipped size list stops at 10,000,000, so the 50,000,000 row is not produced by the repository code): at 50,000,000 ints version1 map 22216 us vs 59665 us sequential (about 2.7x, derived from the relayed book figures), fold 12942 us vs 58689 us (about 4.5x, derived); faster than the std::thread version, especially for fold. The recursive version2 (map half deferred) was no better than sequential. |
| **Workload** | Chapter08/recipe_8_10.h test_mapfold_tasks: in-place map (i+i) and fold (sum into long long) over a std::vector&lt;int&gt;; version1 launches hardware_concurrency std::async(std::launch::async) tasks over equal chunks; version2 is a recursive halving variant; microsecond chrono perf_timer, single run per size. |
| **Metric** | throughput |
| **Hardware** | Windows 64-bit, Intel Core i7 (assumed the same 4 physical, 8 logical core machine as the std::thread recipe; not restated) |
| **Adoption** | 170 stars (Packt book companion repository) |
| **Last commit** | 2024-02-28 |
| **Links** | [repository](https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition) · [benchmark](https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/blob/main/Chapter08/recipe_8_10.h) |

## Verdict

Relayed from the book and absent from the repository: on a Windows 64-bit Intel Core i7 (assumed 4 cores, 8 threads) with 50,000,000 ints, version1 map took 22216 us against 59665 us for sequential std::transform (about 2.7x, derived) and fold 12942 us against 58689 us for std::accumulate (about 4.5x, derived), while version2 was no faster than sequential. One run per size; compiler, build type, flags and exact CPU are not stated, and the repo's harness only reaches 10,000,000 elements.

## Use it when

- Learning or prototyping coarse-grained data parallelism: the chunk, launch, join pattern in about 70 lines with only the standard library.
- A one-off parallel in-place transform or sum over millions of contiguous elements on a toolchain without C++17 parallel algorithms or a thread-pool library.
- Folds where a worker's exception must reach the caller: future::get rethrows it, which the std::thread sibling recipe cannot do.
- Large ranges only: the only relayed figures are at 50,000,000 ints, and at 10,000 elements or fewer the functions run sequentially anyway.

## Skip it when

- Repeated calls or many medium-sized ranges: every call starts hardware_concurrency() new tasks, which per the verifier is a new thread each on libstdc++ and libc++; a pool (dispenso, BS::thread_pool, Taskflow) or std::execution::par amortises that start-up.
- Folds whose identity is not R{} or whose operator is not associative: each chunk starts from R{} (0 for arithmetic types), so product, min or max folds return wrong answers, and version2 combines its halves with a hard-coded + instead of op.
- Stateful functors: f and op are passed through std::forward inside every task, so an rvalue functor is moved from once per task (concurrently in version1, twice per level in version2); only captureless lambdas and std::plus&lt;&gt; are exercised.
- version2 as a design: its map defers the left half with std::launch::deferred, so it runs on the caller and is effectively sequential, and its fold launches about size/10,000 async tasks (roughly 1,000 at 10,000,000 elements).
- Map callers that need errors: parallel_map waits with future::wait, which does not rethrow a worker's exception.

## How it is fast

Plain data parallelism: each task runs the ordinary sequential algorithm on its own contiguous slice, so N logical cores supply up to N times the compute and more memory bandwidth than one core can draw. The fold returns each chunk's partial result through std::future&lt;R&gt;::get and combines them with op. There is no algorithmic change, pooling or work stealing; for operations as cheap as i+i and a sum the gain stays well below the thread count (about 2.7x for map and 4.5x for fold on 8 logical cores in the relayed figures).

## Compared with alternatives

Over the std::thread sibling recipe (8.9) it uses the same chunking but returns partial sums through futures and rethrows fold exceptions, with slightly better relayed figures (map about 2.7x against 2.2x). For production code pick a pool sibling that reuses threads (dispenso, BS::thread_pool, Taskflow or utl::parallel, whose own table puts its pool at 573% of serial speed against 214% for std::async on small non-recursive jobs).

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond the standard library; recipe_8_10.h itself includes only &lt;iostream&gt;, &lt;algorithm&gt;, &lt;future&gt;, &lt;numeric&gt;, &lt;chrono&gt; and &lt;cassert&gt; and gets &lt;vector&gt;, &lt;thread&gt;, &lt;iomanip&gt; and &lt;functional&gt; through the headers Chapter08/main.cpp includes before it |
| **Minimum toolchain** | C++14 for the functions (deduced auto return type), C++17 for the perf_timer harness (std::invoke); the repo builds with /std:c++latest or -std=c++2a and its README lists VC++ 2022 17.7, GCC 14 and Clang 19 |
| **Platforms** | any platform with std::async threads; README targets Windows, Linux and Mac |
| **Thread safety** | Each element is touched by exactly one task; f and op are invoked concurrently from several tasks and must tolerate that; separate calls on disjoint ranges are independent. |
| **Drop-in for the baseline** | partial — same iterator-pair shape as std::transform/std::accumulate, but map is in place only (no output iterator), fold needs an associative op whose identity is R{}, and there is no execution policy or thread-count control |

## Gotchas

- hardware_concurrency() may return 0 when the core count is unknown; version1 then computes size / 0 before launching anything.
- The repo's top-level CMakeLists.txt calls add_subdirectory(chapter08) while the folder is Chapter08, so configuring fails on case-sensitive file systems (open issue #7, 2026-09-27, no reply); it also adds no optimisation flag, and the README's VS 2022 example configures -A Win32, so set the build type and target yourself before timing.
- The harness checks results only with assert (gone under NDEBUG), times each size once with a microsecond high_resolution_clock and no warm-up, and runs inside a program that executes every other Chapter 8 recipe first.
- The shipped size list stops at 10,000,000, so the book's 50,000,000-element row needs an edited list; its sequential fold baseline (58689 us) is about 42% slower than the std::thread recipe's 41374 us at the same size (derived), so the 4.5x fold ratio is probably inflated.

## Known shortcomings

- The shipped size list ends at 10M, so the book's 50M row cannot come from the repo code. The version2 fold launches about size/10000 std::async tasks (a new thread each on libstdc++/libc++, a pool on MSVC); the CMake adds no -O flag; the fold's 4.5x is likely inflated by a slow baseline (58689 vs 41374 us). Stale (last commit 2024-02-28).
- Enricher: wrong results for non-additive folds (R{} seed, hard-coded +), use-after-move of stateful functors, top-level CMake fails on Linux (issue #7); fold baseline 42% slower than in the std::thread recipe, so the 4.5x looks inflated.

## Caveats and trade-offs

The timing numbers are the book's own (quoted in the seed lead); the repository carries the benchmark program but no results file, so the numbers do not appear on the benchmark_url page and the ratios could not be checked against it. The shipped test in recipe_8_10.h stops at 10,000,000 elements (sizes 10000 to 10000000), so the 50,000,000-element row the book quotes cannot be produced without editing the size list. First-party tier C: single run per size, compiler, flags and CPU model not stated. The sequential fold baseline is 58689 us here against 41374 us in the std::thread recipe for the same data size, so the fold ratio (about 4.5x) is probably inflated by a slow or noisy baseline run; map baselines agree within 1% (59665 vs 60049 us). The baseline is single-threaded, so the gain comes from 8 threads and not a better algorithm. version2 uses std::launch::deferred for the map half, which runs on the calling thread, so it is effectively sequential and a poor foil. [verifier] By reading the source (not compiled or run here): version2's fold recurses with std::launch::async down to 10,000-element leaves, so it launches roughly size/10000 asynchronous tasks (about 1,000 at 10M elements), which is a new thread per task on libstdc++ and libc++ but runs on the Windows thread pool with MSVC, so version2 fold timings are not portable across standard libraries. The top-level CMakeLists.txt adds only '/EHc /std:c++latest' (MSVC) or '-std=c++2a -fexceptions -g -Wall' (GCC/Clang) and Chapter08/CMakeLists.txt adds none, so an optimised build depends on the chosen build type, which the book does not state. The README lists VC++ 2022 17.7, GCC 14 and Clang 19 as tested toolchains, not the one used for the timings. Both sides time freshly copied vectors (pages already touched) and thread or task start-up sits inside the parallel timing, which is fair. [retier] Enricher: fold seeds each chunk with R{}, so product, min and max give wrong results, and version2 combines halves with a hard-coded + instead of op; the rvalue functor is std::forward-ed once per task (use-after-move for stateful functors); hardware_concurrency() == 0 divides by zero. Top-level CMake configure fails on Linux (issue #7); main.cpp runs all Chapter 8 recipes in one process and checks results only by assert. The fold baseline is 58689 us here against 41374 us in the std::thread recipe (about 42% slower), suggesting the 4.5x is inflated.

Same chunking scheme as the std::thread recipe but with std::async futures, so worker exceptions propagate through future::get in the fold (the map waits with wait(), which does not rethrow). std::launch::async spawns a thread per task (implementation may or may not pool them); no pool control, threshold of 10,000 elements for the sequential fallback.

## Maintenance

MIT-licensed Packt companion repo (170 stars, 54 forks, 10 commits, last 2024-02-28) with the Linux CMake break reported in 2026 and unanswered; stale teaching code, fine to read and copy for the pattern but not a library to depend on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter08/recipe_8_10.h is public code that times sequential std::transform/std::accumulate against version1 (hardware_concurrency std::async(std::launch::async) chunks) and the recursive version2 with a microsecond chrono timer, one run per size, but the repo has no results and its CMake adds no optimisation flag; the 50M-element figures exist only in the book (first-party), so C.
- **Verifier notes:** Code matches the record; tier C stands. Added the version2 fold thread-count caveat and the CMake no-optimisation-flag note (already in the std::thread sibling). Records 2 and 3 are the same recipe family (8.9 std::thread, 8.10 std::async) on one repo and could fold into one entry if the orchestrator wants. Metadata confirmed on github.com: MIT (LICENSE: Copyright (c) 2023 Packt), 170 stars, not fork or archived, last commit 2024-02-28 'Update README.md' (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-85 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/blob/main/Chapter08/recipe_8_10.h>
  - <https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition>
  - <https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/commits/main>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/main/Chapter08/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition>
  - <https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/issues?q=is%3Aissue>
  - <https://github.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/issues/7>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/HEAD/Chapter08/recipe_8_10.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/HEAD/Chapter08/recipe_8_09.h>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/HEAD/Chapter08/main.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/HEAD/Chapter08/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/HEAD/chapter08/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Modern-Cpp-Programming-Cookbook-Third-Edition/HEAD/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-modern-cpp-programming-cookbook-third-edition-parallel-map-fold-std-async`) · [data/wave1/enrich/raw/paper_book_modern_cpp_programming_cookbook_third_edition_parallel_map_fold_std_async.json](../../../data/wave1/enrich/raw/paper_book_modern_cpp_programming_cookbook_third_edition_parallel_map_fold_std_async.json) (enrichment confidence 0.6)

</details>
