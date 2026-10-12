# KeyDB

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟡 stale

> Multithreaded C++ Redis 6.2 fork serving one keyspace from many event-loop threads; claims \~7x Redis 6 throughput under TLS.

| | |
|---|---|
| **Beats** | Redis |
| **Claimed result** | over 7x faster than Redis when using TLS (KeyDB close to 1M ops/s with TLS at 16 server threads vs \~130k ops/s for Redis 6 with TLS); Redis with TLS drops 36% vs single-threaded non-TLS Redis and 61% vs non-TLS Redis with io-threads, while KeyDB shows almost no decline using TLS; latency claimed up to 7x lower |
| **Workload** | memtier_benchmark --tls --threads=32 (op mix/key sizes not stated on page, i.e. memtier defaults); client on AWS m5.8xlarge (32 cores), KeyDB/Redis servers on m5.4xlarge; KeyDB --server-threads 16 --server-thread-affinity true vs Redis 6 TLS (no io-threads in its TLS start command) |
| **Metric** | throughput |
| **Hardware** | AWS m5.8xlarge (client, 32 cores), m5.4xlarge (server instances) — CPU model not stated |
| **Adoption** | 12.5k stars |
| **Last commit** | 2024-04-04 |
| **Links** | [repository](https://github.com/Snapchat/KeyDB) · [benchmark](https://docs.keydb.dev/blog/2020/09/29/blog-post/) |

## Verdict

KeyDB's own blog (Sept 2020) drove servers on an AWS m5.4xlarge from an m5.8xlarge with memtier_benchmark --tls --threads=32 and otherwise default settings: KeyDB with 16 server threads and TLS got close to 1M ops/s (about 800k with 8 threads) versus \~130k ops/s for single-threaded Redis 6.0 with TLS, which is 36% below non-TLS single-threaded Redis and 61% below non-TLS Redis with io-threads. CPU model, compiler, build flags and exact versions are not given, Redis was not sharded or run as several instances, and the 'up to 7x lower latency' claim has no table.

## Use it when

- A single Redis 6.x node that is CPU-bound on networking, TLS or protocol parsing (many connections, small GET/SET values) and you want more ops/s from one box without sharding into Redis Cluster or running one instance per core
- TLS-terminated Redis traffic: the benchmarked Redis 6 could not combine io-threads with TLS, while KeyDB does TLS on every server thread
- Existing Redis 6.x deployments on Linux (Redis 6 RDB files, modules, Lua) that want a binary swap and can tolerate a stale codebase
- You specifically need active-active (multi-master) replication or per-member hash/set expiry, which upstream Redis does not provide

## Skip it when

- New production deployments: no commits since April 2024, last release v6.3.4 (Oct 2023), the lead developer left Snap in early 2025 and told users to move to Valkey, and deadlock/crash issues (e.g. #883 replication deadlock, #743, #827) remain open
- Anything needing Redis 7+ commands or data: RDB_VERSION is 9, so Redis 7 dumps (RDB v10) fail to load (#527) and Redis 7 commands such as PEXPIRETIME are missing
- Write-heavy or hot-key workloads and long MULTI/EXEC or Lua: every command still runs under one global lock (transactions hold it for the whole EXEC), so parallelism is limited to I/O and parsing
- Non-Linux hosts, and ARM with caution: the threading model relies on Linux SO_REUSEPORT load balancing, and there are open ARM startup-assert reports (#856)
- Multi-master or FLASH setups you cannot babysit: FLASH is labelled experimental/beta, active replication has an open data-consistency report (#366), and HN users reported cluster-wide crashes and deadlocks in multi-master mode

## How it is fast

It runs the stock Redis ae event loop on N threads and pins each connection to one thread at accept() (spread with Linux SO_REUSEPORT plus active client balancing), so socket I/O, TLS and RESP parsing run in parallel. Command execution against the shared keyspace is still serialized by a single global lock: a fair ticket spinlock ('fastlock', with an x86-64 assembly fast path) that spins with pause/yield and falls back to a futex wait, and that uses otherwise wasted spin time to do incremental dict rehashing ('async rehash'). KEYS/SCAN, and optionally GET/MGET ('enable-async-commands') and in-process BGSAVE ('use-fork no'), read from copy-on-write MVCC snapshots of the database so they do not hold the global lock.

## Compared with alternatives

No siblings catalogued yet.

## Integration

| | |
|---|---|
| **Form** | standalone server binary (keydb-server, built with make; Docker image eqalpha/keydb); not a linkable library |
| **Dependencies** | Bundled in deps/: jemalloc, Lua, hiredis, linenoise, hdr_histogram, moodycamel concurrentqueue, cpp-statsd-client, memkind (optional), RocksDB submodule (FLASH only). System: OpenSSL (TLS on by default), libuuid, libcurl (MOTD, disable with NO_MOTD=yes), nasm (x86-64 spinlock), bz2/zstd/lz4/snappy for RocksDB builds; Makefile can link system jemalloc/RocksDB/hiredis instead |
| **Minimum toolchain** | C++17 (-std=c++17 -fno-rtti) plus C11/C99 for the C files; GCC or Clang (Clang builds use libc++); GCC 13.1 build fixed in 6.3.4; minimum compiler versions not documented |
| **Platforms** | Linux (tested); x86-64 gets the assembly spinlock, aarch64 builds exist but have open crash reports; FreeBSD compiles as of 6.3.4; macOS builds but README says only Linux is supported for the threading model |
| **Thread safety** | Server process, so clients get Redis semantics; internally a global keyspace spinlock, EXEC holds it for the whole transaction, and modules run under a GIL taken only when all server threads are paused. With enable-async-commands, writes from other clients may become visible after a delay (max-snapshot-slip); use LFENCE if you need cross-client ordering |
| **Drop-in for the baseline** | partial — protocol, modules, scripts and config compatible with Redis 6.2 (io-threads is aliased to server-threads), but no Redis 7+ commands or RDB v10 and the multithreading is Linux-only |

## Gotchas

- server-threads should follow NIC queue count, not core count: the README recommends 4 (default 2) and warns more threads can be slower because the global lock is a spinlock, yet the headline TLS benchmark used 16 threads with affinity
- An existing redis.conf with 'io-threads 8' silently becomes 8 KeyDB server threads, since io-threads is an alias for server-threads
- KeyDB expects exclusive use of its cores (spinning waiters burn CPU), and keydb-benchmark/redis-benchmark are single-threaded and too slow to measure it; use memtier on separate cores
- multi-master-no-forward yes loses data unless every master is in a full mesh; enable-async-commands relaxes cross-client read-your-writes ordering and currently covers only GET/MGET

## Known shortcomings

- Dead in practice: last commit 2024-04, last release v6.3.4 (2023-10); the lead developer left Snap in early 2025 and pointed users to Valkey (#895); open deadlock/crash issues (#883, #743, #827). Stuck at Redis 6.2 (can't load Redis 7 dumps, #527). A global spinlock still serializes every command, so gains shrink for writes, hot keys and long EXEC/Lua. The benchmark used 16 server-threads (README recommends 4) against an unsharded Redis, with no CPU/compiler/flags; the '7x lower latency' claim has no data. Threading needs Linux SO_REUSEPORT; ARM startup assert (#856); FLASH is beta; multi-master consistency/crash reports (#366). An existing redis.conf 'io-threads' line silently maps to server-threads.

## Caveats and trade-offs

First-party blog benchmark (KeyDB's own team); AWS instance types stated but not the CPU model, compiler, or build flags; memtier op mix and key sizes not stated; Redis TLS run was started without io-threads while KeyDB used 16 server threads; repository has had no commits since April 2024 even though the fork's changes are still substantive vs upstream Redis

Multithreading changes the concurrency/atomicity model vs Redis (MVCC-style access under a global lock for KEYS/SCAN); staying in sync with upstream Redis features is ongoing maintenance burden for a fork

## Maintenance

Stale: last release v6.3.4 (Oct 2023) and last commit April 2024, and the lead developer, leaving Snap, recommended Valkey. The code is BSD-3-Clause and builds with make, but anyone adopting it maintains the fork themselves.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party KeyDB blog (Ben Schermel, Sept 2020) compares KeyDB vs Redis 6 with TLS: 'close to 1 million ops/sec' vs '\~130k ops/sec', 'over 7X faster', with memtier and server command lines shown and AWS instance types. There is no CPU model, compiler, build flags or published benchmark harness, so it is first-party with partial methodology: C.
- **Verifier notes:** Metadata checked via gh: BSD-3-Clause, not archived, 12,504 stars, not a GitHub fork (README calls it 'a high performance fork of Redis', so is_fork_of kept). Latest main commit 603ebb27 has author date 2024-03-21 and committer date 2024-04-04; last_commit set to the committer date. The record's '61% with io-threads+TLS' wording was wrong: the page's 61% is TLS Redis vs non-TLS Redis with io-threads.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://docs.keydb.dev/blog/2020/09/29/blog-post/>
  - <https://github.com/Snapchat/KeyDB>
- **Sources the enricher read:**
  - <https://github.com/Snapchat/KeyDB>
  - <https://github.com/Snapchat/KeyDB/blob/main/README.md>
  - <https://github.com/Snapchat/KeyDB/blob/main/src/Makefile>
  - <https://github.com/Snapchat/KeyDB/blob/main/src/fastlock.h>
  - <https://github.com/Snapchat/KeyDB/blob/main/src/fastlock.cpp>
  - <https://github.com/Snapchat/KeyDB/blob/main/src/aelocker.h>
  - <https://github.com/Snapchat/KeyDB/blob/main/src/snapshot.cpp>
  - <https://github.com/Snapchat/KeyDB/blob/main/src/db.cpp>
  - <https://github.com/Snapchat/KeyDB/blob/main/src/rdb.cpp>
  - <https://github.com/Snapchat/KeyDB/blob/main/src/rdb.h>
  - <https://github.com/Snapchat/KeyDB/blob/main/src/server.cpp>
  - <https://github.com/Snapchat/KeyDB/blob/main/src/config.cpp>
  - <https://github.com/Snapchat/KeyDB/blob/main/src/version.h>
  - <https://github.com/Snapchat/KeyDB/blob/main/keydb.conf>
  - <https://github.com/Snapchat/KeyDB/blob/main/.gitmodules>
  - <https://github.com/Snapchat/KeyDB/releases>
  - <https://github.com/Snapchat/KeyDB/releases/tag/v6.3.4>
  - <https://github.com/Snapchat/KeyDB/releases/tag/v6.3.0>
  - <https://github.com/Snapchat/KeyDB/releases/tag/v6.2.0>
  - <https://github.com/Snapchat/KeyDB/commits/main>
  - <https://github.com/Snapchat/KeyDB/issues/839>
  - <https://github.com/Snapchat/KeyDB/issues/923>
  - <https://github.com/Snapchat/KeyDB/issues/895>
  - <https://github.com/Snapchat/KeyDB/issues/798#issuecomment-2214123117>
  - <https://github.com/Snapchat/KeyDB/issues/527>
  - <https://github.com/Snapchat/KeyDB/issues/883>
  - <https://github.com/Snapchat/KeyDB/issues/856>
  - <https://docs.keydb.dev/blog/2020/09/29/blog-post/>
  - <https://news.ycombinator.com/item?id=36018149>
  - <https://news.ycombinator.com/item?id=31796311>
  - <https://news.ycombinator.com/item?id=35990897>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/snapchat/keydb`) · [data/wave6/enrich/raw/github_com_snapchat_keydb.json](../../../data/wave6/enrich/raw/github_com_snapchat_keydb.json) (enrichment confidence 0.8)

</details>
