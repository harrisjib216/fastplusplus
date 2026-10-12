# Zig (csv-zero): LangArena CSV::Parse

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig csv-zero field iterator plus std.fmt.parseFloat in LangArena CSV::Parse; 2.3x faster than the best C/C++ row, mostly from float conversion.

| | |
|---|---|
| **Beats** | C and C++ CSV parsing: best C/C++ row is C/Clang prod at 2.223 s, a hand-written scalar quote-tracking byte loop (c/src/csv.c) that copies each numeric field into a stack buffer and calls glibc strtod; the C++ test (cpp/src/csv_parse.cpp) uses the header-only lazycsv parser and calls std::stod on a std::string copy of each trimmed cell. |
| **Claimed result** | Zig 0.974 s (ReleaseSafe) vs C/Clang 2.223 s, C++/Clang++ 2.348 s, C++/G++ 2.543 s and C/Gcc 2.572 s (prod, -O2): about 2.3x faster than the best C/C++ row (derived from page data). The -O3 -march=native rows are no faster (C/Gcc/Unsafe 2.378 s, C++/Clang++/Fast 2.396 s, C/Clang/Fast 2.422 s, C++/G++/Fast 2.645 s), so Zig leads the best -O3 row by about 2.4x (derived). Zig/Unchecked (ReleaseFast) is 0.585 s; Rust (simd-csv) 0.881 s and Odin/Default 1.789 s also beat every C/C++ row. Earlier monthly runs show a similar lead: 2.24x on 2026-08-14, 2.18x on 2026-09-03, 1.96x on 2026-09-18 (Zig 0.16.0; derived from the results files). |
| **Workload** | Parse a generated 100,000-row CSV (70 timed iterations, generation untimed) whose quoted text columns contain commas, doubled quotes and a literal backslash-n character pair (no embedded line breaks), extract three unquoted float columns per row (fields 1, 3 and 5) and average them. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 7 3800X 8-Core Processor, 78 GB RAM, x86_64 Linux (results file 2026-10-05, host kostya-ms7c37; the run's change note says the host moved from Ubuntu to Arch Linux) |
| **Compiler and flags** | C/C++ (c/Makefile, cpp/Makefile; versions from the results file): Clang 22.1.8 and GCC 16.0.1 20260322 (trunk r16-8246, Ubuntu package build), libstdc++ (no -stdlib flag), -std=c++20 for C++. Headline 'prod' rows (make -j prod): -O2 -DNDEBUG -fstack-protector-strong -fno-omit-frame-pointer, linked with -Wl,-z,relro,-z,now -Wl,--gc-sections (not -O3, no -march). 'Fast': -O3 -march=native -mtune=native -DNDEBUG -pipe -fstack-protector -ftree-vectorize -funroll-loops. 'Unsafe': -O3 -march=native -ffast-math -fno-stack-protector -fomit-frame-pointer -fvisibility=hidden -fno-trapping-math. 'PGO': -O2 plus -fprofile-instr-use (Clang) or -fprofile-use (GCC). -flto=thin (Fast) and -flto=full (Unsafe) appear only in LDFLAGS while objects are compiled without -flto, so those builds probably get no LTO (inference from cpp/Makefile). All 16 Clang/GCC x C/C++ x prod/Fast/Unsafe/PGO rows were compared (instrumented PGO/Gen rows excluded). Zig: 0.17.0, 'zig build build-zig', which zig/build.zig maps to optimize = .ReleaseSafe (LLVM optimisation with runtime safety checks kept); the target comes from standardTargetOptions with no -Dtarget or -Dcpu in the build command, so it presumably builds for the host CPU (inference from zig/build.zig). The Zig/Unchecked row is ReleaseFast. csv-zero is pinned by commit a687d508 in zig/build.zig.zon. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Why it wins** | Not stated by the suite. The Zig test uses the csv-zero iterator and std.fmt.parseFloat (an Eisel-Lemire style parser), while the C++ test calls std::stod on a std::string copy of each cell, which goes through libc strtod; much of the gap is plausibly float parsing rather than CSV splitting (this agent's inference from reading the sources, not measured). |
| **Adoption** | 41 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/kostya/LangArena) · [benchmark](https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js) |

## Verdict

In LangArena's 2026-10-05 run on an AMD Ryzen 7 3800X (Linux), Zig 0.17.0 in ReleaseSafe parsed a 7.53 MB, 100,000-row CSV 70 times in 0.974 s using csv-zero and std.fmt.parseFloat. The best C/C++ row, C/Clang 22.1.8 at -O2 (a hand-written byte loop with glibc strtod), took 2.223 s, and C++/Clang++ with lazycsv, std::stod and libstdc++ took 2.348 s, so Zig was about 2.3x faster (derived from page data). Every one of the 16 GCC 16 and Clang C/C++ configurations was at least 2.2x slower.

## Use it when

- Zig programs reading large numeric CSV: here csv-zero plus parseFloat reached about 540 MB/s in ReleaseSafe and about 900 MB/s in ReleaseFast on one Ryzen 7 3800X core (7.53 MB per iteration at 13.9 ms and 8.4 ms, derived from page data).
- As evidence when profiling a C or C++ text-to-number pipeline: if strtod or std::stod dominates, replace the float conversion before the tokenizer. libstdc++'s std::from_chars for double is built on fast_float when float and double are IEEE binary32/binary64 (src/c++17/floating_from_chars.cc, USE_LIB_FAST_FLOAT); fast_float itself is another option.
- Well-formed RFC 4180 input with short decimal fields that fit Clinger's fast path (for f64, a mantissa up to 2^53 and a decimal exponent within plus or minus 22), where zero-copy field slices avoid per-field allocation.
- Single-threaded batch parsing of in-memory buffers; peak RSS was 13.1 MB, the same as the C rows (12.7-15.0 MB) and below C++ lazycsv (19.9-21.6 MB).

## Skip it when

- Inside a C or C++ codebase: none of this links in directly. csv-zero can be built as a C library (per its catalogue entry), but the float-conversion win comes from Zig's std.fmt.parseFloat, which you would replace with std::from_chars or fast_float.
- Untrusted or malformed CSV: the csv-zero entry documents a strict-mode hole in which a stray quote inside an unquoted field silently mis-splits fields instead of returning InvalidQuotes. This benchmark also maps any parseFloat error to 0.0 (catch 0.0).
- Inputs that leave the fast path (17-digit values, large exponents, many-digit mantissas): parseFloat falls back to Eisel-Lemire or a slow path, and the suite does not measure how much of the lead survives.
- When you want the fastest row: Rust with simd-csv (0.881 s) beats Zig's ReleaseSafe build (0.974 s) in the same run, and Zig/Unchecked (ReleaseFast) at 0.585 s gives up the runtime safety checks.
- Multi-line quoted fields, CRLF input or ragged rows: the generator writes a literal backslash-n, LF endings and exactly six fields per row, so none of these cases are exercised.

## How it is fast

The suite gives no reason, but its history isolates one. Before commit 4b17587 'unify csv bench' (2026-09-09) the Zig test had no csv-zero: it split the buffer with std.mem.splitScalar on '\n' and ran a scalar per-byte loop that toggled an in_quotes flag, which is the same kind of scan as the current C loop, plus the same std.fmt.parseFloat. That version already ran in 1.03 s (2026-08-14) and 1.028 s (2026-09-03) against 2.28-2.43 s for the C and C++ prod rows. The csv-zero version took 1.119 s on 2026-09-18 with the same Zig 0.16.0, so the SIMD scanner is not where the lead comes from. What both Zig versions share is the float parser. Zig's parseFloat tries convertFast (Clinger's fast path) before Eisel-Lemire. For f64 that path accepts mantissas up to 2^53 and decimal exponents from -22 to 22 (FloatInfo.zig in the last GitHub copy of the Zig tree, which has since moved to Codeberg), so every field here (mantissa below 10^10, exponent -10) is one integer-to-float conversion and one exact division. The C and C++ rows call glibc strtod 300,000 times per iteration, C++ through std::stod on a std::string copy of each cell. fast_float's README measures strtod at 9.10 Mfloat/s (about 110 ns per value) on random [0,1) doubles. At that rate the 21 million timed calls would cost about 2.3 s, the order of the whole C runtime (my estimate: different machine and digit count, not measured here).

## Compared with alternatives

For the parser itself, use the csv-zero entry, whose csv-race harness isolates field splitting against zsv and lazycsv. This row only shows that in a real numeric-CSV job the float conversion, not the splitter, decided the outcome. Among the LangArena text rows it is the one where the gap traces to a standard-library routine (strtod) rather than a container, unlike the Distance::NGram and Etc::Words siblings.

## Integration

| | |
|---|---|
| **Form** | source-drop (benchmark file) using the csv-zero module, fetched by zig build --fetch from build.zig.zon |
| **Dependencies** | csv-zero 0.2.0 pinned at commit a687d508 (zig/build.zig.zon); Zig standard library; the executable also links libc and pcre2-8 for other tests |
| **Minimum toolchain** | Zig 0.17.0 as measured (Zig 0.16.0 in the September runs); the code uses the 0.16+ std.Io.Reader and std.process.Init APIs |
| **Platforms** | Measured on x86-64 Linux (AMD Ryzen 7 3800X). build.zig uses standardTargetOptions with no -Dcpu, so the build presumably targets the host CPU; csv-zero picks its SIMD width at compile time from the target and has a scalar fallback |
| **Thread safety** | Not documented; the iterator mutates its reader and cached bitmask, and the benchmark is single-threaded |
| **Drop-in for the baseline** | no |

## Gotchas

- Correction to the record: the 2026-08-14 and 2026-09-03 leads (2.24x and 2.18x) were measured before commit 4b17587, with a hand-written Zig splitter instead of csv-zero, a different C parser (per-line parse_csv_line) and a checksum of 194814688. The current test's checksum, 1071523081, also hashes the CSV text. My Python replay of the generator reproduces both checksums as 84 runs (14 warm-up plus 70 timed) over identical data, so the workload did not change, but only the 2026-09-18 and 2026-10-05 runs measure csv-zero. Those older runs support the float-parsing explanation rather than the SIMD-library one.
- C++ baseline bug hidden by the checksum: lazycsv's row.cells(1, 3, 5) returns [x, z, y], but cpp/src/csv_parse.cpp assigns z = cells[2] (column 5) and y = cells[1] (column 3). The checksum adds the three averages, so the swap goes undetected; timing is unaffected.
- The C++ and C baselines are weak choices rather than broken ones. std::stod copies each trimmed cell into a std::string (short enough for SSO) and calls strtod, while the C loop copies each field into a 64-byte stack buffer for strtod. Neither uses std::from_chars or fast_float. The -O3 -march=native C/C++ rows (2.378-2.645 s) and the PGO rows (2.443-2.592 s) are no faster than -O2, which is consistent with time spent inside libc rather than in compiled loops (inference).
- Harness check, no timing flaw found: the Zig, C and C++ harnesses all reset the LCG, run 20% of the iterations as warm-up, reset again and time the loop with a monotonic clock (std.Io.Clock .awake, clock_gettime CLOCK_MONOTONIC, std::chrono::steady_clock). There is one measurement per configuration and no variance figure, and ReleaseSafe safety checks cost Zig 66% here (0.974 s against 0.585 s for ReleaseFast).

## Known shortcomings

- A library comparison (SIMD csv-zero plus parseFloat against a scalar C loop with strtod and lazycsv plus std::stod), not the language; no multi-line fields in the workload.
- The 2.24x (2026-08-14) and 2.18x (2026-09-03) leads predate commit 4b17587 'unify csv bench' (2026-09-09): those runs used a hand-written scalar Zig splitter rather than csv-zero, an older C parser and checksum 194814688, so only the 2026-09-18 and 2026-10-05 runs measure csv-zero; a Python replay reproduces both checksums on the same data. The scalar Zig splitter already took 1.03 s against 2.28-2.43 s for C, so the lead is std.fmt.parseFloat's Clinger fast path against glibc strtod and std::stod, not SIMD scanning. The C++ baseline swaps y and z; the checksum sums averages and hides it, timing unaffected.

## Caveats and trade-offs

Library comparison: the suite pins a different CSV parser per language (README: 'for library-based (JSON, Base64, CSV), I use the best practical option for each language'), SIMD csv-zero for Zig against a scalar hand-written C loop and lazycsv for C++, with different float parsers, so the result says nothing about Zig code generation; a C/C++ build with a SIMD CSV scanner and fast_float would be the fair comparison. The workload has no multi-line fields (the '\\n' in the generator is a literal backslash and n). The Zig prod build is ReleaseSafe with safety checks on and presumably host-CPU code generation (inference), against generic x86-64 C/C++ prod builds; the -march=native C/C++ rows still lose. The sibling Rust row of this test is in the wave sys file (batch-29, tier C). LangArena calls itself 'a subjective benchmark' and says AI tools helped translate the tests between languages. One measurement per test and configuration (no variance reported), although the harness checks each run's checksum against run.js. The headline C/C++ 'prod' rows are -O2 with hardening flags, but the -O3 -march=native Fast and Unsafe rows and the PGO rows also lose. Ratios are derived from the results file, not stated by the suite. Rows were picked as text tests where a non-C row beats every C and C++ row; most other text tests go the other way (Base64::Encode and Base64::Decode, where C is about 3x faster than Rust; Distance::Jaro is a tie). [retier] Enricher: the 2026-08-14 and 2026-09-03 leads (2.24x and 2.18x) predate commit 4b17587 'unify csv bench' (2026-09-09) and were measured with a hand-written scalar Zig splitter, an older C parser and checksum 194814688, so only the 2026-09-18 and 2026-10-05 runs measure csv-zero; a Python replay reproduces both checksums on the same data. The scalar splitter already took 1.03 s against 2.28-2.43 s for C, so the lead is std.fmt.parseFloat's Clinger fast path against glibc strtod and std::stod, not SIMD scanning. The C++ baseline swaps y and z; the checksum hides it and timing is unaffected.

Peak RSS about 13 MB, similar to C. Depends on the third-party csv-zero package.

## Maintenance

The MIT-licensed suite is active (41 stars, monthly reruns, last commit 2026-10-08 per the verifier), and this test was rewritten on 2026-09-09. The Zig file is copyable but is a measurement, not a component. Its csv-zero dependency is young, single-author and pinned to a commit, and its strict-validation hole is still open per the csv-zero entry.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** The harness meets A methodology (zig/src/csv_parse.zig, c/src/csv.c, cpp/src/csv_parse.cpp; flags in zig/build.zig, c/Makefile and cpp/Makefile; versions and the Ryzen 7 3800X in the results file), but the two sides do not run the same algorithm: Zig uses the SIMD-accelerated csv-zero library plus std.fmt.parseFloat, against a hand-written scalar C byte loop with glibc strtod and C++ lazycsv with std::stod. same_algorithm false caps the language-level comparison at C (unequal-work precedent, as for the sibling Rust CSV::Parse row in batch-29).
- **Verifier notes:** Downgrade A to C: numbers match the CSV::Parse-runtime entries, but the win is the SIMD csv-zero library plus Zig's Eisel-Lemire float parser against a scalar C loop with strtod and lazycsv with std::stod (same_algorithm false), as for the Rust CSV::Parse row. Workload corrected: no embedded line breaks. Shortcomings to record: library comparison not a language win; arguably D under the crippled-baseline precedent (naive scalar C against a tuned SIMD library) but held at C because the C++ side also uses a CSV library; single run; subjective suite. Metadata checks out (MIT, 41 stars, last commit 2026-10-08).
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-35 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/csv_parse.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/csv.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/csv_parse.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/build.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/build.zig.zon>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/main.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/benchmark.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-zero/HEAD/README.md>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/commits>
- **Sources the enricher read:**
  - <https://github.com/kostya/LangArena/commits/master/zig/src/csv_parse.zig>
  - <https://github.com/kostya/LangArena/commit/4b17587>
  - <https://github.com/kostya/LangArena/issues?q=is%3Aissue>
  - <https://github.com/kostya/LangArena/issues/3>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/csv_parse.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/1d5f7f6/zig/src/csv_parse.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/1d5f7f6/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/csv.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/csv_parse.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/csv_parse.hpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/rust/src/benchmarks/csv_parse.rs>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/build.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/build.zig.zon>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/main.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/benchmark.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/zig/src/helper.zig>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/src/benchmark.cpp>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/src/benchmark.c>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/cpp/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/c/Makefile>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/run.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-10-05-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-18-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-09-03-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/kostya/LangArena/HEAD/results/2026-08-14-kostya-ms7c37.js>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-zero/a687d508e57b1cd62dc1efa7d90f268055e1ca46/src/iterator.zig>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-zero/a687d508e57b1cd62dc1efa7d90f268055e1ca46/README.md>
  - <https://raw.githubusercontent.com/ziglang/zig/master/lib/std/fmt/parse_float.zig>
  - <https://raw.githubusercontent.com/fastfloat/fast_float/main/README.md>
  - <https://raw.githubusercontent.com/gcc-mirror/gcc/master/libstdc++-v3/src/c++17/floating_from_chars.cc>
  - <https://raw.githubusercontent.com/ziglang/zig/master/lib/std/fmt/parse_float/convert_fast.zig>
  - <https://raw.githubusercontent.com/ziglang/zig/master/lib/std/fmt/parse_float/FloatInfo.zig>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:zig/kostya/langarena#csv-parse`) · [data/wave14/enrich/raw/lang_zig_kostya_langarena_csv_parse.json](../../../data/wave14/enrich/raw/lang_zig_kostya_langarena_csv_parse.json) (enrichment confidence 0.7)

</details>
