# HyperSerializer

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `Apache-2.0` · 🟢 active

> Contract-less .NET binary serializer built on runtime-compiled Span/MemoryMarshal proxies; \~16x faster than protobuf-net and MessagePack-CSharp in its author's benchmark.

| | |
|---|---|
| **Beats** | Protocol Buffers (protobuf-net 3.1.26), MessagePack (MessagePack-CSharp 2.4.59) |
| **Claimed result** | README BenchmarkDotNet table (1M serialize+deserialize round-trips, .NET 8): HyperSerializer 46.24 ms vs MemoryPack 98.81 ms (ratio 2.14), MessagePack 768.58 ms (16.62), Protobuf/protobuf-net 769.34 ms (16.64). Allocated: 205.99 MB vs 213.62 / 197.86 / 427.25 MB. The older 2022 PNG chart (Time.png, no environment) shows 50 ms vs ApexSerializer 155 ms (3.1x), MessagePack 899 ms (18.0x), Protobuf 918 ms (18.4x). This older chart is the source of the README's '3x Apex / 18x' sentence. |
| **Workload** | BenchmarkDotNet run of 1,000,000 single-object serialize+deserialize round-trips of a small POCO. The README's 'Test' class has 10 fields: Guid?, int, long, DateTime, uint, decimal, TimeSpan, Guid, enum, string. The 2024 text table compares HyperSerializer, MemoryPack, MessagePack-CSharp and protobuf-net. ApexSerializer appears only in the 2022 PNG chart. |
| **Metric** | throughput |
| **Hardware** | Intel Core i9-10980XE CPU 3.00GHz (18 physical / 36 logical cores), Windows 11 (10.0.22621.3296) |
| **Compiler and flags** | .NET SDK 8.0.203, .NET 8.0.3 RyuJIT x64 AVX2; BenchmarkDotNet v0.13.4; MSBuild argument /p:Optimize=true; RunStrategy=Throughput, InvocationCount=1, LaunchCount=1, UnrollFactor=1 |
| **Adoption** | 85 stars |
| **Last commit** | 2025-11-05 |
| **Links** | [repository](https://github.com/adam-dot-cohen/HyperSerializer) · [benchmark](https://github.com/adam-dot-cohen/HyperSerializer#benchmarks) |

## Verdict

The author's BenchmarkDotNet table (.NET 8.0.3 RyuJIT x64 AVX2, /p:Optimize=true, Intel Core i9-10980XE, Windows 11) shows 1M single-object serialize+deserialize round-trips of a 10-member POCO. HyperSerializer took 46.24 ms, against 98.81 ms for MemoryPack 1.9.16 (2.14x), 768.58 ms for MessagePack-CSharp 2.4.59 and 769.34 ms for protobuf-net 3.1.26 (both \~16.6x). Allocations were similar (\~206 MB), except protobuf-net at 427 MB. The committed harness does not reproduce this exact table: its Test class has no string, and its loop and parameter setup differ. The '18x' and '3x vs Apex' figures come from an older chart with no environment listed.

## Use it when

- Both ends run the same .NET 6-9 build (a shared DTO assembly) and exchange small, flat objects over a trusted link. The README names messaging between services behind a firewall as the target.
- Short-lived caches of flat DTOs, in-process or remote, where you can flush the cache whenever a type changes.
- Hot paths that serialize and deserialize one object at a time. The published run shows \~46 ns per round trip (derived: 46.24 ms / 1M) for a 10-member POCO with Guid, DateTime, decimal, TimeSpan, an enum and a string.
- Bulk arrays of unmanaged structs, such as market ticks. Pass the whole `T[]` and it is stored as a length prefix plus one block copy (see test Test_Struct_Array_Should_Serialize and the author's advice in issue #8).
- Types you cannot or will not annotate. No [ProtoContract], [MessagePackObject] or [Key] attributes are needed.

## Skip it when

- Persisted data, or services deployed on different schedules. The format is positional with no field IDs, so reordering, removing or retyping a member breaks reads. The README warns that mismatched bytes can decode into wrong values with no exception.
- Any reader that is not .NET, or data exchanged across architectures. The bytes are raw CLR memory layout: Microsoft's docs say `MemoryMarshal.Write` copies private fields and implementation details. Byte order is the host's, strings are UTF-16, and no format spec exists.
- Native AOT, trimmed or single-file apps. The library compiles C# with Roslyn at runtime, loads the result dynamically, and builds compiler references from `Assembly.Location`. Native AOT forbids dynamic loading, and single-file apps return an empty `Assembly.Location`.
- Object graphs. Class-typed members and dictionaries are ignored, with no reference or cycle handling (issues #2 and #11), and a top-level `Dictionary<int,int>` throws (issue #1, open since 2022).
- Processes where cold start or footprint matters. The first use of each type runs a Roslyn compilation, and the package depends on Microsoft.CodeAnalysis.CSharp. The repo does not document the compile cost.

## How it is fast

On the first use of each `T`, a static constructor reflects over the type and fills C# source templates to build a proxy class. It compiles that source at runtime with Roslyn (Microsoft.CodeAnalysis.CSharp, Release optimization), loads the assembly, and caches the Serialize/Deserialize delegates in the static generic class `HyperSerializer<T>`. The generated code computes the exact output length (fixed member sizes plus string and array byte counts) and allocates one `byte[]`. It then writes each member as raw memory with `MemoryMarshal.Write` and reads it back with `MemoryMarshal.Read`. Strings are block-copied as UTF-16 through `MemoryMarshal.Cast<char,byte>`, and value-type arrays are block-copied too. The format has no field tags, no varints, no UTF-8 transcoding and no per-member type markers. Its only framing is a 1-byte null flag for each nullable and a 4-byte length prefix for each string or array.

## Compared with alternatives

Bebop is the only sibling with a C# result. Pick HyperSerializer over Bebop when you want no .bop schema and no bebopc codegen step and both ends are the same .NET types. Pick Bebop when TypeScript, Rust or C++ must read the data. rkyv and Apache Fory (C++) are measured outside .NET, so they matter here only if you are not locked to .NET.

## Integration

| | |
|---|---|
| **Form** | shared lib (NuGet package `HyperSerializer`, managed DLL) |
| **Dependencies** | Microsoft.CodeAnalysis.CSharp &gt;= 4.9.2 (Roslyn, used at runtime to compile the per-type proxies) |
| **Minimum toolchain** | .NET 6 (package targets net6.0, net7.0, net8.0, net9.0) |
| **Platforms** | Any OS/architecture running .NET 6-9 with JIT and runtime assembly loading. Native AOT is not supported, and single-file publish is likely incompatible. The wire format uses host byte order. |
| **Thread safety** | The README claims 100% thread-safe. Per-type setup runs once in a static constructor, and the generated methods keep no shared state; each Serialize call allocates a new buffer. One exception: the struct-size cache in ReflectionExtensions.cs is a plain Dictionary that is read outside its lock during setup. |
| **Drop-in for the baseline** | partial — types need no annotations, and each call site is one line. But the wire format is incompatible with protobuf and MessagePack, so both ends must switch together and existing stored data cannot be read. |

## Gotchas

- The async methods are synchronous wrappers, and `SerializeAsync` also copies the result with `ToArray()`. In issue #8, calling SerializeAsync per record into a MemoryStream took 1,967 ms, against 528 ms for TeaFiles, on 3.02M structs. The author's fix was the sync `Span` API, or serializing the whole array in one call.
- Setup runs in the static constructor of `HyperSerializer<T>`, so codegen failures surface as TypeInitializationException (issues #1 and #4). The generated deserializer calls `new()` and assigns every scanned member, and MemberTypeInfo.cs never checks CanWrite. So types appear to need a public parameterless constructor and settable members. Set `HyperSerializerSettings` before the first use of each type.
- Member order is public fields first, then properties, in reflection order. Microsoft documents that GetProperties order is unspecified on .NET 6 and earlier and deterministic from .NET 7. In the current source, setting `SerializeFields = false` keeps fields and drops properties, which is the opposite of what the README describes.
- The README says generic lists work, but `TypeSupport` compares against the open generic `typeof(IEnumerable<>)`, which a `List<int>` never equals. So List members appear to be skipped silently, and the V3 test that covers lists uses a comparison helper that cannot return false. Value-type arrays do round-trip (issue #5 regression test). Struct members must not contain references, because `MemoryMarshal.Write` throws ArgumentException for those.

## Caveats and trade-offs

First-party numbers from the author's own run (the README table was added 2024-04-10). The committed code does not exactly reproduce the table. SyncBenchmarks.cs declares [Params(1_000_000)] iterations but does one round-trip per invocation, and its Test class has no string field. SyncBenchmarksWithStrings.cs loops 1M times, but it uses an 18-field class and has no iterations parameter. The exact class that produced the table cannot be identified. 'Protobuf' is protobuf-net 3.1.26, not Google.Protobuf, although the README links protocolbuffers/protobuf. The '16x' figure (2024 text table) and the '18x' / '3x vs Apex' figures (2022 PNG chart with no environment) come from different runs. The format is contract-less and positional: it has no schema evolution, and dictionaries and complex-type properties are not serialized. The repo LICENSE is Apache-2.0, but the NuGet package ships License.txt with MIT text. Both licenses are OSI-approved.

Contract-less: relies on identical field/property layout between source and destination types, no versioning/schema-evolution support; mismatched types can throw or silently misdecode. .NET only, span-based, described by its author as a 'champion/challenger (C++ vs C#) experiment'.

## Maintenance

Maintained but slow-moving. v1.6 (2025-11-05) only added net9.0; before it, the last code change was in April 2024. The repo has 85 stars, \~44k NuGet downloads and one open issue. Usable via NuGet under Apache-2.0 (the package ships an MIT License.txt), but its runtime Roslyn dependency rules out AOT and makes it heavier than its small source suggests.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** Upgrade from C: the README Benchmarks section has a text BenchmarkDotNet table with its environment block (.NET SDK 8.0.203 / .NET 8.0.3 RyuJIT x64 AVX2, /p:Optimize=true, Intel Core i9-10980XE). The public harness is HyperSerializer.Benchmarks/ (Program.cs config plus Experiments/SyncBenchmarks.cs and SyncBenchmarksWithStrings.cs), and it runs against MessagePack-CSharp 2.4.59 and protobuf-net 3.1.26. The committed code does not exactly match the table (see caveats).
- **Retiered** A to C: Orchestrator retier: the BenchmarkDotNet table states SDK, flags and CPU, but the committed harness does not match the published table (SyncBenchmarks.cs uses a 1M parameter with no loop; SyncBenchmarksWithStrings.cs uses an 18-field class), so the published numbers cannot be reproduced from public code. Tier A requires that.
- **Verifier notes:** Metadata checks out: Apache-2.0, not a fork or archived, 85 stars, last commit 2025-11-05, active. The record's caveat that no environment block is published is false, and the tier moves to A under the rubric. If the orchestrator weights the mismatch between the code and the table, C is the fallback. compared_against_cpp_std_directly was wrong (this is C# against .NET serializers), so it is set to false.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `baseline`, `compiler_and_flags`, `hardware`, `compared_against_cpp_std_directly`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/adam-dot-cohen/HyperSerializer>
  - <https://github.com/adam-dot-cohen/HyperSerializer#benchmarks>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Benchmarks/Experiments/SyncBenchmarks.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Benchmarks/Experiments/SyncBenchmarksWithStrings.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Benchmarks/Experiments/TestObjects.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Benchmarks/Experiments/VersionChampChallenge.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Benchmarks/Program.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Benchmarks/HyperSerializer.Benchmarks.csproj>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer/HyperSerializer.csproj>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/LICENSE>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/License.txt>
  - <https://raw.githubusercontent.com/Hyperlnq/HyperSerializer/main/BenchmarkAssets/Time.png>
  - <https://raw.githubusercontent.com/Hyperlnq/HyperSerializer/main/BenchmarkAssets/Space.png>
- **Sources the enricher read:**
  - <https://github.com/adam-dot-cohen/HyperSerializer>
  - <https://github.com/adam-dot-cohen/HyperSerializer#benchmarks>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer/HyperSerializer.csproj>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer/HyperSerializer.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer/HyperSerializer%7BT%7D.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer/HyperSerializerSettings.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer/Dynamic/Syntax/CodeGen.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer/Dynamic/Syntax/Templates/ProxySyntaxTemplate_Net8.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer/Dynamic/Syntax/Templates/ProxySyntaxTemplate.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer/Dynamic/Syntax/TypeSupport.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer/Dynamic/Syntax/MemberTypeInfo.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer/Utilities/ReflectionExtensions.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer/Utilities/CollectibleLoadContext.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer/Utilities/FrameworkAssemblyPaths.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Test/SerializerTests.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Test/TestBase.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Test/TestWithStrings.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Test/TestStruct.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Test/TestLayout.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Test/HyperSerializer.Test.csproj>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Test/V3/SerializerTests.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Test/V3/TestBase.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Test/SerializerTestsAsync.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Test/SerializerTestsUnsafe.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Benchmarks/Program.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Benchmarks/HyperSerializer.Benchmarks.csproj>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Benchmarks/Experiments/SyncBenchmarks.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Benchmarks/Experiments/SyncBenchmarksWithStrings.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/HyperSerializer.Benchmarks/Experiments/TestObjects.cs>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/BenchmarkAssets/Time.png>
  - <https://github.com/adam-dot-cohen/HyperSerializer/blob/main/BenchmarkAssets/Space.png>
  - <https://github.com/adam-dot-cohen/HyperSerializer/issues?q=is%3Aissue>
  - <https://github.com/adam-dot-cohen/HyperSerializer/issues/1>
  - <https://github.com/adam-dot-cohen/HyperSerializer/issues/2>
  - <https://github.com/adam-dot-cohen/HyperSerializer/issues/3>
  - <https://github.com/adam-dot-cohen/HyperSerializer/issues/4>
  - <https://github.com/adam-dot-cohen/HyperSerializer/issues/5>
  - <https://github.com/adam-dot-cohen/HyperSerializer/issues/8>
  - <https://github.com/adam-dot-cohen/HyperSerializer/issues/9>
  - <https://github.com/adam-dot-cohen/HyperSerializer/issues/11>
  - <https://github.com/adam-dot-cohen/HyperSerializer/commits/main>
  - <https://github.com/adam-dot-cohen/HyperSerializer/releases>
  - <https://www.nuget.org/packages/HyperSerializer/>
  - <https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/>
  - <https://learn.microsoft.com/en-us/dotnet/core/deploying/single-file/overview>
  - <https://learn.microsoft.com/en-us/dotnet/api/system.type.getproperties?view=net-8.0>
  - <https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.memorymarshal.write?view=net-8.0>
  - <https://github.com/6over3/bebop>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/adam-dot-cohen/hyperserializer`) · [data/wave4/enrich/raw/github_com_adam_dot_cohen_hyperserializer.json](../../../data/wave4/enrich/raw/github_com_adam_dot_cohen_hyperserializer.json) (enrichment confidence 0.72)

</details>
