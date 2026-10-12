# cuSpFFT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `CUDA` · `no license` · 🟢 active

> Course-project CUDA 2-D R2C FFT for binary (0/1) sparse matrices; beats dense cuFFT on mid-size non-power-of-2 inputs.

| | |
|---|---|
| **Beats** | cuFFT (dense 2D real-to-complex) and SpFFT (eth-cscs/SpFFT, CUDA backend) |
| **Claimed result** | benzene: custom binary-sparse pipeline 14.65 ms vs dense cuFFT 23.64 ms ('1.61x faster, 10.7x less memory'); variant using cuFFT inside 9.60 ms ('2.46x faster, 10.4x less memory'); SpFFT about 32 ms ('0.74x speed'). pct20stif (52,329 x 52,329): dense cuFFT plan creation failed and SpFFT ran out of device memory, the sparse variants completed in 2,569 ms and 893 ms. |
| **Workload** | Single-precision 2D real-to-complex FFT of binary sparse matrices from SuiteSparse (benzene 8,219 x 8,219, density 0.36%), median of 10 runs after one warm-up, CUDA-event timing. |
| **Metric** | throughput |
| **Hardware** | NVIDIA GeForce RTX 4090 24 GB (compute capability 8.9), driver 555.42.02, Linux x86_64; host CPU not stated |
| **Compiler and flags** | nvcc from CUDA Toolkit 12.5.82, CMake 3.20+, C++17; -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=native; CMakeLists.txt adds CUDA options --expt-relaxed-constexpr -lineinfo |
| **Adoption** | 1 star, 1 fork, 13 commits |
| **Last commit** | 2026-05-24 |
| **Links** | [repository](https://github.com/Darkviper7/cuSpFFT) · [benchmark](https://github.com/Darkviper7/cuSpFFT) |

## Verdict

On one RTX 4090 (CUDA 12.5.82, Release, sm_89), median of 10 runs after a warm-up, the cuFFT-backed sparse variant ran benzene (8,219^2, 0.36% dense) in 9.60 ms and the fully custom one in 14.65 ms vs 23.64 ms for dense cuFFT R2C (2.46x and 1.61x), with about one tenth of the device memory; it loses on small and power-of-2 matrices, and SpFFT (\~32 ms, single run) was slower than dense.

## Use it when

- 2-D FFT of graph adjacency or other 0/1 sparsity patterns with a few thousand to \~65k rows, densities around 0.1-0.4%, and a non-power-of-2 width (benzene 8,219^2: 9.60 ms vs 23.64 ms dense cuFFT on an RTX 4090).
- Inputs where dense cuFFT cannot plan or fit in device memory (pct20stif 52,329^2: dense plan creation failed and SpFFT ran out of memory; the cuFFT-backed sparse variant finished in 893 ms).
- Memory-constrained GPUs: the sparse variants used 310-317 MB vs 3,305 MB for dense cuFFT on benzene; the experimental streaming flag ran pct20stif at about 474 MB.
- As a worked example of Bluestein-at-smooth-length plus tiled sparse front ends on CUDA (README documents factorizations, Nsight profiles and ablations).

## Skip it when

- Power-of-2 widths: delaunay_n14 (16,384^2) took 68.56 ms (cuFFT-backed) and 304.76 ms (custom) vs 7.81 ms for dense cuFFT, because Bluestein doubles the transform length and the pipeline runs five passes.
- Small matrices: on sstmodel (3,345^2) dense cuFFT took 0.85 ms vs 1.39 ms and 3.62 ms for the sparse variants.
- Weighted (non-binary) sparse data: values are discarded on read, so the output is the FFT of the sparsity pattern, not of the matrix.
- Matrices with more than 65,536 rows: the pass-1 phase index is computed as ((uint32_t)u \* (uint32_t)r) % rows, which wraps once rows^2 exceeds 2^32 and would give wrong twiddles for non-power-of-2 row counts (not tested by the repo, whose largest case has 52,329 rows).
- Any shipped product: there is no licence file, so the code is reference-only; it is a CSC 766 course submission with 13 commits and no releases.

## How it is fast

Pass 1 walks a compact CSC (empty columns dropped, no values array, uint16_t indices when rows and cols are at most 65,536) and computes the row-direction DFT directly from the nonzeros, one (output-row tile, column) block per CUDA block with no atomics. The column-direction DFT of arbitrary width is done with Bluestein's chirp-z convolution at a smooth length (3-smooth for the custom radix-2/3/fused-9 Stockham FFT, 7-smooth for the cuFFT-backed variant) instead of padding to a power of two. Output rows are processed in tiles of 128, so scratch memory is 2 x tile x fft_len complex values rather than a dense input plus cuFFT workspace, which is where the \~10x memory saving comes from.

## Compared with alternatives

The GPU FFT siblings (VkFFT, tcFFT, TurboFFT) are dense uniform FFTs and win whenever the dense grid fits and the width is FFT-friendly; FINUFFT/cuFINUFFT handles nonuniform points and MPSFT targets spectra with few large coefficients. Pick cuSpFFT only to study or adapt an input-sparse, binary-valued 2-D transform whose dense cuFFT plan is too large or whose width is awkward (large prime factors), keeping in mind it cannot be copied without a licence.

## Integration

| | |
|---|---|
| **Form** | source-drop (single CMake executable; no installable library target) |
| **Dependencies** | CUDA Toolkit 12.x with cuFFT, cuBLAS, cuSPARSE and NVTX; optional SpFFT (CUDA, single precision) and FFTW3 single precision for baselines and correctness checks |
| **Minimum toolchain** | CMake 3.20+, C++17 host compiler, nvcc from CUDA 12.x (tested with 12.5.82); CMake falls back to sm_80 when no architecture is given |
| **Platforms** | Linux x86_64 with an NVIDIA GPU (tested on RTX 4090, compute capability 8.9) |
| **Thread safety** | not documented (functions launch on the default stream and allocate per call) |
| **Drop-in for the baseline** | partial — produces the same R2C half-spectrum as cufftExecR2C for 0/1 inputs, but takes a COO matrix instead of a dense array, pads the output row stride to a multiple of 4 complex values, and has no plan/exec API |

## Gotchas

- Reported times are CUDA-event timings of the transform loop only: host COO-to-CSC conversion, index uploads and the Bluestein kernel precompute are outside the timed region, as are dense densification and cufftPlan2d for the baseline.
- Accuracy is lower than dense cuFFT: max_abs error vs the FFTW single-precision reference on benzene is 2.0e-01 for the custom FFT path and 6.3e-02 for the cuFFT-backed path vs 4.7e-02 for dense cuFFT (twiddles use the fast __sincosf intrinsic).
- The reported non-streaming variants keep the full output on the device (about 11 GB for pct20stif); only the experimental --csc-stockham-cufft-stream path bounds memory by tile size.
- Default --csc-tile is 1024 while the reported runs use 128, and --repeat defaults to a single run with no warm-up; pass --csc-tile 128 --repeat 10 to match the README tables.

## Known shortcomings

- Slower than dense cuFFT on sstmodel and delaunay_n14; the custom variant is less accurate (max_abs 2.0e-01 vs 4.7e-02); no license (reference only).
- Latent bug: the phase index ((uint32)u\*r)%rows wraps when rows exceed 65,536, giving wrong twiddles for non-power-of-2 row counts (largest tested case 52,329 rows, so no reported number is affected); timed region excludes host COO-to-CSC conversion and the Bluestein precompute.

## Caveats and trade-offs

Course project (CSC 766) with no licence file (LICENSE 404, none shown on GitHub), so the code must not be copied. Wins only on mid-size non-power-of-2 sparse binary inputs: on sstmodel dense cuFFT takes 0.85 ms vs 1.39 ms and 3.62 ms for the sparse variants, and on the power-of-2 delaunay_n14 dense cuFFT takes 7.81 ms vs 68.56 ms and 304.76 ms. The fully custom variant is less accurate than dense cuFFT against the FFTW3 CPU reference (max_abs 2.0e-01 vs 4.7e-02 on benzene). The SpFFT figure is a single run. The dense baseline times only cufftExecR2C (plan creation and densification excluded). Host CPU not stated; the result is a GPU-kernel timing on one RTX 4090. The baseline is a dense GPU FFT that the workload is deliberately unfavourable to; not a general FFT speedup.

Only for binary (all-ones) sparse 2D inputs in CSC form; Bluestein convolution at a smooth length; needs CUDA; the custom variant is less accurate than dense cuFFT (max_abs vs FFTW CPU reference 2.0e-01 vs 4.7e-02 on benzene).

## Maintenance

Finished course project (final submission April 2026, last commit a .gitignore change on 2026-05-24) with no licence, so treat it as reference material rather than a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now A.
- **Tier reason:** Upgraded from C. The benchmark code that runs dense cuFFT, SpFFT and the sparse variants is public (src/main.cu driver, src/dense_baseline.cu, src/sparse_fft_bluestein.cu, scripts/download_matrices.sh); the compiler (nvcc, CUDA 12.5.82), flags (CMakeLists.txt: Release, C++17, --expt-relaxed-constexpr -lineinfo, CUDA_ARCHITECTURES=native) and the GPU (RTX 4090, driver 555.42.02) are stated. This matches the wave's precedent for GPU kernels that name the GPU (vsj001 SpMV, blackwell-tensorcore-kernels).
- **Verifier notes:** All README numbers verified (benzene 23.64 / 14.65 / 9.60 ms, \~32 ms SpFFT, pct20stif 2,569 and 893 ms, losses on sstmodel and delaunay_n14). Upgraded to A on the reproducibility rule, but the code is unlicensed (reference only). Shortcomings worth recording: losses on small and power-of-2 inputs, lower accuracy of the custom variant.
- **Fields the verifier corrected:** `compiler_and_flags`, `last_commit`, `maintenance_status`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Darkviper7/cuSpFFT>
  - <https://raw.githubusercontent.com/Darkviper7/cuSpFFT/HEAD/README.md>
  - <https://github.com/Darkviper7/cuSpFFT/commits>
  - <https://raw.githubusercontent.com/Darkviper7/cuSpFFT/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Darkviper7/cuSpFFT/HEAD/src/main.cu>
  - <https://raw.githubusercontent.com/Darkviper7/cuSpFFT/HEAD/src/dense_baseline.cu>
  - <https://raw.githubusercontent.com/Darkviper7/cuSpFFT/HEAD/src/sparse_fft_bluestein.cu>
- **Sources the enricher read:**
  - <https://github.com/Darkviper7/cuSpFFT>
  - <https://github.com/Darkviper7/cuSpFFT/commits>
  - <https://raw.githubusercontent.com/Darkviper7/cuSpFFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/Darkviper7/cuSpFFT/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Darkviper7/cuSpFFT/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Darkviper7/cuSpFFT/HEAD/src/main.cu>
  - <https://raw.githubusercontent.com/Darkviper7/cuSpFFT/HEAD/src/dense_baseline.cu>
  - <https://raw.githubusercontent.com/Darkviper7/cuSpFFT/HEAD/src/sparse_fft_bluestein.cu>
  - <https://raw.githubusercontent.com/Darkviper7/cuSpFFT/HEAD/src/mtx_reader.cu>
  - <https://raw.githubusercontent.com/Darkviper7/cuSpFFT/HEAD/include/sparse_fft_internal.cuh>
  - <https://raw.githubusercontent.com/Darkviper7/cuSpFFT/HEAD/include/sparse_fft.h>
  - <https://raw.githubusercontent.com/Darkviper7/cuSpFFT/HEAD/scripts/download_matrices.sh>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/darkviper7/cuspfft`) · [data/wave8/enrich/raw/github_com_darkviper7_cuspfft.json](../../../data/wave8/enrich/raw/github_com_darkviper7_cuspfft.json) (enrichment confidence 0.75)

</details>
