# Nerdbank.MessagePack

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `MIT` · 🟢 active

> NativeAOT-ready .NET MessagePack serializer; \~1.2x faster than MessagePack-CSharp on array-encoded small objects, \~5% slower on maps.

| | |
|---|---|
| **Beats** | MessagePack-CSharp |
| **Claimed result** | Array-encoded round-trip: 101.37 ns vs 120.51 ns for MessagePack-CSharp (\~1.19x faster, derived from page data); map-encoded round-trip: 156.08 ns vs 148.36 ns (\~5% slower than MessagePack-CSharp) |
| **Workload** | "SimplePoco" BenchmarkDotNet suite: round-trip serialize+deserialize of a simple object, in both map-encoded and array-encoded MessagePack modes |
| **Metric** | latency |
| **Compiler and flags** | .NET 10, BenchmarkDotNet 0.15.8 (repo), run as 'dotnet run -c Release -f net10.0 -- --filter \*SimplePoco\* --job medium' (test/Benchmarks/update-benchmarks-report.ps1); baseline is MessagePack-CSharp 3.1.7 |
| **Adoption** | 175 stars |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/AArnott/Nerdbank.MessagePack) · [benchmark](https://aarnott.github.io/Nerdbank.MessagePack/docs/performance.html) |

## Verdict

The project's checked-in BenchmarkDotNet SimplePoco suite (.NET 10, BenchmarkDotNet 0.15.8, --job medium; CPU not disclosed) serializes and deserializes a two-property POCO (int + string) against MessagePack-CSharp 3.1.7 with Standard options. Array-encoded round trip: 101.37 vs 120.51 ns (\~1.19x; serialize 38.75 vs 47.01 ns). Map-encoded round trip: 156.08 vs 148.36 ns (\~5% slower). Allocations are equal (80 B round trip, 0 B serialize), and the docs themselves call steady-state throughput 'on par'.

## Use it when

- Small POCOs in array encoding ([Key(n)] or PerfOverSchemaStability=true): the project's SimplePoco benchmark has a 101 ns vs 121 ns round trip against MessagePack-CSharp 3.1.7.
- NativeAOT, trimmed or Unity IL2CPP apps that need MessagePack. The feature table marks MessagePack-CSharp as not NativeAOT-ready or trim-safe.
- Deserializing untrusted msgpack. Secure defaults are on out of the box: SipHash comparers for hashed collections, a MaxDepth nesting limit, and rejection of duplicate property assignment.
- Apps that need async or streaming deserialization, reference preservation or cycles, or round-tripping of unknown properties. MessagePack-CSharp has none of these.
- Existing MessagePack-CSharp codebases that want to move off static resolver state: the analyzers and code fixes do most of the attribute rewrites.

## Skip it when

- Map-encoded objects (property names on the wire) when throughput is the goal. On the same benchmark MessagePack-CSharp wins the round trip (148 vs 156 ns) and serialization (51.7 vs 57.8 ns).
- You need LZ4 compression or typeless serialization (type names in the payload). Neither is supported; LZ4 is an open feature request (issue #34).
- Your peers run MessagePack-CSharp and exchange DateTimeOffset, Guid, decimal, Int128/UInt128 or BigInteger. The encodings differ, and the docs say DateTimeOffset exchange corrupts data.
- You don't need the MessagePack wire format and only want the fastest .NET serializer. MemoryPack and Nino report many-fold wins over MessagePack-CSharp on their own formats.
- Latency-critical async paths. The docs say async APIs are slightly to dramatically slower than the sync ones, and a user-reported streaming case was 1.38x slower than MessagePack-CSharp before a fix (issue #253).

## How it is fast

Converters are built at runtime by a visitor over PolyType type shapes that are source-generated at compile time, so there is no reflection or Reflection.Emit. The docs credit this for faster startup, but no startup numbers are published. Property names are pre-encoded to raw msgpack bytes and copied with WriteRaw; on read, the UTF-8 name span is matched without decoding to a string, using a read-only SpanDictionary that indexes by key length first and falls back to a fastmod hash table. Arrays of float and double use SIMD byte-shuffle converters (AVX-512 VBMI, AVX2, SSSE3/Vector128), and PerfOverSchemaStability switches every object to the smaller, faster array encoding.

## Compared with alternatives

Pick it over MemoryPack or Nino when you need the standard MessagePack wire format (cross-language or existing msgpack peers), NativeAOT/Unity support, or secure deserialization of untrusted input. Those siblings are far faster but use their own binary formats. Among C# MessagePack options it is the only catalogued one with async/streaming reads and reference preservation.

## Integration

| | |
|---|---|
| **Form** | shared lib (NuGet package Nerdbank.MessagePack: managed assembly plus bundled Roslyn analyzers; companion SignalR, ASP.NET Core MVC and Godot packages) |
| **Dependencies** | PolyType (1.4.1 at HEAD, including its source generator), System.IO.Pipelines, Microsoft.VisualStudio.Validation; on netstandard2.0/net472 also Microsoft.Bcl.HashCode, System.Collections.Immutable, System.Text.Json |
| **Minimum toolchain** | Library targets net8.0, net9.0, net472 and netstandard2.0. The docs recommend C# 14 (.NET 10 SDK or Visual Studio 2026); generic attributes such as [GenerateShapeFor&lt;T&gt;] need C# 12+. |
| **Platforms** | any .NET runtime; NativeAOT and trimming on .NET 8+; Unity (Mono and IL2CPP) via NuGetForUnity. SIMD primitive-array converters exist only in the .NET (not netstandard) build and use AVX-512 VBMI, AVX2 or Vector128 paths. |
| **Thread safety** | MessagePackSerializer is immutable and thread-safe; the docs say to create one instance and reuse it. The library has no mutable statics. |
| **Drop-in for the baseline** | partial — same msgpack spec, and it reads MessagePack-CSharp-written objects. The API and attributes differ, though: [GenerateShape] on partial types, and [PropertyShape] replaces [Key("name")] and [IgnoreMember]. Analyzer code fixes automate the migration. MessagePack-CSharp cannot read some of its output. |

## Gotchas

- Guid, decimal, Int128/UInt128 and BigInteger are written as msgpack extension types by default, where MessagePack-CSharp uses bin/string. DateTimeOffset follows the spec, whereas MessagePack-CSharp does not. Check interop before mixing the two libraries.
- PerfOverSchemaStability=true assigns array indices by declaration order. Adding, removing or reordering members, or toggling the flag itself, breaks previously serialized data unless every member has [Key].
- The secure defaults cost some speed on trusted data. Collision-resistant hashing has a small deserialization cost; set ComparerProvider to null to turn it off. Map deserialization always runs duplicate-property detection.
- Types with [GenerateShape] (and any containing types) must be declared partial. Constructing a serializer builds converters, so reuse one instance instead of creating one per call.

## Known shortcomings

- Marginal, mixed win: array round-trip 1.19x faster than MessagePack-CSharp 3.1.7, but map round-trip about 5% slower; the project page itself calls throughput 'on par'. No CPU model stated.
- Narrow benchmark (one 2-property POCO) and the win is array mode only; map mode loses on serialize and round trip. Async APIs are slower than sync. Not a drop-in for MessagePack-CSharp: different API and attributes, no LZ4 or typeless mode, and DateTimeOffset, Guid, decimal, Int128 and BigInteger encode differently (the docs warn DateTimeOffset exchange corrupts data). Its case rests on NativeAOT support and secure defaults, not speed.

## Caveats and trade-offs

Project's own docs explicitly state it and MessagePack-CSharp v3 (source-gen) are 'in the same range for steady-state throughput'; it only wins on the array-encoded workload and loses on map-encoded; no CPU model is disclosed

Newer library than MessagePack-CSharp with smaller ecosystem; result is mixed rather than a clean win

## Maintenance

Actively maintained (v1.3.88 released 2026-09-22, pushes through 2026-09-26), MIT-licensed and on NuGet, but young (created Oct 2024, 175 stars) next to MessagePack-CSharp.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party docs page with numbers from the checked-in SimplePoco BenchmarkDotNet suite (test/Benchmarks/SimplePoco.cs) on .NET 10. The repo script gives 'dotnet run -c Release -f net10.0 --job medium', but no CPU model is disclosed anywhere, so it is C.
- **Verifier notes:** All numbers match the page: array round-trip 101.37 vs 120.51 ns (1.19x; serialize 38.75 vs 47.01 ns, 1.21x) and map round-trip 156.08 vs 148.36 ns (NB \~5% slower). The page itself says throughput is 'on par' with MessagePack-CSharp and claims unquantified 'superior startup performance'. It is a marginal, mixed win with 175 stars, so it is a low-priority entry the orchestrator may choose to drop. Metadata checked: MIT, last commit 2026-09-23, not archived and not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`
- **Pages the verifier opened:**
  - <https://aarnott.github.io/Nerdbank.MessagePack/docs/performance.html>
  - <https://github.com/AArnott/Nerdbank.MessagePack>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/test/Benchmarks/Benchmarks.csproj>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/test/Benchmarks/update-benchmarks-report.ps1>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/Directory.Packages.props>
- **Sources the enricher read:**
  - <https://github.com/AArnott/Nerdbank.MessagePack>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/README.md>
  - <https://aarnott.github.io/Nerdbank.MessagePack/docs/performance.html>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/docfx/docs/performance.md>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/docfx/includes/perf.md>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/docfx/docs/features.md>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/docfx/docs/security.md>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/docfx/docs/migrating.md>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/docfx/docs/unity.md>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/docfx/docs/getting-started.md>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/test/Benchmarks/SimplePoco.cs>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/test/Benchmarks/PocoClass.cs>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/test/Benchmarks/Benchmarks.csproj>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/test/Benchmarks/update-benchmarks-report.ps1>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/samples/cs/Performance.cs>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/Directory.Packages.props>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/global.json>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/src/Nerdbank.MessagePack/Nerdbank.MessagePack.csproj>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/src/Nerdbank.MessagePack/Converters/ObjectMapConverter%601.cs>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/src/Nerdbank.MessagePack/Converters/PropertyCollisionDetection.cs>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/src/Nerdbank.MessagePack/Converters/HardwareAccelerated.cs>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/src/Nerdbank.MessagePack/Utilities/SpanDictionary.cs>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/src/Nerdbank.MessagePack/SerializerConfiguration.cs>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/src/Nerdbank.MessagePack/MessagePackSerializer.cs>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/src/Nerdbank.MessagePack/ConverterCache.cs>
  - <https://github.com/AArnott/Nerdbank.MessagePack/blob/main/src/Nerdbank.MessagePack/StandardVisitor.cs>
  - <https://github.com/AArnott/Nerdbank.MessagePack/issues/253>
  - <https://github.com/AArnott/Nerdbank.MessagePack/issues?q=is%3Aissue+label%3Abug>
  - <https://github.com/AArnott/Nerdbank.MessagePack/releases>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/aarnott/nerdbank.messagepack`) · [data/wave4/enrich/raw/github_com_aarnott_nerdbank_messagepack.json](../../../data/wave4/enrich/raw/github_com_aarnott_nerdbank_messagepack.json) (enrichment confidence 0.78)

</details>
