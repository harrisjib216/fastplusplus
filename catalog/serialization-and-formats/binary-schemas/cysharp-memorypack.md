# MemoryPack

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [Binary schemas](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `MIT` · 🟢 active

> C# source-generated binary serializer that copies unmanaged data raw; \~1.7x faster than MessagePack-CSharp on objects, 40x+ on struct arrays.

| | |
|---|---|
| **Beats** | MessagePack-CSharp (MessagePack) and protobuf-net (Protobuf) |
| **Claimed result** | README: "For standard objects, MemoryPack is x10 faster and x2 \~ x5 faster than other binary serializers. For struct array ... up to x50 \~ x200". The chart's own ns table shows narrower gains against the named baselines. JsonResponseModel (47 fields, nested): MemoryPack 13,176/24,540 ns ser/deser vs MessagePack-CSharp 22,961/39,420 (1.74x / 1.61x), protobuf-net 73,028/51,640 (5.54x / 2.10x), Orleans 58,530/46,210 (4.44x / 1.88x) and JsonSerializer 189,099/308,900 (14.4x / 12.6x). Vector3[10000]: MemoryPack 231/316 ns vs MessagePack-CSharp 9,887/26,335 (42.8x / 83.3x) and protobuf-net 53,769/39,526 (232.8x / 125.1x). All ratios are derived from page data. |
| **Workload** | Serializing/deserializing POCOs and struct arrays via IBufferWriter&lt;byte&gt;, compared against System.Text.Json, protobuf-net, MessagePack-CSharp, and Orleans.Serialization |
| **Metric** | latency |
| **Hardware** | Ryzen 9 5950X |
| **Compiler and flags** | .NET 7 (BenchmarkDotNet); exact optimization flags not stated |
| **Adoption** | 4.7k stars |
| **Last commit** | 2026-07-08 |
| **Links** | [repository](https://github.com/Cysharp/MemoryPack) · [benchmark](https://github.com/Cysharp/MemoryPack#readme) |

## Verdict

The README chart was run with BenchmarkDotNet on .NET 7 and a Ryzen 9 5950X, serializing into a reused ArrayBufferWriter; build flags are not stated. On the 47-field nested JsonResponseModel, MemoryPack serializes/deserializes in 13,176/24,540 ns against 22,961/39,420 ns for MessagePack-CSharp (\~1.7x/1.6x) and 73,028/51,640 ns for protobuf-net (\~5.5x/2.1x). On the panel labelled Vector3[10000] it takes 231/316 ns against MessagePack's 9,887/26,335 ns (\~43x/83x). The checked-in SerializerTestBase builds 1,000 Vector3 elements, not 10,000, and the current Program.cs job uses 1 warmup and 1 iteration.

## Use it when

- .NET-to-.NET traffic where both ends compile the same C# types: MagicOnion RPC, Redis/cache values, ASP.NET Core bodies through MemoryPack.AspNetCoreMvcFormatter, or local save files.
- Payloads dominated by blittable structs or large unmanaged arrays (Vector3[], matrices, numeric buffers, game state), where serialization becomes a memcpy.
- Unity 2022.3.12f1+ projects, including IL2CPP, that need reflection-free serialization. The README reports 3-10x faster than JsonUtility.
- Allocation-sensitive hot paths that write straight into PipeWriter/IBufferWriter&lt;byte&gt;, or that reuse objects and lists through Deserialize(ref value).
- C# servers talking to browser clients, using the generated TypeScript serializer instead of JSON.

## Skip it when

- Cross-language or public interchange (other than the generated TypeScript). The format is not self-describing, decoding needs the C# type, and there is no IDL, so use Protobuf or MessagePack there.
- Size-sensitive payloads full of small integers. Ints are always 4 bytes, against 1-5 bytes with varint in MessagePack or Protobuf, so MemoryPack payloads can be larger. The README suggests LZ4/Zstd/Brotli compression.
- Schemas that must evolve freely. The default mode allows only appending members: no deletes, reorders or type changes. Full version tolerance needs GenerateType.VersionTolerant, which the README says serializes slower and gives slightly larger payloads.
- Big-endian targets. The reference implementation assumes little-endian and does not byte-swap.
- Native AOT deployments. Issues #382 and #414 report 'Failed to create generic virtual method implementation' crashes, and both were closed by the stale bot without a fix in MemoryPack.

## How it is fast

The format uses 'zero encoding'. It writes no field names or tags, members go in declaration order, ints are fixed-width little-endian (no varint), and the object header is a single member-count byte. Unmanaged structs and arrays of them are written with Unsafe.WriteUnaligned or one Unsafe.CopyBlockUnaligned (a memcpy) after a 4-byte length, which is why struct arrays are so much faster. Formatters are generated at compile time by the source generator (IMemoryPackable&lt;T&gt; with C# 11 static abstract members on net7.0+), with no reflection or IL.Emit. The writer is a ref struct that holds a `ref byte` into the destination span. The byte[] path reuses a [ThreadStatic] pinned ReusableLinkedArrayBufferWriter and allocates the result with GC.AllocateUninitializedArray. An optional UTF-16 string mode copies chars directly with no transcoding.

## Compared with alternatives

Nino and HyperSerializer both report beating MemoryPack in their own READMEs (Nino 2.44x/1.90x on SimpleClass; HyperSerializer 2.14x round-trip). Pick MemoryPack for its broader feature set (unions, version-tolerant and circular-reference modes, TypeScript generation, ASP.NET Core formatter, Unity shims) and larger user base. Pick Nerdbank.MessagePack or MessagePack-CSharp when you need MessagePack wire compatibility, and Bebop when you need a cross-language schema.

## Integration

| | |
|---|---|
| **Form** | shared lib (NuGet: MemoryPack = MemoryPack.Core runtime + MemoryPack.Generator Roslyn source generator; optional MemoryPack.Streaming, MemoryPack.AspNetCoreMvcFormatter, MemoryPack.UnityShims; Unity via NuGetForUnity plus a git-URL package) |
| **Dependencies** | none on net7.0/net8.0; the netstandard2.1 target pulls System.Runtime.CompilerServices.Unsafe 6.0.0 and System.Collections.Immutable 6.0.0 |
| **Minimum toolchain** | .NET Standard 2.1 (.NET 5/6) minimum, .NET 7+ recommended (targets net7.0, net8.0, netstandard2.1); Roslyn 4.3.1+ (VS 2022 17.3 / .NET SDK 6.0.401); Unity 2022.3.12f1+ |
| **Platforms** | little-endian only (x86-64, arm64); .NET, Unity (IL2CPP included); Native AOT has open-ended crash reports |
| **Thread safety** | The static MemoryPackSerializer keeps per-thread buffers and state in [ThreadStatic] fields, so concurrent calls from different threads are the intended use. Open issue #458 reports a NullReferenceException on parallel Deserialize, caused by a race in MemoryPackFormatterProvider.Register: Check&lt;T&gt;.registered is set before Cache&lt;T&gt;.formatter. |
| **Drop-in for the baseline** | partial — same attribute-plus-static-Serialize/Deserialize shape as MessagePack-CSharp, but types must be declared partial with [MemoryPackable], the wire format is incompatible with MessagePack/Protobuf (stored data must be migrated), and non-C# consumers are lost |

## Gotchas

- Member declaration order is the wire format. Reordering, deleting or retyping a member in the default mode breaks old data, and nothing on the wire detects it. The README recommends checking the generator's serialization-info output in CI.
- Unmanaged structs are dumped as raw memory, padding included, and cannot take custom formatters (#440). Types with StructLayout.Auto, such as DateTimeOffset and ValueTuple, are not binary-compatible between .NET 7+ and Unity.
- The netstandard2.1 and net7.0 builds do not mix. A MemoryPackable type compiled for netstandard2.1 and used from net7.0 throws TypeLoadException, so libraries must multi-target both.
- Some collection formatters write BCL private fields through Unsafe.As view types (List&lt;T&gt;, Stack&lt;T&gt;, BitArray). Open issue #460 flags this as fragile on future runtimes.

## Known shortcomings

- Against MessagePack-CSharp on standard objects the gain is only about 1.74x serialize and 1.61x deserialize, not the README's 'x2\~x5'; the 'x10' is against System.Text.Json. The large wins (42-83x) are for unmanaged-struct arrays copied as raw memory. No CPU or build configuration stated.
- The chart's Vector3[10000] label is likely wrong: the checked-in benchmark builds 1,000 elements, and 231 ns for 10,000 would imply about 520 GB/s. The current benchmark job uses one warmup and one iteration. Last library release 1.21.4 (2025-02); since then only CI work. Open: NullReferenceException on parallel Deserialize (#458), Native AOT crashes closed unfixed (#382, #414). Little-endian only.

## Caveats and trade-offs

The README chart image does carry a numeric ns table (serialize and deserialize for JsonResponseModel and Vector3[10000]). Against MessagePack-CSharp the standard-object gain is only \~1.6-1.7x, so the README's 'x2\~x5' holds only for protobuf-net and Orleans, and 'x10' is against System.Text.Json. The struct-array win is a blittable memcpy-style path. The chart dates from 2022 on .NET 7 with MessagePack-CSharp 2.4.x. The checked-in benchmark project now targets net8.0 with MessagePack 2.4.35, so it is not v3 and not exactly the setup that made the chart. Build config and flags are not stated; hardware is Ryzen 9 5950X.

C#-specific zero-encoding binary format, not schema-based or cross-language; requires source-generator attributes and partial classes; only limited version tolerance by default

## Maintenance

MIT with 4,739 stars and a stable NuGet package. The last library release is 1.21.4 (Feb 2025), and every commit since (latest 2026-07-08) is CI/chore work, so treat it as maintenance mode. Bugs such as #458 remain open, and the Native AOT crash reports were closed as stale without a fix.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party README chart (image with an embedded ns table) states .NET 7 and a Ryzen 9 5950X, and the benchmark code is public (sandbox/Benchmark/Benchmarks/SerializeTest.cs, DeserializeTest.cs). No build config, flags or BenchmarkDotNet job settings are given, and the struct-array gain is over 50x, so the tier is capped at C.
- **Verifier notes:** The entry is real and the baseline comparison is genuine. The downgrade is for the overstated standard-object multiplier against MessagePack-CSharp: the page's own table gives \~1.6-1.7x, not 2-5x. Tier stays C. Metadata checked: MIT, 4,739 stars, last commit 2026-07-08, not archived and not a fork.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Cysharp/MemoryPack#readme>
  - <https://github.com/Cysharp/MemoryPack>
  - <https://user-images.githubusercontent.com/46207/200979655-63ed38ae-dad2-4ca0-bbb7-9e0aa98914af.png>
  - <https://github.com/Cysharp/MemoryPack/blob/main/sandbox/Benchmark/Benchmark.csproj>
  - <https://github.com/Cysharp/MemoryPack/blob/main/sandbox/Benchmark/Benchmarks/SerializeTest.cs>
- **Sources the enricher read:**
  - <https://github.com/Cysharp/MemoryPack>
  - <https://github.com/Cysharp/MemoryPack#readme>
  - <https://user-images.githubusercontent.com/46207/200979655-63ed38ae-dad2-4ca0-bbb7-9e0aa98914af.png>
  - <https://github.com/Cysharp/MemoryPack/blob/main/src/MemoryPack.Core/MemoryPack.Core.csproj>
  - <https://github.com/Cysharp/MemoryPack/blob/main/src/MemoryPack.Core/MemoryPackWriter.cs>
  - <https://github.com/Cysharp/MemoryPack/blob/main/src/MemoryPack.Core/MemoryPackReader.cs>
  - <https://github.com/Cysharp/MemoryPack/blob/main/src/MemoryPack.Core/Formatters/UnmanagedFormatter.cs>
  - <https://github.com/Cysharp/MemoryPack/blob/main/src/MemoryPack.Core/Formatters/ArrayFormatters.cs>
  - <https://github.com/Cysharp/MemoryPack/blob/main/src/MemoryPack.Core/MemoryPackSerializer.Serialize.cs>
  - <https://github.com/Cysharp/MemoryPack/blob/main/src/MemoryPack.Core/MemoryPackSerializer.Deserialize.cs>
  - <https://github.com/Cysharp/MemoryPack/blob/main/src/MemoryPack.Core/MemoryPackFormatterProvider.cs>
  - <https://github.com/Cysharp/MemoryPack/blob/main/src/MemoryPack.Generator/MemoryPack.Generator.csproj>
  - <https://github.com/Cysharp/MemoryPack/blob/main/sandbox/Benchmark/Benchmark.csproj>
  - <https://github.com/Cysharp/MemoryPack/blob/main/sandbox/Benchmark/Program.cs>
  - <https://github.com/Cysharp/MemoryPack/blob/main/sandbox/Benchmark/Benchmarks/SerializeTest.cs>
  - <https://github.com/Cysharp/MemoryPack/blob/main/sandbox/Benchmark/Benchmarks/DeserializeTest.cs>
  - <https://github.com/Cysharp/MemoryPack/blob/main/sandbox/Benchmark/Benchmarks/SerializerTestBase.cs>
  - <https://github.com/Cysharp/MemoryPack/blob/main/sandbox/Benchmark/Models/Vector3.cs>
  - <https://github.com/Cysharp/MemoryPack/blob/main/sandbox/Benchmark/Models/BinaryPackModels/JsonResponseModel.cs>
  - <https://github.com/Cysharp/MemoryPack/releases>
  - <https://github.com/Cysharp/MemoryPack/commits/main>
  - <https://github.com/Cysharp/MemoryPack/issues>
  - <https://github.com/Cysharp/MemoryPack/issues/460>
  - <https://github.com/Cysharp/MemoryPack/issues/458>
  - <https://github.com/Cysharp/MemoryPack/issues/452>
  - <https://github.com/Cysharp/MemoryPack/issues/440>
  - <https://github.com/Cysharp/MemoryPack/issues/401>
  - <https://github.com/Cysharp/MemoryPack/issues/414>
  - <https://github.com/Cysharp/MemoryPack/issues/382>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/cysharp/memorypack`) · [data/wave4/enrich/raw/github_com_cysharp_memorypack.json](../../../data/wave4/enrich/raw/github_com_cysharp_memorypack.json) (enrichment confidence 0.8)

</details>
