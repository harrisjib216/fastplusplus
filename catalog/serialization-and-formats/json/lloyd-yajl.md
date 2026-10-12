# YAJL

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `ISC` · 🔴 abandoned

> Tiny ISC-licensed C streaming (SAX) JSON parser and generator; its DOM layer parsed 1.3x faster than json-c in nativejson-benchmark.

| | |
|---|---|
| **Beats** | json-c 0.12.1 (also JsonCpp 1.0.0 and Jansson v2.7 in the same suite) |
| **Claimed result** | Project README: 'YAJL is fast ... My hope is that YAJL will perform comparably to the fastest JSON parser out there' (no numbers). Independent shootout rows, derived from page data: DOM parse 103.45 ms vs json-c 134.55 ms (1.30x faster), JsonCpp 165.52 ms (1.60x), Jansson 112.06 ms (1.08x); per file canada 75.62 vs 105.78 ms (json-c), citm 19.55 vs 21.12 ms, twitter 8.28 vs 7.65 ms (YAJL slower). DOM traversal (Statistics) 1.07 ms vs json-c 2.99, JsonCpp 2.62, Jansson 1.62. |
| **Workload** | nativejson-benchmark DOM parse (yajl_tree_parse) of canada.json (2199KB), citm_catalog.json (1737KB) and twitter.json (632KB), time summed over the three files, plus DOM traversal (Statistics). |
| **Metric** | throughput |
| **Hardware** | MacBook Pro (Retina, 15-inch, Mid 2015), Core i7-4980HQ @ 2.80 GHz |
| **Compiler and flags** | clang 7.0 64-bit on macOS as named in the README (in 2016 this must be Apple clang 7.x; inference); build/premake5.lua at the sample's commit a4a9f10 (2016-09-09) sets release config -DNDEBUG, premake optimize "Full", and gmake buildoptions -march=native -Wall -Wextra, identical to the current file |
| **Adoption** | 2.2k stars; widely packaged C library |
| **Last commit** | 2015-09-24 |
| **Links** | [repository](https://github.com/lloyd/yajl) · [benchmark](https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv) |

## Verdict

In nativejson-benchmark's 2016-09-09 sample (Core i7-4980HQ, Apple clang 7.0 64-bit, premake optimize Full with -march=native, best of 10 runs), YAJL at commit 5e3a785 building a yajl_tree DOM took 103.45 ms summed over canada, citm_catalog and twitter vs json-c 0.12.1 at 134.55 ms (1.30x), JsonCpp 1.0.0 at 165.52 ms (1.60x) and Jansson 2.7 at 112.06 ms (1.08x); the margin comes from canada.json (75.62 vs 105.78 ms), YAJL is slower than json-c on twitter.json (8.28 vs 7.65 ms), and its tree traversal took 1.07 vs 2.99 ms. The project itself publishes no comparison: the in-tree perf/perftest.c times validation-only parsing with no callbacks, and the README's hope to match the fastest parser is not borne out (RapidJSON 7.93 ms).

## Use it when

- JSON that arrives in chunks (sockets, pipes, block reads) where you want callbacks as tokens complete instead of buffering the whole document.
- Streams of concatenated or whitespace-separated JSON values (yajl_allow_multiple_values), or filters and reformatters that never build a tree, like the bundled json_reformat and json_verify.
- Validation where a human-readable error with surrounding input text and a position arrow matters (yajl_get_error with verbose set).
- C code bound by json-c 0.12 or JsonCpp 1.0 DOM parsing on number-heavy documents that wants about 1.3-1.6x and a smaller tree, and can take a different API.
- Systems already linked against a distribution yajl package (Debian, Ubuntu and Fedora shipped patches for the three CVEs in July 2023), where switching libraries costs more than the speed gap.

## Skip it when

- Untrusted input on unpatched upstream code: CVE-2017-16516 (escape-sequence decoding bounds), CVE-2022-24795 (heap corruption with \~2 GB inputs in yajl_buf) and CVE-2023-33460 (yajl_tree_parse leak on error) are open upstream, and issue #260 (2026-08-03) shows an ASan heap-buffer-overflow read in hexToDigit at HEAD.
- Throughput-critical DOM parsing: in the same run RapidJSON took 7.93 ms vs YAJL's 103.45 ms over the three files (13x) and cJSON 24.67 ms (about 4.2x, derived from page data); simdjson and yyjson are faster still.
- Serialization: stringify was 2.5x slower than json-c (78.64 vs 30.80 ms), yajl_gen prints doubles with sprintf %.20g so [1.2345] does not round-trip (conformance roundtrip22/23 fail), and strtod/sprintf follow the C locale's decimal separator (open issues #79 and #222).
- Large or deep trees through yajl_tree: it reallocs object and array storage on every added element, mallocs a copy of every string and number text, runs an integer parse plus strtod per number, looks keys up linearly in yajl_tree_get and frees recursively; its own header pitches it for 'smallish JSON docs'.
- Exact numeric and string edge cases: INT64_MIN is rejected as 'integer overflow' through the integer callback, subnormal and underflowing doubles lose YAJL_NUMBER_DOUBLE_VALID in the tree, and tree strings have no length so an embedded \u0000 truncates them (57/66 double and 8/9 string conformance).

## How it is fast

A hand-written byte-at-a-time lexer classifies characters through a 256-entry lookup table, and yajl_string_scan skips runs of ordinary string bytes in a tight loop (the 2.0 'string scanning' tweak the ChangeLog credits with a 20-35% speedup). Strings without escapes are handed to callbacks as pointers into the caller's buffer (zero copy); escaped strings are decoded into one reusable buffer, and nesting is tracked with an explicit byte stack instead of recursion. There is no SIMD; the DOM-parse win over json-c in the benchmark comes mostly from canada.json, and the tree is lighter (12.9 MB vs 33.7 MB for json-c on that file).

## Compared with alternatives

Pick YAJL over json-c, Jansson or cJSON only when you need a push-style SAX parser in C that takes input in arbitrary chunks and multiple concatenated values with verbose error context, and you can carry the distribution CVE patches; for building a DOM, cJSON (about 4.2x faster in the same run), yyjson or simdjson are better, and json-c is faster at stringify.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (CMake builds yajl_s and yajl); small enough to source-drop (about 2,700 lines in src/\*.c) if you supply the CMake-generated yajl_version.h and a yajl/ include directory |
| **Dependencies** | none beyond the C library (strtod, sprintf, malloc) |
| **Minimum toolchain** | C99 compiler (required since 2.0.0); CMake 2.6+ for the bundled build |
| **Platforms** | any: portable C with no intrinsics; ChangeLog and CMakeLists cover Linux, macOS, Windows (MSVC/nmake), NetBSD and QNX |
| **Thread safety** | not documented; from the source all parser state lives in the handle and the character table is const, so one handle per thread works, but number conversion depends on the process-wide C locale |
| **Drop-in for the baseline** | no |

## Gotchas

- Unpaired high surrogate bug (from source reading): yajl_string_decode emits '?' for a \uD800-\uDBFF escape not followed by \u, then also skips the next input byte, so "\ud83dabc" decodes to "?bc"; when the skipped byte is the first half of an escaped backslash, the second backslash is taken as an escape start and hexToDigit reads 4 bytes past the token, which is exactly issue #260's reproducer ["e2d\ud83d\\u0"]. A high surrogate followed by any \u escape is combined without checking for a low surrogate, and UTF-8 validation only checks lead and continuation bit patterns (overlong and surrogate encodings pass).
- yajl_tree_parse silently turns on comment support, measures input with strlen (NUL-terminated only), leaks the partial tree on a parse error (CVE-2023-33460, issues #55, #102, #113, #223, #250 all open) and never checks yajl_alloc for NULL; the lexer also accepts \v and \f as whitespace.
- No malloc failure checks in yajl_alloc, yajl_lex_alloc or yajl_buf (issue #6 open since 2009); the parser has no nesting limit while yajl_tree_free recurses, and yajl_gen has a compile-time depth limit of YAJL_MAX_DEPTH 128 that a caller cannot raise by redefining the macro in its own translation unit.
- Benchmark harness notes (nativejson-benchmark src/tests/yajltest.cpp at a4a9f10), none affecting the timed DOM-parse rows: Parse is best of 10 with the tree freed outside the timer for every library; the Stringify fallback for numbers that are neither int- nor double-valid calls strlen(buffer) on an uninitialized stack array instead of strlen(num) (not reached on the three files, which pass Verify); SaxRoundtrip calls yajl_gen_clear before returning, so its result string is empty, but that output is never checked and the timed work is complete. The 9 double conformance failures (double19, 21-23, 26, 32-34, 37) are all inputs whose value is subnormal or underflows: yajl_tree drops the double-valid flag whenever strtod sets ERANGE.

## Known shortcomings

- nativejson-benchmark 2016 CSV: parse 1.30x over json-c but mid-pack (24th of 40 parse rows), loses to json-c on stringify, prettify and twitter parse, double conformance 57/66. Abandoned 2015-09-24.
- Correctness bug: yajl_string_decode skips one extra byte after an unpaired high surrogate ('\ud83dabc' becomes '?bc'); the same skip is the root cause of the issue #260 heap over-read (hexToDigit). CVE-2017-16516, CVE-2022-24795 and CVE-2023-33460 are unfixed upstream (distros patched July 2023). Numbers stand: last commit 5e3a785 is the commit nativejson-benchmark measured (parse best of 10, free outside the timer). Minor yajltest.cpp bugs do not touch the timed rows (Stringify fallback strlen on an uninitialized buffer, SaxRoundtrip clears the generator before returning). Conformance failures explained: 9 double failures are subnormal/underflow inputs, string04 truncates at \u0000, roundtrip fails from %.20g output and INT64_MIN rejection. Mid-pack: 13x slower than RapidJSON and 4.2x slower than cJSON on parse, stringify 2.5x slower than json-c; locale-dependent number conversion; abandoned since 2015-09-24.

## Caveats and trade-offs

Mixed result, YAJL is mid-pack: its summed DOM parse time ranks 24th of the 40 parse rows in the CSV (rows include the strdup reference and three RapidJSON variants); it is slower than nlohmann v2.0.3 (72.48 ms), cJSON (24.67 ms), ujson4c (8.95 ms) and RapidJSON (7.93 ms, 13x faster), slower than json-c on twitter.json parse (8.28 vs 7.65 ms), and slower than json-c on stringify (78.64 vs 30.80 ms) and prettify (102.12 vs 49.26 ms). SAX round-trip 124.52 ms vs RapidJSON 18.14 ms and SAX statistics 47.35 vs 6.32 ms, so the README's hope to 'perform comparably to the fastest JSON parser out there' is not supported. Conformance in the same suite: parse validation 34/34, parse double 57/66, parse string 8/9, roundtrip 21/27. The sample is a single 2016-09-09 macOS run by RapidJSON's author with YAJL pinned at submodule 5e3a785 (2.1.0 per the README table) and json-c 0.12.1 (acbcc06). The repo ships its own perf/perftest.c (ChangeLog: 'a little in tree performance benchmark') and the ChangeLog cites a 20-35% parsing speedup over an older YAJL, but no comparison numbers against other libraries were found.

Streaming SAX-style callbacks, incremental parsing off a stream, tiny and portable ANSI C, verbose error messages; the tree API used in the benchmark (yajl_tree_parse) is a convenience layer. In the benchmark's canada.json parse the DOM uses 12.9 MB vs json-c 33.7 MB, but needs 501,567 allocations vs 390,651.

## Maintenance

Abandoned: the last commit is 2015-09-24 (5e3a785, the same commit the benchmark measured, so the numbers describe current code), with 89 open issues, 79 open PRs, an unanswered 2025 repository-transfer request (#258) and three CVEs unfixed upstream; ISC-licensed and small enough to vendor, but take the Debian/Ubuntu/Fedora patches and fix the surrogate-skip bug before parsing untrusted input.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent nativejson-benchmark suite: harness code public (src/tests/yajltest.cpp using yajl_tree_parse, same build/premake5.lua), clang 7.0 64-bit on macOS, flags confirmed at the sample's commit a4a9f10 (NDEBUG, optimize Full, -march=native), CPU Core i7-4980HQ; the 'YAJL (C)' and 'json-c (C)' rows sum to the record's 103.45 vs 134.55 ms parse, and every other number in the record matches the CSV.
- **Verifier notes:** Record accurate; only the rank wording (24th of 40 rows, which include strdup and RapidJSON variants) and the flags hedge were tightened. Shortcomings: mid-pack (only beats json-c, JsonCpp and Jansson on DOM parse; loses to json-c on stringify/prettify and twitter parse), 57/66 double conformance, single 2016 run, abandoned since 2015-09-24.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** nativejson-benchmark CSV (verifier); enricher (wave 4)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/conformance.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/a4a9f10f41c515d6abb0f019ab9f5d021ed4bb9e/build/premake5.lua>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/a4a9f10f41c515d6abb0f019ab9f5d021ed4bb9e/src/tests/yajltest.cpp>
  - <https://github.com/miloyip/nativejson-benchmark/tree/a4a9f10f41c515d6abb0f019ab9f5d021ed4bb9e/thirdparty>
  - <https://github.com/lloyd/yajl>
  - <https://github.com/lloyd/yajl/commits>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/perf/perftest.c>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/COPYING>
- **Sources the enricher read:**
  - <https://github.com/lloyd/yajl>
  - <https://github.com/lloyd/yajl/commits/master>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/README>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/COPYING>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/src/CMakeLists.txt>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/src/api/yajl_parse.h>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/src/api/yajl_tree.h>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/src/api/yajl_gen.h>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/src/api/yajl_common.h>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/src/yajl_lex.c>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/src/yajl_lex.h>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/src/yajl_parser.c>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/src/yajl_parser.h>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/src/yajl_tree.c>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/src/yajl_buf.c>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/src/yajl_encode.c>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/src/yajl_alloc.c>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/src/yajl.c>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/src/yajl_gen.c>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/src/yajl_bytestack.h>
  - <https://raw.githubusercontent.com/lloyd/yajl/HEAD/perf/perftest.c>
  - <https://github.com/lloyd/yajl/issues?q=is%3Aissue+CVE+OR+leak+OR+overflow+OR+crash>
  - <https://github.com/lloyd/yajl/issues?q=is%3Aissue+locale>
  - <https://github.com/lloyd/yajl/issues/239>
  - <https://github.com/lloyd/yajl/issues/248>
  - <https://github.com/lloyd/yajl/issues/258>
  - <https://github.com/lloyd/yajl/issues/260>
  - <https://ubuntu.com/security/notices/USN-6233-1>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/a4a9f10f41c515d6abb0f019ab9f5d021ed4bb9e/src/tests/yajltest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/a4a9f10f41c515d6abb0f019ab9f5d021ed4bb9e/src/main.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/conformance.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/data/roundtrip/roundtrip14.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/data/roundtrip/roundtrip22.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/data/roundtrip/roundtrip23.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/data/roundtrip/roundtrip25.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/data/roundtrip/roundtrip26.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/data/roundtrip/roundtrip27.json>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/lloyd/yajl`) · [data/wave4/enrich/raw/github_com_lloyd_yajl.json](../../../data/wave4/enrich/raw/github_com_lloyd_yajl.json) (enrichment confidence 0.85)

</details>
