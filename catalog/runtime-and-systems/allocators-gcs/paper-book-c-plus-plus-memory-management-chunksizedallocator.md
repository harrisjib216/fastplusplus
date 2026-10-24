# ChunkSizedAllocator&lt;N,Sz...&gt; chunked fixed-size-class pool, Packt C++ Memory Management companion code

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Teaching-grade fixed size-class pool (one malloc'd chunk per power-of-two class) used through placement new; about 1.1x over new/delete in the book.

| | |
|---|---|
| **Beats** | glibc/libstdc++ operator new and operator delete (malloc/free) |
| **Claimed result** | Chunked version 12,032 us versus 13,360 us for the standard operator new/delete version, about 90.05% of the standard time (roughly 1.1x, derived from the book's two figures). Numbers are the book's printed figures as relayed in the seed lead; not printed in the repo. |
| **Workload** | Book benchmark: 300,000 allocations (100,000 each of 30-, 60- and 100-byte objects) through placement-style operator new(ChunkSizedAllocator&), then destroy and deallocate through std::function, microseconds, one run. |
| **Metric** | throughput |
| **Compiler and flags** | Book: online gcc 15 at -O2 (per the seed lead; not in the repo, which only links a wandbox permalink I could not open). libstdc++ inferred from gcc. |
| **Adoption** | 87 stars (companion repository) |
| **Last commit** | 2026-08-14 |
| **Links** | [repository](https://github.com/packtpublishing/c-plus-plus-memory-management) |

## Verdict

In the book's single run (online gcc 15, -O2 per the record, CPU not stated), allocating and then freeing 100,000 each of 30-, 60- and 100-byte objects, each stored with a std::function deleter, took 13,360 us through libstdc++ new/delete (glibc malloc) and 12,032 us through ChunkSizedAllocator, about 1.11x. The repo holds the benchmark program but no results, build line or CPU, and the pool side's frees do no work while glibc's free does real bookkeeping.

## Use it when

- Reading or teaching how size-class pools work; the whole allocator is about 60 lines in chapter10/chunk_sized_allocator.cpp.
- Short-lived batch phases with a known upper bound on small objects per size class (the book uses 100,000 each of 30-, 60- and 100-byte objects) that are all thrown away together.
- As a starting point for your own pool when you will add free-slot reuse and drop the per-allocation mutex in single-threaded code.

## Skip it when

- Long-running alloc/free churn: freed slots are never reused, so after N lifetime allocations per class every request pays the class scan, a mutex lock and then ::operator new, and every free pays the range scan before ::operator delete, which is slower than plain new/delete.
- Memory-constrained programs: all N slots of every class (about 22 MB for the book's N = 100,000 with 32/64/128-byte classes) are malloc'd up front whether used or not.
- Multithreaded allocation-heavy code: one std::mutex serialises every allocation.
- Code that needs a drop-in malloc, std::allocator or std::pmr::memory_resource, or array new; none is provided.
- Production use in general: a book exercise with a roughly 10% measured gain, not a maintained library.

## How it is fast

Allocation picks the first class whose size is strictly larger than the request and bumps a per-class index into a contiguous block under a std::mutex, so there is no free-list search, no per-object header and no trip into malloc. Deallocation only checks which block the pointer lies in and returns; freed slots are never handed out again, so free costs a short range scan instead of glibc's bin bookkeeping.

## Compared with alternatives

Pick it to read a compact, compile-time-configured size-class pool; for real use fast-alloc (pool allocate/free 3.0x over new/delete, with GCC 14.2.0 and the CPU named) or mtrebi/memory-allocators (pool and free-list allocators with benchmark code) are better starting points.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (standard library only: &lt;mutex&gt;, &lt;concepts&gt;, &lt;array&gt;, &lt;cstdlib&gt; via transitive includes) |
| **Minimum toolchain** | C++20 for the allocator (concepts, constrained auto parameters); the test driver in the same file uses C++23 &lt;print&gt;. Book build was online gcc 15 at -O2 per the record. |
| **Platforms** | any (portable standard C++ over std::malloc) |
| **Thread safety** | allocate is serialised by a single std::mutex; deallocate takes no lock and is safe only because it never modifies state (the lock is commented out for a future reuse path). |
| **Drop-in for the baseline** | no |

## Gotchas

- The class test is strict (n &lt; sizes[i]), so a request exactly equal to a class size skips it: 32-byte objects land in the 64-byte class and 128-byte objects fall through to ::operator new. The book's 30/60/100-byte test sizes never hit this.
- ::operator delete(p, alloc) only releases memory; it does not run the destructor, so callers must destroy the object themselves first (the benchmark's dummy&lt;N&gt; types are trivially destructible).
- The benchmark times std::function type erasure and std::pair moves into a pre-built vector on both sides, plus first-touch page faults (the pool's blocks are malloc'd before timing but touched inside it), so the 10% gap understates and blurs the raw allocator difference.
- The file relies on &lt;cstdlib&gt; arriving through other headers for std::malloc/std::free; add the include when vendoring.

## Known shortcomings

- Book numbers (12,032 vs 13,360 us) appear on no repo page. Harness: the vector is allocated in an init-capture outside the clock, pool pages are first touched inside the timed run, std::mutex taken per allocate, no reuse.
- Enricher: the size-class test is strict (n &lt; sizes[i]), so exact 32/64/128-byte requests skip their class or fall to ::operator new; freed slots are never reused, so after N lifetime allocations per class every call pays the class scan, the mutex and ::operator new and is slower than the baseline; explicit placement delete skips destructors. Chapter 10 files unchanged since 2024-08-14.

## Caveats and trade-offs

First-party book measurement: one run, online gcc 15 at -O2 (per the lead), CPU not stated; the gain is small (about 10%). Benchmark program is chapter10/chunk_sized_allocator.cpp: it prints the two timings but the repo holds no results, compiler line or CPU. The pool's three malloc'd blocks (100,000 slots each of 32, 64 and 128 bytes, about 22 MB) are allocated in the constructor outside the timed region, but their pages are first touched inside the timed chunked run. The std::vector of 300,000 (pointer, std::function) pairs is allocated in each lambda's init-capture before the clock starts and freed after it stops; filling it and the std::function type erasure are timed on both sides. The standard version runs first in the same process. The chunked allocate locks a std::mutex per call while deallocate does nothing; the book itself warns that locking strongly affects the gain and locking in deallocate would likely erase it. No memory reuse (freed slots are never handed out again; when a class fills up, requests fall through to ::operator new), so not like for like with a real allocator. [retier] Enricher: the size-class test is strict (n &lt; sizes[i]), so exact 32/64/128-byte requests skip their class (128-byte objects fall to ::operator new); freed slots are never reused, so after N lifetime allocations per class each call pays the class scan, the mutex and ::operator new and runs slower than the baseline; ::operator delete(p, alloc) skips destructors; std::function and std::pair moves are timed on both sides, diluting the 10%; the file relies on &lt;cstdlib&gt; arriving through other headers. The chapter10 files are unchanged since 2024-08-14 (later commits touch other chapters).

Fixed pools: N blocks per size class (rounded up to powers of two) allocated up front with malloc, allocation falls back to ::operator new when a pool is exhausted or the size does not fit. Freed memory is never reused (deallocate only checks whether the pointer lies in a pool). Deallocation does a linear scan over the size classes. A mutex guards allocate; the lock in deallocate is commented out. new[] and delete[] are left as an exercise.

## Maintenance

MIT-licensed Packt companion repository (87 stars) with commits through 2026-08-14, but chapter10 files have not changed since their 2024-08-14 upload; small enough to copy, best treated as a worked example.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** chapter10/chunk_sized_allocator.cpp times the same 300,000 mixed-size allocations and frees through plain new/delete and through ChunkSizedAllocator, but the repo holds code only; the 12,032 versus 13,360 us figures are the book's own single run (relayed by the lead, not on any page), with compiler, flags and CPU unstated in the repo, so first-party.
- **Verifier notes:** Code matches the lead's description (sizes 32, 62 rounded to 64, 128; N = 100,000; dummy&lt;30&gt;, dummy&lt;60&gt;, dummy&lt;100&gt;). Book figures could not be checked (book not consulted per harness; wandbox permalinks not opened); kept at C per the wave12 book-record precedent.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-66 (wave 11 book seed pass, 2026-10-24); enrichment (wave 11 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/packtpublishing/c-plus-plus-memory-management>
  - <https://github.com/packtpublishing/c-plus-plus-memory-management/commits>
  - <https://github.com/packtpublishing/c-plus-plus-memory-management/tree/main/chapter10>
  - <https://raw.githubusercontent.com/PacktPublishing/C-Plus-Plus-Memory-Management/HEAD/chapter10/chunk_sized_allocator.cpp>
- **Sources the enricher read:**
  - <https://github.com/packtpublishing/c-plus-plus-memory-management>
  - <https://github.com/packtpublishing/c-plus-plus-memory-management/commits>
  - <https://github.com/packtpublishing/c-plus-plus-memory-management/tree/main/chapter10>
  - <https://github.com/packtpublishing/c-plus-plus-memory-management/commits/main/chapter10>
  - <https://github.com/packtpublishing/c-plus-plus-memory-management/issues>
  - <https://github.com/packtpublishing/c-plus-plus-memory-management/pulls>
  - <https://raw.githubusercontent.com/PacktPublishing/C-Plus-Plus-Memory-Management/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/C-Plus-Plus-Memory-Management/HEAD/chapter10/chunk_sized_allocator.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `paper:book-c-plus-plus-memory-management-chunksizedallocator`) · [data/wave11/enrich/raw/paper_book_c_plus_plus_memory_management_chunksizedallocator.json](../../../data/wave11/enrich/raw/paper_book_c_plus_plus_memory_management_chunksizedallocator.json) (enrichment confidence 0.7)

</details>
