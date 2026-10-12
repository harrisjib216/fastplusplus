# contention_free_shared_mutex (AlexeyAB/object_threadsafe safe_ptr library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Concurrent queues and locks](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Per-thread sharded reader-writer lock and object wrapper claiming up to \~10x std::shared_mutex throughput under read-heavy contention.

| | |
|---|---|
| **Beats** | std::shared_mutex |
| **Claimed result** | README headline: "contention_free_shared_mutex&lt;&gt; - 10 X times faster than std::shared_mutex". CodeProject Article 2 (archived), 16 threads on Xeon E5-2660 v3, std::map guarded by the lock: 0% modifications 34.60 Mops (contfree_safe_ptr&lt;map&gt;) vs 2.44 Mops (safe_ptr&lt;map, std::shared_mutex&gt;), stated as 14x; 15% modifications 5.16 vs 0.74 Mops, stated as 7x. The README charts (90% update/5% insert/5% delete, 20 usec forced delay, 2x Xeon E5-2686 v4) show about 1.9 vs about 0.4 MOps at 64 threads (\~5x, read approximately from the chart image) and near-parity at 16 threads or fewer. |
| **Workload** | Concurrent read/write locking benchmark (bench_contfree / benchmark / CDS_test folders) comparing contention_free_shared_mutex&lt;&gt; to std::shared_mutex under multi-threaded mixed read/write contention on a shared object; exact operation counts and thread counts are shown only in chart images in the README, not as text/tables. |
| **Metric** | throughput |
| **Hardware** | Article numbers: single Intel Xeon E5-2660 v3 2.6 GHz, 16 threads (numactl --cpunodebind=0). README charts: 2x Intel Xeon E5-2686 v4 2.3 GHz (36 cores/72 threads). |
| **Compiler and flags** | GCC 6.3.0 on Linux, g++ -std=c++14 -pthread -O3 (bench_contfree/Makefile). The article also offers an MSVS 2015 build, but the published run command (numactl ... ./benchmark 16) is Linux. |
| **Adoption** | 522 stars |
| **Last commit** | 2020-04-13 |
| **Links** | [repository](https://github.com/AlexeyAB/object_threadsafe) · [benchmark](http://web.archive.org/web/20210806092034id_/https://www.codeproject.com/Articles/1183423/We-Make-a-std-shared-mutex-10-Times-Faster) |

## Verdict

The author's own benchmark (bench_contfree, g++ -std=c++14 -pthread -O3, GCC 6.3.0, 16 threads on one Xeon E5-2660 v3) measured a std::map guarded by contention_free_shared_mutex&lt;&gt; against the same map guarded by std::shared_mutex: 34.60 vs 2.44 Mops at 0% writes (\~14x) and 5.16 vs 0.74 Mops at 15% writes (\~7x). The README's headline '10x' sits between these two figures; a separate real-app chart (2x Xeon E5-2686 v4, 20 usec forced inter-thread delay) shows near-parity up to 16 threads and only \~5x at 64 threads.

## Use it when

- Shared state accessed by a bounded, roughly-known number of threads (&lt;=36 by default, adjustable via the contention_free_count template parameter) under a read-heavy or mixed workload currently guarded by std::shared_mutex.
- You can accept the operator-&gt; / operator\* locking syntax instead of direct member access, or you only need contention_free_shared_mutex&lt;&gt; itself as a mutex-only drop-in.
- You want recursive locking across same-mode combinations (X-&gt;X, S-&gt;S) that std::shared_mutex does not provide.
- The project is small enough (one \~630-line header, Apache-2.0) to vendor and audit or patch yourself.

## Skip it when

- More than \~36 threads regularly contend: past the compiled-in slot count, get_or_set_index() returns -1 and lock_shared() falls back to competing for the same exclusive want_x_lock flag as lock(), erasing the advantage.
- Producer/consumer or queue-shaped concurrency -- this is a general object lock, not a lock-free queue like the sibling entries in this category.
- Any code path upgrades a shared lock to exclusive (S-&gt;X): explicitly documented in the header comment as undefined behavior.
- You create and destroy contention_free_shared_mutex instances repeatedly (e.g. on the stack): open, unfixed issue #5 shows the thread-local index cache can misidentify a new instance that reuses a freed instance's memory address, corrupting lock state.
- You need try_lock/try_lock_shared or timed locking: contention_free_shared_mutex only implements lock/unlock/lock_shared/unlock_shared, not the full BasicLockable/SharedTimedLockable interface std::shared_timed_mutex offers.

## How it is fast

contention_free_shared_mutex shards the 'a reader is present' flag across a fixed-size array (default 36 slots), one cache-line-padded atomic&lt;int&gt; per registered thread; a reader touches only its own slot instead of contending on the single shared atomic that a typical std::shared_mutex reader count uses. A writer sets one global want_x_lock flag, then spins until every slot reports idle. Thread-to-slot mapping is cached in a thread_local unordered_map keyed by the mutex instance so repeat lock_shared() calls skip the registration scan.

## Compared with alternatives

All six sibling entries in this category (atomic_queue, Boost.Lockfree, moodycamel::ReaderWriterQueue, oneTBB concurrent_bounded_queue, xenium, eventpp::SpinLock) are lock-free queues benchmarked against std::mutex for producer/consumer handoff latency; none targets std::shared_mutex. Pick object_threadsafe when the baseline is a std::shared_mutex-guarded object (e.g. a std::map) under a read-heavy or mixed workload with a bounded thread count, not a queue-shaped pipeline.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the standard library (&lt;atomic&gt;, &lt;mutex&gt;, &lt;thread&gt;, and &lt;shared_mutex&gt; when C++14 is detected) |
| **Minimum toolchain** | C++11 for safe_ptr&lt;&gt;/safe_obj&lt;&gt;/contention_free_shared_mutex&lt;&gt;; C++14 (or MSVC 1900+) additionally enables the std::shared_timed_mutex-based shared_mutex_safe_ptr variant via an __cplusplus/_MSC_VER check. Benchmarks were built with g++ -std=c++14 -pthread -O3. |
| **Platforms** | any platform with a C++11/14 standard library and std::atomic; benchmarked on x86-64 Linux with GCC, and ships MSVS 2015 project files for Windows. |
| **Thread safety** | contention_free_shared_mutex&lt;&gt; is itself the synchronization primitive; safe_ptr&lt;&gt;/contfree_safe_ptr&lt;&gt; are thread-safe by construction since every access acquires the wrapped mutex. |
| **Drop-in for the baseline** | partial -- explain: contention_free_shared_mutex&lt;&gt; implements lock()/unlock()/lock_shared()/unlock_shared() like std::shared_mutex and can replace it directly as a mutex type, but lacks try_lock/try_lock_shared and has different (recursive) upgrade semantics. safe_ptr&lt;&gt;/contfree_safe_ptr&lt;&gt; change the access syntax to operator-&gt; / operator\*, so wrapping an existing object for external callers is not drop-in. |

## Gotchas

- S-&gt;X lock upgrade (taking the exclusive lock while already holding a shared lock) is explicitly undefined behavior per the header's own comment.
- Contention-free behavior caps at contention_free_count threads (default 36); beyond that, lock_shared() falls back to the same exclusive want_x_lock path as lock(), per the registration logic in safe_ptr.h.
- Open issue #5 (unfixed as of this check): the per-thread slot index is cached in a thread_local map keyed by the mutex's `this` pointer, so a stack-allocated mutex that is destroyed and a new one reallocated at the same address can be misidentified, corrupting lock state.
- Every contention_free_shared_mutex&lt;&gt; instance allocates contention_free_count x 64-byte padded slots up front (\~2.3 KB at the default of 36), a fixed per-instance memory cost regardless of actual thread count.

## Caveats and trade-offs

First-party benchmark from 2017-era articles. The 10x headline is a middle value: the article shows 14x at 0% writes and 7x at 15% writes, and the lock is contention-free only up to 36 threads (template parameter). Above that it acts as an exclusive lock. The README's real-app chart (20 usec delay) shows parity up to 16 threads and \~5x only at 64 threads. CodeProject's live page now redirects to a lander, so the evidence is the Wayback copy. The last commit is 2020-04-13, so the project is unmaintained.

contention_free_shared_mutex shards locking state per-thread to avoid contention, which increases memory usage relative to std::shared_mutex; safe_ptr&lt;&gt;/contfree_safe_ptr&lt;&gt; wrap objects and change access syntax (operator-&gt; based locking) rather than being a drop-in mutex replacement; recursive-lock semantics differ from std::shared_mutex.

## Maintenance

Abandoned: last commit 2020-04-13, and a known thread-index correctness bug (issue #5) has sat open and unfixed since; still Apache-2.0 and a single \~630-line header, so it remains cheap to vendor and patch yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. The author's CodeProject Article 2 (the live URL now redirects to /lander, so I read the archived copy) benchmarks contention_free_shared_mutex against std::shared_mutex. It states CPU (Intel Xeon E5-2660 v3 2.6 GHz, 16 threads), compiler (GCC 6.3.0 on Linux; run command uses numactl) and text numbers. The benchmark code is public at bench_contfree/main.cpp, and bench_contfree/Makefile gives the flags (g++ -std=c++14 -pthread -O3).
- **Verifier notes:** The record's C tier came from being unable to fetch the CodeProject article. The Wayback copy supplies the CPU, compiler and text numbers, and the repo supplies the code and Makefile flags, so I upgraded it to A. The benchmark measures std::map guarded by each lock, not the bare mutex. Metadata checked: Apache-2.0, 522 stars, not archived, not a fork.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `baseline_stdlib`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/AlexeyAB/object_threadsafe>
  - <https://github.com/AlexeyAB/object_threadsafe/blob/master/Readme.md>
  - <https://github.com/AlexeyAB/object_threadsafe/blob/master/bench_contfree/Makefile>
  - <https://user-images.githubusercontent.com/4096485/79151220-c03c4180-7dd2-11ea-9b73-e281fa561a78.png>
  - <https://user-images.githubusercontent.com/4096485/79151246-caf6d680-7dd2-11ea-9527-db1a0c0a7364.png>
  - <https://www.codeproject.com/Articles/1183423/We-make-a-std-shared-mutex-times-faster>
  - <http://web.archive.org/web/20210806092034id_/https://www.codeproject.com/Articles/1183423/We-Make-a-std-shared-mutex-10-Times-Faster>
- **Sources the enricher read:**
  - <https://github.com/AlexeyAB/object_threadsafe>
  - <https://github.com/AlexeyAB/object_threadsafe/blob/master/Readme.md>
  - <https://github.com/AlexeyAB/object_threadsafe/blob/master/safe_ptr.h>
  - <https://github.com/AlexeyAB/object_threadsafe/blob/master/bench_contfree/Makefile>
  - <https://github.com/AlexeyAB/object_threadsafe/blob/master/bench_contfree/Readme.md>
  - <https://github.com/AlexeyAB/object_threadsafe/issues/5>
  - <https://github.com/AlexeyAB/object_threadsafe/issues/3>
  - <https://github.com/AlexeyAB/object_threadsafe/commits/master>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/alexeyab/object_threadsafe`) · [data/wave1/enrich/raw/github_com_alexeyab_object_threadsafe.json](../../../data/wave1/enrich/raw/github_com_alexeyab_object_threadsafe.json) (enrichment confidence 0.55)

</details>
