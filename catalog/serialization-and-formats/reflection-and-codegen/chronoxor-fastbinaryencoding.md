# Fast Binary Encoding (FBE)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Reflection and code generation](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Schema-compiled binary serializer for C++ and eight other languages; about 4x lower serialize/deserialize latency than Protobuf on small messages.

| | |
|---|---|
| **Beats** | protobuf |
| **Claimed result** | CppSerialization README (CppBenchmark, Apple M1 Pro, run 2025-07-16): FBE 77 ns serialize / 84 ns deserialize vs Protobuf 322/351 ns (\~4.2x/\~4.2x, derived from page data). FBE is also faster than Cap'n Proto (247/184 ns) and than FlatBuffers at serialization (272 ns). FlatBuffers deserializes in 81 ns vs FBE's 84 ns, and SimpleBinaryEncoding (35/52 ns) and zpp::bits (34/37 ns) beat FBE on the same page. |
| **Workload** | CppBenchmark fixtures (performance/\*_serialize.cpp, \*_deserialize.cpp): serialize/deserialize one Account with a wallet and three Orders (128-byte domain object; 120-280-byte messages depending on format), 5 attempts of 5 s each. The Protobuf path builds a fresh message and converts from the domain model on each operation. |
| **Metric** | latency |
| **Hardware** | Apple M1 Pro (CppBenchmark reports 10 cores at 2.400 GHz), 32 GiB RAM, OS version 24.5.0 (Darwin), run 2025-07-16 |
| **Compiler and flags** | Not stated exactly; CppBenchmark report lists 'Process configuration: release' but no compiler name/version/flags |
| **Adoption** | 961 stars |
| **Last commit** | 2026-09-10 |
| **Links** | [repository](https://github.com/chronoxor/FastBinaryEncoding) · [benchmark](https://github.com/chronoxor/CppSerialization#readme) |

## Verdict

The author's CppSerialization page (CppBenchmark; Apple M1 Pro; 'release' configuration, with compiler and flags not stated; run 2025-07-16) times one Account with a wallet and three orders. FBE takes 77 ns to serialize and 84 ns to deserialize; Protobuf takes 322/351 ns, about 4.2x slower. In that setup Protobuf builds a fresh message per operation with no arena, and FBE's verify() runs outside the timed loop. The 66/82 vs 628/759 ns table still in FBE's README comes from a stale 2018 Intel/Windows run.

## Use it when

- Small structured messages of a few hundred bytes (orders, account updates, RPC requests) where per-message encode/decode latency matters more than wire size.
- C++ services that exchange the same messages with C#, Go, Java, Kotlin, Python, Ruby, JavaScript or Swift peers and want one schema that generates code for all of them.
- Protocols that need to evolve: you can append fields, enum values and flags, and old and new readers/writers still interoperate. Struct inheritance lets you extend a third-party schema.
- Frozen protocols that can use `--final`: FBE's own (older) README table shows 152 vs 252 bytes and 57/81 vs 88/98 ns serialize/deserialize for the final model versus the versioned one.
- Projects that want generated Sender/Receiver/Client classes and JSON conversion from the same schema instead of combining separate libraries.

## Skip it when

- When message size matters most: on the benchmark message FBE produces 234 bytes versus 120 for Protobuf, because it uses fixed-width fields and 4-byte offsets instead of varints (the final model gets this down to 152 bytes).
- C++-only code with no cross-language need: on the same benchmark page SimpleBinaryEncoding (35/52 ns) and zpp::bits (34/37 ns) are about 2x faster, and zpp::bits needs no IDL.
- Read-mostly zero-copy access: FlatBuffers deserializes in 81 ns versus FBE's 84 ns, and FBE's `deserialize()` copies into std::string/std::vector domain objects.
- Embedded or unusual targets: the generated fbe.cpp throws exceptions, so -fno-exceptions builds fail (issue #76, open). Platform code covers only Unix and Windows. The fbec build fails on Windows ARM64 and Win32 (issue #108). The C++ generator contains no byte-swapping code, so big-endian hosts are unsupported.
- When you rely on the protobuf ecosystem (gRPC, many third-party tools, oneof/variants): FBE has no union/variant type (issue #55, open) and no vcpkg package (issue #65, open).

## How it is fast

Every struct field has a fixed size and a fixed offset set in the generated code. Fields are read and written as little-endian values through direct pointer-cast loads and stores, with no varint/zigzag coding and no per-field tag parsing. Strings, vectors, optionals and nested structs live out of line behind 4-byte offsets, and their space comes from appending to one growable malloc buffer that is reused after `reset()`. Versioning uses a size-and-type header on each struct, so old readers skip unknown trailing fields without parsing tags. The optional `--final` model drops those headers and offsets to get smaller, faster output, at the cost of versioning.

## Compared with alternatives

Pick FBE over Cista++, struct_pack, YAS or bitsery when the same messages must also be read from C#, Go, Java, Kotlin, Python, Ruby, JavaScript or Swift, or when you want schema versioning plus a generated sender/receiver protocol. For C++-only code those siblings serialize plain structs with no IDL or codegen step.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Generated C++ needs libuuid on Linux/macOS or Rpcrt4 on Windows. {fmt} &gt;= 9 is optional (formatting) and RapidJSON is needed only for --json output. Building the fbec compiler needs CMake 3.20+, flex, bison, python3 with the gil tool, CppCommon and cpp-optparse. |
| **Minimum toolchain** | C++17 for the generated code (std::optional, per the README). The repo's own build sets C++23 through CppCMakeScripts and needs CMake 3.20. |
| **Platforms** | Linux, macOS and Windows; CI covers GCC, Clang, MSVC, MinGW, MSYS2 and Cygwin. Assumes a little-endian host. The fbec build fails on Windows ARM64/Win32 (issue #108). |
| **Thread safety** | Not documented. Models are not safe to share: even the const `deserialize()` shifts the shared buffer offset, so give each thread its own model. The generated request/response Client uses a std::mutex internally. |
| **Drop-in for the baseline** | no |

## Gotchas

- The README's C++ examples show a stale template API (`AccountModel<FBE::WriteBuffer>`). Code generated by 1.15.0.0 has a non-template `AccountModel` over `FBEBuffer`, so follow examples/ or CppSerialization instead.
- `deserialize()` does not validate the whole message. A field that fails its bounds check silently becomes its default in release builds, and asserts fire only in debug builds. Call `verify()` on untrusted input; the timed FBE deserialize loop in the benchmark leaves it out.
- `FBEBuffer::allocate()`/`reserve()` have no size limit and do not check whether malloc() failed (issue #107, open). `FBEBuffer::remove()` uses memcpy on ranges that can overlap. All offsets are uint32, which caps a message at 4 GiB.
- Linux builds fail to link unless you add libuuid (issue #89: undefined `uuid_generate_time`). The fbec build pulls in flex/bison and the author's gil-managed submodules.

## Caveats and trade-offs

This is first-party: FastBinaryEncoding and the comparison repo CppSerialization share the author (chronoxor). The CppBenchmark reports state the CPU (Apple M1 Pro) and 'release' but not the compiler or flags, so the tier is C. The table in FBE's own README (FBE 66/82 ns vs Protobuf 628/759 ns) is a stale 2018 run on an Intel Core i7-6700K / Windows 8 and does not match the current CppSerialization page. The Protobuf benchmark allocates a new message and converts from the domain model on every operation, with no arena. FBE is not the fastest on its own page: SimpleBinaryEncoding and zpp::bits are \~2x faster, and FlatBuffers deserialization is about even (81 vs 84 ns).

Requires its own IDL/schema and a code generator (similar to protobuf/Cap'n Proto), rather than serializing plain C++ structs directly; the linked benchmark uses a small, fixed message (\~100-280 bytes), which may not reflect large-payload behavior.

## Maintenance

Single-maintainer and sporadically maintained: the last functional release was 1.15.0.0 (2025-07-16, compile fixes), the newest commit (2026-09-10) only renamed the default branch, and 36 issues are open. It is MIT-licensed, and the generated C++ is plain source you vendor into your tree.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** This is first-party: chronoxor wrote both FBE and CppSerialization. The benchmark code is public (performance/fbe_serialize.cpp, protobuf_serialize.cpp and the others), and the CppBenchmark reports give the CPU (Apple M1 Pro) and 'Process configuration: release' but no compiler or flags. That rules out A, and being first-party rules out B.
- **Verifier notes:** The record's numbers (66/82, 628/759, 558/359, 830/290 ns) are not on benchmark_url. They come from a 2018 Intel i7-6700K / Windows 8 run that is still shown in FBE's README and was on the CppSerialization README until the July 2025 refresh (I checked README at commit cea1bee5bb). The record paired those old numbers with the current M1 Pro hardware. On the current page the gain over Protobuf is \~4.2x rather than \~9.5x, and the claim that FBE also beats FlatBuffers does not hold for deserialization. License (MIT), stars (961) and last commit (2026-09-10) are confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/chronoxor/CppSerialization#readme>
  - <https://github.com/chronoxor/CppSerialization/blob/cea1bee5bb/README.md>
  - <https://github.com/chronoxor/CppSerialization/blob/main/CMakeLists.txt>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/fbe_serialize.cpp>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/protobuf_serialize.cpp>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/protobuf_deserialize.cpp>
  - <https://github.com/chronoxor/FastBinaryEncoding>
  - <https://github.com/chronoxor/FastBinaryEncoding#readme>
- **Sources the enricher read:**
  - <https://github.com/chronoxor/FastBinaryEncoding>
  - <https://github.com/chronoxor/FastBinaryEncoding#readme>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/documents/FBE.md>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/CMakeLists.txt>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/.gitlinks>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/TODO.md>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/proto/fbe.h>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/proto/fbe.cpp>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/proto/fbe_models.h>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/proto/fbe_models.inl>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/proto/fbe_models.cpp>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/proto/fbe_final_models.h>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/proto/fbe_protocol.h>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/proto/proto.h>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/proto/proto_models.h>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/proto/proto_models.cpp>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/source/generator_cpp.cpp>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/examples/serialization.cpp>
  - <https://github.com/chronoxor/FastBinaryEncoding/blob/main/performance/deserialize.cpp>
  - <https://github.com/chronoxor/FastBinaryEncoding/releases>
  - <https://github.com/chronoxor/FastBinaryEncoding/commits/main>
  - <https://github.com/chronoxor/FastBinaryEncoding/issues>
  - <https://github.com/chronoxor/FastBinaryEncoding/issues/76>
  - <https://github.com/chronoxor/FastBinaryEncoding/issues/81>
  - <https://github.com/chronoxor/FastBinaryEncoding/issues/89>
  - <https://github.com/chronoxor/FastBinaryEncoding/issues/91>
  - <https://github.com/chronoxor/FastBinaryEncoding/issues/103>
  - <https://github.com/chronoxor/FastBinaryEncoding/issues/106>
  - <https://github.com/chronoxor/FastBinaryEncoding/issues/107>
  - <https://github.com/chronoxor/FastBinaryEncoding/issues/108>
  - <https://github.com/chronoxor/CppCMakeScripts/blob/main/SetCompilerFeatures.cmake>
  - <https://github.com/chronoxor/CppSerialization#readme>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/fbe_serialize.cpp>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/fbe_deserialize.cpp>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/protobuf_serialize.cpp>
  - <https://github.com/chronoxor/CppSerialization/blob/main/performance/protobuf_deserialize.cpp>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/chronoxor/fastbinaryencoding`) · [data/wave4/enrich/raw/github_com_chronoxor_fastbinaryencoding.json](../../../data/wave4/enrich/raw/github_com_chronoxor_fastbinaryencoding.json) (enrichment confidence 0.8)

</details>
