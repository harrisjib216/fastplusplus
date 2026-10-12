# Manticore Search

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Text search and indexing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-3.0` · 🟢 active

> SQL/HTTP full-text and analytics search database, C++ core, positioned as a faster Elasticsearch alternative.

| | |
|---|---|
| **Beats** | Elasticsearch |
| **Claimed result** | Manticore blog (Jul 25 2022) citing db-benchmarks.com: 4x faster than tuned Elasticsearch on the 1.7B-doc taxi test; 15x faster on the 1.1M Hacker News comments test; 22x faster on the 10M nginx-log test; 25x faster ingestion of the 1.7B-doc taxi dataset (1h08m vs 28h33m via Logstash). For direct loading of 50M random docs, the page concludes 'Manticore is 2x faster': sharded Manticore without binlog did 894,856 docs/s vs sharded Elasticsearch 416,788 docs/s (plus a 13.5 s refresh). Unsharded, default Elasticsearch was 21% faster (280,519 vs 231,742 docs/s); Manticore was 43% faster only when Elasticsearch used refresh=1 (162,614 docs/s). |
| **Workload** | Independent db-benchmarks.com suite: full-text/analytics queries over a 1.7-billion-row taxi dataset (32-core SSD server), 1.1M curated Hacker News comments, and 10M nginx log lines; plus bulk-load of 1.7B docs via Logstash vs Manticore's built-in indexer, and direct-load throughput of 50M random documents |
| **Metric** | latency |
| **Hardware** | 32-core server with SSD (1.7B taxi ingestion test); server with 16 physical cores plus hyper-threading (50M direct-load test); CPU model not stated on the page |
| **Adoption** | 12k stars |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/manticoresoftware/manticoresearch) · [benchmark](https://manticoresearch.com/blog/manticore-alternative-to-elasticsearch/) |

## Verdict

Vendor blog (Manticore, Jul 2022) benchmarked Manticore 5.0.0-5.0.2 against Elasticsearch 7.15.2/8.3.2 on a 32-core SSD server (CPU model and compiler flags unstated): 4x faster on a 1.7B-row taxi dataset, 15x on 1.1M Hacker News comments, 22x on 10M nginx log lines, 25x faster bulk-load of the 1.7B-doc set (1h08m vs 28h33m via Logstash), and roughly 2x higher direct-load throughput for 50M docs (894,856 vs 416,788 docs/s, sharded configs) — though unsharded default Elasticsearch was actually 21% faster in that same test. The db-benchmarks.com suite behind these numbers is maintained by the Manticore team itself.

## Use it when

- Log/analytics workloads (e.g. nginx logs, time-series) where columnar storage plus the cost-based optimizer avoid JVM/Lucene overhead
- Teams that want SQL over full-text/analytics search rather than learning Elasticsearch's Query DSL, especially existing MySQL-protocol tooling
- Ingest-heavy pipelines where bulk-load throughput matters more than incremental refresh latency
- Resource-constrained deployments: README states \~40MB RSS for an empty instance
- Single query needing both full-text and vector/KNN retrieval (hybrid search) without a separate vector DB

## Skip it when

- Need Elasticsearch's mature aggregation framework, Query DSL, or its large ecosystem of plugins/native Kibana support
- Can't accept GPL-3.0 copyleft for embedding into proprietary systems (vs Elasticsearch's SSPL/Elastic license)
- Require strict ACID guarantees: README states Manticore is 'not fully ACID-compliant', offering only isolated transactions and binary logging
- Basing a purchase decision on the cited speedup numbers: the db-benchmarks.com suite behind them is maintained by the same Manticore team, so treat 4x/15x/22x/25x/2x figures as vendor-reported, not independent
- Need multi-master replication stronger than Galera-based 'virtually synchronous' replication provides

## How it is fast

Query execution is multi-threaded across all CPU cores with a cost-based optimizer choosing execution plans from indexed-data statistics. It offers both row-wise storage (faster, more RAM) and a separate columnar storage engine (Manticore Columnar Library) for datasets too large for RAM. Automatic secondary indexes use a PGM-index (Piecewise Geometric Model) for key-to-location mapping instead of classic B-trees. The core inverted-index/search engine descends from the Sphinx search engine, rewritten and extended in C++17.

## Compared with alternatives

The sibling entries are either embeddable Lucene-replacement indexing libraries (IResearch, Tantivy, SeekStorm) or single-machine grep-replacement CLIs (frg, ngi, trigrep, ugrep); Manticore is the only full standalone SQL/HTTP search server in the set. Pick it when you need a deployable, replicated, multi-user database with backup/restore and SQL access rather than a library to embed in your own indexing pipeline, and specifically over Elasticsearch when your workload matches log/analytics/full-text patterns and you can accept GPL-3.0 and a smaller ecosystem.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Bundled Manticore Columnar Library (git submodule) for columnar storage; optional ICU for CJK/Chinese segmentation; various vendored libs under .gitmodules. Not a linkable library — ships as searchd/indexer binaries. |
| **Minimum toolchain** | C++17, CMake 3.17+ |
| **Platforms** | Linux (Debian/Ubuntu, RHEL/CentOS/Amazon/Oracle/Fedora families) and macOS via Homebrew per install script; Windows has its own CI test template (win_test_template.yml). x86-64 assumed; ARM support not documented in README. |
| **Thread safety** | not documented as a library API (there is none); server internally runs multi-threaded query execution and parallelizes across cores per README |
| **Drop-in for the baseline** | partial — explain: has an Elasticsearch-compatible HTTP write path and MySQL-protocol SQL access, so ingestion pipelines (Logstash/Filebeat/Kafka) can be repointed, but query code must be rewritten from Elasticsearch's Query DSL to Manticore SQL or its own HTTP JSON search syntax. |

## Gotchas

- README explicitly states Manticore is 'not fully ACID-compliant' despite having isolated transactions and binlog
- Columnar storage saves RAM but README says it gives 'lower performance than row-wise storage for some kinds of queries' — pick per-table
- GPL-3.0 licensed and historically forked from the Sphinx search engine — copyleft terms differ materially from Elasticsearch's license
- The benchmark suite (db-benchmarks.com / github.com/db-benchmarks/db-benchmarks) used for the headline multipliers is run by the same Manticore team (top contributor sanikolaev), not an independent third party

## Caveats and trade-offs

First-party: the blog author is Manticore's Sergey Nikolaev, and db-benchmarks.com (github.com/db-benchmarks/db-benchmarks) is maintained by the same Manticore team, so it is not an independent suite. The page dates from July 2022 and uses Elasticsearch 7.15.2 (from the Logstash log) and Manticore 5.0.2 (the docker tag in the 50M test); the CPU model and build flags are not stated. The page's own ingestion conclusion is 2x; a 5.5x figure would pair sharded Manticore with unsharded refresh=1 Elasticsearch. Elasticsearch is Lucene-based, so this is an indirect comparison to Lucene.

GPL-3.0 copyleft (vs Elasticsearch's SSPL/Elastic license) may restrict some proprietary embedding; SQL-like + JSON query interface differs from Elasticsearch's Query DSL; smaller ecosystem/plugin base than the Elastic stack; historically forked from the Sphinx search engine.

## Maintenance

Actively maintained (record's last_commit is current, large nightly/CI test matrix in .github/workflows) and free to install via package manager, Docker, or source build; GPL-3.0 licensing is the main friction point for proprietary embedding rather than any maturity concern.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now C.
- **Tier reason:** Vendor blog post (Manticore CEO, Jul 2022) citing db-benchmarks.com. That suite is maintained by the same Manticore team (top contributor sanikolaev; ships Manticore nightly configs), so it is first-party, not independent. No CPU model or build flags are stated, so C.
- **Verifier notes:** Downgraded B to C because db-benchmarks is Manticore's own framework (not independent). The claimed 5.5x ingestion ratio (894,856 vs 162,614) mixed sharded and unsharded configs; the page says 2x. The 4x/15x/22x/25x figures are on the page. last_commit updated to 2026-09-25.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://manticoresearch.com/blog/manticore-alternative-to-elasticsearch/>
  - <https://github.com/manticoresoftware/manticoresearch>
  - <https://github.com/db-benchmarks/db-benchmarks>
- **Sources the enricher read:**
  - <https://github.com/manticoresoftware/manticoresearch>
  - <https://manticoresearch.com/blog/manticore-alternative-to-elasticsearch/>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/manticoresoftware/manticoresearch`) · [data/wave3/enrich/raw/github_com_manticoresoftware_manticoresearch.json](../../../data/wave3/enrich/raw/github_com_manticoresoftware_manticoresearch.json) (enrichment confidence 0.55)

</details>
