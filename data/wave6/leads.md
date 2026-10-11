# Wave 6 leads for a seed pass

Candidates surfaced by verifiers and enrichers, not yet in any wave's records.

- RocksDB integrated BlobDB (enable_blob_files, https://github.com/facebook/rocksdb): upstream key-value separation, the same technique as Titan with fuller API support. Found by the Titan enricher. Needs a record against stock RocksDB (leveled, no blob files).
- FastPLBF (https://github.com/atsukisato/FastPLBF): runnable MIT reimplementation of PLBF by the CLBF authors (NeurIPS 2023). Found by the PLBF enricher.
- NNG (https://github.com/nanomsg/nng): nanomsg's upstream-recommended successor. Found by the nanomsg enricher.

Seeded as w6-seed-leads (RocksDB integrated BlobDB, FastPLBF, NNG) on 2026-09-26.

For a later wave (not storage-and-data):
- pgrust OLTP (https://github.com/malisper/pgrust): a Rust reimplementation of PostgreSQL with a real head-to-head OLTP result of 1.25-1.40x vs PostgreSQL 18.3 in its own kit. Its columnar ClickBench claim was rejected in wave 6 (benchmark-specific kernels, removed from ClickBench).
- fjall (fjall-rs/fjall): Rust LSM engine; in the redb table batch writes 353 vs RocksDB 451 ms and removals 6004 vs 6900 ms; README has no own benchmarks. Not catalogued (enricher lead, 2026-10-07).
- TickTock (ytyou/ticktock): C++ time-series DB, GPL, 89 stars; 3.2M points/s in its own IoTDB-benchmark shootout (first-party). Not catalogued (enricher lead, 2026-10-07).
- IOWOW (https://github.com/Softmotions/iowow): EJDB2's storage engine, claims to beat LMDB, LevelDB and Kyoto Cabinet; not catalogued (w6-mine-c backfill, 2026-10-07).
- sqlpp11 (https://github.com/rbock/sqlpp11): PR #520 hand date parser vs its own std::regex parser (GCC -O3 0.00733141 s vs 0.923286 s); self-comparison, no record (w6-mine-g, 2026-10-11).
