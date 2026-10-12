# Pogocache

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Multithreaded C cache server speaking RESP, memcache, HTTP and Postgres; about 2x Redis and 1.2-2.3x memcached throughput (author-run).

| | |
|---|---|
| **Beats** | Redis, Memcached |
| **Claimed result** | cache-benchmarks results/output.json (median of 31 runs, pipeline 1, 8 server threads): Pogocache 1.2.0 GET 3,080,753 ops/s vs Redis 8.2.1 1,513,408 (\~2.0x) and memcached 1.6.38 2,601,307 (\~1.18x); SET 2,948,581 vs Redis 1,669,915 (\~1.8x) and memcached 1,271,805 (\~2.3x) (ratios derived from page data). GET p99 is 0.119 ms vs Redis 0.207 ms and memcached 0.191 ms. CPU cycles/op are \~7,053 vs Redis \~9,957 and memcached \~13,400 (derived from page data: perf cycles / total ops). Pogocache beats both Redis and memcached on SET and GET at every thread count (1-16) and pipeline depth (1/10/25/50) in the suite. The figures 3,145,960 vs Redis 909,837 (\~3.5x), 111us and 6968 cycles come from the hidden table in the Pogocache README. That table records the older July 2025 run (Pogocache v0.0.1, Redis 8.0.2; cache-benchmarks commit adc83b4) and is overstated against current results. |
| **Workload** | memtier_benchmark with 16 client threads x 16 connections (256 connections), each doing 100K SETs then 100K GETs with random 1-1024 B values. The server is pinned to cores 0-15 and configured with 1-16 I/O threads; memtier runs on cores 16-31. Pipelining is 1/10/25/50, over a local UNIX socket with persistence off, on AWS c8g.8xlarge (32-core ARM64). Each point is the median of 31 runs, with a warmup SET pass excluded. |
| **Metric** | throughput |
| **Hardware** | AWS c8g.8xlarge, 32-core non-NUMA ARM64 |
| **Adoption** | 2.5k stars |
| **Last commit** | 2026-08-05 |
| **Links** | [repository](https://github.com/tidwall/pogocache) · [benchmark](https://github.com/tidwall/cache-benchmarks) |

## Verdict

The only benchmark is the author's cache-benchmarks suite: memtier_benchmark with 256 connections over a local UNIX socket, 1-1024 B values, persistence off, server pinned to 16 cores of an AWS c8g.8xlarge (ARM64), median of 31 runs. At 8 threads and pipeline 1, Pogocache 1.2.0 did 3.08M GET/s and 2.95M SET/s vs 1.51M/1.67M for Redis 8.2.1 and 2.60M/1.27M for memcached 1.6.38, with GET p99 of 0.119 ms vs 0.207 ms and 0.191 ms. It beats Redis, Valkey, memcached and Dragonfly in every thread/pipeline cell (smallest margin: 1.07x over memcached on GET at 1 thread, pipeline 10). No compiler flags are stated, and the older README table (about 3.5x Redis) is stale.

## Use it when

- Plain string GET/SET caching (sessions, rendered pages, query results; the benchmark used 1 B-1 KB values) where you want more ops per core than Redis or memcached and don't need Redis data types.
- Request/response traffic with little or no pipelining (depth 1-10) from many connections. This is where the author's suite shows the largest margins: about 2x Redis at 8 threads, with GET p99 of 0.12 ms vs 0.21 ms for Redis.
- CPU- or cost-limited hosts: about 7.1K CPU cycles per operation vs about 10K for Redis and 13.4K for memcached in the author's perf runs.
- Replacing memcached for text-protocol clients when you also want TLS, a password, HTTP access and manual SAVE/LOAD snapshots in one binary on Linux or macOS.
- An in-process cache in C/C++: drop in pogocache.c for a thread-safe sharded map with TTLs, eviction/notify callbacks and CAS, with no network hop.

## Skip it when

- You need Redis beyond strings. There are no hashes, lists, sets, sorted sets, streams, pub/sub, MULTI/EXEC, Lua, INFO/HELLO/CLIENT, or databases other than 0 (SELECT only accepts 0). Lists and other types are an open request (issue #14).
- You need replication, failover or clustering. None exist, and high availability has been 'in the works' since Aug 2025 (issue #20). Persistence is only a manual SAVE/LOAD or a save on clean shutdown via --persist.
- Deeply pipelined clients (depth 25-50). In the same suite Garnet beats it on GETs in 34 of 36 pipelined configurations, e.g. 29.5M vs 11.4M ops/s at 8 threads, pipeline 50.
- Strict memory caps. The limit works by polling process RSS once a second. A third-party test with 1 MiB values on a Raspberry Pi 4 hit a VmHWM of 3.3 GB against --maxmemory 2 GiB (about 50% over).
- Risk-averse production. It was first released in July 2025 by a single company/maintainer, and the only published throughput benchmark is the author's own.

## How it is fast

Keys are hashed with th64 (random seed per process) into one of 4096 shards by default. Each shard is an independent Robin Hood open-addressing table with 10-byte buckets (48-bit entry pointer, 24-bit hash fragment, 1-byte distance-to-bucket) guarded by its own compare-and-swap spinlock, so two threads rarely wait on the same lock. Each entry is one heap allocation (mimalloc by default) with keys packed at 6 bits per character ('sixpack'). Networking runs one epoll/kqueue loop per thread with connections assigned round-robin; each tick batches reads, command execution and writes, using io_uring to submit the batched reads/writes on Linux when enough sockets are ready, and low-memory eviction uses 2-random sampling instead of maintaining an LRU list.

## Compared with alternatives

Pick Pogocache over Dragonfly when clients mostly GET/SET strings at low pipeline depth and CPU per request matters: it beat Dragonfly in every thread/pipeline cell of the author's suite, by 1.1x to 5x. Pick Garnet instead for heavily pipelined clients, and Dragonfly when you need broader Redis command coverage. The embedded pogocache.c plays the in-process role for C that Caffeine plays on the JVM.

## Integration

| | |
|---|---|
| **Form** | source-drop: the server binary is built with make (static release builds and a Docker image exist); pogocache.c + pogocache.h are embeddable |
| **Dependencies** | The server build git-clones and statically links mimalloc 3.1.5, jemalloc 5.3.0, liburing 2.12 (Linux) and OpenSSL 3.5.2, which needs cmake, autotools and perl at build time. Each can be disabled with NOMIMALLOC/NOJEMALLOC/NOURING/NOOPENSSL=1. The embedded pogocache.c needs only the C standard library. |
| **Minimum toolchain** | C11 (stdatomic.h, static_assert) plus GCC/Clang extensions (__thread, __builtin_ia32_pause, -flto=auto); minimum compiler versions not documented |
| **Platforms** | 64-bit Linux and macOS (documented; CI on ubuntu-latest); x86-64 and aarch64 spin hints; benchmarked on ARM64 (AWS c8g); no Windows; the Makefile also has an Emscripten/WASM target |
| **Thread safety** | Server: one event loop per thread (default = core count). Embedded API: safe for concurrent use through per-shard spinlocks. Waiters busy-spin unless you supply a yield callback, and the usethreadbatch mode is non-reentrant. |
| **Drop-in for the baseline** | partial — it speaks the memcache text protocol (no meta or binary protocol; CAS is off unless --cas yes) and a RESP2 subset of Redis covering strings and TTLs. It listens on 127.0.0.1:9401 by default and has no Redis data structures, scripting, transactions, pub/sub or replication. |

## Gotchas

- CAS is disabled by default (--cas no). Memcache `gets` returns CAS 0 and every `cas` fails until the server is started with --cas yes.
- Hash buckets store 48-bit pointers. The build assumes heap addresses fit in 48 bits; compile with NO48BITPTRS to get 8-byte pointers on systems with larger virtual address spaces or tagged pointers.
- Embedded mode: the hash seed defaults to 0 (only the server picks a random seed), and there is no built-in memory limit; eviction happens only when the caller passes lowmem=true on store. The header comment says the default is 65536 shards, but the code uses 4096.
- It binds to loopback by default, so in Docker or Kubernetes you must pass -h 0.0.0.0 or clients get dropped connections (issue #21). The --auth password can only be given on the command line.

## Known shortcomings

- The \~3.5x-over-Redis figure is a stale July 2025 run against Redis 8.0.2; the current author-run suite shows \~2.0x Redis 8.2.1 and \~1.18x memcached GET at 8 threads. No compiler or flags. Garnet beats it at pipeline depths 25/50 (verifier downgrade).
- Garnet wins GET in 34 of 36 pipelined cells. Strings only (no Redis data types, pub/sub, MULTI or Lua), no HA/replication, SELECT 0 only. maxmemory is enforced by polling RSS once a second (a third-party Raspberry Pi 4 test ran \~50% over the limit). memcache CAS is off by default (every cas fails without --cas yes). Embedded mode uses hash seed 0 and no memory limit. The benchmarked 1.2.0 was AGPL; MIT only from 1.3.1. Source commits sparse since 2026-01.

## Caveats and trade-offs

The suite is written and run by Pogocache's author (tidwall), so it is not independent. No compiler or build flags are stated for any server; only versions and commits are given. The headline table in the Pogocache README (\~3.5x Redis) is stale: it comes from a July 2025 run with Redis 8.0.2. The current suite with Redis 8.2.1 shows \~2x on GET at 8 threads. The README claim 'faster than Garnet' holds only at low pipelining: at pipeline 25/50 Garnet beats Pogocache by a wide margin (e.g. 8 threads, pipeline 50: Garnet GET 29.5M vs Pogocache 11.4M ops/s). The cache-benchmarks repo has no license file.

Newer/less battle-tested than Redis/Memcached in production; supports Memcache, RESP and Postgres wire protocols but not full Redis command set (data structures, scripting, etc.)

## Maintenance

Releases are still coming (1.3.2, Aug 2026), but source changes have been sparse since Jan 2026 (later commits touch only Docker and README files). It has been MIT-licensed since the Nov 2025 relicense (first MIT release 1.3.1); versions 1.0.0-1.3.0, including the benchmarked 1.2.0, were AGPL-3.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** tidwall/cache-benchmarks publishes its benchmark code (bench-all.sh, cmd/bench/main.go) and raw results (results/output.json), with the hardware (AWS c8g.8xlarge) and server versions stated. It lists no compiler or build flags, and Pogocache's own author wrote and ran it, so it is first-party with partial methodology (C, not B).
- **Verifier notes:** The claim is sound against the baselines: Pogocache beats Redis and memcached at every configuration in the suite. However, the record's numbers are the stale README figures, now replaced by the current output.json medians. The tier drops from B to C because the only benchmark is author-run and has no compiler or flags. Metadata checks out: MIT, 2,518 stars, last commit 2026-08-05, active, not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tidwall/cache-benchmarks>
  - <https://github.com/tidwall/cache-benchmarks/blob/main/bench-all.sh>
  - <https://github.com/tidwall/cache-benchmarks/blob/main/config.jsonc>
  - <https://raw.githubusercontent.com/tidwall/cache-benchmarks/main/results/output.json>
  - <https://raw.githubusercontent.com/tidwall/cache-benchmarks/adc83b4d5be9af7fbda5ccf6db889ca1034e40e6/results/output.json>
  - <https://github.com/tidwall/pogocache>
- **Sources the enricher read:**
  - <https://github.com/tidwall/pogocache>
  - <https://github.com/tidwall/pogocache/blob/main/src/pogocache.h>
  - <https://github.com/tidwall/pogocache/blob/main/src/pogocache.c>
  - <https://github.com/tidwall/pogocache/blob/main/src/main.c>
  - <https://github.com/tidwall/pogocache/blob/main/src/net.c>
  - <https://github.com/tidwall/pogocache/blob/main/src/cmds.c>
  - <https://github.com/tidwall/pogocache/blob/main/src/memcache.c>
  - <https://github.com/tidwall/pogocache/blob/main/src/resp.c>
  - <https://github.com/tidwall/pogocache/blob/main/src/xmalloc.c>
  - <https://github.com/tidwall/pogocache/blob/main/src/uring.c>
  - <https://github.com/tidwall/pogocache/blob/main/src/save.c>
  - <https://github.com/tidwall/pogocache/blob/main/src/hashmap.c>
  - <https://github.com/tidwall/pogocache/blob/main/src/Makefile>
  - <https://github.com/tidwall/pogocache/blob/main/Makefile>
  - <https://github.com/tidwall/pogocache/blob/main/CONTRIBUTING.md>
  - <https://github.com/tidwall/pogocache/blob/main/.github/workflows/main.yml>
  - <https://github.com/tidwall/pogocache/blob/main/deps/build-uring.sh>
  - <https://github.com/tidwall/pogocache/blob/main/deps/build-mimalloc.sh>
  - <https://github.com/tidwall/pogocache/blob/main/deps/build-jemalloc.sh>
  - <https://github.com/tidwall/pogocache/blob/main/deps/build-openssl.sh>
  - <https://github.com/tidwall/pogocache/issues>
  - <https://github.com/tidwall/pogocache/issues/1>
  - <https://github.com/tidwall/pogocache/issues/2>
  - <https://github.com/tidwall/pogocache/issues/12>
  - <https://github.com/tidwall/pogocache/issues/14>
  - <https://github.com/tidwall/pogocache/issues/15>
  - <https://github.com/tidwall/pogocache/issues/20>
  - <https://github.com/tidwall/pogocache/issues/21>
  - <https://github.com/tidwall/pogocache/issues/22>
  - <https://github.com/tidwall/pogocache/issues/36>
  - <https://github.com/tidwall/pogocache/issues/38>
  - <https://github.com/tidwall/pogocache/issues/41>
  - <https://github.com/tidwall/pogocache/issues/51>
  - <https://github.com/tidwall/pogocache/releases>
  - <https://github.com/tidwall/pogocache/commits/main>
  - <https://github.com/tidwall/pogocache/commit/b99f9991>
  - <https://github.com/tidwall/cache-benchmarks>
  - <https://github.com/tidwall/cache-benchmarks/blob/main/bench-all.sh>
  - <https://github.com/tidwall/cache-benchmarks/blob/main/cmd/bench/main.go>
  - <https://raw.githubusercontent.com/tidwall/cache-benchmarks/main/results/output.json>
  - <https://github.com/imchuncai/umem-cache-benchmark/blob/master/Documentation/rpi4b/random-2g-1m.rst>
  - <https://raw.githubusercontent.com/imchuncai/umem-cache-benchmark/3edf0c18d3/Documentation/rpi4b/random-2g-1m.rst>
  - <https://hn.algolia.com/api/v1/search?query=pogocache&tags=story>
  - <https://news.ycombinator.com/item?id=44638076>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/tidwall/pogocache`) · [data/wave6/enrich/raw/github_com_tidwall_pogocache.json](../../../data/wave6/enrich/raw/github_com_tidwall_pogocache.json) (enrichment confidence 0.8)

</details>
