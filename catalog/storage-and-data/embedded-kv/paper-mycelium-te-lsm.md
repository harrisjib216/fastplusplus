# Mycelium (TE-LSM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Embedded key-value stores](README.md)</sub>

**Tier C** (first-party claim) · Study only · `C++` · `no license` · ⚪ unknown

> RocksDB fork that splits columns, re-encodes values or builds secondary indexes during compaction, for faster analytic reads than RocksDB.

| | |
|---|---|
| **Beats** | RocksDB |
| **Claimed result** | Up to 4.25x lower query latency (abstract: 'up to 425% improvements in read latency compared to RocksDB baseline') for Q2, a column-retrieving range query (max over a range). This is with the CONVERT transformer (JSON to FlatBuffers during compaction) against a RocksDB baseline that stores JSON. The split transformation gives 2.8x on Q2, and row-retrieving queries (Q6/Q7) get slower under split. Write-throughput overhead against RocksDB is 10.09% to 21.25% (Table 2): under 16% for a single transformation and about 20% for two. Secondary-index (augment) queries show gains of 'several hundred thousand times' only because plain RocksDB has to do full table scans. |
| **Workload** | RocksDB-based prototype that embeds split, convert (JSON to FlatBuffers) and augment (secondary index) transformations into compaction through cross-column-family 'Tierveling'. Measured: write throughput after a 100 GB preload (200M records of about 500 B), plus query latency (min/P25/P50/P75/max) for Q2 to Q7 (column-retrieving, row-retrieving and index point/range queries) with Zipfian keys, against RocksDB baselines. |
| **Metric** | throughput |
| **Hardware** | 2x 16-core CPUs @ 3.00GHz, 128GB ECC RAM, two 480GB SATA SSDs, Ubuntu 20.04.6 LTS |
| **Links** | [benchmark](https://arxiv.org/abs/2506.08923) |

## Verdict

The test machine had two 16-core 3.0 GHz CPUs, 128 GB RAM and SATA SSDs on Ubuntu 20.04; the paper does not name the CPU model, compiler, flags or RocksDB version. After a 100 GB preload of 200M records, Mycelium's JSON-to-FlatBuffers transform cut latency 4.25x on Q2 (MAX over a key range, Zipfian keys) against RocksDB storing JSON, and split cut it 2.8x; single transforms cost 10-15% of write throughput and split+convert cost 21%. The index-query wins are measured against RocksDB full scans, and the paper's setup text is internally inconsistent (32 vs 50 columns per row, stated as about 500 B).

## Use it when

- Research or prototyping, when you want to measure whether ETL done during compaction (column-group splitting, format conversion, index building) beats a separate pipeline on your own write-heavy data.
- Write-heavy ingest of wide rows (the paper uses rows of about 500 B with 32-50 columns) where later reads project one or a few columns or aggregate over key ranges. On a range MAX query, split gave 2.8x and JSON-to-FlatBuffers gave 4.25x.
- Values arrive as text JSON and you can accept about 15% lower write throughput to have them stored in a compact binary format.
- You need lookups on a non-key attribute and can accept an index that covers only data already compacted out of L0. The paper measured about 10% write-throughput cost for this.

## Skip it when

- Production, or anywhere you need clear licensing. The paper does not link any code. The probable repo is an anonymous single-commit snapshot with no top-level license.
- Row-retrieving workloads (SELECT \* point or range queries). Under the split transform, the point query (Q7) was slower than plain RocksDB at most percentiles, and the range query (Q6) had worse tail latency.
- Systems bound by write throughput. Each transformation cost 10-21% of RocksDB's write throughput in the paper, and each extra cross-column-family compaction adds write amplification (the cost model's WA + n).
- Delete-heavy tables with a secondary index. In the repo, every Delete scans the whole secondary-index column family to find matching entries.
- Workloads that need read-your-writes through the index. Index entries are created only when data leaves L0, and IndexRead never checks the memtable or L0.

## How it is fast

Compaction already reads every record from its SST files and writes it back out. Mycelium does the transformation during that same pass, adding in-memory CPU work but no extra read I/O (the paper calls this 'transformation-embedded compaction'). A cross-column-family compaction writes the source family's merged L0 runs into a destination family's L0, and 'Tierveling' uses tiering for compactions that transform data and leveling for identity compactions. Reads speed up because they touch less data: a column-group split cuts the bytes read and deserialized by single-column queries, JSON-to-FlatBuffers made SSTs 34.76% smaller, and a secondary index replaces a full table scan.

## Compared with alternatives

Every catalogued sibling (KVell, MatrixKV, PebblesDB, SplinterDB, Nova-LSM, NuDB, Titan) speeds up the write or key-lookup path. Mycelium is the only one that reshapes data for column-projection and non-key reads, so consider it only when those reads are the bottleneck. For anything you will ship, Titan (large values) and SplinterDB or PebblesDB (write-heavy loads) have public, licensed code.

## Integration

| | |
|---|---|
| **Form** | static lib (a patched RocksDB 8.5.0 fork plus libmycelium, built with CMake, with the shared-library build forced off). In practice a source-drop from an anonymous repo. |
| **Dependencies** | Protobuf (protoc), FlatBuffers (flatc), jsoncpp, Apache Arrow (find_package REQUIRED, but missing from the README's list), snappy, zlib, bzip2, zstd, lz4, gflags, re2. The README also lists Boost, nlohmann-json, RapidJSON and Avro. |
| **Minimum toolchain** | C++17 (-std=c++17 -Werror), CMake 3.16.3+. The paper does not state a compiler. |
| **Platforms** | Linux only as documented: an Ubuntu 20.04 Dockerfile and an Ubuntu 24.04 benchmark image. The CMake hardcodes /usr/lib/x86_64-linux-gnu/libre2.so, so x86-64 Linux is the only tested target. |
| **Thread safety** | Not documented for MymBroker, although the YCSB harness drives one broker from many client threads. The paper says a transformer is locked to one compaction job at a time. TransformEpochTracker is documented as not thread-safe: there is one per SST, owned by its compaction thread. |
| **Drop-in for the baseline** | partial — writes use the normal RocksDB Put path and RocksDB options. Transformed data lives in hidden internal column families that must not be written to directly. Projected reads, row reassembly and index lookups need the MymBroker wrapper, whose calls return int codes. |

## Gotchas

- In the probable repo, MymBroker::Scan ignores begin_key (it calls SeekToFirst) and ignores the column list, and the code that reassembles split rows in Read/Scan is commented out. The paper's Q2-Q7 query paths therefore cannot be reproduced from this harness as shipped.
- Updates across the tree family are not atomic. The manifest edit for the source column family and the edit for each destination family are separate LogAndApply calls. Delete propagation issues a separate Delete per derived column family, and failures are logged and skipped. Crash consistency is not documented.
- Secondary-index keys are field values converted to strings and joined with '%%' and '\$\$\$KEY\$\$\$'. Numeric fields go through std::to_string, so the index sorts lexicographically rather than numerically, and values that contain the separators are ambiguous.
- Error paths print FATAL and call exit(1) instead of returning a status. More than 4 transformers, or transformer and SchemaDescriptor counts that don't match, throw std::runtime_error. The top-level CMakeLists also copies experiment/\*.sh scripts that are not in the repo.

## Known shortcomings

- The 4.25x is Q2 query latency after converting JSON to FlatBuffers during compaction, not throughput; writes cost 10-21% more. Only a probable anonymous code repo (anon-rev-repo/mycelium-anon, no licence) and no link from the paper.
- The paper links no repo; attribution to anon-rev-repo/mycelium-anon is inferred (one squashed commit, 0 stars, no top-level license). Its Scan ignores begin_key and the column list, and split-row reassembly is commented out, so the paper's Q2-Q7 are not reproducible as shipped.
- Column-family tree updates are not atomic (separate LogAndApply per family); delete scans the whole index family; the index misses memtable/L0. Build needs Arrow (not in README), experiment scripts are missing, an x86-64 re2 path is hard-coded, errors exit(1). Paper is inconsistent (32 vs 50 columns per row); 4.25x is only vs a JSON baseline and row queries are slower under split.

## Caveats and trade-offs

The headline metric is read/query latency, not throughput. The 4.25x win partly comes from a data-format change (JSON to FlatBuffers) that the baseline does not get. Row-retrieving queries are slower under the split transform, and the index-query gains compare against RocksDB full scans (not like-for-like). The CPU model, compiler and flags are not stated. The paper is an arXiv preprint with no journal-ref and says its code is 'hidden due to anonymity'. A probable anonymized review repo (github.com/anon-rev-repo/mycelium-anon, created 2026-07-27, 0 stars) describes Mycelium as a RocksDB-based LSM that piggybacks transformations on compaction and includes a YCSB harness under src/test/ycsb. The paper does not link it, it uses newer terminology (WHLSM, LSM-Grove, mRoutines), and it has no top-level license (only the vendored RocksDB licenses under src/lsm).

Query speedup is achieved by embedding data transformations (e.g. cross-column-family merges) into RocksDB's compaction process, which measurably reduces write throughput (16%-20% overhead) -- a direct read/write tradeoff, not a free win; benefit is workload/query-type dependent.

## Maintenance

Research prototype only: an arXiv v1 preprint (June 2025, UC Santa Cruz) whose code is 'hidden due to anonymity'. The probable code is an anonymous review repo (one squashed commit on 2026-07-27, 0 stars, no top-level license) that has already moved to newer names (WHLSM, LSM-Grove, mRoutines), so treat it as a reference, not a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The arXiv paper (v1, no journal-ref, 'source code is available but hidden due to anonymity') reports first-party YCSB results against RocksDB baselines. The CPU model, compiler and flags are not stated (only '2 CPUs, 16 cores each at 3.00 GHz'), so it cannot be A, and it is not shown to be peer-reviewed, so it cannot be B.
- **Verifier notes:** The numbers are on the page and the RocksDB comparison is real, so the tier C claim holds. The record's metric field says 'throughput' but the headline is latency; metric is not a correctable field, so the orchestrator may want to fix it by hand. repo_url could plausibly be set to https://github.com/anon-rev-repo/mycelium-anon (anonymous, unlicensed), but the paper does not link it, so attribution is inferred from its name and description.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `has_code`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2506.08923>
  - <https://arxiv.org/pdf/2506.08923>
  - <https://github.com/anon-rev-repo/mycelium-anon>
- **Sources the enricher read:**
  - <https://arxiv.org/abs/2506.08923>
  - <https://arxiv.org/pdf/2506.08923>
  - <https://export.arxiv.org/api/query?id_list=2506.08923>
  - <https://github.com/anon-rev-repo/mycelium-anon>
  - <https://github.com/anon-rev-repo/mycelium-anon/commits/main>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/README.md>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/CMakeLists.txt>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/cmake/modules/BuildRocksDB.cmake>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/Dockerfile>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/ddl/flat/row.fbs>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/ddl/proto/data.proto>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/lib_transform/include/mycelium/transformer.h>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/lib_transform/include/mycelium/compaction_hook.h>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/lib_transform/include/mycelium/transform_epoch_tracker.h>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/lib_transform/src/transformer/augment/augmenter.cc>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/lib_transform/src/transformer/convert/converter.cc>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/lsm/include/rocksdb/mym_broker.h>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/lsm/db/mym_broker.cc>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/lsm/db/compaction/compaction_job.cc>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/lsm/CMakeLists.txt>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/lsm/include/rocksdb/version.h>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/test/ycsb/ReadMe.md>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/test/ycsb/run_mycelium.sh>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/test/ycsb/Dockerfile.bench>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/test/ycsb/db/test_splitting.cc>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/test/ycsb/db/test_converting.cc>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/test/ycsb/db/test_rocks_db.cc>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/test/mycelium/test_level_eligibility.cc>
  - <https://github.com/anon-rev-repo/mycelium-anon/blob/main/src/test/mycelium/test_bottommost_compaction.cc>
  - <https://hn.algolia.com/api/v1/search?query=Mycelium%20Transformation-Embedded%20LSM>
  - <https://hn.algolia.com/api/v1/search?query=TE-LSM%20compaction>
  - https://api.semanticscholar.org/graph/v1/paper/arXiv:2506.08923 (HTTP 429, no data)
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `paper:mycelium-te-lsm`) · [data/wave6/enrich/raw/paper_mycelium_te_lsm.json](../../../data/wave6/enrich/raw/paper_mycelium_te_lsm.json) (enrichment confidence 0.5)

</details>
