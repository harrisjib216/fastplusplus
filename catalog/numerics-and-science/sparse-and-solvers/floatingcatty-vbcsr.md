# VBCSR

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `AGPL-3.0` · 🟢 active

> MPI-distributed variable-block CSR matrix library (C++ core, Python API); README claims about 4.2-4.5x over SciPy CSR.

| | |
|---|---|
| **Beats** | SciPy sparse (scipy.sparse CSR/BSR) matrix operations |
| **Claimed result** | README table: 4.21x at 500 blocks (0.0049 s vs 0.0209 s), 4.07x at 1,000 blocks, 4.33x at 5,000 blocks, 4.46x at 10,000 blocks, 4.49x at 20,000 blocks (0.1866 s vs 0.8377 s) over SciPy. |
| **Workload** | Variable-block sparse matrix operations on random block-sparse matrices (README table of 500 to 20,000 blocks, about 9,000 to 360,000 rows; the repo's report script defaults to block sizes 16-20 and about 200 neighbour blocks per row), VBCSR versus SciPy CSR; the README does not say which operation (SpMV, sparse-dense or SpMM) the table times, nor the thread or MPI process count. |
| **Metric** | throughput |
| **Adoption** | 1 star; PyPI package vbcsr |
| **Last commit** | 2026-09-28 |
| **Links** | [repository](https://github.com/DeepElectron/vbcsr) · [benchmark](https://github.com/floatingCatty/vbcsr) |

## Verdict

First-party README table: on random block-sparse matrices of 500 to 20,000 blocks (about 9,000 to 360,000 rows), VBCSR takes 0.0049 s vs SciPy CSR's 0.0209 s (4.21x) up to 0.1866 s vs 0.8377 s (4.49x). The README does not name the operation (the driver's default mode is SpMV), the CPU, compiler, flags or OpenMP thread count, and the current report script no longer reproduces the 20,000-block range.

## Use it when

- Localized-orbital (tight-binding, LCAO) Hamiltonians and overlap matrices where each atom pair gives a dense block of 4-20 orbitals
- Linear-scaling electronic-structure loops (McWeeny purification, KPM density of states, Chebyshev time propagation) that need thresholded sparse-sparse products to keep fill-in down
- Multi-DOF PDE or FEM systems with variable unknowns per node that SciPy BSR cannot represent (BSR needs one fixed block size)
- Python workflows that outgrow single-threaded scipy.sparse and need MPI distribution without leaving NumPy/SciPy solvers
- Real float64 or complex128 data on x86-64 Linux with AVX2

## Skip it when

- Unstructured scalar sparsity (graphs, circuit matrices): the block format brings nothing there and the README only measures block-structured random matrices
- float32 or integer data: only float64 and complex128 are supported, and only double and complex&lt;double&gt; get AVX2 kernels
- Closed-source or proprietary products: AGPL-3.0 copyleft also covers network use
- Production code that needs a stable API: 1 star, version 0.2.2, and the source is mid-way through a documented row-major migration that removed whole kernel families
- Comparisons against a tuned multithreaded library: the published table is against SciPy, and the MKL comparison the driver can run is not published

## How it is fast

Blocks are stored as contiguous row-major dense tiles grouped by shape, so each block product is a small dense GEMV or GEMM rather than scalar CSR gathers. Hand-written AVX2+FMA micro-kernels (3-row output tiles, broadcast A, shared X loads, k-unrolled by 2) handle double and complex&lt;double&gt;; multivectors are padded so every SIMD chunk stays full; and row ranges run in OpenMP parallel-for loops with NUMA-local first-touch zeroing. BLAS (MKL or OpenBLAS, batched strided GEMM/GEMV when available) and an optional MKL or AOCL sparse backend cover other paths.

## Compared with alternatives

Pick VBCSR over sparse_dot_topn (also measured against SciPy) when the matrix has natural dense blocks of varying size and you need MPI distribution or norm-thresholded block SpGEMM; sparse_dot_topn is the better fit for scalar CSR products with top-n pruning. For C++ SpMV on scalar CSR matrices, SPC5 or the merge-based and CSR5 kernels are measured against MKL, which VBCSR's public numbers are not.

## Integration

| | |
|---|---|
| **Form** | header-only C++ core (vbcsr/core/\*.hpp) built into a pybind11 Python extension; pip package vbcsr |
| **Dependencies** | MPI (C and C++), OpenMP, BLAS/LAPACK (MKL or OpenBLAS); optional ParMETIS/METIS (Hilbert-curve fallback), optional MKL sparse or AOCL-sparse; Python side needs numpy, scipy, ase, optional mpi4py |
| **Minimum toolchain** | C++17, CMake 3.15+, Python 3.8+ (scikit-build-core 0.8+, pybind11) |
| **Platforms** | Linux x86-64 (PyPI classifier POSIX Linux; wheels built for AVX2 with a scalar fallback); macOS builds need libomp per the install guide; no GPU |
| **Thread safety** | not documented; operations parallelize internally with OpenMP and are MPI-collective, so concurrent calls on one matrix should be avoided |
| **Drop-in for the baseline** | partial: implements SciPy's LinearOperator interface and converts from SciPy CSR/BSR, but it is its own matrix class with a distributed graph, explicit add_block/assemble, and to_scipy()/to_dense() that export only the local rank's part |

## Gotchas

- The default CMake build uses -march=native (VBCSR_ARCH=native); the CMake comments warn that without a Release build conda's -march=nocona flags silently compile out the AVX2 kernels, and native builds are not portable across CPUs
- Kernels use omp_get_max_threads() and the benchmark driver never sets the thread count, while SciPy's CSR dot is single-threaded, so the README's 4.2-4.5x may be threads rather than format; benchmark_large_scale.py does pin MKL to its max threads for the separate sparse_dot_mkl comparison
- The README's clone URL is the placeholder github.com/yourusername/vbcsr, and the repository now displays as DeepElectron/vbcsr (same 211 commits, 1 star), so github.com/floatingCatty/vbcsr appears to redirect
- save_matrix_market() raises on distributed matrices, and NumPy arrays passed to from_numpy or mult are always the calling rank's local slice

## Known shortcomings

- Benchmark table does not name the operation; 'serial run' is not on the page (removed); README clone URL is a placeholder; baseline SciPy.
- Claim may not be reproducible as a format win: kernels use omp_get_max_threads() and the benchmark never sets the thread count, while SciPy CSR dot is single-threaded, so the 4.2-4.5x is likely threads vs one thread. Only float64/complex128. Default build is -march=native. github.com now shows the repo as DeepElectron/vbcsr (same 211 commits).

## Caveats and trade-offs

First-party table with no CPU, compiler, flags or thread count, and the README table does not say which operation (the page mentions SpMV and SpMM) is timed. The repo also benchmarks against sparse_dot_mkl (MKL) but that result is not in the README I read. SciPy is not SuiteSparse, Eigen or PETSc, so baseline_in_list is false. Very small project (1 star); README clone URL is a placeholder.

Header-only C++ core with pybind11 Python bindings, MPI-distributed variable-block CSR, AVX/AVX2 SIMD, thresholded SpMM; targets localized-orbital Hamiltonians and multi-DOF PDE systems. AGPL-3.0 copyleft. Needs MPI and BLAS/LAPACK.

## Maintenance

Very active (211 commits, last 2026-09-28, an ongoing row-major refactor) but a one-author, 1-star, AGPL-3.0 project at version 0.2.2; fine for research codes in electronic structure, risky as a dependency elsewhere.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README 'Performance at a Glance' table matches the quoted times and speedups; the generator (generate_benchmark_report.py calling tests/benchmark_large_scale.py) is public, but no CPU, compiler, flags or thread/process count is given, so first-party C.
- **Verifier notes:** Numbers verified (4.21x at 500 blocks, 0.0049 s vs 0.0209 s, up to 4.49x at 20,000 blocks, 0.1866 s vs 0.8377 s). The record's 'serial run' is not stated on the page, so I removed it. The current report script defaults (500/1000/2000 SpMV blocks) do not reproduce the README's 20,000-block range, so the table predates it. Metadata confirmed: AGPL-3.0, 1 star, not a fork, 211 commits, last commit 2026-09-28; README clone URL is the placeholder github.com/yourusername/vbcsr.
- **Fields the verifier corrected:** `workload`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/floatingCatty/vbcsr/HEAD/README.md>
  - <https://raw.githubusercontent.com/floatingCatty/vbcsr/HEAD/generate_benchmark_report.py>
  - <https://github.com/floatingCatty/vbcsr>
  - <https://github.com/floatingCatty/vbcsr/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/floatingCatty/vbcsr/HEAD/README.md>
  - <https://github.com/floatingCatty/vbcsr>
  - <https://github.com/DeepElectron/vbcsr>
  - <https://raw.githubusercontent.com/floatingCatty/vbcsr/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/floatingCatty/vbcsr/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/floatingCatty/vbcsr/HEAD/doc/advanced_installation.md>
  - <https://raw.githubusercontent.com/floatingCatty/vbcsr/HEAD/doc/user_guide.md>
  - <https://raw.githubusercontent.com/floatingCatty/vbcsr/HEAD/doc/api_reference.md>
  - <https://raw.githubusercontent.com/floatingCatty/vbcsr/HEAD/generate_benchmark_report.py>
  - <https://raw.githubusercontent.com/floatingCatty/vbcsr/HEAD/tests/benchmark_large_scale.py>
  - <https://github.com/floatingCatty/vbcsr/tree/main/vbcsr/core>
  - <https://github.com/floatingCatty/vbcsr/tree/main/vbcsr/core/detail>
  - <https://github.com/floatingCatty/vbcsr/tree/main/vbcsr/core/detail/kernels>
  - <https://raw.githubusercontent.com/DeepElectron/vbcsr/HEAD/vbcsr/core/detail/kernels/vbcsr_apply.hpp>
  - <https://raw.githubusercontent.com/DeepElectron/vbcsr/HEAD/vbcsr/core/detail/kernels/rowmajor_kernels.hpp>
  - <https://raw.githubusercontent.com/DeepElectron/vbcsr/HEAD/vbcsr/core/detail/kernels/dense_kernels.hpp>
  - <https://raw.githubusercontent.com/DeepElectron/vbcsr/HEAD/vbcsr/core/detail/kernels/csr_apply.hpp>
  - <https://github.com/DeepElectron/vbcsr/issues?q=is%3Aissue>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/floatingcatty/vbcsr`) · [data/wave8/enrich/raw/github_com_floatingcatty_vbcsr.json](../../../data/wave8/enrich/raw/github_com_floatingcatty_vbcsr.json) (enrichment confidence 0.65)

</details>
