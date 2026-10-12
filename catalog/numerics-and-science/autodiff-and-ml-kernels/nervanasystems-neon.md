# Nervana neon (GPU convolution kernels)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `Python` · `Apache-2.0` · 🔴 abandoned

> Archived Python deep learning framework whose hand-assembled Maxwell GPU convolution kernels beat cuDNN R4 by 1.2-2x on 2016 ConvNet benchmarks.

| | |
|---|---|
| **Beats** | cuDNN R4 (fp16 and fp32, via Torch bindings) |
| **Claimed result** | OxfordNet model A fp32: neon 320 ms vs cuDNN R4 529 ms (about 1.65x, derived from page data); fp16: 254 vs 471 ms. GoogleNet V1 fp32: 270 vs 470 ms; fp16: 230 vs 462 ms. Overfeat fp32: 211 vs 268 ms; fp16: 176 vs 242 ms. cuDNN R4 won AlexNet: fp16 71 vs 78 ms, fp32 81 vs 87 ms. |
| **Workload** | Full forward+backward pass time (ms) of AlexNet, Overfeat-fast, OxfordNet (VGG model A) and GoogleNet V1 convolution stacks on a Titan X in the convnet-benchmarks shootout. |
| **Metric** | throughput |
| **Hardware** | 6-core Intel Core i7-5930K @ 3.50GHz + NVIDIA Titan X, Ubuntu 14.04 x86_64 |
| **Adoption** | 3.9k stars; repository archived 2023-01-03 |
| **Last commit** | 2019-05-22 |
| **Links** | [repository](https://github.com/NervanaSystems/neon) · [benchmark](https://github.com/soumith/convnet-benchmarks) |

## Verdict

soumith/convnet-benchmarks (independent; i7-5930K + Titan X, Ubuntu 14.04, full forward+backward, averaged over 10 runs) lists Nervana-neon beside cuDNN R4 via Torch: OxfordNet model A 320 vs 529 ms fp32 and 254 vs 471 ms fp16, GoogleNet V1 270 vs 470 ms fp32 and 230 vs 462 ms fp16, Overfeat 211 vs 268 ms fp32 and 176 vs 242 ms fp16, while cuDNN R4 wins AlexNet. No compiler, driver or CUDA versions are stated, and the kernels benchmarked were the nervanagpu beta release rather than a tagged neon build.

## Use it when

- Reproducing or studying the 2016 convnet-benchmarks results on Maxwell (GTX 9xx, Titan X) or Pascal GPUs, where the SASS kernels were tuned.
- Learning hand-written SASS GEMM and Winograd convolution techniques: the .sass sources, maxas and the Python kernel wrappers are Apache-2.0 (maxas is MIT).
- Legacy neon models that already run on a Maxwell/Pascal box with CUDA 7.x-8.0 and Python 2.7/3 environments of that era.

## Skip it when

- Any new project: the repository was archived on 2023-01-03 with an Intel discontinuation notice, and the last release is v2.6.0 (January 2018).
- Volta, Turing, Ampere, Hopper or later GPUs: maxas is described as an 'Assembler for NVIDIA Maxwell architecture' and nothing in the repo documents support beyond Maxwell/Pascal; pre-Maxwell GPUs fall back to slower CUDA C kernels.
- C++ codebases: the kernels are driven from Python through PyCUDA, with no supported native API.
- Comparisons against current cuDNN: the measured baseline is cuDNN R4, and cuDNN R4 still won AlexNet (71 vs 78 ms fp16, 81 vs 87 ms fp32).
- Modern Python stacks: requirements pin 2016-2018 packages (numpy 1.13.1, Pillow 3.3.2, PyYAML 4.2b1, pycuda &gt;= 2015.1, scikit-cuda 0.5.1).

## How it is fast

The kernels are written directly in NVIDIA SASS (shader assembly) and assembled with maxas, Scott Gray's Maxwell assembler, so register allocation, instruction scheduling and control codes are hand-tuned rather than left to nvcc. For 3x3 stride-1 convolutions the backend uses Winograd minimal filtering, F(2x2,3x3) and F(4x4,3x3) variants for fprop, bprop and weight update, which cuts the multiplies per output. fp16 storage halves memory traffic, and the convnet-benchmarks script passes hand-picked per-layer tile shapes (grid_P, grid_Q, update_size) to each ConvLayer.

## Compared with alternatives

None of the catalogued siblings is a GPU convolution library: NNPACK is the CPU Winograd/FFT convolution counterpart, and LIBXSMM, FeatherCNN and MNN target CPUs. Pick neon only to study or reuse its SASS Winograd/GEMM kernels on Maxwell/Pascal; for current NVIDIA GPUs the cuDNN baseline itself has since added Winograd and is the practical choice.

## Integration

| | |
|---|---|
| **Form** | module (Python package nervananeon; SASS kernels JIT-assembled into cubins on first use) |
| **Dependencies** | PyCUDA, scikit-cuda, numpy, h5py, aeon data loader (separate install), CUDA toolkit with ptxas on PATH, Perl for maxas; MKLML for the CPU backend |
| **Minimum toolchain** | Python 2.7 or 3 (setup.py classifiers), CUDA 7.0-8.0 era toolkit (Makefile searches cuda-8.0, cuda-7.5, cuda-7.0) |
| **Platforms** | Linux and macOS; NVIDIA compute capability 5.0+ for SASS kernels (5.2+ for fp16), 3.0+ via CUDA C fallback kernels; x86 CPUs via MKL |
| **Thread safety** | not documented (the GPU backend owns a PyCUDA context and a cuBLAS handle created at backend init) |
| **Drop-in for the baseline** | no |

## Gotchas

- Kernels are assembled at runtime by running ptxas and maxas.pl and cached under \~/.cache/neon/kernels; issue #416 shows ptxas failing with a floating-point exception for sm_61 under CUDA 9.0, closed without a documented fix.
- Open issue #461 (2019, GTX 1050 Mobile, CUDA 10.0) reports 90.2% misclassification on the MNIST MLP example with the GPU backend while other backends train normally; it never got a reply.
- The suite's fp16/fp32 rows were produced with the separate nervanagpu package (convnew branch) and Nervana's limited-release beta kernels; neon ships a descendant script, neon/backends/convnet-benchmarks.py, that runs the same nets through neon's own NervanaGPU backend (fp16 and AlexNet/BN variants by default).
- The convnet-benchmarks script hard-codes per-layer tile parameters (grid_P, grid_Q, update_size) tuned for the benchmarked shapes, so other layer shapes may not see the same speedup.

## Known shortcomings

- convnet-benchmarks imports the standalone nervanagpu beta kernels (maxas SASS), not the neon repo itself; same lineage but identical kernels not confirmed; archived.
- maxas is a Maxwell-only assembler, nothing past Pascal; open #461: GPU backend 90.2% MNIST error on GTX 1050/CUDA 10, no reply; Python/SASS, not C++.

## Caveats and trade-offs

Numbers compare against cuDNN R4 only; later cuDNN releases added Winograd and other algorithms, so today's gap is likely smaller or reversed (not measured here). The suite states CPU and GPU but no compiler, flags or driver versions. The suite's nervana/README.md says Nervana provided limited-release beta kernels, and its nervana/convnet-benchmarks.py imports the standalone nervanagpu package (convnew branch, kernels assembled with maxas) rather than neon itself; neon later carries a NervanaGPU backend (neon/backends/nervanagpu.py, layer_gpu.py 'mainly used for old benchmarking code'), so the lineage is the same but identical kernels are not confirmed. The fast kernels are hand-written GPU assembly (SASS) driven from Python, not C++. neon's README claims '2x speed of cuDNNv4'; the page shows 1.0-2.0x depending on model and cuDNN wins AlexNet. Repository archived 2023-01-03 with an Intel discontinuation notice.

Python framework with custom GPU kernels; not callable as a C++ library. Intel discontinued the project, so there is no support for newer GPUs or cuDNN versions.

## Maintenance

Abandoned: archived 2023-01-03, last commit 2019-05-22, Intel accepts no patches; Apache-2.0, so the SASS kernels and Winograd wrappers can be copied for study, but they will not run unchanged on GPUs newer than Pascal according to anything the repo documents.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Well-known independent shootout (soumith/convnet-benchmarks) lists Nervana-neon fp16/fp32 rows beside CuDNN[R4] fp16/fp32 on an i7-5930K + Titan X; the benchmark script (nervana/convnet-benchmarks.py) and logs are public but no compiler, flags or library versions are stated, so not A.
- **Verifier notes:** All neon and cuDNN R4 numbers match the convnet-benchmarks README rows (fp16 figures also match nervana/output_fp16.log). Metadata checked on github.com: Apache-2.0, 3.9k stars, archived 2023-01-03, last commit 2019-05-22. Key shortcoming: benchmarked code is the nervanagpu beta-kernel package, not the neon repository as such.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/nervana/README.md>
  - <https://github.com/soumith/convnet-benchmarks/tree/master/nervana>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/nervana/convnet-benchmarks.py>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/nervana/output_fp16.log>
  - <https://raw.githubusercontent.com/NervanaSystems/neon/master/README.md>
  - <https://raw.githubusercontent.com/NervanaSystems/neon/master/neon/backends/nervanagpu.py>
  - <https://raw.githubusercontent.com/NervanaSystems/neon/master/neon/backends/layer_gpu.py>
  - <https://github.com/NervanaSystems/neon>
  - <https://github.com/NervanaSystems/neon/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/NervanaSystems/neon/HEAD/README.md>
  - <https://raw.githubusercontent.com/NervanaSystems/neon/HEAD/setup.py>
  - <https://raw.githubusercontent.com/NervanaSystems/neon/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/NervanaSystems/neon/HEAD/gpu_requirements.txt>
  - <https://raw.githubusercontent.com/NervanaSystems/neon/HEAD/Makefile>
  - <https://raw.githubusercontent.com/NervanaSystems/neon/HEAD/ChangeLog>
  - <https://raw.githubusercontent.com/NervanaSystems/neon/HEAD/neon/backends/nervanagpu.py>
  - <https://raw.githubusercontent.com/NervanaSystems/neon/HEAD/neon/backends/layer_gpu.py>
  - <https://raw.githubusercontent.com/NervanaSystems/neon/HEAD/neon/backends/kernel_specs.py>
  - <https://raw.githubusercontent.com/NervanaSystems/neon/HEAD/neon/backends/winograd_conv.py>
  - <https://raw.githubusercontent.com/NervanaSystems/neon/HEAD/neon/backends/util/check_gpu.py>
  - <https://raw.githubusercontent.com/NervanaSystems/neon/HEAD/neon/backends/convnet-benchmarks.py>
  - <https://raw.githubusercontent.com/NervanaSystems/neon/HEAD/neon/backends/__init__.py>
  - <https://raw.githubusercontent.com/NervanaSystems/neon/HEAD/neon/backends/backend.py>
  - <https://github.com/NervanaSystems/neon>
  - <https://github.com/NervanaSystems/neon/tree/master/neon/backends>
  - <https://github.com/NervanaSystems/neon/issues?q=is%3Aissue+volta>
  - <https://github.com/NervanaSystems/neon/issues?q=is%3Aissue+sass+OR+maxwell+OR+pascal+OR+cuda>
  - <https://github.com/NervanaSystems/neon/issues/416>
  - <https://github.com/NervanaSystems/neon/issues/461>
  - <https://raw.githubusercontent.com/NervanaSystems/maxas/HEAD/README.md>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/nervana/README.md>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/master/nervana/convnet-benchmarks.py>
  - WebSearch: NervanaSystems neon maxas sass kernels Volta V100 sm_70 (no neon-specific answer)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/nervanasystems/neon`) · [data/wave8/enrich/raw/github_com_nervanasystems_neon.json](../../../data/wave8/enrich/raw/github_com_nervanasystems_neon.json) (enrichment confidence 0.75)

</details>
