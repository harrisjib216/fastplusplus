# ART Synchronized (Optimistic Lock Coupling / ROWEX for Adaptive Radix Tree)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> In-memory concurrent Adaptive Radix Tree (OLC and ROWEX variants); roughly 1.5-3x Masstree's throughput on 8-byte integer keys.

| | |
|---|---|
| **Beats** | Masstree (concurrent B-tree/trie hybrid key-value index) -- not one of the assignment's named baselines, recorded honestly as the incumbent the paper actually benchmarks against |
| **Claimed result** | On 50M random 8-byte integer keys, Optimistic Lock Coupling and ROWEX beat Masstree clearly (approximate values read off Figure 5, derived from page data). At 20 threads, lookups run at \~82-86M ops/s vs \~29M (\~3x), inserts at \~56M vs \~24M (\~2.3x), and removes at \~38M vs \~26M (\~1.5x). The per-lookup cycle table gives OLC 348/418 cycles vs Masstree 982/1231 at 1/20 threads, \~2.8-2.9x fewer (derived from page data). The text says OLC needs 4.8x fewer instructions and 3.6x fewer L3 misses than Masstree. On string keys at 20 threads (Figure 7), synchronized ART beats Masstree only on genome inserts (\~29M vs \~7M ops/s). Masstree is roughly on par for genome lookups and faster on both Wikipedia and URL. |
| **Workload** | Concurrent lookup, insert and remove throughput at 1-20 threads on 50M random 8-byte integer keys (low contention). A contention test runs 1 lookup thread and 1 insert+remove thread on 10M dense keys with Zipf skew. Lookup and insert run at 20 threads on three string datasets: genome (256K), Wikipedia titles (16M) and URLs (6.4M). The comparison covers the ART synchronization variants (lock coupling, Optimistic Lock Coupling, ROWEX, HTM) against Masstree. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon E5-2687W v3 (Haswell EP, 10 cores/20 threads), 25MB L3 cache |
| **Adoption** | 129 stars |
| **Last commit** | 2026-05-25 |
| **Links** | [repository](https://github.com/flode/ARTSynchronized) · [benchmark](https://db.in.tum.de/~leis/papers/artsync.pdf) |

## Verdict

The DaMoN 2016 paper benchmarked the ART variants against Masstree (masstree-beta), all using jemalloc, on a single-socket Xeon E5-2687W v3 (10 cores/20 threads, 25 MB L3). It does not state the compiler or flags, publishes no harness, and calls the comparison not apples-to-apples. On 50M random 8-byte integers at 20 threads, OLC and ROWEX reached about 82-86M lookups/s vs about 29M, 56M inserts/s vs 24M, and 38M removes/s vs 26M (read off Figure 5). On string keys at 20 threads, Masstree won on Wikipedia titles and URLs, genome lookups were roughly even, and ART won clearly only on genome inserts (about 29M vs 7M).

## Use it when

- A multi-threaded in-memory ordered index inside a database or storage engine that already has row IDs or record pointers, so loadKey can rebuild the key from the TID.
- Short fixed-length keys (for example 8-byte integers stored big-endian) with many threads running lookups, inserts and removes. At 20 threads on 50M random keys, the paper measured about 82-86M lookups/s and 56M inserts/s, 2-3x Masstree.
- Read-heavy workloads with writers on hot keys: use the ROWEX variant. Its lookups never block and stayed around 15-18M ops/s under extreme Zipf skew, where OLC lookups dropped to about 10M (Figure 6).
- Low-contention workloads where simpler code matters: use OLC. It has slightly faster lookups (about 7%, per the paper) and less code than ROWEX (148 vs 200 lines for insert).
- Single-socket x86-64 Linux deployments that can take on TBB and jemalloc.

## Skip it when

- Longer string keys such as Wikipedia titles (22 bytes on average) or URLs (63 bytes): in the paper's own Figure 7 at 20 threads, Masstree beat it on both lookups and inserts.
- When you need a self-contained key-value map. Keys are not stored, there is no update or upsert API, values are limited to 63-bit TIDs, and lookup() returns 0 for 'not found'.
- Variable-length keys where one key can be a prefix of another (strings without a terminator). The README and issue #8 say this is unsupported by design, and such inserts crash.
- Range scans on the OLC tree running alongside inserts and removes: open issue #6, confirmed by the author in 2021, shows lookupRange (getChildren, findStart, findEnd) can loop forever on obsolete nodes. The single-threaded ART's lookupRange is commented out (issue #9).
- Non-x86 targets, MSVC, multi-socket scaling, or memory-constrained sparse key sets. Node16 uses SSE2 intrinsics with no fallback. The GRE study (PVLDB'22) found ART the least space-efficient traditional index on sparse keys, and saw ART-OLC struggle to scale across sockets on dense-key datasets.

## How it is fast

ART keeps the tree shallow for fewer cache misses. It uses adaptive node sizes (Node4/16/48/256, with an SSE2 compare in Node16), path compression and lazy leaf expansion. Optimistic Lock Coupling puts a 64-bit version/lock/obsolete word in each node. Readers never write shared memory: they re-validate versions and restart from the root on conflict. That avoids the cache-line ping-pong that ruins classic lock coupling, which in the paper's table goes from 418 to 2787 cycles per lookup between 1 and 20 threads. ROWEX (Read-Optimized Write EXclusion) takes locks only for writers and makes every node change atomic for readers (Node4/16 append unsorted, child pointers are atomic, prefix and length are updated in one store), so lookups never block or restart. Epoch-based reclamation frees replaced nodes. Against Masstree, the paper attributes the integer-key gap to 4.8x fewer instructions and 3.6x fewer L3 misses per lookup.

## Compared with alternatives

Pick this when several threads must insert, remove and look up in one ordered index at the same time. The rafaelkallis ART sibling is a single-threaded std::map-like container. GRE notes that, as published, updatable learned indexes such as ALEX and LIPP lacked concurrency (it built its own ALEX+ and LIPP+). In GRE's 24-thread heatmap, ART-OLC (from a modified fork of this repo) was one of three winners and led write-heavy workloads on easy datasets, while the learned indexes kept the edge on read-only and single-threaded numeric workloads.

## Integration

| | |
|---|---|
| **Form** | static lib: the CMake target ARTSynchronized builds all three Tree.cpp files. Each Tree.cpp #includes its node .cpp files and Epoche.cpp, so projects such as GRE vendor it as a source drop by #including Tree.cpp directly. |
| **Dependencies** | Intel TBB (Epoche.h uses tbb::enumerable_thread_specific; the example uses tbb::parallel_for), jemalloc (linked by CMake and used for the paper's numbers), and pthreads |
| **Minimum toolchain** | C++14 (CMake sets -std=c++14 -march=native) with GCC or Clang, since the code uses __builtin_ctz and __builtin_bswap64; CMake 2.8+. The README warns that some g++ versions fail to link jemalloc (check with ldd or LD_PRELOAD it). A g++ build error was fixed in December 2019 (PR #3). |
| **Platforms** | x86-64 only in practice: Node16 includes &lt;emmintrin.h&gt; with no scalar fallback, and leaf tagging assumes 64-bit pointers and TIDs. Install instructions cover only Debian/Ubuntu Linux. The paper's benchmarks ran on a single-socket Haswell-EP. |
| **Thread safety** | ART_OLC::Tree and ART_ROWEX::Tree allow concurrent lookup, insert, remove and lookupRange from any number of threads, as long as each thread uses its own ThreadInfo from getThreadInfo(). OLC readers can restart; ROWEX readers never block or restart. ART_unsynchronized::Tree is single-threaded. |
| **Drop-in for the baseline** | no |

## Gotchas

- The leaf is the TID with bit 63 set as a tag, so TIDs must fit in 63 bits (a comment in example.cpp notes that random keys lose their top bit). TID 0 cannot be told apart from 'not found'. remove(key, tid) deletes only when the stored TID matches.
- Integer keys must be byte-swapped to big-endian for correct order (the example uses __builtin_bswap64). Inserting a key that already exists is not handled: the leaf-split loop compares bytes past the end of the key, and ROWEX guards this only with a debug-build assert.
- ThreadInfo binds to the creating thread's TBB thread-local deletion list, so do not share one across threads. A thread that holds a ThreadInfo but goes idle keeps its old epoch published, which blocks freeing of replaced nodes for every thread until it runs another operation or destroys the ThreadInfo.
- OLC readers restart from the root whenever they see a locked node, with no backoff and no restart limit. The paper suggests capping restarts and falling back to write locks, but the repo does not do this, so writes to hot keys can starve OLC lookups.

## Known shortcomings

- The '2x on genome and URL keys' claim is wrong: Masstree wins on URL and Wikipedia keys and genome lookups roughly tie; the real win is 50M integer keys at 20 threads (\~3x lookups, \~2.3x inserts, Fig. 5). A memory-corruption fix landed 2026-05-25 (verifier downgrade).
- Keys aren't stored: callers must supply a loadKey(TID) callback; TIDs are 63-bit with 0 meaning not found; no upsert, and a duplicate insert reads past the key end. Open author-confirmed infinite loop in OLC lookupRange under concurrent writes (#6); inserted keys not found on the FB dataset (#5). x86-64 only (SSE2, no fallback); needs TBB and jemalloc; an idle ThreadInfo pins the epoch so no nodes are freed; OLC restarts have no backoff or cap, so hot writes can starve lookups. The GRE 24-thread winner was a modified fork, not this repo. Research code, mostly dormant.

## Caveats and trade-offs

The paper itself says ART vs Masstree is not apples-to-apples. ART's big win is on short integer keys; on string keys at 20 threads, Masstree matches or beats synchronized ART everywhere except genome inserts, including Wikipedia and URL lookups and inserts. Synchronization costs \~65% vs unsynchronized ART single-threaded, falling to \~10% at 20 threads. Compiler and flags are not stated, and no benchmark harness against Masstree is published. Masstree is not one of the assignment's named baselines. The last commit (2026-05-25, authored 2026-05-24) fixes a new-delete-type-mismatch memory-corruption bug after \~4 years of inactivity, so treat 'active' loosely.

Requires jemalloc and TBB; ROWEX needs custom epoch-based memory reclamation and is the most complex variant to implement/maintain; the paper itself notes the ART-vs-Masstree comparison is not apples-to-apples since the synchronization protocols and data structures differ

## Maintenance

Research code that has been dormant apart from occasional merges: since 2016 it received a g++ build fix (2019), a README note (2020), a no-upper-bound range scan (2022) and a May 2026 fix for a new/delete type mismatch that affects only the unsynchronized ART. Issues #5 (inserted keys not found on the FB dataset) and #6 (OLC range-scan infinite loop) remain open. The code is Apache-2.0 (per the LICENSE file; GitHub reports NOASSERTION) and small enough to vendor, as GRE did through a fork.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** The peer-reviewed DaMoN 2016 paper benchmarks the synchronized ART variants against Masstree on a Xeon E5-2687W v3. It states no compiler or flags and publishes no comparison harness (the repo's example.cpp does not include Masstree), so B holds, but the claim was misstated.
- **Verifier notes:** The record's claim of 'roughly 2x on genome and URL' is wrong. In Figure 7, Masstree is faster on URL lookups and inserts, and genome lookups are close to a tie. The strong, supportable win is on integer keys (Figure 5 and the CPU-counter table). The LICENSE file is Apache-2.0 (gh reports NOASSERTION), stars are 129, and the repo is not a fork. GRE (PVLDB'22) independently lists ART-OLC, not Masstree, among its 24-thread winners, but I did not verify that GRE uses this repo's implementation.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`, `last_commit`
- **Pages the verifier opened:**
  - <https://db.in.tum.de/~leis/papers/artsync.pdf>
  - <https://github.com/flode/ARTSynchronized>
  - <https://www.vldb.org/pvldb/vol15/p3004-wongkham.pdf>
- **Sources the enricher read:**
  - <https://github.com/flode/ARTSynchronized>
  - <https://github.com/flode/ARTSynchronized/blob/master/README.md>
  - <https://github.com/flode/ARTSynchronized/blob/master/CMakeLists.txt>
  - <https://github.com/flode/ARTSynchronized/blob/master/OptimisticLockCoupling/Tree.h>
  - <https://github.com/flode/ARTSynchronized/blob/master/OptimisticLockCoupling/Tree.cpp>
  - <https://github.com/flode/ARTSynchronized/blob/master/OptimisticLockCoupling/N.h>
  - <https://github.com/flode/ARTSynchronized/blob/master/OptimisticLockCoupling/N.cpp>
  - <https://github.com/flode/ARTSynchronized/blob/master/OptimisticLockCoupling/N16.cpp>
  - <https://github.com/flode/ARTSynchronized/blob/master/ROWEX/Tree.h>
  - <https://github.com/flode/ARTSynchronized/blob/master/ROWEX/Tree.cpp>
  - <https://github.com/flode/ARTSynchronized/blob/master/ROWEX/N.h>
  - <https://github.com/flode/ARTSynchronized/blob/master/ROWEX/N16.cpp>
  - <https://github.com/flode/ARTSynchronized/blob/master/ART/Tree.h>
  - <https://github.com/flode/ARTSynchronized/blob/master/Epoche.h>
  - <https://github.com/flode/ARTSynchronized/blob/master/Epoche.cpp>
  - <https://github.com/flode/ARTSynchronized/blob/master/Key.h>
  - <https://github.com/flode/ARTSynchronized/blob/master/example.cpp>
  - <https://github.com/flode/ARTSynchronized/issues/1>
  - <https://github.com/flode/ARTSynchronized/issues/2>
  - <https://github.com/flode/ARTSynchronized/issues/4>
  - <https://github.com/flode/ARTSynchronized/issues/5>
  - <https://github.com/flode/ARTSynchronized/issues/6>
  - <https://github.com/flode/ARTSynchronized/issues/8>
  - <https://github.com/flode/ARTSynchronized/issues/9>
  - <https://github.com/flode/ARTSynchronized/pull/10>
  - <https://github.com/flode/ARTSynchronized/commit/f00003e>
  - <https://github.com/flode/ARTSynchronized/commits/master>
  - <https://db.in.tum.de/~leis/papers/artsync.pdf>
  - <https://github.com/gre4index/GRE>
  - <https://github.com/gre4index/GRE/blob/master/src/competitor/artsync/artolc.h>
  - <https://github.com/gre4index/GRE/blob/master/.gitmodules>
  - <https://github.com/pohchaichon/ARTSynchronized>
  - <https://www.vldb.org/pvldb/vol15/p3004-wongkham.pdf>
  - <https://hn.algolia.com/api/v1/search?query=ARTSynchronized&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=%22optimistic%20lock%20coupling%22>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/flode/artsynchronized`) · [data/wave6/enrich/raw/github_com_flode_artsynchronized.json](../../../data/wave6/enrich/raw/github_com_flode_artsynchronized.json) (enrichment confidence 0.8)

</details>
