# Numerics and science

<sub>[fastpp](../../README.md) › [Catalog](../README.md)</sub>

BLAS, FFT, sparse solvers, big integers, random numbers, geometry and ML kernels measured against MKL, FFTW, GMP, Eigen and their peers.

**455 entries in 7 categories:** 76 tier A · 90 tier B · 259 tier C · 30 tier D

| Category | Entries | A | B | C | D | What they beat |
|---|--:|--:|--:|--:|--:|---|
| [Autodiff and ML kernels](autodiff-and-ml-kernels/README.md) | 102 | 12 | 22 | 66 | 2 | oneDNN, cuDNN, XNNPACK, Eigen tensor |
| [Big integers and arbitrary precision](big-integer-arbitrary-precision/README.md) | 43 | 10 | 4 | 26 | 3 | GMP, MPFR |
| [BLAS and LAPACK](blas-lapack/README.md) | 63 | 14 | 13 | 28 | 8 | OpenBLAS, Intel MKL, Eigen, BLIS |
| [FFT](fft/README.md) | 49 | 13 | 9 | 21 | 6 | FFTW, MKL FFT, KissFFT |
| [Geometry and spatial](geometry-spatial/README.md) | 76 | 5 | 12 | 55 | 4 | Boost.Geometry, CGAL, GEOS, R-tree baselines |
| [Random and quasi-random numbers](random-and-quasi-random/README.md) | 62 | 15 | 5 | 39 | 3 | std::mt19937, PCG, xoshiro |
| [Sparse matrices and solvers](sparse-and-solvers/README.md) | 60 | 7 | 25 | 24 | 4 | SuiteSparse, Eigen sparse, PETSc |

## Most-adopted tier A picks

Tier A, copyable and actively maintained, ordered by GitHub stars.

| # | Project | What it is | Category | Tier | Language | License | Status |
|--:|---|---|---|:-:|---|---|---|
| 1 | [**FlashAttention-4 (CuTeDSL, Hopper/Blackwell)**](autodiff-and-ml-kernels/paper-flashattention-4.md) | Blackwell/Hopper exact attention kernels in CuTe-DSL; beat cuDNN 9.13 by 1.04-1.29x on B200, roughly tie cuDNN 9.19. | [Autodiff and ML kernels](autodiff-and-ml-kernels/README.md) | **A** | Python | BSD-3-Clause | 🟢 active |
| 2 | [**FlashAttention-3 (flash-attention)**](autodiff-and-ml-kernels/dao-ailab-flash-attention.md) | Fused exact-attention CUDA kernels (FA2/FA3); FA3 on H100 is 1.5-2x faster than FA2 and beats cuDNN at sequence lengths of 1k and up. | [Autodiff and ML kernels](autodiff-and-ml-kernels/README.md) | **A** | CUDA/C++ | BSD-3-Clause | 🟢 active |
| 3 | [**MatX**](fft/nvidia-matx.md) | NumPy-style C++20 GPU array library whose JIT fusion of a cuFFT pipeline ran 1.61x faster than handwritten CUDA + cuFFT. | [FFT](fft/README.md) | **A** | C++ | BSD-3-Clause | 🟢 active |
| 4 | [**Spectra**](sparse-and-solvers/yixuan-spectra.md) | Header-only C++/Eigen implicitly restarted Arnoldi/Lanczos eigensolver; ARPACK redesign, modestly faster than ARPACK-NG in the author's dense tests. | [Sparse matrices and solvers](sparse-and-solvers/README.md) | **A** | C++ | MPL-2.0 | 🟢 active |
| 5 | [**Fastor**](autodiff-and-ml-kernels/romeric-fastor.md) | Header-only C++ fixed-size tensor library whose small-GEMM kernels match MKL JIT and beat padded Blaze. | [Autodiff and ML kernels](autodiff-and-ml-kernels/README.md) | **A** | C++ | MIT | 🟢 active |
| 6 | [**jc_voronoi**](geometry-spatial/jcash-voronoi.md) | Single-header C99 Fortune-sweep 2D Voronoi/Delaunay generator, 1.4-3.7x faster than Boost.Polygon voronoi on random points. | [Geometry and spatial](geometry-spatial/README.md) | **A** | C | MIT | 🟢 active |
| 7 | [**TG (tidwall geometry library)**](geometry-spatial/tidwall-tg.md) | Single-file C11 planar geometry library whose indexed point-in-polygon and intersects tests beat GEOS PreparedGeometry by about 1.1-2.7x. | [Geometry and spatial](geometry-spatial/README.md) | **A** | C | MIT | 🟢 active |
| 8 | [**fast.cu (H100 BF16 matmul and sum-reduction kernels)**](autodiff-and-ml-kernels/pranjalssh-fast-cu.md) | From-scratch Hopper BF16 GEMM (TMA + WGMMA) beating cuBLAS by 2-7% on square H100 matmuls, plus a CUB-level reduction. | [Autodiff and ML kernels](autodiff-and-ml-kernels/README.md) | **A** | C++ | MIT | 🟢 active |
| 9 | [**Malachite**](big-integer-arbitrary-precision/mhogrefe-malachite.md) | Pure-Rust port of GMP/FLINT integer algorithms; beats GMP (via rug) on sub-64-bit values and string parsing, not on large operands. | [Big integers and arbitrary precision](big-integer-arbitrary-precision/README.md) | **A** | Rust | LGPL-3.0-only | 🟢 active |
| 10 | [**HipKittens (AMD) / ThunderKittens sibling**](autodiff-and-ml-kernels/hazyresearch-hipkittens.md) | C++ tile-primitive kernel DSL for AMD Instinct GPUs; its GQA attention backward runs about 3x faster than AITER on MI355X. | [Autodiff and ML kernels](autodiff-and-ml-kernels/README.md) | **A** | C++ | MIT | 🟢 active |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
