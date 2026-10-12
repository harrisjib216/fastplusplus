# zpp::bits

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only C++20 binary serializer using compile-time aggregate reflection; no schema, no codegen, faster than JSON via RapidJSON in third-party benchmarks.

| | |
|---|---|
| **Beats** | JSON serialization (RapidJSON) |
| **Claimed result** | 34ns serialize / 37ns deserialize (zpp::bits, 130 bytes) vs 696ns serialize / 291ns deserialize (JSON via RapidJSON, 301 bytes) — \~20x faster serialize, \~7.9x faster deserialize (derived from page data) |
| **Workload** | Same trading-domain object-graph benchmark as above, from chronoxor/CppSerialization's multi-protocol shootout |
| **Metric** | latency |
| **Hardware** | Apple M1 Pro (10 cores, reported 2.4 GHz), macOS (Darwin 24.5.0); CppBenchmark run 2025-07-16 |
| **Compiler and flags** | Not stated; CppBenchmark report says only 'Process configuration: release' |
| **Adoption** | \~1k stars |
| **Last commit** | 2026-08-09 |
| **Links** | [repository](https://github.com/eyalz800/zpp_bits) · [benchmark](https://github.com/chronoxor/CppSerialization) |

## Verdict

In chronoxor/CppSerialization's trading-object-graph benchmark on Apple M1 Pro (macOS, CppBenchmark 'release' build, compiler/flags otherwise unstated), zpp::bits serialized in 34ns and deserialized in 37ns for a 130-byte message, versus RapidJSON-based JSON at 696ns/291ns for a 301-byte message — about 20x/7.9x faster. This compares a binary format to JSON text rather than the same facility, and the 291ns JSON-deserialize figure excludes a separately reported 771ns JSON-parse step.

## Use it when

- Both ends of the wire are C++ and you control the schema, so a text/interop format isn't needed
- Latency-sensitive object graphs (trading, telemetry) with primitives, vectors, optionals, or variants where nanosecond-scale serialize/deserialize matters
- C++20 toolchain available (CI covers GCC 11-16 and Clang 13/17-22 on Linux and macOS) and types are aggregates or structured-binding-friendly
- Want a single vendorable header (no build step, no schema compiler, no external dependency)
- Need simple RPC (request/response dispatch) without standing up a separate schema/IDL toolchain

## Skip it when

- Need JSON or another human-readable/interoperable wire format — output is a custom binary layout, not JSON
- Need cross-language interop without hand-porting the format — no schema/codegen like Protobuf, Cap'n Proto, or FlatBuffers provide
- Targeting MSVC — CI does not cover it and users have hit internal compiler errors (issue #99) and VS2019 compile failures (issue #80)
- Object graph contains std::vector&lt;bool&gt; — fails to compile as of the open issue #153 (std::_Bit_reference binding error)
- Smallest possible message size matters more than speed — SimpleBinaryEncoding produced smaller messages in the same benchmark shootout

## How it is fast

Member enumeration happens at compile time via structured bindings or an explicit `zpp::bits::members<N>` count, so there is no RTTI or runtime reflection, and the library is written almost entirely `constexpr` so the compiler can inline and specialize per type. It writes fields directly into a contiguous byte buffer (vector, array, or span) with no intermediate DOM/tree, unlike a JSON library that must build an object model. Field sizes can be fixed-width or opted out entirely, avoiding the text formatting and number parsing that JSON serialization pays for on every field.

## Compared with alternatives

Pick over Cap'n Proto when you don't want an IDL/schema-compiler step and want the fastest raw numbers in the same chronoxor/CppSerialization suite (34ns/37ns vs Cap'n Proto's 247ns/184ns); pick over the JSON-based siblings (cjson.cpp, DAW JSON Link, Tachyon.JSON, utl::json) whenever human-readable or cross-language JSON output isn't required and both ends are C++.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (optionally detects and uses zpp::throwing if that header is present, for coroutine-based error handling) |
| **Minimum toolchain** | C++20; CI tests GCC 11-16 and Clang 13, 17-22 on Ubuntu and macOS (Clang 17/18) — MSVC not in CI and has open compile-failure/ICE reports |
| **Platforms** | x86-64 and aarch64 (Linux and macOS in CI); no SIMD or architecture-specific intrinsics used |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | false — different API and a custom binary wire format, not interchangeable with RapidJSON or other JSON libraries |

## Gotchas

- std::vector&lt;bool&gt; serialization does not compile (open issue #153)
- Non-aggregate types need `using serialize = zpp::bits::members<N>;` (member count stated explicitly) or an ADL `serialize()` overload before C++26 lifts this requirement
- RPC layer had a reported memory-leak bug (issue #188, closed) — confirm the fix is in the version you pin
- Raw/non-owning pointers and null pointers are intentionally unsupported (README 'Limitations'); use std::optional instead

## Caveats and trade-offs

Numbers come from a small third-party shootout (chronoxor/CppSerialization, 167 stars), not zpp::bits's own benchmark. Compiler and flags are not stated. This compares a binary format against JSON text (RapidJSON), not the same facility. The JSON-Deserialize figure (291 ns) leaves out parsing (JSON-Parse is 771 ns, reported separately). zpp::bits was the fastest format in that table, narrowly ahead of SimpleBinaryEncoding (35/52 ns). zpp::bits's own README benchmark (fraillt/cpp_serializers_benchmark) compares against bitsery, yas, flatbuffers and protobuf, not JSON.

Header-only C++20 library with no schema/codegen, but needs aggregate/structured-binding-friendly types; output is a compact binary format, not JSON-compatible or human-readable; SimpleBinaryEncoding had an even smaller message size in the same shootout, so the 'winner' depends on which metric (speed vs size) matters most

## Maintenance

Actively maintained (last commit 2026-08-09; CI runs on push/PR and a daily cron against GCC 11-16 and Clang 13-22); MIT-licensed single 6,000-line header, trivially copyable/vendorable into a project with no package manager or build step.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** This uses the same chronoxor/CppSerialization shootout. The benchmark code is public (performance/zpp_bits_\*.cpp) and the Apple M1 Pro CPU is stated, but the compiler and flags are not ('release' only), so it is not A. The suite is small (167 stars) and not well-known, so it does not reach B.
- **Verifier notes:** 34/37 ns (130 bytes) vs 696/291 ns (301 bytes) match the zpp::bits and JSON rows, and the ratios are correctly marked as derived. Downgraded B to C for the same reason as Cap'n Proto. Metadata checks out: MIT, 1,009 stars, last commit 2026-08-09.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** Serializing 100k records with std::string and std::vector members took 26.914 ns/record into a reused output buffer vs 39.735 ns with a fresh buffer each time, so buffer reuse alone was worth 1.48x. In selection it was the fastest of three header-only serializers (24.19/63.37 ns serialize/deserialize vs bitsery 32.22/66.34 and cista 62.87/99.17, median of 11). (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-03-third-party); Recorded as a loss: deserializing the same 100k records took 99.041 ns/record, 32.8x the 3.02 ns memcpy floor (POD only, allocates nothing), and most of the gap is allocating owning members. zpp_bits also defaults to native byte order unless zpp::bits::endian::little{} is passed. (developer source, private repo; gcc 13.3.0 -O2 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-03-third-party)
- **Pages the verifier opened:**
  - <https://github.com/chronoxor/CppSerialization>
  - <https://github.com/chronoxor/CppSerialization/blob/main/README.md>
  - <https://github.com/chronoxor/CppSerialization/tree/main/performance>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/json_deserialize.cpp>
  - <https://github.com/eyalz800/zpp_bits>
  - <https://github.com/eyalz800/zpp_bits/blob/main/README.md>
- **Sources the enricher read:**
  - <https://github.com/eyalz800/zpp_bits>
  - <https://github.com/eyalz800/zpp_bits/blob/main/README.md>
  - <https://github.com/eyalz800/zpp_bits/blob/main/zpp_bits.h>
  - <https://github.com/eyalz800/zpp_bits/blob/main/.github/workflows/actions.yml>
  - <https://github.com/eyalz800/zpp_bits/issues/153>
  - <https://github.com/eyalz800/zpp_bits/issues/188>
  - <https://github.com/eyalz800/zpp_bits/issues/212>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/eyalz800/zpp_bits`) · [data/wave1/enrich/raw/github_com_eyalz800_zpp_bits.json](../../../data/wave1/enrich/raw/github_com_eyalz800_zpp_bits.json) (enrichment confidence 0.58)

</details>
