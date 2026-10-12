# libxlsxwriter

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> ANSI C write-only XLSX library; same API family as Python XlsxWriter, about 4.4x faster than it on a 200k-cell sheet.

| | |
|---|---|
| **Beats** | Python XlsxWriter (the same author's pure-Python XLSX writer, the incumbent for this task) |
| **Claimed result** | hyperfine mean 210.9 ms for C/libxlsxwriter vs 919.1 ms for Python/XlsxWriter; the page's table gives Python as 4.36 times slower than C (919.1 / 210.9 = 4.36, derived from page data). For context, rust_xlsxwriter with zlib took 152.6 ms (C is 1.38x slower) and plain rust_xlsxwriter 240.8 ms (C is 1.14x faster). |
| **Workload** | Create one worksheet of 4,000 rows by 50 columns (alternating write_number 12345 and write_string 'Foo', no formatting) and save the .xlsx file; whole-process wall time measured with hyperfine, warmup 3. |
| **Metric** | throughput |
| **Adoption** | 1.8k stars |
| **Last commit** | 2026-07-07 |
| **Links** | [repository](https://github.com/jmcnamara/libxlsxwriter) · [benchmark](https://raw.githubusercontent.com/jmcnamara/rust_xlsxwriter/main/src/performance.rs) |

## Verdict

In rust_xlsxwriter's performance docs, written by the same author as libxlsxwriter and Python XlsxWriter, hyperfine (warmup 3) timed whole processes writing a 4,000 x 50 sheet of alternating 12345 and 'Foo': C/libxlsxwriter 210.9 ms mean versus Python XlsxWriter 919.1 ms (4.36x), with Python start-up and import inside the Python figure and no compiler, flags, libxlsxwriter build options, Python version or CPU stated; the same run puts rust_xlsxwriter with zlib ahead of C at 152.6 ms. Independent but via a wrapper: rOpenSci's writexl README times writexl (libxlsxwriter inside) at 12.3 s versus openxlsx2 at 19.6 s for nycflights13::flights (336,776 x 19), median of 2 runs, with equal file sizes.

## Use it when

- Generating reports or data exports as .xlsx from C or C++ services where Python XlsxWriter or openpyxl is the bottleneck or the runtime is unavailable.
- Large row-ordered exports (millions of cells) with constant_memory mode, where memory must stay flat regardless of sheet size.
- Workbooks that need real Excel features (formats, charts, conditional formatting, data validation, images, tables) rather than a bare CSV-to-XLSX dump.
- Embedded or portable builds: ANSI C, only zlib required, builds on Linux, BSDs, macOS, iOS, Windows (MSVC, MinGW), 32/64-bit and big-endian targets.
- As the engine under a higher-level binding: R's writexl and other language wrappers already sit on it.

## Skip it when

- Reading, editing or round-tripping existing .xlsx files: it is write-only; use a reader such as xlsxio or openpyxl.
- When rust_xlsxwriter is an option: the same author's own hyperfine run has rust_xlsxwriter with its zlib feature at 152.6 ms versus 210.9 ms for libxlsxwriter on the same 200k-cell sheet (1.38x faster).
- Multi-core throughput on one workbook: the docs say the library is single-threaded and 'optimized but not highly optimized'; each string write does a calloc, strdup and tree insert, then frees the copy if the string already exists.
- Writing out of row order or editing earlier rows in constant_memory mode: data must arrive row by row, and inline strings can grow the file 20-100 percent and are unsupported by some viewers.
- Programs running under a decimal-comma locale with the default build: numbers are formatted with locale-dependent fprintf, which produced corrupt files (issue #64); build with USE_DTOA_LIBRARY or force the C locale.

## How it is fast

Mostly it is compiled C doing what the Python library does in the interpreter: cells are malloc'd structs kept in per-worksheet red-black trees (BSD tree.h) keyed by row and column, shared strings are deduplicated in a red-black tree with strcmp, and the cell-writing loop bypasses the generic XML writer and fprintf's each &lt;c&gt; element directly. Each XML part is written to a temp file (tmpfileplus) or, with USE_MEM_FILE, an open_memstream buffer, then deflated by bundled minizip at Z_DEFAULT_COMPRESSION. constant_memory mode flushes each row as the next one starts and writes inline strings, so memory stays at about one row. The optional USE_DTOA_LIBRARY build swaps printf('%.16G') for Milo Yip's Grisu-style emyg_dtoa, which the docs say is 40-50 percent faster on numeric data (no numbers published).

## Compared with alternatives

Pick it over XLSX I/O (xlsxio) when the job is writing richly formatted workbooks with charts, validation or conditional formatting; xlsxio's catalogued evidence is for reading .xlsx, which libxlsxwriter cannot do at all. Pick it over DuckDB, Polars or the CSV parsers only when the deliverable must be a native Excel file rather than CSV or a dataframe.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (Makefile builds libxlsxwriter.a and .so; CMake 3.16+ and zig build also provided) |
| **Dependencies** | zlib (CMake requires 1.2.8+); bundled minizip (or USE_SYSTEM_MINIZIP), tmpfileplus temp files (or USE_STANDARD_TMPFILE / USE_MEM_FILE), Openwall MD5 for image dedup (or USE_OPENSSL_MD5 / USE_NO_MD5), optional emyg_dtoa |
| **Minimum toolchain** | ANSI C (the Makefile compiles with -ansi -pedantic -O3); README lists GCC, Clang, Xcode, MSVC 2015, ICC, TCC, MinGW and MinGW-w64 |
| **Platforms** | Linux, FreeBSD, OpenBSD, macOS, iOS, Windows, MSYS/MSYS2, Cygwin; 32 and 64 bit; big and little endian; no SIMD or arch-specific code |
| **Thread safety** | Not documented beyond 'the library is currently single threaded'; a workbook and its worksheets must be driven from one thread. Separate workbooks share no obvious mutable globals in the code read, but this is not a documented guarantee. |
| **Drop-in for the baseline** | partial — the C function names and options mirror Python XlsxWriter's methods one to one, so translating code is easy, but it is a different language; Python callers need a wrapper (the Impeller Cython wrapper targets a modified fork, not upstream). |

## Gotchas

- The default build formats doubles with fprintf('%.16G'), which is locale-dependent (decimal comma under de_DE corrupts the file, issue #64; the docs suggest setlocale/uselocale or USE_DTOA_LIBRARY, which is off by default) and keeps only 16 significant digits, so doubles that need 17 digits are not written exactly.
- Even in standard mode every XML part is first written to a temp file in the system tmp dir (or tmpdir option) before zipping; on hosts with /tmp in RAM, or without a writable tmp dir, use the tmpdir option or USE_MEM_FILE (not available with MSVC).
- In constant_memory mode, writing in column-major order silently keeps only the first column (docs), and worksheet_set_row, merge ranges and formatting changes apply only to the current row.
- Fixed memory-safety bugs on non-benchmarked paths show the attack surface: stack overflow in worksheet_set_selection (#447, 2024), read overflows in cell-name parsing in utility.c (#459, 2024), heap overflow with 256+ item data-validation lists and quadratic memory in default table columns (fixed 2026-07-07, after release 1.2.4); take a build from main or newer than 1.2.4 when inputs are untrusted.

## Known shortcomings

- Tier C: numbers come from rust_xlsxwriter src/performance.rs by the same author (C 210.9 ms vs Python XlsxWriter 919.1 ms, 4.36x) with no compiler, flags, CPU or Python version, one 200k-cell run with process startup counted, a Python baseline, and libxlsxwriter loses to rust_xlsxwriter with zlib (152.6 ms); the dtoa 40-50% claim has no numbers and is off by default. Licence BSD-2-Clause-Views (FreeBSD variant), kept copyable; the 2026-07-07 heap-overflow fix is not on the benchmarked path.
- Enricher: no bug behind the numbers; first-party hyperfine run with the build unstated (Makefile -O3, CMake has no default build type); C system time 34.1 ms vs Rust 16.4 ms fits temp-file staging, so a USE_MEM_FILE build may be faster; loses to rust_xlsxwriter with zlib (152.6 vs 210.9 ms). Default build is locale-dependent (%.16G, issue #64 decimal-comma corruption); single-threaded; write-only; heap-overflow and quadratic-memory fixes of 2026-07-07 land after release 1.2.4. Independent wrapper-only comparison: writexl 12.3 s vs openxlsx2 19.6 s.

## Caveats and trade-offs

The only numbers found are in the sister project rust_xlsxwriter's documentation (src/performance.rs), written by the same author as libxlsxwriter and as the Python XlsxWriter baseline, so first-party and tier C. The page lists the C, Rust and Python test programs and the hyperfine command (warmup 3), and its table states Python at 4.36 relative to C directly; compiler, flags, CPU model, Python version and libxlsxwriter build options are not stated. One small workload (200,000 unformatted cells, 4,000 rows x 50 columns), timed as whole-process wall time, so Python interpreter startup and import are included in the 919.1 ms; the Python program writes the integer 12345 where the C program writes 12345.0 (negligible). The comparison is cross-language (C library vs a pure-Python library), and libxlsxwriter loses to rust_xlsxwriter built with its zlib feature (152.6 ms; C is 1.38x slower) while beating plain rust_xlsxwriter (240.8 ms). The libxlsxwriter repo and its docs carry no benchmark of their own: docs/src/working_with_memory.dox and License.txt only say the bundled emyg_dtoa (Milo Yip dtoa) is 40-50 percent faster than the standard sprintf-based conversion for raw numeric data, with no numbers, and that library is optional and off by default (USE_DTOA_LIBRARY=1). Licence file is the FreeBSD variant of BSD-2-Clause (extra non-binding 'views and conclusions' sentence, SPDX BSD-2-Clause-Views); bundled optional parts are minizip (Zlib), tmpfileplus (MPL-2.0), emyg_dtoa (MIT), Openwall MD5 (public domain) and FreeBSD queue.h/tree.h (BSD). Commits of 2026-07-07 fixed a heap overflow with 256+ item data validation lists and quadratic memory use in default table columns; neither is on the benchmarked path. Corroborating but indirect: the Impeller README (https://raw.githubusercontent.com/m9psy/Impeller/HEAD/README.md) reports a Cython wrapper over a modified fork of libxlsxwriter at 4.69 s total vs Python XlsxWriter 18.17 s for 100,000 x 10 cells on Windows, crude results from misc/simple_bench.py, which measures the fork, not upstream.

Write-only (cannot read or modify existing XLSX files); needs zlib; offers a constant_memory mode that flushes rows to temp files and writes inline strings (files can grow 20-100 percent); its own docs say it is single-threaded and 'optimized but not highly optimized'.

## Maintenance

Active (release 1.2.4 on 2026-01-06, security and memory fixes committed 2026-07-07), 1.8k stars, FreeBSD-variant BSD-2-Clause licence, copyable; the cited speedup is first-party with an undocumented build (the Makefile defaults to -O3, but CMake has no default build type), and the C row's 34.1 ms of system time versus 16.4 ms for Rust (derived from page data) is consistent with libxlsxwriter's default temp-file staging of each XML part, so a USE_MEM_FILE build may be faster than the published figure.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers are in rust_xlsxwriter's src/performance.rs, written by the same author as both libxlsxwriter and the Python XlsxWriter baseline: hyperfine output (C 210.9 ms vs Python 919.1 ms, table 'Relative to C' 4.36) with the three test programs listed, but no compiler, flags, CPU model or Python version, so first-party with partial methodology, tier C.
- **Verifier notes:** Numbers verified on src/performance.rs (152.6 / 210.9 / 240.8 / 919.1 ms; table 4.36 relative to C). Shortcomings: first-party (same author owns baseline and sister projects), no compiler/flags/CPU/Python version, single 200k-cell workload with process startup included, cross-language baseline, slower than rust_xlsxwriter+zlib; dtoa 40-50 percent claim has no numbers and the library is off by default. Metadata checked: 1.8k stars, not fork or archived, last commit 2026-07-07, active; licence is the FreeBSD BSD-2-Clause variant (operative terms equal BSD-2-Clause, kept copyable).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-19 (wave 3); enricher (wave 3)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/jmcnamara/rust_xlsxwriter/main/src/performance.rs>
  - <https://github.com/jmcnamara/libxlsxwriter>
  - <https://github.com/jmcnamara/libxlsxwriter/commits>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/License.txt>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/docs/src/working_with_memory.dox>
  - <https://raw.githubusercontent.com/m9psy/Impeller/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/jmcnamara/libxlsxwriter>
  - <https://github.com/jmcnamara/libxlsxwriter/commits>
  - <https://github.com/jmcnamara/libxlsxwriter/issues?q=is%3Aissue+performance+OR+slow+OR+locale+OR+CVE>
  - <https://github.com/jmcnamara/libxlsxwriter/issues/64>
  - <https://github.com/jmcnamara/libxlsxwriter/issues/426>
  - <https://github.com/jmcnamara/libxlsxwriter/issues/459>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/License.txt>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/docs/src/working_with_memory.dox>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/docs/src/getting_started.dox>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/include/xlsxwriter.h>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/include/xlsxwriter/common.h>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/include/xlsxwriter/workbook.h>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/include/xlsxwriter/worksheet.h>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/include/xlsxwriter/utility.h>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/Makefile>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/src/Makefile>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/src/packager.c>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/src/utility.c>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/src/xmlwriter.c>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/src/worksheet.c>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/src/workbook.c>
  - <https://raw.githubusercontent.com/jmcnamara/libxlsxwriter/HEAD/src/shared_strings.c>
  - <https://raw.githubusercontent.com/jmcnamara/rust_xlsxwriter/main/src/performance.rs>
  - <https://raw.githubusercontent.com/ropensci/writexl/HEAD/README.md>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/jmcnamara/libxlsxwriter`) · [data/wave3/enrich/raw/github_com_jmcnamara_libxlsxwriter.json](../../../data/wave3/enrich/raw/github_com_jmcnamara_libxlsxwriter.json) (enrichment confidence 0.75)

</details>
