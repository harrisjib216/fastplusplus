# Parquet Sort (Earnix)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Java` · `Apache-2.0` · 🟡 stale

> Java CLI that sorts a flat Parquet file by one column; 1.12-1.26x faster than DuckDB on TPC-H lineitem.

| | |
|---|---|
| **Beats** | DuckDB |
| **Claimed result** | Time to read, sort and write TPC-H SF10 lineitem.parquet (59M rows) on l_shipdate: DuckDB 1.3.2 20.54s. Parquet Sort takes 18.34s on Corretto 24 (about 1.12x faster), 24.47s on GraalVM 24 JIT (slower) and 16.30s as a GraalVM Native Image (about 1.26x faster). Ratios are derived from page data. |
| **Workload** | Read, sort (bucket sort on l_shipdate), and write a 59-million-row TPC-H SF10 lineitem.parquet file, on AWS EC2 c7i.4xlarge (16 vCPUs, 32GB RAM, gp3 SSD) |
| **Metric** | latency |
| **Hardware** | AWS EC2 c7i.4xlarge, 16 vCPUs, 32GB RAM, Amazon Linux 2023 (kernel 6.1.147), gp3 SSD 16000 IOPS/1000MiB/s, XFS |
| **Compiler and flags** | JVM run (benchmarks.sh): -Xms16g -Xmx16g -XX:+UseParallelGC -XX:+AlwaysPreTouch. Native image (graal_pgo.sh): PGO-instrumented build, then native-image --gc=G1 -march=native -O3 --pgo=default.iprof --no-fallback. JDKs are Corretto 24 and GraalVM 24 (exact builds not stated). DuckDB is the Python package, installed unpinned by pip. |
| **Adoption** | 2 stars |
| **Last commit** | 2025-08-06 |
| **Links** | [repository](https://github.com/Earnix/parquet-sort) · [benchmark](https://github.com/Earnix/parquet-sort#performance-benchmark) |

## Verdict

The benchmark is wall-clock time (bash `time`, including Python or JVM start-up) to read, sort by l_shipdate and write the 59,986,052-row DuckDB-generated TPC-H SF10 lineitem.parquet on one AWS c7i.4xlarge (16 vCPU, 32 GB, gp3 SSD, XFS, Amazon Linux 2023). DuckDB 1.3.2 via Python with default settings (16 threads) took 20.54s. Parquet Sort took 18.34s on Corretto 24 with a 16 GB pre-touched ParallelGC heap (1.12x), 24.47s on GraalVM 24 JIT (0.84x, slower) and 16.30s as a G1, -O3, -march=native PGO native image (1.26x). This is a single first-party run per configuration (benchmarks.sh times each once) with no variance reported, and the sort ran on the radix path rather than the bucket sort the README describes.

## Use it when

- Offline re-sorting of large flat (non-nested) Parquet files by a single int/date/long/double key on a many-core box, where a 10-25% wall-clock cut over DuckDB is worth running a separate tool.
- You have heap for a 4-byte-per-row permutation plus one fully decoded column at a time. The benchmark used a 16 GB pre-touched heap on a 32 GB, 16-vCPU c7i.4xlarge for 60M rows.
- You can build a GraalVM PGO native image (graal_pgo.sh). That configuration had the largest margin (16.30s vs DuckDB 20.54s). Plain Corretto 24 was also faster (18.34s).
- As a readable reference design (about a dozen Java files, Apache-2.0) for column-at-a-time permutation plus parallel row-group file assembly, if you are writing your own JVM Parquet rewriter.

## Skip it when

- Anything production-critical. The README calls it 'a performance demo and not intended for production use'. ParquetForge's README says it is alpha, has had only modest testing and no parquet-compat cross-compatibility testing, and is not recommended where data corruption or loss is unacceptable.
- Sorting so that readers can skip row groups or pages. ParquetForge's README says statistics are not generated in data page headers and that 'pulldown predicates will fail' on its files. Check min/max pruning with your reader before relying on the sorted output.
- Nested/repeated schemas (ParquetForge is 'unstructured parquet only'), INT96 columns as the sort key, multi-column or descending sorts, files over 2^31-1 rows (int row indices with toIntExact), or output codecs other than Snappy (hardcoded).
- Memory- or disk-constrained hosts. Every value of the current column is held in heap (a byte[] object per value for strings). Temporary per-row-group files go in the output file's directory, so peak disk use there is up to about twice the output size. An open PR reports 1m56s total on a 4-core, 16 GB 2020 MacBook Pro, versus 16-18s on the c7i.4xlarge.
- Running on a stock GraalVM JIT. GraalVM 24 in JIT mode took 24.47s, slower than DuckDB's 20.54s.

## How it is fast

First it computes a source-to-destination row permutation from the sort column alone. Non-null int32, int64 and double keys use fastutil's stable parallel indirect radix sort. Everything else (nullable keys, float, binary, boolean) uses fastutil parallelQuickSort with an index comparator. A counting/bucket-sort path exists but is compiled out (`BUCKET_SORT_ENABLED = false`). Then it goes one column at a time: all row-group chunks of that column are decoded in parallel and each value is scattered straight into its destination slot of a full-length primitive array, so rows are never materialized. Each output row group is encoded in parallel into its own temporary Parquet file. The final file is assembled with FileChannel.transferFrom byte copies of those files plus a rebuilt footer with shifted page offsets, so no second encode pass is needed. The fastest configuration also uses a GraalVM native-image build with profile-guided optimization (PGO) trained on a synthetic all-types file (GenPGODataMain).

## Compared with alternatives

Pick it over Apache DataFusion or chDB only when the job is exactly 'sort one flat Parquet file by one key' in a JVM shop and you want a small codebase to adapt. DataFusion and chDB are maintained general SQL engines that can also write sorted Parquet, and the 2023 architecture-performance.fr benchmark this project copies found DuckDB 0.9.2 fastest at this exact task, ahead of chDB 0.15.0 and DataFusion 33.0.0. Vortex and Lance are different file formats, not Parquet rewriters.

## Integration

| | |
|---|---|
| **Form** | source-drop (build a fat-jar CLI with Maven, optionally a GraalVM native-image executable; no published artifact, and ParquetForge is not on Maven Central either) |
| **Dependencies** | ParquetForge (Earnix, built from source; pom pins parquetforge-file 0.0.1-SNAPSHOT), parquet-java (parquet-column / parquet-format-structures, whose shaded fastutil provides the sorts), Guava 33.4.8, slf4j-simple 1.7.33, commons-io, snappy-java |
| **Minimum toolchain** | Java 21 (pom source/target 21; uses List.getFirst), Maven. Benchmarked on Corretto 24 and GraalVM 24; the native build needs GraalVM native-image. |
| **Platforms** | Any JVM platform for the jar. Benchmarked only on x86-64 Linux (Amazon Linux 2023). The native image is built with -march=native, so it is tied to the build machine's CPU features. |
| **Thread safety** | Not documented. It is a CLI that parallelizes internally with parallel streams on the common ForkJoinPool, and runSort can call System.exit. |
| **Drop-in for the baseline** | partial — replaces only DuckDB's COPY (SELECT \* FROM read_parquet(f) ORDER BY col) TO 'out' (FORMAT PARQUET) for one ascending key on flat files. There is no SQL, and nulls sort first where DuckDB defaults to NULLS LAST. |

## Gotchas

- The README says bucket sort is used for l_shipdate, but the only published commit sets BUCKET_SORT_ENABLED = false. The code comment says bucket sort is disabled so the demo is not tuned to the dataset and was worth only about 5%. The author's Show HN post also describes radix/quicksort. So the benchmark sort takes the fastutil radix path, not bucket sort.
- Ordering semantics differ from DuckDB. Nulls sort first in the comparator path (DuckDB's default is ASC NULLS LAST). BINARY and FIXED_LEN_BYTE_ARRAY keys compare as unsigned bytes, so signed decimals stored as FIXED_LEN_BYTE_ARRAY will not sort numerically. INT32/INT64 always compare signed, even with an unsigned logical type. The only unit test sorts 5-row-per-row-group files with no nulls.
- Library use is awkward. Main.runSort calls System.exit(1) if the sort column is missing. main() reads args[2] even when only two arguments are given, so leaving out the column crashes with ArrayIndexOutOfBoundsException instead of printing usage. It also refuses to overwrite an existing output file.
- Reproducibility has drifted. The pom needs parquetforge-file 0.0.1-SNAPSHOT, but benchmarks.sh checks out ParquetForge origin/master, which is now 0.0.5-SNAPSHOT after releases 0.0.1-0.0.4 and API refactors since August 2025. The script as written should no longer resolve its dependency; pin ParquetForge to an early-August-2025 commit (for example 74073acb) or edit the pom.

## Known shortcomings

- Only 1.26x vs DuckDB on TPC-H SF10 sort (Corretto JVM also beats DuckDB 1.12x); needs GraalVM Native with PGO; c7i.4xlarge with no CPU model.
- The benchmarked code used fastutil radix sort (BUCKET_SORT_ENABLED=false), not bucket sort as the README says. Nulls sort first (DuckDB defaults to NULLS LAST); binary keys compare unsigned. ParquetForge is alpha with no page statistics (predicate pushdown fails), a poor fit for sort-for-pruning. The pom pins parquetforge 0.0.1-SNAPSHOT while benchmarks.sh builds master, so the script as written should fail; single commit, stale; memory-heavy; System.exit on a missing column, AIOOBE with 2 args.

## Caveats and trade-offs

First-party single-workload benchmark (the sort only, using bucket sort because l_shipdate has a narrow range). The page names only the EC2 c7i.4xlarge instance type, not a CPU model, and the flags live in the scripts rather than on the page, so it is capped at tier C. The margin over DuckDB is modest: about 1.26x for the PGO-optimized GraalVM Native build and about 1.12x on Corretto 24, while GraalVM 24 JIT is slower than DuckDB. Times are wall-clock via bash time, including Python/JVM startup. The DuckDB side writes through a persistent data.duckdb connection. The author labels the project a performance demo not intended for production.

Only implements sort (not a general query engine); relies on the author's own ParquetForge library; column-wise in-memory reordering means peak memory scales with column size; GraalVM Native build required to beat DuckDB (the plain JIT build was slower than DuckDB in this test).

## Maintenance

Stale: one commit on 2025-08-06 and nothing since, 2 stars, and an unreviewed community PR from 2025-09-19 (indirect radix reorder, reported 1m56s to 1m10s on a laptop). It is Apache-2.0 and small enough to vendor, but it depends on ParquetForge, which is still alpha though active (release 0.0.4 in March 2026) and whose master no longer matches the pinned 0.0.1-SNAPSHOT.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance Benchmark table has exactly the claimed times (DuckDB 1.3.2 at 20.54s; Parquet Sort at 18.34s on Corretto 24, 24.47s on GraalVM 24 and 16.30s on GraalVM Native), and the code is public (benchmarks.sh, graal_pgo.sh, duckdb_benchmark.py). The page names only an EC2 c7i.4xlarge instance, not a CPU model. The JVM and native-image flags appear only in the scripts, and the parquetforge dependency is built from unpinned origin/master. This is first-party with partial methodology, so the tier stays C.
- **Verifier notes:** The numbers match the page exactly. I corrected the caveat that said no flags were stated (they are in benchmarks.sh and graal_pgo.sh). I also noted that Corretto 24 beats DuckDB too, not just the Native build. The metadata (Apache-2.0, 2 stars, last commit 2025-08-06, which makes it stale at about 13.7 months) checks out.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Earnix/parquet-sort>
  - <https://github.com/Earnix/parquet-sort#performance-benchmark>
  - <https://github.com/Earnix/parquet-sort/blob/master/benchmarks.sh>
  - <https://github.com/Earnix/parquet-sort/blob/master/graal_pgo.sh>
  - <https://github.com/Earnix/parquet-sort/blob/master/duckdb_benchmark.py>
- **Sources the enricher read:**
  - <https://github.com/Earnix/parquet-sort>
  - <https://github.com/Earnix/parquet-sort#performance-benchmark>
  - <https://github.com/Earnix/parquet-sort/blob/master/benchmarks.sh>
  - <https://github.com/Earnix/parquet-sort/blob/master/graal_pgo.sh>
  - <https://github.com/Earnix/parquet-sort/blob/master/duckdb_benchmark.py>
  - <https://github.com/Earnix/parquet-sort/blob/master/duckdb_makelineitem_parquet.py>
  - <https://github.com/Earnix/parquet-sort/blob/master/pom.xml>
  - <https://github.com/Earnix/parquet-sort/blob/master/src/main/java/com/earnix/parquet/fastsort/Main.java>
  - <https://github.com/Earnix/parquet-sort/blob/master/src/main/java/com/earnix/parquet/fastsort/SortOrderer.java>
  - <https://github.com/Earnix/parquet-sort/blob/master/src/main/java/com/earnix/parquet/fastsort/ColumnReader.java>
  - <https://github.com/Earnix/parquet-sort/blob/master/src/main/java/com/earnix/parquet/fastsort/ColumnReaderUtil.java>
  - <https://github.com/Earnix/parquet-sort/blob/master/src/main/java/com/earnix/parquet/fastsort/RowGrpWriters.java>
  - <https://github.com/Earnix/parquet-sort/blob/master/src/main/java/com/earnix/parquet/fastsort/GenPGODataMain.java>
  - <https://github.com/Earnix/parquet-sort/blob/master/src/main/java/com/earnix/parquet/fastsort/primitives/SortUtils.java>
  - <https://github.com/Earnix/parquet-sort/blob/master/src/main/java/com/earnix/parquet/fastsort/primitives/IntVals.java>
  - <https://github.com/Earnix/parquet-sort/blob/master/src/main/java/com/earnix/parquet/fastsort/primitives/LongVals.java>
  - <https://github.com/Earnix/parquet-sort/blob/master/src/main/java/com/earnix/parquet/fastsort/primitives/DoubleVals.java>
  - <https://github.com/Earnix/parquet-sort/blob/master/src/main/java/com/earnix/parquet/fastsort/primitives/BaseNullableValueStore.java>
  - <https://github.com/Earnix/parquet-sort/blob/master/src/main/java/com/earnix/parquet/fastsort/primitives/RangedNullableBaseIterator.java>
  - <https://github.com/Earnix/parquet-sort/blob/master/src/test/java/com/earnix/parquet/fastsort/SimpleSortTest.java>
  - <https://github.com/Earnix/parquet-sort/commits/master>
  - <https://github.com/Earnix/parquet-sort/pull/1>
  - <https://github.com/Earnix/parquetforge>
  - <https://github.com/Earnix/parquetforge/blob/master/pom.xml>
  - <https://github.com/Earnix/parquetforge/commits/master>
  - <https://github.com/Earnix/parquetforge/blob/master/parquetforge-base/src/main/java/com/earnix/parquet/columnar/writer/page/InMemPageWriter.java>
  - <https://repo1.maven.org/maven2/com/earnix/parquetforge-file/maven-metadata.xml>
  - <https://news.ycombinator.com/item?id=44810272>
  - <https://architecture-performance.fr/fr/blog/parquet-file-sorting-test>
  - <https://duckdb.org/docs/current/sql/query_syntax/orderby.html>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/earnix/parquet-sort`) · [data/wave6/enrich/raw/github_com_earnix_parquet_sort.json](../../../data/wave6/enrich/raw/github_com_earnix_parquet_sort.json) (enrichment confidence 0.78)

</details>
