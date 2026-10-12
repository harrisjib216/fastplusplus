# PicoJSON

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `BSD-2-Clause` · 🔴 abandoned

> Single-header C++03-compatible JSON DOM on std::map/std::vector; stringified 1.09x faster than nlohmann/json 2.0.3 in a 2016 run, parses 1.9x slower.

| | |
|---|---|
| **Beats** | nlohmann/json |
| **Claimed result** | Stringify total 80.2 ms vs 87.7 ms for nlohmann (1.09x) and 94.3 ms for JsonCpp (1.18x); DOM statistics traversal 0.89 ms vs 2.17 ms for nlohmann (2.4x) and 2.62 ms for JsonCpp (2.9x) (all derived from page data). Parse is slower than nlohmann: 140.3 ms vs 72.5 ms (0.52x) but 1.18x faster than JsonCpp's 165.5 ms (derived). |
| **Workload** | nativejson-benchmark stringify of three DOMs (canada.json, citm_catalog.json, twitter.json) and a DOM statistics traversal, PicoJSON 1.3.0 against nlohmann/json v2.0.3 and JsonCpp. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro (Retina, 15-inch, Mid 2015), Intel Core i7-4980HQ @ 2.80GHz, macOS 64-bit (suite README and result file name) |
| **Compiler and flags** | Apple clang 7.0 64-bit on macOS (suite README: 'MacBook Pro (Retina, 15-inch, Mid 2015, Corei7-4980HQ@2.80GHz) with clang 7.0 64-bit', results updated 2016-9-9); premake5 gmake build, release configuration: optimize "Full" (-O3 under gmake), NDEBUG, buildoptions -march=native -Wall -Wextra (build/premake5.lua); PicoJSON 1.3.0 (suite README; submodule pinned at 11ac591 at HEAD), nlohmann v2.0.3, JsonCpp 1.0.0 per the suite README table |
| **Adoption** | 1.2k stars |
| **Last commit** | 2021-01-17 |
| **Links** | [repository](https://github.com/kazuho/picojson) · [benchmark](https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv) |

## Verdict

In nativejson-benchmark's committed 2016 sample (Apple clang 7.0, optimize Full with -march=native, Core i7-4980HQ, macOS), PicoJSON 1.3.0 stringified canada, citm_catalog and twitter in 80.2 ms total against nlohmann/json 2.0.3's 87.7 ms (1.09x) and JsonCpp 1.0.0's 94.3 ms (1.18x), and its statistics walk took 0.89 vs 2.17 ms, a gap inflated by the harness copying strings on the nlohmann side; it parsed about 1.9x slower than nlohmann. The project makes no speed claim.

## Use it when

- Small configuration or RPC payloads (KB range) in a C++ codebase that wants one dependency-free header and plain std::vector/std::map access to the result.
- Old toolchains: the header keeps C++03 fallbacks (rvalue references and std::isnan only when available), so it builds where nlohmann/json 3.x (C++11) or Boost.JSON cannot.
- Parsing straight from a std::istream or any input iterator without first buffering the whole document.
- Code that already uses PicoJSON and only needs compact stringify of small documents, where the 2016 run showed it slightly ahead of nlohmann 2.0.3 on all three files (canada 71.5 vs 76.3 ms, citm_catalog 5.4 vs 7.2 ms, twitter 3.2 vs 4.2 ms).

## Skip it when

- Parse throughput: in the same 2016 CSV it parsed the three files in 140.3 ms against nlohmann 2.0.3's 72.5 ms, cJSON's 24.7 ms and RapidJSON's 7.9 ms; zzzJSON's later table (i7-6700, g++ 7.3 -O3, versions not stated) has it stringifying the nativejson-benchmark files in 108 ms against nlohmann's 24 ms, so the stringify edge did not survive newer nlohmann releases.
- Untrusted input: a number that overflows a double (for example 1e400) makes value(double) throw std::overflow_error out of parse() instead of returning an error (open issues #94 from 2017 and #162 from 2025; PR #165 to catch it was closed unmerged on 2026-10-05), and the depth limit added in PR #135 only counts arrays (see gotchas).
- 64-bit integers, exact decimals or byte-exact round-trips: integers go through double unless PICOJSON_USE_INT64 is defined, numbers are printed with %.17g (1.2345 becomes 1.2344999999999999), keys come back sorted by std::map, and '/' is escaped as \/; 11 of 27 round-trip tests fail in nativejson-benchmark.
- Builds with -fno-exceptions (issue #117) or code that includes immintrin.h on GCC 11+, whose _serialize() macro collides with picojson's private _serialize member (issue #141, open).
- Projects that need a maintained dependency: the last commit is 2021-01-17 and 34 issues and 27 pull requests are open.

## How it is fast

There is no speed technique: the parser is an iterator-generic recursive descent that reads one byte at a time through input&lt;Iter&gt;::getc(), copies each number into a temporary std::string before strtod, and heap-allocates every string, array and object separately (714,703 allocations for the three benchmark files against 254,045 for nlohmann 2.0.3). Its stringify edge in the 2016 run comes from appending everything to one std::string through std::back_inserter (16-18 allocations per file, against 3,821 for nlohmann 2.0.3 on twitter.json), with numbers printed by snprintf %.17g. The statistics-traversal edge is partly a harness artefact (see gotchas).

## Compared with alternatives

Pick PicoJSON over json.h, cJSON or Jansson only when you want a C++ header that hands back std::vector/std::map and builds on pre-C++11 compilers; for speed, Boost.JSON, yyjson or simdjson parse many times faster, and even among the 2016 nativejson-benchmark entries udp/json-parser (47.3 ms) and json.h parsed far faster than PicoJSON's 140.3 ms.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (C++ standard library only; uses localeconv() from &lt;locale.h&gt; unless PICOJSON_USE_LOCALE is 0) |
| **Minimum toolchain** | C++03 or later (C++11 features are used when detected); CI history covers gcc and clang via make test, and MSVC warnings are suppressed in the header |
| **Platforms** | any |
| **Thread safety** | Concurrent reads of a const value are safe in the default build, but the operator&gt;&gt; interface stores its error in a global (README: not thread-safe), parse and serialize call localeconv() for every number, non-const get(key)/get(idx) return a reference to a function-local static null on a miss, and with PICOJSON_USE_INT64 a const get&lt;double&gt;() rewrites the value in place. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the 2.4x statistics figure: nativejson-benchmark's nlohmanntest.cpp walks the DOM with it.key() and v.get&lt;std::string&gt;(), which in nlohmann 2.0.3 return std::string by value (json.hpp lines 2897 and 7289), so nlohmann's walk copies every key and string (325 and 3,804 allocations in its citm_catalog and twitter statistics rows) while picojsontest.cpp takes const references and allocates nothing; the twitter row (0.664 vs 0.090 ms, 7.4x) is mostly copying, and canada.json, whose short keys fit the small-string buffer (0 allocations in nlohmann's row), shows 1.68x (0.990 vs 0.589 ms, derived from page data).
- From reading picojson.h at HEAD (not executed): default_parse_context::parse_object_start checks depths_ but never decrements it, so the DEFAULT_MAX_DEPTHS=100 limit from PR #135 applies only to arrays and a document of deeply nested objects ({"a":{"a":...}}) recurses without bound; null_parse_context also increments depths_ for every object member.
- The two-argument parse(value&, const std::string&) discards the end iterator, so trailing garbage such as ["x"]] or {} "y" is accepted without error; with the four-argument form you must compare the returned iterator with the end yourself. This, plus leading zeros accepted via strtod (013), is why 4 of 34 parse-validation tests fail.
- get&lt;T&gt;() on the wrong type throws std::runtime_error (PICOJSON_ASSERT), and constructing a value from NaN or infinity throws std::overflow_error; there is no non-throwing build mode.

## Known shortcomings

- nativejson-benchmark 2016 run: stringify 1.09x and stats 2.4x vs nlohmann, but the parse win over JsonCpp holds only on canada.json and it parses slower than json-c. Abandoned since 2021-01-17.
- Enricher: the 2.4x statistics win comes from nativejson-benchmark's nlohmanntest.cpp walking the DOM with it.key() and get&lt;std::string&gt;(), which return std::string by value in nlohmann 2.0.3, so nlohmann copies every key and string (325/3,804 allocations in its citm/twitter rows vs 0 for PicoJSON; the twitter row 7.4x is mostly copying, the canada row 1.68x). Code bugs: object nesting never decrements depths_, so the 100-depth limit covers arrays only; 1e400 throws std::overflow_error out of parse() (#94, #162); the 2-arg parse accepts trailing garbage. The stringify edge is gone against newer nlohmann (zzzJSON table 108 vs 24 ms).

## Caveats and trade-offs

The README makes no performance claim; the only numbers are the third-party suite's. The wins are small (stringify 1.09x over nlohmann, though on all three files: canada 71.546 vs 76.315 ms, citm 5.449 vs 7.178, twitter 3.167 vs 4.239) or on a traversal of the library's own value type (statistics 0.891 vs 2.171 ms). PicoJSON is about 1.9x slower than nlohmann/json at parsing (140.256 vs 72.476 ms) and slower than json-c (134.551 ms); its parse-total win over JsonCpp (165.522 ms) comes only from canada.json (97.212 vs 142.458 ms), while it is slower than JsonCpp on citm_catalog.json (31.023 vs 14.587) and twitter.json (12.021 vs 8.477). It makes 714,703 allocations to parse the three files (nlohmann 254,045). The suite has no PicoJSON prettify row. Conformance in the same suite: 4 of 34 parse-validation and 11 of 27 round-trip tests fail. Last commit is 2021-01-17, so the repo is treated as abandoned although the author has not said so. Sample results are dated 2016-09-09 and use 2016 library versions; today's ratios will differ. Per-library totals are sums of the three per-file rows (canada.json 2199KB, citm_catalog.json 1737KB, twitter.json 632KB) and are derived from page data.

Header-only, dependency-free C++ JSON parser and serializer with STL-friendly types and pull or streaming interfaces; a small variant tree (picojson::value). No prettified-output row in the sample.

## Maintenance

Unmaintained since 2021-01-17 (1.3.1-dev, no release since 1.3.0 in 2015) with open DoS reports on number overflow; BSD-2-Clause and a single header, so easy to vendor, but its speed entry rests on a 2016 run against a 2016 nlohmann release that newer versions overtake.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent nativejson-benchmark: public harness (src/tests/picojsontest.cpp uses value::serialize() and a GenStat walk of picojson::value; src/tests/nlohmanntest.cpp uses dump() and the same walk), clang 7.0 64-bit, build/premake5.lua release optimize Full, NDEBUG, -march=native, Core i7-4980HQ; the stringify and statistics rows against nlohmann/json v2.0.3 match the CSV, so A holds.
- **Verifier notes:** Every number in the record matches the CSV rows 'PicoJSON (C++)', 'Nlohmann (C++11)' and 'JsonCpp (C++)'; I only added that the parse win over JsonCpp is confined to canada.json and that json-c also out-parses it. Shortcomings to record: no project speed claim, small stringify margin, about 1.9x slower parse than nlohmann, conformance failures, 2016 data, abandoned since 2021. Metadata confirmed: BSD-2-Clause, 1.2k stars, not a fork, last commit 2021-01-17.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** nativejson-benchmark CSV (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/conformance.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/build/premake5.lua>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/nlohmanntest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/picojsontest.cpp>
  - <https://github.com/miloyip/nativejson-benchmark/tree/master/thirdparty>
  - <https://github.com/kazuho/picojson>
  - <https://github.com/kazuho/picojson/commits>
  - <https://github.com/kazuho/picojson/commit/11ac591>
- **Sources the enricher read:**
  - <https://github.com/kazuho/picojson>
  - <https://github.com/kazuho/picojson/commits>
  - <https://github.com/kazuho/picojson/issues>
  - <https://github.com/kazuho/picojson/issues?q=is%3Aissue+depth+OR+stack+OR+overflow+OR+crash>
  - <https://github.com/kazuho/picojson/issues/94>
  - <https://github.com/kazuho/picojson/issues/162>
  - <https://github.com/kazuho/picojson/issues/90>
  - <https://github.com/kazuho/picojson/issues/141>
  - <https://github.com/kazuho/picojson/pulls?q=is%3Apr+depth+OR+nest+OR+overflow+OR+performance+OR+speed>
  - <https://github.com/kazuho/picojson/pull/135/files>
  - <https://raw.githubusercontent.com/kazuho/picojson/HEAD/README.mkdn>
  - <https://raw.githubusercontent.com/kazuho/picojson/HEAD/picojson.h>
  - <https://raw.githubusercontent.com/kazuho/picojson/HEAD/Changes>
  - <https://raw.githubusercontent.com/kazuho/picojson/HEAD/Makefile>
  - <https://raw.githubusercontent.com/kazuho/picojson/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kazuho/picojson/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/conformance.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/build/premake5.lua>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/test.h>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/picojsontest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/nlohmanntest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/jsoncpptest.cpp>
  - https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/roundtrip/roundtrip13.json (through roundtrip27.json)
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/jsonchecker/fail07.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/jsonchecker/fail08.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/jsonchecker/fail10.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/jsonchecker/fail13.json>
  - <https://raw.githubusercontent.com/nlohmann/json/v2.0.3/src/json.hpp>
  - <https://raw.githubusercontent.com/dacez/zzzjson/HEAD/README.md>
  - <https://raw.githubusercontent.com/ibireme/yyjson_benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/ibireme/yyjson_benchmark/HEAD/CMakeLists.txt>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/kazuho/picojson`) · [data/wave4/enrich/raw/github_com_kazuho_picojson.json](../../../data/wave4/enrich/raw/github_com_kazuho_picojson.json) (enrichment confidence 0.8)

</details>
