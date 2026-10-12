# metajson (iod::metajson)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Header-only C++17 JSON codec for structs with compile-time-known shape; README claims up to 9x nlohmann/json, 2x RapidJSON.

| | |
|---|---|
| **Beats** | nlohmann/json, RapidJSON |
| **Claimed result** | Up to 9x faster than nlohmann/json and 2x faster than RapidJSON (author states these numbers are not from a comprehensive benchmark) |
| **Workload** | Encoding/decoding C++ structs and vectors whose structure is known at compile time, compared to nlohmann/json and RapidJSON |
| **Metric** | throughput |
| **Compiler and flags** | libraries/metajson/benchmarks/CMakeLists.txt builds the Google Benchmark programs with -std=c++1z -O3 -DNDEBUG -march=native. The README's 'Compilers' section (GCC 7.1.1, Clang 5.0.1) lists supported compilers and does not say which one produced the 9x/2x figures. |
| **Adoption** | 69 stars |
| **Last commit** | 2019-11-26 |
| **Links** | [repository](https://github.com/iodcpp/metajson) · [benchmark](https://github.com/iodcpp/metajson/blob/master/libraries/metajson/README.md) |

## Verdict

The README claims up to 9x faster than nlohmann/json and 2x faster than RapidJSON, but publishes no results table, compiler or CPU. The public Google Benchmark sources (-O3 -march=native) time decoding a 3-field object and 60-element int/float arrays into C++ values, while the RapidJSON and nlohmann versions build a DOM and copy out of it; the author wrote in issue #1 that 'being fair was not the goal' and in issue #6 that nativejson-benchmark could not be implemented with metajson.

## Use it when

- Studying the compile-time-schema, no-DOM decoding idea in about 1,200 lines before adopting its maintained continuation, li::json in matt-42/lithium.
- Decoding small, trusted, fixed-shape messages that your own code produces (a few int/string fields, flat int or float arrays) where every key is known in advance.
- Older GCC 7/8 C++17 codebases that already use iod symbols and metamaps and want struct binding without a DOM.
- Binaries that must stay small for a handful of message types: the README claims up to 8x smaller code than nlohmann/json, measured on one float-array decoder (issue #1).

## Skip it when

- Untrusted input. At HEAD, decode_stringstream never checks the buffer end, so truncated input or an unterminated string reads past the buffer. Keys of 50 or more characters write one byte past a 50-byte stack buffer, and decoding into std::string_view loops forever on any backslash. lithium fixed these in 2026; metajson never got the fixes.
- Numbers you need exactly. Values between -1 and 0 decode as positive (-0.5 becomes 0.5), and li::json still has the same sign logic. The integer part of a float is parsed into an int and overflows past about 2.1e9. Exponents or fractional-digit counts of 18 or more hit a zero power of ten (1.5e-20 gives inf, 1e20 gives 0). '1e+5' is rejected. Floats are encoded with the default 6-digit ostream precision.
- JSON from other producers or evolving schemas. Any key not in the schema fails the whole decode ('Unknown json key'). There is no true/false/null support (bool is written and read as 1/0). std::variant uses a custom {"idx":N,"value":...} wrapper, and std::map is not supported (issue #9, still open).
- Dynamic or schema-less documents such as config files or arbitrary API payloads: there is no DOM or generic value type at all.
- Current libc++ toolchains (Apple Clang, recent LLVM): the headers include &lt;experimental/tuple&gt;, which libc++ no longer ships, and nobody has maintained the code since 2019.

## How it is fast

The schema is a compile-time template expression (one type per symbol, plus metamaps), so the decoder writes each value straight into the target member and the encoder walks the fields without building a tree; key lookup is a linear strncmp over the schema's members. Input is read through a pointer-bumping decode_stringstream over a string_view, and numbers use hand-rolled digit-accumulation parsers (integer part, fractional part divided by a power of ten, power-of-ten exponent) instead of strtod. Part of the gap to the baselines is work it skips: no buffer-end checks, no correctly rounded float parsing, and no skipping of unknown keys.

## Compared with alternatives

glaze and reflect-cpp handle the same typed struct-binding workload, publish multi-document benchmarks (the catalog lists about 3.7x round-trip and about 2x over RapidJSON respectively), support full JSON literals and are maintained, so prefer them for real use. Pick metajson only to read a compact compile-time-schema decoder; if you like its API, use its continuation li::json (lithium_json.hh) instead.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | The single header libraries/metajson/metajson.hh (last regenerated 2018-07) needs only the standard library. The modular headers at HEAD need the iod/symbol and iod/metamap headers from iodcpp/iod. The benchmarks need Google Benchmark, RapidJSON and nlohmann/json. |
| **Minimum toolchain** | C++17 (-std=c++1z). The README lists GCC 7.1.1 and Clang 5.0.1. The code needs &lt;experimental/tuple&gt; (std::experimental::apply), which libstdc++ still ships and current libc++ does not. MSVC is not documented. |
| **Platforms** | any (README: no architecture-specific code). Input must be a contiguous buffer (std::string, string_view or const char\*); std::istream input is not supported. |
| **Thread safety** | Not documented. Parser and encoder state is per call and the headers hold no mutable globals, so concurrent calls on different objects look safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- Encoding copies: json_object_base::encode(O obj) and impl::json_encode(C&, O obj, ...) take the object by value, so every encode copies the struct, including each element of a vector of structs. Every std::string is also copied into a std::stringstream before escaping.
- make_json_error, json_no_error and detect_encoding are non-inline functions defined in the header, so including metajson in more than one .cc file of the same binary gives duplicate-symbol link errors.
- Every failed decode leaks memory: the parser allocates its error std::stringstream with new and never frees it (li::json later switched to unique_ptr).
- Packaging drift: the README's install URL (raw.githubusercontent.com/iodcpp/metajson/master/metajson.hh) returns 404 since the 2019 'Prepare the merge' commit moved everything under libraries/metajson/. That single header is older than the 2019 modular headers, and the repo also carries committed a.out binaries and a 52 MB nlohmann_json.hpp.gch.

## Known shortcomings

- The README says its numbers are not from a comprehensive benchmark; benchmark code exists but no results, hardware or compiler are published. Abandoned since 2019-11; the code lives on in matt-42/lithium.
- Unsafe on untrusted input: no buffer-end checks, a 50+ character key overflows a fixed buffer, string_view decoding loops forever on a backslash, keys match by prefix. Wrong numbers: -0.5 decodes as 0.5, integer parts overflow past \~2.1e9, exponents of 18+ give 0 or inf, 1e+5 rejected, floats written at 6 digits. No true/false/null, no std::map; non-inline header functions break multi-file builds; &lt;experimental/tuple&gt; is gone from current libc++. The author conceded 'being fair was not the goal' (#1). Use lithium's li::json (fixes these) or glaze/reflect-cpp.

## Caveats and trade-offs

The author says the numbers are not from a comprehensive benchmark and are only a rough idea that 'does not take into account the fact that other libraries provides more features'. Benchmark sources (simple_json.cc, decode_float_array\*.cc, decode_int_array.cc, canada.cc) are public but use tiny inputs (a 3-field object, a 60-float array), and no results table or hardware is published. The library only handles JSON whose structure is known at compile time. There have been no commits since 2019-11-26 (last message 'Prepare the merge.'), and the code lives on in matt-42/lithium as li::json, whose docs carry the same claim. The MIT LICENSE sits in libraries/metajson/, so the GitHub API reports no license at the repo root.

Only handles JSON objects whose structure is known at compile time (no dynamic/schema-less JSON); no explicit error reporting for malformed JSON; also claims up to 8x smaller binaries than nlohmann/json and 2x smaller than RapidJSON

## Maintenance

Abandoned since 2019-11-26 and MIT-licensed; the code moved into matt-42/lithium as li::json, which is still maintained (last push 2026-07-31) and received 2026 bounds-checking and security fixes that metajson never got, so metajson is small enough to vendor but only after you fix the parser bugs above.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README states 'Up to 9x faster than nlohmann/json and 2x faster than rapidjson' and adds that the numbers are 'not given by an comprehensive benchmark'. Google Benchmark sources exist (libraries/metajson/benchmarks, CMake flags -O3 -march=native), but no results, CPU or compiler used for the figures are published, so this is first-party evidence without methodology: tier C.
- **Verifier notes:** The record is accurate. The GitHub API license is null because the LICENSE file sits in libraries/metajson/ rather than the repo root; the file is MIT, so license and usability stand. An actively maintained successor exists at https://github.com/matt-42/lithium (MIT, \~1.4k stars, pushed 2026-07-31), which the orchestrator may want to cross-reference.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/README.md>
  - <https://github.com/iodcpp/metajson>
  - <https://api.github.com/repos/iodcpp/metajson>
  - <https://api.github.com/repos/iodcpp/metajson/commits?per_page=1>
  - <https://api.github.com/repos/iodcpp/metajson/languages>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/LICENSE>
  - <https://github.com/iodcpp/metajson/tree/master/libraries/metajson/benchmarks>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/benchmarks/CMakeLists.txt>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/benchmarks/simple_json.cc>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/benchmarks/decode_float_array.cc>
  - <https://api.github.com/repos/matt-42/lithium>
  - <https://github.com/matt-42/lithium/blob/master/docs/json.cc>
- **Sources the enricher read:**
  - <https://github.com/iodcpp/metajson>
  - <https://api.github.com/repos/iodcpp/metajson/git/trees/HEAD?recursive=1>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/README.md>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/LICENSE>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/CMakeLists.txt>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/metajson.hh>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/metajson/metajson.hh>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/metajson/decoder.hh>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/metajson/encoder.hh>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/metajson/decode_stringstream.hh>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/metajson/unicode.hh>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/metajson/utils.hh>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/metajson/error.hh>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/metajson/symbols.hh>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/make_single_header.py>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/release.sh>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/bug.cc>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/tests/decode.cc>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/tests/encode.cc>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/tests/number_parser.cc>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/tests/readme.cc>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/benchmarks/CMakeLists.txt>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/benchmarks/fetch_competitors.sh>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/benchmarks/simple_json.cc>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/benchmarks/decode_float_array.cc>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/benchmarks/decode_int_array.cc>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/benchmarks/canada.cc>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/benchmarks/miloyip.cc>
  - <https://github.com/iodcpp/metajson/blob/master/libraries/metajson/benchmarks/parse_float.cc>
  - <https://api.github.com/repos/iodcpp/metajson/issues?state=all>
  - <https://github.com/iodcpp/metajson/issues/1>
  - <https://github.com/iodcpp/metajson/issues/6>
  - <https://github.com/iodcpp/metajson/issues/9>
  - <https://github.com/iodcpp/metajson/issues/10>
  - <https://github.com/iodcpp/metajson/issues/11>
  - <https://github.com/iodcpp/metajson/issues/12>
  - <https://github.com/iodcpp/metajson/issues/13>
  - <https://api.github.com/repos/iodcpp/metajson/commits?per_page=100>
  - <https://github.com/iodcpp/metajson/commit/24044a14188a7514a9d02a3402309cd9e18de16c>
  - <https://raw.githubusercontent.com/iodcpp/metajson/master/metajson.hh>
  - <https://github.com/matt-42/lithium>
  - <https://api.github.com/repos/matt-42/lithium/git/trees/HEAD?recursive=1>
  - <https://api.github.com/repos/matt-42/lithium/commits?per_page=12>
  - <https://github.com/matt-42/lithium/blob/master/libraries/json/README.md>
  - <https://github.com/matt-42/lithium/blob/master/docs/json.cc>
  - <https://github.com/matt-42/lithium/blob/master/libraries/json/json/decoder.hh>
  - <https://github.com/matt-42/lithium/blob/master/libraries/json/json/decode_stringstream.hh>
  - <https://github.com/matt-42/lithium/security/advisories/GHSA-cv26-62rq-922g>
  - <https://github.com/llvm/llvm-project/tree/main/libcxx/include/experimental>
  - <https://github.com/gcc-mirror/gcc/blob/master/libstdc++-v3/include/experimental/tuple>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/iodcpp/metajson`) · [data/wave4/enrich/raw/github_com_iodcpp_metajson.json](../../../data/wave4/enrich/raw/github_com_iodcpp_metajson.json) (enrichment confidence 0.8)

</details>
