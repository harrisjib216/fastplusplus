# Cap'n Proto

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [JSON serialization](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Zero-copy binary serialization/RPC system: wire format equals in-memory layout, beating RapidJSON-based JSON serialize/deserialize by \~2.8x/1.6x.

| | |
|---|---|
| **Beats** | JSON serialization (RapidJSON) |
| **Claimed result** | 247ns serialize / 184ns deserialize (Cap'n Proto, 208 bytes) vs 696ns serialize / 291ns deserialize (JSON via RapidJSON, 301 bytes) — \~2.8x faster serialize, \~1.6x faster deserialize (derived from page data) |
| **Workload** | Serializing/deserializing a fixed trading-domain object graph (accounts, balances, orders) in chronoxor/CppSerialization's multi-protocol shootout |
| **Metric** | latency |
| **Hardware** | Apple M1 Pro (10 cores, reported 2.4 GHz), macOS (Darwin 24.5.0); CppBenchmark run 2025-07-16 |
| **Compiler and flags** | Not stated; CppBenchmark report says only 'Process configuration: release' |
| **Adoption** | 13.2k stars; used by Cloudflare, Sandstorm |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/capnproto/capnproto) · [benchmark](https://github.com/chronoxor/CppSerialization) |

## Verdict

On chronoxor/CppSerialization's fixed trading-object shootout (accounts/balances/orders) on an Apple M1 Pro under macOS with CppBenchmark's 'release' configuration (compiler and flags not stated), Cap'n Proto serialized in 247ns to 208 bytes and deserialized in 184ns, versus RapidJSON-based JSON at 696ns serialize / 291ns deserialize / 301 bytes — about 2.8x faster to serialize and 1.6x faster to deserialize than JSON in that fixture; independently confirmed against the current CppSerialization README table.

## Use it when

- C++ service-to-service messaging or RPC (not just wire format) where you can adopt promise pipelining via capnp-rpc
- Structured, schema-evolving payloads shared across services/languages, where a build-time codegen step is acceptable
- Read-heavy or partial-read workloads over a message buffer, since Cap'n Proto readers touch only the fields accessed instead of materializing the whole object
- Trading/finance-shaped fixed object graphs like the benchmarked one (accounts, balances, orders) where both serialize and deserialize latency matter
- Cases where message size matters too: 208 bytes here vs. JSON's 301 bytes for the same object

## Skip it when

- You need a human-readable, greppable, or hand-editable wire format (logs, configs, ad hoc debugging) — stay with JSON
- Pure C++-to-C++ traffic with no RPC/schema-evolution need and raw speed is the only goal — zpp::bits (34ns/37ns in the same suite) is \~7x faster with no schema compiler
- Small one-off tools/scripts where adding a .capnp schema and `capnp compile` build step isn't worth the setup
- Teams needing a dynamic/schema-less path in C++ — the generated-code path is the primary supported workflow
- Long-lived buffer lifetime is hard to guarantee — zero-copy readers require the backing buffer to outlive them

## How it is fast

The wire format is identical to the in-memory layout: messages live in arena-allocated segments (BuilderArena/SegmentBuilder) navigated by struct/list/far pointers, so writing is just placing fields directly and reading is pointer validation with no separate decode pass. This skips the DOM-build-then-stringify step JSON needs to write and the parse-then-materialize step JSON needs to read, which is consistent with the benchmark's bigger win on serialize (\~2.8x) than deserialize (\~1.6x, and that JSON figure excludes JSON's own parse cost, reported separately at 771ns).

## Compared with alternatives

Pick Cap'n Proto over the JSON-focused siblings (DAW JSON Link, cjson.cpp, json.cpp, Tachyon.JSON, utl::json) when you can drop JSON as the wire format entirely and want cross-language schemas plus an RPC layer, not just a faster JSON parser. Pick zpp::bits instead when you stay C++-only and don't need RPC or schema evolution — it's markedly faster in the same benchmark (34ns/37ns vs. 247ns/184ns) with no schema compiler.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (plus a codegen step: `capnp compile` generates .h/.c++ from your .capnp schema, which you then build) |
| **Dependencies** | none required for core capnp/kj; optional deps only for extras — OpenSSL (kj-tls), zlib (kj-gzip), Brotli — and the `capnp` schema compiler is needed at build time |
| **Minimum toolchain** | Stable 1.0 line (`master` branch): C++14, GCC 5+/Clang 5+/MSVC 2017+. The repository's current default branch (`v2`, in active development) raises this to C++20, built with -std=gnu++23/​/std:c++23preview |
| **Platforms** | Linux, macOS, Windows (per CMake/Bazel build files and the CppSerialization benchmark's cross-platform build); no SIMD/CPU-arch requirement documented |
| **Thread safety** | Not documented as a blanket guarantee. Source comments flag specific unsafe operations (e.g. MessageBuilder::getOrphanage() is called out in-source as 'not thread-safe'); the KJ async runtime is single-threaded per EventLoop, and cross-thread coordination needs explicit primitives (see GH issue #2234, a TSAN report against CrossThreadFulfiller). |
| **Drop-in for the baseline** | partial — replacing RapidJSON means adopting a .capnp schema, the capnp compiler, and generated Builder/Reader types in place of a JSON DOM/SAX API; not a header swap |

## Gotchas

- Message buffers must outlive every Reader built from them — readers view the buffer directly (zero-copy), so freeing or reusing it early dangles
- MessageBuilder::getOrphanage() is documented in-source as not thread-safe even though adjacent accessors look read-only
- Binary wire format isn't eyeball-debuggable like JSON; inspecting a message needs `capnp decode`/`capnp convert` against the schema
- Schema changes require rerunning `capnp compile` and rebuilding generated headers; there's no schema-less mode on the standard C++ path

## Caveats and trade-offs

Numbers come from a small third-party shootout (chronoxor/CppSerialization, 167 stars), not Cap'n Proto's own benchmarks. Compiler and flags are not stated. This compares a binary wire format against a JSON text format (RapidJSON), not the same facility. The JSON-Deserialize figure (291 ns) leaves out parsing: the JSON is parsed in the fixture, and JSON-Parse is reported separately at 771 ns. The more natural incumbent in the same table, Protobuf (322 ns serialize / 351 ns deserialize), is also slower than Cap'n Proto.

Requires a .capnp schema and code-generation step; wire format is not human-readable, unlike JSON; zero-copy design changes idiomatic usage vs building strings/streams by hand

## Maintenance

Actively maintained (commits as of the record date) under the MIT license, 13.2k stars, used in production by Cloudflare and Sandstorm; MIT terms make it freely redistributable, but it is not a small vendor-in-header — expect to build libcapnp/libkj and wire the capnp compiler into your build.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** chronoxor/CppSerialization has public benchmark code (performance/capnproto_\*.cpp, json_\*.cpp), and its CppBenchmark reports name the Apple M1 Pro CPU. The compiler and flags are not stated (only 'Process configuration: release'), so it is not A. The suite is small (167 stars) and is run by the author of a competing format (FastBinaryEncoding), so it is not a well-known independent suite, which rules out B.
- **Verifier notes:** The 247/184 ns vs 696/291 ns figures match this project's rows in the CppSerialization README table and its per-protocol reports. I downgraded B to C because this is not a well-known suite and the compiler/flags are missing. GitHub reports the license as NOASSERTION, but the LICENSE file is MIT, so the record is correct. Protobuf could serve as a better baseline if the orchestrator prefers one.
- **Fields the verifier corrected:** `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/chronoxor/CppSerialization>
  - <https://github.com/chronoxor/CppSerialization/blob/main/README.md>
  - <https://github.com/chronoxor/CppSerialization/tree/main/performance>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/json_deserialize.cpp>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/capnproto_deserialize.cpp>
  - <https://github.com/capnproto/capnproto>
  - <https://github.com/capnproto/capnproto/blob/v2/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/capnproto/capnproto>
  - <https://github.com/capnproto/capnproto/blob/v2/README.md>
  - <https://github.com/capnproto/capnproto/blob/v2/c%2B%2B/README.txt>
  - <https://github.com/capnproto/capnproto/blob/v2/c%2B%2B/CMakeLists.txt>
  - <https://github.com/capnproto/capnproto/blob/v2/c%2B%2B/compile_flags.txt>
  - <https://github.com/capnproto/capnproto/blob/master/c%2B%2B/src/kj/common.h>
  - <https://github.com/capnproto/capnproto/blob/master/c%2B%2B/src/kj/exception.h>
  - <https://github.com/capnproto/capnproto/blob/master/c%2B%2B/src/capnp/message.h>
  - <https://github.com/capnproto/capnproto/blob/master/c%2B%2B/src/kj/async.h>
  - <https://capnproto.org/cxx.html>
  - <https://github.com/chronoxor/CppSerialization>
  - <https://github.com/chronoxor/CppSerialization/blob/main/README.md>
  - <https://github.com/capnproto/capnproto/issues/2234>
  - <https://github.com/capnproto/capnproto/branches>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/capnproto/capnproto`) · [data/wave1/enrich/raw/github_com_capnproto_capnproto.json](../../../data/wave1/enrich/raw/github_com_capnproto_capnproto.json) (enrichment confidence 0.55)

</details>
