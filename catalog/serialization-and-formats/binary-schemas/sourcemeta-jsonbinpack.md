# JSON BinPack

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `AGPL-3.0-or-later` · 🟢 active

> JSON Schema-driven binary JSON format; its prototype matched or beat Protobuf, Avro, MessagePack on encoded size across 27 documents.

| | |
|---|---|
| **Beats** | Protocol Buffers, FlatBuffers, Cap'n Proto, MessagePack (and Apache Avro, Thrift, CBOR, BSON, UBJSON, Smile, FlexBuffers) |
| **Claimed result** | This is a size result only; nothing is claimed about speed. In all 27 documents, JSON BinPack (schema-driven) produced the smallest or tied-smallest uncompressed encoding. The comparison covered Protocol Buffers (Python protobuf 3.12.4), FlatBuffers (flatc 1.12.0), Cap'n Proto 0.7.0 (binary and packed), MessagePack (Python msgpack 1.0.0), Avro, Thrift, CBOR, BSON, UBJSON, Smile, FlexBuffers and JSON. On four documents it ties with Avro and/or Protocol Buffers. Example: the ESLint configuration encodes to 64 bytes against 1,141 bytes of JSON (\~94.4% smaller, derived from page data). Across the 27 documents the median reduction against JSON is \~86.8% and the mean \~78.8% (derived from page data; arXiv 2211.12799 reports 86.7% and 78.7%). The schema-driven uncompressed output is smaller than JSON compressed with GZIP -9, LZ4 -12 or LZMA -9 in all 27 documents (derived from page data). |
| **Workload** | Encoded size of 27 real-world JSON documents from SchemaStore, measured uncompressed and after GZIP -9, LZ4 -12 and LZMA -9. There is one document per JSON Taxonomy class (tier x type x redundancy x structure), and each is encoded with JSON BinPack (schema-driven and schema-less) and 13 other formats. JSON BinPack was run through the TypeScript proof of concept (npm jsonbinpack 1.1.x), not the C++ code in this repo. |
| **Metric** | memory |
| **Adoption** | 164 stars |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/sourcemeta/jsonbinpack) · [benchmark](https://benchmark.sourcemeta.com/) |

## Verdict

This is a size result only: on the author's json-size-benchmark (27 SchemaStore documents, one per JSON Taxonomy class), the archived TypeScript prototype (npm jsonbinpack 1.1.x) in schema-driven mode produced the smallest or tied-smallest uncompressed encoding against Protobuf 3.12.4, FlatBuffers 1.12.0, Cap'n Proto 0.7.0, MessagePack 1.0.0, Avro, Thrift, CBOR, BSON, UBJSON, Smile and FlexBuffers (e.g. ESLint config 64 B vs Avro 100 B, Protobuf 161 B, JSON 1,141 B), and it beat GZIP/LZ4/LZMA-compressed JSON on all 27 documents. Compiler and hardware are irrelevant for byte counts, no speed was measured, and the C++ code in this repo is not what was benchmarked.

## Use it when

- Payloads crossing metered, slow or lossy links (mobile, IoT, constrained radio), where bytes on the wire cost more than CPU cycles. This is the use case the README names.
- Small to medium JSON messages, from tens of bytes to a few KB, where general-purpose compression does not pay off. On all 27 benchmark documents, the schema-driven output was smaller than JSON compressed with GZIP -9, LZ4 -12 or LZMA -9.
- You already keep JSON Schema 2020-12 definitions (for example in OpenAPI or AsyncAPI) with tight constraints (bounded integers, enums, const, string length bounds) and want to reuse them instead of writing Protobuf or Avro schemas. That is the enum-heavy, Zod-generated-schema storage use case raised in issue #896.
- Storing or sending many schema-conforming records where repeated string values dominate. Even schema-less, string deduplication gave TravisCI config 185 B vs MessagePack 627 B, and .NET project 748 B vs 919 B (benchmark page).
- Integer, number and enum payloads you can encode with the C++ code today. For fully schema-driven objects, the benchmarked Apache-2.0 TypeScript prototype (npm jsonbinpack, archived) is the implementation that has those encoders.

## Skip it when

- Latency- or throughput-bound paths (IPC, intra-datacenter RPC, zero-copy reads). The README itself points these to FlatBuffers or Cap'n Proto. The repo has no speed benchmark, and decoding always builds a sourcemeta::core::JSON DOM.
- You need the benchmark's schema-driven sizes from C++ today. The compiler maps only integer, number and enum/const schemas; object, array and string schemas fall back to schema-less encoding. The status page lists those mappers and nine object/array/string encodings as missing, and the e2e tests cover schema-less only ('TODO: Test schema-driven too'). The maintainer wrote in issue #896 that this repo is not at feature parity with the JS prototype.
- Schemas that rely on \$ref, allOf/anyOf/oneOf, if/then/else, dependentSchemas, unevaluated\* or recursion. The project's status page lists all of these as not covered yet.
- Decoding untrusted bytes. The README calls decoding non-conforming data undefined behavior. Index and range checks in the decoder are assert()s, which disappear in release builds (for example BYTE_CHOICE_INDEX indexes the choices vector unchecked). The repo has no fuzz tests.
- Schema-less-only use as a MessagePack replacement for tiny documents: the gain is often zero. From the benchmark page data, schema-less mode ties MessagePack byte-for-byte on 10 of 27 documents (e.g. TSLint 51 B vs 51 B) and ESLint is 969 B vs 971 B. Also skip it for closed-source network services that cannot accept AGPL-3.0 and will not buy the commercial license.

## How it is fast

It does not make serialization faster; it makes output smaller by turning schema constraints into bit-level choices. Bounded integers (minimum/maximum/multipleOf) become an offset from the minimum in one byte or a Base-128 varint (ZigZag when unbounded), enums become a one-byte or varint index (zero bytes for the first choice of a top-level enum), const costs zero bytes, and decimals become a ZigZag varint of their digits plus the decimal-point position instead of an 8-byte IEEE double. Strings of 3 or more bytes already seen in the stream become a backward offset (dedup cache capped at 20 MiB), and schema-less values pack a 3-bit type tag with a 5-bit small length or integer into one byte. The largest benchmark gaps, such as ESLint at 64 B schema-driven vs 969 B schema-less, come from schema-typed object and array encodings, which the C++ compiler does not generate yet.

## Compared with alternatives

Pick it over fernBuffer or qdf when your data is already described by JSON Schema and you want the fewest bytes per small document from schema-level savings (enums, bounded integers, constants, string dedup), not a MessagePack-style or compression-tier layout. Pick Bebop, SBE, rkyv or YaFF instead when encode/decode latency is what you are buying, because JSON BinPack publishes no speed numbers at all.

## Integration

| | |
|---|---|
| **Form** | static lib or shared lib (CMake, BUILD_SHARED_LIBS), in two components: runtime (encoder/decoder) and compiler (schema to encoding) |
| **Dependencies** | Sourcemeta Core (json, uri, jsonpointer, jsonschema, numeric, regex, io) and Sourcemeta Blaze (alterschema, canonicalizer), both vendored and pinned by commit in DEPENDENCIES. Core in turn vendors PCRE2 and mimalloc, which is linked into executables on Linux/macOS unless SOURCEMETA_CORE_USE_SYSTEM_ALLOCATOR is set. |
| **Minimum toolchain** | C++23 (CMAKE_CXX_STANDARD 23 from vendored Core defaults). The top level declares CMake 3.16, but vendored Core requires 3.24. CI builds on current GitHub runners with GCC and Clang on Ubuntu, Clang on macOS and MSVC on Windows. No minimum compiler versions are documented. |
| **Platforms** | Linux, macOS, Windows per CI (static and shared builds, plus ASan/UBSan jobs). No architecture-specific code was seen in src/. |
| **Thread safety** | not documented. Encoder and Decoder are stateful wrappers over one std::ostream/std::istream, and the Encoder owns a string back-reference cache. Use one instance per thread and stream (inferred from headers). |
| **Drop-in for the baseline** | no |

## Gotchas

- The Encoder's string cache survives across write() calls. A string repeated in a later document on the same Encoder is written as a backward offset into an earlier document's bytes. Create a fresh Encoder per message if each message must decode on its own (inferred from runtime_encoder.h and cache.cc).
- Resolving shared strings makes the Decoder seek backwards (InputStream::rewind calls seek), so it needs a seekable std::istream. Buffer forward-only socket data first.
- Validate against the schema before encoding. The encoder checks bounds, multipleOf and string lengths with assert() only, so in NDEBUG builds an out-of-range value in an 8-bit encoding is silently cast to uint8_t instead of rejected. compile() also mutates the schema you pass in.
- Sizes from this C++ repo won't match the published benchmark. The e2e fixtures show schema-less sizes equal to the prototype's on some documents (ESLint 969 B, package.json 1,957 B), slightly larger on others (GeoJSON 127 vs 117 B; JSON Resume 2,619 vs 2,612 B, where a TODO notes Smile's 2,613 B now wins) and smaller on Road Risk (254 vs 261 B). Wire compatibility with npm jsonbinpack 1.1.x is not documented.

## Known shortcomings

- Not a speed win: its advantage is encoded size only (smallest or tied-smallest on all 27 documents in the benchmark), and its own README recommends FlatBuffers or Cap'n Proto when runtime speed matters. The size numbers come from the archived TypeScript proof of concept, not this C++ implementation, and the papers are arXiv preprints.
- The C++ implementation cannot yet produce the benchmarked schema-driven sizes: its compiler maps only integer, number and enum/const schemas, and object, array and string schemas fall back to schema-less encoding (maintainer, issue #896, Dec 2025). The benchmarked sizes come from the archived TypeScript prototype. Encoder and decoder bounds checks are assert() only, so release builds skip them, and there are no fuzz tests.

## Caveats and trade-offs

The win is size, not speed. The README concedes runtime efficiency and recommends FlatBuffers or Cap'n Proto for extreme runtime efficiency or zero-copy use. The benchmark covers 27 documents; the '400+ SchemaStore documents' figure comes from arXiv 2201.03051, which does not include JSON BinPack. The benchmark ran the archived TypeScript proof of concept (jviotti/jsonbinpack-poc, npm jsonbinpack 1.1.x, February 2022; the page lists 1.1.1 and the Dockerfile installs 1.1.2). The current C++ implementation in this repo is not measured, and the wire format may have changed since. The benchmark is first-party, by the project's author, and the arXiv write-ups are preprints, not peer-reviewed. The README says the MSc dissertation won the 2022 CAR Hoare Prizes. The competitors are older versions (protobuf 3.12.4, flatc 1.12.0, Cap'n Proto 0.7.0). No compiler or hardware is stated, which is irrelevant for byte counts. The license is dual: AGPL-3.0-or-later or commercial.

Dual-licensed (AGPL-3.0-or-later or paid commercial license) — AGPL's network-copyleft is a real adoption barrier for closed-source SaaS use. Space-efficiency focused, not runtime-efficiency focused; project's own FAQ recommends FlatBuffers/Cap'n Proto instead when zero-copy runtime speed matters. Requires JSON Schema 2020-12 definitions for schema-driven mode.

## Maintenance

Flagged active, but since late 2024 nearly all commits are Core/Blaze dependency bumps (last encoding work October 2024, README revised August 2026), with no tagged releases and a single contributor; the code is copyable under AGPL-3.0-or-later or a paid commercial license, and the benchmarked TypeScript prototype is archived but Apache-2.0.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): reject; tier before verification B, tier now C.
- **Tier reason:** This is the project author's own benchmark (sourcemeta/json-size-benchmark, whose Dockerfile pins the implementation versions). The arXiv write-ups 2211.12799 and 2201.03051 are preprints with no journal reference, so they are not peer-reviewed; an MSc dissertation is not a peer-reviewed paper either. No compiler, flags or CPU are given, which matters little for a size benchmark, but those are the tier rules. That makes it first-party with partial methodology: C.
- **Verifier notes:** This is a scope rejection (not-faster): every number checks out, but JSON BinPack's claim is encoded size, and its own README hands runtime speed to FlatBuffers and Cap'n Proto. Under the keep-flagged-entries policy, it could stay with this shortcoming, tier C. Another shortcoming: the benchmark measured the archived TypeScript proof of concept, not this C++ repo. Metadata checked: GitHub shows the license as NOASSERTION, and the LICENSE file gives AGPL-3.0-or-later or commercial (OSI-approved, copyable). 164 stars, not a fork, last commit 2026-09-23.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://benchmark.sourcemeta.com/>
  - <https://github.com/sourcemeta/jsonbinpack>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/README.md>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/LICENSE>
  - <https://github.com/sourcemeta/json-size-benchmark>
  - <https://github.com/sourcemeta/json-size-benchmark/blob/master/Dockerfile>
  - <https://github.com/sourcemeta/json-size-benchmark/blob/master/DEPENDENCIES>
  - <https://github.com/sourcemeta/json-size-benchmark/blob/master/formats/jsonbinpack/targets.mk>
  - <https://github.com/jviotti/jsonbinpack-poc>
  - <https://registry.npmjs.org/jsonbinpack>
  - <http://export.arxiv.org/api/query?id_list=2201.03051,2211.12799,2201.02089>
- **Sources the enricher read:**
  - <https://github.com/sourcemeta/jsonbinpack>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/README.markdown>
  - https://github.com/sourcemeta/jsonbinpack/tree/main (recursive file tree)
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/LICENSE>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/CMakeLists.txt>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/DEPENDENCIES>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/Makefile>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/Brewfile>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/config.cmake.in>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/cmake/FindCore.cmake>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/.github/workflows/ci.yml>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/doxygen/todo.markdown>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/compiler/include/sourcemeta/jsonbinpack/compiler.h>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/compiler/compiler.cc>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/compiler/encoding.h>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/compiler/CMakeLists.txt>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/runtime/include/sourcemeta/jsonbinpack/runtime.h>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/runtime/include/sourcemeta/jsonbinpack/runtime_encoder.h>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/runtime/include/sourcemeta/jsonbinpack/runtime_decoder.h>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/runtime/include/sourcemeta/jsonbinpack/runtime_encoding.h>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/runtime/include/sourcemeta/jsonbinpack/runtime_encoder_cache.h>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/runtime/include/sourcemeta/jsonbinpack/runtime_output_stream.h>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/runtime/include/sourcemeta/jsonbinpack/runtime_input_stream.h>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/runtime/CMakeLists.txt>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/runtime/cache.cc>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/runtime/encoder_common.cc>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/runtime/encoder_integer.cc>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/runtime/encoder_string.cc>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/runtime/encoder_any.cc>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/runtime/decoder_any.cc>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/src/runtime/input_stream.cc>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/test/e2e/CMakeLists.txt>
  - https://github.com/sourcemeta/jsonbinpack/tree/main/test/e2e (all 29 \*/schema-less/size.txt and \*/document.json)
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/test/runtime/encode_test.cc>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/test/packaging/find_package/hello.cc>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/vendor/core/CMakeLists.txt>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/vendor/core/DEPENDENCIES>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/vendor/core/cmake/Sourcemeta.cmake>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/vendor/core/cmake/common/defaults.cmake>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/vendor/core/cmake/common/compiler/options.cmake>
  - <https://github.com/sourcemeta/jsonbinpack/blob/main/vendor/core/cmake/common/targets/library.cmake>
  - <https://github.com/sourcemeta/jsonbinpack/issues>
  - <https://github.com/sourcemeta/jsonbinpack/issues/896>
  - <https://github.com/sourcemeta/jsonbinpack/issues/864>
  - <https://github.com/sourcemeta/jsonbinpack/issues/858>
  - <https://github.com/sourcemeta/jsonbinpack/issues/860>
  - <https://github.com/sourcemeta/jsonbinpack/commits/main>
  - <https://github.com/sourcemeta/jsonbinpack/releases>
  - <https://github.com/sourcemeta/jsonbinpack/tags>
  - <https://github.com/sourcemeta/jsonbinpack/graphs/contributors>
  - <https://github.com/sourcemeta/json-size-benchmark>
  - <https://github.com/jviotti/jsonbinpack-poc>
  - <https://benchmark.sourcemeta.com/>
  - <https://jsonbinpack.sourcemeta.com/>
  - <https://arxiv.org/abs/2211.12799>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/sourcemeta/jsonbinpack`) · [data/wave4/enrich/raw/github_com_sourcemeta_jsonbinpack.json](../../../data/wave4/enrich/raw/github_com_sourcemeta_jsonbinpack.json) (enrichment confidence 0.85)

</details>
