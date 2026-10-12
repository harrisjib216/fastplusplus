# reflect-cpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++20 reflection serializer that reads JSON into structs through embedded yyjson; claims \~2x hand-written RapidJSON, \~10x nlohmann/json.

| | |
|---|---|
| **Beats** | RapidJSON, nlohmann/json |
| **Claimed result** | Benchmarks README: 'reflect-cpp is consistently faster than RapidJSON, usually about twice as fast' and 'consistently about 10 times faster than nlohmann/json'; also states reflect-cpp is 'slightly slower than the fastest JSON libraries for C and C++, namely simdJSON and yyjson' because its JSON backend is built on yyjson |
| **Workload** | Read-only benchmark (parse JSON into typed C++ structs) on three datasets: canada (float-heavy), licenses (nested, string-heavy) and person (small). It compares reflect-cpp (yyjson backend, one-line rfl::json::read) against hand-written nlohmann/json, RapidJSON, simdjson (skipped on clang) and yyjson code with Google Benchmark (benchmarks/json/\*.cpp). Writes are benchmarked only in the separate cross-format suite (benchmarks/all). |
| **Metric** | throughput |
| **Hardware** | Not stated on the page; the CI benchmark jobs run on GitHub-hosted ubuntu-24.04 runners (CPU model not stated) |
| **Compiler and flags** | benchmarks/CMakeLists.txt sets -std=c++20 -Wall -O2 (MSVC: -std:c++20 -O2) and the README builds with -DCMAKE_BUILD_TYPE=Release. The README's 'gcc 11.4 on Ubuntu 22.4' note applies only to the depicted cross-format charts. The JSON-library comparison runs in CI (.github/workflows/linux.yaml 'benchmarks' jobs, gcc 11-14 and clang 16-18), with results written only to GitHub Actions job step summaries. |
| **Adoption** | 1.9k stars |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/getml/reflect-cpp) · [benchmark](https://github.com/getml/reflect-cpp/blob/main/benchmarks/README.md) |

## Verdict

The project's Google Benchmark code times reads of three datasets (canada, licenses, person) into typed structs. It compares rfl::json::read (yyjson backend) with hand-written nlohmann/json, RapidJSON (default non-insitu Parse), yyjson and simdjson on-demand code (simdjson is skipped under clang), built at -O2 Release. The runs happen in GitHub Actions: ubuntu-24.04 with gcc 11-14 and clang 16-18, macOS 15 and Windows MSVC, with no CPU model given. The only published result is prose ('usually about twice as fast' as RapidJSON, 'about 10 times faster' than nlohmann/json, slightly slower than simdjson and yyjson), because per-run numbers exist only in Actions job step summaries that could not be retrieved through the API or an anonymous fetch.

## Use it when

- You now hand-write RapidJSON or nlohmann/json DOM-walking code to fill typed structs and want a one-line rfl::json::read&lt;T&gt; that the project says runs faster (its benchmark code needs about 50-90 lines per dataset for the other libraries).
- Typed configs, API payloads and records where you also want validation (rfl::Validator, rfl::Email, rfl::Timestamp), all field errors collected into one message, and generated JSON Schema (rfl::json::to_schema&lt;T&gt;).
- One struct model that must also go out as msgpack, flexbuffers, BSON, CBOR, YAML, Avro, Cap'n Proto or Parquet. The project's cross-format benchmarks rank flexbuffers, msgpack and yas fastest, ahead of JSON.
- Workloads shaped like the benchmark: float-heavy arrays such as GeoJSON (canada), nested string-heavy records (licenses), or many small objects (person), parsed from an in-memory string.
- C++20 codebases on GCC 11.4+, Clang 14+ or MSVC 17.8+ whose types are plain aggregates without user-declared constructors.

## Skip it when

- Peak parse throughput: the benchmark README says reflect-cpp is slightly slower than simdjson and yyjson used directly, so if you will hand-write the binding anyway, use those instead.
- Untyped or schema-less JSON, or editing JSON in place: the tool maps into structs. rfl::Generic exists, but open issue #368 reports rfl::to_generic running more than 10x slower than rfl::json::write.
- Very large or streaming inputs: read() parses the whole input into a yyjson DOM before it fills the struct, the istream overload first copies the whole stream into a std::string, and YYJSON_READ_INSITU is rejected. Peak memory is roughly input plus DOM plus output.
- Build-time-sensitive projects with wide structs: issue #86 reports compiles going from seconds to minutes, a need for -fconstexpr-depth=1024/2048, and a roughly 130-member struct that was 'prohibitively long' to compile. Maintainers advise putting read/write calls in their own translation unit.
- Types that are not simple aggregates in C++20 mode: custom constructors are unsupported, and C arrays and inheritance need -DREFLECT_CPP_C_ARRAYS_OR_INHERITANCE (fields must still all sit in one struct). The structured-binding path handles at most 256 fields.

## How it is fast

The parsing is done by yyjson, which is vendored as version 0.12.0 and builds an immutable DOM. The README credits yyjson for the speed. reflect-cpp then walks that DOM once with code generated per struct. In C++20 mode, field names come from structured bindings plus parsing std::source_location::function_name() at compile time; C++26 mode uses P2996 std::meta instead. Each JSON key is compared (string_view ==) against the compile-time field names in a fold expression, and each value is placement-new'd straight into an uninitialized, aligned stack buffer of T through a view of member pointers, so no struct is default-constructed first. Writes build a yyjson mutable DOM, serialize it with yyjson_mut_write_opts and copy the result into a std::string.

## Compared with alternatives

Against yyjson or simdjson: pick reflect-cpp when you want typed struct binding without writing the DOM walk and can accept the small overhead its own README admits. Against glaze, the other reflection-based C++ option: the published figures come from different benchmarks and cannot be compared (glaze \~2.9x RapidJSON read, reflect-cpp 'about twice'), so choose reflect-cpp for its wide non-JSON format list (Avro, Cap'n Proto, Parquet, BSON, etc.) and pydantic-style validators rather than for raw read speed.

## Integration

| | |
|---|---|
| **Form** | static lib (shared via REFLECTCPP_BUILD_SHARED). Also packaged for vcpkg and Conan, or as a source drop of include/ plus src/reflectcpp.cpp, src/reflectcpp_json.cpp and src/yyjson.c |
| **Dependencies** | JSON only: none external (yyjson, CTRE and enchantum are bundled). Every other format needs its own library, e.g. msgpack-c, yaml-cpp, libbson, flatbuffers, Apache Arrow or capnproto |
| **Minimum toolchain** | C++20 with GCC 11.4+, Clang 14+ or MSVC 17.8 (19.38)+ and CMake 3.23. The optional C++26 reflection mode needs GCC 16.2+ with -freflection |
| **Platforms** | Linux (CI: gcc 11-14 and clang 16-18), macOS 15 on arm64 and Intel (clang) and Windows (MSVC) all run in CI. No SIMD or ISA requirement is documented |
| **Thread safety** | not documented. Each read/write call builds its own yyjson document and Reader/Writer object, and the JSON paths reviewed show no shared mutable state |
| **Drop-in for the baseline** | partial — it replaces the struct-mapping code you write on top of RapidJSON or nlohmann/json, but offers no API compatible with RapidJSON's Document/Writer or nlohmann::json's DOM |

## Gotchas

- Open issue #719 (2026-08-27): rfl::json::read segfaults under GCC 12 at -O2 for some structs (internal linkage, an std::optional nested aggregate, 12+ fields). read_struct type-puns an unsigned char buffer as T. Workarounds reported: -fno-strict-aliasing, rfl::DefaultIfMissing, or GCC 11/14.
- Unknown JSON keys are silently ignored by default. Add the rfl::NoExtraFields processor to reject them. Missing non-optional fields are errors unless you use DefaultIfMissing.
- Errors: read returns rfl::Result and does not throw, but write() throws std::runtime_error when yyjson refuses to serialize. Open issue #421 reports Windows crashes on strings that are not UTF-8 (e.g. cp1251, some std::wstring or std::filesystem::path values).
- In C++20 mode, enums reflect only values in [-256, 256] by default. Widen the range with RFL_ENUM_RANGE_MIN/RFL_ENUM_RANGE_MAX or rfl::config::enum_range&lt;E&gt;.

## Caveats and trade-offs

The page has no measured numbers for the RapidJSON and nlohmann comparison, only the text summary ('usually about twice as fast', 'about 10 times faster'). The PNG charts in benchmarks/img compare reflect-cpp's own formats (flexbuf, msgpack, bson, json, cbor, toml, yaml, xml) against each other, not against other JSON libraries. Per-run numbers exist only in GitHub Actions job step summaries, which are not in the job logs. No CPU model is given. The comparison is first-party, and reflect-cpp's JSON speed comes from its embedded yyjson backend; the README says it is slightly slower than simdjson and yyjson.

reflect-cpp's JSON path is a thin reflection layer over yyjson, so its speed advantage is really 'yyjson plus near-zero-overhead reflection' vs hand-written RapidJSON/nlohmann code; requires C++20 reflection features; exact numeric results are only published as chart images in CI artifacts, not as text tables in the repo.

## Maintenance

Actively maintained by getML (Code17 GmbH): last commit 2026-09-22, v0.25.0 released 2026-05-16, \~1.9k stars. MIT-licensed and available through vcpkg and Conan, so it is easy to adopt, though GCC 12 users should note open issue #719.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party benchmarks README states in text only that reflect-cpp is 'usually about twice as fast' as RapidJSON and 'about 10 times faster' than nlohmann/json, with no measured values. The public benchmark code (benchmarks/json/{canada,licenses,person}.cpp, Google Benchmark vs nlohmann, RapidJSON, simdjson and yyjson) runs only in CI, whose results sit in job step summaries, and no CPU model is given, so the tier is C.
- **Verifier notes:** The claimed_speedup quotes are accurate. The record's caveat was wrong that the PNG charts show the RapidJSON and nlohmann results: they are cross-format charts. Metadata checks out: MIT, 1,937 stars, last commit 2026-09-22, not archived, not a fork. rfl.getml.com/benchmarks repeats the same text claims, also without numbers.
- **Fields the verifier corrected:** `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/getml/reflect-cpp/blob/main/benchmarks/README.md>
  - <https://github.com/getml/reflect-cpp>
  - <https://github.com/getml/reflect-cpp/blob/main/benchmarks/json/canada.cpp>
  - <https://github.com/getml/reflect-cpp/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/getml/reflect-cpp/blob/main/.github/workflows/linux.yaml>
  - <https://raw.githubusercontent.com/getml/reflect-cpp/main/benchmarks/img/canada_read.png>
  - <https://raw.githubusercontent.com/getml/reflect-cpp/main/benchmarks/img/licenses_read.png>
  - <https://rfl.getml.com/benchmarks>
  - <https://github.com/getml/reflect-cpp/actions/runs/35785689216>
- **Sources the enricher read:**
  - <https://github.com/getml/reflect-cpp>
  - <https://github.com/getml/reflect-cpp/blob/main/README.md>
  - <https://github.com/getml/reflect-cpp/blob/main/benchmarks/README.md>
  - <https://github.com/getml/reflect-cpp/blob/main/benchmarks/json/canada.cpp>
  - <https://github.com/getml/reflect-cpp/blob/main/benchmarks/json/licenses.cpp>
  - <https://github.com/getml/reflect-cpp/blob/main/benchmarks/json/CMakeLists.txt>
  - <https://github.com/getml/reflect-cpp/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/getml/reflect-cpp/blob/main/include/rfl/json/Reader.hpp>
  - <https://github.com/getml/reflect-cpp/blob/main/include/rfl/json/read.hpp>
  - <https://github.com/getml/reflect-cpp/blob/main/include/rfl/json/write.hpp>
  - <https://github.com/getml/reflect-cpp/blob/main/include/rfl/json/Writer.hpp>
  - <https://github.com/getml/reflect-cpp/blob/main/include/rfl/parsing/ViewReader.hpp>
  - <https://github.com/getml/reflect-cpp/blob/main/include/rfl/parsing/Parser_default.hpp>
  - <https://github.com/getml/reflect-cpp/blob/main/include/rfl/internal/get_field_names.hpp>
  - <https://github.com/getml/reflect-cpp/blob/main/include/rfl/internal/cpp20/get_field_names.hpp>
  - <https://github.com/getml/reflect-cpp/blob/main/include/rfl/internal/cpp20/bind_to_tuple.hpp>
  - <https://github.com/getml/reflect-cpp/blob/main/include/rfl/internal/cpp20/num_fields.hpp>
  - <https://github.com/getml/reflect-cpp/blob/main/include/rfl/thirdparty/yyjson.h>
  - <https://github.com/getml/reflect-cpp/blob/main/CMakeLists.txt>
  - <https://github.com/getml/reflect-cpp/blob/main/docs/content/install.md>
  - <https://github.com/getml/reflect-cpp/blob/main/docs/content/structs.md>
  - <https://github.com/getml/reflect-cpp/blob/main/docs/content/c_arrays_and_inheritance.md>
  - <https://github.com/getml/reflect-cpp/blob/main/docs/content/supported_formats/json.md>
  - <https://github.com/getml/reflect-cpp/blob/main/docs/content/enums.md>
  - <https://github.com/getml/reflect-cpp/blob/main/.github/workflows/linux.yaml>
  - <https://github.com/getml/reflect-cpp/blob/main/.github/workflows/macos.yaml>
  - <https://github.com/getml/reflect-cpp/blob/main/.github/workflows/windows.yaml>
  - <https://github.com/getml/reflect-cpp/releases/latest>
  - <https://github.com/getml/reflect-cpp/issues/719>
  - <https://github.com/getml/reflect-cpp/issues/68>
  - <https://github.com/getml/reflect-cpp/issues/594>
  - <https://github.com/getml/reflect-cpp/issues/86>
  - <https://github.com/getml/reflect-cpp/issues/421>
  - <https://github.com/getml/reflect-cpp/issues?q=performance>
  - <https://github.com/getml/reflect-cpp/issues?q=slow>
  - <https://github.com/getml/reflect-cpp/issues?q=bug>
  - <https://github.com/getml/reflect-cpp/issues?q=crash>
  - <https://github.com/getml/reflect-cpp/actions/runs/35785689216>
  - <https://github.com/getml/reflect-cpp/actions/runs/35785689216/summary_partial>
  - <https://rfl.getml.com/benchmarks>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/getml/reflect-cpp`) · [data/wave4/enrich/raw/github_com_getml_reflect_cpp.json](../../../data/wave4/enrich/raw/github_com_getml_reflect_cpp.json) (enrichment confidence 0.8)

</details>
