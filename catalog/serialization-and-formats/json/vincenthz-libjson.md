# libjson (vincenthz)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-2.1-only OR LGPL-3.0-only` · 🟢 active

> Tiny interruptible SAX-style (callback) JSON parser and printer in C; its suite wins over nlohmann/json come from harness code.

| | |
|---|---|
| **Beats** | nlohmann/json |
| **Claimed result** | Against nlohmann/json v2.0.3, sum of the three files (derived from page data): Stringify 68.767 ms vs 87.732 ms (about 1.28x); per file canada.json 61.512 vs 76.315 ms, citm_catalog.json 4.067 vs 7.178 ms, twitter.json 3.188 vs 4.239 ms. These rows time a benchmark-written tree printer: numbers are formatted by the harness with sprintf("%.17g") or "%lld" (libjson does no number conversion), and false/null are printed as quoted strings, so only the canada.json row (no null or false values) produces correct output. The Prettify row (69.279 vs 130.560 ms) is not a valid comparison: the harness never calls json_print_pretty, so libjson emits the same compact text as in Stringify (same time and the same 5.24 MB) while nlohmann runs dump(4). The Statistics row (0.803 vs 2.171 ms) walks the harness's own tree, not libjson code. Parse, the only row using libjson's parser to build a tree, is slower than nlohmann: 107.172 vs 72.476 ms (about 0.68x; canada 77.479 vs 55.591, citm 20.334 vs 9.875, twitter 9.359 vs 7.010 ms); it beats JsonCpp 1.0.0 (165.522 ms, about 1.54x) and json-c 0.12.1 (134.551 ms, about 1.26x) on the totals only because of canada.json (all derived from page data). Parse memory 8.59 MB vs nlohmann 9.90 MB (derived) is the harness tree's footprint. |
| **Workload** | nativejson-benchmark serialisation of three in-memory trees (canada.json, citm_catalog.json, twitter.json) to condensed and prettified JSON strings, plus a DOM statistics traversal, libjson against nlohmann/json v2.0.3. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro (Retina, 15-inch, Mid 2015), Intel Core i7-4980HQ @ 2.80GHz, macOS 64-bit (suite README and result file name) |
| **Compiler and flags** | Apple clang 7.0 64-bit on macOS (suite README: 'MacBook Pro (Retina, 15-inch, Mid 2015, Corei7-4980HQ@2.80GHz) with clang 7.0 64-bit', results updated 2016-9-9); premake5 gmake build, release configuration: optimize "Full" (-O3 under gmake), NDEBUG, buildoptions -march=native -Wall -Wextra (build/premake5.lua); libjson submodule pinned at bd0cad8 (2016-04-19, suite README lists 0.8), nlohmann v2.0.3 per the suite README table |
| **Adoption** | 294 stars |
| **Last commit** | 2026-05-12 |
| **Links** | [repository](https://github.com/vincenthz/libjson) · [benchmark](https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv) |

## Verdict

In nativejson-benchmark's 2016-09-09 sample run (Core i7-4980HQ, Apple clang 7.0, -O3 -march=native, libjson at bd0cad8 vs nlohmann/json v2.0.3), a harness tree printer calling libjson's json_print_raw stringified the three files in 68.8 ms vs 87.7 ms (about 1.28x, derived from page data) while writing false/null as strings, the Prettify win is void (no pretty-printing happened), and the Parse row that uses libjson's parser was 1.48x slower than nlohmann. libjson's own SAX rows have no nlohmann baseline; they beat YAJL on number-heavy canada.json and lose to it on the string-heavy files.

## Use it when

- Input arrives in arbitrary chunks from a socket, pipe or serial line and you want to parse it incrementally with bounded state (no full-document buffer, about 4.3 KB of parser memory in the suite's SAX run).
- Pass-through or reformatting tools (lint, pretty-print, filters) that must keep numbers verbatim: big integers and long decimals are handed over as strings, never rounded.
- Number-heavy SAX workloads where YAJL is the incumbent: in the 2016 suite the SAX round-trip of canada.json took 14.7 ms vs YAJL 112.8 ms, and SAX statistics 11.5 vs 40.9 ms.
- Small embedded or plain-C programs that want a dependency-free parser with optional nesting and size limits, custom allocators and optional C or # comments (jsonstat code-size binary 26,036 bytes vs 42,132 for nlohmann).
- You already have your own tree type (GLib hash tables, an arena) and want the parser to fill it directly through callbacks.

## Skip it when

- You want a DOM or typed access like nlohmann/json: the suite's tree built through json_parser_dom parsed 1.48x slower than nlohmann v2.0.3 (107.2 vs 72.5 ms over three files) and far slower than cJSON (24.7 ms), udp/json-parser (47.3 ms) or RapidJSON (7.9 ms).
- Raw parse throughput matters: the byte-at-a-time state machine has no SIMD; SAX statistics totalled 22.5 ms vs RapidJSON 6.3 ms, and on string-heavy files it lost to YAJL (citm_catalog 7.95 vs 4.74 ms, twitter 3.06 vs 1.71 ms).
- Untrusted input where strict UTF-8 matters: the validator accepts overlong C0/C1 leaders, 5- and 6-byte forms (F8-FD) and code points above U+10FFFF, and \u0000 yields NUL bytes inside values (open issue #31).
- Documents whose root is a scalar (allowed by RFC 7159/8259): the start state only accepts '{' or '[' (RFC 4627 behaviour).
- Static linking into proprietary code: LGPL 2.1 or 3.0 only, and the repo carries no LICENSE file.

## How it is fast

A hand-written table-driven state machine (derived from json.org's JSON_parser.c): each input byte goes through a 128-entry character-class table, a 37-state by 34-class transition table, a parallel buffer-policy table and a UTF-8 header/continuation table, with no backtracking and no number conversion. Parser state is a small struct (256-byte nesting stack, 4 KB value buffer by default; the suite's SAX statistics run peaked at 4,352 bytes). There is no SIMD or bulk scanning: string bytes are copied into the value buffer one at a time, and the printer calls the output callback once per string byte, so throughput lags RapidJSON-class parsers.

## Compared with alternatives

Pick it over cJSON, json.h or udp/json-parser only when you need a resumable, chunk-fed callback parser with constant memory and verbatim number strings; those siblings parse to a DOM 2-6x faster in the same suite. Compared with jsmn (also no number conversion), libjson keeps its own state across arbitrary chunk boundaries instead of needing the whole buffer and a token array; for raw speed use yyjson or simdjson.

## Integration

| | |
|---|---|
| **Form** | source-drop (json.c + json.h; the Makefile also builds a static/shared lib and jsonlint on Linux/BSD) |
| **Dependencies** | none (libc only) |
| **Minimum toolchain** | not documented; plain C using stdint.h, inline and // comments (C99 or C89 with extensions), with shims for MSVC before 2010; header has extern "C" guards for C++ |
| **Platforms** | any (portable byte-wise C, no SIMD); the author recommends embedding the two files rather than using the build system on Windows or macOS |
| **Thread safety** | not documented; by code reading all mutable state lives in caller-owned json_parser, json_printer and json_parser_dom structs and the lookup tables are only read, so one context per thread is independent |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaws behind the numbers (nativejson-benchmark src/tests/vincenthzlibjsontest.cpp, unchanged since 2016): tree_print ignores its print_func argument and always calls json_print_raw, so the Prettify row is compact output and void; it emits false and null as JSON strings, so citm_catalog and twitter Stringify output is wrong; numbers are formatted by harness sprintf and parsed by harness strtoll/atof; and the Parse row (the one libjson loses) includes the harness's grow-by-one realloc per appended element (334,389 allocations on canada.json vs 170,254 for nlohmann).
- Conformance correction: sample/conformance.csv is stale. Harness fixes 274281a and 95936a1 (2016-09-10, a day after the sample run) give 34 of 34 parse validation and 9 of 9 strings; the remaining 8 of 66 double failures are harness strtoll saturating big integers at 9.2233720368547758e18, and all 10 of 27 round-trip failures are harness artifacts (false/null printed as strings, %.17g formatting). None is attributable to libjson's parser.
- Security history: json_parser_dom's dom_push grew its stack by newsize bytes instead of elements (heap overflow past 1,024 nesting levels). The fix e03b4a9 was authored 2018-10-06 but only merged to master on 2024-04-27 (PR #27), so copies vendored before 2024 are vulnerable. Issues #31-#33 (2026-06-15: lax UTF-8, uint32 overflow in dom_push, stack[-1] write on direct API misuse) are open with no maintainer reply; json_parser_dom_callback also ignores dom_push's out-of-memory return.
- API quirks: the README names json_printer_init/_pretty/_raw but the header exports json_print_init, json_print_pretty and json_print_raw; printer functions always return 0 and ignore the output callback's return value; json_parser_dom_init zeroes the struct before allocating, so custom allocators never apply to the initial 1,024-entry stack; nesting and size limits default to 0 (unlimited). Unrelated projects named libjson (SourceForge, xnacly) sit in the same category.

## Known shortcomings

- nativejson-benchmark 2016 run: the wins over nlohmann come from benchmark-written tree code (libjson has no DOM): tree_print never calls json_print_pretty (prettify row void, the 1.88x dropped) and writes false/null as quoted strings (citm and twitter stringify output wrong); parse is 1.48x slower than nlohmann. dom_push heap overflow fixed 2018.
- Enricher: the Parse row (1.48x slower than nlohmann) includes the harness's grow-by-one realloc (334,389 allocs vs 170,254 on canada.json); the suite's sample/conformance.csv is stale (harness fixes 274281a/95936a1 of 2016-09-10 give 34/34 validation and 9/9 strings, and the remaining double and roundtrip failures are harness bugs, not libjson). The dom_push heap-overflow fix (e03b4a9, authored 2018-10-06) was merged only 2024-04-27 (PR #27), so copies before 2024 are vulnerable; the UTF-8 table accepts C0/C1 and F5-FD; top-level scalars are rejected (RFC 4627); open issues #31-#33 unanswered.

## Caveats and trade-offs

Harness flaws behind the numbers (src/tests/vincenthzlibjsontest.cpp, unchanged at HEAD): libjson has 'No object model integrated' (README), so the suite builds its own tree through json_parser_dom callbacks (tree_create_structure, tree_create_data, tree_append) and prints it with its own tree_print; tree_print ignores the json_print_pretty argument and always calls json_print_raw, so the Prettify row is compact output and the 1.88x prettify figure is void; tree_print emits JSON_FALSE and JSON_NULL as JSON_STRING, so twitter.json (2446 false, 1946 null) and citm_catalog.json (1263 null) are serialised wrongly; number formatting is harness sprintf. The Statistics win measures the harness tree. Parse, the row that exercises libjson, is 1.48x slower than nlohmann/json. libjson's own SAX rows have no nlohmann baseline (SAX round-trip 30.778 ms, SAX statistics 22.478 ms, versus RapidJSON 18.143 and 6.318 ms). Conformance in the same suite: 2 of 34 parse-validation, 9 of 66 double-parse and 10 of 27 round-trip tests fail (nlohmann fails 4 of 27 round-trip). The README's 'Fast: use efficient code and small parsing tables for maximum efficiency' has no numbers. Security note: json_parser_dom's dom_push realloc'd its stack without multiplying by the element size (heap overflow past 1024 nesting levels), fixed in e03b4a9 (2018-10-06) after the 2016 run; the test files never nest that deep. Sample results are dated 2016-09-09 and use 2016 library versions (nlohmann v2.0.3); today's ratios will differ. Per-library totals are sums of the three per-file rows and are derived from page data. LGPL-2.1-only OR LGPL-3.0-only (header in json.c; no LICENSE file).

Interruptible SAX-style (SAJ) parser and printer with no object model and no number conversion: the user supplies the tree and converts numbers. LGPL (header in json.c says version 2.1 or 3.0 only); the repo has no LICENSE file. Optional nesting and size limits, UTF-8 validation, comments, custom allocators. Build system is only meant for testing; the author recommends embedding the two source files.

## Maintenance

Low-activity but alive (PR merges in 2024-04 and 2026-05, last commit 2026-05-12) with three security issues from 2026-06 unanswered; LGPL-2.1-only OR LGPL-3.0-only per the file headers (no LICENSE file), small enough to vendor and audit, and kept with tier C because every row that beats nlohmann times buggy benchmark code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now C.
- **Tier reason:** The suite meets A methodology (public harness src/tests/vincenthzlibjsontest.cpp and src/tests/nlohmanntest.cpp, clang 7.0, premake5 optimize Full + -march=native, Core i7-4980HQ), but every libjson row that beats nlohmann/json times benchmark-written code with correctness bugs: tree_print ignores its print_func argument and always calls json_print_raw, so the Prettify row produces compact output, and it emits JSON false and null as quoted strings, so the citm_catalog.json and twitter.json Stringify output is wrong. The one row that exercises libjson's own parser against nlohmann (Parse) is slower, so the bug-in-measured-path rule caps it at C.
- **Verifier notes:** Every number matches the CSV rows 'Vinenthz/libjson (C)' and 'Nlohmann (C++11)', but the wins over nlohmann come from benchmark-written tree code with two correctness bugs (Prettify never pretty-prints; false/null written as strings), and libjson's own parse is slower, so A to C. Shortcomings to record: prettify row void (compact output), stringify output wrong for false/null on citm and twitter, statistics and number formatting are harness code, parse 1.48x slower than nlohmann, conformance failures, 2016 data, pre-2018 dom_push heap overflow. Metadata confirmed: 294 stars, not a fork, last commit 2026-05-12.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** nativejson-benchmark CSV (verifier downgrade A to C); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/conformance.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/build/premake5.lua>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/nlohmanntest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/vincenthzlibjsontest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/twitter.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/citm_catalog.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/canada.json>
  - <https://github.com/miloyip/nativejson-benchmark/tree/master/thirdparty>
  - <https://github.com/vincenthz/libjson>
  - <https://github.com/vincenthz/libjson/commits>
  - <https://github.com/vincenthz/libjson/commits/master>
  - <https://github.com/vincenthz/libjson/commit/bd0cad8>
  - <https://github.com/vincenthz/libjson/commit/e03b4a9098311a0a2a3a3986ecc38b75cf5f77c4>
  - <https://github.com/vincenthz/libjson/blob/master/json.c>
  - <https://raw.githubusercontent.com/vincenthz/libjson/HEAD/README.md>
  - <https://raw.githubusercontent.com/vincenthz/libjson/HEAD/json.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/vincenthz/libjson/HEAD/README.md>
  - <https://raw.githubusercontent.com/vincenthz/libjson/HEAD/json.c>
  - <https://raw.githubusercontent.com/vincenthz/libjson/HEAD/json.h>
  - <https://raw.githubusercontent.com/vincenthz/libjson/HEAD/Makefile>
  - <https://raw.githubusercontent.com/vincenthz/libjson/HEAD/jsonlint.c>
  - <https://raw.githubusercontent.com/vincenthz/libjson/HEAD/documentation.md>
  - <https://github.com/vincenthz/libjson>
  - <https://github.com/vincenthz/libjson/commits/master>
  - <https://github.com/vincenthz/libjson/issues?q=is%3Aissue>
  - <https://github.com/vincenthz/libjson/issues/24>
  - <https://github.com/vincenthz/libjson/issues/31>
  - <https://github.com/vincenthz/libjson/issues/32>
  - <https://github.com/vincenthz/libjson/issues/33>
  - <https://github.com/vincenthz/libjson/pull/27>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/vincenthzlibjsontest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/conformance.csv>
  - https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/conformance_Vinenthz_libjson%20(C).md
  - <https://github.com/miloyip/nativejson-benchmark/commits/master/src/tests/vincenthzlibjsontest.cpp>
  - <https://github.com/miloyip/nativejson-benchmark/commit/274281a>
  - <https://github.com/miloyip/nativejson-benchmark/commit/95936a1>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/jsonchecker/fail02.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/jsonchecker/fail32.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/roundtrip/roundtrip01.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/roundtrip/roundtrip03.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/roundtrip/roundtrip10.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/roundtrip/roundtrip20.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/roundtrip/roundtrip27.json>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/vincenthz/libjson`) · [data/wave4/enrich/raw/github_com_vincenthz_libjson.json](../../../data/wave4/enrich/raw/github_com_vincenthz_libjson.json) (enrichment confidence 0.8)

</details>
