# xlsx_drone

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> Small read-only C11 .xlsx cell reader; through its Ruby FFI binding it read a 600k-cell sheet about 1.9x faster than roo.

| | |
|---|---|
| **Beats** | roo (Ruby gem Roo::Excelx), fastest of four Ruby xlsx readers in the benchmark |
| **Claimed result** | README: 'x2 times faster than the fastest one'. Screenshot of 'rake bm' (real seconds): xlsx_drone 10.63, roo 20.41, simple_xlsx_reader 25.49, creek 28.27, rubyXL 79.56; xlsx_drone is 1.9x faster than roo, 2.4x than simple_xlsx_reader, 2.7x than creek and 7.5x than rubyXL (derived from page data). |
| **Workload** | Ruby binding (xlsx_drone_rb) reading every cell of a 200,000 row x 3 column xlsx (number, string, date) with the C library, against roo, creek, rubyXL and simple_xlsx_reader. |
| **Metric** | throughput |
| **Hardware** | 'my old notebook' per the README; CPU model, OS version, Ruby version and C build flags not stated |
| **Adoption** | 21 stars; Ruby gem xlsx_drone (https://github.com/damian-m-g/xlsx_drone_rb, 5 stars) |
| **Last commit** | 2025-01-09 |
| **Links** | [repository](https://github.com/damian-m-g/xlsx_drone) · [benchmark](https://raw.githubusercontent.com/damian-m-g/xlsx_drone_rb/HEAD/data/README.md_images/bm_result.png) |

## Verdict

One first-party run of the Ruby binding's test/benchmark/speed.rb on the author's 'old notebook' (CPU, OS, Ruby, gem versions and C build flags not stated) read all 600,000 cells of a 200,000-row, 3-column xlsx in 10.63 s against 20.41 s for roo (1.9x), 25.49 s for simple_xlsx_reader, 28.27 s for creek and 79.56 s for rubyXL; each timed block also includes the gem's require and workbook open, it is a single run with roo first, and xlsx_drone pays an FFI call per cell, so it compares native C with pure-Ruby gems rather than C with C.

## Use it when

- A C or C++ program, or a Ruby script via the xlsx_drone gem, that reads values from Excel-saved .xlsx files with a known layout, row by row.
- Replacing roo, creek, rubyXL or simple_xlsx_reader in Ruby when read time dominates and the files come from Excel itself.
- Small embedded tools that want an MIT-licensed reader in a few C files with no external runtime dependencies beyond a writable temp directory.

## Skip it when

- Files written by Apache POI or other generators that order cell attributes differently or use inline strings: they are misread (open issue #14, fix PR #15 unmerged as of 2026-06).
- Untrusted or unusual files: indices into shared strings and styles are not bounds-checked, XML layout is assumed, and the code builds paths with strcpy/strcat into fixed 260-byte buffers.
- Very large sheets on memory-tight systems or read-only/no-temp-dir environments: the whole archive is unpacked to disk and the full sheet is held as an XML DOM.
- Writing, formulas evaluation, rich text, merged cells or any other workbook features: it only returns raw cell values.
- Programs that set a comma-decimal LC_NUMERIC locale: doubles are parsed with plain strtod again (see gotchas).

## How it is fast

There is no special algorithm: the speed in the benchmark comes from doing the work in native C instead of pure Ruby. xlsx_open extracts the whole archive with kuba--/zip (miniz) into a temporary directory and parses sharedStrings.xml, styles.xml and workbook.xml once; xlsx_load_sheet parses the sheet XML into an sxmlc DOM, and each read finds the row by scanning forward from the last row it looked at and the cell by a linear strcmp over that row's cells, so sequential row-major reads stay cheap while random backward reads rescan from the first row. Shared strings are returned as pointers into the DOM with no copying, and the last column is not computed unless asked for.

## Compared with alternatives

No catalogued sibling does the same job: the other binary-schemas entries are serialization formats (Bebop, FlatBuffers alternatives, MessagePack, Protobuf replacements), not spreadsheet readers. The relevant comparisons, C/C++ xlsx readers such as xlsxio and OpenXLSX, are not catalogued and have not been benchmarked against it.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | bundled kuba--/zip 0.3.2 (with miniz) and sxmlc 4.5.4 in ext/; a writable temp directory (\$TMPDIR, /tmp fallback, %TEMP% on Windows) |
| **Minimum toolchain** | C11 (CMakeLists sets C_STANDARD 11, CMake 3.9+); uses VLAs outside MSVC; MSVC supported since 0.3.0 via _alloca |
| **Platforms** | Windows, Linux and macOS (POSIX mkdtemp on non-Windows); prebuilt xlsx_drone_x64/x86.dll and libxlsx_drone_x64.so in share/; no architecture-specific code |
| **Thread safety** | not documented; the error code (xlsx_errno) and the print-errors flag are process-wide statics, so concurrent calls race on error reporting |
| **Drop-in for the baseline** | no |

## Gotchas

- Cell parsing reads attributes by position: 'r' must be the first attribute, 't' the last and 's' the second to last. Apache POI writes r, t, s, so its files are misread (issue #14; PR #15 of 2026-05-29 searches attributes by name and adds inline-string support, not merged). For t="inlineStr" the current code returns the text of the &lt;is&gt; element, which holds no text itself, and rows or cells without the optional 'r' attribute would be read out of bounds (code reading).
- Regression: CHANGELOG 0.2.5 lists issue #5 (doubles parsed with the locale's decimal comma) as fixed, and commit 9a9db6e did add a locale-independent strtodouble(), but it disappeared in 0.3.0-pre (03b3653) and master again calls strtod(cell_text, NULL), so a host program running under a comma-decimal LC_NUMERIC truncates 3.14 to 3.
- xlsx_open unpacks every part of the archive into a mkdtemp directory (tmpnam on Windows) that only xlsx_close deletes; a crash or a missing close leaves the extracted XML behind, and the sheet path is built in a fixed char[260] buffer, so a long TMPDIR can overflow it. Unmerged PR #17 (2026-06-23) would unzip in memory instead.
- Sheets are located as xl/worksheets/sheetN.xml by position in workbook.xml, and shared strings as the first child of each &lt;si&gt;, so workbooks whose sheet part names do not follow sheet order, or rich-text shared strings (&lt;si&gt;&lt;r&gt;...), are not handled (code reading).

## Known shortcomings

- bm_result.png (1.9x over roo): the C library is timed only through Ruby FFI against pure-Ruby gems with no CPU, Ruby version or flags, and the readers do different work. 21 stars, stale.
- Cell attributes are read by fixed position, so Apache POI files and inlineStr cells misread (issue #14, PR #15 unmerged). Regression: the 0.2.5 locale-safe strtodouble was dropped in 03b3653, master is back on strtod while CHANGELOG still says #5 is fixed. Harness: each timed block includes require and open, a single run, one FFI call per cell, native C vs pure Ruby. Unpacks the whole xlsx to a temp dir; char[260] path buffer.

## Caveats and trade-offs

The benchmark lives in the Ruby binding repo (xlsx_drone_rb, which loads the C library through the ffi gem, gemspec 0.6.0) and measures the C library through Ruby FFI, not the C API itself; the baselines are pure-Ruby gems (roo, creek, rubyXL, simple_xlsx_reader), so this is native C against interpreted Ruby and says nothing about C or C++ xlsx readers such as xlsxio or OpenXLSX, or about openpyxl. Result is an undated screenshot from the author's own machine; the script test/benchmark/speed.rb and the 200,000-row file are in the repo, but CPU, OS, Ruby version, gem versions and C build flags are not stated, so tier C. Readers do different work: roo and xlsx_drone use random cell access by (row, column) while creek, rubyXL and simple_xlsx_reader iterate rows; rubyXL builds a full workbook object model; the script's own comment says simple_xlsx_reader cannot tell numbers from strings; each timed block also includes the gem's first require and the workbook open. No numeric comparison in the C repo README, CHANGELOG or issues. Category binary-schemas is a loose fit (spreadsheet file reader over zip and XML).

Read-only (writing is on hold); focus 'speed over functionality'; copy src and ext folders into the project; depends on bundled kuba--/zip 0.3.2 and sxmlc 4.5.4 (BSD-style); cells are looked up by row and column letters; the last column is not computed on load because it costs time on big files. Open issues include an incompatibility with Apache POI generated files (#14) and a crash on an odd format (#12, closed).

## Maintenance

Stale: last release 0.4.0 on 2024-12-09 and a README edit on 2025-01-09, with an outside contributor's fixes (POI compatibility, in-memory unzip) waiting unmerged; MIT and small enough to vendor, but test it on files from your own producers first.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The bm_result.png screenshot of 'rake bm' shows real seconds xlsx_drone 10.633398, roo 20.406725, simple_xlsx_reader 25.493084, creek 28.266484, rubyXL 79.559665, produced by the public script test/benchmark/speed.rb in damian-m-g/xlsx_drone_rb; but it is a first-party run on 'my old notebook' with no CPU model, Ruby version or C build flags, so it stays C.
- **Verifier notes:** Numbers and derived ratios (1.9x roo, 2.4x simple_xlsx_reader, 2.7x creek, 7.5x rubyXL) match the screenshot; record accurate. Shortcomings: C library measured only through a Ruby FFI binding against pure-Ruby gems (no C/C++ reader baseline), unstated hardware/Ruby/flags, readers doing different work, 21 stars, stale (last commit 2025-01-09).
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party screenshot (verifier); enricher (wave 4)
- **Pages the verifier opened:**
  - <https://github.com/damian-m-g/xlsx_drone>
  - <https://github.com/damian-m-g/xlsx_drone/commits>
  - <https://github.com/damian-m-g/xlsx_drone_rb>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone_rb/HEAD/README.md>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone_rb/HEAD/data/README.md_images/bm_result.png>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone_rb/HEAD/test/benchmark/speed.rb>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone_rb/HEAD/lib/xlsx_drone.rb>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone_rb/HEAD/xlsx_drone.gemspec>
- **Sources the enricher read:**
  - <https://github.com/damian-m-g/xlsx_drone>
  - <https://github.com/damian-m-g/xlsx_drone/commits/master>
  - <https://github.com/damian-m-g/xlsx_drone/issues?q=is%3Aissue>
  - <https://github.com/damian-m-g/xlsx_drone/issues/14>
  - <https://github.com/damian-m-g/xlsx_drone/issues/5>
  - <https://github.com/damian-m-g/xlsx_drone/pulls?q=is%3Apr>
  - <https://github.com/damian-m-g/xlsx_drone/pull/15/files>
  - <https://github.com/damian-m-g/xlsx_drone/pull/17>
  - <https://github.com/damian-m-g/xlsx_drone/commit/9a9db6e>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone/HEAD/README.md>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone/HEAD/Rakefile>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone/HEAD/src/xlsx_drone.c>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone/HEAD/src/xlsx_drone.h>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone/master/src/xlsx_drone.c>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone/9a9db6e/src/xlsx_drone.c>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone/9a32fcc/src/xlsx_drone.c>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone/03b3653/src/xlsx_drone.c>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone/9774d74/src/xlsx_drone.c>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone/69392d1/src/xlsx_drone.c>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone_rb/HEAD/README.md>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone_rb/HEAD/test/benchmark/speed.rb>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone_rb/HEAD/lib/xlsx_drone.rb>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone_rb/HEAD/lib/xlsx_drone/sheet.rb>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone_rb/HEAD/lib/xlsx_drone/native_binding.rb>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone_rb/HEAD/xlsx_drone.gemspec>
  - <https://raw.githubusercontent.com/damian-m-g/xlsx_drone_rb/HEAD/Rakefile>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/damian-m-g/xlsx_drone`) · [data/wave4/enrich/raw/github_com_damian_m_g_xlsx_drone.json](../../../data/wave4/enrich/raw/github_com_damian_m_g_xlsx_drone.json) (enrichment confidence 0.75)

</details>
