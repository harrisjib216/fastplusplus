# FastLanes

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🟢 active

> CWI's columnar file format with SIMD-friendly lightweight encodings; decodes 7-44x faster than Parquet, DuckDB and BtrBlocks in its paper.

| | |
|---|---|
| **Beats** | Apache Parquet (Snappy and Zstd variants, written and read with DuckDB v1.2's Parquet implementation) and DuckDB v1.2's native storage format; also BtrBlocks |
| **Claimed result** | Decoding (Table 4, i4i.4xlarge Ice Lake): on average 29x faster than DuckDB's native format, 43x faster than Parquet+Snappy, 44x faster than Parquet+Zstd and 7x faster than BtrBlocks. Totals: 16.32 ms vs 483.45, 712.55, 731.45 and 115.43 ms. Encoding is not faster: FastLanes v0.1 took 81,341.63 ms against 5,867.07 (Parquet+Snappy), 6,927.52 (Parquet+Zstd) and 20,347.82 (DuckDB). That makes it about 14x, 12x and 4x slower, and only about 1.4x faster than BtrBlocks (111,091.39 ms) (derived from page data). Random access (Table 5; text says 315x/416x/800x/5x): first-value retrieval takes 0.14 ms, 315.62x faster than Parquet+Snappy, 413.66x than Parquet+Zstd, 813.57x than BtrBlocks and 5.96x than DuckDB. |
| **Workload** | Decoding/encoding throughput (rowgroups/sec) across real-world datasets and a single-value random-access latency micro-benchmark, comparing the FastLanes file format against DuckDB, Parquet+Snappy, Parquet+Zstd, and BtrBlocks. |
| **Metric** | throughput |
| **Hardware** | All experiments on AWS EC2 i4i.4xlarge: Intel Xeon (Ice Lake), 16 vCPUs, 128 GiB RAM (paper Sec. 4; no CPU model number given). Only the expression-pool micro-benchmark (Table 7, footnote 4) ran on an Apple MacBook Pro M4. |
| **Compiler and flags** | The paper does not name the compiler (the artifact README lists 'gcc / clang'; the current FastLanes CMakeLists defaults to clang++ on non-Windows). FastLanes is built as a CMake Release. The SIMD micro-benchmark (Table 6) used -O3, -O3 -mavx2 and -O3 -mavx512dq. |
| **Adoption** | 713 stars |
| **Last commit** | 2026-04-22 |
| **Links** | [repository](https://github.com/cwida/FastLanes) · [benchmark](https://www.vldb.org/pvldb/vol18/p4629-afroozeh.pdf) |

## Verdict

The paper (VLDB 2025) ran everything on one AWS i4i.4xlarge (Ice Lake, compiler not named, AVX-512 build) over 36 Public BI tables. Total decode time was 16.32 ms for FastLanes against 483 ms for DuckDB v1.2's native format, 713 ms and 731 ms for Parquet+Snappy and Parquet+Zstd (written and read through DuckDB v1.2), and 115 ms for BtrBlocks. First-value access took 0.14 ms (6x to 814x faster), while encoding was 4-14x slower than DuckDB and Parquet. Caveat: the artifact's FastLanes timers cover only get_chunk() on a first rowgroup that is already opened and read into memory, whereas Parquet and DuckDB random access was timed as a full DuckDB 'LIMIT 1' query. The paper's own Parquet+Snappy decode total also differs about 3x between Table 4 (712 ms) and Table 6 (2,071 ms), so treat the multipliers as upper bounds.

## Use it when

- Write-once, scan-many analytics on flat tables (integers, decimals, doubles, strings, dates) where decode CPU dominates and much slower writes are acceptable.
- Your own C++ vectorized engine or research prototype that can consume 1024-value vectors, including still-compressed ones such as dictionary codes in transposed order, to try compressed execution.
- Denormalized data with correlated columns, like the Public BI corpus: FastLanes stored 172 MB, Parquet+Snappy was 41% larger, BtrBlocks 18% larger and Parquet+Zstd 2% larger.
- Point reads of one vector from a rowgroup that is already loaded, where decompressing a whole Parquet page with Snappy/Zstd is the bottleneck.
- Builds that must stay portable across x86-64 and ARM without hand-written SIMD while still gaining from wider vector units.

## Skip it when

- Write-heavy or ETL ingestion. v0.1 encoding took 81.3 s against 5.9 s for Parquet+Snappy and 20.3 s for DuckDB in the paper. The writer also loads the whole table into memory before encoding.
- When you need interop. There is no Arrow, Parquet, DuckDB, Spark or Polars reader or writer. The Python API only exports CSV. In July 2025 the maintainer said HTTP range reads and a DuckDB extension were on the roadmap, not implemented.
- Nested or ML-style data. LIST, STRUCT and MAP appear in the type list, but a list&lt;bigint&gt; column aborts with UNREACHABLE (issue #67, open). The paper lists nested types and schema evolution as future work.
- Normalized or synthetic data such as TPC-H, where Parquet+Zstd compressed 15.3% smaller than FastLanes in the paper.
- Long-term archival or production storage. The format is pre-1.0 (the code's version tag is v0.1.4), the GitHub repo has no releases or tags, and readers accept only a whitelist of five version tags. Crashes on real datasets were reported in 2025 (issue #55, since fixed).

## How it is fast

Every encoding works on 1024-value vectors in the authors' Unified Transposed / 1024-bit interleaved layout (VLDB 2023 'FastLanes Compression Layout'), which removes data dependencies so decode kernels, delta included, are plain scalar loops the compiler auto-vectorizes (no intrinsics; the paper measured AVX-512 builds about 40% faster than SSE). 'Expression encoding' cascades these light operators (e.g. dictionary codes then FFOR bit-packing) and adds multi-column compression that reuses codes or dictionaries across correlated columns, reaching Zstd-class ratios without a heavyweight decompressor. Decoding is vector-at-a-time into L1-sized buffers, and the writer picks each column's expression by trying a fixed pool on a few sampled vectors per rowgroup (paper: 'three-way' sampling; code default 7 vectors).

## Compared with alternatives

Pick FastLanes over BtrBlocks when you want vector-granular decoding, a better compression ratio, or non-x86 targets; the paper says BtrBlocks needs AVX2/AVX-512. Prefer Vortex (which has DuckDB and DataFusion integrations, per its maintainer on HN) or Lance when ecosystem support matters more than peak decode speed. Use ALP, from the same authors and embedded in FastLanes, if you only need a float codec inside your own format.

## Integration

| | |
|---|---|
| **Form** | static lib by default, built with CMake (FetchContent from the dev branch); shared lib via FLS_BUILD_SHARED_LIBS. Bindings: pyfastlanes on PyPI, fls-rs for Rust. |
| **Dependencies** | none external. FlatBuffers is vendored in-tree, and the ALP and FSST codecs are in-tree. GoogleTest is fetched only for tests. |
| **Minimum toolchain** | C++20 and CMake 3.22+. Clang 13+ is the default on Linux and macOS. GCC 11+ and MSVC have been accepted since April 2026 (PR #69), but the maintainer has said Clang is preferred for predictable auto-vectorization (issue #61). |
| **Platforms** | Portable C++ with no intrinsics. CI builds on Linux x86-64 and aarch64, macOS 15 and Windows x64 (Clang and MSVC); the Windows-on-ARM job is disabled. The paper benchmarked only x86 (Ice Lake). |
| **Thread safety** | not documented. From the source: RowgroupReader::get_chunk decodes into, and returns references to, the reader's own mutable expression buffers, and TableReader keeps a reference to its Connection. So use a separate reader per thread. |
| **Drop-in for the baseline** | no |

## Gotchas

- At configure time CMake reads /proc/cpuinfo and adds -march=native (x86 without AVX-512DQ) or -mavx512dq to CMAKE_CXX_FLAGS. A binary built on one host can therefore crash with an illegal instruction on an older CPU. FastLanes also compiles its own sources with -Wall -Werror -Wpedantic, so a newer compiler that adds warnings can break the build.
- The footer is not inlined by default (CFG::Footer::IS_INLINED = false). The reader then looks for a sidecar table_descriptor.fbb in the same directory. Call inline_footer() to get a single self-contained file; the README's Python and Rust examples do this, but the C++ example does not.
- read_csv() takes a directory, not a file. The directory must contain a .csv file and a schema.json, and the default delimiter is '|'. to_fls() throws if the output path already exists.
- Decoded vectors stay in the transposed (UTL) order. To get the original row order you must apply the 1024-entry selection vector, or ask the decoder to restore the order with a gather step.

## Known shortcomings

- The 29/43/44/7x figures are decode only; encoding is 4-14x slower than DuckDB/Parquet. Compiler unnamed and CPU given only as 'Xeon (Ice Lake)'; Parquet was read through DuckDB 1.2.
- The speed comparison is not like-for-like: FastLanes times only get_chunk() on a row group already in memory, while Parquet/DuckDB are timed as a full DuckDB LIMIT 1 query. The paper disagrees with itself (Parquet+Snappy decode 712 ms in Table 4 vs 2,071 ms in Table 6), so the multipliers are upper bounds. The whole table is held in RAM before writing.
- No interop (no Arrow/Parquet/DuckDB reader; Python exports only CSV; no HTTP range reads). list&lt;bigint&gt; columns abort (#67, open); the footer is a separate file by default; CMake adds -march=native. Pre-1.0 format (v0.1.4), no GitHub releases, PyPI last updated 2025-05.

## Caveats and trade-offs

These are the authors' own VLDB 2025 numbers (Afroozeh & Boncz, CWI). The artifact repo cwida/fastlanes-vldb2025 reproduces them. Parquet was run through DuckDB v1.2's Parquet reader and writer, not parquet-cpp/Arrow. The headline multipliers are decoding-only: FastLanes v0.1 encoding is 4-14x slower than DuckDB and Parquet and beats only BtrBlocks, which the authors attribute to an unoptimized encoder. Random access was simulated with LIMIT 1 queries on Parquet and DuckDB and with full block decoding for BtrBlocks. The table and text multipliers differ slightly (413.66x vs 416x, 813.57x vs 800x).

Encoding (compression) speed in the v0.1 code path is explicitly unoptimized per the paper; the file format only recently reached format-stability (v0.36+), so tooling/ecosystem support lags far behind Parquet; zero external dependencies but currently no true random-access-by-row-position support (block decode still required).

## Maintenance

This is MIT-licensed CWI research code that moves slowly: the last commit was 2026-04-22 (GCC/MSVC support), there are no GitHub releases, and pyfastlanes was last published on 2025-05-30. It is easy to vendor via FetchContent, but the format is pre-1.0 and has no ecosystem readers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification A, tier now B.
- **Tier reason:** This is a peer-reviewed VLDB 2025 paper, and its public artifact repo (cwida/fastlanes-vldb2025: master_script.py, scripts/, plus FastLanes CMake targets benchmark_decompression_time and benchmark_random_access) reproduces Tables 3-6 against Parquet, DuckDB and BtrBlocks. It is not A: the paper never names the compiler (the artifact README says 'gcc / clang'), and the CPU is given only as 'Intel Xeon (Ice Lake)' on an i4i.4xlarge with no model number.
- **Verifier notes:** The record's '29x faster decoding/encoding' is overstated: the Table 4 multipliers are for decoding, and FastLanes encoding is slower than Parquet and DuckDB. The record also put Table 5 on the M4, but the M4 footnote belongs to the Table 7 expression-pool experiment. Metadata is confirmed: MIT, 713 stars, last commit 2026-04-22 (active, dev branch).
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://www.vldb.org/pvldb/vol18/p4629-afroozeh.pdf>
  - <https://github.com/cwida/FastLanes>
  - <https://github.com/cwida/FastLanes/blob/dev/CMakeLists.txt>
  - <https://github.com/cwida/fastlanes-vldb2025>
  - <https://github.com/cwida/fastlanes-vldb2025/blob/main/master_script.py>
  - <https://github.com/cwida/fastlanes-vldb2025/blob/main/scripts/run_fastlanes.py>
  - <https://github.com/cwida/fastlanes-vldb2025/blob/main/scripts/helper/system_info.py>
  - <https://github.com/cwida/fastlanes-vldb2025/blob/main/paper_result/decompression_time/public_bi/table_1.tex>
- **Sources the enricher read:**
  - <https://github.com/cwida/FastLanes>
  - <https://github.com/cwida/FastLanes/blob/dev/README.md>
  - <https://github.com/cwida/FastLanes/blob/dev/CMakeLists.txt>
  - <https://github.com/cwida/FastLanes/blob/dev/CHANGELOG.md>
  - <https://github.com/cwida/FastLanes/blob/dev/CLAUDE.md>
  - <https://github.com/cwida/FastLanes/blob/dev/docs/typing_system.md>
  - <https://github.com/cwida/FastLanes/blob/dev/pyproject.toml>
  - <https://github.com/cwida/FastLanes/blob/dev/rust/Cargo.toml>
  - <https://github.com/cwida/FastLanes/blob/dev/src/include/fls/info.hpp>
  - <https://github.com/cwida/FastLanes/blob/dev/src/include/fls/connection.hpp>
  - <https://github.com/cwida/FastLanes/blob/dev/src/connection.cpp>
  - <https://github.com/cwida/FastLanes/blob/dev/src/include/fls/cfg/cfg.hpp>
  - <https://github.com/cwida/FastLanes/blob/dev/src/include/fls/reader/table_reader.hpp>
  - <https://github.com/cwida/FastLanes/blob/dev/src/reader/table_reader.cpp>
  - <https://github.com/cwida/FastLanes/blob/dev/src/include/fls/reader/rowgroup_reader.hpp>
  - <https://github.com/cwida/FastLanes/blob/dev/src/reader/rowgroup_reader.cpp>
  - <https://github.com/cwida/FastLanes/blob/dev/src/reader/csv_reader.cpp>
  - <https://github.com/cwida/FastLanes/blob/dev/src/expression/expression_executor.cpp>
  - <https://github.com/cwida/FastLanes/blob/dev/src/include/fastlanes.h>
  - <https://github.com/cwida/FastLanes/blob/dev/python/bindings/table_reader_binding.cpp>
  - <https://github.com/cwida/FastLanes/blob/dev/benchmark/bench_decompression_time.cpp>
  - <https://github.com/cwida/FastLanes/blob/dev/benchmark/bench_random_access.cpp>
  - <https://github.com/cwida/FastLanes/blob/dev/.github/workflows/cpp.yaml>
  - <https://github.com/cwida/FastLanes/blob/dev/.github/workflows/benchmark.yaml>
  - <https://github.com/cwida/FastLanes/issues/67>
  - <https://github.com/cwida/FastLanes/issues/61>
  - <https://github.com/cwida/FastLanes/issues/55>
  - <https://github.com/cwida/FastLanes/commits/dev>
  - <https://www.vldb.org/pvldb/vol18/p4629-afroozeh.pdf>
  - <https://github.com/cwida/fastlanes-vldb2025>
  - <https://pypi.org/pypi/pyfastlanes/json>
  - <https://news.ycombinator.com/item?id=44671584>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/cwida/fastlanes`) · [data/wave6/enrich/raw/github_com_cwida_fastlanes.json](../../../data/wave6/enrich/raw/github_com_cwida_fastlanes.json) (enrichment confidence 0.85)

</details>
