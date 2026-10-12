# GLU (GPU-accelerated sparse LU solver for circuit simulation)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `BSD-3-Clause` · 🟢 active

> CUDA sparse LU numeric factorization for circuit matrices; papers report 19.56x over KLU (numeric phase only, float32).

| | |
|---|---|
| **Beats** | KLU and UMFPACK (SuiteSparse) |
| **Claimed result** | TVLSI 2016 (GLU 1.0): on typical UFL circuit matrices about 19.56x over KLU and 47.13x over UMFPACK (also 5.71x / 1.46x over single- / 16-threaded PARDISO and 1.47x over a GPU left-looking solver); on general UFL matrices 39.39x over KLU and 24.04x over UMFPACK (geometric mean). Times are numeric factorization only, excluding preprocessing and symbolic analysis. GLU3.0 (IEEE D&T 2020, docs/Peng_DT_2020.pdf Table I): 3.51x arithmetic / 2.81x geometric mean over 32-thread NICSLU on 15 circuit matrices, numeric factorization time. |
| **Workload** | Sparse LU numeric factorization of circuit-simulation and general matrices from the University of Florida (SuiteSparse) collection plus self-generated RLC mesh networks, GPU versus CPU direct solvers (KLU 1.2.0, UMFPACK 5.6.2, PARDISO 5.0.0); preprocessing and symbolic analysis excluded from timings. |
| **Metric** | latency |
| **Hardware** | TVLSI 2016: NVIDIA Tesla K40 (all GPU results), host with two 8-core Xeon E5-2670 and 64 GB DDR3-1600; GLU3.0 paper: NVIDIA GTX TITAN X (Maxwell) with Xeon E5-2698 v3 and 128 GB |
| **Compiler and flags** | TVLSI 2016: CUDA 5.0, compiler flags not stated; GLU3.0 paper: C++ and CUDA C compiled with -O3 |
| **Adoption** | 47 stars, 12 forks |
| **Last commit** | 2026-07-04 |
| **Links** | [repository](https://github.com/sheldonucr/GLU_public) · [benchmark](https://github.com/sheldonucr/GLU_public/blob/master/docs/He_TVLSI_15.pdf) |

## Verdict

TVLSI 2016 (GLU 1.0, PDF in docs/): numeric factorization time only, excluding preprocessing and symbolic analysis, on a Tesla K40 (CUDA 5.0) against CPU solvers on two 8-core Xeon E5-2670: 19.56x over KLU 1.2.0 and 47.13x over UMFPACK 5.6.2 on typical UFL circuit matrices, 39.39x and 24.04x on general matrices. GLU3.0 (IEEE D&T 2020, GTX TITAN X, -O3, float32): numeric factorization including memory copies averages 2.81x geometric mean (3.51x arithmetic) faster than 32-thread NICSLU on 15 circuit matrices, with the larger CPU preprocessing and symbolic times reported separately; neither paper measured the current repo code.

## Use it when

- Large, low-fill circuit-simulation matrices (tens of thousands to millions of rows) on an NVIDIA GPU where numeric factorization dominates: the GLU3.0 paper measured 2.9x to 10.5x over 32-thread NICSLU on ASIC_320ks, ASIC_680ks and G3_circuit.
- Research or prototyping of GPU LU where you will edit the C++/CUDA to reuse one symbolic analysis across many Newton-iteration refactorizations, since the shipped CLI and pyglu redo it every call.
- Python code that wants a GPU splu/spsolve with a SciPy-like call and can live with float32 accuracy.
- Matrices whose CPU factorization is slowed by denormal values (barrier2-11 in the TVLSI paper).
- When you need modifiable source under a permissive license: the GLU code is BSD-3-Clause (the bundled NICSLU is LGPL-2.1).

## Skip it when

- When you need double precision: REAL is typedef float, inputs are cast to float32, the CPU triangular solves run in float32 with no iterative refinement, and issue #2 reported a log-determinant differing from MATLAB at about 1e-9 relative on the 4,960-row add32 example.
- One-shot solves: CPU preprocessing and symbolic time dwarfs the GPU numeric time (9,729 ms vs 878 ms on G3_circuit, 7,241 ms vs 845 ms on Raj1 in the GLU3.0 paper's Table I), and pyglu repeats it on every splu call.
- Small circuits such as circuit_2 and rajat15, where the TVLSI paper says GLU is slower than the CPU solvers; on Raj1 and rajat20 the GLU3.0 numeric time only ties 32-thread NICSLU (0.98x, 1.02x), and on general matrices GLU 1.0 was only 1.12x over 16-thread PARDISO.
- Matrices that need dynamic partial pivoting: the GPU phase does no pivoting and relies on the static MC64-style permutation, plus optional perturbation of tiny pivots to 3.45e-4 times the 1-norm of A (-p / perturb=True).
- Matrices whose nnz approaches 2^32 or whose L+U factors exceed GPU memory (32-bit unsigned indices, issue #3 open), complex-valued systems (issue #5 open), and non-NVIDIA GPUs or non-x86 hosts (NICSLU is built with -msse2).

## How it is fast

A hybrid right-looking column algorithm: symbolic analysis predicts the L+U pattern and groups columns into dependency-free levels (with GLU2.0's double-U dependency check, relaxed in 3.0), so all columns of a level are factorized at once and their submatrix updates are applied with atomicAdd. GLU3.0 adapts the kernel shape to each level: more than 896 columns use 2 warps per block, more than 448 use 4, more than 16 use 32, and the last 16 or fewer columns run as single-column kernels across 16 CUDA streams with 1024 threads each. Values are float32 because the Maxwell GPU used for the paper had no FP64 atomics; the paper expects FP64 to be about 30 percent slower. The TVLSI paper notes part of its large speedups (up to 530x over KLU on mc2depi) comes from denormal numbers that slow the CPU solvers down.

## Compared with alternatives

NICSLU (1.87x over KLU, CPU) is the stronger choice for one-off solves: the GLU3.0 paper puts GLU's numeric phase at 2.81x geometric mean over 32-thread NICSLU, but GLU's CPU preprocessing and symbolic time alone often exceeds NICSLU's whole numeric factorization (7,241 ms vs 825 ms on Raj1). CKTSO-GPU claims 13.29x geometric mean refactorization over KLU 1.3.9 on the same circuit workload. Pick GLU when you want BSD-3-Clause GPU source to modify or a SciPy-style Python entry point, and float32 accuracy is acceptable.

## Integration

| | |
|---|---|
| **Form** | source-drop: src/Makefile builds the lu_cmd executable against bundled NICSLU static libraries; setup.py builds the pyglu Python extension |
| **Dependencies** | CUDA toolkit (nvcc, cudart), bundled NICSLU (LGPL-2.1), pthread, libm, librt; pyglu adds Python &gt;= 3.9, pybind11 &gt;= 2.11, NumPy &gt;= 1.22 and optional SciPy &gt;= 1.9 |
| **Minimum toolchain** | C++11 (g++ -std=c++11 -O3, nvcc -O3 -std=c++11); minimum CUDA version not documented (the TVLSI work used CUDA 5.0) |
| **Platforms** | Linux x86-64 with one NVIDIA GPU; the build passes no -arch flag, so nvcc's default target applies; LUonDevice always uses device 0 |
| **Thread safety** | Not documented; each LUonDevice call allocates and frees its own device buffers on device 0, and memory sizing assumes it is the only user of the GPU |
| **Drop-in for the baseline** | partial — pyglu mirrors scipy.sparse.linalg.splu/spsolve (float64 in and out, float32 inside), but there is no KLU- or UMFPACK-style C API with separate analyze, factor, refactor and solve calls |

## Gotchas

- LUonDevice sizes its dense scratch buffer (tmpMem, one n-length float column per in-flight column) to fit all free GPU memory except 4 GB, or half the free memory when less than 4 GB is free, so a second process or factorization on the same GPU can fail (inferred from numeric.cu).
- Numerical failures can pass silently: pyglu scans the factors for NaN/Inf only when a CUDA error message was produced, and the NaN check in numeric.cu sits behind GLU_DEBUG, which the Makefile passes only to g++, not to nvcc (inferred from the source). Submatrix updates use float atomicAdd, so results are not bit-reproducible run to run.
- Issue #6 (open since May 2023): a matrix written row-wise (CSR) to .mtx gave wrong solutions, while the same matrix in CSC matched SciPy; feed CSC data.
- The February 2026 fixes (a __syncthreads() on a divergent path that could deadlock, unchecked CUDA calls, unsafe scratch sizing) mean pre-2026 checkouts, which the papers measured, can hang or mis-size memory; use current master.

## Known shortcomings

- The TVLSI 2016 paper (docs/He_TVLSI_15.pdf in the repo) times numeric factorization only and measured GLU 1.0, not the GLU 3.0 code now in the repo (float32, 2.81x geomean vs NICSLU). Feb 2026 fixes addressed a __syncthreads deadlock. The repo bundles NICSLU under LGPL.
- float32 only (REAL is float, CPU triangular solve in float, no refinement). The CPU preprocess plus symbolic phase is far slower than the GPU numeric phase (G3_circuit 9,729 ms vs 878 ms; Raj1 7,241 ms vs 845 ms; D&T Table I); Raj1 0.98x and rajat20 1.02x vs 32-thread NICSLU. No refactorization API; pyglu redoes symbolic analysis on every splu; tmpMem takes all free GPU memory minus 4 GB; the NaN check is compiled out under nvcc. Open issues #3 (nnz is 32-bit) and #6 (CSR .mtx gives wrong results).

## Caveats and trade-offs

The 19.56x / 47.13x figures are from the TVLSI 2016 GLU 1.0 paper (docs/He_TVLSI_15.pdf); baselines are old (KLU 1.2.0, UMFPACK 5.6.2, PARDISO 5.0.0) and timings cover numeric factorization only, so symbolic analysis and preprocessing (where KLU is cheap) are excluded. GLU is slower than the CPU solvers on very small circuits (circuit_2, rajat15), and on the self-generated RLC meshes 16-threaded PARDISO is the best CPU solver. The repo now holds GLU3.0, which the 2020 paper measured in single precision against 32-thread NICSLU (2.81x geometric mean); pyglu also runs float32 on the GPU, so precision differs from the double-precision CPU baselines. Recent commits (Feb 2026) fixed a CUDA __syncthreads() deadlock on a divergent path and unchecked CUDA calls, so published numbers were measured on code with those issues. The repo bundles NICSLU (src/nicslu) under LGPL-2.1-or-later alongside the BSD-3-Clause GLU code. README has no benchmark numbers.

Needs CUDA (nvcc); README says the solver runs in single-precision float32 on the GPU, with float64 inputs/outputs converted at the boundary; CSC input; Python bindings (pyglu) and scipy-style splu wrapper; aimed at low-fill circuit matrices.

## Maintenance

UC Riverside research code that sat dormant from 2020 to 2026, then got Codex-assisted bug fixes (Feb 2026), pyglu bindings (Mar 2026) and a GitHub Pages site (Jul 2026); 12 commits, no CI tests (the only workflow publishes Pages), 5 open issues, BSD-3-Clause GLU code bundling LGPL-2.1 NICSLU.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now B.
- **Tier reason:** Upgraded from C: the peer-reviewed TVLSI 2016 paper is checked into the repo (docs/He_TVLSI_15.pdf) and its abstract and Section IV state 19.56x over KLU 1.2.0 and 47.13x over UMFPACK 5.6.2 on UFL circuit matrices (numeric factorization only, K40 GPU, 2x Xeon E5-2670 host, CUDA 5.0). Not A: compiler flags are not stated, the baseline harness is not public, and the paper measured GLU 1.0, not the GLU3.0 code now in the repo.
- **Verifier notes:** Found the TVLSI 2016 and GLU3.0 (D&T 2020) papers as PDFs in docs/ and confirmed the numbers there. Metadata: BSD-3-Clause (LICENSE.txt), 47 stars, 12 forks, last commit 2026-07-04 on master, so active.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/sheldonucr/GLU_public>
  - <https://github.com/sheldonucr/GLU_public/commits>
  - <https://github.com/sheldonucr/GLU_public/tree/master/docs>
  - <https://github.com/sheldonucr/GLU_public/tree/master/src/nicslu>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/HEAD/README.md>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/LICENSE.txt>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/docs/He_TVLSI_15.pdf>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/docs/tvlsi_gpu_lu14.pdf>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/docs/Peng_DT_2020.pdf>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/docs/Peng_GLU3.0_2019.pdf>
- **Sources the enricher read:**
  - <https://github.com/sheldonucr/GLU_public>
  - <https://github.com/sheldonucr/GLU_public/commits/master>
  - <https://github.com/sheldonucr/GLU_public/tree/master/src>
  - <https://github.com/sheldonucr/GLU_public/tree/master/.github/workflows>
  - <https://github.com/sheldonucr/GLU_public/issues?q=is%3Aissue>
  - <https://github.com/sheldonucr/GLU_public/issues/2>
  - <https://github.com/sheldonucr/GLU_public/issues/3>
  - <https://github.com/sheldonucr/GLU_public/issues/6>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/HEAD/README.md>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/CLAUDE.md>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/setup.py>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/pyproject.toml>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/src/Makefile>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/src/numeric.cu>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/src/symbolic.cc>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/src/lu_cmd.cpp>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/src/glu_binding.cpp>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/src/preprocess/preprocess.c>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/src/preprocess/preprocess_arrays.c>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/include/type.h>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/include/symbolic.h>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/docs/He_TVLSI_15.pdf>
  - <https://raw.githubusercontent.com/sheldonucr/GLU_public/master/docs/Peng_DT_2020.pdf>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/sheldonucr/glu_public`) · [data/wave8/enrich/raw/github_com_sheldonucr_glu_public.json](../../../data/wave8/enrich/raw/github_com_sheldonucr_glu_public.json) (enrichment confidence 0.75)

</details>
