# mtrebi/memory-allocators (free list allocator; linear, stack and pool allocators)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🟢 active

> Teaching-grade C++ linear, stack, pool and first-fit free-list allocators; README claims the free list runs about 3x faster than malloc.

| | |
|---|---|
| **Beats** | malloc/free (libc; the benchmark's CAllocator wraps malloc and free) |
| **Claimed result** | README 'Time complexity': 'Malloc is without doubt the worst allocator'; the free list allocator 'is A much better choice than malloc as a general purpose allocator ... It's about three times better than malloc'; linear, stack and pool are faster still but impose restrictions. Exact figures exist only in two chart images (block size 4096, up to about 1M operations; values read off the charts, approximate): with Init() in the timed region malloc about 1500 ms, FREE LIST SEQ about 425 ms, pool about 365 ms, stack about 60 ms, linear about 20 ms; without Init() malloc about 1500 ms, free list about 360 ms, pool about 80 ms, stack and linear about 20 ms. Malloc/free-list ratio about 3.5x with Init and about 4.2x without (derived from page data, chart readings). |
| **Workload** | Time to Init() the allocator and then perform N allocations (and frees) of fixed or randomly chosen sizes (32 to 4096 bytes, alignment 8) single-threaded, charted against number of operations up to about 1 million for block size 4096; custom linear, stack, pool and free-list allocators versus malloc. |
| **Metric** | throughput |
| **Compiler and flags** | Not stated. CMakeLists.txt sets only cxx_std_11 and the README build command passes no CMAKE_BUILD_TYPE, so a default build has no optimization flags unless the user adds them. |
| **Adoption** | 2.0k stars, 171 forks |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/mtrebi/memory-allocators) · [benchmark](https://github.com/mtrebi/memory-allocators) |

## Verdict

First-party only: README prose says the free-list allocator is 'about three times better than malloc', backed by two charts of a block-size-4096 allocate-all-then-free-in-reverse test up to about 1M operations, with no CPU, compiler, flags or libc named. Read off the charts, malloc (a CAllocator wrapper over libc malloc/free) takes about 1500 ms against about 425 ms for the free list with Init timed and about 360 ms without (roughly 3.5x and 4.2x, derived from page data), with pool, stack and linear far lower; the shipped harness runs only 10 operations, so the charts cannot be reproduced from the repo and predate the 2024-2026 stack and pool rewrites.

## Use it when

- Learning or teaching how arena, stack, pool and free-list allocators work; the README walks through each with diagrams and complexity analysis.
- As a starting point for a single-threaded per-frame arena (linear allocator reset every frame) or nested scratch scopes (stack Push/Pop), once you add your own error handling.
- Fixed-size objects allocated and freed in any order by one thread, where a pool with an intrusive free list is enough, after fixing the Reset issue noted below.
- Quick experiments comparing allocation strategies on your own workload, provided you rebuild the harness (real operation count, optimized build, finer timer).

## Skip it when

- As a general-purpose malloc replacement: the free-list allocator is O(n) per allocation and free, carries open correctness bugs, and was only measured with LIFO frees; use a production allocator instead.
- Multithreaded code: no allocator has locks, atomics or thread-local caches (issue #30 asking about concurrency is open).
- Alignment above 8 bytes or 32-bit targets: the free list rebuilds a freed block from the header address and only works when alignment padding is zero (open issue #18 shows the 32-bit failure), and the linear allocator checks offset alignment instead of address alignment.
- Code that must survive running out of memory: pool and free-list exhaustion is an assert, so NDEBUG builds overrun the pool buffer or dereference a null node; LinearAllocator::Free is assert(false).
- Code that needs standard-library integration (std::allocator, std::pmr memory_resource): none is provided.

## How it is fast

It skips the general-purpose allocator per call by taking one big block up front and giving up generality. Linear and stack allocators just advance an offset (the stack keeps rollback offsets in a std::vector, so nothing is written into user memory); the pool hands out chunks by a bump offset and recycles freed chunks through an intrusive LIFO list stored inside them, both O(1) with no headers. The free-list allocator walks an address-ordered singly linked list (first fit, O(free blocks)), writes a 16-byte size and padding header, and coalesces with neighbours on free. There are no size classes, thread caches or locks.

## Compared with alternatives

Pick this as reading material; for code you will ship, fast-alloc (pool and stack allocators with Google Benchmark numbers on a named CPU) or privateMwb ArenaAllocator (measured against std::pmr::monotonic_buffer_resource) are better arena and pool bases, and a TLSF allocator such as XenoAtom.Allocators or rlsf replaces this O(n) free list with O(1) general-purpose allocation in a fixed buffer.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond the C++ standard library (StackAllocator uses std::vector, which itself allocates from the heap) |
| **Minimum toolchain** | C++11 (CMakeLists sets cxx_std_11); CMake 3.5 to build the demo |
| **Platforms** | any hosted C++11 platform; 64-bit assumed (open 32-bit free-list corruption, issue #18) |
| **Thread safety** | none: no locks or atomics in any allocator; single-threaded use only |
| **Drop-in for the baseline** | no |

## Gotchas

- FreeListAllocator bugs: FindBest never updates smallestDiff (it returns the last fitting block) and reports the list's last node as previousNode, so remove() can leave an allocated block on the free list; use FIND_FIRST. Allocate splits off any remainder above 0 bytes even when it is smaller than the 16-byte free-node header, so the header write spills into the neighbouring block (open issue #4 since 2018). Free places the freed node at the header address rather than the block start, which is only correct when alignment padding is 0, and a block freed above every free node or into an empty list is never inserted unless it happens to merge with the last node, so memory leaks once the allocator has filled.
- PoolAllocator: Reset() zeroes the bump offset but keeps the free list, so after a Reset a chunk still on the free list is handed out again by the bump path (two live owners of one chunk); Init() mallocs a new buffer without freeing the old one, and leftover free-list nodes then point into the leaked old buffer. Allocate asserts size == chunk size and ignores alignment.
- StackAllocator::Free ignores its pointer and pops the last saved offset, so an out-of-order free silently releases the wrong allocation; Pop(marker) does not trim the per-allocation markers, so mixing Pop with Free can move the top back up; CalculatePadding returns a full alignment step for an already aligned address, so each stack allocation wastes 8 bytes (issue #25). The README build command uses -S memory-allocator while the clone directory is memory-allocators.
- Harness flaws behind the charts: Benchmark.h hard-codes OPERATIONS to 10 (a stack array of m_nOperations pointers broke MSVC, issue #6) and the timer has millisecond resolution, so the shipped program prints 0 ms; the main.cpp buffer sizes cannot hold 1M 4096-byte blocks, and the default build has no optimization flags. The charted test allocates all N blocks before freeing them in reverse, so at 1M operations malloc must grow the heap to about 4 GB of live blocks and fault in each one, the free list stays at one node (stack-like), linear and stack never write to the memory they return, and the old O(n) pool Init (since replaced) pulled the pool's page faults into Init, so the 'without Init' chart removes them for the pool only. The malloc gap is therefore likely dominated by heap growth and first-touch page faults rather than allocator logic.

## Known shortcomings

- First-party charts (malloc about 1500 ms vs free list about 360 ms) are not reproducible: the harness is hard-coded to 10 operations and the pool sizes in main.cpp are too small for 1M operations; unoptimized default build; the free list is timed only with LIFO frees; a likely page-fault asymmetry (malloc writes headers while the linear and stack allocators never touch memory); FindBest and Free bugs; the charts predate the 2024-2026 fixes.
- Enricher: the charted test allocates all N blocks (about 4 GB at 1M) before freeing, so malloc pays heap growth and page faults while the linear and stack allocators never touch memory and the old pool Init took its page faults outside the timed region: the 3x gap is likely mostly page faults. Correctness bugs: PoolAllocator::Reset keeps the free list but zeroes the offset (one chunk can go out twice), Init leaks the old buffer, FreeList FindBest returns a wrong previousNode (list corruption), remainders smaller than the 16-byte header overflow into the next block (issue #4), Free is wrong with nonzero alignment padding (#18), Stack Free ignores ptr. Shipped OPERATIONS=10 with a ms timer prints 0 ms. Downgraded C to D (Blosc and AssemblyScript precedent: baseline crippled by the harness).

## Caveats and trade-offs

First-party, tier C: no hardware, compiler, flags or libc version stated, and the repo's default build (README: plain cmake, no CMAKE_BUILD_TYPE; CMakeLists.txt sets only cxx_std_11) has no optimization flags for the custom allocators while libc malloc is prebuilt optimized. The shipped harness cannot reproduce the charts: Benchmark.h defines OPERATIONS as 10 (the `#if 0` branch for the real count is disabled) and main.cpp constructs Benchmark(OPERATIONS), so each round runs 10 operations; the allocator sizes in main.cpp also cannot hold 1M 4096-byte blocks (free list 1e8 bytes, about 24k blocks; pool 16 MiB, 4096 chunks; linear and stack 1e9 bytes, about 244k), so the charts came from an unpublished configuration. The charted free list is 'FREE LIST SEQ' with frees in reverse (LIFO) order, which keeps the free list at one node and makes it behave like a stack; random-order frees would walk the list. The linear and stack allocators never write into the returned memory (the stack keeps its markers in a std::vector), while malloc writes an in-band header into each fresh 4096-byte block, so part of the gap is likely first-touch page faults rather than allocator logic. The timed region includes Init() (one large malloc plus setup), which the README itself says distorts the curves. Correctness bugs in the allocators: FreeListAllocator::FindBest never updates smallestDiff and returns the last node as previousNode; FreeListAllocator::Free never inserts a block whose address is above every free node (it is lost); PoolAllocator::Init mallocs a new buffer each round without freeing the old one. The charts predate later fixes and rewrites ('Stack allcoator bugfix' 2024-05-23, PoolAllocator O(1) initialization 2026-04-02, stack rollback refactor 2026-04-12, empty pool free list fix 2026-09-03), so numbers are on code later changed for correctness. The three-times claim is for the free list only; the faster allocators drop general-purpose semantics. Baseline is plain libc malloc, not jemalloc, tcmalloc or mimalloc. [retier] First-party charts (malloc about 1500 ms vs free list about 360 ms) that cannot be reproduced: the harness is hard-coded to 10 operations, the pool sizes in main.cpp are too small for 1M operations, the default build is unoptimized and the free list is timed only with LIFO frees. The charted test allocates all N blocks (about 4 GB at 1M) before freeing, so malloc pays heap growth and page faults while the linear and stack allocators never touch memory and the old pool Init took its page faults outside the timed region; the 3x gap is likely mostly page faults. Correctness: PoolAllocator::Reset keeps the free list but zeroes the offset (one chunk can go out twice), Init leaks the old buffer, FreeList FindBest returns a wrong previousNode, remainders smaller than the 16-byte header overflow into the next block (issue #4), Free is wrong with nonzero alignment padding (#18), Stack Free ignores ptr. The charts predate the 2024-2026 fixes.

Educational implementations: linear (no per-item free), stack (LIFO), pool (single block size) and a first-fit linked-list free-list allocator with minimum-size and alignment constraints; no thread safety, no size classes, no red-black-tree free list (listed as future work).

## Maintenance

A 2017 tutorial repo with community fixes merged through 2026 (last commit 2026-09-21; MIT; 2.0k stars, 171 forks): good reading material and an easy source-drop, but it has no tests and allocator bugs reported since 2018 (#4, #18, #21) are still open, so do not vendor the free-list or pool allocators unchanged.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README text ('about three times better than malloc') plus two chart images (docs/images/operations_over_time.png and operations_over_time_no_init.png) comparing the custom allocators with a CAllocator that wraps libc malloc/free; benchmark code is public (src/Benchmark.cpp, src/main.cpp) but no CPU, compiler, flags or libc version is stated and the shipped harness cannot reproduce the charted 1M-operation runs, so C.
- **Retiered** C to D: Downgraded C to D: the charted 3x over malloc comes from a harness in which malloc pays heap growth and page faults for about 4 GB of live blocks while the linear and stack allocators never touch memory and the pool's page faults fell outside the timed region (Blosc and AssemblyScript precedent), and the measured allocators carry correctness bugs (pool double hand-out after Reset, free-list corruption).
- **Verifier notes:** Record is accurate; chart readings match the images (malloc about 1500 ms, free list about 360 ms without Init at 1M ops). Shortcomings to record: unoptimized default build, harness hard-coded to 10 operations and undersized pools so charts are not reproducible, LIFO-only free-list run, likely page-fault asymmetry (malloc writes headers, linear/stack never touch memory), FindBest/Free bugs, numbers predate 2024-2026 allocator fixes; baseline only glibc-style malloc.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** first-party charts (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/README.md>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/src/Benchmark.cpp>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/includes/Benchmark.h>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/src/CAllocator.cpp>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/src/FreeListAllocator.cpp>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/src/PoolAllocator.cpp>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/src/LinearAllocator.cpp>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/src/StackAllocator.cpp>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/docs/images/operations_over_time.png>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/docs/images/operations_over_time_no_init.png>
  - <https://github.com/mtrebi/memory-allocators>
  - <https://github.com/mtrebi/memory-allocators/commits>
- **Sources the enricher read:**
  - <https://github.com/mtrebi/memory-allocators>
  - <https://github.com/mtrebi/memory-allocators/commits>
  - <https://github.com/mtrebi/memory-allocators/issues?q=is%3Aissue>
  - <https://github.com/mtrebi/memory-allocators/issues/4>
  - <https://github.com/mtrebi/memory-allocators/issues/18>
  - <https://github.com/mtrebi/memory-allocators/issues/21>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/README.md>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/includes/Allocator.h>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/includes/Benchmark.h>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/includes/IO.h>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/includes/Utils.h>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/includes/CAllocator.h>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/includes/LinearAllocator.h>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/includes/StackAllocator.h>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/includes/PoolAllocator.h>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/includes/FreeListAllocator.h>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/includes/SinglyLinkedList.h>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/includes/SinglyLinkedListImpl.h>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/includes/StackLinkedList.h>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/includes/StackLinkedListImpl.h>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/src/Allocator.cpp>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/src/Benchmark.cpp>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/src/CAllocator.cpp>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/src/LinearAllocator.cpp>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/src/StackAllocator.cpp>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/src/PoolAllocator.cpp>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/src/FreeListAllocator.cpp>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/docs/images/operations_over_time.png>
  - <https://raw.githubusercontent.com/mtrebi/memory-allocators/HEAD/docs/images/operations_over_time_no_init.png>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/mtrebi/memory-allocators`) · [data/wave11/enrich/raw/github_com_mtrebi_memory_allocators.json](../../../data/wave11/enrich/raw/github_com_mtrebi_memory_allocators.json) (enrichment confidence 0.75)

</details>
