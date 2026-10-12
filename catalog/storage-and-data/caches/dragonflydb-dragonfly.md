# Dragonfly

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `BUSL-1.1` · 🟢 active

> Multi-threaded, shared-nothing in-memory store that speaks the Redis and Memcached protocols; beats single-process Redis once there are many cores.

| | |
|---|---|
| **Beats** | Redis, Memcached |
| **Claimed result** | Vendor README: on c6gn.16xlarge, 25x the throughput of a single single-threaded Redis process, crossing 3.8M QPS. Vs Memcached on c6gn.16xlarge: SET 3,844K vs 806K QPS (\~4.8x) and GET 3,717K vs 2,100K QPS (\~1.8x) (ratios derived from page data); Memcached had the lower GET p99 (0.34 ms vs 1 ms). Vs Redis on m5.large: about parity (SET 173K vs 159K; GET 191K vs 194K). Vs Redis on m5.xlarge: SET 279K vs 190K, GET 305K vs 220K. Memory: \~30% lower idle memory than Redis, and Redis peak during BGSAVE was almost 3x Dragonfly's. The 25x is contested. Redis's June 2022 rebuttal ran a 40-shard Redis 7.0 Cluster on the same c6gn.16xlarge and reported 18-40% MORE throughput than Dragonfly (e.g. GET pipeline 1: 4.43M vs 3.8M reproduced). The third-party tidwall/cache-benchmarks (c8g.8xlarge; Dragonfly 1.30.3 vs Redis 8.2.1 with io-threads) shows mixed results. Redis is faster at 8 server threads (GET 1.51M vs 1.41M), and Dragonfly is \~2.2x faster at 16 threads (GET 2.94M vs 1.32M). Memcached beats Dragonfly on GET at every thread count and pipeline depth. |
| **Workload** | memtier_benchmark SET/GET ops (-d 256) against Redis on m5.large/m5.xlarge, and against Memcached on c6gn.16xlarge; also idle/peak memory usage during BGSAVE-equivalent snapshot |
| **Metric** | throughput |
| **Hardware** | AWS m5.large, m5.xlarge, c6gn.16xlarge, r6g/c7g (instance types stated; CPU model not stated) |
| **Adoption** | 31.7k stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/dragonflydb/dragonfly) · [benchmark](https://github.com/dragonflydb/dragonfly#benchmarks) |

## Verdict

Vendor memtier_benchmark runs on AWS (instance types only; no CPU model, compiler, flags or baseline versions, and no published harness) show parity with single-threaded Redis on m5.large, about 1.4-1.5x on m5.xlarge, and 3.8M QPS on c6gn.16xlarge, which is the '25x a single Redis process' headline. The same runs show Memcached at 806K SET and 2.1M GET QPS against Dragonfly's 3.84M and 3.72M. Redis's 2022 rebuttal on the same instance, using a 40-shard Redis 7.0 Cluster, measured 18-40% more throughput than Dragonfly (GET pipeline 1: 4.43M vs 3.8M reproduced). tidwall's suite on ARM64 c8g.8xlarge with Dragonfly 1.30.3 gives mixed results: At pipeline 1, Dragonfly beats Redis 8.2.1 on GET at 2 and 10-16 threads, loses at 1 and 3-8 threads, and loses to Memcached on GET in every configuration.

## Use it when

- A single large multi-core box (16+ vCPUs) where you would otherwise run many Redis shards or a Redis Cluster, and you want one endpoint where MULTI/EXEC, Lua and multi-key commands keep single-node semantics.
- Unpipelined GET/SET at high server thread counts. In tidwall/cache-benchmarks (c8g.8xlarge, 16 server cores, pipeline 1) Dragonfly did about 2.9M GET/s against 1.3M for Redis 8.2.1 with io-threads.
- Write-heavy Memcached-protocol traffic on a big instance. On c6gn.16xlarge the vendor measured 3.84M SET/s against 806K for Memcached.
- Large datasets that snapshot often, where the copy-on-write memory spike from Redis fork is the problem. In the vendor's 5 GB BGSAVE test Redis peaked at about 3x Dragonfly's memory.
- Many small keys where per-key overhead dominates. The Dashtable doc estimates 6-16 bytes of table overhead per item against 16-32 for the Redis dict. It measured 20M keys at 1 GB versus 1.73 GB on Redis 6.

## Skip it when

- Small instances or few threads. On a 2-vCPU m5.large the vendor itself shows parity with Redis (GET 191K vs 194K). In tidwall's pipeline-1 runs Redis 8.2.1 with io-threads beat Dragonfly on GET at 1 and 3-8 threads (for example 1.51M vs 1.41M at 8).
- As a read-heavy Memcached replacement. Memcached 1.6.38 posted higher GET throughput than Dragonfly in every tidwall configuration, and in the vendor's own table Memcached had the lower GET p99 (0.34 ms vs 1 ms).
- Deep pipelining. At pipeline 10-50 on 16 threads, Garnet and Pogocache did roughly 3-4x Dragonfly's GET throughput in tidwall's runs. At pipeline 50 on 1 thread, Dragonfly's GET p99 was about 289 ms against about 15 ms for Redis.
- Offering it as a hosted or managed service, or embedding it in an in-memory data store product. The BUSL-1.1 Additional Use Grant forbids both. Each version converts to Apache-2.0 on 2030-11-01 or four years after its release, whichever comes first.
- Setups that need recent Redis features or files, or that let untrusted clients run EVAL. It cannot load the RDB v15 format from Redis 8.10 (#8361; the maintainer says it supports formats up to Redis 7). There is no SCRIPT KILL or lua-time-limit, so one infinite Lua script pins a thread until kill -9 (#8269). Cluster mode has no gossip protocol and needs an external cluster manager.

## How it is fast

It uses a shared-nothing, thread-per-core design built on the helio fiber library, with io_uring by default and epoll on kernels older than 5.10. Each thread owns one shard of the keyspace, and cross-shard work goes by message passing instead of locks. Multi-key atomicity uses the VLL lock-manager scheme from the VLDBJ paper. The main index is Dashtable, an implementation of Dash (extendible hashing): a directory of fixed-size open-addressed segments of 56 buckets plus 4 stash buckets, 14 slots per bucket. Lookups compare 8-bit fingerprints with one SSE2 compare per bucket (sse2neon on aarch64). Growth splits one segment at a time instead of rehashing the whole table. Per-bucket version counters in the table metadata are what make fork-less point-in-time snapshots possible. The same bucket layout drives cache-mode eviction: items are bumped toward the front of their bucket, and the last slot of a stash bucket is evicted.

## Compared with alternatives

Pick Dragonfly over Pogocache, Pelikan/Segcache or Garnet when you need broad Redis data types and commands, replication, snapshots and single-node multi-key atomicity on one big box, not just raw GET/SET cache throughput. In tidwall's suite Pogocache beat it on GET in every configuration, and Garnet beat it in all but two configurations, by about 3x under pipelining. Against KeyDB, both are multithreaded Redis alternatives; Dragonfly is the actively released one (v2.0.0 on 2026-09-16), but its license is BUSL-1.1.

## Integration

| | |
|---|---|
| **Form** | standalone server binary (prebuilt binaries/containers or build from source); not a linkable library |
| **Dependencies** | Build: helio (git submodule: Boost.Fibers-based I/O over io_uring/epoll), Boost.Context, OpenSSL, libunwind, zlib, bison, CMake + Ninja; optional AWS/GCP clients, tiering, search and extension modules via build flags |
| **Minimum toolchain** | C++20 (CMAKE_CXX_STANDARD 20), CMake 3.15+, g++ per build docs (minimum compiler version not documented); Linux kernel 5.10+ for io_uring (5.11+ advised), epoll fallback below |
| **Platforms** | Linux primary; build instructions also cover FreeBSD. x86-64 (SSE2/SSSE3 intrinsics), aarch64 (via sse2neon), plus RISC-V and s390x code paths |
| **Thread safety** | Server process, so this is about command semantics rather than a thread-safety API. Each shard is owned by one thread with no mutexes on data. The docs claim atomicity and strict serializability for multi-key commands, MULTI/EXEC and Lua. Known exception: EXEC is not atomic under maxmemory (#8275). |
| **Drop-in for the baseline** | partial — wire-compatible with Redis and Memcached clients. The gaps: a subset of commands (the README says roughly the Redis 5.0 API plus extensions); Lua scripts must declare their keys by default; there is no SCRIPT KILL; RDB loading only goes up to Redis 7 format (plus Valkey 9 since v2.0); cluster mode needs an external manager; and expiry precision and limits differ. |

## Gotchas

- maxmemory defaults to 80% of detected memory, and the server exits at startup if maxmemory is below 256 MB per proactor thread.
- Lua scripts that touch undeclared keys fail by default. Allowing them (default_lua_flags=allow-undeclared-keys) runs the script as a GLOBAL transaction that locks every shard.
- PEXPIRE/PSETEX deadlines above 2^28 ms (about 3.1 days) are silently rounded to the nearest second. Expiries are capped at about 8 years, strings at 256 MB, and hash-field TTLs have 1-second precision.
- An HTTP console and /metrics are served on the main 6379 port by default; disable with --primary_port_http_enabled=false if the port is exposed. Several 2026 advisories include an unauthenticated heap overflow in the memcached reply builder (GHSA-9q98-cx72-pg45), so stay on current releases.

## Known shortcomings

- The 25x is against a single-threaded Redis process; Redis's 2022 rebuttal ran a 40-shard Redis cluster on the same c6gn.16xlarge and got 18-40% more throughput than Dragonfly. In the tidwall cache-benchmarks suite Redis wins at 8 threads, Dragonfly leads \~2.2x only at 16 threads, and memcached wins GET in every config. BUSL-1.1 licence (not OSI) (verifier downgrade).
- On few cores it ties or loses: about equal to Redis on m5.large; in the tidwall suite Redis 8.2.1 wins at 1 and 3-8 threads and Dragonfly only leads at 16 threads (2.94M vs 1.32M). memcached beats it on GET in every tidwall config, Pogocache in every config and Garnet in all but two. Deep pipelines are weak (1-thread GET p99 \~289 ms vs Redis \~15 ms). BUSL-1.1 forbids hosted/managed services and embedding in in-memory store products (becomes Apache-2.0 on 2030-11-01 or 4 years after release). Compatibility gaps: no SCRIPT KILL (#8269), no Redis 8.10 RDB v15 (#8361), EXEC not atomic under maxmemory (#8275), Lua undeclared keys blocked by default, cluster needs an external manager. Needs &gt;=256 MB per thread or exits; PEXPIRE above 2^28 ms rounds to 1 s; HTTP console on port 6379; a 2026 advisory fixed an unauthenticated heap overflow in the memcached reply builder.

## Caveats and trade-offs

The 25x headline is a vendor claim against one single-threaded Redis process on a 64-vCPU instance, which is not how Redis is scaled. Redis's own 2022 test on the same c6gn.16xlarge with a 40-shard Redis 7.0 Cluster measured 18-40% higher throughput than Dragonfly. That test is also vendor-run and dates from 2022, against Dragonfly built on 2022-06-03. The README states no CPU model, compiler, flags or baseline versions, and publishes no benchmark code. The earlier caveat that tidwall/cache-benchmarks 'corroborates Dragonfly beating Redis/Memcached' is wrong. In that suite Dragonfly beats Redis 8.2.1 (io-threads) only at higher thread counts, loses to it at 8 server threads, and loses to memcached on GET in every configuration; that suite's author also makes the competing Pogocache. License is BUSL-1.1 (not OSI; Apache-2.0 on the Change Date of 2030-11-01, and production use is restricted for competing in-memory data store services).

Business Source License restricts running it as a competing hosted service (converts to Apache-2.0 on 2030-11-01); single shared-nothing multi-threaded architecture differs operationally from Redis single-thread model

## Maintenance

Very active (v2.0.0 released 2026-09-16, last push 2026-09-26, about 31.7k stars) and production-positioned. It is a BUSL-1.1 source-available server, not a library, so evaluate the license and a few days of your own workload (as the FAQ advises) before replacing Redis.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party README numbers only. It gives memtier command lines and AWS instance types, but no CPU model, compiler, flags, Redis/Memcached versions or server configs, and no benchmark code is published. Redis's own 2022 reproduction on the same instance contradicts the headline.
- **Verifier notes:** The README numbers are transcribed accurately, but the headline overstates the win against a fairly configured Redis. Evidence from independent or third-party sources is contradictory or mixed. Tier stays C. The verdict is downgrade because the claim is overstated and the corroboration caveat was wrong. Metadata checks out: LICENSE.md is BSL 1.1 (gh reports NOASSERTION), 31,688 stars, last commit 2026-09-26, active.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/dragonflydb/dragonfly>
  - <https://github.com/dragonflydb/dragonfly#benchmarks>
  - <https://github.com/dragonflydb/dragonfly/blob/main/LICENSE.md>
  - <https://redis.io/blog/redis-architecture-13-years-later/>
  - <https://github.com/tidwall/cache-benchmarks>
  - <https://raw.githubusercontent.com/tidwall/cache-benchmarks/main/results/output.json>
- **Sources the enricher read:**
  - <https://github.com/dragonflydb/dragonfly>
  - <https://github.com/dragonflydb/dragonfly#benchmarks>
  - <https://github.com/dragonflydb/dragonfly/blob/main/LICENSE.md>
  - <https://github.com/dragonflydb/dragonfly/blob/main/docs/dashtable.md>
  - <https://github.com/dragonflydb/dragonfly/blob/main/docs/df-share-nothing.md>
  - <https://github.com/dragonflydb/dragonfly/blob/main/docs/differences.md>
  - <https://github.com/dragonflydb/dragonfly/blob/main/docs/faq.md>
  - <https://github.com/dragonflydb/dragonfly/blob/main/docs/build-from-source.md>
  - <https://github.com/dragonflydb/dragonfly/blob/main/docs/memcached_benchmark.md>
  - <https://github.com/dragonflydb/dragonfly/blob/main/docs/cluster-mode.md>
  - <https://github.com/dragonflydb/dragonfly/blob/main/CMakeLists.txt>
  - <https://github.com/dragonflydb/dragonfly/blob/main/.gitmodules>
  - <https://github.com/dragonflydb/dragonfly/blob/main/src/core/dash_internal.h>
  - <https://github.com/dragonflydb/dragonfly/blob/main/src/core/sse_port.h>
  - <https://github.com/dragonflydb/dragonfly/blob/main/src/server/detail/table.h>
  - <https://github.com/dragonflydb/dragonfly/blob/main/src/server/table.h>
  - <https://github.com/dragonflydb/dragonfly/blob/main/src/server/db_slice.cc>
  - <https://github.com/dragonflydb/dragonfly/blob/main/src/server/dfly_main.cc>
  - <https://github.com/dragonflydb/dragonfly/blob/main/src/server/main_service.cc>
  - <https://github.com/dragonflydb/dragonfly/blob/main/src/server/script_mgr.cc>
  - <https://github.com/dragonflydb/dragonfly/blob/main/src/facade/memcache_parser.cc>
  - <https://github.com/dragonflydb/dragonfly/releases/tag/v2.0.0>
  - <https://github.com/dragonflydb/dragonfly/security/advisories>
  - <https://github.com/dragonflydb/dragonfly/issues/8269>
  - <https://github.com/dragonflydb/dragonfly/issues/8275>
  - <https://github.com/dragonflydb/dragonfly/issues/8361>
  - <https://github.com/dragonflydb/dragonfly/issues/6545>
  - <https://github.com/dragonflydb/dragonfly/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/romange/helio/blob/master/CMakeLists.txt>
  - <https://redis.io/blog/redis-architecture-13-years-later/>
  - <https://github.com/tidwall/cache-benchmarks>
  - <https://raw.githubusercontent.com/tidwall/cache-benchmarks/main/results/output.json>
  - <https://hn.algolia.com/api/v1/search?query=dragonfly%20redis&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/dragonflydb/dragonfly`) · [data/wave6/enrich/raw/github_com_dragonflydb_dragonfly.json](../../../data/wave6/enrich/raw/github_com_dragonflydb_dragonfly.json) (enrichment confidence 0.8)

</details>
