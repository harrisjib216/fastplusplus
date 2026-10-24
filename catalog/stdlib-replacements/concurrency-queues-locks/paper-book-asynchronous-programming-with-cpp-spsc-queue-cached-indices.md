# SPSC lock-free ring buffer with cached head and tail indices (Asynchronous Programming with C++ companion code)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Concurrent queues and locks](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Teaching-grade SPSC ring buffer that caches the peer's index; about 1.6x its own uncached variant in the book's run.

| | |
|---|---|
| **Beats** | the book's own power-of-two SPSC ring buffer without cached head/tail copies (head_ and tail_ atomics on separate 64-byte-aligned slots); not Boost.Lockfree, not a mutex-guarded std::queue |
| **Claimed result** | Book, relayed by the seed lead and not present on the repo page: about 101.6 million to about 162.5 million ops/sec, roughly 60% faster (1.6x); perf stat cache misses 41.30% down to 31.39%. |
| **Workload** | One producer thread (core 2) pushes and one consumer thread (core 12) pops 1 billion ints through a 2^17-element queue; the consumer checks the order; operations per second = iterations divided by wall time. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper Pro 5975WX, Ubuntu 24.04 (from the book via the seed lead; the repo itself does not state a CPU) |
| **Compiler and flags** | Chapter_13/CMakeLists.txt sets -O3 -DNDEBUG -std=c++20 -march=native; README lists GCC 14.2 and Clang 18, the lead says GCC 13 was used. |
| **Adoption** | 95 stars |
| **Last commit** | 2026-04-22 |
| **Links** | [repository](https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP) · [benchmark](https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/blob/main/Chapter_13/13x08-spsp_lock_free_queue.cpp) |

## Verdict

The book reports, for 1 billion ints through a 2^17-slot queue between CPUs 2 and 12 of an AMD Ryzen Threadripper Pro 5975WX (Ubuntu 24.04, GCC 13 per the lead, -O3 -march=native from the repo's CMake), about 101.6 million items per second for the uncached ring buffer against about 162.5 million for the cached-index version, roughly 1.6x, with perf-reported cache misses falling from 41.30% to 31.39%. The benchmark code is in the repo but its results are not, so this is a first-party single-run comparison of two in-house variants with no standard-library or third-party baseline.

## Use it when

- Exactly one producer thread and one consumer thread passing small trivially copyable items (ints, pointers, POD messages) between pinned cores, for example a market-data or logging hand-off.
- Throughput-bound streaming where the consumer usually trails the producer by several items, so the cached indices stay valid across many operations.
- As a readable reference of about 50 lines for teaching, or for hand-rolling a queue in a codebase that cannot take Boost or a third-party header.
- When both ends can afford to busy-spin and you want to avoid a mutex plus condition variable.

## Skip it when

- More than one producer or consumer: there is no compare-and-swap anywhere, so concurrent pushes or concurrent pops corrupt the queue; use an MPMC queue.
- Production use without your own tests: the repo ships no unit or stress tests for this queue, and the only evidence is one book run against the authors' own uncached variant, not against Boost.Lockfree or any other library.
- Large or resource-owning element types: items are copied in and out (no move, no emplace), every slot is default-constructed up front, and a popped value stays alive in its slot until it is overwritten.
- Latency ping-pong or a mostly empty queue: when the consumer is always caught up, each pop misses its cached tail and reloads the shared index, so the saving shrinks (reading of the source; the benchmark measured only bulk throughput).
- Running the benchmark program off Linux: it uses pthread_setaffinity_np and cpu_set_t, although the queue class itself is portable C++.

## How it is fast

Head and tail are std::atomic&lt;size_t&gt; members on separate 64-byte-aligned slots, published with release stores and read with acquire loads, so neither side takes a lock. The optimisation is index caching: the producer keeps a private copy of the consumer's head (cache_head_) and the consumer a private copy of the producer's tail (cache_tail_), and each reloads the shared atomic only when its cached copy says the queue looks full or empty. Most push and pop calls then touch only their own index's cache line, which cuts cross-core coherency traffic; rigtorp/SPSCQueue documents the same technique. Index wrap-around uses a bit mask instead of modulo.

## Compared with alternatives

Pick it only to vendor about 50 dependency-free lines or to learn the cached-index technique; for production SPSC traffic Boost.Lockfree spsc_queue, moodycamel::ReaderWriterQueue and atomic_queue are maintained, tested and have independent shootout numbers (about 42 to 51 ns mean ping-pong latency in the catalogued shootout), while this queue has only the book's comparison against its own uncached variant.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for the queue class (standard &lt;atomic&gt; and &lt;vector&gt;); the benchmark program needs pthreads, and the repo's CMake build links every Chapter 13 program against Google Benchmark and, at the top level, requires Boost 1.86, GoogleTest and {fmt} |
| **Minimum toolchain** | the queue class uses only C++11 features (alignas, std::atomic, default member initialisers); the repo compiles Chapter 13 with -O3 -DNDEBUG -std=c++20 -march=native, and the README lists GCC 14.2 and Clang 18 |
| **Platforms** | any for the queue class; the 13x08 benchmark is Linux/glibc only because of pthread_setaffinity_np, even though the README lists macOS and Windows for the book as a whole |
| **Thread safety** | one producer thread calling push and one consumer thread calling pop; empty() reads both indices with relaxed loads and is only a hint; no other concurrent use is safe |
| **Drop-in for the baseline** | no |

## Gotchas

- The power-of-two capacity check is an assert and the Chapter 13 build defines NDEBUG, so a non-power-of-two capacity silently produces wrong slot indices; usable capacity is capacity minus one.
- alignas(64) on the index members does not pad the members after them, so in the optimised class capacity_ and the vector's pointers share cache_tail_'s line (written by the consumer, read by the producer on every push), and the heap buffer has no padding against neighbouring allocations, which rigtorp/SPSCQueue adds. The book's measured gain therefore also mixes in a layout change between the two classes (reading of the source, effect not measured).
- The benchmark pins the producer to CPU 2 and the consumer to CPU 12 and calls exit(EXIT_FAILURE) when pthread_setaffinity_np fails, so it aborts on machines with 12 or fewer logical CPUs; on other topologies those ids may be SMT siblings or sit in different cache domains, which changes the result.
- Reported ops/sec counts items transferred (one push plus one pop each), from a single run with the uncached queue always run first; consumer() takes its iteration count as int, so raising it past INT_MAX overflows.

## Known shortcomings

- Book numbers only; the baseline is the book's own uncached queue variant; one run in fixed order with the baseline first; steady_clock timing; last code change 2024-11-14.
- Enricher: power-of-two check is an assert compiled out by -DNDEBUG (silent mis-indexing), hard-coded CPUs 2 and 12 exit on small machines, Linux-only affinity, no padding of capacity and buffer pointer, no tests.

## Caveats and trade-offs

Comparison is between two variants of the book's own queue, so there is no standard-library, Boost.Lockfree, rigtorp SPSCQueue or mutex-queue baseline. Numbers are first-party and not in the repo; the CPU model exists only in the book, so tier C. Core ids 2 and 12 are specific to the author's machine and map to different cache domains elsewhere. The two classes also differ in member layout, which the benchmark does not isolate: alignas(64) on head_ and tail_ does not pad the members that follow, so in the baseline capacity_ and the buffer pointer share tail_'s cache line, while in the optimised class they follow cache_tail_ instead (my reading of the source, effect not measured). Single run; both variants run in one process in fixed order (baseline first), so warm-up or frequency effects are not separated. Throughput is timed with std::chrono::steady_clock from the producer's first push to the consumer join. Last code change in the repo is 2024-11-14; the 2026 commits only edit a conference banner in the README. [retier] Enricher: the power-of-two capacity check is an assert, compiled out by Chapter_13's -DNDEBUG, so a non-power-of-two capacity silently mis-indexes. CPUs 2 and 12 are hard-coded and set_affinity exits on machines with 12 or fewer logical CPUs; 13x08 is Linux/glibc only (pthread_setaffinity_np). ops/sec counts items transferred; consumer() takes an int iteration count. In the optimised class capacity_ and the vector pointer share cache_tail_'s line and the buffer is not padded (rigtorp's SPSCQueue pads both). No tests for the queue.

Single-producer single-consumer only; capacity must be a power of two and one slot stays unused; the element type must be default-constructible and copy-assignable; both sides busy-spin when the queue is empty or full; it uses plain std::vector storage with no padding between buffer slots.

## Maintenance

The queue file has had one commit ('Chapter-13 examples', 2024-10-18) and later repo commits only edit the README; it is MIT-licensed, about 50 lines and easy to vendor as a reference, and none of the three open issues (build setup on macOS and Windows, a Chapter 3 timer example) concerns this queue.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** Chapter_13/13x08-spsp_lock_free_queue.cpp runs spsc_lock_free_queue and spsc_lock_free_queue_optimized (cached head/tail copies) back to back with 1e9 ints, 2^17 capacity, producer core 2 and consumer core 12, built with the Chapter_13 -O3 -march=native flags; no CPU model or results in the repo, the ops/sec figures are the book's first-party numbers via the lead, so C.
- **Verifier notes:** Source matches the record's description (cached indices, alignas(64) atomics, order check in consumer). Book figures (101.6M against 162.5M ops/sec) not checkable from the repo.
- **Fields the verifier corrected:** `caveats`, `maintenance_status`
- **Shortcomings recorded by:** verifier batch-86 (wave 1 book seed pass, 2026-10-24); enrichment (wave 1 book seed pass, 2026-10-24)
- **Pages the verifier opened:**
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/commits/main>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/tree/main/Chapter_13>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/blob/main/Chapter_13/13x08-spsp_lock_free_queue.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/Chapter_13/13x08-spsp_lock_free_queue.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/Chapter_13/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/README.md>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/main/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/HEAD/Chapter_13/13x08-spsp_lock_free_queue.cpp>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/HEAD/Chapter_13/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PacktPublishing/Asynchronous-Programming-with-CPP/HEAD/README.md>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/tree/main/Chapter_13>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/commits/main/Chapter_13/13x08-spsp_lock_free_queue.cpp>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/issues>
  - <https://github.com/PacktPublishing/Asynchronous-Programming-with-CPP/issues/27>
  - <https://raw.githubusercontent.com/rigtorp/SPSCQueue/HEAD/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `paper:book-asynchronous-programming-with-cpp-spsc-queue-cached-indices`) · [data/wave1/enrich/raw/paper_book_asynchronous_programming_with_cpp_spsc_queue_cached_indices.json](../../../data/wave1/enrich/raw/paper_book_asynchronous_programming_with_cpp_spsc_queue_cached_indices.json) (enrichment confidence 0.75)

</details>
