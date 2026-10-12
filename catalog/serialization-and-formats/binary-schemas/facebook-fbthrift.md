# fbthrift

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Meta's C++ Thrift serialization and RPC framework; its Binary/Compact protocols encode and decode about 2-3x faster than libprotobuf in Meta's own microbenchmark.

| | |
|---|---|
| **Beats** | Protocol Buffers C++ (protobuf; version not stated), measured with SerializeToArray, SerializeAsString and SerializeToZeroCopyStream |
| **Claimed result** | Source-comment results (2025-11-18, Meta-internal buck2 build, no CPU or protobuf version): serialize 2.2x / 2.7x / 3.1x faster than Protobuf's String row (the Array and ZeroCopy rows call ByteSizeLong twice, inflating the gap to 3.5x); deserialize 1.6-2.1x. CurSe deserialize slower than plain Binary (427.60 vs 396.13 ns). |
| **Workload** | folly::Benchmark microbenchmark in thrift/lib/cpp2/protocol/benchmark: serialize and deserialize a struct of repeated field groups (i32, i64, 8-byte string, list&lt;i32&gt; of 10, map&lt;string,i32&gt; of 5, bool, double) in Small (1 group), Medium (3 groups) and Large (9 groups) sizes, Thrift Binary, Compact and cursor-based (CurSe) protocols against Protobuf equivalents (and an internal Carbon format). |
| **Metric** | latency |
| **Compiler and flags** | buck2 mode opt-clang-lto (Meta-internal fbcode build; clang version and protobuf version not stated) |
| **Adoption** | 2.7k stars |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/facebook/fbthrift) · [benchmark](https://github.com/facebook/fbthrift/blob/main/thrift/lib/cpp2/protocol/benchmark/ThriftProtocolBenchmarks.cpp) |

## Verdict

Meta's folly::Benchmark run pasted into ThriftProtocolBenchmarks.cpp (2025-11-18, buck2 mode/opt-clang-lto, clang, CPU and protobuf version unstated) shows Thrift Binary serializing a synthetic struct of 1/3/9 field groups in 380 ns / 936 ns / 2.72 us versus libprotobuf (no arena) at 832-998 ns / 2.55-3.04 us / 8.32-9.60 us, and deserializing in 396 ns / 1.06 us / 3.15 us versus 661-681 ns / 2.08-2.18 us / 6.58-6.68 us. Both sides build the object inside the timed serialize loop, and the Protobuf Array/ZeroCopy rows pay a redundant size pass.

## Use it when

- You already run folly (or Meta's open-source stack: wangle, fizz, mcrouter) and want a schema-based format plus RPC in one framework
- Encode-heavy services with small-to-medium structs of scalars, short strings, lists and maps, where the \~2.2-3.1x serialize gap over libprotobuf (no arena) in the source-comment numbers matters
- Cross-language service-to-service traffic between C++, Python, Hack, Java or Rust where you control both ends and do not need protobuf wire compatibility
- Streaming or partial access to large structs via CursorBasedSerializer, when fields are read in field-id order and you can skip materializing the object

## Skip it when

- You need protobuf wire compatibility or gRPC interop: Thrift Binary/Compact are different formats; hpp-proto or iguana struct_pb keep the protobuf wire format
- You want a light dependency: the runtime pulls in folly, fizz, wangle, zstd, Boost, OpenSSL, glog/gflags and fmt, and the OSS CMake build breaks often (open issues #707 old-ABI build failure, #682 undefined references, #664 linker errors, #650 configure failure)
- You need a stable versioned API: releases are weekly date tags (v2026.10.05.00, v2026.09.28.00, ...) cut from Meta's monorepo, with no semver or ABI promise
- Big-endian targets with Frozen2 layouts: issue #668 (open) reports Frozen2 serialized data is not portable across byte orders
- Toolchains older than C++20: the CMake build sets cxx_std_20 (GCC 10 needs -fcoroutines)

## How it is fast

The generated cpp2 code writes each field straight into a folly::IOBufQueue with templated BinaryProtocolWriter/CompactProtocolWriter, so there is no reflection or size pre-pass (protobuf computes ByteSizeLong before writing). Containers are plain std::vector/std::map, and Binary uses fixed-width integers that need no varint work. The optional CursorBasedSerializer (CurSe) reads and writes fields in increasing field-id order directly against the buffer without materializing the whole struct, which can skip object construction when you only need some fields.

## Compared with alternatives

Pick fbthrift over hpp-proto or iguana (struct_pb) when you can drop protobuf wire compatibility and want an integrated multi-language RPC stack on folly; pick those two when you must stay on protobuf's wire format with a much lighter dependency footprint. Over Apache Thrift, it buys a modern C++20 code generator, async server and cursor serialization at the cost of a much heavier dependency tree.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | folly, fizz, wangle, zstd, Boost, OpenSSL, zlib, fmt, gflags, glog (thrift compiler alone needs only Boost, CMake and fmt); fetched or built by build/fbcode_builder/getdeps.py |
| **Minimum toolchain** | C++20 (cxx_std_20 in CMakeLists.txt); GCC 10 needs -fcoroutines, GCC 11+ or recent clang preferred |
| **Platforms** | Linux, macOS, Windows (CI badges for all three via getdeps); x86-64 and aarch64 not separately documented |
| **Thread safety** | not documented for generated structs (plain value types with no internal synchronization); protocol writers/readers and CursorSerializationWrapper are per-call objects |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw behind the numbers: the Protobuf Array and ZeroCopy serialize rows call ByteSizeLong() explicitly and then SerializeToArray / SerializeToZeroCopyStream, which call ByteSizeLong() again internally (protobuf message_lite.cc), so Protobuf does two full size passes; this is why the String row, despite an extra copy into an IOBuf, is 12-15% faster than Array. Use the String row as the fair comparator: Binary is about 2.2x (Small), 2.7x (Medium) and 3.1x (Large) faster at serialize, not 2.6-3.5x.
- The benchmark schema is proto2 with unpacked repeated int32 (no [packed=true]), so each of the 10 list elements carries its own tag; proto3 would pack them by default. Together with no protobuf Arena, one-by-one list/map population inside the timed serialize loop and a 5-entry protobuf Map, the setup favors Thrift; the deserialize gap (1.7-2.1x) is the more robust number.
- CurSe's serialize rows write constants straight to the cursor with no struct built, so its 3.6-4.3x over Protobuf is not like-for-like; when every field is read, CurSe deserialize is slightly slower than plain Binary (427.60 ns vs 396.13 ns Small). CursorSerializationWrapper only supports BinaryProtocol (static_assert) and requires fields in increasing field-id order.
- The benchmark is not wired into the OSS CMake build (no CMakeLists in thrift/lib/cpp2/protocol/benchmark; it also needs Meta's Carbon/mcrouter types), so the numbers can only be rerun inside fbcode with buck2 mode/opt-clang-lto.

## Known shortcomings

- Tier C: time/iter numbers match the source comment (2025-11-18) from a Meta-internal buck2 build with no CPU or protobuf version; the timed serialize loop builds objects asymmetrically (protobuf appends list and map entries one by one, Thrift copies prebuilt containers); the CurSe serialize row builds no struct, so its 3.6-4.3x is not like for like. Serialize timing includes object construction.
- Enricher: the Protobuf Array and ZeroCopy serialize rows call ByteSizeLong() themselves and then SerializeToArray / SerializeToZeroCopyStream call it again (protobuf message_lite.cc), so Protobuf does two size passes and its String row is 12-15% faster than Array despite the extra copy; the fair serialize gap against the String row is 2.2x / 2.7x / 3.1x, not up to 3.5x. The schema is proto2 with unpacked repeated int32 and no Arena; CurSe deserialize is slower than plain Binary (427.60 vs 396.13 ns); the benchmark is not in the OSS CMake build and needs Carbon types. Heavy folly/fizz/wangle stack, C++20 required, weekly date tags without semver, OSS build breaks often (open #707, #682, #664, #650), Frozen2 not portable across byte orders (#668).

## Caveats and trade-offs

First-party results pasted into a source comment (dated 2025-11-18); the benchmark code is public but CPU model, core count, clang and protobuf versions are not stated, and it needs the Meta fbcode/buck2 build (mode/opt-clang-lto), so it is not reproducible as published (tier C). Serialize benchmarks build the test object inside the timed loop for Thrift Binary/Compact and Protobuf (createThriftTestData / createProtobufTestData run every iteration), so the ratios mix object population with encoding, and population is not symmetric: Thrift copy-assigns the prebuilt std::vector and std::map, while Protobuf appends the 10 list elements one by one and inserts the 5 map entries one by one into a protobuf Map. The CurSe serialize rows write the constants straight to the cursor writer with no struct built at all, so CurSe-vs-Protobuf serialize ratios are not like-for-like, and the CurSe deserialize row discards what it reads (no doNotOptimizeAway). Deserialize runs exclude serialization via BenchmarkSuspender; the Protobuf String path copies the IOBuf into a std::string inside the timed region, while the Array path parses in place. Protobuf SerializeToArray writes directly into a pre-sized IOBuf (no extra copy); only the SerializeAsString row adds a copyBuffer copy. No protobuf Arena is used. One tiny synthetic schema (i32, i64, 8-byte string, list&lt;i32&gt; of 10, map&lt;string,i32&gt; of 5, bool, double per group; 1, 3 or 9 groups), no realistic string lengths. fbthrift is Facebook's branch of Apache Thrift (GitHub does not mark it a fork; is_fork_of left null). [retier] Asymmetric object construction inside the timed serialize loop (protobuf appends entries one by one, Thrift copies prebuilt containers); Protobuf Array/ZeroCopy rows run two size passes; proto2 schema with unpacked repeated int32, no Arena; CurSe serialize builds no struct. Benchmark not in the OSS CMake build (needs Carbon types). Heavy folly/fizz/wangle dependency stack, C++20, weekly tags without semver, frequent OSS build breaks.

Requires the folly dependency stack and the Thrift compiler and IDL, which is a heavier build than protobuf; fbthrift diverged from Apache Thrift with its own cpp2 code generator, field_ref API, adapters and CursorBasedSerializer. Wire formats differ (Thrift Binary/Compact are larger or comparable but not identical to protobuf varint encoding).

## Maintenance

Very active (weekly tags, latest v2026.10.05.00; Apache-2.0, 2.7k stars), and production-proven at Meta, but the open-source CMake build is heavy and breaks regularly, so plan on pinning a tag and building the whole folly stack.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party folly::Benchmark results pasted into the source comment of thrift/lib/cpp2/protocol/benchmark/ThriftProtocolBenchmarks.cpp (run 2025-11-18, buck2 mode/opt-clang-lto); code is public but the CPU model, clang and protobuf versions are not stated and the build is Meta-internal, so not A.
- **Verifier notes:** All time/iter numbers in the record match the source comment exactly; corrected the caveats: SerializeToArray does not copy, Protobuf population inserts list and map entries one by one while Thrift copies prebuilt containers, and CurSe serialize builds no object, so its 3.6-4.3x is not like-for-like. Metadata from github.com: Apache-2.0, 2.7k stars, not archived, last commit 2026-10-07 (active). Shortcomings: first-party, Meta-internal build, unstated CPU and protobuf version, asymmetric object population inside the timed serialize loop.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-58 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/facebook/fbthrift>
  - <https://github.com/facebook/fbthrift/commits>
  - <https://raw.githubusercontent.com/facebook/fbthrift/main/thrift/lib/cpp2/protocol/benchmark/ThriftProtocolBenchmarks.cpp>
  - <https://raw.githubusercontent.com/facebook/fbthrift/main/thrift/lib/cpp2/protocol/benchmark/ThriftProtocolBenchmarkHelper.h>
  - <https://raw.githubusercontent.com/facebook/fbthrift/main/thrift/lib/cpp2/protocol/benchmark/ThriftProtocolBenchmarkHelper.cpp>
- **Sources the enricher read:**
  - <https://github.com/facebook/fbthrift>
  - <https://raw.githubusercontent.com/facebook/fbthrift/main/README.md>
  - <https://raw.githubusercontent.com/facebook/fbthrift/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/facebook/fbthrift/main/thrift/lib/cpp2/CMakeLists.txt>
  - <https://github.com/facebook/fbthrift/tree/main/thrift/lib/cpp2/protocol/benchmark>
  - <https://raw.githubusercontent.com/facebook/fbthrift/main/thrift/lib/cpp2/protocol/benchmark/ThriftProtocolBenchmarks.cpp>
  - <https://raw.githubusercontent.com/facebook/fbthrift/main/thrift/lib/cpp2/protocol/benchmark/ThriftProtocolBenchmarkHelper.h>
  - <https://raw.githubusercontent.com/facebook/fbthrift/main/thrift/lib/cpp2/protocol/benchmark/ThriftProtocolBenchmarkHelper.cpp>
  - <https://raw.githubusercontent.com/facebook/fbthrift/main/thrift/lib/cpp2/protocol/benchmark/ProtobufTestData.proto>
  - <https://raw.githubusercontent.com/facebook/fbthrift/main/thrift/lib/cpp2/protocol/benchmark/ThriftTestData.thrift>
  - <https://raw.githubusercontent.com/facebook/fbthrift/main/thrift/lib/cpp2/protocol/benchmark/ProtoBufBuild.sh>
  - <https://raw.githubusercontent.com/facebook/fbthrift/main/thrift/lib/cpp2/protocol/CursorBasedSerializer.h>
  - <https://raw.githubusercontent.com/protocolbuffers/protobuf/main/src/google/protobuf/message_lite.cc>
  - <https://github.com/facebook/fbthrift/issues>
  - <https://github.com/facebook/fbthrift/issues/668>
  - <https://github.com/facebook/fbthrift/issues/707>
  - <https://github.com/facebook/fbthrift/tags>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/facebook/fbthrift`) · [data/wave1/enrich/raw/github_com_facebook_fbthrift.json](../../../data/wave1/enrich/raw/github_com_facebook_fbthrift.json) (enrichment confidence 0.75)

</details>
