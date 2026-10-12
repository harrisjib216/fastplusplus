# Ladybug

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Embedded columnar Cypher graph database (the continuation of Kuzu), about 2x lower geomean read-query latency than a server Neo4j.

| | |
|---|---|
| **Beats** | Neo4j Community 2025.12.1 (Cypher over Bolt, Python driver) |
| **Claimed result** | Ladybug 0.21.1 has lower mean latency than Neo4j 2025.12.1 on 26 of 30 queries; README: geometric mean of per-query Neo4j/Ladybug latency ratios 2.02x (recomputed from the table: 2.02x, derived from page data). Largest wins: q20 393.291 ms vs 14.118 ms (27.86x), q30 1055.151 ms vs 88.728 ms (11.89x), q4 3.141 ms vs 0.382 ms (8.22x), q1 4.098 ms vs 1.171 ms (3.50x). Ladybug is slower on 4 queries: q7 23.600 ms vs 1.508 ms (0.06x), q22 7.134 ms vs 2.618 ms (0.37x), q12 7.708 ms vs 3.888 ms (0.50x), q27 3.492 ms vs 2.518 ms (0.72x). README also reports a 1.59x geometric-mean advantage over Kuzu 0.11.3. |
| **Workload** | 30 custom Cypher queries (n-hop traversals with varied cardinalities, filters, projections) on the LDBC SNB SF1 graph (3,181,724 nodes, 17,256,038 relationships), mean latency per query with pytest-benchmark, Python clients; Ladybug 0.21.1 in-process versus Neo4j 2025.12.1 in a VM. |
| **Metric** | latency |
| **Hardware** | Apple M5, 10 logical CPUs, 24 GiB RAM, macOS 26.6.2; Neo4j ran in a native-arm64 Colima VM with 4 CPUs and 10 GiB RAM, embedded engines ran natively. |
| **Compiler and flags** | Prebuilt ladybug 0.21.1 Python package (library build compiler and flags not stated); harness: uv run --frozen pytest benchmark_query.py --benchmark-min-rounds=5 --benchmark-warmup-iterations=5 --benchmark-disable-gc, pytest-benchmark 5.2.3, Python 3.13.14; ANALYZE and six ART secondary indexes enabled. |
| **Adoption** | 1.8k stars |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/LadybugDB/ladybug) · [benchmark](https://github.com/prrao87/graph-benchmark-ldbc) |

## Verdict

In prrao87's custom 30-query suite on LDBC SNB SF1, run on an Apple M5 (10 CPUs, macOS) through pytest-benchmark, Ladybug 0.21.1 (prebuilt Python wheel, in-process, all cores, six extra ART indexes) had lower mean latency than Neo4j 2025.12.1 (Bolt, 4-vCPU VM, ID constraints only) on 26 of 30 queries, a 2.02x geometric mean of Neo4j/Ladybug ratios, and lost on q7, q12, q22 and q27. The Ladybug side was set up by Ladybug's maintainer and re-run on 2026-09-30 against Neo4j numbers from 2026-09-03, so this is a configuration comparison, not an equal-resource one.

## Use it when

- Analytical multi-hop Cypher over a few million nodes and tens of millions of edges inside one process (LDBC SNB SF1 scale: 3.2M nodes, 17M relationships)
- Scan-heavy aggregate pattern queries (counts over all comments or all reply chains) on a multi-core machine, where intra-query parallelism pays off
- Applications, notebooks or agent-memory stores that want a graph store as a library file rather than a server to run and connect to
- Projects already on Kuzu that need a maintained successor after Kuzu's archival
- Mixed graph plus vector or full-text retrieval in one embedded engine

## Skip it when

- Highly selective point traversals from a single node ID: Neo4j won q7 (1.5 ms vs 23.6 ms) and q22 (2.6 ms vs 7.1 ms) in the cited suite
- Many concurrent writers or a shared multi-client server: one read-write Database object per file per process, and concurrent write transactions are off by default (enableMultiWrites = false)
- Workloads that need a stable on-disk format and release cadence: 0.19 to 0.21.2 shipped within about two months, with storage-version fixes and a 0.21 two-hop regression
- Schema-free graphs where labels and properties are not known in advance
- Tiny point lookups on a many-core box with default threading: a user report shows 26 of 30 suite queries got faster when limited to 1 thread

## How it is fast

Data lives in columnar disk storage grouped into node groups of 2^17 rows, and relationships are stored as CSR (compressed sparse row) adjacency lists, so a hop is a sequential scan of a neighbour range instead of pointer chasing through record stores. The query processor is vectorized (2048-value vectors) and factorized, keeps intermediate many-to-many results unflattened, and runs pipelines on all cores by default (maxNumThreads = 0). Floating-point columns are compressed with the vendored ALP library, and query kernels have runtime-dispatched SIMD paths (LBUG_ENABLE_SIMD, on by default).

## Compared with alternatives

Pick Ladybug when the queries are Cypher path patterns over a graph; the relational engines in this category (DataFusion, Umbra, Velox) answer SQL joins and have no CSR adjacency storage. No separate Kuzu entry is catalogued, so this record also stands in for Kuzu 0.11.3, which the same suite puts 1.59x behind Ladybug 0.21.1 by geomean.

## Integration

| | |
|---|---|
| **Form** | shared lib or static lib (liblbug, plus a single-file amalgamated header); prebuilt Python, Node.js, Rust, Go, Java and Swift packages |
| **Dependencies** | none external at runtime beyond threads; vendored third_party sources include ANTLR4 runtime, RE2, zstd, LZ4, Snappy, Brotli, miniz, Parquet/Thrift, mbedTLS, yyjson, utf8proc, Roaring bitmaps, SimSIMD, ALP, fast_float, spdlog and cpp-httplib |
| **Minimum toolchain** | C++20, CMake 3.15+ |
| **Platforms** | Linux and macOS on x86-64 and aarch64 (prebuilt liblbug), Windows CLI builds for x86-64 and arm64, WebAssembly |
| **Thread safety** | Connection is documented as thread-safe and many Connections can share one Database; only one read-write Database object may open a given path (multiple read-only ones are allowed); a single writer by default |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the headline: the two biggest wins over Neo4j (q20 27.86x, q30 11.89x) come from intra-query parallelism. A user's re-run of the same suite in issue #1117 shows q20 at 14.31 ms with 16 threads but 103.68 ms with 1 thread, and q30 at 119.17 ms vs 750.87 ms, while Neo4j was confined to a 4-vCPU Colima VM and Ladybug used all 10 native cores. The harness also builds six ART secondary indexes for Ladybug (including Comment.length, which q4 and q20 filter on, and Person first/last name) while Neo4j gets only ID uniqueness constraints, and Neo4j's ingest loads CSV through polars without date parsing so its q8 converts birthday strings with date() per row.
- Ladybug's timings are in-process Python calls with polars conversion; Neo4j's go over Bolt to a VM, so the per-query floor differs (Neo4j's fastest query is 1.22 ms), which inflates the many 1.4x-4x wins on 1-3 ms queries.
- Open bug #1117 (since 0.21.0, still on 0.21.2 and main): a two-hop traversal whose middle nodes change node group decodes a whole CSR header per change, 67x slower than expected (189 ms vs 2.8 ms) in the reporter's test; the benchmarked 0.21.1 is affected. Other open bugs: a segfault on periodic read-only reconnection (#1007) and an ALP DOUBLE crash during checkpoint (#998).
- throwOnWalReplayFailure defaults to false since 0.19.0: after a crash with a torn WAL tail the database opens silently without the unreplayable tail. SECURITY.md still lists 0.14.x and 0.15.x as the supported versions.

## Known shortcomings

- Downgraded B to C: in prrao87/graph-benchmark-ldbc (LDBC SF1, 30 queries, Apple M5; 26 of 30 wins vs Neo4j, geomean 2.02x) the Ladybug maintainer adsharma committed the Ladybug side of the harness (ART secondary indexes, ANALYZE, prepared statements) while Neo4j got only ID constraints in a 4-CPU VM over Bolt; the benchmark author was a Kuzu Inc. DevRel; arXiv 2609.23315 numbers are snippet only. Continuation of the archived Kuzu codebase (Kuzu folded as duplicate).
- Enricher: the biggest wins come from parallelism (a user re-run in issue #1117 has q20 at 14.31 ms on 16 threads vs 103.68 ms on 1, q30 119.17 vs 750.87) while Neo4j was capped at 4 vCPU in a VM; the harness gives Ladybug ART indexes (Comment.length for q4/q20, Person names) but Neo4j only ID constraints with birthday stored as a string; the Bolt-to-VM floor (Neo4j's fastest query 1.22 ms) inflates small-query wins. Open bug #1117: 0.21.x two-hop traversal regression affects the benchmarked 0.21.1; default throwOnWalReplayFailure=false silently drops a torn WAL tail.

## Caveats and trade-offs

Same codebase as kuzudb/kuzu (README: 'formerly known as Kuzu'; a community continuation of the archived repo, not a GitHub-level fork), so the evidence overlaps the Kuzu entry. The benchmark is a single-author 8-star repo by prrao87, a former Kùzu Inc. AI/DevRel engineer with commits in the Kuzu history Ladybug inherited (to Jul 2025), and Ladybug's maintainer adsharma authored the Ladybug-side harness commits ('Use secondary indexes on ladybugdb where necessary', 'ladybug: use table stats', 'ladybug: use prepared statement', 'Update ladybug to 0.20.2'), so the Ladybug configuration is vendor-tuned. The baseline is not equally set up: Ladybug gets six ART secondary indexes on filtered properties (Place.name, Tag.name, Person.firstName, Person.lastName, Person.birthday, Comment.length) plus ANALYZE, while Neo4j gets only ID uniqueness constraints and no secondary property indexes, and Neo4j ran over Bolt in a Colima VM limited to 4 CPUs and 10 GiB while Ladybug ran in-process and multi-threaded on the native 10-CPU machine; no controlled cold caches. Custom 30-query workload that the README says is not an official LDBC result. Ladybug was re-run on 2026-09-30 (it was benchmarked at 0.20.2, 0.20.4, 0.21.0 and 0.21.1, with Q30 swinging from 480.406 ms in 0.21.0 to 88.728 ms in 0.21.1) while Neo4j and Kuzu values come from the 2026-09-03 run. Result conversion is inside the timed region; results are asserted. Open Ladybug issue #1117 reportedly concerns a two-hop traversal regression since 0.21 (not checked here). An arXiv preprint 2609.23315 ('Graph Memory for LLM Agents: At What Cost?', search snippet only, page blocked) reportedly gives Ladybug 3.97 ms vs Neo4j 6.92 ms query-latency geometric mean at 1.02M nodes; not verified, no artifact found. Prebuilt wheel compiler and flags not stated. [retier] q20 14.31 ms on 16 threads vs 103.68 ms on 1 thread (issue #1117 re-run); Neo4j capped at 4 vCPU, birthday stored as string, Bolt-to-VM floor about 1.22 ms; benchmarked 0.21.1 has the two-hop traversal regression (#1117).

Same design as Kuzu: embedded in-process, declared schema, Cypher, columnar storage, vectorized and factorized joins, multi-threaded. Neo4j is a transactional server, so the comparison is analytical read queries only. Bindings for Python, Node.js, Rust, Go, Swift and Java live in separate repositories.

## Maintenance

Very actively maintained (the 20 newest commits are all dated 2026-10-11, many of them catalog, WAL-replay and storage correctness fixes) and MIT-licensed, but the engine is a fast-moving 0.x with an open 0.21 traversal regression, so pin a release and re-check your own queries on upgrade.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** graph-benchmark-ldbc (ladybugdb/benchmark_query.py, ladybugdb/build_graph.py, results/ladybug-0.21.1.txt) is public code on an Apple M5, but Ladybug is a prebuilt wheel without stated compiler or flags, so not A; the single-author 8-star suite is not well-known or peer-reviewed, and its Ladybug-side setup (ART secondary indexes, ANALYZE/table stats, prepared statements, version bumps) was committed by Ladybug's maintainer adsharma, so the measurement is not independent: C.
- **Verifier notes:** README numbers verified against results/ladybug-0.21.1.txt and results/neo4j-2025.12.1.txt (26/30 wins, 2.02x and 1.59x geomeans recomputed exactly). Downgraded B to C: Ladybug's maintainer tuned the Ladybug side of the harness and Neo4j got no secondary indexes and a 4-CPU VM; record these as shortcomings. Same codebase as the Kuzu entry; orchestrator may fold one into the other.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-91 (wave 6); enricher w6 pair-012
- **Pages the verifier opened:**
  - <https://github.com/prrao87/graph-benchmark-ldbc>
  - <https://github.com/prrao87/graph-benchmark-ldbc/commits/main>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/README.md>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/results/kuzu-0.11.3.txt>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/results/neo4j-2025.12.1.txt>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/results/ladybug-0.21.1.txt>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/kuzu/benchmark_query.py>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/kuzu/README.md>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/neo4j/README.md>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/neo4j/benchmark_query.py>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/neo4j/query.py>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/neo4j/build_graph.py>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/ladybugdb/benchmark_query.py>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/ladybugdb/build_graph.py>
  - <https://github.com/LadybugDB/ladybug>
  - <https://github.com/LadybugDB/ladybug/commits/main>
  - <https://github.com/LadybugDB/ladybug/commits/main?author=prrao87>
- **Sources the enricher read:**
  - <https://github.com/LadybugDB/ladybug>
  - <https://raw.githubusercontent.com/LadybugDB/ladybug/HEAD/README.md>
  - <https://raw.githubusercontent.com/LadybugDB/ladybug/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/LadybugDB/ladybug/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/LadybugDB/ladybug/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/LadybugDB/ladybug/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/LadybugDB/ladybug/HEAD/AGENTS.md>
  - <https://raw.githubusercontent.com/LadybugDB/ladybug/HEAD/security/threat_model.md>
  - <https://raw.githubusercontent.com/LadybugDB/ladybug/HEAD/src/include/main/lbug.h>
  - <https://raw.githubusercontent.com/LadybugDB/ladybug/HEAD/src/include/main/database.h>
  - <https://raw.githubusercontent.com/LadybugDB/ladybug/HEAD/src/include/main/connection.h>
  - <https://github.com/LadybugDB/ladybug/issues/1117>
  - <https://github.com/LadybugDB/ladybug/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/LadybugDB/ladybug/commits/main>
  - <https://github.com/LadybugDB/ladybug/releases>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/README.md>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/ladybugdb/README.md>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/ladybugdb/benchmark_query.py>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/ladybugdb/build_graph.py>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/ladybugdb/query.py>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/neo4j/benchmark_query.py>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/neo4j/build_graph.py>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/neo4j/query.py>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/results/ladybug-0.21.1.txt>
  - <https://raw.githubusercontent.com/prrao87/graph-benchmark-ldbc/HEAD/results/neo4j-2025.12.1.txt>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/ladybugdb/ladybug`) · [data/wave6/enrich/raw/github_com_ladybugdb_ladybug.json](../../../data/wave6/enrich/raw/github_com_ladybugdb_ladybug.json) (enrichment confidence 0.7)

</details>
