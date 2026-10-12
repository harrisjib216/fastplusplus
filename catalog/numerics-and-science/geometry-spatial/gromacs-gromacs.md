# GROMACS

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `LGPL-2.1-or-later` · 🟢 active

> GPU-resident molecular dynamics engine; on one 6N4O PME benchmark 1.04-2.40x NAMD 3.0b5 and 1.11-1.65x OpenMM 8.1 throughput.

| | |
|---|---|
| **Beats** | NAMD 3.0 (3.0b5 multicore-CUDA build) and OpenMM 8.1 |
| **Claimed result** | No project claim; independent measurement in NgFEP/NgFEP-assessment. Per-GPU means of 5 runs computed from the repo's .dat files (derived from page data), GROMACS 2023.3 (the repo writes 23.3) vs NAMD 3.0b5 vs OpenMM 8.1 in ns/day: A100 59.47 vs 39.19 vs 36.00 (1.52x NAMD, 1.65x OpenMM); RTX 4070 54.01 vs 22.46 vs 33.63 (2.40x, 1.61x); RTX A4500 30.85 vs 16.33 vs 21.58 (1.89x, 1.43x); RTX 2080 Ti 28.13 vs 14.25 vs 19.13 (1.97x, 1.47x; the OpenMM file is a byte-identical copy of the GP100 file); Quadro RTX 5000 21.07 vs 12.57 vs 16.39 (1.68x, 1.29x); Quadro RTX 6000 29.59 vs 17.92 vs 23.51 (1.65x, 1.26x); Quadro GP100 22.22 vs 15.23 vs 19.13 (1.46x, 1.16x); RTX 3090 33.03 vs 23.40 vs 26.96 (1.41x, 1.23x); P100 19.69 vs 14.66 vs 13.69 (1.34x, 1.44x); GTX 1080 Ti 15.26 vs 11.80 vs 11.78 (1.29x, 1.30x); V100 25.13 vs 24.26 vs 22.54 (1.04x, 1.11x). Across the 11 GPUs with complete data GROMACS is 1.04x to 2.40x NAMD and 1.11x to 1.65x OpenMM (derived from page data). AMBER 22 pmemd.cuda in the same suite is faster than GROMACS on 5 of these 11 GPUs (up to 1.47x on V100, 36.89 vs 25.13 ns/day, derived from page data). |
| **Workload** | Conventional MD of the 6N4O Argonaute2/miR-122 complex (MDbench dataset), explicit-solvent PME with a 144x144x144 grid, 8 A / 0.8 nm cutoff, 1 fs timestep, NPT, single GPU per run, 5 repeats per GPU; ns/day read from each code's own log. |
| **Metric** | throughput |
| **Hardware** | Per-row NVIDIA GPUs on several lab hosts: A100, V100, P100, GP100, TITAN V, RTX 2080 Ti, Quadro RTX 5000 and 6000, RTX 3090, RTX A4500, RTX 4070, GTX 1080 Ti. Host CPU models and CUDA/driver versions not stated. |
| **Compiler and flags** | Builds and compilers not stated (the README sends users to each package's install guide). GROMACS run line from the repo script: gmx mdrun -ntomp 4 -nb gpu -pme gpu -update gpu -bonded cpu (mdp: dt 0.001, nsteps 10000, V-rescale + Parrinello-Rahman, constraints h-bonds, Verlet nstlist 10, PME order 4, rcoulomb/rvdw 0.8). NAMD run line: namd3 +p1 +idlepoll with CUDASOAintegrate on (NAMD_3.0b5 Linux-x86_64-multicore-CUDA binary named in the script). OpenMM: CUDA platform, mixed precision, LangevinIntegrator 1 fs, MonteCarloBarostat every 25 steps. |
| **Adoption** | 966 stars on the GitHub read-only mirror (code review and issues are on gitlab.com/gromacs/gromacs); widely used MD engine |
| **Last commit** | 2026-10-06 |
| **Links** | [repository](https://github.com/gromacs/gromacs) · [benchmark](https://github.com/NgFEP/NgFEP-assessment) |

## Verdict

An independent lab suite (NgFEP/NgFEP-assessment) ran the 6N4O Argonaute2/miR-122 system (AMBER-parametrized, PME, 0.8 nm cut-off, 1 fs, NPT) five times per GPU with GROMACS 2023.3 (-nb gpu -pme gpu -update gpu -bonded cpu, 4 OpenMP threads), NAMD 3.0b5 multicore-CUDA in GPU-resident mode and OpenMM 8.1 CUDA mixed precision; per-GPU means recomputed this session from all 48 .dat files the plotting notebook reads match the record (A100 59.47 vs 39.19 vs 36.00 ns/day; 1.04-2.40x NAMD and 1.11-1.65x OpenMM over 11 GPUs, derived from page data). Builds, compilers, CUDA and driver versions and host CPUs are not stated, and thermostats, barostats and run lengths differ between codes.

## Use it when

- Explicit-solvent biomolecular MD with PME on a single NVIDIA GPU, where the benchmark shows it ahead of both NAMD 3.0b5 (GPU-resident) and OpenMM 8.1 on all 11 GPUs, by at least 1.23x over both on 9 of them (derived from page data), with its largest margins on consumer cards (RTX 4070: 54.0 vs 22.5 and 33.6 ns/day).
- Throughput farms of many independent single-GPU runs (equilibration, replicas, free-energy windows) where ns/day per GPU is the cost driver.
- Mixed or non-NVIDIA hardware: one code base runs on CUDA, SYCL (Intel GPUs with oneAPI, AMD GPUs with AdaptiveCpp), HIP and OpenCL, plus CPU-only clusters with SIMD kernels.
- Multi-GPU or multi-node runs with domain decomposition and GPU PME decomposition (cuFFTMp or HeFFTe builds) when one GPU is not enough.

## Skip it when

- When AMBER pmemd.cuda is an option: in the same suite AMBER 22 is faster than GROMACS on 5 of 11 GPUs (V100 36.89 vs 25.13 ns/day, RTX 3090 43.42 vs 33.03), so GROMACS is not the fastest code on that page.
- Workflows that need features the GPU-resident path lacks: per the mdrun docs, GPU update is not supported with mass or constraint free-energy perturbation, virtual sites, Ewald surface correction, replica exchange, constraint pulling, orientation restraints or computational electrophysiology, and LJ-PME and PME orders other than 4 do not run on GPUs; those runs fall back to CPU update and lose much of the advantage.
- Custom-force or Python-scripted method development, where OpenMM's API (custom forces, integrators) is the better fit even at lower ns/day.
- Embedding MD inside another C++ product under a permissive licence: GROMACS is LGPL-2.1 and its README asks that modified versions be labelled as derived work and not called official GROMACS.
- V100-class GPUs, where its lead over NAMD 3.0b5 in this suite shrinks to 1.04x (25.13 vs 24.26 ns/day).

## How it is fast

Short-range forces use the Verlet cut-off scheme with cluster-pair (nbnxm) pair lists, dynamic list pruning and hand-written SIMD kernels (SSE2 through AVX-512, NEON, SVE, VSX) or CUDA/SYCL/HIP/OpenCL kernels. In GPU-resident mode (-update gpu) nonbonded forces, PME (GPU FFT via cuFFT or VkFFT), update and LINCS/SETTLE constraints all run on the GPU, so coordinates and forces stay on the device between neighbour-search steps while the CPU can take bonded forces concurrently. mdrun also auto-tunes at start-up: it raises nstlist with a matching Verlet buffer and, with -tunepme on by default, scales the Coulomb cut-off and PME grid spacing together to balance work while keeping equivalent model physics.

## Compared with alternatives

No other molecular dynamics engine is catalogued in geometry-spatial; the spatial-index siblings (nanoflann, ArborX, Pkd-tree) are libraries for neighbour queries you embed, whereas GROMACS's cell and pair lists are internal to mdrun, so pick it when you need whole MD simulations rather than a reusable neighbour-search structure.

## Integration

| | |
|---|---|
| **Form** | built application plus shared/static libgromacs (CMake); gmxapi Python package; optional NB-LIB C++ API install (GMX_INSTALL_NBLIB_API) |
| **Dependencies** | FFT library (FFTW3 by default, MKL, or bundled slow fftpack; GMX_BUILD_OWN_FFTW can download FFTW); optional CUDA toolkit 12.1+ (main branch), SYCL compiler (oneAPI DPC++ 2024.0+ or AdaptiveCpp 24.02+), ROCm/HIP or OpenCL; optional MPI, cuFFTMp, HeFFTe, VkFFT |
| **Minimum toolchain** | C++17; on the current main branch GCC 11+, Clang 14+ or MSVC 2019, CMake 3.28+; CUDA 12.1+ and compute capability 5.0+ for CUDA builds (older releases such as the benchmarked 2023.3 had lower minimums, not checked) |
| **Platforms** | Linux, macOS and Windows; x86-64 (SSE2, SSE4.1, AVX, AVX2, AVX-512), AArch64 (NEON, SVE), POWER (VSX); GPUs: NVIDIA (CUDA), AMD (SYCL/AdaptiveCpp or HIP), Intel (SYCL/oneAPI), Apple M-series (OpenCL) |
| **Thread safety** | Not documented for library use; mdrun parallelizes internally with OpenMP threads, thread-MPI ranks or MPI. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw that understates GROMACS rather than inflating it: the NgFEP script runs only 10,000 steps (10 ps) without -resethway or -resetstep, so the reported ns/day includes start-up and the PME tuning phase that the mdrun docs say these options exist to exclude; it also forces -bonded cpu with -update gpu and keeps nstenergy/nstlog at 100 and tau_t 0.1 ps, while the mdrun docs warn that frequent energy computation and coupling carry large overhead in GPU-resident runs. NAMD and OpenMM ran 100,000 steps. This fits the gap to MDBench (GROMACS 2023.2 at 88.4 ns/day on an A100 for 6n4o, snippet only, against 59.5 here).
- The 'fixed 144^3 PME grid, 0.8 nm cut-off' in the workload is not guaranteed for GROMACS: pmeTuningIsSupported() in src/gromacs/ewald/pme_load_balancing.cpp enables the default -tunepme whenever nonbondeds run on a GPU, so mdrun may have run a larger Coulomb cut-off with a coarser grid (equivalent accuracy, but not the same grid NAMD and AMBER used).
- Rankings flip with versions and run settings: an MDBench snippet shows NAMD 3.0b3 at 42.06 ns/day against GROMACS 2021.4 at 29.5 ns/day on the same A100 for 6n4o, the reverse of this suite, so treat the 1.5x A100 lead as specific to GROMACS 2023 GPU-resident runs.
- Builds are tied to one SIMD level chosen at configure time (GMX_SIMD, default AUTO detects the build host), so a binary built on a newer node can fail or run slowly elsewhere; the known-issues page also lists a severe SVE slowdown with LLVM 20 and test failures with GCC 12-14 on POWER9.

## Known shortcomings

- NgFEP-assessment is an obscure suite (2 stars, no paper) with unequal thermostats, run lengths and CPU threads across GROMACS 23.3, NAMD 3.0 and OpenMM 8.1; curation errors (the OpenMM GP100 file is the RTX 2080 Ti file; the GTX 1080 Ti _4 file was picked); AMBER 22 beats GROMACS on 5 of 11 GPUs; the A100 figure is low against MDBench (88.4 ns/day, snippet only). No compiler or CPU stated. LGPL-2.1-or-later. Poor fit for geometry-spatial.
- Enricher: all 48 NgFEP .dat means match; the harness cuts against GROMACS (10,000 steps, no -resethway, forced -bonded cpu, energies every 100 steps) while the default -tunepme with GPU nonbondeds means the fixed 144^3 grid / 0.8 nm is not guaranteed; the MDBench snippet (NAMD 3.0b3 42.06 vs GROMACS 2021.4 29.5 ns/day on A100) reverses the ranking, so the lead depends on version and settings.

## Caveats and trade-offs

The wave 8 categories have no molecular-dynamics bucket; geometry-spatial (cell and neighbour lists) was kept from the lead's guess and the orchestrator may override. LAMMPS, a listed baseline, is not in this benchmark and no reachable page compares GROMACS with LAMMPS (arXiv, manual.gromacs.org, mdbench.ace-net.ca and the published GROMACS papers were EGRESS_BLOCKED). The suite (NgFEP/NgFEP-assessment, 2 stars, no licence file, one author, no paper found) is independent of all three codes but is not a well-known shootout. The comparison is not like for like: GROMACS uses V-rescale plus Parrinello-Rahman, NAMD Langevin plus Langevin piston, OpenMM Langevin plus a Monte Carlo barostat every 25 steps; run lengths differ (nsteps 10000 for GROMACS, 100000 for NAMD and OpenMM); NAMD ran a 3.0b5 beta build with +p1 (one CPU thread) while GROMACS used 4 OpenMP threads with bonded forces on the CPU; OpenMM picks its PME grid from ewaldErrorTolerance 0.0004 instead of the fixed 144^3 grid; ns/day is parsed from three different log formats, and OpenMM's figure is wall time around sim.step including reporter output. Constraints are equivalent (NAMD 'rigidBonds all' constrains bonds to hydrogen plus rigid water, matching GROMACS h-bonds and OpenMM HBonds). Curation errors in the data: the OpenMM GP100 and RTX 2080 Ti .dat files are byte-identical, so one of those OpenMM rows is a copy; the GTX 1080 Ti GROMACS _1 and _8 files are byte-identical and the plotting notebook uses the _4 file (mean 15.26 vs 14.60 ns/day for the other two, which would give 1.24x NAMD); the TITAN V GROMACS file holds a single 0 (failed run) and is excluded. The same suite's AMBER 22 pmemd.cuda (not OSI-licensed; run on a 128^3 PME grid) is faster than GROMACS on 5 of 11 GPUs (V100 36.89 vs 25.13 ns/day, RTX 3090 43.42 vs 33.03, Quadro RTX 6000 31.83 vs 29.59, RTX 2080 Ti 28.97 vs 28.13, P100 20.07 vs 19.69) and level on Quadro RTX 5000, so GROMACS is not the fastest code on this page. GROMACS '23.3' in the repo is release 2023.3, not the newest. Absolute numbers look untuned next to MDBench (WebSearch snippet only: GROMACS 2023.2 on one Narval A100 at 88.4 ns/day on 6n4o, against 59.5 here); MDBench (Digital Research Alliance of Canada) is a well-known independent suite with GROMACS, NAMD3, PMEMD and OpenMM runs on the same 6n4o system and is the better source for a retier where mdbench.ace-net.ca is reachable. The V100 row (1.04x NAMD) shows the lead is GPU-generation dependent.

Large C++ code base with CUDA, SYCL, OpenCL and CPU SIMD back ends; the best results here need GPU-resident update (-update gpu), which limits some features (not all integrators, constraints or free-energy setups are supported on the GPU path). Library-style reuse is limited; it is a full MD engine (LGPL-2.1, so linking carries LGPL terms).

## Maintenance

Actively developed (GitHub read-only mirror of gitlab.com/gromacs/gromacs, 24,268 commits, last commit 2026-10-06), LGPL-2.1 and packaged widely; usable as an application today, but library reuse is limited to libgromacs, gmxapi and the opt-in NB-LIB API.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Independent third-party suite (NgFEP/NgFEP-assessment, an academic lab unaffiliated with GROMACS, NAMD or OpenMM) publishes run scripts, inputs (c-MD/\*/..._inputs) and per-run raw ns/day .dat files for GROMACS, NAMD 3 and OpenMM 8.1 on 11 usable GPUs; every per-GPU mean in the record re-derives exactly from the .dat files. Not A because build, compiler, flags, CUDA/driver and host CPU models are not stated; held at B as an independent measurement although the suite is obscure (2 stars, no paper found) and has curation errors.
- **Verifier notes:** All record numbers re-derive exactly from the raw .dat files; metadata checked (966 stars, LGPL-2.1-or-later per COPYING and source headers, last commit 2026-10-06, not a fork). Record's caveat that NAMD's 'rigidBonds all' differs from GROMACS h-bonds was wrong and is corrected; new shortcomings: copied OpenMM data file (GP100 = RTX 2080 Ti), GTX 1080 Ti file selection, AMBER 22 beats GROMACS on 5 of 11 GPUs in the same suite, numbers below MDBench. Orchestrator may retier to C if 'well-known suite' is read strictly; category override to a non-geometry bucket is likely needed.
- **Fields the verifier corrected:** `license`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** NgFEP-assessment .dat files (verifier); enricher harness reading
- **Pages the verifier opened:**
  - <https://github.com/NgFEP/NgFEP-assessment>
  - <https://github.com/NgFEP/NgFEP-assessment/blob/main/README.md>
  - <https://github.com/NgFEP/NgFEP-assessment/tree/main/c-MD/GROMACS-benchmark>
  - <https://github.com/NgFEP/NgFEP-assessment/tree/main/c-MD/GROMACS-benchmark/GROMACS_inputs>
  - <https://github.com/NgFEP/NgFEP-assessment/tree/main/c-MD/NAMD-benchmark/NAMD_inputs>
  - <https://github.com/NgFEP/NgFEP-assessment/tree/main/c-MD/OPENMM-benchmark/OPENMM_inputs>
  - <https://github.com/NgFEP/NgFEP-assessment/tree/main/c-MD/GROMACS-benchmark/benchmark_6n4o_gromacs/sylvaner>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/README.md>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/GROMACS-benchmark/GROMACS_inputs/gromacs_production.mdp>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/NAMD-benchmark/NAMD_inputs/namd3_input.in>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/OPENMM-benchmark/OPENMM_inputs/openmm_input.py>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/AMBER-benchmark/AMBER_inputs/pmemd_prod.in>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/GROMACS-benchmark/benchmark_6n4o_gromacs/cerebro/scripts/1_run_benchmark.sh>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/GROMACS-benchmark/benchmark_6n4o_gromacs/cerebro/scripts/2_extract_results.sh>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/NAMD-benchmark/benchmark_6n4o_namd/case/scripts/1_run_namd3_bench.sh>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/NAMD-benchmark/benchmark_6n4o_namd/case/scripts/2_extract_results.sh>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/OPENMM-benchmark/benchmark_6n4o_openmm/case/scripts/1_run_benchmark.sh>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/OPENMM-benchmark/benchmark_6n4o_openmm/case/scripts/2_extract_results.sh>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/GROMACS-benchmark/benchmark_6n4o_gromacs/amarel/A100_results_gromacs.dat>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/NAMD-benchmark/benchmark_6n4o_namd/amarel/A100_results_namd.dat>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/OPENMM-benchmark/benchmark_6n4o_openmm/amarel/A100_results_openmm.dat>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/AMBER-benchmark/benchmark_6n4o_pmemd/amarel/V100_results_amber.dat>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/GROMACS-benchmark/benchmark_6n4o_gromacs/amarel/V100_results_gromacs.dat>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/GROMACS-benchmark/benchmark_6n4o_gromacs/case/TITAN_V_results_gromacs.dat>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/OPENMM-benchmark/benchmark_6n4o_openmm/cerebro/GP100_results_openmm.dat>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/OPENMM-benchmark/benchmark_6n4o_openmm/cerebro/RTX_2080_Ti_results_openmm.dat>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/GROMACS-benchmark/benchmark_6n4o_gromacs/sylvaner/GTX_1080_Ti_results_gromacs_1.dat>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/GROMACS-benchmark/benchmark_6n4o_gromacs/sylvaner/GTX_1080_Ti_results_gromacs_4.dat>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/GROMACS-benchmark/benchmark_6n4o_gromacs/sylvaner/GTX_1080_Ti_results_gromacs_8.dat>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/GROMACS-benchmark/benchmark_6n4o_gromacs/sylvaner/scripts/1_run_benchmark.sh>
  - <https://github.com/gromacs/gromacs>
  - <https://github.com/gromacs/gromacs/commits>
  - <https://raw.githubusercontent.com/gromacs/gromacs/main/COPYING>
  - <https://raw.githubusercontent.com/gromacs/gromacs/main/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/gromacs/gromacs>
  - <https://github.com/gromacs/gromacs/tree/main/api>
  - <https://raw.githubusercontent.com/gromacs/gromacs/main/README>
  - <https://raw.githubusercontent.com/gromacs/gromacs/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/gromacs/gromacs/main/src/gromacs/ewald/pme_load_balancing.cpp>
  - <https://raw.githubusercontent.com/gromacs/gromacs/main/src/gromacs/mdrun/md.cpp>
  - <https://raw.githubusercontent.com/gromacs/gromacs/main/docs/install-guide/index.rst>
  - <https://raw.githubusercontent.com/gromacs/gromacs/main/docs/user-guide/mdrun-performance.rst>
  - <https://raw.githubusercontent.com/gromacs/gromacs/main/docs/user-guide/known-issues.rst>
  - <https://raw.githubusercontent.com/gromacs/gromacs/main/api/nblib/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/README.md>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/GROMACS-benchmark/GROMACS_inputs/gromacs_production.mdp>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/GROMACS-benchmark/benchmark_6n4o_gromacs/cerebro/scripts/1_run_benchmark.sh>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/GROMACS-benchmark/benchmark_6n4o_gromacs/cerebro/scripts/2_extract_results.sh>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/NAMD-benchmark/NAMD_inputs/namd3_input.in>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/NAMD-benchmark/benchmark_6n4o_namd/case/scripts/1_run_namd3_bench.sh>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/NAMD-benchmark/benchmark_6n4o_namd/case/scripts/2_extract_results.sh>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/OPENMM-benchmark/OPENMM_inputs/openmm_input.py>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/OPENMM-benchmark/benchmark_6n4o_openmm/case/scripts/1_run_benchmark.sh>
  - <https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/OPENMM-benchmark/benchmark_6n4o_openmm/case/scripts/2_extract_results.sh>
  - https://raw.githubusercontent.com/NgFEP/NgFEP-assessment/main/c-MD/{AMBER,GROMACS,NAMD,OPENMM}-benchmark/benchmark_6n4o_\*/{sylvaner,case,cerebro,rioja,tesla,amarel}/\*_results_\*.dat (all 48 files listed in c-MD/plot/avg-sd.ipynb)
  - https://mdbench.ace-net.ca/mdbench/benchmark/23 (EGRESS_BLOCKED; WebSearch snippet only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/gromacs/gromacs`) · [data/wave8/enrich/raw/github_com_gromacs_gromacs.json](../../../data/wave8/enrich/raw/github_com_gromacs_gromacs.json) (enrichment confidence 0.7)

</details>
