# std::atomic counter (fetch_add, relaxed) against a std::mutex-guarded counter (Asynchronous Programming with C++ companion code)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Concurrent queues and locks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Relaxed std::atomic fetch_add on a shared counter in place of a std::mutex-guarded increment; teaching idiom, not a library.

| | |
|---|---|
| **Beats** | std::mutex lock/unlock around a shared uint32_t counter increment |
| **Claimed result** | Book Table 5.1, relayed by the seed lead and not present on the repo page: atomic counter 0.82 s, 4.52 s and 9.13 s against mutex 1.03 s, 10.15 s and 24.61 s at one, two and four threads, about 1.3x, 2.2x and 2.7x faster (derived from those book figures). |
| **Workload** | Several threads each increment one shared counter hundreds of millions of times (200 million per thread in the book's Table 5.1 at 1, 2 and 4 threads), timed with std::chrono::high_resolution_clock; the checked-in file runs 4 threads. |
| **Metric** | throughput |
| **Compiler and flags** | Not stated for the table. Root CMakeLists.txt adds -O3 -DNDEBUG only for CMAKE_BUILD_TYPE=Release and sets no default build type; README lists GCC 14.2, Clang 18, Boost 1.86, C++20/23 on Ubuntu 24.04. |
| **Adoption** | 95 stars |
| **Last commit** | 2026-04-22 |
| **Links** | [repository](https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP) · [benchmark](https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/blob/main/Chapter_05/5x01-atomic_flag.cpp) |

## Verdict

The book's Table 5.1, relayed by the seed lead and not in the repo, times 200 million increments per thread of one shared counter: relaxed fetch_add 0.82 s, 4.52 s and 9.13 s against std::mutex 1.03 s, 10.15 s and 24.61 s at 1, 2 and 4 threads, about 1.3x, 2.2x and 2.7x (derived from those figures). No CPU, compiler version or flags come with the table, and the repo's checked-in harness (single std::chrono run, unequal loop counts) does not regenerate it as is.

## Use it when

- Statistics, hit, byte or progress counters updated from many threads and read occasionally, where nothing else has to change together with the count.
- Reference counts, ID or ticket generators where a single fetch_add (using its returned old value) is the whole critical section.
- Code that takes a std::mutex only to protect one integer: per the book's Table 5.1 as relayed in the record, the atomic is cheaper even uncontended (0.82 s against 1.03 s for 200 million increments on one thread).
- Moderate contention on a counter that cannot be sharded, where the book's 2-4 thread figures show the mutex falling 2.2-2.7x behind.

## Skip it when

- Critical sections that update more than one variable or keep an invariant (counter plus container, check-then-act): an atomic counter does not protect them, so keep the mutex.
- Very hot counters hit by many threads: the atomic still serialises on one cache line. From the book figures, 4 threads doing 800 million increments took 9.13 s, about 2.8x longer than one thread at its 0.82 s per 200 million pace would need for the same total (derived from those figures); per-thread or sharded counters summed on read avoid this.
- When other threads must observe data written before the increment (publishing results, completion flags): relaxed gives no ordering, so use release/acquire or the default seq_cst.
- Counter types the platform cannot update lock-free: std::atomic of a large type silently uses an internal lock (the repo's 5x04-atomic_type_not_lock-free.cpp shows a 512-byte struct reporting is_always_lock_free false), which removes the advantage.

## How it is fast

The atomic increment is one hardware read-modify-write on the counter's cache line, so there is no lock acquire/release pair, no separate mutex word to bounce between cores, and no sleep/wake path when threads collide. Under contention the mutex adds lock handoffs and blocking on top of the cache-line ping-pong both variants pay, which is why the gap grows with thread count. memory_order_relaxed requests atomicity only, with no ordering of surrounding memory.

## Compared with alternatives

Same idiom as the sibling 'The Art of Writing Efficient Programs: std::atomic counter increment' entry (book figure 23 ns against 7 ns on one thread); this one adds 2- and 4-thread points and a spinlock middle option, so read both, copy neither harness. The queue siblings (atomic_queue, moodycamel, Boost.Lockfree, xenium) solve message passing; use this idiom when the shared state is a single integer.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the idiom (&lt;atomic&gt;); building the repo's example tree needs Boost 1.86 (thread, system, container), GoogleTest and {fmt} at the root, and Chapter_05 links libatomic |
| **Minimum toolchain** | C++11 for std::atomic and memory orders; the repo targets C++20/23 with GCC 14.2 or Clang 18 |
| **Platforms** | any platform with lock-free 32-bit atomics; repo README lists Linux (Ubuntu 24.04), macOS Sonoma and Windows 11 |
| **Thread safety** | fetch_add is safe for concurrent callers; memory_order_relaxed orders nothing else, so a reader can see the new count before the work it counts |
| **Drop-in for the baseline** | partial — one-for-one only when the mutex guards a single integer update; reads become atomic loads, and any multi-step critical section still needs the lock |

## Gotchas

- The checked-in file does not reproduce the book table like-for-like: the mutex loop runs 200000000 increments per thread but the spinlock and atomic loops run 500000000, with NUM_THREADS fixed at 4; divide by 2.5 or edit the loops before comparing printed times. Each variant is a single run with thread creation inside the timed region and no warm-up.
- The root CMakeLists.txt sets no default build type and adds -O3 -DNDEBUG only for Release, so a plain cmake configure builds the benchmark without optimisation flags; pass -DCMAKE_BUILD_TYPE=Release.
- The file uses std::mutex and uint32_t without including &lt;mutex&gt; or &lt;cstdint&gt;, relying on transitive includes of the standard library it was written against (other standard libraries not checked).
- The companion spin_lock is a bare test_and_set loop with no backoff or pause instruction; it is a teaching foil, not a lock to copy.

## Known shortcomings

- Book numbers only. Not like-for-like: the mutex runs 200M iterations per thread against 500M for the spinlock and atomic (4 threads); no #include &lt;mutex&gt;; no default build type.
- Enricher: unequal loop counts (mutex 200000000 per thread, atomic and spinlock 500000000), thread creation timed, single run, no default build type (plain cmake builds without -O); file frozen since 2024-09-08.

## Caveats and trade-offs

The book's timings are first-party and are not in the repo (no results file); no CPU, compiler version or flags are given with them. The checked-in Chapter_05/5x01-atomic_flag.cpp does not reproduce the table as described: it fixes 4 threads and runs 200000000 iterations per thread for the mutex variant but 500000000 for the spinlock and atomic variants, so its printed times are not like-for-like; it also lacks #include &lt;mutex&gt;. Release flags apply only if the user selects the Release build type. The latest commit (2026-04-22) is titled 'remove expired conference banner', so recent activity looks like repository upkeep rather than code work (code-change dates not checked). Not compared against other mutex or lock implementations. [retier] Enricher: unequal loops (mutex 200000000 iterations per thread, spinlock and atomic 500000000), NUM_THREADS fixed at 4, a single run, and thread creation inside the timed region. No default build type, so a plain cmake build has no -O flags. The file lacks &lt;mutex&gt; and &lt;cstdint&gt; includes; the spinlock is a bare test_and_set. The book figures show 4-thread atomic about 2.8x slower than one thread doing the same total (derived), so shard hot counters rather than relying on atomics alone.

A single shared counter only: an atomic does not protect multi-step critical sections, and relaxed ordering gives no ordering with other variables. The gap is for a maximal-contention microbenchmark with no work between increments.

## Maintenance

MIT-licensed book companion code (95 stars, 34 forks, not archived); this file last changed 2024-09-08 ('Cleaning and fixing unwanted warnings') and the 2026 commits only edit a README banner, so treat it as frozen teaching code and copy the three-line idiom rather than the harness.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter_05/5x01-atomic_flag.cpp times a std::mutex-guarded counter, an atomic_flag spinlock and relaxed fetch_add with 4 threads, but the repo has no results, no CPU and no default optimisation flags; Table 5.1 timings are the book's first-party numbers via the lead, so C.
- **Verifier notes:** Confirmed in source: NUM_THREADS 4, mutex loop 200000000 per thread against 500000000 for spinlock and atomic variants, no #include &lt;mutex&gt;; Chapter_05/CMakeLists.txt adds no flags and links Boost plus libatomic, root CMakeLists sets -O3 only for Release with no default build type. Record's caveats already cover this; book table not checkable here.
- **Fields the verifier corrected:** `maintenance_status`, `caveats`
- **Shortcomings recorded by:** verifier batch-86 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/commits/main>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/tree/main/Chapter_05>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/blob/main/Chapter_05/5x01-atomic_flag.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/Chapter_05/5x01-atomic_flag.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/Chapter_05/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/tree/main/Chapter_05>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/tree/main/Chapter_13>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/commits/main/Chapter_05/5x01-atomic_flag.cpp>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/issues?q=is%3Aissue>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/issues/26>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/issues/27>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/Chapter_05/5x01-atomic_flag.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/Chapter_05/5x04-atomic_type_not_lock-free.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/Chapter_05/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/Chapter_13/13x07-thread_contention.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-asynchronous-programming-with-cpp-atomic-counter-vs-mutex`) · [data/wave1/enrich/raw/paper_book_asynchronous_programming_with_cpp_atomic_counter_vs_mutex.json](../../../data/wave1/enrich/raw/paper_book_asynchronous_programming_with_cpp_atomic_counter_vs_mutex.json) (enrichment confidence 0.5)

</details>
