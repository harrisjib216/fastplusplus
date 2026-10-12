# gpu-compute (SGEMM for Blackwell)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [BLAS and LAPACK](README.md)</sub>

**Tier A** (reproducible public benchmark) · Study only · `CUDA C++` · `no license` · 🟢 active

> Hand-written CUDA SGEMM kernels that beat pedantic-FP32 cuBLAS only on tiny square matrices (N&lt;=256) on an RTX 5080.

| | |
|---|---|
| **Beats** | cuBLAS cublasSgemm with CUBLAS_PEDANTIC_MATH (true FP32) on an RTX 5080 |
| **Claimed result** | Faster than cuBLAS FP32 (pedantic) on every square N from 32 to 256 measured: 8.1 us vs 16.5 us at 32^3 (2.02x), 9.5 vs 16.2 us at 64^3 (1.71x), 9.3 vs 16.2 us at 96^3 (1.75x), 10.9 vs 16.2 us at 128^3 (1.49x), 11.9 vs 16.9 us at 192^3 (1.42x), 13.6 vs 17.8 us at 256^3 (1.30x). Slower everywhere else measured: tall-skinny shapes 0.22x-0.93x (4096x64x4096 is 0.90x), and per results/gemm_tf32.csv the auto kernel is at 3.52 vs 11.46 TFLOP/s at 512^3 (0.31x) and 23.05 vs 36.79 TFLOP/s at 4096^3 (0.63x). |
| **Workload** | Hand-written row-major FP32 SGEMM, square sizes N=32 to 256 (and larger sizes for contrast), timed with CUDA events and checked against cublasSgemm; a 32x32-tile kernel runs one to 64 CTAs. |
| **Metric** | latency |
| **Hardware** | NVIDIA RTX 5080 (Blackwell sm_120, 84 SMs, 15.9 GB) |
| **Compiler and flags** | nvcc from CUDA 13.3 via scripts/build.ps1 (the README's build path): -O3 --use_fast_math -std=c++17 -lineinfo --expt-relaxed-constexpr -arch=sm_120, host MSVC 2022 BuildTools /O2,/std:c++17,/EHsc; CMakeLists.txt alternative uses the same nvcc options with CMAKE_CUDA_ARCHITECTURES=native |
| **Adoption** | 0 stars |
| **Last commit** | 2026-08-25 |
| **Links** | [repository](https://github.com/JohnTitor2003/gpu-compute) · [benchmark](https://github.com/JohnTitor2003/gpu-compute) |

## Verdict

On an RTX 5080 (sm_120, CUDA 13.3, nvcc -O3 --use_fast_math -arch=sm_120, Windows), timed with CUDA events after 15 warm-ups over about 150 ms of back-to-back launches, the auto kernel took 8.1-13.6 us against 16.2-17.8 us for cublasSgemm with CUBLAS_PEDANTIC_MATH on square N=32-256 (2.02x at 32^3, 1.49x at 128^3, 1.30x at 256^3), with max relative error under 1e-6 against cuBLAS. It was slower on every other shape measured.

## Use it when

- Reading material on why launch- or call-overhead dominates tiny GEMMs (FP32, square N of about 32-256) on a big GPU, with a clear fairness write-up (same layout, pedantic math, CUDA events).
- A worked example of the standard SGEMM ladder (naive, smem tile, 8x8 register microtile with transposed A and padded B, split-K, warp-per-row GEMV) in about 400 lines.
- Checking a hypothesis before writing your own size-specialized small-GEMM kernel; the license forbids copying this one.

## Skip it when

- Anything you would ship or publish: the LICENSE is all rights reserved and forbids copying, modification and use in any product, service or benchmark publication.
- Medium and large GEMMs: 0.31x cuBLAS FP32 at 512^3, 0.56x at 1024^3, 0.63x at 4096^3 (23.0 vs 36.8 TFLOP/s).
- Tall-skinny shapes (M=K=4096 or 8192, N=1-128): 0.22x-0.93x of cuBLAS on every one measured.
- When TF32 is acceptable: cuBLAS in TF32 tensor-op mode ran 9.3-9.9 us at 128^3-256^3 in the same CSV, faster than this kernel, so the \~16 us floor is specific to the pedantic FP32 path (derived from page data).
- Shapes the benchmark never tests: every measured dimension is a multiple of 16, and the register-blocked kernels have known edge problems (see gotchas).

## How it is fast

It does not out-compute cuBLAS; it skips work cuBLAS does per call. For small squares launch_auto issues one size-specialized kernel (the classic 32x32 shared-memory tile with one accumulator per thread, 9-64 CTAs for N=80-256; at N&lt;=64 the code actually routes to a single 64x64 register-blocked CTA, although the README credits the 32x32 kernel), which finishes in 8-14 us, while pedantic-FP32 cublasSgemm sits at a roughly constant 16-18 us from 32^3 to 256^3. The README attributes the cuBLAS floor to kernel selection plus a tile sized for large GEMMs; no Nsight counters were captured to confirm it (results/nsight.md says counters were locked).

## Compared with alternatives

Among catalogued GPU GEMM entries it is the only one aimed at tiny launch-bound FP32 shapes; blackwell-tensorcore-kernels (FP16 tensor cores at 8192^3), CUDA-L2 and emugemm-cdna (AMD MI250) target large GEMMs. Because the license forbids reuse, treat it as evidence for the idea rather than as code to adopt.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | CUDA runtime; cuBLAS only for the benchmark |
| **Minimum toolchain** | C++17; README says CUDA 12.8+ (13.x for sm_120); measured with nvcc from CUDA 13.3 and MSVC 2022 host compiler, --use_fast_math |
| **Platforms** | NVIDIA GPUs; measured only on an RTX 5080 (sm_120) under Windows; WMMA TF32 path needs sm_80+; occupancy_splits hard-codes 84 SMs |
| **Thread safety** | not documented; the launchers are stateless and take a cudaStream_t |
| **Drop-in for the baseline** | partial — same math as cublasSgemm for row-major, non-transposed operands, but a different call signature, no ldA/ldB/ldC, and no cuBLAS handle or math modes |

## Gotchas

- Split-K path (N&lt;=128 with M,K&gt;=512): when beta != 0 it skips the memset and atomically adds alpha\*A\*B into the old C, so any beta other than 0 or 1 gives a wrong result; atomicAdd partials also make the sum order nondeterministic.
- The register-blocked kernels (used for M,N&lt;=64, for M or N&gt;384, and for split-K) do float4 loads with no alignment check, so K or N not a multiple of 4 (for example a 33^3 product) should fault with a misaligned-address error; only the 32x32 tiled kernel is fully bounds-safe. Found by reading the code, not by running it.
- The WMMA TF32 kernel ignores beta, overwrites C, and has no edge handling inside a tile, so M and N must be multiples of 16 and K a multiple of 8; the benchmark only runs it when M and N are multiples of 32.
- Built with --use_fast_math, measured on one GPU with one run per CSV and no variance reported; the two CSVs disagree by about 30% on absolute 128^3 times (10.9 vs 14.1 us for this kernel, 16.2 vs 21.7 us for cuBLAS) while the ratio holds (1.49x vs 1.54x).

## Known shortcomings

- Wins only on tiny squares (N 32-256); slower from 512^3 up (0.31x-0.63x) and on skinny shapes (0.22x-0.93x); now all-rights-reserved (first commit was MIT); Windows only.
- Bugs (code read): the split-K path ignores beta (acts as beta=1); float4 loads with no alignment check, so K or N not a multiple of 4 (e.g. 33^3) should fault; README credits a 32x32 tiled kernel at N&lt;=64 but the code uses the 64x64 vec kernel; cuBLAS TF32 ran 9.3-9.9 us at 128-256^3 in the same CSV, so the 16 us floor is path-specific; CSVs differ \~30% on absolute 128^3 times.

## Caveats and trade-offs

The win is cuBLAS's roughly 16 us per-call floor on tiny matrices, not arithmetic throughput; from 512^3 up and on every tall-skinny shape it is slower than cuBLAS FP32. The license was changed from MIT to a view-only 'all rights reserved' text in the second of three commits (same day, 2026-08-25), so the current code cannot be copied, used, or used in a benchmark publication. One GPU, one build, measured on Windows only; compiled with --use_fast_math; the README gives 15 warm-ups and about 150 ms of GPU work per measurement but no run counts or variance.

Only wins in the launch-bound small-square regime (N&lt;=256, used up to about 384); loses on large and tall-skinny shapes; fixed 32x32 tile with one output per thread; row-major C = A@B; includes a labelled WMMA TF32 kernel that does not beat cuBLAS TF32.

## Maintenance

Three commits on one day (2026-08-25), 0 stars, no issues; the license was switched from MIT to view-only in the second commit, so this is reference-only and nothing can be vendored.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** README square-size table and raw results/gemm.csv give kernel vs cublasSgemm (CUBLAS_PEDANTIC_MATH) times; benchmark code is public (gemm/bench_gemm.cu), scripts/build.ps1 states nvcc from CUDA 13.3 with -O3 --use_fast_math -std=c++17 -lineinfo --expt-relaxed-constexpr -arch=sm_120 (MSVC 2022 host /O2), and the GPU is an RTX 5080.
- **Verifier notes:** Numbers match README and results/gemm.csv; the 4096^3 table units are TFLOP/s per results/gemm_tf32.csv. Metadata checked on github.com: LICENSE is all-rights-reserved source-available (usability reference is right), 0 stars, 3 commits, last 2026-08-25, not a fork.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/JohnTitor2003/gpu-compute>
  - <https://github.com/JohnTitor2003/gpu-compute/commits>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/README.md>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/results/gemm.csv>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/results/gemm_tf32.csv>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/gemm/README.md>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/scripts/build.ps1>
- **Sources the enricher read:**
  - <https://github.com/JohnTitor2003/gpu-compute>
  - <https://github.com/JohnTitor2003/gpu-compute/commits>
  - <https://github.com/JohnTitor2003/gpu-compute/tree/main/gemm>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/README.md>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/scripts/build.ps1>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/gemm/README.md>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/gemm/kernels.cuh>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/gemm/bench_gemm.cu>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/results/gemm.csv>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/results/gemm_tf32.csv>
  - <https://raw.githubusercontent.com/JohnTitor2003/gpu-compute/HEAD/results/nsight.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/johntitor2003/gpu-compute`) · [data/wave8/enrich/raw/github_com_johntitor2003_gpu_compute.json](../../../data/wave8/enrich/raw/github_com_johntitor2003_gpu_compute.json) (enrichment confidence 0.8)

</details>
