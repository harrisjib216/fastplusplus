# libcsv

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [CSV and tabular data](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `LGPL-2.1-or-later` · 🔴 abandoned

> Small streaming ANSI-style C CSV reader/writer with callbacks; only speed evidence is a 2012 Ruby wrapper beating Ruby's csv.

| | |
|---|---|
| **Beats** | Ruby's stdlib CSV parser (bench.rb does require 'csv' and labels it FasterCSV, which became Ruby's stdlib csv in 1.9); a pure-Ruby parser, not a C or C++ incumbent |
| **Claimed result** | Rcsv (libcsv backend) 0.060 s user / 0.062248 s real versus FasterCSV (Ruby stdlib CSV) 0.580 s user / 0.618837 s real for 10 parses of the 167 KB test file, about 9.9x on real time and 9.7x on user time (derived from page data). |
| **Workload** | Downstream benchmark in the Rcsv Ruby C extension (which embeds unmodified libcsv 3.0.3): bench.rb parses test/test_rcsv.csv (889 lines, about 167 KB, mixed quoted fields) 10 times with Rcsv.parse(data) in default mode (all fields returned as strings, no per-column conversion) versus CSV.parse(data), timed with Ruby Benchmark.bmbm; not libcsv's own benchmark and not a pure C comparison. |
| **Metric** | throughput |
| **Adoption** | 213 stars; packaged by many distributions as libcsv3; wrapped by the Rcsv Ruby gem |
| **Last commit** | 2021-08-20 |
| **Links** | [repository](https://github.com/rgamble/libcsv) · [benchmark](https://github.com/arp/rcsv) |

## Verdict

Rcsv, a Ruby C extension embedding libcsv in strict mode and returning every field as a Ruby string, parsed an 889-line, 167 KB mixed-quoting CSV 10 times in 0.062 s real versus 0.619 s for Ruby's csv library (labelled FasterCSV, which implies Ruby 1.9.3 rather than 1.8.7), under Benchmark.bmbm in November 2012; Ruby version, compiler, flags and CPU are unstated, and the committed harness raises on the stdlib side unless the header is edited by hand. Nothing measures libcsv against another C or C++ parser.

## Use it when

- C or C++ code that receives CSV in arbitrary chunks (sockets, pipes, decompressor output) and wants a push parser with field and record callbacks plus a void\* user pointer.
- Messy real-world files: by default it accepts stray quotes in unquoted fields and unescaped quotes, with an opt-in CSV_STRICT mode that reports the first violation.
- Streaming very large files with bounded memory, since only the current field is buffered.
- Writing a binding for another language or tool; Ruby (Rcsv) and Perl (Text-CSV-LibCSV) wrappers already exist.
- Projects that prefer a distro-packaged shared library (libcsv3 / libcsv-dev) over vendoring a header-only C++ parser.

## Skip it when

- Raw throughput: it parses one byte per loop iteration with function-pointer checks and no SIMD; the only published figure works out to about 27 MB/s through Rcsv including Ruby string creation (166,591 bytes x 10 in 0.062 s, derived from page data), while SIMD siblings such as zsv report GB/s.
- Zero-copy field views over an mmap'd buffer: every field byte is copied into the internal buffer (issue #32 asks for a CSV_NO_ALLOC option and has no reply).
- Static linking into a proprietary binary without relink provisions (LGPL-2.1-or-later).
- Needs beyond tokenizing: no header mapping, type conversion, parallel parsing or random access.
- Projects that need an active upstream: last commit August 2021, open PRs from 2018 and 2022 unmerged, CMake and Meson requests unanswered.

## How it is fast

The parser is a byte-at-a-time finite-state machine with four states (ROW_NOT_BEGUN, FIELD_NOT_BEGUN, FIELD_BEGUN, FIELD_MIGHT_HAVE_ENDED) that copies parser state into locals for the loop and copies field bytes into one reusable growable buffer, so there is no per-field allocation and memory is bounded by the longest field. There is no SIMD, no memchr-style scanning and no zero-copy path; the 10x in the record comes from tokenizing in C instead of in a Ruby-level parser, not from any special algorithm.

## Compared with alternatives

Pick libcsv over zsv, fast-cpp-csv-parser or Vince's CSV Parser only when you want a tiny C-ABI push parser plus writer that tolerates malformed quoting and ships as a distro package; when throughput matters pick those siblings, which publish C/C++ measurements while libcsv publishes none. For Ruby users, zsv-ruby has current numbers against Ruby's CSV (4.3-6.2x), whereas the libcsv-backed Rcsv figures are from 2012.

## Integration

| | |
|---|---|
| **Form** | shared lib (autotools/libtool, distro package libcsv3) or source-drop of libcsv.c + csv.h |
| **Dependencies** | none (C standard library only) |
| **Minimum toolchain** | C99 compiler in practice: despite the 'pure ANSI C' description, HEAD mixes declarations and statements in csv_parse, csv_fini and csv_increase_buffer (PR #26 'Hoist declarations to conform to ANSI' open since 2022); csv.h has extern "C" guards for C++ |
| **Platforms** | any (portable byte-oriented C, no SIMD or OS-specific code) |
| **Thread safety** | not documented; the code keeps all mutable state in the caller-owned struct csv_parser (only a const error-string table is global), so separate parsers can run in separate threads, but one parser must not be shared without locking |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the numbers: Rcsv's committed bench.rb cannot produce the stdlib row. Its test/test_rcsv.csv header contains a field ' """"' (space before an opening quote), and CSV.parse raises CSV::MalformedCSVError 'Illegal quoting in line 1.' (reproduced this session with Ruby 3.3.6 / csv 3.2.8 on both the 2012 and current copies of the file); bench.rb's own comment says to remove the header quotes by hand. The README table dates from Rcsv's initial commit (2012-11-16, 'Tested on REE 1.8.7 and Ruby 1.9.3', libcsv 3.0.x before the 3.0.3 upgrade of 2013-01-11), so it was measured on an unpublished edited file with unstated Ruby, compiler and CPU.
- The baseline has moved: with the header quotes removed, Ruby 3.3.6's csv 3.2.8 parsed the file 10 times in 0.123-0.139 s on an Intel Xeon @ 2.10GHz in this session versus 0.58 s in the README, so the 9.7x ratio is stale (different hardware; Rcsv itself was not rebuilt or re-timed).
- Defaults differ from RFC 4180: leading and trailing spaces and tabs are stripped from unquoted fields, blank lines are not reported unless CSV_REPALL_NL is set, malformed quoting is accepted unless CSV_STRICT is set, and fields are not NUL-terminated unless CSV_APPEND_NULL is set. The cb1 pointer refers to the reused internal buffer and is only valid during the callback; csv_parse signals errors by returning fewer bytes than given, so callers must compare the return value and call csv_error.
- The internal buffer grows linearly by blk_size (default 128 bytes) per realloc, so a multi-megabyte quoted field triggers tens of thousands of reallocs unless csv_set_blk_size raises it; csv_get_blk_size is documented in csv.3 but not declared in csv.h or defined in libcsv.c (link error), and NULL-parser checks in csv_parse, csv_error, csv_get_delim and csv_get_quote are assert()s that vanish under NDEBUG. The FAQ examples still call csv_init(&p) on a pointer, the pre-3.0 API.

## Known shortcomings

- Tier C: the only numbers are in the Rcsv Ruby-wrapper README (about 9.9x vs the pure-Ruby stdlib CSV/FasterCSV on a 167 KB file parsed 10 times) with no C or C++ baseline and Ruby version, CPU and flags unstated; the bench uses default parsing, not per-column type conversion. LGPL-2.1-or-later; abandoned (last commit 2021-08-20).
- Enricher: the Rcsv bench.rb as committed cannot produce the stdlib row (header field ' """"' makes CSV.parse raise CSV::MalformedCSVError, reproduced with Ruby 3.3.6 / csv 3.2.8 on the 2012 and current test_rcsv.csv; the comment says to strip header quotes by hand), so the numbers came from an unpublished edited file. README numbers date from the Rcsv initial commit 2012-11-16 (REE 1.8.7 / Ruby 1.9.3, libcsv 3.0.x before the 3.0.3 upgrade of 2013-01-11); csv 3.2.8 on the fixed file now takes 0.123-0.139 s for 10 parses (Xeon 2.10GHz) vs the README's 0.58 s, so the 9.7x is stale. Byte-at-a-time state machine, no SIMD, copies every field byte (issue #32 CSV_NO_ALLOC unanswered); buffer grows 128 bytes per realloc; csv_get_blk_size documented in csv.3 but absent from csv.h and libcsv.c (link error); HEAD needs C99 (PR #26 open since 2022); NULL checks are assert()s; about 27 MB/s through Rcsv (derived from page data).

## Caveats and trade-offs

libcsv's own README, man page and repo carry no benchmark; the only numbers are in the README of Rcsv (third-party Ruby wrapper, upstream arp/rcsv, of which 284km/rcsv is a 3-star fork with an identical README) against Ruby's pure-Ruby stdlib CSV parser from the Ruby 1.8/1.9 era (Rcsv was tested on REE, 1.8.7 to 2.2.2). Input is small (167 KB parsed 10 times) and Ruby version, hardware, compiler and flags are unstated; Ruby's csv gem has since been rewritten and is faster, so the ratio is stale and says nothing about libcsv against other C or C++ CSV parsers. The benchmark times object allocation of Ruby strings as well as parsing. Last commit 2021-08-20 (over 3 years ago), so abandoned, though the library is stable (version 3.0.3) and widely packaged as libcsv3. LGPL-2.1-or-later: dynamic linking or relinkable distribution obligations apply. No C or C++ shootout including libcsv was found. [retier] Only evidence is Rcsv's 2012 README (about 9.9x vs pure-Ruby CSV on a 167 KB file parsed 10 times; REE 1.8.7 / Ruby 1.9.3, libcsv 3.0.x). Committed bench.rb fails on the stdlib row (header ' """"' raises MalformedCSVError); current csv 3.2.8 parses the fixed file in 0.123-0.139 s vs README 0.58 s, so the ratio is stale. No C/C++ baseline; byte-at-a-time parser copying every field; about 27 MB/s through Rcsv (derived). LGPL-2.1-or-later; abandoned 2021.

Streaming ANSI C parser with callbacks, LGPL licence (library, not header-only), no SIMD; the repository itself publishes no throughput numbers.

## Maintenance

Abandoned since August 2021 (28 commits, open PRs from 2018 and 2022) but stable at 3.0.3, distro-packaged and small enough to vendor under LGPL-2.1-or-later; its only speed evidence is a 2012 Ruby-wrapper run whose committed harness throws CSV::MalformedCSVError on the baseline side, so treat the 9.7x as stale and not reproducible as published.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The only numbers are in the README of the Rcsv Ruby wrapper (bench.rb is public: Ruby stdlib CSV.parse vs Rcsv.parse on test/test_rcsv.csv, 10 iterations, Benchmark.bmbm), but Ruby version, compiler, flags and CPU are all unstated, and it is not a peer-reviewed paper or a known independent suite, so C.
- **Retiered** C to D: The only number is a 2012 Ruby-wrapper README figure whose committed bench.rb cannot run against the stdlib row (malformed header), so it came from an unpublished edited input; the baseline has since moved about 4x (csv 3.2.8 at 0.123-0.139 s vs 0.58 s) and no C or C++ baseline exists. Directional only.
- **Verifier notes:** Numbers verified verbatim in the Rcsv README and bench.rb; benchmark_url moved from the 284km fork to upstream arp/rcsv (libcsv's README links fiksu/rcsv, now arp/rcsv). The record's caveat that Rcsv does per-column type conversion in this benchmark was wrong: bench.rb calls Rcsv.parse(data) with defaults. Keep at C with the shortcoming that the only evidence is a stale Ruby-wrapper comparison against a pure-Ruby parser, not against any C/C++ baseline.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `workload`, `claimed_speedup`, `license`, `caveats`
- **Shortcomings recorded by:** verifier batch-62 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/rgamble/libcsv>
  - <https://github.com/rgamble/libcsv/commits/master>
  - <https://raw.githubusercontent.com/rgamble/libcsv/HEAD/README>
  - <https://raw.githubusercontent.com/rgamble/libcsv/HEAD/COPYING>
  - <https://raw.githubusercontent.com/rgamble/libcsv/HEAD/libcsv.c>
  - <https://github.com/284km/rcsv>
  - <https://raw.githubusercontent.com/284km/rcsv/HEAD/README.md>
  - <https://github.com/arp/rcsv>
  - <https://raw.githubusercontent.com/arp/rcsv/HEAD/README.md>
  - <https://raw.githubusercontent.com/arp/rcsv/HEAD/bench.rb>
  - <https://raw.githubusercontent.com/arp/rcsv/HEAD/test/test_rcsv.csv>
  - <https://github.com/tc3t/dfglib/blob/master/misc/csvPerformanceRuns.md>
- **Sources the enricher read:**
  - <https://github.com/rgamble/libcsv>
  - <https://github.com/rgamble/libcsv/commits/master>
  - <https://github.com/rgamble/libcsv/issues?q=is%3Aissue>
  - <https://github.com/rgamble/libcsv/issues/32>
  - <https://github.com/rgamble/libcsv/pulls?q=is%3Apr>
  - <https://raw.githubusercontent.com/rgamble/libcsv/HEAD/README>
  - <https://raw.githubusercontent.com/rgamble/libcsv/HEAD/FAQ>
  - <https://raw.githubusercontent.com/rgamble/libcsv/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/rgamble/libcsv/HEAD/libcsv.c>
  - <https://raw.githubusercontent.com/rgamble/libcsv/HEAD/csv.h>
  - <https://raw.githubusercontent.com/rgamble/libcsv/HEAD/csv.3>
  - <https://raw.githubusercontent.com/rgamble/libcsv/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/rgamble/libcsv/HEAD/Makefile.am>
  - <https://raw.githubusercontent.com/rgamble/libcsv/HEAD/COPYING>
  - <https://raw.githubusercontent.com/arp/rcsv/HEAD/README.md>
  - <https://raw.githubusercontent.com/arp/rcsv/HEAD/bench.rb>
  - <https://raw.githubusercontent.com/arp/rcsv/HEAD/test/test_rcsv.csv>
  - <https://raw.githubusercontent.com/arp/rcsv/HEAD/ext/rcsv/rcsv.c>
  - <https://raw.githubusercontent.com/arp/rcsv/HEAD/ext/rcsv/extconf.rb>
  - <https://raw.githubusercontent.com/arp/rcsv/HEAD/ext/rcsv/libcsv.c>
  - <https://raw.githubusercontent.com/arp/rcsv/HEAD/ext/rcsv/csv.h>
  - <https://raw.githubusercontent.com/arp/rcsv/f9cd754/README.md>
  - <https://raw.githubusercontent.com/arp/rcsv/f9cd754/test/test_rcsv.csv>
  - <https://raw.githubusercontent.com/arp/rcsv/f9cd754/ext/rcsv/rcsv.c>
  - <https://github.com/arp/rcsv/commits/master/bench.rb>
  - <https://github.com/arp/rcsv/commits/master/README.md>
  - <https://github.com/tc3t/dfglib/blob/master/misc/csvPerformanceRuns.md>
  - <https://raw.githubusercontent.com/BurntSushi/rust-csv/0.14.7/README.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/rgamble/libcsv`) · [data/wave1/enrich/raw/github_com_rgamble_libcsv.json](../../../data/wave1/enrich/raw/github_com_rgamble_libcsv.json) (enrichment confidence 0.8)

</details>
