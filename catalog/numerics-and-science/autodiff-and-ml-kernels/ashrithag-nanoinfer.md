# nanoinfer (int8 GEMM vs cuBLAS)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Educational from-scratch C++ CNN inference engine plus CUDA int8 GEMM; beats cuBLAS only in its slow NN layout.

| | |
|---|---|
| **Beats** | cuBLAS int8 GEMM; ONNX Runtime |
| **Claimed result** | int8 GEMM vs cuBLAS called with row-major B (NN): 2.09x at n=256, 1.26x at 512, 1.24x at 1024, 0.73x at 2048, 0.71x at 4096; vs cuBLAS TN, cuBLAS is 1.6x-4.5x faster at every size. CPU engine vs ONNX Runtime: MNIST 49 vs 48 us (0.99x), Keyword Spotting 110 vs 67 us (0.60x), Visual Wake Words 240 vs 184 us (0.77x) |
| **Workload** | Hand-written CUDA int8 GEMM (WMMA + shared memory) vs cuBLAS at n=256..4096; CPU conv engine vs ONNX Runtime on Apple M4 Pro. |
| **Metric** | latency |
| **Hardware** | NVIDIA RTX 4090 (sm_89) for GPU; Apple M4 Pro for CPU |
| **Adoption** | 0 stars (3 commits) |
| **Last commit** | 2026-09-14 |
| **Links** | [repository](https://github.com/AshrithaG/nanoinfer) · [benchmark](https://github.com/AshrithaG/nanoinfer) |

## Verdict

On an RTX 4090 its best int8 WMMA kernel beat cuBLAS called in NN layout up to n=1024 (2.09x at 256) and lost from 2048 up, while cuBLAS in its proper TN layout is 1.6-4.5x faster at every size. On an Apple M4 Pro (CMake Release, -O3, Accelerate sgemm) the CPU engine measured 49/110/240 us vs ONNX Runtime's 48/67/184 us on the three MLPerf-Tiny-style models, so it is not faster on CPU.

## Use it when

- Learning or teaching how an inference engine is built: every fast path keeps a reference kernel, and the README documents each optimization step and three subtle correctness bugs
- Small batch-1 edge CNNs on Apple Silicon where you want a tiny dependency-free engine and accept 1.0-0.6x of ONNX Runtime speed
- Studying the int8 GEMM optimization ladder on Ada GPUs (dp4a, WMMA, staging, Triton tile/pipeline ablations)
- Tiny fp32 conv layers (3-channel stem, 1x1 pointwise, depthwise) at batch 1 on GPU, where its fused kernels timed faster than cuDNN back-to-back (not yet re-timed without host cost)

## Skip it when

- Any production int8 GEMM: cuBLAS in TN layout is 1.6x-4.5x faster than its best kernel at every size from 256 to 4096
- When you need speed over ONNX Runtime on CPU: it ties on the dense MNIST model and is 1.3-1.7x slower on depthwise models
- int8 for latency on Apple Silicon: its int8 path is 1.5-6x slower than its own fp32 path (74 vs 49 us MNIST, 1426 vs 240 us VWW)
- Models beyond the 11 supported ops (Conv2d, depthwise, Linear, ReLU, pooling, Add, Softmax, Flatten, quantize/dequantize) or anything not NCHW
- Mature dependencies: 3 commits, 0 stars, single author

## How it is fast

CPU: im2col lowering to a BLAS sgemm (Apple Accelerate, which reaches the AMX unit), bias+ReLU fusion, load-time pre-transposed Linear weights, and passing 1x1 convolutions straight to sgemm without im2col. GPU int8 GEMM: WMMA tensor-core fragments with shared-memory tile staging and a 32x32 output tile per warp (four accumulators). GPU conv: direct convolution with fused bias/ReLU epilogue and filters staged in shared memory.

## Compared with alternatives

Pick it only to learn; for a real mobile CNN runtime use MNN, and for fast CPU matmul in LLM inference use llamafile tinyBLAS or T-MAC.

## Integration

| | |
|---|---|
| **Form** | static lib (CMake) built from source |
| **Dependencies** | a BLAS sgemm (Accelerate on Apple, else a blocked fallback) and pthreads; optional CUDA toolkit with cuBLAS and cuDNN for the GPU backend; uv/Python for export and benchmark tools |
| **Minimum toolchain** | C++20, CMake 3.20; CUDA C++17 for the GPU backend (sm_89 default) |
| **Platforms** | macOS/Apple Silicon is the measured target (NEON, SDOT probed at configure time); other platforms use a scalar/blocked fallback; CUDA on NVIDIA Ada |
| **Thread safety** | Not documented; Model::run writes into a per-model arena and ops share a process-wide singleton ThreadPool, so use one Model per thread at most and do not call set_threads concurrently |
| **Drop-in for the baseline** | no |

## Gotchas

- The headline 2.09x/1.26x/1.24x over cuBLAS is against cuBLAS called with row-major B (NN), a slow path; the author retracts it in the same README
- GPU timings in the first tables are back-to-back launches that include about 10 us of host cost per cuBLAS call at small n
- Tensor-core kernels require dimensions that are multiples of 16 (wmma) or 64 (staged); ragged shapes fall back to CUDA-core kernels
- Author states run-to-run noise of about +/-10% on an unpinned laptop; CPU differences under 15% are ties

## Known shortcomings

- Verifier rejected as not faster: beats cuBLAS only in slow row-major NN layout; README says cuBLAS TN is 1.6-4.5x faster at every size; CPU engine 0.60-0.99x of ONNX Runtime. Kept flagged: not faster than incumbent on its proper path.
- int8 path slower than its own fp32 path on M4 Pro; fused fp32 conv beats cuDNN on 3 of 4 batch-1 edge-CNN shapes but loses 3x on 64-to-64 3x3 (host cost included, weak).

## Caveats and trade-offs

Win over cuBLAS only holds for the row-major (NN) call layout and small n; the author concedes it vanishes against cuBLAS TN. CPU side is not faster than ONNX Runtime. Included as flagged/weak evidence only.

Educational engine; int8 path adds latency on AMX-equipped hardware.

## Maintenance

Active as of September 2026 but a single-author learning project (3 commits, 0 stars); MIT-licensed and small enough to read or vendor, not to depend on.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification C, tier now C.
- **Tier reason:** First-party README tables with benchmark binary (ni_bench_cuda) and RTX 4090 / M4 Pro hardware, but no compiler versions/flags beyond CMake Release; the README itself shows it is slower than cuBLAS's proper TN path at every size and slower than or equal to ONNX Runtime on all three CPU models.
- **Verifier notes:** Author concedes the cuBLAS win is an artifact of calling cuBLAS in its slow NN layout; CPU engine is 1.0-0.6x of ORT. If the orchestrator keeps flagged entries, record shortcoming: not faster than incumbent on its proper path.
- **Fields the verifier corrected:** `hardware`, `claimed_speedup`
- **Pages the verifier opened:**
  - <https://github.com/AshrithaG/nanoinfer>
  - <https://raw.githubusercontent.com/AshrithaG/nanoinfer/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/AshrithaG/nanoinfer>
  - <https://raw.githubusercontent.com/AshrithaG/nanoinfer/HEAD/README.md>
  - <https://raw.githubusercontent.com/AshrithaG/nanoinfer/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/AshrithaG/nanoinfer/HEAD/include/nanoinfer/graph.h>
  - <https://raw.githubusercontent.com/AshrithaG/nanoinfer/HEAD/include/nanoinfer/ops.h>
  - <https://raw.githubusercontent.com/AshrithaG/nanoinfer/HEAD/include/nanoinfer/pool.h>
  - <https://raw.githubusercontent.com/AshrithaG/nanoinfer/HEAD/LICENSE>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ashrithag/nanoinfer`) · [data/wave8/enrich/raw/github_com_ashrithag_nanoinfer.json](../../../data/wave8/enrich/raw/github_com_ashrithag_nanoinfer.json) (enrichment confidence 0.85)

</details>
