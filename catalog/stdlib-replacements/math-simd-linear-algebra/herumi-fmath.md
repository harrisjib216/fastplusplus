# fmath (herumi)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> SIMD array-mode log/exp for float buffers, 9-19x faster than std::logf/std::expf via AVX2/AVX-512.

| | |
|---|---|
| **Beats** | std::logf, std::expf (&lt;cmath&gt;) |
| **Claimed result** | Linux Xeon w9-3495X (AVX-512): logf_v 15.7x, expf_v 18.5x faster than std. Windows Core i7-1165G7 (AVX-512): logf_v 16.9x, expf_v 19.5x. Windows Core i7-1255U (no AVX-512): logf_v 9.4x, expf_v 12.9x. |
| **Workload** | Array-mode natural log and exponential over float arrays (fmath_logf_v / fmath_expf_v), average CPU cycles per 32 elements, using AVX2/AVX-512 |
| **Metric** | throughput |
| **Hardware** | Xeon w9-3495X (Linux, AVX-512); Core i7-1165G7 (Windows, AVX-512); Core i7-1255U (Windows, no AVX-512) |
| **Adoption** | 244 stars |
| **Last commit** | 2026-08-31 |
| **Links** | [repository](https://github.com/herumi/fmath) · [benchmark](https://github.com/herumi/fmath/blob/master/readme.md) |

## Verdict

On the project's own readme benchmark tables (average CPU cycles per 32 elements), fmath's array-mode logf_v/expf_v beat scalar std::log/std::exp array loops by 15.7x/18.5x on a Linux Xeon w9-3495X (AVX-512), 16.9x/19.5x on a Windows Core i7-1165G7 (AVX-512), and 9.4x/12.9x on a Windows Core i7-1255U without AVX-512; compiler and flags used for these numbers are not stated. The comparison code (test/log_v.cpp, test/exp_v.cpp), which loops std::log/std::exp over the same arrays, is public in the repo.

## Use it when

- Hot loops applying std::logf/std::expf over float arrays with n &gt;= 16 that can be laid out as contiguous src/dst buffers
- x86-64 targets guaranteeing AVX2; extra speedup available automatically on AVX-512F+DQ Xeons/desktops
- Single-precision-only workloads (audio, ML feature transforms, scientific arrays) where a fast SIMD approximation's accuracy is acceptable
- Throughput-bound batch processing rather than single-call latency, e.g. bulk activation functions or vectorized transforms

## Skip it when

- Calls with n &lt; 16 elements — the readme explicitly states fmath's array functions are slower than std:: there
- Double precision needed — fmath.h declares only float (logf/expf) variants, no logd/expd in this version
- Scalar call sites that can't be restructured into array form, since the API has no single-value entry point of its own
- Platforms without AVX2 (older x86-64 chips, ARM/aarch64) — AVX2 is a hard minimum, not degraded gracefully further
- Projects wanting a small header-only drop-in — this ships as generated assembly built into a static lib, not header-only, despite include/fmath.h existing

## How it is fast

The log/exp kernels are not written as C++ that the compiler auto-vectorizes; they are generated ahead of time as raw x86 machine code by a Python script (src/gen_fmath.py) using the bundled s_xbyak assembler-generation library, emitting GAS (src/fmath.S) or MASM (src/fmath.asm) that gets assembled into libfmath. This gives hand-tuned SIMD kernels that process 8 (AVX2) or 16 (AVX-512) floats per instruction using a polynomial/lookup-table approximation (table size tunable via LOG_L), amortizing per-call overhead across the whole array in one pass. fmath_init(), run via a GCC constructor attribute or an MSVC CRT init-section hook before main(), auto-selects the AVX-512 kernel when the CPU supports AVX512F+DQ, else falls back to the AVX2 baseline.

## Compared with alternatives

Among siblings, VDT and SLEEF also cover exp/log but at per-call scalar latency (VDT: \~2.8-12.8x vs libm) or double precision; fmath is narrower (float32 logf/expf only, array-mode only) but shows the largest claimed log/exp speedup (9.4-19.5x) because it measures bulk array throughput on AVX2/AVX-512, not single calls. Pick fmath when you specifically need bulk float32 log/exp over large contiguous arrays on x86-64 and can restructure call sites into array form; pick VDT/SLEEF/FastMath C++ instead for scalar call sites, double precision, or a broader function set (sin/cos/pow, etc.).

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | bundled s_xbyak.py (codegen) and xbyak_util.h (runtime CPU feature detection); Python 3 to (re)generate src/fmath.S/.asm; no external runtime deps once built |
| **Minimum toolchain** | C++20 (Makefile builds with -std=c++20, mk.bat with /std:c++20); GCC/Clang on Linux or MSVC cl on Windows |
| **Platforms** | x86-64 with AVX2 required minimum; auto-upgrades to AVX-512F+DQ kernels if detected at startup; no ARM/aarch64 support documented |
| **Thread safety** | not documented; the AVX2-vs-AVX-512 dispatch (global function pointers) is written once via a constructor/CRT-init hook before main(), so concurrent calls into fmath_logf_v/fmath_expf_v on disjoint buffers appear safe, but the project makes no explicit thread-safety claim |

## Gotchas

- Dispatch can be pinned to the AVX2 kernel with the FMATH_CPU=avx2 environment variable, and the AVX-512 log variant switched to the lower-max-error 'tq' form with FMATH_LOG=tq
- No LICENSE file exists in the repo (GitHub's detector reports license: null); BSD-3-Clause is only stated in readme.md and the fmath.h header comment
- This is a rewrite that is explicitly not backward compatible with the older single-header fmath.hpp/Xbyak-JIT version; a since-fixed NaN bug (exp(89.0f), issue #14) was reported and patched against that old version, not this one
- Benchmark numbers are cycles-per-32-elements on specific CPUs; the readme does not state which compiler or flags produced them

## Caveats and trade-offs

GitHub's license detector reports no LICENSE file (license: null). BSD-3-Clause ('modified new BSD license') is stated in readme.md and in the include/fmath.h header comment, but there is no standalone LICENSE file. The benchmark tables give CPU model and OS but not the compiler or flags. The repo's build scripts use Makefile CFLAGS -O2 and, on Windows, mk.bat with MSVC cl /O2 /arch:AVX2, but the readme does not tie the numbers to them. The readme warns the functions are slow for n &lt; 16.

Array-only API operating on raw float buffers (not a drop-in replacement for scalar std::logf/std::expf calls); requires AVX2 as a minimum, auto-upgrades to AVX-512; author explicitly warns against use for small n (&lt;16) because it is slower than std there; single precision only.

## Maintenance

Actively maintained (last commit 2026-08-31, 244 stars, 36 forks) and BSD-3-Clause per readme/header, but there is no standalone LICENSE file, and this version is a non-backward-compatible rewrite of the older fmath.hpp/Xbyak-JIT API, so old issues and usage examples don't carry over.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** readme.md tables give cycles/32 elements for fmath vs std (logf 6.72 vs 105.20 = 15.7x, expf 5.60 vs 103.80 = 18.5x on Xeon w9-3495X, etc.), and the benchmark code is public (test/log_v.cpp, test/exp_v.cpp compare std::log / std::exp array loops). The readme does not say which compiler or flags produced the numbers, so it falls short of A.
- **Verifier notes:** All six speedups match readme.md exactly. The Windows rows were probably built with MSVC (mk.bat uses cl.exe) and the Linux rows with default CC/CXX at -O2. The readme does not say this, so baseline_stdlib and compiler_and_flags are left unchanged.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/herumi/fmath>
  - <https://github.com/herumi/fmath/blob/master/readme.md>
  - <https://github.com/herumi/fmath/blob/master/test/log_v.cpp>
  - <https://github.com/herumi/fmath/blob/master/Makefile>
  - <https://github.com/herumi/fmath/blob/master/mk.bat>
  - <https://github.com/herumi/fmath/blob/master/include/fmath.h>
- **Sources the enricher read:**
  - <https://github.com/herumi/fmath>
  - <https://github.com/herumi/fmath/blob/master/readme.md>
  - <https://github.com/herumi/fmath/blob/master/include/fmath.h>
  - <https://github.com/herumi/fmath/blob/master/Makefile>
  - <https://github.com/herumi/fmath/blob/master/mk.bat>
  - <https://github.com/herumi/fmath/blob/master/test/log_v.cpp>
  - <https://github.com/herumi/fmath/blob/master/src/cpu.cpp>
  - <https://github.com/herumi/fmath/issues/14>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/herumi/fmath`) · [data/wave1/enrich/raw/github_com_herumi_fmath.json](../../../data/wave1/enrich/raw/github_com_herumi_fmath.json) (enrichment confidence 0.6)

</details>
