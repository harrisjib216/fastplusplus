# Rust (LangArena CSV::Parse)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust simd-csv plus core's Eisel-Lemire float parser runs LangArena CSV::Parse 2.5x faster than C and C++ code calling glibc strtod.

| | |
|---|---|
| **Beats** | C and C++ CSV::Parse implementations of the same suite (clang/gcc 'prod' builds) |
| **Claimed result** | LangArena run of 2026-10-05 (AMD Ryzen 7 3800X): CSV::Parse Rust 0.881 s and Zig 0.974 s versus the prod (-O2) builds C/Clang 2.223 s, C++/Clang++ 2.348 s, C++/G++ 2.543 s and C/Gcc 2.572 s, so Rust is about 2.5x faster than C/Clang (derived from page data). The -O3 -march=native Fast and Unsafe C/C++ builds are no faster (C/Gcc/Unsafe 2.378 s, C++/Clang++/Fast 2.396 s, C/Clang/Fast 2.422 s, C++/G++/Fast 2.645 s), so Rust stays about 2.7x ahead of the best -O3 C/C++ row (derived from page data). The fastest rows overall are Zig/Unchecked 0.585 s and Rust/MaxPerf/Unsafe 0.799 s. |
| **Workload** | CSV::Parse test of the LangArena suite (parse generated CSV rows with quoted fields and floats, checksum); seconds; part of 50 tasks across 26 languages. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor with 78 GB, per the 'pc' field of the results file. The run's change note says the host moved from Ubuntu to Arch Linux. The gcc version string is an Ubuntu snapshot package, consistent with the suite's Docker images (README). |
| **Compiler and flags** | Quoted C/C++ rows are 'prod' builds (make -j prod). CFLAGS_PROD in c/Makefile and CXXFLAGS_PROD in cpp/Makefile are -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, linked with -Wl,-z,relro,-z,now -Wl,--gc-sections, with no -march and no LTO; C++ adds -std=c++20. Compilers: clang 22.1.8, and gcc/g++ 16.0.1 trunk r16-8246 (an Ubuntu snapshot package). The Fast rows use -O3 -march=native -mtune=native -ftree-vectorize -funroll-loops with -flto=thin; the Unsafe rows add -ffast-math and -flto=full. Rust 1.99.0 uses cargo build --release with the default release profile from rust/Cargo.toml (opt-level 3, no LTO, no target-cpu flag, no .cargo/config.toml) and the simd-csv 0.13 crate. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | no |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

In LangArena's 2026-10-05 run (AMD Ryzen 7 3800X, Linux), 70 timed passes over 100,000 generated CSV rows took 0.881 s for Rust 1.99.0 (simd-csv 0.13 plus str::parse::&lt;f64&gt;, cargo --release), against 2.223 s for the hand-written C state machine with strtod (clang 22.1.8 at -O2) and 2.348-2.543 s for C++ lazycsv with std::stod. That is about 2.5x over the best C or C++ row of any build configuration (derived from page data); Zig 0.17.0 (csvzero, std.fmt.parseFloat) took 0.974 s.

## Use it when

- Rust tools that parse large in-memory or streamed CSV and convert numeric cells: here 100,000 rows with three float columns took about 12.6 ms per pass on a Ryzen 7 3800X, against about 31.8 ms for the C version (derived from page data).
- Pipelines that need cell boundaries rather than unescaped text, which is what ZeroCopyReader returns; Splitter is faster still if only record boundaries are needed (simd-csv README).
- Records with long cells or wide rows, where the simd-csv README reports the largest gains over the csv crate (about 2-4.7x for its zero-copy reader on most of its test files).
- As a reference point when choosing a language for CSV-to-numbers ingestion: Rust's standard float parser removes the strtod bottleneck that naive C and C++ code hits.

## Skip it when

- As evidence that Rust out-compiles C or C++: the baselines are a byte-at-a-time C loop and lazycsv, both on glibc strtod. No C or C++ row uses fast_float or std::from_chars, although the C++ code is built as C++20, and the -O3 -march=native, -ffast-math and PGO builds are no faster (2.378-2.645 s).
- Inside a C++ codebase: the likely fix is to swap strtod or std::stod for std::from_chars or fast_float (and optionally a SIMD splitter), not to change language. This was not measured by the suite.
- Data with quoted numeric cells or embedded escapes that must be unescaped: ZeroCopyReader returns raw cells, so the benchmark's parse().unwrap() would panic on a quoted number.
- Workloads that need the flexibility of the csv crate (serde integration, flexible record handling): the simd-csv README calls itself less flexible and user-friendly and says worst-case data parses no faster than scalar code.
- Production code copied from the benchmark: 'while let Ok(Some(record))' stops silently at the first CSV error instead of reporting it.

## How it is fast

The speedup comes from two library choices, not from code generation. Rust's str::parse::&lt;f64&gt; is core's dec2flt, an Eisel-Lemire parser with an exact fast path for mantissas up to 2^53 and small powers of ten; every field here is a 10-decimal number below 1, so each conversion should take that path (inference from the dec2flt source and the data format). The C and C++ baselines call glibc strtod: C copies each field into a 64-byte stack buffer, C++ builds a temporary std::string and calls std::stod. simd-csv's ZeroCopyReader also finds delimiters, newlines and quotes with an SSE2 searcher and hands back borrowed cell slices, where the C loop tests every byte. But the cells are 12-20 bytes, the size at which simd-csv's README says the SIMD gain is smallest, and Rust WebAssembly builds without that searcher still beat native C, so scanning is probably the smaller share (inference).

## Compared with alternatives

Unlike the catalogued LangArena same-algorithm rows (Rust slice::sort and Zig pdq on Sort::Self, Nim Binarytrees::Obj), this is a library-choice row. It teaches the same lesson as the Rust serde row from kostya/benchmarks: the parser and float-conversion routine matter more than the language. Pick it as evidence for Rust's standard float parser and simd-csv, not for rustc's code generation.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | simd-csv 0.13.0 (MIT, depends on memchr) as pinned in rust/Cargo.lock; float parsing is core's str::parse::&lt;f64&gt; |
| **Minimum toolchain** | simd-csv 0.13.0 uses edition 2021 and declares no rust-version (crates.io); measured with rustc 1.99.0, default release profile (opt-level 3, no LTO, no target-cpu) |
| **Platforms** | simd-csv 0.13.0 src/searcher.rs has an SSE2 searcher on x86-64 and a NEON searcher on aarch64, and uses memchr's portable Three searcher on every other target, including wasm32 (the README says wasm uses simd128); measured on x86-64 Linux |
| **Thread safety** | Not documented in the sources read; each reader owns its stream state, and the benchmark is single-threaded |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw (crippled baselines): both C and C++ spend their time in glibc strtod. The run does 21 million float conversions (100,000 rows x 3 floats x 70 iterations). C/Clang's 2.223 s is about 106 ns per conversion if conversion took all the time, and its overall rate of about 236 MB/s over about 525 MB of CSV is slow for a byte loop, so conversion rather than CSV scanning most likely dominates (derived from page data; no profile exists). The README says library-based tests use 'the best practical option for each language', but the C++ side, built with -std=c++20, does not use std::from_chars.
- The Rust WebAssembly rows show that SIMD splitting is not what produces the 2.5x. They are built with cargo build --target wasm32-wasip1 --release, where simd-csv 0.13.0 uses memchr's portable searcher instead of its SSE2 code, yet they run 1.226 s (Node), 1.371 s (WasmEdge), 1.462 s (Wasmtime) and 1.626 s (Wasmer), all faster than native C/Clang at 2.223 s.
- No bug behind the timed numbers, but the checksum is weak. Every language must reproduce checksum 1071523081 (run.js), the timer covers only run_all after prepare and a 20% warm-up on both sides (c/src/benchmark.c, rust/src/main.rs), and Rust and C both read cells 1, 3 and 5 as x, z and y. The C++ baseline, however, swaps y and z: row.cells(1, 3, 5) yields columns 1, 3 and 5, but the code takes z from cells[2] (column 5) and y from cells[1] (column 3), assuming cells() returns them in the requested order. The checksum cannot catch this, because it adds the checksums of the three averages, each formatted to 7 decimals, and addition commutes. The swap does not change the work timed. The C baseline also rejects fields of 64 bytes or more, which this data never reaches.
- One timing per configuration per monthly run on one machine (Ryzen 7 3800X; the run note says the host moved to Arch Linux, while gcc 16.0.1 is an Ubuntu trunk snapshot package), with no variance reported. The C and C++ prod builds add -fstack-protector-strong and -fno-omit-frame-pointer at -O2, but the Fast builds without them are no faster.

## Known shortcomings

- A library win (the simd-csv crate plus Eisel-Lemire float parsing against a hand-written C loop with glibc strtod and lazycsv plus std::stod in C++); the -O3 Fast/Unsafe C/C++ rows are no faster (2.378-2.645 s vs Rust 0.881 s).
- Crippled baselines: both C and C++ spend their time in glibc strtod / std::stod with no from_chars or fast_float, about 106 ns per conversion if conversion took all of C's time (derived). The Rust wasm32 builds, which lack simd-csv's SSE2 searcher, still beat native C (1.226-1.626 s vs 2.223 s), so SIMD scanning is not the cause. The C++ baseline swaps y and z (cells[1] and cells[2]); the commutative checksum misses it and timing is unaffected.

## Caveats and trade-offs

This compares libraries and parsers, not languages. The README says library-based tests (JSON, Base64, CSV) use 'the best practical option for each language'. Rust (rust/src/benchmarks/csv_parse.rs) uses the simd-csv 0.13 crate (a pure-Rust SIMD CSV reader, MIT) and str::parse::&lt;f64&gt;. Zig (zig/src/csv_parse.zig) uses the csvzero package and std.fmt.parseFloat. C (c/src/csv.c) is a hand-written byte-at-a-time state machine for quotes and commas that copies each numeric field into a 64-byte stack buffer and calls glibc strtod. C++ (cpp/src/csv_parse.cpp) uses the lazycsv header library and std::stod on a temporary std::string per field. The workload is 3 floats per row, 100,000 rows and 70 iterations (run.js). The prod C/C++ builds use -O2 with hardening while Rust uses opt-level 3, but the -O3 -march=native Fast and Unsafe C/C++ rows are just as slow, so optimisation level does not explain the gap. The suite benchmarked no C or C++ build with a fast float parser (fast_float, std::from_chars) or a SIMD CSV library. Single machine, one monthly run, run by the suite author, who calls the suite subjective. [retier] Enricher: both C and C++ spend their time in glibc strtod / std::stod with no from_chars or fast_float, about 106 ns per conversion if conversion took all of C's time (derived); the Rust wasm32 builds, which lack simd-csv's SSE2 searcher, still beat native C (1.226-1.626 s vs 2.223 s), so SIMD scanning is not the cause. The C++ baseline swaps y and z; the commutative checksum misses it and timing is unaffected. The Zig sibling's enricher notes that LangArena rows before commit 4b17587 (2026-09-09, 'unify csv bench') used older parsers and a different checksum.

Suite is explicitly personal and non-peer-reviewed; implementations were AI-assisted translations; it also publishes 'hack' runs with unsafe flags.

## Maintenance

LangArena is an active MIT suite (41 stars, last commit 2026-10-08, monthly runs, no CSV issues filed) that its author calls subjective; simd-csv is MIT and pre-1.0 (0.14.0 released 2026-09-16, 43,991 downloads), and this row shows the payoff of Rust's Eisel-Lemire float parser over glibc strtod, a harness asymmetry found in this enrichment, more than any compiler advantage.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The harness meets A methodology (c/src/csv.c, cpp/src/csv_parse.cpp and rust/src/benchmarks/csv_parse.rs; flags in c/Makefile, cpp/Makefile and rust/Cargo.toml; clang 22.1.8, gcc 16.0.1, rustc 1.99.0 and the Ryzen 7 3800X in the results file), but the comparison is between libraries, not languages. Rust uses the simd-csv crate with an Eisel-Lemire float parser; C uses a hand-written scalar loop with glibc strtod; C++ uses lazycsv with std::stod. same_algorithm is false and the prod C build is -O2, so the tier stays capped at C (unequal-work precedent).
- **Verifier notes:** The numbers match the CSV::Parse-runtime entries of results/2026-10-05-kostya-ms7c37.js. Metadata checks out: MIT, 41 stars, last commit 2026-10-08. Shortcoming: the win is a library comparison, Rust's simd-csv crate plus an Eisel-Lemire parser against hand-written C with glibc strtod and C++ lazycsv with std::stod, and -O3 C/C++ builds are no faster, so the language is not the reason. D is arguable under the crippled-baseline precedent (naive C loop against a tuned crate); it is held at C because the C++ side also uses a CSV library and the C build is a normal release build. baseline_stdlib is left empty: no -stdlib flag is set, so clang++ presumably used libstdc++, but this was not checked.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-29 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/README.md>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits/master>
  - <https://github.com/kostya/LangArena/tree/master/c>
  - <https://github.com/kostya/LangArena/tree/master/c/src>
  - <https://github.com/kostya/LangArena/tree/master/cpp/src>
  - <https://github.com/kostya/LangArena/tree/master/rust/src>
  - <https://github.com/kostya/LangArena/tree/master/zig/src>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/rust/run>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/src/csv.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/csv_parse.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/rust/src/benchmarks/csv_parse.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/zig/src/csv_parse.zig>
  - <https://crates.io/api/v1/crates/simd-csv>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena/issues?q=csv>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/rust/Cargo.toml>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/rust/Cargo.lock>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/rust/run>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/src/csv.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/c/src/benchmark.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/csv_parse.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/rust/src/benchmarks/csv_parse.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/rust/src/benchmarks/mod.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/rust/src/main.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/rust/src/helper.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/zig/src/csv_parse.zig>
  - <https://crates.io/api/v1/crates/simd-csv>
  - <https://crates.io/api/v1/crates/simd-csv/0.13.0/download>
  - <https://raw.githubusercontent.com/medialab/simd-csv/master/README.md>
  - <https://raw.githubusercontent.com/medialab/simd-csv/master/src/lib.rs>
  - <https://raw.githubusercontent.com/medialab/simd-csv/master/src/searcher.rs>
  - <https://raw.githubusercontent.com/rust-lang/rust/HEAD/library/core/src/num/imp/dec2flt/mod.rs>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:rust/kostya/langarena#csv-parse`) · [data/wave14/enrich/raw/lang_rust_kostya_langarena_csv_parse.json](../../../data/wave14/enrich/raw/lang_rust_kostya_langarena_csv_parse.json) (enrichment confidence 0.75)

</details>
