# obstack (cleeus)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🔴 abandoned

> Pointer-bump C++ object-stack arena with destructor tracking; about 100x faster than glibc malloc in its own 2012 benchmark.

| | |
|---|---|
| **Beats** | malloc/free and new/delete (glibc-2.14.1, gcc-4.5.3 libstdc++, Linux 3.4) |
| **Claimed result** | Single thread (514,000 ops): obstack 272 ms vs malloc/free 26,882 ms vs new/delete 27,654 ms; 2 threads (538,000 ops): 162 ms vs 73,787 ms vs 90,000 ms; 4 threads (540,000 ops): 125 ms vs 108,245 ms vs 108,809 ms |
| **Workload** | Allocate and deallocate 514,000 ops totalling 1 GB (single thread) and 538,000/540,000 ops on two/four threads. |
| **Metric** | throughput |
| **Hardware** | Intel Atom N450 1.6 GHz, Linux 3.4 |
| **Compiler and flags** | gcc-4.5.3 -O2 |
| **Adoption** | 95 stars |
| **Last commit** | 2015-01-06 |
| **Links** | [repository](https://github.com/cleeus/obstack) · [benchmark](https://github.com/cleeus/obstack) |

## Verdict

arena_benchmark.cpp replays one seeded sequence of random sizes from 1 B to 4 MB (in-order, reverse and random free order) through malloc/free, new[]/delete[] and obstack, without touching the payload. On an Intel Atom N450 (gcc-4.5.3 -O2, glibc-2.14.1, Linux 3.4) the author got 272 ms vs 26,882 ms for malloc on 1 thread, and 125 ms vs 108,245 ms on 4 threads. Chunks average about 2 MB, so glibc's large-block mmap/munmap/trim path, a worst case for malloc, probably dominates the baseline. Multi-thread figures are per-thread times summed, not wall time. The README run used 1 GB total, but HEAD uses 512 MB after commit 9540299 ('lower memory usage in benchmark'), so HEAD does not reproduce the printed parameters exactly.

## Use it when

- Parsers (JSON, XML, DER) or request handlers that build many short-lived objects and drop them all together or in roughly LIFO order
- Per-thread scratch arenas where you know the peak size in advance and want no heap locking after setup
- Code that needs destructors run for arena objects (unlike plain bump allocators), with some hardening against forged free pointers
- Single-threaded hot loops where malloc/free of large, varied sizes shows up in profiles

## Skip it when

- Long-lived objects freed in random order: memory of a non-top object is not reusable until everything above it is freed, so the arena can stay full
- Anything needing a standard allocator interface: no std::allocator/pmr adapter (README says interest faded without N2554 scoped-allocator support)
- Unknown peak memory: capacity is fixed at construction and alloc returns NULL when it runs out, with no growth or chaining
- Sharing one arena across threads: no internal locking
- Production use without vetting: abandoned since 2015, C++03-era Boost code, arrays of non-POD types unsupported (TODO in header)

## How it is fast

Pointer bumping: each allocation aligns the top-of-stack pointer, writes a small chunk header (previous-chunk pointer, XOR-encrypted destructor pointer, checksum) and advances it, so no free lists are searched and no lock is taken. Freeing the top chunk rewinds the pointer past every chunk already marked destroyed; out-of-order frees only run the destructor and mark the chunk, so total work stays O(1) amortized. One arena per thread removes shared-heap contention.

## Compared with alternatives

Pick obstack over fast-alloc's pool and stack allocators when objects have mixed sizes and need destructors run on free, with out-of-order frees tolerated. SpeedMalloc is a general-purpose allocator with no public code and solves a different problem.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | Boost (utility, type_traits, static_assert headers; Boost.Random for the cookie in obstack.cpp; Boost.Thread and Boost.Test for benchmark and tests) |
| **Minimum toolchain** | C++03 (built with gcc-4.5.3 in the README); CMake 2.8 |
| **Platforms** | not documented (benchmarked on Linux x86) |
| **Thread safety** | Not thread-safe; intended as one arena per thread |
| **Drop-in for the baseline** | partial — replaces malloc/new only where objects are freed in bulk or LIFO order; different API (alloc&lt;T&gt;, alloc_array&lt;T&gt;, dealloc) |

## Gotchas

- With asserts disabled, dealloc of an invalid or already-destroyed pointer makes mark_as_destructed return NULL and the code then calls that NULL destructor pointer, so the 'pointer checking' turns a bad free into a crash, not a safe no-op
- The security cookies are seeded by XOR-ing 64 KiB of freshly new[]-ed, uninitialized heap memory (undefined behavior, weak entropy)
- The destructor runs after memory is reclaimed in pop(); a throwing destructor is not handled (TODO in header)
- Each object carries a chunk header plus alignment padding; size the arena with max_overhead(n), as the benchmark does

## Caveats and trade-offs

Arena (bump/stack-style) allocator versus general-purpose malloc, so semantics differ; the timing excludes allocating the arena itself, and each thread gets its own arena while malloc threads share the glibc heap. Chunks run from 1 B to 4 MB, so glibc mmap/munmap of large blocks probably dominates the baseline time. 2012-era Atom netbook, gcc-4.5.3 and glibc-2.14.1; the author calls the results preliminary. Abandoned since 2015. [retier] Arena allocator versus general-purpose malloc, so semantics differ; multi-thread times are per-thread sums, not wall time; payload never touched; average chunk about 2 MB so glibc mmap/trim probably dominates the baseline; HEAD runs 512 MB, the README run 1 GB; 2012-era Atom netbook, gcc-4.5.3, glibc-2.14.1; with asserts off an invalid or double dealloc crashes. Abandoned since 2015.

Pointer-bump memory arena; frees whole arena at once, not per-object free; C++ API.

## Maintenance

Abandoned (last commit 2015-01-06, benchmark untouched since August 2012, one open build issue from 2017), but BSL-1.0 and about 700 lines, so it is easy to vendor and modernize.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** Benchmark code is public (arena_benchmark.cpp at the repo root, timing malloc/free, new[]/delete[] and obstack on the same allocation and free sequences), and the README states gcc-4.5.3 with CFLAGS -O2, glibc-2.14.1, Linux 3.4 and the CPU (Intel Atom N450 1.6 GHz). Code, compiler, flags and CPU model are all present, so this is tier A (upgraded from C).
- **Retiered** A to C: Downgraded from A. Enricher read the harness: multi-thread times are per-thread sums rather than wall time, the payload is never touched, the average chunk is about 2 MB so the glibc mmap/trim path probably dominates the baseline, and HEAD uses 512 MB (commit 9540299) rather than the 1 GB of the printed README run, so the printed numbers do not reproduce exactly. Non-performance bugs: with asserts off an invalid or double dealloc calls a NULL dtor, and the cookie is seeded from uninitialized heap memory.
- **Verifier notes:** README numbers match the record exactly; I added the 2-thread row. Metadata checked on github.com: BSL-1.0 (LICENSE_1_0.txt), 95 stars, not archived, last commit 2015-01-06.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/cleeus/obstack>
  - <https://raw.githubusercontent.com/cleeus/obstack/HEAD/README.md>
  - <https://raw.githubusercontent.com/cleeus/obstack/HEAD/arena_benchmark.cpp>
  - <https://github.com/cleeus/obstack/commits>
- **Sources the enricher read:**
  - <https://github.com/cleeus/obstack>
  - <https://raw.githubusercontent.com/cleeus/obstack/HEAD/README.md>
  - <https://raw.githubusercontent.com/cleeus/obstack/HEAD/arena_benchmark.cpp>
  - <https://raw.githubusercontent.com/cleeus/obstack/HEAD/obstack.hpp>
  - <https://raw.githubusercontent.com/cleeus/obstack/HEAD/obstack.cpp>
  - <https://raw.githubusercontent.com/cleeus/obstack/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/cleeus/obstack/HEAD/max_alignment_type.hpp>
  - <https://github.com/cleeus/obstack/commits/master/arena_benchmark.cpp>
  - <https://github.com/cleeus/obstack/issues>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/cleeus/obstack`) · [data/wave11/enrich/raw/github_com_cleeus_obstack.json](../../../data/wave11/enrich/raw/github_com_cleeus_obstack.json) (enrichment confidence 0.75)

</details>
