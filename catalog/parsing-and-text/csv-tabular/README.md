# CSV and tabular data

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md)</sub>

**What these beat:** pandas read_csv, csv-parser libs the benchmark names  
**18 entries:** 4 tier A · 0 tier B · 12 tier C · 2 tier D · 18 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Sep**](nietras-sep.md) | Zero-allocation, SIMD-vectorized .NET CSV/TSV parser built to beat CsvHelper on throughput. | **A** | C# | MIT | 🟢 active |
| 2 | [**Vince's CSV Parser**](vincentlaucsb-csv-parser.md) | RFC 4180 C++ CSV reader/writer with mmap, SIMD and speculative parallel parsing; beats fast-cpp-csv-parser and rapidcsv on large-file ETL. | **A** | C++ | MIT | 🟢 active |
| 3 | [**go-simdcsv**](nnnkkk7-go-simdcsv.md) | AVX-512 SIMD CSV parser for Go; drop-in encoding/csv replacement, faster only on unquoted data. | **A** | Go | MIT | 🟢 active |
| 4 | [**Fast C++ CSV Parser**](ben-strasser-fast-cpp-csv-parser.md) | Single-header C++11 typed CSV reader; beats vincentlaucsb/csv-parser on single-worker raw reads of files around 30 MB. | **A** | C++ | BSD-3-Clause | 🟡 stale |
| 5 | [**DuckDB (CSV reader)**](duckdb-duckdb.md) | In-process OLAP SQL engine that queries CSV files directly, beating pandas read_csv + groupby on large files. | **C** | C++ | MIT | 🟢 active |
| 6 | [**Polars**](pola-rs-polars.md) | Rust DataFrame engine with lazy query optimization and SIMD execution; \~45x faster CSV writing than pandas. | **C** | Rust | MIT | 🟢 active |
| 7 | [**xan**](medialab-xan.md) | CLI CSV toolkit with a SIMD parser and built-in expression language; faster single-threaded select than xsv, Polars, DuckDB. | **C** | Rust | Unlicense | 🟢 active |
| 8 | [**qsv**](dathere-qsv.md) | CLI data-wrangling toolkit that computes CSV summary stats far faster than pandas describe, no DataFrame required. | **C** | Rust | MIT | 🟢 active |
| 9 | [**libxlsxwriter**](jmcnamara-libxlsxwriter.md) | ANSI C write-only XLSX library; same API family as Python XlsxWriter, about 4.4x faster than it on a 200k-cell sheet. | **C** | C | BSD-2-Clause | 🟢 active |
| 10 | [**vroom**](r-lib-vroom.md) | Lazy, ALTREP-backed delimited-file reader for R; indexes then reads on demand, beating base R's read.delim/readr/data.table. | **C** | R | MIT | 🟢 active |
| 11 | [**XLSX I/O (xlsxio)**](brechtsanders-xlsxio.md) | C library that streams .xlsx worksheet values through expat; its Python wrapper reads about 5.8x faster than openpyxl read-only. | **C** | C | MIT | 🟢 active |
| 12 | [**zsv (zsv+lib)**](liquidaty-zsv.md) | SIMD C CSV parser/CLI beating DuckDB and Polars on read throughput, with a slow correct fallback for nonstandard quoting. | **C** | C | MIT | 🟢 active |
| 13 | [**simd-csv (Rust crate)**](medialab-simd-csv.md) | SIMD-accelerated Rust CSV reader/writer family beating the csv crate on throughput, gains data-dependent. | **C** | Rust | MIT | 🟢 active |
| 14 | [**zsv-ruby**](sebyx07-zsv-ruby.md) | Ruby native-extension binding to the zsv C library; drop-in CSV stdlib replacement, 5-6x faster. | **C** | Ruby | MIT | 🟢 active |
| 15 | [**frawk**](ezrosent-frawk.md) | JIT-compiled AWK dialect in Rust with SIMD CSV/TSV parsing; runs AWK scripts several times faster than gawk and mawk. | **C** | Rust | MIT OR Apache-2.0 | 🟡 stale |
| 16 | [**cisv**](sanix-darker-cisv.md) | SIMD-accelerated C CSV parser/writer (AVX-512/AVX2) beating csvkit and PapaParse; monorepo now deprecated. | **C** | C | MIT | 🔴 abandoned |
| 17 | [**vcflib (vcfputtogetheragain)**](vcflib-vcflib.md) | Plain C VCF tool merging overlapping records into multi-allelic records; claimed \~200x faster than vcflib's own zig vcfcreatemulti. | **D** | C | MIT | 🟢 active |
| 18 | [**libcsv**](rgamble-libcsv.md) | Small streaming ANSI-style C CSV reader/writer with callbacks; only speed evidence is a 2012 Ruby wrapper beating Ruby's csv. | **D** | C | LGPL-2.1-or-later | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
