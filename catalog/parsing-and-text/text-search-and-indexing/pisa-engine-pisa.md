# PISA (Performant Indexes and Search for Academia)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Text search and indexing](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Research-grade in-memory C++ inverted-index search engine; trades blows with Lucene 10.4 on top-k ranked queries, loses on counting.

| | |
|---|---|
| **Beats** | Lucene 10.4.0 (also Lucene 10.4.0 with BP doc reordering, and Tantivy 0.26) in the independent search-benchmark-game; the original codec baseline (StreamVByte / SIMD-BP128 inside PISA) has no published numbers |
| **Claimed result** | search-benchmark-game (PISA 0.8.2 vs Lucene 10.4.0, Ryzen 7 9800X3D), clean subset only (derived from page data): TOP_10 on 601 intersection+union queries 0.94x Lucene, 0.73x lucene-bp, 1.34x Tantivy 0.26; intersection TOP_1000 1.34x Lucene; union COUNT 0.36x. The headline geomean 2.19x TOP_1000 rests on union queries that return fewer than k docs and on COUNTs that differ from Lucene, so it is not valid. |
| **Workload** | Search Benchmark, the Game (quickwit-oss/search-benchmark-game, results.json from commit 'use Docker to build pisa, update results', 2026-05-31): English Wikipedia, AOL-derived queries run single-threaded as term/intersection/union/negated/intersection_union queries under TOP_10, TOP_100, TOP_1000, TOP_100_COUNT and COUNT collectors, best of 10 runs per query, warm page cache. PISA 0.8.2 uses FastPFOR blocks of 128, block-max WAND, and doc IDs reordered by recursive graph bisection; it ran 661 of the queries (no phrase queries, which have empty timings). |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 7 9800X3D, Manjaro Linux, kernel 7.0.3-1-MANJARO (search-benchmark-game README environment for results.json) |
| **Compiler and flags** | g++ from Ubuntu 20.04 apt build-essential (GCC 9 series implied by the image; the exact version is not printed), CMake 3.21.3, CMAKE_BUILD_TYPE=Release, -march=native, C++17 (search-benchmark-game engines/pisa-0.8.2/Dockerfile and CMakeLists.txt) |
| **Adoption** | 1.1k stars; used by IR research papers |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/pisa-engine/pisa) · [benchmark](https://raw.githubusercontent.com/quickwit-oss/search-benchmark-game/HEAD/results.json) |

## Verdict

In quickwit-oss/search-benchmark-game results.json (Wikipedia, AOL queries, single-threaded, best of 10, AMD Ryzen 7 9800X3D, PISA 0.8.2 built with Ubuntu 20.04 g++, CMake Release, -march=native, C++17), restricting to the 601 intersection and union queries whose counts match Lucene: top-10 geometric-mean speedup 0.94x vs Lucene 10.4.0, 0.73x vs Lucene 10.4.0-bp, 1.34x vs Tantivy 0.26 (derived from page data). On the 300 intersection queries top-1000 is 1.34x vs Lucene, 1.00x vs Lucene-bp, 1.15x vs Tantivy; union COUNT is 0.36x vs Lucene. The headline TOP_1000 2.19x and TOP_100_COUNT 2.17x include union queries pruned with a top-10 threshold, count-only work and mis-parsed queries.

## Use it when

- IR research or prototyping where you want to swap posting codecs, pruning algorithms and doc-ID orderings and compare them on the same index.
- Static English-like corpora that fit in RAM, rebuilt in batch, served with pure conjunctive or pure disjunctive BM25 top-k queries.
- Conjunctive (AND) ranked queries with large k: on the benchmark-game intersection queries it is about 1.27-1.34x faster than Lucene 10.4.0 at top-100/top-1000 (geometric mean).
- Latency experiments on x86-64 Linux where you control the build (-march=native) and can precompute per-term thresholds.

## Skip it when

- Counting hits over disjunctions: union COUNT queries ran about 2.8x slower than Lucene 10.4.0 (geometric mean 0.36x).
- Top-10 latency against a Lucene index that also uses BP reordering: PISA was 0.73x (slower) on the like-for-like intersection and union queries.
- Anything needing phrase queries, mixed required/optional clauses, negation, incremental updates, deletes, multiple segments or fields; these are absent in the benchmarked build.
- Production services that need a stable API: v0.9.0 notes say breaking changes will be common until a stable release.
- Indexes larger than main memory without sharding: the README states PISA is an in-memory system.

## How it is fast

Doc-at-a-time query processing with dynamic pruning (WAND, block-max WAND, MaxScore variants) over impact-ordered block metadata, with quantized BM25 scores. Postings are stored in SIMD-friendly block codecs (the benchmark uses block_simdbp, i.e. SIMD-BP128 from simdcomp; Elias-Fano/partitioned Elias-Fano, FastPFor, StreamVByte, MaskedVByte, QMX and interpolative are also available), and doc IDs are renumbered by recursive graph bisection so postings compress better and pruning skips more.

## Compared with alternatives

Pick PISA over Tantivy, SeekStorm or IResearch (SereneDB) when you want a C++ research platform with many posting codecs, pruning algorithms and BP reordering to experiment with; pick Tantivy or IResearch for a product-grade engine with phrase queries, segments and updates, where Tantivy was slower than PISA on top-10 (about 0.75x) but PISA's count path is much slower than all three.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | 26 git submodules including Boost, oneTBB, FastPFor, simdcomp, streamvbyte, MaskedVByte, QMX, spdlog, fmt, range-v3, mio, CLI11, gumbo-parser (autotools build), nlohmann_json, Porter2/Krovetz stemmers |
| **Minimum toolchain** | main: C++20, CMake 3.16.9, GCC 9+ (Dockerfile uses gcc:12); benchmarked v0.8.2: C++17 |
| **Platforms** | Unix (CMake adds -march=native on UNIX); x86-64 SIMD codecs; other architectures not documented |
| **Thread safety** | not documented (indexes are read-only memory-mapped structures; the query harness is single-threaded) |
| **Drop-in for the baseline** | no |

## Gotchas

- The benchmark harness (search-benchmark-game engines/pisa-0.8.2/tools/do_query.cpp) seeds block-max WAND with each term's top-10 score threshold for TOP_100 and TOP_1000 too; topk_queue only admits scores &gt;= threshold, so union top-100/top-1000 can return fewer than k documents. This is where the large TOP_1000 win comes from (union queries 3.34x vs intersection 1.34x).
- The harness strips every '+' and treats '-' terms as ordinary terms, so all 40 intersection_union and 19 negated queries compute a different query than Lucene (every one of their COUNT results differs from Lucene's), yet they show 2.3-4.7x 'wins'.
- For TOP_100_COUNT the harness only counts matches (scored_and_query or unscored or_query) without building a top-100 heap, while Lucene and Tantivy compute top-100 plus the count.
- The benchmarked v0.8.2 dates from March 2021; current releases (v0.10.0, December 2024) switched to C++20 and runtime codec dispatch, so the numbers do not describe current main. details.json says FastPFOR blocks, but the harness builds a block_simdbp index.

## Known shortcomings

- Engine-level evidence, not codec-level: quickwit-oss/search-benchmark-game (PISA 0.8.2 vs Lucene 10.4.0, Ryzen 7 9800X3D, g++ ubuntu:20.04 Release -march=native) is mixed, geomean 2.19x on TOP_1000 and 0.56x on COUNT (derived from page data). No published table of its own codecs against varint, Simple8b or FastPFor. Moved to text-search-and-indexing (wave 3 category).
- The search-benchmark-game harness behind the measured numbers has correctness bugs: engines/pisa-0.8.2/tools/do_query.cpp seeds block-max WAND with per-term top-10 thresholds for TOP_100/TOP_1000 too (v0.8.2 topk_queue admits only score &gt;= threshold), so union top-k can return fewer than k docs; all 40 intersection_union and 19 negated queries are mis-parsed ('+' stripped, '-' terms kept); all 59 COUNT results differ from Lucene yet show 2.3-4.7x 'wins'; TOP_100_COUNT only counts with no top-100 heap. On the clean subset PISA is mixed: TOP_10 on 601 intersection+union queries 0.94x Lucene 10.4.0, 0.73x lucene-bp, 1.34x Tantivy 0.26; intersection TOP_1000 1.34x / 1.00x / 1.15x; union COUNT 0.36x (derived from page data). The harness builds block_simdbp (SIMD-BP128), not FastPFOR as details.json says. Benchmarked v0.8.2 dates from 2021 (current v0.10.0, C++20); 26 submodules, API unstable.

## Caveats and trade-offs

The win is mixed and collector-dependent: PISA is faster than Lucene on TOP_1000 and TOP_100_COUNT, roughly even on TOP_10 by geometric mean but slower by mean latency, and about 2x slower on COUNT; Lucene with BP reordering beats it on TOP_10 and COUNT. PISA does not run phrase queries in the suite. These are whole-engine query-latency numbers versus Lucene, not codec decode-speed numbers versus StreamVByte/SIMD-BP128; no per-codec table exists in the PISA repo (benchmarks/ has index_perftest.cpp, perftest_interpolative.cpp and scan_perftest.cpp but no published output). Results were run by the Tantivy maintainers (PSeitz); the suite UI switched to average timings on 2026-09-05, while these figures use best-of-10 per query. The ECIR 2019 paper (Springer), OSIRRC paper (ceur-ws) and pisa-engine.github.io docs were blocked. PISA is a fork of ot/ds2i, which is already a wave 9 integer-bitpacking entry. [retier] Harness bugs in engines/pisa-0.8.2/tools/do_query.cpp invalidate the union TOP_100/TOP_1000 and COUNT rows; the harness builds block_simdbp (SIMD-BP128), not FastPFOR. Benchmarked v0.8.2 (2021); current v0.10.0.

Search engine, not a standalone codec library: codecs (PEF/opt, SIMD-BP128 default, block_interpolative, block_optpfor, QMX, MaskedVByte, StreamVByte) sit behind the inverted-index API; in-memory index only.

## Maintenance

Actively maintained (last commit 2026-09-20, v0.10.0 released December 2024), Apache-2.0, but positioned as an academic platform with an unstable API and a heavy submodule build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification D, tier now C.
- **Tier reason:** Upgraded from D. The independent Search Benchmark, the Game (quickwit-oss/search-benchmark-game) runs PISA 0.8.2 against Lucene 10.4.0 and Tantivy 0.26 with public code (engines/pisa-0.8.2: Dockerfile building with g++ on ubuntu:20.04, CMake Release with -march=native from its CMakeLists.txt) and a named CPU (AMD Ryzen 7 9800X3D); results.json holds per-query timings. This is search-engine query latency against Lucene; it is not codec decode speed, and the record's codec claim itself remains tier D.
- **Retiered** A to C: Lowered A to C: the enricher read the search-benchmark-game harness behind the numbers and found correctness bugs in the PISA engine driver (do_query.cpp seeds block-max WAND with per-term top-10 thresholds for TOP_100/TOP_1000, so union top-k returns fewer than k docs; intersection_union and negated queries are mis-parsed; all 59 COUNT results differ from Lucene). Numbers measured on a harness that returns different results from the baseline do not meet A or B; on the clean subset the result is mixed (TOP_10 0.94x Lucene 10.4.0, intersection TOP_1000 1.34x, union COUNT 0.36x, derived from page data). Kept and documented per the keep-and-document rule.
- **Verifier notes:** I found an independent tier A source: search-benchmark-game results.json has PISA 0.8.2 timings with public build files and a named CPU. The geometric means are my own computation from results.json. The comparison is engine-level against Lucene, so the orchestrator should consider overriding category to text-search-and-indexing (wave 3 lists Tantivy, SereneDB/IResearch and SeekStorm against Lucene, and its batch-05 record already references PISA 0.8.2 in this suite). Metadata confirmed on github.com: Apache-2.0, 1.1k stars, not archived, last commit 2026-09-20 ('Fix CI-build, dockerfiles (#643)').
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** independent search-benchmark-game results; independent search-benchmark-game results, clean subset only
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/pisa-engine/pisa/HEAD/README.md>
  - <https://raw.githubusercontent.com/pisa-engine/pisa/HEAD/LICENSE>
  - <https://github.com/pisa-engine/pisa>
  - <https://github.com/pisa-engine/pisa/commits/main>
  - <https://raw.githubusercontent.com/quickwit-oss/search-benchmark-game/HEAD/README.md>
  - <https://raw.githubusercontent.com/quickwit-oss/search-benchmark-game/HEAD/results.json>
  - <https://github.com/quickwit-oss/search-benchmark-game>
  - <https://github.com/quickwit-oss/search-benchmark-game/commits/master>
  - <https://github.com/quickwit-oss/search-benchmark-game/tree/master/engines/pisa-0.8.2>
  - <https://raw.githubusercontent.com/quickwit-oss/search-benchmark-game/HEAD/engines/pisa-0.8.2/Dockerfile>
  - <https://raw.githubusercontent.com/quickwit-oss/search-benchmark-game/HEAD/engines/pisa-0.8.2/Makefile>
  - <https://raw.githubusercontent.com/quickwit-oss/search-benchmark-game/HEAD/engines/pisa-0.8.2/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/pisa-engine/pisa/HEAD/README.md>
  - <https://raw.githubusercontent.com/pisa-engine/pisa/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/pisa-engine/pisa/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/pisa-engine/pisa/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/pisa-engine/pisa/HEAD/include/pisa/cursor/block_max_scored_cursor.hpp>
  - <https://raw.githubusercontent.com/pisa-engine/pisa/HEAD/include/pisa/index_types.hpp>
  - <https://raw.githubusercontent.com/pisa-engine/pisa/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/pisa-engine/pisa/v0.8.2/include/pisa/topk_queue.hpp>
  - <https://raw.githubusercontent.com/pisa-engine/pisa/a45fcc4/include/pisa/topk_queue.hpp>
  - <https://github.com/pisa-engine/pisa>
  - <https://github.com/pisa-engine/pisa/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/pisa-engine/pisa/releases>
  - <https://github.com/quickwit-oss/search-benchmark-game/tree/master/engines/pisa-0.8.2>
  - <https://github.com/quickwit-oss/search-benchmark-game/tree/master/engines>
  - <https://raw.githubusercontent.com/quickwit-oss/search-benchmark-game/HEAD/engines/pisa-0.8.2/Dockerfile>
  - <https://raw.githubusercontent.com/quickwit-oss/search-benchmark-game/HEAD/engines/pisa-0.8.2/Makefile>
  - <https://raw.githubusercontent.com/quickwit-oss/search-benchmark-game/HEAD/engines/pisa-0.8.2/CMakeLists.txt>
  - <https://raw.githubusercontent.com/quickwit-oss/search-benchmark-game/HEAD/engines/pisa-0.8.2/details.json>
  - <https://raw.githubusercontent.com/quickwit-oss/search-benchmark-game/HEAD/engines/pisa-0.8.2/tools/do_query.cpp>
  - <https://raw.githubusercontent.com/quickwit-oss/search-benchmark-game/HEAD/engines/pisa-0.8.2/tools/build_index.cpp>
  - <https://raw.githubusercontent.com/quickwit-oss/search-benchmark-game/HEAD/engines/lucene-10.4.0/src/main/java/DoQuery.java>
  - <https://raw.githubusercontent.com/quickwit-oss/search-benchmark-game/HEAD/engines/tantivy-0.26/src/bin/do_query.rs>
  - <https://raw.githubusercontent.com/quickwit-oss/search-benchmark-game/HEAD/results.json>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/pisa-engine/pisa`) · [data/wave9/enrich/raw/github_com_pisa_engine_pisa.json](../../../data/wave9/enrich/raw/github_com_pisa_engine_pisa.json) (enrichment confidence 0.8)

</details>
