# Tantivy

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Text search and indexing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `MIT` · 🟢 active

> Embeddable Rust full-text search library, architecturally close to Lucene, ahead on phrase/negated/count-heavy queries.

| | |
|---|---|
| **Beats** | Lucene |
| **Claimed result** | README FAQ says 'approximately 2x faster than Lucene', but the linked suite's current results.json (tantivy-0.26 vs lucene-10.4.0, best of 10 runs, Ryzen 7 9800X3D) shows per-collector geometric-mean speedups of 0.83x (TOP_10, Lucene faster), 1.02x (TOP_100), 1.14x (TOP_1000), 1.31x (TOP_100_COUNT), 1.08x (COUNT) (derived from page data). Tantivy is faster on phrase queries (mean 1.35x-1.58x on TOP_100/TOP_1000/TOP_100_COUNT/COUNT) and negated/term queries, while Lucene is \~2x-2.6x faster on TOP_10 intersection and union and COUNT union (derived from page data). |
| **Workload** | Search Benchmark, the Game: English Wikipedia corpus, stemming disabled; AOL-derived queries (2+ terms, &gt;=1 phrase hit, 962 per collector) run as term/intersection/union/phrase/negated/intersection_union queries under TOP_10 / TOP_100 / TOP_1000 / TOP_100_COUNT / COUNT collectors; single-threaded, best of 10 runs after warm-up (page cache + JIT); Tantivy 0.26 vs Lucene 10.4.0 (plus a Lucene BP-reordering variant). |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 7 9800X3D, Manjaro Linux (rolling), kernel 7.0.3-1-MANJARO |
| **Compiler and flags** | Tantivy 0.26: Rust 1.96.0, RUSTFLAGS='-C target-cpu=native' cargo build --release with [profile.release] lto=true, opt-level=3 (engines/tantivy-0.26). Lucene 10.4.0: OpenJDK 21.0.11, java -XX:+UseParallelGC --add-modules jdk.incubator.vector (engines/lucene-10.4.0/Makefile). |
| **Adoption** | 16.1k stars; used in production by Etsy, ParadeDB, Nuclia, Element.io, and others |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/quickwit-oss/tantivy) · [benchmark](https://github.com/quickwit-oss/search-benchmark-game) |

## Verdict

In the search-benchmark-game suite, Tantivy 0.26 (Rust 1.96.0, target-cpu=native, LTO, opt-level=3) vs Lucene 10.4.0 (OpenJDK 21.0.11, ParallelGC) on an AMD Ryzen 7 9800X3D shows per-collector geometric-mean ratios from 0.83x (Lucene faster on TOP_10) to 1.31x (TOP_100_COUNT) — not the README's claimed '\~2x faster' — with Tantivy's wins concentrated in phrase, negated, and count-heavy collectors and Lucene ahead on TOP_10 and intersection/union queries.

## Use it when

- Embedding a BM25 full-text index directly into a Rust binary, CLI, or service without running a separate search server or JVM
- Read-heavy workloads dominated by phrase, negated, or count-only queries (COUNT / TOP_100_COUNT), where the current benchmark shows it ahead of Lucene
- Append-mostly / batch indexing that fits a commit-based, immutable-segment model rather than constant per-document mutation
- Need multi-language stemming (17 languages), JSON fields, facets, or range queries out of the box in a single crate
- Fine with a Rust core and using community bindings (tantivy-py, Ruby) rather than a JVM dependency

## Skip it when

- Latency-sensitive TOP_10 result pages or intersection/union-heavy boolean queries, where the current benchmark shows Lucene \~2x-2.6x faster
- Frequent in-place document edits: segments are immutable, so updates are delete-then-reindex plus a merge
- Need a standalone search server out of the box; Tantivy itself has no REST/network layer (pair with Quickwit or build one)
- Team is JVM-only and doesn't want a Rust toolchain in the stack just for search
- Need Lucene's much longer operational history and broader third-party tooling/plugin ecosystem

## How it is fast

Indexes are immutable, mmap'd segments with FST-based term dictionaries (tantivy-fst) for fast term lookup and block-bitpacked (bitpacker4x) SIMD-friendly postings compression. Top-k boolean queries use Block-Max WAND pruning (src/query/boolean_query/block_wand_intersection.rs and block_wand_union.rs): documents are processed in 128-doc windows and whole blocks are skipped when their precomputed max score can't beat the current threshold. These are the same algorithmic family Lucene uses, reimplemented in Rust.

## Compared with alternatives

Pick Tantivy over IResearch/SereneDB or SeekStorm (same category, also run through the same search-benchmark-game harness against Lucene) when you want the most mature, widely production-used Rust search crate (Etsy, ParadeDB, Nuclia) rather than the largest headline multiple — IResearch and SeekStorm claim bigger speedups in that same suite but have far less deployment history.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | many small Rust crates (regex, aho-corasick, tantivy-fst, bitpacking, rayon, lz4_flex/zstd optional, serde); no external services or JVM |
| **Minimum toolchain** | Rust 1.87 (edition 2021, per Cargo.toml rust-version); the benchmark build used Rust 1.96.0 with target-cpu=native + LTO |
| **Platforms** | any (pure Rust, Linux/macOS/Windows per README); SIMD integer postings compression activates on SSE2-capable CPUs |
| **Thread safety** | not documented as a blanket guarantee; source shows one active IndexWriter per index (internally multithreaded, up to 8 worker threads, memory-budgeted per thread) while Searcher/IndexReader snapshots are cheap to clone and read concurrently |
| **Drop-in for the baseline** | partial — explain: mirrors Lucene's design (BM25, schema, segments, merge policy) but is a different language and API, not wire- or source-compatible |

## Gotchas

- Segments are immutable; deletes are tombstones resolved only at merge time, so delete-heavy workloads need merge-policy tuning
- Only one IndexWriter may be open on an index at a time (directory-locked); concurrent writers must be coordinated externally
- SIMD postings gains are CPU-dependent (SSE2 assumed); the published benchmark numbers were built with -C target-cpu=native and LTO, which a default `cargo build --release` from crates.io won't reproduce
- Experimental features like the jitexpr predicate crate are explicitly marked unstable and likely to change

## Caveats and trade-offs

The README's '\~2x faster than Lucene' is not borne out by the suite's committed results since at least Sept 2025 (tantivy-0.25 vs lucene-10.3.0 geo-means 0.90x-1.33x) and in the current run Tantivy is slower on TOP_10 and roughly at parity on TOP_100; the win is concentrated in phrase, term, negated and count-heavy (TOP_100_COUNT) workloads, and Lucene with BP doc reordering is faster still on most collectors. The live dashboard tantivy-search.github.io/bench/ is JS-rendered; ratios here are computed from results.json. Benchmark is maintained by the Tantivy team.

Immutable segments (documents must be deleted and reindexed to edit); library, not a standalone server (Quickwit is the distributed-search layer built on top); Rust-only core API (bindings exist for Python/Ruby).

## Maintenance

Actively maintained (last commit 2026-09-23, Cargo.toml already at 0.27.0) with 16.1k stars and real production users (Etsy, ParadeDB, Nuclia, Element.io); MIT-licensed and usable as an ordinary vendored Rust dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now A.
- **Tier reason:** Public harness quickwit-oss/search-benchmark-game (engines/tantivy-0.26/Makefile + Cargo.toml, engines/lucene-10.4.0/Makefile) states Rust 1.96.0 with -C target-cpu=native/LTO/opt-level=3, OpenJDK 21.0.11 JVM flags, and CPU AMD Ryzen 7 9800X3D, so A stands; but its committed results do not show the \~2x win the README states.
- **Verifier notes:** Real, notable entry, but the headline claim is stale/overstated against Lucene 10.x, so downgrade on the claim with tier A kept; the orchestrator may want to reframe it as 'faster on phrase/count workloads' or reconsider inclusion. Last commit on main is 2026-09-23 (record had the pushed_at date 2026-09-24); MIT, 16,141 stars confirmed.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `last_commit`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/quickwit-oss/tantivy>
  - <https://github.com/quickwit-oss/tantivy#readme>
  - <https://tantivy-search.github.io/bench/>
  - <https://github.com/quickwit-oss/search-benchmark-game>
  - <https://github.com/quickwit-oss/search-benchmark-game/blob/master/README.md>
  - <https://github.com/quickwit-oss/search-benchmark-game/blob/master/results.json>
  - <https://github.com/quickwit-oss/search-benchmark-game/blob/master/Makefile>
  - <https://github.com/quickwit-oss/search-benchmark-game/blob/master/engines/tantivy-0.26/Makefile>
  - <https://github.com/quickwit-oss/search-benchmark-game/blob/master/engines/tantivy-0.26/Cargo.toml>
  - <https://github.com/quickwit-oss/search-benchmark-game/blob/master/engines/lucene-10.4.0/Makefile>
  - <https://github.com/quickwit-oss/search-benchmark-game/commit/c2b2850fdc6d0462afd5f8dce1388962b399ef6c>
- **Sources the enricher read:**
  - https://github.com/quickwit-oss/tantivy (README)
  - <https://github.com/quickwit-oss/tantivy/blob/main/Cargo.toml>
  - https://github.com/quickwit-oss/tantivy (repo tree listing)
  - https://github.com/quickwit-oss/tantivy/issues (search: corruption OR data loss OR panic)
  - <https://github.com/quickwit-oss/tantivy/blob/main/src/lib.rs>
  - <https://github.com/quickwit-oss/tantivy/blob/main/src/query/boolean_query/block_wand_intersection.rs>
  - <https://github.com/quickwit-oss/tantivy/blob/main/CHANGELOG.md>
  - <https://github.com/quickwit-oss/tantivy/blob/main/src/indexer/index_writer.rs>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/quickwit-oss/tantivy`) · [data/wave3/enrich/raw/github_com_quickwit_oss_tantivy.json](../../../data/wave3/enrich/raw/github_com_quickwit_oss_tantivy.json) (enrichment confidence 0.8)

</details>
