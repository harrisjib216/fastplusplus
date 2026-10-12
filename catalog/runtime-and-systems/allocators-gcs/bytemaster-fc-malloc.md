# fc_malloc

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `C++` · `no license` · 🔴 abandoned

> 2013 proof-of-concept thread-caching allocator with a dedicated free-recycling thread; README claims about 2x faster than glibc and jemalloc.

| | |
|---|---|
| **Beats** | glibc malloc and jemalloc |
| **Claimed result** | Single thread 2.6s vs glibc 5.8s and jemalloc 4.5s; 10 threads 6.8s vs glibc 18.2s and jemalloc 13.6s. A second table vs jemalloc only shows 4.8s vs 9.7s at 1 thread up to 12.9s vs 27.9s at 10 threads, with fc_malloc using about 14% more RAM (e.g. 308 MB vs 270 MB at 10 threads). |
| **Workload** | Random producer-consumer test: one array per thread of 500K slots, random 128-byte allocs and frees, single thread and 10 threads. |
| **Metric** | throughput |
| **Adoption** | 189 stars |
| **Last commit** | 2013-05-07 |
| **Links** | [repository](https://github.com/bytemaster/fc_malloc) · [benchmark](https://github.com/bytemaster/fc_malloc/blob/master/README.md) |

## Verdict

First-party wall times from one random producer-consumer run on unstated hardware, compiler and jemalloc version: 2.6 s vs 5.8 s glibc and 4.5 s jemalloc on 1 thread, and 6.8 s vs 18.2 s and 13.6 s on 10 threads; a second table shows 4.8-12.9 s vs jemalloc's 9.7-27.9 s at 1-10 threads with about 14% more RAM. The benchmarked allocator (malloc2.cpp at 39e4d67) serves one fixed 60-byte size, uses a spinning extra thread, and its unbounded-overwrite rings can drop or double-issue blocks under exactly this cross-thread free load, so the numbers do not describe a general-purpose, correct malloc.

## Use it when

- As reading material on Disruptor-style allocator design: single-producer free queues per thread plus a dedicated recycler thread.
- To reproduce a 2013-era producer-consumer microbenchmark with fixed-size blocks, cross-thread frees and a spare core for the recycler.
- As a starting point for a fixed-size-class pool inside your own code, after you rewrite the synchronization with proper atomics and backpressure.

## Skip it when

- Anything in production: no license (issue #1 closed without one), abandoned since 2013-05-07, and the last commit message says the fixed_pool design 'still has multi-threaded' bugs.
- Mixed allocation sizes: in the benchmarked malloc2.cpp, get_bin() ignores the size and returns the same bin for every request, so a recycled small block can be handed out for a larger request (heap overflow).
- Programs that free in bursts faster than the single recycler thread can drain them: the per-thread garbage ring and the shared recycle ring have no backpressure, so the writer can lap the reader and pointers get dropped (leak) or recycled twice (double handout).
- Machines without a spare core: the recycler thread busy-spins (its usleep is commented out) even when idle.
- Programs that need memory returned to the OS: pages are never unmapped.

## How it is fast

It borrows the LMAX Disruptor single-writer idea. Each thread bump-allocates from its own 8 MB mmap page and pushes freed pointers into a private, non-atomic ring buffer (16K slots). One garbage-collector thread busy-polls every thread's ring and moves the pointers into a shared 1M-slot recycle ring. Allocating threads then claim 16 recycled blocks at a time with a single relaxed fetch_add, so the fast path is a thread-local cache pop with no locks or CAS.

## Compared with alternatives

Effectively never for use: IsoAlloc, Spaces or micromalloc are licensed, maintained, size-class-correct malloc replacements with real benchmarks. Read fc_malloc only for the Disruptor-style recycler-thread idea, which none of the catalogued siblings use.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for malloc2.cpp (its own disruptor.hpp, mmap_alloc.hpp, fast_rand.cpp); HEAD CMakeLists links the benchmark against jemalloc |
| **Minimum toolchain** | C++11 (-std=c++0x), GCC/Clang builtins (__builtin_clzll, __thread) |
| **Platforms** | Linux and macOS (POSIX mmap); x86 rdtsc in fast_rand.cpp; Windows not supported despite CMake defines |
| **Thread safety** | Claimed lock-free and thread-safe, but cross-thread handoff uses plain or volatile int64 fields with no acquire/release ordering (data races under the C++ memory model), and the rings can overflow (see when_not_to_use) |
| **Drop-in for the baseline** | no |

## Gotchas

- The README says 128-byte allocations, but the benchmark at the commit that added the tables (39e4d67, malloc2.cpp) allocates 60 bytes (rounded to 64 plus a 16-byte header) and never touches the memory; HEAD bench.cpp instead allocates 10000 bytes into 32K-slot arrays with memset, a configuration that matches neither table.
- free2() publishes its ring position only after more than 10 frees, so up to 10 frees per thread stay invisible to the recycler.
- mmap_alloc checks `if(!limit)` instead of MAP_FAILED, so a failed mmap returns (char\*)-1; on Linux it opens /dev/zero for every page and never closes the fd. The HEAD fixed_pool maps at address hints that encode the size class ((ItemSize&lt;&lt;32) + pos\*PageSize) and only asserts that the hint was honoured; on macOS it passes MAP_FIXED to that address, which can clobber existing mappings.
- Open issues #3-#5 (2020) report double allocation after block merging and duplicate ring-buffer claims in malloc3.cpp; none were answered.

## Known shortcomings

- The benchmarked code is malloc2.cpp at commit 39e4d67, not fc_malloc. Its get_bin() ignores size so all sizes share one bin (heap overflow on mixed sizes); the garbage ring (16K) and recycle ring (1M) have no backpressure, so blocks can be dropped or handed out twice under the 10-thread cross-free load; the recycler thread busy-spins on an extra core; the bench used 60 B, not the README's 128 B. HEAD fc_malloc.cpp/.h do not compile.

## Caveats and trade-offs

Author calls these initial benchmarks; the two README tables disagree on single-thread times (2.6s vs 4.8s) with no explanation. Compiler, flags, CPU and jemalloc version not stated; 128-byte fixed-size allocations only; uses a dedicated background thread for frees. No license file in the repo, so code cannot be copied. Last commit 2013-05-07. [retier] Benchmarked code is malloc2.cpp at 39e4d67, not fc_malloc; get_bin() ignores size (heap overflow on mixed sizes); garbage and recycle rings have no backpressure so blocks can be dropped or handed out twice under 10-thread cross-free load; recycler busy-spins on an extra core; bench used 60 B, not 128 B; HEAD fc_malloc.cpp/.h do not compile. Two README tables disagree on single-thread time (2.6 s vs 4.8 s). No license file.

Dedicated thread moves freed blocks to the shared pool, so it costs a core; each thread maps 4 MB chunks, so memory use is high; 128-byte test only.

## Maintenance

Abandoned since 2013-05-07 with no license (all rights reserved) and HEAD sources that do not compile as a library; reference only.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now D.
- **Tier reason:** README table gives first-party wall times vs glibc and jemalloc (bench.cpp in repo), but no compiler, flags, CPU or jemalloc version, so C.
- **Retiered** C to D: Downgraded from C. The enricher found the numbers measure a different file (malloc2.cpp at 39e4d67, not fc_malloc) with correctness bugs behind them: get_bin() ignores size so all sizes share one bin, and the rings drop or double-hand-out blocks under the 10-thread cross-free load; the bench used 60 B rather than the README's 128 B and the HEAD sources do not compile. Kept and documented per the keep-and-document rule.
- **Verifier notes:** No LICENSE/COPYING file found (raw fetches 404, file list has none). Not a fork per page view; 189 stars. gh CLI blocked, so archived flag not checked via API.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/bytemaster/fc_malloc/blob/master/README.md>
  - <https://github.com/bytemaster/fc_malloc>
  - <https://github.com/bytemaster/fc_malloc/commits/master>
- **Sources the enricher read:**
  - <https://github.com/bytemaster/fc_malloc>
  - <https://github.com/bytemaster/fc_malloc/commits/master>
  - <https://github.com/bytemaster/fc_malloc/commit/39e4d67>
  - <https://github.com/bytemaster/fc_malloc/issues?q=is%3Aissue>
  - <https://github.com/bytemaster/fc_malloc/issues/1>
  - <https://github.com/bytemaster/fc_malloc/issues/5>
  - <https://raw.githubusercontent.com/bytemaster/fc_malloc/HEAD/README.md>
  - <https://raw.githubusercontent.com/bytemaster/fc_malloc/HEAD/bench.cpp>
  - <https://raw.githubusercontent.com/bytemaster/fc_malloc/HEAD/fc_malloc.cpp>
  - <https://raw.githubusercontent.com/bytemaster/fc_malloc/HEAD/fc_malloc.h>
  - <https://raw.githubusercontent.com/bytemaster/fc_malloc/HEAD/fixed_pool.hpp>
  - <https://raw.githubusercontent.com/bytemaster/fc_malloc/HEAD/fc_heap.hpp>
  - <https://raw.githubusercontent.com/bytemaster/fc_malloc/HEAD/mmap_alloc.hpp>
  - <https://raw.githubusercontent.com/bytemaster/fc_malloc/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bytemaster/fc_malloc/HEAD/ideas.txt>
  - <https://raw.githubusercontent.com/bytemaster/fc_malloc/39e4d672aaf38207105321859445beab30255a4e/malloc2.cpp>
  - <https://raw.githubusercontent.com/bytemaster/fc_malloc/39e4d672aaf38207105321859445beab30255a4e/disruptor.hpp>
  - <https://raw.githubusercontent.com/bytemaster/fc_malloc/39e4d672aaf38207105321859445beab30255a4e/fast_rand.cpp>
  - <https://raw.githubusercontent.com/bytemaster/fc_malloc/39e4d672aaf38207105321859445beab30255a4e/README.md>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/bytemaster/fc_malloc`) · [data/wave11/enrich/raw/github_com_bytemaster_fc_malloc.json](../../../data/wave11/enrich/raw/github_com_bytemaster_fc_malloc.json) (enrichment confidence 0.8)

</details>
