# cudaFoam (cudaPCG: GPU PCG pressure-solver plugin for OpenFOAM)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `GPL-3.0` · 🟢 active

> OpenFOAM 12 plugin running the pressure-equation PCG on an NVIDIA GPU; edges CPU GAMG, 5.6x over CPU PCG-DIC.

| | |
|---|---|
| **Beats** | OpenFOAM 12 CPU GAMG and CPU PCG-DIC (single rank) |
| **Claimed result** | vs CPU GAMG: 17.2 s -&gt; 13.3 s (1.3x) at 305,625 cells and 95.0 s -&gt; 88.3 s (1.08x) at 1,222,500 cells. vs CPU PCG-DIC: 56.0 s -&gt; 13.3 s at 305,625 cells, 498 s -&gt; 88.3 s (5.6x) at 1,222,500 cells, and 93.1 s -&gt; 65.1 s at 12,225 cells (1000 steps; no GAMG run at that size). |
| **Workload** | OpenFOAM 12 incompressibleFluid pitzDaily tutorial scaled to 12,225 / 305,625 / 1,222,500 cells (1000 / 5 / 5 time steps); wall time of foamRun with the pressure equation solved by cudaPCG (cuSPARSE SpMV plus multicolor symmetric Gauss-Seidel preconditioner with FP32 sweeps) versus stock CPU GAMG and CPU PCG-DIC at identical tolerances. |
| **Metric** | latency |
| **Hardware** | AWS g5.xlarge (NVIDIA A10G GPU), single CPU rank (nProcs 1); CPU model not stated |
| **Compiler and flags** | nvcc -std=c++17 -O3 -arch=sm_86 --compiler-options -fPIC (cudaPCG/Allwmake, ARCH overridable), plugin linked with wmake; CUDA 12.x/13.x; OpenFOAM 12 build 12-86e126a7bc4d (log header); optimization flags of the OpenFOAM CPU baseline are not stated |
| **Adoption** | 1 star, 5 commits (repo created 2026-09-13) |
| **Last commit** | 2026-09-14 |
| **Links** | [repository](https://github.com/Lilkat002/cudafoam) · [benchmark](https://github.com/Lilkat002/cudafoam) |

## Verdict

One foamRun per configuration of the OpenFOAM 12 pitzDaily kEpsilon case on an AWS g5.xlarge (A10G GPU, one CPU rank, CPU model and OpenFOAM build flags not stated): whole-run ExecutionTime 13.15 s vs 17.13 s for CPU GAMG at 305,625 cells and 88.0 s vs 94.7 s at 1,222,500 cells over 5 steps (README rounds to 13.3/17.2 and 88.3/95.0), and 88.0 s vs 497.9 s for CPU PCG-DIC; times include the non-pressure equations. Per-step increments in the same logs show GAMG ahead over steps 3-5 at 1.22M cells (45.5 s vs 48.7 s, derived from page data), so the 1.08x lead rests on the first two steps and is within run-to-run noise.

## Use it when

- Single-rank incompressible OpenFOAM 12 cases where the symmetric pressure equation dominates run time and a recent NVIDIA GPU is available (measured on an AWS g5.xlarge with an A10G).
- Meshes of a few hundred thousand cells, where the measured lead over single-rank CPU GAMG was largest (13.15 s vs 17.13 s at 305,625 cells).
- Cases that currently run CPU PCG-DIC (for example because GAMG is unsuitable): about 4.2x at 306k cells (56.0 s vs 13.3 s) and 5.6x at 1.22M cells per the README table.
- Periodic cases with plain cyclic patches, which stay on the GPU (validated by the author on channel395).
- As a short, readable reference (about 900 lines in two source files) for writing your own GPU lduMatrix solver plugin.

## Skip it when

- Decomposed (MPI) runs: processor interfaces force the CPU PCG-DIC fallback, which is several times slower than the GAMG most parallel cases use.
- Asymmetric equations (U, k, epsilon, energy): it only registers as a symmetric-matrix solver.
- When CPU GAMG already runs on several cores: the only GAMG comparison is single rank, the lead at 1.22M cells is 1.08x from one 5-step run, and multi-rank GAMG was not benchmarked.
- Non-NVIDIA GPUs or tiny meshes (about 10k cells and below, which the README says are launch-latency bound); also AMI/non-conformal couplings, which always take the CPU path.
- Production runs that need a maintained, tested solver: single-author repo created 2026-09-13 with 5 commits, 1 star and no test suite in the tree.

## How it is fast

The LDU matrix is converted to CSR once (structure cached, values re-gathered per solve through a permutation kernel) and SpMV goes through cuSPARSE in FP64. The preconditioner is a multicolor symmetric Gauss-Seidel: a greedy graph coloring (2 colors on the pitzDaily meshes) turns each triangular sweep into one fully parallel kernel per color, with FP32 matrix values to halve memory traffic, replacing cuSPARSE level-scheduled triangular solves that the README says were slower than the CPU. All CG scalars stay on the device (block-reduce plus atomicAdd dot products, fused update-and-residual kernel), so the host syncs once per iteration on a 16-byte readback. The gain is GPU memory bandwidth, not algorithm: the logs show 2,700-4,100 iterations per pressure solve at 1.22M cells versus about 1,900-2,100 for CPU DIC-PCG and 5-70 for GAMG.

## Compared with alternatives

Ginkgo (usable from OpenFOAM through the OGL plugin, which has MPI support and CUDA/HIP/SYCL backends) and AMGCL bring AMG-class methods that cut iteration counts by orders of magnitude, which this plain PCG cannot; pick cudaFoam only when you want a zero-configuration, CUDA-only, two-file drop-in for a single-rank OpenFOAM 12 pressure solve.

## Integration

| | |
|---|---|
| **Form** | shared lib (OpenFOAM runtime-loaded plugin libcudaPCG.so, built by Allwmake: nvcc for cudaKernels.cu, then wmake) |
| **Dependencies** | OpenFOAM 12 (finiteVolume headers and library), CUDA runtime, cuSPARSE |
| **Minimum toolchain** | nvcc -std=c++17 -O3 with CUDA 12.x or 13.x; OpenFOAM 12 wmake (ESI v2412 compile-verified per README) |
| **Platforms** | Linux with an NVIDIA GPU; default -arch=sm_86 (Ampere), override with ARCH=sm_XX; Make/options hard-codes /usr/local/cuda include and lib64 paths; FP64 atomicAdd in the reductions needs sm_60 or newer (inferred from the code) |
| **Thread safety** | Not documented; the code keeps one file-static GPU context (struct Ctx, one stream and cuSPARSE handle) shared by all cudaPCG instances, so it is not re-entrant |
| **Drop-in for the baseline** | partial — selected in fvSolution exactly like GAMG or PCG with no OpenFOAM changes, but only for symmetric matrices on a single rank; anything else silently becomes CPU PCG-DIC after a one-time warning |

## Gotchas

- The GPU context is cached on (nCells, nFaces, number of cyclic couplings) only: alternating between symmetric matrices of different sizes (multi-region cases) redoes the host-side coloring and all cudaMalloc calls on every switch, and a topology change that keeps those counts would reuse stale CSR addressing (inferred from cudaKernels.cu).
- Any CUDA or cuSPARSE error calls exit(1), killing foamRun without an OpenFOAM FatalError and without falling back to the CPU solver.
- Dot products and residual sums use FP64 atomicAdd, so summation order varies between runs and iteration counts or final digits may not be bit-reproducible (inferred from the code).
- wmake does not track the nvcc-built cudaKernels.o; after editing the .cu file, delete libcudaPCG.so or touch cudaPCG.C (README). Set CUDAPCG_VERBOSE to see per-solve GPU/CPU path and CUDAPCG_FP64_PRECOND=1 for FP64 sweeps.

## Known shortcomings

- README rounds times up slightly versus the logs; margin over OpenFOAM GAMG is only 1.08x at 1.2M cells.
- One 5-step run per configuration; per-step log increments show CPU GAMG ahead over steps 3-5 at 1.22M cells (45.5 s vs 48.7 s, derived from page data), so the 1.08x lead comes from the first two steps and is within noise. GPU PCG needs 2,700-4,100 iterations per pressure solve against 1,900-2,100 for CPU DIC-PCG. The GPU context is one file-static struct cached only on (nCells, nFaces, nExtra), so it is not re-entrant; CUDA errors call exit(1).

## Caveats and trade-offs

Brand-new first-party repo with a single author; numbers are whole-case foamRun ExecutionTime (include non-pressure equations), not pressure-solve-only times. Margin over GAMG is small (1.08x at 1.2M cells); the large ratio is against CPU PCG-DIC, which is the weaker algorithm. Raw logs are in benchmark/results/: the tails of v4_huge_gpu.log (88.0046 s) and v4_huge_gamg.log (94.6959 s) differ slightly from the README's 88.3 s and 95.0 s. Pressure fields differ from the CPU reference by 0.017-0.06 percent of range on small/medium meshes and 0.56 percent at 1.2M cells (README says this is within GAMG-vs-PCG scatter). Baseline is OpenFOAM's solver, not one of SuiteSparse/Eigen sparse/PETSc. Benchmark mesh dicts and logs are public; CPU model and CPU baseline compile flags are not stated.

Symmetric matrices only (pressure/Laplacian-type equations); single rank and single GPU, otherwise it falls back to OpenFOAM's own PCG; requires an NVIDIA GPU with CUDA and OpenFOAM 12 (ESI v2412 compile-verified); GPL-3.0 because it builds against OpenFOAM; FP32 preconditioner sweeps with FP64 CG; GPU PCG needs far more iterations than GAMG.

## Maintenance

Brand-new single-author project (5 commits on 2026-09-13/14, 1 star); GPL-3.0 because it builds against OpenFOAM, small enough to audit and vendor, but validated only on the author's pitzDaily and channel395 runs.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table against stock OpenFOAM 12 CPU GAMG and PCG-DIC, backed by public mesh dicts and raw foamRun logs in benchmark/results/ (v4_\*_cpu/gamg/gpu.log, nProcs 1, build 12-86e126a7bc4d); nvcc flags are in cudaPCG/Allwmake, but the host CPU model and the OpenFOAM CPU build flags are not stated, so not A.
- **Verifier notes:** Logs checked: final ExecutionTime is 497.9 s (PCG-DIC), 94.70 s (GAMG), 88.00 s (GPU) at 1.22M cells; 55.9 / 17.13 / 13.15 s at 306k; 93.1 / 65.1 s at 12k. README rounds these slightly upward (95.0, 88.3, 17.2, 13.3); ratios are unchanged. The GPU run needs \~3000-4000 PCG iterations per pressure solve versus 10-70 for GAMG. Last commit 2026-09-14, 5 commits, 1 star, 0 forks, GPL-3.0.
- **Fields the verifier corrected:** `compiler_and_flags`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/Lilkat002/cudafoam>
  - <https://github.com/Lilkat002/cudafoam/commits>
  - <https://github.com/Lilkat002/cudafoam/tree/main/benchmark/results>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/README.md>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/cudaPCG/Allwmake>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/benchmark/results/v4_huge_gpu.log>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/benchmark/results/v4_huge_gamg.log>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/benchmark/results/v4_huge_cpu.log>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/benchmark/results/v4_pitzDailyBig_gpu.log>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/benchmark/results/v4_pitzDailyBig_gamg.log>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/benchmark/results/v4_pitzDailyBig_cpu.log>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/benchmark/results/v4_pitzDaily_gpu.log>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/benchmark/results/v4_pitzDaily_cpu.log>
- **Sources the enricher read:**
  - <https://github.com/Lilkat002/cudafoam>
  - <https://github.com/Lilkat002/cudafoam/commits>
  - <https://github.com/Lilkat002/cudafoam/tree/main/cudaPCG>
  - <https://github.com/Lilkat002/cudafoam/tree/main/benchmark/results>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/README.md>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/cudaPCG/Allwmake>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/cudaPCG/Make/files>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/cudaPCG/Make/options>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/cudaPCG/cudaPCG.H>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/cudaPCG/cudaPCG.C>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/cudaPCG/cudaKernels.cu>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/benchmark/results/v4_huge_gpu.log>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/benchmark/results/v4_huge_gamg.log>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/benchmark/results/v4_huge_cpu.log>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/benchmark/results/v4_pitzDailyBig_gpu.log>
  - <https://raw.githubusercontent.com/Lilkat002/cudafoam/HEAD/benchmark/results/v4_pitzDailyBig_gamg.log>
  - <https://github.com/hpsim/OGL>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/lilkat002/cudafoam`) · [data/wave8/enrich/raw/github_com_lilkat002_cudafoam.json](../../../data/wave8/enrich/raw/github_com_lilkat002_cudafoam.json) (enrichment confidence 0.75)

</details>
