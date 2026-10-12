# IResearch (SereneDB)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Text search and indexing](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> C++ inverted-index search library (ex-ArangoSearch) embedded in SereneDB; claims 5x over Lucene, real gains are 1.0x-1.7x.

| | |
|---|---|
| **Beats** | Lucene |
| **Claimed result** | Project README says 'up to 5x faster than Lucene and Tantivy'. In the suite's current results.json (iresearch-26.03.1 vs lucene-10.4.0 / tantivy-0.26, best of 10 runs, Ryzen 7 9800X3D), per-collector geometric-mean speedup vs Lucene is 0.99x (TOP_10), 1.20x (TOP_100), 1.41x (TOP_1000), 1.67x (TOP_100_COUNT), 1.25x (COUNT), and vs Tantivy 1.15x-1.28x; &gt;=5x vs Lucene occurs on about 0.1% of queries (max 8.5x on the single term query 'the') (derived from page data). Lucene 10.4.0 with BP doc reordering is faster than IResearch on TOP_10/TOP_100 mean latency. In the cited commit f4149454 (vs lucene-10.3.0 / tantivy-0.25) the geo-mean speedup was 1.14x-1.84x vs Lucene and 1.33x-1.48x vs Tantivy (derived from page data). |
| **Workload** | Search Benchmark, the Game (quickwit-oss/search-benchmark-game): English Wikipedia corpus, AOL-derived queries (962 per collector) run as term/intersection/union/phrase/negated/intersection_union queries under TOP_10 / TOP_100 / TOP_1000 / TOP_100_COUNT / COUNT collectors; single-threaded, best of 10 runs, warm page cache; vs Lucene 10.4.0 (plus Lucene -bp variant), Tantivy 0.26 and PISA 0.8.2. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 7 9800X3D, Manjaro Linux, kernel 7.0.3-1-MANJARO (README environment for the current results.json, re-run 2026-05-30 by a Tantivy maintainer); the hardware for IResearch's own submission run (commit f4149454, 2026-03-24) is undocumented. |
| **Compiler and flags** | IResearch: clang/clang++ 21 with lld 21 (repo Dockerfile, llvm-toolchain-noble-21), cmake --preset bench = CMAKE_BUILD_TYPE=Release, static executables, jemalloc (serenedb CMakePresets.json), built in Docker per engines/iresearch-26.03.1/Makefile (PGO targets exist but are not the default compile target). Tantivy 0.26: Rust 1.96.0, RUSTFLAGS='-C target-cpu=native' cargo build --release, lto=true, opt-level=3. Lucene 10.4.0: OpenJDK 21.0.11, -XX:+UseParallelGC, jdk.incubator.vector. |
| **Adoption** | 831 stars (serenedb/serenedb monorepo); production search backend since 2018 (originally ArangoSearch) |
| **Last commit** | 2026-09-25 |
| **Links** | [repository](https://github.com/serenedb/serenedb) · [benchmark](https://github.com/quickwit-oss/search-benchmark-game) |

## Verdict

On the third-party Search Benchmark, The Game (English Wikipedia + AOL-derived queries, single-threaded, warm cache, best of 10 runs, AMD Ryzen 7 9800X3D), IResearch 26.03.1 (clang 21/lld 21, Release, jemalloc) shows per-collector geo-mean speedups of 0.99x-1.67x vs Lucene 10.4.0 (OpenJDK 21, UseParallelGC) and 1.15x-1.28x vs Tantivy 0.26 (Rust 1.96, LTO release) -- not the README's 'up to 5x', which occurs on about 0.1% of queries (max 8.5x on the term query 'the').

## Use it when

- Embedding a C++ inverted-index engine directly into an application or DuckDB-based database instead of running a JVM search server
- Need BM25/TFIDF/LM-Dirichlet scoring plus vector (HNSW/IVF) and geospatial (S2) search in one library without separate services
- Workload is dominated by TOP_100/TOP_1000/TOP_100_COUNT/COUNT-style multi-hit collection, where the measured 1.2x-1.7x gain over Lucene 10.4.0 actually applies
- JVM-free deployment is a hard requirement (embedded/edge, memory-constrained hosts)
- Team can build with a very recent clang/lld (21+) and is willing to vendor SereneDB as a git submodule

## Skip it when

- Workload is TOP_10 single/few-hit lookups: geo-mean is roughly parity with Lucene 10.4.0 (0.99x) there, and Lucene with BP doc reordering beats IResearch on TOP_10/TOP_100 mean latency
- Specifically hits intersection or union query shapes at TOP_10: IResearch is slower than plain Lucene 10.4.0 on both (390 vs 241us intersection, 372 vs 309us union)
- Need a stable, versioned public C API/ABI: this is a C++26 CMake target meant to be vendored as source, not a library with ABI guarantees
- Need a widely deployed, mature standalone search library: outside SereneDB, IResearch's install base is essentially just ArangoDB since 2018 (188-star archived iresearch-toolkit/iresearch predecessor)
- Toolchain is older than clang/lld 21 or CMake 3.28: the repo requires C++26 and pins a bleeding-edge compiler

## How it is fast

A vectorized, block-at-a-time SIMD scoring pipeline processes posting lists in batches instead of doc-by-doc; postings use a block-128 format with simdcomp bit-packing and a burst-trie term dictionary plus skip lists for fast term/intersection seeks. Lazy evaluation defers non-lead iterators in conjunctions, exclusions and two-phase queries so cheap clauses avoid unnecessary work. The project's own blog series attributes gains to top-K candidate collection, block scoring, norm gathering, lazy two-phase queries and an adaptive posting-list format, but the measured geo-mean speedup vs Lucene 10.4.0 in the current benchmark run is only 0.99x-1.67x depending on collector type, well short of the 5x headline.

## Compared with alternatives

Pick IResearch over Tantivy or SeekStorm when native C++ embedding into a DuckDB-based engine and JVM-freedom matter more than winning the benchmark outright -- on the same suite Tantivy is close (IResearch is only 1.15x-1.28x over Tantivy) and both Tantivy and SeekStorm are more mature as standalone, independently-installable libraries than IResearch is outside SereneDB/ArangoDB.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | simdcomp (posting bit-packing), ICU (icu_text_tokenizer), fastText, S2 geometry (geo filters), Abseil, DuckDB (column codec + buffer manager integration), liburing (optional, SDB_IOURING), jemalloc/tcmalloc (optional allocator) |
| **Minimum toolchain** | C++26 (CMAKE_CXX_STANDARD 26), CMake 3.26+ (benchmark build uses 3.28.3+), clang/clang++ + lld 21.1.8+ |
| **Platforms** | Linux (repo Docker images use llvm-toolchain-noble-21, glibc 2.35+); io_uring feature is Linux-only; macOS/Windows/aarch64 support not documented |
| **Thread safety** | IndexWriter guards commits with an internal recursive mutex, a commit lock, and a filesystem write.lock -- a single-writer-per-index model similar to Lucene; parallel indexing is supported (per the benchmark engine README) but not documented in prose beyond the header's locking code |
| **Drop-in for the baseline** | partial -- API is a distinct C++ class hierarchy (IndexWriter/DirectoryReader/Field structs, id-based column access), not source- or wire-compatible with Lucene; only query syntax (Lucene-style query strings) is compatible |

## Gotchas

- Requires C++26 and a very new clang/lld toolchain (repo's own Docker image and the benchmark harness both pin clang/lld 21) -- will not build with older compilers
- Field-to-column mapping is id-based, not name-based; callers own the field_id -&gt; name mapping (per the basic.cpp example's comments)
- The legacy `Write()` STORE callback was removed; stored values now go through a separate `.col` writer that needs a DuckDB DatabaseInstance for codec lookup
- Open issue #937 describes a bug in BlockDisjunction's sub-iterator refill (uses advance() where seek() is needed); issue #364 tracks a still-open broader 'IResearch optimizations' plan, i.e. some perf paths are acknowledged unfinished

## Caveats and trade-offs

The 'up to 5x' headline is a per-query maximum; typical per-collector geo-mean gains vs Lucene 10.4.0 are \~1.0x-1.7x, IResearch is slower than Lucene on TOP_10 intersection (mean 390 vs 241 us) and union (372 vs 309 us), and Lucene with BP reordering beats it on TOP_10/TOP_100 means, so SereneDB's 'outperforms Lucene across every query type' is not borne out by the committed results. Results were contributed by the SereneDB team (PR #82), approved/merged by fulmicoton and 'confirmed by @PSeitz', then re-run by the Tantivy maintainers. Originally iresearch-toolkit/iresearch (now archived, 188 stars), moved into serenedb/serenedb iresearch/ by the same maintainers; is_fork_of left null.

C++ library embedded via CMake (target iresearch-static), not a standalone server; JVM-free; the 5x headline also includes beating Tantivy, which is not one of this category's three named baselines (only the Lucene comparison counts here).

## Maintenance

Actively maintained (last commit 2026-09-25) as part of the SereneDB monorepo, Apache-2.0 and copyable as a CMake submodule, but its C++26/clang-21 toolchain requirement raises the vendoring bar compared to more portable C++ search libraries.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now A.
- **Tier reason:** Third-party Tantivy-team suite with public code (engines/iresearch-26.03.1 Makefile + serenedb `bench` CMake preset, clang-21/lld-21 via repo Dockerfile, Release build) re-run by Tantivy maintainer Pascal Seitz (commit c2b2850f, 2026-05-30) with CPU stated in README (AMD Ryzen 7 9800X3D). The cited commit f4149454 alone would not be A: its README still described an older AWS Xeon 8488C/Rust 1.89 environment that did not produce those numbers.
- **Verifier notes:** benchmark_url moved from the SereneDB-authored commit f4149454 (undocumented hardware; README env at that commit was stale) to the suite repo, whose current results.json is from Tantivy-maintainer commit https://github.com/quickwit-oss/search-benchmark-game/commit/c2b2850fdc6d0462afd5f8dce1388962b399ef6c on the documented 9800X3D. The '5x' figure is not on the commit page; it is IResearch's own README framing and is overstated as a headline, hence downgrade. License Apache-2.0, 831 stars, last commit 2026-09-25 confirmed via gh.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/quickwit-oss/search-benchmark-game/commit/f4149454e8de6d97a0b5c1b4253db1a6e2c82622>
  - <https://github.com/quickwit-oss/search-benchmark-game/pull/82>
  - <https://github.com/quickwit-oss/search-benchmark-game>
  - <https://github.com/quickwit-oss/search-benchmark-game/blob/master/README.md>
  - <https://github.com/quickwit-oss/search-benchmark-game/blob/master/results.json>
  - <https://github.com/quickwit-oss/search-benchmark-game/blob/master/Makefile>
  - <https://github.com/quickwit-oss/search-benchmark-game/blob/master/Dockerfile>
  - <https://github.com/quickwit-oss/search-benchmark-game/blob/master/engines/iresearch-26.03.1/Makefile>
  - <https://github.com/quickwit-oss/search-benchmark-game/blob/master/engines/iresearch-26.03.1/README.md>
  - <https://github.com/quickwit-oss/search-benchmark-game/blob/master/engines/iresearch-26.03.1/details.json>
  - <https://github.com/quickwit-oss/search-benchmark-game/commit/c2b2850fdc6d0462afd5f8dce1388962b399ef6c>
  - <https://github.com/serenedb/serenedb>
  - <https://github.com/serenedb/serenedb/blob/main/README.md>
  - <https://github.com/serenedb/serenedb/blob/main/iresearch/README.md>
  - <https://github.com/serenedb/serenedb/blob/main/CMakePresets.json>
  - <https://github.com/iresearch-toolkit/iresearch>
- **Sources the enricher read:**
  - <https://github.com/serenedb/serenedb>
  - <https://github.com/serenedb/serenedb/blob/main/README.md>
  - <https://github.com/serenedb/serenedb/blob/main/iresearch/README.md>
  - <https://github.com/serenedb/serenedb/blob/main/CMakePresets.json>
  - <https://github.com/serenedb/serenedb/blob/main/CMakeLists.txt>
  - <https://github.com/serenedb/serenedb/blob/main/iresearch/CMakeLists.txt>
  - <https://github.com/serenedb/serenedb/blob/main/third_party/LICENSES.md>
  - <https://github.com/serenedb/serenedb/blob/main/iresearch/index/index_writer.hpp>
  - <https://github.com/serenedb/serenedb/blob/main/iresearch/index/directory_reader.hpp>
  - <https://github.com/serenedb/serenedb/blob/main/examples/iresearch/basic.cpp>
  - <https://github.com/serenedb/serenedb/issues/937>
  - <https://github.com/serenedb/serenedb/issues/364>
  - <https://github.com/quickwit-oss/search-benchmark-game/blob/master/engines/iresearch-26.03.1/README.md>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/serenedb/serenedb`) · [data/wave3/enrich/raw/github_com_serenedb_serenedb.json](../../../data/wave3/enrich/raw/github_com_serenedb_serenedb.json) (enrichment confidence 0.78)

</details>
