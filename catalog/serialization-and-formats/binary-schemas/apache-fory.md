# Apache Fory (C++)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Apache Fory's C++ serializer for plain annotated structs, cross-language binary format; 1.3-11x Protobuf's throughput in its benchmarks.

| | |
|---|---|
| **Beats** | Protobuf |
| **Claimed result** | 1.2x-4.5x higher throughput than Protobuf across cases: MediaContent serialize 4.5x (2,254,915 vs 504,410 ops/sec), MediaContent deserialize 1.9x, Sample serialize/deserialize \~1.3x, NumericStruct serialize 1.6x / deserialize 1.2x |
| **Workload** | Serialize/deserialize three C++ structs of increasing complexity (NumericStruct, Sample, MediaContent) using Google Benchmark, comparing Fory's C++ implementation against Protobuf. |
| **Metric** | throughput |
| **Hardware** | Darwin 24.5.0, arm64, 12 physical/12 logical cores, 48GB RAM (specific CPU model, e.g. which Apple silicon chip, not named) |
| **Compiler and flags** | CMake Release build with explicit -O3 -DNDEBUG (benchmarks/cpp/CMakeLists.txt), C++17; Protobuf v25.5, Google Benchmark v1.9.1 and msgpack-c cpp-6.1.0 via FetchContent. The compiler and its version are not stated |
| **Adoption** | 4.6k stars |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/apache/fory) · [benchmark](https://github.com/apache/fory/blob/main/docs/benchmarks/object-serialization/xlang/cpp/README.md) |

## Verdict

Fory's own Google Benchmark suite (xlang compatible mode, reference tracking off, reused output buffer) against Protobuf v25.5, built Release with -O3 on an unnamed compiler, ran on a 12-core, 48 GB arm64 Mac (Darwin 24.6.0, chip not named). Its 2026-06-12 report shows 1.27x-10.9x Protobuf's throughput, e.g. MediaContent serialize at 8.81M vs 2.12M ops/s (4.15x). Most of the Protobuf timings include converting to and from plain C++ structs on every iteration; on Sample, the one case that uses native protobuf objects, Fory was 1.59x on serialize and 2.25x on deserialize. The older benchmarks/cpp README table (Darwin 24.5.0) shows 1.2x-4.5x.

## Use it when

- C++ code that already models data as plain structs (strings, vectors, maps, nested structs) and today pays to copy them into protobuf message objects and back; that conversion is where the benchmark's biggest serialize wins (4-11x) come from
- Throughput-bound serialization of small-to-medium messages (roughly 80 B to 2 KB in the benchmarks), using one Fory instance per thread and a reused Buffer via serialize_to
- Payloads exchanged between C++ and Java/Python/Go/Rust/JS/C# services that should share one wire format, with type IDs registered consistently or types generated from Fory/protobuf IDL
- Object graphs with shared or cyclic std::shared_ptr references (track_ref(true)), which protobuf cannot express
- Rolling deployments that need add/remove/reorder field evolution (compatible mode is the default); for C++-only, same-schema traffic, .xlang(false).compatible(false) gives smaller, faster payloads

## Skip it when

- You need protobuf wire compatibility, preservation of unknown fields, or protobuf/gRPC tooling (reflection, interceptors). Fory bytes are not protobuf bytes, and its own docs recommend protobuf for these cases
- Payload size matters more than CPU. In the 2026-06-12 report Fory's output was larger than Protobuf's for Sample (445 vs 375 B) and MediaContent (362 vs 301 B); it was smaller only for the numeric structs
- Large messages where you read a few fields in place. Object mode decodes the whole struct; flat formats (or Fory's separate row format) avoid that
- You need a long-stable C++ API. The C++ object-graph serializer arrived in November 2025, and v1.7.0 through v1.7.5 shipped within four weeks (2026-08-28 to 2026-09-25), alongside codec-boundary hardening commits in late August 2026
- Decoding untrusted input without extra setup. The C++ security guide requires registering only accepted types and keeping the graph-memory and depth limits; Fory's Java and Python implementations have had deserialization CVEs (CVE-2025-59328, CVE-2026-50076, CVE-2025-61622, CVE-2026-48207), and none are listed for C++

## How it is fast

FORY_STRUCT generates constexpr field metadata, and fields are sorted at compile time: non-nullable fixed-width primitives come first by size, then varints, then everything else. The serializer can therefore reserve the maximum size once and write the leading primitives at compile-time offsets with a single writer-index update, skipping per-field capacity checks and error propagation. It encodes straight from the user's struct with no intermediate message object, using zigzag varints for int32/int64 and a combined length-plus-encoding header for strings (Latin-1/UTF-16/UTF-8). In compatible mode, schema metadata (a TypeDef identified by a 52-bit MurmurHash3 hash) is written once per stream and cached by the reader, and per-field reads are unrolled through compile-time switch dispatch.

## Compared with alternatives

Pick Fory over YaFF, SBE or ProtoCache when you want to decode into ordinary owning C++ structs (strings, vectors, maps, shared_ptr graphs) with schema evolution on by default and readers in other languages. Pick SBE for fixed-layout, low-latency messages, and YaFF or ProtoCache when you read a few fields in place from a buffer without a full decode.

## Integration

| | |
|---|---|
| **Form** | static lib (or shared); a compiled library pulled in with CMake FetchContent (SOURCE_SUBDIR cpp, target fory::serialization) or as a Bazel module; not header-only |
| **Dependencies** | none at runtime (MurmurHash3 and its hash map are vendored); googletest only for tests; gRPC C++ 1.39+ only for the generated gRPC companions; the foryc compiler is optional, for IDL codegen |
| **Minimum toolchain** | C++17; CMake 3.16+ or Bazel 8+. The docs disagree on compiler minimums: the install guide lists GCC 7+/Clang 5+/MSVC 2017+, the benchmark README GCC 8+/Clang 7+/MSVC 2019+. MSVC requires /Zc:preprocessor |
| **Platforms** | x86-64 (CMake compiles Fory's sources with -mavx2 or /arch:AVX2 by default), aarch64 (NEON paths), plus SSE2 and scalar fallbacks; CI runs on ubuntu-latest, macos-latest and windows-2022, with ASan/UBSan jobs |
| **Thread safety** | A Fory instance is not thread-safe (it is the fastest option; use one per thread). build_thread_safe() returns a ThreadSafeFory backed by a pool of instances. Register types before starting threads. |
| **Drop-in for the baseline** | partial: foryc can compile existing .proto schemas into plain C++ structs with Fory serializers, but the wire format is not protobuf-compatible, unknown fields are not preserved, and the API (FORY_STRUCT + register_struct + Result&lt;T, Error&gt;) differs from generated protobuf classes |

## Gotchas

- Each struct needs a FORY_STRUCT(...) list placed after its fields (in a public: section inside a class), plus register_struct&lt;T&gt;(id) on every Fory instance. A missing registration fails at runtime with 'Type not registered', not at compile time.
- The defaults are track_ref(true) and compatible(true), and both cost speed and size. The published benchmark switched reference tracking off, so disable it for value-shaped data.
- On x86-64, CMake's FORY_USE_AVX2 option defaults to ON and adds -mavx2 to Fory's compiled sources. Set it to OFF if the binary must run on CPUs without AVX2.
- With compatible(false), mismatched schemas 'may cause errors or undefined behavior' (per the docs). Even in compatible mode, renaming a field is not supported because fields match by snake_case name or tag ID. Raw pointers and std::array are listed as unsupported.

## Caveats and trade-offs

First-party benchmark (Apache Fory's own repo); the CPU model and compiler are not disclosed. The README table's numbers have not changed since at least 2026-03-23; commit 7f8e2237ec on 2026-05-08 only renamed a row. A newer generated report (docs/benchmarks/object-serialization/xlang/cpp/README.md, 2026-06-12, Darwin 24.6.0, the same 12-core/48 GB arm64 machine) has Fory 1.27x-10.9x faster than Protobuf, e.g. MediaContent serialize 8,808,084 vs 2,122,926 ops/s (4.15x) and SampleList serialize 3,864,068 vs 353,391 (10.9x) (ratios derived from page data). Fory also beats msgpack-c there. The Protobuf timings for NumericStruct, MediaContent and the list cases include converting to/from a plain C++ struct on every iteration (to_pb_\*/from_pb_\*), while Sample uses native protobuf objects and shows the smallest gain in the README table (1.3x). Fory runs in xlang compatible mode and reuses its output buffer.

Much larger, multi-language xlang framework rather than a lightweight C++-only library; C++ support is newer and less battle-tested than Fory's Java implementation

## Maintenance

Actively maintained (last commit 2026-09-23, v1.7.5 released 2026-09-25) and Apache-2.0 licensed, but the C++ object serializer is under a year old and is consumed as a CMake or Bazel-built library rather than vendored headers.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The first-party benchmarks/cpp/README.md table compares Fory against Protobuf (e.g. MediaContent serialize 2,254,915 vs 504,410 ops/s, 4.5x). The code is public (benchmarks/cpp/benchmark.cc, Google Benchmark) and the flags are stated (-O3 -DNDEBUG, Release), but the compiler is not stated and the CPU model is not named (arm64, 12 cores, 48 GB only), so it is C.
- **Verifier notes:** Every number and ratio in claimed_speedup appears in the README table. The newer 2026-06-12 report in docs/benchmarks/object-serialization/xlang/cpp/README.md is more current, and enrichment may prefer it as benchmark_url. I removed the unverified Java '170x' remark from the caveats. The metadata is correct (Apache-2.0, 4,558 stars, last commit on main 2026-09-23).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `benchmark_url`
- **Pages the verifier opened:**
  - <https://github.com/apache/fory>
  - <https://github.com/apache/fory/blob/main/benchmarks/cpp/README.md>
  - <https://github.com/apache/fory/tree/main/benchmarks/cpp>
  - <https://github.com/apache/fory/blob/main/benchmarks/cpp/CMakeLists.txt>
  - <https://github.com/apache/fory/blob/main/benchmarks/cpp/benchmark.cc>
  - <https://github.com/apache/fory/blob/main/docs/benchmarks/object-serialization/xlang/cpp/README.md>
  - <https://github.com/apache/fory/commit/7f8e2237ec>
  - <https://github.com/apache/fory/commit/4420b6881b>
- **Sources the enricher read:**
  - <https://github.com/apache/fory>
  - <https://github.com/apache/fory/blob/main/README.md>
  - <https://github.com/apache/fory/blob/main/cpp/README.md>
  - <https://github.com/apache/fory/blob/main/docs/benchmarks/object-serialization/xlang/cpp/README.md>
  - <https://github.com/apache/fory/blob/main/benchmarks/cpp/README.md>
  - <https://github.com/apache/fory/blob/main/benchmarks/cpp/benchmark.cc>
  - <https://github.com/apache/fory/blob/main/benchmarks/cpp/CMakeLists.txt>
  - <https://github.com/apache/fory/blob/main/docs/object-serialization/cpp/index.md>
  - <https://github.com/apache/fory/blob/main/docs/object-serialization/cpp/configuration.md>
  - <https://github.com/apache/fory/blob/main/docs/object-serialization/cpp/security.md>
  - <https://github.com/apache/fory/blob/main/docs/object-serialization/cpp/schema-evolution.md>
  - <https://github.com/apache/fory/blob/main/docs/object-serialization/cpp/native.md>
  - <https://github.com/apache/fory/blob/main/docs/object-serialization/cpp/type-registration.md>
  - <https://github.com/apache/fory/blob/main/docs/object-serialization/cpp/supported-types.md>
  - <https://github.com/apache/fory/blob/main/docs/specification/xlang_serialization_spec.md>
  - <https://github.com/apache/fory/blob/main/docs/compiler/index.md>
  - <https://github.com/apache/fory/blob/main/docs/compiler/protobuf-idl.md>
  - <https://github.com/apache/fory/blob/main/docs/grpc/cpp.md>
  - <https://github.com/apache/fory/blob/main/cpp/fory/serialization/struct_serializer.h>
  - <https://github.com/apache/fory/blob/main/cpp/fory/serialization/fory.h>
  - <https://github.com/apache/fory/blob/main/cpp/fory/serialization/context.h>
  - <https://github.com/apache/fory/blob/main/cpp/fory/util/buffer.h>
  - <https://github.com/apache/fory/blob/main/cpp/fory/util/string_util.h>
  - <https://github.com/apache/fory/blob/main/cpp/fory/util/string_util.cc>
  - <https://github.com/apache/fory/blob/main/cpp/fory/util/macros.h>
  - <https://github.com/apache/fory/blob/main/cpp/CMakeLists.txt>
  - <https://github.com/apache/fory/blob/main/cpp/fory/serialization/CMakeLists.txt>
  - <https://github.com/apache/fory/blob/main/cpp/fory/serialization/BUILD>
  - <https://github.com/apache/fory/blob/main/cpp/fory/util/BUILD>
  - <https://github.com/apache/fory/blob/main/cpp/fory/row/BUILD>
  - <https://github.com/apache/fory/blob/main/cpp/fory/thirdparty/BUILD>
  - <https://github.com/apache/fory/blob/main/cpp/fory/thirdparty/flat_hash_map.h>
  - <https://github.com/apache/fory/blob/main/.bazelrc>
  - <https://github.com/apache/fory/blob/main/.github/workflows/ci.yml>
  - <https://github.com/apache/fory/issues?q=label%3Ac%2B%2B>
  - <https://github.com/apache/fory/issues?q=is%3Aopen+label%3Abug>
  - <https://github.com/apache/fory/issues/2958>
  - <https://github.com/apache/fory/releases>
  - <https://github.com/apache/fory/commits/main/cpp>
  - <https://github.com/apache/fory/commits/main/docs/benchmarks/object-serialization/xlang/cpp/README.md>
  - <https://github.com/apache/fory/commits/main/benchmarks/cpp/README.md>
  - <https://github.com/apache/fory/commits/main/benchmarks/cpp/benchmark.cc>
  - <https://github.com/advisories/GHSA-5hmf-8wx5-4qq3>
  - <https://github.com/advisories/GHSA-8f39-v287-78jf>
  - <https://github.com/advisories/GHSA-538v-3wq9-4h3r>
  - <https://github.com/advisories/GHSA-m5gw-83w2-7749>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/apache/fory`) · [data/wave4/enrich/raw/github_com_apache_fory.json](../../../data/wave4/enrich/raw/github_com_apache_fory.json) (enrichment confidence 0.8)

</details>
