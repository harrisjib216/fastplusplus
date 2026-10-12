# Easy Reflection

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Reflection and code generation](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> C++17 reflection via Clang code generation; serializes structs to JSON, YAML and binary, charted 3.3x faster JSON writes than nlohmann/json.

| | |
|---|---|
| **Beats** | nlohmann/json (JSON) and yaml-cpp (YAML); RapidJSON also measured |
| **Claimed result** | Per-operation times in microseconds read from the README chart (benchmarks/performance_chart.png, labelled Core i5): JSON serialization 2.8 vs nlohmann 9.3 (3.3x faster, derived from chart data); JSON deserialization 17.4 vs nlohmann 20.8 (1.2x), and 5.7 with the optional simdjson parser (3.6x); YAML serialization 3.4 vs yaml-cpp 331.8 (about 98x) and YAML deserialization 18.1 vs yaml-cpp 274.5 (about 15x), derived from chart data. RapidJSON on the same chart: 3.4 serialize, 7.4 parse. README text: 'JSON is faster than nlohmann json. Serialization is the same fast as rapid json, deserialization is a little faster with simdjson parser and more than twice slower without.' |
| **Workload** | Google Benchmark of serializing and deserializing one 2.9 KB user-profile document (benchmarks/data/boba_fett.json) to and from a reflected C++ struct, against nlohmann::json parse/dump, RapidJSON DOM parse/Writer and yaml-cpp load/emit of a generic node. |
| **Metric** | latency |
| **Hardware** | Only 'Core i5' (image alt text); exact CPU model not stated |
| **Adoption** | 104 stars |
| **Last commit** | 2026-08-20 |
| **Links** | [repository](https://github.com/chocolacula/easy_reflection_cpp) · [benchmark](https://github.com/chocolacula/easy_reflection_cpp) |

## Verdict

First-party Google Benchmark (benchmarks/serialization.cpp) on one 2.9 KB document, chart labelled only Core i5, no compiler, flags or build type in the repo: typed-struct JSON write 2.8 us vs nlohmann/json DOM dump 9.3 us and read 17.4 vs 20.8 us (5.7 us via simdjson), YAML write 3.4 vs 331.8 us and read 18.1 vs 274.5 us against yaml-cpp, with RapidJSON at 3.4 us write and 7.4 us read; outputs are not checked for equivalence and the writers skip escaping and quoting.

## Use it when

- Learning or prototyping attribute-driven reflection with Clang code generation on C++17: enum-to-string, field iteration, method calls and debug printing without hand-written glue.
- Round-tripping your own structs where the same library writes and reads the data and strings are plain text (no quotes, backslashes, control characters or \u escapes).
- Small typed documents (the benchmark used one 2.9 KB profile) parsed through the simd_json path, which is the only JSON reader here that decodes escapes properly.
- Compact storage of your own structs: the repo chart puts the VLQ binary encoding at 61% of the JSON byte size.

## Skip it when

- Production use: the README calls the project mostly a proof of concept and recommends glaze instead, and the repository has been archived read-only since 2026-08-20.
- Any JSON or YAML exchanged with other software: strings containing quotes, backslashes or newlines produce invalid JSON on write, escaped input is stored undecoded by the native parser, and YAML strings such as true, 123 or 'a: b' are written unquoted and change type or structure on reload.
- Untrusted or loosely shaped input: parse_bool treats any token other than false as true, number conversions are unchecked, and an unknown key makes the native parser's get_field(...).unwrap() throw std::runtime_error instead of skipping the field.
- Floating-point data: doubles are written with std::fixed and setprecision(9), so magnitudes below about 5e-10 print as 0.000000000 and round trips keep only 9 decimal places; the repo's own threshold tests compare floats with a 0.1 tolerance.
- Teams that cannot build a patched LLVM from source (about 45 minutes on a GitHub runner per readme/installation.md) whenever reflected types change; generated files can be committed, but regenerating needs that toolchain.

## How it is fast

The generator emits per-type field tables, so serialization walks a type-erased TypeInfo tree and appends straight into a std::string through a virtual IWriter, and deserialization writes values directly into struct fields with no intermediate DOM. The native JSON parser is a RE-flex generated DFA lexer (adapted from Robert van Engelen's RE-flex JSON example) feeding a recursive-descent parser; the optional simd_json path parses with simdjson's DOM parser and copies the tape into fields. Part of the charted gap is skipped work, not technique: the JSON writer never escapes strings, the native lexer never decodes escapes, numbers go through unchecked strtoll/strtoull/strtod, and the YAML writer emits every string as an unquoted plain scalar.

## Compared with alternatives

Rarely: for JSON from reflected structs, glaze (the author's own recommendation) or simdjson's experimental_json_builder (C++26 reflection, no external generator) are the safer picks, and for binary, struct_pack, bitsery or YAS. Choose Easy Reflection only to study a Clang-attribute reflection design that also covers runtime enum strings, method invocation and YAML on C++17.

## Integration

| | |
|---|---|
| **Form** | static lib (`reflection`) plus a code generator binary (er_gen) that emits one .h/.cpp per reflected type |
| **Dependencies** | RE-flex (git submodule, linked statically) and simdjson (default, disable with -DUSE_SIMD_JSON=OFF); er_gen needs a patched LLVM/Clang built from source, inja and tclap; benchmarks add Google Benchmark, RapidJSON and yaml-cpp; all fetched through a vcpkg submodule |
| **Minimum toolchain** | C++17, CMake 3.19+; CI builds the generator and tests in Release on Ubuntu 22.04 |
| **Platforms** | README claims Linux, macOS and Windows on x86 and ARM; CI covers only Ubuntu 22.04 x86 |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Correctness bug behind the serialization numbers: json.cpp writes std::string contents between quotes with no escaping, and the native lexer rule [^"\\]\*(?:\\.[^"\\]\*)\* assigns the raw string body, so \n, \" and \uXXXX stay undecoded. The benchmark document (boba_fett.json) has no backslashes, so its output happens to be valid, but the timed er writer skips the per-byte escape scan that nlohmann's dump_escaped (with strict UTF-8 checking) and RapidJSON's WriteString escape table perform; the 3.3x serialization gap is not like-for-like. The round-trip tests use CharSet::WoSymbols strings and never exercise escapes.
- The yaml-cpp ratios (about 98x write, 15x read) compare an emitter that writes strings as unquoted plain scalars against yaml-cpp's full YAML::Node emitter and loader; treat them as an upper bound on unequal work, not a like-for-like speedup.
- The JSON scalar rule needs a value followed immediately by ',', '}', ']' or '\n' (lookahead (?=[,}\]\n])), so input like [1 ] or CRLF line endings after a number or boolean does not match it.
- Every array element is parsed into a heap-allocated Box and then copied into the container (no move support, issue #9 open), and the simd_json path constructs a new simdjson dom::parser and a padded_string copy on every call.

## Known shortcomings

- Chart values only (serialization.cpp does real work); compiler flags and CPU missing. Typed-struct reflection vs generic DOM, so not like-for-like; the yaml-cpp gain (about 98x) is capped at C. The README claim that nlohmann and RapidJSON convert values lazily is wrong. Single 2.9 KB doc; proof of concept that points users to glaze. Archived 2026-08-20, last code change 2025-02-04.
- Enricher: the JSON writer never escapes strings and the native lexer leaves \n, \" and \uXXXX undecoded, so the 3.3x serialization gap skips the escape scan nlohmann and RapidJSON perform; the YAML writer emits every string unquoted, so the yaml-cpp 98x/15x rows are unequal work; unknown keys throw std::runtime_error, doubles are written fixed with 9 decimals (lossy), and round-trip tests use symbol-free strings only. Downgraded C to D (uniwidth precedent: bug in the measured hot path).

## Caveats and trade-offs

Numbers exist only inside chart images (read from benchmarks/performance_chart.png); the README text gives no figures. Compiler, build type, flags and CPU model are not stated, and neither benchmarks/CMakeLists.txt nor the root CMakeLists.txt sets a build type or optimisation flags. The benchmark compares different jobs: Easy Reflection builds or dumps a typed struct, while nlohmann, RapidJSON and yaml-cpp build or dump a generic DOM. The README justifies this by saying the others do not convert strings to int, float or bool until accessed, which does not hold for nlohmann::json::parse or RapidJSON Document::Parse (both convert numbers and booleans at parse time). One small 2.9 KB document only (boba_fett.json, 2933 bytes). The yaml-cpp ratios (about 98x and 15x) are implausibly large for unstated flags; the yaml-cpp serialization case streams a YAML::Node through std::ostream, and the README itself says 'if I did the benchmark right'. Outputs are not checked for equivalence. The README calls the project 'mostly a proof of concept' and tells users who want this in production to use glaze instead. Repository archived and read-only since 2026-08-20 (the last commits that day only update the README; the last code change is 2025-02-04). [retier] Chart values only (serialization.cpp does real work) with compiler flags and CPU missing; typed-struct reflection vs generic DOM. The JSON writer never escapes strings and the native lexer leaves \n, \" and \uXXXX undecoded, so the 3.3x serialization gap skips the escape scan nlohmann and RapidJSON perform; the YAML writer emits every string unquoted, so the yaml-cpp rows are unequal work. Unknown keys throw std::runtime_error, doubles are written fixed with 9 decimals (lossy), round-trip tests use symbol-free strings only. The README claim that nlohmann and RapidJSON convert values lazily is wrong. Single 2.9 KB doc; proof of concept that points users to glaze. Archived 2026-08-20, last code change 2025-02-04.

Needs a clang-based code-generation step that parses [[er::reflect]] attributes and emits reflection code; C++17; native JSON, YAML 1.2 and a variable-length-integer binary format deserialize straight into typed objects (strings are converted to int, float and bool on load). Binary form is 61% of the JSON byte size (YAML 104%) per the repo's second chart, which is serialized size, not RAM.

## Maintenance

Archived read-only since 2026-08-20 (last code change 2025-02-04), Apache-2.0 and copyable, but a self-described proof of concept with string-escaping and YAML-quoting bugs; use it as a design reference, not a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party Google Benchmark code is public (benchmarks/serialization.cpp) and the chart numbers match the record, but compiler, flags and exact CPU model are missing (only 'Core i5' alt text; benchmarks/CMakeLists.txt and root CMakeLists.txt set no build type or optimisation flags), and the yaml-cpp gain is about 98x with unstated flags, so capped at C.
- **Retiered** C to D: Downgraded C to D: enricher found the JSON writer never escapes strings and the YAML writer emits all strings unquoted, so the measured serialization gaps (3.3x vs nlohmann/RapidJSON, 98x/15x vs yaml-cpp) skip work the baselines do and the output is wrong for strings that need escaping (uniwidth and fast_resize precedents; kept as directional since the chart values are real measurements of a flawed writer).
- **Verifier notes:** Chart values confirmed exactly (er JSON ser 2.8 vs nlohmann 9.3 us, deser 17.4 vs 20.8, simdjson path 5.7; YAML 3.4 vs 331.8 and 18.1 vs 274.5; RapidJSON 3.4 and 7.4) and the benchmark loop does real work for every library (no no-op found). Metadata verified: Apache-2.0, 104 stars, archived 2026-08-20, last commit 2026-08-20 (README-only). Shortcomings: unstated flags and CPU, typed struct vs generic DOM, single 2.9 KB document, implausible yaml-cpp ratios, proof-of-concept project that points to glaze, archived.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party chart (verifier); enricher code reading
- **Pages the verifier opened:**
  - <https://github.com/chocolacula/easy_reflection_cpp>
  - <https://github.com/chocolacula/easy_reflection_cpp/commits/main>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/benchmarks/performance_chart.png>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/benchmarks/serialization.cpp>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/benchmarks/data/boba_fett.json>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/vcpkg.json>
- **Sources the enricher read:**
  - <https://github.com/chocolacula/easy_reflection_cpp>
  - <https://github.com/chocolacula/easy_reflection_cpp/issues?q=is%3Aissue>
  - <https://github.com/chocolacula/easy_reflection_cpp/tree/main/tests>
  - <https://github.com/chocolacula/easy_reflection_cpp/tree/main/library/include/er/type_info/variants>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/vcpkg.json>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/readme/installation.md>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/readme/how_to_use.md>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/.github/workflows/cmake.yml>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/benchmarks/serialization.cpp>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/benchmarks/config.yaml>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/benchmarks/data/user_profile.h>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/benchmarks/data/boba_fett.json>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/benchmarks/data/boba_fett.yaml>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/CMakeLists.txt>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/cmake/tools.cmake>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/lexers/json.l>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/include/er/serialization/json.h>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/include/er/serialization/simd_json.h>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/include/er/serialization/yaml.h>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/include/er/serialization/binary.h>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/include/er/expected.h>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/include/er/type_info/variants/object/object.h>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/include/er/tools/stringify.h>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/src/tools/stringify.cpp>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/src/serialization/json/json.cpp>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/src/serialization/json/parser_json.cpp>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/src/serialization/json/parser_json.h>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/src/serialization/json/lexer_json.yy.cpp>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/src/serialization/json/simd_json.cpp>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/src/serialization/writers/iwriter.h>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/src/serialization/writers/string_writer.h>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/src/serialization/yaml/yaml.cpp>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/library/src/serialization/yaml/serializer.h>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/tests/various.cpp>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/tests/library.cpp>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/tests/tresholds.cpp>
  - <https://raw.githubusercontent.com/chocolacula/easy_reflection_cpp/HEAD/tests/tools.h>
  - <https://raw.githubusercontent.com/Tencent/rapidjson/HEAD/include/rapidjson/writer.h>
  - <https://raw.githubusercontent.com/nlohmann/json/HEAD/include/nlohmann/detail/output/serializer.hpp>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/chocolacula/easy_reflection_cpp`) · [data/wave4/enrich/raw/github_com_chocolacula_easy_reflection_cpp.json](../../../data/wave4/enrich/raw/github_com_chocolacula_easy_reflection_cpp.json) (enrichment confidence 0.75)

</details>
