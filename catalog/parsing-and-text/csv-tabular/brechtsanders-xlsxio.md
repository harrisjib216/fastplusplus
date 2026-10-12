# XLSX I/O (xlsxio)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> C library that streams .xlsx worksheet values through expat; its Python wrapper reads about 5.8x faster than openpyxl read-only.

| | |
|---|---|
| **Beats** | openpyxl (read_only=True, list(ws.iter_rows())); also xlrd (a pre-2.0 release, since xlrd 2.0 dropped .xlsx) and sxl in the same table. The table's xlsx2csv rows actually time openpyxl (copy-paste bug in benchmark.py), so xlsx2csv was never measured. |
| **Claimed result** | Big file (100,000 rows incl. header, 8 mixed-type columns), min of 3 runs: xlsxio with types 1.08584 s, without types 0.93787 s, without types all bytes 0.88268 s, with types from memory 1.09569 s, versus openpyxl read_only 6.34512 s, xlrd 4.10823 s, sxl 4.9788 s. Small file (100 rows): xlsxio with types 0.00128 s versus openpyxl 0.01131 s, xlrd 0.00486 s, sxl 0.00627 s. About 5.8x faster than openpyxl and 3.8x faster than xlrd on the big file with types (derived from page data); about 7.2x versus openpyxl with untyped bytes (derived from page data). The README's 'xlsx2csv' rows (6.53466 s big file) are not xlsx2csv: benchmark.py passes READ_OPENPYXL_SETUP/READ_OPENPYXL_STRING to all four xlsx2csv bench() calls, so they are a second openpyxl run and give no xlsx2csv comparison. |
| **Workload** | Read every row of a 100,000-row mixed-type .xlsx file (and a 100-row file) into a Python list, via the python-xlsxio Cython wrapper around the xlsxio C reader, versus pure-Python xlsx readers. |
| **Metric** | throughput |
| **Hardware** | Linux 5.4.44-1-MANJARO x86_64 (kernel string only, no CPU model) |
| **Compiler and flags** | not stated; setup.py builds the vendored xlsxio, expat, zlib and minizip C sources into one setuptools/Cython Extension with Python's default CFLAGS and the macros USE_MINIZIP, NOCRYPT, NOUNCRYPT (README says building from source with Cython gives about 5% more speed than the PyPI wheel); Python, Cython, openpyxl, xlrd and sxl versions not stated |
| **Adoption** | 525 stars (xlsxio); the benchmarking wrapper python-xlsxio has 9 stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/brechtsanders/xlsxio) · [benchmark](https://github.com/Chiorufarewerin/python-xlsxio) |

## Verdict

The only numbers come from the third-party python-xlsxio wrapper's README (about June 2020, Linux 5.4.44 Manjaro; CPU, compiler, Python and library versions not stated): reading a generated 100,000-row x 8-column mixed-type sheet into Python lists took 1.09 s with types (0.94 s as str, 0.88 s as bytes) versus 6.35 s for openpyxl read_only, 4.11 s for xlrd (pre-2.0) and 4.98 s for sxl, min of 3 runs, about 5.8x versus openpyxl (derived from page data). It measures C plus Cython against pure Python, not xlsxio against any C or C++ reader, and the 'xlsx2csv' rows are a mislabelled second openpyxl run.

## Use it when

- Reading large data-table .xlsx exports (header row plus homogeneous columns) from C or C++ when only cell values matter, not formatting.
- Python ETL jobs bottlenecked on openpyxl read_only or xlrd for 10^5-row sheets that can declare column types (python-xlsxio: about 1.09 s vs 6.35 s for 100,000 rows x 8 columns).
- Streaming a big sheet row by row with bounded memory, as long as the shared-string table fits in RAM.
- Writing a plain single-sheet table (strings, ints, floats, datetimes) from C with only zlib/minizip as dependencies, or converting from the shell with the bundled xlsxio_xlsx2csv and xlsxio_csv2xlsx tools.

## Skip it when

- Untrusted .xlsx input in a long-running process: open crash reports include #151 (NULL dereference on a Relationship without Id), #136 (segfault under ASan) and #123 (infinite loop listing sheets); CVE-2023-34795 and a heap over-read in the xlsxioread_open_memory path (#150) were fixed in 2023 and 2026-09-24; no fuzzing is documented.
- You need cell types, number formats or dates detected automatically: styles.xml is never parsed, so dates come back as Excel serial numbers unless the caller asks for datetime per column (open issue #19), and the 1904 date system is not handled.
- Workbooks with very many unique strings: the whole shared-string table is held in memory, and its pointer array grows by a realloc of one element per string.
- Writing anything beyond one plain sheet: no multiple worksheets, shared strings, formulas or styling, and the sheet is always deflated at level 9; libxlsxwriter covers that.
- Data that is or can be CSV: the catalogued CSV parsers avoid ZIP inflation and XML parsing altogether.

## How it is fast

The worksheet XML is inflated by minizip (or libzip) in 256-byte chunks and fed straight into expat's SAX parser, so the sheet is never built as a DOM; only the shared-string table is loaded into memory first. Parsing is a state machine that swaps expat element and character-data handlers per state (find row, find cell, find value), and the pull API rides on expat's suspend/resume (XML_StopParser with resumable=true at each cell). The gain over openpyxl, xlrd and sxl is compiled SAX parsing versus Python object construction; there is no SIMD or custom tokenizer, and every cell value is still a separate heap allocation (shared strings are strdup'd per cell).

## Compared with alternatives

The catalogued siblings (zsv, Vince's CSV Parser, fast-cpp-csv-parser, DuckDB, Polars) all parse CSV; pick xlsxio only when the input arrives as .xlsx and you want a small MIT C dependency instead of converting first. For writing, libxlsxwriter (same category) is the richer choice with formats, formulas and multiple sheets; for a speed-first C reader, xlsx_drone (catalogued under binary-schemas) is the other option, also with first-party numbers only.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (libxlsxio_read, libxlsxio_write, experimental UTF-16 libxlsxio_readw) built with CMake or a plain Makefile; Conan package; Python via the third-party python-xlsxio (wheels only up to CPython 3.10) |
| **Dependencies** | expat (reader only), minizip (preferred; minizip-ng supported) or libzip, zlib; the writer uses pthreads (Windows threads on Windows) |
| **Minimum toolchain** | any C compiler (gcc, clang, MinGW/MinGW-w64; MSVC fixes landed 2024); CMake 2.6+ optional, but open issue #147 reports CMake 4 does not work |
| **Platforms** | Windows, macOS, Linux per README; prebuilt binaries for Windows 32/64-bit only |
| **Thread safety** | not documented; each reader handle owns its expat parser and zip state, but one xlsxioreader handle cannot interleave operations (minizip reentry crash fixed in #148; open #128 'Cannot use sheetlist_next after sheet_open') |
| **Drop-in for the baseline** | no |

## Gotchas

- Datetime truncation: xlsxioread_sheet_next_cell_datetime computes (serial - 25569) \* 86400 and casts to time_t, truncating instead of rounding. Simulating the benchmark's 'Last activity' column (openpyxl writes serials with '%.16g'), 36,007 of 100,000 values come back one second early, against 0 with rounding. xlsxio's own writer adds 0.499 s before converting, so round-trip tests on xlsxio-written files hide it. This corrupts output of the wrapper's 'with types' rows, not their timing.
- xlsxioread_sheet_next_cell_int parses with sscanf("%" PRIi64): %i auto-detects the base, so a text cell '010' reads as 8 and '0x1A' as 26, '45000.5' silently becomes 45000, and an unparseable cell yields 0 rather than an error. The wrapper's bool type goes through the same path.
- Shared strings (lib/xlsxio_read_sharedstrings.c) are matched with plain strcasecmp on 'sst', 'si' and 't', while sheet parsing strips namespace prefixes (XML_Char_icmp_ins); from code reading, a namespace-prefixed &lt;x:sst&gt; table, the case in issue #29 (closed 2020), would load no strings and shared-string cells would come back empty. Not tested here.
- Benchmark harness flaws behind the published table: the four 'xlsx2csv' rows rerun openpyxl (READ_OPENPYXL_\* constants pasted), generate_xlsx.py writes benchmark.xlsx while benchmark.py reads benchmark_big.xlsx and benchmark_small.xlsx (the 100-row file is not scripted), xlrd needs a pre-2.0 release, and the 'without types' rows (0.88-0.94 s) return dates and numbers as raw strings while openpyxl returns typed values, so the 7.2x untyped ratio compares unequal work.

## Known shortcomings

- Tier C: python-xlsxio README numbers (1.08584 s vs openpyxl 6.34512 s, about 5.8x derived) come from a 9-star third-party wrapper, a table from about June 2020, C vs pure Python only (no C or C++ rival), no CPU, compiler or versions, unequal work (ReadOnlyCell vs plain values); the xlsx2csv row is a second openpyxl run (benchmark.py passes READ_OPENPYXL_\* to all four xlsx2csv calls) and was dropped from the claim; the xlrd row needs xlrd&lt;2.0; the 100-row file is not scripted. Security fixes 2026-09-24 (#150 underflow in minizip_io_memory_read_file_fn) and 2026-06-28 (#148). MIT, active.
- Enricher: xlsxioread_sheet_next_cell_datetime truncates (serial-25569)\*86400 to time_t instead of rounding; simulating the benchmark's 'Last activity' column (openpyxl writes %.16g) 36,007 of 100,000 values come back 1 s early (rounding gives 0); this corrupts the wrapper's 'with types' output, not its timing, and xlsxio's own writer adds .499 s so round trips on its own files hide it (simulation, not a library run). next_cell_int uses sscanf %i ('010' reads as 8, floats truncated, failures return 0); sharedstrings.c uses plain strcasecmp so a prefixed &lt;x:sst&gt; table (issue #29) probably loads no strings (code reading). Harness: xlsx2csv rows rerun openpyxl; the generator writes benchmark.xlsx but the bench reads _big/_small; the untyped 7.2x compares raw strings with openpyxl's typed values. Open crash reports #151 (NULL deref), #136, #123 (infinite loop); styles never parsed (#19); no 1904 epoch; shared-string array grows by realloc +1 per string; writer always deflates at level 9; open #147 CMake 4 broken; python-xlsxio idle since 2022.

## Caveats and trade-offs

Evidence is not from xlsxio's own repo (xlsxio's README and Changelog carry no performance numbers): the numbers measure the third-party python-xlsxio Cython wrapper (author Artur Beltsov, not the xlsxio author; last commit 2022-01-23, last PyPI release 0.1.5 on 2022-01-23), including Python object construction, against pure-Python libraries, so it shows C-versus-Python reading, not a C or C++ rival such as OpenXLSX or libxlsxwriter. The table dates from about June 2020 (kernel 5.4.44 built 2020-06-03, first PyPI release 2020-06-21) and used whatever xlsxio commit the wrapper vendored then (the submodule now points at b3dfd27). Harness flaws: the four 'xlsx2csv' rows run the openpyxl code (READ_OPENPYXL_\* constants passed by mistake), so the xlsx2csv figures are a mislabelled second openpyxl run; generate_xlsx.py writes benchmark.xlsx (header plus 99,999 rows) while benchmark.py reads benchmark_big.xlsx and benchmark_small.xlsx, and the 100-row file is not scripted; the xlrd rows need xlrd below 2.0, which no longer reads .xlsx; openpyxl builds ReadOnlyCell objects while xlsxio returns plain values, and xlsxio needs column types supplied up front (or reads everything as str/bytes), so the work is not equal. Compiler flags, CPU model, Python version and library versions are not stated, so tier C. xlsxio fixed an integer underflow in minizip_io_memory_read_file_fn on 2026-09-24 (#150, the xlsxioread_open_memory path the wrapper's 'from memory' rows use) and a minizip reentry issue in xlsxio_read.c on 2026-06-28 (#148). No numeric comparison was found for the xlsxio writer or against another C/C++ xlsx reader. Ratios are computed from table rows, not quoted by the wrapper. [retier] python-xlsxio README (about June 2020, 9-star wrapper, no CPU/compiler/versions): about 5.8x vs openpyxl read-only on a 100,000-row file, C vs pure Python only; xlsx2csv row is a second openpyxl run; untyped row compares raw strings with typed values. xlsxioread_sheet_next_cell_datetime truncates instead of rounding (about 36% of %.16g-written datetimes read 1 s early, simulated); next_cell_int uses sscanf %i; case-insensitive sharedstrings matching may load no strings for prefixed &lt;x:sst&gt;. Open crashes #151, #136, #123; styles unparsed (#19); CMake 4 broken (#147). Security fixes 2026-09-24 (#150) and 2026-06-28 (#148).

Reader assumes a data table (first row headers, values only; formulas, layout and charts ignored); whole shared string table is loaded in memory; worksheet cells are streamed. Writer supports a single worksheet and inline strings only (no shared strings, no formulas or styling). Depends on expat and minizip or libzip (zlib). The xlsxio README itself carries no benchmark.

## Maintenance

Lightly but actively maintained (security fixes merged 2026-06-28 and 2026-09-24, yet 42 open issues including unanswered crash reports #151 and #123) and MIT-licensed and small enough to vendor, while the benchmarked python-xlsxio wrapper has been idle since January 2022 with wheels only to CPython 3.10; a simulation of the benchmark's datetime column shows about 36% of values truncated one second early by xlsxioread_sheet_next_cell_datetime.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The python-xlsxio README table (script benchmark/benchmark.py, generator benchmark/generate_xlsx.py) shows the xlsxio-backed reader at 1.08584 s versus openpyxl read_only at 6.34512 s on a 100,000-row file, but gives only a kernel string: no CPU model, compiler, flags, Python or library versions. It is the wrapper author's own promotional table (9-star repo), not a well-known independent suite, so C.
- **Verifier notes:** Confirm at C: openpyxl, xlrd and sxl rows are genuine and the record's numbers match the README table, but the record also cited the xlsx2csv row, which benchmark.py actually fills with a second openpyxl run (copy-paste bug); claimed_speedup and baseline were corrected to drop it. Shortcomings to record: third-party 9-star wrapper benchmark from 2020, C versus pure-Python only (no C/C++ rival), no CPU/compiler/versions, mislabelled xlsx2csv rows, unequal work (cell objects vs plain values), xlrd row needs xlrd&lt;2.0. Metadata checked: MIT, 525 stars, 131 forks, not a fork, not archived, last commit 2026-09-24.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-18 (wave 3); enricher (wave 3)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Chiorufarewerin/python-xlsxio/HEAD/README.md>
  - <https://raw.githubusercontent.com/Chiorufarewerin/python-xlsxio/HEAD/benchmark/benchmark.py>
  - <https://raw.githubusercontent.com/Chiorufarewerin/python-xlsxio/HEAD/benchmark/generate_xlsx.py>
  - <https://raw.githubusercontent.com/Chiorufarewerin/python-xlsxio/HEAD/setup.py>
  - <https://raw.githubusercontent.com/Chiorufarewerin/python-xlsxio/HEAD/xlsxio/xlsxio_read.pyx>
  - <https://github.com/Chiorufarewerin/python-xlsxio>
  - <https://github.com/Chiorufarewerin/python-xlsxio/commits>
  - <https://github.com/Chiorufarewerin/python-xlsxio/blob/master/benchmark/benchmark.py>
  - <https://github.com/Chiorufarewerin/python-xlsxio/tree/master/deps>
  - <https://github.com/Chiorufarewerin/python-xlsxio/tree/master/xlsxio>
  - <https://pypi.org/pypi/python-xlsxio/json>
  - <https://github.com/brechtsanders/xlsxio>
  - <https://github.com/brechtsanders/xlsxio/commits>
  - <https://raw.githubusercontent.com/brechtsanders/xlsxio/HEAD/README.md>
  - <https://raw.githubusercontent.com/brechtsanders/xlsxio/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/brechtsanders/xlsxio/HEAD/Changelog.txt>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/brechtsanders/xlsxio/HEAD/README.md>
  - <https://raw.githubusercontent.com/brechtsanders/xlsxio/HEAD/Changelog.txt>
  - <https://raw.githubusercontent.com/brechtsanders/xlsxio/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/brechtsanders/xlsxio/HEAD/include/xlsxio_read.h>
  - <https://raw.githubusercontent.com/brechtsanders/xlsxio/HEAD/include/xlsxio_write.h>
  - <https://raw.githubusercontent.com/brechtsanders/xlsxio/HEAD/lib/xlsxio_read.c>
  - <https://raw.githubusercontent.com/brechtsanders/xlsxio/HEAD/lib/xlsxio_write.c>
  - <https://raw.githubusercontent.com/brechtsanders/xlsxio/HEAD/lib/xlsxio_read_sharedstrings.c>
  - <https://raw.githubusercontent.com/brechtsanders/xlsxio/HEAD/lib/xlsxio_read_sharedstrings.h>
  - <https://raw.githubusercontent.com/brechtsanders/xlsxio/HEAD/lib/xlsxio_private.h>
  - <https://raw.githubusercontent.com/brechtsanders/xlsxio/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/brechtsanders/xlsxio/HEAD/Makefile>
  - <https://github.com/brechtsanders/xlsxio>
  - <https://github.com/brechtsanders/xlsxio/commits/master>
  - <https://github.com/brechtsanders/xlsxio/issues?q=is%3Aissue>
  - <https://github.com/brechtsanders/xlsxio/issues?page=2&q=is%3Aissue>
  - <https://github.com/brechtsanders/xlsxio/issues?q=is%3Aissue%20slow%20OR%20performance%20OR%20speed%20OR%20namespace%20OR%20date>
  - <https://github.com/brechtsanders/xlsxio/issues/151>
  - <https://github.com/brechtsanders/xlsxio/issues/123>
  - <https://github.com/brechtsanders/xlsxio/issues/142>
  - <https://github.com/brechtsanders/xlsxio/issues/136>
  - <https://github.com/brechtsanders/xlsxio/issues/29>
  - <https://github.com/brechtsanders/xlsxio/issues/88>
  - <https://github.com/brechtsanders/xlsxio/pull/148>
  - <https://github.com/brechtsanders/xlsxio/pull/150>
  - <https://raw.githubusercontent.com/Chiorufarewerin/python-xlsxio/HEAD/README.md>
  - <https://raw.githubusercontent.com/Chiorufarewerin/python-xlsxio/HEAD/benchmark/benchmark.py>
  - <https://raw.githubusercontent.com/Chiorufarewerin/python-xlsxio/HEAD/benchmark/generate_xlsx.py>
  - <https://raw.githubusercontent.com/Chiorufarewerin/python-xlsxio/HEAD/setup.py>
  - <https://raw.githubusercontent.com/Chiorufarewerin/python-xlsxio/HEAD/xlsxio/xlsxio_read.pyx>
  - <https://pypi.org/pypi/python-xlsxio/json>
  - <https://pypi.org/pypi/openpyxl/json>
  - <https://files.pythonhosted.org/packages/c0/da/977ded879c29cbd04de313843e76868e6e13408a94ed6b987245dc7c8506/openpyxl-3.1.5-py2.py3-none-any.whl>
  - <https://github.com/tafia/calamine>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/brechtsanders/xlsxio`) · [data/wave3/enrich/raw/github_com_brechtsanders_xlsxio.json](../../../data/wave3/enrich/raw/github_com_brechtsanders_xlsxio.json) (enrichment confidence 0.8)

</details>
