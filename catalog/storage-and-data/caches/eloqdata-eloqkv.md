# EloqKV

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `GPL-2.0-only OR AGPL-3.0-only` · 🟢 active

> Multi-threaded Redis-API distributed KV database with ACID transactions; vendor benchmark shows about 4.5-8.5x single-threaded Redis throughput.

| | |
|---|---|
| **Beats** | Redis |
| **Claimed result** | Text: 'EloqKV and DragonflyDB both outperform Redis due to their support for multiple worker threads' and 'both significantly outperform Redis, both in throughput and in latency'. The chart images (read by eye, approximate) show Redis flat at about 200 KOps at every concurrency. EloqKV is about 950 KOps at 128 connections, about 1,400 at 256, and about 1,600-1,700 at 512-1024, roughly 4.5-8.5x Redis. Redis P999 reaches about 11-12 ms at 1024 connections vs about 3 ms for EloqKV. DragonflyDB is slightly ahead of EloqKV throughout. |
| **Workload** | memtier_benchmark write-only (ratio 1:0), read-only (ratio 0:1), and mixed (ratio 1:10 put:get) workloads against a single-node in-memory-only (persistence/WAL disabled) instance, 128-byte values, 5,000,000-key keyspace, concurrency swept from 128 to 1024 (32 threads x 4/8/16/32 clients), 300s test runs |
| **Metric** | throughput |
| **Hardware** | AWS EC2, region us-east-1, Ubuntu 22.04: server = c7g.8xlarge (Graviton, ARM64) running Redis 7.2.5 / DragonflyDB 1.21.2 / EloqKV 0.7.4 one at a time; client = c6gn.8xlarge running memtier_benchmark |
| **Adoption** | 1.5k stars |
| **Last commit** | 2026-09-17 |
| **Links** | [repository](https://github.com/eloqdata/eloqkv) · [benchmark](http://web.archive.org/web/20260616115015/https://eloqdata.com/blog/2024/08/17/benchmark-single-node) |

## Verdict

EloqData's own August 2024 post (now only on the Wayback Machine) tested EloqKV 0.7.4 with WAL and data store off against Redis 7.2.5 (persistence off, no io-threads) and DragonflyDB 1.21.2. Server: one AWS c7g.8xlarge Graviton. Client: memtier_benchmark on a c6gn.8xlarge. Workload: 128-byte values, 5M keys, 128-1024 connections, 300 s runs. Read by eye from the charts, Redis stays near 200K ops/s while EloqKV rises from about 950K to 1.7M ops/s (roughly 4.5-8.5x), and at 1024 connections P999 is about 3 ms for EloqKV versus 11-12 ms for Redis. No compiler or build flags are given, and the page itself says Redis would normally run as a multi-instance cluster on such a machine.

## Use it when

- You want one large multi-core Redis-API node instead of running a Redis Cluster, and the traffic is mostly simple string, hash, list, set or sorted-set commands. The benchmark used 128-byte values, 5M keys and 128-1024 connections.
- You need real multi-key atomicity: BEGIN/COMMIT/ROLLBACK sessions, MULTI/EXEC that rolls back on error, or Lua scripts that read and create keys across nodes without hash-tag co-location.
- You want Redis-API data that survives power loss (WAL on) and can be larger than RAM, with cold data on local disk or object storage. A metadata store is a better fit than a throwaway cache.
- You run on Linux x86-64 or ARM64 (the benchmark host was Graviton) and can use the Ubuntu 24.04 release tarballs or a privileged Docker container.

## Skip it when

- Production or commercial use of a build from this repo without a deal with EloqData. On 2026-01-27 the required data_substrate/tx_service submodule moved from GPLv2/AGPLv3 to a 'Business Source License 2.0' text. That license allows only non-production, non-commercial use until the 2031-01-08 change date.
- Apps that need commands with no handler registered in src/redis_service.cpp at HEAD: Streams (XADD), HyperLogLog (PFADD), Geo, RENAME, COPY, OBJECT, WAIT, TOUCH, RANDOMKEY, FUNCTION/FCALL, BZPOPMIN/BZPOPMAX and HELLO (so no RESP3). The vendor compatibility page also marks ACL users, CLIENT TRACKING, MONITOR and SCRIPT KILL as unsupported.
- Pure in-memory cache throughput is the only goal. In EloqData's own test DragonflyDB was slightly ahead on every workload, with lower P999 latency on the read-only and mixed runs.
- Code that depends on exact Redis semantics. On the first runtime error, MULTI/EXEC aborts the whole transaction (#502). OCC conflicts make MULTI and Lua re-run from the start, so a PUBLISH inside a script can be delivered twice (#500). Pub/Sub is best-effort, process-local plus forwarding, and not scoped by namespace (#499).
- You need proven HA and correctness under faults. The shipped eloqkv.ini says node_group_replica_num currently supports only 1, which means no automatic failover. An internal Jepsen run that ended with no responsive nodes is still open (#188).

## How it is fast

It uses a thread-per-core, shared-nothing design. Keys are partitioned (Redis CRC16 hash slots) into one CcShard per core, and each shard is driven by one TxProcessor. Work for another shard is passed to that shard as a message, not done under a lock, so each shard's state has a single writer. With external processing on (the CMake default), brpc worker N runs the processing round for shard N, so a command can be parsed and executed on the same worker without a thread hand-off. Each shard also allocates from its own mimalloc heap. Networking uses io_uring by default; the 2024 benchmark post said io_uring networking was missing then and that EloqKV was bound by the network stack. The margin over Redis comes mostly from using all 32 vCPUs where Redis runs commands on one thread.

## Compared with alternatives

Pick EloqKV over Dragonfly, Valkey or KeyDB when you need ACID BEGIN/COMMIT/ROLLBACK, cross-node transactions without hash tags, or durable larger-than-RAM data behind the Redis API. For a pure in-memory cache, Dragonfly was slightly faster than EloqKV even in EloqData's own benchmark.

## Integration

| | |
|---|---|
| **Form** | standalone server binary (Docker image eloqdata/eloqkv, Ubuntu 24.04 tarballs, or CMake source build); clients connect over the Redis protocol |
| **Dependencies** | data_substrate (eloqdata/tx_service, BSL 2.0) and its Log Service; brpc, gflags, glog, abseil, gRPC, RocksDB/rocksdb-cloud or EloqStore, mimalloc, OpenSSL, libcurl for cloud stores; vendored Lua, crcspeed and fpconv |
| **Minimum toolchain** | C++20 and CMake 3.12+. The documented build environment is Ubuntu 24.04 (eloqdata/ubuntu-dev:24.04). Compiler versions are not documented. |
| **Platforms** | Linux only. Release builds are Ubuntu 24.04 amd64 and arm64. io_uring is on by default, so Docker needs --privileged and memlock=-1. |
| **Thread safety** | This is a server, so the question is concurrent clients, not a thread-safe API. Clients are served across per-core shards under OCC or 2PL, at ReadCommitted or RepeatableRead isolation. An open data race on connection Pub/Sub state is tracked in #501. |
| **Drop-in for the baseline** | partial — existing Redis clients work over RESP2, but only about 178 commands are implemented (no Streams, HyperLogLog, Geo, RENAME, RESP3 or Functions). MULTI/EXEC error behaviour differs. RDB/AOF persistence is replaced by WAL plus checkpoints: DUMP/RESTORE and offline RDB/AOF exporters exist, but SAVE and BGSAVE do not. |

## Gotchas

- The shipped eloqkv.ini sets enable_wal = off, so a default install is not durable even though durability is the headline feature. The README's docker-compose example turns it on with -enable_wal=true.
- Lua has no time limit and there is no SCRIPT KILL, so one infinite EVAL pins a worker and holds its locks indefinitely (#507). Scripts are also re-run in full on OCC conflicts.
- The EVALSHA script cache is per process and not replicated, so EVALSHA must reach a node that has already seen the script body.
- Open replay and serialization bugs filed in June 2026: SET ... KEEPTTL loses the TTL on WAL replay (#504); SET over a non-string key stores an empty value on replay paths (#503); keys are serialized with a uint16 length although MAX_KEY_SIZE allows 32 MB (#498).

## Known shortcomings

- First-party benchmark in which Redis ran without io-threads; chart values are approximate. The tx_service core is BSL-licensed (usability mixed).
- LICENSE CHANGE: the required data_substrate core moved from GPL/AGPL to BSL 2.0 on 2026-01-27 (non-production, non-commercial use only until 2031), so a source build is not production-usable without a commercial agreement. Benchmark is a vendor 2024 v0.7.4 run (Wayback copy) read off charts; Redis single-threaded without io-threads; Dragonfly slightly faster.
- 178 commands at HEAD (no Streams/HLL/Geo/RENAME/COPY/RESP3/Functions/SCRIPT KILL). Default eloqkv.ini has enable_wal=off (not durable out of the box) and one replica (no auto-failover). Open bugs: MULTI aborts on first error (#502), no Lua timeout (#507), replay TTL/key-length bugs (#503/#504/#498), Jepsen stall (#188). Linux only; io_uring default needs --privileged in Docker.

## Caveats and trade-offs

This is a first-party benchmark by EloqData, the company behind EloqKV, not an independent third party. The live URL eloqdata.com/blog/2024/08/17/benchmark-single-node returns HTTP 404 and www.eloqdata.com did not connect as of 2026-09-26; the content comes from a Wayback snapshot dated 2026-06-16. Redis was started as 'redis-server --save "" --appendonly no' with no --io-threads, so single-threaded Redis was compared against multi-threaded servers on a 32-vCPU box. The page itself concedes that Redis would normally be scaled out as a cluster. No compiler or build flags are given for any server. The README cites 'up to 1.6M QPS on AWS c6g.8xlarge' while the blog used c7g.8xlarge. License: the eloqkv repo (the Redis API layer) is dual GPLv2 or AGPLv3 with no 'or later' in LICENSE or the source headers. Its required core submodule eloqdata/tx_service (Data Substrate) is under the Business Source License 2.0 (non-OSI; Change Date 2031-01-08 to Apache-2.0), so a full build is not all-OSI.

EloqKV splits compute/logging/storage into separate services (TxService + LogService + Storage Service) and enables io_uring by default, requiring --privileged and custom ulimits in Docker; adds full ACID distributed transactions (BEGIN/COMMIT/ROLLBACK, cross-node, no CROSSSLOT) that Redis lacks, at the cost of architectural complexity; for this specific cache-mode benchmark EloqKV had its own persistent storage and WAL turned off to make the comparison to Redis/DragonflyDB fair, so it does not exercise EloqKV's durability path.

## Maintenance

Actively developed (release 1.3.8 on 2026-09-09, nightly builds, last push 2026-09-17, 1.5k stars), but usability is mixed. The Redis layer is GPLv2 or AGPLv3, while the mandatory Data Substrate core is BSL 2.0 limited to non-production use until 2031. The benchmarked 0.7.4 is two years older than current builds.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** EloqData's own blog (2024-08-17, Wayback 2026-06-16) runs EloqKV 0.7.4 against Redis 7.2.5 and DragonflyDB 1.21.2 on c7g.8xlarge with full memtier commands. It says both 'significantly outperform Redis', with throughput and P999 shown only in chart images. The numbers are first-party, and no compiler, flags or CPU model beyond the instance type are given, so it is C.
- **Verifier notes:** Tier C and the claim hold. I corrected the license from '-or-later' to '-only' per the LICENSE and file headers. I changed usability to 'mixed' because the tx_service core submodule is BSL. I read approximate values off the three archived chart images. Metadata matches: 1,501 stars, last commit 2026-09-17, not a fork, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <http://web.archive.org/web/20260616115015/https://eloqdata.com/blog/2024/08/17/benchmark-single-node>
  - <https://eloqdata.com/blog/2024/08/17/benchmark-single-node>
  - <https://www.eloqdata.com/blog/2024/08/17/benchmark-single-node>
  - <http://web.archive.org/web/20260616115015im_/https://eloqdata.com/assets/images/eloqkv_dragon_redis_set_new-a76936c4ee2d026bac83f207a0f44ccb.png>
  - <http://web.archive.org/web/20260616115015im_/https://eloqdata.com/assets/images/eloqkv_dragon_redis_get_new-4faa58954a32cea37b13093d6165ba40.png>
  - <http://web.archive.org/web/20260616115015im_/https://eloqdata.com/assets/images/eloqkv_dragon_redis_setget_new-a74e59e6ae22f76c8639804b134b21cf.png>
  - <https://github.com/eloqdata/eloqkv>
  - <https://github.com/eloqdata/tx_service>
- **Sources the enricher read:**
  - <https://github.com/eloqdata/eloqkv>
  - <https://github.com/eloqdata/eloqkv/blob/main/README.md>
  - <https://github.com/eloqdata/eloqkv/blob/main/docs/01-architecture-overview.md>
  - <https://github.com/eloqdata/eloqkv/blob/main/docs/02-command-processing.md>
  - <https://github.com/eloqdata/eloqkv/blob/main/docs/03-data-model.md>
  - <https://github.com/eloqdata/eloqkv/blob/main/docs/04-scripting-pubsub-blocking.md>
  - <https://github.com/eloqdata/eloqkv/blob/main/docs/07-persistence-and-tools.md>
  - <https://github.com/eloqdata/eloqkv/blob/main/.gitmodules>
  - <https://github.com/eloqdata/eloqkv/blob/main/CMakeLists.txt>
  - <https://github.com/eloqdata/eloqkv/blob/main/LICENSE>
  - <https://github.com/eloqdata/eloqkv/blob/main/eloqkv.ini>
  - <https://github.com/eloqdata/eloqkv/blob/main/src/redis_service.cpp>
  - <https://github.com/eloqdata/eloqkv/blob/main/.github/workflows/release.yml>
  - <https://github.com/eloqdata/eloqkv/releases>
  - <https://github.com/eloqdata/eloqkv/issues>
  - <https://github.com/eloqdata/eloqkv/issues/188>
  - <https://github.com/eloqdata/eloqkv/issues/405>
  - <https://github.com/eloqdata/eloqkv/issues/406>
  - <https://github.com/eloqdata/eloqkv/issues/502>
  - <https://github.com/eloqdata/eloqkv/issues/507>
  - <https://github.com/eloqdata/tx_service>
  - <https://github.com/eloqdata/tx_service/blob/main/README.md>
  - <https://github.com/eloqdata/tx_service/blob/main/LICENSE>
  - <https://github.com/eloqdata/tx_service/commit/2154e111>
  - <https://github.com/eloqdata/tx_service/blob/main/docs/02-threading-model.md>
  - <https://github.com/eloqdata/tx_service/blob/main/docs/03-concurrency-control.md>
  - <http://web.archive.org/web/20260616115015/https://eloqdata.com/blog/2024/08/17/benchmark-single-node>
  - <http://archive.org/wayback/available?url=eloqdata.com/eloqkv/kvstore_compatibility>
  - <http://web.archive.org/web/20260521172529/https://www.eloqdata.com/eloqkv/kvstore_compatibility>
  - <https://hn.algolia.com/api/v1/search?query=EloqKV>
  - <https://hn.algolia.com/api/v1/items/44937978>
  - <https://hn.algolia.com/api/v1/items/41590905>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/eloqdata/eloqkv`) · [data/wave6/enrich/raw/github_com_eloqdata_eloqkv.json](../../../data/wave6/enrich/raw/github_com_eloqdata_eloqkv.json) (enrichment confidence 0.55)

</details>
