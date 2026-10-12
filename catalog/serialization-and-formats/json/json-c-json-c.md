# json-c

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Long-standing reference-counted C JSON DOM; in a 2016 independent run it stringified a parsed canada.json 4x faster than Jansson, losing elsewhere.

| | |
|---|---|
| **Beats** | Jansson v2.7 (same suite also: nlohmann/json v2.0.3, JsonCpp 1.0.0, cJSON 1.5.0) |
| **Claimed result** | Stringify time, sum of the three files (derived from page data): json-c 30.804 ms (16.260 + 9.990 + 4.554) vs Jansson 69.910 ms (about 2.3x), cJSON 71.283 ms (about 2.3x), Nlohmann 87.732 ms (about 2.8x) and JsonCpp 94.261 ms (about 3.1x); prettify sum 49.256 ms vs Jansson 80.380 ms (about 1.6x) and Nlohmann 130.560 ms (about 2.7x). The whole win comes from canada.json (stringify 16.260 ms vs Jansson 64.221, cJSON 49.510, Nlohmann 76.315, JsonCpp 84.443; prettify 29.737 vs Jansson 73.837, Nlohmann 112.750). On citm_catalog.json and twitter.json json-c is slower than Jansson (stringify 9.990/4.554 ms vs 3.764/1.925 ms; prettify 14.057/5.462 vs 4.373/2.170), Nlohmann (stringify 7.178/4.239) and JsonCpp (stringify 5.679/4.139), and beats only cJSON (15.016/6.757). All ratios derived from page data. |
| **Workload** | nativejson-benchmark: serialize the parsed DOM of canada.json (2199KB), citm_catalog.json (1737KB) and twitter.json (632KB) with json_object_to_json_string_ext (plain and pretty modes), json-c 0.12.1. |
| **Metric** | throughput |
| **Hardware** | MacBook Pro (Retina, 15-inch, Mid 2015), Core i7-4980HQ @ 2.80GHz |
| **Compiler and flags** | clang 7.0, 64-bit macOS. Flags are not recorded in the results file; the public build/premake5.lua sets the release configuration to optimize Full with NDEBUG, and gmake builds add -march=native -Wall -Wextra |
| **Adoption** | 3.3k stars |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/json-c/json-c) · [benchmark](https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv) |

## Verdict

In nativejson-benchmark's 2016 sample (clang 7.0, release build with NDEBUG and -march=native, Core i7-4980HQ, macOS), json-c 0.12.1 stringified the parsed canada, citm_catalog and twitter DOMs in 30.8 ms total against Jansson 2.7's 69.9 ms, nlohmann/json 2.0.3's 87.7 ms and JsonCpp 1.0.0's 94.3 ms, but the whole margin is canada.json, where it copies each double's cached input text instead of formatting it; it is slower than Jansson, nlohmann and JsonCpp on the other two files. The project makes no speed claim.

## Use it when

- Parse-then-re-emit pipelines over number-heavy documents (GeoJSON coordinates, telemetry arrays) where doubles are passed through unchanged: the cached original text is written back byte-for-byte, which is both the source of the canada.json win (16.3 ms vs Jansson 64.2 ms) and exact numeric round-tripping (27 of 27 roundtrip conformance tests).
- C programs that receive JSON in pieces (sockets, pipes) and want an incremental tokener that resumes across buffers without assembling the full document first.
- Projects that want a widely packaged, ABI-versioned system library (symbol versions since 0.15) with JSON Pointer and JSON Patch support rather than a vendored single file.
- Building and editing small-to-medium JSON trees in C where parse throughput is not the bottleneck.

## Skip it when

- Parse-bound workloads: in the same 2016 run json-c 0.12.1 parsed the three files in 134.6 ms against cJSON 24.7 ms, udp/json-parser 47.3 ms, nlohmann/json 72.5 ms and RapidJSON 7.9 ms (sums derived from page data).
- Serializing string- and object-heavy documents: on citm_catalog.json and twitter.json json-c stringified 2.4-2.7x slower than Jansson (9.99/4.55 ms vs 3.76/1.93 ms) and also behind nlohmann/json and JsonCpp.
- Memory-constrained parsing: the 2016 run recorded 33.7 MB and 390,651 allocations to parse the 2.2 MB canada.json (nlohmann 5.3 MB); 0.15 cut object and array overhead, but each object still allocates its own hash table and each double keeps a strdup of its text.
- Validating untrusted input with the default entry point: json_tokener_parse is lenient and accepted 12 of the suite's invalid documents (trailing commas, single quotes, a leading zero, raw tab and newline in strings, text after the closing bracket, incomplete exponents such as [0e]); pass JSON_TOKENER_STRICT through json_tokener_set_flags for RFC behaviour.
- Multi-threaded parsing on NetBSD, Solaris 11.3 or older and native Windows: open issue #855 reports that json_tokener_parse's locale switching disturbs other threads' strtod/sprintf.

## How it is fast

It is not a speed-oriented design: every value is its own malloc, every object carries its own linkhash table, and numbers go through strtod. The measured stringify win comes from a parse-time cache: the tokener stores a strdup of each double's original text (json_object_new_double_s, still in json_tokener.c at HEAD) and installs a serializer that memcpy's that text back, so re-emitting a parsed, number-heavy document skips double-to-text conversion; doubles created in code still go through snprintf("%.17g"). Output goes into one growing printbuf per call.

## Compared with alternatives

Pick json-c over Jansson or cJSON when you need an incremental tokener, JSON Pointer/Patch, or exact pass-through of parsed number text, or when it is already the system library; pick cJSON (about 5x faster parse in the same run), Jansson (faster stringify of string-heavy documents) or yyjson when throughput is the goal.

## Integration

| | |
|---|---|
| **Form** | shared lib and static lib (CMake by default, meson build added in 0.19) |
| **Dependencies** | none (libc; libm when needed) |
| **Minimum toolchain** | Plain C compiler (gcc, clang, MSVC, clang-cl; C89 build fixed in 0.19); CMakeLists.txt requires CMake 3.9+, README recommends 3.16+ |
| **Platforms** | any: Linux and other Unix, macOS, AIX, Windows (MSVC, MinGW, vcpkg), Android, Amiga/MorphOS |
| **Thread safety** | Partial. Separate trees in separate threads are fine; reference counting is atomic only when built with -DENABLE_THREADING=ON (off by default); json_object_to_json_string_ext writes into a buffer stored on the object, so concurrent stringify of one object needs external locking (the header says to strdup the result); each parse call switches the numeric locale with uselocale/newlocale, and issue #855 (open) reports cross-thread interference on platforms that fall back to setlocale. |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark detail behind the numbers: nativejson-benchmark reports the minimum of 10 stringify trials on the same DOM, and json-c's json_object_to_json_string_ext keeps its output printbuf on the root object and only resets it, so trials 2-10 write into an already grown 7 MB buffer while the recorded memory and allocation counts (21 allocations) come from trial 0 only; libraries that build a fresh output buffer each call pay growth and page faults on every trial. This is a small edge compared with the number-text cache, which is the main reason for the canada.json result.
- The speed of serializing numbers depends on where they came from: a parsed double re-emits its original text (so 1.0E+2 stays 1.0E+2), while json_object_new_double or json_object_set_double values are printed with %.17g (for example 0.1 becomes 0.10000000000000001); json_c_set_serialization_double_format changes the format globally or per thread.
- Default serialization escapes every '/' as '\/' unless JSON_C_TO_STRING_NOSLASHESCAPE (0.13+) is passed, so output is larger than other libraries' on URL-heavy data such as twitter.json.
- The measured release is 0.12.1 (2016). Later releases changed the cost profile with no comparable public numbers: 0.13 removed variadic printf from serialization and stored small strings inline, 0.15 split json_object into per-type structs (project bench: 5.8% faster, 6-12% less memory) and shrinks parsed arrays (9% faster, 39-50% less peak memory), 0.16 replaced ctype calls in the tokener and serializer. Avoid 0.17 (ABI break, flagged in the ChangeLog).

## Known shortcomings

- nativejson-benchmark 2016 run: the stringify/prettify win holds only on canada.json and comes from double text cached at parse time (json_object_new_double_s); loses to Jansson, nlohmann and JsonCpp on citm and twitter, and parsing is slow and memory-heavy. The suite README version table was edited after the 2016-09-09 run (lists cJSON 1.5.0, released 2017-05-02), so measured versions are uncertain.
- Enricher: nativejson-benchmark reports the minimum of 10 stringify trials on the same DOM and json-c keeps its output printbuf on the root object (jso-&gt;_pb, reset only), so trials 2-10 reuse an already-grown 7 MB buffer (allocation stats come from trial 0 only); the canada.json stringify win rests on the parse-time double-text cache (json_object_new_double_s strdup, still at HEAD). The default json_tokener_parse is lenient (accepted 12 invalid JSON_checker documents); issue #855 (locale switching not thread-safe on NetBSD/Solaris/Windows) is open; 0.15 cut memory 39-50%, so the 2016 data is stale.

## Caveats and trade-offs

The stringify win is confined to canada.json and comes from a parse-time cache: json-c's tokener stores a strdup of every double's original text (json_object_new_double_s, 0.12.1 json_tokener.c line 703, still present at HEAD) and the serializer memcpy's that text back instead of formatting the double, so a DOM built from parsing skips double-to-text conversion while doubles created in code go through snprintf("%.17g"). The cost moves to parsing: json-c's canada.json parse is 105.784 ms with 33.7 MB and 390,651 allocations (Nlohmann 55.591 ms, 5.3 MB). On citm_catalog.json and twitter.json json-c stringifies 2.4-2.7x slower than Jansson and slower than Nlohmann and JsonCpp. Parse time (134.551 ms for the three files) is slower than most libraries in the suite and beats only JsonCpp (165.522 ms), PicoJSON (140.256 ms) and a few others; RapidJSON stringifies the three files in 11.209 ms. Third-party suite by the RapidJSON author (disclosed), numbers from 2016 with json-c 0.12.1, many releases behind the current 0.19. Library versions come from the suite README's table, which was edited after the 2016-09-09 sample run (it lists cJSON 1.5.0, released 2017-05-02), so the exact versions measured are not certain. Conformance in the same suite: 22 of 34 parse-validation, 57 of 66 double-parse, 9 of 9 string and 27 of 27 roundtrip tests. json-c's README makes no benchmark claim. Flags come from the repo's premake file, not from the result file. Output formatting differs between libraries, so serialized bytes are not identical across rows.

Serialization is fast but parsing and memory are not: parse of the three files takes 134.551 ms vs Nlohmann 72.476 ms and udp/json-parser 47.338 ms (sums derived from page data), and the parsed DOM uses 49,886,288 bytes vs 9,897,872 for Nlohmann. Reference-counted object model with C API; the README makes no speed claim and says only that it aims at RFC conformance.

## Maintenance

Actively maintained (0.19 released 2026-06-27, merges through 2026-10-04), MIT, packaged by most Linux distributions; usable and copyable, but the speed entry rests on a 2016 run of 0.12.1 and on a parse-time cache that shifts cost from stringify to parse.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification A, tier now A.
- **Tier reason:** The independent nativejson-benchmark sample CSV has json-c, Jansson, cJSON, Nlohmann and JsonCpp Stringify/Prettify rows on a Core i7-4980HQ with clang 7.0 64-bit; the harness is public (src/tests/jsonctest.cpp calls json_object_to_json_string_ext with JSON_C_TO_STRING_PLAIN/PRETTY, src/tests/janssontest.cpp etc.) and build/premake5.lua sets release optimize Full, NDEBUG and -march=native, so A holds as for the Jansson and ujson4c entries.
- **Verifier notes:** Every number matches the CSV, but the summed stringify/prettify win hides that json-c loses to Jansson, Nlohmann and JsonCpp on two of three files; the canada.json win comes from re-emitting each double's original text cached at parse time (json_object_new_double_s). Shortcomings to record: win confined to canada.json via parse-time number-text cache, slow and memory-heavy parse, 2016 data on 0.12.1, README version table postdates the run.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** nativejson-benchmark CSV (verifier downgrade, claim narrowed); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/build/premake5.lua>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/conformance.csv>
  - <https://github.com/miloyip/nativejson-benchmark/tree/master/src/tests>
  - <https://github.com/miloyip/nativejson-benchmark/tree/master/sample>
  - <https://github.com/miloyip/nativejson-benchmark/tree/master/thirdparty>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/jsonctest.cpp>
  - <https://raw.githubusercontent.com/json-c/json-c/json-c-0.12.1-20160607/json_tokener.c>
  - <https://raw.githubusercontent.com/json-c/json-c/json-c-0.12.1-20160607/json_object.c>
  - <https://raw.githubusercontent.com/json-c/json-c/HEAD/json_tokener.c>
  - <https://raw.githubusercontent.com/json-c/json-c/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/DaveGamble/cJSON/HEAD/CHANGELOG.md>
  - <https://github.com/json-c/json-c>
  - <https://github.com/json-c/json-c/commits/master.atom>
- **Sources the enricher read:**
  - <https://github.com/json-c/json-c>
  - <https://github.com/json-c/json-c/commits/master>
  - <https://raw.githubusercontent.com/json-c/json-c/HEAD/README.md>
  - <https://raw.githubusercontent.com/json-c/json-c/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/json-c/json-c/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/json-c/json-c/HEAD/json_tokener.c>
  - <https://raw.githubusercontent.com/json-c/json-c/HEAD/json_tokener.h>
  - <https://raw.githubusercontent.com/json-c/json-c/HEAD/json_object.c>
  - <https://raw.githubusercontent.com/json-c/json-c/HEAD/json_object.h>
  - <https://raw.githubusercontent.com/json-c/json-c/HEAD/json_object_private.h>
  - <https://raw.githubusercontent.com/json-c/json-c/HEAD/printbuf.c>
  - <https://raw.githubusercontent.com/json-c/json-c/HEAD/linkhash.c>
  - <https://raw.githubusercontent.com/json-c/json-c/HEAD/json_util.c>
  - <https://raw.githubusercontent.com/json-c/json-c/HEAD/issues_closed_for_0.13.md>
  - <https://github.com/json-c/json-c/tree/master/bench>
  - <https://raw.githubusercontent.com/json-c/json-c/HEAD/bench/README.bench.md>
  - <https://raw.githubusercontent.com/json-c/json-c/json-c-0.12.1-20160607/json_tokener.c>
  - <https://raw.githubusercontent.com/json-c/json-c/json-c-0.12.1-20160607/json_object.c>
  - <https://raw.githubusercontent.com/json-c/json-c/json-c-0.12.1-20160607/printbuf.c>
  - <https://github.com/json-c/json-c/issues?q=is%3Aissue+performance+OR+slow+OR+speed>
  - <https://github.com/json-c/json-c/issues/855>
  - <https://github.com/json-c/json-c/issues/552>
  - <https://github.com/json-c/json-c/issues/947>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/sample/conformance.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/tests/jsonctest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/src/main.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/HEAD/build/premake5.lua>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/json-c/json-c`) · [data/wave4/enrich/raw/github_com_json_c_json_c.json](../../../data/wave4/enrich/raw/github_com_json_c_json_c.json) (enrichment confidence 0.75)

</details>
