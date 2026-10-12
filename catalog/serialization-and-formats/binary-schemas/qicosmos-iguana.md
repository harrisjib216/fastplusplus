# iguana (struct_pb)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> Header-only C++17/20 reflection serializer whose struct_pb mode writes protobuf proto3 wire format from plain structs; claims 2.4x/3.4x over protobuf.

| | |
|---|---|
| **Beats** | Google protobuf C++ (SerializeToString / ParseFromString) |
| **Claimed result** | In the benchmark monster scenario struct_pb serialization is 2.4x protobuf and deserialization is 3.4x protobuf (README text lang/struct_pb_intro.md, translated from Chinese: 'serialization speed is 2.4 times protobuf, deserialization 3.4 times'). |
| **Workload** | Monster message (game-monster struct with nested fields), serialize and deserialize loops of iguana::to_pb / from_pb against protobuf's generated code, in benchmark/pb_benchmark.cpp (bench3). |
| **Metric** | throughput |
| **Compiler and flags** | Not stated for the claim. In-repo CMakeLists.txt: default build type Release with CMAKE_CXX_FLAGS_RELEASE '-O3' plus '-Wall -pthread -g' (no -DNDEBUG), C++17 by default, libstdc++ unless LINKLIBC++; protobuf is whatever find_package(Protobuf) finds. |
| **Adoption** | 1.3k stars |
| **Last commit** | 2026-08-12 |
| **Links** | [repository](https://github.com/qicosmos/iguana) · [benchmark](https://github.com/qicosmos/iguana/blob/master/lang/struct_pb_intro.md) |

## Verdict

First-party sentence (lang/struct_pb_intro.md, 2024): in a 'monster' message benchmark, struct_pb serializes 2.4x and deserializes 3.4x faster than Google protobuf's generated C++ code (SerializeToString/ParseFromString). No hardware, compiler, protobuf version or results file is published; the in-repo bench3 is a 100,000-iteration high_resolution_clock loop built at -O3 -g without -DNDEBUG, and the yalantinglibs harness the doc points to times an empty struct_pb Monster against a full protobuf one.

## Use it when

- You own both C++ endpoints (or must talk proto3 binary to an existing service) and want to keep plain structs instead of protoc-generated classes.
- Small-to-medium messages with short strings and few nested messages, decoded into fresh objects without a protobuf Arena, where libprotobuf's per-submessage and per-string heap allocations dominate.
- Header-only builds where adding libprotobuf and protoc to the toolchain is unwelcome; also gives JSON/XML/YAML from the same struct definitions.
- Already using yalantinglibs (struct_pb there is this library re-exported) or coro_rpc.

## Skip it when

- You need proto2 (required fields, extensions), services, custom options, proto3 JSON mapping or text format; the conformance target covers only the proto3 binary subset.
- Schemas are owned as .proto files across languages: field numbers come from C++ member order unless you pin them with YLT_REFL_PB or annotations, so a reordered member silently changes the wire format.
- Messages dominated by repeated fixed-width or zigzag integers: issue #301 (2024-09) reported from_pb slower than protobuf ParseFromString on the bench's RepeatIguanaTypeMsg; it was closed with no recorded fix or numbers.
- You already decode into protobuf Arenas or reuse message objects: the speedup was never measured against those modes.
- You need documented thread safety or a stable ABI: the README FAQ says iguana is not thread-safe yet and tells users to lock around calls.

## How it is fast

Field layout and wire types are resolved at compile time and inlined, so encode/decode is a straight-line walk over members instead of protobuf's table-driven parser over heap-allocated message objects. Decoding writes into plain std::string/std::vector members (std::string_view members give zero-copy strings), sub-messages are embedded by value rather than heap-allocated, output strings are resized without zero-fill (resize_and_overwrite in C++23, otherwise a private-member access hack on libstdc++/libc++/MSVC STL), and an optional SEQUENTIAL_PARSE fast path matches fields in declaration order before falling back to a field-number map.

## Compared with alternatives

Pick iguana over hpp-proto when you want protobuf wire compatibility straight from existing C++ structs with no .proto files or codegen step; pick hpp-proto when the schema lives in .proto files, you need proto2, or you want a published Linux comparison against Google protobuf with arenas and stated hardware. Apache Fory C++ and ProtoCache are faster in their own benchmarks but use their own wire formats, not protobuf's.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | frozen (bundled in the repo); no protobuf runtime for to_pb/from_pb |
| **Minimum toolchain** | C++17 (CI: GCC 11.2, Clang 14, AppleClang, MSVC 19.33); C++20 drops the need for YLT_REFL; optional C++26 reflection path needs GCC 16.1 with -std=gnu++26 -freflection |
| **Platforms** | any platform with those compilers (CI on Linux, macOS, Windows); string resize hack targets libstdc++, libc++ and MSVC STL, other standard libraries fall back to std::string::resize |
| **Thread safety** | README FAQ: 'Not yet', lock around calls. from_pb uses function-local static member tables and a thread_local recursion counter. |
| **Drop-in for the baseline** | partial: wire-compatible with proto3 binary (iguana's bench asserts byte-identical output for most test messages), but the API is free functions on user structs, not protobuf message classes |

## Gotchas

- Harness flaw in the reproduction path the claim names: lang/struct_pb_intro.md says to reproduce the 2.4x/3.4x monster numbers with the struct_pack benchmark in alibaba/yalantinglibs. There, src/struct_pack/benchmark/struct_pb_sample.hpp declares Monster(Vec3 a, int32_t b, int32_t c, std::string d, std::string e, Color f, std::vector&lt;Weapon&gt; g, Weapon h, std::vector&lt;Vec3&gt; i) {} with an empty body (present since PR #680 of 2024-05-29, the PR that brought this struct_pb into yalantinglibs, and still at HEAD), so create_monsters() builds struct_pb Monsters with empty name/inventory, no weapons, no path and uninitialized pos/mana/hp/color, while protobuf_sample.hpp fills every field. The MONSTER and MONSTERS rows there time struct_pb on a message holding only a few scalar fields (no strings, weapons or path; protobuf's full monster is about 112 bytes on the wire, derived from the field values) and read indeterminate values. iguana's own benchmark/pb_benchmark.cpp bench3 builds both monsters correctly, so it is unclear which harness produced the published ratios.
- iguana's own pb_benchmark.cpp hard-codes '#define SEQUENTIAL_PARSE' (as does yalantinglibs' benchmark.cpp), while the CMake option ENABLE_SEQUENTIAL_PARSE defaults to OFF, so the measured from_pb is a non-default fast path; the input always arrives in declaration order, so it always hits.
- The deserialize loops build protobuf messages without an Arena (arena.h is included, data_def.proto sets cc_enable_arenas, but no Arena is used), and all monster strings fit in std::string's small-string buffer, so the gap mostly reflects libprotobuf's roughly a dozen heap allocations per Monster (sub-messages, repeated elements, string objects) against iguana's few vector allocations.
- from_pb does not clear the target: parsing into a reused object appends to repeated (std::vector) fields instead of replacing them, unlike ParseFromString. Malformed input throws std::invalid_argument or std::runtime_error, and nesting deeper than 100 throws.

## Known shortcomings

- Tier C: the 2.4x serialize / 3.4x deserialize vs protobuf sentence is first-party with no hardware, compiler or result files, and the benchmark never uses the parsed objects (dead-code-elimination risk); the same sentence appears in the yalantinglibs docs (namespace struct_pb = iguana). Not a duplicate of the wave 4 yalantinglibs entry, which covers struct_pack. Filed under binary-schemas by category override.
- Enricher: lang/struct_pb_intro.md says to reproduce the 2.4x/3.4x with yalantinglibs' struct_pack benchmark, where src/struct_pack/benchmark/struct_pb_sample.hpp has a Monster(...) constructor with an empty body (since PR #680, 2024-05-29, still at HEAD), so struct_pb Monsters have no name, inventory, weapons or path and uninitialized pos/mana/hp/color while protobuf_sample fills every field; the MONSTER/MONSTERS rows time unequal work (iguana's own pb_benchmark.cpp bench3 builds both correctly, so the claim's harness is unclear). pb_benchmark.cpp hard-codes #define SEQUENTIAL_PARSE (CMake default OFF, a non-default fast path); protobuf runs without an Arena; all strings fit the small-string buffer so the gap is mostly protobuf heap allocations; issue #301 found from_pb slower than ParseFromString on repeated fixed/zigzag fields (closed without a fix shown); from_pb appends to vectors of a reused object.
- Domain set to serialization-and-formats to match its binary-schemas category.

## Caveats and trade-offs

First-party claim in a Chinese-language doc; the numbers carry no hardware, compiler version or protobuf version, and the doc points to 'the benchmark in struct_pack' (alibaba/yalantinglibs) for reproduction. The identical 2.4x / 3.4x sentence is in yalantinglibs' struct_pb docs (website/docs/zh and en/struct_pb/struct_pb_intro.md), where struct_pb is iguana re-exported (include/ylt/struct_pb/struct_pb_impl.hpp: 'namespace struct_pb = iguana;'); yalantinglibs' published struct_pack charts (Alibaba Clang 13, Xeon Platinum 8163) cover struct_pack, not struct_pb. The in-repo benchmark/pb_benchmark.cpp prints iguana/protobuf ratios from a high_resolution_clock around whole loops (default 100000 iterations) but commits no results; deserialization allocates a fresh object per iteration for both libraries, and the parsed objects are never used, so the header-only from_pb could be partly optimised away while protobuf's out-of-line ParseFromString cannot (a risk, not demonstrated). The claim may predate the current code, which was refactored heavily (C++26 reflection; a draft JSON DOM parser PR #386 is still open). The README FAQ answer 'Is iguana high performance? Yes, because it is based on compile-time reflection' has no numbers. No JSON-versus-RapidJSON or other numbers found in README or docs. The claim is about the protobuf binary wire format, so binary-schemas fits better than serialization-json. [retier] First-party sentence (2.4x serialize / 3.4x deserialize vs protobuf) with no hardware, compiler or result files. The documented reproduction harness builds struct_pb Monsters with an empty constructor body (yalantinglibs PR #680) against fully populated protobuf Monsters; iguana's pb_benchmark.cpp hard-codes SEQUENTIAL_PARSE (non-default), runs protobuf without an Arena, uses small-string-buffer-sized strings and never consumes parsed objects. Issue #301 reported from_pb slower than ParseFromString on repeated fixed/zigzag fields.

Header-only C++17/C++20 (C++26 reflection path with GCC 16.1); structs defined in C++ with YLT_REFL / YLT_REFL_PB instead of .proto files and protoc. Protobuf support is proto3 binary wire only: no proto2 required fields, extensions, custom options or services, no proto3 JSON or text format; official conformance runs only the binary subset.

## Maintenance

Actively maintained (last commit 2026-08-12, C++26 reflection port in May 2026) and Apache-2.0 header-only, so easy to vendor; but the speed claim is first-party, predates the 2026 refactor, and its named reproduction harness benchmarks unequal monster payloads, so treat 2.4x/3.4x as unverified and measure against protobuf with arenas on your own messages.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party one-sentence claim in lang/struct_pb_intro.md ('序列化速度是protobuf的2.4倍，反序列化是protobuf的3.4倍') with no hardware, compiler or protobuf version; the in-repo benchmark/pb_benchmark.cpp (bench3, monster) is public but no results are committed, so C.
- **Retiered** C to D: The documented reproduction harness (yalantinglibs struct_pb_sample.hpp) constructs empty struct_pb Monsters against fully populated protobuf Monsters, so the published 2.4x/3.4x may time unequal work, and iguana's own pb_benchmark.cpp measures a non-default SEQUENTIAL_PARSE fast path; no hardware, compiler or result files. Directional only (not rejected because iguana's own bench3 builds both sides correctly and the claim's harness is unclear).
- **Verifier notes:** Claim text confirmed verbatim; metadata confirmed (1.3k stars, Apache-2.0, last commit 2026-08-12, not a fork). Not a duplicate: yalantinglibs (wave 4, struct_pack entry) vendors iguana and re-exports it as struct_pb, but the listed claim is struct_pack's; consider a category override to binary-schemas. Shortcomings: first-party, no methodology, no committed results, unused parse results in the benchmark loop.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-61 (wave 1); enricher (wave 1); orchestrator domain fix 2026-10-11
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/qicosmos/iguana/HEAD/lang/struct_pb_intro.md>
  - <https://raw.githubusercontent.com/qicosmos/iguana/HEAD/benchmark/pb_benchmark.cpp>
  - <https://raw.githubusercontent.com/qicosmos/iguana/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/qicosmos/iguana/HEAD/README.md>
  - <https://github.com/qicosmos/iguana>
  - <https://github.com/qicosmos/iguana/commits>
  - <https://github.com/qicosmos/iguana/pull/386>
  - <https://raw.githubusercontent.com/alibaba/yalantinglibs/HEAD/website/docs/zh/struct_pb/struct_pb_intro.md>
  - <https://raw.githubusercontent.com/alibaba/yalantinglibs/HEAD/website/docs/en/struct_pb/struct_pb_intro.md>
  - <https://raw.githubusercontent.com/alibaba/yalantinglibs/HEAD/website/docs/en/struct_pack/struct_pack_intro.md>
  - <https://raw.githubusercontent.com/alibaba/yalantinglibs/HEAD/include/ylt/struct_pb.hpp>
  - <https://raw.githubusercontent.com/alibaba/yalantinglibs/HEAD/include/ylt/struct_pb/struct_pb_impl.hpp>
- **Sources the enricher read:**
  - <https://github.com/qicosmos/iguana>
  - <https://raw.githubusercontent.com/qicosmos/iguana/HEAD/README.md>
  - <https://raw.githubusercontent.com/qicosmos/iguana/HEAD/lang/struct_pb_intro.md>
  - <https://raw.githubusercontent.com/qicosmos/iguana/HEAD/benchmark/pb_benchmark.cpp>
  - <https://raw.githubusercontent.com/qicosmos/iguana/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/qicosmos/iguana/HEAD/test/proto/unittest_proto3.h>
  - <https://raw.githubusercontent.com/qicosmos/iguana/HEAD/test/proto/data_def.proto>
  - <https://raw.githubusercontent.com/qicosmos/iguana/HEAD/iguana/pb_writer.hpp>
  - <https://raw.githubusercontent.com/qicosmos/iguana/HEAD/iguana/pb_reader.hpp>
  - <https://raw.githubusercontent.com/qicosmos/iguana/HEAD/iguana/pb_util.hpp>
  - <https://raw.githubusercontent.com/qicosmos/iguana/HEAD/iguana/iguana.hpp>
  - <https://raw.githubusercontent.com/qicosmos/iguana/HEAD/iguana/detail/string_resize.hpp>
  - <https://github.com/qicosmos/iguana/issues?q=is%3Aissue+pb>
  - <https://github.com/qicosmos/iguana/issues/301>
  - <https://github.com/qicosmos/iguana/issues/332>
  - <https://github.com/qicosmos/iguana/commits/master/benchmark/pb_benchmark.cpp>
  - <https://github.com/qicosmos/iguana/commits/master/lang/struct_pb_intro.md>
  - <https://github.com/alibaba/yalantinglibs/tree/main/src/struct_pack/benchmark>
  - <https://raw.githubusercontent.com/alibaba/yalantinglibs/HEAD/src/struct_pack/benchmark/struct_pb_sample.hpp>
  - <https://raw.githubusercontent.com/alibaba/yalantinglibs/HEAD/src/struct_pack/benchmark/protobuf_sample.hpp>
  - <https://raw.githubusercontent.com/alibaba/yalantinglibs/HEAD/src/struct_pack/benchmark/benchmark.cpp>
  - <https://github.com/alibaba/yalantinglibs/commits/main/src/struct_pack/benchmark/struct_pb_sample.hpp>
  - <https://raw.githubusercontent.com/alibaba/yalantinglibs/476b584/src/struct_pack/benchmark/struct_pb_sample.hpp>
  - <https://raw.githubusercontent.com/alibaba/yalantinglibs/7207de8/src/struct_pack/benchmark/struct_pb_sample.hpp>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/qicosmos/iguana`) · [data/wave1/enrich/raw/github_com_qicosmos_iguana.json](../../../data/wave1/enrich/raw/github_com_qicosmos_iguana.json) (enrichment confidence 0.75)

</details>
