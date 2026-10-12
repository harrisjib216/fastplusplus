# libJSON (IgnacioPomar)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Unlicense` · 🟢 active

> Learning-project C++17 JSON DOM (shared_ptr nodes) that parses and walks 1.25-1.42x faster than nlohmann/json in its author's benchmark.

| | |
|---|---|
| **Beats** | nlohmann/json |
| **Claimed result** | Read faster than nlohmann/json at every size tested: \~1.25x (small, 21.1us vs 26.4us), \~1.42x (medium, 2632.2us vs 3737.0us), \~1.38x (large, 19772.3us vs 27254.9us) (derived from page data); loses on write, and loses to RapidJSON/simdjson/glaze on both read and write |
| **Workload** | Read (parse + walk full DOM) and write (build DOM + serialize) of random-walk OHLC minute-candle JSON at three sizes (10, 1,440 and 10,080 candles), minimum time over 30 rounds. |
| **Metric** | latency |
| **Compiler and flags** | Not stated with the results; benchmarks/CMakeLists.txt defaults to CMAKE_BUILD_TYPE=Release (benchmark executable C++20, libJSON built as C++17 static lib); nlohmann_json 3.12.0, rapidjson cci.20250205, simdjson 4.6.3, glaze 2.9.5 via Conan |
| **Adoption** | 0 stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/IgnacioPomar/libJSON) · [benchmark](https://github.com/IgnacioPomar/libJSON/blob/main/README.md#how-does-it-compare) |

## Verdict

The author's harness took the minimum of 30 sequential rounds in a CMake Release build with nlohmann/json 3.12.0 from Conan; compiler, flags and CPU are not stated. Parsing a random-walk OHLC document and walking the full DOM to sum open/high/low/close took libJSON 21.1 vs 26.4 us (10 candles), 2,632.2 vs 3,737.0 us (1,440) and 19,772.3 vs 27,254.9 us (10,080) against nlohmann/json. Caveat: each library parses its own writer's output. libJSON reads six-decimal doubles (about 10 characters each), while nlohmann/json reads its Grisu2 shortest-round-trip dump (about 17-18 characters for these values, roughly a third more bytes by my estimate), so part of the gap may come from input size rather than parser speed.

## Use it when

- Reading small, trusted, machine-generated JSON: configs, or a few thousand records of plain ASCII strings, 32-bit ints and doubles, where you want error codes instead of exceptions and no dependencies
- Projects that need public-domain (Unlicense) code, can vendor six .cpp files, and would otherwise use nlohmann/json only to parse and walk a DOM
- Code ported from Java's org.json that should keep the same put/get shape in C++17
- Learning or teaching how a shared_ptr/virtual-dispatch DOM compares with arena- and variant-based DOMs; the repo includes a harness comparing five libraries

## Skip it when

- Anything where speed matters beyond beating nlohmann/json. In the author's own tables, RapidJSON, simdjson (DOM) and glaze json_t read 2-7x faster. libJSON is also the slowest writer, e.g. 32,568.2 vs 21,225.0 us against nlohmann/json on 10,080 candles
- Untrusted or arbitrary input. There is no conformance test suite and no nesting-depth limit in the recursive parser, bytes after the root value are not checked, and an integer outside 32-bit int makes std::stoi throw std::out_of_range even though the API reports errors by code
- Anywhere you need a faithful round-trip. Doubles are written with std::to_string at six fixed decimals, so 1e-7 is written as 0.000000. Strings and keys are written without escaping, so a value that contains a quote or backslash produces invalid JSON
- Editing documents in place. There is no public way to overwrite or remove a field, and put() silently keeps the old value; the author's own usability annex points this out
- Objects with many keys. Each insert checks for a duplicate by linear scan and get() is linear, so building a large object costs O(n^2) and each lookup costs O(n)

## How it is fast

Nothing exotic here. The parser is a hand-written, single-pass recursive-descent parser over a NUL-terminated char\*. Objects are a flat std::vector&lt;std::pair&lt;std::string, shared_ptr&gt;&gt; searched by linear scan, and arrays are a std::vector&lt;shared_ptr&gt;. The author credits the read win to the 2026-09-22 switch to these vectors from the earlier unordered_map and list containers, while nlohmann/json stores objects in std::map by default. Serialization appends every node into one caller-owned buffer (appendTo). Each value is still its own make_shared heap node reached through virtual dispatch, which is why this was the slowest writer tested.

## Compared with alternatives

Choose it over Boost.JSON, jsoncons or cJSON, which also beat nlohmann/json in their catalogued benchmarks (Boost.JSON by \~3.3-3.5x on citm_catalog parse), only if you specifically want Unlicense code with a Java org.json-style API and error codes, and your inputs are small and trusted. For speed, conformance or editing, glaze, simdjson or yyjson are better picks; the author says he would use glaze himself.

## Integration

| | |
|---|---|
| **Form** | static lib (a shared build is optional via Conan -o shared=True / BUILD_SHARED_LIBS) |
| **Dependencies** | none for the library; GoogleTest (via Conan) only for tests. The documented build uses CMake &gt;= 3.21 and Conan 2.x, but the six .cpp files can be vendored directly |
| **Minimum toolchain** | C++17 (the Conan recipe enforces cppstd 17); CMake 3.21+. No compiler versions are documented. Commit history targets Visual Studio 2017-2022, and the dev container uses GCC 12 on Debian 12 |
| **Platforms** | any platform with a C++17 standard library (portable scalar code, no SIMD); only Windows/MSVC and Linux/GCC are evidenced in the repo |
| **Thread safety** | not documented. The containers have no synchronization, and copies alias the same storage, so mutating through any copy while another thread reads is a data race |
| **Drop-in for the baseline** | no |

## Gotchas

- Escape decoding is wrong: \n, \t, \r, \b and \f are stored as the plain letters n, t, r, b and f (JSONParser.cpp getStr). \uXXXX is decoded one code unit at a time, so UTF-16 surrogate pairs such as emoji are not combined, and the conversion uses std::wstring_convert, which has been deprecated since C++17
- A number with an exponent but no fraction (1e5, 2E-3) is rejected with BAD_FORMAT_UNEXPECTED_VALUE, because the exponent is only parsed after a '.'
- Copying a JSONObject or JSONArray shares its storage, which the author documents as a feature. Mutating a copy changes the original, and put(obj) stores a live handle rather than a snapshot
- You must pick the root type before parsing (JSONObject or JSONArray), so a scalar or unknown-type root is unsupported. Parsing into a non-empty object appends to it, get() on a missing key allocates a fresh null node, and JSONArray::get(idx) has no bounds check

## Known shortcomings

- Read-side only: about 1.25-1.42x faster than nlohmann/json at reading, but slower at writing; the author says they would pick glaze. No compiler, flags or CPU stated. 0 stars. Unlicense gives no patent grant.
- The read benchmark feeds each library its own writer's output: libJSON's six-decimal doubles are about 1.3-1.4x shorter than nlohmann's round-trip doubles, close to the claimed 1.25-1.42x win. Parser turns \n, \t etc. into plain letters, rejects 1e5, throws std::out_of_range on 64-bit integers; the serializer does not escape strings and writes doubles with %f (1e-7 becomes 0.000000). O(n^2) object building; no CI or conformance tests.

## Caveats and trade-offs

Self-described learning project, solo author, 0 stars. The repo dates from 2021; the benchmarks and the vector-based containers behind the read win were added 2026-09-22. No CPU model, compiler or flags are stated for the numbers. The results table is in the root README, and the methodology and usability annex are in the Spanish benchmarks/README.md, which has no numbers. It loses on write: nlohmann/json is faster at every size (34.0 vs 21.0 us, 4,388.1 vs 3,042.3 us, 32,568.2 vs 21,225.0 us). It also loses to RapidJSON, simdjson (DOM) and glaze json_t on both read and write. The author says he would pick glaze for real use and praises RapidJSON. The win over nlohmann/json (1.25x-1.42x read) is modest. The README documents that libJSON has no public API for modifying an existing field. Unlicense public-domain dedication, so there is no patent grant.

Every JSON node is its own heap allocation via shared_ptr (one make_shared per value), making it the slowest of the four libraries tested at writing; author explicitly built it as a C++17/shared_ptr learning exercise, not for production use; loses to RapidJSON, simdjson and glaze on every measured workload and only beats nlohmann/json.

## Maintenance

All recent activity is a one-day burst on 2026-09-22 (CMake/Conan build, GoogleTest, benchmarks, vector containers) after no commits since April 2024. It is Unlicense and only six .cpp files, so it is easy to vendor, but it is a self-described learning project with 0 stars, no CI and no external issues or PRs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The benchmark code is public and symmetric: benchmarks/src/main.cpp plus the per-library adapters bench_libjson.cpp and bench_nlohmann.cpp, both of which parse the text and walk the full DOM, summing open/high/low/close. The build is CMake Release with nlohmann_json 3.12.0 from Conan. No compiler, flags or CPU model is stated with the results, so this is first-party partial methodology: C.
- **Verifier notes:** The record's benchmark_url (benchmarks/README.md) holds only the Spanish methodology and usability annex, with no numbers. The exact read figures (21.1/26.4, 2,632.2/3,737.0, 19,772.3/27,254.9 us, minimum over 30 rounds) are in the root README's 'How does it compare?' section, so I repointed benchmark_url there. The derived ratios 1.25x/1.42x/1.38x check out. Metadata was verified via gh: Unlicense (OSI-approved, so copyable stays), not a fork or archived, 0 stars, last commit 2026-09-22 (active).
- **Fields the verifier corrected:** `benchmark_url`, `compared_against_cpp_std_directly`, `stars_or_usage`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/IgnacioPomar/libJSON>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/benchmarks/README.md>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/README.md>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/benchmarks/src/main.cpp>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/benchmarks/src/bench_common.h>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/benchmarks/src/bench_libjson.cpp>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/benchmarks/src/bench_nlohmann.cpp>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/benchmarks/conanfile.txt>
- **Sources the enricher read:**
  - <https://github.com/IgnacioPomar/libJSON>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/README.md>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/benchmarks/README.md>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/benchmarks/conanfile.txt>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/benchmarks/src/main.cpp>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/benchmarks/src/bench_common.h>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/benchmarks/src/bench_libjson.cpp>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/benchmarks/src/bench_nlohmann.cpp>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/benchmarks/src/candle_data.h>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/benchmarks/src/candle_data.cpp>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/include/libJSON.h>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/include/libJSON_cfg.h>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/include/JSONBase.h>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/include/JSONBasicTypes.h>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/include/JSONObject.h>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/include/JSONArray.h>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/include/JSONParser.h>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/include/JSONParserPriv.h>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/include/JSONParseUchar.h>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/src/JSONParser.cpp>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/src/JSONObject.cpp>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/src/JSONArray.cpp>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/src/JSONBase.cpp>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/src/JSONBasicTypes.cpp>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/src/JSONParseUchar.cpp>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/src/CMakeLists.txt>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/CMakeLists.txt>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/conanfile.py>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/devLinks.txt>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/.devcontainer/Dockerfile>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/test_package/example.cpp>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/test/CMakeLists.txt>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/test/src/001_CreateJSON.cpp>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/test/src/002_parseJSON.cpp>
  - <https://github.com/IgnacioPomar/libJSON/blob/main/test/src/003_parseTypesJSON.cpp>
  - <https://github.com/IgnacioPomar/libJSON/commits/main>
  - <https://github.com/IgnacioPomar/libJSON/issues?q=is%3Aissue%20OR%20is%3Apr>
  - <https://github.com/IgnacioPomar/libJSON/actions>
  - <https://github.com/nlohmann/json>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/ignaciopomar/libjson`) · [data/wave4/enrich/raw/github_com_ignaciopomar_libjson.json](../../../data/wave4/enrich/raw/github_com_ignaciopomar_libjson.json) (enrichment confidence 0.75)

</details>
