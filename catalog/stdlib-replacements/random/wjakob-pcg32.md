# wjakob/pcg32

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Random numbers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `Apache-2.0` · 🔴 abandoned

> Tiny two-header PCG32 RNG beating std::mt19937 on speed, with an optional AVX2 8-wide variant.

| | |
|---|---|
| **Beats** | std::mt19937 |
| **Claimed result** | pcg32: 940.39M gen/s vs std::mt19937: 270.65M gen/s (\~3.47x, derived from page data); pcg32_8 (8-wide header): 944.20M gen/s (\~3.49x, derived from page data) |
| **Workload** | Raw 32-bit integer generation (scalar pcg32, and an 8-wide vectorized pcg32_8 variant), mean time per generation over 100 repetitions. |
| **Metric** | throughput |
| **Hardware** | Intel Core i5-3570 @ 3.40GHz |
| **Compiler and flags** | clang, -O3 -DNDEBUG, no architecture-specific optimization flags |
| **Adoption** | 88 stars |
| **Last commit** | 2016-06-07 |
| **Links** | [repository](https://github.com/wjakob/pcg32) · [benchmark](https://github.com/zeFresk/cpp-random-benchmarks) |

## Verdict

In the zeFresk/cpp-random-benchmarks shootout (clang, -O3 -DNDEBUG, no -march flag, Intel i5-3570 @ 3.40GHz, 100 repetitions), pcg32::nextUInt averaged 940.39M gen/s vs std::mt19937's 270.65M gen/s (\~3.47x). pcg32_8 measured 944.20M gen/s, but since this CPU has no AVX2, that number reflects the header's scalar 8-instance fallback path rather than the intended vectorized path.

## Use it when

- Bulk generation of 32-bit random values for non-cryptographic use (simulations, games, sampling)
- Need jump-ahead/jump-back (advance()) or stream-distance queries that std::mt19937 doesn't offer
- Want to vendor a tiny, dependency-free source drop (two headers) instead of linking a library
- Target CPU has AVX2 and the workload can batch draws 8 at a time (pcg32_8)
- MT19937-class statistical quality is sufficient; cryptographic security is not required

## Skip it when

- Cryptographic or adversarial contexts — neither PCG32 nor MT19937 is designed for that
- Need a native 64-bit output engine — this repo only has 32-bit pcg32 (use imneme/pcg-cpp for pcg64 variants)
- Code needs to satisfy std::uniform_random_bit_generator (e.g. pass the engine to std::uniform_int_distribution or std::shuffle) — pcg32 has no operator() or static min()/max()
- Building for a CPU without AVX2 while expecting the pcg32_8 speedup — it silently compiles to the scalar 8-instance fallback with no warning
- Need active upstream maintenance — no commits since June 2016 and an open 'Missing LICENSE' issue since 2021

## How it is fast

Implements the PCG technique: a 64-bit linear congruential state advanced each step, with an XSH-RR permutation (xorshift on the high bits, then a data-dependent rotate) producing the 32-bit output. The 16-byte state and few-instruction step are cheaper than MT19937's 624-word state and tempering. pcg32_8 vectorizes eight independent PCG32 streams with AVX2 (32-bit lane multiplies via partial products, permutevar8x32 lane shuffles, variable-shift rotate) to emit 8 outputs per step on capable hardware.

## Compared with alternatives

Pick this over pcg-cpp (imneme/pcg-cpp) when you want the smallest possible PCG32-only source drop (two headers, no build system) rather than the full PCG engine family. On the same benchmark, pcg-cpp's pcg32_fast is about 14% faster (1071.97M vs 940.39M gen/s) and adds 64-bit engines, so prefer pcg-cpp when raw throughput or 64-bit output matters more than minimalism.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none beyond the STL (pcg32.h: &lt;inttypes.h&gt;, &lt;cmath&gt;, &lt;cassert&gt;, &lt;algorithm&gt;; pcg32_8.h additionally: &lt;immintrin.h&gt;, &lt;utility&gt;, and includes pcg32.h) |
| **Minimum toolchain** | not documented — no CMakeLists or pinned language standard; code uses only C++11-era features |
| **Platforms** | pcg32.h: any platform with a C++ compiler; pcg32_8.h: x86-64 with AVX2 (guarded by #if defined(__AVX2__)), else compiles a portable scalar fallback |
| **Thread safety** | not documented; each pcg32/pcg32_8 instance owns its own state with no internal locking, so per-thread instances are safe by construction but this isn't stated in the source |
| **Drop-in for the baseline** | partial — explain: nextUInt()/nextFloat()/nextDouble() mirror engine-style usage, but pcg32 lacks operator() and static min()/max(), so it does not satisfy std::uniform_random_bit_generator and can't be passed directly to std::uniform_int_distribution or std::shuffle |

## Gotchas

- pcg32_8's AVX2 path is selected purely by the __AVX2__ macro at compile time; forgetting -mavx2 (or /arch:AVX2) silently yields the scalar fallback with no warning or error
- No operator()/min()/max(), so it can't be used as a standard UniformRandomBitGenerator with &lt;random&gt; distributions — use its own nextUInt(bound) or shuffle() instead
- Apache-2.0 is only stated in file header comments; there is no root LICENSE file, so GitHub reports 'no license' and an open issue (#2, 'Missing LICENSE', filed 2021) is still unresolved
- advance() and operator- assume both generators share the same inc (stream) value; this is only checked via assert(), which is compiled out in NDEBUG/release builds

## Caveats and trade-offs

Same third-party shootout as the pcg-cpp entry, run on the same 2012-era CPU. The build used no -march flag and the i5-3570 (Ivy Bridge) has no AVX2, so __AVX2__ was undefined. The pcg32_8 row therefore measured the header's scalar fallback path, not the AVX2 path; the table's own remark notes the vectorized version should be faster on capable CPUs. The repo has had no commits since 2016. The license (Apache-2.0) is declared in the source headers, but there is no root LICENSE file, so GitHub's license detector reports none.

Minimal, single-purpose reimplementation of PCG32 (not the full pcg-cpp family: no 64-bit output engine, no stream/rewind variants beyond what's included); pcg32_8 requires AVX for its intended speedup path; smaller state/period guarantees than MT19937.

## Maintenance

Abandoned since June 2016 (no further commits; an open 'Missing LICENSE' issue since 2021) but Apache-2.0-licensed (declared in file headers only) and small enough — two headers — to vendor as-is.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** The shootout's README table has the wjakob pcg32 row at 940.393M/s and pcg32_8 at 944.200M/s, against std::mt19937 at 270.652M/s. The benchmark code is public: zeFresk/cpp-random-benchmarks src/pcg32.cpp and src/std.cpp, with wjakob/pcg32 pinned at 70099ea. The README states clang with -O3 -DNDEBUG and an Intel i5-3570.
- **Verifier notes:** The pcg32 ratio 940.393/270.652 is 3.4745, so I corrected \~3.48x to \~3.47x. I also clarified the AVX caveat by checking pcg32_8.h (#if defined(__AVX2__)). The metadata checked out: 88 stars, last commit 2016-06-07, abandoned, Apache-2.0 in headers.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/zeFresk/cpp-random-benchmarks>
  - <https://github.com/zeFresk/cpp-random-benchmarks/blob/main/src/pcg32.cpp>
  - <https://github.com/zeFresk/cpp-random-benchmarks/blob/main/src/std.cpp>
  - <https://github.com/wjakob/pcg32>
  - <https://github.com/wjakob/pcg32/blob/master/pcg32.h>
  - <https://github.com/wjakob/pcg32/blob/master/pcg32_8.h>
- **Sources the enricher read:**
  - <https://github.com/wjakob/pcg32>
  - <https://github.com/wjakob/pcg32/blob/master/pcg32.h>
  - <https://github.com/wjakob/pcg32/blob/master/pcg32_8.h>
  - <https://github.com/wjakob/pcg32/issues>
  - <https://github.com/zeFresk/cpp-random-benchmarks>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/wjakob/pcg32`) · [data/wave1/enrich/raw/github_com_wjakob_pcg32.json](../../../data/wave1/enrich/raw/github_com_wjakob_pcg32.json) (enrichment confidence 0.83)

</details>
