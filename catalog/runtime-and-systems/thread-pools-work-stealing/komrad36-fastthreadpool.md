# FastThreadPool (komrad36)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Thread pools and work stealing](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `MIT` · 🔴 abandoned

> 183-line header: an unbounded MPMC work queue of plain function pointers with spin-bit locking; no benchmark against any thread pool.

| | |
|---|---|
| **Beats** | None named by the author; std::async, boost::asio::thread_pool and BS::thread_pool are the natural incumbents (inferred by the search agent, never compared) |
| **Claimed result** | No numbers. README: 'A super fast lock-free (though not always wait-free) thread pool.' |
| **Workload** | None: the repository contains no benchmark code and reports no measurement. |
| **Metric** | throughput |
| **Adoption** | 10 stars |
| **Last commit** | 2021-10-19 |
| **Links** | [repository](https://github.com/komrad36/FastThreadPool) |

## Verdict

Nothing was measured: the README's only claim is 'a super fast lock-free (though not always wait-free) thread pool', with no baseline, compiler, hardware or benchmark code, and no comparison against std::async, boost::asio::thread_pool or BS::thread_pool exists.

## Use it when

- You are writing your own worker threads on x86-64 and want a tiny, dependency-free MPMC queue of void(\*)() jobs to read and adapt rather than a full pool.
- Teaching or study material: a compact example of a two-lock linked-list queue with tag-bit locks and annotated (but unproven) memory orders.
- Jobs are global functions with no arguments and no results, and you already have your own sleep/wake policy for idle workers.

## Skip it when

- You need a real thread pool (worker threads, std::function or move-only callables, arguments, futures, wait-for-all): use BS::thread_pool, dp::thread_pool, riften::Thiefpool or inkooboo/thread-pool-cpp instead.
- ARM, POWER or other weakly ordered CPUs: the consumer reads the tail with relaxed loads before reading the old head's next pointer, so the C++ memory model does not guarantee it sees the link the producer published (see gotchas); only x86 TSO hides this.
- Latency-sensitive systems where a preempted thread must not stall others: a producer holding the tail tag or a consumer holding the head sentinel blocks everyone else, so despite the README it is not lock-free in the formal sense.
- Allocation-sensitive hot paths: every AddWork does a new and every RemoveWork a delete, with no allocator hook or node pooling.
- Anything that needs a measured speedup: there is no benchmark, test or comparison in the repository.

## How it is fast

It is a singly linked FIFO in the style of the Michael-Scott two-lock queue, with the two locks folded into the pointers: producers claim the tail by CAS-setting bit 0 of m_pTail, consumers claim the head by CAS-swapping m_pHead to the sentinel value 1, and waiters spin with _mm_pause. Head and tail sit on separate 64-byte cache lines (alignas(64)), so producers and consumers mostly touch different lines and an uncontended enqueue or dequeue is one CAS plus a couple of stores. Nothing in the repository measures how fast this is.

## Compared with alternatives

Pick it over inkooboo/thread-pool-cpp, nexus or BS-style pools only when you want a few dozen lines of queue code to vendor into your own x86-only worker design; every catalogued sibling (thread-pool-cpp, nexus, dp::thread_pool, riften::Thiefpool) ships worker threads, callable wrappers and at least a first-party benchmark, which this repository lacks.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C++ standard library &lt;atomic&gt;, &lt;cstdint&gt;; &lt;emmintrin.h&gt; when __SSE2__ is defined) |
| **Minimum toolchain** | C++11 (std::atomic, alignas); not documented beyond that |
| **Platforms** | any target with std::atomic; the _mm_pause spin hint is emitted only when __SSE2__ is defined (GCC/Clang on x86), so on ARM and under MSVC the spin loops have no pause or yield; memory ordering is only safe on x86 (see gotchas) |
| **Thread safety** | AddWork and RemoveWork may be called concurrently from any number of threads; construction and destruction must happen with no concurrent callers (the destructor walks and deletes the list without synchronization) |
| **Drop-in for the baseline** | no |

## Gotchas

- Memory-ordering flaw (analysis of fast_thread_pool.h, not reproduced): in RemoveWork the consumer loads m_pTail with memory_order_relaxed (L4, and relaxed CAS failure ordering) and, on seeing a tail different from the node it holds, reads pHead-&gt;m_next with acquire. The relaxed tail read creates no happens-before with the producer's release store of m_next (S4), so on ARM or POWER the consumer can see the new tail yet read a null next pointer, set m_pHead to nullptr and strand every queued and future item (RemoveWork then returns nullptr forever and the nodes leak). Making the L4 loads acquire would close it; x86 TSO never reorders the two loads.
- The head hand-off store (S9) is relaxed, so a later consumer's acquire CAS on m_pHead synchronizes with nothing and its read of the plain (non-atomic) m_f field is formally a data race under the C++ memory model; it works in practice on x86 and through address dependencies on ARMv8, but sanitizers such as TSan may flag it.
- MSVC does not define __SSE2__, so on Windows MSVC builds Pause() compiles to nothing and the spin loops busy-wait without a pause hint; RemoveWork on an empty queue returns nullptr immediately, so the caller's idle loop decides whether workers spin (the README's TODO says they should sleep).
- AddWork takes void f() (a function pointer): lambdas with captures, std::function, member functions and arguments are not accepted, and new can throw std::bad_alloc out of AddWork.

## Known shortcomings

- No numbers and no baseline; the header is a function-pointer MPMC queue rather than a thread pool, its tag-bit spinning means it is not truly lock-free, and the repo has been abandoned since 2021-10-19.
- Enricher (code reading, not reproduced): RemoveWork reads m_pTail relaxed and then pHead-&gt;m_next, so on ARM or POWER the consumer can see the new tail with a null next pointer, set head to nullptr and strand every queued item (x86 TSO hides it); the relaxed head hand-off makes the read of m_f a data race; Pause() is a no-op on MSVC (no __SSE2__ define); tag bits act as spinlocks, so it is not lock-free.

## Caveats and trade-offs

Pure assertion with no numbers and no baseline run; kept as a tier D record only because the author (komrad36) is a known performance-oriented developer. The repo has 5 commits, all on 2021-10-18 and 2021-10-19, no tests and no benchmark. Despite the name, fast_thread_pool.h (183 lines) is not a thread pool: it is an intrusive linked-list MPMC queue of plain void(\*)() function pointers with AddWork/RemoveWork; it creates no threads and has no worker loop, futures, arguments or captures, so users must write the workers themselves. AddWork and RemoveWork spin with _mm_pause on a tag bit set in the head/tail pointers, which acts as a short spinlock, so a preempted thread can stall the others (not lock-free in the formal sense despite the README). Every AddWork heap-allocates a node with new and every RemoveWork deletes one. The README's own TODOs say it 'could probably be faster with block queues' and should sleep instead of spinning when idle. The memory-order annotations (S1-S9, L1-L6) are not backed by a proof or test; L4 reads the tail with a relaxed load before reading pHead-&gt;m_next with acquire, which looked unproven on weakly ordered CPUs (not analysed further). Not comparable to std::async or BS::thread_pool in features, so any speed claim would need a like-for-like queue benchmark. [retier] Enricher (code reading): relaxed tail read followed by pHead-&gt;m_next lets a consumer on ARM or POWER see a null next pointer and strand all queued items; Pause() is a no-op on MSVC; not lock-free (tag bits spin).

fast_thread_pool.h (183 lines, header-only) is a lock-free multi-producer multi-consumer linked-list queue of plain function pointers (void (\*)()), not a full pool: no worker threads are created by the class, no arguments or return values (no std::function, no futures), one heap allocation per AddWork. Waiters spin with _mm_pause; the README itself says it should sleep instead of spin after a while (TODO) and could be faster with block queues, so idle consumers burn CPU.

## Maintenance

Abandoned after five commits on 2021-10-18 and 2021-10-19 (the last one, 'update consume operations', made m_next atomic and added the acquire load), with no issues, tests or releases; MIT-licensed and small enough to vendor, but the tail loads in RemoveWork need acquire ordering before use on ARM.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now D.
- **Tier reason:** README is a one-line assertion ('A super fast lock-free (though not always wait-free) thread pool'); the repo holds only LICENSE, README.md and fast_thread_pool.h, with no benchmark, no numbers and no baseline.
- **Verifier notes:** Metadata confirmed: MIT, 10 stars, 3 forks, 5 commits, last 2021-10-19 'update consume operations', so abandoned. Shortcomings: no numbers or baseline, it is a function-pointer queue rather than a thread pool, tag-bit spinning means it is not truly lock-free, no tests. Kept at D per keep-and-document rule (not-notable reject avoided).
- **Fields the verifier corrected:** `baseline`, `caveats`
- **Shortcomings recorded by:** verifier batch-63 (wave 11 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/komrad36/FastThreadPool>
  - <https://github.com/komrad36/FastThreadPool/commits>
  - <https://raw.githubusercontent.com/komrad36/FastThreadPool/master/fast_thread_pool.h>
- **Sources the enricher read:**
  - <https://github.com/komrad36/FastThreadPool>
  - <https://github.com/komrad36/FastThreadPool/issues>
  - <https://github.com/komrad36/FastThreadPool/commits/master>
  - <https://github.com/komrad36/FastThreadPool/commit/55670cf>
  - <https://raw.githubusercontent.com/komrad36/FastThreadPool/HEAD/README.md>
  - <https://raw.githubusercontent.com/komrad36/FastThreadPool/HEAD/fast_thread_pool.h>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/komrad36/fastthreadpool`) · [data/wave11/enrich/raw/github_com_komrad36_fastthreadpool.json](../../../data/wave11/enrich/raw/github_com_komrad36_fastthreadpool.json) (enrichment confidence 0.75)

</details>
