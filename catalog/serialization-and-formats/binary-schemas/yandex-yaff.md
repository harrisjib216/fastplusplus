# YaFF (Yet another Flat Format)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Zero-copy wire format for existing .proto schemas. In-place field reads beat Protobuf parse-then-read \~25-50x and FlatBuffers \~2x.

| | |
|---|---|
| **Beats** | Protobuf |
| **Claimed result** | Flat Layout reads are \~25-50x faster than Protobuf and \~2-2.5x faster than FlatBuffers on flat messages (e.g. 100-field flat read: 25.99ns YaFF vs 1383.74ns Protobuf vs 54.81ns FlatBuffers); hierarchical hot access is \~25x faster than Protobuf and \~3.5x faster than FlatBuffers |
| **Workload** | Median time to read every field out of an already-serialized buffer, for flat messages (10/100 uint64 fields) and a 3-level hierarchical message under hot (\~2KB working set) and cold (\~512MB working set) access patterns, using google/benchmark. |
| **Metric** | latency |
| **Hardware** | AMD EPYC 7713, x86-64 |
| **Compiler and flags** | Clang 20.1.8, CMake Release build (CMake's Release default is -O3 -DNDEBUG; no -march or other extra flags in the benchmark CMakeLists), C++20; google/benchmark 1.9.5, FlatBuffers 24.12.23, Protobuf &gt;=5.26 via Conan (the exact Protobuf version is not stated) |
| **Adoption** | 531 stars |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/yandex/yaff) · [benchmark](https://github.com/yandex/yaff/blob/main/docs/benchmarks/access.md) |

## Verdict

In the authors' google/benchmark suite (Clang 20.1.8, Release build with no -march, AMD EPYC 7713), reading all 100 uint64 fields from a prebuilt buffer took 25.99 ns with YaFF's Flat layout, 54.81 ns with FlatBuffers 24.12.23 and 1383.74 ns with Protobuf (version unpinned, &gt;=5.26); the Protobuf time includes ParseFromString into a fresh message on every iteration. On a 3-level hierarchy with a \~512 MB cold working set the lead shrinks to 1.9x over Protobuf and 1.45x over FlatBuffers (206.64 vs 387.48 vs 300.13 ns).

## Use it when

- A C++ service already uses Protobuf and a hot path parses whole messages only to read some fields. YaFF keeps the .proto and removes the parse: 25.99 ns vs 1383.74 ns to read 100 uint64 fields.
- Dense, mostly populated messages of fixed-width scalars read repeatedly from cache-resident data (the \~2 KB hot working set). There the Flat layout stays within about 1.2-3x of a raw C++ struct.
- Read-mostly blobs (precomputed features, documents, cached responses) that you write once and then mmap or pass around and query in place, where you control both writer and reader.
- An alternative to FlatBuffers when you want one .proto source of truth and Protobuf's schema-evolution rules. In the authors' runs Flat is \~2x faster on flat reads and \~1.45x faster on cold random access.
- Small fixed-shape records (coordinate pairs, key/value entries) pinned to LAYOUT_FIXED and inlined into arrays for single-load, struct-like access, as long as that schema never changes.

## Skip it when

- Buffers from untrusted sources. There is no verifier (unlike FlatBuffers' Verifier), so reading a malformed or hostile buffer is undefined behavior.
- Size-sensitive storage or network links with sparse or small-valued data. YaFF has no varints, so Protobuf with small values is smaller in every measured case: at 50 fields and 5% density, Flat is 294 B vs 14-32 B for Protobuf.
- Non-C++ consumers. Only C++ is supported today and other language bindings are on the roadmap. CI covers only Linux with GCC 13 and Clang 17, so MSVC is untested.
- Schemas that rely on proto2 extensions (their values are dropped), groups (unsupported), field numbers above 8190 (these must be remapped), large maps (stored as a key-sorted array searched with binary search) or keeping unknown fields when converting back to Protobuf (they are lost on ParseTo).
- Code that needs in-place mutation or a stable API. Views are read-only, the only release is v0.1.0 (pre-1.0), and generated code must match the runtime's exact version or it fails to compile.

## How it is fast

Field offsets are computed at code-generation time (a constexpr FLAT_OFFSETS table per message). A Flat-layout read is one bounds compare against a 2-byte header plus one unaligned memcpy load. Values are stored XORed with their default, so unset fields are zero bytes, and nested messages are reached through 32-bit relative offsets. The layout structs are declared [[gnu::packed, gnu::may_alias]] and the generated accessors [[gnu::pure]], so GCC and Clang can eliminate repeated accessor chains such as root.intermediate().leaf().x(), which FlatBuffers users have to cache by hand. The default 'dynamic' layout switches each message at runtime between this Flat layout and a Sparse layout that finds fields through a per-message offset table (close to FlatBuffers' vtable approach); the Flat path is marked as the likely branch.

## Compared with alternatives

Choose YaFF over ProtoCache, the other zero-copy format driven by .proto files, when field-read latency matters more than data size and you want Protobuf's own evolution rules; ProtoCache aims at compact cached data and changes some schema semantics. Choose SBE for fixed-layout, multi-language financial messaging with XML schemas, and Fory when serialize/deserialize throughput matters more than reading fields in place.

## Integration

| | |
|---|---|
| **Form** | static lib (header-only runtime yaff::core + static yaff::proto + protoc-gen-yaff code generator) |
| **Dependencies** | Protobuf &gt;= 5.26 (libprotobuf at runtime, protoc for code generation); CMake &gt;= 3.20; Conan 2 optional (the package is built into a local cache, not published on ConanCenter) |
| **Minimum toolchain** | C++20, CMake 3.20; CI tests GCC 13 and Clang 17; the published benchmarks used Clang 20.1.8 |
| **Platforms** | CI covers only Linux x86-64 (Ubuntu 24.04). The headers have MSVC fallbacks (pragma pack, with no may_alias or pure), but MSVC is not tested. Byte order is not documented: values are read with native-order memcpy and never byte-swapped. |
| **Thread safety** | Not documented. Read views are const, noexcept overlays on immutable bytes and keep no state, so concurrent readers of one buffer look safe. yaff::Serializer is a mutable builder that cannot be copied or moved, so use one per thread. |
| **Drop-in for the baseline** | partial — reuses the .proto and mirrors Protobuf's getter names, but the wire format is new and not binary-compatible with Protobuf, the types live in a separate protoyaff:: namespace, views are read-only, and you convert explicitly with yaff::Serialize and ParseTo |

## Gotchas

- The headline numbers need the Flat layout. Removing a field with plain `reserved` (or deleting it) drops its type, and the dynamic layout then falls back to Sparse, which runs at about FlatBuffers speed (60.11 vs 54.81 ns for 100 fields). To stay on Flat, mark the field `[deprecated = true]` or restate its type in the `reserved_fields` option.
- YaFF treats some changes as breaking that Protobuf calls conditionally safe: changing a default, widening int32 to int64, or turning a singular field into a repeated one. Every enum is open, including proto2 enums that Protobuf treats as closed.
- The fast direct-write API (generated SerializeFoo(ys, ...)) is documented as internal. Its arguments are positional, so removing a middle field can silently shift values onto other fields of the same type. The recommended path builds from a Protobuf object, so writes still pay for Protobuf message construction.
- The buffer must outlive every view and string_view taken from it. Choosing Flat or Sparse for dynamic messages is manual today (Serializer::EnforceDynamicAlternative, default Flat); automatic, data-driven selection is still on the roadmap. Presence detection for float/double fields was fixed on 2026-09-23 (PR #18), so use a recent commit.

## Caveats and trade-offs

Very young project (repo created 2026-04-07), first-party benchmark on a single machine (EPYC 7713, DDR4); the authors say only the ratios generalize. The Protobuf timings include ParseFromString/ParseFromArray of the whole message on every iteration, because Protobuf cannot read fields without parsing. So this compares zero-copy field access with parse-plus-access, not serialization speed. The win shrinks sharply with cold random access (\~512 MB working set): 206.64 vs 387.48 ns vs Protobuf (\~1.9x) and vs 300.13 ns for FlatBuffers (\~1.45x). With hot hierarchical access and hand-cached access chains, FlatBuffers is only \~2.1x slower (20.89 vs 9.81 ns), not 3.5x (derived from page data). The Protobuf version is not pinned (Conan protobuf/[&gt;=5.26]). GitHub reports the license as NOASSERTION, but the LICENSE file is the standard Apache-2.0 notice (Copyright 2026 YANDEX LLC).

Still requires an existing .proto schema (built as a companion physical layout for Protobuf, not a schema replacement); adds adaptive-layout complexity; C++ only today, multi-language bindings are roadmap items

## Maintenance

The Yandex project is active (last commit 2026-09-23) but very young: repo created April 2026, one v0.1.0 release, pre-1.0 API, no GitHub issues filed yet; it is Apache-2.0 (GitHub shows NOASSERTION, but LICENSE is the standard Apache text) and builds with CMake or as a local Conan 2 package.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/benchmarks/access.md compares YaFF directly against Protobuf, FlatBuffers and a raw C++ struct (e.g. Flat/100: 25.99 vs 1383.74 vs 54.81 ns), and it states x25-50 and x2-2.5 (flat) and x25 and x3.5 (hot hierarchical) itself. The code is public in benchmarks/access/flat.cpp and hierarchical.cpp (google/benchmark), and docs/benchmarks/overview.md names Clang 20.1.8, a Release build (no extra flags in the benchmark CMakeLists) and an AMD EPYC 7713, so it meets A.
- **Verifier notes:** All numbers in claimed_speedup match the access.md table and the ratios stated in its text. I read both benchmark sources to confirm the methodology: Protobuf is parsed inside the timed loop, while YaFF and FlatBuffers read the buffer in place. The metadata is correct: 531 stars, last commit 2026-09-23, not archived and not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/yandex/yaff>
  - <https://github.com/yandex/yaff/blob/main/README.md>
  - <https://github.com/yandex/yaff/blob/main/LICENSE>
  - <https://github.com/yandex/yaff/blob/main/docs/benchmarks/access.md>
  - <https://github.com/yandex/yaff/blob/main/docs/benchmarks/overview.md>
  - <https://github.com/yandex/yaff/blob/main/CMakeLists.txt>
  - <https://github.com/yandex/yaff/blob/main/conanfile.py>
  - <https://github.com/yandex/yaff/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/yandex/yaff/blob/main/benchmarks/access/CMakeLists.txt>
  - <https://github.com/yandex/yaff/blob/main/benchmarks/access/flat.cpp>
  - <https://github.com/yandex/yaff/blob/main/benchmarks/access/hierarchical.cpp>
- **Sources the enricher read:**
  - <https://github.com/yandex/yaff>
  - <https://github.com/yandex/yaff/blob/main/README.md>
  - <https://github.com/yandex/yaff/blob/main/docs/index.md>
  - <https://github.com/yandex/yaff/blob/main/docs/quick_start.md>
  - <https://github.com/yandex/yaff/blob/main/docs/integration.md>
  - <https://github.com/yandex/yaff/blob/main/docs/versioning.md>
  - <https://github.com/yandex/yaff/blob/main/docs/benchmarks/access.md>
  - <https://github.com/yandex/yaff/blob/main/docs/benchmarks/overview.md>
  - <https://github.com/yandex/yaff/blob/main/docs/benchmarks/space.md>
  - <https://github.com/yandex/yaff/blob/main/docs/schema/overview.md>
  - <https://github.com/yandex/yaff/blob/main/docs/schema/layouts.md>
  - <https://github.com/yandex/yaff/blob/main/docs/schema/limits.md>
  - <https://github.com/yandex/yaff/blob/main/docs/schema/evolution.md>
  - <https://github.com/yandex/yaff/blob/main/docs/reference/cpp/generated.md>
  - <https://github.com/yandex/yaff/blob/main/docs/reference/cpp/support.md>
  - <https://github.com/yandex/yaff/blob/main/docs/reference/cpp/untrusted.md>
  - <https://github.com/yandex/yaff/blob/main/CMakeLists.txt>
  - <https://github.com/yandex/yaff/blob/main/conanfile.py>
  - <https://github.com/yandex/yaff/blob/main/VERSION>
  - <https://github.com/yandex/yaff/blob/main/NOTICES>
  - <https://github.com/yandex/yaff/blob/main/.github/workflows/ci.yaml>
  - <https://github.com/yandex/yaff/blob/main/include/CMakeLists.txt>
  - <https://github.com/yandex/yaff/blob/main/include/yaff/proto/CMakeLists.txt>
  - <https://github.com/yandex/yaff/blob/main/include/yaff/proto/options.proto>
  - <https://github.com/yandex/yaff/blob/main/include/yaff/base.h>
  - <https://github.com/yandex/yaff/blob/main/include/yaff/message.h>
  - <https://github.com/yandex/yaff/blob/main/include/yaff/array.h>
  - <https://github.com/yandex/yaff/blob/main/include/yaff/buffer.h>
  - <https://github.com/yandex/yaff/blob/main/include/yaff/serializer.h>
  - <https://github.com/yandex/yaff/blob/main/include/yaff/util.h>
  - <https://github.com/yandex/yaff/blob/main/include/yaff/yaff.h>
  - <https://github.com/yandex/yaff/blob/main/include/yaff/any_message.h>
  - <https://github.com/yandex/yaff/blob/main/include/yaff/reflect.h>
  - <https://github.com/yandex/yaff/blob/main/src/compilation/cpp_gen.cpp>
  - <https://github.com/yandex/yaff/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/yandex/yaff/blob/main/benchmarks/access/CMakeLists.txt>
  - <https://github.com/yandex/yaff/blob/main/benchmarks/access/flat.cpp>
  - <https://github.com/yandex/yaff/blob/main/benchmarks/access/hierarchical.cpp>
  - <https://github.com/yandex/yaff/blob/main/benchmarks/access/protoyaff/hierarchical.proto>
  - <https://github.com/yandex/yaff/issues?q=is%3Aissue>
  - <https://github.com/yandex/yaff/pulls?q=is%3Apr>
  - <https://github.com/yandex/yaff/pull/18>
  - <https://github.com/yandex/yaff/pull/16>
  - <https://github.com/yandex/yaff/pull/12>
  - <https://github.com/yandex/yaff/pull/11>
  - <https://github.com/yandex/yaff/releases>
  - <https://github.com/yandex/yaff/commits/main>
  - <https://yaff.tech/docs/integration>
  - <https://yaff.tech/docs/en/llms.txt>
  - <https://github.com/PeterRK/protocache>
  - <https://github.com/aeron-io/simple-binary-encoding>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/yandex/yaff`) · [data/wave4/enrich/raw/github_com_yandex_yaff.json](../../../data/wave4/enrich/raw/github_com_yandex_yaff.json) (enrichment confidence 0.86)

</details>
