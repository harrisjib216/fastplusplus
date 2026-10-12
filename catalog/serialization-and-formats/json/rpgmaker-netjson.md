# NetJSON

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `MIT` · 🟢 active

> C# JSON serializer that emits per-type IL at runtime; \~3.4x faster serialization than Json.NET in a 2014 benchmark.

| | |
|---|---|
| **Beats** | Json.NET (Newtonsoft.Json) |
| **Claimed result** | README states 3.4x faster than JSON.NET, 2.4x than ServiceStack JSON, 1.8x than Jil, 6x than JSON.NET BSON, 16.5x than JavaScriptSerializer, 4.3x than DataContractJsonSerializer, 1.6x than protobuf-net. In the linked 2014 theburningmonk results table (image), these ratios match serialization times only: NetJson 112.24 ms vs Json.Net 380.59 ms (\~3.39x, derived from linked table data). Deserialization gain is smaller: 175.00 ms vs 437.53 ms (\~2.5x vs Json.NET, derived). In that same table protobuf-net beat NetJSON on both serialization (100.68 vs 112.24 ms) and deserialization (163.20 vs 175.00 ms). The README's 1.6x-vs-protobuf-net figure comes from its own separate log: serialization 157.99 vs 257.98 ms, deserialization about equal (252.18 vs 251.50 ms). |
| **Workload** | Serialization and deserialization of a simple object (SimpleSpeedTester harness, theburningmonk 2014 JSON serializers benchmark), comparing NetJSON with Json.NET 6.0.4, ServiceStack.Text 4.0.24, Jil 1.7.0, protobuf-net, JavaScriptSerializer, DataContractJsonSerializer and others. The README's headline ratios correspond to serialization times. |
| **Metric** | throughput |
| **Adoption** | 238 stars; NuGet package NetJSON (latest 1.4.7, \~1.22M total downloads) |
| **Last commit** | 2026-09-05 |
| **Links** | [repository](https://github.com/rpgmaker/NetJSON) · [benchmark](https://github.com/rpgmaker/NetJSON) |

## Verdict

The README's ratios are serialization times from a 2014 theburningmonk SimpleSpeedTester run on one small object: NetJson 112.24 ms vs 380.59 ms for Json.NET 6.0.4 (\~3.4x). Deserialization was 175.00 vs 437.53 ms (\~2.5x), protobuf-net beat NetJSON on both, and no CPU, .NET runtime or build settings were given. The README's '1.6x faster than protobuf-net' comes from a separate undocumented log in which deserialization was a tie (252.18 vs 251.50 ms).

## Use it when

- Hot paths that serialize small, statically typed POCOs through the generic Serialize&lt;T&gt;. In the author's .NET 5 BenchmarkDotNet run (issue #238, i7-8650U), a 2-property object took 219.8 ns vs 503.0 ns for System.Text.Json.
- Legacy .NET Framework 3.5/4.0 code bases that need a faster JSON mapper than Json.NET. The 1.4.7 package still ships net35 and net40 builds.
- Services that exchange JSON as .NET strings (UTF-16) rather than UTF-8 byte buffers.
- Long-running processes with a fixed set of types, where the one-time IL-generation cost per type is paid back over many calls.
- Trusted, well-formed payloads produced by your own systems.

## Skip it when

- Object-typed data such as Dictionary&lt;string, object&gt; with mixed values, or boxed values. A contributor's .NET 5 run in issue #238 measured NetJSON at 6.387 us vs 1.494 us for System.Text.Json on such a dictionary, and a boxed int at 937 ns vs 161 ns.
- UTF-8 or stream pipelines such as ASP.NET Core request and response bodies. There is no byte[], Span, Stream or async API, and the TextReader overloads call ReadToEnd, so the whole payload is buffered (issue #232). Utf8Json beat NetJSON in the same #238 run (150.8 vs 219.8 ns).
- Untrusted input. The parser skips type validation by design, and infinite loops on malformed JSON have been reported and fixed several times (#197, #217, #226).
- High-precision decimal fields such as money: decimal values are parsed through a hand-written double parser (new Decimal(FastStringToDouble(...))), so digits beyond double precision are lost.
- Native AOT, trimmed or other no-JIT targets: serializers are emitted with Reflection.Emit at runtime and there is no source generator.

## How it is fast

The first time it sees a type, it generates a specialized serializer/deserializer class with System.Reflection.Emit (a TypeBuilder in one shared dynamic assembly plus DynamicMethod stubs) and caches it in a static generic field, so later calls do no reflection. The generated code appends into a StringBuilder cached per thread, formats integers with a 4-digit lookup table into stackalloc buffers (IntUtility), and deserializes by walking the string with unsafe char\* pointers and hand-written number parsers. Property names are matched by a generated chain of string.Equals checks. It deliberately skips type validation: the author declined type-mismatch checks for performance (issue #217).

## Compared with alternatives

No .NET siblings are catalogued in this category: the listed JSON entries (simdjson, yyjson, Sonic, orjson, sonic-rs, etc.) serve C/C++, Go, Rust or Python. NetJSON matters only if you are on .NET and want typed POCO-to-string mapping, not a native parser behind bindings.

## Integration

| | |
|---|---|
| **Form** | shared lib (NuGet package `NetJSON`, managed DLL). The library is five .cs files that need AllowUnsafeBlocks if you vendor them. |
| **Dependencies** | none on the net35 to net9.0 targets; the netstandard1.6/2.0 targets pull in the System.Reflection.Emit\* packages, plus Microsoft.Extensions.DependencyModel on 1.6 |
| **Minimum toolchain** | .NET Framework 3.5, .NET Standard 1.6 or .NET 5. The 1.4.7 package ships net35, net40, net462, net472, netstandard1.6, netstandard2.0 and net5.0 through net9.0 builds. |
| **Platforms** | Any OS or architecture running a JIT-capable CLR with Reflection.Emit; the code uses unsafe pointers. Native AOT support is not documented, and it is unlikely to work because serializers are generated at runtime. |
| **Thread safety** | Not documented. The caches are ConcurrentDictionary, type generation runs under locks, and the StringBuilders and settings are [ThreadStatic], so concurrent Serialize/Deserialize calls appear to be intended. The global static option setters are not synchronized. |
| **Drop-in for the baseline** | no |

## Gotchas

- Defaults differ from Json.NET. SkipDefaultValue is true, so members holding 0, false or null are left out of the output. The wiki documents the default DateFormat as a "\Date(value)" form, not ISO 8601.
- The global options (NetJSON.DateFormat, CaseSensitive and others, mostly [Obsolete]) are copied into a [ThreadStatic] NetJSONSettings.CurrentSettings the first time each thread uses it. Changing a static option later does not affect threads that have already serialized, so pass a NetJSONSettings instance instead.
- The IncludeFields setter ignores its argument and always sets true, so public fields are serialized along with properties. The wiki still says the default is false.
- GenerateTypesInto and GenerateAssembly can save a precompiled DLL only on .NET Framework. On .NET Standard and .NET 5+ the dynamic assembly is run-only, so the first-call IL-generation cost cannot be moved to build time.

## Known shortcomings

- The README ratios come from a 2014 blog run and are serialization-only (3.4x vs Json.NET); deserialization is about 2.5x. In that same table protobuf-net is faster than NetJSON, contradicting the README's '1.6x faster than protobuf-net'. No CPU or build configuration stated.
- Against System.Text.Json on .NET 5 (#238): about 2.3x faster on a 2-property object, but Utf8Json was faster still, and a contributor measured NetJSON 4.3-5.8x slower on object-typed data (Dictionary&lt;string,object&gt;, boxed int). Decimals are parsed through a double parser, losing precision. No type validation by design (#217) and past infinite loops on malformed JSON; not for untrusted input. No UTF-8/Span/Stream/async API; Reflection.Emit makes Native AOT unlikely.

## Caveats and trade-offs

The README ratios are serialization-only figures from a 2014 third-party blog post whose results are images, with no CPU, .NET runtime version or build configuration disclosed. The deserialization advantage is smaller (\~2.5x vs Json.NET). The cited blog table shows protobuf-net faster than NetJSON, contradicting the README's 1.6x claim, which comes from a separate undocumented run. Library versions are over a decade old. The blog's 'System.Text.Json 1.9.9.1' is an unrelated old package, and Microsoft's modern System.Text.Json incumbent was not tested.

The cited numbers come from a single 2014 third-party blog post (theburningmonk.com) built on the author's own SimpleSpeedTester harness; that page presents results as charts rather than a machine-readable table and does not state CPU/hardware or .NET runtime version; the comparison predates System.Text.Json (shipped in .NET Core 3.0), so the modern .NET default serializer was never benchmarked against it.

## Maintenance

Active but in single-maintainer bug-fix mode: releases are sporadic, and 1.4.7 (2026-09-05) fixed ISO DateTime formatting (#253, #254). It is MIT-licensed, has \~1.22M NuGet downloads and is easy to add from NuGet, but no UTF-8, Span or Stream support has landed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): downgrade; tier before verification C, tier now C.
- **Tier reason:** The README states ratios against Json.NET and others, and they trace to a 2014 single-blog benchmark (theburningmonk, SimpleSpeedTester harness) with results only as images. It gives no CPU, .NET runtime or build flags, and it is not a well-known benchmark suite, so tier C.
- **Verifier notes:** Downgraded for an overstated claim, not tier: the record presented serialization-only ratios as a round-trip result, and the cited source contradicts the protobuf-net ratio. The earlier caveat that the ratios could not be checked is wrong: the blog's second image is a readable ms table that matches the README's serialization ratios. Metadata checked: MIT, 238 stars, not a fork, last commit 2026-09-05 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** NetJSON issue #238 (BenchmarkDotNet, .NET 5, i7-8650U): 2-property object serialize 219.8 ns vs System.Text.Json 503.0 ns and Utf8Json 150.8 ns.
- **Pages the verifier opened:**
  - <https://github.com/rpgmaker/NetJSON>
  - <https://github.com/rpgmaker/NetJSON/blob/master/README.md>
  - <http://theburningmonk.com/2014/08/json-serializers-benchmarks-updated-2/>
  - <https://theburningmonk.com/2014/08/json-serializers-benchmarks-updated-2/>
  - <https://theburningmonk.com/wp-content/uploads/2014/08/image.png>
  - <https://theburningmonk.com/wp-content/uploads/2014/08/image1.png>
  - <https://api.nuget.org/v3/registration5-semver1/netjson/index.json>
  - <https://azuresearch-usnc.nuget.org/query?q=packageid:NetJSON&take=1>
- **Sources the enricher read:**
  - <https://github.com/rpgmaker/NetJSON>
  - <https://github.com/rpgmaker/NetJSON/blob/master/README.md>
  - <https://github.com/rpgmaker/NetJSON/wiki/Quick-Guide>
  - <https://raw.githubusercontent.com/wiki/rpgmaker/NetJSON/Quick-Guide.md>
  - <https://github.com/rpgmaker/NetJSON/blob/master/NetJSON/NetJSON.cs>
  - <https://github.com/rpgmaker/NetJSON/blob/master/NetJSON/NetJSON.Internals.cs>
  - <https://github.com/rpgmaker/NetJSON/blob/master/NetJSON/Models.cs>
  - <https://github.com/rpgmaker/NetJSON/blob/master/NetJSON/IntUtility.cs>
  - <https://github.com/rpgmaker/NetJSON/blob/master/NetJSON/NetJSON.nuspec>
  - <https://github.com/rpgmaker/NetJSON/blob/master/NetJSON/NetJSON.csproj>
  - <https://github.com/rpgmaker/NetJSON/blob/master/NetJSON.Standard2_0/NetJSON.Standard2_0.csproj>
  - <https://github.com/rpgmaker/NetJSON/blob/master/NetJSON.Net9_0/NetJSON.Net9_0.csproj>
  - <https://github.com/rpgmaker/NetJSON/blob/master/NetJSON.Benchmark.Net5_0/Program.cs>
  - <https://github.com/rpgmaker/NetJSON/blob/master/NetJSON.Benchmark.Net5_0/Benchmark.cs>
  - <https://github.com/rpgmaker/NetJSON/blob/master/NetJSON.Benchmark.Net5_0/Models/SimpleObjectBenchmark.cs>
  - <https://github.com/rpgmaker/NetJSON/blob/master/NetJSON.Benchmark.Net5_0/Models/DictionariesBenchmark.cs>
  - <https://github.com/rpgmaker/NetJSON/issues>
  - <https://github.com/rpgmaker/NetJSON/issues/252>
  - <https://github.com/rpgmaker/NetJSON/issues/238>
  - <https://github.com/rpgmaker/NetJSON/issues/232>
  - <https://github.com/rpgmaker/NetJSON/issues/226>
  - <https://github.com/rpgmaker/NetJSON/issues/217>
  - <https://github.com/rpgmaker/NetJSON/issues/254>
  - <https://github.com/rpgmaker/NetJSON/commits/master>
  - <https://theburningmonk.com/2014/08/json-serializers-benchmarks-updated-2/>
  - <https://theburningmonk.com/wp-content/uploads/2014/08/image1.png>
  - <https://azuresearch-usnc.nuget.org/query?q=packageid:NetJSON&take=1>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/rpgmaker/netjson`) · [data/wave4/enrich/raw/github_com_rpgmaker_netjson.json](../../../data/wave4/enrich/raw/github_com_rpgmaker_netjson.json) (enrichment confidence 0.75)

</details>
