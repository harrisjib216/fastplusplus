# The Art of Writing Efficient Programs: publishing pointer (ts_unique_ptr) instead of an atomic std::shared_ptr

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Smart pointers and reference counting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Book sample: single-writer publishing pointer over std::atomic&lt;T\*&gt; versus atomic_load/atomic_store on a std::shared_ptr; never frees replaced objects.

| | |
|---|---|
| **Beats** | std::shared_ptr accessed through std::atomic_load_explicit and std::atomic_store_explicit |
| **Claimed result** | Book: single-threaded dereference matches a raw pointer and std::unique_ptr, and the publishing pointer is about 60 times faster than the atomic std::shared_ptr on one thread (Figures 6.5 to 6.7 hold the chart). |
| **Workload** | Chapter06/03_owning_ptr_mbm.C against 03b_shared_ptr_mbm.C and 03a_raw_ptr_mbm.C (Google Benchmark, ThreadRange(1, numcpu) so 1, 2, 4, ... threads all running the same operation, real time): BM_ptr_deref copies the published object through the pointer and BM_ptr_assign publishes a pointer, 64 unrolled operations per iteration; there is no mixed reader/writer run. ts_unique_ptr is a std::atomic&lt;T\*&gt; with release publish and acquire get. |
| **Metric** | latency |
| **Hardware** | x86; CPU model not stated |
| **Compiler and flags** | Not stated for the book's run. The repo's generic build command (Chapter02/ReadMe.md) is \$CXX (GCC or Clang) -g -O3 --std=c++17 linked against Google Benchmark with -lpthread -latomic -lrt -lm; compiler, version and standard library unnamed. |
| **Adoption** | 405 stars (Packt book companion repository) |
| **Last commit** | 2024-05-13 |
| **Links** | [repository](https://github.com/packtpublishing/the-art-of-writing-efficient-programs) · [benchmark](https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/blob/master/Chapter06/03_owning_ptr_mbm.C) |

## Verdict

The book, relayed by the seed lead (the repo holds no numbers), reports single-threaded dereference through ts_unique_ptr matching a raw pointer and about 60x faster than dereferencing a std::shared_ptr read through std::atomic_load_explicit, with thread-scaling charts in the book only. Compiler, standard library and CPU (only x86 is stated) are not named; the repo's generic build line is GCC or Clang -g -O3 --std=c++17, and the code was read, not built, here.

## Use it when

- One writer and many readers where published objects are immutable and either never freed while the program runs (configuration or lookup tables set up once) or retired by a separate scheme such as epochs, RCU or hazard pointers.
- Read-mostly hot paths where each reader needs the pointer only for a short access and a lock or reference-count update per read shows up in profiles.
- Replacing std::atomic_load on a std::shared_ptr that exists only to publish a snapshot, when leaking or deferring the old snapshots is acceptable.
- Studying the cost of memory ordering and shared ownership: the three Chapter06 files are a ready side-by-side harness.

## Skip it when

- Replaced objects must be freed: operator= does not delete the old object (the delete is commented out), and deleting it at publish time would free it under readers still holding the raw pointer from get().
- Readers need ownership or lifetime extension: get() hands out a raw pointer and nothing keeps the object alive.
- Several writers need read-modify-write updates: only store and load exist, with no exchange or compare_exchange.
- Expecting the 60x everywhere: the ratio is against mutex-pool atomic shared_ptr access; C++20 std::atomic&lt;std::shared_ptr&gt; in current libstdc++ uses a lock bit in the control-block pointer instead of the global mutex pool, so the gap differs, and the repo does not measure it.

## How it is fast

Reading is one acquire load and publishing one release store of a plain pointer; on x86-64 both map to ordinary MOV instructions, so a dereference costs what a raw pointer costs. The baseline's free-function atomic access to a shared_ptr is lock-based in the mainstream libraries: libstdc++ locks one of 16 mutexes chosen by hashing the shared_ptr's address and libc++ one of 32, and each load also copies the shared_ptr (an atomic increment and later decrement of the control block's count). The speedup is the removal of that lock and the two reference-count read-modify-writes, along with the cache-line traffic they cause when several threads read the same pointer.

## Compared with alternatives

Against CDRC (concurrent_deferred_rc), which gives atomic shared and weak pointers with safe deferred reclamation, pick ts_unique_ptr only when published objects are immortal or retired by your own scheme and you want the cheapest possible read. The same chapter's intr_shared_ptr (04_intr_shared_ptr_mbm.C, an intrusive count guarded by a per-pointer spin lock that swaps in a sentinel) is the middle ground when objects must be freed.

## Integration

| | |
|---|---|
| **Form** | source-drop (a class template of about 15 lines inside the benchmark file) |
| **Dependencies** | none (&lt;atomic&gt;); the benchmarks need Google Benchmark |
| **Minimum toolchain** | C++11 (std::atomic); the repo's generic build line (Chapter02/ReadMe.md) is GCC or Clang with -g -O3 --std=c++17 -lpthread -latomic |
| **Platforms** | any target with lock-free std::atomic&lt;T\*&gt;; the benchmark files include unistd.h and call sysconf, so they build on Linux and macOS only |
| **Thread safety** | Concurrent get() calls and one publisher are race-free on the pointer itself; object lifetime and reclamation are left to the caller |
| **Drop-in for the baseline** | no |

## Gotchas

- No reclamation, by necessity in this harness: BM_ptr_assign republishes the same pointer q, so the commented-out delete-on-assign would free q and then publish it; the destructor deletes only the last published object, so the initial A(42) leaks.
- The baseline protects nothing it pays for: 03b's get() returns .get() of a temporary shared_ptr that dies at the end of the expression, so each dereference takes the pool mutex and does an increment and decrement yet leaves the reader with an unprotected raw pointer; with one global p every thread contends on the same mutex, and each 03b assign also copies q by value (one more count update on a shared control block).
- Counting and symmetry: REPEAT runs 64 operations per iteration but SetItemsProcessed counts 32, so items/s figures are 2x low in all three files (ratios unaffected); 03a uses a volatile pointer and calls ClobberMemory every iteration while 03 does not; deref and assign run as separate benchmarks, so no mixed reader/writer contention is measured.
- The baseline API is legacy: libstdc++ marks the std::atomic_load/atomic_store overloads for shared_ptr deprecated in C++20 and points to std::atomic&lt;std::shared_ptr&lt;T&gt;&gt;; the repo builds with --std=c++17.

## Known shortcomings

- Book numbers only. REPEAT does 64 operations but SetItemsProcessed counts 32, so items/s is 2x off (ratios unaffected); ts_unique_ptr's operator= leaks with no reclamation; Chapter06 has no std::unique_ptr benchmark; every thread runs the same operation (ThreadRange).
- Enricher: baseline pays a lock and refcount round trip per dereference while protecting nothing, one pool mutex for all threads; deprecated C++20 overloads, so the 60x is library-specific; initial object leaks.

## Caveats and trade-offs

The timing numbers are the book's own (quoted in the seed lead); the repository carries the benchmark program but no results file, so the numbers do not appear on the benchmark_url page and the ratios could not be checked against it. The 60x is mostly the cost of the library's atomic shared_ptr access: libstdc++ and libc++ have implemented std::atomic_load on a shared_ptr through a global mutex pool, so the ratio depends on the standard library and version (C++20 std::atomic&lt;std::shared_ptr&gt; differs again) and the book does not name it. Compiler, flags and CPU not stated. The baseline does extra work (reference counting) that the publishing pointer avoids by design, so it is a different safety contract and not a like-for-like swap. [verifier] Harness defects: REPEAT expands to 64 operations per iteration in all three files but SetItemsProcessed counts 32, so items-per-second figures (and any per-operation time derived from them) are off by a factor of 2; the ratios between files are unaffected because all share the error. ts_unique_ptr's operator= publishes without deleting the previous object (the delete is commented out), so the publishing pointer leaks on reassignment and offers no reclamation, which is the work the shared_ptr baseline pays for: each 03b dereference copies a shared_ptr through atomic_load_explicit (a lock from the mutex pool plus a reference-count increment and decrement). The raw-pointer file calls ClobberMemory every iteration while the owning-pointer file does not. The Chapter06 listing has no std::unique_ptr benchmark, so the 'matches std::unique_ptr' part of the claim is the book's text only. [retier] Enricher: the 03b baseline's get() returns .get() of a temporary shared_ptr, so it pays the lock plus a count increment and decrement on every dereference yet protects nothing; all threads contend on one pool mutex (libstdc++ uses 16, libc++ 32); each 03b assign also copies q by value. The commented-out delete cannot be enabled (BM_ptr_assign republishes the same q and would free it) and the initial A(42) leaks. The baseline's atomic_load/atomic_store overloads for shared_ptr are deprecated in C++20, and libstdc++'s C++20 atomic&lt;shared_ptr&gt; uses a control-block lock bit instead, so the 60x is library-specific.

Not a drop-in replacement: get() returns a raw pointer, there is no shared ownership, publish() does not free the object it replaces (the benchmark just republishes one pointer), so retired objects must be kept alive or reclaimed by the caller, and readers can dangle if a writer deletes. Single writer and many readers is the intended use.

## Maintenance

Stale Packt companion repo (62 commits, last on 2024-05-13) under MIT; the class is small enough to copy but needs a reclamation scheme before production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter06/03_owning_ptr_mbm.C (ts_unique_ptr over std::atomic&lt;T\*&gt;) and 03b_shared_ptr_mbm.C (the same interface over std::shared_ptr with atomic_load_explicit/atomic_store_explicit) run identical BM_ptr_deref and BM_ptr_assign benchmarks, but the repo holds code only; the 60x figure is the book's own run relayed by the lead, with no named compiler, standard library or CPU, so first-party tier C.
- **Verifier notes:** Code matches the record's description of ts_unique_ptr and the shared_ptr baseline. Kept at C; the claim compares a non-reclaiming atomic raw pointer with mutex-pool atomic shared_ptr access, so the ratio is library-specific. Metadata checked on github.com: MIT, 405 stars, last commit 2024-05-13, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-89 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/blob/master/Chapter06/03_owning_ptr_mbm.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/HEAD/Chapter06/03_owning_ptr_mbm.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/HEAD/Chapter06/03b_shared_ptr_mbm.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/HEAD/Chapter06/03a_raw_ptr_mbm.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/HEAD/Chapter06/04b_atomic_shared_ptr_mbm.C>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/tree/master/Chapter06>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter06/03_owning_ptr_mbm.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter06/03a_raw_ptr_mbm.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter06/03b_shared_ptr_mbm.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter06/04_intr_shared_ptr_mbm.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter06/04a_shared_ptr_mbm.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter06/04b_atomic_shared_ptr_mbm.C>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/master/Chapter02/ReadMe.md>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/tree/master/Chapter06>
  - <https://github.com/PacktPublishing/The-Art-of-Writing-Efficient-Programs/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc++-v3/src/c++11/shared_ptr.cc>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc++-v3/src/c++11/mutex_pool.h>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc++-v3/include/bits/shared_ptr_atomic.h>
  - <https://raw.githubusercontent.com/llvm/llvm-project/main/libcxx/src/memory.cpp>
  - https://www.cl.cam.ac.uk/\~pes20/cpp/cpp0xmappings.html (search snippet only: x86 acquire load and release store map to MOV)
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-the-art-of-writing-efficient-programs-publishing-pointer`) · [data/wave1/enrich/raw/paper_book_the_art_of_writing_efficient_programs_publishing_pointer.json](../../../data/wave1/enrich/raw/paper_book_the_art_of_writing_efficient_programs_publishing_pointer.json) (enrichment confidence 0.6)

</details>
