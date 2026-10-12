# SeekStorm

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Text search and indexing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0` · 🟢 active

> Rust in-process search engine with native lexical and vector indexes; claims sub-millisecond BM25 latency beating Lucene.

| | |
|---|---|
| **Beats** | Apache Lucene |
| **Claimed result** | Current search-benchmark-game run (SeekStorm 1.0.0 vs Lucene 10.3.0-bp vs Tantivy 0.25; results.json in SeekStorm/search-benchmark-game), as a ratio of mean best-of-10 latency vs Lucene: intersection 1.5x-2.0x, phrase 3.1x-6.4x, union 1.3x-13.1x across the TOP_10 / COUNT / TOP_10_COUNT collectors; 115x-135x on the single 'two-phase-critic' query. The single term 'the' is 7.3x (TOP_10) and 169x (TOP_10_COUNT) faster but about 3x SLOWER than Lucene for COUNT. Against Tantivy 0.25: 2.2x-9.2x on intersection/phrase/union (derived from page data). The Dec 2023 blog (older versions) reported 4.6x-10.1x vs Lucene on all/union queries, 1.6x-1.8x on intersection, and 174.8x-734.1x on 'the'/two-phase-critic. |
| **Workload** | BM25 lexical search on English Wikipedia (5,032,105 docs per blog), single-threaded, best of 10 runs: 300 intersection, 300 phrase and 301 union AOL-derived queries plus the term 'the' and a two-phase-critic query, under COUNT, TOP_10 and TOP_10_COUNT collectors. Uses SeekStorm's fork of quickwit-oss/search-benchmark-game. |
| **Metric** | latency |
| **Hardware** | ThinkPad P1 Gen 6, Intel Core i7-13700H, SK hynix 2TB PCIe 4.0 NVMe SSD, Ubuntu 24.04 LTS (fork README). Dec 2023 blog: ThinkPad P1, 64 GB RAM, i7-13700H 2.40GHz, 2TB Hynix NVMe |
| **Compiler and flags** | Rust 1.90, RUSTFLAGS='-C target-cpu=native' cargo build --release (SeekStorm 1.0.0, Tantivy 0.25); OpenJDK 21, java -XX:+UseParallelGC --add-modules jdk.incubator.vector (Lucene 10.3.0-bp); per fork README and engines/\*/Makefile |
| **Adoption** | 1.9k stars |
| **Last commit** | 2026-09-12 |
| **Links** | [repository](https://github.com/SeekStorm/SeekStorm) · [benchmark](https://github.com/SeekStorm/search-benchmark-game) |

## Verdict

Against Lucene 10.3.0-bp (OpenJDK 21, -XX:+UseParallelGC, --add-modules jdk.incubator.vector) with SeekStorm 1.0.0 built via RUSTFLAGS='-C target-cpu=native' cargo build --release on Rust 1.90, run on a ThinkPad P1 Gen 6 (i7-13700H, NVMe SSD, Ubuntu 24.04): over 300 intersection, 300 phrase and 301 union AOL-derived queries plus 'the' and a two-phase-critic query on 5,032,105-doc English Wikipedia, mean best-of-10 latency was 1.5x-2.0x faster for intersection, 3.1x-6.4x for phrase, 1.3x-13.1x for union, and 115x-135x for the two-phase-critic query, but about 3x slower than Lucene on 'the' under the COUNT collector.

## Use it when

- Million-doc-scale BM25 lexical search (like the Wikipedia benchmark) where sub-millisecond latency and low tail latency (P99) matter
- Need lexical + vector hybrid search behind one query planner (RRF fusion) instead of bolting a vector DB onto Lucene
- Want a single-binary Rust deployment with no JVM, avoiding GC pauses and segment-merge latency spikes
- True real-time search requirement: every indexed document must be searchable immediately, not near-real-time
- Willing to adopt a new schema/query API and Rust crate ecosystem instead of reusing an existing Lucene index

## Skip it when

- Need drop-in Lucene/Solr/Elasticsearch compatibility: index format, Query DSL, and Java plugin ecosystem are not compatible with SeekStorm's own REST API and schema
- Risk-averse production use: 1.9k stars and a young issue tracker, smaller deployment base than Lucene/Tantivy
- Workload is dominated by single very-frequent-term COUNT queries: SeekStorm measured about 3x slower than Lucene on the term 'the' under the COUNT collector, and plain TOP_10 union gains are only 1.3x, not the 100x+ figures reported for other collectors
- Platform outside x86-64/aarch64 or Windows/Linux/macOS: other OSes are explicitly untested per README
- Need the 20-year analyzer/connector/plugin ecosystem Lucene has accumulated

## How it is fast

Term-proximity BM25F ranking with block-max WAND/Maxscore query pruning and roaring-bitmap-compressed posting lists cuts work per query; intersection/union routines are hand-written with SIMD (see intersection_simd.rs, AVX2/NEON). Being a single Rust binary avoids JVM warm-up, GC pauses, and Lucene-style segment merges, which the README credits for stable tail latency (no cold-start or merge-triggered spikes). True real-time indexing means new documents are searchable immediately, without a commit/refresh delay.

## Compared with alternatives

Pick SeekStorm over Tantivy or IResearch (SereneDB) when you need a first-class native vector index and hybrid RRF fusion in the same engine, not just lexical search; its phrase/union speedups (3.1x-13.1x) are also larger in its own benchmark run than Tantivy's \~2x README claim, though intersection gains (1.5x-2.0x) are in a similar range and SeekStorm is the youngest, smallest-community project of the three.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | many: tokio, serde/serde_json, rayon, zstd, ahash (or optional gxhash), regex, model2vec-rs for embeddings, optional pdfium-render (feature "pdf") and Chinese segmentation (feature "zh") — see Cargo.toml for full list (\~30 deps) |
| **Minimum toolchain** | Rust edition 2024 (Cargo.toml edition="2024"); the verified benchmark build used Rust 1.90 with RUSTFLAGS='-C target-cpu=native' |
| **Platforms** | x86-64 and aarch64 with SIMD acceleration on both; Windows, Linux, macOS documented, other OS untested per README |
| **Thread safety** | not formally documented beyond usage pattern; README examples wrap the index in Arc&lt;RwLock&lt;..&gt;&gt; and require an async Tokio runtime (#[tokio::main]) for indexing and search calls |
| **Drop-in for the baseline** | partial — explain: the server exposes a REST API like a search backend, but uses its own JSON schema, query syntax and OpenAPI spec, not Lucene's API or index format |

## Gotchas

- Requires an async Tokio runtime even for basic single-threaded indexing/search calls
- Default Cargo features pull in Chinese word segmentation, PDF text extraction (pdfium-render), and varint bitpacking; disable with default-features=false if not needed
- Historical panics reported on commit() after reopening an external-vector index (issue #65) and during realtime search (issue #36); both closed/fixed but indicate edge cases under specific update sequences
- Optional gxhash feature needs AES/SSE2 hardware support; enabling it without that support is a documented risk

## Caveats and trade-offs

The harness is SeekStorm's own fork of quickwit-oss/search-benchmark-game, run by SeekStorm on one laptop. We derived the current-run multipliers from results.json as a ratio of mean best-of-10 latencies. Gains vary strongly by collector: union vs Lucene is only 1.3x for TOP_10 but 13x for TOP_10_COUNT, and SeekStorm is about 3x slower than Lucene on the 'the' COUNT query. The 100x+ figures come from single queries ('the', 'two-phase-critic'), not from general throughput. The Dec 2023 blog numbers used older, unstated engine versions.

Rust, single binary, no JVM/segment-merge GC pauses (claimed benefit for tail latency); newer project than Lucene/Tantivy with a smaller ecosystem and fewer production deployments; benchmark adapters are written by each engine's own authors ('for maximum authenticity') rather than a fully neutral third party.

## Maintenance

Actively maintained (last commit 2026-09-12), Apache-2.0 licensed, and copyable as a Rust crate; 1.9k stars is small next to Lucene's install base, but the CHANGELOG and issue tracker show ongoing bug fixes and feature work.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded B to A. SeekStorm's public search-benchmark-game fork runs against Lucene 10.3.0-bp with code in engines/seekstorm-1.0.0 and engines/lucene-10.3.0-bp. The README states i7-13700H, Rust 1.90 and OpenJDK 21, and the Makefiles state the flags (RUSTFLAGS='-C target-cpu=native' cargo build --release; java -XX:+UseParallelGC).
- **Verifier notes:** Blog numbers verified, but the record put intersection in the 4.6x-10.1x range; the blog shows 1.6x-1.8x vs Lucene for intersection. Found stronger evidence in the fork (versions, flags, CPU, results.json), so the tier is upgraded to A and claimed_speedup is re-derived from current data. Metadata (Apache-2.0, 1.9k stars, last commit 2026-09-12) verified.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `compiler_and_flags`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://seekstorm.com/blog/sneak-peek-seekstorm-rust/>
  - <https://github.com/SeekStorm/SeekStorm>
  - <https://github.com/SeekStorm/search-benchmark-game>
  - <https://github.com/SeekStorm/search-benchmark-game/blob/master/results.json>
  - <https://github.com/SeekStorm/search-benchmark-game/blob/master/engines/seekstorm-1.0.0/Makefile>
  - <https://github.com/SeekStorm/search-benchmark-game/blob/master/engines/lucene-10.3.0-bp/Makefile>
- **Sources the enricher read:**
  - <https://github.com/SeekStorm/SeekStorm>
  - <https://github.com/SeekStorm/SeekStorm/blob/main/README.md>
  - https://github.com/SeekStorm/SeekStorm (recursive file tree)
  - <https://github.com/SeekStorm/SeekStorm/blob/main/seekstorm/Cargo.toml>
  - <https://github.com/SeekStorm/SeekStorm/blob/main/Cargo.toml>
  - <https://github.com/SeekStorm/SeekStorm/blob/main/seekstorm/src/lib.rs>
  - https://github.com/SeekStorm/SeekStorm/issues (search: bug)
  - <https://github.com/SeekStorm/SeekStorm/issues?state=open>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/seekstorm/seekstorm`) · [data/wave3/enrich/raw/github_com_seekstorm_seekstorm.json](../../../data/wave3/enrich/raw/github_com_seekstorm_seekstorm.json) (enrichment confidence 0.6)

</details>
