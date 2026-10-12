# csv-zero (Zig SIMD CSV field iterator)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig zero-allocation SIMD CSV field iterator; counts fields 1.4-2.6x faster than zsv (C) and 1.1-2.9x faster than lazycsv (C++) in its author's harness.

| | |
|---|---|
| **Beats** | zsv (C library, built from src/c/zsv with 'cc -O3 main.c -lzsv'; labelled 'zsc (c)' in the result CSV) and lazycsv (C++ header library, g++ -O3 -march=native); Rust simd-csv and csv also measured |
| **Claimed result** | csv-race result-all.csv wall times, csv-zero vs zsv (C) vs lazycsv (C++): \~32 MB no-quotes 52 col 6.62 ms vs 14.1 ms vs 18.7 ms; \~696 MB 574 ms vs 1.50 s vs 1.25 s; \~3.2 GB no-quotes 603 ms vs 1.32 s vs 1.65 s (Rust simd-csv 870 ms); \~9.9 GB quoted 7.73 s vs 12.7 s vs 12.1 s. csv-zero is the fastest of the 5 parsers on all 10 files. Ratios are 1.36x to 2.61x against zsv and 1.08x to 2.85x against lazycsv (derived from page data). On the four real-world files csv-zero takes 0.78 to 2.86 ms (775 us on nfl.csv vs zsv 1.78 ms). These files are only 0.72 to 2.6 MB, so the rows include process start-up (the \~1 KB file takes 427 us). Independent corroboration: LangArena results/2026-10-05-kostya-ms7c37.js (AMD Ryzen 7 3800X), CSV::Parse runtime: Zig 0.974 s, best C row C/Clang 2.223 s, C++/Clang++ 2.348 s. The Zig implementation imports csv-zero (zig/build.zig.zon). Rust (0.881 s) and Zig/Unchecked (0.585 s) are faster still. |
| **Workload** | Iterate a whole CSV file and count its fields with a 64 KB input buffer (csv-race harness): four real-world files (nfl.csv, worldcitiespop.csv, GTFS mbta stop-times, game.csv) and generated files from about 1 KB to about 9.9 GB, with and without quoting. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5 PRO 5650U, 30 GB RAM, Linux 6.17.8-arch1-1 (csv-race README) |
| **Compiler and flags** | csv-race at the Dec 2025 results commit: Zig 0.15.2 'zig build --release=fast' (build.zig uses standardTargetOptions, so the default target is the native CPU); zsv harness 'cc -O3 main.c -lzsv' against a manually built, system-installed libzsv whose flags are not stated; lazycsv 'g++ -std=c++17 -O3 -march=native'; Rust 'cargo build --release'. The cc and g++ versions are not stated. Timed with poop -d 10000 (perf counters). The harness moved to Zig 0.16 (May 2026) after the results were taken. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README of csv-zero: SIMD-accelerated scanning, a zero-allocation field iterator that returns slices into one internal buffer, and strict RFC 4180 validation that simplifies fast paths. The author's blog post with details (peymanmo.com) was not opened (host blocked). |
| **Adoption** | 38 stars (csv-zero); companion harness csv-race has 2 stars |
| **Last commit** | 2026-07-29 |
| **Links** | [repository](https://github.com/peymanmortazavi/csv-zero) · [benchmark](https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/result-all.csv) |

## Verdict

The author's csv-race harness (Ryzen 5 PRO 5650U laptop, Linux 6.17, poop for 10 s per command, results from December 2025) counted fields with a 64 KB buffer. Zig 0.15.2 ReleaseFast native csv-zero was fastest of five parsers on all 10 files: 1.36-2.61x faster than zsv (cc -O3 harness against a libzsv of unstated build flags) and 1.08-2.85x faster than lazycsv (g++ -O3 -march=native, mmap). Inputs were almost certainly served from the page cache (30 GB RAM, repeated runs).

## Use it when

- Zig programs that stream large CSV or TSV files and only need to locate fields (counting, filtering, projecting columns) before doing their own conversion.
- Mostly unquoted data with long fields: its largest margin is on the 3.2 GB 52-column unquoted file, 603 ms (about 5.3 GB/s) against 1.32 s for zsv and 1.65 s for lazycsv (derived from page data).
- Memory-constrained scans: peak RSS stays around 820 KB at any input size, while lazycsv memory-maps the input (10.6 GB peak RSS on the 9.9 GB file).
- C or C++ code that wants a small static library for field scanning and accepts the C API's slower path, which the README says still beats the other csv-race parsers.

## Skip it when

- Untrusted or messy CSV where malformed quoting must be rejected: the strict RFC 4180 checks the README promises are not reliable for a quote inside an unquoted field (see gotchas).
- Fields longer than the reader buffer: such a field fails with error.FieldTooLong, and the allocating fallback is only an open proposal (issue #8).
- Record- or struct-oriented code: there is no row type, header handling or type conversion, so for a whole-task parser use zsv, simd-csv or the Rust csv crate.
- Projects pinned to an older Zig: HEAD requires Zig 0.17.0 (build.zig.zon), the benchmark was taken on 0.15.2, and std.Io churn has forced two upgrades in 2026. There are no tagged releases.
- Dense, short, heavily quoted fields: on game.csv, after subtracting each parser's \~1 KB start-up time, lazycsv (about 1.94 ms) beats csv-zero (about 2.43 ms) (derived from page data).

## How it is fast

nextDelimPos loads 64-byte blocks (on AVX2 or AVX-512 targets) as a @Vector, compares them against quote, delimiter and newline splats, and caches the resulting 64-bit mask. Successive fields pop the lowest set bit (count-trailing-zeros plus clear-lowest-bit) without rescanning, and a 256-entry lookup table handles tails shorter than one vector. Inside quoted fields it walks the same mask from quote to quote rather than building a prefix-XOR quote mask. There is no per-field allocation or copying, the buffer is a fixed 64 KB, and statically linked Zig binaries start fast, which matters on the small files in the benchmark.

## Compared with alternatives

The sibling 'Zig (csv-zero): LangArena CSV::Parse' is the same library measured independently on a whole parse-and-strtod task (Zig 0.974 s vs C/Clang 2.223 s), so treat it as corroboration, not an alternative. Over the CLI siblings (hck, tsv-utils, cw) pick csv-zero only when you are embedding field scanning in Zig or C code rather than running a command.

## Integration

| | |
|---|---|
| **Form** | module (Zig package via zig fetch; static or shared C library via zig build) |
| **Dependencies** | none (Zig standard library only) |
| **Minimum toolchain** | Zig 0.17.0 at HEAD (minimum_zig_version); csv-race's pinned commit 733f2a0 needs Zig 0.16; benchmark taken with Zig 0.15.2 |
| **Platforms** | any Zig target; the SIMD width is chosen at comptime from the build target (64 bytes on AVX2, AVX-512 and SVE, 32 on SSE and NEON aarch64, 16 on 32-bit ARM NEON and wasm simd128), with a scalar fallback when vector_length is null |
| **Thread safety** | not documented; the iterator mutates its reader and cached bitmask, so use one iterator per thread |
| **Drop-in for the baseline** | no |

## Gotchas

- Correctness hole in strict mode, found by reading src/iterator.zig and replaying its next()/findQuotedRegion()/nextDelimPos() logic in a Python transcription (not run under Zig). next() sends any quote byte, even one in the middle of an unquoted field, to nextQuotedRegion(), which tosses one byte from the field start. As a result 5'10",x silently yields the field '10 (the 5 and the quote are lost) instead of InvalidQuotes. When the cached 64-byte SIMD mask still holds the next special character, the scan jumps past the stray quote: in id,height\n1,5'10"\n2,6'1"\n the field '10"\n2,6'1 swallows a row boundary. The repo's own bad_quote_in_unquoted_region.csv fixture returns 'nquoted region ... closed' without error once the SIMD path is active.
- The test suite cannot catch this on AVX2 machines: most cases use a 64-byte read buffer, and the SIMD loop only runs when i + 64 &lt; end, so with the 64-byte vectors that suggestVectorLength() picks on AVX2 and AVX-512 the iterator tests exercise only the scalar path. The comment on the 34-byte cases ('enough for vectorization in x86') dates from a 32-byte width. There is no fuzzing or differential test against another parser.
- Field slices are valid only until the next next() call (unless the reader is fixed), and field.unescaped() rewrites the buffer in place.
- The benchmark harness counts fields without unescaping or checking that the parsers agree on counts. game.csv, which the csv-race README calls real-world, is one 26-byte row (hello,","," ",world,1,"!") repeated 100,000 times. The other three real-world files are 0.7-1.4 MB samples where the \~0.4-1.2 ms process start-up is a large share of wall time. The generated 'Mix Quotes' files come from csv-zero's own Emitter and contain no embedded newlines.

## Known shortcomings

- Author's own harness counting fields only; libzsv flags and cc/g++ versions unstated; small real files dominated by start-up; the harness changed after the results were taken; tier A rests on the lazycsv baseline (-O3 -march=native). LangArena 2026-10-05 corroborates (Zig 0.974 s vs C/Clang 2.223 s).
- Correctness bug found by reading iterator.zig and replaying its logic in Python (not run under Zig): a quote inside an unquoted field skips strict validation, so 5'10",x yields the field '10 with no error; on the SIMD path a field can swallow a row boundary, and the repo's own bad_quote_in_unquoted_region fixture passes with no error. Tests use 64-byte buffers, so on AVX2 targets they exercise only the scalar path. The benchmark numbers are unaffected (all 4 data files pass a strict scan). game.csv is one 26-byte row repeated 100,000 times, not real-world data; after subtracting start-up time lazycsv beats csv-zero on game.csv (derived). The LangArena evidence duplicates the sibling entry.

## Caveats and trade-offs

The harness is written by the csv-zero author, and the task only counts fields, so it isolates scanning and says nothing about downstream parsing. No harness step checks that the parsers report the same field count. The result chart set shows the top five parsers only; result-all.csv holds the five measured here (csv-parser, rapidcsv, csv-core and a Go parser are built by the Makefile but not in the CSV). 'zsc (c)' is the zsv library linked with -lzsv from a manual build whose flags are not stated, and its harness is built without -march=native. lazycsv and csv-zero (native Zig target) both target the host CPU. lazycsv memory-maps the input (10.6 GB peak RSS on the 9.9 GB file) instead of using a 64 KB buffer. The four real-world files are 0.72-2.6 MB samples (nfl 1.36 MB, worldcitiespop 0.96 MB, mbta 0.72 MB, game 2.6 MB), so those rows partly measure process start-up. The results date from 2025-12-22/23. Later harness changes: a Zig 0.16 pin, and a fix by the simd-csv author (2026-07-30) that removed double buffering in the Rust csv and simd-csv harnesses, so those two Rust rows are understated. csv-zero's CRLF chunk-boundary fix (2026-01-06) does not affect these LF-only files. Single machine (laptop-class Ryzen 5 PRO 5650U), one table. The csv-zero README claims it outperforms every library in csv-race but gives no numbers; the numbers come from result-all.csv. In LangArena the C/C++ CSV implementations were not inspected, and Rust beats the Zig row there. zsv (C) is already catalogued as a separate entry; this record is about the Zig library. [retier] A quote inside an unquoted field skips strict validation (5'10",x yields the field '10 with no error) and on the SIMD path a field can swallow a row boundary; the repo's own bad_quote_in_unquoted_region fixture passes with no error, and the tests' 64-byte buffers exercise only the scalar path on AVX2 targets. The benchmark files all pass a strict scan, so the numbers stand. game.csv is one 26-byte row repeated 100,000 times; after subtracting start-up time lazycsv beats csv-zero on it.

Low-level API: yields fields (with a last-column flag), not records, and allocates nothing; strict RFC 4180 (an unquoted field containing a double quote is an error); no type conversion; Zig 0.15 to 0.17 toolchain churn; a C API exists per the README.

## Maintenance

MIT, single author, 39 stars, no tagged releases; active (last commit 2026-07-29, a Zig 0.17 upgrade) but young (first commit 2025-12-19), with the strict-validation hole above unreported in its 6 open issues, so validate untrusted input elsewhere or use the scalar path (vector_length = null) until it is fixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** csv-race result-all.csv lists csv-zero, zsv ('zsc (c)') and lazycsv (C++) on all 10 files, and every quoted number matches. The harness code is public (src/zig/src/csv_zero.zig, src/c/zsv/main.c and build.sh, src/cpp/lazycsv/main.cpp and build.sh, generate_charts.py with poop), the flags are stated (zig --release=fast, cc -O3, g++ -std=c++17 -O3 -march=native) and so is the CPU (Ryzen 5 PRO 5650U). A holds through the lazycsv baseline. libzsv's own build flags and the cc/g++ versions are not stated.
- **Verifier notes:** Accurate record; tier A kept on the strength of the lazycsv (-O3 -march=native) comparison. Shortcomings for the decision record: the author's own harness; libzsv build flags and C/C++ compiler versions are unstated; the task only counts fields, with no cross-check of counts; small real-world files are start-up dominated; the harness changed after the results; LangArena's 2026-10-05 run independently confirms Zig (csv-zero) 0.974 s vs C/Clang 2.223 s.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-61 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/peymanmortazavi/csv-zero>
  - <https://github.com/peymanmortazavi/csv-zero/commits/HEAD>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/result-all.csv>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/README.md>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/Makefile>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/src/c/zsv/build.sh>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/src/c/zsv/main.c>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/src/cpp/lazycsv/build.sh>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/src/cpp/lazycsv/main.cpp>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/src/zig/build.zig>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/src/zig/build.zig.zon>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/src/zig/src/csv_zero.zig>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/src/zig/src/data_gen.zig>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/generate_charts.py>
  - <https://github.com/peymanmortazavi/csv-race/commits/HEAD>
  - <https://github.com/peymanmortazavi/csv-race/commits/HEAD/result-all.csv>
  - <https://github.com/peymanmortazavi/csv-race/commit/a1b278a>
  - <https://github.com/peymanmortazavi/csv-race/tree/HEAD/data>
  - <https://github.com/kostya/LangArena>
  - <https://github.com/kostya/LangArena/tree/master/zig>
  - <https://github.com/kostya/LangArena/tree/master/results>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/zig/build.zig.zon>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/README.md>
  - <https://raw.githubusercontent.com/kostya/LangArena/master/results/2026-10-05-kostya-ms7c37.js>
- **Sources the enricher read:**
  - <https://github.com/peymanmortazavi/csv-zero>
  - <https://github.com/peymanmortazavi/csv-zero/commits/main>
  - <https://github.com/peymanmortazavi/csv-zero/tree/main/src>
  - <https://github.com/peymanmortazavi/csv-zero/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-zero/HEAD/README.md>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-zero/HEAD/build.zig>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-zero/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-zero/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-zero/HEAD/src/iterator.zig>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-zero/HEAD/src/simd.zig>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-zero/HEAD/src/root.zig>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-zero/HEAD/src/c_api.zig>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-zero/HEAD/src/emitter.zig>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-zero/HEAD/src/tests.zig>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-zero/HEAD/test/bad_quote_in_unquoted_region.csv>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-zero/HEAD/test/bad_unescaped_quotes.csv>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/README.md>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/Makefile>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/result-all.csv>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/generate_charts.py>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/src/c/zsv/build.sh>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/src/c/zsv/main.c>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/src/cpp/lazycsv/build.sh>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/src/cpp/lazycsv/main.cpp>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/src/zig/build.zig>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/src/zig/build.zig.zon>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/src/zig/src/csv_zero.zig>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/src/zig/src/data_gen.zig>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/data/nfl.csv>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/data/worldcitiespop.csv>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/data/gtfs-mbta-stop-times.csv>
  - <https://raw.githubusercontent.com/peymanmortazavi/csv-race/HEAD/data/game.csv>
  - WebSearch: csv-zero Zig CSV parser SIMD benchmark zsv simd-csv (ziggit.dev thread found; host unreachable)
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/peymanmortazavi/csv-zero`) · [data/wave14/enrich/raw/github_com_peymanmortazavi_csv_zero.json](../../../data/wave14/enrich/raw/github_com_peymanmortazavi_csv_zero.json) (enrichment confidence 0.75)

</details>
