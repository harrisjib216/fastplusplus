# FastMath C++ Library (fast_math_cpp)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only float math library beating glibc's &lt;cmath&gt; on composed functions (sinh, tanh, atan2, integer pow), not raw trig or exp/log.

| | |
|---|---|
| **Beats** | &lt;cmath&gt; single-precision (float) overloads (std::sinh, std::tanh, std::atanh, std::atan2, std::pow, std::acos, std::log10, std::tan, std::exp, std::log, etc.), backed by glibc libm (sinhf, tanhf, ...) |
| **Claimed result** | Scalar float calls vs std:: (glibc) at identical flags, x86_64 / Raspberry Pi 4. sinh 2.96x/3.94x, tanh 2.94x/3.91x, atanh 2.42x/2.49x, atan2 2.18x/1.63x, integer pow base^2 2.02x/4.54x, acos 1.76x/1.57x, log10 1.45x/2.20x, tan 1.44x/1.40x. 21 of 28 scalar measurements match or beat std on each platform. Slower cases: sincos [-2pi,2pi] 0.88x/0.63x, sin [-2pi,2pi] 1.03x/0.73x, cos [-2pi,2pi] 1.04x/0.82x, sincos [-pi,pi] 0.71x on the Pi, fractional pow 0.84x/0.90x. exp/log/log2/sqrt are 0.94x-1.01x because they forward to std. Batch API vs std loops: atan2 6.16x/3.48x, sincos vs std::sin+std::cos 3.84x/1.97x, sin 2.15-2.28x on x86 but only 0.98-1.06x (parity) on the Pi. |
| **Workload** | 1,000,000 scalar single-precision (float) calls per function across 28 function/domain combinations (trig, hyperbolic, exp/log family, pow, rounding). Each result is the best of 25 runs with the two implementations interleaved run by run. Benchmarked on x86_64 (GCC 11.4, WSL2) and Raspberry Pi 4 (GCC 12.2); the Pi column takes the minimum over two recorded runs. A batch/array API (1M elements per call) for sin/cos/sincos/atan2 is measured separately. |
| **Metric** | throughput |
| **Hardware** | x86_64: WSL2 (Linux 6.6.87.2-microsoft-standard-WSL2), GCC 11.4, CPU model not stated. Raspberry Pi 4 (Cortex-A72): Linux 6.12 aarch64, GCC 12.2. |
| **Compiler and flags** | Both library and baseline built with identical flags via the fast_math_bench target: -O3 -march=native -funroll-loops |
| **Adoption** | 2 stars |
| **Last commit** | 2026-07-28 |
| **Links** | [repository](https://github.com/hijimasa/fast_math_cpp) · [benchmark](https://github.com/hijimasa/fast_math_cpp/blob/main/README.md) |

## Verdict

Scalar float calls, both sides built with identical flags (-O3 -march=native -funroll-loops), best of 25 interleaved runs of 1,000,000 calls, on WSL2 x86_64 GCC 11.4 (no CPU model stated) and Raspberry Pi 4 GCC 12.2 against glibc's float &lt;cmath&gt;: composed functions like sinh (2.96x/3.94x), tanh (2.94x/3.91x) and integer pow (2.02x/4.54x) win; exp/log/log2/sqrt sit at parity (0.94x-1.01x) because they forward to std::; scalar sin/cos/sincos on wide angle ranges lose on ARM (0.63x-0.82x). A separate batch/array API for sin/cos/sincos/atan2 reached up to 6.16x (atan2) over a std:: loop on x86 and 3.48x on the Pi.

## Use it when

- Scalar composed functions on floats: sinh/cosh/tanh/asinh/acosh/atanh/log10 -- 1.2x-4.5x over glibc, wider margin on ARM than x86
- Squared or small-integer-power distances: pow(base, int) is 1.5x-4.5x faster than std::pow via the explicit int overload
- Array workloads (lidar scans, particle sets): batch sin/cos/sincos/atan2, 2x-6.2x over a std:: loop depending on platform and function
- Scalar sin/cos/sincos on angles already normalized to [-pi, pi], where this ties or slightly beats std on both platforms
- Header/robotics C++17 codebases already tolerant of float precision that want one namespace instead of mixing FastMath:: and std::

## Skip it when

- exp, log, log2, sqrt, or pow with a fractional exponent -- these are thin std:: forwarders, switching buys nothing
- Scalar sin/cos/sincos on angles still needing range reduction ([-2pi,2pi]) on ARM -- measured slower than std (0.63x-0.82x on Pi)
- Anywhere double precision is needed -- the API is float-only, no double overloads exist
- Builds that require -ffast-math -- the library's rounding trick and inf/NaN/signed-zero contracts break under -ffinite-math-only, so it errors out rather than compiling silently wrong
- Dependencies where maintainer bus-factor matters -- 2 GitHub stars, single author, no issues or PRs filed to gauge responsiveness

## How it is fast

The scalar wins come from composing sinh/tanh/atanh/asinh/acosh/log10 directly out of std::exp/std::log rather than calling glibc's own (non-table-based) composed routines, plus binary exponentiation for pow(base,int). An FP-register rounding trick (add/subtract 1.5\*2^23 to a float) gets the integer part needed for exp's and the angle reduction's range folding without crossing to the general-purpose register file. Where glibc already uses lookup tables (exp, log, log2, sqrt), the library forwards to std:: instead of trying to beat it with a polynomial. The batch API's speed comes from SIMD (GCC vector extensions compiling to SSE on x86 / NEON on aarch64) processing 4 floats per iteration, amortizing the call overhead and branches that dominate scalar timings.

## Compared with alternatives

Pick this over VDT, SLEEF, fmath, or trigno_simd_cpp when the workload is scalar, float-only composed math (sinh/tanh/atan2/integer pow) rather than raw vectorized double trig or bulk elementwise arrays -- those siblings post larger, more consistent multiples (VDT 4.7x-12.8x on double exp/sin, SLEEF/fmath on vectorized batches), but fast_math_cpp is the only one of this set that documents where it loses (exp/log/sqrt/fractional pow at parity, ARM scalar sin/cos regressing on wide angles) rather than only showing wins.

## Integration

| | |
|---|---|
| **Form** | static lib (default) or shared lib (CMake FAST_MATH_BUILD_SHARED_LIBS option) -- despite the README's 'Header-Only Design' claim, include/fast_math.hpp only declares functions; definitions live in src/fast_math.cpp and src/fast_math_batch.cpp and must be built/linked via CMake add_subdirectory + target_link_libraries |
| **Dependencies** | none for the library itself; GoogleTest required only to build the test target (BUILD_TESTS=ON by default, disable with -DBUILD_TESTS=OFF to skip the GTest dependency) |
| **Minimum toolchain** | C++17, CMake 3.16+; CI builds with GCC 11 and Clang 15 |
| **Platforms** | x86_64 and aarch64 (Raspberry Pi 4 / Cortex-A72) directly benchmarked; README badge also claims macOS/Windows but GitHub Actions CI only runs ubuntu-latest, so those are untested claims |
| **Thread safety** | not documented; public API is stateless free functions over value arguments, no mutable global/static state visible in the header |
| **Drop-in for the baseline** | partial -- explain: matching float signatures and semantics under a FastMath:: namespace (a namespace swap, not a literal drop-in), and exp/log/log2/sqrt/fractional-pow are literally std:: under the hood; float-only, so it does not cover call sites using double math |

## Gotchas

- CMakeLists.txt has a stray add_library(mcl::map ALIAS fast_math_cpp) -- looks like a leftover from a robotics 'MCL' (Monte Carlo Localization) template this was extracted from; harmless but a sign of how small/informal the project is
- -ffast-math is deliberately rejected by the build -- it silently breaks the FP-register rounding trick (folds (v+magic)-magic back to v), so the library errors out at compile time rather than returning wrong answers under it
- log, log2, asinh-family etc. return a sentinel (-1e38f) for out-of-domain input instead of -inf/NaN like std:: -- a behavioral difference from the baseline being replaced
- sqrt() returns 0 for non-positive input instead of NaN/domain-error like std::sqrt -- another silent semantic deviation

## Caveats and trade-offs

The API is float-only, so the baseline is the float std:: overloads (glibc \*f functions), not double precision. The x86 column ran under WSL2 with no stated CPU model. The README warns that run-to-run variance is 5-10% and that some Pi std-library rows moved up to \~70% between runs. The batch sin API is only at parity with std::sin on the Pi. Very small personal project (2 stars). The README is unusually open about parity and slower cases.

Header-only; several functions (exp, log, log2, sqrt) are deliberately thin wrappers over std:: because the author's own polynomial attempts could not beat glibc's table-based implementations; scalar sin/cos/sincos regress vs std on ARM for angles needing range reduction; author documents 5-10% run-to-run variance and treats anything under 1.1x as a tie.

## Maintenance

Active (last commit 2026-07-28), MIT-licensed, small enough to vendor -- but a very small personal project (2 stars, no issues or PRs filed, single named author), so verify it still builds against your toolchain before depending on it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. The public benchmark code bench/fast_math_bench.cpp (CMake target fast_math_bench, -O3 -march=native -funroll-loops for both sides) produces the README tables. The Raspberry Pi 4 (Cortex-A72) column states compiler GCC 12.2, the flags and the CPU, and raw output is in sample_result/. The x86 column alone would not qualify: it ran on WSL2 with no CPU model.
- **Verifier notes:** The numbers match the README and sample_result/x86_bench_result.txt. The record overstated the batch API as '2-6x' on both platforms, but batch sin on the Pi is 0.98-1.06x. Tier raised to A on the strength of the Raspberry Pi 4 results; the metadata (MIT, 2 stars, last commit 2026-07-28, active) is correct.
- **Fields the verifier corrected:** `claimed_speedup`, `baseline`, `baseline_stdlib`, `workload`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/hijimasa/fast_math_cpp>
  - <https://github.com/hijimasa/fast_math_cpp/blob/main/README.md>
  - <https://github.com/hijimasa/fast_math_cpp/blob/main/sample_result/x86_bench_result.txt>
  - <https://github.com/hijimasa/fast_math_cpp/blob/main/sample_result/raspi4_bench_result.txt>
  - <https://github.com/hijimasa/fast_math_cpp/blob/main/include/fast_math.hpp>
  - <https://github.com/hijimasa/fast_math_cpp/blob/main/bench/fast_math_bench.cpp>
  - <https://github.com/hijimasa/fast_math_cpp/blob/main/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/hijimasa/fast_math_cpp>
  - <https://github.com/hijimasa/fast_math_cpp/blob/main/README.md>
  - <https://github.com/hijimasa/fast_math_cpp/blob/main/CMakeLists.txt>
  - <https://github.com/hijimasa/fast_math_cpp/blob/main/include/fast_math.hpp>
  - <https://github.com/hijimasa/fast_math_cpp/blob/main/.github/workflows/ci.yml>
  - <https://github.com/hijimasa/fast_math_cpp/issues>
  - <https://github.com/hijimasa/fast_math_cpp/pulls>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/hijimasa/fast_math_cpp`) · [data/wave1/enrich/raw/github_com_hijimasa_fast_math_cpp.json](../../../data/wave1/enrich/raw/github_com_hijimasa_fast_math_cpp.json) (enrichment confidence 0.78)

</details>
