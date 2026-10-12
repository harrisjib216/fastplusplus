# BVLSM

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Study only · `C++` · `no license` · ⚪ unknown

> Research RocksDB variant that splits big values out at WAL-write time. Paper reports 7.6x RocksDB random-write throughput at 64KB.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | 64KB random writes: 7.6x throughput vs RocksDB v9.7.3 and 1.9x vs BlobDB with async WAL (R-WA); \~7x vs RocksDB and \~3x vs BlobDB with sync WAL (R-WS); up to 8x vs RocksDB and 2x vs BlobDB with WAL off (R-WO). Sequential writes: S-WS \~4.1x RocksDB / 9.8x BlobDB, S-WA \~1.3x / 2.2x, S-WO up to 1.3x / 2x. YCSB-A (8KB values): insert/update/read latency is 27.2%/28.4%/19.7% of RocksDB's. 100GB sustained random write: 1.5x RocksDB and 2x BlobDB on average. |
| **Workload** | db_bench random and sequential writes with 4KB-64KB values under sync, async and disabled WAL (R-WS/R-WA/R-WO, S-WS/S-WA/S-WO); YCSB workload A (16B keys, 8KB values, 500k preloaded records); 100GB sustained random-write stability test. Baselines are RocksDB v9.7.3 and BlobDB. The comparison is WAL-time vs flush-time key-value separation. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 5218 (16C/32T, 2.30GHz), 4x32GB DDR4-2933 (128GB), Samsung 990 EVO NVMe SSD (1TB), Ubuntu 20.04 |
| **Links** | [benchmark](https://arxiv.org/abs/2506.04678) |

## Verdict

The authors ran db_bench on a Xeon Gold 5218 with 128GB DDR4 and a Samsung 990 EVO NVMe (Ubuntu 20.04): 100GB of data, 16B keys, 4-64KB values, against RocksDB v9.7.3 and BlobDB 'configured identically' (configs not published). With 64KB random writes they report 7.6x RocksDB and 1.9x BlobDB with async WAL, about 7x and 3x with sync WAL, and up to 8x and 2x with WAL off. YCSB-A with 8KB values gives insert, update and read latencies of 27.2%, 28.4% and 19.7% of RocksDB's, and a 100GB sustained 4KB-value write test averages 1.5x RocksDB and 2x BlobDB. Compiler, flags and thread counts are not stated, and nobody else has reproduced the results.

## Use it when

- As a design reference if you maintain a RocksDB fork and want to separate values before the WAL rather than at flush.
- Ingest of values of 16-64KB and up (images, embeddings, large log chunks) on NVMe, where RocksDB throughput flattens above 32KB and L0 stalls make it oscillate. The paper's gains are largest at 32-64KB.
- Big-value writes that must use a synchronous WAL. Only pointer-sized records reach the WAL, and this is where the paper shows its largest relative gains: about 7x RocksDB on random writes and 4.1x on sequential writes.
- As an argument when you evaluate BlobDB or Titan: flush-time separation still buffers full values in MemTables and the WAL.

## Skip it when

- Any time you need running code. There is no public repository, license, build instructions or API, so you would have to reimplement it from an 8-page paper.
- Small values. Values under the threshold (example 4KB) stay inline and take RocksDB's normal path, and nothing below 4KB was benchmarked.
- Update- or delete-heavy or space-constrained workloads. The paper describes no garbage collection or space reclamation for BValue files and reports no space-amplification numbers. Integrated BlobDB and Titan both have GC.
- Range-scan or iterator-heavy reads. No scan benchmark is reported, and any separated value missing from the BVCache costs an extra random read from a BValue file.
- Anything with strict durability needs. No crash-recovery testing is reported. In WAL-disabled mode values sit in an in-memory buffer until a background thread writes them, and the paper does not say how those writes are ordered against MemTable flushes.

## How it is fast

It moves WiscKey-style key-value separation from flush time, where BlobDB and WiscKey do it, to the write path before the WAL. MemTables then hold only pointers, so flushes are rarer, fewer WAL bytes are written, and compaction rewrites only keys plus pointers. That cuts write amplification and the L0-stall throughput dips seen in RocksDB. Separated values are spread by hash or round-robin across several BValue files, each meant to feed its own NVMe submission queue. The paper credits this for up to 40% more write throughput; its FIO microbenchmark (4 threads, 4KB) shows multi-queue 60.6% faster than single-queue. A BVCache (a fixed-size deque plus hash table, sized like one MemTable) keeps recently written entries to cut read latency on separated values.

## Compared with alternatives

For large values you can actually deploy, use Titan (Apache-2.0 RocksDB plugin, commits as recent as September 2026) or RocksDB's integrated BlobDB. KVell, PebblesDB, MatrixKV and SplinterDB also ship code. BVLSM is the only catalogued entry that separates values before the WAL, so read it only as a design reference when your values are 32KB or more and ingest is bound by the synchronous WAL.

## Integration

| | |
|---|---|
| **Form** | none published: a paper-only design described as a modification inside RocksDB's write path; no source, library or binary |
| **Dependencies** | not documented (the experiments use RocksDB v9.7.3 as the underlying engine) |
| **Minimum toolchain** | not documented (compiler and flags not stated) |
| **Platforms** | Tested only on x86-64 Linux (Xeon Gold 5218, Ubuntu 20.04, kernel 4.15) with a Samsung 990 EVO NVMe SSD. The multi-queue value store assumes NVMe; other devices are not evaluated. |
| **Thread safety** | not documented (db_bench and YCSB thread counts are also not stated) |
| **Drop-in for the baseline** | no |

## Gotchas

- The 7.6x headline comes from the async-WAL mode (R-WA), but the design section defines only two modes: WAL-enabled (value fsync'd to its BValue file, then the pointer record written synchronously to the WAL, so two syncs per Put with no group commit described) and WAL-disabled (values buffered and written by a background thread). How async-WAL mode behaves is not described.
- Write-time separation is not new inside RocksDB. The legacy StackableDB BlobDB wrote blob files synchronously in the write API. The RocksDB wiki says the integrated BlobDB moved to flush and compaction for consistency and large I/Os. The paper benchmarks only the integrated BlobDB and does not discuss the legacy one.
- The paper contradicts itself in places. BVCache eviction is described as Most-Recent-Write-First, as LRU tail eviction, and as time- or frequency-based 'depending on system load'. The text says BlobDB cuts read latency by 35.5%, but Fig. 8 shows BlobDB at 29.1us vs RocksDB's 82.1us, i.e. 35.4% of RocksDB. The setup lists '1 immutable and 5 mutable MemTables'. A '2.49x BlobDB' figure appears in the FIO-only section.
- The benchmark datasets are small relative to the host's 128GB RAM: 100GB for db_bench, and about 4GB for YCSB-A (500k x 8KB). So the YCSB read latencies were probably served largely from the page cache (my inference; the paper does not discuss caching).

## Known shortcomings

- The '7x/3x over RocksDB' was wrong: the 3x is against BlobDB with a synchronous WAL. IEEE HPCC 2025; no code.
- Paper only: no code, license or repo (a GitHub 'bvlsmz' result is spam); 0 citations. No GC or space reclamation for BValue files; no scan, crash-recovery or space-amplification tests. The 7.6x headline comes from an async-WAL mode the design section never defines; sync mode does two syncs per Put.
- Write-time key-value separation is not novel (legacy StackableDB BlobDB did it) and the paper does not discuss it. Internal contradictions (BVCache eviction policy, BlobDB read-latency percentages, MemTable counts). Datasets (\~4 GB YCSB) are small against 128 GB RAM, so reads are likely page-cached. No compiler, flags or thread counts.

## Caveats and trade-offs

Peer-reviewed: published in the 2025 IEEE International Conference on High Performance Computing and Communications (HPCC 2025, Exeter UK, Aug 13-15 2025), pp. 34-41, doi:10.1109/HPCC67675.2025.00037. This was found via Crossref; the arXiv page has no journal-ref. No public code repository exists (a GitHub search for BVLSM returns only an unrelated spam repo), and compiler/flags are not stated, so it cannot reach tier A. All numbers are the authors' own. The earlier '\~7x and 3x over RocksDB' was a misreading: under sync WAL it is \~7x over RocksDB and \~3x over BlobDB.

Separates key/value at WAL-write time rather than at flush time so MemTables only hold lightweight metadata; adds a multi-queue BValue store and BVCache; targets big-value (multimedia/embedding) workloads specifically, smaller advantage expected for small-value workloads typical of many RocksDB deployments.

## Maintenance

Paper only: arXiv v2 from June 2025, peer-reviewed at IEEE HPCC 2025 (pp. 34-41, doi:10.1109/HPCC67675.2025.00037). There is no code, repository or license (the only GitHub hit for 'bvlsm' is an unrelated spam repo), and OpenAlex shows zero citations as of 2026-09-26, so it is usable only as a design reference.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: Crossref shows the paper was peer-reviewed and published at IEEE HPCC 2025 (pp. 34-41, doi:10.1109/HPCC67675.2025.00037, same title and authors). It benchmarks BVLSM against RocksDB v9.7.3 and BlobDB on a stated Xeon Gold 5218. It is not A because no code is public and the compiler/flags are unstated.
- **Verifier notes:** Tier upgraded C -&gt; B after Crossref showed IEEE HPCC 2025 publication. claimed_speedup is fixed: the '3x' was vs BlobDB, not RocksDB. Per-WAL-mode figures, sequential-write, YCSB-A and sustained-write figures are added. No repo to check metadata against.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2506.04678>
  - <https://arxiv.org/pdf/2506.04678>
  - <https://api.crossref.org/works?query.title=BVLSM+WAL-Time+Key-Value+Separation&rows=3&select=title,container-title,DOI,type,published>
  - <https://api.crossref.org/works/10.1109/hpcc67675.2025.00037>
  - <https://github.com/beanian67/bvlsmz>
- **Sources the enricher read:**
  - <https://arxiv.org/abs/2506.04678>
  - <https://arxiv.org/pdf/2506.04678>
  - <https://api.crossref.org/works/10.1109/hpcc67675.2025.00037>
  - <https://api.openalex.org/works/doi:10.1109/HPCC67675.2025.00037>
  - <https://api.openalex.org/works?search=BVLSM>
  - <https://github.com/search?q=BVLSM&type=repositories>
  - <https://github.com/search?q=BVCache&type=code>
  - <https://github.com/beanian67/bvlsmz>
  - <https://hn.algolia.com/api/v1/search?query=BVLSM>
  - <https://github.com/facebook/rocksdb/wiki/BlobDB>
  - <https://github.com/tikv/titan>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:bvlsm`) · [data/wave6/enrich/raw/paper_bvlsm.json](../../../data/wave6/enrich/raw/paper_bvlsm.json) (enrichment confidence 0.6)

</details>
