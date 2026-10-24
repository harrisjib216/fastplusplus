# Hands-On Design Patterns with C++ 2nd ed: small_queue, a fixed-capacity circular-buffer queue with local storage

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Sequence containers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> A 20-line fixed-capacity ring-buffer int queue stored inside the object, benchmarked against std::queue&lt;int&gt; (std::deque); buggy as published.

| | |
|---|---|
| **Beats** | std::queue&lt;int&gt; |
| **Claimed result** | Book table (relayed via the seed lead from the book, not shown on any repo page I opened): std::queue&lt;int&gt; 472 ns per iteration (67.8M items/s) against small_queue 100 ns (319.9M items/s). About 4.7x (derived from the relayed numbers). |
| **Workload** | Google Benchmark, per iteration 32 repetitions of: push 7 ints, then while not empty read front() (DoNotOptimize) and pop(); std::queue&lt;int&gt; against small_queue (a 16-int power-of-two ring buffer inside the object). |
| **Metric** | throughput |
| **Compiler and flags** | Not stated. The repo has no build files (no CMakeLists.txt or Makefile at the root or in Chapter10); the README lists only 'GCC, Clang or Visual Studio' for Chapter 1 and no flags. |
| **Adoption** | 137 stars; Packt companion repository of the book Hands-On Design Patterns with C++, 2nd ed. (2023) |
| **Last commit** | 2024-08-29 |
| **Links** | [repository](https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition) · [benchmark](https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/blob/main/Chapter10/08_small_queue.C) |

## Verdict

The book reports (relayed by the seed lead; no numbers in the repo) 472 ns against 100 ns per benchmark iteration, about 4.7x, for 32 rounds of push 7 ints then drain, std::queue&lt;int&gt; on its default std::deque&lt;int&gt; against small_queue; standard library, compiler, flags and CPU are not stated. The timing was taken on the off-by-one version; by reading the code, the fix (post-increment, &gt;= in the full check) adds no loads, stores or branches to the hot path, so the ratio plausibly carries over, but nobody has published a rerun.

## Use it when

- The maximum queue depth is small and known at compile time (a handful to a few dozen trivially copyable elements), e.g. a lookahead or pending-event buffer that is filled and drained in a hot loop.
- Profiles show std::deque node allocation or its segmented indexing in a queue that never holds many elements.
- Single-threaded code where a queue object is created per call or per item and heap traffic matters.
- As a pattern to copy, template on element type and capacity, and fix (see gotchas) rather than as a dependency.

## Skip it when

- As published: front() returns the wrong element (open issue #22) and the full check lets a 17th element overwrite a live slot, so the file is not a correct FIFO.
- Unbounded or data-dependent depth: push() simply returns false at capacity and nothing grows.
- Element types other than int, or non-trivial types: the class is hard-wired to int and has no placement construction or destruction logic.
- Concurrent producers and consumers: the indices are plain size_t with no atomics; use a single-producer/single-consumer ring buffer instead.
- Large capacities embedded in objects that are copied or moved often: the whole buffer is copied with the object.

## How it is fast

The storage is an in-object array, so the queue never touches the heap; std::queue&lt;int&gt; defaults to std::deque&lt;int&gt;, which allocates fixed-size nodes and keeps a node map (with libstdc++, 512-byte nodes of 128 ints per the GCC 13 header, so a push-7/drain-7 cycle allocates and frees a node roughly every 18 rounds). Capacity is a power of two, so wrap-around is a bitmask (& 15) on two free-running size_t counters instead of a modulo or a segmented iterator, and every operation is a few inlinable instructions.

## Compared with alternatives

For a real fixed-capacity in-object queue, ETL's etl::queue&lt;T, SIZE&gt; (from the catalogued ETL library) is templated, maintained and checks full() on push; plf::stack is the catalogued pick when the access pattern is LIFO rather than FIFO against a deque-backed adaptor. Take small_queue only as a short teaching example to copy, fix and template.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the class; the file's benchmark needs Google Benchmark (no build files in the repo; unmerged third-party PR #8 adds a Chapter10 CMakeLists.txt that fetches benchmark v1.7.1) |
| **Minimum toolchain** | C++11 (static constexpr member, default member initializers, static_assert); PR #8 builds the chapter as C++20. The repo README lists only 'GCC, Clang or Visual Studio'. |
| **Platforms** | any |
| **Thread safety** | not documented; non-atomic indices, single-threaded use only |
| **Drop-in for the baseline** | partial — same push/front/pop/empty names, but push returns bool and fails at 16 elements, no back()/emplace(), int only, and the published push/front pair is off by one |

## Gotchas

- Off-by-one: push() writes buf_[(++front_) & 15] while front() reads buf_[tail_ & 15], so front() returns the element pushed one step earlier and the first read is an uninitialised slot. A reduced copy run by the enricher (GCC 13.3) pushed 100..106 and read back 0, 100..105. Issue #22 (opened 2024-04-27, no reply) proposes front_++; it is unfixed on main.
- The full check (front_ - tail_ &gt; 16) admits a 17th element into the 16-slot buffer, overwriting the oldest live entry (the reduced copy accepted 17 of 20 pushes); it should be &gt;=. The benchmark never holds more than 7 elements, so neither bug shows in its timing.
- The benchmark calls SetItemsProcessed(32 \* iterations) although each iteration pushes and pops 224 ints (32 rounds of 7), so the reported items/s are 7x low on both sides; the ratio is unaffected.
- No results, compiler, flags or CPU are in the repo; the unmerged CMake PR sets no build type or optimization flags, so a default build of it would not reproduce an optimized run.

## Known shortcomings

- Correctness bugs in the measured code: front()/push() indices are off by one and the 17th element overflows the buffer. SetItemsProcessed counts 32 items per iteration while each does 224 operations, so items/s is 7x low (the ratio is unaffected). No build files in the repo.
- Enricher: off-by-one bugs confirmed by a reduced build (reads back a stray 0 and drops the last item; accepts 17 of 20 pushes; issue #22 unanswered); items/s 7x low on both sides.

## Caveats and trade-offs

The queue as written in this file is functionally wrong (by reading the source, not compiled or run here): push() writes buf_[(++front_) & 15] while front() reads buf_[tail_ & 15], so front() returns the element pushed one step earlier (the first read is an uninitialised slot) and the last pushed element is never read; the benchmark only passes front() to DoNotOptimize and checks no values, so the timing does not catch it, but the 4.7x is measured on a container that is not yet a correct FIFO. The size check (front_ - tail_ &gt; 16) also lets a 17th element in, overwriting a live slot. state.SetItemsProcessed(32\*iterations) counts 32 items per iteration although each iteration pushes and pops 224 ints (32 x 7), so the items/s figures understate real throughput 7x on both sides (the ratio is unaffected). Bounded versus unbounded, so not a drop-in replacement; std::queue&lt;int&gt; uses its default std::deque&lt;int&gt;. Book numbers, compiler, flags and CPU not stated, first-party. Tier C. File opened: Chapter10/08_small_queue.C. [retier] Enricher: off-by-one bugs confirmed by running a reduced copy (GCC 13.3): pushing 100..106 reads back 0, 100..105, and 17 of 20 pushes are accepted (issue #22, open since 2024-04-27, no reply); the timed work is the same push/pop loop, so the speed comparison stands but the container is not correct. SetItemsProcessed is 7x low on both sides (ratio unaffected). No build files; the unmerged CMake PR #8 sets no build type or flags. etl::queue&lt;T, SIZE&gt; is a correct fixed-capacity alternative.

Fixed capacity of 16 ints inside the object (push returns false when full), no heap allocation, no growth, trivially small; std::queue&lt;int&gt; is unbounded and deque-backed. Useful only when the maximum depth is known and small.

## Maintenance

Stale Packt companion repo (last commit 2024-08-29; issue #22 and 18 CMake PRs open without response), MIT-licensed and about 20 lines, so copy it and apply the two fixes rather than depend on it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter10/08_small_queue.C registers BM_queue&lt;std::queue&lt;int&gt;&gt; and BM_queue&lt;small_queue&gt; with Google Benchmark on the same push-7/pop-all loop repeated 32 times, but the repo holds no results, build files, flags or CPU; the 472 ns versus 100 ns figures are the book's own run, so first-party with incomplete methodology.
- **Verifier notes:** Off-by-one front()/push() bug and 17th-element overflow confirmed from source; extra harness defect: items-processed counter is 7x low. MIT, 137 stars, last commit 2024-08-29 (stale) confirmed; README errata cover only page 64. baseline_in_list left true since std::queue&lt;int&gt; is an adaptor over std::deque (listed), though std::queue itself is not named in the category list.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-82 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/main/Chapter10/08_small_queue.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/main/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/main/README.md>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/commits/main>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/tree/main/Chapter10>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/main/Chapter10/08_small_queue.C>
  - <https://raw.githubusercontent.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/main/README.md>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/tree/main/Chapter10>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/issues?q=is%3Aissue>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/issues/22>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/pulls>
  - <https://github.com/PacktPublishing/Hands-On-Design-Patterns-with-CPP-Second-Edition/pull/8/files>
  - <https://raw.githubusercontent.com/ETLCPP/etl/master/include/etl/queue.h>
  - <https://raw.githubusercontent.com/ETLCPP/etl/master/include/etl/circular_buffer.h>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-hands-on-design-patterns-with-cpp-second-edition-small-queue`) · [data/wave1/enrich/raw/paper_book_hands_on_design_patterns_with_cpp_second_edition_small_queue.json](../../../data/wave1/enrich/raw/paper_book_hands_on_design_patterns_with_cpp_second_edition_small_queue.json) (enrichment confidence 0.7)

</details>
