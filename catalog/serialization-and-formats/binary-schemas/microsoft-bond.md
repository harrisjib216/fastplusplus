# Microsoft Bond (Compact Binary v1)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Discontinued Microsoft schema-based serializer whose Compact Binary wire format is smaller than FlatBuffers and unpacked Cap'n Proto.

| | |
|---|---|
| **Beats** | FlatBuffers, Cap'n Proto |
| **Claimed result** | JSON Resume: Bond Compact Binary v1 is 2256 bytes vs FlatBuffers 3116 (\~28% smaller), Cap'n Proto binary 3152 (\~28% smaller) and Cap'n Proto packed 2549 (\~11% smaller). Protobuf is smaller than Bond at 2225 bytes. CircleCI-blank: Bond 10 bytes vs FlatBuffers 20 and Cap'n Proto binary 24; packed Cap'n Proto is 6 and Protobuf 5. Across all 27 documents, Bond is smaller than FlatBuffers on 27/27, than binary Cap'n Proto on 26/27 and than packed Cap'n Proto on 21/27, but smaller than Protobuf on only 1/27 (geojson). The benchmark measures size only, not speed. (Percentages and counts derived from page data.) |
| **Workload** | Uncompressed encoded byte size of 27 real-world JSON documents (SchemaStore test-suite samples), each re-encoded with the format's own schema. The quoted cases are the JSON Resume example (3,048 bytes as minified JSON, per the page's JSON row) and CircleCI Definition (Blank) (14 bytes as JSON). |
| **Metric** | memory |
| **Adoption** | 2.6k stars (2,620, microsoft/bond); the open-source project ended in March 2025 and the repo is archived |
| **Last commit** | 2025-04-01 |
| **Links** | [repository](https://github.com/microsoft/bond) · [benchmark](https://github.com/jviotti/binary-json-size-benchmark) |

## Verdict

This is a size-only result from jviotti/binary-json-size-benchmark, an archived suite run by the JSON BinPack author. It re-encoded 27 SchemaStore JSON documents with hand-written schemas, using Bond C++ 9.0.4 Compact Binary v1, flatc 1.12.0, capnp 0.8.0 and Python protobuf 3.15.3. Bond was smaller than FlatBuffers on 27 of 27 documents (JSON Resume: 2,256 vs 3,116 B), than unpacked Cap'n Proto on 26 of 27 and than packed Cap'n Proto on 21 of 27, but larger than Protobuf on 26 of 27 (summed: 7,456 vs 7,146 B). No speed was measured, and no compiler, flags or hardware are given.

## Use it when

- FlatBuffers or Cap'n Proto payloads are too large for your RPC or storage and you don't need zero-copy reads. Summed over the 27 SchemaStore documents, Bond needed 7,456 B against 12,452 B for FlatBuffers and 11,776 B for unpacked Cap'n Proto.
- You already have Bond schemas or stored Compact Binary data (common in Microsoft services) that you must keep reading and writing. C++ 13.0.1 is the final release.
- You need one schema shared by C++, C#, Java and Python, with schema evolution through optional fields and defaults.
- You want to transcode between protocols (for example Compact Binary to JSON) or pass data through without the struct definition, using bonded&lt;T&gt;/bonded&lt;void&gt;.
- You store many records that share one schema. Simple Binary (untagged, with the runtime schema stored once) removes per-field tags, but this benchmark did not measure it.

## Skip it when

- Your goal is the smallest encoding. In the same suite Protobuf was smaller than Bond on 26 of 27 documents, Thrift Compact and unframed Avro were never larger, ASN.1 PER was larger only once, and JSON BinPack was smallest everywhere.
- You need in-place or random access into the buffer, which is the reason to choose FlatBuffers or Cap'n Proto. Bond decodes the whole payload into STL structs, and this benchmark measured no speed at all.
- You parse untrusted input. Bond gets no security fixes after March 2025. Releases 11.0.1 and 13.0.1 fixed CPU DoS, oversized-allocation and deep-nesting stack-overflow issues, and the benchmarked 9.0.4 predates those fixes.
- Your data is mostly floating point. Doubles always take 8 bytes: the GeoJSON sample encoded to 298 B in Bond against 190 B as minified JSON.
- You want a simple build. You need Boost, RapidJSON and the gbc compiler (built with Haskell Stack). The template-heavy code compiles slowly, and Bond's CMake files cannot be pulled in with add_subdirectory.

## How it is fast

This entry's win is about size, not speed. Compact Binary is a tagged format. Each field has a 1-byte header that packs a 5-bit type with a field id of 5 or less; ids up to 255 take 2 bytes. Unsigned integers are LEB128 varints and signed ones are zigzag-encoded first. Strings and containers carry varint counts, and a struct ends with a single BT_STOP byte instead of an offset table or vtable. FlatBuffers and Cap'n Proto spend bytes on alignment padding, pointers or vtables and fixed-width scalars so they can read without decoding, which is why Bond comes out smaller on small, text-heavy documents. Floats and doubles are still fixed 4/8-byte IEEE 754.

## Compared with alternatives

Pick Bond only if you are already invested in Bond, or you need its multi-language schema evolution and transcoding and FlatBuffers/Cap'n Proto size is the complaint. For the fewest bytes, JSON BinPack (smallest on all 27 of the same documents) or a Protobuf-wire implementation such as hpp-proto is the better pick, since Protobuf was smaller than Bond on 26 of 27. For low-latency access, Simple Binary Encoding or the zero-copy siblings target speed, which Bond's catalogued result never measured.

## Integration

| | |
|---|---|
| **Form** | header-only template core, plus a static lib (libbond, optional libbond_apply) when you use runtime-schema or bond.bond types; also needs a gbc codegen step with an optional per-schema _apply.cpp |
| **Dependencies** | Boost headers (1.61+ per the build docs), RapidJSON (git submodule, or an external copy via BOND_FIND_RAPIDJSON), and the gbc compiler. Building from source needs CMake 3.1+ and Haskell Stack 1.5.1+. A vcpkg 'bond' port also exists. |
| **Minimum toolchain** | C++11. The changelog lists Clang 3.4+, GCC 4.7+ and MSVC 2013+ as minimums; the build README says features are limited to VS 2015 and that it was tested with Clang 3.8 and GCC 5.4. The final 13.0.1 added Boost 1.83 support. |
| **Platforms** | Linux, macOS and Windows are documented. CPU architecture requirements are not documented. Compact Binary stores floats as little-endian IEEE 754. |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- The default CompactBinaryWriter/Reader version is v1. v2 adds struct length prefixes, which enable constant-time skipping and bonded&lt;T&gt; deserialization, but its two-pass encoding makes serialization up to 30% slower. Reader and writer must be constructed with the same version.
- Fields marked 'required' are always written; only optional fields left at their default are omitted. The benchmark marked every field required: its one-false-bool document is 3 B in Bond and 0 B in proto3 Protobuf.
- The protocol-selection macros (BOND_COMPACT_BINARY_PROTOCOL and similar) must be defined identically in every translation unit, or you get ODR violations. The docs strongly advise disabling MSVC link-time code generation.
- Errors surface as C++ exceptions: bond::CoreException, bond::StreamException, std::bad_alloc when a payload declares huge containers, and std::range_error from JSON string conversion. The deserialization depth limit is set process-wide through bond::SetDeserializeMaxDepth.

## Known shortcomings

- Not smaller than Protobuf: in the binary-json-size-benchmark suite Protobuf is smaller than Bond on 26 of 27 documents; Bond only beats FlatBuffers and Cap'n Proto on size. The suite is small and run by the author of a competing format (JSON BinPack), and its arXiv write-up is not peer-reviewed.
- Size-only win, no speed measured, and Bond decodes into STL structs rather than reading in place. The benchmark used Bond 9.0.4, which predates fixes for a CPU DoS, oversized allocations and deep-nesting stack overflows (11.0.1, 13.0.1); no security fixes since March 2025. Only Compact Binary v1 was measured.

## Caveats and trade-offs

Size-only benchmark with no CPU time. It is run by Juan Cruz Viotti, author of the competing JSON BinPack format, as a small suite (26 stars). It was archived in Nov 2023 and superseded by benchmark.sourcemeta.com, which no longer includes Bond. The tool versions are stated (Bond C++ 9.0.4, capnp 0.8.0, flatc 1.12.0, protobuf 3.15.3); no compiler, flags or CPU are stated. The arXiv write-up 2201.03051 is an unrefereed preprint. Protobuf is smaller than Bond on 26 of 27 documents, and Thrift, Avro and ASN.1 PER are usually smaller as well. The win holds only against FlatBuffers and Cap'n Proto. Results vary per document; the page has 27 documents, not \~24.

Comparison is static wire-size only, not runtime speed; Bond is not uniformly smallest across all documents or formats (varint formats like Avro/MessagePack/Protobuf beat it on raw size, just not on FlatBuffers/Cap'n Proto); the Bond project itself is discontinued

## Maintenance

Microsoft archived Bond when the open-source project ended on 31 March 2025, with no further bug or security fixes; the last C++ release was 13.0.1 (October 2024). It is MIT-licensed and still installable from source or vcpkg, but the Haskell-built gbc and the Boost dependency make vendoring much heavier than dropping in a header.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification B, tier now C.
- **Tier reason:** The jviotti/binary-json-size-benchmark README tables do show Bond Compact Binary v1 smaller than FlatBuffers and Cap'n Proto. The code is public (benchmark/&lt;doc&gt;/bond/, Makefile) and the tool versions are pinned in DEPENDENCIES. But this is a small suite (26 stars, archived) run by the author of a competing format (JSON BinPack), and its arXiv write-up (2201.03051) is an unrefereed preprint. So it is not a well-known independent suite, and no compiler, flags or CPU are stated. That makes it C, matching how this wave tiered JSON BinPack and the CppSerialization suite.
- **Verifier notes:** The quoted numbers match the page, but the record's '\~2.1KB source JSON' was wrong: minified it is 3,048 bytes. The baseline choice (FlatBuffers, Cap'n Proto) hides that Protobuf beats Bond on size in almost every document. The metadata is confirmed: MIT license, archived, last commit 2025-04-01, abandoned.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** Size totals over the 27 binary-json-size-benchmark documents (derived from page data): Bond 7,456 B vs FlatBuffers 12,452, Cap'n Proto 11,776 (packed 8,145), Protobuf 7,146, Thrift 7,091. Bond beats MessagePack on 25 of 27 documents. The suite's .bond schemas mark every field required, which works against Bond.
- **Pages the verifier opened:**
  - <https://github.com/jviotti/binary-json-size-benchmark>
  - <https://github.com/jviotti/binary-json-size-benchmark/blob/main/README.md>
  - <https://github.com/jviotti/binary-json-size-benchmark/blob/main/DEPENDENCIES>
  - <https://github.com/microsoft/bond>
  - <https://github.com/microsoft/bond/blob/master/README.md>
  - <https://benchmark.sourcemeta.com>
  - <https://arxiv.org/abs/2201.03051>
- **Sources the enricher read:**
  - <https://github.com/microsoft/bond>
  - <https://github.com/microsoft/bond/blob/master/README.md>
  - <https://github.com/microsoft/bond/blob/master/README.old.md>
  - <https://github.com/microsoft/bond/blob/master/cpp/inc/bond/protocol/compact_binary.h>
  - <https://github.com/microsoft/bond/blob/master/cpp/inc/bond/core/bond_version.h>
  - <https://github.com/microsoft/bond/blob/master/cpp/inc/bond/core/traits.h>
  - <https://github.com/microsoft/bond/blob/master/cpp/inc/bond/core/protocol.h>
  - <https://github.com/microsoft/bond/blob/master/cpp/inc/bond/protocol/encoding.h>
  - <https://github.com/microsoft/bond/blob/master/doc/src/why_bond.md>
  - <https://github.com/microsoft/bond/blob/master/doc/src/bond_cpp.md>
  - <https://github.com/microsoft/bond/blob/master/CHANGELOG.md>
  - <https://github.com/microsoft/bond/releases>
  - <https://github.com/microsoft/bond/issues/1215>
  - <https://github.com/microsoft/bond/issues/1111>
  - <https://github.com/microsoft/bond/issues?q=performance>
  - <https://github.com/jviotti/binary-json-size-benchmark>
  - <https://github.com/jviotti/binary-json-size-benchmark/blob/main/README.md>
  - <https://github.com/jviotti/binary-json-size-benchmark/blob/main/DEPENDENCIES>
  - <https://github.com/jviotti/binary-json-size-benchmark/blob/main/skeleton/bond/encode.cpp>
  - <https://github.com/jviotti/binary-json-size-benchmark/blob/main/benchmark/jsonresume/bond/schema.bond>
  - <https://github.com/jviotti/binary-json-size-benchmark/blob/main/benchmark/commitlintbasic/bond/schema.bond>
  - <https://github.com/jviotti/binary-json-size-benchmark/blob/main/benchmark/commitlintbasic/document.json>
  - <https://github.com/jviotti/binary-json-size-benchmark/blob/main/benchmark/geojson/bond/schema.bond>
  - <https://github.com/jviotti/binary-json-size-benchmark/blob/main/benchmark/geojson/protobuf/schema.proto>
  - <https://github.com/jviotti/binary-json-size-benchmark/blob/main/benchmark/geojson/document.json>
  - <https://arxiv.org/abs/2201.03051>
  - <https://benchmark.sourcemeta.com>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/microsoft/bond`) · [data/wave4/enrich/raw/github_com_microsoft_bond.json](../../../data/wave4/enrich/raw/github_com_microsoft_bond.json) (enrichment confidence 0.8)

</details>
