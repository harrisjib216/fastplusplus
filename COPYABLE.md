# Copyable

Entries with a confirmed OSI license: code can be vendored, wrapped, or forked. Grouped by license family, then category; tier A/B first, tier C/D under *Unverified claims*.

## Permissive

### concurrency-queues-locks

#### atomic_queue  `C++`  `MIT`  `active`  `Tier A`

Header-only lock-free MPMC/SPSC ring-buffer queues beating std::mutex-guarded queues by 4-10x in latency and throughput.

**Beats:** std::mutex — On the author's own shootout (gcc-14.2.0, libstdc++, Ryzen 5950X with SMT on), AtomicQueue's SPSC ping-pong round-trip latency is 42ns versus 320ns for a std::mutex-guarded ring buffer baseline (~7.6x lower), and OptimistAtomicQueue reaches 33ns (~9.7x lower); 1-producer/1-consumer throughput is ~142.7M msg/s for AtomicQueue and a highly variable ~1.23B msg/s for OptimistAtomicQueue versus ~4.1M msg/s for std::mutex, though with 2-16 producer/consumer pairs only OptimistAtomicQueue keeps a large (4-24x) lead while plain AtomicQueue is roughly at parity with std::mutex.

**How:** A ring buffer with compile-time or construction-time fixed capacity avoids heap allocation and pointer chasing after construction, and value semantics (no references into the buffer) avoid pointer aliasing. It issues the bare minimum of atomic instructions per push/pop, explicitly pads to avoid false sharing, and its SPSC mode drops expensive atomic read-modify-write ops in favor of plain atomic loads/stores. There is no OS-blocking wait path: push/pop either fail fast (try_ variants) or busy-spin (optimist push/pop), avoiding the roughly 1-3us syscall/wake-up latency of a blocked thread.

**Use it when:**
- Fixed/bounded number of in-flight small, cheaply copyable/movable messages (integers, pointers, small PODs) between a known set of threads.
- Sub-microsecond push-to-pop latency matters more than avoiding CPU spin, and dedicated cores/threads are available to spin.
- SPSC hot path (e.g. one I/O thread feeding one processing thread) where the SPSC-tuned mode avoids read-modify-write atomics entirely.
- Shared-memory IPC between processes: non-B variants are position-independent and can be placement-new'd into mmap/shm_open segments.
- Need back-pressure signaling via try_push failure rather than letting a queue grow unbounded.

**Skip it when:**
- Need unbounded or dynamically-growing capacity; maximum size must be fixed at compile time (array buffer) or construction time (B variants).
- Threads should sleep/block instead of spinning; there is no OS-blocking wait, so waiting threads pin a CPU core at 100%.
- Elements are large or expensive to copy/move, since push/pop always copies or moves the element and no in-place references are exposed.
- Need per-element priorities or ordering guarantees beyond FIFO/the optional totally-ordered mode.
- Atomic-element queues: pushing the reserved NIL sentinel is undefined behavior in release builds (only debug asserts catch it), so element type/value range must exclude it.

**Integration:** header-only · none to use the library; Boost.Test is needed only to build its own unit tests · C++14; also builds under C++20/C++23 as of v1.9.4 (v1.9.3 had a C++20 AtomicQueueB2 constructor bug on Apple clang, fixed in v1.9.4) · Linux x86_64 (primary dev/benchmark target); CI also covers Linux ARM, RISC-V, PowerPC, S390, LoongArch (via QEMU), Windows x86_64, and macOS ARM

**Vs siblings:** Pick atomic_queue's OptimistAtomicQueue when the workload has contention from multiple producer/consumer pairs, since it is the only queue in this shootout that keeps a large (4-24x) throughput lead over std::mutex from 2 to 16 pairs, or when queue objects must be position-independent for shared-memory IPC. For a pure low-contention SPSC channel, moodycamel::ReaderWriterQueue (43ns) and Boost.Lockfree spsc_queue (51ns) post comparable ping-pong latency with smaller, more established codebases, and plain (non-optimist) AtomicQueue itself is only at parity with std::mutex once several producer/consumer pairs contend.

**Gotchas:**
- NIL sentinel (default 0) must never be pushed into atomic-element queues; release builds have no runtime check and violation causes UB such as deadlocks or lost elements.
- No OS-blocking push/pop: busy-spin waiting consumes a full CPU core, unsuitable for threads that should yield or sleep.
- v1.9.3 broke AtomicQueueB2's constructor under -std=c++20 on Apple clang (issue #109, fixed in v1.9.4, released 2026-09-16); use >=1.9.4.
- Capacity is fixed once (compile time for array buffers, construction time for heap/B-variant buffers) and cannot grow; undersizing it makes try_push start failing under load.

**Status:** Actively maintained (recent commits and the v1.9.4 point release as of September 2026) under the MIT license; header-only and small enough to vendor directly.

[repo](https://github.com/max0x7ba/atomic_queue) · [benchmark](https://max0x7ba.github.io/atomic_queue/html/benchmarks.html)

#### Boost.Lockfree  `C++`  `BSL-1.0`  `active`  `Tier A`

Boost's lock-free MPMC/SPSC queue and stack family; beats std::mutex on latency, not contended MPMC throughput.

**Beats:** std::mutex — An independent third-party benchmark (the atomic_queue shootout; gcc-14.2.0 -O3 -march=native, AMD Ryzen 5950X, Linux) measured ping-pong round-trip latency of spsc_queue at 51ns and queue at 92ns against std::mutex at 320ns (about 6.3x and 3.5x lower). A separate 2017 evpp benchmark (gcc-4.8.2, Xeon E5-2630 v2) found boost::lockfree::queue giving 75-150% higher throughput than a mutex-guarded std::vector, but only with multiple producers. Neither benchmark is Boost's own, and the same shootout's MPMC throughput data shows boost::lockfree::queue losing to std::mutex once 2 or more producer/consumer pairs are contending.

**How:** queue implements Michael & Scott's lock-free MPMC algorithm with a tagged-pointer freelist that recycles nodes instead of returning memory to the OS on every pop. spsc_queue is a wait-free single-producer/single-consumer ring buffer (the same technique used in the Linux kernel) with no compare-and-swap on its hot path at all. Skipping mutex acquisition removes the futex/syscall path and priority-inversion risk that dominate std::mutex latency under contention. bounded_ticket_queue additionally implements a Vyukov turnstile algorithm that becomes wait-free when producer or consumer count is fixed to one side.

**Use it when:**
- Exactly one producer thread and one consumer thread need a ring buffer and latency matters (spsc_queue measured at 51ns vs std::mutex 320ns in the atomic_queue shootout)
- MPMC queue with a bounded/fixed-size capacity, where avoiding OS-level allocation and priority inversion matters more than peak contended throughput
- Already depend on Boost and want an actively maintained (last commit 2026-08-14), widely-used lock-free structure without adding a new third-party dependency
- Element type is a small, trivially-copyable POD (ints, small structs, raw pointers used carefully) rather than move-only or exception-throwing

**Skip it when:**
- Heavily contended MPMC throughput: in the atomic_queue shootout, boost::lockfree::queue loses to a std::mutex-guarded ring buffer at every count of 2+ producer/consumer pairs (5.9M vs 13.0M msg/s at 2 pairs; 1.5M vs 2.3M at 16)
- T is a pointer type: open issue #120 reports a data race where concurrent pop() can hand the same pointer to two threads
- Code depends on pop() returning false only when the queue is truly empty: open issue #119 shows pop() can spuriously return false under concurrent push/pop on a non-empty queue
- Need move-only element types or exception-safety guarantees in push/pop: unsupported (open request #125); docs explicitly discourage exceptions in lock-free code
- Need std::queue/std::stack API compatibility such as iteration or arbitrary resizing: the API is deliberately narrower

**Integration:** header-only · Boost.Align, Boost.Assert, Boost.Atomic, Boost.Config, Boost.Core, Boost.Parameter, Boost.Predef, Boost.Utility (ships as part of Boost, not standalone) · C++14 (CMake target_compile_features cxx_std_14); uses C++20 concepts opportunistically when available · any platform with CAS/double-width-CAS atomic support; internal tagged-pointer representation switches between a DCAS scheme and a pointer-compression scheme depending on platform, not documented as restricted to a specific ISA

**Vs siblings:** Pick Boost.Lockfree when you already depend on Boost and want an actively-maintained, well-tested queue without adding a new dependency. Pick atomic_queue or moodycamel::ReaderWriterQueue instead when SPSC latency is the priority (42-43ns vs Boost's 51ns) or for contended MPMC throughput, where boost::lockfree::queue loses to a plain std::mutex ring buffer.

**Gotchas:**
- boost::lockfree::queue<T*> has an open data-race report (issue #120): concurrent pop() can return the same pointer to two threads
- pop() can spuriously return false on a non-empty queue under concurrent push/pop (issue #119), so a false return does not strictly mean 'empty'
- T must be trivially copy-assignable and trivially destructible for queue; move-only types fail to compile rather than degrading gracefully
- capacity<> and allocator<> policy options are mutually exclusive (static_assert) - pick compile-time-fixed or runtime-allocated sizing, not both

**Status:** Actively maintained as part of mainline Boost (last commit 2026-08-14); BSL-1.0 licensed and header-only, so it is cheap to adopt if you already take Boost as a dependency.

[repo](https://github.com/boostorg/lockfree) · [benchmark](https://max0x7ba.github.io/atomic_queue/html/benchmarks.html)

#### moodycamel::ReaderWriterQueue  `C++`  `BSD-2-Clause`  `active`  `Tier A`

Header-only lock-free SPSC queue for C++11; beats a mutex-guarded queue by ~7x in ping-pong latency.

**Beats:** std::mutex — In the independent max0x7ba/atomic_queue SPSC ping-pong shootout (gcc-14.2.0, -O3 -march=native -mtune=native, AMD Ryzen 5950X, readerwriterqueue commit 2ae710d), moodycamel::ReaderWriterQueue measured a 43ns mean round-trip latency versus 320ns for a mutex-guarded ring buffer used as the std::mutex baseline (~7.4x lower). The project's own benchmarks/bench.cpp never compares against std::mutex at all — only against the 1024cores SPSC queue and folly::ProducerConsumerQueue.

**How:** Queue-of-queues design: a circular-linked-list of fixed-size 'block' ring buffers, with the producer owning tail indices/pointers and the consumer owning front indices/pointers so each thread only writes its own state. Enqueue/dequeue are wait-free (no CAS loop, no spinning), O(1) except when a new block must be malloc'd. On x86/x86-64 the required memory barriers compile down to no-ops, so the hot path is just plain loads and stores.

**Use it when:**
- Exactly one fixed producer thread and one fixed consumer thread that never swap roles
- Passing small, cheaply-movable/copyable values (counters, pointers, small structs) between the two threads
- Need sub-100ns round-trip latency and want to avoid std::mutex-guarded queue overhead entirely
- Want a 2-file header-only drop with zero build step and zero external dependencies
- Running on x86/x86-64 (the best-tested and only architecture the author has directly validated)

**Skip it when:**
- Need multiple producers or multiple consumers (use the same author's moodycamel::ConcurrentQueue instead)
- Threads need to switch producer/consumer roles at runtime, or use the queue from more than 2 threads
- Targeting AArch64 or another weakly-ordered architecture on an old pinned commit: size_approx() had a real SIGSEGV race from a missing release fence before publishing new blocks (issue #171); fixed, but verify the fix is in your pinned commit
- Need a version-pinned release: the project ships no tags (open issues #144/#146 ask for one), so you pin a raw commit SHA
- Destroying the queue while a thread is blocked in wait_dequeue() is undefined behavior — risky in ad-hoc shutdown paths

**Integration:** header-only · none (readerwriterqueue.h + atomicops.h; atomicops.h embeds Preshing's zlib-licensed semaphore for the blocking variant) · C++11; MSVC2010+, GCC 4.7+ (GCC 4.6 has a fence bug), ICC 13+ · x86/x86-64 (only architecture directly tested by the author); portable to ARM/PowerPC per code comments but AArch64 had a confirmed weak-memory-model race, fixed in a recent commit (issue #171); explicitly not for DEC Alpha

**Vs siblings:** Pick this over atomic_queue, Boost.Lockfree, xenium, or oneTBB when you want the smallest possible header-only footprint (2 files, no build) purely for the SPSC case and don't need bounded/blocking strategy choices or MPMC support; atomic_queue's AtomicQueue (42ns) and OptimistAtomicQueue (33ns) edge it out slightly in the same shootout, so pick those instead if the last few nanoseconds matter more than dependency count.

**Gotchas:**
- size_approx() could dereference a null block on AArch64 due to a missing release fence in inner_enqueue() (issue #171) — fixed, but confirm the fix predates whatever commit you pin
- Plain enqueue() can malloc and grow the queue on demand; only try_enqueue() is guaranteed never to allocate
- Destroying the queue while a thread is blocked in wait_dequeue()/wait_dequeue_timed() is undefined behavior
- No tagged releases exist (open issues #144, #146); vendor a commit SHA rather than expecting semver tags

**Status:** Actively maintained (last commit 2026-09-07, 4.6k stars) but ships no tagged releases; BSD-2-Clause (Simplified BSD, per LICENSE.md — GitHub's license detector shows NOASSERTION) and small enough (2 headers) to vendor directly.

[repo](https://github.com/cameron314/readerwriterqueue) · [benchmark](https://max0x7ba.github.io/atomic_queue/html/benchmarks.html)

#### oneTBB concurrent_bounded_queue  `C++`  `Apache-2.0`  `active`  `Tier A`

Bounded/blocking FIFO queue in Intel's oneTBB parallelism library; non-blocking try_push/try_pop mode cuts round-trip latency ~3.9x vs std::mutex.

**Beats:** std::mutex — In the independent max0x7ba/atomic_queue SPSC ping-pong shootout on an AMD Ryzen 5950X (gcc-14.2.0, -O3 -march=native -mtune=native, TBB 2021.11.0-2ubuntu2, mitigations=off), tbb::concurrent_bounded_queue driven via non-blocking try_push/try_pop averaged 83ns round-trip latency versus 320ns for a std::mutex-guarded queue over libstdc++, about 3.9x lower latency; the same suite's MPMC throughput test showed only ~2x std::mutex at 1 producer/1 consumer, with std::mutex ahead at 2 and 4 pairs.

**How:** Enqueue/dequeue hand out monotonically increasing 'tickets' from head_counter/tail_counter atomics via compare-exchange, mapping each ticket to a slot in a lazily-grown ring of fixed-size micro-segments, so there is no single global mutex on the hot path. Blocking waits (capacity-limited push, empty pop) go through a dedicated concurrent_monitor wait/notify mechanism implemented in the compiled runtime rather than busy-spinning, and internal structures are cache-line aligned (cache_aligned_allocator, alignment asserts against max_nfs_size) to reduce false sharing between producer and consumer cache lines. The cited benchmark used non-blocking try_push/try_pop, which skips the monitor-wait path entirely and reduces each operation to a handful of atomics plus one CAS.

**Use it when:**
- Already linking oneTBB elsewhere in the app, so adding another dependency just for a queue is unnecessary
- Need bounded capacity plus real blocking push/pop with a documented cancellation path (abort())
- Producer/consumer counts are modest (roughly 1 pair) where ~3.9x lower latency and ~2x throughput over std::mutex is enough headroom
- Want an Apache-2.0, multi-platform (Windows/Linux/macOS/Android) queue backed by an industry foundation rather than a single-maintainer header library
- Value signed size()/empty() semantics that expose how many consumers are waiting

**Skip it when:**
- Pure SPSC ping-pong latency is the goal: moodycamel::ReaderWriterQueue (43ns) and atomic_queue (42ns) are faster and header-only
- Cannot add a compiled runtime/link dependency: the blocking and abort machinery lives in the compiled oneTBB library, not just the header
- Higher contention (2+ producer/consumer pairs): in the same shootout's MPMC throughput test std::mutex actually beat concurrent_bounded_queue at 2 pairs (13.0M vs 11.1M msg/s) and 4 pairs (6.9M vs 6.5M msg/s)
- Exceptions are disabled: abort() and blocked waiters signal cancellation by throwing exception_id::user_abort, not via a non-throwing flag
- Want a minimal, easily vendored single header; oneTBB is a large library with its own build/install story

**Integration:** shared lib (headers call into a compiled runtime; can also be built static via CMake) · oneTBB runtime library (libtbb) must be built/linked; no third-party deps for the queue itself. oneTBB overall optionally uses hwloc for NUMA-aware scheduling elsewhere in the library, not required for this queue. · C++11 minimum per the CMake default (CMAKE_CXX_STANDARD); GCC 8-16, Clang 7-22, MSVC 14.2+ (VS2019+), or Intel oneAPI DPC++/C++ per SYSTEM_REQUIREMENTS.md · x86-64 primary; Windows, Linux, and macOS officially supported, Android 9 supported; MinGW, FreeBSD, Windows on ARM/ARM64, and macOS on ARM64 are community-supported; separate WASM support documented

**Vs siblings:** Pick oneTBB's concurrent_bounded_queue over atomic_queue, Boost.Lockfree, moodycamel::ReaderWriterQueue, or xenium when you already depend on oneTBB or specifically need its bounded-capacity blocking push/pop plus abort()-based cancellation with vendor-grade, multi-platform support; all four siblings are faster in raw ping-pong latency (42-60ns vs 83ns) and are header-only, so prefer them when latency or a zero-dependency drop-in matters more than having one production parallelism library.

**Gotchas:**
- abort() and any blocked push()/pop() unblock by throwing exception_id::user_abort, so callers need exceptions enabled and abort-aware code, not a simple non-throwing cancel flag
- Default capacity is effectively unbounded (near SIZE_MAX / item size); set_capacity() is required to get real bounding, and the docs note bounded queues are slower than unbounded ones
- empty() means size() <= 0, not 'no elements present' — with pending pops, size() is negative
- Not a single-header drop-in: it links against a compiled oneTBB runtime rather than working as a standalone header like a typical lock-free queue library

**Status:** Actively maintained by the UXL Foundation as Intel's flagship C++ threading library (about 6.7k stars); Apache-2.0 licensed and copyable, but adopting concurrent_bounded_queue alone still means pulling in oneTBB's full compiled runtime, not vendoring a small file.

[repo](https://github.com/uxlfoundation/oneTBB) · [benchmark](https://max0x7ba.github.io/atomic_queue/html/benchmarks.html)

#### xenium  `C++`  `MIT`  `stale`  `Tier A`

Header-only lock-free MPMC queue templates (Michael-Scott, Ramalhete, Vyukov) beating std::mutex latency 2.5-5.7x.

**Beats:** std::mutex — Independent third-party shootout (max0x7ba/atomic_queue benchmarks.cc, gcc-14.2.0, xenium commit f6416d3, -O3 -march=native -mtune=native, libstdc++, AMD Ryzen 5950X, mitigations=off) measured mean round-trip ping-pong latency of 56ns for ramalhete_queue, 60ns for vyukov_bounded_queue, and 128ns for michael_scott_queue against 320ns for std::mutex — roughly 5.7x, 5.3x, and 2.5x lower respectively; xenium's own benchmark suite has no std::mutex comparison.

**How:** ramalhete_queue implements Ramalhete & Correia's FAAArrayQueue: array-segmented linked-list nodes with fetch-and-add push/pop index cursors instead of a CAS per element, cutting contention on the fast path. michael_scott_queue is the classic Michael & Scott (1996) CAS-based lock-free linked-list queue. vyukov_bounded_queue uses Vyukov's bounded MPMC ring-buffer design with per-slot sequence numbers so producers and consumers avoid contending on shared head/tail counters. In the benchmark that produced these numbers, both node-based queues were configured with xenium::reclamation::new_epoch_based (confirmed in atomic_queue's benchmarks.cc), avoiding hazard-pointer-style per-op bookkeeping.

**Use it when:**
- Low-latency SPSC/MPMC ping-pong or handoff paths where std::mutex+std::queue's lock overhead dominates (measured 56-128ns vs 320ns round trip)
- Fixed, known-capacity workloads where an allocation-free bounded ring buffer is acceptable -> vyukov_bounded_queue
- Value types that are raw pointers, std::unique_ptr, or small trivially copyable PODs and you want the fastest of the three -> ramalhete_queue
- Arbitrary movable value types where ramalhete_queue's type restriction is unacceptable and you can absorb per-push allocation -> michael_scott_queue
- C++17 codebases willing to vendor a header-only dependency and explicitly choose a reclamation-scheme policy

**Skip it when:**
- High push contention with ramalhete_queue: an open, maintainer-confirmed double-free bug in the node destructor when pop_idx/push_idx wrap (issue #44, opened Oct 2025, unresolved)
- Object destructors that themselves push to a xenium queue using the same reclamation scheme can recurse into reclamation and double-destruct (issue #41, open; workaround is using a different reclaimer per structure)
- Repo has had no commits in ~14 months (last push 2025-07-29); treat as stale, not actively developed
- Need arbitrary non-trivial value types and want the fastest queue: ramalhete_queue's type restriction (pointer-like or small trivially copyable) rules it out
- Teams that want to avoid template-heavy header-only code and reclamation-scheme decisions versus the simplicity of std::mutex+std::queue

**Integration:** header-only · none for library use (C++17 standard library only); googletest, taocpp/json, taocpp/config are only needed as submodules to build the unit tests/benchmarks · C++17; CI validates gcc9, clang10, Visual Studio 2019 · x86-64 confirmed in the cited benchmark (Ryzen 5950X, Linux); CI also covers Windows/VS2019; no documented architecture restriction, ARM not verified

**Vs siblings:** Pick xenium when you also want a reusable library of composable reclamation schemes (hazard pointers, epoch-based, stamp-it) shared across other lock-free structures like hash maps and sets, not just a queue; atomic_queue and moodycamel::ReaderWriterQueue are narrower, simpler, and measured faster (33-51ns) with no reclamation-scheme decision to make, and Boost.Lockfree/oneTBB trade some speed for being part of a more widely vetted, already-deployed library.

**Gotchas:**
- Open, maintainer-confirmed bug: ramalhete_queue's node destructor can double-free under high push contention when pop_idx/push_idx wrap around (issue #44, unresolved as of this writing)
- Pushing to a queue from inside an object's destructor while that object is being reclaimed by the same scheme can recurse and double-destruct (issue #41); maintainer recommends a different reclamation scheme per data structure
- ramalhete_queue only accepts raw pointers, std::unique_ptr (custom deleters not yet supported), or trivially copyable types no larger than a pointer
- stamp_it reclaimer emits -Winvalid-memory-model warnings under gcc12 with -Werror (issue #26, open since 2022, documented one-line workaround)

**Status:** Stale: no commits since 2025-07-29 (~14 months) though the maintainer still replies to issues; MIT-licensed, header-only, and small enough to vendor, but two open double-free/double-destruction bug reports (#41, #44) remain unresolved.

[repo](https://github.com/mpoeter/xenium) · [benchmark](https://max0x7ba.github.io/atomic_queue/html/benchmarks.html)

### hash-maps-sets

#### emhash (ktprime/emhash: emhash5/6/7/8 + emilib)  `C++`  `MIT`  `active`  `Tier A`

Header-only open-addressing C++ hash table family; emhash7 beats std::unordered_map on insert/find/erase/iterate at 10M elements.

**Beats:** std::unordered_map — On an AMD Ryzen 7 5800H / Windows 10, GCC 11.3 (-O3 -march=native -std=c++17) build, emhash7 beat std::unordered_map (libstdc++) at 10M integer-key elements: insert ~4.5x (66.0 vs 295), find-hit ~2x (16.9 vs 33.0), find-miss ~2.9x (18.1 vs 52.0), erase ~14x (20.4 vs 293), and iterate ~85x (0.74 vs 62.6). These are the project's own docs/performance.md numbers, reproducible via bench/ebench but not independently re-run for this entry.

**How:** emhash7 stores key-value pairs inline in one contiguous array plus a separate bitmask for fast empty-slot scanning, and repairs the bucket chain on erase instead of leaving tombstones, so mixed insert/erase workloads don't degrade even at load factor 0.999. Iteration is a straight scan of that array, which is why it beats std::unordered_map's pointer-chasing linked-node layout by roughly 85x on the 10M-element iterate benchmark. The emilib variants instead use Swiss-table-style SIMD group probing with a 1-byte H2 tag per bucket to filter most candidates before a full key comparison.

**Use it when:**
- Mixed insert/find/erase workloads on integer or POD keys where throughput close to hand-tuned open addressing matters (emhash7)
- Need a load factor above 0.9 (up to 0.999) without the clustering/degradation open addressing usually shows at that density
- Iteration-heavy hot paths over the whole map/set (emhash7/emhash8), since the flat array scan beats std::unordered_map's node chasing by an order of magnitude
- Want a header-only, dependency-free drop-in (copy one .hpp) rather than adding a build dependency
- Input keys are trusted/internal, not adversarially chosen

**Skip it when:**
- Code holds long-lived references or pointers into the map across inserts — open addressing invalidates them on rehash; std::unordered_map does not
- Keys come from untrusted/adversarial input: emhash7/8 don't cap probe-sequence length by default, which SECURITY.md flags as a hash-flooding DoS risk unless you enable EMH_SAFE_HASH or switch to an emilib EMH_SAFE_PSL variant
- Multiple threads write concurrently without your own locking — emhash provides no internal synchronization
- You want independently reproduced numbers rather than the vendor's own benchmark (emhash's table is self-measured on one Windows/GCC config, not verified here against Ankerl 2022 or Allan 2024 methodology)
- Very large value types where rehash-driven moves are costly and you haven't wrapped them in unique_ptr

**Integration:** header-only · none (wyhash is bundled in config.hpp; pass -DEMH_NO_BUILTIN_WYHASH to supply your own) · C++17 (some examples use C++20); GCC, Clang, or MSVC · Windows, Linux, macOS; x86-64 and ARM64 (Apple M1/M2). emhash5-8 are scalar (no SIMD requirement); emilib variants add SSE2/AVX2/AVX-512 group probing where available

**Vs siblings:** Pick emhash over rigtorp::HashMap, ska::flat_hash_map, or tsl::robin_map/hopscotch_map when you need a load factor up to 0.999 without tombstone-driven degradation on mixed insert/erase workloads, or want a matched family (emhash6/7/8) tuned per access pattern instead of one fixed design. Pick a sibling instead when you want a single implementation whose speedup was measured by an independent, cross-library suite (e.g. Ankerl 2022) rather than the vendor's own benchmark.

**Gotchas:**
- emhash7/8 do not cap probe-sequence length by default; SECURITY.md calls this a hash-flooding DoS risk on untrusted keys. Mitigate with EMH_SAFE_HASH (~10% overhead) or an emilib EMH_SAFE_PSL variant
- Any insert that triggers a rehash invalidates all existing references and iterators, unlike std::unordered_map's node-based stability
- Erasing inside a plain range-for is undefined behavior; use the iterator-returning erase(it) or erase_if() instead
- Some thirdparty/emilib variants (e.g. emilib2ss) can degrade into a full table scan under an all-keys-collide attack; the maintained include/emilib/emihmap2.hpp (emilib2::HashMap) is not the affected fork, but pick emilib2o/emilib2s for untrusted input regardless

**Status:** Actively maintained (last commit 2026-09-05, v1.1.0) and MIT-licensed; header-only, so a single .hpp such as hash_table7.hpp can be vendored with no external dependency.

[repo](https://github.com/ktprime/emhash) · [benchmark](https://github.com/ktprime/emhash/blob/master/docs/performance.md)

#### google::dense_hash_map (sparsehash)  `C++`  `BSD-3-Clause`  `abandoned`  `Tier A`

Open-addressing C++ hash map beating std::unordered_map on lookups/inserts at large memory cost.

**Beats:** std::unordered_map — On Tessil's independent hash-table shootout (Clang 5.0, -O3 -march=native -DNDEBUG, libstdc++, Intel i5-5200u), google::dense_hash_map beat std::unordered_map in 20 of 21 tests, a ~2.3x geometric-mean speedup, including read_random_full at n=3,000,000 (0.054s vs 0.297s, ~5.5x) and insert_random_full (0.309s vs 1.056s, ~3.4x); its sole loss was insert_string at ~0.90x.

**How:** It stores all key/value pairs inline in one contiguous array (densehashtable.h) using quadratic-probing open addressing, so lookups walk cache lines instead of chasing per-node pointers/allocations the way node-based chaining maps do. A reserved empty-key sentinel marks free slots without a separate occupancy bitmap, and erase() writes a deleted-key tombstone instead of compacting, which avoids iterator invalidation but leaves stale entries until a resize. Confirmed against README.md, the dense_hash_map header, and densehashtable.h in the repo, and against Tessil's independent shootout (Clang 5.0, -O3 -march=native -DNDEBUG, Intel i5-5200u), which measured it fastest in 20 of 21 tests.

**Use it when:**
- Read-heavy workloads with fixed-size keys (integers, pointers, short strings) where lookup latency matters more than memory footprint.
- Data sets that comfortably fit in RAM with headroom to spare for a doubling resize.
- You can carve out two sentinel key values (empty + deleted) that will never appear as real data.
- You can build and run under an older/stable C++ toolchain (GCC/Clang pre-C++20) and pin -DNDEBUG so asserts don't eat the speed gain.
- You're fine vendoring a BSD-3-Clause, unmaintained-since-2020 header set rather than depending on active upstream support.

**Skip it when:**
- Memory-constrained services: README states a 2-4x steady-state overhead, rising to a 6x 'high-water mark' mid-resize (old 2x table plus new 4x table coexist).
- Heavy erase/reinsert cycles near max_load_factor(1): issue #141 shows find() on a missing key can loop forever once every bucket is either occupied or a deleted-tombstone.
- Very large datasets: issue #123 reports dense_hash_map hanging/failing around ~900M entries (16-process distributed job) where std::unordered_map ran fine.
- Element counts that land just below a power of two: issue #172 (open, filed Dec 2025) reports an unresolved, order-of-magnitude slowdown in the 2.0.4 release near power-of-two sizes, absent in 2.0.3.
- String-heavy or variable-length keys, and any build on GCC 11+ with -std=c++20/c++2b: Tessil's shootout shows it losing on insert_string (0.90x vs std::unordered_map), and open PRs/issues (#165, #166) report c++20 build fixes needed and a c++2b segfault in libc_allocator_with_realloc.

**Integration:** header-only · none at the API level, but the build needs autotools (./configure/make install) or an equivalent packaged sparseconfig.h to generate the platform's HASH_FUN_H macro before the headers are usable · C++03/11-era API (tr1-style hash<>); upstream has not verified newer standards - open reports of build failures/segfaults under -std=c++20/c++2b on GCC 11+ · any (README reports Linux, Solaris, FreeBSD, macOS, and Windows/MSVC support, last verified against toolchains circa 2010-2015; pure C++, no SIMD/intrinsics required)

**Vs siblings:** Within the sparsehash family, pick dense_hash_map over sparsepp when you have RAM to spare and want the fastest lookups; sparsepp trades some of that speed for much lower memory and reportedly beats dense_hash_map's stability at very large sizes. Against actively maintained alternatives (tsl::robin_map, ska::flat_hash_map, emhash), dense_hash_map's only real draw is its long-proven quadratic-probing design — those get comparable or better speed without the mandatory empty/deleted-key setup or an unmaintained-since-2020 codebase with open hang/perf-regression reports.

**Gotchas:**
- set_empty_key() must be called right after construction (or passed to the iterator-range constructor) and set_deleted_key() before any erase() call; skipping either, or inserting a key equal to one, causes undefined/mysterious failures per the header comments.
- erase() never reclaims memory or invalidates iterators; repeated erase/insert cycles bloat memory until you call resize(0), and at max_load_factor(1) a fully-occupied table (valid + deleted buckets only) can make find() on an absent key loop forever (issue #141).
- Resizing needs up to 6x the raw entry size as a transient high-water mark (README), so budget memory headroom well beyond the steady-state 2-4x overhead.
- dense_hash_map's disk-serialization methods (write_metadata/write_nopointer_data) are present in the API but unimplemented and always fail — only sparse_hash_map actually supports save/restore to disk.

**Status:** Abandoned since its last commit on 2020-08-12 — the repo has 20+ open issues/PRs including an unresolved December 2025 report of a severe performance regression near power-of-two sizes in the 2.0.4 release; it's BSD-3-Clause and small enough to vendor, but expect friction building under modern C++ standards/compilers.

[repo](https://github.com/sparsehash/sparsehash) · [benchmark](https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html)

#### ska::flat_hash_map / ska::bytell_hash_map  `C++`  `BSL-1.0`  `abandoned`  `Tier A`

Header-only Robin Hood open-addressing hash map/set beating std::unordered_map on lookups, inserts, and erases.

**Beats:** std::unordered_map — Ankerl 2022 (martinus/map_benchmark; clang++13 -O3 -march=native; Intel i7-8700 @3200MHz; libstdc++), normalizing to the same hash function for both sides, measured ska::flat_hash_map at 2.06-2.32x std::unordered_map geometric-mean runtime (number find 2.8-3.6x, string find 1.55-1.95x, random insert/erase 4.0-4.6x, iteration 0.79-0.97x i.e. slightly slower) and ska::bytell_hash_map at 2.12-2.31x geomean (insert-then-erase 4.4-4.6x). The author's own 2017 post claims the fastest lookups he tested, but shows only graphs with no stated compiler or hardware.

**How:** Both use Robin Hood open addressing with backward-shift deletion (no tombstones) and cap worst-case probe length at max(4, log2(bucket_count)), so lookups stay bounded regardless of hash quality. flat_hash_map defaults to a fibonacci hash policy (multiply-shift, no modulo) with a low 0.5 max load factor to keep probe chains short; a power_of_two_std_hash wrapper opts into masking instead. bytell_hash_map keeps the same Robin Hood core but stores per-slot state in packed metadata blocks (a triangular-number jump-distance table) and raises max load factor to 0.9375, trading some speed for a smaller footprint.

**Use it when:**
- Hot lookup/insert/erase paths on int or short string keys, single-threaded, where you control hash quality: Ankerl 2022 shows 2.06-2.32x geomean over libstdc++ std::unordered_map with the same hash.
- Sizes known up front (reserve()-able) with light iteration, since the gain is on insert/erase/find, not on scanning.
- Insert/erase churn workloads, especially with bytell_hash_map (insert-then-erase ~4.4-4.6x vs std::unordered_map) where the 0.9375 load factor also keeps memory tight.
- Small vendorable dependency for game/offline C++11-14 code that can't take on Abseil or a newer-toolchain-only library.
- Trusted, non-adversarial key inputs (internal data, not user-controlled strings from the network).

**Skip it when:**
- Iteration-heavy code: flat_hash_map's iteration is 0.79-0.97x std::unordered_map (Ankerl 2022) and described by that benchmark as one of the slowest tested; memory use is also high.
- bytell_hash_map erase-during-iteration loops: issue #41 reports duplicate elements returned after erase() while iterating; a fix was posted in comments but never merged.
- Builds using -O2 -DNDEBUG with bytell_hash_map: issue #11 reports a 'free(): invalid pointer' SIGSEGV traced to sherwood_v8_block::empty_block()'s static sentinel; unresolved since 2018.
- Untrusted/attacker-influenced keys: no seeded/randomized hashing (issue #17, 'Unsafe with attacker controlled keys'), same exposure as raw std::hash but with nobody patching it.
- Code shared across shared-library/module boundaries: issues #43 and #26 describe static-data (empty_default_table) problems when the header is instantiated in multiple translation units.
- Anywhere you rely on std::unordered_map's iterator/reference stability: backward-shift deletion relocates other elements on erase (issue #30, 'Insert invalidate iterators').

**Integration:** header-only · none beyond the STL (<cstdint> <cstddef> <functional> <cmath> <algorithm> <iterator> <utility> <type_traits>; bytell_hash_map.hpp additionally includes flat_hash_map.hpp, <vector>, <array>) · C++11 (variadic templates, rvalue refs, allocator_traits; ships its own void_t shim rather than relying on C++14/17, so no later standard is required) · any standard C++ target, no SIMD/intrinsics; open issues note past failures on 32-bit ARM (fix referenced in issue #18) and a still-open concern about jump_distances on x86 builds for bytell_hash_map (issue #37)

**Vs siblings:** Pick this over emhash, sparsepp, robin-map, or rigtorp::HashMap when the independent Ankerl 2022 head-to-head numbers (same-hash, normalized geomean) matter more than a vendor's own benchmark, or when you specifically want bytell_hash_map's lower memory overhead (0.9375 load factor) at some cost to lookup/iteration speed. Prefer an actively maintained sibling (e.g. tsl::robin_map, emhash) if you need try_emplace, bucket() semantics, or bug fixes — this repo has had zero commits since 2018-07-15 and 42 open issues, including the correctness/crash bugs above.

**Gotchas:**
- erase() performs backward-shift deletion: elements after the erased slot get moved in memory, invalidating their iterators/references too, not just the erased one's (sherwood_v3_table::erase; issue #30).
- bytell_hash_map: duplicate-item-after-erase bug when erasing during iteration (issue #41), fix posted in comments but never merged.
- bytell_hash_map: reported SIGSEGV under -O2 -DNDEBUG tied to sherwood_v8_block::empty_block()'s static sentinel (issues #11, #14), unresolved.
- No seeded hashing; adversarial keys can force worst-case probing exactly like plain std::hash (issue #17).

**Status:** Abandoned since 2018-07-15 with 42 open issues, including two unresolved correctness/crash bugs specific to bytell_hash_map; declared BSL-1.0 in every header despite GitHub showing no LICENSE file, so it's freely copyable and small enough to vendor and patch yourself.

[repo](https://github.com/skarupke/flat_hash_map) · [benchmark](https://martin.ankerl.com/2022/08/27/hashmap-bench-01/)

#### sparsepp (spp::sparse_hash_map, greg7mdp/sparsepp)  `C++`  `BSD-3-Clause`  `active`  `Tier A`

Header-only open-addressing hash map/set beating std::unordered_map on memory and, per two independent suites, speed.

**Beats:** std::unordered_map — Two independent third-party suites (not the author's own graphs) show spp::sparse_hash_map beating libstdc++'s std::unordered_map: Ankerl 2022 (clang++13, -O3 -march=native, Intel i7-8700) measured geometric-mean speedups of 1.98-2.03x depending on hash choice, with number-find up to 2.51x, but spp timed out on integer insert/erase/find when using an unmixed identity hash. Tessil's 2017 shootout (Clang 5.0 with libstdc++, 200K-3M entries) measured 1.11-3.31x faster successful lookups and 1.15-5.60x faster misses, with inserts ranging 0.61-1.47x (slower than std::unordered_map on string keys).

**How:** Uses Google sparsehash's 'sparsetable' layout: slots are grouped (SPP_GROUP_SIZE, 32 or 64) and each group carries a bitmap (group_bm_type in spp.h) marking which slots are occupied, so mostly-empty regions cost almost nothing to store. Open addressing itself avoids std::unordered_map's per-node allocation and pointer chasing. The README says this layout also keeps the resize memory spike small compared to a plain open-addressing table, though the resize algorithm itself wasn't inspected this session. Integer keys get a built-in bit-mixing default hash to avoid the pathological slowdown that sequential/identity-hashed keys cause on non-present lookups.

**Use it when:**
- Memory-constrained C++ workloads (embedded, large in-memory indexes) where per-entry overhead or resize memory spikes from std::unordered_map/dense_hash_map are the bottleneck
- Integer or string key/value hash tables in the hundreds-of-thousands to ~100M entry range, matching the benchmarked workload
- Projects on pre-C++11 or older MSVC/g++ toolchains that can't take the C++11 requirement of greg7mdp/parallel-hashmap
- Throughput-oriented insert/lookup/erase workloads, not strict latency SLAs, with no need for concurrent writers
- Need built-in binary serialize()/unserialize() of the whole table to a file or stream

**Skip it when:**
- Peak throughput matters most: google::dense_hash_map beats sparsepp on insert, lookup, and delete in the author's own bench.md
- Any C++11+ toolchain is available: the author's README now recommends greg7mdp/parallel-hashmap (or gtl) instead of sparsepp
- Code holds long-lived references or pointers into the map across insert()/erase() — sparsepp invalidates them more aggressively than std::unordered_map
- Code uses a sparse_hash_map/set after moving from it — moved-from tables segfault on further use (issue #83, open, unresolved)
- Hash quality is uncertain (e.g. an unmixed identity hash on integer keys) — spp degrades badly or times out per Ankerl 2022

**Integration:** header-only · none (C++ standard library only) · Works with C++03; C++11 features (move semantics, initializer lists) auto-detected and used if the compiler supports them. Tested on VS2010-2015, g++, clang++. · Windows, Linux, macOS; x86/x64, no SIMD required. Compiler/platform detection macros derived from Boost for portability.

**Vs siblings:** Pick sparsepp over google::dense_hash_map when the final table size is unknown and you can't absorb dense_hash_map's larger resize memory spike; pick it over tsl::robin_map/ska::flat_hash_map/emhash mainly when stuck on a pre-C++11 toolchain, since for any C++11+ project the author's own README recommends parallel-hashmap (not sparsepp) over those newer designs too.

**Gotchas:**
- Moved-from sparse_hash_map/set is left in an inconsistent state; calling find() or other operations on it segfaults (issue #83, open as of 2026-09-23; author's own workaround suggestion is to switch to parallel-hashmap)
- insert()/erase() can invalidate references and pointers to stored values, unlike std::unordered_map where references survive unless a rehash occurs
- Default integer hash does bit-mixing to dodge sequential-key pathologies; a user-supplied hash with similar low-order bits across keys needs the SPP_MIX_HASH macro or collisions increase
- Copy construction/assignment is slow relative to the baseline (per verification caveats)

**Status:** Actively maintained (last commit 2026-09-19, BSD-3-Clause, 1311 stars, not a fork or archived) but the author's own README now steers users to greg7mdp/parallel-hashmap for any C++11+ project, calling it a better speed/memory trade-off than sparsepp.

[repo](https://github.com/greg7mdp/sparsepp) · [benchmark](https://martin.ankerl.com/2022/08/27/hashmap-bench-01/)

#### tsl::hopscotch_map (Tessil/hopscotch-map)  `C++`  `MIT`  `active`  `Tier A`

Header-only C++17 hopscotch-hashing hash map/set, faster than std::unordered_map with dense_hash_map-like speed.

**Beats:** std::unordered_map — Against std::unordered_map (libstdc++, Clang 5.0, -O3 -march=native -DNDEBUG, Intel i5-5200u/8GB RAM/Linux 4.11), the author's benchmark (200K-3M entries, int64 identity-hash and 15/50-char string keys) found hopscotch_map faster in every measured case: 1.08-2.67x on insert, 1.51-5.47x on successful/unsuccessful lookup, 1.55-10.1x on erase, and 4.6-13.2x on iteration.

**How:** Hopscotch hashing keeps every key within a fixed-size neighborhood (bitmap) of its ideal bucket, so a lookup only scans a small, cache-local run of buckets instead of following a chain; neighborhoods are rearranged on insert to preserve this bound. Elements are stored contiguously via open addressing, avoiding the per-node heap allocation std::unordered_map's separate chaining requires. The default power-of-two growth policy replaces modulo with a bitmask; a prime growth policy (_pg variants) is offered when the hash has weak low-bit entropy, at some speed cost. Optional hash caching (StoreHash) and passing a precalculated hash into find() avoid recomputing hashes on rehash/lookup.

**Use it when:**
- Read-heavy workloads (successful/unsuccessful lookup, iteration) with int64 or short-to-medium string keys, in the low-hundred-thousands to low-millions element range (benchmarked at 200K-3M).
- You want a near-drop-in replacement for std::unordered_map without adopting its chained-bucket allocation overhead, and can require C++17 and header-only integration.
- You want dense_hash_map-like throughput but without reserving sentinel/deleted-key values or accepting dense_hash_map's more restrictive API.
- You control the hash function well enough to avoid low-bit collisions, or are willing to switch to the _pg (prime growth) variant if you can't.
- You need optional worst-case DoS resistance (bhopscotch_map/set) for keys that are LessThanComparable, at a throughput cost.

**Skip it when:**
- Identity or otherwise weak hash functions on adversarial/clustered-bit-pattern keys with the default power-of-two policy: the independent Ankerl 2022 suite reports hopscotch timing out on random insert/erase with identity std::hash.
- Code that depends on std::unordered_map's iterator/reference stability across insert: hopscotch invalidates all iterators and references on any insert (only erase preserves them).
- Move-only value types whose move constructor isn't noexcept: not supported, since rehash needs the nothrow guarantee under open addressing.
- Code relying on bucket-introspection methods (bucket(), bucket_size(), etc.): not implemented.
- Inserting implicitly-converted move-only pairs (e.g. a derived-class unique_ptr into a base-class-keyed map) via the generic insert(P&&) overload: open bug #66, a regression after PR #63, still open as of 2026-09-23.

**Integration:** header-only · none for the library; Boost Test is needed only to build the test suite · C++17-compliant compiler · architecture-agnostic; the headers read include only standard library headers, no SIMD intrinsics or platform-specific code observed

**Vs siblings:** Pick hopscotch_map over robin_map/ska/emhash when you want the bhopscotch_map DoS-resistant option or heterogeneous lookups with dense_hash_map-like throughput and lower memory than dense_hash_map; robin-hood-style siblings (robin_map, ska::flat_hash_map, emhash) tend to edge it out on raw insert throughput in independent benchmarks.

**Gotchas:**
- Insert/emplace invalidate all iterators and references, unlike std::unordered_map's node-based stability; only erase is safe.
- it->second is not assignable; iterators dereference to const std::pair, so mutate via it.value() = ...
- Default growth policy is power-of-two; a hash with poor low-bit entropy causes heavy collisions — check overflow_size() and switch to the _pg (prime) variant if it's nonzero.
- Open issue #66: insert(P&&) is broken for implicitly-convertible move-only pairs (e.g. derived-to-base unique_ptr), a regression introduced after PR #63 and unresolved at time of writing.

**Status:** Actively maintained (last commit 2025-11-02) under MIT; small and header-only enough to vendor, but requires C++17 and currently has one open correctness bug (#66) in a move-only insert overload.

[repo](https://github.com/Tessil/hopscotch-map) · [benchmark](https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html)

#### tsl::ordered_map (Tessil/ordered-map)  `C++`  `MIT`  `active`  `Tier A`

Insertion-order-preserving hash map/set beating std::unordered_map on inserts, misses, and iteration.

**Beats:** std::unordered_map — Author-run benchmark (Tessil hash-table-shootout, tsl::ordered_map v0.4) on an Intel i5-5200u/8GB RAM/Linux 4.11 with Clang 5.0 -O3 -march=native -DNDEBUG, against libstdc++'s std::unordered_map: inserts 1.12-2.87x faster, unsuccessful lookups 2.34-4.40x faster, iteration 22-45x faster, successful lookups mixed at 0.55-2.02x, and about 84MB vs 126MB memory at 3M int64 entries.

**How:** Open addressing with linear robin hood probing plus backward shift deletion keeps probe sequences short and avoids tombstones, which speeds inserts and unsuccessful lookups relative to libstdc++'s node-based std::unordered_map. Storing values contiguously in a deque/vector instead of scattered nodes gives cache-friendly, pointer-chasing-free iteration, which is where the largest measured gains appear (22-45x). The tradeoff is an O(bucket_count) ordered erase() unless the O(1) pop_back()/unordered_erase() variants are used, which break insertion order.

**Use it when:**
- Insert- and miss-heavy workloads on int64 or short/medium string keys, where 1.12-2.87x (inserts) and 2.34-4.40x (unsuccessful lookups) gains were measured
- Need for insertion-order iteration (config/JSON-like objects, ordered dictionaries) that std::unordered_map cannot provide at all
- Iteration-heavy code paths (serialization, dumping, full-container walks) - 22-45x faster than std::unordered_map in the cited shootout
- Memory-constrained multi-million-entry containers (about 84MB vs 126MB at 3M int64 entries in the cited benchmark)
- C++11-only toolchains that need a header-only, dependency-free drop-in with no build step

**Skip it when:**
- Erase-heavy workloads that must preserve order: erase() is O(bucket_count); only unordered_erase()/pop_back() are O(1) and they break ordering
- Read-heavy workloads dominated by successful lookups: measured only 0.55-2.02x vs std::unordered_map, sometimes slower (e.g. read_random_shuffle_range)
- Code relying on bucket-level APIs (bucket(), bucket_size(), ...): not supported
- Decisions needing current-version confidence: the cited numbers are from v0.4 (2017) on an old i5-5200u laptop, not part of the newer Ankerl 2022 suite, and ordered_map is absent from the benchmark page's main charts
- Containers needing more than 2^32-1 values without raising the IndexType template parameter

**Integration:** header-only · none (Boost Test only needed to build the test suite) · C++11 (tested with GCC 4.8.4, Clang 3.5.0, Visual Studio 2015); C++20 required only for the optional module build · any (portable C++11, no SIMD/arch-specific requirement)

**Vs siblings:** Pick tsl::ordered_map over the other cataloged std::unordered_map beaters (hopscotch_map, robin_map, ska flat/bytell, emhash, sparsepp, rigtorp/HashMap, libcuckoo, Verstable, dense_hash_map) when insertion-order iteration is a hard requirement - it is the only one of these that preserves order. Those siblings generally win on raw insert/lookup throughput but give no ordering guarantee at all.

**Gotchas:**
- erase() is O(bucket_count); use unordered_erase()/pop_back() for O(1) removal, but this breaks insertion order
- Iterators expose const std::pair<Key,T>; modify values through it.value(), not it->second
- operator==/!= are order-dependent: two containers with identical key/value pairs inserted in different order compare unequal
- Default IndexType caps the container at 2,294,967,295 (2^32-1) values; raise the IndexType template parameter for larger sizes

**Status:** Active (last commit 2026-06-13, CI passing, MIT-licensed); header-only form makes it trivial to vendor and keep working even if upstream maintenance later lapses.

[repo](https://github.com/Tessil/ordered-map) · [benchmark](https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html)

#### tsl::robin_map (Tessil/robin-map)  `C++`  `MIT`  `active`  `Tier A`

Header-only robin hood open-addressing hash map/set beating std::unordered_map on insert, lookup, erase, and iteration.

**Beats:** std::unordered_map — Author-run benchmark (Clang 5.0, -O3 -march=native -DNDEBUG; Intel i5-5200u, 8GB RAM, Linux 4.11 x64; libstdc++) across 200K-3M entries with int64_t and 15/50-char string keys found robin_map faster than std::unordered_map in every measured case: inserts 1.08-3.63x, successful lookups 1.55-5.34x, unsuccessful lookups 1.66-6.57x, erase 1.58-13.5x, iteration 2.6-5.3x. The independent Ankerl 2022 suite puts the geometric-mean advantage around 2.4x, but in that same suite robin_map times out on random insert/erase with an identity std::hash and iterates slower (0.80-0.92x) than std::unordered_map.

**How:** Robin hood hashing with linear probing keeps entries close to their ideal bucket, so lookups scan a short, cache-resident run instead of chasing pointers through separate chaining nodes. Erase uses backward-shift deletion (no tombstones), which keeps probe sequences short after deletes. Optional per-entry hash caching (StoreHash) and a precalculated_hash parameter let callers skip recomputing hashes on rehash or lookup when the hash or key-equality function is expensive.

**Use it when:**
- int64_t or other cheap-to-hash keys where you supply a decent hash (not the identity std::hash) and want faster inserts/lookups/erases than std::unordered_map
- std::string keys, especially short (SSO-sized) strings, where robin_map's automatic hash caching gives a large insertion win
- workloads dominated by successful/unsuccessful lookups or full-table iteration at sizes from ~200K to several million elements
- code that needs heterogeneous lookup (find by a different-but-comparable type) or binary serialize/deserialize of the table
- environments where -fno-exceptions or TSL_NO_EXCEPTIONS is desired; the library supports exception-free builds via std::terminate

**Skip it when:**
- pointer/reference/iterator stability across modification matters: open addressing invalidates all of them on any insert, erase, or rehash, unlike std::unordered_map
- keys hashed with the default identity-like std::hash for integers combined with the default power-of-two growth policy: linear inserts can trigger exponential storage growth (GH issue #39); switch to robin_pg_map/robin_pg_set or supply a better hash
- code that erases elements while iterating and depends on visiting each element exactly once: backward-shift deletion can revisit an already-seen element (GH issue #20, open, no fix planned)
- memory-constrained int64 workloads at large scale: at 3M entries the author's own CSV shows ~202MB for robin_map vs ~126MB for std::unordered_map (~1.6x)
- key/value types that are not swappable or not copy/move constructible, or where you rely on std::unordered_map's bucket-inspection API (bucket(), bucket_size(), etc.), which robin_map omits

**Integration:** header-only · none for the library; Boost Test only needed to build the test suite · C++17 (README: "should work with any C++17 standard-compliant compiler") · portable C++17, no SIMD or arch-specific intrinsics in the source; CI covers Linux and macOS (GCC and Clang) and Windows (MSVC via Visual Studio 2025, x64 and x86)

**Vs siblings:** Prefer tsl::robin_map over ska::flat_hash_map/bytell_hash_map or sparsepp when you want an actively maintained, documented library with heterogeneous lookup, binary serialization, and a built-in prime-growth fallback (robin_pg_map) for weak hashes. Prefer tsl::hopscotch_map instead when erase-heavy iteration or memory density at high load factor matters more than raw lookup/insert throughput, since hopscotch avoids robin-map's backward-shift erase cost and identity-hash growth pathology.

**Gotchas:**
- Any insert, erase, or rehash invalidates all iterators, pointers, and references into the table (stricter than std::unordered_map).
- Default power-of-two growth policy + a poor/identity hash (common for std::hash<integral>) can make a linear insertion sequence blow up storage exponentially; use robin_pg_map/robin_pg_set or a stronger hash.
- erase(iterator) walks forward to the next nonempty bucket to return a valid iterator, which is O(expensive) at low load factor; use void erase_fast(iterator) when you don't need the returned iterator.
- Iterating while erasing can visit one element twice due to backward-shift deletion wrap-around; open upstream issue (#20) since 2019, maintainer's stance is 'that's the way it is'.

**Status:** Actively maintained (last commit 2026-06-13, 1508 stars, CI green across GCC/Clang/MSVC), MIT-licensed and header-only, so it is trivially vendorable even if upstream development ever stopped.

[repo](https://github.com/Tessil/robin-map) · [benchmark](https://tessil.github.io/2016/08/29/benchmark-hopscotch-map.html)

#### Verstable  `C`  `MIT`  `stale`  `Tier A`

Single-header C hash table beating std::unordered_map on lookups, erasures, and iteration; insertion only average.

**Beats:** std::unordered_map — On the author's own interactive benchmark (GCC 13.2.0 via MinGW-w64, -O3 -DNDEBUG, AMD Ryzen 7 5800H at 90% locked frequency, libstdc++'s std::unordered_map as baseline, across 32-bit int, 64-bit-int/large-value, and string-key workloads), the page states std::unordered_map is far slower than most open-addressing tables except at looking up existing keys, and at least an order of magnitude slower at iteration; Verstable is described as having extremely fast lookups and erasures of nonexisting keys, iteration beaten only by boost::unordered_flat_map, emilib2, and contiguous-storage tables (and faster than absl::flat_hash_map on iteration), but 'only average' insertion speed. Results are shown as interactive charts rather than a numeric table.

**How:** It's open addressing with quadratic probing, but colliding keys that hash to the same 'home bucket' are linked into a chain via an 11-bit displacement value; a 1-bit flag keeps each chain rooted at its home bucket by evicting non-belonging occupants on insert. This chain metadata, plus a 4-bit hash-code fragment per bucket, lives in a separate uint16_t array instead of alongside the key/value, so lookups can skip most non-matching keys without touching the buckets array or calling the comparison function, and iteration walks a compact metadata array rather than sparse, cache-missing buckets. Deletion and insertion move at most one existing key and require no tombstones. The author describes it as a hybrid of open addressing and separate chaining, related to Malte Skarupke's Bytell table and classic coalesced hashing.

**Use it when:**
- C code that needs a generic, type-safe hash map/set without hand-rolling one, or C++ code that can call a C API via extern "C"
- Lookup- and iteration-heavy workloads, including lookups of nonexisting keys, where std::unordered_map's node-based layout causes cache misses
- Large keys/values or expensive hash/compare functions, since insert/delete move at most one existing key instead of shifting many (unlike Robin Hood schemes)
- High load factors, since the design is described as largely impervious to load factor for lookup speed
- Willing to vendor a single header and accept a non-STL API in exchange for speed

**Skip it when:**
- Need a true drop-in std::unordered_map replacement with C++ container semantics, allocator/exception conventions, or STL iterator guarantees
- Insertion throughput is the dominant cost: the benchmark author calls Verstable's insertion 'only average', and it sits behind absl/boost on raw speed generally
- Keys with a weak, low-entropy, or attacker-influenced hash function: a bucket's collision chain is capped at ~2,048 keys, and hitting that repeatedly makes the table grow until it exhausts memory instead of degrading to a linear scan
- Targeting an FPU-less embedded platform: the default max-load-factor check uses floating point (open issue #23 asks for an integer-only option)
- Need active upstream maintenance guarantees: last commit 2025-05-06, tagged 'stale' by the catalog

**Integration:** header-only · none (C standard library only; malloc/free by default, both overridable) · C99 (with explicit HASH_FN/CMPR_FN); full vt_*-generic macro API requires C11 _Generic; tested under GCC, Clang, MinGW, and MSVC; usable from C++ via extern "C" · not documented as architecture-restricted (portable C, no SIMD intrinsics in the header); an open issue notes the floating-point load-factor check is awkward on FPU-less embedded hardware

**Vs siblings:** Pick Verstable when the code is C (or C++ that can bind to a C ABI) and you want a single-header, type-safe table with tombstone-free deletion and strong lookup/iteration speed; the sibling C++-only tables (ska::flat_hash_map/bytell_hash_map, tsl::robin_map, tsl::hopscotch_map) use similar open-addressing ideas but require a C++ compiler, and emhash/emilib2/google::dense_hash_map generally edge it out on raw insertion or peak throughput if a C-only API isn't a requirement.

**Gotchas:**
- Insert, get_or_insert, erase, erase_itr, reserve, and shrink invalidate all existing iterators; use erase_itr's return value to keep iterating while deleting
- No RAII: forgetting to call NAME_cleanup leaks the table's memory (a reported 'stuck insert' bug turned out to be missing cleanup across repeated runs, per issue #22)
- A degenerate hash function (near-constant output) can make a bucket chain exceed its ~2,048-key limit, causing the table to keep doubling until allocation fails rather than falling back to a slow linear scan
- Custom allocators need CTX_TY plus matching MALLOC_FN/FREE_FN signatures that take a size and context pointer, not a drop-in std::allocator interface

**Status:** Maintenance status is 'stale' (last commit 2025-05-06), but it's MIT-licensed and a single vendorable header, so freezing at the current commit carries little risk; the bigger adoption cost is its non-STL API rather than staleness.

[repo](https://github.com/JacksonAllan/Verstable) · [benchmark](https://jacksonallan.github.io/c_cpp_hash_tables_benchmark/)

#### libcuckoo (cuckoohash_map, efficient/libcuckoo)  `C++`  `Apache-2.0`  `active`  `Tier B`

Header-only concurrent cuckoo hash map with per-bucket locks; beats std::unordered_map only under real multi-core contention.

**Beats:** std::unordered_map — On a 16-core machine the EuroSys'14 paper reports ~40M inserts/sec and ~70M lookups/sec; Figure 1 (4-core Intel i7-4770 Haswell, 120M 8-byte-key/8-byte-value pairs, 1:1 read:write) places libcuckoo well above C++11 std::unordered_map, but the only explicit numeric multiplier given in text is 'up to 2.5x' vs Intel TBB concurrent_hash_map — the std::unordered_map comparison is visual-only in the figure, and the paper treats std::unordered_map as a single-writer table (run under a global or TSX lock), so the measured win is multi-core scalability, not single-threaded op speed.

**How:** Uses cuckoo hashing: each key maps to 2 candidate buckets of SLOT_PER_BUCKET=4 slots, so a lookup touches at most 2 cache lines and displacement chains stay short. Concurrency comes from fine-grained per-bucket spinlocks combined with a resize counter/versioning scheme (the EuroSys'14 optimistic-locking design), letting many writers and readers operate on different buckets simultaneously instead of serializing on one table-wide lock the way std::unordered_map does under concurrent access.

**Use it when:**
- Multi-threaded workloads with genuine concurrent inserts and lookups across several cores (paper measures gains at 4-16 cores, 1:1 read:write and mixed operation mixes).
- Fixed-shape, trivially hashable keys/values (paper benchmark uses 8-byte key/8-byte value, ~120M entries) where the 2-cache-line cuckoo probe pays off.
- Code that can adopt a non-STL API (out-parameter find, functor-based update/upsert) instead of std::unordered_map's interface.
- Workloads that need occasional safe bulk iteration via locked_table(), not concurrent iteration.
- C++11-capable toolchain on Linux/macOS; header-only, so easy to vendor into a build with no link step.

**Skip it when:**
- Single-threaded or low-contention use: the per-bucket spinlock/version machinery is pure overhead with no payoff.
- Memory-constrained settings: users report roughly 3x higher RSS than std::unordered_map for long-key/int-value maps at ~42M entries (issues #134, #136).
- Many reader threads hammering the same hot keys: open issue #159 reports spinlock contention degrading badly past ~16-64 threads, since even find() takes the bucket spinlock (no shared/exclusive mode).
- Code relying on std::unordered_map's free iterators or erase-while-iterating: normal access has no standalone iterators, only locked_table() does, and that locks the entire table.
- Scaling requirements beyond what's measured: the peer-reviewed numbers stop at 16 cores, and at least one independent report (issue #152) found scalability collapsing beyond ~16 threads in their own workload.

**Integration:** header-only · none (self-contained headers: cuckoohash_map.hh, bucket_container.hh, cuckoohash_config.hh, cuckoohash_util.hh; optional C wrapper in libcuckoo-c/) · C++11; clang++ >= 3.3 or g++ >= 4.8 per README (latest versions recommended for atomics support); CMake >= 3.1.0 needed only to build tests/examples · Tested on macOS >= 10.8 and Ubuntu >= 12.04 (README); no stated architecture restriction, plain std::atomic used, no SIMD/intrinsics observed in the header; Windows build status is an open/unclear question (issue #62)

**Vs siblings:** All catalogued siblings (emhash, dense_hash_map, rigtorp/HashMap, Verstable, sparsepp, hopscotch/ordered/robin-map, ska::flat_hash_map/bytell_hash_map) are single-threaded tables tuned for single-core cache behavior and are not safe for concurrent access without an external lock. Pick libcuckoo over any of them only when multiple threads genuinely insert into and look up the same map concurrently.

**Gotchas:**
- find(key, val) (bool-returning, out-parameter) and find(key) (returns mapped_type or throws std::out_of_range) are different overloads; there is no iterator/end() sentinel on the normal concurrent path.
- Automatic expansion throws load_factor_too_low if load factor falls below minimum_load_factor() (default 0.05) — a weak hash function or adversarial key set can trigger this.
- Bulk/STL-style iteration requires locked_table(), which takes an exclusive lock over the whole table for as long as it's held, blocking every other thread.
- Reported ~3x memory overhead vs std::unordered_map for 8-byte-key/4-byte-value workloads at scale (issues #134, #136); size capacity planning accordingly.

**Status:** Active (last commit 2026-07-31, 1747 stars); Apache-2.0, header-only, and small enough to vendor directly into a project (usability: copyable).

[repo](https://github.com/efficient/libcuckoo) · [benchmark](https://www.cs.princeton.edu/~mfreed/docs/cuckoo-eurosys14.pdf)

### number-parsing-formatting

#### Boost.Charconv  `C++`  `BSL-1.0`  `active`  `Tier A`

Portable std::to_chars/from_chars reimplementation for pre-C++17 toolchains and MSVC, winning there and near-parity on GCC.

**Beats:** std::to_chars, std::from_chars — Maintainer-run benchmarks (test/STL_benchmark.cpp) on Linux GCC 13.1/libstdc++, Windows MSVC 14.3, and macOS ARM (M1 Pro) GCC 13.2 score Boost.Charconv against std::to_chars/from_chars, itself scored against std::printf/std::strtoX; results run from near-parity to ~1.3x in most cells, with the clearest wins on MSVC float/double from_chars (~2.0x/~4.2x) and Linux uint32_t from_chars (~1.3x), and a few Windows/ARM cells (double/uint64_t to_chars, ARM from_chars) slightly slower than std.

**How:** to_chars for floats uses the Dragonbox shortest-round-trip algorithm (detail/dragonbox/dragonbox.hpp, floff.hpp for fixed format); from_chars for floats uses Daniel Lemire's fast_float parser (detail/fast_float/); 80-bit/128-bit long double and __float128 go through Ryu's generic 128-bit path (detail/ryu/ryu_generic_128.hpp); integer to_chars uses precomputed digit-count/significand lookup tables (integer_search_trees.hpp, significand_tables.hpp) for branch-light itoa. These are the same published algorithms most std::to_chars/from_chars implementations already use, so gains show up mainly where the target stdlib (MSVC's) hasn't adopted them as aggressively.

**Use it when:**
- Targeting MSVC and needing float/double from_chars roughly 2-4x faster than std::from_chars (the largest measured win)
- Building for a C++11/14 toolchain (GCC 5+, Clang 3.8+, MSVC 2015+) that lacks <charconv> entirely
- Need to_chars/from_chars for __float128 or 80-bit long double, which std <charconv> doesn't cover
- Already depend on Boost and want one to_chars/from_chars-shaped API across compilers instead of per-compiler fallbacks
- High-volume uint32_t from_chars parsing on Linux/GCC, where Boost measures ~1.3x over std::from_chars

**Skip it when:**
- Already on a recent GCC/libstdc++ or Clang target, where most cells are near parity (0.97-1.0x) with std::to_chars/from_chars
- Want a true header-only drop-in: charconv ships src/to_chars.cpp and src/from_chars.cpp as separately-compiled sources, plus Boost.Assert/Config/Core as dependencies
- Parsing untrusted long double/__float128 strings over 1024 bytes, the one documented path where it allocates
- Need an independent (non-maintainer) benchmark; the published numbers are run and maintained by the library's own authors
- On Windows double/uint64_t to_chars, where Boost measured very slightly slower than std (15.26 vs 15.77; 2.06 vs 2.10)

**Integration:** static lib | shared lib (compiled sources in src/; not header-only) · Boost.Assert, Boost.Config, Boost.Core; optional libquadmath for __float128/std::float128_t · C++11 (GCC 5+, Clang 3.8+, MSVC 2015 / 19.24+, NVCC 12.8+ for optional CUDA); constexpr paths need C++14 · x86/x86_64/ARM on Linux, macOS, Windows; libquadmath path limited to Linux x86/x86_64/PPC64/IA64; partial CUDA and SYCL device support

**Vs siblings:** Pick Boost.Charconv when you need an actual std::to_chars/from_chars-compatible surface (same enums, same result types) on a pre-C++17 toolchain, MSVC, or for __float128/long double, not a different API or output format. Pick c4core, rigtorp/CharConv, or jeaiii/itoa instead when you want larger, unambiguous wins on a modern GCC/Linux stack and don't need std-API compatibility.

**Gotchas:**
- Parsing a long double/__float128 string longer than 1024 bytes is the one documented path that allocates, despite the library's non-allocating claim elsewhere
- The fixed-format float path (floff, Dragonbox-based) had buffer-overflow and internal-overflow bugs (issues #186, #190) fixed in 2024; a to_chars-with-precision correctness bug (#158) was also fixed; issue #166 (more to_chars problems) was still open as of the last check
- __float128/std::float128_t support needs libquadmath and only builds on Linux x86/x86_64/PPC64/IA64
- b2/CMake auto-detect and link libquadmath when available; other build systems must define BOOST_CHARCONV_HAS_QUADMATH and link it manually

**Status:** Actively maintained (last master commit 2026-08-13, CI/fuzzing/codecov all wired up); BSL-1.0 licensed and copyable, but as a Boost library it pulls in Boost.Assert/Config/Core and a compiled component rather than being a single vendorable header.

[repo](https://github.com/boostorg/charconv) · [benchmark](https://github.com/boostorg/charconv/blob/master/doc/charconv/benchmarks.adoc)

#### fast_double_parser  `C++`  `Apache-2.0`  `stale`  `Tier A`

Header-only C++11 double parser using the Eisel-Lemire algorithm; 2.5-9.5x strtod throughput, superseded by fast_float.

**Beats:** std::stod (strtod) — Benchmarked against strtod_l (C locale) on Apple clang 11.0.0 / Intel Core i7-7700K: 460.64 MB/s vs strtod's 186.90 MB/s (~2.5x) parsing random doubles in [0,1), and 662.01 MB/s vs 69.73 MB/s (~9.5x) parsing the canada.json real-world coordinate dataset; the README's '4x' headline sits between these two workload-specific ratios. The same run also reports abseil and double-conversion figures, both slower than fast_double_parser on both workloads.

**How:** Implements the Eisel-Lemire algorithm (Lemire, "Number Parsing at a Gigabyte per Second," arXiv:2101.11408): accumulate up to 19 significant digits into a 64-bit integer, then multiply it by a precomputed 64-bit truncated mantissa for the decimal exponent using a 128-bit full multiplication (hardware `_umul128`/`__uint128_t`, with an emulated fallback) to directly assemble the correctly-rounded IEEE754 bit pattern. This skips strtod's general parsing path entirely and falls back to the platform's locale-independent strtod_l/_strtod_l only for the rare >19-significant-digit or ambiguous-rounding cases.

**Use it when:**
- Hot-path parsing of many decimal doubles from files/network (GeoJSON, CSV, log lines) where strtod is a measured bottleneck
- JSON-shaped numeric literals only (no hex floats, no locale decimal comma)
- Header-only vendoring is acceptable (drop include/fast_double_parser.h into the build)
- C++11-only toolchains that can't adopt fast_float's newer API/build requirements
- Throughput-bound batch parsing (MB/s) rather than a single latency-critical call

**Skip it when:**
- Any new project — the README itself tells users to adopt fast_float instead (more grammar support, same speed, wider adoption/testing)
- Need std::from_chars-style explicit begin/end pointers rather than a null/non-numeric-terminated C string — use fast_float
- Need 32-bit float parsing — this library is double-only
- Need hex floats, NaN/Infinity, or non-JSON strtod grammar (e.g. leading '+', "0x1p3", leading zeros like "01")
- Repo is stale (last commit 2025-05-27) with only 2 open issues (macro hygiene, power-range tightening) and no active feature work

**Integration:** header-only · none (the benchmark target pulls in abseil and double-conversion, but the library itself has zero deps) · C++11 (CMakeLists sets CMAKE_CXX_STANDARD 11); MSVC, GCC, and Clang all supported · x86-64, ARM64, and 32-bit (native _umul128/__uint128_t 128-bit multiply where available, emulated fallback otherwise); Windows/Linux/macOS plus a stringstream-based strtod workaround for Cygwin/MSYS2/Solaris

**Vs siblings:** No catalogued sibling targets double parsing (they cover to_chars/from_chars formatting or integer conversions); the real alternative is its own successor fast_float. Pick fast_double_parser only when a C++11-only toolchain or an existing call site already depends on its exact pointer-in/pointer-out API — otherwise fast_float matches its speed with a std::from_chars-style API and broader (non-JSON-restricted) grammar support.

**Gotchas:**
- Global-namespace macros (WARN_UNUSED, really_inline, unlikely) defined in the header are never #undef'd and can collide with same-named macros pulled in transitively from other libraries (issue #66); this bit a real user combining it with Microsoft LightGBM, which itself vendors this same library
- Rejects some strtod-valid-but-JSON-invalid forms: leading zeros ("01"), a bare trailing decimal point ("1."), hex floats, and never produces NaN/Infinity
- Falls back to platform strtod_l for any number with >19 significant digits, so very long decimal mantissas get strtod's speed rather than the fast path
- Assumes the FPU rounding mode is round-to-nearest (FE_TONEAREST); behavior under other rounding modes is unverified

**Status:** Maintenance status is stale — last commit 2025-05-27, no active feature development, and the maintainer's own README recommends migrating to fast_float — but it's a single small header under a dual Apache-2.0/Boost-1.0 license, cheap to vendor and freeze if a project already depends on its exact API.

[repo](https://github.com/lemire/fast_double_parser) · [benchmark](https://github.com/lemire/fast_double_parser/blob/master/README.md)

### ordered-maps-trees

#### fast-containers (SIMD/hugepage B+Tree)  `C++`  `BSD-3-Clause`  `active`  `Tier A`

Header-only C++23 B+tree with SIMD search and hugepage allocators, 2-5x faster than std::map on large trees.

**Beats:** std::map — On an isolated core of an AMD Ryzen 9 5950X (Linux 6.16.3, Clang Release build with -O3 -march=haswell -mavx2 -mfma -flto=thin), the repo's own RDTSC-timed benchmark shows the SIMD+hugepage btree beating std::map by roughly 2.1-4.8x on P50/P99.9 insert/find/erase at 10M elements with 8-byte keys and 32B or 256B values; at 10K elements the advantage shrinks and std::map wins ERASE P99.9 with 256B values (213.6ns vs 245.7ns).

**How:** Fixed-size leaf/internal nodes (heuristically sized to ~1-2KB, 16-32 cache lines) replace the per-node pointer-chasing of a red-black tree. Node search uses AVX2 SIMD linear scans (`SearchMode::SIMD`) over a dense sorted array (`dense_map`) instead of branchy binary search. A pooling `HugePageAllocator` backs node storage with 2MB hugepages, cutting TLB misses and making allocation near-free compared to the default allocator; the README calls this 'the single most important optimization,' giving a 2-3x speedup on its own.

**Use it when:**
- Ordered int64-keyed maps with 32-256 byte values at large scale (roughly 1M-10M+ elements) where TLB misses and allocator overhead dominate runtime
- You need both P50 and P99.9 latency wins over std::map for insert/find/erase, not just throughput
- You control an x86-64 Linux environment with AVX2 (Haswell/Excavator or newer) and can configure OS hugepages
- You're willing to tune node size, SearchMode, and allocator per key/value size instead of relying on one default
- You're also considering Abseil's btree: this implementation beats absl+hugepages by 20-135% in the repo's own benchmarks

**Skip it when:**
- Trees under roughly 10K elements: std::map becomes competitive and even wins some tail-latency cases (e.g. ERASE P99.9 with 256B values: 213.6ns vs 245.7ns)
- Non-x86-64 or non-Linux targets — SIMD paths and RDTSC timing are x86-64-specific, and the README states Windows is untested
- Workloads relying on std::map's pointer/iterator stability across mutations; the header documents that some operations invalidate all iterators
- Environments where OS hugepages can't be configured/administered — losing hugepages removes most of the measured advantage
- Risk-averse adoption: single-author, explicitly AI-agent-assisted, actively-changing work-in-progress with self-reported, not independently reproduced benchmarks

**Integration:** header-only · none for the library itself; tests/benchmarks pull in Abseil, Google Benchmark, Catch2, lyra, unordered_dense, and a histograms library as git submodules · C++23, GCC 14+ or Clang 19+, CMake 3.30+ · x86-64 with AVX2 (Intel Haswell 2013+ / AMD Excavator 2015+); built and tested on Linux only

**Vs siblings:** Pick this over tlx::btree_map or boost::container::flat_map/flat_set when the workload is specifically very large (multi-million element), int64-keyed trees on x86-64 Linux and hugepages are available to configure; its P99.9 gains at 10M elements are larger than tlx's reported multiset comparisons and target a size range boost's flat_set (best at 2-256 elements) doesn't cover. Prefer tlx or boost instead for portability, small-to-mid-size trees, or a longer track record than a single-author work-in-progress.

**Gotchas:**
- Header docs state some operations invalidate all iterators — no red-black-tree-style iterator/pointer stability like std::map
- A closed bug (issue #47) found incorrect SIMD comparison semantics for composite and unsigned key types — fixed, but signals SIMD comparator correctness needs care for non-trivial key types
- The hugepage allocator needs OS-level hugepage configuration; without it the library is still faster than std::map but by a much smaller margin than the headline numbers
- The benchmarked 'winner' configuration (SIMD search + hugepage allocator, specific leaf/internal node sizes) is one tuned instantiation — other node-size/SearchMode combinations are meaningfully slower

**Status:** Actively developed (last commit 2026-01-06, all filed issues closed) but explicitly a single-author work-in-progress built with heavy AI-agent assistance; BSD-3-Clause and header-only make it cheap to vendor, but expect API and behavior churn before treating it as stable.

[repo](https://github.com/kressler/fast-containers) · [benchmark](https://github.com/kressler/fast-containers/blob/main/results/btree_benchmark_results.md)

#### tlx::btree_map / btree_set / btree_multimap (STX B+Tree lineage)  `C++`  `BSL-1.0`  `stale`  `Tier A`

Header-only B+ tree implementing STL's map/set/multimap/multiset; beats libstdc++'s red-black tree at large n.

**Beats:** std::map, std::multiset — Evidence tier A: the author's own STX-btree/tlx speedtest (code public in tests/container/btree_speedtest.cpp) measured random-integer multiset insert-only, insert+find+erase, and find-only workloads at n from 125 to tens of millions against libstdc++'s std::multiset/std::multimap (red-black tree). Per the benchmark page (fetched this session): the 2007 run (g++ 4.1.2, -O3 -fomit-frame-pointer, Pentium 4 3.2GHz) showed the red-black tree taking almost 2x as long as a 32-slot B+ tree above roughly 1,024,000 items; the 2011/2013 reruns (gcc 4.4.5/4.5.0, Core i7 9xx, -O3 with -fomit-frame-pointer or -march=native) show the same divergence starting near 100,000 items. The input record additionally reports a 2019 in-repo results PDF (btree_speedtest_results.pdf, not opened by me this session) showing tlx::btree_multiset roughly 3x faster than std::multiset by n=2^26, with no hardware/compiler stated for that run.

**How:** Leaf and inner nodes are sized by btree_default_traits to hold as many keys as fit in roughly a 256-byte block, so a comparison step touches one cache line instead of the one-key-per-node layout of a red-black tree. Leaves store keys and their associated data in two separate parallel arrays rather than an array of key/value pairs, and descent does an in-node search over a wide node instead of following per-key left/right/parent pointers. Net effect: fewer pointer-chasing cache misses per operation at large n, at the cost of more in-node comparisons per level.

**Use it when:**
- Large (roughly >100k-1M+ element) in-memory ordered map/set/multiset/multimap of cheaply-comparable keys (e.g. integers) where insert, find and erase are all exercised and cache-miss-bound traversal dominates.
- You want an STL-like drop-in-ish replacement for std::map/std::set without taking on SIMD or hugepage requirements.
- You need sorted-order range queries (lower_bound/upper_bound/equal_range) alongside point lookups; B+ tree leaves are linked so range scans stay cheap.
- You can vendor a small BSL-1.0 header (or the wider tlx repo) instead of a heavier dependency.
- Your workload includes bulk-loading a pre-sorted range into an empty container (bulk_load()).

**Skip it when:**
- You rely on std::map's pointer/reference/iterator stability across insert/erase; tlx's B+ tree gives no such guarantee.
- You need C++17/20 map features: emplace, try_emplace, insert_or_assign, extract, merge, or node_type/heterogeneous lookup; none appear in btree_map.hpp.
- You need move construction/assignment on the container itself; only a copy constructor, copy assignment, and swap() are defined in the header I read.
- Small containers (tens of elements or fewer); none of the record's benchmarks show a win below tens of thousands of items, and boost::flat_set/flat_map targets exactly that small-size regime.
- You need erase(first,last) or lock-free/concurrent access; range-erase is unimplemented (only aborts under a debug-only macro) and no synchronization is documented or visible in the header.

**Integration:** header-only (for the btree containers themselves; the wider tlx repo also builds a small static/shared libtlx for unrelated modules like digest/string helpers, but tlx/container/btree*.hpp are pure templates with no matching .cpp in LIBTLX_SOURCES) · none for normal insert/find/erase use (README states zero external dependencies; btree.hpp only includes <algorithm> <cassert> <cstddef> <functional> <iterator> <memory> <utility> and tlx/die/core.hpp). Caveat: verify() and the self_verify trait call tlx_die_unless() -> die_with_message(), which is declared in tlx/die/core.hpp but defined only in tlx/die/core.cpp, so using invariant verification requires linking libtlx or compiling that one file yourself. · C++11 minimum. Root CMakeLists.txt auto-probes compiler flags, preferring -std=c++20 and falling back through c++17/c++14/c++11/c++0x. CI (.github/workflows/cmake.yml) builds with GCC 7.5, 9.3 (incl. -m32), 11, 13 and Clang 15 on macOS 13-15; requires CMake >= 3.7. · x86-64 and 32-bit x86 on Linux, and macOS (Clang) are exercised in the GitHub Actions matrix I read; a Windows job exists in that same file but is commented out/disabled. README claims general portability ('smartphones, supercomputers, windows, etc.') and the README badge references a separate AppVeyor Windows build, which I did not open this session.

**Vs siblings:** Pick tlx::btree over fast-containers, S+/S-tree, or boost::container::flat_set/flat_map when the workload is genuinely dynamic (both insert and erase, not build-once-then-query) at large scale (roughly >100k-1M items) and you want a permissively licensed (BSL-1.0), dependency-free header with no SIMD/AVX/hugepage requirement; prefer S+/S-tree if the workload is static (bulk-built once, then read-only lower_bound queries), fast-containers if you can require SIMD+hugepages for its larger, more recently measured wins at 10M-element scale, or boost::flat_set/flat_map if containers stay small (roughly 2-128 elements).

**Gotchas:**
- verify()/self_verify require linking tlx/die/core.cpp (or libtlx) for die_with_message(); not fully header-only if you use invariant checking.
- No move constructor or move-assignment on btree_map/btree_set — only copy constructor, copy assignment, and swap() are defined.
- erase(first, last) is unimplemented: it only exists (and aborts) if TLX_BTREE_TODO is defined, otherwise the method is absent entirely.
- No iterator/pointer stability guarantee across insert/erase, unlike std::map/std::set — don't hold iterators or pointers across mutations.

**Status:** Stale: last commit 2025-01-10 per the record, and the only open GitHub issue I found (#62) concerns the unrelated d_ary heap, not btree. BSL-1.0 licensed (unlike the GPL-3.0 predecessor stx-btree) and small enough to vendor as a handful of headers — copyable per the record's usability field.

[repo](https://github.com/tlx/tlx) · [benchmark](https://panthema.net/2007/stx-btree/speedtest/)

### regex

#### Boost.Regex  `C++`  `BSL-1.0`  `active`  `Tier A`

Header-only successor to std::regex: same backtracking engine, hand-tuned matcher and pooled allocation for real throughput gains.

**Beats:** std::regex — On mariomka/regex-benchmark (g++ 7.5.0, -std=c++11 -O3, Boost 1.65.1 linked via -lboost_regex, Docker ubuntu:bionic on a 2019 MacBook Pro i9), Boost.Regex compiled and matched 3 patterns (Email/URI/IPv4) over the Learn-X-in-Y-minutes corpus in 104ms total versus 1023ms for libstdc++'s std::regex (~9.8x, including compilation time). The independent rust-leipzig regex-performance suite (18 patterns over a ~16MB text file, AMD Threadripper 3960X, compiler unstated) confirmed the same direction on 13 of 14 shared patterns, from ~1.0x up to ~47x, losing on one alternation-heavy pattern ('([A-Za-z]awyer|[A-Za-z]inn)\s').

**How:** Same backtracking-NFA design as std::regex: basic_regex_creator compiles the pattern into a graph of states, then perl_matcher walks it. The implementation is heavily hand-tuned around that: a non-recursive matcher (perl_matcher_non_recursive.hpp) that uses an explicit stack instead of C++ call recursion, a pooled memory-block allocator (mem_block_cache.hpp) that reuses backtracking-stack memory across matches instead of hitting the heap, precompiled character-class bitmaps, and a leading-literal fast-skip so scanning for a required prefix doesn't reevaluate the whole state machine at every position. There is no SIMD and no asymptotic change over backtracking matching -- the win is fewer allocations and tighter C++, and it can still hit catastrophic backtracking on adversarial patterns just like std::regex.

**Use it when:**
- Need std::regex-shaped semantics (ECMAScript/Perl/POSIX syntax, smatch-like results) but higher matching throughput on typical (non-adversarial) patterns.
- Pattern set is compiled once and reused across many inputs, so per-call matching cost dominates over one-time compilation.
- Need the POSIX regcomp/regexec API, MFC string support, or ICU/Unicode string iteration that std::regex does not provide.
- Already on or willing to add Boost (or the standalone header mode) and accept BSL-1.0, for a well-documented ~9.8x total / up to ~47x per-pattern win over libstdc++ std::regex on text-scanning workloads like log or URI/email extraction.
- Building against Boost 1.77+ where the library is header-only, so no extra link step is needed for the core C++ API.

**Skip it when:**
- Patterns come from untrusted input (user-supplied regex or unbounded nested quantifiers/alternation): this is the same backtracking/ReDoS risk class as std::regex, not a safer engine (see GH issue #178, 'Subroutine call backtracking bug').
- Need a hard guarantee of linear-time matching regardless of pattern shape -- pick a DFA/Thompson-NFA engine like RE2 instead of any backtracking engine, including this one.
- Targeting Boost older than 1.77 (before Boost.Regex 6.0.0, 2021) where the library still requires linking a compiled boost_regex lib, as the mariomka benchmark used (Boost 1.65.1, built with -lboost_regex).
- Want a truly zero-dependency drop-in: even in standalone mode you still add a distinct type hierarchy (boost::regex != std::regex); non-standalone mode also pulls in Boost.Config/Assert/Predef/ThrowException.
- Small, one-off, latency-sensitive regex use where std::regex's ubiquity and zero extra header outweigh a ~2x-ish smaller, but still real, integration cost.

**Integration:** header-only · none in standalone mode (BOOST_REGEX_STANDALONE, or auto-detected under C++17 with __has_include when <boost/version.hpp> is absent); otherwise Boost.Config, Boost.Assert, Boost.Predef, Boost.ThrowException. Optional ICU for Unicode string integration. The POSIX C API (src/posix_api.cpp, src/wide_posix_api.cpp) is still compiled/linked separately if used. · C++11 minimum; C++03 support was formally deprecated in 6.0.0/Boost 1.77 (doc/history.qbk). C++17 is only needed for automatic standalone-mode detection via __has_include, not as a hard floor. · any (portable C++; no SIMD/ISA requirement found in headers or docs)

**Vs siblings:** Pick Boost.Regex over RE/flex or REAL when you want an API and feature set (POSIX/ICU/MFC support, Perl/ECMAScript syntax) almost identical to std::regex for an easy migration, rather than adopting a scanner-generator workflow (RE/flex) or a from-scratch header-only engine (REAL/real-regex) for their larger reported multipliers. Unformat is not comparable here -- it only handles fixed-shape format strings at compile time, not general regex.

**Gotchas:**
- Header-only status is recent (Boost.Regex 6.0.0 / Boost 1.77, 2021, confirmed via CMakeLists.txt's `add_library(boost_regex INTERFACE)`); the benchmark numbers in this record used Boost 1.65.1, compiled with `-lboost_regex`, from before that change.
- Same backtracking design as std::regex: pathological patterns can still blow up, with no linear-time guarantee (GH #178).
- Standalone mode drops Boost.Config's compiler-defect workarounds; if you disable exceptions in standalone mode you must define BOOST_NO_EXCEPTIONS yourself.
- Changing the global C locale from one thread while another thread is mid-match is explicitly called out as unsafe in the docs.

**Status:** Actively maintained (last commit 2026-05-22 on the default branch) and BSL-1.0 licensed, so freely copyable/vendorable; GitHub reports a null license for the repo, but the header comments carry the Boost Software License 1.0 text directly.

[repo](https://github.com/boostorg/regex) · [benchmark](https://github.com/mariomka/regex-benchmark)

#### RE/flex  `C++`  `BSD-3-Clause`  `active`  `Tier A`

Flex-style C++ lexer generator plus a multi-engine regex matcher library; DFA scanners far outrun std::regex, PCRE2, and Boost.Regex at tokenizing.

**Beats:** std::regex — On a 2 KB representative C source file tokenized into 244 tokens, a reflex --fast --noindent generated scanner (RE/flex 3.4.1) measured 8.7 us versus 6490 us for std::cregex_iterator (C++11 std::regex, libc++ inferred from platform) — about 746x faster — measured with clang 12.0.0 -O2 on a 2.9 GHz Intel Core i7 / 16 GB LPDDR3 Mac running macOS 12.6.9. The repo is now at 6.5.0; the std::regex leg was run through RE/flex's own std-ecma matcher adapter with one large alternation pattern rather than a hand-written std::regex loop.

**How:** The native RE/flex regex engine compiles patterns to a DFA using a backtrack-free lazy-matching transformation (credited to Robert van Engelen) that matches in linear time without backtracking, unlike std::regex's NFA engine. Generated scanners run as compact FSM code rather than re-entering a general matching engine per token. Matcher::find() and related search paths additionally use runtime-dispatched SIMD (SSE2/AVX2/AVX512BW on x86, NEON/AArch64 on Arm) to accelerate scanning for the next candidate match.

**Use it when:**
- Tokenizing/scanning a stream into many tokens (lexer/parser front-ends) where std::regex's per-call setup and backtracking overhead dominate
- Building a Flex/Bison-based C++ toolchain and wanting Unicode-aware, POSIX-compliant scanning with less porting effort than plain Flex++
- Need indent/dedent-sensitive tokenizing (Python-like languages) or multi-encoding (UTF-8/16/32, legacy code pages) file input
- Want one API that can fall back to PCRE2 or Boost.Regex for fuller Perl syntax while keeping the fast DFA engine on the hot path
- Large text/file scanning workloads (RE/flex backs ugrep) where guaranteed linear-time DFA matching is preferable to std::regex's backtracking risk

**Skip it when:**
- Need capture groups with RE/flex's own fast engine: not supported natively (open issue #95, only non-capturing groups); must switch to PCRE2Matcher/BoostMatcher/StdMatcher and give up some speed
- Need backreferences or lookaround: the native engine is IEEE POSIX P1003.2-compliant DFA matching, which structurally excludes these (only the PCRE2/Boost adapters support them)
- Only need a handful of ad hoc regex checks in otherwise std::regex-shaped code: the reflex code-generation step plus a libreflex build add more integration surface than warranted
- Pattern shapes with a leading unanchored wildcard (e.g. `.*literal`) used with Matcher::find(): one reported benchmark (#220) showed ~15000x slowdown versus removing the leading `.*`, so verify your actual pattern shape
- Strict correctness under MemorySanitizer: issue #234 reports a use-of-uninitialized-value warning in AbstractMatcher::reset_text() via text()

**Integration:** static lib | shared lib · none required; PCRE2 and Boost.Regex are optional, only needed if you use reflex::PCRE2Matcher or reflex::BoostMatcher · C++11 (CMAKE_CXX_STANDARD 11 in CMakeLists.txt); strview() needs C++17 · Windows, macOS, Linux, NetBSD, BSD; x86-64 with SSE2/AVX2/AVX512BW auto-detected at runtime (configure --disable-avx / --disable-sse2 to turn off), aarch64/NEON supported for search, portable C++ fallback otherwise

**Vs siblings:** Pick RE/flex over Boost.Regex, REAL, or Unformat when the job is generating a real tokenizer/scanner (many tokens per input, Flex/Bison-style workflow) rather than replacing scattered std::regex match/search calls; Boost.Regex and REAL are closer to a source-level drop-in for individual std::regex call sites with far less build/integration surface.

**Gotchas:**
- Native Matcher has no capture groups (non-capturing groups only); this is a known, still-open design gap, not a bug that will be fixed soon
- A leading unanchored `.*` in a pattern used with find() can be ~15000x slower than the equivalent anchored/literal search on the same input (issue #220)
- libreflex is a real build artifact (libreflex.a/.so via configure/make or CMake), not a header you can just #include and go
- SIMD (AVX2/AVX512BW) is auto-detected at runtime by default; disable via configure flags if you hit CPU-detection or build issues on older toolchains

**Status:** Actively maintained (last commit 2026-09-15, now versioned 6.5.0 vs. the benchmarked 3.4.1) and BSD-3-Clause/copyable, but the reflex code-generation step and libreflex build make it heavier to vendor than a header-only std::regex replacement.

[repo](https://github.com/Genivia/RE-flex) · [benchmark](https://github.com/Genivia/RE-flex/blob/master/README.md)

### sorting

#### Boost.Sort — spreadsort  `C++`  `BSL-1.0`  `active`  `Tier A`

Hybrid radix/comparison sort in Boost; beats std::sort on large random integers, strings, and objects.

**Beats:** std::sort — In the library's own linux_single.qbk benchmark (GCC 6.3, -std=c++11 -march=native -O3, Intel i7-5820K, libstdc++), spreadsort sorted 100M random 64-bit ints in 4.2248s vs std::sort's 8.2154s (~1.94x), 10M random strings in 2.4323s vs 6.2442s (~2.57x), and 100M 8-byte objects with a heavy comparator in 5.10s vs 8.25s (~1.62x); spreadsort was slower than std::sort on reverse-sorted ints (1.87s vs 1.36s).

**How:** It is a hybrid radix/comparison sort: it recursively buckets elements by their most-significant bits (read via a right-shift functor) and dynamically chooses radix or comparison-based sorting per bucket, whichever has better worst-case cost. Worst case is the lesser of O(N log N) comparisons and O(N log(K/S + S)) operations, where K is key bit-width and S (max_splits, default 11) is a tunable constant. This gives near-linear behavior on wide or clustered integer/float/string keys where std::sort spends more time on comparisons.

**Use it when:**
- Sorting 100K-100M+ 64-bit integers, floats, or std::strings single-threaded, where the ~2x win on random data matters.
- Large or expensive-to-compare elements (long keys, heavy comparators, key+payload records) — the object benchmark shows bigger wins as element size grows.
- Data that is already sorted or nearly sorted forward — spreadsort has an early-exit fast path competitive with pdqsort.
- Custom numeric-like keys where you can write a correct right-shift functor (fixed-point types, custom integer wrappers).
- You are fine with an unstable sort, same as std::sort.

**Skip it when:**
- Reverse-sorted or adversarial input — the repo's own benchmark shows spreadsort slower than std::sort here (1.87s vs 1.36s on 100M ints).
- Inputs under ~1000 elements — falls back to pdqsort internally, so there is no spreadsort-specific benefit.
- Need a stable sort — use Boost's spinsort/flat_stable_sort instead, though neither beat std::stable_sort on random data in this same benchmark, only on near-sorted input.
- Indirect/argsort-style sorting through an index lookup — GitHub issue #85 shows overriding only the right-shift functor without also overriding the comparator silently falls back to plain (wrong-looking) comparison behavior for small inputs.
- Need the benchmarked ~2x margins reproduced on current hardware/toolchains — the doc's numbers are from GCC 6.3 on a 2017-era CPU and have not been re-run since.

**Integration:** header-only · Boost.Range, Boost.TypeTraits, Boost.Core (static_assert) — ships as part of Boost, not a standalone zero-dependency library · C++11 (README states a C++11 compiler is required; parallel algorithms in the same repo also need C++11) · any — portable C++ template code, no SIMD/intrinsics or arch-specific code observed in the spreadsort headers

**Vs siblings:** Pick spreadsort over comparison-based siblings (BlockQuicksort, pdqsort-class sorts) when data is plain integers/floats/strings with wide or clustered key bits and you don't need stability or multithreading; pick IPS4o or x86-simd-sort instead when you can parallelize or vectorize, and pick fluxsort/quadsort instead when stability matters more than raw unstable-sort throughput.

**Gotchas:**
- Right-shift functor must fully discriminate between elements consistent with operator< (documented requirement, GitHub issue #7).
- Overriding the right-shift functor alone for indirect/argsort use (sorting indices via a lambda into another array) without also overriding the comparator can give surprising results on small inputs that fall back to default comparison (issue #85).
- Doc header warns exceptions during comparisons, swaps/moves, the right shift, or iterator operations propagate and 'may cause data loss'; only the internal small-vector-resize-throw path is documented as data-loss-free.
- Needs O(key_length) extra memory for radix buckets, so memory scales with key bit-width as well as N — not a fixed small overhead like introsort's O(log N).

**Status:** Actively maintained as part of Boost (last commit 2026-04-11 on develop); BSL-1.0 licensed, header-only, and small enough to vendor without a build step.

[repo](https://github.com/boostorg/sort) · [benchmark](https://github.com/boostorg/sort/blob/develop/doc/linux_single.qbk)

#### IPS⁴o (In-place Parallel Super Scalar Samplesort)  `C++`  `BSD-2-Clause`  `stale`  `Tier A`

In-place parallel/sequential comparison sort beating std::sort via cache-efficient block-based samplesort partitioning.

**Beats:** std::sort — On the four-machine benchmark suite (arXiv 2009.13569, GCC 7.5.0, -march=native -O3), sequential IPS4o averaged roughly 2x std::sort's throughput on double/uint64/uint32 keys (Table 1 'Total' slowdown factors 1.20-1.78 for IPS4o vs 2.47-3.93 for std::sort's libstdc++ introsort), and Fig. 11 shows std::sort off-plot and slower than IPS4o on uniform uint64 across all four machines (AMD Ryzen 9 3950X, AMD EPYC Rome 7702P, 2x Xeon E5-2683 v4, 4x Xeon Gold 6138). The paper gives no direct parallel-vs-std::sort figure; its parallel speedups (8.37x-40.92x) are relative to sequential IPS4o, not std::sort.

**How:** Superscalar samplesort: recursively partitions the array in-place into many buckets per pass using a branchless decision tree over sampled splitters, then permutes elements block-by-block to stay cache-efficient without extra memory. It special-cases inputs with many equal elements to avoid pathological partitioning, and the parallel version dynamically load-balances buckets across threads.

**Use it when:**
- Sorting large arrays/vectors of primitives, floats, or small records (Pair/Quartet/100-byte) in-place with no extra buffer
- Multi-core machines where parallel::sort (OpenMP or std::thread + TBB) can use the extra cores for large inputs (roughly n >= 2^18)
- Data with many duplicate keys or skewed distributions, which the branchless classifier handles without the usual pathological slowdown
- Sequential drop-in replacement for std::sort on Linux/macOS with a C++14-capable GCC or Clang toolchain

**Skip it when:**
- Windows builds -- the README states the code does not currently compile on Windows
- Very small inputs (n <= 2^15), where BlockQuicksort is faster per the record's caveats
- Need a stable sort that preserves the relative order of equal keys -- not documented as stable, and in-place bucket permutation gives no such guarantee
- Can't add TBB and libatomic (or -mcx16 / native 16-byte CAS) to the build -- parallel mode requires them; sequential-only mode is header-only with no dependencies
- Sanitizer-clean concurrency required -- open, unresolved TSan-flagged data race in the parallel presort check (issue #3)

**Integration:** header-only · sequential: none. parallel: pthreads/std::thread, TBB, libatomic (or -mcx16 / native 16-byte compare-and-exchange) · C++14 (CMakeLists sets CMAKE_CXX_STANDARD 14); benchmarked with GCC 7.5.0, -march=native -O3 · Linux/macOS, GCC or Clang, x86-64 (16-byte CAS needed for fastest parallel mode); does not compile on Windows

**Vs siblings:** Pick IPS4o over BlockQuicksort/quadsort/fluxsort when you need a parallel multi-core sort or must stay robust across many data types and skewed/duplicate-heavy distributions; pick those instead for a header-only, dependency-free sequential drop-in with a simpler build.

**Gotchas:**
- Parallel mode needs 16-byte atomic compare-and-exchange (-march=native or -mcx16, plus -latomic) or it falls back to lock emulation and loses speed
- CMake's IPS4O_OPTIMIZE_FOR_NATIVE defaults to ON (-march=native), which can produce binaries that crash on other CPUs if redistributed
- Open, unresolved TSan-flagged data race in the parallel presort check (issue #3)
- The ips4o/ips4o repo ships no benchmark code (only src/example.cpp); the paper's numbers come from the separate GPL-3.0 ips4o-benchmark-suite, which is not linked from the README

**Status:** Stale (last commit 2025-01-15) but the maintained successor to the deprecated SaschaWitt/ips4o fork; BSD-2-Clause and header-only for sequential use, so it is easy to vendor even without upstream activity.

[repo](https://github.com/ips4o/ips4o) · [benchmark](https://arxiv.org/abs/2009.13569)

## Permissive — Unverified claims (tier C/D)

### hash-maps-sets

#### rigtorp/HashMap  `C++`  `MIT`  `stale`  `Tier C`

Header-only open-addressing hash map with backshift deletion, up to ~5x faster than std::unordered_map on delete-heavy workloads.

**Beats:** std::unordered_map — Self-published benchmark (README + src/HashMapBenchmark.cpp), gcc 10.2.1 on an AMD Ryzen 9 3900X (Fedora, isolcpus-isolated CCX), against libstdc++'s std::unordered_map in a delete-heavy insert-or-erase loop with size_t keys and 24-byte values. In-cache (100K entries): HashMap mean 24 ns/iter vs std::unordered_map 67 ns/iter (~2.8x). Out-of-cache (10M entries): HashMap 75 ns/iter vs 408 ns/iter (~5.4x). Optimization flags are not stated (CMakeLists.txt sets no CMAKE_BUILD_TYPE, only -mavx2 and warnings), and it's a single hardware configuration with no independent reproduction.

**How:** Open addressing with linear probing stores entries directly in a single contiguous std::vector of buckets, avoiding per-node allocation and pointer chasing. On erase it uses backshift deletion (shifting later entries back into the vacated slot) instead of tombstones, so probe sequences stay short even under the paired insert/erase churn in the benchmark. Bucket count is kept a power of two so index computation is a mask (idx & mask) rather than a modulo, and load factor is hard-capped at 50% to bound probe length.

**Use it when:**
- Delete-heavy or high-churn workloads (repeated insert+erase of the same keyspace) where backshift deletion avoids the tombstone buildup that degrades linear probing over time
- Keys/values are cheap, default-constructible, and copyable (the benchmark uses size_t keys and a 24-byte POD value), and you can reserve one sentinel value as the 'empty key'
- You want a single-header, zero-dependency container to vendor rather than pull in Abseil/Folly for a hash map
- Latency matters for both cache-resident and larger-than-L3 working sets, and you can tolerate stricter iterator-invalidation and no-destructor-on-erase semantics

**Skip it when:**
- You need a true drop-in replacement: the constructor signature differs (bucket_count, empty_key) and Key/T must be default constructible, which is also why it's excluded from Martin Ankerl's independent map_benchmark suite (per repo issue #2)
- Values own resources (std::string, std::vector, std::unique_ptr, etc.) where you rely on the destructor running on erase — HashMap does not call destructors on erase
- You need iterator/reference/pointer stability across mutations — every insert, erase, or rehash invalidates them, stricter than std::unordered_map
- You need >50% load factor for memory efficiency, multi-threaded access (thread safety is undocumented), or an actively maintained dependency (last commit 2023-09-25, effectively unmaintained)

**Integration:** header-only · none (STL only). The benchmark binary optionally links Abseil and uses x86 CRC32/AVX2 intrinsics plus a Linux huge-page allocator, but none of that is required by the library itself. · C++14 (CMake target_compile_features cxx_std_14 for the library; the benchmark target additionally requires C++17 and -mavx2) · any (the library is portable, architecture-agnostic C++14); only the benchmark's CRC32 hash, AVX2 flag, and MAP_HUGETLB allocator are x86-64/Linux-specific

**Vs siblings:** Pick HashMap when you want the smallest possible dependency (one ~250-line header, no external deps) specifically for delete-heavy/churn workloads where backshift deletion matters; the in-repo numbers show it beating both std::unordered_map and absl::flat_hash_map at that workload. Prefer emhash, ska::flat_hash_map/tsl::robin_map, or absl instead when you need iterator stability, don't want to manage an empty-key sentinel, or want a design that's actually included in independent benchmark suites (Ankerl 2022) and sees ongoing maintenance.

**Gotchas:**
- A reserved empty-key sentinel is mandatory at construction; using that value as a real key is undefined behavior (only asserted in debug builds)
- Destructors are never invoked on erase — backshift deletion just moves/overwrites slots, so resource-owning values leak until overwritten or the table is destroyed
- Iterators, pointers, and references are invalidated by every insert, erase, or rehash, not just rehashes as in std::unordered_map
- Max load factor is hard-coded to 50%; every insert path calls reserve(size_+1), so the table silently doubles capacity earlier than std::unordered_map would, trading memory for probe length

**Status:** Maintenance is stale (last commit 2023-09-25, about to cross into 'abandoned'), but it's MIT-licensed, header-only, and small enough (~250 lines) to vendor and audit directly rather than depend on for long-term support.

[repo](https://github.com/rigtorp/HashMap) · [benchmark](https://github.com/rigtorp/HashMap)

### number-parsing-formatting

#### c4core (charconv/xtoa/atox module)  `C++`  `MIT`  `active`  `Tier C`

Low-level C++ utility library whose charconv module (xtoa/atox) beats std::to_chars and std::from_chars on integers.

**Beats:** std::to_chars, std::from_chars — On Linux with g++11.2 Release, c4core's own CI microbenchmark (bm/bm_charconv.cpp) shows c4::to_chars beating std::to_chars by 1.07x-2.44x and c4::from_chars beating std::from_chars by 1.05x-1.54x across 8/16/32/64-bit signed and unsigned integers, measured in MB/s. Float/double comparisons exist only as PNG charts from a separate g++12.1 (Linux) / VS2019 (Windows) run; no CPU or hardware is disclosed for either run.

**How:** For integers, c4core uses its own digit-counting and decimal-digit extraction routines (digits_dec()/write_dec()/read_dec()) with no locale handling, format-flag dispatch, or allocation, avoiding overhead present in libstdc++/MSVC STL's std::to_chars/from_chars. For float/double, c4core does not implement its own parsing algorithm: from_chars for floating types is answered by the bundled fast_float submodule (already catalogued separately) when C++17 and the fastfloat option are enabled (the default), so the float speedup is fast_float's algorithm, not original c4core code.

**Use it when:**
- Hot loops converting many fixed-width integers (u8-u64, i8-i64) to/from decimal ASCII, e.g. log lines or serialization formatting
- Already using c4core/rapidyaml or want one low-level utility library instead of many point solutions
- Comfortable with a substr/csubstr buffer API instead of std::to_chars' pointer-pair + result-struct signature
- Building on a toolchain without full C++17 <charconv>: c4core still gets integer speedups on C++11, and floats route through fast_float
- Want MIT-licensed source that can be vendored as a single amalgamated header (tools/amalgamate.py)

**Skip it when:**
- Only need fast float/double parsing: use fast_float directly, since c4core's float path is just fast_float underneath with extra library weight on top
- Want a minimal, single-purpose charconv library: c4core pulls in a large general-purpose utility library (span, allocators, error handling, etc.)
- Need the exact std::to_chars/from_chars call signature for drop-in replacement without call-site changes
- Need independently-verified numbers: only the project's own README/CI benchmarks exist (evidence tier C), with no hardware/CPU disclosed
- Targeting old MSVC (<2019): std::to_chars/from_chars interop is unavailable, and the README's text table itself is from an older g++11.2 run vs. current CI's newer compilers

**Integration:** source-drop (CMake subproject/static lib) or single-header via tools/amalgamate.py · fast_float (bundled git submodule, used for float/double parsing when C++17 + fastfloat option enabled, the default); sg14 inplace_function (BSL-1.0) and debugbreak (BSD-2-Clause) are bundled for other parts of c4core, not charconv itself · C++11 minimum for the library and integer xtoa/atox; C++17 with MSVC2019+/GCC or a compiler exposing <charconv> is needed to enable the std::to_chars/from_chars interop path · x64, x86, arm, aarch64, wasm (emscripten), ppc64le, s390x tested in CI; bare-metal, RISC-V and LoongArch reported working via issues/PRs but not in the official CI matrix

**Vs siblings:** Pick c4core's charconv when you already want its broader utility library (substr, span, error handling) and only need integer to/from-decimal speed; its documented integer wins (1.05x-2.44x over std) are smaller than Boost.Charconv's or rigtorp/CharConv's claimed multiples, so choose one of those instead — or fast_double_parser/fast_float — if isolated charconv or float-parsing performance alone is the goal.

**Gotchas:**
- Requires cloning with --recursive (or `git submodule update --init`) for the cmake/, fast_float, and debugbreak submodules; the amalgamation script is the alternative for header-only use
- On MSVC, c4core deliberately disables std::from_chars in favor of fast_float ('prefer fast_float with MSVC'), so float from_chars comparisons on Windows are effectively fast_float vs. an MSVC STL that also uses similar techniques internally
- A static-assertion failure in charconv.cpp on VS2019 was reported (issue #19, closed as duplicate in 2020) — worth checking current MSVC versions before relying on it
- Float/double results in the README exist only as PNG charts (g++12.1 Linux / VS2019 Windows), not in the text MB/s table, which covers integers only

**Status:** Actively maintained (last commit 2026-09-03, ~149 stars); MIT-licensed core with permissively-licensed bundled dependencies (fast_float, sg14 BSL-1.0, debugbreak BSD-2-Clause), so it is safely copyable/vendorable, including via the single-header amalgamation script.

[repo](https://github.com/biojppm/c4core) · [benchmark](https://github.com/biojppm/c4core/blob/master/README.md)

#### CharConv.h (rigtorp)  `C++`  `MIT`  `stale`  `Tier C`

Header-only base-10 int32/int64 to/from-string conversion; beats stringstream, to_string, atoi/strtol, stoi.

**Beats:** iostreams (std::stringstream); std::to_string; std::stoi/atoi/strtol — In-repo Google Benchmark dated 2017-12-26 on a Xeon E5-2620 v4 (compiler/flags not disclosed): to_chars ran 9-20ns vs sprintf 73-87ns, std::to_string 76-90ns, and std::stringstream 34-55ns; checked from_chars ran 9-19ns vs atoi/strtol 14-28ns and std::stoi 16-29ns; from_chars_unchecked ran 4-10ns. No std::to_chars/std::from_chars comparison exists in the repo.

**How:** to_chars precomputes the exact digit count with a clz-based bit-length-to-decimal-digits formula (__builtin_clz/__builtin_clzll against a static power-of-10 table) so it writes straight into a correctly sized span instead of a scratch buffer plus reversal or a strlen pass, then emits digits back-to-front via repeated /10, %10. from_chars accumulates digits with __builtin_mul_overflow/__builtin_add_overflow so overflow detection adds no separate check pass; a from_chars_unchecked variant skips overflow checks for a further speedup. Everything is noexcept, constexpr, and hinted with __builtin_expect.

**Use it when:**
- Hot loops converting many 1-9 digit signed/unsigned 32/64-bit integers to base-10 text (log lines, CSV/JSON emitters, wire protocols).
- Parsing base-10 integers with overflow detection but without exceptions or locale overhead (from_chars).
- Trusted, pre-validated input where the unchecked from_chars_unchecked path's extra speed is worth skipping validation.
- You already have a fixed buffer/pointer and want to skip std::to_string's allocation or stringstream's formatting machinery.
- GCC/Clang-only target where vendoring one ~200-line, zero-dependency header is acceptable.

**Skip it when:**
- Need floating-point to_chars/from_chars — not implemented at all here.
- Need MSVC support — code depends on GCC/Clang builtins (__builtin_clz, __builtin_clzll, __builtin_mul_overflow, __builtin_add_overflow) with no MSVC equivalents provided.
- Need real interchangeability with std::to_chars/std::from_chars (exact result types, base 2-36, std::chars_format) — this API is similar but distinct, not a swap-in.
- Want the fastest available integer formatter — sibling libraries (jeaiii/itoa, c4core) use digit-pair lookup tables and report larger margins; this repo never benchmarks against them or against actual std::to_chars.
- Expect upstream maintenance — no commits, issues, or PRs since the 2023-09-25 push; algorithm and code are unchanged since the 2018 copyright.

**Integration:** header-only · none for consumers (vendors Google Benchmark and Catch2 only for the repo's own benchmark/test binaries) · C++17 (if constexpr); relies on GCC/Clang builtins, exact minimum GCC/Clang version not documented · any GCC/Clang target (x86-64, aarch64, etc.); MSVC not supported, no intrinsic fallback provided

**Vs siblings:** Pick this over Boost.Charconv or c4core when you want a zero-dependency, ~200-line header covering only base-10 32/64-bit integers and don't need float support; pick Boost.Charconv or c4core instead when you need floats or an actual std::to_chars/from_chars head-to-head, since this repo never benchmarks against std at all.

**Gotchas:**
- from_chars_unchecked skips overflow validation entirely — only safe on pre-validated input.
- to_chars_result/from_chars_result are rigtorp's own types, not std::to_chars_result/std::from_chars_result — don't assume interchangeability.
- Caller must size the output buffer itself (worst case 11 bytes for int32/uint32 with sign, 20 for int64/uint64); no allocating convenience wrapper is provided.
- Compiler-builtin dependent (__builtin_clz/__builtin_mul_overflow/etc.) — porting off GCC/Clang requires substituting equivalents.

**Status:** Stale since the last push on 2023-09-25 (0 open issues/PRs, no recent activity) but MIT-licensed, header-only, and small enough to vendor as-is.

[repo](https://github.com/rigtorp/CharConv) · [benchmark](https://github.com/rigtorp/CharConv/blob/master/README.md)

#### jeaiii/itoa  `C++`  `MIT`  `abandoned`  `Tier C`

Header-only branchless integer-to-ASCII conversion, ~7-9x faster than sprintf/MSVC _itoa, ~1.6-1.8x vs {fmt}.

**Beats:** sprintf (C standard library, MSVC CRT) and MSVC _itoa/_ui64toa in the README's release charts; {fmt} in the godbolt table. No std::to_chars comparison exists. — Author-run release-mode benchmark (Visual C++ 2019, win64, hardware unstated) using jeaiii's fork of miloyip/itoa-benchmark shows, on uniform-random-digit-length inputs, u32toa at 20.5 cycles vs sprintf's 160.5 and MSVC _ui64toa's 174.5 (~8x), and vs {fmt}'s 33.5 (~1.6x); u64toa is 32.75 cycles vs sprintf's 226.75 and MSVC's 312 (~7-9x), and vs {fmt}'s 58 (~1.8x). A separate debug-built Google Benchmark on godbolt, which the author explicitly disclaims as not a good benchmark, shows 10.2ns vs {fmt}'s 16.6ns. No comparison against std::to_chars is published anywhere in the repo.

**How:** Uses a per-digit-length unrolled code path chosen by a small binary-search branch tree on the number's decimal length, so short numbers take fewer branches than long ones instead of looping once per digit. Digits are produced two at a time via fixed-point multiply-shift arithmetic against a 100-entry '00'-'99' ASCII lookup table, avoiding per-digit division; only one true integer divide is used, to split 64-bit values into two 8-digit halves. The fixed-point constants follow the classic multiply-by-2^k/10^n itoa trick, refined using the mathematical analysis in dragonbox author Junekey Jeon's write-up, which removed a redundant addition.

**Use it when:**
- Hot paths that serialize many plain base-10 integers to text (logging, JSON/CSV encoders, protocol formatting) on MSVC, clang, or gcc
- Fixed 8/16/32/64-bit integer types where you control the destination buffer size and will add the null terminator yourself
- Workloads with uniform or skewed digit-length distributions (IDs, counters) where branch-prediction-unfriendly random lengths matter
- Need a single self-contained, zero-dependency header (not even <cstdint>) that works from C++11 up, easy to vendor
- You're comfortable auditing/patching abandonware yourself rather than depending on upstream maintenance

**Skip it when:**
- Need floating-point-to-string conversion; integers only, no float/double support at all
- Need std::to_chars' API contract: error_code / bool success return, [first,last) bounds-checked span; this header has neither
- Need guaranteed-correct output without your own verification: the repo has shipped at least two silent, large-magnitude correctness bugs on big 64-bit inputs (issues #12, #18), both fixed only because users noticed
- Want zero-padding or fixed-point/decimal formatting; explicitly requested in issue #15 and not implemented
- Need a plain-C API; this is C++ template code with no official C binding (issue #10 still open, unresolved)

**Integration:** header-only · none · C++11 (compiles on clang, MSVC, and gcc per README) · any (no architecture-specific intrinsics in the header; author's benchmarks are x86/x64 Windows/VC2019)

**Vs siblings:** Pick jeaiii/itoa over CharConv.h (rigtorp) or c4core when you want the smallest possible single header with zero includes and don't need from_chars/parsing or float formatting. Pick c4core or Boost.Charconv instead when you need a maintained, std::to_chars/from_chars-compatible API with float support and bounds-checked spans.

**Gotchas:**
- Output is not null-terminated; caller must write '\0' at the returned pointer (see test/main.cpp's to_string wrappers)
- No bounds checking: caller must size the buffer for the worst case (up to 20 digits + sign for 64-bit) or risk a buffer overflow
- History of silent large-magnitude correctness bugs on 64-bit inputs (issue #12: off by 10,000,000 on a 19-digit value; issue #18: wrong values near a specific 11-digit range), both fixed before the final 2022-11-24 commit but with no maintainer left to catch new regressions
- Repo contains multiple header variants (include/itoa/jeaiii_to_text.h is current; itoa/to_text_from_integer.h and itoa/int_to_chars_jeaiii.h are older macro-based versions) — include the one under include/itoa/, not the legacy ones

**Status:** Abandoned since its last commit on 2022-11-24 with no tagged releases; MIT-licensed and small enough (~200-line single header) to vendor and patch yourself, but its history of correctness bugs on large 64-bit values means you should add your own exhaustive round-trip test before trusting it in production.

[repo](https://github.com/jeaiii/itoa) · [benchmark](https://github.com/jeaiii/itoa/blob/main/README.md)

### ordered-maps-trees

#### boost::container::flat_set / flat_map  `C++`  `BSL-1.0`  `active`  `Tier C`

Vector-backed sorted set/map beating std::set on insert+remove at small sizes, up to ~256 elements.

**Beats:** std::set — A single-author 2014 blog benchmark (500,000 random insert-then-erase operations on int keys, -O3, compiler and hardware unstated) timed boost::container::flat_set against std::set across sizes 2-8192: flat_set was ~2.5x faster at size 2, ~1.1x faster at 128, then lost ground from 256 elements up, with std::set ~13.4x faster at 8192.

**How:** Core technique is cache-friendly linear storage: a sorted vector-like sequence (default plain vector, or a user-supplied vector-like container) gives contiguous memory and random-access iterators, avoiding the pointer-chasing and per-node allocation of a red-black tree. For small containers this locality and lack of per-element allocation outweighs the O(n) shifting cost of insert/erase; std::set's balanced-tree structure only pays off once n is large enough that O(log n) tree operations beat O(n) vector shifts (crossover around 128-256 elements per the cited benchmark).

**Use it when:**
- Sets/maps that stay small (roughly <=128-256 elements per container), even if there are many such containers
- Read-mostly or lookup-heavy workloads where iteration/cache locality matters more than mutation cost
- Cheap-to-move key types (ints, small PODs) where shifting on insert/erase is cheap
- Existing std::set/std::map code that can tolerate iterator/reference invalidation on mutation
- Memory-constrained code avoiding the per-node allocation overhead of tree containers

**Skip it when:**
- Large sets/maps (thousands+ elements) mutated frequently -- std::set was ~13.4x faster than flat_set at 8192 elements in the cited benchmark
- Code relying on iterator/reference/pointer stability across insert/erase -- flat containers invalidate on shift/reallocation
- Bulk one-at-a-time insertion of very large unsorted datasets -- GitHub issue #154 reports near-hang (100% CPU) inserting ~9M elements individually into flat_map
- Workloads needing guaranteed O(log n) worst-case insert/erase (latency-bounded mutation)
- Large or expensive-to-move key/value types, since every insert/erase move-shifts surrounding elements

**Integration:** header-only · Boost.Config, Boost.Move, Boost.Intrusive (ships as part of Boost; no separately compiled library) · C++03 baseline (README states C++03 support); has conditional code paths for C++11 features like initializer_list and variadic templates when available · any (portable C++, no architecture-specific code observed)

**Vs siblings:** Pick flat_set/flat_map over fast-containers, S+ tree, or tlx::btree when the working set stays small (roughly <=128-256 elements) and you want a true drop-in std::set/map replacement shipped with Boost and no extra dependency; the sibling B-tree/B+tree structures target much larger n (up to 10M-scale) and win precisely in the size range where flat_set has already crossed over to being slower than std::set.

**Gotchas:**
- Insert/erase invalidate iterators and references to elements after the mutation point (vector shift/reallocation), unlike std::set's per-node stability
- Underlying sequence container is swappable (e.g. stable_vector, static_vector, small_vector) -- use stable_vector for reference stability at the cost of contiguity
- One-at-a-time insertion of large unsorted data can effectively hang (see issue #154); prefer bulk/sorted-range construction to amortize shifting
- Provides random-access iterators, so generic code that dispatches on iterator category behaves differently than with std::set's bidirectional iterators

**Status:** Actively maintained as a core part of Boost (repo shows a commit dated 2026-09-23) and BSL-1.0 licensed, so it is freely copyable/redistributable with no licensing friction.

[repo](https://github.com/boostorg/container) · [benchmark](https://blog.fellstat.com/?p=376)

### regex

#### REAL (real-regex)  `C++`  `MIT`  `active`  `Tier C`

Header-only C++20 linear-time regex engine with lookaround support, beating std::regex 8x-152x and RE2 on every supported pattern.

**Beats:** std::regex — REAL's own in-repo benchmark (benchmarks/bench_engines.cpp via make bench-engines, c++ -std=c++20 -O2; g++ 13.3.0 on an unnamed x86-64 host, Apple Clang 16 on arm64 Apple Silicon) counted non-overlapping matches for 12 general-purpose patterns and measured REAL 8.20x-41.97x faster than std::regex (libstdc++) on x86-64 and 15.31x-151.97x faster than std::regex (libc++) on arm64, 2.90x-16.34x/2.41x-11.53x faster than RE2 where RE2 supports the pattern, and ahead of PCRE2-JIT on 7 of 12 rows on both ISAs - all figures matched exactly what is published in docs/BENCHMARKS.md this session.

**How:** Routes each compiled pattern to the cheapest execution tier that can handle it - exact-literal/fixed-shape fast paths, a one-pass DFA, a lazy DFA with a bounded state cache, or the general Pike VM (Thompson-NFA simulation) as fallback - instead of always running one general matcher. Character-class steps use SIMD probing (engine/simd.hpp), and a required-literal prefilter rejects non-matching input (e.g. classic ReDoS patterns) in microseconds without entering the NFA at all. Constexpr-friendly parsing/compilation lets patterns known at compile time be parsed, compiled and matched at compile time.

**Use it when:**
- C++20 codebase needing linear-time, ReDoS-safe matching AND lookaround in the same engine (RE2/Rust regex lack lookaround, PCRE2/std::regex backtrack)
- Single-pattern throughput workloads - word/digit/field extraction, hex/date matching, alternation - where the project's own benchmark shows 8.20x-41.97x (x86-64) / 15.31x-151.97x (arm64) over std::regex and wins over RE2 in every case RE2 supports
- Untrusted or adversarial regex patterns/subject text where catastrophic backtracking (e.g. (a+)+b) is a real operational risk
- Need the same engine exposed from Python, Rust, Go and C via the project's own bindings, not just C++
- Willing to pay a header-only compile-time cost (measured 4.3s / 213KiB __text for one TU vs 1.1s / 47KiB for <regex>, arm64 clang -O2) in exchange for the runtime win

**Skip it when:**
- Pattern needs backreferences or conditional groups - REAL rejects these outright by design (real::regex_error, no silent fallback in its native API)
- Matching many patterns against one text at once (regex_set) with N much above ~56 - REAL's pure N-walk mode degrades hard (~559 MB/s at N=16 down to ~39 MB/s at N=128 on the project's own bench) and loses to RE2::Set/Hyperscan at scale
- Lookahead-heavy or fixed-width date/hex workloads specifically - PCRE2-JIT still wins those rows outright (0.71x-0.92x, i.e. PCRE2 faster) in REAL's own tables
- Toolchain stuck below C++20 - this is a hard minimum, asserted in every header, versus std::regex's C++11 floor
- Risk-averse teams: this is an extremely new project (4 stars, repo created 2026-06-13) with benchmarks that are self-published and not yet independently reproduced

**Integration:** header-only · none (zero runtime deps; the SciForge harness is only needed to build the test suite/CI, never the library itself) · C++20 (hard requirement, enforced via a static_assert in every header); tested in CI with g++ 13.3.0, Apple Clang 16, and MSVC on Windows · Linux x86-64 and AArch64, macOS arm64, Windows (MSVC) per CI matrix; no specific SIMD ISA extension (e.g. AVX2) documented as mandatory

**Vs siblings:** Pick REAL over Boost.Regex when you need a linear-time ReDoS-safe guarantee with lookaround - Boost.Regex is a backtracking engine like std::regex and doesn't offer that guarantee. Pick it over RE/flex when you need general runtime regex matching rather than an offline lexer-generator workflow, and over Unformat when the task is general pattern matching rather than std::format-style structured parsing.

**Gotchas:**
- Possessive quantifiers/atomic groups are only linear-time (Tier 1) for a single atom or one atom wrapped in one capturing group ([^x]*+, \d++, (?>\w+)); a compound body inside them is rejected outright, never silently mismatched
- Nullable patterns (a*, (x)?) keep REAL's ReDoS-safe search/match, but regex_replace and iteration on them are delegated to std::regex per-operation - the linear-time guarantee doesn't cover every operation on every pattern
- find_iter (and Python finditer) do not get the trailing-lookahead fast path that count_matches/search/match/replace get - benchmarks that compare via len(findall(...)) rather than count_matches are not comparable to this project's own numbers
- Backreferences, recursion, subroutine calls and callouts are excluded by design (raise real::regex_error) - not a roadmap gap but a permanent rejection to preserve the linear-time guarantee

**Status:** Actively maintained - near-daily CalVer releases (release notes run through v2026.9.7, last commit 2026-09-24) - and MIT-licensed, header-only, so trivially vendorable, but still a very new, small project (4 stars, repo created 2026-06-13) with no external validation of its benchmarks beyond its own suite.

[repo](https://github.com/RECHE23/real-regex) · [benchmark](https://github.com/RECHE23/real-regex/blob/main/docs/BENCHMARKS.md)

#### Unformat  `C++`  `Unlicense`  `active`  `Tier C`

Single-header scanf-style '{}' field extractor for fixed-shape strings; beats std::regex when regex is overkill.

**Beats:** std::regex — On the repo's own Google Benchmark run (32 x 2420 MHz CPUs; compiler, flags, and OS unstated), Unformat took 32.6 ns per call (11.5 ns with the constexpr make_format path) versus 3269 ns for std::regex parsing the same 4-field string. The std::regex leg constructs (compiles) the regex object inside the timed loop every iteration, so that 3269 ns bundles NFA compilation with the match itself; against a precompiled regex the gap would be far smaller than the ~100x-284x (or advertised '300x') headline suggests.

**How:** It avoids std::regex entirely: no NFA construction, no std::string allocations, no capture-group bookkeeping. The constexpr make_format path precomputes each placeholder's byte offset and delimiter character at compile time, so unformat_internal just walks pointers with inlined, per-type combined scan+parse loops (fixed-point digit accumulation instead of std::stoi/std::stof). Numeric parsing accumulates an integer mantissa and applies one final multiply against precomputed powers-of-10 tables, with a noinline cold path reserved for scientific notation or >18-digit literals.

**Use it when:**
- Extracting a handful of ints/floats/strings from a fixed, known-shape line (logs, telemetry, simple protocols) where std::regex would only be used for its capture groups, not real pattern matching.
- Hot loops calling the same format thousands of times per second, where std::regex's per-construction NFA compile is the bottleneck (the benchmarked 3269 ns/call includes that compile, not just matching).
- The format string can be pinned as a compile-time literal, so ay::make_format runs at compile time (11.5 ns vs 32.6 ns for the runtime-parsed path, per the repo's own benchmark).
- Header-only vendoring is acceptable: copy unformat.h into a codebase with no other dependencies and no build-system integration.
- Input is trusted and guaranteed to match the format exactly (internal data, not raw user/network input).

**Skip it when:**
- You need actual regex features -- wildcards, character classes, alternation, quantifiers, anchors; Unformat only matches literal text between '{}' tokens.
- Input may be malformed, truncated, or adversarial: the string_view/char scan path (unformat_arg_scan<ay::string_view> in unformat.h) has no check against the input's terminating null while hunting for a delimiter, so a non-matching string can read past the buffer end.
- You need match/fail feedback: there is no success return, exception, or optional -- bad input silently yields wrong values (a 'does this match' check was requested in issue #3 back in 2017 and is still open).
- More than 16 '{}' placeholders in one format string (hard-coded format::MAX_COUNT = 16).
- Your real baseline is a precompiled std::regex rather than one rebuilt every call -- the ~100x-284x gap narrows a lot once compilation is amortized (see verified_claims_summary).

**Integration:** header-only · none (only <cstddef> from the standard library) · C++14 in practice for the constexpr make_format path -- make_format_non_template declares a local variable, uses a loop, and a throw, which need C++14 relaxed-constexpr rules. CMakeLists.txt sets CMAKE_CXX_STANDARD 11 for the test/benchmark build, which predates that; the plain runtime unformat() call compiles fine under C++11. · any -- portable C++, no SIMD/intrinsics; MSVC/GCC/Clang are detected via macros only to pick inline/noinline/restrict hints, with a generic fallback for other compilers

**Vs siblings:** Pick Unformat over Boost.Regex, RE/flex, or REAL when you're pulling a few typed fields out of a fixed-shape string and don't need any real regex syntax (wildcards, classes, alternation) -- it's a smaller, dependency-free single header, where the siblings are full regex engines (or, for RE/flex, a code-generation tool) sized for genuine pattern-matching workloads.

**Gotchas:**
- The string_view/char scan path has no null-terminator check while hunting for a placeholder's end delimiter -- malformed input that never contains that delimiter can read out of bounds (verified in unformat.h's unformat_arg_scan<ay::string_view> specialization).
- Exceeding 16 '{}' placeholders throws a raw string literal ("Max number of {} has been exceeded.") from the format constructor -- a compile error in a constexpr context, an untyped throw at runtime.
- ay::string_view is a bare {const char* data; size_t size;}, non-owning into the original input buffer -- it dangles if the source string is freed, reallocated, or goes out of scope.
- CMakeLists.txt declares C++11 but constexpr make_format needs C++14 relaxed-constexpr to actually compile as constexpr; verify your compiler's effective standard before relying on the compile-time path.

**Status:** Actively maintained as of March 2026, with recent commits micro-optimizing numeric parsing and the pow10 tables; public-domain (Unlicense) and small enough (one header) to vendor and maintain yourself even if upstream activity stops.

[repo](https://github.com/adamyaxley/Unformat) · [benchmark](https://github.com/adamyaxley/Unformat/blob/master/README.md)

### sorting

#### fluxsort  `C`  `Unlicense`  `stale`  `Tier C`

Stable branchless quicksort/mergesort hybrid with a qsort-style C interface, claimed ~3x faster than std::stable_sort on random ints.

**Beats:** std::stable_sort — Author's own bench.c (wolfsort benchmark suite), compiled with g++ -O3 -w -fpermissive on GCC 7.5.0/Ubuntu 18.04 under WSL, hardware unstated: best-of-100 sorting 100,000 random 32-bit ints took 0.001906s for fluxsort vs 0.006113s for std::stable_sort (~3.2x); on ascending-order input, 0.000044s vs 0.000804s (~18x); 64-bit random ints were 0.002032s vs 0.006008s (~3.0x).

**How:** A top-down analyzer first checks for fully ordered/reversed runs and per-quarter presortedness, falling back to its sibling quadsort when a segment is mostly ordered. Partitioning is quicksort-style but partially in-place: elements <=pivot are written back in place and elements >pivot go to an auxiliary swap buffer, which cuts the branch-misprediction cost that plagues classic quicksort and gives memory-level parallelism on the writes. Pivots are chosen via a branchless quasimedian-of-9 (up to a median of 1024 for large partitions, an approximation of cbrt(n)), and partitions under 96 elements are sorted with quadsort's branchless small-array routine; a 1/16 partition-imbalance guard bounds the worst case to n log n.

**Use it when:**
- Stable sorting of primitive fixed-width integers, longs, or doubles (8/16/32/64-bit, long double) where you would otherwise use std::stable_sort
- Arrays from ~10K to 10M elements of random or partially-ordered data on x86-64/GCC, where extra O(n) scratch memory is affordable
- Data with exploitable structure - ascending/descending runs, sawtooth, pipe-organ patterns - where the analyzer gives the largest (10-18x) gains
- C/C++ code that can vendor a small C source drop and compile it with GCC -O3 (the author's tuned toolchain)
- Offline/batch sorting where a first-party-benchmarked throughput gain is sufficient evidence, not latency-critical or safety-certified code

**Skip it when:**
- You need the actual std::stable_sort C++ template API (iterators, allocators, arbitrary value types by move) - fluxsort is a C function with the qsort comparator contract, a code change, not a header swap
- Memory is constrained: fluxsort allocates n elements of swap memory (shared with quadsort); if allocation fails it silently falls back to quadsort's slower in-place rotations. Use blitsort (same author) for a true in-place stable sort
- Your comparator is subtraction-based (`a - b`) or otherwise not a strict, overflow-safe ordering - reported "bugs" (issue #10 buffer overflow, issue #4 stability failure) both turned out to be caller comparator mistakes, but they show how easy this footgun is to hit
- You need current, independently verified performance evidence: the project is stale (last commit 2024-07-27) and every published benchmark is first-party (author's own bench.c/wolfsort suite) on an old GCC 7.5.0/WSL toolchain with hardware unstated
- You're sorting only unsigned 32-bit ints at very large scale and can use radix sorting instead - the README itself says wolfsort (adaptive radix, same author) beats fluxsort on 8/16/32-bit types, and crumsort beats it if stability isn't required

**Integration:** header-only · none (fluxsort.h textually includes fluxsort.c and bundles quadsort.h/quadsort.c for the small-array/run fallback; all four files must sit in the same directory) · Plain C (no version stated beyond needing stdlib.h/string.h/assert.h); author recommends compiling with gcc -O3 for the numbers claimed - the README's own clang-10 benchmark shows some fluxsort/quadsort routines 2-3x slower under clang · any (portable C, no SIMD/intrinsics in the header); all published benchmarks are x86-64 (WSL/Ubuntu)

**Vs siblings:** Pick fluxsort over the unstable/radix/SIMD siblings (BlockQuicksort, IPS4o, x86-simd-sort, LearnedSort, poor-circle/radix_sort) when you need a stable, portable scalar C sort rather than raw unsigned-int throughput. Prefer quadsort itself, its stablemate, when the data has long ordered runs or is strings/objects (README: quadsort's branchless merge beats fluxsort there); fluxsort's edge is random or low-cardinality data plus the same qsort-style interface.

**Gotchas:**
- Comparator must be a real strict ordering that returns a consistent sign for all inputs; `a - b`-style comparators on 64-bit values silently truncate/overflow to int and cause out-of-bounds writes or unstable results (reported as a fluxsort bug in issue #10, root-caused to the caller's comparator)
- fluxsort_prim only covers 32/64-bit signed/unsigned integers (size = sizeof(int) or sizeof(long long), +1 to select unsigned); anything else needs fluxsort_size with a by-reference comparator, same as sorting an array of pointers
- Falls back silently to quadsort (still stable, but in-place via rotations) if the swap-memory malloc fails - a correctness safety net that is also a silent performance cliff
- A closed 2024 issue shows a Rust-glue port mismapped its comparator into fluxsort's internal contract and produced an apparent stability failure; the C library itself is not the source of that bug, but it illustrates how fragile porting the comparator convention is

**Status:** Stale (last commit 2024-07-27) but Unlicense (public-domain) makes it safe to freeze and vendor; the only known-good configuration is the author's GCC 7.5.0 -O3 toolchain, and no independent benchmark against std::stable_sort was found.

[repo](https://github.com/scandum/fluxsort) · [benchmark](https://github.com/scandum/fluxsort#benchmarks)

#### quadsort  `C`  `Unlicense`  `stale`  `Tier C`

Stable branchless bottom-up adaptive merge sort in C, beating std::stable_sort on random and partially ordered arrays.

**Beats:** std::stable_sort — On WSL2/Ubuntu 18.04 with g++ 7.5.0 (-O3 -w -fpermissive), the author's own wolfsort bench.c measured quadsort at 0.005664s vs std::stable_sort's 0.013871s (best-of-50) sorting weighted random arrays of 513-1024 32-bit ints, about 2.4x, with roughly 2.0-4.9x across the full 1-4096 item weighted sweep; no CPU model is stated. The README's larger 100,000-element, 11-distribution table (~4-16x claims) is mislabeled 'fluxsort' in its row data despite a 'quadsort' bar-graph caption, so those bigger numbers cannot be confidently attributed to quadsort itself.

**How:** An 8-element analyzer detects ascending or descending runs using a 4-comparison bitmask trick, cutting branch mispredictions to about 0.2 per 8 elements versus ~3.2 for naive comparisons, and exits with pre-sorted 8-element blocks. Small blocks are combined with branchless swap and 'parity merge' macros, then merged bottom-up with a single reusable O(n) swap buffer (like std::stable_sort's own auxiliary buffer) instead of per-level allocation. The branchless macros are written as GCC-style conditional stores on gcc and as ternary expressions on clang, so codegen and speed differ by compiler.

**Use it when:**
- Large arrays (100K+) of primitives on gcc/x86 where std::stable_sort's overhead is measured to be a bottleneck
- Partially ordered input (ascending/descending runs, sawtooth, pipe-organ patterns) where the run-detecting analyzer pays off most
- C codebases already built around qsort-style comparators, or C++ call sites that can pass contiguous arrays of PODs
- Fixed-width 32/64-bit integer arrays, via quadsort_prim, to skip comparator call overhead entirely
- Projects fine vendoring a small, unlicensed (public-domain) header/source pair instead of linking a library

**Skip it when:**
- Call sites that need std::stable_sort's actual iterator/comparator signature over arbitrary containers, not just contiguous arrays
- Bit-reversal-ordered input: the vendor's own benchmark table shows quadsort slower than std::stable_sort there
- Building with clang instead of gcc: author states the branchless merge/small-sort routines run 2-3x slower under clang
- Need current, independently reproduced numbers: last commit 2024-07-27 ('stale'), sole benchmark is first-party with no CPU stated, and the README's big 100,000-element per-distribution table is mislabeled 'fluxsort' even though its graph is captioned 'quadsort'
- Memory-constrained sorts expecting an in-place win: quadsort still needs an O(n) auxiliary swap buffer, same as std::stable_sort

**Integration:** header-only (quadsort.h #includes quadsort.c internally; single #include "quadsort.h" is enough) · none (stdlib.h, stdio.h, assert.h, errno.h, float.h, string.h only) · plain C (no C99/C11-specific features observed); README benchmarks used GCC 7.5.0 and clang 10 with -O3; the C++ bench harness needed -fpermissive to compile the C header as C++ · any target with a C compiler; portable C with no SIMD intrinsics, but branchless codegen and measured speed are tuned for gcc/x86 (2-3x slower merge/small-sort routines under clang per the author)

**Vs siblings:** Pick quadsort over the same author's fluxsort when you specifically want the mergesort half without fluxsort's quicksort partitioning (fluxsort itself is the faster average-case hybrid per the vendor's own comparisons); pick quadsort over BlockQuicksort, Boost.Sort/spreadsort, IPS4o, LearnedSort, or x86-simd-sort specifically when stability is required, since those all target unstable std::sort rather than std::stable_sort.

**Gotchas:**
- QUAD_CACHE (default 262144) gates performance for pointer/struct sorts via quadsort_size; the header comments say it needs tuning for large arrays and L3 cache size
- Branchless macros branch on the __clang__ define, so gcc and clang run genuinely different code paths for the same source, not just different optimizer output
- quadsort and quadsort_size malloc their own O(n) swap buffer internally with no custom-allocator hook, and assert() on malloc failure rather than returning an error code
- A user-filed correctness question about cross_merge's tail pointer possibly running past the block's tail (issue #20) is closed but its resolution isn't confirmed in the visible thread

**Status:** Maintenance is stale (last commit 2024-07-27, no recent activity) but the code is Unlicense (public domain) and a small, single header/source pair, cheap to vendor and freeze indefinitely.

[repo](https://github.com/scandum/quadsort) · [benchmark](https://github.com/scandum/quadsort#benchmark-quadsort-vs-stdstable_sort-vs-timsort)

#### vxsort-cpp  `C++`  `MIT`  `abandoned`  `Tier C`

AVX2/AVX-512 vectorized quicksort for primitive arrays; beats a ported .NET GC introsort, not std::sort.

**Beats:** scalar introsort ported from the .NET CoreCLR GC (gcsort::introsort_orig), not std::sort — The README's reported ~4.5-4.8x speedup (e.g., 1M int64: 53.08ns/elt scalar vs 11.54ns/elt with 8x unroll; measured on an AMD Ryzen 9 3950X @3.8GHz in a June 2020 benchmark) is against gcsort::introsort_orig, a scalar port of the .NET CoreCLR GC's introsort — not std::sort. No compiler version is stated, and no std::sort numbers are published even though the current repo contains a BM_fullsort.stdsort.cpp benchmark file.

**How:** Branchless AVX2/AVX-512 vectorized partitioning (the 'partition machine') replaces std::sort's scalar Hoare partition, falling back to an in-register bitonic sorting network for blocks under 1024 elements instead of insertion sort. A depth-limited heap-sort fallback guards worst-case recursion, and an Unroll template parameter (1-12) controls how many vector lanes are processed per partitioning step, trading code size for fewer loop-carried dependencies.

**Use it when:**
- Sorting large arrays (benchmarked 4,096 to 1,048,576 elements) of raw i16/u16/i32/u32/i64/u64/f32/f64 on x86-64 with AVX2 or AVX-512 available
- Throughput-bound batch sorts where you can pick the ISA/unroll variant at compile time and don't need a comparator or non-primitive keys
- You want per-element latency down for pointer-sized keys (README: int64 drops from ~53ns/elt scalar introsort to ~11.5ns/elt with unroll x8, unverified against std::sort)
- You're OK vendoring a small, currently unmaintained C++ codebase (MIT) and rebuilding it for your target ISA

**Skip it when:**
- Need a drop-in std::sort replacement with comparators, custom types, or non-x86 targets — no comparator API, and NEON/AArch64 support is stubbed (issue #1, open since 2020) but not implemented
- Need std::sort-relative numbers to justify the switch — README only compares against a self-ported CoreCLR-GC scalar introsort, not std::sort, and no std::sort numbers are published despite a BM_fullsort.stdsort.cpp benchmark existing in the repo
- Care about active maintenance — the default branch's last commit is 2023-05-10; only an unrelated-history 'nextgen' branch has recent (2026) activity
- Small arrays under 4K elements (not benchmarked) or workloads needing a stable sort — this is in-place but not stable, and uses a fixed-size internal scratch buffer sized per template instantiation
- Want CI confidence out of the box — an open 'Build fail' issue (#2) shows the bench/test build breaking against a newer clang/CMake/googlebenchmark combination

**Integration:** static lib · cpu_features (Google, ISA detection), fmt; googlebenchmark and googletest additionally for bench/tests only · C++20 (CMakeLists sets CMAKE_CXX_STANDARD 20), CMake 3.24+; clang recommended by the README, GCC also handled in CMakeLists · x86-64 with AVX2 or AVX-512 (ISA chosen per template instantiation at compile time); AArch64/NEON detection is present in demo.cpp but the sort call is unimplemented

**Vs siblings:** Pick this only if you specifically want an AVX2/AVX-512 partition-plus-bitonic-network vectorized quicksort port of .NET's VxSort for raw numeric arrays and don't need comparator/generic-type support; x86-simd-sort, BlockQuicksort, quadsort, and fluxsort all publish real std::sort or std::stable_sort comparisons and are more actively maintained, so prefer one of them when the baseline claim matters or adoption/maintenance risk is a concern.

**Gotchas:**
- ISA is selected at compile time via which header you include (vxsort.avx2.h vs vxsort.avx512.h) and the vxsort_targets_enable_*.h wrapper; using the wrong one for the running CPU is a caller error (the demo does its own cpu_features runtime check before choosing)
- Only built-in numeric types appear in the benchmark/test suite (i16/u16/i32/u32/f32/i64/u64/f64); no evidence of support for arbitrary structs, strings, or custom comparators
- Internally falls back to heap_sort past a depth limit and to a bitonic-network small-sort under 1024 elements — behavior isn't a single flat algorithm the way std::sort's introsort is, though this is invisible at the call site
- Open issue #2 shows the benchmark/test build breaking under newer clang/CMake due to a googlebenchmark C-dialect flag mismatch — unrelated to the sort code but relevant if you try to reproduce the published numbers

**Status:** Abandoned on its default branch since 2023-05-10 (later activity moved to an unrelated-history 'nextgen' branch); MIT-licensed and small/self-contained enough to vendor, but only 33 stars and an open build-fail issue against its bench/test harness.

[repo](https://github.com/damageboy/vxsort-cpp) · [benchmark](https://github.com/damageboy/vxsort-cpp#results-ryzen-3950x-38ghz)

#### x86-simd-sort (numpy/x86-simd-sort)  `C++`  `BSD-3-Clause`  `active`  `Tier C`

AVX-512/AVX2 SIMD quicksort/select library beating std::sort on primitive arrays and key-derived struct sorts (object_qsort).

**Beats:** std::sort — Numbers come from x86-simd-sort's own README benchmark (benchmarks/bench-objsort.hpp, Google Benchmark, run with --benchmark_filter=*obj*), comparing object_qsort against std::sort on arrays of 3D Point structs (float or double x/y/z) sorted by one coordinate or by Manhattan, Euclidean, or Chebyshev distance from the origin, on an unspecified x86 processor with AVX-512 and no disclosed compiler or flags: up to ~5x faster for float (32-bit) keys and ~4x for double (64-bit) keys sorting by one coordinate, up to ~10x faster sorting by Euclidean distance.

**How:** Built-in-type routines vectorize quicksort partitioning using AVX-512 compressstore instructions (with an AVX2 fallback), based on two cited SIMD-partitioning papers, and drop to bitonic sorting networks on AVX-512/AVX registers for arrays below a size threshold (64-512 elements). object_qsort does not vectorize struct comparisons directly: it extracts each object's key into a separate array, sorts the resulting (key, index) pairs with the SIMD keyvalue_qsort, then permutes the original object array into place with a scalar cycle-following swap loop. Its speedup therefore comes from the primitive keyvalue sort plus, for expensive keys like Euclidean distance, auto-vectorized key computation, not from vectorizing the object comparisons themselves.

**Use it when:**
- Sorting arrays of built-in 16/32/64-bit ints, floats, or doubles (or key-value pairs) on x86-64 hardware with AVX2 or AVX-512, where std::sort's per-element comparator overhead dominates
- Sorting an array of structs by one scalar key -- a single member or a computed metric like Euclidean/Manhattan/Chebyshev distance -- via object_qsort's key-extraction lambda
- Need argsort/argselect/partial_qsort with built-in NaN placement control (nans_last) instead of hand-rolling NaN partitioning around std::sort/std::nth_element
- Batch or offline sorts where allocating O(N) extra memory for keys and an index array is acceptable
- Comfortable depending on code already proven at NumPy/PyTorch/OpenJDK vendoring scale rather than a smaller, newer project

**Skip it when:**
- Target hardware lacks AVX2/AVX-512, or is not x86-64 (no aarch64/ARM support)
- Sort key isn't reducible to one scalar of 32 or 64 bits -- object_qsort's key_func must return exactly float/double/(u)int32/64, not a multi-field comparator
- Memory-constrained settings: object_qsort needs O(N) extra space (a key array plus a uint32/64 index array) on top of the object array itself
- Need numbers independently verified on disclosed hardware/compiler: the object_qsort chart names only 'a processor with AVX-512', no CPU model, compiler, or flags, and the numbers are first-party
- Care about scaling on adversarial input distributions: an independent 2023 analysis (Voultapher sort-research-rs) found worse-than-O(N log N) scaling for the primitive AVX-512 qsort on a random_p5 pattern

**Integration:** header-only (src/x86simdsort-static-incl.h, compile-time AVX2/AVX-512 selection) or static/shared lib (Meson build under lib/, runtime CPUID dispatch) · none for the core routines; googletest and Google Benchmark (>=1.9.2) only if building the optional test/benchmark suite; OpenMP optional for parallelizing qsort/argsort/keyvalue_qsort · C++17; GCC 8+ (GCC 12+ required for _Float16/AVX-512FP16), Clang 8.0+, MSVC 2019 16.8+, or Intel icx · x86-64 with AVX2 or AVX-512 (exact subset varies: skylake-avx512 for 32/64-bit, icelake-client for 16-bit, sapphirerapids for _Float16); no aarch64/ARM

**Vs siblings:** A maintainer directly asked how this compares to vxsort-cpp (issue #12) and no comparison was ever produced, so there's no first-party head-to-head with that sibling. Pick x86-simd-sort over the other primitive-array sorters in this catalog (BlockQuicksort, Boost.Sort spreadsort, IPS4o, LearnedSort, fluxsort, quadsort, radix_sort) specifically when the workload is 'sort a struct by one field or a derived distance metric' via object_qsort, not a flat array of ints -- none of the other siblings' benchmarks target that struct/key-sort shape.

**Gotchas:**
- object_qsort's gain shrinks as sizeof(T) grows or the key gets cheap to compute relative to swap cost, since the final struct permutation is a scalar cycle-following swap loop, not SIMD
- object_qsort's key_func return type must be exactly 32 or 64 bits (float/double/int32/int64/uint32/uint64) or the call fails a static_assert at compile time
- For built-in-type routines, hasnan defaults to false; if the array actually contains NaNs and hasnan isn't set true, behavior is undefined
- GCC 16.0.1 with LTO enabled reportedly failed to build (issue #224, closed without a posted fix) when vendored into NumPy, due to an 'inlining failed: target specific option mismatch' error on an always_inline comparator

**Status:** Actively maintained (last commit 2026-06-25); BSD-3-Clause. 'Copyable' fits since the src/ headers can be vendored standalone at compile time -- as NumPy, PyTorch, and OpenJDK already do -- while the runtime-dispatching library form requires a Meson build.

[repo](https://github.com/numpy/x86-simd-sort) · [benchmark](https://github.com/numpy/x86-simd-sort/blob/main/README.md)

## Copyleft

### sorting

#### BlockQuicksort  `C++`  `GPL-3.0`  `abandoned`  `Tier A`

In-place Quicksort using block-buffered Hoare partitioning to avoid branch mispredictions; ~88% more elements/s than GCC std::sort on random ints.

**Beats:** std::sort — On GCC 4.8.4 (-O3 -march=native) on an Intel Core i5-2500K (4 cores, Ubuntu 14.04.4), the optimized BlockQuicksort variant needs ~45 ns/element vs ~85 ns/element for the repo's bundled copy of GCC 4.7.2's std::sort at n=2^28 on random 32-bit ints (~88% more elements sorted per second); smaller but still positive gains hold on 10-dim Vector and 21-field Record comparators for the mo-sqrt(n), duplicate-check variant, and std::sort wins on sorted/nearly-sorted input.

**How:** partition.h's hoare_block_partition_* functions compare a BLOCKSIZE=128 chunk of elements against the pivot into small fixed-size index buffers first, then do the swaps in a second, branch-free loop, so the CPU's branch predictor never has to guess the per-element comparison outcome during the swap phase. Pivot selection samples a median of ~sqrt(n) elements (median.h), and the qsort_double_pivot_check main loop (quicksort.h) adds a check for duplicate-heavy partitions adapted from Elmasry/Katajainen/Stenmark's Tuned Quicksort, falling back to insertion sort/std::partial_sort at small sizes like libstdc++'s introsort.

**Use it when:**
- Sorting large (n in the hundreds of millions) arrays of random 32-bit ints where per-element comparison is cheap and branch mispredictions dominate cost — the paper's largest reported gain (~88%) is at n=2^28.
- Multi-field comparators (the paper's 10-dim Vector / 21-field Record benchmarks) where smaller but still positive gains hold for the mo-sqrt(n),dc variant.
- Batch/offline throughput-oriented sorts where an unstable, in-place sort is acceptable and you're willing to hand-integrate a research header into your own call sites.
- As a reference implementation or benchmarking baseline for new sequential sort research — it's already used as the 'closest sequential competitor' in the IPS4o paper.
- Random or otherwise non-sorted input distributions; the paper itself reports std::sort wins on sorted/nearly-sorted input.

**Skip it when:**
- Need stability (equal elements keep relative order) — not stable, no stable variant provided.
- Sorted or nearly-sorted input — the input record's own claim notes std::sort wins there.
- Want a true drop-in replacement for std::sort with no call-site changes — this exposes sort() under its own namespace, not an overload of std::sort.
- Production/commercial use needing an actively maintained, permissively-licensed dependency — repo abandoned since Nov 2021 with two issues open and unanswered since 2019, and it's GPL-3.0 (the branch-avoidance technique itself has since been reimplemented under more permissive licenses in pdqsort and PPQSort).
- Want to just include one clean header — mixing more than one *.h++ interface file in the same translation unit causes duplicate-template-definition compile errors (open issue #6, unresolved).

**Integration:** source-drop · none external; each *.h++ variant needs matching repo-internal headers (quicksort.h, partition.h, median.h, insertionsort.h, rotations.h) included alongside it · C++11 (repo makefile: g++ -O3 -std=c++11 -march=native; benchmarked with GCC 4.8.4) · x86-64 only benchmarked (-march=native, Intel Core i5-2500K); portable C++11 templates with no explicit SIMD intrinsics observed — the branch-avoidance win depends on the compiler auto-vectorizing/optimizing the small fixed-size block-classification loop, so results are compiler- and arch-dependent

**Vs siblings:** Pick this over Boost.Sort/IPS4o/LearnedSort/etc. only when you specifically want the original peer-reviewed (ESA 2016 / JEA 2019) branch-avoidance partitioner — e.g. reproducing or benchmarking against it as IPS4o did — since the technique itself is now available in actively maintained, permissively-licensed form in pdqsort and PPQSort; for production sequential sorting prefer fluxsort or a pdqsort-family library instead of this abandoned GPL-3.0 repo.

**Gotchas:**
- Including more than one *.h++ interface header in the same translation unit triggers 'redefinition of template' errors from median.h (issue #6, open since 2019).
- Release-flag builds compile with -DNDEBUG, so the assert() sanity checks scattered through partition.h are stripped in the benchmarked configuration.
- The README recommends only blocked_double_pivot_check_mosqrt.h++ and blocked_simple.h++ out of ~40 header variants; a user asked in issue #5 (2019, still open) for clearer guidance on which variant to actually use.
- BLOCKSIZE (128) and pivot-sample-size constants are compile-time #defines tuned for the paper's int/Vector/Record types on one CPU; other key types or hardware may need retuning.

**Status:** Abandoned since its last commit on 2021-11-29, with two open issues unanswered since 2019, but classified 'copyable' — the source is small enough to vendor directly if your project's license tolerates GPL-3.0.

[repo](https://github.com/weissan/BlockQuicksort) · [benchmark](https://drops.dagstuhl.de/opus/volltexte/2016/6389/pdf/LIPIcs-ESA-2016-38.pdf)

#### LearnedSort  `C++`  `GPL-3.0`  `abandoned`  `Tier A`

CDF-model-based sort for numeric arrays, ~4x faster than std::sort on random data, ~15-20x on sorted/duplicate data.

**Beats:** std::sort — On 50M double-precision keys via Google Benchmark (GCC 9.3.0-10ubuntu2, CMake Release with -O3 -march=native -mavx, Intel Xeon Gold 6150), LearnedSort ran ~1080-1150ms vs std::sort's ~4850-5030ms (~4.2-4.6x) across Uniform, Exponential, Mixture-of-Gaussians, Zipf-0.75, and TwoDups, and ~50-60ms vs std::sort's ~750-1000ms (~15-20x) on Sorted, ReverseSorted, and Identical -- all read off the README's bar chart (plots/perf_charts.png), which prints no exact numeric labels.

**How:** Builds a two-layer 'recursive model index' (RMI): a root linear model plus, by default, 1000 leaf linear models trained on a 1% sample of the keys, which together approximate the empirical CDF. Each key's model-predicted CDF value picks one of ~1000 buckets directly (O(1) per key instead of O(log n) comparisons), the array is partitioned into those buckets in one pass, and each bucket is finished with std::sort/insertion sort. Separately, sort() first does a linear is_sorted/is_reverse_sorted check and returns immediately if it hits, which is why Sorted/ReverseSorted/Identical inputs are ~15-20x faster than std::sort -- that path bypasses the CDF model entirely.

**Use it when:**
- Large batches (tens of millions+) of primitive numeric keys (double/int/long) with no attached payload
- Data from a reasonably smooth/well-behaved distribution (uniform, exponential, Gaussian mixture, Zipfian, moderate duplicates) where the RMI's CDF approximation is accurate
- One-off or batch/offline sorts where the model-training cost amortizes over a large input, not per-call microsorts
- You can vendor a small header-only GPL-3.0 dependency and your project tolerates copyleft
- x86-64 Linux/GCC builds with AVX and -march=native, matching the environment this was actually benchmarked on

**Skip it when:**
- Sorting records/structs with payloads or string keys -- explicitly unsupported per the README's Limitations section
- Small inputs -- below roughly fanout x threshold (1000 x 100 = 100,000 elements by default) it just calls std::sort, so there's no upside
- GPL-3.0 is unacceptable for the target codebase -- heavier copyleft than most sibling sort libraries in this catalog
- Need active maintenance -- no commits since August 2021, all filed issues closed, unmaintained academic prototype
- Sorted, reverse-sorted, or all-duplicate inputs where you want a general-purpose winner -- the project's own chart shows IS4o matching or beating LearnedSort there

**Integration:** header-only · none for the sort itself (STL only, include/learned_sort.h + rmi.h + utils.h); the repo's benchmark/test harness additionally pulls in Google Benchmark, Google Test, and several third-party sort implementations, but those aren't needed to call learned_sort::sort · C++20 (CMakeLists.txt sets CMAKE_CXX_STANDARD 20); benchmarked with GCC 9.3.0-10ubuntu2 · Only tested on Linux (RHEL 7, Ubuntu 20.04); Release flags include -march=native -mavx, so x86-64 with AVX is assumed. A Windows/MinGW-w64 GCC10 user hit a correctness bug (issue #16), since fixed

**Vs siblings:** Pick LearnedSort over IPS4o/BlockQuicksort/x86-simd-sort/radix_sort when you have large batches (10M+) of doubles or ints from a smooth distribution and accept GPL-3.0 plus an unmaintained codebase for the ~4x win; for sorted/duplicate-heavy or adversarial data, or if you need ongoing support, IS4o matches or beats it on those inputs per LearnedSort's own benchmark chart.

**Gotchas:**
- Automatically short-circuits to std::sort for inputs at or below ~fanout*threshold elements (100,000 by default) or when RMI training fails, so the learned path silently never runs on small inputs
- The huge Sorted/ReverseSorted speedups come from an explicit is_sorted()/is_reverse_sorted() linear-scan pre-check with early return, not from the CDF model doing work
- Historically had several correctness bugs specific to integer key types (slope underflow, int-division in RMI training, failures with many repeated keys) -- all filed as issues and fixed via PRs by mid-2021, but there's been no activity since to catch anything similar
- No payload/tuple or string-key support (README 'Limitations'); only bare numeric arrays are sortable

**Status:** Abandoned academic prototype: no commits since August 2021 and every filed issue is closed with no further activity, but it's a small header-only, GPL-3.0 library, so it's easy to vendor and freeze at the last known-good GCC 9/10 toolchain.

[repo](https://github.com/anikristo/LearnedSort) · [benchmark](https://github.com/anikristo/LearnedSort/blob/master/plots/perf_charts.png)

## Copyleft — Unverified claims (tier C/D)

### sorting

#### poor-circle/radix_sort  `C++`  `GPL-3.0`  `abandoned`  `Tier C`

Header-only C++20 LSD byte-radix sort for ints/floats/pointers/pairs/structs; drop-in call syntax beats std::sort.

**Beats:** std::sort — First-party benchmark (author's benchmark/benchmark.cpp, MSVC 2022 release build, Intel i9-9900K @4.7GHz / DDR4-3000): sequential radix_sort sorted 1e9 int32 elements in 6402ms vs std::sort's 91407ms (~14.3x) and std::stable_sort's 82896ms (~12.9x); the margin narrows to ~5.2x on uint64 and ~2.9x on pair<uint64,uint64>, and measured against std::sort(par) instead of sequential std::sort the parallel win is only ~4.8x on int32, with radix_sort(par) slightly slower than std::sort(par) on pair<uint64,uint64> (24608ms vs 23532ms).

**How:** LSD (least-significant-byte-first) radix sort: one 256-bucket counting-sort pass per byte of the key (histogram, prefix-sum, scatter), so it never does a per-element comparison. The count and scatter loops are manually unrolled 4-wide with Duff's device, and each pass ping-pongs the data between the input and an auxiliary buffer rather than sorting in place. The `std::execution::par` overload shards the range across std::async tasks that count locally, merge per-thread histograms, then scatter concurrently for each byte pass, layering thread parallelism on top of the linear-time algorithm.

**Use it when:**
- Sorting large (1e6+) arrays of int32/uint32/float/pointer keys, where the key type already has or can get a radix_trait
- Composite keys such as std::pair<K,V> or small structs, where a byte-radix trait can be written for the sort key
- Throughput-bound batch sorting, sequential or with std::execution::par, on x86 with MSVC-class compilers
- Need for stable, comparator-free sorting of fixed-width keys rather than an arbitrary Compare predicate
- Willing to vendor one C++20 header (GPL-3.0 permitting) into the project

**Skip it when:**
- Need arbitrary/custom comparators (sort by a runtime-selected field or lambda) — radix_sort needs a compile-time radix_trait, not a Compare object
- Wide keys (64-bit ints, pair<uint64,uint64>): sequential speedup drops to ~2.9-5.2x, and radix_sort(par) can be slightly slower than std::sort(par) (measured 24608ms vs 23532ms on 1e9 pair<uint64,uint64>)
- Memory-constrained workloads: needs an O(n) auxiliary buffer the size of the input unless the caller supplies one
- Non-MSVC toolchains: the author only benchmarked MSVC STL on Windows, not libstdc++/libc++
- Projects needing active upstream support: single author, no commits since Jan 2022, one open usage question unanswered

**Integration:** header-only · none (standard library only: <vector>, <array>, <execution>, <future>, <memory>, <cstring>, <limits>) · C++20 (uses std::unsigned_integral/signed_integral/floating_point concepts and requires-clauses) · any (portable C++20, no SIMD or platform intrinsics); author only benchmarked Windows/MSVC x86-64

**Vs siblings:** Unlike the comparison-based siblings (BlockQuicksort, IPS4o, LearnedSort, x86-simd-sort) or the stable-sort replacements (fluxsort, quadsort), radix_sort is the only non-comparison LSD byte-radix sort in this set; pick it when the key is an integer, float, pointer, or a pair/struct you can describe with a byte-radix trait and you want the largest win on 32-bit keys, and prefer a comparison-sort sibling for 64-bit/wide keys or arbitrary comparators where radix_sort's edge shrinks or vanishes.

**Gotchas:**
- std::execution::par is accepted only as a dispatch tag; it always drives its own std::async tasks internally rather than routing through a standard execution-policy engine
- demo/demo.cpp's custom-struct example does not compile as written (its radix_trait<mystruct> and my_trait reference undefined p1/p2 identifiers) — follow the README's mystruct pattern instead
- Signed integers and floats flip the sign/exponent bit (XOR 0x80) inside the built-in radix_trait so byte order matches numeric order; a hand-written trait for a new type must replicate this or sort order breaks silently
- Without a caller-supplied buffer, every call allocates a full extra copy of the input (sizeof(value_type) * n bytes)

**Status:** Abandoned since its last commit on 2022-01-31 (single author, one unanswered open issue); GPL-3.0-licensed and a single header, so still copyable, but expect no fixes or support.

[repo](https://github.com/poor-circle/radix_sort) · [benchmark](https://github.com/poor-circle/radix_sort#benchmark)
