# Infinity

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Text search and indexing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> C++ AI-native search database for RAG; vendor run shows 10x Elasticsearch's full-text QPS on 33M Wikipedia documents.

| | |
|---|---|
| **Beats** | Elasticsearch 8.13.4 (full-text and dense vector search); Qdrant 1.9.2 also measured |
| **Claimed result** | Enwiki full-text (33M documents, 16 Python clients): 13731 QPS vs 1340 for Elasticsearch (10.2x, derived from page data) and 179 for Quickwit; P95 latency 1.37 ms vs 14.75 ms (10.8x, derived); insert and build index 1562 s vs 2289 s (1.5x, derived); memory 10.0 GB vs 21.0 GB. SIFT1M (top 100): 16320 QPS vs 934 for Elasticsearch (17.5x, derived) and 1303 for Qdrant (12.5x, derived) at recall 0.973 vs 0.992 and 0.979. GIST1M: 2200 QPS vs 305 and 339 (7.2x and 6.5x, derived) at recall 0.946 vs 0.885 and 0.947. Infinity is slower than Qdrant at insert and index build (74 s vs 46 s on SIFT1M, 463 s vs 366 s on GIST1M) and uses more disk on SIFT1M (792 MB vs 418 MB). |
| **Workload** | Repo benchmark doc (docs/references/benchmark.md): 100,000 generated full-text OR queries (top 10) on 33M English Wikipedia documents with 16 Python clients, and L2 top-100 vector search on SIFT1M (10,000 queries) and GIST1M (1,000 queries), reporting QPS, recall, P95 latency, index build time, memory and disk; the vector tables do not state the client count (the doc's commands use 16). |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-13500H, 16 vCPU, 32 GB RAM, 1 TB disk, OpenSUSE Tumbleweed x86_64 |
| **Compiler and flags** | Not stated: all engines run from Docker images (elasticsearch:8.13.4 with ES_JAVA_OPTS=-Xms16384m -Xmx32000m, qdrant/qdrant:v1.9.2, quickwit/quickwit:0.8.1, infiniflow/infinity:nightly); no build flags for Infinity. |
| **Adoption** | about 4.7k stars |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/infiniflow/infinity) · [benchmark](https://raw.githubusercontent.com/infiniflow/infinity/main/docs/references/benchmark.md) |

## Verdict

The Infinity team ran its own Python driver on one Intel Core i5-13500H (16 vCPU, 32 GB, OpenSUSE Tumbleweed) with every engine in Docker (Elasticsearch 8.13.4 with a 32 GB max heap, Qdrant 1.9.2, Quickwit 0.8.1, Infinity labelled v0.2.0 but started from the floating nightly image): 13,731 vs 1,340 QPS (10.2x) and 1.37 vs 14.75 ms P95 for 100,000 top-10 OR queries on 33M Enwiki documents, 16,320 vs 934 (Elasticsearch) and 1,303 (Qdrant) QPS on SIFT1M top-100 at lower recall (0.973 vs 0.992 and 0.979, LVQ 8-bit vs float32), and 2,200 vs 305 and 339 QPS on GIST1M. No compiler flags are given for any engine, and the harness flaws listed under gotchas mean the recall column is not reproducible from the repo.

## Use it when

- RAG retrieval that needs BM25, dense and sparse vector search and reranking in one engine on one machine, for example behind RAGFlow.
- High-QPS top-10 keyword OR queries over tens of millions of short documents, where Elasticsearch's memory footprint matters (10.0 GB vs 21.0 GB in the vendor Enwiki run).
- Million-scale ANN search where recall around 0.95-0.97 at top-100 is acceptable in exchange for 7-17x the QPS of Elasticsearch 8.13 in the vendor run.
- Python-first stacks that want a single-binary server or an embedded Python module instead of a JVM cluster.

## Skip it when

- When top-100 recall must exceed about 0.98 on SIFT-like data: Elasticsearch reached 0.992 and Qdrant 0.979 against Infinity's 0.973 with its LVQ-quantised index.
- When index build time or disk footprint dominate: Qdrant built SIFT1M in 46 s vs 74 s and GIST1M in 366 s vs 463 s, and used 418 MB vs 792 MB of disk on SIFT1M.
- Write-heavy concurrent DELETE plus INSERT ingestion: open issue #3418 (v0.7.0-dev5) reports a delete-conflict livelock, compaction replaying one timestamp for hours with memory growing from 8.5 to 14.8 GiB, and leaked sessions exhausting connections.
- When you need Elasticsearch API compatibility, aggregations or a multi-node cluster; none is described in the README.
- On x86-64 CPUs without AVX2 (the README requires it), or when you want a C++ library to link rather than a server to operate.

## How it is fast

Full-text search runs over its own inverted index with block-max WAND (blockmax_wand_iterator), a batch OR iterator and a BM25 ranker, so top-k OR queries skip posting blocks whose maximum score cannot enter the heap. Dense search uses HNSW graphs whose vectors can be stored with LVQ (locally-adaptive 8-bit scalar quantization) or RaBitQ, scored with runtime-dispatched SIMD int8 and float L2/IP kernels (HNSW_I8L2_64 and similar). The server is C++23 with modules, built at -O3 in Release.

## Compared with alternatives

Pick Infinity over Manticore Search, the other server-style sibling that beats Elasticsearch, when you need dense, sparse and tensor vector search fused with BM25 in one engine for RAG; pick Tantivy, SeekStorm or PISA when you want an embeddable search library with independent search-benchmark-game numbers rather than a server measured only by its vendor.

## Integration

| | |
|---|---|
| **Form** | server binary (Docker image infiniflow/infinity or standalone) with Python, HTTP and PostgreSQL-wire clients; embedded Python module |
| **Dependencies** | building from source needs vcpkg packages including Abseil, Arrow/Parquet, Boost.Asio, RocksDB, Thrift, oatpp, simdjson, re2, CRoaring, pcre2, spdlog and OpenSSL; client side needs Python 3.11+ and infinity-sdk |
| **Minimum toolchain** | Clang 20+, CMake 4.0.3+, Ninja, C++23 with modules and import std (to build the server); Python 3.11+ for the SDK |
| **Platforms** | x86-64 with AVX2 on Linux (glibc 2.17+), macOS, Windows 10+ via WSL/WSL2; ARM64 builds go through SIMDe |
| **Thread safety** | The server serves many concurrent clients (connection_pool_size 128 by default); the benchmark code notes the SDK socket is unsafe to share between workers, so open one connection per process or thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the checked-in recall code compares results against expected_result[i][1:], dropping each query's true nearest neighbour and capping top-100 recall at 0.99, and it cannot score Elasticsearch's vector results at all (they are (id, score) tuples, so `x >> 32` raises a TypeError). Elasticsearch's published 0.992 is above that cap, qdrant_gist.json has no ground_truth_path, and there is no elasticsearch_gist.json, so run.py refuses an Elasticsearch GIST run; the recall column and the Elasticsearch GIST row cannot be reproduced from the repo.
- Harness asymmetry on Enwiki: the Elasticsearch client sends a plain match query without `_source` filtering or track_total_hits:false, so every response carries the full source of 10 documents and Elasticsearch counts hits up to its default 10,000 before pruning, while the Infinity client asks only for _row_id and _score over Thrift; Elasticsearch is configured with 5 shards and all 16 Python client processes share the 16-vCPU host with the server.
- The QPS mode replays random queries from the 100,000-query set for 30 minutes, so each query repeats about 250 times at Infinity's rate; Infinity has a result_cache option (off in conf/infinity_conf.toml) and the Elasticsearch config disables its request cache, so check the cache setting of the image you benchmark.
- Operational bugs open as of 2026-10: WAL files are never recycled because WalFile::RecycleWalFile is commented out (#3435, 54,000 files on one instance, and manual cleanup segfaulted on restart), WAL replay crashes in InitPhase2 (#3497), and an unrecovered append aborts the server (#3434); a block-max WAND crash on queries with 15+ terms was fixed only on 2026-09-21.

## Known shortcomings

- First-party benchmark on a Docker nightly image (build unpinned, no compiler or flags). Its LVQ 8-bit index is compared with float32 indexes at lower recall; clients use HTTP/JSON for Elasticsearch and Qdrant but Thrift for Infinity; the Elasticsearch heap equals machine RAM. Index build is slower than Qdrant. Filed under text-search-and-indexing (Elasticsearch is the baseline).
- Enricher: the benchmark's recall code compares against expected_result[i][1:], dropping the true nearest neighbour, so top-100 recall caps at 0.99 (Elasticsearch's published 0.992 is above that cap) and raises TypeError on Elasticsearch's (id, score) tuples; qdrant_gist.json has no ground_truth_path and elasticsearch_gist.json does not exist, so the recall column and the Elasticsearch GIST row cannot be reproduced. The Elasticsearch Enwiki query returns full _source and does not set track_total_hits:false while the Infinity client asks only _row_id and _score over Thrift; QPS mode repeats each query about 250 times. Open crash issues #3435 (WAL files never recycled), #3497, #3434, #3418.

## Caveats and trade-offs

First-party benchmark by the Infinity authors on one laptop-class CPU (i5-13500H, 32 GB). The table names Infinity v0.2.0 (about 2024) but the run command uses the floating infiniflow/infinity:nightly image and the current release is 0.7.x, so the measured build is not pinned. The vector comparison is not like for like: Infinity's SIFT config builds HNSW (M 16, ef_construction 200, ef 200) with LVQ 8-bit encoding, while Elasticsearch and Qdrant index float32 vectors with default search settings (Elasticsearch num_candidates 200), and Infinity's SIFT1M recall (0.973) is below both. Queries come from Python clients that talk HTTP/JSON to Elasticsearch and Qdrant (the Qdrant client does not enable gRPC) but Thrift to Infinity, so client-side serialisation may account for part of the QPS gap. Elasticsearch gets -Xmx32000m on a 32 GB machine, leaving little memory for the OS page cache Lucene relies on; Lucene itself is not measured separately. Infinity loses to Qdrant on vector index build time and SIFT1M disk use. None of the category's listed baselines (B-tree/LSM in RocksDB, LevelDB, LMDB, SQLite; learned indexes) is measured. The README headline claims (0.1 ms vector latency and 15K+ QPS; 1 ms and 12K+ QPS full-text on 33M documents) are in the same range as the doc table. [retier] First-party benchmark on a Docker nightly image (build unpinned, no compiler or flags). The LVQ 8-bit index is compared with float32 indexes at lower recall, and the recall column cannot be reproduced: the recall code compares against expected_result[i][1:], dropping the true nearest neighbour so top-100 recall caps at 0.99 (Elasticsearch's published 0.992 exceeds the cap) and raises TypeError on Elasticsearch's (id, score) tuples; qdrant_gist.json has no ground_truth_path and elasticsearch_gist.json does not exist. Clients are asymmetric: Elasticsearch and Qdrant over HTTP/JSON (the Enwiki query returns full _source and leaves track_total_hits on) vs Infinity over Thrift asking only _row_id and _score; QPS mode repeats each query about 250 times; the Elasticsearch heap equals machine RAM; index build is slower than Qdrant. Open crash issues #3435, #3497, #3434, #3418.

Single-node AI-native database whose index and engine are specialised for hybrid search; lower recall than Elasticsearch on SIFT1M (0.973 vs 0.992); needs AVX2 on x86_64; time to build the vector index is slower than Qdrant on both datasets (74 s vs 46 s on SIFT1M insert plus build, 463 s vs 366 s on GIST1M); Elasticsearch uses more memory (21.0 GB vs 10.0 GB on Enwiki) but Infinity needs about the same vCPU.

## Maintenance

Actively developed (last commit 2026-09-23, SDK 0.7.3), Apache-2.0, about 4.7k stars with 98 open issues including a stream of September 2026 SDK and WAL crash reports; usable as a server for RAG workloads, not as a library to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party benchmark by the Infinity authors with a public driver (python/benchmark/run.py plus clients/ and configs/) and a stated CPU (Intel Core i5-13500H), but no compiler or flags: every engine runs from a Docker image, Infinity from the floating infiniflow/infinity:nightly tag while the table says v0.2.0. Missing compiler and flags fails A, and first-party numbers with partial methodology are C.
- **Verifier notes:** Numbers match the doc table, but tier A was not justified: no compiler or flags, Docker nightly image, first-party, so C. Shortcomings to record: first-party, unpinned nightly build, LVQ-quantised index vs float32 competitors at lower recall, HTTP/JSON vs Thrift client protocols, Elasticsearch heap set to machine RAM, slower than Qdrant at index build; baseline_in_list set to false because Elasticsearch is not an indexes-category baseline, and the full-text comparison against Elasticsearch (Lucene) fits text-search-and-indexing better than indexes, so consider a category override. Metadata checks out: Apache-2.0, about 4.7k stars, last commit 2026-09-23, active.
- **Fields the verifier corrected:** `baseline_in_list`, `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party benchmark (verifier downgrade A to C); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/docs/references/benchmark.md>
  - <https://github.com/infiniflow/infinity>
  - <https://github.com/infiniflow/infinity/tree/main/python/benchmark>
  - <https://github.com/infiniflow/infinity/commits/main.atom>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/clients/qdrant_client.py>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/clients/elasticsearch_client.py>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/clients/infinity_client.py>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/configs/qdrant_sift.json>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/configs/elasticsearch_sift.json>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/configs/infinity_sift.json>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/configs/infinity_enwiki.json>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/configs/elasticsearch_enwiki.json>
- **Sources the enricher read:**
  - <https://github.com/infiniflow/infinity>
  - <https://github.com/infiniflow/infinity/commits/main.atom>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/README.md>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/docs/references/benchmark.md>
  - <https://github.com/infiniflow/infinity/commits/main/docs/references/benchmark.md.atom>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/README.md>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/run.py>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/clients/base_client.py>
  - <https://github.com/infiniflow/infinity/commits/main/python/benchmark/clients/base_client.py.atom>
  - <https://github.com/infiniflow/infinity/blame/main/python/benchmark/clients/base_client.py>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/clients/infinity_client.py>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/clients/elasticsearch_client.py>
  - <https://github.com/infiniflow/infinity/commits/main/python/benchmark/clients/elasticsearch_client.py.atom>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/clients/qdrant_client.py>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/clients/quickwit_client.py>
  - <https://github.com/infiniflow/infinity/tree/main/python/benchmark/configs>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/configs/infinity_sift.json>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/configs/infinity_gist.json>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/configs/infinity_enwiki.json>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/configs/elasticsearch_sift.json>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/configs/elasticsearch_enwiki.json>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/configs/elasticsearch_gist.json>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/configs/qdrant_sift.json>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/python/benchmark/configs/qdrant_gist.json>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/conf/infinity_conf.toml>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/infiniflow/infinity/main/src/storage/knn_index/knn_hnsw/dist_func_l2.cppm>
  - <https://github.com/infiniflow/infinity/tree/main/src/storage/invertedindex/search>
  - <https://github.com/infiniflow/infinity/tree/main/src/storage/knn_index/knn_hnsw>
  - <https://github.com/infiniflow/infinity/issues?q=is%3Aissue+is%3Aopen+crash>
  - <https://github.com/infiniflow/infinity/issues/3435>
  - <https://github.com/infiniflow/infinity/issues/3418>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/infiniflow/infinity`) · [data/wave6/enrich/raw/github_com_infiniflow_infinity.json](../../../data/wave6/enrich/raw/github_com_infiniflow_infinity.json) (enrichment confidence 0.75)

</details>
