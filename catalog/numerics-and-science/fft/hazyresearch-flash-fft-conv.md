# FlashFFTConv

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `CUDA/C++ with PyTorch (Python) interface` · `Apache-2.0` · 🟡 stale

> CUDA tensor-core FFT convolution for PyTorch; 1.3x to 7.9x faster than torch.fft (cuFFT) convolution on H100.

| | |
|---|---|
| **Beats** | PyTorch FFT convolution (torch.fft, backed by cuFFT) |
| **Claimed result** | README table (gated convolution, one H100-SXM, all results scaled to batch 64, hidden 768; time units not stated in the table): 5.64x at 256, 7.93x at 1K, 6.64x at 4K, 5.42x at 8K, 2.45x at 16K, 3.22x at 32K, 1.74x at 1M, 1.37x at 2M, 1.30x at 4M (e.g. 1K: 0.29 vs 2.30); memory savings 2.81x-6.65x in the table; README text says 'up to 7.93 times faster than PyTorch FFT convolutions, with up to 8.21 times less memory usage' (the 8.21x memory figure is not in the table). The ICLR paper abstract (per search snippet) says up to 8.7x over PyTorch. |
| **Workload** | Gated long convolution via FFT on one H100-SXM, batch 64, hidden dimension 768, sequence lengths 256 to 4M, bf16/fp16. |
| **Metric** | latency |
| **Hardware** | 1x H100-SXM (also tested on A100) |
| **Compiler and flags** | Nvidia PyTorch container 23.05, PyTorch 2.0, CUDA 12.1 toolkit; CUDA extension built with nvcc -O3 -lineinfo --use_fast_math -std=c++17 --generate-code=arch=compute_80,code=compute_80 and cxx -O3 (csrc/flashfftconv/setup.py) |
| **Adoption** | 355 stars; README says it targets language models such as Monarch Mixer, H3 and Hyena |
| **Last commit** | 2024-12-28 |
| **Links** | [repository](https://github.com/HazyResearch/flash-fft-conv) · [benchmark](https://raw.githubusercontent.com/HazyResearch/flash-fft-conv/HEAD/README.md) |

## Verdict

On one H100-SXM, the README's gated-convolution table (fp16, times in ms per the benchmark script's torch.utils.benchmark mean x 1000, scaled to batch 64 x hidden 768) shows FlashFFTConv at 0.29 vs 2.30 at 1K (7.93x) and 10,049 vs 13,031 at 4M (1.30x) against a PyTorch reference that upcasts to fp32 and uses complex torch.fft.fft/ifft (not rfft). Rows from 16K up were measured at smaller batch/hidden sizes and rescaled, so the comparison favours FlashFFTConv on precision (fp16 vs fp32) and on the baseline's choice of complex rather than real FFT.

## Use it when

- Training or running long-convolution sequence models (Hyena, H3, HyenaDNA, Monarch Mixer) in PyTorch on Ampere or Hopper GPUs.
- Sequence lengths of 256 to 32K, where the README table shows the largest wins (5.4x to 7.9x at 256 to 8K, 2.5x to 3.2x at 16K to 32K).
- Gated and causally padded convolutions, where fusing the gates and padding saves several memory passes and about 6x activation memory.
- fp16/bf16 mixed-precision training where a 1e-2 absolute tolerance against an fp32 reference is acceptable.

## Skip it when

- You need a general FFT (spectra, non-convolution transforms, real-valued output spectra): use cuFFT, VkFFT or tcFFT instead.
- fp32/fp64 accuracy is needed: only fp16 and bf16 inputs are supported, and the tests only assert allclose with atol=1e-2.
- Non-power-of-two FFT sizes, sizes below 256 or above 4,194,304, odd L, or H not a multiple of 16 for FFT sizes above 32K: the module raises NotImplementedError or fails.
- AMD GPUs, pre-Ampere NVIDIA GPUs or C++-only code bases: CUDA-only PyTorch extension (ROCm support is an open request, issue #34).
- Very long sequences (1M to 4M), where the gain falls to 1.3x to 1.7x and memory savings to about 2.8x.

## How it is fast

It writes the FFT as a Monarch decomposition: a length-N DFT becomes small 16x16 or 32x32 DFT matrix multiplies plus twiddle multiplies, which run on tensor cores in fp16/bf16 (separate kernels for 256/1K, 512/2K real-to-real, 4K, 8K, 16K, 32K, and 16x/32x/64x/128x butterfly stages for 64K to 4M). FFT, pointwise multiply by the kernel spectrum and inverse FFT are fused in one kernel, so the intermediate spectra never go to HBM. Causal zero-padding and input/output gating are done inside the kernel (implicit padding), which removes the extra pad and gate passes a PyTorch implementation makes.

## Compared with alternatives

Pick it over tcFFT, TurboFFT or VkFFT when the job is a fused FFT convolution inside a PyTorch training loop (with gating or causal padding) rather than a standalone FFT; those siblings give a general FFT API and compare against cuFFT on the transform alone.

## Integration

| | |
|---|---|
| **Form** | module (PyTorch CUDA extension monarch_cuda built with setup.py, plus the pure-Python flashfftconv package) |
| **Dependencies** | PyTorch 2.0, CUDA toolkit (tested 12.1), einops; the README recommends the NVIDIA PyTorch container 23.05 |
| **Minimum toolchain** | nvcc with C++17 (-std=c++17); CUDA 12.1 tested; build emits compute_80 PTX only |
| **Platforms** | NVIDIA Ampere/Hopper GPUs (tested on A100 and H100; README says 3090/4090 should work); Linux with CUDA |
| **Thread safety** | not documented; the README recommends one FlashFFTConv object per model, shared across layers |
| **Drop-in for the baseline** | partial — replaces a hand-written torch.fft convolution (fft, multiply, ifft, optional pad and gates) with one module call, but needs fp16/bf16 inputs, an fp32 kernel, contiguous (B, H, L) layout and a fixed power-of-two FFT size chosen at construction |

## Gotchas

- The kernel spectrum is still computed with torch.fft in fp32 on every forward call (the code says 'replace this with a kernel'), so precomputing FFT(k) is not supported.
- Input-size rules are enforced by crashes rather than checks: an odd L with implicit padding gives a CUDA 'misaligned address' error (issue #20, open), and a bf16 batch of about 140,000 x 4 x 4096 gives an illegal memory access (issue #27, open).
- Gated variants at 131K and above raise NotImplementedError when use_32_butterfly=False; the FlashDepthWiseConv1d bf16 backward pass has a known bug per the README.
- setup.py hard-codes --generate-code=arch=compute_80,code=compute_80, so Hopper runs JIT-compiled sm_80 PTX rather than sm_90 code; several open issues report build or cudaFuncSetAttribute errors (#6, #19, #29).

## Known shortcomings

- PyTorch baseline runs fp32 while FlashFFTConv runs fp16; rows of 16K and longer are scaled from a smaller batch; README's 8.21x memory claim exceeds its own table's 6.65x max.
- PyTorch baseline upcasts to fp32 and uses complex fft/ifft, not rfft; open crash bugs: misaligned address with odd L under implicit padding (#20), illegal memory access at bf16 batch \~140k (#27); only compute_80 PTX is built (Hopper JIT-compiles); 18 of 25 issues open.

## Caveats and trade-offs

The baseline is PyTorch's FFT convolution (torch.fft, cuFFT), not FFTW, MKL or KissFFT, and is a GPU task, so it only speaks to the cuFFT/PyTorch route. In benchmarks/benchmark_flashfftconv.py the PyTorch reference upcasts inputs to fp32 before torch.fft while FlashFFTConv runs in fp16 (bf16 also supported), so precision is not like-for-like. For sequence lengths of 16K and above the script shrinks batch and hidden size (set_B_H) and the README says results are scaled to batch 64, hidden 768. Gain shrinks to 1.3x at 4M tokens. The 8.21x memory claim in the README text exceeds the 6.65x maximum in its own table. The CUDA extension is compiled for compute_80 PTX only. Last commit December 2024.

FP16 and BF16 only, power-of-two FFT sizes 256 to 4,194,304, Ampere/Hopper GPUs, fused Monarch-decomposition kernels that use tensor cores; computes convolutions, not a general FFT API.

## Maintenance

Stale since December 2024, with 18 of the 25 listed issues open and no maintainer replies on the bug reports checked (#14, #20, #27), but Apache-2.0 and usable as a pinned PyTorch extension on Ampere/Hopper.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** ICLR 2024 paper (confirmed by search results pointing to the OpenReview forum and proceedings.iclr.cc PDF) plus README table on one H100-SXM against PyTorch FFT convolution; benchmark code (benchmarks/benchmark_flashfftconv.py) and nvcc flags (csrc/flashfftconv/setup.py) are public, but long-sequence rows are scaled from smaller batch/hidden sizes and the baseline runs in fp32 while FlashFFTConv runs fp16/bf16, so kept at B rather than A.
- **Verifier notes:** Repo, Apache-2.0, 355 stars, 37 forks, 35 commits, last commit 2024-12-28 confirmed on github.com; stale is right. Paper pages (arxiv.org, openreview.net) blocked by egress; venue taken from search results. GPU-only entry; consider whether the fft category should carry GPU-vs-PyTorch claims.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/HazyResearch/flash-fft-conv/HEAD/README.md>
  - <https://raw.githubusercontent.com/HazyResearch/flash-fft-conv/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/HazyResearch/flash-fft-conv/HEAD/benchmarks/benchmark_flashfftconv.py>
  - <https://raw.githubusercontent.com/HazyResearch/flash-fft-conv/HEAD/csrc/flashfftconv/setup.py>
  - <https://github.com/HazyResearch/flash-fft-conv>
  - <https://github.com/HazyResearch/flash-fft-conv/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/HazyResearch/flash-fft-conv/HEAD/README.md>
  - <https://raw.githubusercontent.com/HazyResearch/flash-fft-conv/HEAD/csrc/flashfftconv/setup.py>
  - <https://raw.githubusercontent.com/HazyResearch/flash-fft-conv/HEAD/setup.py>
  - <https://raw.githubusercontent.com/HazyResearch/flash-fft-conv/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/HazyResearch/flash-fft-conv/HEAD/flashfftconv/__init__.py>
  - <https://raw.githubusercontent.com/HazyResearch/flash-fft-conv/HEAD/flashfftconv/conv.py>
  - <https://raw.githubusercontent.com/HazyResearch/flash-fft-conv/HEAD/flashfftconv/depthwise_1d.py>
  - <https://raw.githubusercontent.com/HazyResearch/flash-fft-conv/HEAD/benchmarks/benchmark_flashfftconv.py>
  - <https://raw.githubusercontent.com/HazyResearch/flash-fft-conv/HEAD/benchmarks/benchmark.py>
  - <https://raw.githubusercontent.com/HazyResearch/flash-fft-conv/HEAD/tests/test_flashfftconv.py>
  - <https://github.com/HazyResearch/flash-fft-conv/issues?q=is%3Aissue>
  - <https://github.com/HazyResearch/flash-fft-conv/issues/27>
  - <https://github.com/HazyResearch/flash-fft-conv/issues/14>
  - <https://github.com/HazyResearch/flash-fft-conv/issues/20>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/hazyresearch/flash-fft-conv`) · [data/wave8/enrich/raw/github_com_hazyresearch_flash_fft_conv.json](../../../data/wave8/enrich/raw/github_com_hazyresearch_flash_fft_conv.json) (enrichment confidence 0.8)

</details>
