# cachegrand

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟡 stale

> Multi-threaded C key-value server speaking the Redis protocol (string commands only); out-scales single-threaded Redis on many-core Linux.

| | |
|---|---|
| **Beats** | Redis |
| **Claimed result** | GET, d128-c25, per load-generation node n01, AGGREGATED AVERAGE of 3 runs: cachegrand v0.2.1 at t16 = 935,576.61 ops/sec (benchmarks/cachegrand/v0.2.1/d128-c25/n01/t16/get/memtier_stdout.txt) vs Redis v7.0.11 at t1 = 71,143.97 ops/sec (benchmarks/redis/v7.0.11/d128-c25/n01/t1/get/memtier_stdout.txt; Redis was only run at t1), approx 13.2x (derived from page data). At matched t1, cachegrand 78,840.39 vs Redis 71,143.97 ops/sec, approx 1.11x (derived from page data). At t64, cachegrand reaches 2,241,838.36 ops/sec on n01, approx 31.5x Redis's t1 figure (derived from page data). The repo README chart sums both load nodes (about 4.5M GET ops/sec for cachegrand at 64 threads vs about 0.14M for Redis at 1 thread). The high-thread ratios also use 16x or 64x more client connections than the Redis run. |
| **Workload** | memtier_benchmark (scripts/run-memtier.sh) GET and SET against the Redis-protocol interface, 128-byte values, keys 1,000,000-2,000,000, 120 s per run, 3 runs averaged, from 2 load-generation nodes (n01, n02). tN is the memtier client thread count (-t N, 25 connections per thread per node; the chart calls this '50 clients per thread, 1 Thread per core'). cachegrand v0.2.1 was run at t1-t64 and Redis v7.0.11 only at t1. |
| **Metric** | throughput |
| **Hardware** | AMD EPYC 7502P (32c/64t), 8x32GB DDR4-3200, Ubuntu 22.04 (kernel 5.15.0-70), 2x25Gbit Intel XXV710 (bonded). The main server and the load-generation servers use the same spec (per benchmarks/cachegrand/v0.2.1/README.md, which is identical to benchmarks/redis/v7.0.11/README.md). |
| **Adoption** | 1k stars |
| **Last commit** | 2025-01-02 |
| **Links** | [repository](https://github.com/danielealbano/cachegrand) · [benchmark](https://github.com/cachegrand/cachegrand-benchmarks) |

## Verdict

Vendor memtier_benchmark runs (128 B values, Gaussian keys over a 1M-key range, 25 connections per memtier thread, two load servers) on an AMD EPYC 7502P 32c/64t with bonded 2x25GbE and Ubuntu 22.04 measured cachegrand v0.2.1 at 935.6K GET ops/s per load node with 16 client threads against Redis 7.0.11's 71.1K with 1 client thread (about 13x). At equal single-thread load it was only 78.8K vs 71.1K (about 1.1x), and Redis was never run with more client threads or as multiple instances; both were built from source by the prep script (cachegrand as a CMake Release build, which is -O2, with t1ha2; Redis with a plain make), but the GCC version and the server configs are not published.

## Use it when

- String-only Redis workloads (GET/SET/MGET/INCR/EXPIRE on small values; the vendor test used 128 B) that need more throughput than one Redis process gives, where you would rather not shard across several Redis instances.
- Many concurrent client connections hitting a many-core Linux x86-64 or aarch64 server (kernel 5.7+ for io_uring) on which you can dedicate cores, pin NIC queues and grant hugepages and unlimited memlock.
- A cache with a known keyspace ceiling: the hashtable is sized up front from database.limits.hard.max_keys, which suits workloads whose maximum key count you can set in advance.
- Studying or vendoring a BSD-3-Clause C implementation of a cache-line-packed SIMD concurrent hashtable, fibers and io_uring networking.

## Skip it when

- Anything beyond Redis strings and keys: other data types, pub/sub, MULTI/EXEC, Lua/functions, replication and cluster mode are missing, and the transactions and cluster-mode issues are still open.
- Single-client or pipelined traffic. In the vendor data it is only about 1.1x Redis at one memtier thread without pipelining, and with pipeline=64 Redis 7.0.11 beat it on SET (386K vs 273K ops/s per load node).
- Production systems that need an active upstream. There has been no release since v0.4.0 (May 2023), the last commit was 2025-01-02, and the expiry tests for SET/SETEX/PSETEX/GETEX were commented out as broken in December 2024.
- Non-Linux hosts, older kernels, or sandboxes and containers that block io_uring or high memlock limits; io_uring is the only network backend.
- A keyspace that can grow past a preset limit. There is no online resize (storage_db hard-codes can_auto_resize = false), and the memory limit does not count key bytes (open issue #439).

## How it is fast

It runs one pinned worker thread per core; each worker multiplexes connections as user-space fibers (hand-written x86-64/aarch64 context switch) over io_uring, so there is no thread per connection and few syscalls. All workers share one multi-producer/multi-consumer open-addressing hashtable that packs 14 32-bit slot IDs (filled bit, probe distance, 16-bit hash fragment) into each 64-byte cache line, a layout borrowed from Folly's F14. It probes at most 32 neighbouring lines and compares a whole line with two AVX2 compares; AVX-512F, AVX, NEON and scalar variants are chosen at startup through GNU ifunc. Writes take a small spinlock per 14-slot chunk, so contention is spread across the table instead of behind one global lock, and memory comes from mimalloc with optional 2 MB hugepages.

## Compared with alternatives

Dragonfly and KeyDB also serve the Redis protocol from many threads but cover far more of the command set and are maintained; Valkey is the maintained Redis fork. Pick cachegrand only for a GET/SET-only cache where its own data showing it ahead of Dragonfly v1.1.2 matters (about 1.4x GET and 1.25x SET at 64 memtier threads, about 3x GET with pipelining), or when you want a small BSD C hashtable and io_uring design to study or vendor.

## Integration

| | |
|---|---|
| **Form** | standalone server binary (CMake build from source or the cachegrand/cachegrand-server Docker image); not a library |
| **Dependencies** | liburing, libnuma, libyaml/libcyaml, mbedTLS &gt;= 2.28, libcurl, pcre2, json-c, liblzf, libatomic, mimalloc, t1ha/xxHash (several vendored under 3rdparty); hiredis only for tests; optional sentry |
| **Minimum toolchain** | GCC (the build docs require gcc; the README's sample log shows gcc 11.3.0), CMake 3.16+, C11 (C++17 for tests and benches), Linux kernel 5.7+ |
| **Platforms** | Linux only: x86-64 (runtime dispatch across AVX-512F/AVX2/AVX/scalar) and aarch64 (NEON) |
| **Thread safety** | Server-level. All workers share one database. Hashtable writes take per-chunk (14-slot) spinlocks, and since PR #434 (Oct 2023) reads take per-chunk read locks inside a transaction. |
| **Drop-in for the baseline** | partial — speaks RESP and implements about 53 string/keyspace commands plus RDB snapshots, so unmodified clients work for GET/SET-style caching; clients using other data types, pub/sub, transactions, scripting, replication or cluster will fail |

## Gotchas

- The hashtable size is fixed at start: the next power of two of database.limits.hard.max_keys (default 1,000,000). Probing stops after 32 cache lines (448 slots), so once a neighbourhood fills, inserts fail instead of the table resizing.
- The skeleton config binds 0.0.0.0 and :: on 6379/6380 with require_authentication: false and max_clients: 100. If you turn on sentry, it uploads crash minidumps, which may contain stored data, to the author's sentry.io DSN by default.
- The hashtable doc and the v0.2.1 benchmark describe lock-free, fence-based GETs. Since PR #434 (Oct 2023) GETs take per-chunk read spinlocks, and current main has not been re-benchmarked.
- It needs high memlock and nofile ulimits (io_uring shares locked memory with the kernel) and preferably 2 MB hugepages. The performance docs also tell you to pin NIC IRQ/XPS queues per worker and disable irqbalance to approach the published numbers.

## Known shortcomings

- Own benchmark repo with no compiler/flags. tN is memtier client threads, not server workers, and Redis was run only at t1, so the 13.2x/31.5x at t16/t64 compare 16-64x more clients; at equal load it is \~1.11x.
- Partial Redis compatibility (\~53 string/key commands; no lists/hashes/sets/zsets/pubsub/MULTI/Lua/replication/cluster; Kafka/Memcache/WASM are plans). The win comes from threads, not the algorithm: at matched single-thread load it is \~1.1x, and with pipeline=64 at one thread Redis beats it on SET (386K vs 273K). The hash table is fixed-size (default 1M keys, no resize, 32-line probe cap) so inserts fail when full; the memory limit ignores key bytes (#439).
- SECURITY: the default config has auth off and binds 0.0.0.0, and if Sentry reporting is enabled crash dumps go to the author's DSN. The benchmarked v0.2.1 had lock-free GETs, but main takes read spinlocks since PR #434 (2023-10) and was never re-benchmarked; expiry tests are commented out as broken (2024-12); last release v0.4.0 (2023-05). Needs io_uring, kernel 5.7+ and a high memlock limit.

## Caveats and trade-offs

Self-published by the project author and not independently reproduced. Raw memtier outputs and the run script are public, and the CPU is documented, but the compiler and build flags of the benchmarked binaries are not stated. The only compiler mention is an example startup log in the main README showing a v0.3.0 'Release build, compiled using gcc v11.3.0', which is not the benchmarked build. Redis was measured only with 1 memtier thread (25 connections per node), so the large multi-thread ratios compare a multi-threaded server under 16-64x more client connections against single-threaded Redis. At equal load the gain is only about 1.1x. The benchmark data is licensed CC BY-NC-ND 4.0 and run-memtier.sh is GPL-3.0. The main repo's last commit was 2025-01-02, so it is stale.

Only implements a subset of the Redis protocol/command set (still WIP per README); multi-threaded architecture means the 13x figure mostly reflects Redis's single-threaded design rather than a faster per-operation algorithm (per-thread parity is closer to \~1.1x); Linux x86-64/aarch64 only; project is a young, self-published key-value store, not a drop-in Memcached/Redis replacement (Memcached protocol support listed as 'planned', not implemented)

## Maintenance

Stale since 2025-01-02, with no release after v0.4.0 (May 2023), about 1k stars and one main author; it is BSD-3-Clause and builds with CMake, but treat it as a research-grade server, not a production Redis replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** First-party benchmark repo (cachegrand/cachegrand-benchmarks, scripts/run-memtier.sh plus raw memtier_stdout.txt files for cachegrand v0.2.1 and Redis v7.0.11) with the CPU model (AMD EPYC 7502P) stated, but no compiler or build flags for the tested binaries and no peer review or independent reproduction; the project's own benchmark code with partial methodology is C, not B.
- **Verifier notes:** The original benchmark_url is a single cachegrand-only memtier output; its 935,576.61 figure is correct, and the Redis figure 71,143.97 is correct but comes from the separate redis/v7.0.11 file, so I repointed benchmark_url to the benchmark repo root, whose README chart compares against Redis, KeyDB and Dragonfly. The record said the tN folders were server worker-thread counts, but per scripts/run-memtier.sh they are memtier client thread counts; I corrected this. Metadata checked via gh: BSD-3-Clause, 1,002 stars, not a fork, not archived, last commit 2025-01-02.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/danielealbano/cachegrand>
  - <https://raw.githubusercontent.com/danielealbano/cachegrand/main/README.md>
  - <https://github.com/cachegrand/cachegrand-benchmarks>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/README.md>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/cachegrand/v0.2.1/README.md>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/redis/v7.0.11/README.md>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/cachegrand/v0.2.1/d128-c25/n01/t16/get/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/cachegrand/v0.2.1/d128-c25/n02/t16/get/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/cachegrand/v0.2.1/d128-c25/n01/t1/get/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/cachegrand/v0.2.1/d128-c25/n02/t1/get/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/cachegrand/v0.2.1/d128-c25/n01/t64/get/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/cachegrand/v0.2.1/d128-c25/n02/t64/get/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/redis/v7.0.11/d128-c25/n01/t1/get/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/redis/v7.0.11/d128-c25/n02/t1/get/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/scripts/run-memtier.sh>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/images/latest-benchmark-results.png>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/images/latest-benchmarks-get-set.png>
- **Sources the enricher read:**
  - <https://github.com/danielealbano/cachegrand>
  - <https://raw.githubusercontent.com/danielealbano/cachegrand/main/README.md>
  - <https://github.com/danielealbano/cachegrand/blob/main/docs/architecture/hashtable.md>
  - <https://github.com/danielealbano/cachegrand/blob/main/docs/architecture/modules/redis.md>
  - <https://github.com/danielealbano/cachegrand/blob/main/docs/architecture/modules/memcache.md>
  - <https://github.com/danielealbano/cachegrand/blob/main/docs/build-from-source.md>
  - <https://github.com/danielealbano/cachegrand/blob/main/docs/performance-tips.md>
  - <https://github.com/danielealbano/cachegrand/blob/main/docs/configuration.md>
  - <https://github.com/danielealbano/cachegrand/blob/main/docs/benchmarks/hashtable.md>
  - <https://github.com/danielealbano/cachegrand/blob/main/docs/benchmarks/linear-vertical-scalability.md>
  - <https://github.com/danielealbano/cachegrand/blob/main/etc/cachegrand.yaml.skel>
  - <https://github.com/danielealbano/cachegrand/blob/main/src/data_structures/hashtable/mcmp/hashtable.h>
  - <https://github.com/danielealbano/cachegrand/blob/main/src/data_structures/hashtable/mcmp/hashtable_op_get.c>
  - <https://github.com/danielealbano/cachegrand/blob/main/src/data_structures/hashtable/mcmp/hashtable_op_set.c>
  - <https://github.com/danielealbano/cachegrand/blob/main/src/data_structures/hashtable/mcmp/hashtable_support_hash_search_avx2.h>
  - <https://github.com/danielealbano/cachegrand/blob/main/src/data_structures/hashtable/mcmp/hashtable_support_op_arch.c>
  - <https://github.com/danielealbano/cachegrand/blob/main/src/data_structures/hashtable/mcmp/hashtable_support_op.c>
  - <https://github.com/danielealbano/cachegrand/blob/main/src/storage/db/storage_db.h>
  - <https://github.com/danielealbano/cachegrand/blob/main/src/storage/db/storage_db.c>
  - <https://github.com/danielealbano/cachegrand/blob/main/src/worker/worker.c>
  - <https://github.com/danielealbano/cachegrand/blob/main/src/fiber/fiber_scheduler.c>
  - <https://github.com/danielealbano/cachegrand/blob/main/CMakeLists.txt>
  - <https://github.com/danielealbano/cachegrand/blob/main/tools/cmake/arch/arch-x86_64.cmake>
  - <https://github.com/danielealbano/cachegrand/blob/main/tools/cmake/compiler/compiler.cmake>
  - <https://github.com/danielealbano/cachegrand/blob/main/tools/cmake/build-types/build-types.cmake>
  - <https://github.com/danielealbano/cachegrand/issues>
  - <https://github.com/danielealbano/cachegrand/issues/103>
  - <https://github.com/danielealbano/cachegrand/issues/219>
  - <https://github.com/danielealbano/cachegrand/issues/439>
  - <https://github.com/danielealbano/cachegrand/pull/434>
  - <https://github.com/danielealbano/cachegrand/pull/445>
  - <https://github.com/danielealbano/cachegrand/releases>
  - <https://github.com/danielealbano/cachegrand/commits/main>
  - <https://github.com/cachegrand/cachegrand-benchmarks>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/README.md>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/scripts/run-memtier.sh>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/scripts/prep-node-for-benchmarking.sh>
  - <https://github.com/danielealbano/cachegrand/blob/v0.2.1/tools/cmake/build-types/build-types.cmake>
  - <https://github.com/danielealbano/cachegrand/blob/v0.2.1/tools/cmake/arch/arch-x86_64.cmake>
  - <https://github.com/danielealbano/cachegrand/blob/main/src/data_structures/hashtable/mcmp/hashtable_data.h>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/cachegrand/v0.2.1/README.md>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/dragonfly/v1.1.2/README.md>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/cachegrand/v0.2.1/d128-c25/n01/t1/get/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/cachegrand/v0.2.1/d128-c25/n01/t16/get/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/cachegrand/v0.2.1/d128-c25/n01/t64/get/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/cachegrand/v0.2.1/d128-c25/n01/t64/set/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/cachegrand/v0.2.1/d128-c5-pipeline64/n01/t1/set/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/cachegrand/v0.2.1/d128-c5-pipeline64/n01/t64/get/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/redis/v7.0.11/d128-c25/n01/t1/get/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/redis/v7.0.11/d128-c5-pipeline64/n01/t1/set/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/dragonfly/v1.1.2/d128-c25/n01/t64/get/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/dragonfly/v1.1.2/d128-c25/n01/t64/set/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/dragonfly/v1.1.2/d128-c5-pipeline64/n01/t64/get/memtier_stdout.txt>
  - <https://raw.githubusercontent.com/cachegrand/cachegrand-benchmarks/main/benchmarks/keydb/v6.3.2/d128-c25/n01/t16/get/memtier_stdout.txt>
  - <https://hn.algolia.com/api/v1/search?query=cachegrand&tags=story>
  - <https://hn.algolia.com/api/v1/search?query=cachegrand&tags=comment&hitsPerPage=30>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/danielealbano/cachegrand`) · [data/wave6/enrich/raw/github_com_danielealbano_cachegrand.json](../../../data/wave6/enrich/raw/github_com_danielealbano_cachegrand.json) (enrichment confidence 0.75)

</details>
