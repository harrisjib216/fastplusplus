# custom-memory-allocator (atul-singh-as)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Educational C++20 fixed-size pool and first-fit free-list allocators; the pool beats macOS malloc/free on bulk 16 B allocation.

| | |
|---|---|
| **Beats** | malloc/free (macOS system allocator) |
| **Claimed result** | README sample output, 16 B x 200000: bulk 5.68 ms malloc/free vs 0.89 ms Pool (about 6.4x, derived from page data) vs 8.06 ms FreeList (slower); churn 0.00 ms malloc vs 0.44 ms Pool vs 1.74 ms FreeList. README text: Pool 'often 5-15x faster than malloc'. |
| **Workload** | Fixed-size block allocation of 200000 blocks (16 B and larger) in bulk and churn patterns, plus a mixed random-size workload, pool and free-list allocators against malloc/free. |
| **Metric** | throughput |
| **Compiler and flags** | clang++ -std=c++20 -O2 (Release, NDEBUG) per README build instructions |
| **Adoption** | 1 star |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/atul-singh-as/custom-memory-allocator) · [benchmark](https://github.com/atul-singh-as/custom-memory-allocator/blob/main/README.md) |

## Verdict

The README's sample output, measured on an unspecified macOS machine (Apple clang, -O2, Release), shows the pool completing 200000 16-byte allocations and frees in bulk in 0.89 ms against 5.68 ms for macOS malloc/free (about 6.4x, derived from page data). The free-list allocator was slower (8.06 ms), and the churn column is not usable because malloc reads 0.00 ms. The README's '5-15x' and 'FreeList clearly faster on churn' claims are not supported by its own sample.

## Use it when

- Single-threaded code that allocates many same-sized objects (nodes, particles, entities) and knows an upper bound on their count up front
- Frame-style workloads that can drop everything at once with PoolAllocator::Reset()
- As a small, readable reference for how slab and free-list allocators work before adopting a production allocator
- Vendoring about 300 lines of MIT code when a full allocator dependency is not wanted

## Skip it when

- Any multithreaded allocation: neither allocator is thread-safe and there are no thread caches
- As a general malloc replacement: FreeListAllocator was slower than macOS malloc in its own sample (8.06 ms vs 5.68 ms bulk at 16 B) and does a linear first-fit search
- When the object count is unbounded: the pool returns nullptr once exhausted and never grows
- Security-sensitive code: no guard pages, no poisoning, no ownership check in PoolAllocator::Free
- Production use in general: one commit, 1 star, and the author calls it an educational/portfolio implementation

## How it is fast

The pool is a classic intrusive free list (a slab allocator): each free slot's first 8 bytes point to the next free slot, so Allocate and Free are a single pointer pop or push with no size classes, locking or metadata lookup. The free-list allocator is textbook first-fit (or best-fit) over a doubly linked free list, with boundary headers holding physical prev/next links for coalescing. It walks the list linearly, so it is not a fast path.

## Compared with alternatives

Pick it only for learning, or to vendor a minimal single-threaded pool; NotKeira/fast-alloc gives a similar pool with Linux numbers on a named CPU, and Bloodmoon001/memory-allocator and privateMwb/ArenaAllocator cover the same educational niche. For anything general-purpose, use the catalogued malloc replacements (mimalloc-class allocators, IsoAlloc, Mesh).

## Integration

| | |
|---|---|
| **Form** | source-drop (CMake static lib target 'allocator') |
| **Dependencies** | none |
| **Minimum toolchain** | C++20 (CMake 3.16+); uses aligned ::operator new |
| **Platforms** | any (build instructions are macOS-only; no platform-specific code seen) |
| **Thread safety** | Not thread-safe; the README says to wrap it in a mutex |
| **Drop-in for the baseline** | partial: a separate class API (Allocate/Free on an allocator object), no malloc/operator new override and no std::allocator adapter |

## Gotchas

- The README says both allocators assert on double free, but only FreeListAllocator::Free has that assert; PoolAllocator::Free has no double-free or ownership check and silently corrupts the free list.
- PoolAllocator rounds blockSize up only to sizeof(void\*), not to the requested alignment, so a block size that is not a multiple of the alignment (e.g. 24 B with 16 B alignment) returns misaligned slots after the first one. The benchmark sizes are all multiples of 16, so they are unaffected.
- Harness bias: the pool's constructor, outside the timed region, threads the free list through every slot and so pre-faults all pages, while the malloc bulk timing includes first-touch page faults. The churn column shows malloc at 0.00 ms, which is consistent with the compiler eliding the unused malloc/free pair, so churn comparisons are meaningless.
- blockSize \* blockCount is not checked for overflow, and FreeListAllocator stores an 8-byte offset before every user pointer plus a 48-byte header, so per-allocation overhead is large for 16 B objects.

## Known shortcomings

- Harness bias: the Pool constructor prefaults its pages outside the timed loop while malloc pays first-touch faults inside it, and the 0.00 ms malloc churn is likely elided. README says both allocators assert on double free but only FreeListAllocator does; PoolAllocator::Free checks nothing. Pool also misaligns slots when blockSize is not a multiple of the alignment (bench sizes are multiples of 16, so unaffected).

## Caveats and trade-offs

Only the Pool bulk row shows a win. The churn column shows malloc at 0.00 ms, most likely because clang elides the unused malloc/free pair in BenchMalloc's churn loop, so churn ratios are meaningless, and the README's claim that FreeList is 'clearly faster on churn' contradicts its own sample (1.74 ms vs 0.00 ms). The sample prints 2 decimals while main.cpp uses setprecision(3), so it may not be verbatim output. macOS malloc baseline, CPU unspecified; single initial commit; not thread-safe; educational project per the author.

Not thread-safe; fixed-size pool; arena is pre-reserved; no guard pages or thread caches; the author calls it an educational/portfolio implementation.

## Maintenance

One initial commit (2026-09-23) on a 1-star MIT repo labelled educational by its author; small enough to read and vendor, but not hardened.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README sample output compares Pool and FreeList against malloc/free with benchmark code in src/main.cpp and clang++ -O2 flags, but no CPU model is given ("Apple Silicon / Intel timings will differ"), so C.
- **Verifier notes:** Kept at C; Pool bulk win is the only supported claim, FreeList is not shown faster. MIT, 1 star, last commit 2026-09-23 confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/atul-singh-as/custom-memory-allocator/HEAD/README.md>
  - <https://raw.githubusercontent.com/atul-singh-as/custom-memory-allocator/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/atul-singh-as/custom-memory-allocator/HEAD/src/main.cpp>
  - <https://github.com/atul-singh-as/custom-memory-allocator>
  - <https://github.com/atul-singh-as/custom-memory-allocator/commits>
- **Sources the enricher read:**
  - <https://github.com/atul-singh-as/custom-memory-allocator>
  - <https://raw.githubusercontent.com/atul-singh-as/custom-memory-allocator/HEAD/README.md>
  - <https://raw.githubusercontent.com/atul-singh-as/custom-memory-allocator/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/atul-singh-as/custom-memory-allocator/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/atul-singh-as/custom-memory-allocator/HEAD/include/PoolAllocator.hpp>
  - <https://raw.githubusercontent.com/atul-singh-as/custom-memory-allocator/HEAD/src/PoolAllocator.cpp>
  - <https://raw.githubusercontent.com/atul-singh-as/custom-memory-allocator/HEAD/include/FreeListAllocator.hpp>
  - <https://raw.githubusercontent.com/atul-singh-as/custom-memory-allocator/HEAD/src/FreeListAllocator.cpp>
  - <https://raw.githubusercontent.com/atul-singh-as/custom-memory-allocator/HEAD/tests/test_allocator.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/atul-singh-as/custom-memory-allocator`) · [data/wave11/enrich/raw/github_com_atul_singh_as_custom_memory_allocator.json](../../../data/wave11/enrich/raw/github_com_atul_singh_as_custom_memory_allocator.json) (enrichment confidence 0.6)

</details>
