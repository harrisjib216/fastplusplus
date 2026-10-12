# Lance

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust columnar file and table format for AI/ML data, built for random row access where default-configured Parquet is slow.

| | |
|---|---|
| **Beats** | Apache Parquet (the parquet-rs Rust crate, tuned, in the paper). Iceberg is named only in the README/homepage marketing and is not benchmarked in the paper. |
| **Claimed result** | README/homepage marketing: '100x faster random access than Parquet or Iceberg'. The README's 'Vs. parquet' section attributes this to a preliminary Oxford Pet dataset test ('For batched random access, Lance is 100x better than both parquet and raw files'). The paper (arXiv 2504.15247) states instead that Parquet 'when configured correctly, can achieve over 60x better random access performance than default settings' (parquet-rs default 5,500 rows/s vs optimized 350,000 rows/s on small scalars). It also says the Lance 2.1 encoding 'generally tie[s] or beat[s] Parquet' in random access without the scan-performance and RAM trade-offs, but gives no single speedup figure against tuned Parquet. |
| **Workload** | Paper (arXiv 2504.15247): parallel 'take' operations of 256 random indices from a single column, run for 10 s and reported as rows fetched per second, over 8 data types (UInt64 scalars through 100 KiB image lists) with 10% nulls. Small types use about 1 billion rows. Parquet uses 8 KiB pages with compression and dictionary encoding off. Full-scan, compression-ratio and struct-packing experiments are also included. All runs are on local NVMe. |
| **Metric** | latency |
| **Hardware** | Samsung 970 EVO Plus 2TB NVMe drive (measured 850K random 4KiB reads/s, 3,400 MiB/s) with an Intel i7-10700K CPU (8 cores/16 threads), per the paper |
| **Adoption** | 7.1k stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/lance-format/lance) · [benchmark](https://arxiv.org/abs/2504.15247) |

## Verdict

The LanceDB authors' arXiv paper (2504.15247, v1 April 2025, no journal reference) ran parallel 256-index takes for 10 s over random data with 10% nulls (about 1B rows for small types) on an i7-10700K with a Samsung 970 EVO Plus NVMe. Against parquet-rs v54 tuned to 8 KiB pages without compression or dictionary, Lance 2.1 'generally tie[s] or beat[s]' Parquet in rows/s with no single ratio given, and slightly trails Lance 2.0 on simple scalars. The 100x figure appears only in the README's preliminary Oxford Pet table, which gives no methodology.

## Use it when

- Fetching scattered rows by index or row id in batches of tens to hundreds from large tables on local NVMe or an NVMe cache: materializing search results, or shuffled training sampling through a torch `__getitems__` batch hook.
- Tables that mix small scalars with large values (768-dim float32 embeddings of about 3 KiB, images, long text). Here Parquet with tiny pages would need about 20 bytes of page-offset-index RAM per page, or roughly 20 GiB per billion one-value pages per the paper, while full-zip needs no search cache.
- Point reads into nested List/Struct columns: with the 2.1+ encodings, extra nesting levels add no IOPs, unlike Arrow-IPC-style layouts, which need one more IOP per validity or offsets buffer.
- When you want vector/full-text/scalar indexes, versioning and cheap column backfills in the storage layer itself, used from Python alongside PyArrow, DuckDB or Polars.

## Skip it when

- Pure OLAP scans and aggregations. The README's own preliminary table has Lance slightly slower than Parquet on analytics (2.7 vs 2.3 ms, 2.8 vs 2.5 ms), and the paper claims only scan performance 'equal to or greater than' Parquet 'in nearly all cases'.
- One-row-at-a-time lookups or key-value-store latency targets. Issue #3983 (Lance 0.29, 54 KB values) measured point lookups 13x slower than LMDB, and 223x slower again with zstd. Maintainers blame per-take decoder/scheduler setup, and an open issue (#5068) traces about 60% of random-access latency to I/O-scheduler task overhead.
- Interchange with the Parquet/Iceberg ecosystem. Lance files are not Parquet, so every reader needs a Lance library or connector, and older Lance releases cannot read newer data_storage_versions.
- Risk-averse production writes without testing. Recent data-corruption bugs include compaction corrupting files (#8501, fixed Aug 2026) and sub-schema merge_insert corruption on format 2.2 (#6338, fixed); #8282 (merge_insert ordering invariant) is still open. pylance still carries the 'Development Status :: 3 - Alpha' classifier, and the repo shows about 1,281 open issues and PRs.
- macOS on Intel: pylance 12.0.0 ships wheels only for macOS arm64, manylinux x86-64/aarch64 and Windows x86-64, so other platforms must build the Rust crate from source.

## How it is fast

The paper calls the idea 'adaptive structural encoding': each column page picks one of two layouts. Small values use mini-block: data is cut into power-of-two-count chunks of about 4-8 KiB (max 32 KiB) with Parquet-like repetition/definition levels, and 2 bytes of per-chunk metadata stay in an in-memory 'search cache', so a random read is one small chunk read plus decode. Large values use full-zip: rep/def levels are bit-packed into a 1-4 byte control word and zipped row-major in front of each value's transparently compressed bytes (bit-packing, FSST, per-value LZ4/zstd), with a repetition index of offsets, so a fixed-width value costs 1 IOP and a variable-width one 2 IOPs however deep the nesting. Values of about 1 MiB and up can go to an out-of-line blob layout. Dictionaries sit in the search cache, struct packing is opt-in, and a Linux io_uring reader is available via the `file+uring://` URI scheme.

## Compared with alternatives

Pick Lance over Vortex (the other Parquet replacement here, catalogued on scan/write throughput ratios) when the workload is row fetches by index, vector or full-text search, and versioned AI/ML tables rather than raw scan and compression speed. Lance is storage, not a query engine, so it complements chDB, Velox or StarRocks rather than competing with them.

## Integration

| | |
|---|---|
| **Form** | crate (`lance` on crates.io); also the `pylance` Python wheel (PyO3, abi3) and Java JNI bindings |
| **Dependencies** | arrow-rs 58, DataFusion 54, object_store 0.14 and OpenDAL, tokio async runtime, AWS SDK (S3, DynamoDB), io-uring (Linux), plus many more workspace crates. Python: pyarrow&gt;=14, numpy&gt;=1.22, lance-namespace. |
| **Minimum toolchain** | Rust 1.91 (workspace rust-version, edition 2024; the repo pins 1.97.0 for development); Python &gt;=3.10 |
| **Platforms** | Linux x86-64 and aarch64, macOS arm64, Windows x86-64 (pylance wheels). The io_uring reader is Linux-only (kernel 5.1+) and falls back to the normal local reader elsewhere. |
| **Thread safety** | Documented as thread-safe: APIs can be called concurrently and tables shared across threads. Concurrent writers use optimistic concurrency with automatic retries on conflict. There are separate I/O (8 threads local, 64 cloud; LANCE_IO_THREADS) and compute (LANCE_CPU_THREADS) pools. |
| **Drop-in for the baseline** | partial — not a Parquet reader/writer, so data must be converted; the Python dataset implements pyarrow.dataset.Dataset, so code that consumes PyArrow datasets (pandas, DuckDB, Polars) keeps working |

## Gotchas

- The '100x vs Parquet' headline is a preliminary README table (Oxford Pet 'filter data': 3.9 ms Lance vs 553.7 ms Parquet) with no hardware, versions or Parquet settings. The paper shows parquet-rs going from 5,500 to 350,000 rows/s (over 60x) just by tuning it (8 KiB pages, compression and dictionary off, page offset index), and dictionary encoding alone dropped Parquet to 2% of ideal. Most of the headline gap is Parquet configuration.
- Format versions matter. The code now defaults new datasets to 2.2, while 2.3/'next' is unstable with no compatibility guarantee, and the paper measured 2.1 while it was still experimental. Newer files are unreadable by older Lance, and one encoder fix (FixedSizeList with all-null inner values) makes new files require reader 11.1.0 or later; older readers panic on them instead of returning an error. Pin data_storage_version in mixed-version deployments.
- Memory defaults are large: 1 GiB metadata cache, 6 GiB index cache, and a 2 GB io_buffer_size per scan, with scans able to use about 2x io_buffer_size plus batch_size x compute threads. Caches are not shared between separately opened tables, so open a table once and share it, or pass a common session.
- The paper and current spec differ: the full-zip cutoff is 128 bytes in the paper but 256 bytes in today's encoding doc. Also, 2.1 trailed 2.0 on simple scalars because a whole mini-block must be decoded per value, and the fix that exploits transparent encodings in mini-blocks (#5066) is still open.

## Known shortcomings

- The '100x faster than Parquet' is a preliminary README test (Oxford Pet); in the paper tuned Parquet is 60x faster than default Parquet and Lance only ties or beats it. VLDB'25 venue unconfirmed; Iceberg not tested.
- Slower than Parquet on the README's own analytics rows (2.7 vs 2.3 ms); point lookups are 13x slower than LMDB (#3983); I/O scheduler overhead issue #5068 open. Format churn: default is now 2.2 while the paper measured 2.1, and older readers (&lt;11.1.0) panic on some new files. Corruption bugs #8501 and #6338 fixed, #8282 open; pylance is labelled Alpha; no macOS x86 wheel.

## Caveats and trade-offs

The '100x faster than Parquet or Iceberg' figure comes from README/homepage copy, backed only by a 'preliminary' Oxford Pet dataset test without methodology. The paper, written by LanceDB employees, undercuts it by showing tuned Parquet recovers over 60x versus default Parquet, and it claims only tie-or-beat against tuned Parquet. Lance 2.1 slightly underperforms Lance 2.0 on simple scalar types. The project homepage says the paper was published at VLDB 2025, but arXiv v1 carries no journal reference and a crossref title search found no match, so peer review is unconfirmed. The paper mentions reproduction scripts but gives no link. The paper's metric is throughput (rows/s) rather than latency.

Rust-native with Python/Java bindings (pylance); optimized for AI/ML lakehouse workloads (multimodal blobs, vector indexes, data versioning) rather than general OLAP scans; file format still evolving under a data_storage_version compatibility contract.

## Maintenance

Very active (commits daily, 7.1k stars, Apache-2.0; crate and pylance 12.0.0 released 2026-09-17, 13.0 betas on main), but releases are frequent, pylance still calls itself Alpha, and only stable data_storage_versions carry a read-compatibility promise.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The arXiv paper by LanceDB authors compares Lance 2.1 random access against tuned parquet-rs on stated hardware (i7-10700K, Samsung 970 EVO Plus). In the text it reports only that Lance 'generally tie[s] or beat[s] Parquet', with no stated ratio. The 100x headline comes only from first-party README/homepage copy without methodology. Peer review (VLDB '25) is claimed by the project homepage but could not be confirmed, and neither compiler/flags nor a linked script path is given, so the tier is C.
- **Verifier notes:** Metadata is confirmed: Apache-2.0, 7,117 stars, last commit 2026-09-26, not a fork. The record's 'metric: latency' is really throughput (rows/s) in the paper; metric is not a correctable field. The tier stays C.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `workload`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2504.15247>
  - <https://arxiv.org/pdf/2504.15247>
  - <https://github.com/lance-format/lance>
  - <https://github.com/lance-format/lance/blob/main/README.md>
  - <https://raw.githubusercontent.com/lance-format/lance/main/docs/theme/home.html>
  - <https://api.crossref.org/works?query.bibliographic=Lance%3A+Efficient+Random+Access+in+Columnar+Storage+through+Adaptive+Structural+Encodings&rows=5>
- **Sources the enricher read:**
  - <https://github.com/lance-format/lance>
  - <https://github.com/lance-format/lance/blob/main/README.md>
  - <https://github.com/lance-format/lance/blob/main/Cargo.toml>
  - <https://github.com/lance-format/lance/blob/main/rust-toolchain.toml>
  - <https://github.com/lance-format/lance/blob/main/python/pyproject.toml>
  - <https://github.com/lance-format/lance/blob/main/docs/src/format/file/versioning.md>
  - <https://github.com/lance-format/lance/blob/main/docs/src/format/file/encoding.md>
  - <https://github.com/lance-format/lance/blob/main/docs/src/guide/performance.md>
  - <https://github.com/lance-format/lance/blob/main/rust/lance-io/src/uring.rs>
  - <https://github.com/lance-format/lance/blob/main/rust/lance-file/src/version.rs>
  - <https://github.com/lance-format/lance/blob/main/rust/lance/src/dataset.rs>
  - <https://raw.githubusercontent.com/lance-format/lance/main/docs/src/images/lance_perf.png>
  - <https://github.com/lance-format/lance/issues/3981>
  - <https://github.com/lance-format/lance/issues/3983>
  - <https://github.com/lance-format/lance/issues/4374>
  - <https://github.com/lance-format/lance/issues/5066>
  - <https://github.com/lance-format/lance/issues/5067>
  - <https://github.com/lance-format/lance/issues/5068>
  - <https://github.com/lance-format/lance/issues/5069>
  - <https://github.com/lance-format/lance/issues?q=data+corruption>
  - <https://github.com/lance-format/lance/issues?q=random+access+performance>
  - <https://arxiv.org/abs/2504.15247>
  - <https://arxiv.org/pdf/2504.15247>
  - <https://export.arxiv.org/api/query?id_list=2504.15247>
  - <https://dblp.org/search/publ/api?q=adaptive+structural+encodings+lance&format=json>
  - <https://pypi.org/pypi/pylance/json>
  - <https://crates.io/api/v1/crates/lance>
  - <https://hn.algolia.com/api/v1/search?query=lancedb%20lance%20parquet&tags=story>
  - <https://hn.algolia.com/api/v1/items/36144450>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/lance-format/lance`) · [data/wave6/enrich/raw/github_com_lance_format_lance.json](../../../data/wave6/enrich/raw/github_com_lance_format_lance.json) (enrichment confidence 0.8)

</details>
