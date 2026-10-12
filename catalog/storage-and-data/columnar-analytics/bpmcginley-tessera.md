# Tessera

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Columnar analytics](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C#` · `MIT` · 🟢 active

> Small .NET 9 columnar library whose sorted merge-sweep as-of join is about 14x faster than pandas.merge_asof on 1M x 1M rows.

| | |
|---|---|
| **Beats** | pandas |
| **Claimed result** | Tessera merge-sweep: 10.8ms mean (\~92M rows/s, 11.4MB allocated) vs pandas.merge_asof: 152.8ms (\~6.5M rows/s) -- about 14x faster; also \~7.7x faster than a per-symbol binary-search join implemented in C# |
| **Workload** | Backward as-of join (merge_asof semantics) of 1,000,000 trades against 1,000,000 quotes across 500 symbols, on a single dev laptop with .NET 9 |
| **Metric** | throughput |
| **Hardware** | unstated ('single dev laptop'; the SIMD section says AVX2, 4 doubles/lane) |
| **Compiler and flags** | .NET 9, Release configuration (BenchmarkDotNet via dotnet run -c Release); pandas/numpy/Python versions unstated |
| **Adoption** | 1 star |
| **Last commit** | 2026-06-27 |
| **Links** | [repository](https://github.com/bpmcginley/Tessera) · [benchmark](https://github.com/bpmcginley/Tessera#results) |

## Verdict

Synthetic data: 1M trades and 1M quotes over 500 symbols, pre-sorted, with int symbol codes. BenchmarkDotNet (.NET 9 Release) reports a mean of 10.8 ms for Tessera's backward join, against 82.9 ms for a hand-written C# per-symbol binary-search join (\~7.7x). A separate Python script times a single pandas.merge_asof call with perf_counter after a 1,000-row warm-up and gets 152.8 ms (\~14x). The two sides generate the same data shape with different RNGs (System.Random vs numpy), not identical rows. Pandas, NumPy and Python versions and the CPU are not stated beyond 'single dev laptop'.

## Use it when

- A .NET 9 backtester or tick-processing service that must attach the prevailing quote to each trade, in memory, on arrays in the \~1M-row range
- Feeds already sorted by time with int64 nanosecond timestamps and a modest, dense symbol universe (the benchmark uses 500 symbols)
- You need pandas-style backward, forward or nearest as-of semantics with tolerance and allowExactMatches, but inside a C# process without Python
- You want a short, readable implementation to vendor and adapt: the core is a handful of source files with no runtime dependencies
- Building OHLCV+VWAP bars from ticks in the same process (supported, but not benchmarked)

## Skip it when

- Your pipeline is in pandas or Python: there are no Python bindings, and moving DataFrames into .NET plus factorizing keys is outside the benchmarked time
- General dataframe work: there are no equality joins, group-by, filters, expression layer or file readers and writers in the source tree
- Data larger than RAM: memory-mapped, out-of-core columns are an unchecked roadmap item
- Production-critical use: all 7 commits landed within about a day (2026-06-26 to 06-27), with AI co-author trailers. It has 1 star, no releases, no NuGet package and no issues filed, so there is no outside usage signal
- Very high-cardinality or sparse keys: the group table is sized to max code + 1 on every join (twice for nearest), and CombineCodes throws if the product of cardinalities overflows int32. The sweep is single-threaded

## How it is fast

It uses a sort-merge as-of join. Because both inputs are globally sorted by time, one right-side cursor only moves forward while the left rows are walked. A per-group 'last seen row' array indexed directly by the dense int symbol code replaces any per-row search, so the join is a single O(n+m) pass. Output is a gather through an int32 match-index array allocated uninitialized, which is why the result costs only about 11.4 MB. Current pandas main also does a single sorted sweep (Cython asof_join_backward_on_X_by_Y) but keys it with a khash int64 hash table and adds validation and DataFrame overhead. So the win over pandas comes from direct array indexing and lower constant factors, not from better asymptotics. The O(n+m) vs O(n log m) framing applies only to the repo's own C# binary-search baseline.

## Compared with alternatives

Pick Tessera when you need an as-of join on in-memory arrays inside a .NET process. Pick QuestDB when the data already lives in a time-series database (its SQL ASOF JOIN supports ON keys and TOLERANCE), and data.table when you work in R (rolling joins via roll=TRUE/'nearest'). chDB and cuDF (cudf.pandas) are better when you want to keep a pandas-shaped workflow rather than port to C#.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none for Tessera.Core (BenchmarkDotNet 0.14.0 for the benchmarks, xunit 2.9.2 for the tests) |
| **Minimum toolchain** | .NET 9 SDK (targets net9.0 with LangVersion latest; uses C# collection expressions and static abstract interface members) |
| **Platforms** | any platform .NET 9 runs on. The as-of join is scalar code; VectorOps uses the portable System.Numerics.Vector&lt;T&gt;, whose width depends on hardware (the comments cite 4 doubles on AVX2 and 8 on AVX-512) |
| **Thread safety** | not documented. The operations are static methods over immutable Tables with no shared state, but Column.Values hands out the mutable backing array, and tables share arrays |
| **Drop-in for the baseline** | partial: it follows pandas merge_asof semantics (directions, tolerance, allowExactMatches, ties to backward on nearest) but is a C# API. It needs time as long ns, int32 dense 'by' codes and pre-sorted input, and tolerance=0 means something different |

## Gotchas

- Sortedness is not validated. Unsorted or only per-group-sorted time columns give silently wrong matches, whereas pandas raises 'left keys must be sorted'. Run Table.SortByTime first; it is a comparison-delegate Array.Sort whose cost is not in the benchmark
- tolerance &lt;= 0 means no limit, while in pandas tolerance=0 is valid (non-negative) and restricts matches to equal timestamps
- Unmatched rows get NaN only for double and float columns. Int and long 'bring' columns get 0 (a test asserts this), which cannot be told apart from real zeros. There is no null mask
- Both sides must use one shared code mapping (Categoricals.FactorizeShared). Factorizing each table separately silently mismatches symbols, and a negative code would index out of range

## Known shortcomings

- pandas was timed once with perf_counter against a BenchmarkDotNet mean for the C# side; no CPU model; the repo is about a day old with 1 star.
- The 14x is not asymptotic (pandas' merge_asof is also a single O(n+m) sweep); the win is direct array indexing and low overhead. No sortedness check, so unsorted input gives silent wrong results (pandas raises); tolerance=0 means no limit (pandas: exact only); unmatched int columns become 0, not null. The C# and Python benches use different RNGs (not identical rows); single-threaded, no out-of-core; about a day of history with an AI co-author, no NuGet release.

## Caveats and trade-offs

Very small single-author project (1 star). The repo was created 2026-06-26 and all 7 commits landed between 2026-06-26 and 2026-06-27, so the project was about a day old at its last commit, not a month. No CPU model is stated (only 'single dev laptop'; the SIMD section says AVX2) and the pandas, numpy and Python versions are not given, which caps evidence at tier C. The comparison is one specialized operation (a backward as-of join on presorted data with pre-factorized int symbol codes), not general dataframe performance. The pandas side is a single time.perf_counter measurement after a small warm-up, while the C# side is a BenchmarkDotNet mean, so the \~14x crosses languages and timing methods.

Requires inputs pre-sorted by time; join key must be a dense int code (via provided Categoricals.Factorize helpers); no out-of-core / memory-mapped support yet; narrow scope (as-of join + OHLCV bars + a few vectorized column ops), not a general dataframe library.

## Maintenance

The repo is technically 'active', but its whole history spans about one day (last commit 2026-06-27). It is MIT-licensed and small enough to copy the few source files, but it is not published to NuGet and several unrelated 'Tessera' packages already exist there.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README Results table shows Tessera at 10.8 ms (\~92M rows/s, 11.4 MB), a per-symbol binary-search join at 82.9 ms and pandas.merge_asof at 152.8 ms, with the \~14x and \~7.7x stated. The benchmark code is public (bench/Tessera.Benchmarks/Program.cs uses BenchmarkDotNet; bench/python/merge_asof_bench.py) and it runs on .NET 9 Release, but no CPU model or pandas/Python version is given, so the tier stays at C.
- **Verifier notes:** The numbers match the README exactly, and the metadata checks out (MIT, 1 star, last commit 2026-06-27, not a fork). The caveat's '\~1 month old' was wrong: the whole history spans about a day. The commits carry an AI co-author trailer.
- **Fields the verifier corrected:** `caveats`, `hardware`, `compiler_and_flags`
- **Pages the verifier opened:**
  - <https://github.com/bpmcginley/Tessera>
  - <https://github.com/bpmcginley/Tessera#results>
  - <https://github.com/bpmcginley/Tessera/blob/main/bench/Tessera.Benchmarks/Program.cs>
  - <https://github.com/bpmcginley/Tessera/blob/main/bench/python/merge_asof_bench.py>
- **Sources the enricher read:**
  - <https://github.com/bpmcginley/Tessera>
  - <https://github.com/bpmcginley/Tessera#results>
  - <https://github.com/bpmcginley/Tessera/blob/main/src/Tessera.Core/AsOfJoin.cs>
  - <https://github.com/bpmcginley/Tessera/blob/main/src/Tessera.Core/Columns.cs>
  - <https://github.com/bpmcginley/Tessera/blob/main/src/Tessera.Core/Table.cs>
  - <https://github.com/bpmcginley/Tessera/blob/main/src/Tessera.Core/Categoricals.cs>
  - <https://github.com/bpmcginley/Tessera/blob/main/src/Tessera.Core/Sorting.cs>
  - <https://github.com/bpmcginley/Tessera/blob/main/src/Tessera.Core/Bars.cs>
  - <https://github.com/bpmcginley/Tessera/blob/main/src/Tessera.Core/VectorOps.cs>
  - <https://github.com/bpmcginley/Tessera/blob/main/src/Tessera.Core/Tessera.Core.csproj>
  - <https://github.com/bpmcginley/Tessera/blob/main/bench/Tessera.Benchmarks/Program.cs>
  - <https://github.com/bpmcginley/Tessera/blob/main/bench/Tessera.Benchmarks/Tessera.Benchmarks.csproj>
  - <https://github.com/bpmcginley/Tessera/blob/main/bench/python/merge_asof_bench.py>
  - <https://github.com/bpmcginley/Tessera/blob/main/tests/Tessera.Tests/Tessera.Tests.csproj>
  - <https://github.com/bpmcginley/Tessera/blob/main/tests/Tessera.Tests/AsOfJoinTests.cs>
  - <https://github.com/bpmcginley/Tessera/blob/main/tests/Tessera.Tests/AsOfDirectionTests.cs>
  - <https://github.com/bpmcginley/Tessera/commits/main>
  - <https://github.com/bpmcginley/Tessera/issues>
  - <https://github.com/bpmcginley/Tessera/releases>
  - <https://azuresearch-usnc.nuget.org/query?q=Tessera&take=10>
  - <https://raw.githubusercontent.com/pandas-dev/pandas/main/pandas/core/reshape/merge.py>
  - <https://raw.githubusercontent.com/pandas-dev/pandas/main/pandas/_libs/join.pyx>
  - <https://raw.githubusercontent.com/Rdatatable/data.table/master/man/data.table.Rd>
  - <https://github.com/questdb/documentation/blob/main/documentation/query/sql/asof-join.md>
  - <https://hn.algolia.com/api/v1/search?query=bpmcginley%20Tessera&restrictSearchableAttributes=url>
  - <https://hn.algolia.com/api/v1/search?query=Tessera%20merge_asof>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/bpmcginley/tessera`) · [data/wave6/enrich/raw/github_com_bpmcginley_tessera.json](../../../data/wave6/enrich/raw/github_com_bpmcginley_tessera.json) (enrichment confidence 0.8)

</details>
