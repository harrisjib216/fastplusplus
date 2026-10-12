# json.cpp

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Lean C++11 JSON parser/serializer beating nlohmann::json 2-3x on parse/round-trip latency and compile time.

| | |
|---|---|
| **Beats** | nlohmann::json (nlohmann::ordered_json) |
| **Claimed result** | README says '2x-3x faster' and that parsing the json_test.cpp example was '3x faster' than nlohmann. Benchmark table (ns, 2000x each), json.cpp vs nlohmann::ordered_json: object_test 71 vs 202, deep_test 226 vs 659, parse_test 675 vs 1928, round_trip_test 1309 vs 4258, json_test_suite 10462 vs 16617, i.e. \~2.8x / 2.9x / 2.9x / 3.25x / 1.6x (derived from page data). README also claims '10x' faster compile (\~120 ms vs &gt;=1200 ms) and '10x less code' (json.h 233 + json.cpp 1,303 lines vs nlohmann json.h 24,766 lines). |
| **Workload** | Parsing and serializing JSON test fixtures (object_test, deep_test, parse_test, round_trip_test, json_test_suite), each run 2000x, comparing json.cpp to nlohmann::ordered_json |
| **Metric** | latency |
| **Hardware** | AMD Ryzen Threadripper PRO 7995WX |
| **Compiler and flags** | gcc -O3, version 13.2, Ubuntu 24.04 |
| **Adoption** | 796 stars |
| **Last commit** | 2026-04-08 |
| **Links** | [repository](https://github.com/jart/json.cpp) · [benchmark](https://github.com/jart/json.cpp/blob/main/README.md) |

## Verdict

On gcc 13.2 -O3 (Ubuntu 24.04, AMD Ryzen Threadripper PRO 7995WX), json.cpp's own benchmark (2000 runs per fixture) reports roughly 2.8x-3.25x lower latency than nlohmann::ordered_json on object/deep/parse/round-trip micro-tests and about 1.6x on a locally modified json_test_suite run; this is a first-party, single-machine result with no independent reproduction found.

## Use it when

- Hot-path JSON parse/serialize where nlohmann::json's per-value overhead or header compile cost is the bottleneck
- Projects that can tolerate std::map key-ordered (not insertion-ordered) JSON objects
- Contexts where vendoring a small source-drop (json.h/json.cpp + double-conversion) beats pulling in a large header-only library
- Need accurate float32 round-tripping (e.g. embeddings served over HTTP) without upcasting to double
- C++11-only or less common toolchains/architectures: CI covers gcc/Ubuntu, ppc64le, s390x (via QEMU), macOS, and MSVC 2022

## Skip it when

- Need nlohmann::json's feature surface: JSON Pointer, SAX interface, custom (de)serializers, CBOR/MessagePack/BSON, or ordered_json's true insertion-order objects
- Need a widely audited, battle-tested parser; json.cpp has 796 stars and has been public only since late 2024, versus nlohmann's much longer track record
- Can't accept abort() as a possible outcome of a type-mismatch getter call in exception-disabled builds
- Can't take on Google double-conversion as a build dependency (vendored, but still required)
- Need independently reproduced numbers: the benchmark is first-party, single-machine, and the README itself flags an unexplained 39x result on the unmodified json_test_suite case

## How it is fast

Speed comes from a small, allocation-conscious value type (a union of primitive/std::string/vector/map with no std::variant or type-erasure layer) and a direct byte-level recursive-descent parser that walks raw char pointers guided by a precomputed 256-entry classification table (kJsonStr) instead of stream or iterator abstractions. Float/double-to-string conversion is offloaded to Google's double-conversion library rather than the locale-aware sstream/strtod paths nlohmann and the STL use. The small overall code size (233 + 1,303 lines) also keeps compile times and instruction-cache pressure down versus nlohmann's single \~24,766-line header.

## Compared with alternatives

Among the nlohmann-beating siblings, pick json.cpp over utl::json when you want a much smaller (233+1,303-line) source drop instead of a header-only library and don't need utl::json's wider UTL ecosystem. If the workload needs SIMD-scale throughput on large documents rather than a 2-3x win over nlohmann on small/medium fixtures, look at a simdjson/yyjson-class parser instead (see DAW JSON Link's or Tachyon.JSON's comparisons).

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Google double-conversion (vendored in-repo under double-conversion/) |
| **Minimum toolchain** | C++11 (CMAKE_CXX_STANDARD 11 in CMakeLists.txt); builds with GCC, Clang/AppleClang, and MSVC 2022 per CI |
| **Platforms** | x86-64, ppc64le, s390x (CI via QEMU), macOS, Windows (MSVC) — no SIMD requirement |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — similar is\*/get\*/operator[] API shape to nlohmann, but parse() returns a Status/Json pair instead of throwing, type-mismatch getters abort() or throw std::logic_error (not nlohmann::type_error), and std::map-backed objects sort by key instead of preserving insertion order like the ordered_json baseline it's benchmarked against |

## Gotchas

- Object keys are stored in std::map, so iteration/serialization order is alphabetical, not insertion order — a real behavioral difference from the ordered_json baseline used in its own benchmark
- Getter type mismatches call abort() by default, or throw std::logic_error instead if __cpp_exceptions/__EXCEPTIONS/_CPPUNWIND is defined at compile time (json.cpp, ON_LOGIC_ERROR macro)
- The headline json_test_suite benchmark number (\~1.6x/3x) comes from a locally modified version of that test that keeps only the passing cases; the README states the unmodified test shows a 39x gap the authors 'haven't figured out how to explain yet'
- Requires Google double-conversion at build time; it's vendored in the repo (not a git submodule) so no separate fetch is needed, but it is a hard link dependency

## Caveats and trade-offs

First-party 'quick and dirty' benchmark run by the author on the author's hardware; no independent reproduction found. Compiler/CPU are stated in the README intro bullet, not next to the table. json_test_suite() was changed locally to include only the successful cases; the README says the unmodified test shows a 39x (not 3x) advantage for json.cpp that the authors 'haven't figured out how to explain yet'. Needs Google double-conversion as a dependency.

Far smaller feature/API surface than nlohmann::json (233 vs \~24.7k lines); newer and much less battle-tested; API is not drop-in compatible with nlohmann's

## Maintenance

Actively maintained (last commit 2026-04-08, 796 stars, 3 open issues), Apache-2.0 licensed and small enough to vendor, but young (public since late 2024) and far less battle-tested than nlohmann::json.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** README 'Benchmark Results' table compares json.cpp to nlohmann::ordered_json. The benchmark code is public (json_test.cpp BENCH(2000, ...) macro and nlohmann/json_test.cpp), and the README states gcc 13.2 -O3 on Ubuntu 24.04 with an AMD Ryzen Threadripper PRO 7995WX, so it meets A.
- **Verifier notes:** Speed numbers match the README exactly. I fixed claimed_speedup because the record's '\~100x fewer source lines' counted only json.h (233 lines) against nlohmann's json.h; the README itself says 10x, since json.cpp adds 1,303 lines. GitHub reports the license as NOASSERTION, but the LICENSE file is Apache-2.0 text (Mozilla, 2024), so the record's license is correct.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/jart/json.cpp>
  - <https://github.com/jart/json.cpp/blob/main/README.md>
  - <https://github.com/jart/json.cpp/blob/main/LICENSE>
  - <https://github.com/jart/json.cpp/blob/main/json_test.cpp>
  - <https://github.com/jart/json.cpp/tree/main/nlohmann>
- **Sources the enricher read:**
  - <https://github.com/jart/json.cpp>
  - <https://github.com/jart/json.cpp/blob/main/README.md>
  - <https://github.com/jart/json.cpp/blob/main/json.h>
  - <https://github.com/jart/json.cpp/blob/main/json.cpp>
  - <https://github.com/jart/json.cpp/blob/main/CMakeLists.txt>
  - <https://github.com/jart/json.cpp/blob/main/.github/workflows/ubuntu.yml>
  - <https://github.com/jart/json.cpp/blob/main/.github/workflows/macos.yml>
  - <https://github.com/jart/json.cpp/blob/main/.github/workflows/msvc.yml>
  - <https://github.com/jart/json.cpp/blob/main/json_test.cpp>
  - <https://github.com/jart/json.cpp/issues/12>
  - <https://github.com/jart/json.cpp/issues>
  - <https://github.com/jart/json.cpp/tree/main/double-conversion>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/jart/json.cpp`) · [data/wave1/enrich/raw/github_com_jart_json_cpp.json](../../../data/wave1/enrich/raw/github_com_jart_json_cpp.json) (enrichment confidence 0.7)

</details>
