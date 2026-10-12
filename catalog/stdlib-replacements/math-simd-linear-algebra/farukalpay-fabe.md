# FABE13-HX

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> SIMD sin/cos/sincos array kernel for C beating libm; rational Ψ-Hyperbasis approximation, no bit-exact IEEE guarantee.

| | |
|---|---|
| **Beats** | libm sin/cos/sincos (the implementation &lt;cmath&gt;'s std::sin/std::cos ultimately call into) |
| **Claimed result** | README: 'up to 8.4x' faster than libm on x86 AVX2+FMA (Replit Clang 14 and MacBook Pro AppleClang 16), shown only in chart images with no table. The ARM64/NEON table ranges from 1.00x (N=10) through 2.33-2.56x (N=100-10k) and 1.53x (N=100k) to 4.36-4.44x (N=1M-100M) and 5.82x (N=1e9). Max diff vs libm \~1.2e-11. |
| **Workload** | sin/cos/sincos evaluated over arrays ranging from 10 to 1e9 doubles, compared against system libm (GNU math.h on Linux, macOS system math.h) |
| **Metric** | throughput |
| **Hardware** | No specific CPU model/SKU given; platforms described only as 'Replit cloud Linux (AVX2+FMA)', 'MacBook Pro 16-inch (AVX2+FMA)', and generic 'ARM64/NEON' |
| **Compiler and flags** | Clang 14 (Replit/Linux, nix) / AppleClang 16.0 (macOS); -Ofast -march=native -funroll-loops -ffast-math (build.sh) |
| **Adoption** | 64 stars |
| **Last commit** | 2025-04-20 |
| **Links** | [repository](https://github.com/farukalpay/FABE) · [benchmark](https://github.com/farukalpay/FABE/blob/main/README.md) |

## Verdict

The README compares fabe13_sincos array throughput to system libm's sincos (GNU math.h on Replit Linux/Clang 14, macOS system math.h on AppleClang 16) on unspecified x86 AVX2+FMA hardware, claiming 'up to 8.4x' only via headline text and chart images, with no table. Its one real table, for unspecified ARM64/NEON hardware, shows 1.00x-2.56x for N=10-10k, 1.53x at N=100k, and 4.36x-5.82x from N=1M-1e9, with max sin/cos error \~1.2e-11 vs libm; both fabe13 and the libm reference loop were built with -Ofast -ffast-math.

## Use it when

- Batch sin/cos/sincos over arrays of roughly 1e6-1e9 doubles on x86-64 (AVX2+FMA or AVX-512F) or aarch64 (NEON), where the README's own numbers show the real gains (4.4x-5.8x on ARM).
- You can build with -Ofast -ffast-math (or accept its semantics) and don't need bit-exact/IEEE-754-strict results — max observed diff vs libm is \~1.2e-11.
- You want a single small MIT-licensed C99 source pair to vendor directly into a build rather than link a shared library.
- You only need sin/cos/sincos/tan/cot/sinc acceleration, not asin/acos/atan, which just forward to libm here.

## Skip it when

- Small arrays (N &lt;= 10,000): the README's own ARM table shows only 1.0x-2.56x there, and x86 has no per-size table at all, only headline chart images.
- You need strict IEEE-754 semantics or bit-reproducible output — default build flags are -Ofast -march=native -ffast-math.
- You need float32/single-precision (fabe13_sinf, etc.) — listed only on the roadmap, not implemented.
- You need an actively maintained or independently reproduced benchmark — last commit 2025-04-20, zero GitHub issues, single-author README-only numbers, no CPU model given for any platform.
- You need accelerated asin/acos/atan — those symbols exist but call straight into system libm.

## How it is fast

Replaces libm's polynomial minimax approximations with a rational 'Ψ-Hyperbasis' core, Ψ(x) = x/(1+(3/8)x²), plus rational correction terms for sin/cos, avoiding some of the work a general-purpose libm does. A GCC/Clang constructor function probes the CPU once at load time (AVX-512F &gt; AVX2+FMA &gt; NEON &gt; scalar) and locks in one dispatch target for the process. The array path uses branchless quadrant correction and Payne-Hanek range reduction, unrolled and vectorized per architecture, so large arrays amortize reduction cost across SIMD lanes.

## Compared with alternatives

Pick FABE13 only if you want a tiny, MIT, two-file C sincos batch kernel to vendor and don't need rigor; SLEEF and VDT are the safer defaults for sin/cos vs libm since they carry more independent/peer-reviewed benchmarking, and trigno_simd_cpp is a closer weight-class alternative but also less scrutinized than SLEEF/VDT.

## Integration

| | |
|---|---|
| **Form** | source-drop (fabe13.c + fabe13.h) or static lib via the provided CMakeLists.txt |
| **Dependencies** | none for the library itself; links libm (m) for the atan/asin/acos passthroughs and the reference benchmark, which also links rt on non-Apple platforms |
| **Minimum toolchain** | C99 (CMakeLists sets C_STANDARD 99); CMake 3.15+ for the provided build; verified with Clang 14 and AppleClang 16.0 |
| **Platforms** | x86-64 (AVX2+FMA baseline, optional AVX-512F via FABE13_USE_AVX512), aarch64 (NEON); scalar fallback elsewhere |
| **Thread safety** | not documented explicitly; CPU dispatch runs once via __attribute__((constructor)) before main and sets a static global (active_impl_type) that is read-only afterward, so concurrent calls appear safe by construction, but the optional FABE13_ENABLE_FAST_FP define flips FTZ/DAZ bits in the process-wide MXCSR register, affecting all threads' FP state |
| **Drop-in for the baseline** | partial — explain: fabe13_sin/cos/tan/cot/sinc match libm's double(double) signature, but fabe13_sincos(in, sin_out, cos_out, n) is a new batch API with no libm equivalent to swap in for, and fabe13_atan/asin/acos are pass-throughs to libm, not replacements |

## Gotchas

- fabe13_atan, fabe13_asin, fabe13_acos sit next to the accelerated functions but the header/source say they 'use standard libm' — no speedup despite looking like part of the same API.
- FABE13_ENABLE_FAST_FP (opt-in compile define) sets FTZ/DAZ on the CPU's MXCSR, relaxing subnormal handling process-wide, not just for this library's own calls.
- The default build (build.sh, CMakeLists.txt) compiles everything, including the libm comparison loop inside the benchmark, with -Ofast -march=native -ffast-math, so relaxed FP semantics apply to both sides of the reported comparison.
- fabe13_get_active_implementation_name()/fabe13_get_active_simd_width() let you check which kernel (AVX-512F/AVX2/NEON/scalar) was actually selected at load time — worth calling once at startup to confirm you got a SIMD path, not scalar fallback.

## Caveats and trade-offs

First-party README benchmark only, with no independent reproduction. No CPU model is stated for any platform. The x86 '8.4x' appears only as a headline and chart images. The ARM speedup is 1.0-2.6x below 1M elements. The benchmark seeds rand() with time(NULL), so it is not bit-reproducible. The libm reference loop is also compiled with -Ofast -ffast-math. The MIT LICENSE file lives at fabe13-old/LICENSE (the README points to it), so the GitHub API reports no license. It uses the author's own branding ('Psi-Hyperbasis', 'Lightcap Initiative') and has no third-party citations.

Approximate, not correctly rounded; built with -Ofast -ffast-math, which relaxes IEEE-754 semantics and can itself inflate speed deltas versus a strict-mode libm build; exposes a scalar API (fabe13_sin(double) etc.) despite internally using SIMD

## Maintenance

Stale: last commit 2025-04-20, zero open or closed GitHub issues (no community vetting); MIT-licensed and small enough to vendor (2 files, C99), but the LICENSE file only exists under fabe13-old/LICENSE so GitHub's own license badge reports none.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** The README benchmarks FABE13 sincos against system libm and says 'up to 8.4x' on x86 (in text and chart images only). It has an ARM64/NEON table. The benchmark code (fabe13/benchmark_fabe13.c), compilers and flags are public, but no CPU model is given, so it is C.
- **Verifier notes:** Downgraded for an overstated claim, not for tier. The record's '4.36-5.82x on ARM64 depending on array size' omits the 1.00-2.56x results at small sizes. Metadata verified: 64 stars, last commit 2025-04-20 (stale), MIT text confirmed in fabe13-old/LICENSE.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/farukalpay/FABE/blob/main/README.md>
  - <https://github.com/farukalpay/FABE>
  - <https://github.com/farukalpay/FABE/blob/main/fabe13-old/LICENSE>
  - <https://github.com/farukalpay/FABE/blob/main/CMakeLists.txt>
  - <https://github.com/farukalpay/FABE/blob/main/build.sh>
  - <https://github.com/farukalpay/FABE/blob/main/fabe13/benchmark_fabe13.c>
- **Sources the enricher read:**
  - <https://github.com/farukalpay/FABE>
  - <https://github.com/farukalpay/FABE/blob/main/README.md>
  - <https://github.com/farukalpay/FABE/blob/main/CMakeLists.txt>
  - <https://github.com/farukalpay/FABE/blob/main/build.sh>
  - <https://github.com/farukalpay/FABE/blob/main/fabe13/fabe13.h>
  - <https://github.com/farukalpay/FABE/blob/main/fabe13/fabe13.c>
  - <https://github.com/farukalpay/FABE/blob/main/fabe13/benchmark_fabe13.c>
  - <https://github.com/farukalpay/FABE/issues>
  - <https://github.com/farukalpay/FABE/blob/main/fabe13-old/LICENSE>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/farukalpay/fabe`) · [data/wave1/enrich/raw/github_com_farukalpay_fabe.json](../../../data/wave1/enrich/raw/github_com_farukalpay_fabe.json) (enrichment confidence 0.3)

</details>
