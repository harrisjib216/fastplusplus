# Garnet

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C#` · `MIT` · 🟢 active

> Multi-threaded Redis-protocol (RESP) cache-store in C# from Microsoft Research; up to \~100x Valkey/Redis throughput on many-core servers.

| | |
|---|---|
| **Beats** | Redis |
| **Claimed result** | Table 1 (normalized to Redis; the paper says Redis performs like Valkey and leaves it out of most runs, so the measured comparisons are against Valkey v8.1): node throughput 108x, latency at batch size 16 0.25x (4x lower), checkpoint speed 257x (Valkey 273.1s vs Garnet 1.06s), scale-out/migration speed 94x vs Valkey; memtier (1:9 SET:GET, 256M keys, 6400 clients): at least 20x higher throughput and 3x lower P99 latency than standalone Valkey, up to 40x/6x higher throughput than KeyDB/Dragonfly |
| **Workload** | RESP-translated YCSB-A workload, 256M 8-byte keys, string values 8B-several KB, using memtier_benchmark and Garnet's own Resp.bench load generator against Garnet/Valkey/KeyDB/Dragonfly on Azure Standard F72s_v2 VMs (72 vCPUs, 144GB RAM), Ubuntu 24.04, accelerated TCP networking |
| **Metric** | throughput |
| **Hardware** | Azure Standard F72s_v2 VMs, 72 vCPUs, 144GB RAM, Ubuntu 24.04 with accelerated TCP networking |
| **Adoption** | 12k stars; the paper says Garnet is 'already widely deployed in large-scale scenarios across Microsoft' |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/microsoft/garnet) · [benchmark](https://badrish.net/papers/garnet-vldb2026.pdf) |

## Verdict

In the authors' own PVLDB 2026 paper, run on Azure F72s_v2 VMs (72 vCPUs, 144 GB, Ubuntu 24.04, accelerated TCP; CPU model and .NET version not stated), Garnet's GET throughput at 128 client sessions was 108x Valkey 8.1, which stood in for Redis. A memtier run (1:9 SET:GET, 256M 8-byte keys, 6400 clients) showed at least 20x the throughput and 3x lower P99 than standalone Valkey; checkpointing 256M keys took 1.06 s against 273.1 s, and migrating all slots between two nodes was 94x faster. Most figures come from Garnet's own Resp.bench tool, and none of the sources read here show an independent reproduction.

## Use it when

- Tens to hundreds of concurrent client connections doing small GET/SET, ideally pipelined or batched, on a many-core box where single-threaded Redis/Valkey saturates one core (the paper measures 108x Valkey GET throughput at 128 sessions on a 72-vCPU VM).
- Datasets larger than RAM that still need a RESP interface: --storage-tier keeps hot records in memory and spills older log pages to SSD or Azure storage.
- Frequent snapshots or warm restarts where Redis fork-based SAVE doubles memory or stalls: the paper checkpoints 256M keys in 1.06 s against Valkey's 273.1 s.
- .NET teams that want to embed the cache in-process (Microsoft.Garnet NuGet) or write atomic server-side logic as C# stored procedures instead of Lua.
- Sharded clusters that rebalance often: slot migration is server-to-server and measured 94x faster than Valkey's client-driven migration (paper).

## Skip it when

- Apps that use Redis Streams (every X\* command is unsupported), Redis Functions (FCALL/FUNCTION), client-side caching (CLIENT TRACKING), SORT, WAIT/WAITAOF, CLIENT PAUSE or loadable Redis modules.
- Cluster deployments that expect built-in failover: cluster mode is passive, with no leader election, so you must run your own control plane (for example a Kubernetes operator) to detect failures and promote replicas.
- Tiered storage combined with multiple logical databases (SELECT n): open bug #2152 (Sept 2026) says all databases share one log file, so a read on db 0 can return db 1's value. Open #2163 is an IndexOutOfRangeException on ZADD over an expired record read back from disk. The disk-tier paths are less mature than the in-memory path.
- Teams that rely on exact Redis semantics or eviction policies: MSET is not atomic, eviction follows log order (FIFO for read-only records unless --copy-reads-to-tail) rather than Redis maxmemory-policy choices, and with the storage tier on, reads may run out of order relative to earlier writes in the same pipeline.
- Environments that cannot run or tune a managed runtime: Garnet needs the .NET 8/10 runtime with server GC, and large indexes and logs live on the pinned managed heap by default (the native allocator is opt-in and then needs GC hard-limit tuning).

## How it is fast

Sessions are shared-nothing and the store is shared-everything. Each connection's packet is TLS-decrypted, parsed and executed on the .NET socket I/O completion thread (SocketAsyncEventArgs), with no hand-off to per-core shard workers, so every core can serve every key and a pipelined batch runs without thread switches. Storage is Tsavorite, from the FASTER lineage: a latch-free hash index of 64-byte cache-line buckets (7 tagged entries plus an overflow/lock word) over a 'hybrid log' of records. Records in the mutable in-memory region are updated in place, new records are linked with CAS, and epoch protection (epoch-protected state machines) handles index resize, page flush/eviction, checkpoints and slot migration without blocking. The parser matches whole RESP headers for hot commands (GET, SET, DEL, INCR...) with Vector128 SIMD compares and falls back to a CRC32-hashed command table. Checkpoints use CPR-style version shifts instead of fork() and write with io_uring.

## Compared with alternatives

Pick Garnet over KeyDB when you want many-core throughput, larger-than-memory tiering or fast checkpoints. In the Garnet paper, KeyDB (a multi-threaded network layer over a lock-guarded store) scored 0.6x Valkey throughput and took 481.7 s to checkpoint, against Garnet's 108x and 1.06 s. KeyDB's own headline is a TLS-specific 7x over Redis. Pelikan/Segcache is a memcached-protocol TTL cache and Caffeine is an in-process JVM cache, so Garnet is the one to pick when you need Redis data types, persistence and clustering over the network.

## Integration

| | |
|---|---|
| **Form** | standalone server (dotnet run, the garnet-server dotnet tool, or the repo's Dockerfiles) or a NuGet library (Microsoft.Garnet) hosted in your own .NET process |
| **Dependencies** | .NET runtime 8 or 10; NuGet packages including CommandLineParser, Microsoft.Extensions.Logging, Azure.Storage.Blobs, Azure.Identity, Microsoft.IdentityModel/System.IdentityModel.Tokens.Jwt, KeraLua (Lua scripting) and diskann-garnet (vector sets) |
| **Minimum toolchain** | .NET 10 SDK to build (global.json pins 10.0.400, roll-forward to latest major); assemblies target net8.0 and net10.0; C# latest with unsafe code |
| **Platforms** | Linux and Windows are both documented as first-class; the paper also lists x64/ARM and macOS. Dockerfiles exist for Alpine, Ubuntu, Azure Linux, chiseled and Nano Server. The io_uring checkpoint path and huge-page hints are Linux-only. |
| **Thread safety** | Multi-threaded server: any number of concurrent client sessions, each processed in strict FIFO order. Single-key operations are atomic under bucket locks. MULTI/EXEC, Lua and stored procedures use two-phase locking on hash buckets, with WATCH as optimistic checks. MSET is not atomic. |
| **Drop-in for the baseline** | partial — wire-compatible with Redis clients, but about 100 commands are missing (Streams, Functions, client tracking and others), Redis modules are unsupported, MSET is non-atomic, configuration uses different flags (maxmemory maps to --memory/LogMemorySize), and cluster mode has no automatic failover |

## Gotchas

- Memory is set with two knobs: the hash index (-i, rule of thumb 16 bytes per expected key; it never shrinks, and auto-grow only runs if --index-resize-freq is set) and the log (-m). The storage tier is off by default, so records pushed out of memory are simply dropped.
- Durability defaults are weak: with AOF on, writes are acknowledged before the log commits unless --aof-commit-wait is set. Checkpoint and AOF formats are compatible only from 2.1.0 onward within 2.x, and an older binary cannot read a newer checkpoint.
- Published headline numbers ran Garnet with --no-obj --no-pubsub (the object store disabled) and large batches of up to 4096 requests (website Resp.bench setup). The paper switched from memtier to its own Resp.bench because memtier became client-bound, so re-measure at your own batch size and command mix.
- The lowest-latency results in the paper (4-5x lower P99 PING) use an eRPC/DPDK kernel-bypass path that the paper calls a prototype, not part of open-source Garnet.

## Known shortcomings

- Evidence is the authors' own paper (all Microsoft Research): Redis mostly not run (Valkey 8.1 stands in), most figures from Garnet's own Resp.bench, website numbers with --no-obj --no-pubsub and batches up to 4096; no independent reproduction. Best-latency numbers use an eRPC/DPDK kernel-bypass prototype not in the OSS release. Not a full drop-in: \~100 commands unsupported (Streams, FCALL/FUNCTION, CLIENT TRACKING, SORT, WAIT), no modules, MSET not atomic, passive cluster without failover. Open disk-tier bugs: cross-db corruption with multi-db + storage tier (#2152), crash on ZADD over an expired record read from disk (#2163). Eviction is log order, not LRU; storage tier off by default (overflow dropped); AOF acks before commit unless --aof-commit-wait. C#/.NET, not C++.

## Caveats and trade-offs

Evaluation run and published by Garnet's own authors (all seven are Microsoft Research); the paper is peer-reviewed (PVLDB 19(2):224-237) but is not independent. Redis itself was mostly not run: the paper says open-source Redis performs like Valkey and uses Valkey v8.1 (plus KeyDB v6.3.4 and Dragonfly v1.29.0) as the measured baselines, so the 'normalized to Redis' ratios stand in for Redis. The CPU model is not given (only the Azure F72s_v2 SKU), and the .NET runtime version and build flags are not stated. memtier_benchmark became client-bottlenecked, so most headline figures come from Garnet's own Resp.bench tool. Language is C#, not C++.

Runs on the .NET runtime (GC, JIT) rather than being a native binary; kernel-bypass networking (eRPC/DPDK path) used for the best latency numbers is a prototype not shipped in the open-source build; complex RESP data types (SortedSet, HyperLogLog) add overhead

## Maintenance

Very active: v2.1.8 shipped 2026-09-16 with commits landing daily. MIT-licensed, about 12k stars, used widely inside Microsoft and offered as the managed Azure Cosmos DB Garnet Cache. Usable today via the dotnet tool, Docker or NuGet, but the storage-tier and multi-database paths still have open correctness bugs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** Peer-reviewed PVLDB 19(2):224-237 paper; Table 1 (normalized to Redis) and Sec. 8 give 108x throughput, 0.25x latency, 257x checkpoint and 94x scale-out, and the load generator is public (benchmark/Resp.benchmark in the repo). It is not A because the paper names only the Azure VM SKU (F72s_v2), with no CPU model and no .NET/compiler version or flags.
- **Verifier notes:** The record's caveat claiming Facebook/Meta-adjacent academic co-authors was wrong: all authors are Microsoft Research, and I corrected it. The measured baseline is Valkey v8.1 (a Redis fork) acting as the Redis proxy. The C++-only search filter returned a C# project.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://badrish.net/papers/garnet-vldb2026.pdf>
  - <https://github.com/microsoft/garnet>
- **Sources the enricher read:**
  - <https://github.com/microsoft/garnet>
  - <https://badrish.net/papers/garnet-vldb2026.pdf>
  - <https://github.com/microsoft/garnet/blob/main/global.json>
  - <https://github.com/microsoft/garnet/blob/main/Directory.Build.props>
  - <https://github.com/microsoft/garnet/blob/main/main/GarnetServer/GarnetServer.csproj>
  - <https://github.com/microsoft/garnet/blob/main/libs/host/Garnet.host.csproj>
  - <https://github.com/microsoft/garnet/blob/main/libs/server/Resp/Parser/RespCommandSimdPatterns.cs>
  - <https://github.com/microsoft/garnet/blob/main/libs/server/Resp/Parser/RespCommandHashLookup.cs>
  - <https://github.com/microsoft/garnet/blob/main/libs/server/Resp/Parser/RespCommand.cs>
  - <https://github.com/microsoft/garnet/blob/main/libs/common/Networking/TcpNetworkHandlerBase.cs>
  - <https://github.com/microsoft/garnet/blob/main/website/docs/getting-started/build.md>
  - <https://github.com/microsoft/garnet/blob/main/website/docs/getting-started/memory.md>
  - <https://github.com/microsoft/garnet/blob/main/website/docs/getting-started/configuration.md>
  - <https://github.com/microsoft/garnet/blob/main/website/docs/getting-started/security.md>
  - <https://github.com/microsoft/garnet/blob/main/website/docs/welcome/compatibility.md>
  - <https://github.com/microsoft/garnet/blob/main/website/docs/welcome/faq.md>
  - <https://github.com/microsoft/garnet/blob/main/website/docs/commands/api-compatibility.md>
  - <https://github.com/microsoft/garnet/blob/main/website/docs/cluster/overview.md>
  - <https://github.com/microsoft/garnet/blob/main/website/docs/benchmarking/overview.md>
  - <https://github.com/microsoft/garnet/blob/main/website/docs/benchmarking/results-resp-bench.md>
  - <https://github.com/microsoft/garnet/releases>
  - <https://github.com/microsoft/garnet/issues/158>
  - <https://github.com/microsoft/garnet/issues/2152>
  - <https://github.com/microsoft/garnet/issues?q=evict>
  - <https://github.com/microsoft/garnet/issues?q=data+loss>
  - <https://github.com/microsoft/garnet/issues?q=crash>
  - <https://github.com/microsoft/garnet/security/advisories>
  - <https://hn.algolia.com/api/v1/search?query=microsoft%20garnet&tags=story>
  - <https://news.ycombinator.com/item?id=39752504>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/microsoft/garnet`) · [data/wave6/enrich/raw/github_com_microsoft_garnet.json](../../../data/wave6/enrich/raw/github_com_microsoft_garnet.json) (enrichment confidence 0.85)

</details>
