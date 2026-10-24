# SizeBasedArena&lt;T,N&gt; bump arena (Orc Tribe), Packt C++ Memory Management companion code

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Allocators and garbage collectors](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Per-class bump arena behind class-specific operator new/delete; book run shows about 1.3x faster construction than new/delete.

| | |
|---|---|
| **Beats** | glibc/libstdc++ operator new and operator delete (malloc/free) |
| **Claimed result** | operator new: 23433 us standard library vs 17906 us Meyers-singleton arena vs 17573 us global-singleton arena (arena about 76.4% of the standard time); operator delete: 7943 us standard vs 638 us Meyers-singleton arena (8.03%) vs 0 us global-singleton arena (no-op). Numbers are the book's printed figures as relayed in the seed lead; they are not printed anywhere in the repo. |
| **Workload** | Book benchmark: allocate then destroy 1,000,000 16-byte Orc objects with class-specific operator new/delete backed by a mutex-guarded bump arena, single thread, std::chrono timing in microseconds, one run. |
| **Metric** | throughput |
| **Compiler and flags** | Book: online gcc 15 at -O2 (per the seed lead; not in the repo, whose files only carry wandbox permalinks that I could not open: wandbox.org ENOTFOUND). libstdc++ inferred from gcc. |
| **Adoption** | 87 stars (companion repository) |
| **Last commit** | 2026-08-14 |
| **Links** | [repository](https://github.com/packtpublishing/c-plus-plus-memory-management) |

## Verdict

In the book's single run (online gcc 15, -O2 per the record, CPU not stated), constructing 1,000,000 16-byte Orc objects took 23,433 us through libstdc++ operator new (glibc malloc) versus 17,906 us (Meyers-singleton arena) and 17,573 us (global-singleton arena), about 1.3x; destroying them took 7,943 us with free() versus 638 us and 0 us for the arena's no-op delete. The repo carries the five driver programs (identical loops, only the operator overloads differ) but no results, build line or CPU, and the arena side still pays a mutex per allocation and first-touch page faults inside the timed loop.

## Use it when

- Single-class, allocate-many-then-drop-all phases (a level's entities, a parse tree, a batch job) with a known lifetime cap on the number of objects created.
- Retrofitting an existing class whose call sites use plain new/delete, by adding four class-level operator overloads.
- Teaching or prototyping region allocation before moving to a production arena such as std::pmr::monotonic_buffer_resource.

## Skip it when

- Any workload that creates more than N objects over the program's life, even if few are alive at once: delete never returns space and allocate_one has no bounds check, so object N+1 writes past the malloc'd buffer.
- Class hierarchies: operator new ignores its size argument and hands out sizeof(T) slots, so a larger derived class overruns the next slot unless you use the -safer variant (static_assert(std::is_final_v&lt;T&gt;)).
- Multithreaded hot allocation paths: every allocation takes the arena's single std::mutex.
- Memory-sensitive code: N \* sizeof(T) bytes (16 MB for 1,000,000 Orcs) are reserved up front and released only when the singleton dies at program exit.
- Anything that needs a general allocator; it serves one type and is a book example, not a maintained library.

## How it is fast

Allocation is a pointer bump (cur += sizeof(T)) under a std::mutex, with no size-class lookup, no per-object header and no call into malloc after the first one. Deallocation is an empty function, so freeing is free; the global-singleton variant lets the compiler delete the whole free loop, which is where the book's 0 us delete figure comes from. Objects are packed contiguously at sizeof(T) stride (16 bytes for Orc), so the timed loop touches fewer fresh pages than glibc's header-carrying chunks.

## Compared with alternatives

Pick it when you want the smallest possible per-class arena with unchanged call sites; ArenaAllocator (privateMwb) has a real benchmark against std::pmr::monotonic_buffer_resource, and obstack (cleeus) or fast-alloc are better choices when you need arena or pool code with published measurements.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (standard library &lt;mutex&gt;, &lt;cstdlib&gt;, &lt;cassert&gt;; &lt;type_traits&gt; for the safer variant) |
| **Minimum toolchain** | C++17 for the arena (class template argument deduction in std::lock_guard, std::is_final_v in the safer variant); the test drivers use C++23 &lt;print&gt;. Book build was online gcc 15 at -O2 per the record. |
| **Platforms** | any (portable standard C++ over std::malloc) |
| **Thread safety** | allocate_one/allocate_n are serialised by one std::mutex; the Meyers-singleton construction is thread-safe function-local static initialisation; deallocate is a no-op. |
| **Drop-in for the baseline** | partial — call sites keep new/delete unchanged for the one class that overloads its operators, but delete never frees and capacity is fixed at N objects for the whole run |

## Gotchas

- No exhaustion check: past N lifetime allocations the arena silently hands out memory beyond its buffer (heap overflow), unlike a pool that falls back to ::operator new.
- Array new differs by variant: the Tribe versions' operator new[] is assert(false) with no return statement (undefined behaviour under NDEBUG); SizeBasedArena's version computes n / sizeof(T) and so assumes the compiler adds no array cookie, which holds only for trivially destructible T such as Orc.
- Singleton choice changes timing: with the Meyers singleton the 16 MB malloc happens inside the first timed new and every call pays a static-guard check (the 638 us delete loop); the global static member avoids both but is exposed to static initialisation order if another translation unit's static initialiser news the class.
- The book's delete comparison is glibc free() against an empty function the optimiser can drop, so the 8.03% and 0 us delete ratios measure doing nothing, not a faster free.

## Known shortcomings

- Book numbers on no repo page. The 0 us global-singleton delete means the compiler removed the loop; the Meyers-singleton 638 us is mostly the static-local guard check, not allocation.
- Enricher: no exhaustion check, so past N lifetime allocations the arena overflows its heap buffer; operator new ignores the size, so a derived class overruns its slot (only the -safer variant blocks it); the Tribe variants' operator new[] is assert(false) with no return (undefined behaviour under NDEBUG) and SizeBasedArena's new[] assumes no array cookie. The delete comparison sets free() against an empty function. Chapter 10 files unchanged since 2024-08-14.

## Caveats and trade-offs

First-party book measurement: one run on an unnamed online gcc 15 machine (per the lead), CPU not stated; flags and numbers come from the book, not the repo. The repo carries the benchmark programs in chapter10 (carnage-stdlib-version.cpp, carnage-homemade-version-meyers-singleton.cpp, carnage-homemade-version-global-singleton.cpp, carnage-homemade-version-SizeBasedArena.cpp, carnage-homemade-version-SizeBasedArena-safer.cpp) with no printed results or build lines; the record's figures cover only the stdlib, Meyers-singleton and global-singleton variants. Not like for like: the arena never reuses memory, delete does nothing, and the test is allocate-all then free-all, the best case for a bump allocator. The 0 us delete in the global-singleton version means the compiler removed the whole loop (empty deallocate, no static-local guard); the Meyers version's 638 us is mostly the per-call static-local guard check. In the Meyers-singleton version the arena's one-time malloc of 1,000,000 Orc slots (16 MB) runs inside the first timed operator new call, and the arena's pages are first touched in the timed loop on both homemade variants. The std::vector&lt;Orc\*&gt; is reserved before timing on all variants. The arena locks a std::mutex per allocation while glibc malloc takes its single-thread fast path. Generic typed-arena speedup over malloc is well known; the evidence is a teaching example.

Bump allocation only: freed memory is never reused, delete is a no-op, so memory is reclaimed only when the arena is destroyed. Capacity N\*sizeof(T) is malloc'd up front, with no bounds check on exhaustion. A mutex is taken on every allocation. Serves one class (operator new/delete overloads for Orc); operator new[] and delete[] assert false. A SizeBasedArena-safer variant adds static_assert(std::is_final_v&lt;T&gt;) so derived classes cannot be allocated from a too-small slot.

## Maintenance

MIT-licensed Packt companion repository (87 stars) with commits through 2026-08-14, but the chapter10 arena files are unchanged since their 2024-08-14 upload; tiny and copyable, best treated as a worked example rather than a library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** chapter10/carnage-stdlib-version.cpp, carnage-homemade-version-meyers-singleton.cpp and carnage-homemade-version-global-singleton.cpp time 1,000,000 new Orc then 1,000,000 delete with the same driver (only the HOMEMADE_VERSION define and singleton style differ), but the repo holds code only; the microsecond figures are the book's own single run (relayed by the lead), with compiler, flags and CPU unstated in the repo, so first-party.
- **Verifier notes:** Diffed the five carnage files: stdlib and Meyers versions differ only by the HOMEMADE_VERSION define, the global version moves the singleton to a static member. sizeof(Orc) is 16 bytes (char[4], int, double). Book figures not checked (book not consulted per harness).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-66 (wave 11 book seed pass, 2026-10-24); enrichment (wave 11 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/packtpublishing/c-plus-plus-memory-management>
  - <https://github.com/packtpublishing/c-plus-plus-memory-management/commits>
  - <https://github.com/packtpublishing/c-plus-plus-memory-management/tree/main/chapter10>
  - <https://raw.githubusercontent.com/PacktPublishing/C-Plus-Plus-Memory-Management/HEAD/chapter10/carnage-stdlib-version.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/C-Plus-Plus-Memory-Management/HEAD/chapter10/carnage-homemade-version-meyers-singleton.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/C-Plus-Plus-Memory-Management/HEAD/chapter10/carnage-homemade-version-global-singleton.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/C-Plus-Plus-Memory-Management/HEAD/chapter10/carnage-homemade-version-SizeBasedArena.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/C-Plus-Plus-Memory-Management/HEAD/chapter10/carnage-homemade-version-SizeBasedArena-safer.cpp>
- **Sources the enricher read:**
  - <https://github.com/packtpublishing/c-plus-plus-memory-management>
  - <https://github.com/packtpublishing/c-plus-plus-memory-management/commits>
  - <https://github.com/packtpublishing/c-plus-plus-memory-management/tree/main/chapter10>
  - <https://github.com/packtpublishing/c-plus-plus-memory-management/commits/main/chapter10>
  - <https://github.com/packtpublishing/c-plus-plus-memory-management/issues>
  - <https://github.com/packtpublishing/c-plus-plus-memory-management/pulls>
  - <https://raw.githubusercontent.com/PacktPublishing/C-Plus-Plus-Memory-Management/HEAD/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/C-Plus-Plus-Memory-Management/HEAD/chapter10/carnage-stdlib-version.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/C-Plus-Plus-Memory-Management/HEAD/chapter10/carnage-homemade-version-meyers-singleton.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/C-Plus-Plus-Memory-Management/HEAD/chapter10/carnage-homemade-version-global-singleton.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/C-Plus-Plus-Memory-Management/HEAD/chapter10/carnage-homemade-version-SizeBasedArena.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/C-Plus-Plus-Memory-Management/HEAD/chapter10/carnage-homemade-version-SizeBasedArena-safer.cpp>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `paper:book-c-plus-plus-memory-management-sizebasedarena`) · [data/wave11/enrich/raw/paper_book_c_plus_plus_memory_management_sizebasedarena.json](../../../data/wave11/enrich/raw/paper_book_c_plus_plus_memory_management_sizebasedarena.json) (enrichment confidence 0.7)

</details>
