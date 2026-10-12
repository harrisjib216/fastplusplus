# SimdUnicode

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C#` · `MIT` · 🟢 active

> Drop-in faster UTF-8 validator for .NET, beating the runtime's private SIMD validator on non-ASCII text.

| | |
|---|---|
| **Beats** | .NET runtime's built-in UTF-8 validator (Utf8Utility.GetPointerToFirstInvalidByte; private in the runtime, benchmarked through a vendored MIT copy in benchmark/UTF8_runtime.cs) |
| **Claimed result** | README, Intel Xeon Gold 6548N (.NET 10, AVX-512): up to 14x on Emoji-Lipsum (15 vs 1.1 GB/s), 2.5x on Twitter.json (36 vs 14 GB/s), 2.8x-9.1x on other non-ASCII lipsum sets, and slower than .NET on pure-ASCII Latin-Lipsum (72 vs 107 GB/s). Apple M2: 1.5x-4.1x (Twitter.json 1.8x, 25 vs 14 GB/s). Graviton 3 / Neoverse V1 / Qualcomm 8cx gen3 / Graviton 2: 1.2x-5.8x. The earlier blog post (2024-06-20) reported Ice Lake up to 13x on emoji and 2.4x on Twitter.json (29 vs 12 GB/s). |
| **Workload** | UTF-8 validation (GetPointerToFirstInvalidByte) of Twitter.json and lipsum texts in Arabic, Chinese, emoji, Hebrew, Hindi, Japanese, Korean, Latin and Russian, with BenchmarkDotNet on x64 (AVX-512) and several ARM64 systems |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Gold 6548N (x64 AVX-512); Apple M2; AWS Graviton 3 (Neoverse V1); Qualcomm 8cx gen3; Graviton 2 (Neoverse N1). Earlier blog run: Intel Ice Lake |
| **Compiler and flags** | .NET 10 (net10.0), BenchmarkDotNet 0.15.4, `dotnet run -c Release`; AVX-512 kernel on x64, NEON on ARM; .NET version not stated for the ARM tables |
| **Adoption** | 49 stars; the author (Lemire) proposed it for the .NET runtime in dotnet/runtime issue #103781 (open) |
| **Last commit** | 2026-08-19 |
| **Links** | [repository](https://github.com/simdutf/SimdUnicode) · [benchmark](https://github.com/simdutf/SimdUnicode/blob/main/README.md) |

## Verdict

On an Intel Xeon Gold 6548N (.NET 10, AVX-512, BenchmarkDotNet 0.15.4, dotnet run -c Release), SimdUnicode reaches 36 GB/s vs 14 GB/s (2.5x) on Twitter.json and up to 14x on Emoji-Lipsum (15 vs 1.1 GB/s), measured against a vendored copy of the runtime's private Utf8Utility.GetPointerToFirstInvalidByte; it is slower than .NET on pure ASCII (72 vs 107 GB/s). ARM64 systems (Apple M2, Graviton 2/3, Qualcomm 8cx gen3) show 1.2x-5.8x gains, with .NET version unstated for those runs.

## Use it when

- Validating mixed or mostly non-ASCII UTF-8 (Arabic, CJK, emoji, Hindi, etc.) on a hot path
- Running on AVX-512-capable x64 (Zen 4 / Ice Lake+) or ARM64 NEON hardware, where the gap is largest
- .NET 10 codebases that need an unsafe byte\* validation entrypoint mirroring the private runtime API
- Need the offset of the first invalid byte, not just a valid/invalid boolean
- Comfortable vendoring MIT-licensed source directly since there is no NuGet package

## Skip it when

- Pure-ASCII-heavy workloads on x64: .NET 10's own validator is faster there (107 vs 72 GB/s, Latin-Lipsum)
- Need a managed/safe API; this is unsafe pointer-only, no documented Span&lt;byte&gt; overload
- Fuzzing is still an open item (issue #27), so hardening against adversarial input is unproven beyond unit tests
- Small user base (49 stars) and source-drop-only distribution, no package manager integration
- Targeting anything outside C#/.NET; no bindings for other runtimes

## How it is fast

Implements the Keiser-Lemire 'less than one instruction per byte' UTF-8 validation algorithm (arXiv 2010.03090), the same algorithm used by Node.js, Bun, GraalVM and PHP. It processes 16-64 bytes per iteration with SIMD shuffle-based lookup tables that classify byte roles and continuation-byte counts in a handful of vector ops instead of per-byte branches. A runtime dispatcher picks the widest available kernel per host CPU: NEON on ARM64, then AVX-512BW, AVX2, SSE4.2/SSSE3, falling back to a scalar implementation.

## Compared with alternatives

Pick SimdUnicode when you're specifically on .NET and want the fastest available replacement for Utf8Utility.GetPointerToFirstInvalidByte; unlike simdutf8 (Rust) or utf8_range (C++/protobuf), it's the only sibling targeting the C#/.NET runtime and its own private validator as baseline. For non-.NET stacks or a larger adoption base, look at simdutf8 or utf8_range instead.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none |
| **Minimum toolchain** | .NET 10 (net10.0), AllowUnsafeBlocks enabled |
| **Platforms** | x86-64 (SSE4.2/AVX2/AVX-512BW tiers), aarch64 (NEON), scalar fallback elsewhere |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | partial — same signature and semantics as Utf8Utility.GetPointerToFirstInvalidByte, but that method is private in the BCL, so callers must reference SimdUnicode.UTF8 explicitly rather than getting it automatically via the runtime |

## Gotchas

- unsafe byte\* API only; caller manages pinning and buffer lifetime, no managed overload
- slower than the built-in .NET validator on pure ASCII text (Latin-Lipsum benchmark)
- SharpFuzz fuzzing not yet wired in (issue #27 open); correctness on hostile input relies on unit tests only
- ARM benchmark tables don't state a .NET version, unlike the fully specified x64 table

## Caveats and trade-offs

First-party benchmark (simdutf/Lemire team). The baseline is a vendored copy of the runtime's private validator compiled into the benchmark, not the shipped BCL call path. On pure ASCII (Latin-Lipsum), .NET 10's own validator is faster on x64 (107 vs 72 GB/s). .NET version is not stated for the ARM results. Low adoption (49 stars).

C#/.NET only; baseline being beaten is .NET's own SIMD-accelerated validator (already fast), not ICU/std::codecvt/simdutf directly, though it is the same simdutf-family algorithm ported to C#

## Maintenance

Actively maintained (last commit 2026-08-19) and MIT-licensed, small enough to vendor as source, but adoption is minimal (49 stars) and it remains a self-proposed candidate for the .NET runtime (dotnet/runtime#103781) rather than a shipped feature.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now A.
- **Tier reason:** Tier upgraded to A on stronger evidence. The repo README's x64 results name an Intel Xeon Gold 6548N and .NET 10 (AVX-512), and the public BenchmarkDotNet code (benchmark/Benchmark.cs, net10.0, run with `dotnet run -c Release`) benchmarks against a vendored copy of the runtime's Utf8Utility.GetPointerToFirstInvalidByte. The cited blog post alone is first-party with only a microarchitecture name ('Ice Lake'), which would be C, not B.
- **Verifier notes:** The blog numbers in the record are accurate. The README has newer, fully specified x64 results (Xeon Gold 6548N, .NET 10), so I moved benchmark_url there and upgraded the tier to A. Issue #103781 was opened by lemire himself, so 'flagged as a candidate' is a self-proposal. Metadata matches: MIT, 49 stars, last commit 2026-08-19.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `baseline`, `compiler_and_flags`, `hardware`, `workload`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://lemire.me/blog/2024/06/20/validating-gigabytes-of-unicode-strings-per-second-in-c/>
  - <https://github.com/simdutf/SimdUnicode>
  - <https://github.com/simdutf/SimdUnicode/blob/main/README.md>
  - <https://github.com/simdutf/SimdUnicode/blob/main/benchmark/Benchmark.cs>
  - <https://github.com/simdutf/SimdUnicode/blob/main/benchmark/benchmark.csproj>
  - <https://github.com/simdutf/SimdUnicode/blob/main/benchmark/UTF8_runtime.cs>
  - <https://github.com/dotnet/runtime/issues/103781>
- **Sources the enricher read:**
  - <https://github.com/simdutf/SimdUnicode>
  - <https://github.com/simdutf/SimdUnicode/blob/main/README.md>
  - <https://github.com/simdutf/SimdUnicode/blob/main/src/SimdUnicode.csproj>
  - <https://github.com/simdutf/SimdUnicode/blob/main/docs/articles/how-it-works.md>
  - <https://github.com/simdutf/SimdUnicode/blob/main/info/FUTUREWORK.md>
  - <https://github.com/simdutf/SimdUnicode/blob/main/src/UTF8.cs>
  - <https://github.com/simdutf/SimdUnicode/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/simdutf/simdunicode`) · [data/wave3/enrich/raw/github_com_simdutf_simdunicode.json](../../../data/wave3/enrich/raw/github_com_simdutf_simdunicode.json) (enrichment confidence 0.6)

</details>
