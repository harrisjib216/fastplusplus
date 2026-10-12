# JsonFusion

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++23 reflection-based JSON parser that parses, validates and fills your structs in one pass, beating RapidJSON plus hand-written mapping.

| | |
|---|---|
| **Beats** | RapidJSON |
| **Claimed result** | vs RapidJSON + manual mapping (parse+validate+populate): \~same speed on static embedded config (vs hand-written SAX), 40% faster dynamic embedded config, 20% faster telemetry, 65% faster RPC commands, 15% faster log events, 20% faster bus events, 15% faster metrics; about 1.5x faster on twitter.json (1020 vs 1620 microseconds/iter). On canada.json it is \~15% slower than RapidJSON for parse-and-populate and \~80% slower than hand-written RapidJSON SAX for typed streaming; only with selective field-skipping (float parsing skipped) is it \~60% faster than hand-written RapidJSON SAX. |
| **Workload** | Six realistic parse+validate+populate scenarios (embedded config static/dynamic, telemetry samples, RPC commands, log events, bus events, metrics/time-series), 1M iterations each; separately, twitter.json (0.6 MB, 100 status objects) parse+populate+validate benchmark comparing full C++ library workflows. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Max, macOS 26.1 (6-scenario benchmark); arm64 Ubuntu Linux 24.04 machine, CPU model not stated (twitter.json benchmark); canada.json hardware not stated |
| **Compiler and flags** | GCC 14 (6-scenario benchmark), GCC 14.3 (twitter.json benchmark); canada.json compiler not stated. The README states no optimization flags or build type. The repo CMakeLists.txt adds -flto=8 -ffunction-sections -fdata-sections (plus -fno-exceptions -fno-rtti on the synthetic and canada targets) only in the Release config. |
| **Adoption** | 15 stars |
| **Last commit** | 2026-08-06 |
| **Links** | [repository](https://github.com/tucher/JsonFusion) · [benchmark](https://github.com/tucher/JsonFusion/blob/master/README.md) |

## Verdict

These are the author's own README numbers. On an Apple M1 Max (macOS 26.1, GCC 14, 1M iterations), parse+validate+populate into structs ran 15-65% faster than RapidJSON DOM plus hand-written mapping in six small-message scenarios, and tied a hand-written RapidJSON SAX handler on static embedded config. On twitter.json (arm64 Ubuntu 24.04, GCC 14.3, CPU not named) it took 1020 vs 1620 us/iter (\~1.6x) against RapidJSON ParseInsitu plus manual populate. On canada.json it loses (\~15% slower parse+populate) unless floats are skipped. The README gives no compiler flags; the repo's scripts/run_benchmarks.sh builds in CMake Release mode, and each result is a single timed loop with no repeated runs.

## Use it when

- Known-schema config, RPC, telemetry, log or event messages parsed straight into structs, where you would otherwise write RapidJSON DOM plus mapping code. The README reports 15-65% faster on six such small-message scenarios.
- Microcontroller firmware (Cortex-M0+/M7, ESP32) built with -Os -fno-exceptions -fno-rtti and no heap. With std::array or char[N] fields the library allocates nothing, and the README reports 21.8 KB .text on Cortex-M7 for two models parsed and serialized.
- Input that arrives in pieces (UART, socket, file iterator): forward-only iterators work, so you don't have to buffer the whole document first.
- You need range, length and enum validation plus JSON-path error locations (e.g. \$.statuses[3].user.name) in the same pass, or the same model over both JSON and CBOR.
- Counting or filtering large documents where most values can be marked `skip` or consumed by a streaming consumer instead of stored.

## Skip it when

- Peak throughput on JSON already in memory with a fixed schema: the author's own table puts Glaze about 3x ahead on twitter.json (360 vs 1020 us/iter).
- Float-heavy data or data that needs exact float values: canada.json parse-and-populate is \~15% slower than RapidJSON, and the default float backend is only accurate to within 1 ULP and does not round-trip doubles exactly (issue #3 is open).
- You need a DOM, ad-hoc queries or schema-less editing. The README says in capitals that this is not a DOM library.
- Toolchains other than GCC 14+ or Clang 20+ (MSVC is not supported), pre-C++23 codebases, or non-aggregate classes with custom constructors or virtual functions, unless you use GCC 16's C++26 reflection mode.
- Teams that need a mature, widely used dependency: one contributor, 15 stars, and published benchmarks that no one else has reproduced. On 8-bit AVR its code is also larger than cJSON or jsmn.

## How it is fast

It wins by doing less work, not by scanning faster. One pass reads tokens straight into the destination fields: no DOM is allocated, no second traversal copies values out, and the validators are compile-time template options that turn into inline branches. Compile-time reflection (Boost.PFR) generates a parser for each struct type. An object key is read into a stack buffer sized to the longest known key and matched by linear comparison against a constexpr field table, and a std::bitset catches duplicate keys. Fields marked `skip` are syntax-checked without converting their numbers, which is the whole source of the canada.json win. The reader is plain scalar code over generic iterators with no SIMD, and the docs say the default in-house float parser is 2-5x slower than fast_float, which explains the losses on float-heavy data.

## Compared with alternatives

Pick it over Glaze when you need forward-only or byte-by-byte input, no allocations inside the library, small -Os builds (the README reports 21.8 KB vs Glaze's 30.4 KB .text on Cortex-M7) or JSON-path errors; pick Glaze for raw speed, since it is \~3x faster on twitter.json. Against reflect-cpp it is slightly faster on twitter.json (1020 vs 1130 us/iter) and skips reflect-cpp's intermediate yyjson DOM. If you want a DOM or the fastest raw parse, simdjson or yyjson fit better.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none required (Boost.PFR is bundled under include/). Optional: the yyjson library for YyjsonReader, rapidyaml for YAML, and the bundled fast_float/simdjson float headers for JSONFUSION_FP_BACKEND=1. |
| **Minimum toolchain** | C++23 with GCC 14+ or Clang 20+ (MSVC not supported); the optional C++26 reflection mode needs GCC 16+ with -std=c++26 -freflection |
| **Platforms** | any. There is no SIMD or architecture-specific code, and the README reports builds on x64, arm64 (Apple M1, Linux), ARM Cortex-M0+/M7, ESP32 (Xtensa LX6) and AVR ATmega2560 (the last needs avr-gcc 15 plus avr-libstdcpp). |
| **Thread safety** | not documented. Parse and Serialize keep their state in per-call reader and context objects, and the README says the constexpr core has no hidden global state or thread-local caches, but it never states a concurrency guarantee. |
| **Drop-in for the baseline** | false — there is no DOM or SAX-compatible API. You define C++ structs and call Parse(obj, input); it replaces RapidJSON plus your hand-written mapping and validation code, not RapidJSON's Document interface. |

## Gotchas

- Unknown JSON keys are a parse error (EXCESS_FIELD) unless the struct carries `allow_excess_fields`, and duplicate keys are always an error. Absent keys, by contrast, are not an error unless you add required&lt;&gt; or not_required&lt;&gt;, so a missing field is silently left untouched.
- Integer fields reject numbers written with a decimal point or exponent (1.0, 1e3). Number tokens longer than 63 characters fail unless you raise JSONFUSION_NUMBER_BUF_SIZE. Skipping an unmodeled value nested more than 64 levels deep fails with SKIPPING_STACK_OVERFLOW (the MaxSkipNesting template parameter).
- Doubles do not round-trip exactly with the default backend. To fix that, define JSONFUSION_FP_BACKEND=1 (fast_float, which loses constexpr) or parse through YyjsonReader (which adds a DOM allocation and a yyjson dependency).
- Recursive model types fail a static_assert unless JSONFUSION_ALLOW_DYNAMIC_ERROR_STACK is defined. Streaming through true single-pass iterators such as std::istreambuf_iterator was broken by a peek-ahead bug reported in issue #4; the owner says it is fixed, but the issue is still open.

## Known shortcomings

- Loses on canada.json: about 15% slower than RapidJSON for parse-and-populate and about 80% slower than hand-written RapidJSON SAX for typed streaming. The '\~60% faster' result skips float parsing, so it is not equal work. No optimization flags or build type stated; canada.json hardware not stated.
- Default float backend does not round-trip doubles exactly and is 2-5x slower than fast_float (#3), which causes the canada.json losses. Single timed loop per result, no warm-up. Unknown keys fail the parse by default while missing keys are silently accepted; tokens over 63 characters and skipped values nested beyond 64 levels fail. GCC 14+ or Clang 20+ only; one contributor, 15 stars.

## Caveats and trade-offs

First-party README benchmark. The CPU model is given for one table only (M1 Max), and neither table gives optimization flags or build type, so methodology is only partly specified. Mixed results: on canada.json it is \~15% slower than RapidJSON parse+populate and \~80% slower than RapidJSON SAX in typed streaming, and the \~60% win needs skip annotations that avoid float parsing entirely, so it is not equal work. The README says Glaze is \~3x faster on twitter.json. The README's benchmark links (benchmarks/main.cpp, benchmarks/canada_json_parsing.cpp) are stale; the code now lives in benchmarks/syntetic/ and benchmarks/canada_json/. A very young, low-star project, recently added to vcpkg; the numbers are self-reported and have not been reproduced independently.

Header-only C++23 reflection-based parser (uses Boost.PFR); no SIMD, no hand-tuned assembly by design; forward-only-iterator streaming API differs from DOM-based RapidJSON; default floating-point backend does not guarantee perfect round-trip precision; \~3x slower than Glaze and \~15% slower than RapidJSON on canada.json parse-and-populate; on 8-bit AVR its code size (25.8KB) is larger than jsmn/cJSON.

## Maintenance

Actively maintained by a single author (v1.1.1 tagged 2026-08-06, 343 commits by one contributor, 15 stars). It is MIT-licensed, header-only and packaged for vcpkg, Conan and PlatformIO, so it is easy to vendor, but the API is young.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README numbers against RapidJSON (DOM plus manual populate, or hand-written SAX), with public code (benchmarks/syntetic/, benchmarks/twitter_json/, benchmarks/canada_json/). The README never states optimization flags or build type, and the twitter.json and canada.json runs name no CPU model, so this is partial methodology and cannot be A.
- **Verifier notes:** All claimed numbers appear in the README's Parsing Speed section and its twitter.json table (1620/1020 = 1.59x; the page says 'about 1.5x'). The record left out the canada.json losses, so I added them to claimed_speedup. Metadata checks out (MIT, 15 stars, last commit 2026-08-06, not a fork, not archived).
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/tucher/JsonFusion/blob/master/README.md>
  - <https://github.com/tucher/JsonFusion>
  - <https://github.com/tucher/JsonFusion/tree/master/benchmarks>
  - <https://github.com/tucher/JsonFusion/tree/master/benchmarks/twitter_json>
  - <https://github.com/tucher/JsonFusion/tree/master/benchmarks/syntetic>
  - <https://github.com/tucher/JsonFusion/tree/master/benchmarks/canada_json>
  - <https://github.com/tucher/JsonFusion/blob/master/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/tucher/JsonFusion>
  - <https://github.com/tucher/JsonFusion/blob/master/README.md>
  - <https://github.com/tucher/JsonFusion/blob/master/include/JsonFusion/string_search.hpp>
  - <https://github.com/tucher/JsonFusion/blob/master/include/JsonFusion/parser.hpp>
  - <https://github.com/tucher/JsonFusion/blob/master/include/JsonFusion/json.hpp>
  - <https://github.com/tucher/JsonFusion/blob/master/include/JsonFusion/fp_to_str.hpp>
  - <https://github.com/tucher/JsonFusion/blob/master/include/JsonFusion/validators.hpp>
  - <https://github.com/tucher/JsonFusion/blob/master/docs/explanation/architecture.md>
  - <https://github.com/tucher/JsonFusion/blob/master/docs/FP_BACKEND_ARCHITECTURE.md>
  - <https://github.com/tucher/JsonFusion/blob/master/docs/ANNOTATIONS_REFERENCE.md>
  - <https://github.com/tucher/JsonFusion/blob/master/docs/how-to/ERROR_HANDLING.md>
  - <https://github.com/tucher/JsonFusion/blob/master/docs/vcpkg_usage.md>
  - <https://github.com/tucher/JsonFusion/blob/master/docs/tutorials/02-modeling-json-types.md>
  - <https://github.com/tucher/JsonFusion/blob/master/docs/tutorials/03-validation-and-annotations.md>
  - <https://github.com/tucher/JsonFusion/blob/master/TODO.md>
  - <https://github.com/tucher/JsonFusion/blob/master/CMakeLists.txt>
  - <https://github.com/tucher/JsonFusion/blob/master/scripts/run_benchmarks.sh>
  - <https://github.com/tucher/JsonFusion/blob/master/.github/workflows/benchmarks.yml>
  - <https://github.com/tucher/JsonFusion/tree/master/benchmarks/twitter_json>
  - <https://github.com/tucher/JsonFusion/blob/master/benchmarks/twitter_json/benchmark.hpp>
  - <https://github.com/tucher/JsonFusion/blob/master/benchmarks/twitter_json/twitter_json_parsing.cpp>
  - <https://github.com/tucher/JsonFusion/blob/master/benchmarks/twitter_json/twitter_json_parsing_rapidjson.cpp>
  - <https://github.com/tucher/JsonFusion/blob/master/benchmarks/twitter_json/rapidjson_populate.hpp>
  - <https://github.com/tucher/JsonFusion/blob/master/benchmarks/twitter_json/twitter_model_generic.hpp>
  - <https://github.com/tucher/JsonFusion/tree/master/benchmarks/syntetic>
  - <https://github.com/tucher/JsonFusion/blob/master/benchmarks/syntetic/main.cpp>
  - <https://github.com/tucher/JsonFusion/blob/master/benchmarks/syntetic/bench_matrix.hpp>
  - <https://github.com/tucher/JsonFusion/issues>
  - <https://github.com/tucher/JsonFusion/issues/3>
  - <https://github.com/tucher/JsonFusion/issues/4>
  - <https://github.com/tucher/JsonFusion/pulls>
  - <https://github.com/tucher/JsonFusion/tags>
  - <https://github.com/tucher/JsonFusion/commits/master>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/tucher/jsonfusion`) · [data/wave4/enrich/raw/github_com_tucher_jsonfusion.json](../../../data/wave4/enrich/raw/github_com_tucher_jsonfusion.json) (enrichment confidence 0.6)

</details>
