# Bebop

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C#` · `Apache-2.0` · 🟢 active

> Schema-first binary serializer with C#, TypeScript, Rust and C++ codegen; its C# decoder beat Google.Protobuf and MessagePack 4-9x.

| | |
|---|---|
| **Beats** | Protocol Buffers, MessagePack |
| **Claimed result** | Deserialize complex POCO once, mean latency: BebopStruct 166.1 ns vs Protobuf (Google.Protobuf, C#) 1,051.4 ns (\~6.3x) and vs MessagePack-CSharp 1,584.6 ns (\~9.5x). BebopMessage 231.7 ns is \~4.5x faster than Protobuf and \~6.8x faster than MessagePack (ratios derived from page data). The benchmark repo's README says Bebop is 'the fastest in every benchmark, serialization and deserialization', and that on deserialization Protobuf 'becomes the slowest of the binary serializers'. |
| **Workload** | BenchmarkDotNet serialize/deserialize latency of tiny/simple/complex POCOs (once and in bulk), comparing Bebop (Message and Struct variants) against Newtonsoft.Json, System.Text.Json, Google.Protobuf, and MessagePack-CSharp, in an independent third-party benchmark repo. |
| **Metric** | latency |
| **Hardware** | AMD Ryzen 9 3950X, 1 CPU, 32 logical and 16 physical cores. BenchmarkDotNet reports the OS as Windows 10.0.22449. |
| **Compiler and flags** | BenchmarkDotNet v0.13.1 DefaultJob (default Release build configuration, X64 RyuJIT), .NET SDK 6.0.100-preview.7.21379.14, runtime .NET 5.0.9 (5.0.921.35908). The net5.0 target sets no custom optimization properties in Benchmarks/Benchmarks.csproj. Packages: bebop 2.2.6, Google.Protobuf 3.17.3, MessagePack 2.3.75. |
| **Adoption** | 2.2k stars |
| **Last commit** | 2026-02-17 |
| **Links** | [repository](https://github.com/6over3/bebop) · [benchmark](https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/BenchmarkResults/Deserialize_Once_ComplexPocos.md) |

## Verdict

The run is ProgrammerAL/SerializationBenchmarks (BenchmarkDotNet 0.13.1 in Release, .NET 5.0.9 x64 RyuJIT, Ryzen 9 3950X, Windows, 2021). Bebop 2.2.6 decoded a complex record in 166 ns (struct) and 232 ns (message), against 1,051 ns for Google.Protobuf 3.17.3 and 1,585 ns for MessagePack-CSharp 2.3.75, and decoded a like-for-like two-int32 record in 11.9 ns against 85.5 ns for Protobuf. Serialize gains were smaller (1.07-3.9x over Protobuf). The complex schemas differ (Protobuf uses a string GUID and Timestamp sub-messages), which widens the complex-decode gap.

## Use it when

- .NET 8+ services that decode many small or medium records where decode latency dominates. In the cited run, a two-int32 record decoded in 11.9 ns against 85.5 ns for Google.Protobuf.
- Systems where several languages share one schema (C#, TypeScript, Rust, C/C++, Dart, Python), e.g. a browser client talking to a .NET server.
- Record shapes that will never change, which you can declare as a struct. Structs are the fastest and most compact Bebop encoding (166 ns vs 232 ns for the message form on the complex decode).
- Hot send paths that can reuse buffers: EncodeIntoBuffer(byte[]) sized by MaxByteCount and backed by ArrayPool avoids the allocation of the default Encode().
- Payloads with many GUIDs, timestamps or float arrays. Bebop stores these natively instead of as strings or sub-messages.

## Skip it when

- You need Protobuf wire compatibility or the gRPC ecosystem. Bebop's format is its own.
- Wire size matters for small integers. With fixed-width ints and no varints, a two-int32 record is 8 B (struct) or 15 B (message), against 6 B for Protobuf and 7 B for MessagePack; the simple record is 48-57 B against 42 B.
- Allocation-sensitive code that serializes through the default Encode(). It starts from an empty buffer, doubles it as it grows, then copies with ToArray. The complex struct allocated 1,032 B, against 400 B for Protobuf and 304 B for MessagePack.
- Big-endian hosts: the C# BebopReader and BebopWriter throw on them. Also .NET Framework or runtimes before .NET 8 on current 3.x packages.
- Untrusted input, or reading one field of a large message. Decoders trust the uint32 length prefixes (generated C# allocates an array of the declared length before reading its elements), and no hardening guidance is documented. The maintainer also says Bebop is record-oriented, so it has no FlatBuffers-style partial reads.

## How it is fast

The wire format uses fixed-width little-endian integers and IEEE floats. There are no varints and no per-field wire-type tags, so the C# runtime reads each value with one unaligned load (Unsafe.ReadUnaligned over a ReadOnlySpan&lt;byte&gt;) and writes it with WriteUnaligned. bebopc emits straight-line code for each type: a struct is a fixed sequence of reads with no tags or length prefix, and a message is a uint32 body length plus 1-byte field indices handled by a switch loop. The native guid type (16 raw bytes) and date type (8-byte tick count) need no string or sub-message conversion, and float arrays are block-copied through MemoryMarshal.AsBytes. It is not zero-copy: decode copies strings and byte arrays into managed objects.

## Compared with alternatives

Pick Bebop over HyperSerializer when data crosses language boundaries or needs schema evolution. HyperSerializer is .NET-only and serializes types positionally with no contract, while Bebop generates code for six-plus languages from one .bop schema with versionable messages. Pick SBE instead for fixed-layout, low-latency financial messaging; its code generator runs as a Java jar, while bebopc is a native binary.

## Integration

| | |
|---|---|
| **Form** | module: NuGet package `bebop` (C# runtime) plus the bebopc code generator (bebop-tools on NuGet, npm or cargo). The C++ runtime is a single header, Runtime/C++/src/bebop.hpp. |
| **Dependencies** | none at runtime (the bebop 3.2.3 nuspec lists no dependencies); code generation needs the bebopc binary |
| **Minimum toolchain** | .NET 8: bebop 3.2.3 targets net8.0 and net9.0 and uses static abstract interface members. The C# getting-started page still lists .NET Framework 4.7.2 and .NET Core 3.1, which is out of date. Generated C++ needs C++17 (std::optional, std::variant); the runtime test builds with g++ -std=c++17. |
| **Platforms** | Little-endian only in C#. bebopc ships prebuilt for Linux, macOS and Windows on x64 and arm64, plus a WASI .wasm build. |
| **Thread safety** | Not documented. In the source, each C# encode/decode call creates its own ref-struct BebopReader/BebopWriter with no shared mutable state. The TypeScript runtime reuses one process-wide BebopView. |
| **Drop-in for the baseline** | no |

## Gotchas

- The C# BebopWriter.WriteDate converts a DateTime to whole milliseconds since the Unix epoch before writing 100 ns ticks. Sub-millisecond precision is lost on round-trip, and all dates come back as UTC.
- Messages encode fields in declaration order. When an old reader hits an unknown field index, the generated decoder jumps to the end of the message, so it drops any known fields encoded after the new one. Field indices are also a single byte.
- Structs cannot evolve. Adding or removing a field breaks every existing reader, per the docs.
- TypeScript: encode() returns a subarray of a shared singleton BebopView, so the next encode overwrites earlier results unless you copy them (issue #209, open since 2022).

## Caveats and trade-offs

All numbers are C#: Bebop 2.2.6 vs the C# Protobuf (Google.Protobuf 3.17.3) and MessagePack-CSharp 2.3.75 runtimes on .NET 5.0.9, run in 2021. Bebop is now at v3.2.3 (2025-09-16) and .NET 5 is out of support, so current versions are untested. The benchmark repo is small (6 stars, last commit 2021-09-05) and publishes a single BenchmarkDotNet run on one desktop. The complex-POCO schemas are not like-for-like, which inflates Protobuf's complex-deserialize cost: Protobuf stores the child GUID as a string and uses google.protobuf.Timestamp sub-messages and double Percentage/Cost, Bebop uses native guid/date/float32, and MessagePack uses a decimal Cost. On the like-for-like tiny POCO (two int32 fields), Deserialize_Once_TinyPocos still shows BebopStruct 11.93 ns vs Protobuf 85.51 ns (\~7.2x, derived). Serialization gains are much smaller, e.g. Serialize_Once_SimplePocos BebopMessage 94.40 ns vs Protobuf 100.82 ns (\~1.07x) and Serialize_Once_ComplexPocos BebopStruct 239.2 ns vs Protobuf 926.5 ns (\~3.9x) (derived). Bebop's serialize allocates more than both baselines: 1,032 B for complex serialize-once BebopStruct vs 400 B for Protobuf and 304 B for MessagePack. Bebop's own README claims \~10x over Protobuf in C# and TypeScript, but shows only a chart image.

Bebop also targets TypeScript, Rust, Dart, C, and other languages via its own IDL/codegen, but the cited numeric evidence here is specifically for its C# implementation. Requires a `.bop` schema and code generation step (like Protobuf), unlike schema-less formats.

## Maintenance

Active: last push 2026-02-17, latest release v3.2.3 on 2025-09-16, Apache-2.0, and the runtime has no dependencies. But the only independent numbers are from 2021 (Bebop 2.2.6 on .NET 5), and the docs lag the code: the supported .NET list is stale and the known-issues page reads 'TODO'.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The independent ProgrammerAL/SerializationBenchmarks repo publishes its BenchmarkDotNet code against Google.Protobuf and MessagePack-CSharp: Benchmarks/Deserialize_Once_ComplexPocos.cs and 17 sibling classes, run by Benchmarks/Program.cs, with the schemas in SerializationEntities/. Each results page states the toolchain (.NET SDK 6.0.100-preview.7, .NET 5.0.9 X64 RyuJIT, BenchmarkDotNet 0.13.1 DefaultJob, which builds in Release) and the CPU (AMD Ryzen 9 3950X), so it is A, the same call as the earlier Sep and simdunicode BenchmarkDotNet entries.
- **Verifier notes:** All six rows in the record match the page, and Bebop leads in all 18 BenchmarkResults tables. I pointed benchmark_url at the canonical /blob/main/ path (/blob/master/ 302-redirects to it) and set compared_against_cpp_std_directly to false, because the baselines are C# Protobuf/MessagePack runtimes, not the C++ standard library. The 6.3x complex figure is flattered by a schema mismatch (see caveats), but the like-for-like tiny-POCO table still shows \~7x, so the tier stays A.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/master/BenchmarkResults/Deserialize_Once_ComplexPocos.md>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/BenchmarkResults/Deserialize_Once_ComplexPocos.md>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/README.md>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/tree/main/BenchmarkResults>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/Benchmarks/Deserialize_Once_ComplexPocos.cs>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/Benchmarks/Serialize_Once_ComplexPocos.cs>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/Benchmarks/Benchmarks.csproj>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/Benchmarks/Program.cs>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/SerializationEntities/EntityInstances.cs>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/SerializationEntities/SerializationEntities.csproj>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/SerializationEntities/Bebop/BebopPocos.bop>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/SerializationEntities/Bebop/BebobUtilities.cs>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/SerializationEntities/Protobuf/ProtobufPocos.proto>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/SerializationEntities/Protobuf/ProtobufUtilities.cs>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/SerializationEntities/MessagePack/ComplexPocoMsgPack.cs>
  - <https://github.com/6over3/bebop>
  - <https://github.com/6over3/bebop/blob/master/README.md>
  - <https://github.com/6over3/bebop/releases>
- **Sources the enricher read:**
  - <https://github.com/6over3/bebop>
  - <https://github.com/6over3/bebop/blob/master/README.md>
  - https://github.com/6over3/bebop/tree/master (recursive tree listing)
  - <https://github.com/6over3/bebop/blob/master/Runtime/C%23/Bebop.csproj>
  - <https://github.com/6over3/bebop/blob/master/Runtime/C%23/Runtime/BebopReader.cs>
  - <https://github.com/6over3/bebop/blob/master/Runtime/C%23/Runtime/BebopWriter.cs>
  - <https://github.com/6over3/bebop/blob/master/Runtime/C%23/Runtime/BebopRecord.cs>
  - <https://github.com/6over3/bebop/blob/master/Runtime/C%23/Runtime/BebopSerializer.cs>
  - <https://github.com/6over3/bebop/blob/master/Runtime/C++/README.md>
  - <https://github.com/6over3/bebop/blob/master/Runtime/C++/src/bebop.hpp>
  - <https://github.com/6over3/bebop/blob/master/Runtime/C++/test/Makefile>
  - <https://github.com/6over3/bebop/blob/master/Runtime/TypeScript/index.ts>
  - <https://github.com/6over3/bebop/blob/master/Core/Generators/CSharp/CSharpGenerator.cs>
  - <https://github.com/6over3/bebop/blob/master/Core/Generators/CPlusPlus/CPlusPlusGenerator.cs>
  - <https://github.com/6over3/bebop/blob/master/Laboratory/C/README.md>
  - <https://github.com/6over3/bebop/blob/master/docs/src/content/docs/reference/wire-format.mdx>
  - <https://github.com/6over3/bebop/blob/master/docs/src/content/docs/reference/struct.mdx>
  - <https://github.com/6over3/bebop/blob/master/docs/src/content/docs/reference/message.mdx>
  - <https://github.com/6over3/bebop/blob/master/docs/src/content/docs/reference/types.mdx>
  - <https://github.com/6over3/bebop/blob/master/docs/src/content/docs/guide/getting-started-csharp.mdx>
  - <https://github.com/6over3/bebop/blob/master/docs/src/content/docs/guide/installation.mdx>
  - <https://github.com/6over3/bebop/blob/master/docs/src/content/docs/known-issues.mdx>
  - <https://github.com/6over3/bebop/blob/master/docs/src/content/docs/faq.mdx>
  - <https://github.com/6over3/bebop/releases>
  - <https://github.com/6over3/bebop/releases/tag/v3.2.3>
  - <https://github.com/6over3/bebop/commits/master>
  - <https://github.com/6over3/bebop/issues>
  - <https://github.com/6over3/bebop/issues/386>
  - <https://github.com/6over3/bebop/issues/312>
  - <https://github.com/6over3/bebop/issues/233>
  - <https://github.com/6over3/bebop/issues/209>
  - <https://github.com/6over3/bebop/issues/144>
  - <https://api.nuget.org/v3-flatcontainer/bebop/index.json>
  - <https://api.nuget.org/v3-flatcontainer/bebop/3.2.3/bebop.nuspec>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/BenchmarkResults/Deserialize_Once_ComplexPocos.md>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/BenchmarkResults/Deserialize_Once_TinyPocos.md>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/BenchmarkResults/Serialize_Once_ComplexPocos.md>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/BenchmarkResults/Serialize_Once_SimplePocos.md>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/README.md>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/Benchmarks/Serialize_Once_ComplexPocos.cs>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/Benchmarks/Deserialize_Once_ComplexPocos.cs>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/SerializationEntities/Bebop/BebopPocos.bop>
  - <https://github.com/ProgrammerAL/SerializationBenchmarks/blob/main/SerializationEntities/Protobuf/ProtobufPocos.proto>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/README.md>
  - <https://github.com/aeron-io/simple-binary-encoding/blob/master/README.md>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/6over3/bebop`) · [data/wave4/enrich/raw/github_com_6over3_bebop.json](../../../data/wave4/enrich/raw/github_com_6over3_bebop.json) (enrichment confidence 0.8)

</details>
