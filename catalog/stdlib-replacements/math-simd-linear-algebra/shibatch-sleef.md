# SLEEF (SIMD Library for Evaluating Elementary Functions)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `BSL-1.0` · 🟢 active

> Vectorized C library of libm math functions (sin, cos, exp, log, pow); beats scalar &lt;cmath&gt;/libm when call sites are SIMD-batched.

| | |
|---|---|
| **Beats** | &lt;cmath&gt; (scalar libm, represented in the paper by FDLIBM as the reference scalar implementation) |
| **Claimed result** | Table 2, reciprocal throughput in ns per call, 1-ulp variants. SLEEF is the 256-bit AVX2 vectorized function (each call evaluates 4 doubles); FDLIBM 5.3 is scalar (1 value per call). sin [0,1e+100]: FDLIBM 162.3 vs SLEEF 48.79 (\~3.3x per call). cos [0,1e+100]: 162.1 vs 50.38 (\~3.2x). tan [0,1e+100]: 177.0 vs 48.82 (\~3.6x). log [0,1e+300]: 31.66 vs 15.46 (\~2.0x). exp [-700,700]: 12.19 vs 7.663 (\~1.6x). pow: 69.40 vs 55.53 (\~1.25x). On the fast-path domain [0.4,0.5], scalar FDLIBM is FASTER per call (sin 4.927 vs 11.43, cos 11.42 vs 13.75, tan 7.819 vs 17.30), as it is for acos (12.07 vs 16.09) and atan (10.16 vs 22.12). Per element (dividing by 4 lanes), SLEEF is faster in every 1-ulp row. (derived from page data) |
| **Workload** | Reciprocal throughput (ns per call) of 256-bit vectorized double-precision SLEEF 3.4 (plus Vector-libm and Intel SVML) vs scalar FDLIBM 5.3. A single-threaded tight loop makes 10^10 calls over pre-generated, uniformly random arguments in each listed domain. The calling loop was compiled without optimization so calls are not elided (the libraries use their -O3 flags), and it is timed with clock_gettime. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-6700 CPU @ 3.40GHz, Turbo Boost disabled (physical PC, no VM) |
| **Compiler and flags** | SLEEF and FDLIBM compiled with gcc-7.3.0 -O3 -mavx2 -mfma; Vector-libm compiled with gcc-7.3.0 -O3 -march=native -ftree-vectorize -ftree-vectorizer-verbose=1 -fno-math-errno; SVML via Intel C Compiler 19 with -fimf-max-error=1.0/4.0 |
| **Adoption** | 853 stars |
| **Last commit** | 2025-12-25 |
| **Links** | [repository](https://github.com/shibatch/sleef) · [benchmark](https://arxiv.org/pdf/2001.09258) |

## Verdict

A peer-reviewed paper (Shibata & Petrogalli, IEEE TPDS vol. 31 no. 6, 2020; arXiv 2001.09258) Table 2 measured reciprocal throughput (ns/call) of SLEEF 3.4's 256-bit AVX2 double-precision vector functions (4 lanes/call, 1-ULP tier) against scalar FDLIBM 5.3, both built with gcc-7.3.0 -O3 -mavx2 -mfma, on an Intel Core i7-6700 with Turbo off: wide-domain sin/cos/tan ran \~3.2-3.6x faster per call, log \~2.0x, exp \~1.6x, pow \~1.25x; on narrow argument domains and for acos/atan, scalar FDLIBM was faster per call than vector SLEEF. This is a SIMD-vs-scalar comparison, not a like-for-like scalar replacement of std::sin/std::exp.

## Use it when

- Hot loops that already batch scalar math across arrays and can call the Sleef_\*dN_u10/u35 vector entry points directly instead of std::sin/std::exp per element
- Wide-domain or branchy transcendental workloads (large-magnitude arguments needing full range reduction) where scalar libm's branches hurt SIMD throughput — Table 2 shows \~3.2-3.6x per-call wins for wide-domain sin/cos/tan, \~2.0x log, \~1.6x exp, \~1.25x pow (SLEEF 4-wide AVX2 vs scalar FDLIBM)
- Need one source portable across AVX2, AVX512F, AdvSIMD (and experimentally SSE2/RISC-V) via runtime dispatch
- Can tolerate the 3.5-ULP accuracy tier for extra speed on non-critical paths
- Also need DFT or quad-precision elementary functions bundled with the math kernels

## Skip it when

- Scalar call sites (one value at a time): the benchmarked win is SIMD-vs-scalar, and on narrow argument domains or for acos/atan, scalar FDLIBM was faster per call than vector SLEEF in the same table
- Want a drop-in &lt;cmath&gt; replacement without restructuring loops to load SIMD vectors — API is a different symbol/type surface, not operator/name-compatible with std::sin
- SSE2-only x86 targets (experimental, 'seeking sponsorship') or RISC-V RVV targets (unmaintained, may be removed without notice)
- Code that compiles the inline-header path without -O3: open issue #436 reports wrong results in that configuration
- Need guaranteed-correct cos() when any vector lane's argument may reach &gt;=1e14: open issue #444 reports inconsistent per-lane results there, and the benchmarked domain here goes up to 1e100

## How it is fast

Processes multiple lanes per call (4/8 doubles, 8/16 floats depending on ISA) instead of looping scalar libm calls, and uses a modified Payne-Hanek argument-reduction algorithm redesigned to minimize the data-dependent branching that otherwise forces every SIMD lane onto the slow path if any single lane needs it (paper: 'SLEEF: A Portable Vectorized Library of C Standard Mathematical Functions', Shibata & Petrogalli). It offers a 1-ULP tier (compensated double-double arithmetic) and a faster \~3.5-ULP tier with a shorter polynomial, trading accuracy for speed. Portability comes from wrapping each ISA's intrinsics behind common inline-function/macro helper headers (helperavx2.h, helperadvsimd.h, helpersve.h, ...) compiled per-target.

## Compared with alternatives

Pick SLEEF over VDT, fmath, or trigno_simd_cpp when you need multiple ISAs (AVX2/AVX512F/AdvSIMD/RISC-V) behind one API with runtime dispatch, plus quad-precision or DFT routines, or want a tunable 1-ULP/3.5-ULP accuracy knob; those siblings target a single ISA/precision and a narrower function set.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (CMake build; not header-only, though inline-header build path also exists) |
| **Dependencies** | none at runtime for the library itself; build needs CMake 3.18+ and matching C/C++ compiler versions; TLFloat is auto-fetched if not present; tests additionally need libssl/libcrypto, libgmp, libmpfr, libfftw |
| **Minimum toolchain** | CMake 3.18+; GCC/Clang/MSVC (README requires the C and C++ compilers to be the same version) |
| **Platforms** | x86-64 (SSE2 experimental, AVX2 and AVX512F mainline-supported), AArch64 AdvSIMD (mainline), RISC-V RVVM1/RVVM2 (unmaintained); toolchain files also exist for POWER (ppc64el) and s390x; CI-tested on Linux/Windows/macOS per the README support matrix |
| **Thread safety** | not documented as thread-safe; open issue #560 (2024) reports the runtime CPU-feature-detection dispatcher races on the first call across threads |
| **Drop-in for the baseline** | false — separate Sleef_\* symbols take native SIMD vector types (e.g. __m256d), not scalar double/float, so call sites must be rewritten to pass vectors |

## Gotchas

- Inline-header build path gives wrong results if the including translation unit is compiled without -O3 (open issue #436, since 2021)
- Vectorized cos() can give inconsistent per-lane results once any lane's argument is &gt;=1e14 (open issue #444) — relevant since the benchmarked domain in this record runs up to 1e100
- exp and pow can return infinity earlier than correct (open issue #600, 2024)
- Runtime CPU-extension dispatch is not thread-safe on first call, per an open maintainer-acknowledged issue (#560)

## Caveats and trade-offs

Table 2 compares SLEEF's 4-wide AVX2 vector functions against scalar FDLIBM. It is not a like-for-like scalar replacement of std::sin/std::exp: the gains need vectorized call sites, and SLEEF's scalar entry points are not in the table. Per call, FDLIBM beats vector SLEEF on narrow-domain sin/cos/tan and on acos/atan. FDLIBM is a reference libm, not glibc's libm or the libm behind libstdc++/libc++/MSVC &lt;cmath&gt;. The benchmark loop was built unoptimized for every library alike. The sleef.org benchmark page compares only against SVML. The Table 2 harness for FDLIBM is not in the repo.

Vectorized code takes the slow path for a whole SIMD register if any lane needs it; library offers a 1-ULP and a faster 3.5-ULP accuracy tier as a speed/accuracy tradeoff; on narrow argument domains the scalar-equivalent speed roughly ties FDLIBM rather than beating it, the win is concentrated in wide-domain/branchy cases and true vector (multi-lane) throughput.

## Maintenance

Actively maintained — last commit 2025-12-25, latest tagged release 3.9.0 (March 2025); this session found five open issues touching accuracy and thread-safety dating back to 2021. BSL-1.0 licensed and small enough to vendor or build as a static/shared lib; the cited benchmark used the older 3.4 branch, several major releases behind current master.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now B.
- **Tier reason:** A peer-reviewed paper (IEEE TPDS vol. 31 no. 6, June 2020; arXiv 2001.09258) gives Table 2 reciprocal throughputs for SLEEF vs scalar FDLIBM 5.3, with gcc-7.3.0 -O3 -mavx2 -mfma on an i7-6700 with Turbo off. The Table 2 harness is not published: SLEEF 3.4.0's src/libm-benchmarks has only SLEEF/SVML benches, not FDLIBM, and master no longer has that directory. So it is not A.
- **Verifier notes:** The record misread Table 2. Its 'narrow domain parity, sin 11.43 vs 11.41' pairs two SLEEF cells (the [0.4,0.5] and [0,6.28] rows); the actual FDLIBM value for narrow-domain sin is 4.927, so FDLIBM wins per call there. The record also hid that the comparison is SIMD-vs-scalar. The tier stays B; the verdict is downgrade because the claim needed substantive correction. The metadata (BSL-1.0, 853 stars, last commit 2025-12-25, active) is correct.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/pdf/2001.09258>
  - <https://github.com/shibatch/sleef>
  - <https://github.com/shibatch/sleef/tree/3.4.0/src/libm-benchmarks>
- **Sources the enricher read:**
  - <https://github.com/shibatch/sleef>
  - <https://github.com/shibatch/sleef/blob/master/README.adoc>
  - <https://github.com/shibatch/sleef/blob/master/src/libm/dispatcher.h>
  - <https://github.com/shibatch/sleef/issues/436>
  - <https://github.com/shibatch/sleef/issues/444>
  - <https://github.com/shibatch/sleef/issues/600>
  - <https://github.com/shibatch/sleef/issues/560>
  - <https://github.com/shibatch/sleef/issues/570>
  - <https://github.com/shibatch/sleef/releases>
  - <https://arxiv.org/abs/2001.09258>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/shibatch/sleef`) · [data/wave1/enrich/raw/github_com_shibatch_sleef.json](../../../data/wave1/enrich/raw/github_com_shibatch_sleef.json) (enrichment confidence 0.72)

</details>
