# arena-allocator (ShortAlloc)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Allocators](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟡 stale

> Single-file bump-pointer arena allocator with an STL-compatible wrapper; beats glibc malloc via std::vector, especially above the mmap threshold.

| | |
|---|---|
| **Beats** | operator new/delete (GNU/glibc malloc via std::vector's default std::allocator) |
| **Claimed result** | Stack/arena allocator 2.2x-4.4x faster for objects up to 512B, and 93x-230x faster for 1KB-8KB objects (crossing glibc's mmap threshold) |
| **Workload** | std::vector&lt;TestClass&gt;::emplace_back of 100 objects of sizes 8B-8KB, using a stack-backed bump-pointer Arena + ShortAlloc STL allocator vs the default heap allocator, measured on QuickBench (AWS-hosted). |
| **Metric** | latency |
| **Hardware** | QuickBench-hosted AWS machine pool: the QuickBench result context shows 1 CPU at 2300 MHz, 32KB L1d, 256KB L2, 45MB L3; CPU model unstated. The README includes QuickBench's disclaimer that absolute timings are unreliable. |
| **Compiler and flags** | clang 17.0, -O3, -std=c++20, libstdc++ ('gnu' lib), per the QuickBench options of the linked benchmarks (not stated in the README) |
| **Adoption** | 9 stars; featured in a Hacker News 'Show HN' post |
| **Last commit** | 2025-03-13 |
| **Links** | [repository](https://github.com/shantanu/arena-allocator) · [benchmark](https://github.com/shantanu/arena-allocator#%EF%B8%8F-performance-benchmarks) |

## Verdict

On QuickBench (clang 17.0, -O3, -std=c++20, libstdc++, single CPU core from a shared AWS pool), std::vector&lt;TestClass, ShortAlloc&gt; doing 100 emplace_back calls was 2.2x-4.4x faster than std::vector's default allocator (glibc malloc) for 8B-512B objects, and 93x-230x faster for 1KB-8KB objects — the latter driven by the default allocator crossing glibc's mmap threshold during vector reallocation, not a general per-allocation speed advantage at that size.

## Use it when

- Short-lived, single-threaded scopes with a known upper bound on total allocation, e.g. a function-local std::vector that shouldn't touch the heap
- Many same-sized emplace_back/reallocation cycles where the arena can be sized to the container's peak footprint
- LIFO-order allocate/deallocate patterns, since deallocate() only reclaims the block at the top of the arena
- Containers whose elements grow into the 1KB-8KB+ range, where you want to sidestep glibc's mmap-threshold latency cliff
- Reference/teaching use: a \~180-line file showing a bump allocator plus STL-allocator plumbing

## Skip it when

- Multi-threaded code — no locking or atomics in Arena or ShortAlloc; concurrent use is undefined behavior
- Workloads needing out-of-order or random-order frees, since only the most recent allocation can be reclaimed
- Long-running or size-unbounded containers — the arena is a fixed std::array&lt;N&gt; and silently falls back to global operator new once exhausted, with no bookkeeping to route the matching free back correctly
- Anywhere licensing matters — the repo ships no LICENSE file, so reuse terms are undefined
- Copy-pasting the repo as-is into production — the committed source has active std::cout debug prints in allocate()/deallocate() that the benchmarked version did not have

## How it is fast

Allocation is a pointer bump plus an alignment round-up (no free-list search, no locking, no syscalls) as long as the arena has room, so it stays in cache and skips heap-manager bookkeeping entirely. The largest gains (93x-230x) show up once std::vector's reallocations grow past glibc's mmap threshold (\~128KB total), where the default allocator pays for an mmap syscall and first-touch page faults that the arena avoids by staying on the stack-backed buffer.

## Compared with alternatives

Pick this over general-purpose allocator replacements in the catalog (Hoard, SuperMalloc, NUMAlloc, scalloc) when you want a tiny, dependency-free, single-file bump allocator for a bounded, single-threaded, LIFO-style scope rather than a global malloc replacement for multi-threaded programs. Against the other same-domain arena-allocator (yaroslavaristov), prefer that one for broader, harder benchmark evidence (AMD EPYC and Apple M1, direct malloc/free comparison); prefer this one specifically for the ready-made STL-compatible ShortAlloc wrapper usable as std::vector&lt;T, Alloc&gt;.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (only &lt;iostream&gt;, &lt;vector&gt;, &lt;array&gt;, &lt;memory&gt;, &lt;cstdint&gt; from the STL) |
| **Minimum toolchain** | C++17 (uses std::byte, std::array); benchmarked with clang 17.0, -std=c++20, libstdc++ |
| **Platforms** | any (portable standard C++, no architecture-specific code) |
| **Thread safety** | not documented; source has no mutex/atomics — Arena and ShortAlloc are not thread-safe |
| **Drop-in for the baseline** | partial — explain: ShortAlloc is STL-allocator-compatible so it plugs into std::vector&lt;T, ShortAlloc&lt;T,N&gt;&gt;, but you must declare an Arena&lt;N&gt;, construct the container with a reference to it, and keep the arena alive; it does not replace global operator new/delete. |

## Gotchas

- The GitHub source (arena-benchmark.cpp) has its std::cout diagnostic lines active inside allocate()/deallocate(); the QuickBench snippet that produced the published numbers has those lines commented out, so running the repo file as-is will not reproduce the benchmark
- deallocate() silently no-ops (leaks the block) if you free anything that isn't both in-buffer and the most-recently-allocated block — no error or assertion is raised
- Once the arena is exhausted, allocate() falls back to ::operator new, but deallocate() has no bookkeeping to route those heap-backed blocks to ::operator delete except via the top-of-stack pointer check — mixed arena/heap blocks can be freed incorrectly
- The free operator== / operator!= for ShortAlloc reference a nonexistent `rhs.arena` member (the field is actually private `d_arena`) and access it without a friend declaration — this code would fail to compile if a container ever invoked allocator comparison

## Caveats and trade-offs

The README does not state compiler or flags, but the QuickBench runs used clang 17.0 -O3 with libstdc++. The CPU model is unknown and QuickBench's shared AWS pool makes absolute durations unreliable, so it stays at Tier C. The 93x-230x ratios for 1KB-8KB objects coincide with crossing glibc's mmap threshold (as the README explains), so they are not a general allocator speed claim. The arena cannot free non-top allocations. There is no LICENSE file, so usability is 'reference' only.

Bump allocator: cannot free individual objects out of order, only the whole arena at once (or most-recent-first); backed by a fixed-size std::array, so capacity is bounded by the configured arena size; not thread-safe.

## Maintenance

Stale (last commit 2025-03-13, 9 GitHub stars, no open issues, no LICENSE file) and marked 'reference' usability — best read as a worked example of a bump allocator plus STL-allocator wiring rather than adopted as-is; the repo currently ships the un-optimized, debug-print-enabled source, so strip those lines before reusing it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party QuickBench numbers compare against std::vector with the default allocator (glibc malloc). The code is public (arena-benchmark.cpp and the QuickBench links), and the QuickBench options show clang 17.0 -O3 with libstdc++. The CPU model is unknown (shared AWS pool), so it cannot be A.
- **Verifier notes:** All README table numbers match (2.2x-4.4x up to 512B; 93x, 150x, 190x, 230x for 1K-8K). Compiler and flags were retrieved from the QuickBench API (quick-bench.com/quick/&lt;id&gt;). The Show HN post exists (2025-03-13, 2 points).
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/shantanu/arena-allocator>
  - <https://github.com/shantanu/arena-allocator#%EF%B8%8F-performance-benchmarks>
  - <https://quick-bench.com/q/hnEZC5GC-9UoXK6aMM5VZ-66CKY>
  - <https://quick-bench.com/quick/hnEZC5GC-9UoXK6aMM5VZ-66CKY>
  - <https://quick-bench.com/quick/FSVMOb4MG32-acROZFLstV0xmbc>
  - <https://quick-bench.com/quick/5BRGLEjOHhZYnX6Wbojy8xDAb0g>
  - <https://hn.algolia.com/api/v1/search?query=github.com/shantanu/arena-allocator&restrictSearchableAttributes=url>
- **Sources the enricher read:**
  - <https://github.com/shantanu/arena-allocator>
  - <https://github.com/shantanu/arena-allocator#%EF%B8%8F-performance-benchmarks>
  - <https://github.com/shantanu/arena-allocator/blob/main/arena-benchmark.cpp>
  - <https://github.com/shantanu/arena-allocator/issues>
  - <https://quick-bench.com/quick/hnEZC5GC-9UoXK6aMM5VZ-66CKY>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/shantanu/arena-allocator`) · [data/wave1/enrich/raw/github_com_shantanu_arena_allocator.json](../../../data/wave1/enrich/raw/github_com_shantanu_arena_allocator.json) (enrichment confidence 0.4)

</details>
