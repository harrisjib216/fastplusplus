# Psi4

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `LGPL-3.0-only` · 🟢 active

> Open-source C++/Python quantum chemistry suite; in one 2020 community benchmark its non-DF B3LYP run edged out GAMESS-US.

| | |
|---|---|
| **Beats** | GAMESS-US 2020 |
| **Claimed result** | Psi4 1.3 vs GAMESS: 1.05x at 1-4 cores, 1.5x at 16 cores (scaling 12.1x vs 8.5x), on a Threadripper 1950X; slower than ORCA, Q-Chem, Turbomole and Gaussian 09 in the same table. |
| **Workload** | Single-point B3LYP/6-31G(d) energy of C20 (20 atoms) at 1, 2, 4, 8 and 16 cores, timing the whole run of each package with its default convergence criteria and grids and density fitting turned off in Psi4. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen Threadripper 1950X 16-core (32 threads, hyperthreading on), 32 GB DDR4-2666, 2 TB SSD (misc/README.md of the benchmark repo) |
| **Compiler and flags** | Psi4 build not described: the repo's compile/README.md lists only 'Build-in Multithreading in Python 3.7' for Psi4 (apparently a prebuilt binary); GAMESS-US built with GNU 4.8.5 and OpenBLAS 0.3.10; Gaussian, Q-Chem and Turbomole builds not described. |
| **Adoption** | 1.2k stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/psi4/psi4) · [benchmark](https://github.com/r2compchem/benchmark-qm) |

## Verdict

In the r2compchem/benchmark-qm table (October 2020, AMD Threadripper 1950X, 16 cores, SMT on, 32 GB), a single-point B3LYP/6-31G(d) energy of C20 with density fitting off took Psi4 1.3 726.2, 193.2 and 60.2 (units not stated, presumably seconds) at 1, 4 and 16 cores vs 766.2, 202.0 and 90.1 for GAMESS-US 2020 (GNU 4.8.5, OpenBLAS 0.3.10), so 1.05x at 1-4 cores and 1.50x at 16 (derived from page data). Each package ran with its own convergence and grid defaults and the Psi4 build is not described.

## Use it when

- Medium-sized molecules (tens of atoms, up to a few thousand basis functions per the README) on one multi-core node, where Psi4's OpenMP scaling beat GAMESS-US's socket build by 1.27x at 8 cores and 1.50x at 16 in the C20 B3LYP test.
- When you need a free, LGPL-3.0 code that you can script from Python (PsiAPI, NumPy interop) for high-throughput or method-development workflows instead of a commercial package.
- Intermolecular interaction work (SAPT family) and density-fitted SCF/MP2, which are Psi4's default and best-tuned paths.
- Installs via conda on Linux (x86-64 and ARM64), macOS (Intel and Apple Silicon), Windows and WSL.

## Skip it when

- If raw single-node SCF/DFT speed is the goal: in the same table Psi4 1.3 was slower than ORCA 4, Turbomole 7, Q-Chem 5 and Gaussian 09 at every core count (726.2 vs 195.6 for Q-Chem at 1 core, 60.2 vs 14.2 for Turbomole at 16), and slower than Gaussian 16 at 1 to 4 cores.
- On 1 to 4 cores against GAMESS-US the difference is about 5% (1.05x), within what different convergence criteria or BLAS builds could explain.
- Multi-node runs: the top-level CMakeLists.txt exposes ENABLE_OPENMP and no MPI option, so one calculation runs on one machine; in the benchmark, ORCA, NWChem, Firefly and Dalton were the OpenMPI builds.
- If you want the benchmarked configuration: it measured Psi4 with density fitting turned off, which is not how Psi4 runs by default, so the numbers do not describe ordinary Psi4 usage in either direction.

## How it is fast

SCF and DFT cost is dominated by building the Coulomb and exchange (J/K) matrices and the exchange-correlation quadrature. Psi4 offers several JK algorithms, from conventional PK (pre-sorted integral supermatrix), DIRECT and OUT_OF_CORE to density fitting (DF, its default for SCF and DFT) and newer composite builders (DFDIRJ+COSX, DFDIRJ+LINK, sn-LinK through GauXC); integrals come from Libint2, DFT grids from gau2grid with Libxc functionals, and the heavy lifting is OpenMP-threaded BLAS/LAPACK (MKL in the conda binaries). In the benchmark the advantage over GAMESS-US came mainly from thread scaling: Psi4 ran 12.1x faster on 16 cores than on 1, GAMESS-US 8.5x (derived from page data).

## Compared with alternatives

No catalogued sibling in sparse-and-solvers is a quantum chemistry code (they are sparse BLAS, direct solvers and QP solvers), and Psi4's hot paths are dense BLAS and integral kernels, so this entry sits in the category only loosely; pick Psi4 when you need a whole electronic-structure program, not a solver library.

## Integration

| | |
|---|---|
| **Form** | module (Python package with a compiled C++ core library); conda binaries or a CMake build |
| **Dependencies** | BLAS/LAPACK (MKL in conda builds), Python with NumPy, pybind11, Libint2 (with Eigen and Boost headers), Libxc, gau2grid, QCElemental and qcengine, plus runtime networkx, pint, pydantic, msgpack, SciPy, py-cpuinfo and psutil; many optional add-ons |
| **Minimum toolchain** | C++20 compiler and CMake 3.19+ on current master; Python 3.10 to 3.14 per the README |
| **Platforms** | Linux (x86-64, ARM64), macOS (Intel, Apple Silicon), Windows and WSL per the README |
| **Thread safety** | Parallel inside one calculation via OpenMP (thread count set by the user); the Python driver keeps global option state (core.set_global_option), so run concurrent calculations as separate processes; not otherwise documented in the files read |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the benchmark turned density fitting off for Psi4, yet Psi4's driver switches SCF_TYPE to DF whenever the user has not set it (proc_util.py in v1.3.2 and on master), and the README does not say which conventional algorithm (PK, DIRECT or OUT_OF_CORE) replaced it; there are no input files to check.
- Not an equal-accuracy comparison: Psi4 1.3.2's energy() converges SCF to 1e-6 in energy and 1e-6 in the orbital-gradient density criterion on a 75 x 302 unpruned grid, GAMESS-US converges on the SCF density change, and Gaussian 16 uses UltraFine grids and 1e-12 integral accuracy (README note); each package used its own defaults.
- Different builds and math libraries: Psi4 is listed only as 'Build-in Multithreading in Python 3.7', most likely the conda binary, which per the v1.3.2 conda docs ships with MKL and statically linked BLAS, while GAMESS-US was compiled with GNU 4.8.5, OpenBLAS 0.3.10 and socket parallelism; single runs, no units, and an implausible Dalton row (1502.0 s at 1 core, 6215.0 at 2) further weaken the harness.
- Stale versions: the table is Psi4 1.3 from an October 2020 run; Psi4 is at v1.11 (2026-06-29) and has since added DFDIRJ+COSX, DFDIRJ+LINK and GauXC sn-LinK exchange builders and faster range-separated DirectJK, none of which were measured.

## Known shortcomings

- Independent r2compchem/benchmark-qm table (Threadripper 1950X) matches, but the win over GAMESS is only 1.05x at 1-4 cores and 1.5x at 16; slower than ORCA, Q-Chem, Turbomole and Gaussian 09; no input files; Psi4 build undescribed; implausible Dalton row (1502.0 at 1 core, 6215.0 at 2). GAMESS is not a sparse-and-solvers baseline (baseline_in_list false).
- Enricher: the benchmark-qm run says DF was turned off but the Psi4 driver defaults SCF_TYPE to DF (proc_util.py v1.3.2 and master) and the conventional algorithm is unstated with no inputs; convergence and grids are unequal (Psi4 1e-6/1e-6, 75x302 unpruned vs GAMESS's density-change criterion); Psi4 was probably the conda MKL binary against GAMESS built with GCC 4.8.5, OpenBLAS and sockets; the win is 1.05x at 1-4 cores and the 16-core win is scaling (12.1x vs 8.5x self-speedup); stale (Psi4 1.3, Oct 2020 run, vs v1.11).

## Caveats and trade-offs

Third-party community benchmark by the r2compchem group: 23 stars, 42 commits, no input files in the repo (benchmark/ holds only three PNG charts), no stated units, one molecule and one method, only Psi4 1.3 (2019; Psi4 is now at v1.11). Only the 'General test' (C20) has data; the SCF-cutoff, MP2 and CCSD(T) sections say 'The result is coming'. Defaults differ across packages (Gaussian 16 uses UltraFine grids and 10^-12 integral accuracy, Gaussian 09 FineGrid and 10^-10; GAMESS and Firefly converge on density change; RI/DF is off in ORCA, Psi4 and Turbomole), so it is not an equal-accuracy comparison, and the authors say they do not aim to rank packages. The table has at least one implausible row (Dalton 2018: 1502.0 at 1 core but 6215.0 at 2 cores), which lowers confidence in the harness. The win over GAMESS is only about 5 percent at 1 to 4 cores (derived from page data). Psi4 loses to Gaussian 09, Turbomole 7, Q-Chem 5 and ORCA 4 at every core count (for example 726.2 vs 573.0 for ORCA 4 at 1 core and 60.2 vs 45.5 at 16), and to Gaussian 16 at 1 to 4 cores. GAMESS-US is not one of the sparse-and-solvers baselines (SuiteSparse, Eigen sparse, PETSc), and the category is approximate: Psi4 is a quantum chemistry package and no wave 8 category fits exactly. Corroboration of the PySCF row: pyscf issue #1956 (user report, RKS/PBE cc-pVTZ on C6H10 with density fitting, one thread) shows Psi4 at about 45-50 s vs PySCF at about 110 s (and 190 s vs 150 s with density fitting off, where PySCF is faster); the maintainers attributed the PySCF slowness to sparse grid code and thread oversubscription (fixed for small systems in PR #1962). Forum reports (not opened) also have Psi4 slower than Gaussian and Molpro on other workloads. [retier] No input files; Psi4 build undescribed (probably conda MKL); GAMESS built with GCC 4.8.5, OpenBLAS, sockets; DF probably on for Psi4 (driver default); unequal convergence and grids; stale Psi4 1.3 (Oct 2020) vs v1.11; implausible Dalton row.

C++ core driven by a Python (Pybind11) front end; free and open source, whereas Gaussian, Q-Chem and Turbomole are commercial. In the benchmark Psi4 was run with density fitting turned off, which is not the way Psi4 is normally used.

## Maintenance

Actively maintained (last commit 2026-10-08, v1.11 released 2026-06-29, about 16k commits, 384 open issues) and LGPL-3.0, easy to install from conda; the speed evidence is a small, input-less 2020 community benchmark of a non-default, now-stale configuration, which fits tier B only as an independent measurement and gives a 5 to 50 percent edge over a baseline outside the category.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now C.
- **Tier reason:** Independent third-party multi-package benchmark (r2compchem/benchmark-qm README table) with CPU model (Threadripper 1950X, misc/README.md) and package versions stated; every Psi4 and GAMESS-US number in the record matches the table. Not A: no input files are in the repo (benchmark/ holds only three PNGs) and the Psi4 build and flags are not described; B is borderline since the suite is small (23 stars) and not well known.
- **Retiered** B to C: Lowered B to C: the independent benchmark-qm table compares unequal setups (Psi4 conda MKL binary vs GAMESS GCC 4.8.5 with OpenBLAS and sockets; unequal convergence thresholds and grids; DF status unclear because Psi4 defaults SCF_TYPE to DF and no inputs are published), the single-core win is 1.05x and the 16-core win is thread scaling, and the Dalton row is implausible; the measurement is independent but not comparable enough for B.
- **Verifier notes:** Numbers verified against the README table row by row (Psi4 1.3 726.2/372.2/193.2/102.1/60.2 vs GAMESS-US 2020 766.2/389.1/202.0/130.1/90.1); compile/README.md lists only 'Build-in Multithreading in Python 3.7' for Psi4 and GNU 4.8.5 plus OpenBLAS 0.3.10 for GAMESS-US. Shortcomings: small win (1.05x at 1-4 cores, 1.5x at 16), slower than most commercial codes in the same table, no inputs, Dalton row anomaly, baseline not in the category list. Metadata checked: LGPL-3.0-only (source headers say 'version 3'), 1.2k stars, 515 forks, last commit 2026-10-08.
- **Fields the verifier corrected:** `baseline_in_list`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-173 (wave 8); enricher w8 pair-036
- **Pages the verifier opened:**
  - <https://github.com/r2compchem/benchmark-qm>
  - <https://raw.githubusercontent.com/r2compchem/benchmark-qm/HEAD/README.md>
  - <https://raw.githubusercontent.com/r2compchem/benchmark-qm/HEAD/compile/README.md>
  - <https://raw.githubusercontent.com/r2compchem/benchmark-qm/HEAD/misc/README.md>
  - <https://github.com/r2compchem/benchmark-qm/tree/master/benchmark>
  - <https://github.com/psi4/psi4>
  - <https://github.com/psi4/psi4/commits/master>
  - <https://raw.githubusercontent.com/psi4/psi4/master/psi4/src/psi4/libmints/basisset.cc>
- **Sources the enricher read:**
  - <https://github.com/psi4/psi4>
  - <https://github.com/psi4/psi4/commits/master>
  - <https://github.com/psi4/psi4/releases>
  - <https://github.com/psi4/psi4/issues?q=is%3Aissue%20slow%20DFT>
  - <https://github.com/psi4/psi4/issues/3568>
  - <https://raw.githubusercontent.com/psi4/psi4/master/README.md>
  - <https://raw.githubusercontent.com/psi4/psi4/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/psi4/psi4/master/psi4/src/read_options.cc>
  - <https://raw.githubusercontent.com/psi4/psi4/master/psi4/__init__.py>
  - <https://raw.githubusercontent.com/psi4/psi4/master/psi4/extras.py>
  - <https://raw.githubusercontent.com/psi4/psi4/master/psi4/driver/procrouting/proc_util.py>
  - <https://raw.githubusercontent.com/psi4/psi4/master/doc/sphinxman/source/conda.rst>
  - <https://raw.githubusercontent.com/psi4/psi4/v1.3.2/doc/sphinxman/source/conda.rst>
  - <https://raw.githubusercontent.com/psi4/psi4/v1.3.2/psi4/driver/procrouting/proc_util.py>
  - <https://raw.githubusercontent.com/psi4/psi4/v1.3.2/psi4/src/read_options.cc>
  - <https://raw.githubusercontent.com/psi4/psi4/v1.3.2/psi4/driver/driver.py>
  - <https://github.com/r2compchem/benchmark-qm>
  - <https://github.com/r2compchem/benchmark-qm/commits/master>
  - <https://raw.githubusercontent.com/r2compchem/benchmark-qm/HEAD/README.md>
  - <https://raw.githubusercontent.com/r2compchem/benchmark-qm/HEAD/compile/README.md>
  - <https://raw.githubusercontent.com/r2compchem/benchmark-qm/HEAD/misc/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/psi4/psi4`) · [data/wave8/enrich/raw/github_com_psi4_psi4.json](../../../data/wave8/enrich/raw/github_com_psi4_psi4.json) (enrichment confidence 0.65)

</details>
