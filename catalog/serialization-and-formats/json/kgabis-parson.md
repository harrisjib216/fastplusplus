# Parson

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Two-file C89 JSON DOM with dot-path access; parsed 1.85x faster than JsonCpp 1.0.0 in a 2016 run, mostly on number-heavy canada.json.

| | |
|---|---|
| **Beats** | JsonCpp (also json-c) |
| **Claimed result** | Parse, sum of the three files (derived from page data): Parson 89.549 ms vs JsonCpp 1.0.0 165.522 ms (about 1.85x), json-c 0.12.1 134.551 ms (about 1.50x) and Qt 5.6 QJsonDocument 124.957 ms (about 1.40x). The win is driven by canada.json (64.573 ms vs JsonCpp 142.458, json-c 105.784, Qt 114.775); on citm_catalog.json Parson (17.144 ms) is slower than JsonCpp (14.587) and Qt (7.052) and faster than json-c (21.122); on twitter.json (7.832 ms) it is faster than JsonCpp (8.477) and slower than json-c (7.645) and Qt (3.130). Parse memory 9.14 MB vs JsonCpp 24.56 MB and json-c 49.89 MB (derived; Qt allocations are not tracked), though Parson makes more allocations (594,122 vs JsonCpp 386,181). Stringify 110.903 ms is slower than nlohmann/json v2.0.3 (87.732), JsonCpp (94.261) and json-c (30.804) and faster only than Qt (152.185, about 1.37x, derived). There is no valid prettify comparison: the suite's Parson Prettify calls json_serialize_to_string (compact), so its 111.205 ms is not comparable with nlohmann's dump(4) 130.560 ms. Parse is slower than nlohmann/json (72.476 ms), cJSON (24.671) and RapidJSON (7.932). |
| **Workload** | nativejson-benchmark parse of canada.json, citm_catalog.json and twitter.json into each library's DOM, Parson against JsonCpp, json-c and Qt QJsonDocument (and nlohmann/json v2.0.3 as the faster reference). |
| **Metric** | throughput |
| **Hardware** | MacBook Pro (Retina, 15-inch, Mid 2015), Intel Core i7-4980HQ @ 2.80GHz, macOS 64-bit (suite README and result file name) |
| **Compiler and flags** | Apple clang 7.0 64-bit on macOS (suite README: 'MacBook Pro (Retina, 15-inch, Mid 2015, Corei7-4980HQ@2.80GHz) with clang 7.0 64-bit', results updated 2016-9-9); premake5 gmake build, release configuration: optimize "Full" (-O3 under gmake), NDEBUG, buildoptions -march=native -Wall -Wextra (build/premake5.lua); Parson revision not stated in the suite README (submodule pinned at c22be79 at HEAD), JsonCpp 1.0.0, json-c 0.12.1, Qt 5.6.1-1, nlohmann v2.0.3 per the suite README table |
| **Adoption** | 1.5k stars |
| **Last commit** | 2026-09-15 |
| **Links** | [repository](https://github.com/kgabis/parson) · [benchmark](https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv) |

## Verdict

In nativejson-benchmark's committed 2016 sample (Apple clang 7.0, optimize Full with -march=native, Core i7-4980HQ, macOS), the 2016 Parson revision c22be79 parsed canada, citm_catalog and twitter in 89.5 ms total against JsonCpp 1.0.0's 165.5 ms (1.85x), json-c 0.12.1's 134.6 ms (1.50x) and Qt 5.6's 125.0 ms (1.40x), a lead that comes from canada.json; it was slower than nlohmann/json 2.0.3, cJSON and RapidJSON, and its stringify was slower than every library but Qt. The project makes no speed claim.

## Use it when

- C or C++ projects that want two files to vendor (parson.c, parson.h), C89 compatibility and an MIT licence for reading configs or API responses in the KB to low-MB range.
- Code that addresses nested fields by path: json_object_dotget_\* and json_object_dotset_\* replace chains of lookups and auto-create intermediate objects.
- Memory-constrained parsing where JsonCpp or json-c are the alternative: the 2016 run used 9.1 MB for the three files against 24.6 MB (JsonCpp) and 49.9 MB (json-c), and json_set_allocation_functions plugs in a custom allocator.
- Config files with comments, through json_parse_string_with_comments / json_parse_file_with_comments.

## Skip it when

- Parse throughput: in the 2016 CSV cJSON parsed the same three files in 24.7 ms, udp/json-parser in 47.3 ms and RapidJSON in 7.9 ms against Parson's 89.5 ms, and Parson lost to JsonCpp and Qt on citm_catalog.json and to json-c and Qt on twitter.json.
- Serialization-heavy work: stringify was slower than JsonCpp, nlohmann/json 2.0.3 and json-c (3.6x) in 2016, and zzzJSON's later table (i7-6700, g++ 7.3 -O3, versions not stated) has Parson at 857 ms stringify across its corpora against 431 ms for JsonCpp and 217 ms for nlohmann.
- Strict validation of untrusted JSON: since 1.4.0 (2022-03-06) it accepts trailing commas in arrays and objects, json_parse_string parses only the first value and ignores trailing text, and object keys are hashed with an unseeded djb2 hash and linear probing, so crafted colliding keys can make large-object parsing quadratic.
- Documents with duplicate keys: json_object_add refuses a key already present, so the whole parse returns NULL instead of keeping the first or last value.
- Non-NUL-terminated buffers or programs that change LC_NUMERIC: there is no length-bounded parse call, and strtod/sprintf follow the C locale, so a comma-decimal locale breaks number parsing and output.

## How it is fast

It is not built for speed: the parser walks the input with a char pointer, calls strtod directly on the buffer for numbers, and mallocs every node separately (each string twice: a worst-case buffer, then a trimmed copy). Its 2016 parse lead over JsonCpp 1.0.0 and json-c 0.12.1 comes almost entirely from canada.json, the number-heavy file (64.6 vs 142.5 and 105.8 ms). Serialization is slow by design: json_serialize_to_string runs a full size-computing pass, then json_serialize_to_buffer runs that pass again before the writing pass, so every number goes through sprintf("%1.17g") three times; that matches its 110.9 ms stringify total against json-c's 30.8 ms in the same run.

## Compared with alternatives

Pick Parson over cJSON, Jansson or json-c when dot-path access, a two-file C89 drop-in and low parse memory matter more than speed; pick cJSON (3.6x faster parse in the same 2016 run) or udp/json-parser for parse speed, json-c for serialization (3.6x faster stringify), and yyjson when throughput is the goal.

## Integration

| | |
|---|---|
| **Form** | source-drop (parson.c + parson.h); CMake and meson files also build a static or shared library |
| **Dependencies** | none (C standard library and libm) |
| **Minimum toolchain** | C89 compiler (tests build with -std=c89 -pedantic-errors and as C++ with g++); CMake 3.5+ or meson 0.46+ if used |
| **Platforms** | any; a 2023 fix (1.5.3) covers macOS sprintf deprecation and CI runs on GitHub Actions |
| **Thread safety** | Separate values can be parsed and serialized concurrently, but the allocator hooks, slash escaping, float format and number-serializer settings are process globals; the header says json_set_escape_slashes is not thread safe and json_set_allocation_functions must be called once before any other call. |
| **Drop-in for the baseline** | no |

## Gotchas

- The measured revision is not today's code: nativejson-benchmark pins c22be79 (2016), whose parson.c stored objects as arrays with a linear duplicate-key scan and hard limits of 960 keys per object (OBJECT_MAX_CAPACITY), 122,880 elements per array and 19 levels of nesting; objects became hash maps in 1.2.0 (2021-08-05), MAX_NESTING is now 2048, and serialization changed in 2021 and 1.5.0 (2022). Current speed relative to JsonCpp is unmeasured.
- Harness flaws (not in the catalogued parse claim): the suite's Parson Prettify calls json_serialize_to_string, the compact serializer, so that row is void; and its Statistics walk looks every member up by name with json_object_get_value(o, name) instead of json_object_get_value_at(o, i), a linear scan per member against the 2016 object arrays, so Parson's statistics rows (0.997 ms on twitter.json against 0.090 for PicoJSON) measure the harness, not the DOM.
- Slashes are escaped as \/ on output unless json_set_escape_slashes(0) is called, numbers print with %1.17g (1.2345 becomes 1.2344999999999999), and 13 of 27 round-trip and 3 of 34 parse-validation tests failed in the 2016 run (trailing text after the first value was accepted).
- Recent memory-safety fixes: an out-of-bounds read in is_valid_utf8 on truncated multi-byte sequences was fixed on 2026-09-15 (1.5.4), after earlier reports of a stack buffer overflow in parson_sprintf (#221) and an out-of-bounds read on unterminated strings (#222); use 1.5.4 or later for untrusted input.

## Known shortcomings

- nativejson-benchmark 2016 run: the harness Prettify calls the compact json_serialize_to_string, so the 1.17x prettify vs nlohmann is dropped; the parse win over JsonCpp, json-c and Qt comes mostly from canada.json; stringify is slower than nlohmann, JsonCpp and json-c.
- Enricher: the benchmarked revision c22be79 (2016) is different code (linear-scan objects, 960-key cap, 122,880-element array cap, nesting 19); hash maps arrived in 1.2.0 (2021-08-05) and current speed is unmeasured. The Statistics rows look members up by name (linear in 2016), so they are harness artefacts; the serializer at HEAD runs the size pass twice plus a write pass with sprintf %1.17g three times per number. Accepts trailing commas since 1.4.0; duplicate keys fail the whole parse; the unseeded djb2 hash lets crafted keys flood it.

## Caveats and trade-offs

Nobody claims Parson is fast: the README calls it lightweight and has no performance claim. The parse win over JsonCpp, json-c and Qt rests mostly on canada.json; on citm_catalog.json and twitter.json Parson loses to Qt and to one of JsonCpp/json-c. It loses to nlohmann/json, cJSON (24.671 ms parse total) and RapidJSON (7.932 ms), and its stringify is 3.6x slower than json-c (30.804 vs 110.903 ms). The suite's Prettify row for Parson calls the compact serializer, so the prettify 1.17x figure against nlohmann is void. Conformance in the same suite: 3 of 34 parse-validation, 1 of 9 string-parse and 13 of 27 round-trip tests fail. Library revision used in the sample is not stated, and the suite README's version table was edited after the run. Sample results are dated 2016-09-09 and use 2016 library versions; today's ratios will differ. Per-library totals are sums of the three per-file rows (canada.json 2199KB, citm_catalog.json 1737KB, twitter.json 632KB) and are derived from page data.

Two-file, C89-compatible DOM library with dot-notation access and a small memory footprint (about 2.7x less parse memory than JsonCpp in this run). Not a speed library: its own README makes no performance claim.

## Maintenance

Active (1.5.4 on 2026-09-15 with a memory-safety fix), MIT, two files and easy to vendor; the speed entry rests on a 2016 run of a pre-hash-map revision against 2016 baselines, so treat it as a lightweight-API pick rather than a speed pick.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now A.
- **Tier reason:** Independent nativejson-benchmark: public harness (src/tests/parsontest.cpp calls json_parse_string; src/tests/jsoncpptest.cpp, jsonctest.cpp, nlohmanntest.cpp), clang 7.0 64-bit, build/premake5.lua release optimize Full, NDEBUG, -march=native, Core i7-4980HQ, so A holds for the parse claim against JsonCpp and json-c. Verdict is downgrade only because the claim included an invalid prettify comparison.
- **Verifier notes:** All parse, stringify, memory and conformance numbers match the CSVs, but the record's 'prettify 1.17x vs nlohmann' compares Parson's compact serializer (harness bug) with nlohmann's indented dump, so I dropped it; tier A stays for the parse win over JsonCpp/json-c. Shortcomings to record: no project speed claim, parse win confined mostly to canada.json, slower than nlohmann/cJSON/RapidJSON, stringify slowest bar Qt, prettify row void, conformance failures, 2016 data. Metadata confirmed: MIT, 1.5k stars, not a fork, last commit 2026-09-15 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** nativejson-benchmark CSV (verifier, claim narrowed); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/conformance.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/build/premake5.lua>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/nlohmanntest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/parsontest.cpp>
  - <https://github.com/miloyip/nativejson-benchmark/tree/master/thirdparty>
  - <https://github.com/kgabis/parson>
  - <https://github.com/kgabis/parson/commits>
  - <https://github.com/kgabis/parson/commit/c22be79>
- **Sources the enricher read:**
  - <https://github.com/kgabis/parson>
  - <https://github.com/kgabis/parson/commits>
  - <https://github.com/kgabis/parson/commits/master?until=2021-08-10>
  - <https://github.com/kgabis/parson/commit/c22be79>
  - <https://github.com/kgabis/parson/issues?q=is%3Aissue+slow+OR+performance+OR+speed+OR+hash+OR+overflow+OR+CVE+OR+crash>
  - <https://github.com/kgabis/parson/issues/37>
  - <https://github.com/kgabis/parson/issues/230>
  - <https://raw.githubusercontent.com/kgabis/parson/HEAD/README.md>
  - <https://raw.githubusercontent.com/kgabis/parson/HEAD/parson.c>
  - <https://raw.githubusercontent.com/kgabis/parson/HEAD/parson.h>
  - <https://raw.githubusercontent.com/kgabis/parson/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kgabis/parson/HEAD/Makefile>
  - <https://raw.githubusercontent.com/kgabis/parson/HEAD/meson.build>
  - <https://raw.githubusercontent.com/kgabis/parson/HEAD/package.json>
  - <https://raw.githubusercontent.com/kgabis/parson/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kgabis/parson/c22be79/parson.c>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/conformance.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/build/premake5.lua>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/test.h>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/parsontest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/jsoncpptest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/jsonctest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/picojsontest.cpp>
  - https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/roundtrip/roundtrip13.json (through roundtrip27.json)
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/jsonchecker/fail07.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/jsonchecker/fail08.json>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/data/jsonchecker/fail10.json>
  - <https://raw.githubusercontent.com/dacez/zzzjson/HEAD/README.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/kgabis/parson`) · [data/wave4/enrich/raw/github_com_kgabis_parson.json](../../../data/wave4/enrich/raw/github_com_kgabis_parson.json) (enrichment confidence 0.8)

</details>
