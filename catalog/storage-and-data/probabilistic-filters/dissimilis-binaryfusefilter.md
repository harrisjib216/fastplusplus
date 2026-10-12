# BinaryFuseFilter (.NET)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `MIT` · 🟢 active

> Managed C# binary fuse filter: about 9 bits/key at 0.39% FPP, queried \~21x faster than BloomFilter.NetCore.

| | |
|---|---|
| **Beats** | Bloom filter (BloomFilter.NetCore package) |
| **Claimed result** | Query: BloomFilter.NetCore time ratio 20.76 vs BinaryFuse8Filter's 1.00 (BloomFilter.NetCore \~20.76x slower). Construction: BloomFilter.NetCore ratio 2.32 (86x more allocation) vs 1.00 for BinaryFuse8Filter. Also beats XORFilterDotNet (8.68x slower query; 58.6x slower / 366x more allocation to construct). |
| **Workload** | BenchmarkDotNet run on .NET 10 x64: mixed hit/miss query-latency and construction-time ratios over 1,000,000 pre-hashed 64-bit keys, comparing BinaryFuse8Filter against BloomFilter.NetCore (same 0.39% FPP) and XORFilterDotNet. |
| **Metric** | throughput |
| **Compiler and flags** | .NET 10, Release configuration, BenchmarkDotNet (`dotnet run -c Release --project src/BinaryFuseFilter.Benchmarks`) |
| **Adoption** | 1 star; NuGet BinaryFuseFilter 1.0.0 \~131 total downloads |
| **Last commit** | 2026-08-03 |
| **Links** | [repository](https://github.com/Dissimilis/BinaryFuseFilter) · [benchmark](https://github.com/Dissimilis/BinaryFuseFilter#performance) |

## Verdict

In one BenchmarkDotNet run on .NET 10 x64 (CPU not stated), with 4,096 half-hit/half-miss lookups against filters built from 1M random 64-bit keys, BinaryFuse8Filter was 20.76x faster than BloomFilter.NetCore 3.0.0 at the same 0.39% FPP and 8.68x faster than XORFilterDotNet 1.2.0, and it built from 1M keys 2.32x faster than creating the Bloom filter and adding every key (86x less allocation). Only ratios are published, and both baselines hash 8-byte arrays internally (the Bloom filter also locks on every call), so the ratios compare these libraries, not Bloom vs binary fuse as algorithms.

## Use it when

- In-process .NET sets that are static or rebuilt now and then (blocklists, known-ID sets, 'definitely not in cache/DB/disk' pre-checks), queried far more often than built, where memory is the limit: about 9 bits/key, against 64+ bits/key for a FrozenSet&lt;ulong&gt;.
- You already have 64-bit IDs or hashes. The ulong API mixes each key with a Murmur64 finalizer, so raw sequential IDs work. For string, byte[] or Guid keys, the generic wrapper hashes with XxHash64.
- Replacing BloomFilter.NetCore's in-memory filter for a fixed set on a hot path. Its per-call lock and byte[] hashing are what the 20.76x query and 2.32x build ratios expose.
- Filters built once and shipped to other processes or to disk. The 32-byte little-endian header is checked field by field before load, and the same keys on the same library version serialize to identical bytes.
- Codebases targeting anything from netstandard2.0 to net10.0 that want no native dependencies. Hashing and serialization have explicit big-endian paths.

## Skip it when

- The set changes over time, or you need a shared or distributed filter. There is no Add or Remove, so every change is a full rebuild. BloomFilter.NetCore supports inserts and has Redis backends.
- Memory is not tight. In the same run, an exact FrozenSet&lt;ulong&gt; queried only 1.13x slower than BinaryFuse8 at 1M keys and has no false positives. What you gain here is mainly about 7x less memory, not speed.
- Filters far larger than CPU cache. The published query ratios use a 1M-key filter of about 1.1 MB, which the author calls cache-resident. Every lookup makes three random reads, and there is no Bloom comparison at the 32M-key (\~36 MB) scale that the BatchScale benchmark runs.
- You need an FPP between the fixed steps, or the smallest static filter possible. Only 8/16/32-bit widths exist, with no 4-wise fuse or ribbon option. Ribbon filters (BuRR, RocksDB Ribbon) get closer to the space lower bound.
- You need a proven dependency. It is at v1.0.0 only: all 22 commits landed in about 2.5 hours on 2026-08-03, and there are 1 star, about 131 NuGet downloads and no issues or PRs. The netstandard2.0 build compiles, but CI runs tests only on net8.0 and net10.0 on ubuntu-latest.

## How it is fast

It implements binary fuse filters (Graf & Lemire, JEA 2022, arXiv:2201.01174): each key maps to three fingerprint slots in adjacent power-of-two segments, and construction peels the 3-uniform hypergraph (a queue of degree-one slots, then back-substitution from a stack) so that fingerprint(key) = F[h0] ^ F[h1] ^ F[h2]. A query does one Murmur64 finalizer on key+seed, a 64x32 multiply-high and two masked offsets, then three loads through `Unsafe.Add` refs with no branches or bounds checks, where a Bloom filter needs k probes (optimal k is about 8 at 0.39% FPP). Construction is a port of FastFilter/xorfilter's Go code with bounds-check-free refs, ArrayPool scratch buffers and a Vector256/Vector128 scan for degree-one slots on net8.0+. Much of the measured gap is the baseline's cost, though: BloomFilter.NetCore's `FilterMemory.Contains` computes all k Murmur3 positions from the byte span, takes an AsyncLock on every call, then reads BitArray buckets.

## Compared with alternatives

It is the only .NET entry in this category, so pick it for a static key set in C#; in C, Go, Rust or Java, use the older and far more widely used xor_singleheader, FastFilter/xorfilter, xorf or komiya-atsushi/xor-filter. If the set needs inserts or deletes, a cuckoo or quotient filter (efficient/cuckoofilter, CQF) fits instead.

## Integration

| | |
|---|---|
| **Form** | module (NuGet package BinaryFuseFilter; a pure managed assembly of about 15 small .cs files, easy to vendor under MIT) |
| **Dependencies** | System.IO.Hashing (XxHash64 for the generic hashers), plus System.Memory on netstandard2.0. MinVer and SourceLink are build-only. |
| **Minimum toolchain** | Consumers need netstandard2.0 or net8.0/net9.0/net10.0. Building the repo needs .NET SDK 10.0.100 (global.json) and LangVersion latest. The SIMD construction scan and Math.BigMul path are compiled only for net8.0+. |
| **Platforms** | Any .NET runtime and architecture (pure managed code). On net8.0+, construction uses Vector256 or Vector128 when hardware-accelerated and falls back to scalar code otherwise. Queries are scalar everywhere. Serialization and built-in hashing are endianness-independent. |
| **Thread safety** | Documented: filters are immutable, and queries are thread-safe and never throw. Tests cover parallel queries and concurrent independent builds, which use pooled scratch arrays. |
| **Drop-in for the baseline** | partial — it replaces a Bloom filter only for a static set. You pass the full key set to Create (pre-hashed ulongs, or T through a hasher), and the API has no Add, no incremental growth, no async or Redis variants, and only three FPP choices. Query calls look similar (Contains). |

## Gotchas

- BinaryFuseFilter&lt;T&gt; serializes only the core filter. Deserializing with a different hasher than the one used to build it gives silently wrong answers, as the README warns. The built-in string hasher hashes UTF-16 code units, so hashes of the same text as UTF-8 bytes elsewhere will not match.
- Seeds are deterministic: the first is SplitMix64 from a fixed state of 1, and the seed is stored in the serialized header. The built-in integer hashers are identity functions. Anyone who knows the filter can therefore compute false-positive keys, so do not use it as a security boundary against attacker-chosen queries.
- From the code, construction rents about 24 bytes/key of scratch (13 B per slot at about 1.125 slots/key, plus 9 B per key) from ArrayPool&lt;T&gt;.Shared, and those arrays can stay pooled after the build. Create(IEnumerable) and the generic Create also copy the input to arrays. The fingerprint array is capped below 2^31 elements, and Create throws InvalidOperationException if 1,024 seeds fail, which the code says should not happen.
- The benchmark source warns that 'the benchmark machine is busy: judge by the Ratio column within one run only'. BinaryFuse32 queried faster than BinaryFuse16 (ratios 1.32 vs 1.41), which points to noise. The batch Contains(span) API is no faster than a plain loop (README; a 4-wide interleaved version lost by 13-17%).

## Known shortcomings

- The Bloom/XOR baselines hash key bytes while the fuse filter takes pre-hashed keys, so part of the 20.76x is hashing; NuGet \~131 downloads.
- The Bloom baseline (BloomFilter.NetCore) takes an AsyncLock on every Contains and hashes byte[], so the 20.76x is a library gap, not an algorithm gap; FrozenSet&lt;ulong&gt; is only 1.13x slower at 1M keys, so the real win is \~7x less memory. One noisy run with a cache-resident 1.1 MB filter. Immutable, FPP fixed at 8/16/32 bits, deterministic seeds stored in the header (false-positive keys are computable); v1.0.0 written in one afternoon; deserializing Generic&lt;T&gt; with the wrong hasher gives silent wrong answers.

## Caveats and trade-offs

This is a very new, single-author repo (1 star; the NuGet package BinaryFuseFilter 1.0.0 has about 131 total downloads). The CPU model is not stated, so the evidence is capped below A/B. The comparison is not like-for-like: per QueryBenchmarks.cs, BinaryFuse8Filter queries pre-hashed ulong keys, while BloomFilter.NetCore and XORFilterDotNet receive 8-byte arrays and hash them internally (the source notes this for XORFilterDotNet). Part of the 20.76x query ratio is therefore hashing overhead and BloomFilter.NetCore's implementation, not a fundamental Bloom-filter limit. All figures are ratios from a single run; no absolute times are published.

Filter is immutable after construction (no add/remove); pure managed C#, no native dependencies.

## Maintenance

A brand-new single-author MIT project whose v1.0.0 shipped on 2026-08-03 after one day of work, with no commits since; it is small and well-tested enough to vendor, but has almost no users yet.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Performance section has first-party BenchmarkDotNet time ratios from one run on .NET 10 x64, and the benchmark code is public (src/BinaryFuseFilter.Benchmarks/QueryBenchmarks.cs, ConstructionBenchmarks.cs). The page does not state the CPU model, so it is C.
- **Verifier notes:** The README tables match the claim exactly. Query ratios: Bloom 20.76, XOR 8.68. Construction ratios: Bloom 2.32 time / 86 allocation; XOR 58.6 time / 366 allocation. MIT, not a fork, last commit 2026-08-03 ('active'), all confirmed through gh.
- **Fields the verifier corrected:** `caveats`, `stars_or_usage`
- **Pages the verifier opened:**
  - <https://github.com/Dissimilis/BinaryFuseFilter>
  - <https://github.com/Dissimilis/BinaryFuseFilter#performance>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/HEAD/src/BinaryFuseFilter.Benchmarks/QueryBenchmarks.cs>
  - <https://azuresearch-usnc.nuget.org/query?q=packageid:BinaryFuseFilter&prerelease=true>
- **Sources the enricher read:**
  - <https://github.com/Dissimilis/BinaryFuseFilter>
  - <https://github.com/Dissimilis/BinaryFuseFilter#performance>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter/BinaryFuseCore.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter/BinaryFuse8Filter.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter/BinaryFuseFilter.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter/BinaryFuseFilterOfT.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter/Hashing.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter/DefaultHashers.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter/FilterLayout.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter/FingerprintOps.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter/Serialization.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter/BinaryFuseFilter.csproj>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/Directory.Build.props>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/Directory.Packages.props>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/global.json>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter.Baseline/README.md>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter.Benchmarks/QueryBenchmarks.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter.Benchmarks/ConstructionBenchmarks.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter.Benchmarks/BatchScaleBenchmarks.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter.Benchmarks/BaselineBenchmarks.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter.Benchmarks/BinaryFuseFilter.Benchmarks.csproj>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter.Benchmarks/Program.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter.Tests/ConcurrencyTests.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter.Tests/FalsePositiveTests.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter.Tests/ConstructionTests.cs>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/src/BinaryFuseFilter.Tests/BinaryFuseFilter.Tests.csproj>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/.github/workflows/ci.yml>
  - <https://github.com/Dissimilis/BinaryFuseFilter/blob/main/.github/workflows/release.yml>
  - <https://github.com/Dissimilis/BinaryFuseFilter/commits/main>
  - <https://github.com/Dissimilis/BinaryFuseFilter/releases/tag/v1.0.0>
  - <https://azuresearch-usnc.nuget.org/query?q=packageid:BinaryFuseFilter&prerelease=true>
  - <https://github.com/vla/BloomFilter.NetCore/blob/master/README.md>
  - <https://github.com/vla/BloomFilter.NetCore/blob/master/src/BloomFilter/FilterMemory.cs>
  - <https://arxiv.org/abs/2201.01174>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/dissimilis/binaryfusefilter`) · [data/wave6/enrich/raw/github_com_dissimilis_binaryfusefilter.json](../../../data/wave6/enrich/raw/github_com_dissimilis_binaryfusefilter.json) (enrichment confidence 0.8)

</details>
