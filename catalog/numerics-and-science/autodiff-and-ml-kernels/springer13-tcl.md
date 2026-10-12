# TCL (Tensor Contraction Library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `LGPL-3.0` · 🔴 abandoned

> Multithreaded C++ tensor contraction library (TTGT over BLAS + HPTT); up to 18x over the best of Eigen Tensor, NumPy, ITensor and Tensor Toolbox.

| | |
|---|---|
| **Beats** | Eigen Tensor, Tensor Toolbox, NumPy, ITensor |
| **Claimed result** | Speedup over the best reference among Eigen, Tensor Toolbox, NumPy and ITensor, 'reaching up to 18x' for low arithmetic intensity contractions |
| **Workload** | 1000 random tensor contractions on 24 threads (TTGT-based contraction). |
| **Metric** | throughput |
| **Hardware** | 2-socket Intel Haswell-EP E5-2680 v3, 24 threads |
| **Compiler and flags** | README lists tested compilers g++ 5.1.0 and icpc 17.0.2; compiler and flags used for the benchmark not stated |
| **Adoption** | 55 stars |
| **Last commit** | 2019-08-22 |
| **Links** | [repository](https://github.com/springer13/tcl) · [benchmark](https://github.com/springer13/tcl) |

## Verdict

The author measured 1000 random contractions on a 2-socket Intel Xeon E5-2680 v3 (Haswell-EP, 24 threads) against the fastest of Eigen Tensor, Tensor Toolbox, NumPy and ITensor for each case; TCL was faster on every case, up to 18x at low arithmetic intensity, falling toward parity as GEMM dominates. Compiler and flags for the run are not stated; first-party only.

## Use it when

- CPU dense tensor contractions with many index permutations (quantum chemistry, tensor networks) where Eigen Tensor or numpy.einsum is the bottleneck
- Low-arithmetic-intensity contractions (small contracted dimensions), where the README reports the largest gains (up to 18x)
- Multicore x86 servers with a multithreaded BLAS and pinned threads (benchmark: 2-socket Haswell-EP, 24 threads)
- Python code using einsum that can call tcl.tensorMult instead

## Skip it when

- Concurrent contractions from several threads: a global MemoryBroker is not thread-safe (issue #3, assertion failure under OpenMP)
- Memory-constrained runs: TTGT needs auxiliary buffers for the transposed tensors (README limitation); GETT, which avoids them, was never added
- GEMM-dominated (high arithmetic intensity) contractions, where speedup falls toward 1x because any BLAS-backed library hits peak
- Projects needing maintenance or GPU support: abandoned since 2019; the author points to NVIDIA cuTENSOR
- Sparse or symmetric tensors: dense contractions only

## How it is fast

It uses the Transpose-Transpose-GEMM-Transpose (TTGT) approach: operands are permuted with HPTT, a high-performance tensor transposition library, into layouts that turn the contraction into one large GEMM on a tuned BLAS (BLIS, MKL, OpenBLAS). The speedup comes mostly from fast transpositions, so it is largest for low-arithmetic-intensity contractions where transposes dominate.

## Compared with alternatives

It is the only general tensor-contraction entry in the category; pick it over hand-rolled transposes plus a GEMM kernel (e.g. the AVX-512 DGEMM sibling) when contractions have arbitrary index orders, and prefer T-MAC or llamafile for quantized LLM matmul instead.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | HPTT, a BLAS (BLIS by default in the Makefile; MKL/OpenBLAS/ATLAS), OpenMP |
| **Minimum toolchain** | C++11; tested with g++ 5.1.0 and icpc 17.0.2 |
| **Platforms** | x86-64 Linux as tested; Makefile builds with -march=native |
| **Thread safety** | Internally multithreaded via OpenMP; not safe to call concurrently (global MemoryBroker, issue #3) |
| **Drop-in for the baseline** | no |

## Gotchas

- Plain Makefile with -march=native: you must edit HPTT_ROOT/BLIS_ROOT paths, and the binary is not portable to other CPUs
- Set thread affinity (KMP_AFFINITY/taskset) and OMP_NUM_THREADS, and link Python against a multithreaded BLAS, or performance suffers (README)
- Index strings define the contraction; layout defaults to column-major, so row-major callers must pass useRowMajor
- LGPL-3.0: static linking into closed-source code carries relinking obligations

## Known shortcomings

- First-party only; speedup vs the best of Eigen/Tensor Toolbox/NumPy/ITensor with no per-library figures; compiler and flags not stated; unmaintained since 2019-08-22 (README points to cuTENSOR).
- Not thread-safe for concurrent calls (global MemoryBroker assertion under OpenMP, issue #3, unfixed); TTGT needs extra memory for transposed tensors; Makefile builds with -march=native.

## Caveats and trade-offs

Speedup is vs the best of several references; per-library numbers not given on the page; old hardware. README states the project is no longer maintained and points to NVIDIA cuTENSOR. LGPL-3.0.

Depends on HPTT transposition library; dual LGPL-3.0/GPL-3.0; unmaintained, author points to NVIDIA cuTensor.

## Maintenance

Abandoned (last commit 2019-08-22, README says no longer maintained), LGPL-3.0; small enough to vendor but expect to fix the thread-safety bug yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** README figure (misc/tcl_speedup.png) shows speedup over the best of Eigen/Tensor Toolbox/NumPy/ITensor on a 2-socket E5-2680 v3, 24 threads, 'reaching up to 18x'; first-party, benchmark script exists (benchmark/python/benchmark.sh) but compiler and flags for the run are not stated.
- **Verifier notes:** Claim and metadata (55 stars, LGPL-3.0, last commit 2019-08-22, abandoned) verified; the author explicitly marks it unmaintained.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/springer13/tcl/HEAD/README.md>
  - <https://raw.githubusercontent.com/springer13/tcl/HEAD/LICENSE>
  - <https://github.com/springer13/tcl>
  - <https://github.com/springer13/tcl/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/springer13/tcl/HEAD/README.md>
  - <https://raw.githubusercontent.com/springer13/tcl/HEAD/include/tcl.h>
  - <https://raw.githubusercontent.com/springer13/tcl/HEAD/include/contract.h>
  - <https://raw.githubusercontent.com/springer13/tcl/HEAD/include/memoryBroker.h>
  - <https://raw.githubusercontent.com/springer13/tcl/HEAD/Makefile>
  - <https://github.com/springer13/tcl/issues>
  - <https://github.com/springer13/tcl/issues/3>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/springer13/tcl`) · [data/wave8/enrich/raw/github_com_springer13_tcl.json](../../../data/wave8/enrich/raw/github_com_springer13_tcl.json) (enrichment confidence 0.8)

</details>
