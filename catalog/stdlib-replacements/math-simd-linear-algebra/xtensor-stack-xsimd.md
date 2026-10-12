# xsimd

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> Header-only C++ SIMD abstraction: portable batch&lt;T,Arch&gt; type replaces scalar loops across x86/ARM/RISC-V/WASM.

| | |
|---|---|
| **Beats** | std::transform / scalar loops |
| **Claimed result** | No numeric claim found; only qualitative statements such as SIMD instructions "significantly accelerate code execution" and xsimd provides "accelerated implementation of common mathematical functions" |
| **Workload** | None found -- checked README.md, docs/source/\*.rst (including vectorized_code.rst), the benchmark/ directory, and the original author's pre-xsimd blog series |
| **Metric** | other |
| **Adoption** | 2.8k stars; adopted by Mozilla Firefox, Apache Arrow, Pandas, KDE Krita, Meta Velox, Milvus, Pythran |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/xtensor-stack/xsimd) |

## Verdict

No numeric benchmark is published anywhere in the repo, docs, or README. The repo's benchmark/ directory (main.cpp, xsimd_benchmark.hpp) is a Google-Benchmark-style harness that times scalar loops against xsimd batches, but no results are committed or published, so 'faster than scalar/std::transform' is an unverified qualitative claim, not a measured number against any specific compiler, flag set, or hardware.

## Use it when

- Tight numeric kernels applying the same arithmetic/math op over large arrays of floats/doubles/ints
- Need one portable source across x86-64, ARM (NEON/SVE), RISC-V (RVV), WASM, PowerPC (VSX), LoongArch, or IBM z, without hand-written per-ISA intrinsics
- Want vectorized exp/log/trig/pow without trusting the compiler's autovectorizer
- Header-only vendoring is acceptable (no separate build/link step)
- Need runtime dispatch across multiple ISAs from a single binary via xsimd::dispatch()

## Skip it when

- Workload sizes rarely align to the SIMD width and remainder-loop bookkeeping is unwanted overhead
- Using -ffast-math with log() on AVX2 pre-fix builds: issue #1264 showed materially wrong results (now closed/fixed, but confirm the fix is in your pinned version)
- Chained math-function expressions (e.g. sqrt((cos+sin)/2) over 1e8 elements): issue #880 is an open, unresolved report of xsimd being \~3x slower than the scalar std:: equivalent on AVX2 for that pattern
- You need a published, reproducible benchmark before committing — none exists in this repo (evidence tier D, no numbers in README/docs/benchmark/)
- Toolchain is older than GCC 10 / Clang 16 / MSVC 2022, or pre-C++17

## How it is fast

It compiles operators and math functions directly to the target ISA's real SIMD instructions instead of relying on the autovectorizer or scalar code, via either an explicit Arch template parameter or auto-selection based on compiler flags (e.g. -mavx2). The vectorized math functions (exp/log/trig/pow) are lightweight polynomial-approximation implementations inherited from the now-deprecated boost.SIMD project. xsimd::dispatch() adds runtime ISA dispatch so one binary can pick the best available instruction set at startup.

## Compared with alternatives

no siblings catalogued yet

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (optional: xtl, only if you enable XSIMD_ENABLE_XTL_COMPLEX for xtl::xcomplex constructors) |
| **Minimum toolchain** | C++17; GCC 10+, Clang 16+, MSVC 2022+ |
| **Platforms** | x86-64 (SSE2..AVX512, FMA3/FMA4), ARM (NEON, NEON64, SVE), WebAssembly (WASM), PowerPC64 (VSX), RISC-V (RVV), LoongArch64 (LSX/LASX), IBM z/Architecture (VXE) |
| **Thread safety** | not documented; batch&lt;T,Arch&gt; is a stateless value type with no shared mutable state, so read-only concurrent use appears safe by construction, but the project makes no explicit guarantee |
| **Drop-in for the baseline** | partial — explain: replaces the operator/math-function bodies of a scalar loop, but the caller must restructure the loop into batch-width chunks and write the tail/remainder loop by hand; it is not a transparent std::transform substitute |

## Gotchas

- log() on AVX2 compiled with -ffast-math produced wrong results (issue #1264); reported closed/fixed but verify against your pinned xsimd version
- Compound math expressions (cos/sin/sqrt combined) were reported \~3x slower than the equivalent scalar std:: code on AVX2 over 1e8 elements (issue #880, open, unconfirmed by maintainers) — benchmark your actual expression before assuming a win
- Pinning an explicit Arch template parameter (e.g. batch&lt;double, xsimd::avx2&gt;) fails to compile on hardware lacking that ISA; leave Arch unset to auto-select based on compiler flags for portability
- Caller owns tail-loop correctness: batch operations only cover size - (size % simd_size) elements

## Caveats and trade-offs

The repo ships a benchmark/ directory (main.cpp, xsimd_benchmark.hpp) but it contains only Google-Benchmark-style harness code with no published results committed to the repo or docs. The project's documentation (readthedocs) and README are purely API/usage-focused with no performance section. The original author's 2014 blog post 'Performance Considerations About SIMD Wrappers' (predecessor project to xsimd) was checked directly and contains only assembly-level qualitative discussion, no timing numbers. Recorded at tier D per the rule for notable projects with no located numeric comparison.

Requires explicit handling of the tail/remainder loop for sizes not divisible by the SIMD width; the portable API spans many ISAs (SSE/AVX/AVX512/NEON/SVE/RVV/WASM/VSX) which trades some architecture-specific peak performance for a single uniform interface.

## Maintenance

Actively maintained (last commit 2026-09-22; 2.8k stars; used by Firefox, Apache Arrow, Pandas, KDE Krita, Meta Velox, Milvus, and Pythran); BSD-3-Clause and header-only, so it is trivial and low-risk to vendor even without ongoing upstream engagement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-24): confirm; tier before verification D, tier now D.
- **Tier reason:** There is no benchmark_url, and none of README.md, docs/source/\*.rst or Changelog.rst has a performance number. benchmark/xsimd_benchmark.hpp times scalar loops against xsimd batches but publishes no results, so the tier stays D.
- **Verifier notes:** This is a notable project (2,758 stars; the README names Firefox, Arrow, Pandas, Krita, Velox, Milvus and Pythran as users), so it stays at tier D rather than being rejected. The in-repo benchmark does compare scalar against SIMD code, so a baseline comparison exists without published numbers. I did not re-check the 2014 blog post named in the caveats. Metadata checks out: BSD-3-Clause, last commit 2026-09-22.
- **Shortcomings recorded by:** A fused sum+min+max over 8.4M floats ran at 0.18 ns/element with xsimd vs 1.277 ns for the scalar loop (7.08x), because gcc emits zero vector instructions for that float reduction at -O3 -march=native without -ffast-math. The xsimd result was also 158x more accurate against a double-precision reference. (developer source, private repo; gcc 13.3.0 -O3 -march=native (benchmarks forced to -O3 per the row's re-measurement note), Intel Xeon @ 2.10GHz, run 2026-09-03-third-party); Where gcc can vectorise, the margin shrank: dot product over 8.4M floats 0.317 vs 0.717 ns/element (2.26x, memory-bound) and an integer filter/count 0.164 vs 0.249 ns (1.51x, kept as the negative control). The filter/count result was 1.82x before the scalar baseline was corrected from -O2 to -O3. (developer source, private repo; gcc 13.3.0 -O3 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-03-third-party); On a 128x128 float32 matmul an explicit xsimd ikj kernel (162,632 ns) lost to the plain ikj loop with __restrict on the parameters (122,170 ns; 1.33x, derived). Hand-written xsimd did win fixed 4x4 multiplies against a naive triple loop (3.091 vs 6.247 ns, 2.02x) and was the fastest complex multiply-add variant measured (0.147 ns/element SoA vs 0.966 for AoS std::complex&lt;float&gt;). (developer source, private repo; gcc 13.3.0 -O3 -march=native, Intel Xeon @ 2.10GHz, run 2026-09-03-third-party)
- **Pages the verifier opened:**
  - <https://github.com/xtensor-stack/xsimd>
  - <https://github.com/xtensor-stack/xsimd/tree/master/benchmark>
  - <https://github.com/xtensor-stack/xsimd/blob/master/benchmark/xsimd_benchmark.hpp>
  - <https://github.com/xtensor-stack/xsimd/tree/master/docs/source>
- **Sources the enricher read:**
  - <https://github.com/xtensor-stack/xsimd>
  - <https://github.com/xtensor-stack/xsimd/blob/master/docs/source/build_options.rst>
  - <https://github.com/xtensor-stack/xsimd/blob/master/docs/source/vectorized_code.rst>
  - <https://github.com/xtensor-stack/xsimd/issues/625>
  - <https://github.com/xtensor-stack/xsimd/issues/1009>
  - <https://github.com/xtensor-stack/xsimd/issues/1264>
  - <https://github.com/xtensor-stack/xsimd/issues/880>
- **Raw records:** [data/wave0-seed/verified.json](../../../data/wave0-seed/verified.json) (id `https://github.com/xtensor-stack/xsimd`) · [data/wave0-seed/enrich/raw/github_com_xtensor_stack_xsimd.json](../../../data/wave0-seed/enrich/raw/github_com_xtensor_stack_xsimd.json) (enrichment confidence 0.72)

</details>
