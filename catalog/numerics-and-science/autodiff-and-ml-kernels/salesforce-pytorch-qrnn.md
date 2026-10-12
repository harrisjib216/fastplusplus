# pytorch-qrnn (QRNN CUDA kernels)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python (CUDA kernels compiled at runtime via CuPy and pynvrtc)` · `BSD-3-Clause` · 🔴 abandoned

> Archived PyTorch QRNN layer with a runtime-compiled CUDA recurrence kernel; trained language models about 2x faster per epoch than cuDNN LSTM.

| | |
|---|---|
| **Beats** | NVIDIA cuDNN LSTM |
| **Claimed result** | README text: 'betwen 2 and 17 times faster than the highly optimized NVIDIA cuDNN LSTM implementation depending on the use case'; repo description: 'up to 16 times faster'. The reproduced paper figure (Figure 4, measured on the paper's earlier implementation) shows inference speed advantages over cuDNN LSTM from 1.3x (batch 256) to 16.9x (batch 8, sequence length 512), and training on a two-layer 640-unit PTB LM of roughly 290 ms/batch for the cuDNN LSTM vs roughly 150 ms/batch for the QRNN (read off the bar chart). Numbers measured with this PyTorch code (awd-lstm-lm README, NVIDIA Quadro GP100): Penn Treebank LSTM 65 s/epoch vs QRNN 28 s/epoch, WikiText-2 180 vs 90 s/epoch (about 2.3x and 2.0x, derived from page data). |
| **Workload** | Training speed of a two-layer 640-unit PTB language model (batch of 20 examples, 105 timesteps) and inference speed of a 320-unit QRNN layer alone vs an equal-sized cuDNN LSTM layer across batch sizes and sequence lengths. |
| **Metric** | throughput |
| **Hardware** | NVIDIA Quadro GP100 for the awd-lstm-lm per-epoch times; GPU for the paper figure not stated on the pages opened |
| **Adoption** | 1.3k stars; ICLR 2017 paper (Bradbury et al.) |
| **Last commit** | 2022-02-12 |
| **Links** | [repository](https://github.com/salesforce/pytorch-qrnn) · [benchmark](https://github.com/salesforce/awd-lstm-lm/blob/HEAD/README.md) |

## Verdict

The README's 2-17x figure is Figure 4 of the ICLR 2017 QRNN paper, measured on an earlier (pre-PyTorch) implementation: a 320-unit QRNN layer is 1.3x (batch 256) to 16.9x (batch 8, sequence 512) faster than an equal-size cuDNN LSTM in inference, and a two-layer 640-unit PTB LM trains at roughly 150 vs 290 ms per batch (read off the bar chart). The only numbers on this PyTorch code are first-party from awd-lstm-lm on an NVIDIA Quadro GP100: Penn Treebank 28 vs 65 s/epoch and WikiText-2 90 vs 180 s/epoch for QRNN vs cuDNN LSTM, with differently shaped models and no PyTorch, CUDA or cuDNN versions given.

## Use it when

- Studying or reproducing QRNN / AWD-QRNN language-model results from 2017-2018 on the PyTorch versions of that era
- Unidirectional sequence models on GPU with long sequences or small batches, where the paper figure shows the largest advantage over cuDNN LSTM (up to 16.9x at batch 8, sequence length 512)
- As a template for a fused gated linear recurrence: the 60-line ForgetMult kernel is easy to port to a modern torch.autograd.Function or a C++/CUDA extension

## Skip it when

- Current PyTorch: GPUForgetMult is a legacy autograd.Function with a non-static forward, which newer PyTorch rejects ('Legacy autograd function with non-static forward method is deprecated', issue #29, unanswered)
- Bidirectional models, batch_first inputs, bias=False or PackedSequence variable-length batches: the constructor asserts against the first three and the README lists PackedSequence as unsupported
- fp16, bf16 or fp64 training: the CUDA kernels are written for float pointers only and the Python wrapper does not check the dtype
- Large-batch workloads: the paper figure shows only 1.3x-1.4x at batch 256 for every sequence length, and the awd-lstm-lm README notes that most time then goes to softmax and optimizer overhead
- Cases needing an exact LSTM: QRNN gives 'similar accuracy' after retraining, not identical outputs or transferable weights

## How it is fast

QRNN removes the hidden-to-hidden matrix product: the candidate, forget and output gates for all timesteps come from one large nn.Linear over the input (with a window of 1 or 2 previous inputs concatenated), which runs as a single big GEMM. The only sequential part is ForgetMult, a small CUDA kernel compiled at runtime with NVRTC and launched through CuPy, which assigns one thread per (batch, hidden unit) and walks the timesteps in a loop; the backward kernel walks them in reverse with a double-precision accumulator. The README says gains are largest at small batch sizes and long sequences, where cuDNN LSTM is limited by its step-by-step dependency.

## Compared with alternatives

No catalogued sibling is a GPU recurrent-layer replacement for cuDNN LSTM; RTNeural is the pick for small real-time LSTM/GRU inference on CPU, while the transformer runtimes (CTranslate2, LightSeq, FasterTransformer) target attention models. Choose pytorch-qrnn only if you specifically want the QRNN architecture and are prepared to modernise its autograd code.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | PyTorch (2017-era Variable API), CuPy, pynvrtc (NVIDIA NVRTC Python bindings), a CUDA toolkit with NVRTC |
| **Minimum toolchain** | Python 3; PyTorch 0.2-0.4 era (awd-lstm-lm, its main user, requires PyTorch 0.4); exact upper bound not documented |
| **Platforms** | Linux with an NVIDIA GPU for the fast path; CPU fallback is a Python loop over timesteps |
| **Thread safety** | not documented; compiled kernels and the CUDA stream are cached per device in a class-level dict on first use |
| **Drop-in for the baseline** | partial: same constructor arguments and tensor shapes as nn.LSTM for unidirectional time-major models, but a different architecture whose hidden output is a single tensor (no LSTM cell state), so weights and accuracy do not carry over |

## Gotchas

- The CUDA stream is captured once per device when the kernel is first configured; later calls on a different stream still launch on the cached one
- Installation breaks with newer pynvrtc (issue #26: 'bytes' object has no attribute 'encode'; issue #17 on double encoding), and there are open reports of window=2 size mismatches (issue #19)
- The forget-gate convention is the reverse of the paper's equation (issue #22, unanswered); harmless when training from scratch but matters when porting weights between implementations
- With window=2 and save_prev_x=True you must call reset() between independent sequences, or the previous batch's last input leaks into the next one

## Known shortcomings

- README figure comes from the Nov 2016 paper, which predates this code (first commit 2017-09-28); low end overstated (1.3x at batch 256, not 2x); measured numbers for this code are only about 2x per epoch on a Quadro GP100 (awd-lstm-lm README).
- Does not run on current PyTorch (legacy non-static autograd.Function, #29). Kernel takes float pointers with no dtype check, so fp16/fp64 input is a correctness risk. CUDA stream cached per device. pynvrtc install breaks (#26, #17). Gate convention flipped vs the paper (#22).

## Caveats and trade-offs

The README's 2-17x figure is Figure 4 of the ICLR 2017 paper, measured before this PyTorch code existed (by a WebSearch summary, on a Chainer implementation); the figure itself starts at 1.3x, not 2x, at batch size 256. Numbers measured on this code come only from the sibling awd-lstm-lm README (about 2x per epoch on a Quadro GP100) with no PyTorch, CUDA or cuDNN versions, and the QRNN and LSTM models there differ in depth and width. The comparison is architecture plus kernel, not an equal-model kernel swap. CUDA kernels are compiled at runtime via CuPy and pynvrtc against 2017-era PyTorch (Variable API); the repository is archived (2022-02-12) and its last code commit is 2017-11-26. Old cuDNN (2016-2017 era); modern cuDNN LSTM is faster.

QRNN is a different architecture, not a faster LSTM: gains come from batching the input matmuls and a light element-wise recurrence (ForgetMult kernel). Accuracy is described as similar, not identical. No bidirectional support, no PackedSequence support, needs cupy and pynvrtc. Archived 2022-02-12.

## Maintenance

Abandoned: last code commit 2017-11-26, archived 2022-02-12, BSD-3-Clause; small enough to vendor and port, but it does not run unmodified on current PyTorch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now C.
- **Tier reason:** The README's speed figure is Figure 4 of the QRNN paper (arXiv 1611.01576, Nov 2016), which predates this repository's first commit ('QRNN Release', 2017-09-28); a WebSearch summary says the paper's experiments used a Chainer implementation, so no peer-reviewed number was measured on this code. The only numbers for this PyTorch code are first-party: the awd-lstm-lm README gives per-epoch times on an NVIDIA Quadro GP100 without PyTorch, CUDA or cuDNN versions.
- **Verifier notes:** Downgraded B to C: the peer-reviewed numbers belong to the paper's earlier implementation, and this repository has only first-party per-epoch timings (via awd-lstm-lm). The low end of the README claim is overstated (the figure shows 1.3x at batch 256). Metadata matches: BSD-3-Clause, 1.3k stars, archived 2022-02-12.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `hardware`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/salesforce/pytorch-qrnn>
  - <https://raw.githubusercontent.com/salesforce/pytorch-qrnn/HEAD/README.md>
  - <https://raw.githubusercontent.com/salesforce/pytorch-qrnn/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/salesforce/pytorch-qrnn/HEAD/images/qrnn_speed.png>
  - <https://github.com/salesforce/pytorch-qrnn/commits>
  - <https://github.com/salesforce/pytorch-qrnn/commits/master>
  - <https://raw.githubusercontent.com/salesforce/awd-lstm-lm/HEAD/README.md>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/salesforce/pytorch-qrnn/HEAD/README.md>
  - <https://raw.githubusercontent.com/salesforce/pytorch-qrnn/HEAD/setup.py>
  - <https://raw.githubusercontent.com/salesforce/pytorch-qrnn/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/salesforce/pytorch-qrnn/HEAD/torchqrnn/__init__.py>
  - <https://raw.githubusercontent.com/salesforce/pytorch-qrnn/HEAD/torchqrnn/forget_mult.py>
  - <https://raw.githubusercontent.com/salesforce/pytorch-qrnn/HEAD/torchqrnn/qrnn.py>
  - <https://raw.githubusercontent.com/salesforce/pytorch-qrnn/HEAD/images/qrnn_speed.png>
  - <https://github.com/salesforce/pytorch-qrnn/issues?q=is%3Aissue>
  - <https://github.com/salesforce/pytorch-qrnn/issues/29>
  - <https://github.com/salesforce/pytorch-qrnn/issues/22>
  - <https://raw.githubusercontent.com/salesforce/awd-lstm-lm/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/salesforce/pytorch-qrnn`) · [data/wave8/enrich/raw/github_com_salesforce_pytorch_qrnn.json](../../../data/wave8/enrich/raw/github_com_salesforce_pytorch_qrnn.json) (enrichment confidence 0.8)

</details>
