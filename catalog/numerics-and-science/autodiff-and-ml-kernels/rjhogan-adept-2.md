# Adept-2

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0 (library); GNU all-permissive license for test and benchmark code` · 🟢 active

> Expression-template reverse/forward-mode C++ AD library with Fortran-like arrays; tapes faster than ADOL-C, CppAD and Ceres in third-party benchmarks.

| | |
|---|---|
| **Beats** | CppAD (measured in the benchmark); autodiff (autodiff/autodiff, measured); ADOL-C and Sacado (named in the user guide, qualitative) |
| **Claimed result** | Xcelerit ad-benchmarks (GCC 13.3, Xeon 8488C, run by the XAD vendor): Adept 2 beats CppAD on all 4 rows (e.g. Heston 91 vs 268 ms) and loses to XAD on all 4; ADBench (OMS 2018, Adept 1.1) showed gains over ADOL-C on GMM (1.8x unsplit). |
| **Workload** | Time to compute all sensitivities (reverse-mode adjoint AD) for four quant-finance workloads: Heston Monte Carlo (8 sensitivities), SABR calibration (15), XVA CVA (40), LIBOR swaption (161). |
| **Metric** | latency |
| **Hardware** | Intel Xeon Platinum 8488C, Ubuntu 24.04 |
| **Compiler and flags** | GCC 13.3, -O3 -mavx2 -mfma on all libraries, median of 10 measured iterations after warmup (ad-benchmarks README) |
| **Adoption** | 189 stars; used in climate and weather codes (ECMWF) |
| **Last commit** | 2025-10-05 |
| **Links** | [repository](https://github.com/rjhogan/Adept-2) · [benchmark](https://github.com/auto-differentiation/ad-benchmarks) |

## Verdict

The ADBench paper (Microsoft, AD2016 / Optimization Methods and Software 2018) timed Adept 1.1-era code on a Xeon E5-1620 under Windows 10 with no compiler flags stated: bundle-adjustment Jacobians were about 12.5x faster than ADOL-C and 3.3x faster than Ceres at the smallest size (10.7x vs ADOL-C at the largest, where Ceres crashed), and split GMM gradients about 16x faster than ADOL-C, but unsplit GMM only about 1.8x and ADOL-C won at several sizes. Separately, Xcelerit's ad-benchmarks (GCC 13.3, -O3 -mavx2 -mfma, Xeon Platinum 8488C) show Adept 2 faster than CppAD on Heston MC (91 vs 268 ms), SABR (19 vs 32 ms), XVA CVA (7.1 vs 8.0 s) and LIBOR swaption (1.15 vs 4.57 s), but slower than XAD on all four.

## Use it when

- Reverse-mode gradients of scalar objectives written in plain C++ with many inputs, where you want one-line taping per call and no separate tape-replay step (e.g. variational data assimilation, retrieval schemes, model calibration).
- Code that already thinks in Fortran-style arrays: Adept arrays let you differentiate whole-array expressions and exchange arrays with Fortran (array_fortran.h).
- Small dense Jacobians per residual, as in bundle adjustment, where ADBench measured Adept about 3.3x faster than Ceres and 10-12x faster than ADOL-C (derived from page data).
- Quant-style Monte Carlo or calibration sensitivities when you need an Apache-2.0 tape library and XAD is not an option: in Xcelerit's ad-benchmarks Adept 2 beat CppAD on all four workloads.
- Projects that need old toolchains: the ChangeLog keeps C++98 compatibility, with C++11 features (thread_local, move semantics, initializer lists) used when available.

## Skip it when

- When you need maximum tape speed: XAD's open-source tape mode was 1.1x (LIBOR) to 2.3x (Heston) faster than Adept 2 in ad-benchmarks, and the FastAD paper claims 2-10x over Adept.
- Higher-order derivatives: ad-benchmarks lists Adept as forward and reverse only, while CppAD and XAD are listed as higher-order; the Adept minimizers use first derivatives or a user-supplied Hessian.
- Very large single recordings: in ADBench unsplit Adept crashed on GMM at 429k parameters (and from the second size up on the 1k-point GMM), so large problems must be split into per-term recordings.
- Matrix-heavy code without an optimized BLAS: configure warns that without BLAS matrix multiplication is unavailable and without LAPACK linear-algebra routines are unavailable.
- When a hand-written adjoint or a source-transformation tool is feasible: ADBench found hand-written C++ about 3.5x faster than Adept on BA and Tapenade faster on GMM and BA.

## How it is fast

Expression templates collapse each right-hand-side statement into a single compile-time expression, so the tape stores one statement plus its precomputed partial derivatives instead of one node per elementary operation (Hogan 2014, ACM TOMS 40:26). Taping is cheap enough to redo on every call, which is why the ADBench paper found Adept's per-call ('split') taping barely slower than one large tape while ADOL-C slowed down markedly. The Stack uses raw dynamically allocated arrays (the base.h comment says these are faster than STL containers), passive array expressions are vectorized with SSE2/AVX/AVX-512/ARM NEON packets, and Jacobians are computed in OpenMP-parallel strips.

## Compared with alternatives

Pick Adept over XAD or FastAD when you want Apache-2.0 AD with built-in multidimensional arrays, Fortran interop and minimizers more than peak tape speed (both siblings measure faster than Adept), and over Enzyme when you cannot depend on an LLVM/Clang plugin. HyperJet is for small dense second-order derivatives and Sleipnir is an AD-plus-NLP-solver stack, so neither replaces a general reverse-mode library.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (autotools build); a library-free single-translation-unit mode (adept_source.h) also exists |
| **Dependencies** | none for scalar AD; BLAS and LAPACK (detected via a Fortran compiler at configure time) for matrix multiply and linear algebra; OpenMP optional for parallel Jacobians |
| **Minimum toolchain** | C++98 (C++11 required for ADEPT_STORAGE_THREAD_SAFE; thread_local used when available); autotools needed to build from a git snapshot (autoreconf -i) |
| **Platforms** | any; vectorization on x86 SSE2/AVX/AVX-512 and 64-bit ARM NEON, disabled on 32-bit ARM |
| **Thread safety** | The global Stack pointer is thread-local, so each thread can record on its own Stack; it falls back to thread-unsafe where thread_local is unavailable (older Mac toolchains). Array reference counts are not atomic unless ADEPT_STORAGE_THREAD_SAFE is defined (C++11). ADEPT_FAST makes the stack thread-unsafe. |
| **Drop-in for the baseline** | partial — replaces CppAD/ADOL-C-style operator-overloading AD for first-order derivatives, but with its own types (aReal, aVector, Stack) and API; it is not a drop-in for oneDNN/cuDNN/XNNPACK/Eigen Tensor kernels. |

## Gotchas

- Call stack.new_recording() after initializing independent variables and before any active arithmetic; the old Stack::start(), clear() and clear_statements() now throw feature_not_available.
- Errors are reported by throwing adept::exception subclasses (gradient_out_of_range, gradients_not_initialized, stack_already_active, wrong_gradient, non_finite_gradient, array exceptions).
- Compiling with -ffast-math silently turns on ADEPT_FAST_EXPONENTIAL, which changes exp results; ADEPT_FAST also disables dimension and alias checking, so aliased array statements need eval().
- Correctness history: 2020-2021 releases fixed wrong derivatives of Active&lt;double&gt;/int and product, wrong maxval/minval and norm2, and unaligned AVX crashes; two 2025 reports of wrong gradients on extreme-magnitude or redundant expressions (issues #36, #37) were closed with no maintainer fix shown on the issue pages.

## Known shortcomings

- ADBench (OMS 2018) tested Adept 1.1 (2015), not Adept-2; Ceres crashed rather than 'did not finish'; unsplit GMM gain only 1.8x vs ADOL-C (the 16x is split-vs-split); ADOL-C is faster at some GMM sizes; baseline not in the category list.
- Record mixed two sources: workload, benchmark_url, compiler and hardware describe Xcelerit ad-benchmarks (GCC 13.3, Xeon 8488C, run by the XAD vendor) while claimed_speedup came from ADBench (Adept 1.1 era); in ad-benchmarks Adept 2 beats CppAD on all 4 rows (Heston 91 vs 268 ms) and loses to XAD on all 4. Issues #36/#37 (wrong gradients, 2025) closed with no fix shown; unsplit GMM crashed at 429k parameters.

## Caveats and trade-offs

The ADBench paper used the newest tool versions available in July-August 2015, i.e. Adept 1.1 (June 2015 per the Adept-2 ChangeLog), not Adept 2.x (2.0 released September 2017); the Adept-2 README claims it is as fast as Adept 1.1 but that is first-party. Compiler and flags are not stated. On GMM without manual splitting ADOL-C was faster than Adept at some sizes (330 parameters: 8.79e-02 vs 9.61e-02; 3,300: 8.49e-01 vs 9.76e-01; 10,700: 1.90 vs 3.11), unsplit Adept crashed at 429k parameters and unsplit ADOL-C crashed from 21.5k parameters up. Ceres is forward-mode only in this test, which disadvantages it. Tapenade (C source transformation) was faster than Adept on both GMM and BA. The table captions do not restate the time unit. Adept is not the incumbent in this category's baseline list (oneDNN, cuDNN, XNNPACK, Eigen tensor). ADBench repository is archived (July 2024). [retier] Two sources were mixed in the original record (ad-benchmarks for workload/hardware, ADBench for the speedup); ad-benchmarks is vendor-run by XAD's maker.

Operator-overloading AD with expression templates; Adept 2 adds array classes and optimizers; autotools build; reverse mode records a tape; optimized BLAS recommended for matrix work.

## Maintenance

Maintained by Robin Hogan at ECMWF (last commit 2025-10-05, version 2.1.4 in progress, 189 stars); the Apache-2.0 library and all-permissive tests make it safe to vendor, though the official site and user guide (met.reading.ac.uk) were unreachable from here and open issues include a Mac install problem and out-of-tree build failure.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now B.
- **Tier reason:** Peer-reviewed comparison (ADBench paper; the source says shorter versions appeared at AD2016 and in Optimization Methods and Software, Feb 2018) with absolute-runtime tables for BA and GMM where Adept beats ADOL-C and Ceres; benchmark code is public in microsoft/ADBench and the CPU (Xeon E5-1620 @ 3.60GHz, Windows 10) is stated, but no compiler or flags, so not A.
- **Verifier notes:** Every cited number is in the ms.tex tables (tab:ba-abs, tab:gmm-10k-abs); fixed 'Ceres did not finish' to 'crashed' (bullet = crash per caption) and added the much smaller unsplit GMM ratio. Metadata checked: Apache-2.0 core (test/ and benchmark/ under GNU all-permissive), 189 stars, not archived, last commit 2025-10-05.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/microsoft/ADBench/master/Documents/ms.tex>
  - <https://github.com/microsoft/ADBench>
  - <https://raw.githubusercontent.com/rjhogan/Adept-2/HEAD/README.md>
  - <https://raw.githubusercontent.com/rjhogan/Adept-2/HEAD/ChangeLog>
  - <https://github.com/rjhogan/Adept-2>
  - <https://github.com/rjhogan/Adept-2/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/rjhogan/Adept-2/HEAD/README.md>
  - <https://raw.githubusercontent.com/rjhogan/Adept-2/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/rjhogan/Adept-2/HEAD/NEWS>
  - <https://raw.githubusercontent.com/rjhogan/Adept-2/HEAD/configure.ac>
  - <https://raw.githubusercontent.com/rjhogan/Adept-2/HEAD/COPYING>
  - <https://raw.githubusercontent.com/rjhogan/Adept-2/HEAD/include/adept.h>
  - <https://raw.githubusercontent.com/rjhogan/Adept-2/HEAD/include/adept/base.h>
  - <https://raw.githubusercontent.com/rjhogan/Adept-2/HEAD/include/adept/Stack.h>
  - <https://raw.githubusercontent.com/rjhogan/Adept-2/HEAD/include/adept/exception.h>
  - <https://raw.githubusercontent.com/rjhogan/Adept-2/HEAD/include/adept_optimize.h>
  - <https://github.com/rjhogan/Adept-2>
  - <https://github.com/rjhogan/Adept-2/issues?q=is%3Aissue>
  - <https://github.com/rjhogan/Adept-2/issues/36>
  - <https://github.com/rjhogan/Adept-2/issues/37>
  - <https://raw.githubusercontent.com/auto-differentiation/ad-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/microsoft/ADBench/master/Documents/ms.tex>
  - http://www.met.reading.ac.uk/clouds/adept/adept_documentation.pdf (403, not read)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/rjhogan/adept-2`) · [data/wave8/enrich/raw/github_com_rjhogan_adept_2.json](../../../data/wave8/enrich/raw/github_com_rjhogan_adept_2.json) (enrichment confidence 0.75)

</details>
