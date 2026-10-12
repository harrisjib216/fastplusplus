# Sonic-Cpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only SIMD JSON DOM parser and serializer for C++ with a RapidJSON-style API, about 2x RapidJSON on nativejson-benchmark files.

| | |
|---|---|
| **Beats** | RapidJSON (also nlohmann/json and taocpp/json in the nativejson-benchmark chart; simdjson, yyjson, cJSON and JsonCpp in the project's own benchmark) |
| **Claimed result** | No figures in the README text; numbers exist only as bar charts. Values below are read off the chart images, approximate, not printed. nativejson parse chart (docs/images/parse.png, axis 0-100 ms): Sonic about 1.0 ms vs RapidJSON about 2.1 ms (about 2.2x faster), nlohmann about 6.2 ms (about 6x), taocpp/json about 5.7 ms; simdjson about 0.85 ms is faster than Sonic and YYjson about 1.1 ms is close. Serialize chart (docs/images/serialize.png, axis 0-40 ms): Sonic about 0.55 ms vs RapidJSON about 1.2 ms (about 2.2x), nlohmann about 4.6 ms (about 8x), taocpp/json about 2.65 ms, simdjson about 5.7 ms; YYjson about 0.42 ms is faster than Sonic. Own decode/encode charts normalize SonicDyn to 1.0 (higher is better): RapidJSON decode bars span about 0.16 to 0.74 (Sonic about 1.4x to 6x faster) and encode about 0.17 to 0.64; simdjson decode about 0.76 to 1.44 (above Sonic on lottie, github_events, citm_catalog and twitter, tied on canada) and encode about 0.19 to 0.49; yyjson decode about 0.68 to 1.54 (at or above Sonic on 7 of 11 files) and encode about 0.40 to 1.51 (above Sonic on 6 of 11 files). |
| **Workload** | (a) Project's own Google Benchmark decode and encode of 11 JSON files (book, gsoc-2018, fgo, lottie, canada, github_events, otfcc, poet, citm_catalog, twitter, twitterescaped) against RapidJSON, yyjson and simdjson; (b) miloyip/nativejson-benchmark DOM parse and stringify of canada, citm_catalog and twitter (Time in ms, 3 files) against 30+ libraries. |
| **Metric** | latency |
| **Compiler and flags** | Charts generated in 2022 (commit c16e355) with Bazel: benchmark target copts -O3 -msse4 -Wall -Wextra -mavx2 -mbmi -mpclmul -mlzcnt -DNDEBUG -std=c++17; yyjson built with -O3 -DNDEBUG -march=haswell -g, simdjson with -O3 -DNDEBUG (bazel/\*.BUILD at that commit). At HEAD the CMake path compiles bench with -O3 -DNDEBUG -g plus arch flags (Google Benchmark v1.9.5), while the Bazel benchmark target carries no -O level and scripts/tools/draw-decode-encode.py runs 'bazel build :benchmark' without --compilation_mode=opt. Compiler and version not stated. |
| **Adoption** | 977 stars; ByteDance project |
| **Last commit** | 2026-07-17 |
| **Links** | [repository](https://github.com/bytedance/sonic-cpp) · [benchmark](https://github.com/bytedance/sonic-cpp) |

## Verdict

These are first-party bar charts from 2022 (commit c16e355), with no CPU or compiler named. In the authors' nativejson-benchmark rerun on canada, citm_catalog and twitter, Sonic parses in about 1.0 ms against about 2.1 ms for RapidJSON and serializes in about 0.55 ms against about 1.2 ms (about 2.2x each); simdjson parses faster and yyjson serializes faster. The project's own Google Benchmark charts, normalized to Sonic, put RapidJSON at 0.16-0.74 on decode, but that RapidJSON build had its SSE paths compiled out.

## Use it when

- x86-64 Linux services on AVX2 hardware (Haswell or newer) that use the RapidJSON DOM today and want roughly 2x faster parsing and serialization with a familiar API.
- Workloads that parse, modify and re-serialize documents (add, remove or set members) rather than only reading them.
- Extracting one or a few fields by a known key path from large payloads with ParseOnDemand, which skips everything else.
- Teams that want a header-only C++ library with no runtime dependencies and an Apache-2.0 licence.

## Skip it when

- Inputs that need UTF-8 validation: docs/usage.md says Sonic assumes UTF-8 and does not verify it, and the ParseFlags enum in flags.h has no validation flag.
- Windows/MSVC, or macOS without checking first: the README supports only GCC or Clang on Linux; issue #133 asks whether it runs on macOS and #116 reports that the unit tests fail to compile on aarch64, although NEON, SVE2-128 and RISC-V code has landed since 2024.
- When raw speed is the only criterion: in Sonic's own charts yyjson is at or above Sonic on 7 of 11 decode files and 6 of 11 encode files, simdjson parses faster on several files and on the nativejson chart, and yyjson serializes faster there.
- Large objects queried many times: members are stored in a vector, so FindMember is a linear scan unless you call CreateMap to build a std::multimap index. Issue #86 reports string-heavy parsing performance about equal to RapidJSON (no numbers given).
- Older checkouts on untrusted input: recent commits fixed a use-after-free in Stack::Reserve (2025-12-26), OOM handling (2026-04-23) and a bounded emoji-escape tail (2026-07-17); issue #111 reported an ASan heap-buffer-overflow read on a malformed nested input; issue #140 asks when the next release is.

## How it is fast

SIMD (AVX2/SSE, with NEON and SVE2 paths at HEAD) skips whitespace and finds quote and escape characters in strings during parsing, and finds characters that need escaping during serialization. A SAX-style handler builds a compact node tree whose objects store members in a vector, so building the tree is cheap. Numbers are parsed with Eisel-Lemire plus a decimal fallback (atof_native.h) and printed with the Schubfach algorithm (ftoa.h). ParseOnDemand uses SIMD and bit masks to skip values it does not need.

## Compared with alternatives

Choose Sonic over RapidJSON when you are on x86 AVX2 Linux and want a mutable DOM with near-RapidJSON call names plus on-demand path extraction. Choose yyjson (portable C, validates UTF-8, as fast or faster on most files in Sonic's own charts) or simdjson (faster parsing with UTF-8 validation) when portability, validation or read-only throughput matter more, and glaze when you are mapping JSON to C++ structs.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (benchmark and tests fetch Google Benchmark, GoogleTest, RapidJSON, yyjson, simdjson, cJSON and JsonCpp) |
| **Minimum toolchain** | C++11 (README); GCC or Clang compiled with -mavx2 -mpclmul -mbmi or -march=haswell (docs/usage.md); old GCC releases fail to build (issues #74 and #98, gcc 4.8.5) |
| **Platforms** | x86-64 with AVX2 on Linux is the documented target; the build files also have SSE4.2, NEON, SVE2-128 and RISC-V rv64gc/zbb options and an optional -DSONIC_DYNAMIC_DISPATCH=1 mode; MSVC is unsupported |
| **Thread safety** | not documented; each Document owns its allocator by default, and re-parsing a Document invalidates pointers and iterators from the earlier parse (docs/usage.md) |
| **Drop-in for the baseline** | partial: method names follow RapidJSON (Parse, HasParseError, FindMember, MemberBegin, GetString) and it reuses RapidJSON's allocator concept, but the namespace, types, writer and flags differ and RawNumber is missing, so call sites need porting |

## Gotchas

- Harness flaw in the project's own decode/encode benchmark: RapidJSON is built without RAPIDJSON_SSE2 or RAPIDJSON_SSE42. Neither the 2022 bazel/rapidjson.BUILD, the HEAD BUILD.bazel nor the CMake bench target defines them, so RapidJSON's SIMD whitespace-skip and string-scan code (reader.h) is compiled out while Sonic gets AVX2. nativejson-benchmark's rapidjsontest.cpp turns these on from __SSE2__/__SSE4_2__, which fits the smaller gap there (about 2.2x) against the own chart's 1.4x to 6x. The adapter also uses kParseNoFlags (no full-precision float parsing).
- Harness flaw: the simdjson adapter keeps a dom::parser inside each ParseResult, and BM_Decode makes a new ParseResult every iteration, so simdjson re-allocates its parser buffers on every timed parse instead of reusing the parser. Its stat_impl and find_impl are stubs that return true, so the round-trip check after decoding verifies nothing for simdjson.
- The round-trip correctness check is weak for every library: GetStats and find_value in the Sonic and RapidJSON adapters reset 'stat = DocStat()' on each recursive call, so stat1 != stat2 compares only the root counts plus the last subtree visited. The timings are unaffected, but a wrong parse would mostly go unnoticed.
- Document::Parse copies the input into its own padded string buffer (allocateStringBuffer, SONICJSON_PADDING 64), and string nodes point into that buffer, so keep the Document alive while you use its strings. The README roadmap is stale: it lists JSON Pointer and JSON Path as missing, but AtPointer is documented and a 'support jsonpath' commit landed on 2026-03-25.

## Known shortcomings

- Charts only (commit c16e355, 2022-11-24) with no CPU or compiler stated: yyjson is faster on the serialize chart and on 7 of 11 decode and 6 of 11 encode files in Sonic's own charts, and simdjson parses faster; no UTF-8 validation; the HEAD chart script builds without the -c opt and the 2022 flags (-O3 -mavx2) were recorded separately.
- Enricher: RapidJSON was built without RAPIDJSON_SSE2/SSE42 (c16e355 rapidjson.BUILD, HEAD Bazel and CMake), so its SIMD paths were compiled out while nativejson-benchmark enables them (gap there about 2.2x vs the own-chart 1.4-6x); the simdjson adapter builds a new dom::parser every iteration and its stat/find are stubs; GetStats/find_value reset the stat on each recursive call, so the round-trip check compares a fragment only; no UTF-8 validation flag. Downgraded C to D (AssemblyScript precedent: baseline crippled by the build).

## Caveats and trade-offs

Evidence is first-party and chart-only: no printed numbers, no CPU model, no compiler version; the y-axis label 'HIB' in the decode/encode charts is undefined (read as higher is better, normalized to SonicDyn = 1.0). All four charts date from 2022-11-24 and have not been regenerated, so they reflect late-2022 versions of Sonic, RapidJSON, yyjson and simdjson. The nativejson-benchmark chart is a rerun by the Sonic authors on unstated hardware, with libraries of unknown versions, and the Sonic adapter for that suite is not linked from the README. Sonic is not the fastest in its own charts: simdjson parses faster on the nativejson chart and on several own decode files, and yyjson serializes faster on the nativejson chart and beats Sonic on 7 of 11 decode and 6 of 11 encode files in the project's own benchmark; the clear win is over RapidJSON, nlohmann and taocpp/json. Sonic does not validate UTF-8 (README TODO 'Support validating UTF-8'), so comparisons with validating parsers such as simdjson are not like-for-like. Rerunning the chart script at HEAD (bazel build without -c opt, no -O in the benchmark target copts) would produce an unoptimized build. Requires x86 AVX2 and Linux per the README. The project's own benchmark does not include nlohmann/json. [retier] Charts only (commit c16e355, 2022-11-24) with no CPU or compiler stated and values read by pixel length. The RapidJSON baseline was built without RAPIDJSON_SSE2/SSE42 (rapidjson.BUILD at c16e355, and the HEAD Bazel and CMake files), so its SIMD paths were compiled out; nativejson-benchmark enables them and shows a gap of about 2.2x against the own-chart 1.4-6x. The simdjson adapter builds a new dom::parser every iteration and its stat/find are stubs; GetStats/find_value reset the stat on each recursive call, so the round-trip check compares a fragment only. In Sonic's own charts yyjson is faster on serialize and on 7 of 11 decode and 6 of 11 encode files, and simdjson parses faster. No UTF-8 validation; the HEAD chart script builds without the -c opt (2022 flags -O3 -mavx2 recorded separately).

Header-only, C++11 or newer; README requires x86 with AVX2, GCC or LLVM, Linux and says MSVC is unsupported (the recent commit log mentions ARM, SVE2 and RISC-V work). Parses into a compact document tree and has an ondemand mode; SIMD whitespace skipping, string-escape search and a STOA float algorithm. The README roadmap still lists UTF-8 validation, JSON Pointer, JSON Path and RawNumber as unsupported, so it does less checking than simdjson.

## Maintenance

Active ByteDance project (977 stars, last commit 2026-07-17, Apache-2.0, header-only and easy to vendor), but the performance charts date from 2022 and users are waiting for a new release (issue #140).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party bar charts only (docs/images/compare_Decode.png, compare_Encode.png, parse.png, serialize.png, all committed 2022-11-24 in c16e355); benchmark code (benchmark/ and scripts/tools/draw-decode-encode.py) and 2022 Bazel flags are public, but no CPU model or compiler is stated and the nativejson rerun was done by the Sonic authors on unstated hardware.
- **Retiered** C to D: Downgraded C to D: the own-benchmark RapidJSON baseline was built without RAPIDJSON_SSE2/SSE42, so its SIMD paths were compiled out (AssemblyScript precedent: baseline crippled by a build default), the simdjson adapter rebuilds its parser every iteration, and the charts carry no CPU or compiler.
- **Verifier notes:** Chart readings re-checked from the PNGs and broadly match; corrected Sonic parse to about 1.0 ms and added that yyjson beats Sonic on the serialize chart and on most of Sonic's own decode/encode files. Tier C stands (no CPU or compiler). Shortcomings: chart-only 2022 first-party data, no UTF-8 validation, slower than yyjson/simdjson on many files, HEAD chart script builds without optimization.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** first-party charts (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/bytedance/sonic-cpp>
  - <https://github.com/bytedance/sonic-cpp/commits>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/docs/images/parse.png>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/docs/images/serialize.png>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/docs/images/compare_Decode.png>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/docs/images/compare_Encode.png>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/BUILD.bazel>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/scripts/tools/draw-decode-encode.py>
  - <https://github.com/bytedance/sonic-cpp/commits/master/docs/images/compare_Decode.png>
  - <https://github.com/bytedance/sonic-cpp/commits/master/scripts/tools/draw-decode-encode.py>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/c16e355adc1e56a1efe40fcf20a38bed65c0e842/scripts/tools/draw-decode-encode.py>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/c16e355adc1e56a1efe40fcf20a38bed65c0e842/BUILD.bazel>
  - <https://github.com/bytedance/sonic-cpp/tree/c16e355adc1e56a1efe40fcf20a38bed65c0e842>
  - <https://github.com/bytedance/sonic-cpp/tree/c16e355adc1e56a1efe40fcf20a38bed65c0e842/bazel>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/c16e355adc1e56a1efe40fcf20a38bed65c0e842/bazel/yyjson.BUILD>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/c16e355adc1e56a1efe40fcf20a38bed65c0e842/bazel/simdjson.BUILD>
- **Sources the enricher read:**
  - <https://github.com/bytedance/sonic-cpp>
  - <https://github.com/bytedance/sonic-cpp/commits>
  - <https://github.com/bytedance/sonic-cpp/issues?q=is%3Aissue>
  - <https://github.com/bytedance/sonic-cpp/issues/86>
  - <https://github.com/bytedance/sonic-cpp/issues/100>
  - <https://github.com/bytedance/sonic-cpp/issues/111>
  - <https://github.com/bytedance/sonic-cpp/issues/119>
  - <https://github.com/bytedance/sonic-cpp/tree/master/include/sonic/dom>
  - <https://github.com/bytedance/sonic-cpp/tree/master/include/sonic/internal>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/docs/usage.md>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/BUILD.bazel>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/MODULE.bazel>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/cmake/external.cmake>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/cmake/set_arch_flags.cmake>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/benchmark/main.cpp>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/benchmark/json.h>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/benchmark/sonic.hpp>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/benchmark/rapidjson.hpp>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/benchmark/simdjson.hpp>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/benchmark/yyjson.hpp>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/benchmark/jsoncpp.hpp>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/benchmark/ondemand.hpp>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/scripts/tools/draw-decode-encode.py>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/include/sonic/sonic.h>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/include/sonic/macro.h>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/include/sonic/dom/flags.h>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/include/sonic/dom/parser.h>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/include/sonic/dom/generic_document.h>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/include/sonic/internal/arch/sonic_cpu_feature.h>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/include/sonic/internal/ftoa.h>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/include/sonic/internal/atof_native.h>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/HEAD/include/sonic/internal/parse_number_normal_fast.h>
  - <https://raw.githubusercontent.com/bytedance/sonic-cpp/c16e355adc1e56a1efe40fcf20a38bed65c0e842/bazel/rapidjson.BUILD>
  - <https://raw.githubusercontent.com/Tencent/rapidjson/24b5e7a8b27f42fa16b96fc70aade9106cf7102f/include/rapidjson/reader.h>
  - <https://raw.githubusercontent.com/miloyip/nativejson-benchmark/master/src/tests/rapidjsontest.cpp>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/bytedance/sonic-cpp`) · [data/wave4/enrich/raw/github_com_bytedance_sonic_cpp.json](../../../data/wave4/enrich/raw/github_com_bytedance_sonic_cpp.json) (enrichment confidence 0.75)

</details>
