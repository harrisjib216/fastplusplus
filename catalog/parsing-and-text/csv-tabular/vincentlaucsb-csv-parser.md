# Vince's CSV Parser

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> RFC 4180 C++ CSV reader/writer with mmap, SIMD and speculative parallel parsing; beats fast-cpp-csv-parser and rapidcsv on large-file ETL.

| | |
|---|---|
| **Beats** | fast-cpp-csv-parser (also rapidcsv and Glaze's CSV reader in the same suite) |
| **Claimed result** | Median real time, generated 8-column CSV, own harness. Single-worker comparisons hold only for the 500K inputs (28.7 MB, under the 50 MB speculative-parallel threshold): materialization 156.8 ms vs fast-cpp-csv-parser 218.8 ms (about 1.4x, derived from page data) and materialize plus multi-pass aggregation 215.4 vs 237.1 ms and 262.9 vs 280.7 ms (about 1.1x, derived from page data); rapidcsv DataFrame load 1.48x at 500K multiline (220.4 vs 325.2 ms). The 5M rows (297-445 MB) ran csv-parser with speculative parallel parsing (speculative_parallel_threads=0, auto = 12 hardware threads) against single-threaded baselines: materialization 739.6 vs 2,105 ms (2.8x), quoted 930.6 vs 2,489 ms (2.7x), materialize plus aggregation 1,251 vs 2,252 ms (1.8x) and 1,517 vs 3,090 ms (2.0x), rapidcsv 3.45-4.53x, Glaze 739.6 vs 1,972 ms; the explicit single-worker 5M read took 1,442 ms in the same session. Positional read with 4 speculative workers 702.2 ms vs 915.1 ms (spec-8 605.0 ms). Loses the small raw reads (500K clean count 146.5 vs 81.8 ms, read 164.9 vs 82.8 ms) and the multi-pass-only step on materialized rows (5M clean 479.5 vs 141.6 ms). |
| **Workload** | Google Benchmark median real time on a generated 8-column CSV (id,city,state,category,amount,quantity,flag,note) of 500K and 5M rows in clean, quoted and multiline profiles: raw row count/read, one-pass row materialization, materialize plus multi-pass aggregation, and DataFrame load and load+edit+save against rapidcsv. |
| **Metric** | throughput |
| **Hardware** | 12th Gen Intel Core i5-12400 (12 logical CPUs, about 2.5 GHz), Windows 11 Home 25H2, Samsung 990 EVO SSD |
| **Compiler and flags** | MSVC 19.50 (Visual Studio 2026), Windows SDK 10.0.26100.0, C++20 (Glaze targets C++23), CMake Release configuration (MSVC Release defaults; benchmarks/CMakeLists.txt adds no optimization flags), /arch:AVX2 added as a PUBLIC compile option of the csv library target in include/internal/CMakeLists.txt (so it reaches every benchmark binary that links csv, but not the standalone fast_cpp_csv_parser_\* and glaze_csv_\* binaries), CSV_ENABLE_THREADS=ON, Google Benchmark v1.8.5 via FetchContent; fast-cpp-csv-parser and rapidcsv fetched at unpinned master, Glaze v7.5.0 |
| **Adoption** | 1.1k stars |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/vincentlaucsb/csv-parser) · [benchmark](https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/README.md) |

## Verdict

The author's Google Benchmark suite (median real time, generated 8-column CSV, Windows 11, MSVC 19.50 C++20 Release with /arch:AVX2 on the csv-parser binaries, Core i5-12400) shows csv-parser materializing 500K rows 1.4x faster than fast-cpp-csv-parser and about 1.1x faster with aggregation, but 1.8-2.0x slower on raw count and read; the larger 5M-row leads (2.8x materialize, 1.8-2.0x ETL, 3.45-4.53x vs rapidcsv) were measured with csv-parser's default speculative parallel parsing active (12 workers by inference from code defaults and timings) against single-threaded baselines.

## Use it when

- Real-world CSV with quoted fields, embedded line breaks, ragged rows or unknown delimiters, where fast-cpp-csv-parser throws or needs a fixed column count.
- Large file-backed inputs (above the 50 MB speculative threshold) on a multi-core machine: with 4 to 8 parser workers positional reads beat fast-cpp-csv-parser (5M rows clean 702.2 / 605.0 ms vs 915.1 ms on an i5-12400).
- Runtime schemas: lookup by column name, per-field type checks and conversions, JSON export, without writing a struct per file.
- Load-edit-save table workflows: the DataFrame plus CSVWriter path beat rapidcsv 1.56x on load and 2.2x on load+save at 500K rows with a single parser worker.
- WebAssembly or embedded builds that need a CSV reader without threads (CSV_ENABLE_THREADS=0 keeps the same API).

## Skip it when

- Single-core or small-file raw reads: with one parser worker it is slower than fast-cpp-csv-parser (500K rows count 146.5 vs 81.8 ms, read 164.9 vs 82.8 ms; 5M rows single-worker positional read 1,442 vs 915.1 ms).
- Many repeated passes over materialized rows: lazy CSVRow fields are re-parsed on every get&lt;&gt;, so the multi-pass-only step was 3.4x slower than fast-cpp's pre-converted structs (479.5 vs 141.6 ms at 5M rows); convert once into your own structs.
- Maximum raw scan throughput: its SIMD only skips to the next special byte; C parsers built around SIMD and parallel scanning, such as zsv, report far higher count rates.
- Builds with -fno-exceptions: the library requires C++ exceptions.
- Memory-tight hosts: speculative mode reads chunk_size x worker_count windows (10 MB x 12 workers on a 12-thread CPU), and a vector of CSVRow keeps every referenced 10 MB chunk alive.

## How it is fast

File inputs are memory-mapped and parsed in 10 MB chunks by a background producer thread while the caller consumes rows; rows are lightweight views into shared chunk buffers and fields are only converted when asked. A SIMD skip loop (AVX2, SSE2 or NEON, chosen at compile time) jumps to the next delimiter, quote, LF or CR. Since 5.0.0, files of 50 MB or more are split across workers with speculative parallel parsing after Ge et al., 'Speculative Distributed CSV Data Parsing for Big Data Analytics' (SIGMOD 2019): each chunk guesses its quote state and a validator repairs row fragments when the guess is wrong.

## Compared with alternatives

Pick it over fast-cpp-csv-parser when files may contain quoted line breaks or ragged rows, the schema is only known at runtime, or the file is large and several cores are free; keep fast-cpp-csv-parser for fixed-schema files on one core. Pick zsv when you need the highest raw scan rate from a C library, and DuckDB or Polars when the goal is SQL or dataframe analytics rather than embedding a C++ reader.

## Integration

| | |
|---|---|
| **Form** | single generated header (csv.hpp) or CMake static lib (target csv); also on the Bazel Central Registry |
| **Dependencies** | none external (bundles string-view-lite for pre-C++17 and its classify_scalar conversion code); Threads::Threads when CSV_ENABLE_THREADS is on |
| **Minimum toolchain** | C++11 minimum, C++20 default in CMake (CMake 3.15+); exceptions required; std::optional API needs C++17 and as&lt;T&gt;() needs C++23 std::expected |
| **Platforms** | any C++11 platform with std::thread (or threads disabled); SIMD paths for x86 AVX2/SSE2 and ARM NEON (since 5.1.0), selected at compile time; mmap replaced by ifstream on Emscripten; CI covers g++, clang, MSVC and MinGW |
| **Thread safety** | One CSVReader per consumer thread; it runs its own background parser thread and, for files of 50 MB or more, speculative worker threads. Parallel processing of rows is offered through chunk_parallel_apply and DataFrame helpers; concurrent use of one reader is not documented. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the README labels the materialization, ETL and rapidcsv comparisons as single-parser-worker or single-threaded, but bench_format() leaves speculative_parallel_threads at 0 (auto = std::thread::hardware_concurrency(), 12 on the i5-12400) and the 50 MB threshold, and the 5M-row inputs are 297 MB (clean) to 445 MB (multiline), so at 5M rows csv-parser ran speculative parallel parsing against fast-cpp's one parser thread and rapidcsv's single thread. Timings agree: 5M materialize 739.6 ms vs the explicitly single-worker read 1,442 ms in the same session, while at 500K rows (28.7 MB, below threshold) materialize 156.8 ms matches the single-worker read 154.5 ms. The single-worker gains are the 500K rows: about 1.4x materialize and 1.1x materialize+aggregation over fast-cpp-csv-parser.
- By default rows with missing or extra columns are silently dropped (VariableColumnPolicy::IGNORE_ROW); set THROW or KEEP if data loss matters.
- CSVReader::iterator is an input iterator over chunks that are freed as it advances: std algorithms that need forward iterators are undefined behaviour, get&lt;string_view&gt; is valid only while its CSVRow lives, and parse_unsafe() requires the source string to outlive the rows.
- On MSVC x86 the csv target adds /arch:AVX2 as a PUBLIC compile option, so every consumer is built for AVX2 with no runtime dispatch and will not run on pre-AVX2 CPUs unless CSV_NO_SIMD is set; GCC/Clang only take the AVX2 path when you pass -mavx2/-march (or CSV_FORCE_AVX2), otherwise SSE2 on x86-64.

## Known shortcomings

- Own harness (MSVC 19.50 Release /arch:AVX2, i5-12400, 2026-05-08): the materialize tables compare lazy CSVRow against fast-cpp-csv-parser's eager std::string structs, csv-parser loses the multi-pass step (479.5 vs 141.6 ms on 5M clean) and only the csv-parser binaries get AVX2; single Windows machine. Load range low end is 1.48x, not 1.56x.
- Enricher: the README calls the materialize, ETL and rapidcsv tables single-parser-worker, but bench_format() leaves speculative_parallel_threads=0 (auto, hardware_concurrency 12) with a 50 MB threshold, so the 5M inputs (297-445 MB) ran speculative parallel parsing against single-threaded baselines (5M materialize 739.6 ms vs the explicit single-worker read's 1,442 ms in the same session; the 500K rows, under the threshold, match single-worker timings). True single-worker gains are 500K only: about 1.4x materialize and 1.1x ETL; the 5M claims (2.8x, 1.8-2.0x, 3.45-4.53x vs rapidcsv) are multi-threaded vs single-threaded. /arch:AVX2 is PUBLIC on MSVC with no runtime dispatch.

## Caveats and trade-offs

Project's own benchmarks, one machine, one OS and one compiler (Windows 11, MSVC 19.50), result JSON dated 2026-05-08 while the library has changed since (last commit 2026-10-06), so ordering may shift on GCC/Clang, Linux or newer code. The 'materialization' tables compare different amounts of work: csv-parser pushes CSVRow handles that keep parser-owned buffers alive and parse fields lazily on get&lt;&gt;, while fast-cpp-csv-parser copies six std::string fields and converts two integers per row into a struct (and Glaze deserializes into reflected structs); the cost shows up later, where csv-parser's multi-pass step on materialized rows is 3.4x slower (479.5 ms vs 141.6 ms at 5M clean). The fairer materialize+aggregation table still favours csv-parser, by about 1.1x at 500K rows and 1.8-2.0x at 5M rows. Flag asymmetry: /arch:AVX2 is a PUBLIC option of the csv target, so csv-parser binaries (and both libraries inside csv_parser_fast_cpp_read_bench) build with AVX2 while the standalone fast_cpp_csv_parser_\* and glaze_csv_\* binaries build with the MSVC default ISA. fast-cpp-csv-parser wins the 500K raw read and count tests; csv-parser times grow sublinearly from 500K to 5M rows (count 146.5 to 547.6 ms), so fixed start-up cost dominates the small runs. The rapidcsv comparison pits csv-parser's filename path (memory-mapped reader with its background worker thread on, CSV_ENABLE_THREADS=ON) against rapidcsv's single-threaded Document. Comparison libraries are fetched at unpinned master (fast-cpp-csv-parser, rapidcsv). No comparison against std::getline or any libstdc++/libc++ code was found. 'Likely one of the fastest general-purpose C++ CSV ETL libraries' is the author's wording. Inputs are generated, not real-world data (the README's Kaggle-file timings, such as 1.4 GB in about 0.5 s on warm cache, have no baseline). [retier] Project's own benchmarks on one machine, OS and compiler (Windows 11, MSVC 19.50 Release, /arch:AVX2 as a PUBLIC option of the csv target with no runtime dispatch, so only csv-parser binaries get AVX2; i5-12400; results dated 2026-05-08). The README labels the materialize, ETL and rapidcsv tables single-parser-worker, but bench_format() leaves speculative_parallel_threads=0 (auto = hardware_concurrency, 12) with a 50 MB threshold, so every 5M input ran speculative parallel parsing against single-threaded baselines; the 500K inputs are the only like-for-like rows. The materialization tables also compare different work: csv-parser pushes lazy CSVRow handles while fast-cpp-csv-parser copies six std::string fields and converts two integers per row, and csv-parser's later multi-pass step on materialized rows is 3.4x slower. Same defaults in 92fe668 (5.0.0, 2026-05-08).

Fully RFC 4180-compliant out of the box (embedded newlines, quoted fields), which fast-cpp-csv-parser does not support and which costs raw throughput. Dynamic row model with string-valued fields and optional type conversion rather than compile-time typed columns. Fast paths use memory-mapped files and a speculative parallel parser (after Ge et al., SIGMOD 2019) with a background thread, 10 MB default chunks, so it uses more cores and more memory than a single-threaded streaming reader. C++11 minimum, C++20 recommended; ships a DataFrame and a CSV writer.

## Maintenance

Very actively developed by a single maintainer (v5.4.0 September 2026, last commit 2026-10-06, 1 open issue), MIT-licensed and easy to vendor as one header, but the 5.x speculative parser is only five months old and the published benchmark JSON (2026-05-08) predates releases 5.1-5.4.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** benchmarks/README.md carries every number in the record and the raw Google Benchmark JSON under benchmarks/results/ matches it (e.g. 5M clean materialize median 739.6 ms vs 2,104.5 ms); the harness is public (benchmarks/csv_parser_multi_pass_bench.cpp vs benchmarks/fast_cpp_csv_parser_multi_pass_bench.cpp, csv_parser_fast_cpp_read_bench.cpp, glaze_csv_\*_bench.cpp, dataframe_rapidcsv_roundtrip_bench.cpp, built by benchmarks/CMakeLists.txt), compiler MSVC 19.50, flags recoverable from public CMake files (Release plus /arch:AVX2 as a PUBLIC option of the csv target) and CPU i5-12400 are stated, so A holds.
- **Verifier notes:** Numbers match the README and the tracked result JSON; tier A stands (public harness, MSVC 19.50, Release plus /arch:AVX2 from public CMake files, i5-12400). Record shortcomings: materialization tables compare lazy CSVRow handles with fast-cpp's eager std::string structs (csv-parser then loses the multi-pass-only step 479.5 vs 141.6 ms), AVX2 only on the csv-parser binaries, Windows/MSVC single machine, results from 2026-05-08 code. baseline_in_list set true because the category's baselines are 'csv-parser libs the benchmark names'; metadata (MIT, 1.1k stars, not a fork, last commit 2026-10-06) verified on github.com.
- **Fields the verifier corrected:** `baseline_in_list`, `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** first-party public harness (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/README.md>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/LICENSE>
  - <https://github.com/vincentlaucsb/csv-parser>
  - <https://github.com/vincentlaucsb/csv-parser/commits/master>
  - <https://github.com/vincentlaucsb/csv-parser/tree/master/benchmarks>
  - <https://github.com/vincentlaucsb/csv-parser/tree/master/benchmarks/results>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/include/internal/CMakeLists.txt>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/csv_parser_multi_pass_bench.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/fast_cpp_csv_parser_multi_pass_bench.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/dataframe_rapidcsv_roundtrip_bench.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/csv_parser_fast_cpp_read_bench.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/bench_common.hpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/results/5000000_rows/clean/csv_parser_multi_pass_bench.json>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/results/5000000_rows/clean/fast_cpp_csv_parser_multi_pass_bench.json>
- **Sources the enricher read:**
  - <https://github.com/vincentlaucsb/csv-parser>
  - <https://github.com/vincentlaucsb/csv-parser/releases>
  - <https://github.com/vincentlaucsb/csv-parser/issues>
  - <https://github.com/vincentlaucsb/csv-parser/issues?q=is%3Aissue+is%3Aclosed+label%3Abug>
  - <https://github.com/vincentlaucsb/csv-parser/tree/master/include/internal>
  - <https://github.com/vincentlaucsb/csv-parser/commits/master/include/internal/parser/orchestrator.hpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/README.md>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/include/internal/CMakeLists.txt>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/bench_common.hpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/csv_parser_multi_pass_bench.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/fast_cpp_csv_parser_multi_pass_bench.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/csv_parser_fast_cpp_read_bench.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/csv_parser_read_bench.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/dataframe_rapidcsv_roundtrip_bench.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/include/internal/csv_format.hpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/include/internal/csv_format.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/include/internal/csv_reader.hpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/include/internal/csv_reader.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/include/internal/common.hpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/include/internal/ARCHITECTURE.md>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/include/internal/basic_csv_parser_simd.hpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/include/internal/parser/orchestrator.hpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/include/internal/parser/mmap.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/include/internal/parser/mmap.hpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/92fe668/include/internal/parser/orchestrator.hpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/92fe668/include/internal/common.hpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/92fe668/include/internal/csv_format.hpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/92fe668/benchmarks/csv_parser_multi_pass_bench.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/92fe668/benchmarks/multi_pass_etl.hpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/92fe668/benchmarks/fast_cpp_csv_parser_multi_pass_bench.cpp>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/results/5000000_rows/clean/csv_parser_multi_pass_bench.json>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/results/5000000_rows/clean/csv_parser_fast_cpp_read_bench.json>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/results/5000000_rows/clean/csv_parser_read_bench.json>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/results/5000000_rows/clean/fast_cpp_csv_parser_multi_pass_bench.json>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/results/500000_rows/clean/csv_parser_multi_pass_bench.json>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/results/5000000_rows/multiline/dataframe_rapidcsv_roundtrip_bench.json>
  - <https://raw.githubusercontent.com/vincentlaucsb/csv-parser/HEAD/benchmarks/results/500000_rows/clean/dataframe_rapidcsv_roundtrip_bench.json>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/vincentlaucsb/csv-parser`) · [data/wave3/enrich/raw/github_com_vincentlaucsb_csv_parser.json](../../../data/wave3/enrich/raw/github_com_vincentlaucsb_csv_parser.json) (enrichment confidence 0.8)

</details>
