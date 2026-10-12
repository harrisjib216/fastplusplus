# SpFFT (sparse-input 3D FFT)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `BSD-3-Clause` · 🟡 stale

> 3D FFT layer for sparse (spherical-cutoff) frequency data that skips empty columns before calling FFTW/MKL/cuFFT/rocFFT; no published speedup.

| | |
|---|---|
| **Beats** | FFTW / MKL and cuFFT / rocFFT dense 3D FFT (implied; no comparison is published; SpFFT itself calls these libraries for its 1D/2D sub-transforms) |
| **Claimed result** | none: no numbers or speedup claim appear in the README, docs/source details.rst, index.rst, examples.rst or tests/programs/benchmark.cpp |
| **Workload** | No benchmarked workload. Design target: 3D FFT of sparse frequency-domain data with spherical cutoff, as in plane-wave electronic-structure codes, with MPI slab and pencil decomposition and CUDA or ROCm backends. |
| **Metric** | other |
| **Adoption** | 56 stars, 16 forks; conda-forge package; listed as a required dependency ('domain-specific FFT library') in the SIRIUS README, the electronic-structure library used by Quantum ESPRESSO and CP2K |
| **Last commit** | 2025-07-25 |
| **Links** | [repository](https://github.com/eth-cscs/SpFFT) |

## Verdict

Nothing measured: the repository, its docs and its benchmark program make no speed claim and contain no comparison against FFTW, MKL, cuFFT or rocFFT. The only third-party numbers found (cuSpFFT README, RTX 4090, single precision, 2D full-output use) show SpFFT slower than dense cuFFT, which is outside SpFFT's sparse 3D design point.

## Use it when

- Plane-wave DFT or similar codes where frequency data is a sphere inside a cube, so most z-columns are empty (this is what SIRIUS, and through it Quantum ESPRESSO and CP2K, use it for).
- Repeated transforms of the same sparsity pattern, where the cost of building the Grid/Transform (FFTW planning, index setup) is amortized over many calls.
- MPI-distributed 3D grids that already use z-column ownership per rank, on CPU or on NVIDIA (CUDA 11+) or AMD (ROCm 5+) GPUs, with optional GPU-aware MPI.
- Codes that need one interface for host and GPU execution and C/Fortran bindings.

## Skip it when

- Dense frequency data or 2D problems: there is nothing to prune, and a third-party test (cuSpFFT course project, RTX 4090, single precision, full R2C output set) measured SpFFT at 0.74x, 0.41x and 0.17x the speed of plain dense cuFFT with 1.3-2.3x more device memory; it ran out of memory on a 52,329^2 case.
- When you need evidence of a speedup: the repo publishes no timings against FFTW, MKL or cuFFT, and tests/programs/benchmark.cpp times only SpFFT itself.
- Sparsity in the space domain (sparse inputs to a forward transform) or arbitrary non-column patterns: only frequency-side sparsity grouped into complete z-columns is supported.
- 1D FFTs, non-uniform FFTs, or sizes with large prime factors: it only does 3D transforms and inherits the backend's speed on sizes not of the form 2^a 3^b 5^c 7^d.
- Projects that need a multi-GPU single transform: each Grid/Transform is tied to one GPU.

## How it is fast

Pruned 3D FFT by dimension: on the host it runs the batched 1D z-transforms only over the z-columns that hold data (decompress, z-FFT, transpose), then the y-transforms only for x indices that own a column (Transform1DVerticalHost with uniqueXIndices), and full x-transforms last, so zero columns and empty y-lines are never touched. For R2C/C2R it exploits Hermitian symmetry so only half the columns (plus the non-redundant half of the x=0 plane) are needed. The z-to-xy redistribution is an MPI all-to-all (Alltoall, Alltoallv or Alltoallw variants, optionally exchanging doubles as floats to halve traffic), and Grid buffers are reused across transforms; all 1D/2D kernels are FFTW, MKL, ARMPL, NVPL, cuFFT or rocFFT plans, not SpFFT's own.

## Compared with alternatives

Pick SpFFT over heFFTe (dense distributed 3D FFT) when your frequency data is a plane-wave cutoff sphere and you want the empty columns skipped for you. cuSpFFT solves a different problem (binary-sparse 2D inputs on one GPU) and beat SpFFT only in an off-design test where SpFFT was given a full output set.

## Integration

| | |
|---|---|
| **Form** | shared lib (static with SPFFT_STATIC=ON); CMake build, conda-forge package |
| **Dependencies** | a library with the FFTW 3.x interface (FFTW3, Intel MKL, ARM Performance Libraries or NVPL); optional MPI, OpenMP, CUDA 11+ (cuFFT) or ROCm 5+ (rocFFT/hipFFT) |
| **Minimum toolchain** | C++17; GCC 7+, Clang 5+ or ICC 19+; CMake 3.18 (3.21 for ROCm) |
| **Platforms** | Linux HPC targets: x86-64 and Arm CPUs, NVIDIA and AMD GPUs; other platforms not documented |
| **Thread safety** | Grid/Transform creation is thread-safe only if no other FFTW calls run concurrently (and MPI_THREAD_MULTIPLE when distributed); execution is thread-safe when each thread uses its own Grid and Transform. Creation and execution are collective over all MPI ranks. |
| **Drop-in for the baseline** | partial: it calls FFTW/MKL/cuFFT/rocFFT underneath, but the caller must supply the sparse index triplets and use the Grid/Transform API, so it replaces a hand-rolled pruned 3D FFT rather than an fftw_plan_dft_3d call |

## Gotchas

- Index layout rules: all elements of one z-column must be on the same rank, R2C inputs need x in [0, n/2], and the docs say the order and rank distribution of z-columns strongly affects speed (continuous in y for host, in x for GPU).
- Normalization is only applied on forward transforms (1/(Nx\*Ny\*Nz)); backward is never scaled.
- Bug history in released versions: wrong results with 2 OpenMPI ranks (issue #51, labelled Bug/Wrong Results, closed January 2022), ROCm Release builds left debug device_synchronize() on (fixed in 1.1.0), C/Fortran multi-transform segfault (fixed in 1.1.1), and an array size mismatch for local transforms fixed in PR #65 (2025-07-25) after the last release v1.1.1.
- Creating Grids/Transforms inside an OpenMP parallel region crashed in FFTW planning (issue #32); create them outside the region.

## Known shortcomings

- No speed claim at all; it wraps FFTW/cuFFT. Kept as a required SIRIUS dependency. Post-v1.1.1 fix #65 (array size mismatch for local transforms) not yet released.
- The repo makes no speed claim; pruning covers the z-FFT over occupied columns and the y-FFT for occupied x only, while the GPU path runs a full 2D xy. The third-party cuSpFFT README (RTX 4090, single precision, 2D full output, off-design) puts SpFFT at 0.74x/0.41x/0.17x of dense cuFFT with 1.3-2.3x memory and OOM at 52,329^2. Issue #51: wrong results with 2 OpenMPI ranks (closed Jan 2022); ROCm Release builds carried debug syncs until 1.1.0; the post-v1.1.1 array fix (PR #65) is unreleased.

## Caveats and trade-offs

Tier D: no numeric comparison against any recognizable baseline and no stated speed claim. tests/programs/benchmark.cpp (CLI11 plus rt_graph timing, JSON output) runs only SpFFT transforms, with no FFTW, cuFFT or dense reference; README and docs/source/details.rst state no speed numbers. details.rst says the underlying computation is done by FFT libraries such as FFTW and cuFFT, so SpFFT is a sparse-aware decomposition layer on top of the baseline, not a replacement kernel; any gain comes from skipping work on empty z-columns and planes plus its MPI exchange schemes. Published performance data, if any (for example SIRIUS papers), is behind egress-blocked hosts (readthedocs, doi.org, arXiv) and was not checked. Notability: 56 stars, but SIRIUS lists it as a required dependency (verified in the SIRIUS README). The latest commit, 'fix array size mismatch for local transforms (#65)' on 2025-07-25, comes after the last release v1.1.1 (2025-01-19); the PR has no description, so whether released builds can mis-size buffers for local transforms is unknown. Last commit date read from the github.com commits page.

Not a new FFT kernel: the 1D transforms are done by FFTW, MKL or cuFFT underneath, and the gain comes from skipping z-columns that are all zero in frequency space and exploiting Hermitian symmetry for R2C and C2R. Needs a precomputed list of non-zero columns, sizes best of the form 2^a 3^b 5^c 7^d, optional MPI, OpenMP, CUDA 11+ or ROCm 5+; C++17, with C and Fortran interfaces; pre-allocated Grid objects are reused between transforms.

## Maintenance

Stale but maintained at a low rate: last release v1.1.1 (2025-01-19) and last commit 2025-07-25; BSD-3-Clause, packaged on conda-forge and a required dependency of SIRIUS, so it is exercised in production electronic-structure codes.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now D.
- **Tier reason:** No numbers and no comparison against FFTW, MKL or cuFFT in the README, docs/source/details.rst, index.rst or tests/programs/benchmark.cpp (which times only SpFFT transforms); not even a directional speed claim, so D.
- **Verifier notes:** Confirmed D with no speed claim at all; kept rather than rejected because it is a required dependency of SIRIUS (QE/CP2K backend). Shortcoming worth recording: unreleased post-v1.1.1 fix for an array size mismatch in local transforms (#65).
- **Fields the verifier corrected:** `baseline`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/eth-cscs/SpFFT>
  - <https://raw.githubusercontent.com/eth-cscs/SpFFT/master/README.md>
  - <https://github.com/eth-cscs/SpFFT/tree/master/docs/source>
  - <https://raw.githubusercontent.com/eth-cscs/SpFFT/master/docs/source/details.rst>
  - <https://raw.githubusercontent.com/eth-cscs/SpFFT/master/docs/source/index.rst>
  - <https://raw.githubusercontent.com/eth-cscs/SpFFT/master/tests/programs/benchmark.cpp>
  - <https://github.com/eth-cscs/SpFFT/commits/master>
  - <https://github.com/eth-cscs/SpFFT/pull/65>
  - <https://raw.githubusercontent.com/electronic-structure/SIRIUS/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/eth-cscs/SpFFT/master/README.md>
  - <https://raw.githubusercontent.com/eth-cscs/SpFFT/master/docs/source/details.rst>
  - <https://raw.githubusercontent.com/eth-cscs/SpFFT/master/docs/source/index.rst>
  - <https://raw.githubusercontent.com/eth-cscs/SpFFT/master/docs/source/installation.rst>
  - <https://raw.githubusercontent.com/eth-cscs/SpFFT/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/eth-cscs/SpFFT/master/include/spfft/grid.hpp>
  - <https://raw.githubusercontent.com/eth-cscs/SpFFT/master/include/spfft/transform.hpp>
  - <https://raw.githubusercontent.com/eth-cscs/SpFFT/master/tests/programs/benchmark.cpp>
  - <https://raw.githubusercontent.com/eth-cscs/SpFFT/master/src/execution/execution_host.cpp>
  - <https://raw.githubusercontent.com/eth-cscs/SpFFT/master/src/execution/execution_gpu.cpp>
  - <https://raw.githubusercontent.com/eth-cscs/SpFFT/master/src/fft/transform_1d_host.hpp>
  - <https://github.com/eth-cscs/SpFFT/tree/master/src>
  - <https://github.com/eth-cscs/SpFFT/tree/master/src/execution>
  - <https://github.com/eth-cscs/SpFFT/issues?q=is%3Aissue>
  - <https://github.com/eth-cscs/SpFFT/issues/17>
  - <https://github.com/eth-cscs/SpFFT/issues/32>
  - <https://github.com/eth-cscs/SpFFT/issues/51>
  - <https://github.com/eth-cscs/SpFFT/issues/53>
  - <https://github.com/eth-cscs/SpFFT/issues/58>
  - <https://github.com/eth-cscs/SpFFT/releases>
  - <https://raw.githubusercontent.com/Darkviper7/cuSpFFT/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/eth-cscs/spfft`) · [data/wave8/enrich/raw/github_com_eth_cscs_spfft.json](../../../data/wave8/enrich/raw/github_com_eth_cscs_spfft.json) (enrichment confidence 0.8)

</details>
