# DiaLSM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · 🟢 active

> Hash-sharded LSM built on RocksDB 8.3.2 that reroutes writes around stalled shards, cutting write stalls \~94%. Code not released.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | 8KB FillRandom: up to 2.4x higher throughput and \~50% lower latency than ADOC (a RocksDB-based auto-tuner), not stock RocksDB. 94.3% fewer write stalls: ADOC and RocksDB show up to 17.6x higher stall rates. \~50% lower average/median latency than both RocksDB(16) and ADOC(16) (Fig. 7). ReadRandomWriteRandom: 1.8x vs ADOC. YCSB-E: \~1.7x vs ADOC and RocksDB at the default scan length 128, and 3.3x/5.7x/8.9x at scan lengths 1K/4K/16K; YCSB-C at parity. Sysbench on MariaDB/MyRocks: 2.3x vs ADOC on oltp_insert, up to 9.9x on oltp_write_only, 2.2x vs ADOC on oltp_read_write. |
| **Workload** | db_bench FillRandom (128B/1KB/8KB values, 10M entries per I/O thread) and ReadRandomWriteRandom (100M 1KB entries preloaded); YCSB A-F with 1KB values; Sysbench OLTP on MariaDB/MyRocks. DiaLSM is built atop RocksDB v8.3.2. Baselines are RocksDB v8.3.2 with Sub-Compaction, and ADOC. For all systems, write throttling (WST), commit logging and block cache were disabled. |
| **Metric** | throughput |
| **Hardware** | Two AMD EPYC 7352 24-core CPUs, 256GB RAM, MZSLR3T8HBLS-00A07 NVMe SSD, CentOS 7 with ext4 |
| **Adoption** | 1 star |
| **Last commit** | 2026-09-13 |
| **Links** | [repository](https://github.com/DISCOS-LAB/DiaLSM) · [benchmark](https://arxiv.org/abs/2609.14370) |

## Verdict

Setup: arXiv preprint (v1, 2026-09-13). Hardware: 2x AMD EPYC 7352, 256GB DRAM, one 3.84TB Samsung PCIe Gen3x4 NVMe, CentOS 7/ext4. Baselines: RocksDB v8.3.2 with Sub-Compaction and ADOC, all with throttling, WAL and block cache off. Results: on 8KB FillRandom, DiaLSM had up to 2.4x ADOC's throughput, 94.3% fewer stalls than both baselines, and about 50% lower mean/median latency than both. YCSB-E was about 1.7x over both at scan length 128 and 3.3x/5.7x/8.9x at 1K/4K/16K. Compiler and flags are not stated, and there is no artifact to reproduce the numbers.

## Use it when

- Sustained write-heavy ingest with large values (the paper's best case is 8KB FillRandom), where RocksDB write stalls cap throughput and cause p99.99+ latency spikes.
- Write-dominated mixes such as ReadRandomWriteRandom at 10% reads / 90% writes, or insert/update-heavy OLTP on MyRocks (Sysbench oltp_insert, oltp_write_only), on a many-core box with spare CPU. The paper gave DiaLSM 32 compaction threads split across shards.
- Long range scans (1K-16K keys per scan), where parallel per-shard iteration gave 3.3x-8.9x over both ADOC and RocksDB.
- Servers with several NVMe SSDs: shards can be spread across devices, and with 8KB values throughput kept scaling past 8 shards only when a second SSD was added.
- As a reference design for LSM write-stall work (queueing model plus fallback redirection). Until code ships it is not a library you can adopt.

## Skip it when

- Anything that needs working code now. The repo is one README commit saying source 'will be available soon', with no license.
- Read-dominant or read-only workloads. YCSB-C is at parity with RocksDB and ADOC. At 90% reads / 10% writes, DiaLSM loses some throughput as shards grow while ADOC stays flat. On the fallback path a Get needs two shard reads.
- Short scans with many shards: YCSB-E at the default scan length of 128 peaks at 4 shards (about 1.7x) and then declines as the cost of parallel iteration outweighs the gain.
- Space- or CPU-constrained setups. Space amplification is 1.14x-1.5x with 2-16 shards (Table IV, millions of CEs), and DiaLSM uses more CPU than both baselines (Fig. 15).
- Deployments that need the full RocksDB feature set (transactions, column families, snapshots, WAL durability, block cache) or elastic shard counts. Only Open/Close/Put/Get/Seek is described, every benchmark ran with WAL and block cache off, and hash-mod-N placement has no resharding or auto-tuning.

## How it is fast

The authors model the write-flush-compaction pipeline as an M/G/1 queue with vacations, where each vacation is a stall. The model says tuning one stage only moves stalls to another layer (a 'balloon effect'): this applies to ADOC's memtable/thread tuning and to RocksDB Sub-Compaction. With L independent shards, the chance that all of them stall at once falls roughly as alpha^L. A write to a stalled primary goes to the fallback shard with the smallest L0, then lowest memtable use, then smallest pending backlog, then smallest total size. It leaves a 20-byte Clue Entry (CE) in a 2MB reserved memtable area that stall thresholds ignore. CEs are pinned in L0 ('CE L0 capping') and mirrored in an in-memory CE cache so the extra hop stays cheap. Range scans run Seek/Next on all shards in parallel, which is where the large YCSB-E gains on long scans come from.

## Compared with alternatives

MatrixKV also targets write stalls but needs NVM for its matrix container, while PebblesDB (fragmented LSM) and Titan (key-value separation for large values) change the on-disk layout. DiaLSM is the one to watch if you want to stay on plain NVMe with stock RocksDB format per shard and remove stalls by structure rather than tuning. Today, pick MatrixKV, PebblesDB or Titan when you need code you can run, since DiaLSM has none.

## Integration

| | |
|---|---|
| **Form** | Not released. The paper describes a modified RocksDB v8.3.2 source tree (a db_master class over N RocksDB instances), so expect a source-drop fork if it ships. |
| **Dependencies** | RocksDB v8.3.2 (DiaLSM is built on top of it); nothing else documented |
| **Minimum toolchain** | Not documented for DiaLSM. Its base, RocksDB v8.3.2, requires C++17 (GCC &gt;= 7, Clang &gt;= 5). |
| **Platforms** | Evaluated only on x86-64 Linux (2x AMD EPYC 7352, CentOS 7, ext4, NVMe); nothing else documented |
| **Thread safety** | Not documented. The benchmarks drive db_master from 10 concurrent I/O threads, while a 0.1s shard-state monitor, per-shard flush/compaction threads and optional rollback threads run in the background. |
| **Drop-in for the baseline** | partial — it wraps N RocksDB instances behind a db_master API (Open/Close/Put/Get/Seek) and was run under MyRocks, but the paper covers no other RocksDB API, and with no code the compatibility cannot be checked |

## Gotchas

- Every headline experiment ran with rollback disabled. Rollback is the step that moves redirected keys back to their primary shards. Turned on after an 850K-CE write burst, it added about 60s of delay before reads. Once CEs pass the default limit of 1M, rollback is forced and no new CEs are accepted, so write stalls come back.
- The benchmark config is non-default for every system: write-stall throttling, WAL/commit logging and block cache all off. The RocksDB baseline was also reconfigured: 2m memtables of 512/m MB each and 32 compaction threads. The 2.4x/1.8x/2.2x/2.3x headlines are against ADOC, not stock RocksDB.
- Crash recovery scans shards for redirected keys whose CE is missing and blocks user I/O while it runs. Because the WAL was off in all experiments, the cost with durability on was never measured.
- Algorithm 1 bounds a range scan at Kstart + L and appends each shard's results with no merge step, even though global ordering is a stated design goal. YCSB-E ran with a single I/O thread 'to avoid the parallel processing overhead'.

## Known shortcomings

- The 2.4x/1.8x/2.2x gains are against ADOC, not RocksDB; against RocksDB it is \~50% lower latency, 94.3% fewer stalls and 8.9x on YCSB-E. 'ICDE 2027' is an author claim only (conference in May 2027, no accepted list yet). The repo is README-only (verifier downgrade).
- The repo is README-only: no code, no license. The big wins (2.4x/1.8x/2.2x/2.3x) are vs ADOC, not stock RocksDB, and all runs disable throttling, WAL and block cache. Rollback is off in the main runs; above 1M compaction entries rollback is forced and stalls return. Space amplification 1.14-1.5x; more CPU.
- Read-heavy: parity on YCSB-C, loses throughput beyond a few shards at 90% reads; short scans peak at 4 shards. The paper's API is only Open/Close/Put/Get/Seek, the scan algorithm shows no merge step, no resharding. ICDE 2027 acceptance is author-claimed only (program page 404).

## Caveats and trade-offs

Venue is author-reported only. The arXiv comment (v1, 2026-09-13) and the repo README say the paper was accepted to the 43rd IEEE ICDE 2027 (Copenhagen, May 17-21 2027). The date fits ICDE 2027's Round-1 notification (2026-09-10), but there is no public accepted-papers list or proceedings, so peer review cannot be confirmed yet. Tier is held at C; it can go to B once ICDE 2027 lists the paper. The headline 2.4x/1.8x/2.2x/2.3x gains are against ADOC, not stock RocksDB. Against RocksDB the paper shows \~50% lower latency, 94.3% fewer stalls and the YCSB-E range-scan wins. The RocksDB config is non-default: throttling, WAL/commit logging and block cache were all disabled. The paper says the code is 'publicly available' at DISCOS-LAB/DiaLSM, but the repo holds only a README ('will be available soon') and has no license. Compiler/flags are not stated.

Shards the write-flush-compaction pipeline internally to avoid a single monolithic stall path; adds shard-management complexity and per-shard resource overhead.

## Maintenance

The repo was created 2026-09-13 with a single README commit (1 star, no license, no code); ICDE 2027 acceptance is author-claimed and not yet listed publicly. The lab's earlier DownForce paper did publish a GPL-2.0 RocksDB fork, so a release is plausible, but for now this is a paper to read, not a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** The arXiv preprint (v1, 2026-09-13) benchmarks DiaLSM against RocksDB v8.3.2 (with Sub-Compaction) and ADOC on stated hardware (2x AMD EPYC 7352). The ICDE 2027 acceptance comes only from the authors: the conference is in May 2027, there is no public accepted-papers list or proceedings yet, and no code is released. That leaves first-party preprint numbers, which is tier C, not B.
- **Verifier notes:** The record credited ADOC-relative numbers to RocksDB; claimed_speedup is rewritten with the correct baseline for each number. The ICDE 2027 acceptance is plausible from the notification date but unverifiable today (conference not held, no published list), so the tier goes from B to C. Repo metadata checks out via gh: 1 star, README-only, no license, single commit 2026-09-13.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2609.14370>
  - <https://arxiv.org/pdf/2609.14370>
  - <https://github.com/DISCOS-LAB/DiaLSM>
  - <https://icde2027.github.io/>
  - <https://icde2027.github.io/cf-research-papers.html>
- **Sources the enricher read:**
  - <https://github.com/DISCOS-LAB/DiaLSM>
  - <https://arxiv.org/abs/2609.14370>
  - <https://arxiv.org/pdf/2609.14370>
  - <https://github.com/DISCOS-LAB>
  - <https://github.com/DISCOS-LAB/DownForce>
  - <https://github.com/DISCOS-LAB/Resystance>
  - <https://hn.algolia.com/api/v1/search?query=%22DiaLSM%22&typoTolerance=false>
  - <https://icde2027.github.io/>
  - <https://icde2027.github.io/program.html>
  - <https://raw.githubusercontent.com/facebook/rocksdb/v8.3.2/HISTORY.md>
  - <https://raw.githubusercontent.com/facebook/rocksdb/v8.3.2/CMakeLists.txt>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/discos-lab/dialsm`) · [data/wave6/enrich/raw/github_com_discos_lab_dialsm.json](../../../data/wave6/enrich/raw/github_com_discos_lab_dialsm.json) (enrichment confidence 0.6)

</details>
