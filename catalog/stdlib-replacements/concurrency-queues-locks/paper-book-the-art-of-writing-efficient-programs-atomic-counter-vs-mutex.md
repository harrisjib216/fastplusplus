# The Art of Writing Efficient Programs: std::atomic counter increment instead of a mutex-guarded counter

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Concurrent queues and locks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> std::atomic fetch_add on a shared counter in place of a std::mutex-guarded ++x; a book idiom, not a library.

| | |
|---|---|
| **Beats** | std::mutex with std::lock_guard around ++x |
| **Claimed result** | Book: single-thread increment costs 23 ns under a mutex versus 7 ns for the atomic (about 3.3x, derived from the book figures); the gap widens with more threads. |
| **Workload** | Chapter06/01a_atomic_count.C against 01b_mutex_count.C (and BM_atomic against BM_mutex in 01_sharing_incr_mbm.C): Google Benchmark, one shared counter incremented by 1 to numcpu threads, real time. |
| **Metric** | latency |
| **Hardware** | x86; CPU model not stated |
| **Adoption** | 405 stars (Packt book companion repository) |
| **Last commit** | 2024-05-13 |
| **Links** | [repository](https://github.com/packtpublishing/the-art-of-writing-efficient-programs) · [benchmark](https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/blob/master/Chapter06/01_sharing_incr_mbm.C) |

## Verdict

Per the book figures relayed in the record, one thread incrementing a shared counter costs about 23 ns under std::lock_guard&lt;std::mutex&gt; against about 7 ns as an atomic increment (about 3.3x, derived from those figures), and the gap widens with more threads. The repository has the benchmark code but no results, compiler, flags, standard library or CPU model, and it does not say which file produced the 7 ns figure, so that figure may carry the mbm file's 2x items-per-iteration error.

## Use it when

- Statistics, hit or byte counters bumped from many threads and read occasionally, where nothing else has to change together with the count.
- ID, ticket or sequence generators where the old value returned by a single fetch_add is the whole critical section.
- Existing code that takes a std::mutex only around ++counter: the book figures relayed in the record put one thread at about 23 ns per locked increment against about 7 ns atomic, with the gap widening as threads are added.
- As a reference point before trying other schemes: the same Chapter06 folder times a CAS loop (01e), a spinlock (01c) and a pointer lock (01d) on the identical counter, so one build compares all five.

## Skip it when

- Updates that touch more than one variable or keep an invariant (counter plus container, check-then-act): one atomic word does not protect them, so keep the lock or use a concurrent data structure.
- Very hot counters updated by every thread: the atomic still serialises on one cache line, so it does not scale; per-thread counters on separate cache lines that are folded into the total rarely (the sibling Chapter05 padding entry) avoid that single hot line.
- Read-modify-write logic that is not a plain add (saturating, conditional, min/max): that needs a compare_exchange loop like 01e_cas_count.C, which can retry repeatedly under contention.
- Running the harness as-is on a current toolchain: the files target the pre-1.6 Google Benchmark API and the repo ships no build files (see gotchas).

## How it is fast

An atomic increment is one locked read-modify-write on the counter's cache line, while even an uncontended mutex needs an atomic acquire of the lock word, the increment, and an atomic release, plus the calls into the threading library. Under contention the mutex adds lock handoffs and possible blocking on top of the cache-line transfers both variants pay, so the gap grows with thread count. Relaxed ordering is enough for a pure counter; on x86 relaxed and sequentially consistent fetch_add both compile to the same locked add.

## Compared with alternatives

Same idiom as the sibling 'std::atomic counter (fetch_add, relaxed) against a std::mutex-guarded counter' entry from Asynchronous Programming with C++ (book Table 5.1 at 1, 2 and 4 threads); this one is a Google Benchmark harness that sweeps up to every logical CPU and also times a CAS loop, a spinlock and a pointer lock on the same counter. The queue siblings (atomic_queue, moodycamel, Boost.Lockfree, xenium) are for passing data between threads; use this idiom when the only shared state is one integer.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the idiom (&lt;atomic&gt;); the benchmark files need Google Benchmark and POSIX headers (unistd.h for sysconf; the spinlock and pointer-lock variants also call nanosleep) |
| **Minimum toolchain** | C++11 for std::atomic and memory orders; the benchmark files need Google Benchmark 1.5.x or older, because they read state.thread_index as a data member that v1.6.0 replaced with thread_index() |
| **Platforms** | any platform with lock-free 64-bit atomics for the idiom; the benchmark files are POSIX-only (unistd.h, sysconf) although the README lists Visual Studio and Windows |
| **Thread safety** | The atomic counter is safe for concurrent increments and reads; memory_order_relaxed orders nothing else, so the count must not be used to publish other writes. |
| **Drop-in for the baseline** | partial — replaces a mutex-guarded single-integer increment exactly; does not replace a mutex that guards several fields or an invariant |

## Gotchas

- Chapter06/01_sharing_incr_mbm.C repeats ++x 64 times per BM_atomic iteration (REPEAT is REPEAT64) but reports SetItemsProcessed(32\*iterations), so its atomic items/s is half the true rate and its time per item double; 01a_atomic_count.C (one fetch_add per iteration) is the clean file. Chapter05/03_mutex_incr.C has the opposite mismatch (32 locked increments per iteration reported as 32\*32 items).
- 01a, 01b, 01c, 01e and 01_sharing_incr_mbm.C read state.thread_index as a data member; Google Benchmark v1.6.0 (PR #1208, merged 2021-08-23) made that member private behind a thread_index() accessor, so these files fail to compile against current releases until edited. Only 01d_ptrlock_count.C already calls thread_index(). There is no Makefile or CMake file, so compiler and flags are not recorded.
- The thread sweep runs from 1 to sysconf(_SC_NPROCESSORS_CONF), which counts configured logical CPUs including SMT siblings, and threads are not pinned; the high-thread points therefore depend on thread placement, and the mutex cost depends on the standard library (libstdc++, libc++, MSVC).
- 01a uses fetch_add(memory_order_relaxed) while the mbm file's BM_atomic uses a sequentially consistent ++x; both are the same locked add on x86, but they can differ on weakly ordered CPUs, so do not mix numbers from the two files there.

## Known shortcomings

- Book numbers only. Item-count bugs: BM_atomic does 64 operations but reports 32 items, and Chapter05/03_mutex_incr.C does 32 but reports 1024; the repo does not say which file produced the book's 7 ns.
- Enricher: mbm file reports 32 items for 64 operations (2x error); most files use the pre-1.6 Google Benchmark thread_index member and do not compile against current releases; no build files.

## Caveats and trade-offs

The timing numbers are the book's own (quoted in the seed lead); the repository carries the benchmark program but no results file, so the numbers do not appear on the benchmark_url page and the ratios could not be checked against it. Obvious result for a one-word counter; the interest is the size of the gap. In 01_sharing_incr_mbm.C BM_atomic repeats the increment 64 times per iteration (REPEAT is REPEAT64) but reports 32 items per iteration, which doubles its reported time per item, so the per-item figures from that file are inconsistent; 01a_atomic_count.C does one fetch_add per iteration and is correct. Chapter05/03_mutex_incr.C has the opposite mistake (32 lock and increment per iteration, 1024 items reported). Compiler, flags, CPU and standard library not stated, and the cost of an uncontended std::mutex differs between libstdc++, libc++ and MSVC. The repository has no Makefile, CMake file, build script or results file in Chapter05-07; the top-level README only lists 'GCC, Clang, Visual Studio' and Google Benchmark generically. Harness check: 01a uses fetch_add(memory_order_relaxed) while the mbm file's BM_atomic uses a sequentially consistent ++x; both compile to a locked add on x86 but differ on weakly ordered CPUs. Which file produced the book's 7 ns figure is not stated in the repo, so it may carry the mbm file's 2x reporting error. Sibling files 01c_spinlock_count.C, 01d_ptrlock_count.C and 01e_cas_count.C time the same counter under a spinlock, a pointer lock and a CAS loop. [retier] Enricher: confirmed: 01_sharing_incr_mbm.C runs REPEAT64 but reports 32 items, so its atomic items/s is off by 2x (01a is clean). 01a, 01b, 01c, 01e and the mbm file read state.thread_index as a data member, which Google Benchmark v1.6.0 (PR #1208, 2021-08-23) made private behind thread_index(), so they do not compile against current Google Benchmark without edits (only 01d uses thread_index()). No build files; the thread sweep runs to _SC_NPROCESSORS_CONF unpinned, including SMT siblings; POSIX-only despite the README listing MSVC.

Atomic fetch_add only guards a single word; anything bigger than one counter needs a lock or a lock-free design.

## Maintenance

MIT-licensed Packt companion repository (405 stars, 91 forks, not archived) whose Chapter06 folder last changed in a 2022-11-30 upload and whose last commit is 2024-05-13; treat it as frozen teaching code, copy the one-line idiom, and port the harness to thread_index() before running it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter06/01_sharing_incr_mbm.C registers BM_atomic against BM_mutex (std::lock_guard&lt;std::mutex&gt; around ++x), and 01a_atomic_count.C/01b_mutex_count.C split the same pair, so the comparison code is public, but the 23 ns and 7 ns figures are the book author's own with no compiler, flags or CPU model in the repo: first-party, tier C.
- **Verifier notes:** Code matches the record; reporting-count bugs in 01_sharing_incr_mbm.C (64 ops, 32 items) and Chapter05/03_mutex_incr.C (32 ops, 1024 items) confirmed. Numbers book-only.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-87 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter06/01_sharing_incr_mbm.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter06/01a_atomic_count.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter06/01b_mutex_count.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter05/03_mutex_incr.C>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/tree/master/Chapter06>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/commits/master>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/tree/master/Chapter06>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/commits/master/Chapter06>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter06/01_sharing_incr_mbm.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter06/01a_atomic_count.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter06/01b_mutex_count.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter06/01c_spinlock_count.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter06/01d_ptrlock_count.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter06/01e_cas_count.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter05/03_mutex_incr.C>
  - <https://github.com/google/benchmark/releases/tag/v1.6.0>
  - <https://github.com/google/benchmark/pull/1208>
  - <https://raw.githubusercontent.com/google/benchmark/v1.5.6/include/benchmark/benchmark.h>
  - <https://raw.githubusercontent.com/google/benchmark/v1.6.0/include/benchmark/benchmark.h>
  - <https://raw.githubusercontent.com/google/benchmark/v1.7.0/include/benchmark/benchmark.h>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-the-art-of-writing-efficient-programs-atomic-counter-vs-mutex`) · [data/wave1/enrich/raw/paper_book_the_art_of_writing_efficient_programs_atomic_counter_vs_mutex.json](../../../data/wave1/enrich/raw/paper_book_the_art_of_writing_efficient_programs_atomic_counter_vs_mutex.json) (enrichment confidence 0.55)

</details>
