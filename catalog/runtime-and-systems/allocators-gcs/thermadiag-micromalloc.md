# micromalloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Low-overhead general-purpose C/C++ malloc that usually beats glibc malloc on speed while using about as little memory.

| | |
|---|---|
| **Beats** | glibc malloc |
| **Claimed result** | Memory overhead very close to glibc but with better performance; cross-thread: slower than snmalloc and jemalloc yet above glibc with the lowest memory overhead; Larson scales well. No exact numbers (plots only). |
| **Workload** | Same-thread and cross-thread alloc/dealloc plus Larson, measuring Mops/s and memory overhead ratio against glibc 2.17, jemalloc 5.3.0, mimalloc 1.8 and snmalloc 3.14. |
| **Metric** | memory |
| **Hardware** | Intel Xeon Gold 5220R 2.20GHz, 95 processors, CentOS 7 |
| **Compiler and flags** | GCC 10.3.0 (flags not stated) |
| **Adoption** | 33 stars |
| **Last commit** | 2024-11-14 |
| **Links** | [repository](https://github.com/Thermadiag/micromalloc) · [benchmark](https://github.com/Thermadiag/micromalloc/blob/main/md/benchmarks.md) |

## Verdict

First-party plots (md/benchmarks.md) compare micro with glibc 2.17, jemalloc 5.3.0, mimalloc 1.8 and snmalloc 3.14, built with gcc 10.3.0 (flags not stated) on a Xeon Gold 5220R under CentOS 7: same-thread alloc/free of random sizes up to 500 or 5000 bytes for 1-10 threads, a cross-thread random-free test and Larson, plotting Mops/s against peak-RSS/requested-bytes. Micro is faster than glibc with similar overhead, slower than snmalloc and jemalloc, and has the lowest overhead cross-thread; no numbers are given in text. Harness note from benchs/alloc_dealloc_same_thread.cpp: every allocator runs in sequence in one process (micro first), and overhead is computed from getrusage peak RSS, which is a lifetime maximum. If the plots came from such runs, later allocators' overhead can never read lower than micro's peak. The cleanup call (micro_clear, malloc_trim, mi_heap_collect) is inside the timed region, and snmalloc gets no cleanup.

## Use it when

- Replacing glibc malloc (or the Windows Low-fragmentation Heap) system-wide or per-process where resident memory matters more than the last bit of throughput.
- Many-threaded programs where glibc malloc scales negatively and per-thread caches in jemalloc/mimalloc would inflate RSS.
- Workloads that create and destroy many short-lived threads (Larson-style servers).
- Arena-style code that wants independent heaps freed in one call, or allocation out of a fixed buffer or a memory-mapped file.
- Small-memory systems: memory level 0 targets machines with only a few MBs.

## Skip it when

- Raw allocation throughput is the goal: the README says it is usually slower than mimalloc, snmalloc, tbbmalloc and jemalloc, and the cross-thread plot shows snmalloc and jemalloc well ahead.
- Security-sensitive or attacker-facing heaps: the README states it has no hardening against heap exploitation.
- macOS and Android: replacement of the system allocator is untested there per the README.
- Huge-page dependent workloads: huge pages are not supported yet.
- Projects that need a well-tested, widely deployed allocator: single author, 33 stars, test suite described as incomplete.

## How it is fast

Medium allocations (under 512 KiB) use a two-level radix tree of free chunks sorted by size with fine-grained locking: a true best-fit with immediate coalescing, O(1) like TLSF but exact instead of approximate. Small allocations (under 656 bytes by default) use 16-byte-spaced segregated size classes in 4 KiB-aligned blocks whose header is found by address masking, and those blocks are themselves carved from the radix tree. Threads are bound round-robin to per-core arenas instead of using thread-local caches, which keeps memory low and makes thread creation cheap (the reason it does well on Larson).

## Compared with alternatives

Pick it over v8malloc or FastAlloc when lower RSS than glibc matters more than throughput, and over Mesh when you want low overhead without page meshing; pick a TLSF allocator like XenoAtom.Allocators or rlsf instead for a single-threaded or embedded pool with deterministic timing.

## Integration

| | |
|---|---|
| **Form** | static lib, shared lib, or header-only (define MICRO_HEADER_ONLY); micro_proxy for malloc replacement |
| **Dependencies** | none (embeds a simplified komihash) |
| **Minimum toolchain** | C++14 (CMake 3.8+); gcc, clang or msvc |
| **Platforms** | Linux and most Unix systems, Windows; macOS/Android untested for replacement |
| **Thread safety** | Thread-safe: per-core arenas with fine-grained locking in the radix tree; MICRO_NO_LOCK build option removes locking for single-threaded systems |
| **Drop-in for the baseline** | partial — link micro_proxy (or use the mp LD_PRELOAD tool) to replace malloc/free process-wide; otherwise call the micro_\* API explicitly |

## Gotchas

- Memory profile is a compile-time choice (MICRO_MEMORY_LEVEL 0-4, default 2); levels 3-4 trade memory for speed, and the radix tree has a static per-arena cost that grows with the level.
- Arena depletion (MICRO_DEPLETE_ARENAS=1, default) lowers memory at the expense of parallelism; behavior is also tunable through many MICRO_\* environment variables read at startup.
- With the file page provider, setting MICRO_PAGE_FILE_PROVIDER to a fixed filename makes spawned child processes share the same file ('certain crash' per the README); use MICRO_PAGE_FILE_PROVIDER_DIR instead.
- All allocations are only 16-byte aligned.

## Known shortcomings

- Measurement flaw in benchs/alloc_dealloc_same_thread.cpp: all allocators run in sequence in one process with micromalloc first, and the overhead uses getrusage peak RSS, a lifetime maximum, so later allocators cannot read lower than micromalloc's peak; cleanup is inside the timed region and snmalloc gets no cleanup. This weakens the 'lowest memory overhead' claim.

## Caveats and trade-offs

README admits it is usually not faster than mimalloc, jemalloc or snmalloc; the claim to beat glibc is shown only as plots; first-party; flags not stated.

Low memory overhead by design; usually slower than mimalloc, snmalloc, tbbmalloc, jemalloc; O(1) alloc and free; can allocate from preallocated buffers or memory-mapped files.

## Maintenance

Stale since late 2024 (one closed issue, single author) but MIT-licensed, dependency-free and usable header-only, so it is easy to trial via the mp LD_PRELOAD tool before committing.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** md/benchmarks.md compares against glibc 2.17, jemalloc 5.3.0, mimalloc 1.8 and snmalloc 3.14 with gcc 10.3.0 on a Xeon Gold 5220R, and the benchs/ code is public, but compiler flags are not stated and results are plots only, so C.
- **Verifier notes:** Page text matches the record: lower memory overhead, faster than glibc (which scales negatively with threads), slower than snmalloc and jemalloc. Metadata (MIT, 33 stars, last commit 2024-11-14) matches.
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/Thermadiag/micromalloc>
  - <https://github.com/Thermadiag/micromalloc/commits>
  - <https://raw.githubusercontent.com/Thermadiag/micromalloc/HEAD/README.md>
  - <https://raw.githubusercontent.com/Thermadiag/micromalloc/HEAD/md/benchmarks.md>
  - <https://raw.githubusercontent.com/Thermadiag/micromalloc/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Thermadiag/micromalloc/HEAD/README.md>
  - <https://raw.githubusercontent.com/Thermadiag/micromalloc/HEAD/md/benchmarks.md>
  - <https://raw.githubusercontent.com/Thermadiag/micromalloc/HEAD/md/examples.md>
  - <https://raw.githubusercontent.com/Thermadiag/micromalloc/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Thermadiag/micromalloc/HEAD/benchs/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Thermadiag/micromalloc/HEAD/benchs/alloc_dealloc_same_thread.cpp>
  - <https://raw.githubusercontent.com/Thermadiag/micromalloc/HEAD/micro/testing.hpp>
  - <https://raw.githubusercontent.com/Thermadiag/micromalloc/HEAD/micro/os_page.hpp>
  - <https://raw.githubusercontent.com/Thermadiag/micromalloc/HEAD/micro/micro.h>
  - <https://raw.githubusercontent.com/Thermadiag/micromalloc/HEAD/micro/internal/os_page.cpp>
  - <https://raw.githubusercontent.com/Thermadiag/micromalloc/HEAD/md/images/same_thread.svg>
  - <https://github.com/Thermadiag/micromalloc/issues?q=is%3Aissue>
  - <https://github.com/Thermadiag/micromalloc/tree/main/benchs>
  - <https://github.com/Thermadiag/micromalloc/tree/main/micro>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/thermadiag/micromalloc`) · [data/wave11/enrich/raw/github_com_thermadiag_micromalloc.json](../../../data/wave11/enrich/raw/github_com_thermadiag_micromalloc.json) (enrichment confidence 0.75)

</details>
