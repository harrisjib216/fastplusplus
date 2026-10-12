# jsoncons

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> Header-only C++ JSON/CBOR/MessagePack/BSON library whose DOM reads \~2x and writes \~2-4x faster than nlohmann/json in the author's benchmark.

| | |
|---|---|
| **Beats** | nlohmann/json |
| **Claimed result** | Integer file (540.82MB): jsoncons reads in 3.918s and writes in 0.744s vs nlohmann 8.177s / 2.885s (\~2.1x read, \~3.9x write faster, derived from page data). Against RapidJSON (2.254s / 0.656s) jsoncons is slower on both read and write (derived from page data). Float file (794.72MB): jsoncons 8.879s / 3.879s vs nlohmann 15.997s / 7.165s (\~1.8x faster both ways, derived from page data). Against RapidJSON (3.443s / 3.061s) jsoncons is slower on both (derived from page data). |
| **Workload** | Read and write two large synthetic JSON files (540.82MB text+integers, 794.72MB text+floating point) into each library's native document type, on a Windows workstation. |
| **Metric** | throughput |
| **Hardware** | Page lists 'Lenovo Thinkpad X Extreme with 8 cores, 16 hardware threads, 32 GB memory, 2 TB solid state drive'; Environment 'Windows, Intel'; OS given as 'Windows 2011'. No CPU model stated. |
| **Compiler and flags** | Visual Studio 2022 Version 17.14.16, /O2 /Ot, /std:c++23preview |
| **Adoption** | 853 stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/danielaparker/jsoncons) · [benchmark](https://github.com/danielaparker/json_benchmarks/blob/master/report/big.text.integer.md) |

## Verdict

In the author's own json_benchmarks (single run; MSVC 17.14.16 /O2 /Ot /std:c++23preview; Lenovo ThinkPad X Extreme, CPU model not stated), parsing a 540.82 MB text+integer file from std::ifstream into jsoncons::json took 3.918 s vs 8.177 s for nlohmann::json (2.1x), and writing took 0.744 s vs 2.885 s (3.9x). On the 794.72 MB text+double file it was 8.879 s / 3.879 s vs 15.997 s / 7.165 s (1.8x both ways), and the same pages show yyjson, RapidJSON and Boost.JSON beating jsoncons on both read and write.

## Use it when

- You use nlohmann/json and want a mutable DOM that reads 1.8-2.1x and writes 1.8-3.9x faster (author's large-file test) without switching to an immutable-document library.
- Mixed-format pipelines: the same basic_json value and reflection traits read and write JSON, CBOR (including typed arrays and stringref), MessagePack, BSON, UBJSON and CSV.
- Multi-GB JSON or unbounded streams: json_stream_cursor pull-parses in 16 KB chunks, and pipe filters let you skip events, so you never build the whole tree.
- You need JSONPath, JMESPath or JSON Schema validation in the same dependency. Compiled expressions and json_schema objects are documented as immutable and thread-safe, so they can be shared across threads.
- Memory-bound DOM work: the parsed 540 MB integer file took 343 MB, against nlohmann 409, Boost.JSON 502 and yyjson 871 MB in the same run. RapidJSON used a little less (332 MB).

## Skip it when

- Raw parse/serialize throughput is the goal. In the author's own shootout, yyjson reads the integer file 3.9x faster (1.007 s vs 3.918 s), and RapidJSON, Boost.JSON and glaze also read faster.
- Building big objects by random-order insertion: json stores objects as a sorted vector, so each insert shifts elements. A user benchmark in issue #346 (still open) measured 1000 insert+erase at 11.75 ms vs nlohmann's 0.47 ms. ojson avoids sorting, but its find() is a linear scan.
- Float-heavy input built with toolchains outside the std::from_chars auto-detection (GCC 11+ or MSVC 19.24+, C++17), where double parsing falls back to strtod. Separately, the 2016 nativejson-benchmark (clang 7) had an old jsoncons parsing canada.json slower than nlohmann (77.3 vs 55.6 ms).
- You need a stable API. Recent minor releases renamed public types (1.9.0: string_source, order_preserving_policy, json_conv_traits; 1.8.0: json_pointer_arg), and 1.8.0 changed the basic_json copy constructor from shallow to deep copies of json_ref pointers, so pin a version.

## How it is fast

The parser is a scalar, resumable, byte-at-a-time state machine that feeds a SAX-style visitor and reads streams in 16 KB chunks (no SIMD). The DOM decoder pushes members onto one flat stack and builds each object at end_object with a single std::sort on (key, index) into a sorted std::vector of key/value pairs, rather than allocating a std::map node per member; lookups are then std::lower_bound binary search. Values are 16 bytes: strings up to 13 chars are stored inline and longer strings take one header-plus-data allocation, which is why its DOM was among the smallest in the shootout (343 MB vs nlohmann 409 MB on the integer file). Doubles are printed with Grisu3, falling back to snprintf %.15g and then %.17g if the result does not round-trip, and parsed with std::from_chars where the config enables it.

## Compared with alternatives

Pick jsoncons over yyjson, simdjson or Boost.JSON when you want one header-only dependency that covers a mutable DOM, struct mapping, pull streaming, the binary formats (CBOR/MessagePack/BSON) and JSONPath/JMESPath/Schema, with a DOM under half the size of yyjson's in the author's test. If you only need fast JSON parse/serialize, yyjson (3.9x faster read here), simdjson (read-only parsing) or Boost.JSON (1.7x faster read here) are the better picks.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (vcpkg port available; the optional extensions are in include/jsoncons_ext) |
| **Minimum toolchain** | C++11. The std::from_chars number path needs C++17 with GCC 11+ or MSVC 19.24+, and the pmr:: aliases need std::pmr::polymorphic_allocator. README CI matrix: VS2019/2022, GCC 6-12, clang 3.9-15, Xcode 11-14. |
| **Platforms** | any. Portable scalar code; the only intrinsics are optional F16C (half floats) and MSVC BMI2 mulx. CI runs on Windows x86/x64, Ubuntu x64 and macOS. |
| **Thread safety** | Not documented for basic_json, parsers or encoders. Compiled JSONPath/JMESPath expressions and json_schema are documented as immutable and thread-safe. |
| **Drop-in for the baseline** | partial — same model (mutable variant DOM; json sorts keys like nlohmann::json's std::map, ojson keeps insertion order), but accessor, iteration and reflection APIs differ, so call sites need porting |

## Gotchas

- Duplicate keys: the parsed json keeps the first occurrence. {"first":1,"second":2,"first":3} yields first == 1 (test parse_duplicate_names).
- Lenient by default: allow_comments defaults to true, so /\* \*/ and // comments are silently accepted. Set allow_comments(false) in json_options for strict parsing. max_nesting_depth defaults to 1024.
- lossless_bignum defaults to true, so integers beyond 64 bits come back as strings tagged semantic_tag::bigint, and out-of-range floats as bigdec, not as doubles.
- Errors are reported by exceptions (only some APIs return std::error_code). With -fno-exceptions or JSONCONS_NO_EXCEPTIONS, every throw becomes std::terminate.

## Caveats and trade-offs

This is a first-party shootout run by the jsoncons author: a single run on a single machine with no CPU model. The timed read and write include std::ifstream / std::ofstream I/O. jsoncons beats nlohmann (and jsoncpp and reflect-cpp) but is slower on read than yyjson, RapidJSON, Boost.JSON and glaze, and slower on write than yyjson, Boost.JSON and RapidJSON. The float-file page prints the jsoncons version as an unexpanded macro string; the integer page says 1.8.1. The independent miloyip/nativejson-benchmark (2016, clang 7.0, i7-4980HQ) showed mixed results against nlohmann for old versions: slower on canada parse (77.3 vs 55.6 ms), faster on twitter parse (3.5 vs 7.0 ms).

jsoncons beats nlohmann/json clearly but is not the fastest option in this same shootout (yyjson and RapidJSON both beat it on these workloads); jsoncons trades some speed for API breadth (JSON Pointer/Patch/Path, JMESPath, multiple binary formats).

## Maintenance

Actively maintained (v1.9.0 released 2026-08-07, commits through 2026-09-22, OSS-Fuzz integrated, no NVD CVEs found for 'jsoncons'), and header-only under the Boost Software License 1.0, so you can vendor it by copying include/jsoncons (plus include/jsoncons_ext for the extensions).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now C.
- **Tier reason:** The numbers come from the project author's own benchmark repo; its README says it exists 'to measure how jsoncons compares to other json libraries'. It is first-party and neither well-known nor independent (6 stars). The code is public (src/tests/\*_benchmark.cpp, src/test_driver.cpp), and the compiler (VS 2022 17.14.16) and flags (/O2,/Ot) are stated, but there is no CPU model, only 'Windows, Intel' and the laptop model. That makes it first-party and short of A, so C, not B.
- **Verifier notes:** Every number matches the jsoncons rows on the two report pages (report updated 2026-07-03). GitHub license spdx is NOASSERTION, but the LICENSE file is the Boost Software License 1.0 text, so BSL-1.0 and copyable stand. The star count (853) and last commit (2026-09-22) are confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/danielaparker/jsoncons>
  - <https://github.com/danielaparker/jsoncons/blob/master/LICENSE>
  - <https://github.com/danielaparker/jsoncons/blob/master/README.md>
  - <https://github.com/danielaparker/json_benchmarks>
  - <https://github.com/danielaparker/json_benchmarks/blob/master/report/big.text.integer.md>
  - <https://github.com/danielaparker/json_benchmarks/blob/master/report/big.text.floating_point.md>
  - <https://github.com/danielaparker/json_benchmarks/blob/master/src/tests/jsoncons_benchmark.cpp>
  - <https://github.com/danielaparker/json_benchmarks/blob/master/src/tests/nlohmann_benchmark.cpp>
  - <https://github.com/danielaparker/json_benchmarks/blob/master/src/test_driver.cpp>
  - <https://github.com/miloyip/nativejson-benchmark>
  - <https://github.com/miloyip/nativejson-benchmark/blob/master/sample/performance_Corei7-4980HQ@2.80GHz_mac64_clang7.0.csv>
- **Sources the enricher read:**
  - <https://github.com/danielaparker/jsoncons>
  - <https://github.com/danielaparker/jsoncons/blob/master/README.md>
  - <https://github.com/danielaparker/jsoncons/blob/master/CHANGELOG.md>
  - <https://github.com/danielaparker/jsoncons/releases>
  - <https://github.com/danielaparker/jsoncons/blob/master/include/jsoncons/json_parser.hpp>
  - <https://github.com/danielaparker/jsoncons/blob/master/include/jsoncons/json_decoder.hpp>
  - <https://github.com/danielaparker/jsoncons/blob/master/include/jsoncons/basic_json.hpp>
  - <https://github.com/danielaparker/jsoncons/blob/master/include/jsoncons/sorted_json_object.hpp>
  - <https://github.com/danielaparker/jsoncons/blob/master/include/jsoncons/ordered_json_object.hpp>
  - <https://github.com/danielaparker/jsoncons/blob/master/include/jsoncons/json_options.hpp>
  - <https://github.com/danielaparker/jsoncons/blob/master/include/jsoncons/json_reader.hpp>
  - <https://github.com/danielaparker/jsoncons/blob/master/include/jsoncons/json_fwd.hpp>
  - <https://github.com/danielaparker/jsoncons/blob/master/include/jsoncons/source.hpp>
  - <https://github.com/danielaparker/jsoncons/blob/master/include/jsoncons/utility/read_number.hpp>
  - <https://github.com/danielaparker/jsoncons/blob/master/include/jsoncons/utility/write_number.hpp>
  - <https://github.com/danielaparker/jsoncons/blob/master/include/jsoncons/utility/heap_string.hpp>
  - <https://github.com/danielaparker/jsoncons/blob/master/include/jsoncons/config/compiler_support.hpp>
  - <https://github.com/danielaparker/jsoncons/blob/master/doc/ref/corelib/basic_json.md>
  - <https://github.com/danielaparker/jsoncons/blob/master/doc/ref/corelib/basic_json_options.md>
  - <https://github.com/danielaparker/jsoncons/blob/master/doc/ref/jsonpath/jsonpath.md>
  - <https://github.com/danielaparker/jsoncons/blob/master/doc/ref/jmespath/jmespath.md>
  - <https://github.com/danielaparker/jsoncons/blob/master/doc/ref/jsonschema/json_schema.md>
  - <https://github.com/danielaparker/jsoncons/blob/master/test/corelib/src/json_object_tests.cpp>
  - <https://github.com/danielaparker/jsoncons/blob/master/.github/workflows/macos.yml>
  - <https://github.com/danielaparker/jsoncons/blob/master/.github/workflows/ubuntu.yml>
  - <https://github.com/danielaparker/jsoncons/blob/master/.github/workflows/windows.yml>
  - <https://github.com/danielaparker/jsoncons/blob/master/.github/workflows/cifuzz.yml>
  - <https://github.com/danielaparker/jsoncons/blob/master/.github/workflows/codeql-analysis.yml>
  - <https://github.com/danielaparker/jsoncons/blob/master/.github/workflows/flawfinder.yml>
  - <https://github.com/danielaparker/jsoncons/blob/master/.circleci/config.yml>
  - <https://github.com/danielaparker/jsoncons/security/advisories>
  - <https://github.com/danielaparker/jsoncons/issues/346>
  - <https://github.com/danielaparker/jsoncons/issues/391>
  - <https://github.com/danielaparker/jsoncons/issues/417>
  - <https://github.com/danielaparker/jsoncons/issues/684>
  - <https://github.com/danielaparker/jsoncons/issues/728>
  - <https://github.com/danielaparker/json_benchmarks>
  - <https://github.com/danielaparker/json_benchmarks/blob/master/report/big.text.integer.md>
  - <https://github.com/danielaparker/json_benchmarks/blob/master/report/big.text.floating_point.md>
  - <https://github.com/danielaparker/json_benchmarks/blob/master/src/tests/jsoncons_benchmark.cpp>
  - <https://github.com/danielaparker/json_benchmarks/blob/master/src/tests/nlohmann_benchmark.cpp>
  - <https://github.com/danielaparker/json_benchmarks/blob/master/src/tests/yyjson_benchmark.cpp>
  - <https://github.com/miloyip/nativejson-benchmark/blob/master/sample/performance_Corei7-4980HQ@2.80GHz_mac64_clang7.0.csv>
  - <https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=jsoncons>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/danielaparker/jsoncons`) · [data/wave4/enrich/raw/github_com_danielaparker_jsoncons.json](../../../data/wave4/enrich/raw/github_com_danielaparker_jsoncons.json) (enrichment confidence 0.82)

</details>
