# struct_pack (yalantinglibs)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Reflection and code generation](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only C++ binary serializer that reflects plain structs at compile time, no .proto or macros; \~2-20x faster than protobuf.

| | |
|---|---|
| **Beats** | protobuf |
| **Claimed result** | (derived from page data, estimated from the PNG bar charts; each case is a vector of 20 objects) Serialize: struct_pack \~15-20 ns vs protobuf \~325 ns for 20 rect (\~16-20x), \~100-110 ns vs \~540 ns for 20 person (\~5x), \~665 ns vs \~2,900 ns for 20 monster (\~4.4x); msgpack \~1,100-8,000 ns on the same cases. Deserialize: \~210 ns vs protobuf \~1,090 ns (20 rect, \~5x), \~960 ns vs \~2,130 ns (20 person, \~2.2x), \~7,600 ns vs \~17,500 ns (20 monster, \~2.3x). Repo README: '2-20x faster than protobuf' |
| **Workload** | Serialize and deserialize vectors of 20 objects of three struct shapes (rect: 4 int32_t; person: int64_t id, std::string name, int age, double salary; nested Monster with strings, vectors and an enum), with pre-initialized objects and pre-allocated buffers, averaged over one million iterations; compared to protobuf, msgpack and flatbuffers (flatbuffers serialize only), using compile-time reflection (no macros for aggregate types) |
| **Metric** | latency |
| **Hardware** | Intel(R) Xeon(R) Platinum 8163 CPU @ 2.50GHz |
| **Compiler and flags** | Alibaba Clang 13 (stated on the page). Flags are not on the page; cmake/build.cmake defaults CMAKE_BUILD_TYPE to Release (-O3 -DNDEBUG), and the benchmark target defines STRUCT_PACK_OPTIMIZE and MSGPACK_NO_BOOST |
| **Adoption** | 2.2k stars |
| **Last commit** | 2026-09-21 |
| **Links** | [repository](https://github.com/alibaba/yalantinglibs) · [benchmark](https://github.com/alibaba/yalantinglibs/blob/main/website/docs/en/struct_pack/struct_pack_intro.md) |

## Verdict

Project bar charts measured on Alibaba Clang 13 on a Xeon Platinum 8163 @ 2.5 GHz, in a CMake Release build with STRUCT_PACK_OPTIMIZE, show average time for a vector of 20 objects against protobuf's SerializeToString/ParseFromString. Serialize is \~16-20x faster for 20 four-int rects (\~15-20 ns vs \~325 ns), \~5x for persons and \~4.4x for Monsters; deserialize is \~5x, \~2.2x and \~2.3x faster (Monsters \~7.6 µs vs \~17.5 µs). Values are read from PNGs, and the benchmark committed when the charts were added used 100,000 iterations and a 3-character name ("tom", consistent with the \~400 B size chart), whereas the page says one million and today's code uses a 1,024-char name.

## Use it when

- C++-to-C++ messaging or persistence where both sides compile the same struct definitions: RPC between your own services, cache blobs, snapshots. It is the wire format of the same repo's coro_rpc.
- Payloads that are mostly trivially copyable data (POD structs, std::vector/std::array of PODs). These become one memcpy, which is where the \~16-20x serialize gap over protobuf appears (the 20-rect case).
- Hot paths that serialize small-to-medium nested structs with strings, vectors and enums, where protobuf's generated serialize/parse took \~2-5x longer in the project's person and Monster cases.
- Codebases that want serialization without a protoc step, IDL files or hand-written serialize() functions, on C++17 or newer (tested down to GCC 9.1, Clang 6, MSVC 19.20).
- Reading one field from a large blob (get_field&lt;T, I&gt;()), or zero-copy deserialization into std::string_view/std::span members pointing into a buffer you keep alive.

## Skip it when

- You need cross-language readers, schema files for other teams, or protobuf wire compatibility. The documented implementation is C++ only (the same repo's struct_pb handles protobuf-format C++ structs without protoc).
- Bandwidth- or storage-bound traffic of small integers. Integers are fixed-width by default, so 20 rects encode to \~325 B vs \~255 B for protobuf and \~220 B for msgpack in the project's own size chart, and msgpack is also smaller for Monsters (\~1,540 B vs \~1,830 B). Turn on ENCODING_WITH_VARINT/USE_FAST_VARINT or pick a varint format.
- Schemas that change in ways other than appending fields. You may not delete, reorder or retype fields, compatible&lt;T, version&gt; numbers must strictly increase (otherwise the docs call the result undefined behavior), and compatible fields inside structs held in containers or unordered_maps had data-corruption and 'not supported' bugs fixed only in 2025-2026 (issues #1026, #1167).
- Parsing hostile input where you need a proven hardened decoder. Reads are bounds-checked (they return no_buffer_space) and stream reads cap unconfirmed preallocation at 1 MB, but the repo has no fuzz tests, and in release mode the type check is only a 31-bit hash, which the docs say leads to undefined behavior on collision.
- Big-endian targets. Data is always stored little-endian, so the memcpy fast paths are off for multi-byte types there, and the docs say performance is lower.

## How it is fast

The field list comes from compile-time aggregate reflection: it counts members by probing brace-initialization with a type that converts to anything (the Boost.PFR/magic_get trick). All type dispatch is resolved in templates, so per-field code is inlined with no virtual calls or runtime schema walk, and the type check is an MD5 hash computed at compile time, so the runtime check is one 32-bit compare. Trivially copyable structs, and contiguous containers of them, are written and read with a single memcpy on little-endian hosts. Serialize first computes the exact output size, grows the buffer once (skipping zero-fill through a private-member hack on libstdc++, libc++ and MSVC STL), then writes through an unchecked pointer, with one length-prefix width (1/2/4/8 bytes) chosen per message from the largest container.

## Compared with alternatives

Pick struct_pack over FBE (the other protobuf-baseline entry) when both ends are C++ and you want no domain-model/codegen step; FBE generates code for 9 languages. Pick it over bitsery when you don't want to write a serialize(S&, T&) function per type. Prefer Cista++ for in-place access to mmapped data and libFuzzer-checked parsing, or bitsery for the smallest payloads. struct_pack's edge over Cista++ is that it works on std::string, std::vector and other std containers directly rather than Cista's own data:: types.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for struct_pack itself, but it needs the bundled include/ylt/reflection headers and include/ylt/util/expected.hpp. Packaged for vcpkg, Homebrew, CMake FetchContent/add_subdirectory and Bazel. The asio/async_simple dependencies of the monorepo apply only to its RPC/HTTP libraries. |
| **Minimum toolchain** | C++17 (tested minimums GCC 9.1, Clang 6.0, MSVC 19.20/VS2019). C++20 also memcpy's user-defined trivial contiguous containers. CI runs GCC 11.2, Clang 14, AppleClang 14 and MSVC 19.33. |
| **Platforms** | any: little- and big-endian, 32- and 64-bit (memcpy fast paths only on little-endian). CI runs on Ubuntu, macOS and Windows. |
| **Thread safety** | Not documented. The API is stateless free functions over caller-owned objects and buffers, and the only static state seen in unpacker.hpp is thread_local, so concurrent calls on distinct buffers appear safe. |
| **Drop-in for the baseline** | no |

## Gotchas

- Debug and release builds write different bytes. Debug embeds the full type-name string to catch hash collisions, while release stores only the hash. If DISABLE_META_INFO is set on one side it must be set on the other, or behavior is undefined.
- Trivially copyable structs go out in their in-memory layout, padding included. The type hash covers alignment, so an alignas/#pragma pack mismatch fails cleanly instead of misreading, but #pragma pack users must also specialize struct_pack::pack_alignment&lt;T&gt; (and struct_pack::alignment&lt;T&gt; when combined with alignas).
- Buffers are resized without zero-fill by writing private members of std::string/std::vector&lt;char&gt; (string_thief/vector_thief), with a fallback to resize() under ASan. This caused random MSVC crashes with std::wstring (issue #630, fixed 2024), and an MSVC-only bug copied data between map entries of types with a user-defined copy assignment (issue #1140, fixed Dec 2025).
- Errors come back as struct_pack::err_code or expected&lt;T, err_code&gt; (a breaking change in Jan 2024); the only throw is std::runtime_error for an unknown struct_pack_id when serializing a polymorphic unique_ptr&lt;base&gt;. Reflection is capped at 256 fields (124 for YLT_REFL on MSVC without /Zc:preprocessor), and very large structs have overflowed small debug stacks (issue #1132, fixed Dec 2025).

## Known shortcomings

- The person-benchmark charts (committed 2023-07-05) likely come from a 100,000-iteration run with a 3-character name, not the one-million-iteration, 1,024-character setup the page and current code describe. For small integers its output is larger than protobuf's and msgpack's.

## Caveats and trade-offs

Numbers are only in PNG bar charts (no text table), so the figures are estimates from the chart axes. Each chart case is a vector of 20 objects. Alibaba Clang 13 is Alibaba's internal Clang build, which limits exact reproduction. The charts were added to the docs on 2023-07-05 and are not tied to a stated commit; the current benchmark.cpp also runs single-object cases and struct_pb. The docs compare against protobuf/msgpack/flatbuffers, not Boost.Serialization or cereal, hence baseline_in_list=false.

Works best on aggregate structs; non-aggregate types (private members, custom order) need the YLT_REFL macro. Forward/backward compatibility requires explicitly wrapping new fields in struct_pack::compatible&lt;T,version&gt;. Ships as part of a large multi-library monorepo (yalantinglibs) rather than a standalone single-purpose dependency.

## Maintenance

Actively maintained: last commit 2026-09-21, release 0.6.1 in April 2026, Apache-2.0. struct_pack is header-only and can be vendored with its reflection and util headers, but it ships inside a large multi-library monorepo and had schema-evolution fixes as recently as April 2026.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** struct_pack_intro.md charts compare struct_pack with protobuf, msgpack and flatbuffers using public code (src/struct_pack/benchmark/benchmark.cpp, config.hpp: OBJECT_COUNT=20, ITERATIONS=1000000). The page states Alibaba Clang 13 and a Xeon Platinum 8163. Flags come from the committed build config: cmake/build.cmake defaults CMAKE_BUILD_TYPE to Release, matching how earlier verdicts treated a default Release build.
- **Verifier notes:** Record's person serialize figure (\~120 ns, \~4.4x) was slightly off; pixel measurement gives \~100-110 ns vs \~540 ns (\~5x). 'Used internally at Alibaba' is not stated in the README or the benchmark page, so it was removed from stars_or_usage. Metadata correct (Apache-2.0, 2,181 stars, last commit 2026-09-21, active).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/alibaba/yalantinglibs>
  - <https://github.com/alibaba/yalantinglibs/blob/main/README.md>
  - <https://github.com/alibaba/yalantinglibs/commits>
  - <https://github.com/alibaba/yalantinglibs/blob/main/website/docs/en/struct_pack/struct_pack_intro.md>
  - <https://github.com/alibaba/yalantinglibs/blob/main/website/docs/en/struct_pack/images/struct_pack_bench_serialize.png>
  - <https://github.com/alibaba/yalantinglibs/blob/main/website/docs/en/struct_pack/images/struct_pack_bench_deserialize.png>
  - <https://github.com/alibaba/yalantinglibs/tree/main/src/struct_pack/benchmark>
  - <https://github.com/alibaba/yalantinglibs/blob/main/src/struct_pack/benchmark/CMakeLists.txt>
  - <https://github.com/alibaba/yalantinglibs/blob/main/src/struct_pack/benchmark/config.hpp>
  - <https://github.com/alibaba/yalantinglibs/blob/main/src/struct_pack/benchmark/benchmark.cpp>
  - <https://github.com/alibaba/yalantinglibs/blob/main/CMakeLists.txt>
  - <https://github.com/alibaba/yalantinglibs/blob/main/cmake/build.cmake>
  - <https://github.com/alibaba/yalantinglibs/blob/main/cmake/develop.cmake>
- **Sources the enricher read:**
  - <https://github.com/alibaba/yalantinglibs>
  - <https://github.com/alibaba/yalantinglibs/blob/main/README.md>
  - <https://github.com/alibaba/yalantinglibs/blob/main/website/docs/en/struct_pack/struct_pack_intro.md>
  - <https://github.com/alibaba/yalantinglibs/blob/main/website/docs/en/struct_pack/struct_pack_tips.md>
  - <https://github.com/alibaba/yalantinglibs/blob/main/website/docs/en/struct_pack/struct_pack_layout.md>
  - <https://github.com/alibaba/yalantinglibs/blob/main/website/docs/en/struct_pack/struct_pack_type_system.md>
  - <https://github.com/alibaba/yalantinglibs/blob/main/website/docs/en/struct_pack/images/struct_pack_bench_serialize.png>
  - <https://github.com/alibaba/yalantinglibs/blob/main/website/docs/en/struct_pack/images/struct_pack_bench_deserialize.png>
  - <https://github.com/alibaba/yalantinglibs/blob/main/website/docs/en/struct_pack/images/struct_pack_bench_binary_size.png>
  - <https://github.com/alibaba/yalantinglibs/blob/main/website/docs/en/struct_pb/struct_pb_intro.md>
  - <https://github.com/alibaba/yalantinglibs/blob/main/include/ylt/struct_pack.hpp>
  - <https://github.com/alibaba/yalantinglibs/tree/main/include/ylt/struct_pack>
  - <https://github.com/alibaba/yalantinglibs/blob/main/include/ylt/struct_pack/unpacker.hpp>
  - <https://github.com/alibaba/yalantinglibs/blob/main/include/ylt/struct_pack/packer.hpp>
  - <https://github.com/alibaba/yalantinglibs/blob/main/include/ylt/struct_pack/util.h>
  - <https://github.com/alibaba/yalantinglibs/blob/main/include/ylt/struct_pack/marco.h>
  - <https://github.com/alibaba/yalantinglibs/blob/main/include/ylt/struct_pack/reflection.hpp>
  - <https://github.com/alibaba/yalantinglibs/blob/main/include/ylt/struct_pack/calculate_size.hpp>
  - <https://github.com/alibaba/yalantinglibs/blob/main/include/ylt/struct_pack/endian_wrapper.hpp>
  - <https://github.com/alibaba/yalantinglibs/blob/main/include/ylt/reflection/member_count.hpp>
  - <https://github.com/alibaba/yalantinglibs/blob/main/include/ylt/version.hpp>
  - <https://github.com/alibaba/yalantinglibs/blob/main/src/struct_pack/benchmark/benchmark.cpp>
  - <https://github.com/alibaba/yalantinglibs/blob/main/src/struct_pack/benchmark/config.hpp>
  - <https://github.com/alibaba/yalantinglibs/blob/main/src/struct_pack/benchmark/CMakeLists.txt>
  - <https://github.com/alibaba/yalantinglibs/blob/main/src/struct_pack/benchmark/struct_pack_sample.hpp>
  - <https://github.com/alibaba/yalantinglibs/blob/main/src/struct_pack/benchmark/protobuf_sample.hpp>
  - <https://github.com/alibaba/yalantinglibs/blob/333b1299/src/struct_pack/benchmark/struct_pack_sample.hpp>
  - <https://github.com/alibaba/yalantinglibs/blob/333b1299/src/struct_pack/benchmark/config.hpp>
  - <https://github.com/alibaba/yalantinglibs/commit/66da6c93>
  - <https://github.com/alibaba/yalantinglibs/commits/main/src/struct_pack/benchmark/struct_pack_sample.hpp>
  - <https://github.com/alibaba/yalantinglibs/commits/main/website/docs/en/struct_pack/struct_pack_intro.md>
  - <https://github.com/alibaba/yalantinglibs/commits/main/include/ylt/struct_pack>
  - <https://github.com/alibaba/yalantinglibs/commits/main>
  - <https://github.com/alibaba/yalantinglibs/blob/main/src/struct_pack/examples/CMakeLists.txt>
  - <https://github.com/alibaba/yalantinglibs/releases>
  - <https://github.com/alibaba/yalantinglibs/issues>
  - <https://github.com/alibaba/yalantinglibs/issues/1140>
  - <https://github.com/alibaba/yalantinglibs/issues/1073>
  - <https://github.com/alibaba/yalantinglibs/issues/1026>
  - <https://github.com/alibaba/yalantinglibs/issues/1167>
  - <https://github.com/alibaba/yalantinglibs/issues/630>
  - <https://github.com/alibaba/yalantinglibs/issues/1132>
  - <https://github.com/chronoxor/FastBinaryEncoding>
  - <https://github.com/felixguendling/cista>
  - <https://github.com/fraillt/bitsery>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/alibaba/yalantinglibs`) · [data/wave4/enrich/raw/github_com_alibaba_yalantinglibs.json](../../../data/wave4/enrich/raw/github_com_alibaba_yalantinglibs.json) (enrichment confidence 0.8)

</details>
