# taoJSON

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++17 JSON/CBOR/MsgPack/UBJSON value-and-events library; beat nlohmann 2.0.3 in a 2016 run, mainly on number-heavy JSON.

| | |
|---|---|
| **Beats** | nlohmann/json (Nlohmann v2.0.3 row in nativejson-benchmark) |
| **Claimed result** | Parse time summed over the three files: taocpp/json 41.230 ms vs Nlohmann 72.476 ms, about 1.8x faster (derived from page data; canada 25.621 vs 55.591 ms, citm_catalog 10.266 vs 9.875 ms i.e. slightly slower there, twitter 5.343 vs 7.010 ms). Stringify summed: 30.997 ms vs 87.732 ms, about 2.8x faster (derived from page data; canada 21.560 vs 76.315, citm 6.078 vs 7.178, twitter 3.359 vs 4.239). In the same CSV RapidJSON parses the three files in 7.932 ms, so taocpp/json is about 5.2x slower than RapidJSON (derived from page data). Versions: taocpp/json submodule commit d380c63 (2016) vs Nlohmann v2.0.3; the suite README's version table lists taocpp/json 1.0.0-beta.7, but that tag postdates the CSV by eight months. taoJSON's own README makes no speed claim; it says only 'Achieves a 100% conformance score in the Native JSON Benchmark tests'. |
| **Workload** | Parse in-memory JSON into a DOM and stringify the DOM, summed over canada.json, citm_catalog.json and twitter.json, in the nativejson-benchmark sample run of 2016-09-09 (commit a4a9f10). At that commit the thirdparty submodules point to taocpp/json d380c63 (a 2016 development commit, before the 1.0.0-beta.7 tag of 2017-05-19) and nlohmann/json c8d01fa (merge of release/2.0.3). |
| **Metric** | throughput |
| **Hardware** | MacBook Pro (Retina, 15-inch, Mid 2015), Core i7-4980HQ @ 2.80GHz |
| **Compiler and flags** | clang 7.0 64-bit on macOS (suite README); build/premake5.lua release configuration: optimize 'Full' with '-march=native -Wall -Wextra' (read from the build file). |
| **Adoption** | 680 stars |
| **Last commit** | 2026-09-20 |
| **Links** | [repository](https://github.com/taocpp/json) · [benchmark](https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv) |

## Verdict

In nativejson-benchmark's 2016-09-09 sample run (clang 7.0 64-bit, premake 'Full' optimisation with -march=native, Core i7-4980HQ, macOS), the 2016 taoJSON development commit d380c63 parsed canada.json, citm_catalog.json and twitter.json into a DOM in 41.2 ms total vs 72.5 ms for nlohmann 2.0.3 (1.8x) and stringified them in 31.0 vs 87.7 ms (2.8x). Per file, the parse win is 2.2x on canada.json, 1.3x on twitter.json and 0.96x (slower) on citm_catalog.json; excluding canada.json, the totals are 1.08x for parse and 1.21x for stringify (derived from page data).

## Use it when

- You want one value model and one events pipeline across JSON, JAXN, CBOR, MsgPack and UBJSON, with transformers, JSON Pointer and JSON Patch in a header-only C++17 library
- Correctness matters more than throughput: it has a 100% Native JSON Benchmark conformance score, correctly rounded double parsing and shortest round-trip double printing
- Your documents are number-heavy (coordinates, telemetry), which is the only workload where a measured win over nlohmann exists: 2.2x parse and 3.5x stringify on canada.json against nlohmann 2.0.3 in 2016
- You want to bind JSON directly to C++ structs through binding traits or the parts parser instead of walking a DOM
- Your project already uses PEGTL and you want consistent error messages with source positions

## Skip it when

- Raw parse or serialise speed is the goal: in the same 2016 suite it parsed 5.2x slower than RapidJSON, and in a 2019 Boost.JSON table (no harness published) it was about 9-13x slower than RapidJSON. simdjson, yyjson or glaze are the speed picks
- Your documents are string-heavy: it was slightly slower than nlohmann 2.0.3 on citm_catalog parse (10.27 vs 9.88 ms), and it was 4-5x slower than nlohmann in the 2019 Boost.JSON table
- Input is untrusted and may be deeply nested: no nesting-depth limit is visible in the grammar or parse entry points, and issue #121 reported a stack overflow on a malformed file
- Your inputs contain duplicate keys or you must preserve key order: objects are a sorted std::map, and DOM parsing throws on a duplicate key
- Memory or binary size is tight: in 2016 its parse peak memory was 1.6-1.9x nlohmann's and its test binary was 105,256 vs 42,132 bytes (derived from page data). It is also still pre-1.0 (1.0.0-beta.11), and the README says parts of the API may change

## How it is fast

The JSON grammar is a PEGTL parsing-expression grammar compiled through templates into a recursive-descent parser that sends events directly to a consumer, with no separate tokenizer. Integers of 20 digits or fewer take a strtoull fast path; other numbers go through the bundled V8 double-conversion Strtod for correctly rounded doubles. Output writes integers with jeaiii itoa and doubles with Ryu shortest round-trip printing. The design notes say it 'strives for speed through minimalism (rather than complicated optimisations)': it has no SIMD, no arena allocator, and strings are UTF-8-validated one code point at a time. That explains why it beat an old nlohmann on numbers but trails RapidJSON by about 5x.

## Compared with alternatives

Pick it over jsoncons or nlohmann when you specifically want its events and transformer architecture, JAXN support and strict conformance; jsoncons covers the same binary formats and has measured 2.1x read and 3.9x write wins over nlohmann. For speed, pick glaze, yyjson or simdjson; taoJSON was never close to RapidJSON.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | PEGTL 3.x (CMake asks for 3.1.0 or later and falls back to the external/PEGTL git submodule); the double-conversion, Ryu and jeaiii itoa code is bundled in include/tao/json/external |
| **Minimum toolchain** | C++17 (CMake 3.10+ for the bundled build; Conan package taocpp-json) |
| **Platforms** | Windows, macOS, Linux and Android in CI; commits add loongarch64 (2024) and riscv64 (2026) support; non-Windows builds need the compiler to define __BYTE_ORDER__ |
| **Thread safety** | not documented (the value is a plain std::variant over STL containers, and no locking appears in basic_value.hpp) |
| **Drop-in for the baseline** | no |

## Gotchas

- Parsing into a value throws std::runtime_error on a duplicate object key (set_value::member calls try_emplace, then throw_duplicate_key_exception). Objects are std::map&lt;std::string, value, std::less&lt;&gt;&gt;, so serialising emits keys in sorted order rather than input order.
- The JSON grammar recurses (value, array, element, value) under PEGTL's default control and has no nesting-depth guard in grammar.hpp, action.hpp, errors.hpp or from_input.hpp. Issue #121 (2022, stack overflow from from_file on a malformed file) is closed with no visible fix comment, so guard untrusted input yourself.
- The record's Boost.JSON caveat is wrong. At boostorg/json commit 8102e7b, doc/qbk/benchmarks.qbk (added in e73d488, 2019-10-23) lists tao-json and nlohmann in the same table on the same inputs: 2056-2178 ms vs 491-495 ms for 55,952,763 bytes and 22952-23265 ms vs 4195-4320 ms for 488,889,121 bytes. That makes tao-json about 4.2-5.5x slower than nlohmann (derived from page data). No tao-json harness exists in any of the ten bench/bench.cpp versions checked, and no hardware or compiler is stated, so this is unreproducible directional evidence. It still contradicts the 2016 win.
- nativejson-benchmark's harness (src/tests/taocpptest.cpp on master) calls tao::json::sax::from_string, sax::from_value and sax::to_stream, which no longer exist (the current tree uses tao::json::events). The 2016 numbers cannot be re-run against today's taoJSON without porting the harness. That suite also reports best-of-10 timings with DOM destruction excluded.

## Known shortcomings

- No claim from the project itself: the 2016 nativejson-benchmark run (submodule commit d380c63, before 1.0.0-beta.7) shows 1.8x parse over nlohmann v2.0.3 but slower than nlohmann on citm_catalog parse and 5.2x slower than RapidJSON; a later chart suggests the margin shrank or reversed.
- Enricher: the 2016 nativejson-benchmark win is mostly canada.json (citm 0.96x; without canada, parse 1.08x and stringify 1.21x over nlohmann), and Boost.JSON's doc/qbk/benchmarks.qbk (e73d488, 2019-10-23) has tao-json and nlohmann in the same table at 2056-2178 vs 491-495 ms and 22952-23265 vs 4195-4320 ms, so tao-json is about 4.2-5.5x slower than nlohmann there (no harness, hardware or compiler published). The nativejson harness uses the removed tao::json::sax API, so no rerun on current code; no nesting-depth limit (issue #121 stack overflow); DOM parse throws on duplicate keys; sorted std::map; peak memory 1.6-1.9x nlohmann; still pre-1.0 (beta.11).

## Caveats and trade-offs

Weak and stale. The project makes no performance claim; the evidence is a 2016-09-09 third-party shootout run by RapidJSON's author (taocpp/json at a 2016 development commit d380c63, not the 1.0.0-beta.7 the suite README's later version table names, vs Nlohmann v2.0.3), so both libraries have changed a great deal since. taocpp/json is slightly slower than Nlohmann on citm_catalog parse; the summed win comes mostly from canada.json (number-heavy). A later rerun of the same suite shown in the Sonic-Cpp README (2022 chart, hardware and versions unstated; values read off the bars, approximate) has taocpp/json parse about 5.6 ms vs Nlohmann about 6.2 ms (about 1.1x) and stringify about 2.65 vs 4.6 ms (about 1.7x), so the margin may have shrunk. Boost.JSON commit 7e72366 ('shrink sizeof(array)', doc/qbk/benchmarks.qbk) removed aggregate tao-json lines ('parse 55952763 bytes in 2178ms', 'parse 488889121 bytes in 22952ms') and added per-file nlohmann lines (1297 to 13899 ms); the two never appear in the same file version and measure different inputs, so they give no taoJSON-vs-nlohmann comparison. taocpp/json is slower than RapidJSON in every suite found. The repo has src/perf/json benchmark programs but no published comparison numbers. [retier] No performance claim from the project itself; the only A-grade numbers are the 2016 nativejson-benchmark run (taocpp/json submodule d380c63, before 1.0.0-beta.7; clang 7.0, i7-4980HQ) where the 1.8x parse over nlohmann v2.0.3 is mostly canada.json (citm_catalog 0.96x; without canada, parse 1.08x and stringify 1.21x) and tao-json is 5.2x slower than RapidJSON. Boost.JSON's doc/qbk/benchmarks.qbk (e73d488, 2019-10-23) lists tao-json and nlohmann in one table on the same inputs at 2056-2178 vs 491-495 ms and 22952-23265 vs 4195-4320 ms, so tao-json is about 4.2-5.5x slower than nlohmann there, with no harness, hardware or compiler published. The nativejson harness uses the removed tao::json::sax API, so the result cannot be re-run on current code. No nesting-depth limit (issue #121 stack overflow), DOM parse throws on duplicate keys, sorted std::map objects, peak memory 1.6-1.9x nlohmann, still pre-1.0 (beta.11).

Header-only, C++17, built on the PEGTL parsing expression grammar library; generic Value class with type traits and an events interface that converts to and from JSON, JAXN, CBOR, MsgPack and UBJSON; MIT with bundled V8 double-conversion and Ryu portions under their own licences (BSD-3 style and Apache-2.0 or BSL-1.0). Designed for flexibility and conformance rather than raw speed.

## Maintenance

Maintained but slow-moving: the last commit, a riscv64 port merged on 2026-09-20, follows mostly CI and build fixes since 2023. It is still pre-1.0 (1.0.0-beta.11), MIT-licensed, header-only and easy to vendor with PEGTL. The only reproducible speed evidence is the 2016 run against nlohmann 2.0.3, and an independent but unreproducible 2019 Boost.JSON table shows it 4-5x slower than nlohmann, so treat it as a conformance and flexibility choice, not a speed one.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Independent nativejson-benchmark sample CSV (miloyip, committed 2016-09-09 in a4a9f10) has taocpp/json and Nlohmann rows; harness code is public (src/tests/taocpptest.cpp, src/tests/nlohmanntest.cpp), flags are in build/premake5.lua (release optimize 'Full', -march=native), compiler (clang 7.0 64-bit, macOS) and CPU (Core i7-4980HQ) are stated in the suite README. All summed figures in the record re-derive exactly from the CSV.
- **Verifier notes:** Numbers verified exactly against the CSV; tier A holds on the suite's public harness, premake flags, compiler and CPU. Corrected the version attribution (CSV run used taocpp/json d380c63 from 2016; 1.0.0-beta.7 was tagged 2017-05-19) and the Boost.JSON caveat (tao and nlohmann numbers there were never in the same run). Shortcomings: no first-party claim, 2016 data, slower than Nlohmann on citm_catalog parse, 5.2x slower than RapidJSON.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** nativejson-benchmark CSV (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/build/premake5.lua>
  - <https://github.com/miloyip/nativejson-benchmark/tree/master/src/tests>
  - <https://github.com/miloyip/nativejson-benchmark/commits/master/sample/performance_Corei7-4980HQ@2.80GHz_mac64_clang7.0.csv>
  - <https://github.com/miloyip/nativejson-benchmark/tree/a4a9f10/thirdparty>
  - <https://github.com/taocpp/json/commit/d380c63be15b0c14344d48ed4b13132dd41c3c6e>
  - <https://github.com/nlohmann/json/commit/c8d01fa7b90bda4dbd8c317d640bb008bff4d180>
  - <https://github.com/taocpp/json>
  - <https://github.com/taocpp/json/commits>
  - <https://github.com/taocpp/json/tags?after=1.0.0-beta.9>
  - <https://github.com/boostorg/json/commit/7e72366>
- **Sources the enricher read:**
  - <https://github.com/taocpp/json>
  - <https://github.com/taocpp/json/commits/main>
  - <https://github.com/taocpp/json/tree/main/include/tao/json>
  - <https://github.com/taocpp/json/tree/main/include/tao/json/external>
  - <https://github.com/taocpp/json/tree/main/include/tao/json/internal>
  - <https://github.com/taocpp/json/tree/main/src/perf/json>
  - <https://github.com/taocpp/json/issues>
  - <https://github.com/taocpp/json/issues?q=is%3Aissue+performance+OR+slow+OR+speed+OR+benchmark>
  - <https://github.com/taocpp/json/issues?q=is%3Aissue+stack+OR+crash+OR+overflow+OR+depth+OR+nesting+OR+fuzz>
  - <https://github.com/taocpp/json/issues/148>
  - <https://github.com/taocpp/json/issues/118>
  - <https://github.com/taocpp/json/issues/121>
  - <https://github.com/taocpp/json/issues/97>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/README.md>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/doc/README.md>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/doc/Design-Decisions.md>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/doc/Changelog.md>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/doc/Overview.md>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/doc/Interoperability.md>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/doc/Value-Class.md>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/doc/Parser-Interface.md>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/doc/Instance-Sharing.md>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/internal/grammar.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/internal/number_state.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/internal/action.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/internal/escape.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/internal/errors.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/internal/endian.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/internal/endian_gcc.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/basic_value.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/forward.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/from_string.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/to_string.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/events/from_string.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/events/from_file.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/events/from_input.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/events/to_stream.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/events/to_value.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/events/set_value.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/include/tao/json/external/double.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/src/perf/json/bench_mark.hpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/src/perf/json/benchmark.cpp>
  - <https://raw.githubusercontent.com/taocpp/json/HEAD/src/perf/json/parse_file.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/sample/performance_Corei7-4980HQ%402.80GHz_mac64_clang7.0.csv>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/README.md>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/src/main.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/src/tests/taocpptest.cpp>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/src/tests/nlohmanntest.cpp>
  - <https://github.com/boostorg/json/commit/7e72366>
  - <https://raw.githubusercontent.com/boostorg/json/8102e7b325f4bb331c6b309e440da971483aff7c/doc/qbk/benchmarks.qbk>
  - <https://github.com/boostorg/json/commits/8102e7b325f4bb331c6b309e440da971483aff7c/doc/qbk/benchmarks.qbk>
  - <https://github.com/boostorg/json/tree/8102e7b325f4bb331c6b309e440da971483aff7c/bench>
  - <https://raw.githubusercontent.com/boostorg/json/8102e7b325f4bb331c6b309e440da971483aff7c/bench/bench.cpp>
  - <https://raw.githubusercontent.com/boostorg/json/e73d4886ea69a9f7e2b7281d415e50f66af5fba4/bench/bench.cpp>
  - <https://github.com/boostorg/json/commits/e73d4886ea69a9f7e2b7281d415e50f66af5fba4/bench/bench.cpp>
  - <https://raw.githubusercontent.com/boostorg/json/0273148f693470d916d948f3e69571ce9aa6f93c/doc/qbk/benchmarks.qbk>
  - <https://raw.githubusercontent.com/Loki-Astari/json_performance/HEAD/README.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/taocpp/json`) · [data/wave4/enrich/raw/github_com_taocpp_json.json](../../../data/wave4/enrich/raw/github_com_taocpp_json.json) (enrichment confidence 0.75)

</details>
