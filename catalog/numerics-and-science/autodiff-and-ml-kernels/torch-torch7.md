# Torch7

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `BSD-3-Clause` · 🟡 stale

> Lua-scripted C tensor library (TH) behind the Torch7 framework; a 2015-16 Bosch study found it fastest on CPU versus Caffe and Theano.

| | |
|---|---|
| **Beats** | Caffe (BVLC) and Theano |
| **Claimed result** | Paper conclusion: 'Torch results in best performance when comparing CPU times'. LeNet batch 64, ms gradient / forward, 12 threads: Torch 16.5 / 4.6 (arXiv v3; 31.6 / 14.0 in v1), Caffe 66.4 / 33.7, Theano 204.3 / 78.7; so about 4.0x faster than Caffe on gradient and 12x faster than Theano (derived from the v3 figures; about 2.1x and 6.5x on v1). Torch 1 thread: 46.1 / 18.1 (v3), 70.4 / 29.0 (v1). Neon 545.6 / 172.7 on one thread. |
| **Workload** | LeNet CPU timing, per-batch gradient computation and forward pass at batch size 64, Torch with 12 threads against Caffe and Theano with 12 threads (Bahrampour et al., Robert Bosch research; the paper also covers AlexNet and a stacked autoencoder). |
| **Metric** | latency |
| **Adoption** | 9.1k stars, 2.3k forks |
| **Last commit** | 2025-03-31 |
| **Links** | [repository](https://github.com/torch/torch7) · [benchmark](https://github.com/DL-Benchmarks/DL-Benchmarks) |

## Verdict

Bahrampour et al. (Robert Bosch, arXiv 1511.06435, ICLR 2016 workshop) timed a modified LeNet at batch 64 on a six-core Hyper-Threading CPU, Torch at 1/6/12 threads against Caffe fixed at 12 threads, Theano at 6/12 and Neon at 1, and concluded Torch was best on CPU (about 4x Caffe's gradient time per v3 search snippets, 16.5 vs 66.4 ms); the per-cell milliseconds, CPU model and BLAS remain unread because arxiv.org is blocked here. The public companion code (DL-Benchmarks, MIT) confirms the network, batch size, 200 warm-up and 200 timed iterations, float32 Torch tensors and 12 Torch threads, but its README publishes only GPU (M40, cuDNNv4) updates, where Torch leads only LeNet forward.

## Use it when

- Maintaining or reproducing existing Lua Torch7 research code (2014-2017 models, .t7 files) on CPU
- Small CPU-bound convnets at batch sizes of tens of images, where batch-level OpenMP over many cores helps and the study's LeNet setting (batch 64, 12 threads) applies
- Embedding a compact BSD-licensed C tensor library (lib/TH, C99/gnu99, optional BLAS/LAPACK) where ATen's C++ build is too heavy
- Historical baselines: comparing a new kernel against the framework most 2015-era convnet benchmarks used

## Skip it when

- Any new project: the README says 'Torch is not in active development' and that the TH/THNN backend continues as ATen in PyTorch; the community was 'close to non-existent' by 2019
- GPU training of larger models: in the study authors' own updated M40/cuDNNv4 table Torch is slowest on AlexNet gradient (408.8 ms vs Neon 247.0 and Caffe 279.3) and on LSTM (93.2 ms vs Theano 17.3); in soumith/convnet-benchmarks its native GPU convolution is slightly slower than Caffe's
- Modern platforms: open issues report install failures on Apple M1 (#1240), AArch64 Fedora 33 (#1231), Ubuntu 20.04 under WSL (#1245) and current CUDA/cuDNN combinations
- Builds without a tuned BLAS: if CMake does not find one, gemm/gemv fall back to unblocked triple loops and the CPU speed advantage disappears
- NumPy-style code: TH has no broadcasting (the README says ATen added it), and Python users have no supported binding

## How it is fast

Dense work goes to the system BLAS: THBlas gemm/gemv call sgemm_/dgemm_ when CMake finds a BLAS (torch/distro builds OpenBLAS with USE_OPENMP=1), and fall back to naive triple loops otherwise. Elementwise ops use runtime-dispatched SSE/AVX/AVX2/NEON/VSX kernels (THVectorDispatch) and OpenMP loops above TH_OMP_OVERHEAD_THRESHOLD = 100000 elements. Convolution in nn is im2col plus GEMM (THNN SpatialConvolutionMM), and its forward and input-gradient passes run '#pragma omp parallel for' across the images of a batch; Caffe's native convolution loops over images serially and relies on BLAS threads, which is a plausible reason Torch scaled better on the small LeNet GEMMs (an inference, not stated by the study).

## Compared with alternatives

Pick Torch7 over PyTorch only to keep legacy Lua Torch code running; PyTorch inherited the same TH kernels through ATen and is maintained. Against Caffe, Torch7 was the faster CPU option in the Bosch study but not on GPU convolution; for a tiny dependency-free C network on CPU, KANN is the smaller choice.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | Lua 5.1 or LuaJIT (distro default LUAJIT21), luarocks packages paths and cwrap, CMake; optional BLAS (OpenBLAS or MKL), LAPACK and OpenMP; torch/nn for neural-network layers |
| **Minimum toolchain** | C99 (gnu99) compiler, CMake 2.8 (2.8.12 on macOS); GCC 4.6.2+ for OpenMP on macOS per CMakeLists.txt |
| **Platforms** | Linux and macOS primarily (torch/distro scripts for Ubuntu, Fedora, Arch, openSUSE, Debian, CentOS); Windows via CMake build commands in the rockspec; SIMD paths for x86 SSE/AVX/AVX2, ARM NEON and ppc64le VSX, disableable with TH_NO_AVX2, TH_NO_AVX, TH_NO_SSE, TH_NO_VSX |
| **Thread safety** | not documented; ops parallelize internally with OpenMP and torch.setnumthreads sets the process-wide OpenMP thread count (THSetNumThreads calls omp_set_num_threads); tensor refcounts and the heap counter use atomics |
| **Drop-in for the baseline** | no |

## Gotchas

- The measured 'Torch' is torch7 plus torch/nn (THNN) plus whatever BLAS was linked; the convolution kernel credited for the CPU win lives in torch/nn, not in this repository.
- Study harness (DL-Benchmarks/DL-Benchmarks, read this session): Torch timing covers model:forward and model:backward only and excludes the ClassNLLCriterion, while Caffe's 'caffe time' includes its DummyData and SoftmaxWithLoss layers and feeds constant input. The Theano LeNet uses the legacy theano.tensor.nnet.conv.conv2d op, and theano/readme.txt gives the CPU command as THEANO_FLAGS='device=cpu' with no floatX=float32, so unless a local .theanorc overrode Theano's float64 default the CPU Theano rows ran in double precision while Torch set torch.FloatTensor (the paper, which might state the setting, was not reachable). Both tilt the comparison toward Torch, the floatX point mainly against Theano; the Torch and Theano scripts ship configured for GPU (conf.mode = 'GPU'; Torch's 12 threads hard-coded).
- SpatialConvolutionMM keeps an unfolded im2col buffer for the whole batch (finput is batch x kW\*kH\*nInputPlane x outH\*outW), so memory grows with batch size; accGradParameters runs serially over the batch.
- TH memory is invisible to the Lua garbage collector except through THSetGCHandler heap-size heuristics, so Lua code that churns tensors can hold large amounts of memory until a collection runs.

## Known shortcomings

- Snippet-only: the Bahrampour paper (arXiv 1511.06435) is unreachable (arxiv.org, web3.arxiv.org, hgpu.org ENOTFOUND), so the LeNet CPU figures (16.5 ms gradient vs Caffe 66.4, Theano 204.3, 12 threads) are unverified, confidence 0.35. Timings measure the whole framework (torch/nn plus BLAS), not the torch7 core; convnet-benchmarks shows native Torch-7 not faster than Caffe on GPU. Stale, README says not in active development (last commit 2025-03-31).
- Enricher: the benchmark code is public (DL-Benchmarks/DL-Benchmarks, MIT) but theano/readme.txt's CPU command never sets floatX, so the Theano rows probably ran float64 against Torch's FloatTensor; Theano used legacy conv.conv2d; Torch timing leaves out the criterion while caffe time includes loss and DummyData; the 12x-over-Theano figure is therefore suspect, and the CPU win most likely comes from torch/nn SpatialConvolutionMM running OpenMP across the batch, not from torch7 itself. In the authors' GPU table Torch is slowest on AlexNet (408.8 vs 247.0/279.3 ms) and LSTM (93.2 vs 17.3).

## Caveats and trade-offs

SNIPPET ONLY: arxiv.org, web3.arxiv.org, hgpu.org, openreview.net and ar5iv were unreachable, so the paper was not opened; the LeNet millisecond figures come from WebSearch results and must be re-read on the paper (a later search snippet attributing 25/46 ms Torch and 121/203 ms Caffe figures to the study looks like a mix-up with the AlexNet rows of soumith/convnet-benchmarks and should be ignored). CPU model, library versions, BLAS backend and build flags were not seen. Peer review is only an ICLR 2016 workshop track (v2) plus arXiv v3, 2015-2016 vintage. The measured 'Torch' is the whole framework (torch7 tensors plus the separate torch/nn modules and whatever BLAS it was linked against), so the CPU win cannot be credited to the torch7 repository alone; Caffe was built for a fixed 12 threads. In the reachable soumith/convnet-benchmarks README (6-core i7-5930K, Titan X) Torch-7 native GPU convolution (SpatialConvolutionMM, which lives in torch/cunn) is not faster than Caffe: AlexNet 342 ms vs 324 ms, Overfeat 878 vs 823, OxfordNet 1105 vs 1068, layer-wise 1265 vs 1231 ms; the fast rows there are cuDNN or fbfft kernels called through Torch bindings. The Theano paper (arXiv 1605.02688, via search snippet) reports Theano slightly faster than Torch on an LSTM benchmark. The README states 'Torch is not in active development'; the last commits (2025-03-31) are merged typo and build-fix pull requests. [retier] Theano rows likely float64 vs Torch float32; Theano legacy conv.conv2d; Torch timing excludes the criterion, Caffe includes loss and DummyData; CPU win from torch/nn SpatialConvolutionMM OpenMP batch parallelism; Torch slowest on GPU AlexNet (408.8 vs 247.0/279.3 ms) and LSTM (93.2 vs 17.3 ms) in the same tables; stale, not in active development.

Lua front end over C tensor libraries (TH, THNN); the README says 'Torch is not in active development' and that the C backend was rewritten as ATen inside PyTorch, so new work belongs there. Community described as 'close to non-existent' as of 2019.

## Maintenance

Stale: the last commits (2025-03-31) merge a typo fix and an arm64-osx build fix, substantive development stopped in 2017 and the README declares it not in active development; BSD-3-Clause and buildable from source, but treat it as a frozen legacy codebase. The study's benchmark code is public (github.com/DL-Benchmarks/DL-Benchmarks, MIT) and its documented Theano CPU command leaves floatX at the float64 default, so the 12x-over-Theano figure is suspect; tier stays C until the paper's CPU table, hardware, BLAS and floatX setting are read.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The benchmark is a third-party paper (Bahrampour et al., Bosch Research, arXiv 1511.06435, ICLR 2016 workshop) that would rate B, but arxiv.org (and web3.arxiv.org, hgpu.org) do not resolve here and no GitHub copy of the PDF was found; only search snippets confirm the setup (modified LeNet on MNIST, batch 64, Caffe at 12 threads only, Theano and Torch at 6 and 12 threads, Neon one thread) and the conclusion that Torch is best on CPU. The per-cell millisecond figures stay unverified, so C (snippet only).
- **Verifier notes:** Could not open the paper (arxiv.org ENOTFOUND; three WebSearch queries found no GitHub-hosted copy and no snippet with the Table 3 milliseconds), so the record's numbers are unverified and tier stays C. Metadata checked: BSD-3-Clause (COPYRIGHT.txt), 9.1k stars, 2.3k forks, not archived, last commit 2025-03-31, so maintenance_status corrected from abandoned to stale by the 1-3 year rule although the README says Torch is not in active development; convnet-benchmarks figures in caveats confirmed.
- **Fields the verifier corrected:** `maintenance_status`, `caveats`, `benchmark_url`
- **Shortcomings recorded by:** verifier batch-178 (wave 8); enricher w8 pair-042
- **Pages the verifier opened:**
  - <https://github.com/torch/torch7>
  - <https://github.com/torch/torch7/commits>
  - <https://raw.githubusercontent.com/torch/torch7/HEAD/COPYRIGHT.txt>
  - <https://raw.githubusercontent.com/soumith/convnet-benchmarks/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/torch/torch7>
  - <https://github.com/torch/torch7/commits>
  - <https://github.com/torch/torch7/issues>
  - <https://github.com/torch/torch7/issues?q=is%3Aissue+openblas+OR+wrong+OR+crash+OR+segfault>
  - <https://raw.githubusercontent.com/torch/torch7/HEAD/README.md>
  - <https://raw.githubusercontent.com/torch/torch7/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/torch/torch7/HEAD/rocks/torch-scm-1.rockspec>
  - <https://raw.githubusercontent.com/torch/torch7/HEAD/COPYRIGHT.txt>
  - <https://raw.githubusercontent.com/torch/torch7/HEAD/lib/TH/CMakeLists.txt>
  - <https://raw.githubusercontent.com/torch/torch7/HEAD/lib/TH/README.md>
  - <https://raw.githubusercontent.com/torch/torch7/HEAD/lib/TH/THGeneral.h.in>
  - <https://raw.githubusercontent.com/torch/torch7/HEAD/lib/TH/THGeneral.c>
  - <https://raw.githubusercontent.com/torch/torch7/HEAD/lib/TH/generic/THBlas.c>
  - <https://raw.githubusercontent.com/torch/torch7/HEAD/lib/TH/generic/THTensorMath.c>
  - <https://raw.githubusercontent.com/torch/torch7/HEAD/lib/TH/generic/THVectorDispatch.c>
  - <https://raw.githubusercontent.com/torch/nn/HEAD/lib/THNN/generic/SpatialConvolutionMM.c>
  - <https://raw.githubusercontent.com/torch/nn/HEAD/SpatialConvolution.lua>
  - <https://raw.githubusercontent.com/torch/distro/HEAD/install-deps>
  - <https://raw.githubusercontent.com/torch/distro/HEAD/install.sh>
  - <https://github.com/DL-Benchmarks/DL-Benchmarks>
  - <https://github.com/DL-Benchmarks/DL-Benchmarks/tree/master/torch>
  - <https://github.com/DL-Benchmarks/DL-Benchmarks/tree/master/caffe>
  - <https://raw.githubusercontent.com/DL-Benchmarks/DL-Benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/DL-Benchmarks/DL-Benchmarks/HEAD/torch/run.sh>
  - <https://raw.githubusercontent.com/DL-Benchmarks/DL-Benchmarks/HEAD/torch/LeNet/lenet.lua>
  - <https://raw.githubusercontent.com/DL-Benchmarks/DL-Benchmarks/HEAD/caffe/run.sh>
  - <https://raw.githubusercontent.com/DL-Benchmarks/DL-Benchmarks/HEAD/caffe/LeNet/lenet_train_test.prototxt>
  - <https://raw.githubusercontent.com/DL-Benchmarks/DL-Benchmarks/HEAD/theano/run.sh>
  - <https://raw.githubusercontent.com/DL-Benchmarks/DL-Benchmarks/HEAD/theano/LeNet/lenet.py>
  - <https://raw.githubusercontent.com/DL-Benchmarks/DL-Benchmarks/HEAD/theano/layers.py>
  - <https://github.com/DL-Benchmarks/DL-Benchmarks/tree/master/theano>
  - <https://raw.githubusercontent.com/DL-Benchmarks/DL-Benchmarks/HEAD/theano/readme.txt>
  - <https://raw.githubusercontent.com/DL-Benchmarks/DL-Benchmarks/HEAD/torch/readme.txt>
  - https://arxiv.org/abs/1511.06435v3 (ENOTFOUND; WebSearch snippets only)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/torch/torch7`) · [data/wave8/enrich/raw/github_com_torch_torch7.json](../../../data/wave8/enrich/raw/github_com_torch_torch7.json) (enrichment confidence 0.55)

</details>
