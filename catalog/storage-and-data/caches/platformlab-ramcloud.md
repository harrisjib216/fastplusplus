# RAMCloud

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `ISC` · 🔴 abandoned

> Distributed, durable in-DRAM key-value store with kernel-bypass RPC; beats Redis 2.6 on read-heavy YCSB, not on writes.

| | |
|---|---|
| **Beats** | Redis |
| **Claimed result** | FAST '14 paper, Figure 12: RAMCloud outperforms Redis on the read-heavy YCSB workloads B, C and D with both kernel sockets and Verbs, and the Verbs transport 'more than doubles read throughput' compared with RAMCloud on kernel sockets. On the write-heavy workloads A and F, RAMCloud with kernel sockets trails Redis, and with Verbs it matches Redis write throughput at 75% utilisation but is 25% slower than Redis on workload A at 90%. Exact per-bar values appear only in the figure. Separately, the project wiki claims reads in as little as 5us and writes under 15us, calling RAMCloud '10-1000x faster than other available alternatives', and contrasts it with memcached only in words. |
| **Workload** | YCSB workloads A, B, C, D, F (E omitted, no scans), 1 KB objects, 100M operations per client, 24 YCSB clients on 24 nodes against 12 storage-server nodes, triple replication; Redis 2.6.14 and HyperDex 1.0rc4 used kernel sockets over Infiniband, and RAMCloud ran both with kernel sockets and with its kernel-bypass Infiniband Verbs transport at 75% and 90% memory utilisation |
| **Metric** | latency |
| **Hardware** | 80-node cluster: Xeon X3470 (4x2.93 GHz, 3.6 GHz Turbo), 24 GB DDR3-800, 2x Crucial M4 128 GB SSDs, Mellanox ConnectX-2 Infiniband HCA, Mellanox SX6036 4X FDR switch, Linux 2.6.32 |
| **Adoption** | 503 stars |
| **Last commit** | 2019-10-16 |
| **Links** | [repository](https://github.com/PlatformLab/RAMCloud) · [benchmark](https://www.usenix.org/system/files/conference/fast14/fast14-paper_rumble.pdf) |

## Verdict

FAST '14 Figure 12 measured aggregate YCSB throughput from 24 client nodes against 12 storage nodes: 1 KB objects, triple replication, on an 80-node cluster (Xeon X3470, ConnectX-2 InfiniBand, Linux 2.6.32). The baselines were Redis 2.6.14 (AOF with 1 s fsync, asynchronous replicas) and HyperDex 1.0rc4, both over kernel sockets. RAMCloud beat Redis on the read-heavy workloads B, C and D, and its Verbs transport more than doubled read throughput versus its own kernel-socket runs, but it lost or tied on the write-heavy workloads A and F. Results are given only as bars, no compiler or flags are stated, and the caption gives both 100M and 10M for the key count (the TOCS rerun says 10M operations on 10M keys).

## Use it when

- Online requests that make long chains of dependent small reads (graph walks, multi-step lookups), where the TOCS paper's 4.7 us median read of a 100 B object over InfiniBand changes what is feasible
- Small objects (about 100 B to 1 KB; it is tuned for a few hundred bytes or less) that must be durable and strongly consistent on write, replacing a memcached-plus-database cache-aside setup and its invalidation logic
- Datacenters with InfiniBand (Mellanox ConnectX-2/3) or other kernel-bypass NICs and a spare core per server for polling
- Datasets larger than one machine's DRAM that can be sharded into tables across many servers; batched multiRead reached about 6M objects/s from a single server in TOCS
- Research or teaching on log-structured memory, fast crash recovery or microsecond RPC, where the code and papers are the reference implementation

## Skip it when

- Write-heavy workloads: on FAST '14 YCSB A and F, RAMCloud over kernel sockets trailed Redis, and with Verbs it only matched Redis at 75% memory use and was 25% slower on workload A at 90%
- Commodity Ethernet with kernel TCP only: TOCS says the advantage 'drops significantly' on 1 Gb/s kernel TCP, and TcpTransport adds about 50-100 us over InfRcTransport
- Caching use cases that need eviction or TTLs, range scans, or Redis data types: RAMCloud is a durable store with no eviction and no scans (YCSB E was omitted for this reason)
- Anything that needs vendor support or a modern toolchain: support ended 2019-10-07, the wiki links a known build break on newer Ubuntu and OpenSuse (RAM-553), the Python bindings are Python 2 only, and there is no georeplication
- Small or single-box deployments: it needs a coordinator, ZooKeeper or LogCabin, and storage servers with backup devices of about 2 x DRAM x replication factor, and it was only ever tested on an 80-node cluster

## How it is fast

The main latency technique is kernel bypass plus polling. InfRcTransport drives Mellanox NICs from user space through InfiniBand Verbs reliably-connected queue pairs, and both clients and servers busy-poll instead of taking interrupts or waking threads (the TOCS paper puts a condition-variable wakeup at about 2 us). On each server, one dispatch thread polls the NIC and hands each RPC to a worker thread. Objects live in log-structured memory: 8 MB segments built from 64 KB seglets, indexed by a hash table with cache-line buckets and one pointer per object. Two-level cleaning (in-memory segment compaction plus an LFS-style cost-benefit combined cleaner) runs in parallel threads, which keeps memory use at 80-90%. A write is acknowledged once it reaches the backups' in-memory buffers, and the backups write whole 8 MB segments sequentially later.

## Compared with alternatives

Garnet, Dragonfly and KeyDB are catalogued as Redis replacements and measured on ordinary server hardware, and MICA, MemC3 and Pelikan are single-node caches with eviction. Pick RAMCloud only when you need writes synchronously replicated before they are acknowledged, data sharded across many nodes' DRAM with 1-2 s crash recovery, and an InfiniBand or kernel-bypass fabric to realise the latency.

## Integration

| | |
|---|---|
| **Form** | shared lib (libramcloud client library plus separate coordinator and storage-server daemons, built from source with GNU make) |
| **Dependencies** | Boost (program_options, filesystem, system), Google protobuf, pcrecpp, OpenSSL (libssl/libcrypto), ZooKeeper C client (on by default; LogCabin is an optional submodule), gtest submodule; optional libibverbs (auto-detected), DPDK, SolarFlare OpenOnload. At runtime it also needs a ZooKeeper or LogCabin cluster. |
| **Minimum toolchain** | C++11 (GNUmakefile defaults to -std=c++11); the wiki lists GNU g++ 4.9.x, and the last CI config used g++ 5.4 on Ubuntu 16.04. Newer compilers are not documented. |
| **Platforms** | Linux only; x86-64 with SSE4.2 (the build defaults to -msse4.2 -march=native). Best on Mellanox InfiniBand with Verbs; DPDK, UDP and kernel TCP transports also exist. |
| **Thread safety** | The client RamCloud object is not thread-safe; use one per thread. The server uses one polling dispatch thread plus worker threads, and its internal HashTable is documented as not thread-safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- The default build is a debug/test build (DEBUG=yes: -DTESTING=1, -fno-builtin, no -O3), and the wiki warns this 'slows the system down considerably'. Build with DEBUG=no before measuring anything.
- A coordinator started without -x (external storage) loses all cluster data if it crashes. The backup -f target is treated as a raw block device and overwritten, and undersized backup space (below about 2 x DRAM x replication factor) can eventually stop writes from being served.
- Write durability assumes backups can flush their DRAM buffers after a power failure is detected (or that NVDIMMs are fitted); without that, a datacenter power loss can drop writes that were already acknowledged.
- Servers busy-poll and use a full core even when idle. TOCS reports 30-100 us tail spikes (about 1 in 1,000 reads and 1 in 100 writes) when Linux deschedules the server threads, and the single dispatch thread caps small-read throughput at about 950K reads/s per server.

## Known shortcomings

- The wiki names memcached only in prose; the measurable evidence is the FAST'14 YCSB comparison vs Redis 2.6.14 (Fig. 12), where RAMCloud wins read-heavy B/C/D but trails or ties write-heavy A/F. Needs low-latency NICs for its headline latency; abandoned; GitHub shows no license although the code is ISC.
- On write-heavy YCSB A/F kernel sockets lose to Redis and Verbs only ties at 75% memory (25% slower on A at 90%). Over kernel TCP the latency edge mostly disappears (+50-100 us per TOCS); needs InfiniBand/kernel bypass and a full cluster (coordinator, ZooKeeper/LogCabin, backups). No scans, eviction/TTL or Redis protocol.
- Support ended 2019-10-07; built for g++ 4.9-5.4 and breaks on newer distros (RAM-553); Python bindings are Python 2 only. The default build is debug (no -O3); idle servers burn a core polling; durability assumes backups flush buffers after a power-fail warning.

## Caveats and trade-offs

The win over Redis holds only for the read-heavy workloads; RAMCloud trails or ties Redis on write-heavy YCSB A/F. The comparison is not like-for-like on durability: RAMCloud waits for synchronous triple replication, while Redis used append-only logging with a 1s fsync and asynchronous replicas. The best RAMCloud numbers need Infiniband kernel bypass (Verbs). The baseline is Redis 2.6.14 from 2013, and the paper is by the RAMCloud authors. Exact values are only in a bar chart, and no compiler or flags are stated. The wiki's 5us/15us and '10-1000x' figures are marketing with no methodology, and the memcached contrast is qualitative only (the TOCS 2015 paper cites \~300us memcached latency at Facebook from a personal communication, not from a benchmark). The project is marked 'No Longer Maintained', with its last commit in 2019. GitHub reports the license as NOASSERTION, but the LICENSE file is plain ISC.

Requires keeping the whole dataset in DRAM across a cluster (disk/flash used only for backup logging), unlike Memcached's standalone cache-aside model; needs a full cluster (coordinator + masters + backups) rather than a single process; lowest latencies assume InfiniBand/kernel-bypass transport

## Maintenance

Abandoned: the repo is marked 'No Longer Maintained', the wiki says support ended 2019-10-07 and the last commit was 2019-10-16. It is ISC-licensed but is about 100K lines of C++11 with Boost, protobuf and ZooKeeper dependencies, so it is a system to operate rather than something to vendor, and the last CI-tested toolchain is g++ 5.4 on Ubuntu 16.04.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C to B on stronger evidence: the peer-reviewed FAST '14 paper (Rumble, Kejriwal, Ousterhout, 'Log-structured Memory for DRAM-based Storage', Section 8.7, Figure 12) measures RAMCloud against Redis 2.6.14 and HyperDex on YCSB and shows RAMCloud ahead on the read-heavy workloads. It is not A because the paper gives no compiler or flags and no YCSB driver path, and the original wiki page only contrasts with memcached in words (5us/15us, '10-1000x faster than other available alternatives'), which alone would be C.
- **Verifier notes:** The wiki page does contain the quoted 5us/15us and '10-1000x' text, but it names memcached only in words, so I switched the record's evidence to the FAST '14 YCSB comparison against Redis, which is peer-reviewed. The record's metric should become 'throughput' because the paper compares throughput and metric is not a correctable field. If the orchestrator wants memcached kept as the baseline, the tier falls back to C. Metadata checked: ISC LICENSE file, not a fork, not archived, 503 stars, last commit 2019-10-16, abandoned.
- **Fields the verifier corrected:** `baseline`, `benchmark_url`, `workload`, `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/PlatformLab/RAMCloud>
  - <https://raw.githubusercontent.com/PlatformLab/RAMCloud/master/LICENSE>
  - <https://ramcloud.atlassian.net/wiki/spaces/RAM/overview>
  - <https://www.usenix.org/system/files/conference/fast14/fast14-paper_rumble.pdf>
  - <https://web.stanford.edu/~ouster/cgi-bin/papers/ramcloud-tocs.pdf>
- **Sources the enricher read:**
  - <https://github.com/PlatformLab/RAMCloud>
  - <https://github.com/PlatformLab/RAMCloud/blob/master/README.md>
  - <https://github.com/PlatformLab/RAMCloud/blob/master/GNUmakefile>
  - <https://github.com/PlatformLab/RAMCloud/blob/master/.travis.yml>
  - <https://github.com/PlatformLab/RAMCloud/blob/master/.gitmodules>
  - <https://github.com/PlatformLab/RAMCloud/blob/master/LICENSE>
  - <https://github.com/PlatformLab/RAMCloud/blob/master/misc/libmemcached_with_RAMCloud.txt>
  - <https://github.com/PlatformLab/RAMCloud/blob/master/src/RamCloud.h>
  - <https://github.com/PlatformLab/RAMCloud/blob/master/src/HashTable.h>
  - <https://github.com/PlatformLab/RAMCloud/blob/master/src/Crc32C.h>
  - <https://github.com/PlatformLab/RAMCloud/issues>
  - <https://github.com/PlatformLab/RAMCloud/pulls>
  - <https://github.com/PlatformLab/RAMCloud/commits/master>
  - <https://github.com/PlatformLab/RAMCloud/issues/19>
  - <https://github.com/PlatformLab/RAMCloud/issues/24>
  - <https://github.com/PlatformLab/RAMCloud/issues/26>
  - <https://github.com/PlatformLab/RAMCloud/issues/27>
  - <https://github.com/PlatformLab/RAMCloud/issues/28>
  - <https://github.com/PlatformLab/RAMCloud/issues/29>
  - <https://github.com/PlatformLab/RAMCloud/issues/36>
  - <https://www.usenix.org/system/files/conference/fast14/fast14-paper_rumble.pdf>
  - <https://web.stanford.edu/~ouster/cgi-bin/papers/ramcloud-tocs.pdf>
  - <https://ramcloud.atlassian.net/wiki/spaces/RAM/pages/6848532/Setting+Up+a+RAMCloud+Cluster>
  - <https://ramcloud.atlassian.net/wiki/rest/api/content/6848532?expand=body.storage>
  - <https://ramcloud.atlassian.net/wiki/rest/api/content/6848533?expand=body.storage>
  - <https://ramcloud.atlassian.net/wiki/rest/api/content/6848537?expand=body.storage>
  - <https://ramcloud.atlassian.net/wiki/rest/api/content/6848614?expand=body.storage>
  - <https://ramcloud.atlassian.net/wiki/rest/api/content?spaceKey=RAM&limit=200>
  - <https://hn.algolia.com/api/v1/search?query=RAMCloud&tags=story&hitsPerPage=10>
  - <https://hn.algolia.com/api/v1/items/18431140>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/platformlab/ramcloud`) · [data/wave6/enrich/raw/github_com_platformlab_ramcloud.json](../../../data/wave6/enrich/raw/github_com_platformlab_ramcloud.json) (enrichment confidence 0.8)

</details>
