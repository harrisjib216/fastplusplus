# ProtoCache

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Zero-copy flat binary format for Protobuf schemas; reads messages in place \~20x faster than Protobuf parse-and-traverse.

| | |
|---|---|
| **Beats** | Protobuf |
| **Claimed result** | Decode+traverse+dealloc 132ns vs Protobuf 2620ns (\~19.8x); with reflection 270ns vs Protobuf 8189ns (\~30.3x); ProtoCacheEX full serialization of twitter.proto 101us vs Protobuf 215us (\~2.1x) (ratios derived from page data) |
| **Workload** | Decode+traverse+deallocate (and reflection-based decode+traverse) of a Protobuf-schema message, plus full serialization of the complex twitter.proto dataset, comparing Protobuf, ProtoCache, ProtoCacheEX, FlatBuffers, Cap'n Proto, and Fory. |
| **Metric** | latency |
| **Compiler and flags** | Compiler not stated. The CMake benchmark target (WITH_BENCHMARK=ON) adds -march=native (CMakeLists.txt), and the README build example uses CMAKE_BUILD_TYPE=Release. |
| **Adoption** | 83 stars |
| **Last commit** | 2026-09-07 |
| **Links** | [repository](https://github.com/PeterRK/protocache) · [benchmark](<https://github.com/PeterRK/protocache (README.md benchmark tables; code in test/benchmark)>) |

## Verdict

The README times one test.proto 'Main' message in a single-threaded loop of 1M iterations on the same hot buffer (steady_clock, millisecond resolution). ProtoCache's cast plus full traversal took 132ns vs 2620ns for Protobuf (arena ParseFromString, traversal and arena teardown), and 270ns vs 8189ns when both traverse through reflection. A separate row reports 101us vs 215us for reserializing twitter.proto (ProtoCacheEX vs SerializeToString), but main.cc never calls that benchmark. Compiler, Protobuf version and CPU are not stated. The benchmark target is built with -march=native, and the ProtoCache path runs without bounds checks.

## Use it when

- Read-mostly data that is built once and read many times, such as caches, config or feature blobs held in memory, where you currently run ParseFromString on every read.
- You already have .proto schemas and a protoc toolchain and want FlatBuffers-style zero-copy reads without rewriting the schemas as .fbs or .capnp.
- Schemas with maps you need to look up by key in place: the O(1) perfect-hash index is built into the format.
- Generic, schema-driven consumers such as converters, debug dumpers and pipelines that walk messages through reflection: 270ns vs 8189ns for Protobuf reflection on the project's test message.
- Readers in several languages: the repo ships C++, Python and TypeScript/WASM, and the author maintains Go, Java, C#, Rust and Swift ports.

## Skip it when

- Paths dominated by encoding. Converting a Protobuf message to ProtoCache takes 6493ns vs 557ns for Protobuf SerializeToString, and a fully touched EX object takes 1879ns to reserialize on the same small message.
- When bytes on the wire or on disk matter most: 780B vs 574B for Protobuf uncompressed. The bundled naive zero-run compressor brings it to 571B but adds 427ns to compress and 229ns to decompress.
- Maximum raw read speed on flat data: FlatBuffers is faster on the same test (89ns vs 132ns).
- Untrusted or possibly truncated input, unless you consistently pass the `end` bounds pointer. Bounds checks are opt-in, out-of-bounds read fixes landed as recently as 2026-08-19, and the tree has no fuzz targets.
- Big-endian targets (compile-time #error). Also schemas that need proto2 features (required fields, custom defaults, extensions, groups), oneof exclusivity, unknown-field preservation, bool map keys, or field numbers above 6387 or sparse numbering.

## How it is fast

Decoding is a pointer cast. Scalars are fixed-width 4- or 8-byte words and strings are length-prefixed byte arrays, both read in place, so there is no varint/zigzag decoding, no string copying and no arena allocation. Each message header stores a 2-bit width per field ID, so finding field N takes a mask and a popcount over that bitmap (O(1), no tag scan). Objects of up to 3 words are stored inline and larger ones are reached through a forward relative offset. Repeated scalars are packed arrays exposed as spans, and each map carries a BDZ minimal perfect-hash index (3-hypergraph, SpookyHash), so key lookup is O(1) with no hash table built at read time. Its reflection API uses the same popcount field access, which is why reflective traversal stays cheap next to Protobuf reflection.

## Compared with alternatives

Pick ProtoCache over YaFF, which also keeps .proto schemas and reports faster C++ flat reads, when you need readers outside C++ (YaFF lists multi-language bindings only as roadmap) or perfect-hash map lookup in a compact buffer. Pick it over Apache Fory when reads dominate: on ProtoCache's own table, decode+traverse takes 132ns vs Fory's 1748ns, while Fory gives smaller output (615B vs 780B) and faster encoding.

## Integration

| | |
|---|---|
| **Form** | static lib (protocache or protobuf-free protocache-lite; shared lib optional on Linux/macOS) plus header-only generated code |
| **Dependencies** | Protobuf (libprotobuf for the full library and the Serialize/Deserialize bridge, libprotoc/protoc for code generation) and Threads. protocache-lite needs no Protobuf at link time, but the CMake build still requires Protobuf. GoogleTest is needed for tests and gflags for the CLI tools. |
| **Minimum toolchain** | C++17 compiler, CMake 3.13+; minimum compiler and Protobuf versions not documented |
| **Platforms** | Little-endian only (compile-time #error otherwise). The manually triggered CI matrix covers ubuntu-latest, macos-latest and windows-latest; Windows gets static libraries only. Uses POPCNT when __POPCNT__ is defined, with a portable fallback. There is also a WASM build for the TypeScript binding. |
| **Thread safety** | Not documented. The basic API is const, non-owning views over an immutable buffer with no internal mutation in access.h (inferred from reading the header). EX objects are ordinary mutable C++ objects built on std::vector and std::unique_ptr. |
| **Drop-in for the baseline** | partial — it uses the same .proto files through a protoc plugin and can convert to and from google::protobuf::Message, but the wire format, generated accessor API and several semantics (oneof, presence, deprecated fields, unknown fields) differ, and only a proto3 subset is supported |

## Gotchas

- Every accessor takes an optional `const uint32_t* end`, and the default (nullptr) skips all bounds checking. The published benchmark uses this unchecked path. Pass `end`, or run Detect(), on anything you did not produce yourself.
- Buffers must be 4-byte aligned. 64-bit values and section headers are read through reinterpret_cast from 4-byte-aligned words, so check alignment when you mmap or slice buffers.
- Marking a field `deprecated = true` removes it from the ProtoCache schema view, which is an API change and not just a warning. oneof members are stored as independent fields, and unknown fields are dropped on a decode/re-encode round trip.
- Map indexes are built with a BDZ hash whose seed comes from the clock (steady_clock), so serializing the same map twice can produce different bytes (inferred from perfect_hash.cc). Don't rely on byte-identical output for dedup or content hashing.

## Caveats and trade-offs

No CPU model or compiler is disclosed for the timing tables; the only flag known is -march=native from CMakeLists.txt. The comparison is not like-for-like: ProtoCache 'decode' is a zero-copy view cast over the buffer, while Protobuf does a full ParseFromString into an arena. FlatBuffers is faster on the same read test (89ns vs 132ns). ProtoCache loses elsewhere: serializing from a Protobuf message takes 6493ns vs 557ns for Protobuf (\~11.7x slower), and its data is larger (780B vs 574B). The twitter.proto serialize functions (BenchmarkTwitterSerializePB/PC) exist in test/benchmark but main.cc does not call them, so that row cannot be reproduced from the harness as shipped. Small project (83 stars); numbers are first-party.

Requires an existing Protobuf schema/toolchain (protoc + protoc-gen-pccx plugin); ProtoCache's own plain Serialize is actually slower than Protobuf per its own table (6493ns vs 557ns) — the win is specifically on decode/traverse, not on encode

## Maintenance

Actively maintained by a single author: last commit 2026-09-07, tags up to v1.2.5, 83 stars, and no issues or PRs ever filed. It is BSD-3-Clause and installs as a CMake package, so it is easy to vendor. Recent commits include fixes for out-of-bounds reads and for short-alias handling, as well as several refactors labelled 'by AI'.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README tables show 2620ns (Protobuf) vs 132ns (ProtoCache), 8189 vs 270ns with reflection, and a twitter.proto serialize time of 215us (Protobuf) vs 101us (ProtoCacheEX). The benchmark code is public (test/benchmark/main.cc, protobuf.cc, protocache.cc, common.h), and CMakeLists.txt adds -march=native to the benchmark target. No compiler or CPU model is stated anywhere, so these are first-party numbers with partial methodology: C.
- **Verifier notes:** All quoted numbers are on the README, and the Protobuf comparison is run in the same harness. I only added the '(derived from page data)' marker to the ratios and recorded the known flag. Metadata checks out via gh: BSD-3-Clause, 83 stars, not a fork, not archived, last commit 2026-09-07 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/PeterRK/protocache>
  - <https://github.com/PeterRK/protocache/blob/main/README.md>
  - <https://github.com/PeterRK/protocache/tree/main/test/benchmark>
  - <https://github.com/PeterRK/protocache/blob/main/test/benchmark/main.cc>
  - <https://github.com/PeterRK/protocache/blob/main/test/benchmark/protobuf.cc>
  - <https://github.com/PeterRK/protocache/blob/main/test/benchmark/protocache.cc>
  - <https://github.com/PeterRK/protocache/blob/main/test/benchmark/common.h>
  - <https://github.com/PeterRK/protocache/blob/main/CMakeLists.txt>
  - <https://github.com/PeterRK/protocache/commits/main>
- **Sources the enricher read:**
  - <https://github.com/PeterRK/protocache>
  - <https://github.com/PeterRK/protocache/blob/main/README.md>
  - <https://github.com/PeterRK/protocache/blob/main/data-format.md>
  - <https://github.com/PeterRK/protocache/blob/main/schema.md>
  - <https://github.com/PeterRK/protocache/blob/main/CMakeLists.txt>
  - <https://github.com/PeterRK/protocache/blob/main/include/protocache/access.h>
  - <https://github.com/PeterRK/protocache/blob/main/include/protocache/access-ex.h>
  - <https://github.com/PeterRK/protocache/blob/main/include/protocache/perfect_hash.h>
  - <https://github.com/PeterRK/protocache/blob/main/include/protocache/serialize.h>
  - <https://github.com/PeterRK/protocache/blob/main/include/protocache/utils.h>
  - <https://github.com/PeterRK/protocache/blob/main/include/protocache/extension/utils.h>
  - <https://github.com/PeterRK/protocache/blob/main/src/perfect_hash.cc>
  - <https://github.com/PeterRK/protocache/blob/main/src/hash.cc>
  - <https://github.com/PeterRK/protocache/blob/main/src/access.cc>
  - <https://github.com/PeterRK/protocache/blob/main/src/extension/serialize.cc>
  - <https://github.com/PeterRK/protocache/blob/main/test/benchmark/main.cc>
  - <https://github.com/PeterRK/protocache/blob/main/test/benchmark/common.h>
  - <https://github.com/PeterRK/protocache/blob/main/test/benchmark/protobuf.cc>
  - <https://github.com/PeterRK/protocache/blob/main/test/benchmark/protocache.cc>
  - <https://github.com/PeterRK/protocache/blob/main/test/benchmark/flatbuffers.cc>
  - <https://github.com/PeterRK/protocache/blob/main/test/test.pc.h>
  - <https://github.com/PeterRK/protocache/blob/main/.github/workflows/cpp.yml>
  - <https://github.com/PeterRK/protocache/commits/main>
  - <https://github.com/PeterRK/protocache/commit/d890dfd7fa90f8faabdf03eb6334144f4a1107f1>
  - <https://github.com/PeterRK/protocache/issues>
  - <https://github.com/PeterRK/protocache/pulls>
  - <https://github.com/PeterRK/protocache/tags>
  - <https://github.com/PeterRK/protocache/releases>
  - <https://github.com/yandex/yaff>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/peterrk/protocache`) · [data/wave4/enrich/raw/github_com_peterrk_protocache.json](../../../data/wave4/enrich/raw/github_com_peterrk_protocache.json) (enrichment confidence 0.8)

</details>
