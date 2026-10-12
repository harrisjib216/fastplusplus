# MountDB (learned indexing integrated into RocksDB)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Indexes](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++ (no code released)` · `no license` · ⚪ unknown

> Paper-only RocksDB v8.10 extension replacing SkipList memtable and fence-pointer index with learned indexes; up to 1.77x reads.

| | |
|---|---|
| **Beats** | RocksDB v8.10.0 (plus the learned-index LSMs DobLIX and TridentKV, ported to RocksDB 8.10.0) |
| **Claimed result** | Against stock RocksDB v8.10.0: up to 1.77x read-only and 1.44x balanced throughput (Fig. 6), up to 2.8x read throughput at the smallest value sizes (Fig. 8), and up to 1.3x write-only throughput over RocksDB's SkipList memtable (up to \~1.5x as value size shrinks). The abstract's 'up to 1.5x write, 2.1x read vs state-of-the-art systems' is against the learned-index LSMs DobLIX and TridentKV (2.1x is vs DobLIX at the smallest values), not against RocksDB. |
| **Workload** | Six real-world/synthetic datasets (\~55 GB each, 500M operations, 16 client threads, compression off). Write-only, balanced 1:1 and read-only mixes, YCSB A-F, and varied/mixed value sizes (UDB, ZippyDB, UP2X). MountDB uses an ALEX+ Memtable with skeletonized model reuse and a block-aware PGM (Fence) on-disk index. |
| **Metric** | throughput |
| **Hardware** | 2x Intel Xeon E5-2690 v4 (14 cores each, 2.60 GHz), 126 GB RAM, 500 GB NVMe SSD, Ubuntu 22.04.5 LTS |
| **Links** | [benchmark](https://arxiv.org/abs/2605.23815) |

## Verdict

The authors ran db_bench on a 2x Xeon E5-2690 v4 machine with an NVMe SSD (16 client threads, 64 MB Memtables, compression off, 8-byte keys and 100-byte values, about 55 GB and 500M operations per dataset). They report up to 1.3x write-only, 1.44x balanced and 1.77x read-only throughput over stock RocksDB v8.10.0, rising to 2.8x for reads at 16 B values. No compiler or flags are given, and no independent reproduction exists.

## Use it when

- You are designing or evaluating learned indexing inside an LSM store and want a worked recipe (an ALEX+ Memtable with skeleton reuse, and PGM over fence keys) that leaves RocksDB's SST and block format unchanged.
- Read-heavy RocksDB workloads with numeric 8-byte keys and a mostly cached working set: up to 1.77x over RocksDB on read-only, and 1.34-1.52x over all baselines when the data is fully cached.
- Small values (16-64 B): up to 2.8x read and about 1.5x write throughput over RocksDB at the smallest sizes, and 1.3-1.6x reads on the mixed-size UDB, ZippyDB and UP2X traces.
- Write-heavy ingest with smooth or slowly shifting key distributions, where the reused skeleton stays accurate: up to 1.3x write-only, and 0.95-1.05 vs 0.6-0.7 Mops/s (98 s vs 161 s) in the microbenchmark that cycles through six distributions.

## Skip it when

- You need working code. Nothing is released: the lead author's GitHub has only an unmodified RocksDB fork and a DobLIX port, so you would reimplement MountDB against RocksDB internals yourself.
- String or variable-length keys: the design and evaluation cover numeric keys only, and learned string indexing is left to future work.
- I/O-bound reads: with use_direct_reads, throughput was 'virtually the same' across all systems, and with only 10% of the data cached the gain shrinks to 1.2-1.3x.
- Irregular key distributions or abrupt distribution shifts: write gains narrow to about 1.2x on OSM, and a never-refreshed skeleton lost throughput when the distribution changed.
- Production use: it is an unreviewed preprint pinned to RocksDB v8.10.0, evaluated with compression disabled, and it never discusses deletes, recovery or the rest of RocksDB's feature surface.

## How it is fast

In memory it uses ALEX+ (the concurrent variant of ALEX, with gapped arrays and model-based placement) plus 'skeletonization': every 10 flushes (phi=10) a background task bulk-loads ALEX+ from the immutable Memtable's sorted keys and strips payloads, counters and locks. New Memtables then start from that model hierarchy and gap bitmap instead of cold. Without this, a 64 MB ALEX+ Memtable is flushed about every 0.4 s, before it converges, and ends up no better than SkipList. On disk, PGM (Fence) trains a PGM-index with epsilon=1 on only the first key of each block. A lookup therefore predicts a block and reads it together with both neighbours in one FilePrefetchBuffer I/O, and the resulting index is about 172 KB per 64 MB SST, versus 296 KB for RocksDB's fence table.

## Compared with alternatives

Compared with Bourbon, MountDB's design also speeds up writes (Bourbon indexes only the disk component and depends on WiscKey's key-value separation) and keeps RocksDB's SST format, but Bourbon ships an artifact and MountDB ships none. If you need something runnable against RocksDB today, the practical routes are TerarkDB (a RocksDB fork with code) or building directly on the ALEX and PGM-index libraries.

## Integration

| | |
|---|---|
| **Form** | source-drop (unreleased; described as a patched RocksDB v8.10.0 that swaps the Memtable index and the SST index block) |
| **Dependencies** | not documented (unreleased). Per the paper: RocksDB v8.10.0, ALEX+ (the 'alexol' concurrent ALEX in the GRE benchmark repo, which has no license file) and the PGM-index (Apache-2.0). |
| **Minimum toolchain** | not documented (no compiler, version or flags are given) |
| **Platforms** | not documented. It was evaluated only on x86-64 (2x Xeon E5-2690 v4, 126 GB RAM, 500 GB NVMe SSD, Ubuntu 22.04.5). |
| **Thread safety** | Per the paper, the ALEX+ Memtable supports concurrent reads and inserts (an optimistic lock per data node, shared-exclusive locks on internal nodes). It was run with 16 client threads and 8 compaction threads, and skeleton building runs as a background task during flush. None of this can be checked without code. |
| **Drop-in for the baseline** | partial — explain: it is designed to keep RocksDB's API, read and write paths and SST data-block format, and it replaces only the Memtable index and the SST index block. But no code exists, keys must be numeric, and the paper does not say whether its SSTs stay readable by stock RocksDB. |

## Gotchas

- The abstract's 'up to 1.5x write, 2.1x read' is measured against DobLIX and TridentKV (the 2.1x only at the smallest value size), not against RocksDB. Against stock RocksDB at the default 100 B values the figures are 1.3x write-only, 1.44x balanced and 1.77x read-only.
- PGM (Fence) always reads three blocks (the predicted one plus or minus one), so MountDB cuts the maximum block size to a third of the default. The paper says the baselines had identical Memtable, cache and compaction settings, but it does not say whether their block size was matched.
- Skeletons are a partial deep copy of the previous Memtable's ALEX+ nodes (keys and gap bitmap, with null payloads). Their memory cost is not quantified, and the refresh interval phi=10 was chosen empirically.
- The authors ported the DobLIX and TridentKV baselines from RocksDB 5.x to 8.10.0 themselves, and the DobLIX code lacks its paper's RL tuner, so the learned-LSM comparisons are against reduced versions.

## Known shortcomings

- arXiv preprint with no code. The abstract's 1.5x/2.1x is vs DobLIX/TridentKV; vs RocksDB it is up to 1.77x reads (2.8x at small values) and \~1.3x writes.
- Numeric keys only, compression off, pinned to RocksDB 8.10; deletes and recovery are not discussed. With direct I/O all systems are about equal and with 10% cached the gain is 1.2-1.3x; block size was cut to a third for the 3-block read and it is unclear whether baselines matched. Baselines were ported by the authors (DobLIX without its RL tuner); the lead author's GitHub has only a plain RocksDB fork and a DobLIX port.

## Caveats and trade-offs

Preprint only (arXiv 2605.23815, McGill; not peer-reviewed as of 2026-09-26); no code released (a GitHub search for 'MountDB' finds only an unrelated repo). The headline abstract numbers are against competing learned-index systems; the gains over stock RocksDB are up to 1.77x (default value size) or 2.8x (smallest values) for reads and \~1.3x for writes. No compiler or flags are stated.

Requires modifying RocksDB internals (Memtable and on-disk index replacement) and maintaining model-reuse state across Memtable instances.

## Maintenance

This is an arXiv preprint from McGill (v1, 22 May 2026; not peer-reviewed as of 2026-09-26) with no released code or license, so it is a reference design only, and its maintenance status is unknown.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** This is an arXiv preprint (2605.23815v1, 22 May 2026; no venue or DOI found via crossref), so it is not peer-reviewed. It has first-party numbers against stock RocksDB v8.10.0 and the ported DobLIX/TridentKV on stated hardware (2x Xeon E5-2690 v4). But no code is released and no compiler or flags are given, so it stays C.
- **Verifier notes:** The arXiv abstract matches the record's quote exactly. The body resolves the ambiguity the record flagged: the 2.1x read and 1.5x write headline is against DobLIX/TridentKV, and the RocksDB-specific gains are listed in the corrected claimed_speedup. Keep it as a paper-only reference entry.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2605.23815>
  - <http://export.arxiv.org/api/query?id_list=2605.23815>
  - <https://arxiv.org/pdf/2605.23815v1>
  - <https://api.crossref.org/works?query.title=A+Pragmatic+Approach+to+Learned+Indexing+in+RocksDB&rows=3>
- **Sources the enricher read:**
  - <https://arxiv.org/abs/2605.23815>
  - <http://export.arxiv.org/api/query?id_list=2605.23815>
  - <https://arxiv.org/pdf/2605.23815v1>
  - <https://api.crossref.org/works?query.bibliographic=MountDB+learned+indexing+RocksDB&rows=5>
  - <https://hn.algolia.com/api/v1/search?query=%22MountDB%22>
  - <https://hn.algolia.com/api/v1/search?query=2605.23815>
  - <https://github.com/search?q=MountDB&type=repositories>
  - <https://github.com/ShubhamVashisth7>
  - <https://github.com/ShubhamVashisth7/rocksdb>
  - <https://github.com/ShubhamVashisth7/DobLIX/tree/copilot/integrate-learned-index-in-rocksdb>
  - <https://github.com/theoanab>
  - <https://github.com/gre4index/GRE>
  - <https://github.com/gvinciguerra/PGM-index>
  - <https://github.com/microsoft/ALEX>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:mountdb-learned-indexing-integrated-into-rocksdb`) · [data/wave6/enrich/raw/paper_mountdb_learned_indexing_integrated_into_rocksdb.json](../../../data/wave6/enrich/raw/paper_mountdb_learned_indexing_integrated_into_rocksdb.json) (enrichment confidence 0.55)

</details>
