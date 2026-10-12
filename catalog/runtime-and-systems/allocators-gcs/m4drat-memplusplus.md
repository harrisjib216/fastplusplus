# mem++ (memplusplus)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟡 stale

> Experimental single-threaded C++ arena allocator with GC smart pointers and heap compaction; beats jemalloc in its own charts, not glibc malloc.

| | |
|---|---|
| **Beats** | jemalloc, mimalloc, rpmalloc, ptmalloc2/3 (glibc malloc), gcpp |
| **Claimed result** | Charts only (values read off the plots, approximate): allocating 4096 random-size objects mem++ about 590 us vs jemalloc about 1160 us and mimalloc about 960 us, but slower than ptmalloc2 (glibc 2.31) about 220 us and rpmalloc about 150-200 us. Complex 1M-op benchmark: mem++ about 1010 ms vs jemalloc about 2000 ms and rpmalloc about 1340 ms, but slower than mimalloc about 670 ms and ptmalloc2 about 700 ms. README: heap compaction improves linked-list iteration 4-8x versus its own randomized layout. |
| **Workload** | Bump-style allocator with GC and heap compaction; benchmarks of 4096 random-size allocations/deallocations, 1M/2M mixed ops, and linked-list iteration before and after compaction. |
| **Metric** | throughput |
| **Adoption** | 55 stars |
| **Last commit** | 2023-11-22 |
| **Links** | [repository](https://github.com/m4drat/memplusplus) · [benchmark](https://github.com/m4drat/memplusplus-benchmarks) |

## Verdict

First-party Google Benchmark runs (clang-15, Release, CPU unknown, results only as box-plot images): 4096 random-size allocations take about 590 us for mem++ vs about 1160 us for jemalloc and 960 us for mimalloc, but about 220 us for glibc 2.31 malloc and 150-200 us for rpmalloc; the 1M-op mixed benchmark is about 1010 ms vs jemalloc about 2000 ms and rpmalloc about 1340 ms, but slower than mimalloc (about 670 ms) and glibc malloc (about 700 ms). The 4-8x figure compares iterating a linked list after compaction with the same list randomized in mem++'s own heap.

## Use it when

- Research or teaching on compacting GC and locality-improving heap layout in C++.
- Single-threaded programs built around pointer-chasing structures (linked lists) whose nodes end up scattered in memory, where a manual compaction pass can pay off.
- Experiments comparing bump/treap allocators against jemalloc, which its own complex benchmark shows about 2x slower than mem++ (chart-read values).

## Skip it when

- As a faster general allocator: in its own charts glibc malloc (ptmalloc2, glibc 2.31) and rpmalloc beat it on the 4096-allocation test, and mimalloc and glibc malloc beat it on the 1M-op complex test.
- Any multithreaded program: the README says it supports only single-threaded applications, and multithreading is an open low-priority issue (#21).
- Production code: the README says it is not recommended for production, the API is unstable (0.3.5), and the last commit was 2023-11-22.
- Code that keeps references or raw pointers into GC-managed objects across CollectGarbage(), since compaction invalidates them.
- Windows, or projects needing a clear license: Windows support is an open issue (#27) and the repo has no LICENSE file.

## How it is fast

Allocation is a bump of the arena's top chunk when it has room; otherwise it does a best-fit lookup in a per-arena treap of freed chunks (ChunkTreap, GetFirstGreaterOrEqualToChunk) and splits the result. Free coalesces with neighbouring chunks and the top chunk, ptmalloc-style, using 16-byte headers and 32-byte minimum chunks. During GC it splits the object graph into connected components, places each component contiguously in one arena, and for singly-linked-list-shaped components lays nodes out in traversal order, which is where the 4-8x iteration speedup over a randomized list comes from.

## Compared with alternatives

Pick mem++ over SGCL only if you want compaction and locality-driven relocation rather than a concurrent tracing collector; for plain allocation speed, fast-alloc pools or IsoAlloc beat glibc malloc where mem++ does not.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none at runtime beyond libc/mmap; googletest and google benchmark only for tests and benchmarks |
| **Minimum toolchain** | C++20 (CMAKE_CXX_STANDARD 20), CMake 3.13+, g++ or clang++ |
| **Platforms** | Unix-like systems with mmap; Windows not supported |
| **Thread safety** | Not thread-safe; single-threaded only per README |
| **Drop-in for the baseline** | partial — malloc/free-like mpp::Allocate/Deallocate exist (deprecated) but nothing replaces malloc or operator new globally; the GC API is a different, smart-pointer interface |

## Gotchas

- The allocator benchmarks call the deprecated raw mpp::Allocate/Deallocate, not the GC path, so they do not measure MakeShared or CollectGarbage cost.
- Allocate and Deallocate scan the arena list linearly (GetSuitableChunk loops over every arena; Deallocate finds the owning arena by range check), so cost grows with the number of 32 MB arenas.
- The 'ptmalloc2' column in the benchmarks is the build machine's system malloc (glibc 2.31); the benchmark build uses clang-15 Release with Google Benchmark, 5 repetitions, CPU not stated.
- Garbage collection is manual only; automatic collection is an open issue (#45). Compaction moves objects and invalidates raw pointers and references.

## Known shortcomings

- Not faster than glibc malloc: its own charts show ptmalloc2 ahead on both timing benchmarks; it beats only jemalloc and rpmalloc. No LICENSE file.
- Bench build is clang-15 Release with Google Benchmark, 5 repetitions, CPU unknown. The alloc benches call the deprecated raw mpp::Allocate/Deallocate, not the GC path; the 'ptmalloc2' column is system glibc 2.31 malloc. Allocate/Deallocate scan the arena list linearly. Still no LICENSE (404), stale since 2023-11-22, single-thread only.

## Caveats and trade-offs

Slower than glibc malloc (ptmalloc2) in both the allocation and the complex benchmark shown; wins only against jemalloc and rpmalloc in some charts. No LICENSE file in the repo (license unknown, reference only). Headline 4-8x is against its own uncompacted layout. Single-threaded only; README says not for production; hardware and compiler flags not stated; numbers only as images.

Single-threaded only; Unix-like systems with g++ or clang++; API unstable (0.3.5) and author says not for production.

## Maintenance

Stale since 2023-11-22 with 22 open issues, no LICENSE file and an author warning against production use, so it is reference material only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmark code (memplusplus-benchmarks: benchmark_alloc.cpp, benchmark_complex.cpp, etc.) with results only as box-plot images; no compiler flags or CPU stated, so C.
- **Verifier notes:** Kept as C; the orchestrator may want a not-faster-than-glibc shortcoming, since ptmalloc2 beats it on both charted timing benchmarks.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party charts; code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/m4drat/memplusplus>
  - <https://github.com/m4drat/memplusplus/commits>
  - <https://raw.githubusercontent.com/m4drat/memplusplus/HEAD/README.md>
  - <https://raw.githubusercontent.com/m4drat/memplusplus-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/m4drat/memplusplus-benchmarks/HEAD/bench-results/graphs/bench-results-without-ptmalloc3/allocate-4096-time.png>
  - <https://raw.githubusercontent.com/m4drat/memplusplus-benchmarks/HEAD/bench-results/graphs/bench-results-without-ptmalloc3/complex_1m-time.png>
- **Sources the enricher read:**
  - <https://github.com/m4drat/memplusplus>
  - <https://github.com/m4drat/memplusplus/issues>
  - <https://github.com/m4drat/memplusplus/tree/master/libmemplusplus/src>
  - <https://raw.githubusercontent.com/m4drat/memplusplus/HEAD/README.md>
  - <https://raw.githubusercontent.com/m4drat/memplusplus/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/m4drat/memplusplus/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/m4drat/memplusplus/HEAD/libmemplusplus/CMakeLists.txt>
  - <https://raw.githubusercontent.com/m4drat/memplusplus/HEAD/libmemplusplus/src/memory_manager.cpp>
  - <https://raw.githubusercontent.com/m4drat/memplusplus/HEAD/libmemplusplus/src/arena.cpp>
  - <https://raw.githubusercontent.com/m4drat/memplusplus/HEAD/libmemplusplus/src/gc.cpp>
  - <https://github.com/m4drat/memplusplus-benchmarks>
  - <https://github.com/m4drat/memplusplus-benchmarks/tree/master/benchmarks/mempp>
  - <https://raw.githubusercontent.com/m4drat/memplusplus-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/m4drat/memplusplus-benchmarks/HEAD/compile_all_and_run.sh>
  - <https://raw.githubusercontent.com/m4drat/memplusplus-benchmarks/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/m4drat/memplusplus-benchmarks/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/m4drat/memplusplus-benchmarks/HEAD/benchmarks/benchmark_alloc.cpp>
  - <https://raw.githubusercontent.com/m4drat/memplusplus-benchmarks/HEAD/benchmarks/benchmark_complex.cpp>
  - <https://raw.githubusercontent.com/m4drat/memplusplus-benchmarks/HEAD/benchmarks/allocator_api_override.h>
  - <https://raw.githubusercontent.com/m4drat/memplusplus-benchmarks/HEAD/benchmarks/mempp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/m4drat/memplusplus-benchmarks/HEAD/benchmarks/mempp/allocator_api_override.cpp>
  - <https://raw.githubusercontent.com/m4drat/memplusplus-benchmarks/HEAD/benchmarks/mempp/benchmark_memory_access.cpp>
  - <https://raw.githubusercontent.com/m4drat/memplusplus-benchmarks/HEAD/benchmarks/ptmalloc2/allocator_api_override.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/m4drat/memplusplus`) · [data/wave11/enrich/raw/github_com_m4drat_memplusplus.json](../../../data/wave11/enrich/raw/github_com_m4drat_memplusplus.json) (enrichment confidence 0.65)

</details>
