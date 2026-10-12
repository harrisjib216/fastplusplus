# Jsonifier

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 JSON library that binds to registered structs; 1.1-1.8x simdjson ondemand read throughput on most whole documents.

| | |
|---|---|
| **Beats** | simdjson |
| **Claimed result** | Small-value tests. Each value in the file is parsed as its own tiny document (e.g. [START]true[END]). Double Test Read: 1345.06 vs simdjson 270.869 MB/s (\~5.0x). Bool Test Read: 3090.41 vs 225.22 MB/s (\~13.7x). String Test Read: 3881.15 vs 1591.5 MB/s (\~2.4x). Uint64 Test Read: 2221.44 vs 637.965 MB/s (\~3.5x). Whole-document reads are closer. Twitter (Minified): 2115.62 vs 1212.07 MB/s (\~1.75x). CitmCatalog (Minified): 1816.6 vs 1050.96 MB/s (\~1.73x). Canada (Minified): 866.14 vs 633.802 MB/s (\~1.37x). The page marks Twitter, Google Maps and Random (Prettified) as statistical ties with simdjson. Jsonifier loses Mesh (Prettified): 1918.85 vs simdjson 2113.31 MB/s (derived from page data) |
| **Workload** | Read (parse into typed C++ structs, with UTF-8 validation on for all libraries) throughput against simdjson ondemand. Glaze is the only library compared on write. Tests: small-value files where each value is parsed as a separate tiny document (Double/Uint64/Int64/Bool/String), plus whole documents (Twitter, CitmCatalog, Canada, Discord, Google Maps, Instruments, Marine IK, Mesh, Random, minified and prettified). Measured by the adaptive-sampling BenchmarkSuite harness (commit 49d7727), pinned to Jsonifier 9b1cd1d, Glaze 76db773 and simdjson 6913ee1 |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-14900KF (the page prints 'i9-14900KF-AVX2'), running under WSL2 (Linux 6.18.40.1-microsoft-standard-WSL2) |
| **Compiler and flags** | Clang 24.0.0, Release. From Json-Performance CMakeLists.txt: -std=c++23 -O3 -march=native -funroll-loops -fomit-frame-pointer -flto=thin -finline-functions -ffunction-sections -fdata-sections, linked with lld (-Wl,-O2 --gc-sections). simdjson is built with SIMDJSON_DEVELOPMENT_CHECKS OFF and UTF-8 validation on. Jsonifier uses its AVX2 backend and simdjson uses haswell |
| **Adoption** | 103 stars |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/nihilai-collective/Jsonifier) · [benchmark](https://github.com/nihilai-collective/Json-Performance/blob/main/Linux-Clang.md) |

## Verdict

In the authors' own Json-Performance harness (Clang 24.0.0, -O3 -march=native -flto=thin, AVX2 backend vs simdjson haswell, i9-14900KF under WSL2, UTF-8 validation on for all libraries), Jsonifier reads into typed structs were 2.4-13.7x faster than simdjson ondemand on files of tiny single-value documents. On most whole documents the gain was about 1.1-1.75x (e.g. Twitter minified 2116 vs 1212 MB/s), with statistical ties on Twitter, Google Maps and Random prettified and a loss on Mesh prettified (1919 vs 2113 MB/s); Jsonifier ran with knownOrder=true and minified set to match the input, options ondemand has no equivalent for.

## Use it when

- Deserializing stable, known schemas (API responses, protocol messages, log records) into C++ structs where you would otherwise hand-write simdjson ondemand traversal. The largest whole-document gains are on minified input, e.g. Twitter minified 2116 vs 1212 MB/s and Instruments minified 3335 vs 1476 MB/s.
- Many tiny documents parsed one at a time, like single scalars or small messages. With no per-document stage-1 setup, the authors measured 2.4-13.7x over ondemand on files of single-value documents.
- Producers that emit keys in a different order than your struct declares. The learned key-order table avoids ondemand's forward rescans: Marine IK Reverse minified reads at 810 vs 191 MB/s.
- You also want fast typed writes, minify and prettify from the same library. simdjson has no struct serializer, and on the Clang page Jsonifier's writes beat Glaze in most tests (Twitter minified write 7689 vs 5868 MB/s).
- Server builds where you control the target CPU at compile time (-march=native style): x86-64 with AVX2 or AVX-512, or aarch64 with NEON.

## Skip it when

- Schemas only known at runtime, or exploratory traversal. raw_json_data is the fallback, and the docs say it is slower than registered structs. The authors' own design paper names simdjson DOM/On-Demand as the right tool for dynamic workloads.
- GCC builds reading pretty-printed input. On the authors' Linux/GCC 16.1 page, simdjson ondemand wins Twitter prettified (2266 vs 1802 MB/s), Mesh prettified (2241 vs 1549), Random prettified (1701 vs 1367), and CitmCatalog and Canada prettified. The authors' own tally for Linux/GCC is 18 wins, 1 tie and 12 losses against simdjson.
- Portable binaries for CPUs you don't know in advance. The SIMD backend is fixed when you configure with no runtime dispatch, so a wrong JSONIFIER_CPU_INSTRUCTIONS gives SIGILL or a silent scalar fallback. The vcpkg port does not support Windows ARM, Xbox or 32-bit targets.
- ARM SVE2 targets. That backend is marked experimental with known incorrect parsing cases, and NEON is the recommended production path.
- Teams that need a mature, widely reviewed dependency. It has one listed contributor, 103 stars and v1.0.0 only in June 2026. Past ASan-found string over-reads (issues #27 and #30) were fixed. The docs contradict each other on some defaults: validateUtf8 is listed as false in one page but defaults to true in config.hpp, and the minimum Clang is 14 in one page and 16 in another. Glaze also beats it on Discord and Google Maps minified reads.

## How it is fast

A full-document parse skips simdjson-style stage-1 structural indexing and makes one schema-guided pass over the raw bytes, comparing each member header against a key literal built at compile time (with minified+knownOrder, `,"key":` is a single fixed-length compare). When keys arrive out of order it falls back to a hash-map dispatch generated at compile time for that struct's exact key set, and a thread_local per-type table learns the observed order so the next document takes the fast path. UTF-8 is validated only over string bytes, inside the SIMD string-unescape loop, and the ISA is fixed at compile time, so there is no runtime dispatch. The Langdale-Lemire stage-1 index (clmul prefix-XOR, batched tzcnt drain, VBMI2 compress on AVX-512) runs only for partialRead, minify and prettify.

## Compared with alternatives

Pick it when you work in C++, your incumbent is simdjson, and you want typed struct binding with compile-time reflection plus serialization. LJSON and zzzJSON are benchmarked only against RapidJSON, and simd-json, jiter, Sonic, go-json, jsoniter and easyjson serve Rust or Go, not C++.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none at runtime (fast_float code is vendored in-tree); the unit tests fetch rt-ut via CMake FetchContent |
| **Minimum toolchain** | C++20; README lists MSVC 2022+, GCC 11+ and Clang 16+ (Installation.md says Clang 14+); CMake 3.28+. The INTERFACE target raises the constexpr evaluation limits (-fconstexpr-steps=100000000 on Clang, -fconstexpr-ops-limit=1000000000 on GCC, /constexpr:steps100000000 on MSVC) |
| **Platforms** | x86-64 (scalar, AVX, AVX2, AVX-512 with F+BW+VBMI2) and aarch64 NEON; SVE2 experimental; CI runs on Ubuntu, macOS and Windows; Android is best-effort |
| **Thread safety** | Not documented. In the source, a jsonifier_core instance holds mutable scratch buffers and the error list, so use one per thread. The per-type knownOrder tables and root-array scratch vectors are thread_local, so instances on different threads do not share parse state. |
| **Drop-in for the baseline** | no |

## Gotchas

- nullTerminated defaults to true, so the parser relies on a '\0' after the buffer and skips bounds checks. Passing std::vector&lt;char&gt; or a raw file/socket buffer without a trailing NUL is undefined behavior unless you set nullTerminated=false.
- minified=true is a promise about the input: whitespace then causes parse failures. The published benchmark runs Jsonifier with knownOrder=true and minified set to match each file, so measure with the flags your input actually guarantees.
- The build depends on CMake. Configure runs a CPU probe and writes include/jsonifier-incl/simd/jsonifier_cpu_instructions.hpp into the source tree (the checked-in copy hard-codes 111 = AVX2+BMI+CLMUL). The JSONIFIER_PLATFORM_\*/COMPILER_\*/INLINE macros are also CMake compile definitions, so copying the headers in by hand means defining all of them yourself. Include only &lt;jsonifier&gt;: internal headers #define reinterpret_cast, const_cast, dynamic_cast and memcpy to static_assert traps.
- A default jsonifier_core&lt;&gt; allocates a 1 MB string buffer plus a 1M-entry uint32 tape (about 5 MB), possibly on huge pages, so reuse one per thread instead of constructing one per call. The string_view returned by serializeJson(data) is invalidated by the next parse or serialize call on that instance.

## Caveats and trade-offs

Run and published by the Jsonifier authors in their companion repo (Json-Performance), not by an independent party. The largest gains vs simdjson (5-14x) come from small-value tests that parse thousands of tiny single-value documents, where simdjson ondemand's per-document iterate() setup cost dominates. On whole documents the gain is \~1.1-1.8x, several tests are statistical ties, and simdjson wins Mesh (Prettified). The Marine IK Reverse tests deliberately read keys out of order, which is a known worst case for ondemand. The run was on WSL2 with a Clang 24 development snapshot and pinned to commits dated 2026-09-23, so results may shift with later commits

Requires C++20; compile-time reflection via member-pointer registration (no macros/codegen); ARM SVE2 backend explicitly marked experimental with known incorrect cases; NEON recommended for production ARM

## Maintenance

Actively developed by a single maintainer (v1.0.2 released 2026-09-22, CI green on main), MIT-licensed and packaged in vcpkg; it is header-only but should be consumed through its CMake target rather than copied in by hand.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** Linux-Clang.md compares Jsonifier, Glaze and simdjson ondemand, with a row for each library in every read test. The benchmark code is public: Json-Performance source/main.cpp, include/tests.hpp and include/common.hpp, built by CMakeLists.txt. The page states Clang 24.0.0 and the i9-14900KF CPU, and CMakeLists.txt gives the flags (-O3 -march=native -funroll-loops -fomit-frame-pointer -flto=thin -finline-functions, lld), so this is Tier A.
- **Verifier notes:** All four quoted figures match the simdjson rows exactly. I added the whole-document range because the quoted tests are the most favorable microbenchmarks. Metadata checks out: MIT, 103 stars, not a fork, not archived, last commit 2026-09-24. The README also links an independent suite (Loki-Astari/JsonBenchmark), which I did not open.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/nihilai-collective/Json-Performance/blob/main/Linux-Clang.md>
  - <https://github.com/nihilai-collective/Json-Performance>
  - <https://github.com/nihilai-collective/Json-Performance/blob/main/ReadMe.md>
  - <https://github.com/nihilai-collective/Json-Performance/blob/main/CMakeLists.txt>
  - <https://github.com/nihilai-collective/Json-Performance/blob/main/CMakePresets.json>
  - <https://github.com/nihilai-collective/Json-Performance/blob/main/.github/workflows/Benchmark.yml>
  - <https://github.com/nihilai-collective/Json-Performance/blob/main/source/main.cpp>
  - <https://github.com/nihilai-collective/Json-Performance/blob/main/include/tests.hpp>
  - <https://github.com/nihilai-collective/Json-Performance/blob/main/include/common.hpp>
  - <https://github.com/nihilai-collective/Json-Performance/blob/main/json/Bool%20Test.json>
  - <https://github.com/nihilai-collective/Jsonifier>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/README.md>
  - <https://github.com/nihilai-collective/Jsonifier/commit/9b1cd1d>
- **Sources the enricher read:**
  - <https://github.com/nihilai-collective/Jsonifier>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/ReadMe.md>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/Two-Stages.md>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/documentation/Installation.md>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/documentation/Known_Order.md>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/documentation/PartialReading.md>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/documentation/Optimizing_For_Minified_Json.md>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/documentation/Usage_Serializing_Parsing.md>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/documentation/Reflection.md>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/documentation/Parsing_Arbitrary_Data.md>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/documentation/CPU_Architecture_Selection.md>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/documentation/Errors.md>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/CMakeLists.txt>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/cmake/library_setup.cmake>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/include/jsonifier>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/include/jsonifier-incl/core/config.hpp>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/include/jsonifier-incl/core/jsonifier_core.hpp>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/include/jsonifier-incl/parsing/parse_impl.hpp>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/include/jsonifier-incl/parsing/parser.hpp>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/include/jsonifier-incl/utilities/simd.hpp>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/include/jsonifier-incl/utilities/string.hpp>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/include/jsonifier-incl/containers/allocator.hpp>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/include/jsonifier-incl/simd/jsonifier_cpu_instructions.hpp>
  - <https://github.com/nihilai-collective/Jsonifier/blob/main/include/jsonifier-incl/simd/simd_types.hpp>
  - <https://github.com/nihilai-collective/Jsonifier/issues?q=is%3Aissue>
  - <https://github.com/nihilai-collective/Jsonifier/issues/27>
  - <https://github.com/nihilai-collective/Jsonifier/issues/30>
  - <https://github.com/nihilai-collective/Jsonifier/issues/35>
  - <https://github.com/nihilai-collective/Jsonifier/issues/37>
  - <https://github.com/nihilai-collective/Jsonifier/releases>
  - <https://github.com/nihilai-collective/Jsonifier/graphs/contributors>
  - <https://github.com/nihilai-collective/Jsonifier/actions/workflows/unit-tests.yml>
  - <https://github.com/nihilai-collective/Json-Performance/blob/main/Linux-Clang.md>
  - <https://github.com/nihilai-collective/Json-Performance/blob/main/Linux-GCC.md>
  - <https://github.com/nihilai-collective/Json-Performance/blob/main/ReadMe.md>
  - <https://github.com/nihilai-collective/Json-Performance/blob/main/include/tests.hpp>
  - <https://github.com/Loki-Astari/JsonBenchmark>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/nihilai-collective/jsonifier`) · [data/wave4/enrich/raw/github_com_nihilai_collective_jsonifier.json](../../../data/wave4/enrich/raw/github_com_nihilai_collective_jsonifier.json) (enrichment confidence 0.8)

</details>
