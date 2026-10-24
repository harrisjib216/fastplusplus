# The Art of Writing Efficient Programs: preallocate-once buffer instead of new[] and delete[] every iteration

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Book sample: allocate a scratch buffer once at its maximum size instead of new[]/delete[] on every loop iteration.

| | |
|---|---|
| **Beats** | Per-iteration new char[N] / delete[] (system operator new) |
| **Claimed result** | Book-reported (relayed via the seed lead; no numbers anywhere in the repository): allocating every iteration runs at about 40% of the speed of the version that allocates the maximum size once (preallocation about 2.5x faster, derived from the relayed book figure); the penalty is larger with 8 threads (book charts only). |
| **Workload** | Chapter09/04_buffer.C (Google Benchmark, 1 to numcpu threads, real time): build a random-size string of up to 1 KB with memset; BM_make_str_new allocates and frees each iteration, BM_make_str_max reuses one buffer of the maximum size allocated before the loop, BM_make_str_buf uses a grow-only buffer. |
| **Metric** | throughput |
| **Hardware** | CPU model not stated |
| **Compiler and flags** | Chapter02/ReadMe.md (linked from the root README as the how-to-run page) gives the generic build line: \$CXX (GCC or Clang) -g -O3 --std=c++17 -lpthread -latomic. Compiler version and CPU of the book's run are not stated. |
| **Adoption** | 405 stars (Packt book companion repository) |
| **Last commit** | 2024-05-13 |
| **Links** | [repository](https://github.com/packtpublishing/the-art-of-writing-efficient-programs) · [benchmark](https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/blob/master/Chapter09/04_buffer.C) |

## Verdict

The book, relayed by the seed lead (the repo holds no numbers), reports the per-iteration new char[N]/delete[] loop running at about 40% of the speed of the allocate-once loop (preallocation about 2.5x faster, derived) for random N up to 1 KB filled with memset, with a larger penalty at 8 threads in its charts. Compiler, standard library, allocator, flags and CPU of that run are not stated; the repo's generic build line is GCC or Clang -g -O3 --std=c++17, and the code was read, not built, here.

## Use it when

- A hot loop that needs a temporary buffer on every iteration (formatting, serialization, decompression or I/O staging) whose size has a known or cheaply bounded maximum.
- Scratch space that can live across many calls as an object member or a per-thread buffer, so one allocation serves the whole run.
- Sizes that vary per call but settle toward a stable maximum: the grow-only Buffer pattern (BM_make_str_buf) keeps the high-water allocation and stops reallocating after warm-up.
- Profiles that show malloc/free or operator new/delete high inside one loop, where restructuring that loop is easier than swapping the program's allocator.

## Skip it when

- The maximum size is unbounded or rarely reached: the buffer (or the grow-only high-water mark, which never shrinks) is held for the owner's lifetime.
- One buffer shared across threads or re-entrant calls: the pattern is only safe with one buffer per thread or per caller.
- The data must outlive the iteration (returned to a caller, queued, handed to another thread): reuse would overwrite live data.
- Expecting the book's roughly 2.5x in real code: it was measured at sizes up to 1 KB where a malloc/free pair costs about as much as the memset; with more work per iteration, larger buffers or a different allocator the share changes, and the repo has no data for those cases.

## How it is fast

Every new[]/delete[] pair goes through operator new and the C allocator's malloc/free path (size-class lookup, free-list pop and push, chunk bookkeeping); reusing one buffer removes those calls from the loop and leaves only the memset. With glibc, requests of up to 1032 bytes on 64-bit are served from the per-thread tcache, the allocator's cheapest path, so the gap this harness shows is the fast-path cost of a malloc/free pair against nothing. The grow-only variant amortizes the same way: it reallocates (copying the old contents) only when a request exceeds the largest size seen so far, so after warm-up it behaves like the preallocated buffer.

## Compared with alternatives

The siblings are drop-in allocators (mimalloc, snmalloc, jemalloc, TCMalloc, rpmalloc) and arenas (arena-allocator, fastcpp::arena); hoisting the buffer removes the allocator calls from the loop entirely with no dependency, so try it first when one hot loop allocates a bounded scratch buffer. Pick a drop-in allocator such as mimalloc when allocations are spread across the program and cannot be restructured, or an arena when many objects share one lifetime.

## Integration

| | |
|---|---|
| **Form** | source-drop (a code pattern; the grow-only Buffer class is about 10 lines) |
| **Dependencies** | none for the pattern; the benchmark needs Google Benchmark |
| **Minimum toolchain** | C++11 for std::unique_ptr&lt;char[]&gt;; the repo's generic build line (Chapter02/ReadMe.md) is GCC or Clang with -g -O3 --std=c++17 |
| **Platforms** | any for the pattern; the benchmark file includes unistd.h and calls sysconf(_SC_NPROCESSORS_CONF), so it builds on Linux and macOS only |
| **Thread safety** | Not thread-safe when one buffer is shared; the benchmark gives each thread its own buffer because each thread runs the benchmark function, which allocates locally |
| **Drop-in for the baseline** | partial — the same call sites work on the reused buffer, but you must move the allocation out of the loop, own the buffer's lifetime and know or bound the size |

## Gotchas

- Harness UB: the random-size table vr is built with reserve() and then written with v[i] = rand(), so its size() stays 0 and every vr[ir++ % nr] read in the timed loops is an out-of-bounds operator[] that only works because the moved buffer still holds the values; a build with _GLIBCXX_ASSERTIONS or MSVC debug iterators aborts.
- Only one size bound (Arg 1&lt;&lt;10) is benchmarked and every thread replays the same random sequence; at that size glibc takes each new[] from the per-thread tcache without locking, so the result covers only the allocator's fast path. The book's larger multi-thread penalty cannot be checked: the repo has no results and does not name the allocator or glibc version.
- The `if (r < 0) cout << buf` line never runs (rand() is non-negative); it is there so the compiler must keep the buffer and the memset. If it ever ran it would print an unterminated buffer. Keep some escape such as benchmark::DoNotOptimize when you copy this harness, or the timed work can be optimized away.
- Buffer::resize memcpy's the old contents on every growth even though callers overwrite them, and starts at 1 byte, so its first iterations reallocate; it is move-only (unique_ptr member).

## Known shortcomings

- Book numbers only. The vr table's size() stays 0, so every timed read is out of bounds (undefined behaviour; aborts under _GLIBCXX_ASSERTIONS); POSIX-only build (sysconf) and no build file in Chapter09; requests up to 1 KB hit glibc's tcache fast path. Stale (last commit 2024-05-13).
- Enricher: only 1 KiB buffers, served by glibc's lock-free tcache, so only the allocator fast path is measured; compiler line found in Chapter02/ReadMe.md (-g -O3 --std=c++17).

## Caveats and trade-offs

The timing numbers are the book's own (quoted in the seed lead); the repository carries the benchmark program but no results file, so the numbers do not appear on the benchmark_url page and the ratios could not be checked against it. Hoisting an allocation out of a loop is a general idiom, and the size of the win depends on the allocator (glibc malloc, tcmalloc and jemalloc differ) which the book does not name; requests of at most 1 KB fall in glibc's per-thread tcache range, so the result is specific to small-block allocator fast paths. The harness fills its random-size table with v[i] = rand() after only reserve(), writing past size() (undefined behaviour, works in practice), and the baseline also pays memset and a never-taken cout branch that the compared variants share. [verifier] By reading the source (not compiled or run here): the vector returned by that lambda keeps size() 0, so every vr[ir++ % nr] read in the timed loops is also an out-of-bounds operator[] access that only works because the moved buffer still holds the values; a build with _GLIBCXX_ASSERTIONS or MSVC debug iterators would abort. The file includes unistd.h and calls sysconf(_SC_NPROCESSORS_CONF), so it builds on Linux or macOS only. Chapter09 has no build file, so compiler, flags and CPU are not stated anywhere in the repository. [retier] Enricher: only Arg 1&lt;&lt;10 is run and every thread replays the same rand sequence; glibc serves sizes up to 1032 bytes from the per-thread tcache with no lock, so the run measures only the allocator's fast path and the book's 8-thread penalty cannot be checked. The never-taken cout &lt;&lt; buf branch is a deliberate escape against dead-code elimination (it would print an unterminated buffer if taken); Buffer::resize copies the old contents for nothing. The CPU is still unstated.

Holds the maximum buffer for the object's lifetime and needs the maximum size known or bounded; shared across calls it is not thread-safe unless one buffer per thread.

## Maintenance

Stale Packt companion repo (62 commits, last on 2024-05-13, 1 open issue) under MIT; nothing to vendor beyond the hoisting pattern or the 10-line Buffer class.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter09/04_buffer.C is public Google Benchmark code that times BM_make_str_new (new char[N]/delete[] every iteration) against BM_make_str_max (one buffer allocated before the loop) and BM_make_str_buf (grow-only buffer) at Arg 1&lt;&lt;10 over ThreadRange(1, numcpu), but Chapter09 has no build file, results or README and the repo README names no compiler, flags or CPU; the 40%-of-speed figure exists only in the book (first-party), so C.
- **Verifier notes:** Code matches the record (three variants, Arg 1&lt;&lt;10, ThreadRange(1, numcpu), UseRealTime); numbers are book-only, tier C stands. Added the size()-0 read UB and POSIX-only build to caveats. Metadata confirmed on github.com: MIT (LICENSE: Copyright (c) 2020 Packt), 405 stars, not fork or archived, last commit 2024-05-13 'Update README.md' (stale).
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`, `compiler_and_flags`
- **Shortcomings recorded by:** verifier batch-85 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/blob/master/Chapter09/04_buffer.C>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/commits/master>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/tree/master/Chapter09>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/LICENSE>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter09/04_buffer.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/ReadMe.md>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/tree/master/Chapter09>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/bminor/glibc/master/malloc/malloc.c>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-the-art-of-writing-efficient-programs-preallocated-buffer-reuse`) · [data/wave1/enrich/raw/paper_book_the_art_of_writing_efficient_programs_preallocated_buffer_reuse.json](../../../data/wave1/enrich/raw/paper_book_the_art_of_writing_efficient_programs_preallocated_buffer_reuse.json) (enrichment confidence 0.6)

</details>
