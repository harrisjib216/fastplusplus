# MICA

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Caches](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `Apache-2.0 (license text embedded in README; no separate LICENSE file in the repo)` · 🔴 abandoned

> Research in-memory key-value cache/store over DPDK UDP; 65-77 Mops on tiny items per 16-core server, far above Memcached.

| | |
|---|---|
| **Beats** | memcached |
| **Claimed result** | Tiny items (8B/8B), Fig. 10: MICA reaches 75.5-76.9 Mops on uniform and 65.6-70.5 Mops on skewed workloads. The next-best system (Masstree) tops out at 16.5 Mops; Memcached, MemC3 and RAMCloud stay at or below 6.1 Mops. Paper headline: 4-13.5x faster than the next fastest system, and 10.8x on skewed 50% GET. Against the custom Memcached (ported to MICA's kernel-bypass stack), which gets 0.7-1.3 Mops, MICA is roughly 50-110x faster on tiny items (derived from page data). Latency (Fig. 13, uniform 50% GET, tiny items) vs original kernel-stack Memcached: at a similar \~40 us latency MICA serves 69 Mops, 'more than two orders of magnitude faster than Memcached'. Original Memcached's latency is almost flat, while MICA's varies between 24 and 52 us depending on load. |
| **Workload** | Network GET/PUT benchmark over UDP with MICA's DPDK kernel-bypass stack and no client-side batching. Item sizes: tiny (8B/8B), small (16B/64B) and large (128B/1024B). Key popularity is uniform or Zipf(0.99), at 50% and 95% GET. The server has 16 cores running 16 partitions (EREW). Compared against custom versions of Memcached (87e2f36), MemC3, Masstree and RAMCloud, all modified to use MICA's network stack, each run at its best core count. The latency test uses original Memcached with the kernel network stack. |
| **Metric** | throughput |
| **Hardware** | Server: dual 8-core Intel Xeon E5-2680 @2.70GHz, 64GiB RAM (32GiB/NUMA node), 20MiB L3/CPU, eight 10Gb Ethernet ports (four Intel X520-T2 dual-port NICs); Clients: two machines with dual 6-core Intel Xeon L5640 @2.27GHz and Intel X520-T2 NICs |
| **Compiler and flags** | Not stated in the paper. The repo README requires gcc &gt;= 4.6.0, and src/CMakeLists.txt sets -O9 -msse4.2 -march=corei7 -g. |
| **Adoption** | 215 stars |
| **Last commit** | 2016-01-18 |
| **Links** | [repository](https://github.com/efficient/mica) · [benchmark](https://www.usenix.org/system/files/conference/nsdi14/nsdi14-paper-lim.pdf) |

## Verdict

NSDI'14 Fig. 10 tested a dual 8-core Xeon E5-2680 server with eight 10GbE ports, running DPDK 1.4.1 with 16 EREW partitions, 8B/8B items and no client batching. MICA's cache mode served 75.5-76.9 Mops on uniform keys and 65.6-70.5 Mops on Zipf-0.99. Memcached rev 87e2f36, ported to MICA's DPDK stack and at its best with 2 cores, reached 0.7-1.3 Mops, and the next-best system, Masstree, reached 16.5 Mops. The paper does not give the compiler version; the repo's flags are -O9 -msse4.2 -march=corei7. MICA was network-bound (54.9-66.4 Gbps used), so the gap narrows for 16B/64B and 128B/1024B items (8.6-14.6 Mops on the large set). The latency comparison (MICA at 24-52 us) was against stock Memcached on the kernel network stack.

## Use it when

- You control both clients and servers and can give a cache tier dedicated Intel 10GbE (ixgbe, Flow Director) NICs and hugepages for kernel bypass.
- Many tiny or small items (8-64 B values, keys of 255 B or less) under write-heavy or Zipf-skewed traffic where lock-based stores stop scaling. The paper shows MICA holding 65.6-76.9 Mops, losing at most 14% to skew.
- Cache semantics are acceptable: silent eviction on a full hash bucket or on log wrap-around is fine for your data.
- You need high throughput with a single round trip per request: the paper measured 24-52 us average end-to-end latency while serving tens of Mops.
- You want a compact reference implementation (about 12K lines of C) of EREW partitioning, client-steered NIC request direction, and a circular log with a lossy set-associative index.

## Skip it when

- You need a memcached drop-in. It has no memcached text or binary protocol, no TCP, and no client library beyond the benchmark clients, so applications must adopt its UDP format and handle loss and retries themselves.
- You need values larger than one packet, multi-get, CAS, range queries, persistence or replication. The paper lists durability and multi-packet items as non-goals.
- Cloud VMs, non-Intel NICs or current DPDK. The build links only DPDK's ixgbe PMD and relies on Flow Director and a 2014-era DPDK make-based setup (&gt;= 1.5.0). gen_confs.py hard-codes the paper's testbed (8 server ports, a 16-core server, 12-core clients, 10.0.0.x addresses).
- Anything that needs upstream support. master was frozen on 2014-03-03, the isca2015 branch on 2016-01-18, no issue or PR has ever been filed, and Apache-2.0 appears only as README text with no LICENSE file.
- Store mode where writes must never fail for lack of space. Spare buckets are fixed at 10% of the main buckets, and once they run out a SET is rejected with an out-of-space error.

## How it is fast

It partitions data by keyhash in EREW mode, so each core owns its partitions outright with no locks or cache-line sharing. Clients help the NIC route requests: the Intel Flow Director perfect-match filter sends each packet to the owning core's RX queue based on its UDP port, over DPDK with burst I/O (up to 32 packets) and zero-copy replies built inside the request buffer. In cache mode, items live in a per-partition circular log on hugepages (FIFO, or approximate LRU by re-appending, with no garbage collection). That log is indexed by a lossy set-associative hash index: 15 tag+offset slots per 128-byte bucket, where a collision evicts the oldest entry instead of being resolved, and 48-bit offsets let dangling pointers be detected cheaply. Multi-stage software prefetching overlaps the packet, bucket and log-entry cache misses across a burst, and store mode swaps in segregated fits plus bulk chaining (spare buckets sized at 10% of the main buckets).

## Compared with alternatives

Choose MICA over MemC3 (same CMU group, memcached-compatible) or Pelikan/Segcache (a production memcached replacement) only when you own the NIC, the client library and the hardware, and peak tiny-item ops per server is the goal. For anything that has to work with standard clients or on commodity cloud hosts, Pelikan, Dragonfly or Pogocache are the practical choices.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Intel DPDK &gt;= 1.5.0 (paper used 1.4.1; rte_eal, rte_mempool, rte_ring, rte_mbuf, ethdev, ixgbe PMD), libcrypto, librt, libm, pthread, hugetlbfs mounted at /mnt/huge, cmake &gt;= 2.6, Python 2.7 and bash 4 for config generation |
| **Minimum toolchain** | GNU C with gcc &gt;= 4.6.0 and cmake &gt;= 2.6; repo builds with -O9 -msse4.2 -march=corei7 |
| **Platforms** | x86-64 Linux &gt;= 3.2 only (SSE4.2, Nehalem or newer); peak results need a dual-socket NUMA server with Intel 10GbE ixgbe NICs that support Flow Director, plus 2 MiB hugepages |
| **Thread safety** | The access mode is set per table at init. EREW gives one core per partition with no synchronization. CREW allows a single writer, with optimistic lock-free readers checking per-bucket 32-bit version counters. CRCW makes writers take per-bucket CAS spinlocks. The server hard-codes these optimizations and cannot switch modes at runtime, and the paper advises avoiding CRCW. |
| **Drop-in for the baseline** | no |

## Gotchas

- Build mode matters. configure_all.sh sets NDEBUG=yes, but a plain `cmake ..` leaves asserts on, and the debug path in mehcached_get deliberately asserts on any value longer than 1500 bytes. With NDEBUG=yes, error paths written as `assert(false)` (such as hugepage allocation failure during table or pool init) print a message and keep going instead of aborting.
- Cache mode is lossy by design. A SET into a full 15-slot bucket evicts that bucket's oldest entry even when the log has free space. A GET with a too-small output buffer returns success with a silently truncated value (partial-value handling is marked TODO).
- expire_time is stored and echoed back to clients but never enforced by the server (netbench_server.c: 'TODO: use expire_time'), so clients must check staleness themselves.
- Log pool sizes are rounded up to the next power of two (and a 2 MiB multiple), so memory use can nearly double. Init also shells out to `rm /mnt/huge/mehcached_shm_*`. basic_types.h does `typedef int bool`, which breaks when included from C++ or alongside stdbool.h.

## Known shortcomings

- Baseline is Memcached, which peaks at 2 cores in the paper's setup; 16 partitions, and Memcached's latency is flat, so the 'more stable latency' claim does not hold.
- Not a memcached drop-in: its own UDP protocol with client-computed key hashes, no TCP, no client library beyond benchmarks. Needs an Intel ixgbe NIC with Flow Director, a DPDK 1.5-era build and hugepages at /mnt/huge; will not build on current DPDK without porting.
- Lossy cache mode: a full bucket evicts its oldest entry; a too-small GET buffer truncates the value but still returns success; TTL is stored but never enforced. A plain cmake build keeps asserts and aborts on GETs of values &gt;1500 B, while NDEBUG turns assert(false) error paths into no-ops. Log pool rounds up to a power of two; 'typedef int bool' breaks C++. Abandoned (master 2014); the successor mica2 is idle since 2017.

## Caveats and trade-offs

The paper does not state the compiler version or build flags (flags appear only in the repo's CMake files), which is why this is capped at Tier B. The vs-Memcached/MemC3 throughput figures use custom versions of those systems ported to MICA's lightweight network stack, and those modified versions are not in this repo. The paper used DPDK 1.4.1 and the README requires DPDK &gt;= 1.5.0, 2014-era APIs that will not build against modern DPDK without porting. The license (Apache-2.0) is asserted only in README text, with no LICENSE file. master was last committed 2014-03-03; the most recent commit anywhere is on the isca2015 branch (2016-01-18).

Requires Intel DPDK, hugepages, and a specific dual-socket/multi-NIC hardware layout to hit peak numbers; UDP-based protocol with no TCP or automatic loss recovery beyond GET/PUT idempotency; partitioned (EREW) design trades flexibility for scalability; cache mode uses a lossy, approximate-LRU hash index by design

## Maintenance

Abandoned: master was last committed 2014-03-03 and the isca2015 branch 2016-01-18, no issues or PRs have ever been filed, and Apache-2.0 is stated only in the README. It is a copyable C reference to learn from rather than a deployable service, and its C++ successor efficient/mica2 (DPDK 16.11, g++ &gt;= 5.3) has also been idle since 2017.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed NSDI'14 paper benchmarks MICA against Memcached, MemC3, Masstree and RAMCloud (Fig. 10, 13, 14) with the hardware stated. The netbench code and build flags (src/CMakeLists.txt) are in the repo, but the paper does not state the compiler version and the modified baseline versions are not published, so it is not A. The roughly 50-110x gap to Memcached exceeds the 50x cap threshold but is not implausible: it is against a peer-reviewed baseline that the paper shows peaks at 2 cores (Fig. 14), and the headline claim is 4-13.5x over the next-fastest system.
- **Verifier notes:** The core throughput numbers match the paper; the vs-Memcached gap is actually much larger than the record's '&gt;10x'. The workload's '8-partition' was wrong (the paper uses 16 partitions), and the latency clause 'more stable' was wrong (Memcached's latency is the flat one). last_commit 2016-01-18 is the isca2015 branch; the default branch is 2014-03-03; both are abandoned. 215 stars, gh license null, README Apache-2.0: all confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://www.usenix.org/system/files/conference/nsdi14/nsdi14-paper-lim.pdf>
  - <https://github.com/efficient/mica>
  - <https://github.com/efficient/mica/blob/master/src/CMakeLists.txt>
  - <https://github.com/efficient/mica/blob/master/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/efficient/mica>
  - <https://github.com/efficient/mica/blob/master/README.md>
  - <https://github.com/efficient/mica/blob/master/CMakeLists.txt>
  - <https://github.com/efficient/mica/blob/master/src/CMakeLists.txt>
  - <https://github.com/efficient/mica/blob/master/src/mehcached.h>
  - <https://github.com/efficient/mica/blob/master/src/config.h>
  - <https://github.com/efficient/mica/blob/master/src/common.h>
  - <https://github.com/efficient/mica/blob/master/src/basic_types.h>
  - <https://github.com/efficient/mica/blob/master/src/table.h>
  - <https://github.com/efficient/mica/blob/master/src/table.c>
  - <https://github.com/efficient/mica/blob/master/src/proto.h>
  - <https://github.com/efficient/mica/blob/master/src/shm.c>
  - <https://github.com/efficient/mica/blob/master/src/alloc_pool.c>
  - <https://github.com/efficient/mica/blob/master/src/hash.c>
  - <https://github.com/efficient/mica/blob/master/src/test.c>
  - <https://github.com/efficient/mica/blob/master/src/netbench_server.c>
  - <https://github.com/efficient/mica/blob/master/src/netbench_client.c>
  - <https://github.com/efficient/mica/blob/master/build/gen_confs.py>
  - <https://github.com/efficient/mica/blob/master/scripts/setup_dkdp_env.sh>
  - <https://github.com/efficient/mica/blob/master/configure_all.sh>
  - <https://github.com/efficient/mica/blob/master/configure_server.sh>
  - <https://github.com/efficient/mica/blob/master/configure_client.sh>
  - <https://github.com/efficient/mica/branches>
  - <https://github.com/efficient/mica/commits/isca2015>
  - <https://github.com/efficient/mica/commits/master>
  - <https://github.com/efficient/mica/issues?q=is%3Aissue+OR+is%3Apr>
  - <https://github.com/efficient/mica2>
  - <https://www.usenix.org/system/files/conference/nsdi14/nsdi14-paper-lim.pdf>
  - <https://hn.algolia.com/api/v1/search?query=MICA%20key-value%20store&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/efficient/mica`) · [data/wave6/enrich/raw/github_com_efficient_mica.json](../../../data/wave6/enrich/raw/github_com_efficient_mica.json) (enrichment confidence 0.86)

</details>
