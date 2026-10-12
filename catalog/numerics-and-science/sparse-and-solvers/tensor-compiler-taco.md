# TACO (Tensor Algebra Compiler)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Sparse matrices and solvers](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++` · `MIT` · 🟡 stale

> Compiler that generates fused C/CUDA kernels for any sparse/dense tensor expression; matches Eigen and MKL, beats uBLAS, Gmm++ and MATLAB Tensor Toolbox.

| | |
|---|---|
| **Beats** | Eigen (sparse), Intel MKL, OSKI and pOSKI, uBLAS and Gmm++ for sparse linear algebra; SPLATT and the MATLAB Tensor Toolbox for sparse 3rd-order tensor kernels |
| **Claimed result** | The paper's headline is parity: performance 'competitive with best-in-class hand-optimized kernels in popular libraries' (abstract). SpMV (Fig. 14): 'competitive with Intel MKL and matches, if not slightly exceeds, single-threaded performance of all of the other libraries'; Eigen's bars sit at about 1.0x to 1.1x taco's time, and MKL is slightly faster on rma10 and cant. Compound operations (Fig. 16, bars read off the chart, so approximate): Eigen takes about 0.93x to 1.4x taco's time (largest on webbase-1M for MATTRANSMUL and RESIDUAL, where MKL and OSKI are also about 1.2x to 1.4x slower). Fig. 16 labels its off-scale bars: uBLAS 2,411.81x to 73,404.75x slower on SDDMM; PLUS3 bars at 4.88x to 5.79x (uBLAS) and 9.16x to 16.75x (Gmm++, 'about an order of magnitude slower'). Table 2 (serial unless noted): the MATLAB Tensor Toolbox is 9.329x to 1856x slower. MTTKRP against SPLATT: SPLATT takes 1.218x taco's time serial and 1.266x parallel on Facebook, but 0.7157x and 0.8371x on NELL-2 and NELL-1, and 0.6542x parallel on NELL-1, i.e. taco is up to 1.53x slower. Blocked SpMV: 'OSKI outperforms taco in almost all cases.' |
| **Workload** | OOPSLA 2017 paper, Section 8. SpMV on six SuiteSparse matrices (rma10, cant, cop20k, scircuit, mac-econ, pwtk). Blocked SpMV against tuned OSKI/pOSKI. Compound kernels: SDDMM, PLUS3 (A = B + C + D), MATTRANSMUL (y = alpha A^T x + beta z) and RESIDUAL (y = b - Ax), the last two also on webbase-1M. 3rd-order tensor kernels TTV, TTM, MTTKRP, PLUS and INNERPROD on the Facebook, NELL-2 and NELL-1 tensors. Average cold-cache times, serial unless marked -par (12 threads on one socket). |
| **Metric** | throughput |
| **Hardware** | Two-socket 12-core/24-thread 2.4 GHz Intel Xeon E5-2695 v2, 32 KB L1d, 30 MB L3 per socket, 128 GB RAM; parallel runs use 12 threads pinned to one socket with numactl |
| **Compiler and flags** | GCC 5.4 (paper). taco-bench/CMakeLists.txt builds the harness and the header-only baselines with -O3 -ffast-math -std=c++11. taco JIT-compiles its generated C kernels with TACO_CFLAGS, which defaults to '-O3 -ffast-math -std=c99' in src/codegen/module.cpp at HEAD; the 2017 default was not checked. Baseline library versions (Eigen, MKL, OSKI, Boost uBLAS, Gmm++, SPLATT) are not stated. |
| **Adoption** | 1.4k stars, 200 forks |
| **Last commit** | 2025-04-14 |
| **Links** | [repository](https://github.com/tensor-compiler/taco) · [benchmark](https://raw.githubusercontent.com/tensor-compiler/tensor-compiler.github.io/HEAD/files/kjolstad-oopsla17-tensor-compiler.pdf) |

## Verdict

The peer-reviewed OOPSLA 2017 paper ran serial and 12-thread kernels on a two-socket Xeon E5-2695 v2 with GCC 5.4 (the taco-bench harness builds with -O3 -ffast-math): taco's SpMV matched Eigen within about 0-10% and was close to MKL across six SuiteSparse matrices, fused compound kernels ran up to about 1.4x faster than Eigen, MKL and OSKI on webbase-1M, uBLAS and Gmm++ were 5x to 73,000x slower on some kernels for algorithmic reasons, and SPLATT's MTTKRP was faster on two of three tensors. Overall the result is parity with hand-tuned libraries plus far wider coverage, not a broad speedup.

## Use it when

- Compound or unusual sparse kernels (SDDMM, A^T x residuals, B + C + D, sparse tensor contractions) that no fixed library API offers as one fused call
- Sparse 3rd-order and higher tensor kernels (TTV, TTM, MTTKRP, inner products) in CSF or mixed formats, where the MATLAB Tensor Toolbox was 9x to 1856x slower in the paper
- Generating a standalone C or CUDA kernel offline with the taco CLI (e.g. -f=B:ds for CSR SpMV) and vendoring the emitted code with no runtime dependency
- Exploring format choices (CSR vs DCSR vs blocked vs dense) for a kernel before hand-tuning it
- Research prototypes that need a correct-by-construction baseline for new sparse formats or schedules

## Skip it when

- Plain SpMV, where it only matches Eigen and MKL (MKL was slightly faster on rma10 and cant in the paper) and tuned register-blocked OSKI beat it in almost all blocked cases
- MTTKRP on large tensors where SPLATT is available: SPLATT was up to about 1.5x faster on NELL-1 and NELL-2 in the paper
- Sparse outputs of products (A\*B, A^T\*A, A\*B\*C): the umbrella bug issue #297 (open since 2020) says taco does not currently generate correct code for such sparse outputs
- Deployments where invoking a C compiler at run time is unacceptable (the library JIT path shells out to cc/nvcc and dlopens the result from a temp dir)
- Projects that need active maintenance: last commit 2025-04-14, 25 open bug-labelled issues including crashes and wrong-result reports

## How it is fast

The OOPSLA 2017 paper combines three ideas: per-dimension storage formats, iteration graphs that order the loop nest to follow each operand's storage tree, and merge lattices that generalise the two-way sparse merge loop so co-iteration over several sparse operands runs as specialised while-loops that drop exhausted operands. Compound expressions (e.g. y = alpha A^T x + beta z, or SDDMM) become one fused loop nest with no temporaries, which is where it beats Eigen, uBLAS and Gmm++. At HEAD a scheduling language (split, divide, reorder, fuse, pos, precompute into a workspace, parallelize with output-race strategies, unroll) lets you tile, add workspaces and target OpenMP or CUDA; generated C is compiled with -O3 -ffast-math by default.

## Compared with alternatives

Pick taco over Sympiler when you need arbitrary fused tensor or matrix expressions rather than sparse Cholesky or triangular solves, and over the fixed SpMV kernels (CSR5, merge-spmv, SPC5, CVR) when the operation is not SpMV or the operands are higher-order tensors; for raw SpMV throughput those specialised kernels are the better pick.

## Integration

| | |
|---|---|
| **Form** | shared lib by default (TACO_SHARED_LIBRARY=ON) plus taco CLI; generated kernels can be used as source-drop C/CUDA |
| **Dependencies** | none for the core library; a C compiler at run time for JIT; optional OpenMP (-DOPENMP=ON), CUDA toolkit (-DCUDA=ON, generated CUDA needs compute capability 6.1+), Python 3 with NumPy/SciPy and the pybind11 submodule for pytaco |
| **Minimum toolchain** | C++14 (CMake sets -std=c++14), GCC 5.0+ or Clang 3.9+, CMake 3.4+; generated C is C99 |
| **Platforms** | CPUs targeted by the host C compiler; build docs cover Linux (Debian/Ubuntu packages), and the JIT relies on system() and dlopen, so Windows is not documented; NVIDIA GPUs via generated CUDA (compute capability 6.1+) |
| **Thread safety** | not documented; generated kernels can be OpenMP-parallel, and the JIT writes and dlopens libraries in a shared temp directory |
| **Drop-in for the baseline** | no |

## Gotchas

- Default JIT flags are -O3 -ffast-math -std=c99 (override with TACO_CFLAGS, compiler with the target's env var, TACO_NVCC/TACO_NVCCFLAGS for CUDA), so results can differ from strict-IEEE Eigen or MKL in the last bits
- Operands whose formats point opposite ways (CSR + CSC, transposes) form a cycle in the iteration graph, which the code generator does not support; convert formats first
- The paper's automatic parallelisation only parallelises outer for-loops with a fully dense output and no scatter; other cases need an explicit parallelize() schedule with an output race strategy
- Open bugs include a heap-buffer-overflow and misaligned access when inserting int values into a dense tensor (#514), a segfault for a kernel with a workspace (#519), and invalid COO pack/unpack code from the CUDA generator (#438)

## Known shortcomings

- Mostly parity with Eigen/MKL (Eigen takes about 0.93x-1.4x of taco's time); huge wins only over uBLAS (SDDMM 2,412x-73,405x); SPLATT up to 1.53x faster and OSKI faster on blocked SpMV; taco-bench disabled validation for MKL SpMV, Gmm++ PLUS3 and uBLAS SDDMM/PLUS3.
- Correctness: open bug #297 (since 2020) says taco generates incorrect code for sparse outputs of products (A\*B, A^T\*A, A\*B\*C); #514 heap-buffer-overflow and misaligned access on int insert(); #519 segfault with a workspace kernel; 25 open bug-labelled issues. JIT shells out to cc with -O3 -ffast-math by default.

## Caveats and trade-offs

The README and paper claim parity, not a broad win. Against Eigen sparse, the incumbent, taco is roughly equal on SpMV and up to about 1.4x faster on fused compound operations; Eigen is slightly faster on some SDDMM and PLUS3 matrices. MKL is slightly faster on some SpMV matrices, tuned OSKI beats taco on blocked SpMV in almost all cases, and SPLATT's MTTKRP is up to 1.53x faster on NELL-1/NELL-2. The very large ratios have algorithmic causes: uBLAS SDDMM does Theta(n^3) dense work, and the Tensor Toolbox matricizes in MATLAB. The taco-bench harness covers only the linear-algebra libraries (no SPLATT or Tensor Toolbox code). Its last commits (2017-08-31 and 2017-09-01) disabled result validation for MKL SpMV, Gmm++ PLUS3 and uBLAS SDDMM/PLUS3. Baseline library versions are not stated. The measurements are from 2017 on an Ivy Bridge-EP Xeon with GCC 5.4 and -ffast-math on both sides; taco HEAD has changed since. Stale: last taco commit 2025-04-14, taco-bench last commit 2017-09-01.

Usable as a C++ library to load tensors and compute expressions, or as a code generator that emits C functions for a given expression and format. The README links the OOPSLA 2017 paper and two technical reports (arXiv 1802.10574 on optimization, 1804.10112 on formats) for details.

## Maintenance

Stale (last commit 2025-04-14; the paper's taco-bench harness last changed 2017) but MIT-licensed, and kernels emitted by the CLI are plain C that can be vendored without the compiler.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now A.
- **Tier reason:** Upgraded from D. The peer-reviewed OOPSLA 2017 paper (opened from the project site's GitHub Pages repo) measures taco against Eigen sparse, Intel MKL, OSKI/pOSKI, uBLAS and Gmm++, plus SPLATT and the MATLAB Tensor Toolbox. It states GCC 5.4 and a two-socket Intel Xeon E5-2695 v2. The paper's artifact repo github.com/tensor-compiler/taco-bench (taco-bench.cpp with eigen-bench.h, mkl-bench.h, oski-bench.h, poski-bench.h, ublas-bench.h, gmm-bench.h) runs the SpMV, SDDMM, PLUS3, MATTRANSMUL and RESIDUAL comparisons, and its CMakeLists.txt gives the flags (-O3 -ffast-math -std=c++11). So code, compiler, flags and CPU are all public for the linear-algebra results; the tensor results against SPLATT and the Tensor Toolbox have no public harness there.
- **Verifier notes:** The paper and its artifact repo turned the D entry into A, though for a mostly-parity claim: real but modest wins over Eigen and MKL on fused kernels, large wins over uBLAS, Gmm++ and the Tensor Toolbox, and losses to tuned OSKI (blocked) and SPLATT (NELL tensors). tensor-compiler.org, arxiv.org, dspace.mit.edu, dl.acm.org and researchgate were blocked by egress. The PDF was read from the site's source repo (tensor-compiler/tensor-compiler.github.io, files/kjolstad-oopsla17-tensor-compiler.pdf); it is the published version (29 pp., CC-BY 4.0). The arXiv follow-ups 1802.10574 and 1804.10112 were not opened.
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `baseline_in_list`, `compared_against_cpp_std_directly`, `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/tensor-compiler/taco>
  - <https://github.com/tensor-compiler/taco/commits/master>
  - <https://raw.githubusercontent.com/tensor-compiler/taco/HEAD/README.md>
  - <https://raw.githubusercontent.com/tensor-compiler/taco/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tensor-compiler/taco/HEAD/src/codegen/module.cpp>
  - <https://github.com/orgs/tensor-compiler/repositories>
  - <https://raw.githubusercontent.com/tensor-compiler/tensor-compiler.github.io/HEAD/files/kjolstad-oopsla17-tensor-compiler.pdf>
  - <https://github.com/tensor-compiler/taco-bench>
  - <https://github.com/tensor-compiler/taco-bench/commits>
  - <https://raw.githubusercontent.com/tensor-compiler/taco-bench/HEAD/README.md>
  - <https://raw.githubusercontent.com/tensor-compiler/taco-bench/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tensor-compiler/taco-bench/HEAD/taco-bench.cpp>
  - <https://raw.githubusercontent.com/tensor-compiler/taco-bench/HEAD/eigen-bench.h>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/tensor-compiler/taco/HEAD/README.md>
  - <https://raw.githubusercontent.com/tensor-compiler/taco/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/tensor-compiler/taco/HEAD/src/codegen/module.cpp>
  - <https://github.com/tensor-compiler/taco/tree/master/include/taco/index_notation>
  - <https://raw.githubusercontent.com/tensor-compiler/taco/HEAD/include/taco/index_notation/transformations.h>
  - <https://raw.githubusercontent.com/tensor-compiler/taco/HEAD/include/taco/index_notation/index_notation.h>
  - <https://raw.githubusercontent.com/tensor-compiler/tensor-compiler.github.io/HEAD/files/kjolstad-oopsla17-tensor-compiler.pdf>
  - <https://github.com/tensor-compiler/taco/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/tensor-compiler/taco/issues/297>
  - <https://github.com/tensor-compiler/taco/issues/514>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/tensor-compiler/taco`) · [data/wave8/enrich/raw/github_com_tensor_compiler_taco.json](../../../data/wave8/enrich/raw/github_com_tensor_compiler_taco.json) (enrichment confidence 0.75)

</details>
