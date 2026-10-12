# SPC5 (block-based SpMV kernels for AVX-512 and ARM SVE)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `MIT` · 🔴 abandoned

> Single-header block-based SpMV kernels for AVX-512 and 512-bit SVE; median 1.2-1.5x over sequential MKL CSR SpMV.

| | |
|---|---|
| **Beats** | Intel MKL CSR SpMV (sequential column of the results CSV) |
| **Claimed result** | From results/results-avx-2.csv, taking the best of the four SPC5 sequential kernels per matrix against the MKL CSR column, rows without manual horizontal sum (derived from page data): median 1.23x in double and 1.49x in float, geometric mean 1.18x and 1.45x, SPC5 ahead on 16 of 23 matrices in double and 17 of 23 in float, up to 1.90x (double) and 3.00x (float), but slower on others (worst 0.45x double, 0.41x float). The MHSUM=ON build gives similar figures (double median 1.24x, float median 1.64x, max 3.12x). |
| **Workload** | Sequential SpMV y=Ax over 23 SuiteSparse matrices in double and float on AVX-512, SPC5 kernels 1rVc/2rVc/4rVc/8rVc compared with MKL CSR, in GFlop/s. |
| **Metric** | throughput |
| **Hardware** | PlaFRIM 'bora' Intel Cascade Lake nodes (SLURM constraint bora&intel&cascadelake, 36 CPUs per task); exact CPU model not stated |
| **Compiler and flags** | g++ 11.2.0 with MKL 2022.0.2 (from jobs-plafrim.sh); CMake -DCMAKE_BUILD_TYPE=RELEASE -DUSE_AVX512=ON -DCPU=CNL; OpenMP with OMP_PROC_BIND=true |
| **Adoption** | 6 stars; GitHub mirror of gitlab.inria.fr/bramas/spc5 |
| **Last commit** | 2023-07-25 |
| **Links** | [repository](https://github.com/berenger-eu/spc5) · [benchmark](https://raw.githubusercontent.com/berenger-eu/spc5/HEAD/results/results-avx-2.csv) |

## Verdict

On PlaFRIM Cascade Lake nodes (exact CPU model not given), g++ 11.2.0 with MKL 2022.0.2 sequential, the best of SPC5's four sequential kernels per matrix beat MKL's legacy mkl_cspblas_?csrgemv CSR SpMV by a median 1.23x in double and 1.49x in float over 23 SuiteSparse matrices, up to 1.90x and 3.00x, but lost on 7 and 6 matrices respectively (derived from page data, results-avx-2.csv). The baseline is MKL's deprecated legacy CSR routine, not the inspector-executor mkl_sparse_?_mv with mkl_sparse_optimize, and the A64FX CSV has no Arm Performance Libraries column, only a scalar CSR loop.

## Use it when

- Repeated SpMV with the same matrix (iterative solvers, power iterations) on AVX-512 x86 (Skylake-SP/Cascade Lake class) where the CSR-to-SPC5 conversion, about 40-55 SpMVs' worth of time on one measured matrix, is amortised.
- Matrices whose nonzeros cluster in short column runs within rows or neighbouring rows (FEM, structured or banded patterns), where blocks hold several values each; the shipped CSV shows the 2rVc and 4rVc kernels winning on 19 of 23 matrices in double.
- A64FX (512-bit SVE) machines with no tuned vendor SpMV at hand: on the 23-matrix A64FX run the best SPC5 kernel is a median 2.9x (double) and 3.45x (float) over a plain scalar CSR loop (derived from page data, results-arm-8.csv).
- Projects that want to vendor a small MIT kernel rather than link MKL: one header plus farm_sve.h for the SVE-on-x86 emulation path.

## Skip it when

- One-shot or few-shot SpMV: conversion costs tens of multiplies, and MKL beat the best SPC5 kernel on some matrices outright (worst ratios 0.45x double, 0.41x float in the shipped CSV).
- Matrices with scattered single nonzeros per row (graph-like, power-law), where each block carries one value and the per-block header and x load dominate.
- CPUs without AVX-512 (AVX2-only x86, AMD before Zen 4, Apple and other NEON-only ARM) or SVE vectors narrower than 512 bits: the code hard-codes 512-bit vectors (ValPerVec = 512/(8\*sizeof(T)); SVE kernels build 8-lane double masks), so 128/256-bit SVE cores such as Graviton or Neoverse are not a documented target and would likely need code changes.
- Matrices with more than 2^31 nonzeros or rows: all indices and counts are int.
- Codebases needing a maintained library with tests, CI or an issue tracker: the GitHub mirror's last commit is 2023-07-25 and it has 6 stars.

## How it is fast

Each block stores one starting column (int) plus a per-row bitmask (8 bits for double, 16 for float) of which of the next vector-width columns are nonzero, and the values are stored packed without zero padding. The AVX-512 kernel does an unaligned load of 8 (double) or 16 (float) x values at the block's column and a masked expand-load (_mm512_maskz_expandloadu_pd) that scatters the packed values into the lanes the mask names, then one FMA per row per block and popcount(mask) to advance the value pointer; the SVE kernel instead compacts x with svcompact to line up with the packed values. Multi-row blocks reuse the same x load across rows. Optional MHSUM does hand-written horizontal reductions of the 2/4/8 row accumulators, and FACTOLOAD (SVE) loads x once for the whole block.

## Compared with alternatives

Pick SPC5 over CSR5 or merge-spmv when the target is AVX-512 or A64FX, the matrix has locally clustered nonzeros, and you want an MIT header you can vendor; pick merge-spmv or CVR for irregular, scale-free matrices where load balance, not vectorisation of short runs, is the bottleneck, and ALBUS or CSR5 if you also need GPU or non-AVX-512 targets.

## Integration

| | |
|---|---|
| **Form** | header-only (src/spc5.hpp, plus src/farm_sve.h for the x86 SVE emulation path); not a true multi-TU header, see gotchas |
| **Dependencies** | none for the kernels; OpenMP optional for the parallel kernels; Intel MKL or Arm Performance Libraries only for the comparison example |
| **Minimum toolchain** | C++17 (CMake sets CMAKE_CXX_STANDARD 17); the published runs used g++ 11.2.0 on x86 and gcc 10.3.0 on A64FX; AVX-512 flags -mavx512f -mavx512cd -mavx512vl -mavx512bw -mavx512dq (plus vbmi/ifma for CPU=CNL); SVE needs -march=armv8.2-a+sve |
| **Platforms** | x86-64 with AVX-512 (define USE_AVX512); aarch64 with 512-bit SVE (A64FX); on x86 without USE_AVX512 it builds the SVE code through FARM emulation, which is for testing, not speed |
| **Thread safety** | not documented; SPC5_Spmv takes the matrix by const reference and writes only y, and the OpenMP path gives each thread its own copy of its row range and y buffer before merging |
| **Drop-in for the baseline** | partial — replaces an MKL CSR SpMV call only after you convert to SPC5Mat (int indices, its own CSR loader) and pad x and y; computes y += A\*x rather than MKL csrgemv's y = A\*x |

## Gotchas

- Conversion is in place: CSR_to_SPC5_\*(&mat) overwrites the CSR's values and row pointer, so keep a copy if you still need CSR.
- The kernels are defined in the header as non-inline functions (core_SPC5_\*_Spmv_double/float, hsum_stor_\*, SPC5_opti_merge_\*), so including spc5.hpp in more than one translation unit should give duplicate-symbol link errors; include it in one .cpp and expose your own wrapper.
- The scalar reference path for multi-row formats indexes the block row pointer with the row number (core_SPC5_rVc_Spmv_scalar uses mat.rowsSize[idxRow] while conversion fills rowsSize per block row), and several asserts use mat-&gt;format on a reference, which only compiles when NDEBUG removes them; use the vector kernels, which the example checks against CSR.
- The OpenMP split copies each thread's slice of values and block headers into per-thread buffers, so the parallel path holds roughly a second copy of the matrix; SPC5_find_best's cubic predictor only considers 1rVc, 2rVc and 4rVc and uses one fixed set of fitted coefficients for every CPU.

## Known shortcomings

- No CPU model; conversion to the SPC5 format costs about 40-55 SpMVs.
- MKL baseline is the legacy mkl_cspblas_?csrgemv, not inspector-executor. Header defines non-inline kernels, so including it in 2+ translation units gives link errors. Scalar multi-row path indexes rowsSize by row instead of block-row (bug). Asserts on mat-&gt;format compile only with NDEBUG. Hard-coded 512-bit vectors, likely wrong on 128/256-bit SVE. A64FX CSV has no ARMPL column, scalar CSR only.

## Caveats and trade-offs

The best kernel is picked per matrix after the fact, which flatters SPC5 (the library ships a performance predictor, but the ratios above use the measured best). The CSV has an MKL column only for sequential runs; parallel SPC5 columns have no MKL counterpart. Conversion is costly: on CO (double) the raw log shows SPC5 conversion of 0.39-0.46 s against 0.09 s for MKL CSR, while 16 timed SpMVs take 0.13-0.19 s, so a conversion costs roughly 40-55 SpMVs (derived from page data), and MKL (1.89 GFlop/s) beats the best SPC5 kernel (1.70) on that matrix. The CSV is the 2023 data of the 2024 ComSIS paper, not the 2018 PeerJ CS paper. CPU class only (PlaFRIM bora Cascade Lake nodes), no model. The GitHub repo is a mirror of gitlab.inria.fr/bramas/spc5, which could not be checked (blocked), so the official repo may be newer than the mirror's 2023-07-25 last commit.

Needs a conversion from CSR to SPC5's block formats; AVX-512 or ARM SVE only (SVE emulated on x86 through FARM); C++17; compact code meant to be copied (spc5.hpp).

## Maintenance

GitHub mirror of gitlab.inria.fr/bramas/spc5 with its last commit on 2023-07-25 (the GitLab original could not be checked), so treat it as research code that is finished rather than maintained; MIT-licensed and compact enough to copy.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** results/results-avx-2.csv has an MKL CSR column beside the four SPC5 kernels, and the README labels it 'results for the paper & avx512', i.e. the data of the peer-reviewed SPC5 SVE/AVX-512 paper (Regnault and Bramas, Computer Science and Information Systems 21(1):203-221, 2024, per search results; comsis.org is blocked so the paper was not opened). Code (load_mm_and_compare, jobs-plafrim.sh), g++ 11.2.0, MKL 2022.0.2 and CMake flags are public, but no exact CPU model is given, so not A.
- **Verifier notes:** Recomputed every ratio from the CSV (92 rows: 23 matrices x double/float x hsum yes/no) and they match the record. Repo page: MIT, 6 stars, 2 forks, 108 commits, mirror of the Inria GitLab; latest commit 2023-07-25 ('update readme'). The tier stays B because the CSV is the data of a peer-reviewed 2024 paper, not because of the 2018 PeerJ paper.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/berenger-eu/spc5/HEAD/results/results-avx-2.csv>
  - <https://raw.githubusercontent.com/berenger-eu/spc5/HEAD/README.md>
  - <https://raw.githubusercontent.com/berenger-eu/spc5/HEAD/jobs-plafrim.sh>
  - <https://raw.githubusercontent.com/berenger-eu/spc5/HEAD/results/results-avx-2/res_CO_nohsum_double.txt>
  - <https://github.com/berenger-eu/spc5/tree/master/results/results-avx-2>
  - <https://github.com/berenger-eu/spc5>
  - <https://github.com/berenger-eu/spc5/commits>
- **Sources the enricher read:**
  - <https://github.com/berenger-eu/spc5>
  - <https://github.com/berenger-eu/spc5/tree/master/src>
  - <https://github.com/berenger-eu/spc5/tree/master/examples>
  - <https://raw.githubusercontent.com/berenger-eu/spc5/HEAD/README.md>
  - <https://raw.githubusercontent.com/berenger-eu/spc5/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/berenger-eu/spc5/HEAD/LICENCE>
  - <https://raw.githubusercontent.com/berenger-eu/spc5/HEAD/src/spc5.hpp>
  - <https://raw.githubusercontent.com/berenger-eu/spc5/HEAD/examples/load_mm_and_compare.cpp>
  - <https://raw.githubusercontent.com/berenger-eu/spc5/HEAD/jobs-plafrim.sh>
  - <https://raw.githubusercontent.com/berenger-eu/spc5/HEAD/jobs-afx64.sh>
  - <https://raw.githubusercontent.com/berenger-eu/spc5/HEAD/results/results-avx-2.csv>
  - <https://raw.githubusercontent.com/berenger-eu/spc5/HEAD/results/results-arm-8.csv>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/berenger-eu/spc5`) · [data/wave8/enrich/raw/github_com_berenger_eu_spc5.json](../../../data/wave8/enrich/raw/github_com_berenger_eu_spc5.json) (enrichment confidence 0.75)

</details>
