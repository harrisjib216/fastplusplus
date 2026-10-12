# CharConv.h (rigtorp)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Number parsing and formatting](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Header-only base-10 int32/int64 to/from-string conversion; beats stringstream, to_string, atoi/strtol, stoi.

| | |
|---|---|
| **Beats** | iostreams (std::stringstream); std::to_string; std::stoi/atoi/strtol |
| **Claimed result** | Own to_chars takes 9-20 ns, against sprintf 73-87 ns (\~4.4-8x), std::to_string 76-90 ns (\~4.5-8.4x) and std::stringstream 34-55 ns (\~2.75-3.8x). Own from_chars (checked) takes 9-19 ns, against atoi/strtol 14-28 ns (\~1.5x) and std::stoi 16-29 ns (\~1.5-1.8x). The unchecked variant takes 4-10 ns (\~2.8-3.5x faster than atoi/strtol). |
| **Workload** | Converting base-10 32/64-bit signed/unsigned integers to and from strings across 1-9 digit lengths, measured in nanoseconds per call via Google Benchmark, against sprintf, std::to_string, std::stringstream, atoi, strtol, and std::stoi. |
| **Metric** | latency |
| **Hardware** | Intel Xeon E5-2620 v4 @ 2.10GHz, 32 cores, L1 32K/L2 256K/L3 20480K caches |
| **Compiler and flags** | Not stated (Google Benchmark output shown; compiler/optimization flags absent from README) |
| **Adoption** | 25 stars |
| **Last commit** | 2023-09-25 |
| **Links** | [repository](https://github.com/rigtorp/CharConv) · [benchmark](https://github.com/rigtorp/CharConv/blob/master/README.md) |

## Verdict

In-repo Google Benchmark dated 2017-12-26 on a Xeon E5-2620 v4 (compiler/flags not disclosed): to_chars ran 9-20ns vs sprintf 73-87ns, std::to_string 76-90ns, and std::stringstream 34-55ns; checked from_chars ran 9-19ns vs atoi/strtol 14-28ns and std::stoi 16-29ns; from_chars_unchecked ran 4-10ns. No std::to_chars/std::from_chars comparison exists in the repo.

## Use it when

- Hot loops converting many 1-9 digit signed/unsigned 32/64-bit integers to base-10 text (log lines, CSV/JSON emitters, wire protocols).
- Parsing base-10 integers with overflow detection but without exceptions or locale overhead (from_chars).
- Trusted, pre-validated input where the unchecked from_chars_unchecked path's extra speed is worth skipping validation.
- You already have a fixed buffer/pointer and want to skip std::to_string's allocation or stringstream's formatting machinery.
- GCC/Clang-only target where vendoring one \~200-line, zero-dependency header is acceptable.

## Skip it when

- Need floating-point to_chars/from_chars — not implemented at all here.
- Need MSVC support — code depends on GCC/Clang builtins (__builtin_clz, __builtin_clzll, __builtin_mul_overflow, __builtin_add_overflow) with no MSVC equivalents provided.
- Need real interchangeability with std::to_chars/std::from_chars (exact result types, base 2-36, std::chars_format) — this API is similar but distinct, not a swap-in.
- Want the fastest available integer formatter — sibling libraries (jeaiii/itoa, c4core) use digit-pair lookup tables and report larger margins; this repo never benchmarks against them or against actual std::to_chars.
- Expect upstream maintenance — no commits, issues, or PRs since the 2023-09-25 push; algorithm and code are unchanged since the 2018 copyright.

## How it is fast

to_chars precomputes the exact digit count with a clz-based bit-length-to-decimal-digits formula (__builtin_clz/__builtin_clzll against a static power-of-10 table) so it writes straight into a correctly sized span instead of a scratch buffer plus reversal or a strlen pass, then emits digits back-to-front via repeated /10, %10. from_chars accumulates digits with __builtin_mul_overflow/__builtin_add_overflow so overflow detection adds no separate check pass; a from_chars_unchecked variant skips overflow checks for a further speedup. Everything is noexcept, constexpr, and hinted with __builtin_expect.

## Compared with alternatives

Pick this over Boost.Charconv or c4core when you want a zero-dependency, \~200-line header covering only base-10 32/64-bit integers and don't need float support; pick Boost.Charconv or c4core instead when you need floats or an actual std::to_chars/from_chars head-to-head, since this repo never benchmarks against std at all.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none for consumers (vendors Google Benchmark and Catch2 only for the repo's own benchmark/test binaries) |
| **Minimum toolchain** | C++17 (if constexpr); relies on GCC/Clang builtins, exact minimum GCC/Clang version not documented |
| **Platforms** | any GCC/Clang target (x86-64, aarch64, etc.); MSVC not supported, no intrinsic fallback provided |
| **Thread safety** | not documented; code has no shared mutable state (only const power-of-10 tables), so functions appear reentrant |
| **Drop-in for the baseline** | partial — same ptr/ec result shape as std::to_chars/from_chars per README but with distinct result struct types, and a buffer-based, non-allocating signature that doesn't match stringstream/to_string/atoi/strtol/stoi at all |

## Gotchas

- from_chars_unchecked skips overflow validation entirely — only safe on pre-validated input.
- to_chars_result/from_chars_result are rigtorp's own types, not std::to_chars_result/std::from_chars_result — don't assume interchangeability.
- Caller must size the output buffer itself (worst case 11 bytes for int32/uint32 with sign, 20 for int64/uint64); no allocating convenience wrapper is provided.
- Compiler-builtin dependent (__builtin_clz/__builtin_mul_overflow/etc.) — porting off GCC/Clang requires substituting equivalents.

## Caveats and trade-offs

Benchmark is dated 2017-12-26 (pre-dates widely-available std::to_chars/from_chars implementations), and compiler/optimization flags are not disclosed, only hardware — so despite having a real, reproducible in-repo benchmark, it is capped below Tier A. No direct std::to_chars/std::from_chars comparison was found in this repo; baseline recorded reflects what was actually benchmarked (stringstream/to_string/atoi/strtol/stoi).

Only base-10 32/64-bit signed/unsigned integers, no floating point; its own to_chars/from_chars functions have an API 'similar, but not identical' to std::to_chars/std::from_chars — this repo does not itself call or benchmark the actual std::to_chars/std::from_chars functions, only stringstream/to_string/atoi/strtol/stoi.

## Maintenance

Stale since the last push on 2023-09-25 (0 open issues/PRs, no recent activity) but MIT-licensed, header-only, and small enough to vendor as-is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** Benchmark code exists in the repo (src/CharConvBenchmark.cpp, Google Benchmark) and the README shows its output with the hardware (Xeon E5-2620 v4). The compiler and optimization flags are not stated, and CMakeLists.txt sets no build type. So it is not A. It is not B because there is no paper or independent third-party suite. That leaves C.
- **Verifier notes:** The README numbers match the record. The speedup ratios were slightly rounded up and have been corrected. The prior tier B was invalid because B requires peer-reviewed or independent evidence, so the tier is now C. There is no std::to_chars/from_chars comparison, and the benchmark is from 2017.
- **Fields the verifier corrected:** `claimed_speedup`
- **Pages the verifier opened:**
  - <https://github.com/rigtorp/CharConv>
  - <https://github.com/rigtorp/CharConv/blob/master/README.md>
  - <https://github.com/rigtorp/CharConv/tree/master/src>
  - <https://github.com/rigtorp/CharConv/blob/master/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/rigtorp/CharConv>
  - <https://github.com/rigtorp/CharConv/blob/master/README.md>
  - <https://github.com/rigtorp/CharConv/tree/master>
  - <https://github.com/rigtorp/CharConv/blob/master/CMakeLists.txt>
  - <https://github.com/rigtorp/CharConv/blob/master/LICENSE>
  - <https://github.com/rigtorp/CharConv/blob/master/include/rigtorp/CharConv.h>
  - <https://github.com/rigtorp/CharConv/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/rigtorp/charconv`) · [data/wave1/enrich/raw/github_com_rigtorp_charconv.json](../../../data/wave1/enrich/raw/github_com_rigtorp_charconv.json) (enrichment confidence 0.8)

</details>
