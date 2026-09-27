# Wave 6 leads for a seed pass

Candidates surfaced by verifiers and enrichers, not yet in any wave's records.

- RocksDB integrated BlobDB (enable_blob_files, https://github.com/facebook/rocksdb): upstream key-value separation, the same technique as Titan with fuller API support. Found by the Titan enricher. Needs a record against stock RocksDB (leveled, no blob files).
- FastPLBF (https://github.com/atsukisato/FastPLBF): runnable MIT reimplementation of PLBF by the CLBF authors (NeurIPS 2023). Found by the PLBF enricher.
- NNG (https://github.com/nanomsg/nng): nanomsg's upstream-recommended successor. Found by the nanomsg enricher.

Seeded as w6-seed-leads (RocksDB integrated BlobDB, FastPLBF, NNG) on 2026-09-26.
