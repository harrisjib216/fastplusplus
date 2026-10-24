# The Art of Writing Efficient Programs: cache-line padding of per-thread partial sums

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Concurrent queues and locks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Per-thread counters spaced 128 bytes apart instead of in adjacent array slots, removing false sharing; book demo, not a library.

| | |
|---|---|
| **Beats** | Per-thread counters stored adjacent in a plain unsigned long array (false sharing) |
| **Claimed result** | Book: with the counters on separate cache lines the accumulation stays approximately twice as fast (Figure 5.8) and scales with the thread count. |
| **Workload** | Chapter05/04_local_incr.C (Google Benchmark, 1 to numcpu threads, real time): each thread increments its own counter 1024 times per iteration then adds it to a global atomic; BM_false_shared uses x2a[thread_index], BM_not_shared uses x3a[16\*thread_index] (128-byte stride). |
| **Metric** | throughput |
| **Hardware** | x86 server, 1 to 16+ threads; CPU model not stated |
| **Adoption** | 405 stars (Packt book companion repository) |
| **Last commit** | 2024-05-13 |
| **Links** | [repository](https://github.com/packtpublishing/the-art-of-writing-efficient-programs) · [benchmark](https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/blob/master/Chapter05/04_local_incr.C) |

## Verdict

The book, relayed by the seed lead, reports that with the counters on separate cache lines the per-thread accumulation stays about twice as fast as with adjacent counters (Figure 5.8) and keeps scaling with thread count; the ratio is the author's own, read from a chart, with no CPU model, compiler, flags or results file in the repository. The checked-in harness is symmetric (the same 1024 increments and one shared atomic add per iteration in both variants), so the comparison is fair, but the figure cannot be reproduced from the repository alone.

## Use it when

- Per-thread counters, partial sums, histograms or statistics slots kept in an array indexed by thread id and written in a hot loop.
- Thread pools or split loops where each worker writes its own result slot or progress field next to other workers' slots.
- Hot fields that ended up adjacent by accident (consecutive globals, an array of small per-thread structs): pad them or give them alignas(64) or a 128-byte stride.
- Scaling a counter past one shared atomic: accumulate per thread on separate lines and fold into the shared total rarely, as this harness does once per 1024 increments.

## Skip it when

- Single-threaded code or data that threads only read: there is no false sharing to remove, and the book's own claim is that the effect is absent at one thread.
- Large per-element arrays: padding 8-byte values to 64 or 128 bytes multiplies memory and cache footprint 8 to 16 times, which can cost more than it saves.
- Data that threads genuinely share (one counter everyone updates): padding does nothing for true sharing; use per-thread copies or a different algorithm.
- Expecting a fixed speedup: the 'about twice as fast' figure is one book chart on an unstated CPU, and the gain grows with thread count and write rate.

## How it is fast

Caches stay coherent per cache line, so when threads write different words of the same line the line moves between their caches on every write and each store waits for ownership even though no data is logically shared (false sharing). Spacing the counters 16 unsigned longs apart puts each on its own line, so increments stay in the writing core's cache and threads run independently. The 128-byte stride also separates adjacent-line pairs: folly sets its hardware_destructive_interference_size to 128 on non-ARM targets because its microbenchmarks saw destructive interference between line pairs under heavy atomic increments on Sandy Bridge.

## Compared with alternatives

The sibling 'alignas(64) per-thread result slots' entry from Asynchronous Programming with C++ shows the same fix with a much larger book figure (4403 ms against 160 ms, about 27x) and the cleaner alignas(64) form; this entry adds a Google Benchmark sweep over thread counts and a 128-byte stride that also covers adjacent-line pairs. Against the atomic-counter siblings, per-thread padded counters folded into one atomic are the usual next step when a single shared atomic becomes the bottleneck.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the technique; the benchmark file needs Google Benchmark and POSIX headers (unistd.h for sysconf) |
| **Minimum toolchain** | any C++ for manual stride padding, C++11 for alignas(64), C++17 for std::hardware_destructive_interference_size; the benchmark file needs Google Benchmark 1.5.x or older because it reads state.thread_index as a data member |
| **Platforms** | any; folly assumes 64-byte destructive interference on ARM and s390x and 128 bytes elsewhere, so a 128-byte stride is the conservative choice |
| **Thread safety** | Each padded slot must be written by one thread only; whoever sums the slots needs atomics or a join/barrier to see final values (the harness folds each counter into a std::atomic). |
| **Drop-in for the baseline** | partial — same code with a stride or alignas change, but the array grows 8 to 16 times and indexing changes from x[i] to x[16\*i] or to an array of aligned structs |

## Gotchas

- x3a is a plain unsigned long array without alignas; the padding comes only from the 16-element (128-byte) stride, which is enough for one 8-byte counter per thread but not for larger per-thread structs, which need alignas(64) or alignas(128) on the struct as 02_sharing_incr.C does with __attribute__((aligned(64))).
- 02_sharing_incr.C uses GCC's __attribute__((aligned(64))) and every file uses unistd.h and sysconf, so the code builds with GCC or Clang on POSIX only, although the README lists Visual Studio and Windows; use standard alignas when copying.
- std::hardware_destructive_interference_size is not a safe ABI constant: GCC warns (-Winterference-size) that its value can vary between compiler versions or -mtune/-mcpu flags, and folly suppresses that warning only on the assumption that the whole application is built with the same options; use a fixed 64 or 128 in public headers.
- The file reads state.thread_index as a data member, which Google Benchmark v1.6.0 (PR #1208, merged 2021-08-23) made private behind thread_index(), so it must be edited to compile against current releases; there is no Makefile or CMake file. The sweep runs 1 to sysconf(_SC_NPROCESSORS_CONF) unpinned threads including SMT siblings, and the shared accumulators x2 and x3 are unpadded globals next to the arrays, so their placement relative to thread 0's counter is up to the compiler and linker.

## Known shortcomings

- Book numbers only; no compiler, flags, CPU, build files or results in the repo. The padded array is not alignas(64), though its 128-byte stride covers it. Stale (last commit 2024-05-13).
- Enricher: files use the pre-1.6 Google Benchmark thread_index member and do not compile against current releases; shared accumulators unpadded.

## Caveats and trade-offs

The timing numbers are the book's own (quoted in the seed lead); the repository carries the benchmark program but no results file, so the numbers do not appear on the benchmark_url page and the ratios could not be checked against it. Only a ratio from the text; the chart values are in a figure image. The effect is zero at one thread and grows with thread count, so the single factor of 2 hides the shape. Textbook false-sharing result, not a library claim. Same chapter's 02_sharing_incr.C compares aligned and unaligned atomics, with the false-shared registrations commented out. Compiler, flags and CPU not stated. The repository has no Makefile, CMake file, build script or results file in Chapter05-07; the top-level README only lists 'GCC, Clang, Visual Studio' and Google Benchmark generically. Harness check: both variants do the same work (1024 DoNotOptimize(++x) increments per iteration, then one add to a shared global atomic), so the comparison is symmetric; the padded array is not alignas(64), but the 128-byte stride keeps each counter on its own cache line regardless. BM_local (a register-local counter) is in the file but commented out. [retier] Enricher: the harness is symmetric (1024 DoNotOptimize increments plus one shared atomic add on both sides; the benchmark's memory clobber forces each store). 04_local_incr.C and 02_sharing_incr.C use the pre-1.6 Google Benchmark state.thread_index member and do not compile against current releases without edits. The shared accumulators x2 and x3 are unpadded globals next to the arrays. folly pads to 128 bytes (adjacent-line prefetch since Sandy Bridge); GCC warns about std::hardware_destructive_interference_size ABI stability (-Winterference-size).

Costs 8 to 16 times the memory per counter; needs alignas(64) or manual padding (C++17 std::hardware_destructive_interference_size). No semantic change.

## Maintenance

MIT-licensed Packt companion repository (405 stars, 91 forks, not archived); Chapter05 has not changed since the September 2021 folder rename and the last commit is 2024-05-13, so copy the layout rule (alignas(64) or a 128-byte stride) rather than the harness.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter05/04_local_incr.C registers BM_false_shared (x2a[thread_index], adjacent 8-byte slots) against BM_not_shared (x3a[16\*thread_index], 128-byte stride), so the comparison code is public, but the only numbers are the book author's own with no compiler, flags or CPU model in the repo: first-party, tier C.
- **Verifier notes:** Code matches the record's workload description exactly; numbers are book-only and unverifiable from the repo. Metadata re-checked: MIT, 405 stars, not a fork or archived, last commit 2024-05-13 (stale).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-87 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter05/04_local_incr.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter05/02_sharing_incr.C>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/tree/master/Chapter05>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/commits/master>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/tree/master/Chapter05>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/commits/master/Chapter05>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter05/04_local_incr.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter05/02_sharing_incr.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter05/03_mutex_incr.C>
  - <https://github.com/google/benchmark/releases/tag/v1.6.0>
  - <https://github.com/google/benchmark/pull/1208>
  - <https://raw.githubusercontent.com/google/benchmark/v1.5.6/include/benchmark/benchmark.h>
  - <https://raw.githubusercontent.com/google/benchmark/v1.6.0/include/benchmark/benchmark.h>
  - <https://raw.githubusercontent.com/facebook/folly/main/folly/lang/Align.h>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-the-art-of-writing-efficient-programs-cache-line-padding-false-sharing`) · [data/wave1/enrich/raw/paper_book_the_art_of_writing_efficient_programs_cache_line_padding_false_sharing.json](../../../data/wave1/enrich/raw/paper_book_the_art_of_writing_efficient_programs_cache_line_padding_false_sharing.json) (enrichment confidence 0.55)

</details>
