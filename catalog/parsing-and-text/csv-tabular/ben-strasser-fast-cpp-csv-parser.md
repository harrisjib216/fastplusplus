# Fast C++ CSV Parser

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-3-Clause` · 🟡 stale

> Single-header C++11 typed CSV reader; beats vincentlaucsb/csv-parser on single-worker raw reads of files around 30 MB.

| | |
|---|---|
| **Beats** | vincentlaucsb/csv-parser (Vince's CSV Parser) |
| **Claimed result** | Single-parser-worker raw read, median real time (csv-parser vs fast-cpp-csv-parser): 500K clean count 146.5 ms vs 81.8 ms (\~1.8x, derived from page data), read 164.9 ms vs 82.8 ms (\~2.0x, derived from page data); 500K quoted count 197.2 ms vs 118.8 ms (\~1.7x, derived from page data), read 223.5 ms vs 136.2 ms (\~1.6x, derived from page data); 5M clean read 1,087 ms vs 944.2 ms (\~1.15x, derived from page data). Reversed at 5M rows elsewhere: 5M clean count 547.6 ms for csv-parser vs 881.5 ms, 5M quoted count 665.4 ms vs 1,153 ms, 5M quoted read 1,140 ms vs 1,164 ms (csv-parser ahead). csv-parser also wins both materialization tables (e.g. 5M clean 739.6 ms vs 2,105 ms) and the positional-read table once it uses 4+ speculative parser workers (500K clean spec-4 76.6 ms vs fast-cpp SPSC 88.0 ms). |
| **Workload** | Reading a generated 8-column CSV (id,city,state,category,amount,quantity,flag,note) of 500K or 5M rows with clean and quoted-field profiles, in a count-rows loop and a full read loop into std::string cells, warm cache, single parser worker, Google Benchmark median real time. |
| **Metric** | throughput |
| **Hardware** | 12th Gen Intel Core i5-12400 (12 logical CPUs, \~2.5 GHz), Windows 11 Home 25H2, Samsung 990 EVO SSD |
| **Compiler and flags** | MSVC 19.50 (Visual Studio 2026), Windows SDK 10.0.26100.0, C++20, CMake Release configuration (MSVC Release defaults; no extra optimization flags in benchmarks/CMakeLists.txt), /arch:AVX2 added to CMAKE_CXX_FLAGS by csv-parser's top-level CMakeLists.txt on MSVC (in csv-parser's own directory scope, so the fast-cpp benchmark executables in benchmarks/ probably build without it), CSV_ENABLE_THREADS=ON, Google Benchmark 1.8.5 |
| **Adoption** | 2.4k stars |
| **Last commit** | 2025-02-02 |
| **Links** | [repository](https://github.com/ben-strasser/fast-cpp-csv-parser) · [benchmark](https://github.com/vincentlaucsb/csv-parser/blob/master/benchmarks/README.md) |

## Verdict

In csv-parser's own Windows comparison (MSVC 19.50, C++20 Release, i5-12400, Google Benchmark median of 5 repetitions, warm 8-column files of about 29 MB at 500K rows and 297 MB at 5M rows), fast-cpp-csv-parser read 500K rows in 81.8-136.2 ms versus 146.5-223.5 ms for csv-parser (about 1.6-2.0x) and won the 5M clean read (944 ms vs 1,087 ms), but lost the 5M count runs, the 5M quoted read, both materialization tables and the positional-read table once csv-parser used 4 or more parser workers. Its throughput was flat at about 315-350 MB/s across sizes, whereas csv-parser's count path rose from about 196 MB/s at 500K to 543 MB/s at 5M (derived from the result JSON), so the 500K wins mostly reflect csv-parser's fixed per-reader start-up cost rather than a faster parsing loop.

## Use it when

- Fixed-schema files (known column names and types) where you want typed values straight into local variables with a tiny loop.
- Large single-line-per-record files read sequentially on one core, where a 1 MiB block prefetch thread helps hide disk latency.
- Projects that need a vendorable single header with no dependencies and a C++11 floor.
- Pipelines that read char\* columns and do their own parsing (std::from_chars etc.) to stay zero-copy.
- Simple TSV or custom-separator files where quoting can be compiled out entirely for extra speed.

## Skip it when

- Any file that may contain quoted fields with embedded line breaks: these are unsupported and throw escaped_string_not_closed (README FAQ, open issue #92).
- Variable or unknown column counts, or schemas only known at runtime: column count is a template parameter (open issues #140, #119).
- Numeric data where exact double round-tripping matters: the built-in float parser is not correctly rounded (open issue #122).
- Multi-core throughput on large files: csv-parser's 4-8 worker speculative mode and its mmap count path beat it at 5M rows, and SIMD parsers such as zsv go much faster.
- Projects wanting an actively maintained library: last commit 2025-02-02, 21 open issues, no tagged release (issue #99).

## How it is fast

Input is read unbuffered (setvbuf _IONBF) in 1 MiB blocks into a 3 MiB buffer, and a background std::thread prefetches the next block while the caller parses the current one (double buffering that overlaps disk I/O with parsing). Lines and fields are tokenized in place by writing NUL terminators into the buffer, so char\* columns cost no copy or allocation. Trimming, quoting, overflow and comment handling are template policy classes resolved at compile time, so disabled features add no branches. There is no SIMD: separators and newlines are found with plain byte loops (about 315-350 MB/s in the cited run, derived from the result JSON).

## Compared with alternatives

Pick it over zsv or DuckDB's CSV reader when you want a dependency-free single header that hands typed values of a known schema to C++ code; pick zsv for SIMD throughput, dynamic columns and multiline quoted fields, and DuckDB when you want SQL or columnar loading rather than a row loop.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the C++ standard library; uses std::thread, so GCC builds need -lpthread unless CSV_IO_NO_THREAD is defined |
| **Minimum toolchain** | C++11 (README; developed with GCC 4.6.1). Open issue #77 reports a build failure with VS 2017 in C++17 mode; the 2026 comparison builds it with MSVC 19.50 in C++20. |
| **Platforms** | any platform with a C++11 compiler; no SIMD or architecture-specific code; handles \n and \r\n line endings and skips a UTF-8 BOM |
| **Thread safety** | Not documented beyond: each reader owns one background I/O thread (started only when the input exceeds 2 MiB), and a custom ByteSourceBase::read may be called from either thread but never concurrently. Treat each reader as single-consumer; separate readers share no globals in csv.h. |
| **Drop-in for the baseline** | no |

## Gotchas

- Float parsing is hand-rolled (digit accumulation plus repeated multiplication for exponents), not correctly rounded: issue #122 (open since 2021) shows 9.855536508 read as 9.8555365080000054 instead of 9.8555365080000001, although the README says the input 'is rounded to the next floating point'. Read char\* and use std::from_chars or strtod when exactness matters.
- Empty numeric cells parse silently as 0 (the integer and float parsers accept an empty string, and a lone '-' or '.' also yields 0); there is no NaN/inf support.
- The current csv.h limits a line to block_len = 2^20 bytes (about 1 MiB) and throws line_length_limit_exceeded, while the README and the exception text still say 2^24-1.
- Defaults are not RFC 4180: CSVReader&lt;N&gt; uses no_quote_escape (quoted commas split columns) and trims spaces and tabs; you must opt into double_quote_escape&lt;',','"'&gt;, and quoted fields keep inner spaces because trimming happens before unquoting.

## Known shortcomings

- Wins only the 500K and 5M clean-read rows of csv-parser's benchmarks/README.md (a competitor's harness); loses the 5M count, 5M quoted read, materialization and 4+ worker reads. Harnesses differ (fast-cpp copies all 8 fields). Flags given only as 'CMake Release'; the harness fetched master unpinned. Last commit 2025-02-02.
- Enricher: the float parser is not correctly rounded (issue #122: 9.855536508 reads as 9.8555365080000054), empty numeric cells silently become 0, the real line limit is 2^20 (block_len) not the README's 2^24-1, and the default reader has no quote handling. In the csv-parser harness the csv-parser targets get /arch:AVX2 through a PUBLIC compile option while the standalone fast-cpp binary does not; the result JSON shows the 500K wins mostly measure csv-parser start-up cost (csv-parser count 196 MB/s at 500K vs 543 MB/s at 5M, fast-cpp flat at 315-350 MB/s).

## Caveats and trade-offs

The benchmark is in the competitor's repo (csv-parser author), not the project's own, and it was written to show where csv-parser wins: fast-cpp-csv-parser wins only at 500K rows and the 5M clean read, and loses the 5M count rows (clean and quoted), the 5M quoted read, both materialization tables and the 4+ worker positional-read comparison. The two read harnesses do different work: fast-cpp's 'count rows' still copies all 8 fields into std::string per row while csv-parser's count only iterates rows, and fast-cpp's 'read' copies all 8 fields while csv-parser takes 3 string_views by column name; fast-cpp is configured with double_quote_escape and trim_chars even on the clean profile. Windows/MSVC only, one machine, Google Benchmark overhead included. The fast-cpp-csv-parser source is fetched with FetchContent GIT_TAG master, so no commit is pinned (the repo has not changed since 2025-02-02). Optimization flags are implied by CMake Release rather than listed. fast-cpp-csv-parser cannot parse quoted line breaks (multiline profile skipped). The project's own README has no numbers, and no measurement against the guessed std::getline baseline was found (dfglib's csvPerformanceRuns.md only compares it with dfglib's own readers). [retier] Third-party competitor harness (vincentlaucsb/csv-parser benchmarks/README.md, 'CMake Release', unpinned master): wins only the 500K and 5M clean-read rows and loses 5M count, 5M quoted read, materialization and 4+ worker reads; the csv-parser targets get /arch:AVX2 through a PUBLIC compile option while the standalone fast-cpp binary gets no AVX2, and the result JSON shows the 500K wins mostly measure csv-parser start-up cost (csv-parser count 196 MB/s at 500K vs 543 MB/s at 5M, fast-cpp flat at 315-350 MB/s). Harnesses differ (fast-cpp copies all 8 fields). Correctness: the float parser is not correctly rounded (issue #122), empty numeric cells silently become 0, the real line limit is 2^20 (block_len) not 2^24-1, and the default reader has no quote handling. Last commit 2025-02-02.

Single header csv.h. Column count and types are fixed at compile time (read_header plus read_row with typed arguments), so there is no dynamic row model. Does not parse quoted fields with embedded line breaks (the comparison marks the multiline profile unsupported). Optional background I/O thread (needs pthread with GCC, or CSV_IO_NO_THREAD). The caller owns row materialization and any parallelism.

## Maintenance

Stale (last commit 2025-02-02, open bugs on float precision and multiline fields unanswered) but BSD-3-Clause, a single 1,200-line header and easy to vendor; the cited numbers come from the competing project's harness, which copies all 8 fields into std::string for fast-cpp while csv-parser takes string_views, and which compiles csv-parser's binaries with /arch:AVX2 (a PUBLIC option on the csv target) while the standalone fast-cpp binary that produced the raw-throughput table gets no AVX2 flag.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The csv-parser benchmarks/README.md raw-throughput table carries every number in the record; the harness is public (vincentlaucsb/csv-parser benchmarks/fast_cpp_csv_parser_read_bench.cpp vs benchmarks/csv_parser_read_bench.cpp, built by benchmarks/CMakeLists.txt with Google Benchmark v1.8.5), compiler MSVC 19.50, flags derivable from public build files (CMake Release config, /arch:AVX2 added by csv-parser's top-level CMakeLists.txt on MSVC), CPU i5-12400. Third-party (competitor) run, so A holds.
- **Verifier notes:** Numbers check out row by row; the record omitted that fast-cpp also loses the 5M quoted count and read, now added. Count/read harnesses are not identical (fast-cpp copies all 8 fields into std::string, csv-parser does not), which if anything handicaps fast-cpp. Metadata verified on github.com: BSD-3-Clause LICENSE, 2.4k stars, 438 forks, not a fork, last commit 2025-02-02 (stale). The category's baseline list names 'csv-parser libs the benchmark names', so baseline_in_list could be argued true; left unchanged.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** csv-parser benchmarks (verifier); enricher code and result reading
- **Pages the verifier opened:**
  - <https://github.com/vincentlaucsb/csv-parser/blob/master/benchmarks/README.md>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/fast_cpp_csv_parser_read_bench.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/csv_parser_read_bench.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/CMakeLists.txt>
  - <https://github.com/ben-strasser/fast-cpp-csv-parser>
  - <https://github.com/ben-strasser/fast-cpp-csv-parser/commits>
  - <https://raw.githubusercontent.com/ben-strasser/fast-cpp-csv-parser/HEAD/README.md>
  - <https://raw.githubusercontent.com/ben-strasser/fast-cpp-csv-parser/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/ben-strasser/fast-cpp-csv-parser/HEAD/README.md>
  - <https://raw.githubusercontent.com/ben-strasser/fast-cpp-csv-parser/HEAD/csv.h>
  - <https://raw.githubusercontent.com/ben-strasser/fast-cpp-csv-parser/HEAD/LICENSE>
  - <https://github.com/ben-strasser/fast-cpp-csv-parser/issues>
  - <https://github.com/ben-strasser/fast-cpp-csv-parser/issues/122>
  - <https://github.com/ben-strasser/fast-cpp-csv-parser/issues/115>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/fast_cpp_csv_parser_read_bench.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/csv_parser_read_bench.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/results/500000_rows/clean/csv_parser_read_bench.json>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/results/500000_rows/clean/fast_cpp_csv_parser_read_bench.json>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/results/5000000_rows/clean/csv_parser_read_bench.json>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/results/5000000_rows/clean/fast_cpp_csv_parser_read_bench.json>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/include/internal/CMakeLists.txt>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/ben-strasser/fast-cpp-csv-parser`) · [data/wave3/enrich/raw/github_com_ben_strasser_fast_cpp_csv_parser.json](../../../data/wave3/enrich/raw/github_com_ben_strasser_fast_cpp_csv_parser.json) (enrichment confidence 0.8)

</details>
