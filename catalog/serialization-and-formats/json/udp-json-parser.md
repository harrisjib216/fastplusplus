# json-parser (udp/json-parser)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `BSD-2-Clause` · 🟢 active

> Two-file, non-recursive C89 DOM parser; parsed 1.5x faster than nlohmann/json 2.0.3 in a 2016 run, entirely on number-heavy input.

| | |
|---|---|
| **Beats** | nlohmann/json v2.0.3 (same suite also: json-c 0.12.1, Jansson v2.7, JsonCpp 1.0.0) |
| **Claimed result** | Parse time, sum of the three files (derived from page data): udp/json-parser 47.338 ms (29.536 + 13.058 + 4.744) vs Nlohmann 72.476 ms (55.591 + 9.875 + 7.010), about 1.5x; vs Jansson 112.056 ms about 2.4x, json-c 134.551 ms about 2.8x, JsonCpp 165.522 ms about 3.5x. The win over Nlohmann comes entirely from canada.json (29.536 vs 55.591 ms), the double-heavy file where udp's number parser is not correctly rounded; on citm_catalog.json plus twitter.json udp takes 17.802 ms vs Nlohmann 16.885 ms (about 5% slower), Jansson 33.591 ms (about 1.9x), json-c 28.767 ms (about 1.6x) and JsonCpp 23.064 ms (about 1.3x). Stringify/prettify come from the separate udp/json-builder library, which prints doubles with sprintf("%g") (6 significant digits), so its canada.json rows time lossy output and are not comparable; on citm_catalog.json plus twitter.json (integers and strings, one 0.087) stringify is 2.444 ms vs Nlohmann 11.417 ms (about 4.7x), Jansson 5.689 ms (about 2.3x) and RapidJSON 1.871 ms, prettify 2.797 ms vs Nlohmann 17.810 ms (about 6.4x). All ratios derived from page data. |
| **Workload** | nativejson-benchmark: parse in-memory canada.json (2199KB), citm_catalog.json (1737KB) and twitter.json (632KB) into a DOM with udp/json-parser (json_parse_ex, suite README lists 1.1.0, submodule 7053321); stringify and prettify of that DOM use the separate udp/json-builder library (json_measure_ex + json_serialize_ex, submodule 19c739f). |
| **Metric** | throughput |
| **Hardware** | MacBook Pro (Retina, 15-inch, Mid 2015), Core i7-4980HQ @ 2.80GHz |
| **Compiler and flags** | clang 7.0, 64-bit macOS. Flags are not recorded in the results file; the public build/premake5.lua sets the release configuration to optimize Full with NDEBUG, and gmake builds add -march=native -Wall -Wextra |
| **Adoption** | 1.3k stars |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/json-parser/json-parser) · [benchmark](https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv) |

## Verdict

In nativejson-benchmark's 2016 sample (clang 7.0, release build with NDEBUG and -march=native, Core i7-4980HQ, macOS), json-parser parsed canada, citm_catalog and twitter in 47.3 ms total against nlohmann/json 2.0.3's 72.5 ms, Jansson 2.7's 112.1 ms, json-c 0.12.1's 134.6 ms and JsonCpp 1.0.0's 165.5 ms; the lead over nlohmann rests on canada.json (29.5 vs 55.6 ms), where its inexact number parser does less work, and it is slightly slower than nlohmann on the other two files. The project itself publishes no numbers.

## Use it when

- C89 or embedded C code that wants two vendorable files (json.c, json.h) with no dependencies beyond libm and a plain read-only DOM for configs and messages.
- Untrusted input where stack depth and memory must be bounded: parsing never recurses, and json_settings.max_memory caps the total allocation; a custom allocator (arena, pool) can be plugged in with user data.
- Read-mostly documents dominated by integers and strings, where the exact-size allocations keep each node's arrays and key names contiguous.
- Tools that need per-value source positions for error reporting (JSON_TRACK_SOURCE).

## Skip it when

- Data where doubles must come back bit-exact: only 37 of 66 double-parse conformance tests pass (nlohmann 66 of 66), because mantissa, fraction and exponent are combined with separate floating-point operations.
- Parse throughput as the goal: in the same 2016 run cJSON parsed the three files in 24.7 ms, RapidJSON in 7.9 ms and sheredom/json.h canada.json in 9.4 ms, against json-parser's 47.3 ms; on citm_catalog.json plus twitter.json it was about 5% slower than nlohmann/json 2.0.3.
- Round-tripping documents: the companion json-builder prints doubles with sprintf("%g") (6 significant digits, unchanged at HEAD), so parse-then-serialize silently truncates coordinates, prices and timestamps stored as doubles.
- Large objects queried by key: the C++ operator[] does a linear strcmp scan over the entries, and there is no hash index.
- Integers outside int64 or unsigned 64-bit values: json_int_t is signed only; HEAD converts overflowing integers to double, while the 1.1.0-era code measured in the benchmark overflowed signed arithmetic (issue #185).

## How it is fast

It scans the input twice: the first pass validates, creates one node per value and counts array and object lengths, string lengths and the total bytes of each object's key names; the second pass allocates exactly sized arrays and strings plus one block per object holding its entries and all key names, then copies the characters in. Numbers are parsed by hand in the first pass (digit accumulation, fraction divided by pow(10, digits), then multiplied by pow(10, exponent)) instead of strtod, which is cheap and locale-free but not correctly rounded; that number path is where the canada.json advantage over nlohmann/json comes from. Parsing and freeing use parent pointers instead of recursion.

## Compared with alternatives

Pick json-parser over cJSON (about 1.9x faster parse in the same run, recursive with a 1000-level CJSON_NESTING_LIMIT, built-in printing with %1.15g/%1.17g) or sheredom/json.h when you need a non-recursive C89 parser with a hard memory cap, pluggable allocator and source positions; pick cJSON or yyjson when throughput or exact numbers matter more.

## Integration

| | |
|---|---|
| **Form** | source-drop (json.c and json.h), or static and shared lib via the autoconf configure/Makefile with a pkg-config file |
| **Dependencies** | none (libm for pow); json-builder (separate repository) for serialization |
| **Minimum toolchain** | C89 compiler; json_int_t is int_fast64_t under C99/C++11, long under C89, __int64 on MSVC |
| **Platforms** | any |
| **Thread safety** | not documented; json.c has no mutable global state and no locale calls, so separate json_parse_ex calls are independent (inferred from source), and a parsed tree is plain data |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark detail behind the numbers: nativejson-benchmark's udpjsontest.cpp parses with settings.value_extra = json_builder_extra so json-builder can later print the tree, which adds an int and two size_t (about 24 bytes on 64-bit) to every node; the reported 17.2 MB parse footprint and part of the parse time include that, so a parse-only user allocates less. The stringify and prettify rows time json-builder, not json-parser, and its %g output on canada.json is lossy, so those rows are not comparable.
- The measured commit differs from HEAD in number handling: at 7053321 the fraction digits accumulate in json_int_t and integer digits have no overflow check; HEAD accumulates the fraction in a double and converts overflowing integers to double (September 2026 commits including 'Fix improper rejection of long floats' for #178; the UBSan overflow report #185 is closed) and fixes surrogate-pair decoding. Both versions apply the exponent as a separate pow(10, e) multiply, so values near the double limits can overflow to inf or underflow to 0 (for example 0.1e309).
- json_parse_ex strcpy's its message into the caller's error buffer without a length; pass at least json_error_max (128) bytes. Issue #175 (unbounded error writes) is open for a v2.0.0 API change.
- No version after 1.1.0 (configure.ac still says 1.1.0 and the GitHub releases page is empty); the maintained repository is github.com/json-parser/json-parser and the September 2026 fixes exist only on master.

## Known shortcomings

- nativejson-benchmark 2016 run: the stringify/prettify rows time json-builder (a separate repo) printing doubles with %g at 6 significant digits, so canada.json output is lossy; the parse win over nlohmann holds only on canada, where doubles are rounded inexactly (37/66 conformance). Claim restated on citm and twitter parse only. Measured versions uncertain (suite README edited after the run). Repo moved to json-parser/json-parser.
- Enricher: two-pass non-recursive parser whose canada.json win rests on hand-rolled inexact number parsing; the pinned 7053321 accumulates the fraction in json_int_t with no integer overflow check (#185; HEAD switched to double), json-builder's %g output is still lossy at HEAD, and open #175 leaves the error-buffer strcpy unbounded. The harness sets value_extra=json_builder_extra (about +24 B per node), inflating the 17.2 MB parse-memory figure. GitHub releases page empty; still 1.1.0.

## Caveats and trade-offs

Number handling is loose: the parser builds a double as integer part + fraction / pow(10, digits), then multiplies by pow(10, exponent) (same code at the pinned 7053321 and at HEAD), so values are not correctly rounded (37 of 66 double-parse conformance tests pass vs 66 of 66 for Nlohmann), and the parse win over Nlohmann exists only on the double-heavy canada.json; on the other two files it is about 5% slower. Output rows are produced by udp/json-builder, a separate repository, which formats doubles with "%g" (6 significant digits, still so at HEAD): canada.json's 17-digit coordinates are truncated, so those stringify/prettify timings measure lossy output (22 of 27 roundtrip tests pass). The benchmark wrapper's own comment says stringify is 'Very slow in the current version'. Third-party suite by the RapidJSON author (disclosed in its README), sample numbers from 2016-09-09; Library versions come from the suite README's table, which was edited after the 2016-09-09 sample run (it lists cJSON 1.5.0, released 2017-05-02), so the exact versions measured are not certain. Conformance: 26 of 34 parse-validation, 37 of 66 double-parse, 9 of 9 string, 22 of 27 roundtrip (Nlohmann 34/34, 66/66, 9/9, 23/27). RapidJSON parses the three files in 7.932 ms. The project README gives no performance numbers, only design claims (never recurses, allocates only what it needs). September 2026 commits fixed parser correctness edge cases (rejection of long floats #178, overflow handling, UTF-16 surrogate pairs); the benchmark files exercise none of them (canada.json parsed, no \u escapes in citm_catalog.json or twitter.json), so the 2016 numbers are not capped by them. The repository now lives at github.com/json-parser/json-parser (udp/json-parser redirects there). Flags come from the repo's premake file, not from the result file.

Parse memory is higher than nlohmann: 17,195,056 bytes after parsing the three files vs 9,897,872 for Nlohmann (about 1.7x more, derived from page data), though lower than json-c (49,886,288). The README itself claims only a very low footprint, never recursing and never allocating more than needed. C89-portable, no dependencies, small API; the json-builder companion is needed for output.

## Maintenance

Revived in 2026 (repository moved to the json-parser organisation, fixes through 2026-09-19, still versioned 1.1.0 with no packaged release), BSD-2-Clause and two files, so easy to vendor; usable and copyable, but the speed entry is a 2016 parse run and serialization comes from a separate, lossy library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now A.
- **Tier reason:** For parsing, the independent nativejson-benchmark sample CSV has udp/json-parser and Nlohmann/Jansson/json-c/JsonCpp '1. Parse' rows on a Core i7-4980HQ with clang 7.0 64-bit; the harness is public (src/tests/udpjsontest.cpp calls json_parse_ex; src/tests/nlohmanntest.cpp) and build/premake5.lua sets release optimize Full, NDEBUG and -march=native, so A holds for the parse claim. The stringify/prettify claim is not valid on canada.json (lossy %g output from udp/json-builder) and is restated on the other two files.
- **Verifier notes:** Numbers match the CSV, but the stringify/prettify sums include canada.json rows where udp/json-builder emits doubles with %g (6 significant digits), i.e. lossy output, so I restated them on citm+twitter only; the parse win over Nlohmann is confined to canada.json, where udp's doubles are inexactly rounded. Shortcomings to record: lossy %g serializer (json-builder, separate repo) behind the canada output rows, inexact double parsing (37/66), no parse win over Nlohmann outside canada.json, 2016 data. Metadata checked (BSD-2-Clause, 1.3k stars, last commit 2026-09-19); the repo moved to github.com/json-parser/json-parser, so a repo_url override may be worth recording.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Shortcomings recorded by:** nativejson-benchmark CSV (verifier downgrade, claim narrowed); enricher code reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/build/premake5.lua>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/conformance.csv>
  - <https://github.com/miloyip/nativejson-benchmark/tree/master/src/tests>
  - <https://github.com/miloyip/nativejson-benchmark/tree/master/sample>
  - <https://github.com/miloyip/nativejson-benchmark/tree/master/thirdparty>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/udpjsontest.cpp>
  - <https://raw.githubusercontent.com/udp/json-parser/v1.1.0/json.c>
  - <https://raw.githubusercontent.com/udp/json-parser/7053321/json.c>
  - <https://raw.githubusercontent.com/udp/json-parser/HEAD/json.c>
  - <https://raw.githubusercontent.com/udp/json-parser/HEAD/README.md>
  - <https://raw.githubusercontent.com/udp/json-builder/19c739f/json-builder.c>
  - <https://raw.githubusercontent.com/udp/json-builder/HEAD/json-builder.c>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/citm_catalog.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/twitter.json>
  - <https://github.com/udp/json-parser>
  - <https://github.com/udp/json-parser/commits/master.atom>
  - <https://github.com/json-parser/json-parser>
- **Sources the enricher read:**
  - <https://github.com/json-parser/json-parser>
  - <https://github.com/json-parser/json-parser/commits/master>
  - <https://github.com/json-parser/json-parser/issues?q=is%3Aissue>
  - <https://github.com/json-parser/json-parser/issues/175>
  - <https://github.com/json-parser/json-parser/issues/178>
  - <https://github.com/json-parser/json-parser/issues/185>
  - <https://github.com/json-parser/json-parser/releases>
  - <https://raw.githubusercontent.com/json-parser/json-parser/HEAD/README.md>
  - <https://raw.githubusercontent.com/json-parser/json-parser/HEAD/json.c>
  - <https://raw.githubusercontent.com/json-parser/json-parser/HEAD/json.h>
  - <https://raw.githubusercontent.com/json-parser/json-parser/HEAD/AUTHORS>
  - <https://raw.githubusercontent.com/json-parser/json-parser/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/json-parser/json-parser/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/json-parser/json-parser/HEAD/Makefile.in>
  - <https://raw.githubusercontent.com/json-parser/json-parser/7053321/json.c>
  - <https://raw.githubusercontent.com/json-parser/json-parser/7053321/json.h>
  - <https://raw.githubusercontent.com/json-parser/json-builder/HEAD/json-builder.c>
  - <https://raw.githubusercontent.com/json-parser/json-builder/HEAD/json-builder.h>
  - <https://raw.githubusercontent.com/json-parser/json-builder/HEAD/README.md>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/conformance.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/udpjsontest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/build/premake5.lua>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/jsonchecker/fail15.json>
  - <https://raw.githubusercontent.com/DaveGamble/cJSON/HEAD/cJSON.c>
  - <https://raw.githubusercontent.com/DaveGamble/cJSON/HEAD/cJSON.h>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/udp/json-parser`) · [data/wave4/enrich/raw/github_com_udp_json_parser.json](../../../data/wave4/enrich/raw/github_com_udp_json_parser.json) (enrichment confidence 0.75)

</details>
