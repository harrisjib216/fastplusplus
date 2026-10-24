# Concurrent queues and locks

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::mutex, std::atomic, std::queue+mutex, std::condition_variable  
**12 entries:** 6 tier A · 0 tier B · 6 tier C · 0 tier D · 12 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**oneTBB concurrent_bounded_queue**](uxlfoundation-onetbb.md) | Bounded/blocking FIFO queue in Intel's oneTBB parallelism library; non-blocking try_push/try_pop mode cuts round-trip latency \~3.9x vs std::mutex. | **A** | C++ | Apache-2.0 | 🟢 active |
| 2 | [**moodycamel::ReaderWriterQueue**](cameron314-readerwriterqueue.md) | Header-only lock-free SPSC queue for C++11; beats a mutex-guarded queue by \~7x in ping-pong latency. | **A** | C++ | BSD-2-Clause | 🟢 active |
| 3 | [**atomic_queue**](max0x7ba-atomic-queue.md) | Header-only lock-free MPMC/SPSC ring-buffer queues beating std::mutex-guarded queues by 4-10x in latency and throughput. | **A** | C++ | MIT | 🟢 active |
| 4 | [**Boost.Lockfree**](boostorg-lockfree.md) | Boost's lock-free MPMC/SPSC queue and stack family; beats std::mutex on latency, not contended MPMC throughput. | **A** | C++ | BSL-1.0 | 🟢 active |
| 5 | [**xenium**](mpoeter-xenium.md) | Header-only lock-free MPMC queue templates (Michael-Scott, Ramalhete, Vyukov) beating std::mutex latency 2.5-5.7x. | **A** | C++ | MIT | 🟡 stale |
| 6 | [**contention_free_shared_mutex (AlexeyAB/object_threadsafe…**](alexeyab-object-threadsafe.md) | Per-thread sharded reader-writer lock and object wrapper claiming up to \~10x std::shared_mutex throughput under read-heavy contention. | **A** | C++ | Apache-2.0 | 🔴 abandoned |
| 7 | [**Cosmopolitan Libc (pthread_mutex_t)**](jart-cosmopolitan.md) | Portable libc whose pthread_mutex_t (Google nsync underneath) beat glibc 2.7x and musl 9.6x on a contended 30-thread lock test. | **C** | C | ISC | 🟢 active |
| 8 | [**moodycamel::ConcurrentQueue**](cameron314-concurrentqueue.md) | Lock-free MPMC C++11 queue with per-producer sub-queues and bulk ops, beating boost::lockfree::queue on throughput. | **C** | C++ | BSD-2-Clause OR BSL-1.0 | 🟢 active |
| 9 | [**eventpp::SpinLock (eventpp GeneralThreading policy)**](wqking-eventpp.md) | Header-only spinlock policy for eventpp's EventQueue/EventDispatcher, swapping std::mutex for a std::atomic_flag test-and-set lock at &lt;=core-count thread counts. | **C** | C++ | Apache-2.0 | 🟡 stale |
| 10 | [**alignas(64) per-thread result slots against false sharing…**](paper-book-asynchronous-programming-with-cpp-false-sharing-alignas-64.md) | Pad each thread's result slot to its own 64-byte cache line with alignas(64) to stop false sharing between packed slots. | **C** | C++ | MIT | 🟡 stale |
| 11 | [**SPSC lock-free ring buffer with cached head and tail…**](paper-book-asynchronous-programming-with-cpp-spsc-queue-cached-indices.md) | Teaching-grade SPSC ring buffer that caches the peer's index; about 1.6x its own uncached variant in the book's run. | **C** | C++ | MIT | 🟡 stale |
| 12 | [**std::atomic counter (fetch_add, relaxed) against a…**](paper-book-asynchronous-programming-with-cpp-atomic-counter-vs-mutex.md) | Relaxed std::atomic fetch_add on a shared counter in place of a std::mutex-guarded increment; teaching idiom, not a library. | **C** | C++ | MIT | 🟡 stale |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
