# XAD

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `AGPL-3.0` · 🟢 active

> Operator-overloading C++ AD library whose adjoint tape beats Adept 2 and CppAD by 1.1-2.3x on quant-finance gradients.

| | |
|---|---|
| **Beats** | CppAD, Adept 2, autodiff (C++ AD libraries), finite differences |
| **Claimed result** | Open-source XAD tape mode (gradient time) vs Adept 2 / CppAD: Heston MC 40 ms vs 91 / 268 ms; SABR 8.4 ms vs 19 / 32 ms (autodiff 38 ms); XVA CVA 2.6 s vs 7.1 / 8.0 s; LIBOR swaption 1.00 s vs 1.15 / 4.57 s. The page says 'fastest tape library on every benchmark, by margins of \~1.1x (LIBOR vs Adept) up to 2.3x (Heston vs Adept)'. The commercial XAD-Codegen backend is 2x-5x faster than tape mode (Heston 21 ms, SABR 4.9 ms, XVA 0.57 s, LIBOR 0.31 s). Adjoint is \~70x faster than finite differences on LIBOR (161 inputs). |
| **Workload** | Gradient computation (adjoint AD) on four quant-finance kernels: Heston Monte Carlo (10K paths), SABR calibration, XVA CVA, LIBOR swaption. |
| **Metric** | throughput |
| **Hardware** | Intel Xeon Platinum 8488C |
| **Compiler and flags** | GCC 13.3, -O3 -mavx2 -mfma, Ubuntu 24.04 |
| **Adoption** | 430 stars |
| **Last commit** | 2026-09-08 |
| **Links** | [repository](https://github.com/auto-differentiation/XAD) · [benchmark](https://github.com/auto-differentiation/ad-benchmarks) |

## Verdict

In the vendor's ad-benchmarks repo (GCC 13.3, -O3 -mavx2 -mfma, Intel Xeon Platinum 8488C, Ubuntu 24.04, median of 10 iterations after warmup), open-source XAD tape-mode gradients took 40 ms (Heston MC), 8.4 ms (SABR), 2.6 s (XVA CVA) and 1.00 s (LIBOR swaption), against Adept 2 at 91 ms / 19 ms / 7.1 s / 1.15 s and CppAD at 268 ms / 32 ms / 8.0 s / 4.57 s. The commercial xad-codegen column (21 ms / 4.9 ms / 0.57 s / 0.31 s) cannot be reproduced from public code.

## Use it when

- Many-inputs/one-output gradients (risk sensitivities, calibration Jacobians) where finite differences cost O(N) primal runs; the vendor run shows about 70x over FD at 161 inputs
- Monte Carlo pricing and XVA-style workloads in existing double-based C++ code, including QuantLib (via QuantLibAAD)
- Projects that need higher-order derivatives, checkpointing for tape memory, or hooks for external (non-AD) functions
- Codebases already using Eigen that need AD through Eigen expressions
- AGPL-compatible projects, or teams willing to buy the commercial licence

## Skip it when

- Proprietary/closed-source distribution without a commercial licence: the library is AGPL-3.0
- If you expect the headline benchmark speeds for free: the fastest column is xad-codegen, a closed commercial add-on
- Small statically-known expression graphs where an expression-template-only library such as FastAD may be faster (not measured head-to-head here)
- Very long recordings on memory-tight machines: reverse-mode tapes grow with operation count unless you use checkpointing
- Tensor/ML-style workloads; XAD targets scalar operator-overloading AD, not batched tensor kernels

## How it is fast

Adjoint AD by operator overloading onto a tape (the benchmark repo labels XAD tape-based, like CppAD, while Adept 2 uses expression templates with stack recording); the internal tape layout is not documented in the pages read. An optional JIT backend interface supports record-once/replay-many for Monte Carlo; the commercial xad-codegen backend compiles the recorded graph to AVX2 native code and is 2-5x faster than the tape in the vendor's runs. Compile-time options trade speed for memory (XAD_REDUCED_MEMORY, XAD_TAPE_REUSE_SLOTS), force inlining (XAD_USE_STRONG_INLINE) or remove thread-local tape overhead (XAD_NO_THREADLOCAL).

## Compared with alternatives

Pick XAD over FastAD when you need a maintained, general-purpose AD with forward/reverse/higher-order modes, checkpointing, Eigen support and QuantLib integration; FastAD's own paper reports bigger margins over Adept on small expression benchmarks but is narrower in scope. The other siblings (DGEMM kernels, tinyBLAS, MNN, T-MAC, TCL, nanoinfer) are ML/linear-algebra kernels, not AD libraries.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none (Eigen optional; xad-codegen optional and commercial) |
| **Minimum toolchain** | C++11; GCC 7+, Clang 11+, Apple Clang 11+, Visual Studio 2019+; CMake 3.15.2+ |
| **Platforms** | Linux, macOS, Windows; x86-64 with SSE2/AVX/AVX2/AVX512 selectable via XAD_SIMD_OPTION (default AVX), Apple M1 option on macOS |
| **Thread safety** | Tapes are thread-local by default (one active tape per thread); XAD_NO_THREADLOCAL disables this for single-threaded use |
| **Drop-in for the baseline** | no |

## Gotchas

- Tape behaviour is fixed at build time through CMake options written into a generated Config.hpp; build your project and XAD with the same compiler and flags (the install guide warns about this)
- XAD_ALLOW_INT_CONVERSION is ON by default: real-to-int conversions compile silently and can drop dependencies from the derivative
- Moving from tape to xad-codegen requires rewriting data-dependent branches as xad::less(a,b).If(then,else) so the recorded graph is branch-free
- The benchmark harness pulls XAD, CppAD, Adept and autodiff from their main/master branches, so the numbers are not tied to fixed versions

## Known shortcomings

- Vendor-run benchmark (Xcelerit sells XAD-Codegen); original headline numbers came from the closed commercial Codegen backend; open AGPL tape mode is only \~1.1-2.3x faster than Adept.
- Benchmark harness pulls every library from main/master (numbers not tied to versions); XAD_ALLOW_INT_CONVERSION on by default can silently drop dependencies.

## Caveats and trade-offs

The benchmark repo (1 commit, 5 stars, MIT, (c) 2026 Xcelerit Computing Ltd) belongs to the vendor that sells XAD enterprise support and xad-codegen. The headline numbers are XAD-Codegen, a commercially licensed add-on that is not part of AGPL XAD; the open tape mode's margin is only \~1.1x-2.3x over Adept. Baselines are AD libraries (CppAD, Adept 2, autodiff), not oneDNN/XNNPACK/Eigen tensor. autodiff completed only SABR (forward dual mode). AGPL-3.0 is copyleft.

AGPL-3.0 copyleft (commercial license sold separately); tape-based reverse mode uses memory; native-code codegen backend is AVX2-targeted.

## Maintenance

Actively maintained (last commit September 2026) with a commercial backer (Xcelerit); usable as source under AGPL-3.0, with a paid licence for closed-source use and for xad-codegen.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** ad-benchmarks repo has public per-library benchmark code (xad/, cppad/, adept/, autodiff/, src/) and states GCC 13.3, -O3 -mavx2 -mfma, Intel Xeon Platinum 8488C, Ubuntu 24.04; the open-source XAD tape mode beats CppAD, Adept 2 and autodiff on all four kernels. The XAD-Codegen column needs the commercially licensed xad-codegen, so that part cannot be reproduced from public code.
- **Verifier notes:** The numbers match the ad-benchmarks README. The record attributed XAD-Codegen numbers (commercial add-on) to the AGPL library, and its SABR 'competitors 8.4-38 ms' counted XAD's own tape time as a competitor; claimed_speedup is rewritten to lead with the open tape mode. Consider recording a shortcoming: vendor-run benchmark, and the headline backend is closed and commercial.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/auto-differentiation/XAD>
  - <https://github.com/auto-differentiation/XAD/commits>
  - <https://raw.githubusercontent.com/auto-differentiation/XAD/HEAD/README.md>
  - <https://raw.githubusercontent.com/auto-differentiation/XAD/HEAD/LICENSE.md>
  - <https://github.com/auto-differentiation/ad-benchmarks>
  - <https://raw.githubusercontent.com/auto-differentiation/ad-benchmarks/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/auto-differentiation/XAD/HEAD/README.md>
  - <https://raw.githubusercontent.com/auto-differentiation/XAD/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/auto-differentiation/XAD/HEAD/cmake/XADSetupOptions.cmake>
  - <https://auto-differentiation.github.io/installation/cxx/>
  - <https://raw.githubusercontent.com/auto-differentiation/ad-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/auto-differentiation/ad-benchmarks/HEAD/CMakeLists.txt>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/auto-differentiation/xad`) · [data/wave8/enrich/raw/github_com_auto_differentiation_xad.json](../../../data/wave8/enrich/raw/github_com_auto_differentiation_xad.json) (enrichment confidence 0.75)

</details>
