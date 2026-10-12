# BitSerializer

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++17 multi-format struct serializer whose built-in MsgPack archive saves about 33x and loads about 22x faster than nlohmann::json's MsgPack path.

| | |
|---|---|
| **Beats** | nlohmann::json (nlohmann::json::to_msgpack / from_msgpack, DOM-based MsgPack path) |
| **Claimed result** | BitSerializer-MsgPack vs NlohmannJson-MsgPack: save to memory 86842 vs 2621 fields/ms (about 33x, derived from page data), load from memory 49254 vs 2206 fields/ms (about 22x, derived from page data). README also says the built-in JSON archive is about 40% faster than BitSerializer's own RapidJSON-based JSON archive, and that wrapped third-party formats (RapidJSON, PugiXml, RapidYAML) cost about 5% against their native APIs. |
| **Workload** | Fields per millisecond saving a C++ test model (array of objects with 10 fields each: bool, int8, uint64, float, double and five strings including long, Russian Unicode, escaped and multi-line values) to an in-memory std::string and loading it back, MsgPack format; best (minimum) time over a 30 second window per stage, thread pinned to one core. |
| **Metric** | throughput |
| **Adoption** | 34 stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/PavelKisliak/BitSerializer) · [benchmark](https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/benchmark_results/serialization_speed_report.json) |

## Verdict

First-party report in benchmarks/archives (speed report last updated with the 2026-01-10 chart commit): saving a 30-object, 330-field test model (bool, int8, uint64, float, double and five strings per object) to an in-memory std::string as MsgPack ran at 86842 fields/ms with BitSerializer versus 2621 with nlohmann::json's DOM plus to_msgpack (about 33x, derived from page data), and loading at 49254 versus 2206 fields/ms (about 22x), each the minimum single-run time over a 30 s window after a 10 s CPU warm-up on one pinned core. Compiler, flags, nlohmann version and CPU are not stated; the harness validates the loaded model after each load stage, and the nlohmann JSON-text benchmark class exists but is never run.

## Use it when

- You serialize typed C++ structs to MsgPack today via nlohmann::json (struct to json DOM, then to_msgpack/from_msgpack); the committed report shows 86842 vs 2621 fields/ms on save and 49254 vs 2206 on load for that swap.
- One mapping must target several formats (JSON for debugging, MsgPack on the wire, CSV export) with named keys, fields loadable in any order, and versioning by optional or renamed fields.
- Loading needs validation and error collection (Required, MaxSize, Email, PhoneNumber, custom validators, refiners) rather than bare parsing.
- Large MsgPack, CSV or JSON inputs read from std::istream with bounded memory (built-in archives read in chunks; the RapidJSON, PugiXml and RapidYAML wrappers keep the whole document in memory).
- Cross-platform C++17 code on Windows, Linux or macOS (x86, x64, arm32, arm64) installed through vcpkg, Conan Center or CMake FetchContent.

## Skip it when

- You need to inspect or edit arbitrary JSON as a tree: there is no DOM type, only struct mapping.
- Raw binary throughput matters more than named keys and schema tolerance: positional serializers (zpp::bits, Cap'n Proto) are a different class, and no dedicated MsgPack library (msgpack-c/cpp, glaze, cereal) was ever benchmarked against it, so the README's 'best-in-class' MsgPack claim is unsupported.
- JSON, XML or YAML through the RapidJSON, PugiXml or RapidYAML wrappers: the committed report shows them 0-9% slower than the native libraries (RapidJSON load 11149 vs 11957 fields/ms, PugiXml load 13693 vs 15068), never faster; the faster built-in JSON archive is unreleased (master only) and its '40% faster' claim has no committed numbers.
- Builds with exceptions disabled: the README states that working without exceptions is not supported, and all errors (type mismatch, overflow, validation) are reported by throwing.
- Exchanging MsgPack timestamps before 1970 or after 2514 with other MsgPack implementations (timestamp 96 byte-order bug, see gotchas).

## How it is fast

The built-in MsgPack archive (like CSV and the new built-in JSON archive) is DOM-free: the writer appends type-tagged big-endian values straight into the caller's std::string, and the string reader parses the input in place and hands strings out as std::string_view, so no tree of std::map nodes and heap-allocated keys is built, which is what nlohmann::json's to_msgpack/from_msgpack path requires. Object fields are looked up with a cursor that continues from the previous key and only rewinds and skips (SkipValue) when keys arrive out of order, so loading in write order is a single linear pass. There is no SIMD or other low-level trick; each value still goes through a virtual IMsgPackWriter/IMsgPackReader call, so the gain is purely architectural (no intermediate DOM).

## Compared with alternatives

Pick BitSerializer over zpp::bits or Cap'n Proto when you need named-key, schema-tolerant formats (MsgPack, JSON, CSV, XML, YAML) from one struct mapping with validation, and over cmp when you want typed C++ struct mapping rather than a low-level C MsgPack API. For JSON throughput specifically, DAW JSON Link and json.cpp carry stronger JSON-specific evidence; BitSerializer's measured win is MsgPack against nlohmann::json only.

## Integration

| | |
|---|---|
| **Form** | static lib (default) or shared lib: each archive (msgpack-archive, csv-archive, json-archive, rapidjson-archive, pugixml-archive, rapidyaml-archive) is a compiled CMake target over a header-only core; the MsgPack docs state it is not header-only |
| **Dependencies** | none for the built-in MsgPack, CSV and JSON archives; RapidJSON, PugiXml or RapidYAML for the corresponding wrapper archives |
| **Minimum toolchain** | C++17; VS 2019, GCC 8.3+ (CMake warns below 8.3), Clang 8+, AppleClang 12, Clang-cl; CMake 3.10+ |
| **Platforms** | Windows, Linux, macOS on x86, x64, arm32, arm64 and arm64be (README) |
| **Thread safety** | not documented (each SaveObject/LoadObject call creates its own archive and reader/writer; no shared mutable state seen in the MsgPack code read) |
| **Drop-in for the baseline** | partial — the MsgPack bytes are standard, so data written by nlohmann::json::to_msgpack loads into a matching struct, but the API is different: nlohmann adl_serializer to_json/from_json code must be rewritten as Serialize() methods, and code that builds or queries nlohmann::json values has no equivalent |

## Gotchas

- MsgPack timestamp 96 is written and read in the wrong field order: CMsgPackStringWriter/CMsgPackStreamWriter emit 0xC7 0x0C 0xFF then int64 seconds then nanoseconds, and both readers expect the same, while the MsgPack spec puts the 32-bit nanoseconds before the 64-bit seconds; the unit tests ShouldWriteTimestamp96 and ShouldReadTimestamp96 encode the swapped order. It round-trips with itself but other MsgPack implementations misread std::chrono/time_t values whose seconds are negative or at least 2^34 (pre-1970, post-2514), despite docs/bitserializer_msgpack.md claiming full compliance with the Timestamp extension. This does not touch the benchmark numbers (the test model has no timestamps).
- Harness favours the DOM-free side beyond the format work itself: the output std::string is reserved to 16384 bytes and reused across iterations (the 12783-byte MsgPack output never reallocates) and CBasicTestModel's constructor pre-reserves every target string, while the nlohmann path rebuilds a std::map-based DOM per call, grows the std::vector from to_msgpack from empty and then copies it into the std::string (nlohmann's to_msgpack has an output_adapter&lt;char&gt; overload that writes into a std::string directly), and loads via a DOM although nlohmann's sax_parse supports MsgPack. Each figure is the best single run of a cache-hot \~13 KB, 30-object payload (about 3.8 us vs 126 us per save), so the 33x/22x ratios overstate gains on cold, allocation-heavy real workloads.
- Out-of-order keys cost a rescan: the object scope searches forward from the last key and rewinds with SkipValue, so loading fields in a different order than they were written turns each lookup into O(fields) skips (README: maximum performance only when loading in the same order).
- Streams are much slower than memory buffers: MsgPack save to std::ostream measured 11379 vs 86842 fields/ms to std::string (the stream writer calls put/write per value) and the RapidJSON archive 1045 vs 13636; serialize to a string and write it out in hot paths. The README also requires the application and the compiled archive libraries to share C++ standard, optimisation flags and runtime, so there is no ABI stability.

## Known shortcomings

- First-party report (MsgPack 86,842/49,254 vs nlohmann-to_msgpack 2,621/2,206 fields/ms) against a weak baseline (nlohmann DOM plus to_msgpack, no real MsgPack library compared), with no compiler, flags or CPU; the NlohmannJson-Json class exists but main.cpp never runs it; the '40% faster' built-in JSON claim has no committed numbers; other formats are at parity or slower than native libraries.
- Harness flaws behind the 33x/22x vs nlohmann: the output string is pre-reserved to 16384 bytes and reused, target strings are pre-reserved, while the nlohmann side rebuilds a std::map DOM each call, grows its to_msgpack vector from empty, copies it into a string (the output_adapter&lt;char&gt; overload is unused) and never uses sax_parse; the figure is the best single run on a cache-hot \~13 KB payload (3.8 us vs 126 us), with compiler, CPU and nlohmann version unstated. Correctness bug outside the benchmark: MsgPack timestamp 96 is written and read as seconds then nanoseconds (spec says nanoseconds first) and the unit tests lock in the swapped order, so it round-trips with itself but breaks interop for pre-1970/post-2514 times despite 'fully compliant' docs. Archives are compiled static/shared libraries, not header-only; out-of-order keys rescan with SkipValue; ostream paths are 7.6x slower (MsgPack 11379 vs 86842); wrappers are 0-9% slower than RapidJSON/PugiXml/RapidYAML; the built-in JSON archive's '40% faster' has no committed numbers; no exceptions-off support; no ABI stability.

## Caveats and trade-offs

Benchmark source is public (benchmarks/archives: main.cpp, benchmark_base.cpp, competitors/nlohmannjson_benchmark.h) but no compiler, flags or CPU model are stated anywhere in the repo or README, and the committed report JSON and chart carry no machine information, so it is a first-party result with partial methodology (tier C, not A). The only nlohmann::json row is MsgPack: competitors/nlohmannjson_benchmark.h also defines a NlohmannJson-Json (text JSON) class, but main.cpp never runs it, so there is no nlohmann JSON text row. The baseline converts the struct into a nlohmann::json DOM (whose objects are std::map nodes) and then calls to_msgpack/from_msgpack, while BitSerializer maps the struct straight to bytes; the README itself calls Serializer-vs-Parser comparisons 'not entirely fair', and the README text never quotes the nlohmann numbers (they appear only in the report JSON and chart). No dedicated MsgPack library (msgpack-c/cpp, cereal, glaze, zpp_bits) is compared, so 'best-in-class' MsgPack speed is unsupported. Correctness: the harness validates the loaded model against the source after every load stage (ValidateTargetModel), so round-trip correctness is checked, but serialized bytes are not compared across libraries and the committed output-size report (last changed 2025-05-01) has no NlohmannJson-MsgPack row. The committed speed report has no row for the new built-in JSON archive (BitSerializer::Json::JsonArchive), so the README's 'about 40% faster than the RapidJSON-based archive' claim has no committed numbers. Against RapidJSON, PugiXml and RapidYAML the BitSerializer archives are within about 5% or slightly slower, not faster (RapidJson save 14103 vs 13636, load 11957 vs 11149 fields/ms), so the speedup claim holds only for MsgPack against nlohmann. The 33x and 22x ratios are derived from the report's two numbers. Results are the minimum time per stage over a 30 s window after a 10 s CPU warm-up, which favours best-case numbers for every library equally. [retier] First-party benchmark: BitSerializer reuses a 16384-byte pre-reserved output string while the nlohmann side rebuilds a std::map DOM per call, grows to_msgpack's vector from empty and copies it, without sax_parse; best single run on a cache-hot \~13 KB payload (3.8 us vs 126 us), compiler/CPU/nlohmann version unstated. MsgPack timestamp 96 field order swapped (seconds before nanoseconds), interop bug. Archives are compiled libraries, not header-only; ostream paths 7.6x slower.

Header-style C++17 library; types need a Serialize function or KeyValue mapping per class (non-intrusive). MsgPack, CSV and the new built-in JSON archive have no external dependencies; the RapidJSON, PugiXml and RapidYAML archives pull in those libraries. Streams straight to and from the model with no intermediate DOM, so it cannot do arbitrary DOM manipulation the way nlohmann::json can.

## Maintenance

Actively developed (last commit 2026-09-30, v0.85 released 2026-01-11, built-in JSON archive only on master and set to replace the RapidJSON archive), MIT-licensed, 34 stars and 8 forks, packaged in vcpkg and Conan Center; usable now for MsgPack and CSV, but fix or avoid timestamp 96 if other MsgPack readers consume your data.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party committed report (benchmarks/archives/benchmark_results/serialization_speed_report.json) produced by the public harness in benchmarks/archives (main.cpp, benchmark_base.cpp, competitors/nlohmannjson_benchmark.h), with NlohmannJson-MsgPack save 2621 and load 2206 fields/ms versus BitSerializer-MsgPack 86842 and 49254; no compiler, flags or CPU model stated anywhere, so not A.
- **Verifier notes:** Numbers match the report exactly; the win is only against nlohmann::json's DOM-plus-to_msgpack path, a weak baseline, with no dedicated MsgPack library compared and other formats at parity or slightly slower than their native libraries. The harness does validate round-trip correctness of loaded models, so the record's 'output equivalence not checked' was softened; the nlohmann JSON text benchmark class exists but is never run, and the built-in JSON archive's '40% faster' claim has no committed numbers. Metadata confirmed: MIT, 34 stars, last commit 2026-09-30, not a fork.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party report (verifier); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/benchmark_results/serialization_speed_report.json>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/benchmark_results/serialization_output_size_report.json>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/README.md>
  - <https://github.com/PavelKisliak/BitSerializer>
  - <https://github.com/PavelKisliak/BitSerializer/tree/master/benchmarks/archives>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/main.cpp>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/benchmark_base.cpp>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/benchmark_base.h>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/test_model.h>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/competitors/nlohmannjson_benchmark.h>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/competitors/bitserializer_benchmark.h>
  - <https://github.com/PavelKisliak/BitSerializer/commits/master/benchmarks/archives/benchmark_results>
  - <https://github.com/PavelKisliak/BitSerializer/commits/master>
- **Sources the enricher read:**
  - <https://github.com/PavelKisliak/BitSerializer>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/README.md>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/docs/bitserializer_msgpack.md>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/main.cpp>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/benchmark_base.cpp>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/benchmark_base.h>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/test_model.h>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/competitors/nlohmannjson_benchmark.h>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/competitors/bitserializer_benchmark.h>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/CMakeLists.txt>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/benchmark_results/serialization_speed_report.json>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/benchmarks/archives/benchmark_results/serialization_output_size_report.json>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/include/bitserializer/msgpack_archive.h>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/include/bitserializer/serialization_detail/bin_timestamp.h>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/src/msgpack/msgpack_archive.cpp>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/src/msgpack/msgpack_readers.h>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/src/msgpack/msgpack_readers.cpp>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/src/msgpack/msgpack_writers.h>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/src/msgpack/msgpack_writers.cpp>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/src/testing_tools/perf_utils.h>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/tests/unit_tests/msgpack_tests/msgpack_writer_tests.cpp>
  - <https://raw.githubusercontent.com/PavelKisliak/BitSerializer/HEAD/tests/unit_tests/msgpack_tests/msgpack_reader_tests.cpp>
  - <https://github.com/PavelKisliak/BitSerializer/tree/master/include/bitserializer>
  - <https://github.com/PavelKisliak/BitSerializer/tree/master/src>
  - <https://github.com/PavelKisliak/BitSerializer/tree/master/src/msgpack>
  - <https://github.com/PavelKisliak/BitSerializer/tree/master/tests>
  - <https://github.com/PavelKisliak/BitSerializer/tree/master/tests/unit_tests>
  - <https://github.com/PavelKisliak/BitSerializer/tree/master/tests/unit_tests/msgpack_tests>
  - <https://github.com/PavelKisliak/BitSerializer/commits/master/benchmarks/archives/benchmark_results>
  - <https://github.com/PavelKisliak/BitSerializer/commits/master>
  - <https://github.com/PavelKisliak/BitSerializer/releases>
  - <https://github.com/PavelKisliak/BitSerializer/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/msgpack/msgpack/master/spec.md>
  - <https://raw.githubusercontent.com/nlohmann/json/develop/single_include/nlohmann/json.hpp>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/pavelkisliak/bitserializer`) · [data/wave1/enrich/raw/github_com_pavelkisliak_bitserializer.json](../../../data/wave1/enrich/raw/github_com_pavelkisliak_bitserializer.json) (enrichment confidence 0.82)

</details>
