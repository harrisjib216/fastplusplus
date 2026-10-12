# Cachelot

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-2-Clause` · 🔴 abandoned

> Single-threaded C++ LRU cache library plus a memcached-text-protocol server that fits 7-16% more data than Memcached in the same RAM.

| | |
|---|---|
| **Beats** | memcached |
| **Claimed result** | The page says Cachelot 'keeps more items in the same amount of RAM than Memcached (saves up to 15% RAM, depending on the data and store patterns)', with 5-7% metadata overhead. The chart data (benchmarks.js, 2048MB budget, 10 runs) shows effective memory of 91.2-93.9% vs 79.5% for Memcached on small values (10B-1KB), 94.2-98.6% vs 86.7% on 1-4KB, 93.3-96.9% vs 87.2-87.3% on 4KB-1MB, and 93.4-97.4% vs 86.9-87.0% on mixed. That is up to about 14.4 points of the budget, or 7-18% more stored data (derived from page data). The README says Cachelot 'is faster in terms of latency' but gives no numbers. |
| **Workload** | A Python script (test/memory_consumption.py) generates 2GB of random keys (10-60 chars) and values in four size ranges: 10B-1KB, 1-4KB, 4KB-1MB, and 10B-1MB. It fills cachelotd and Memcached, each limited to 2GB, over 10 shuffled runs and measures 'effective memory', the total bytes of surviving keys and values. |
| **Metric** | memory |
| **Adoption** | 376 stars |
| **Last commit** | 2023-04-12 |
| **Links** | [repository](https://github.com/cachelot/cachelot) · [benchmark](https://cachelot.io/index.html#benchmarks) |

## Verdict

The author's own chart (cachelot.io, circa 2016) fills Cachelot and Memcached, each capped at 2 GB, with the same shuffled random dataset over 10 runs and counts surviving key+value bytes. Cachelot keeps 91-94% of the budget vs 79.5% for Memcached on 10 B-1 KB values, 94-99% vs 86.7% on 1-4 KB, 93-97% vs 87.3% on 4 KB-1 MB, and 93-97% vs 86.9% on mixed sizes, which is 7-16% more stored data by the 10th run. Cachelot's figures fall slightly each run while Memcached's stay flat. No CPU, compiler, flags or Memcached version is given, and the script in the repo now uses 4 GB, not 2 GB.

## Use it when

- A memcached text-protocol cache that is memory-bound with mostly small values (10 B-1 KB): the vendor chart shows about 91-94% of a 2 GB budget holding live data vs about 79.5% for Memcached
- Embedding a hard-capped LRU cache inside a single-threaded event loop, or one instance per core/shard, where you want no malloc after startup and predictable memory use
- Resource-limited targets (the README lists 32-bit ARM and x86-64) where the cache must never exceed a fixed arena
- 'Consistent cache' use (-M / enable_evictions=false), where a full cache should return an error instead of silently evicting data
- C or FFI embedding through the provided C API (cachelot_set/get/add/cas-style calls and an eviction callback)

## Skip it when

- You need one multi-threaded process or concurrent readers. The author states it is not thread-safe by design, and even get() mutates the LRU state, so you must shard or put it behind a single worker queue
- You need full memcached compatibility: there is no binary protocol, no SASL/TLS, no meta commands and no 'stats &lt;arg&gt;'; flush_all and exptime semantics differ; flags are 16-bit
- You pick a cache for throughput or latency. The only published comparison is memory efficiency; the 'faster latency' claim has no numbers, and siblings such as Pelikan, MemC3 and Pogocache publish throughput data
- Hit ratio is sensitive to eviction precision. LRU is tracked per page (1 MB by default), and an eviction drops every item on the chosen page whatever their individual recency
- You need a maintained, security-reviewed daemon. The last commit was April 2023, the only CI config is a legacy .travis.yml (no GitHub Actions), and several CLI flags are silently ignored

## How it is fast

The memory gain comes from the allocator, not the index. One power-of-two arena is split into fixed pages (1 MB by default). Inside each page, items are variable-size blocks with an 8-byte header, kept on segregated free lists (power-of-two ranges each cut into 32 sub-classes, TLSF-style), and split or coalesced with their neighbours. Each item is stored close to its exact size, instead of being rounded up to a slab-class chunk as in memcached. Items keep the key and value inline behind a compact header (64-bit CAS stamp, 32-bit hash, length, expiry, 16-bit flags). The index is a Robin Hood open-addressing hash table with hashes stored in a separate array, FNV-1a 32-bit hashing and a 93% max load factor, and it grows by incremental two-table rehashing to avoid resize stalls. There are no locks anywhere.

## Compared with alternatives

Pick Cachelot over Pelikan/Segcache, MemC3, Pogocache or Dragonfly only when RAM efficiency on a memcached-text workload, or an embeddable fixed-arena single-threaded LRU library, matters more than throughput; those siblings publish multi-threaded throughput wins over Memcached (for example Segcache at about 8x with 24 threads) and are better choices for a maintained, concurrent server.

## Integration

| | |
|---|---|
| **Form** | static lib (libcachelot, mostly inline headers plus a few .cpp files) and a cachelotd server binary; Docker image cachelot/cachelot |
| **Dependencies** | Boost &gt;= 1.53 (system, program_options and asio for the server, unit_test_framework for tests; the library itself uses Boost error_code/intrusive pieces); CMake |
| **Minimum toolchain** | C++11 (CMAKE_CXX_STANDARD 11); GCC, Clang or MSVC (VS 2022 via vcpkg for Boost on Windows) |
| **Platforms** | x86-64 and 32-bit ARM; the README says it is tested on Alpine, CentOS 7, Ubuntu, macOS and Windows 10/11 |
| **Thread safety** | Not thread-safe by design (cache.h note; author in issues #24, #28, #35 and #40). Concurrent reads are unsafe too, because get() touches the page LRU and lookups can advance incremental rehashing. Stats counters are one process-global, non-atomic struct shared by all Cache instances. |
| **Drop-in for the baseline** | partial — the memcached ASCII protocol on port 11211 works for get/gets/set/add/replace/cas/append/prepend/delete/incr/decr/touch/stats/version/flush_all/quit, but the binary protocol is unimplemented and flush_all, exptime and flags semantics differ |

## Gotchas

- flush_all only removes items that have already expired; unlike memcached, it does not invalidate live items. exptime is always taken as relative seconds, with no absolute-Unix-time rule for values over 30 days, so absolute expiries effectively never fire
- The server's -d (daemon), -l (listen), -C (no-cas) and socket-access flags are parsed but never applied (issue #15 confirms -d is unimplemented). TCP and UDP both bind to all interfaces on 11211 by default, and UDP memcached on a public interface is a known reflection-amplification vector, so pass -U 0 or firewall it
- Eviction works per page: touching an item promotes its whole page, and evicting a page frees every item on it after a linear scan of the page table. A smaller -P page gives finer eviction but also caps the maximum item size, because an item must fit in one page
- -m and -P must be powers of two. Library calls throw system_error (out_of_memory, key_too_long, item_too_big), and the pointer returned by do_get is valid only until the next Cachelot call

## Known shortcomings

- The win is memory ('saves up to 15% RAM'; the chart shows 7-18% more data stored), not speed. Abandoned (last commit 2023-04).
- The memory win (7-16% more stored bytes than Memcached, shrinking each run) comes only from a vendor chart with no Memcached version or hardware; no throughput/latency numbers. Single-threaded by design (even get() mutates the page LRU; stats are a global non-atomic struct). The binary protocol throws not_implemented; flush_all drops only expired items; exptime is always relative; 16-bit flags.
- SECURITY: the -d/-l/-C options are parsed but ignored and it binds TCP and UDP on 0.0.0.0:11211 by default, a UDP amplification risk. Page-level LRU evicts a whole 1 MB page with a linear page scan. Abandoned since 2023-04; Boost dependency.

## Caveats and trade-offs

No CPU model, compiler, flags or Memcached version are stated for the vs-Memcached test. It measures memory efficiency only; the latency claim has no numbers, and a memslap throughput script (src/benchmark/memslap_benchmark.sh) exists with no published results. The current script's MEMORY_LIMIT is 4GB while the page reports 2GB runs. There is no independent verification. The last commit on master was 2023-04-12 (pushed_at 2024-08-07 is not a commit), over 3 years ago.

Single-threaded server design (scales via sharding/multiple processes, not one multithreaded process); fixed pre-allocated memory pool; only a subset of the memcached wire protocol

## Maintenance

Abandoned since the last commit on 2023-04-12, but the BSD-2-Clause library is small and self-contained apart from Boost, so it is easy to vendor; treat the cachelotd daemon as unhardened.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party cachelot.io chart compares Cachelot vs Memcached effective memory under a 2GB limit across four value-size datasets. The benchmark script (test/memory_consumption.py) is public, but no CPU, compiler, flags or Memcached version are stated, so it is C.
- **Verifier notes:** The page shows a real vs-Memcached memory comparison. The '15%' is the page's own 'saves up to 15% RAM' wording, not 'more usable data'; the chart implies 7-18% more stored bytes. last_commit was the pushed_at date; the real last commit is 2023-04-12, which makes the project abandoned rather than stale. BSD-2-Clause and 376 stars confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `last_commit`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <http://cachelot.io/index.html#benchmarks>
  - <https://cachelot.io/assets/js/benchmarks.js>
  - <https://github.com/cachelot/cachelot>
  - <https://github.com/cachelot/cachelot/blob/master/test/memory_consumption.py>
  - <https://github.com/cachelot/cachelot/blob/master/src/benchmark/memslap_benchmark.sh>
  - <https://github.com/cachelot/cachelot/blob/master/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/cachelot/cachelot>
  - <https://github.com/cachelot/cachelot/blob/master/readme.md>
  - <https://github.com/cachelot/cachelot/blob/master/src/cachelot/cache.h>
  - <https://github.com/cachelot/cachelot/blob/master/src/cachelot/memalloc.h>
  - <https://github.com/cachelot/cachelot/blob/master/src/cachelot/memalloc-inl.h>
  - <https://github.com/cachelot/cachelot/blob/master/src/cachelot/hash_table.h>
  - <https://github.com/cachelot/cachelot/blob/master/src/cachelot/dict.h>
  - <https://github.com/cachelot/cachelot/blob/master/src/cachelot/item.h>
  - <https://github.com/cachelot/cachelot/blob/master/src/cachelot/item.cpp>
  - <https://github.com/cachelot/cachelot/blob/master/src/cachelot/expiration_clock.h>
  - <https://github.com/cachelot/cachelot/blob/master/src/cachelot/hash_fnv1a.h>
  - <https://github.com/cachelot/cachelot/blob/master/src/cachelot/stats.h>
  - <https://github.com/cachelot/cachelot/blob/master/src/cachelot/c_api.h>
  - <https://github.com/cachelot/cachelot/blob/master/src/server/main.cpp>
  - <https://github.com/cachelot/cachelot/blob/master/src/server/settings.h>
  - <https://github.com/cachelot/cachelot/blob/master/src/server/memcached/proto_ascii.cpp>
  - <https://github.com/cachelot/cachelot/blob/master/src/server/memcached/proto_binary.cpp>
  - <https://github.com/cachelot/cachelot/blob/master/src/server/memcached/conversation.h>
  - <https://github.com/cachelot/cachelot/blob/master/src/server/socket_datagram.h>
  - <https://github.com/cachelot/cachelot/blob/master/CMakeLists.txt>
  - <https://github.com/cachelot/cachelot/blob/master/src/cachelot/CMakeLists.txt>
  - <https://github.com/cachelot/cachelot/blob/master/src/benchmark/CMakeLists.txt>
  - <https://github.com/cachelot/cachelot/blob/master/src/benchmark/benchmark_cache.cpp>
  - <https://github.com/cachelot/cachelot/blob/master/test/memory_consumption.py>
  - <https://github.com/cachelot/cachelot/blob/master/.travis.yml>
  - <https://github.com/cachelot/cachelot/issues>
  - <https://github.com/cachelot/cachelot/issues/40>
  - <https://github.com/cachelot/cachelot/issues/35>
  - <https://github.com/cachelot/cachelot/issues/28>
  - <https://github.com/cachelot/cachelot/issues/24>
  - <https://github.com/cachelot/cachelot/issues/15>
  - <https://github.com/cachelot/cachelot/issues/18>
  - <https://github.com/cachelot/cachelot/issues/36>
  - <https://cachelot.io/index.html>
  - <https://cachelot.io/assets/js/benchmarks.js>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/cachelot/cachelot`) · [data/wave6/enrich/raw/github_com_cachelot_cachelot.json](../../../data/wave6/enrich/raw/github_com_cachelot_cachelot.json) (enrichment confidence 0.75)

</details>
