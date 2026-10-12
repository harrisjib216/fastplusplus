# EVE (Expressive Vector Engine)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSL-1.0` · 🟢 active

> C++20 SIMD wrapper (eve::wide) with a large vectorised math library and SIMD STL-style algorithms; successor of Boost.SIMD, no published speedups.

| | |
|---|---|
| **Beats** | scalar C++ / compiler auto-vectorization (no baseline stated; successor of Boost.SIMD) |
| **Claimed result** | No numbers: README says the goal is 'an efficient, low-level, high-abstraction library suited for high performance' and cites three papers (PACT 2012, HPCS 2018, a 2014-era Scalable Computing article) without summarizing results. |
| **Workload** | C++20 SIMD wrapper with a math function library for SSE2 to AVX-512, NEON/ASIMD and fixed-size SVE; the repo has a benchmarks/module harness (nanobench) but no published results. |
| **Metric** | throughput |
| **Adoption** | 1.4k stars, 77 forks |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/jfalcou/eve) · [benchmark](https://github.com/jfalcou/eve) |

## Verdict

Nothing measured: the README states a goal ('efficient, low-level, high-abstraction') and cites PACT 2012, HPCS 2018 and an older Scalable Computing paper without results, and the benchmarks/ nanobench harness (std:: scalar function versus eve scalar and eve::wide of 64 bytes, 92 KiB arrays, warmup 1500) has no committed output. The 2023 LMU bachelor thesis that compared six C++ SIMD libraries against intrinsics was unreachable, so whether EVE was among them is still unknown.

## Use it when

- Portable C++20 code that must vectorise the same source for x86 (SSE2 to AVX-512) and ARM (NEON A32/A64, ASIMD, SVE at fixed 128/256/512 bits)
- Bulk float/double transcendental work (sin/cos/exp/log/pow and the d/pi variants) where you can state the input range and use the reduced-range decorators
- Byte and integer scans or filters (find, mismatch, copy_if, keep_if, set_intersection) over contiguous ranges that you want written once instead of per-ISA intrinsics
- Projects already on GCC 13+, Clang 16+ or MSVC 19.44+ that can ship one binary per ISA or compile with -march for a known fleet

## Skip it when

- You need evidence before adopting: the repo publishes no benchmark results and no comparison against Highway, xsimd, std::simd or vector libm; measure your kernel yourself
- Pre-C++20 toolchains, or codebases that need a stable API: the README calls EVE a research project whose API and minimum compiler may change before a 0.1 release, and the last tag is v2023.02.15 while main has moved on
- Scalable (length-agnostic) SVE, RISC-V V or GPUs: SVE is fixed-size only, PowerPC VMX/VSX is partial, GPGPU is out of scope
- Single-binary runtime dispatch across ISAs without dlopen: EVE has no built-in function multiversioning, only the per-variant shared-library pattern
- Debug (-O0) builds on hot paths: issue #1740 reports eve::algo::copy about 40x slower than std::ranges::copy at -O0, and the maintainers advise memcpy/memmove for plain byte copies

## How it is fast

Explicit SIMD: each function is implemented per instruction-set family with intrinsics behind tag dispatch, so the code you write once compiles to the widest registers the target flags allow instead of relying on auto-vectorisation. Math functions are vectorised polynomial approximations whose range reduction can be narrowed with decorators (cos[quarter_circle], cos[half_circle], cos[medium], cos[big], exp[raw], [fast]) so callers who know their input range skip the expensive reduction. The algorithm layer handles alignment, tails and unrolling through traits (no_aligning, expensive-kernel and fused-operation traits added in 2023.02.15).

## Compared with alternatives

Pick EVE over Vector Class Library (also numberless in this catalogue) when you need ARM NEON or fixed-size SVE builds or STL-style SIMD algorithms on top of the wrapper; pick math_intrinsics or SIMD-math-prims when you only need a few approximate float functions in plain C with published libm comparisons. vstat, a catalogued sibling, is built on EVE and is the closest thing to third-party performance evidence for it.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none external; kumi, raberu and spy are vendored under include/eve/deps |
| **Minimum toolchain** | C++20; g++ 13+, clang++ 16+, MSVC 19.44+ (recommended g++ 14+, clang++ 19+) |
| **Platforms** | x86 SSE2 to AVX2/FMA3 and AVX-512 (Skylake-AVX512 subset), ARM NEON A32/A64, ASIMD, SVE fixed 128/256/512; PowerPC VMX/VSX partial; no dynamic-length SVE |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- Build with -DNDEBUG: without it asserts stay in the generated code; open issue #2085 (Ryzen 9 7940HS, g++ 14.2.1 and clang++ 19.1.7) measured a 4-lane float gather at 0.198 ns with -O3 and 1.01 ns with -O3 -mavx2, about 5x slower, still unresolved; EVE_USE_BMI_ON_AVX2 is documented as 'beneficial on Intel, disastrous on AMD'.
- Harness flaw in the repo's own benchmarks (no published numbers depend on it): 24 math 'regular' benchmarks (sin, cos, tan, sincos, sec, csc, cot, their d/pi variants, atan2, atan2d, atan2pi) draw inputs with std::uniform_real_distribution&lt;double&gt;(valmin, valmax); for double this violates the b - a &lt;= max precondition and libstdc++ returns +inf for every element (reproduced locally with g++: 11,776 of 11,776 inputs were inf), so the std::cos versus eve::cos double rows time only the inf-to-NaN path; the float rows are valid but every input has |x| &gt;= 1e30, so they time only huge-argument reduction.
- Other benchmark build defects: the MSVC bench flags read /0x (zero) instead of /Ox, and the GCC/Clang bench flags are -O3 without -march, so a default configure benchmarks SSE2 unless you add CMAKE_CXX_FLAGS; benchmarks are OFF by default (EVE_BUILD_BENCHMARKS) and compare only against scalar std:: functions.
- README's licence block prints MIT text under a 'Boost Software License' heading; LICENSE.md is BSL-1.0, which the project adopted in 2022.09.0 when it moved from MIT.

## Known shortcomings

- No numbers anywhere; benchmarks/ is a harness only. Notable (1.4k stars, BSL-1.0). Retier lead: the 2023 LMU thesis rock23.pdf comparing six SIMD libraries (blocked, EVE not confirmed among them).
- Still no published numbers (LMU thesis rock23.pdf blocked). Harness flaw in the repo's own math benches: 24 'regular' benches (sin/cos/tan/sec/csc/cot and d/pi variants, sincos family, atan2) draw inputs with uniform_real_distribution&lt;double&gt;(valmin, valmax), which breaks the b-a &lt;= max precondition for double; libstdc++ returned +inf for 11,776 of 11,776 inputs (checked locally with g++), so the std::cos vs eve::cos double rows time only the inf-to-NaN path, and every float input has |x| &gt;= 1e30. MSVC bench flag is '/0x' (zero) instead of /Ox; bench flags have no -march; open issue #2085 (AVX2 gather 5x slower); no tag since v2023.02.15; README licence block shows MIT text under a Boost heading.

## Caveats and trade-offs

No benchmark numbers in the README or repo; benchmarks/ has only the nanobench harness (CMakeLists.txt, experiment.hpp, generators.hpp, nanobench.h, module/ with algorithm, combinatorial, core, math and special subdirectories) and no result tables. The README calls EVE a research project first, with API and minimum compiler subject to change before a 0.1 release, and says some performance issues may remain. Documentation and the cited papers (PACT 2012 Boost.SIMD, HPCS 2018 small matrix-vector, Scalable Computing EVE article) live on github.io, ACM and HAL pages that were blocked here. Lead for a retier: Felix Rocke's April 2023 LMU bachelor thesis 'Evaluation of C++ SIMD Libraries' benchmarks six SIMD libraries against intrinsics on AVX2, AVX-512, SVE and NEON (abstract, snippet only: several libraries matched intrinsics, Highway strongest on the integer case study); whether EVE is among the six was not confirmed (nm.ifi.lmu.de blocked). Requires C++20 (g++ 13+, clang++ 16+, MSVC 19.44+); no dynamic-size SVE.

Requires C++20; fixed-size SVE only; marked 'operational' with possible performance issues remaining.

## Maintenance

Actively developed (2,059 commits, latest 2026-10-11, 1.4k stars) and BSL-1.0, header-only and copyable, but still a self-described research project with no tagged release since v2023.02.15 and 102 open issues.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** No numbers anywhere reachable: the README only says the library aims to be 'efficient' and cites three papers without results, and benchmarks/ holds only a nanobench harness (experiment.hpp, generators.hpp, module/{algorithm,combinatorial,core,math,special}) with no committed result tables. The cited papers (PACT 2012, HPCS 2018) and the github.io docs are unreachable here, so D stands.
- **Verifier notes:** Repo checked on github.com: BSL-1.0, 1.4k stars, not archived or a fork, last commits 2026-10-11, so metadata holds. Kept at D as a notable (1.4k stars) successor of Boost.SIMD with no published numbers; shortcoming: no benchmark results and no comparison against scalar code, Highway, xsimd or std::simd anywhere reachable. Retier lead: the 2023 LMU thesis (rock23.pdf) and the CppCon 2021 talk.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-13 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/jfalcou/eve>
  - <https://github.com/jfalcou/eve/commits>
  - <https://github.com/jfalcou/eve/tree/main/benchmarks>
  - <https://github.com/jfalcou/eve/tree/main/benchmarks/module>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/README.md>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/benchmarks/experiment.hpp>
- **Sources the enricher read:**
  - <https://github.com/jfalcou/eve>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/README.md>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/LICENSE.md>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/benchmarks/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/benchmarks/experiment.hpp>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/benchmarks/generators.hpp>
  - <https://github.com/jfalcou/eve/tree/main/benchmarks/module/math>
  - <https://github.com/jfalcou/eve/tree/main/benchmarks/module/math/cos>
  - <https://github.com/jfalcou/eve/tree/main/benchmarks/module/math/cos/regular>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/benchmarks/module/math/cos/regular/cos.hpp>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/benchmarks/module/math/cos/big/cos.hpp>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/benchmarks/module/math/cos/quarter_circle/cos.hpp>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/benchmarks/module/math/CMakeLists.txt>
  - https://raw.githubusercontent.com/jfalcou/eve/HEAD/benchmarks/module/math/&lt;fn&gt;/regular/&lt;fn&gt;.hpp (65 files, acos through tanpi)
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/cmake/benchmark.cmake>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/cmake/bench.cpp.in>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/cmake/config/types.cmake>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/cmake/config/options.cmake>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/cmake/config/compiler.cmake>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/cmake/target/generate_benchmark.cmake>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/doc/setup.md>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/doc/changelog.md>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/doc/index.md>
  - <https://github.com/jfalcou/eve/tags>
  - <https://github.com/jfalcou/eve/commits/main>
  - <https://github.com/jfalcou/eve/issues?q=is%3Aissue+performance>
  - <https://github.com/jfalcou/eve/issues/2085>
  - <https://github.com/jfalcou/eve/issues/1740>
  - <https://github.com/jfalcou/eve/tree/main/include/eve>
  - <https://github.com/jfalcou/eve/tree/main/include/eve/deps>
  - <https://github.com/jfalcou/eve/tree/main/include/eve/module>
  - <https://github.com/jfalcou/eve/tree/main/include/eve/module/algo/algo>
  - <https://github.com/jfalcou/eve/tree/main/doc>
  - <https://github.com/jfalcou/eve/tree/main/examples>
  - <https://github.com/jfalcou/eve/tree/main/examples/multi-arch>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/examples/multi-arch/main.cpp>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/examples/multi-arch/CMakeLists.txt>
  - <https://raw.githubusercontent.com/jfalcou/eve/HEAD/examples/multi-arch/compute.cpp>
  - https://www.nm.ifi.lmu.de/pub/Fopras/rock23/PDF-Version/rock23.pdf (blocked: CONNECT 403; abstract known from WebSearch snippet only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/jfalcou/eve`) · [data/wave13/enrich/raw/github_com_jfalcou_eve.json](../../../data/wave13/enrich/raw/github_com_jfalcou_eve.json) (enrichment confidence 0.7)

</details>
