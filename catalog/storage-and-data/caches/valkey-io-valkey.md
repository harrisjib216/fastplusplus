# Valkey

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟢 active

> BSD-licensed fork of Redis OSS 7.2 whose async I/O threads give \~37% more SET throughput than Redis 8.0.

| | |
|---|---|
| **Beats** | Redis |
| **Claimed result** | Valkey 8.1.1 999.8K RPS on SET at 0.8ms p99 vs Redis 8.0 729.4K RPS on SET at 0.99ms p99. The page itself states '37% higher on SET and 16% higher on GET, alongside 30% faster p99 latencies for SET and 60%+ faster on GET' (these are stated, not derived). Absolute GET RPS is not printed in the text. |
| **Workload** | valkey-benchmark -t SET,GET -r 3000000 -d 1024 --threads 6: each iteration is 50M SETs followed by 50M GETs, with 1KB values and a 3M-key keyspace. Connection count was tuned per system: Valkey peaked at 400 connections, Redis at 384. Both servers ran in Docker with --io-threads 6 and persistence off (--save '' --appendonly no), pinned to 6 cores with NIC IRQs pinned to the other 2. |
| **Metric** | throughput |
| **Hardware** | AWS Graviton4-based c8g.2xlarge (8 vCPU) server in an EC2 cluster placement group; c8g.8xlarge (32 vCPU) load generator |
| **Compiler and flags** | Official Docker images valkey/valkey:8.1.1 and redis:8.0, run with --io-threads 6 --save '' --appendonly no --maxmemory 10gb; client was valkey-benchmark with --threads 6. Compiler/build flags of the images are not stated. |
| **Adoption** | 27.3k stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/valkey-io/valkey) · [benchmark](https://www.gomomento.com/blog/valkey-turns-one-how-the-community-fork-left-redis-in-the-dust/) |

## Verdict

Momento, a vendor that sells Valkey-based services, ran the official Docker images valkey/valkey:8.1.1 and redis:8.0 (build flags not stated) on the same AWS Graviton4 c8g.2xlarge, both with io-threads 6, persistence off and 6 pinned cores, driven by valkey-benchmark with 1 KB values, a 3M-key keyspace, no pipelining and per-server tuned connection counts. Valkey reached 999.8K vs 729.4K SET RPS (\~1.37x) at 0.8 vs 0.99 ms p99, and the post states +16% on GET; because Redis 8.0 has its own new I/O-threading implementation, this compares two threaded servers.

## Use it when

- You run Redis OSS 7.2 or older on a box with 6-8+ cores and one instance is saturating its main thread on simple GET/SET. Turning on io-threads can take one node from roughly 240K to about 1M RPS (1 KB values) without sharding or pipelining.
- Many concurrent connections (hundreds) with small or medium values (512 B-1 KB), where the network syscalls and parsing, not command logic, eat the CPU.
- Memory-bound caches holding many small keys: the 8.1 hash table saves about 20 B per key (about 30 B per key with a TTL) over the old dict.
- You need a permissively licensed (BSD-3-Clause) Redis-compatible server rather than Redis 8's RSALv2/SSPLv1/AGPLv3 choice.
- Workloads that do not shard well, such as hot keys, large collections or same-slot multi-key operations, where a bigger, faster single shard helps.

## Skip it when

- Small boxes (3-4 cores or fewer) or io-threads left at 1. Momento measured parity without I/O threads (239K vs 235K SET RPS), and the two were neck-and-neck until the 4th thread.
- You depend on Redis CE 7.4+ or Redis 8.x. Their RDB files cannot be loaded by Valkey, and Redis 8's built-in Query Engine, JSON, time series, probabilistic types and vector sets are not part of the Valkey core server.
- You need well beyond \~1M simple ops/s on one node. Command execution is still single-threaded, and designs that execute commands on multiple threads report higher per-node numbers.
- Tail latency matters and connection counts are untuned. Going from 400 to 1024 connections doubled Valkey's p99 from 0.8 ms to 1.6 ms. At 256 connections with 6 threads, Redis 8.0's p99 (0.84 ms) was actually lower than Valkey's (0.93 ms).
- Over-provisioning io-threads: open issue #4114 (2026-07) shows io-threads 8 running slower than io-threads 4 on a 32-core host, because idle I/O threads burn cycles in their polling loop.

## How it is fast

Valkey 8.0's async I/O threading (an AWS contribution) keeps all command execution on the single main thread but hands socket reads and RESP parsing, reply writes, epoll_wait and object frees to worker threads as jobs, scaling the number of active I/O threads with load (current unstable passes jobs over lock-free SPMC/MPSC/SPSC ring queues). Before running each batch of parsed commands, the main thread interleaves and prefetches the hash-table lookups for every key in the batch ("memory access amortization", memory_prefetch.c), so cache misses overlap instead of stalling one after another. AWS reports this cut lookupKey time by more than 80% and added almost 50% throughput. Valkey 8.1 also replaced the chained dict with a hash table of 64-byte, cache-line buckets (7 slots plus 1-byte secondary hashes, inspired by Swiss tables), which cuts a lookup to about two memory accesses and saves about 20 bytes per key.

## Compared with alternatives

Pick Valkey over Dragonfly, Garnet or Pogocache when you want the actual Redis OSS codebase (same RDB/AOF files, config and module API), so migration is effectively an upgrade, and \~1M RPS per 8-vCPU node is enough. Garnet's paper uses Valkey 8.1 as the baseline it beats, and Pogocache reports \~2x Redis 8.2.1 GET throughput, so those win when raw per-node throughput matters more than byte-level Redis compatibility.

## Integration

| | |
|---|---|
| **Form** | server binary built with make (CMake build is marked experimental); official valkey/valkey Docker images |
| **Dependencies** | Vendored in deps/: jemalloc (default allocator on Linux), Lua, libvalkey, linenoise, hdr_histogram, fpconv, lz4, fast_float. Optional: OpenSSL (TLS), librdmacm/libibverbs (experimental RDMA), libsystemd, static Zstandard &gt;= 1.4.7, libbacktrace. |
| **Minimum toolchain** | C compiler with gnu11 (C11 _Atomic). The Makefile probes for it and falls back to -std=c99. Default -O3. |
| **Platforms** | Linux, macOS, OpenBSD, NetBSD, FreeBSD; big- and little-endian; 32- and 64-bit; Solaris best effort. The hash table has x86 SIMD and ARM NEON paths; the TSC/CNTVCT hardware clock is used on x86-64 Linux and aarch64. RDMA is Linux-only and experimental. |
| **Thread safety** | Network server: any number of clients, but every command runs on the main thread. I/O threads only do socket read/parse, write, polling and frees, so command semantics stay single-threaded and atomic, as in Redis. |
| **Drop-in for the baseline** | partial — drop-in for Redis OSS 2.x-7.2.x (protocol, config, RDB/AOF, RedisModule_ API; `make install` creates redis-server/redis-cli symlinks), but not for Redis CE 7.4+/8.x data files or Redis 8's integrated modules |

## Gotchas

- io-threads is off by default and must be set explicitly. The count includes the main thread (io-threads 9 = main thread + 8 I/O threads). valkey-benchmark also needs --threads, or it cannot show the gain.
- With I/O threads on, the main and I/O threads busy-poll, so OS CPU usage reads near 100% even when the server is lightly loaded (issue #4001; noted in the 9.1 release post). Plan capacity with the main/I/O thread usage metrics added in 9.1.
- INFO reports redis_version:7.2.4 for compatibility. Tools must read server_name/valkey_version to detect Valkey and its real version.
- It shares Redis's Lua attack surface (CVE-2025-49844, a Lua use-after-free that can lead to RCE). 2026 brought several high-severity use-after-free advisories (TLS, stream deserialization, RDMA, the Lua debugger), plus an io-threads + TLS assertion crash (#4347, fixed), so stay on current patch releases (9.1.2 / 9.0.6 / 8.1.10, 2026-09-01).

## Known shortcomings

- The 37%/16% SET/GET gains vs Redis 8.0 come from a Momento blog; Momento sells hosted Valkey, so the source is not independent.
- No gain on small machines: parity without io-threads (239K vs 235K) and tied up to 4 threads. At 256 connections Redis 8.0 p99 (0.84 ms) beats Valkey (0.93 ms); p99 doubles at 1024 connections. Too many io-threads can be slower (#4114); CPU shows \~100% from busy polling (#4001). Cannot load Redis 7.4+/8 RDB files; Redis 8 built-in modules absent; several high-severity use-after-free advisories in 2026.

## Caveats and trade-offs

Momento (the blog's publisher) is a caching-as-a-service vendor that also sells Valkey-based products (valkey-router, valkey-operator), so it is not a fully neutral third party even though it is independent of the Valkey project itself; the article includes a 'Try it Yourself' reproduction section but does not link a public benchmark-code repository, so it falls short of tier A. A secondary aggregator blog (andrewbaker.ninja, 2026-01-04) cites the same 37%/999.8K-RPS figures, corroborating they were not altered in transmission. [retier] Evidence is a blog by Momento, a vendor selling hosted Valkey (not independent).

Valkey originated as a community fork of Redis (created when Redis relicensed away from BSD) and has since added its own multi-threaded I/O path in the 8.x line, which is the source of this speedup; API/RESP-protocol compatible so migration cost from Redis is low, but as with any fork it can diverge over time from upstream Redis modules and Redis Enterprise-only features.

## Maintenance

Very active BSD-3-Clause server under LF Projects (commits on 2026-09-26, 9.2.0-rc1 on 2026-09-16, patch releases still shipping for the 8.0, 8.1, 9.0 and 9.1 lines, 27.3k stars) that you deploy, not a library you vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now C.
- **Tier reason:** Momento's blog (Khawaja Shams, 2025-05-07) is independent of the Valkey project and runs Valkey 8.1.1 against Redis 8.0 on the same c8g.2xlarge. It gives the exact docker and valkey-benchmark commands and states 999.8K vs 729.4K SET RPS, '37% higher on SET and 16% higher on GET', and 30%/60%+ faster p99. It falls short of A because the servers are official Docker images with unstated compiler/flags, and no benchmark repo is linked. B follows the batch-39 precedent that an independent vendor blog counts as B.
- **Retiered** B to C: Orchestrator consistency retier: the only numbers come from a Momento blog, and Momento sells a managed Valkey service, so the source is a vendor, not an independent suite or peer-reviewed paper. Same rule as other vendor-blog evidence in waves 5-6: tier C.
- **Verifier notes:** I verified every figure on the page. One small fix: the 16%/60%+ figures are printed on the page, not derived. The page's headline has a typo, 'Redis 8.0 got as high as 729.4 RPS'; the connection-tuning section confirms 729.4K. Valkey is a hard fork of Redis per its README (GitHub fork flag false), so I set is_fork_of. Metadata matches: BSD-3-Clause, 27,299 stars, last commit 2026-09-26. The author is at Momento, which sells Valkey-based services, so the tier holds only if interested-vendor blogs count as B; otherwise it is C.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `is_fork_of`, `caveats`
- **Pages the verifier opened:**
  - <https://www.gomomento.com/blog/valkey-turns-one-how-the-community-fork-left-redis-in-the-dust/>
  - <https://andrewbaker.ninja/2026/01/04/redis-vs-valkey-a-deep-dive-for-enterprise-architects/>
  - <https://github.com/valkey-io/valkey>
- **Sources the enricher read:**
  - <https://github.com/valkey-io/valkey>
  - <https://github.com/valkey-io/valkey/blob/unstable/README.md>
  - <https://github.com/valkey-io/valkey/blob/unstable/src/io_threads.c>
  - <https://github.com/valkey-io/valkey/blob/unstable/src/memory_prefetch.c>
  - <https://github.com/valkey-io/valkey/blob/unstable/src/hashtable.c>
  - <https://github.com/valkey-io/valkey/blob/unstable/src/queues.h>
  - <https://github.com/valkey-io/valkey/blob/unstable/src/Makefile>
  - <https://github.com/valkey-io/valkey/blob/unstable/valkey.conf>
  - <https://github.com/valkey-io/valkey/releases>
  - <https://github.com/valkey-io/valkey/security/advisories>
  - <https://github.com/valkey-io/valkey/issues/4114>
  - <https://github.com/valkey-io/valkey/issues/4001>
  - <https://github.com/valkey-io/valkey/issues/2055>
  - <https://github.com/valkey-io/valkey/issues/4347>
  - <https://github.com/valkey-io/valkey/issues?q=io-threads>
  - <https://github.com/valkey-io/valkey-io.github.io/blob/main/content/blog/2024-07-07-unlock-one-million-rps.md>
  - <https://github.com/valkey-io/valkey-io.github.io/blob/main/content/blog/2024-09-13-unlock-one-million-rps-part2.md>
  - <https://github.com/valkey-io/valkey-io.github.io/blob/main/content/blog/2025-03-28-new-hash-table/index.md>
  - <https://github.com/valkey-io/valkey-io.github.io/blob/main/content/blog/2026-05-19-valkey-9-1-delivers-improvements-in-security-performance-and-more/index.md>
  - <https://github.com/valkey-io/valkey-doc/blob/main/topics/migration.md>
  - <https://github.com/redis/redis/releases/tag/8.0.0>
  - <https://www.gomomento.com/blog/valkey-turns-one-how-the-community-fork-left-redis-in-the-dust/>
  - <https://hn.algolia.com/api/v1/search?query=valkey%20redis%20benchmark&tags=story>
  - <https://hn.algolia.com/api/v1/items/45069760>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/valkey-io/valkey`) · [data/wave6/enrich/raw/github_com_valkey_io_valkey.json](../../../data/wave6/enrich/raw/github_com_valkey_io_valkey.json) (enrichment confidence 0.82)

</details>
