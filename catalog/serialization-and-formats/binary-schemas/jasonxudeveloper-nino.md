# Nino

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C#` · `MIT` · 🟢 active

> C# source-generated binary serializer for .NET and Unity; beats MessagePack-CSharp and edges MemoryPack on its own microbenchmarks.

| | |
|---|---|
| **Beats** | MessagePack (MessagePack-CSharp, NuGet package 'MessagePack'); MemoryPack also compared |
| **Claimed result** | SimpleClass: 13.68x faster serialize / 5.17x faster deserialize than MessagePack (also 2.44x/1.90x faster than MemoryPack); SimpleStruct: 52.05x faster serialize than MessagePack (1.29x faster than MemoryPack) |
| **Workload** | BenchmarkDotNet micro-benchmarks timing serialize and deserialize separately (not a round trip). Serialize writes into a reused buffer writer. Payloads: one SimpleClass (int, bool, Guid, DateTime, two strings, int[100], List&lt;DateTime&gt;(10), two 10-entry Dictionary&lt;int,...&gt;), one SimpleStruct (int + DateTime), arrays of 100 of each, and a 10,000-element Vector4[] |
| **Metric** | latency |
| **Hardware** | Apple M1, 1 CPU, 8 logical and 8 physical cores, macOS Sequoia 15.1.1 |
| **Compiler and flags** | .NET 9.0.0 (9.0.24.52809) Arm64 RyuJIT AdvSIMD; .NET SDK 9.0.101 (host .NET 8.0.6); BenchmarkDotNet v0.14.0 ShortRun job (3 iterations, 1 launch, 3 warmups), Release build (csproj Optimize=true), GcServer(true) |
| **Adoption** | 649 stars |
| **Last commit** | 2026-06-12 |
| **Links** | [repository](https://github.com/JasonXuDeveloper/Nino) · [benchmark](https://nino.xgamedev.net/en/perf/micro) |

## Verdict

The project's docs page ran BenchmarkDotNet 0.14.0 ShortRun (3 iterations) on .NET 9.0.0 Arm64 RyuJIT with Server GC on an Apple M1. Serializing one mixed SimpleClass into a reused buffer took 128 ns for Nino, 1,757 ns for MessagePack-CSharp (13.68x) and 314 ns for MemoryPack (2.44x); deserializing took 424 ns, 2,185 ns (5.17x) and 804 ns (1.90x). The page gives no package versions, some rows have Error larger than the mean, and the struct-only rows (0.39–2.8 ns) sit at the timer floor.

## Use it when

- Both ends are C# (.NET 6/8 or Unity 2022.3+): game saves, C# client/server messages, IPC and local caches, where nothing else needs to read the bytes.
- Payloads dominated by primitive fields, primitive arrays and List&lt;T&gt; of structs, where the memcpy paths do most of the work. The project page shows 13.68x faster serialize and 5.17x faster deserialize than MessagePack on a mixed class.
- Allocation-sensitive hot paths: serialize into a reused NinoArrayBufferWriter and deserialize into existing objects with DeserializeRef or [NinoRefDeserialization].
- Unity projects on IL2CPP, HybridCLR or ILRuntime that need interface or abstract-class polymorphism and Unity math types (Vector3, Quaternion, Matrix4x4).

## Skip it when

- Data that other languages or tools must read, or that must stay readable for years. The format is C#-only and follows CLR struct layout, and the Versioning page lists wire-format breaks at v3.0.0, 3.0.3, 3.2.0 and 3.3.4. The recovery path it gives is to keep a copy of the old generated deserializer.
- Projects that need a stable release. v4 is still in beta (4.0.0-beta.47, Feb 2026), and the newest non-beta on NuGet is 3.9.17, a line the Quick Start page tells users not to use.
- Untrusted input. The Reader does unchecked unaligned reads (Unsafe.ReadUnaligned before the span slice) and trusts length headers, and no hardening against hostile payloads is documented.
- Object graphs with cycles (issue #132, open) or user-defined collection types, including List&lt;T&gt; subclasses. The maintainer says these are unsupported in v4 (issue #166, open).
- Size-sensitive storage or links. Strings are UTF-16 unless marked [NinoUtf8], fields are fixed-width with struct padding, and no built-in compression is documented. The mixed SimpleClass payload is 1.13 KB, against 1.09 KB for MessagePack.

## How it is fast

All code is generated at compile time, so there is no reflection. Unmanaged structs, and arrays or List&lt;T&gt; of unmanaged T, are copied as raw memory (Unsafe.WriteUnaligned, or MemoryMarshal.AsBytes plus CopyTo, with CollectionsMarshal.AsSpan for lists). Runs of up to 16 adjacent unmanaged fields in a class are packed into one sequential-layout NinoTuple struct and written with a single store. Strings are copied as raw UTF-16 bytes by default with no transcoding, fields are fixed-width with no varints or per-member keys, and polymorphic dispatch reads the type handle straight from the object header, then checks a 4-entry inline cache before falling back to a FastMap lookup.

## Compared with alternatives

MemoryPack is the closest sibling, with the same memcpy-style C# design. Pick Nino over it only if the 2.44x/1.90x SimpleClass serialize/deserialize margin on Nino's own page matters and you accept beta software; the two tie on Vector4[], and MemoryPack is the stable, much more widely used option (1.21.4, about 4.7k stars). Choose Nerdbank.MessagePack (MessagePack wire format) or Bebop (schema-based: C#, TypeScript, Rust, C++) when another language or tool must read the data.

## Integration

| | |
|---|---|
| **Form** | shared lib (NuGet meta-package Nino = Nino.Serialization runtime + Nino.Generator Roslyn source generator; Unity via OpenUPM com.jasonxudeveloper.nino) |
| **Dependencies** | System.Buffers, System.Memory, System.Runtime.CompilerServices.Unsafe (NuGet). In Unity the generator needs Microsoft.CodeAnalysis. |
| **Minimum toolchain** | The runtime targets net6.0, net8.0 and netstandard2.1 (the docs say .NET 5+ or .NET Standard 2.0+). You need a compiler and IDE with source-generator support (the generator is built against Roslyn 4.3), or Unity 2022.3+. .NET Framework is not supported. |
| **Platforms** | Any .NET or Unity player platform, 32- and 64-bit (there are separate 32-bit copy paths). It assumes little-endian; big-endian needs a custom build with a define symbol. |
| **Thread safety** | The README claims fully concurrent serialization and deserialization without external locks. Serialize() uses a thread-static buffer plus a ConcurrentQueue pool, the polymorphic type cache accepts benign races, and the repo includes a multithreading test. |
| **Drop-in for the baseline** | false — it uses [NinoType] instead of [MessagePackObject]/[Key], a different API and an incompatible wire format. A type can carry both attribute sets side by side, as the benchmark types do. |

## Gotchas

- [NinoUtf8] appears to be ASCII-only. Writer.WriteUtf8 writes the UTF-16 char count as the byte length and commits only that many bytes, and Reader.ReadUtf8 builds a string of that length, so non-ASCII text would be truncated or throw. The only unit test uses "Hello, World!". This comes from reading the code; it was not run.
- Adding members requires the WEAK_VERSION_TOLERANCE symbol, which changes the wire format: data written with it cannot be read by builds without it, and the reverse. Deleting members is never allowed.
- The wire layout is CLR memory layout, padding included: the int+DateTime SimpleStruct is 16 bytes. ValueTuple serializes differently on .NET Core and on Mono/Unity, per the Limitations page.
- The docs lag the v4 code. The Basic Usage page shows Serializer.Serialize and Deserializer.Deserialize(data, out T), while the code uses NinoSerializer and NinoDeserializer. The Limitations page says to define BIG_ENDIAN, but Reader.cs and TypeCollector.cs check BIGENDIAN.

## Known shortcomings

- The published page came from an older 2025 version of the benchmark code, with only 3 iterations (BenchmarkDotNet ShortRun). Struct timings are under 3 ns, so the struct ratios mean little.
- No stable v4 release (4.0.0-beta.47; the docs warn against 3.9.x, the newest non-beta). C#-only wire format that follows CLR struct layout and has broken four times in v3; WEAK_VERSION_TOLERANCE changes the format. [NinoUtf8] likely truncates or throws on non-ASCII text (writes the UTF-16 char count as byte length; source reading). Reader trusts length headers; not hardened for untrusted input. No circular references (#132) or custom collection types (#166). Some benchmark rows have error larger than the mean; Nino ties MemoryPack on Vector4[].

## Caveats and trade-offs

First-party results on the project's docs site. The page is undated and gives no package versions. From its BenchmarkDotNet 0.14.0 header and Vectors rows it was made with a 2025 harness revision (Feb-Jul 2025, when the csproj pinned MessagePack 3.1.3 and MemoryPack 1.21.4). Current main uses BenchmarkDotNet 0.15.2 and MessagePack 3.1.7, so a re-run may differ. The ShortRun job (3 iterations) is statistically light. The struct rows are near the timer floor (Nino SimpleStruct deserialize 0.39 ns, serialize 2.82 ns), so the 52x/120x struct ratios mean little; the SimpleClass ratios (13.68x/5.17x vs MessagePack) are the meaningful ones. MemoryPack ties Nino on Vector4[] (ratio 0.99 on deserialize, 1.01 on serialize).

C#-only, source-generator based; smaller community/ecosystem than MessagePack-CSharp; Protobuf is not part of this specific comparison

## Maintenance

Active (last commit 2026-06-12, 649 stars, MIT) and installable from NuGet or OpenUPM, but v4 is still a beta (4.0.0-beta.47, Feb 2026) with a wire format that has broken across versions before.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification A, tier now A.
- **Tier reason:** The perf page has BenchmarkDotNet tables comparing Nino against MessagePack-CSharp and MemoryPack. The Ratio column gives 13.68 (MessagePack) and 2.44 (MemoryPack) for SimpleClass serialize, 5.17 and 1.90 for deserialize, and 52.05 and 1.29 for SimpleStruct serialize. The environment block states .NET 9.0.0 Arm64 RyuJIT AdvSIMD, BenchmarkDotNet v0.14.0 ShortRun (a Release build), and an Apple M1 CPU. The harness is public in src/Nino.Benchmark/SimpleTest.cs, with the same method names, ShortRunJob(Net90) and payload column, plus SimpleBenchmarkData.cs and Program.cs, so this stays A.
- **Verifier notes:** The claimed ratios match the page exactly. The page also shows 12.92x/3.25x (serialize/deserialize) over MessagePack for arrays of 100 SimpleClass. Repo metadata is correct: MIT, not a fork, 649 stars, last commit 2026-06-12, active.
- **Fields the verifier corrected:** `baseline`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://nino.xgamedev.net/en/perf/micro>
  - <https://github.com/JasonXuDeveloper/Nino>
  - <https://github.com/JasonXuDeveloper/Nino/tree/main/src/Nino.Benchmark>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Benchmark/SimpleTest.cs>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Benchmark/Nino.Benchmark.csproj>
- **Sources the enricher read:**
  - <https://github.com/JasonXuDeveloper/Nino>
  - <https://github.com/JasonXuDeveloper/Nino/releases>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Core/Writer.cs>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Core/Reader.cs>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Core/NinoSerializer.cs>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Core/NinoDeserializer.cs>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Core/NinoArrayBufferWriter.cs>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Core/INinoBufferWriter.cs>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Core/NinoTuple.cs>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Core/TypeCollector.cs>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Core/Nino.Core.csproj>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino/Nino.csproj>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Generator/Nino.Generator.csproj>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Generator/Metadata/NinoType.cs>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Generator/Common/SerializerGenerator.Trivial.cs>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Generator/Common/DeserializerGenerator.Trivial.cs>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Benchmark/Nino.Benchmark.csproj>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Benchmark/SimpleTest.cs>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Benchmark/SimpleBenchmarkData.cs>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.Benchmark/Program.cs>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.UnitTests/TestClass.cs>
  - <https://github.com/JasonXuDeveloper/Nino/blob/main/src/Nino.UnitTests/BasicSerializationTests.cs>
  - <https://github.com/JasonXuDeveloper/Nino/issues/132>
  - <https://github.com/JasonXuDeveloper/Nino/issues/166>
  - <https://github.com/JasonXuDeveloper/Nino/issues/143>
  - <https://nino.xgamedev.net/en/perf/micro>
  - <https://nino.xgamedev.net/en/doc/start>
  - <https://nino.xgamedev.net/en/doc/basic>
  - <https://nino.xgamedev.net/en/doc/advanced>
  - <https://nino.xgamedev.net/en/doc/types>
  - <https://nino.xgamedev.net/en/doc/versioning>
  - <https://nino.xgamedev.net/en/doc/limit>
  - <https://api.nuget.org/v3-flatcontainer/nino/index.json>
  - <https://github.com/6over3/bebop>
  - <https://github.com/Cysharp/MemoryPack>
  - <https://github.com/AArnott/Nerdbank.MessagePack>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/jasonxudeveloper/nino`) · [data/wave4/enrich/raw/github_com_jasonxudeveloper_nino.json](../../../data/wave4/enrich/raw/github_com_jasonxudeveloper_nino.json) (enrichment confidence 0.8)

</details>
