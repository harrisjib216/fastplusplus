# llm.c (GPT-2/GPT-3 training in C/CUDA)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C (CUDA)` · `MIT` · 🟡 stale

> GPT-2/GPT-3 pretraining in plain C/CUDA with hand-written fused kernels; about 7% faster than PyTorch nightly on one A100.

| | |
|---|---|
| **Beats** | PyTorch Nightly (parallel reference implementation train_gpt2.py) |
| **Claimed result** | Discussion #344 (2024-05-03): 'llm.c: at \~167K tok/s (on SOTA PR from this morning that is merging imminently), on master at \~160K'; 'PyTorch code as is on master runs at \~150K tok/s'; 'If you manually pad the vocab size to 50304, tok/s improves \~150K -&gt; \~156K, reducing llm.c speed improvement to \~7%.' Also: 'Compared to the current PyTorch stable release 2.3.0, we are actually \~46% faster.' README: 'Currently, llm.c is a bit faster than PyTorch Nightly (by about 7%).' |
| **Workload** | GPT-2 (124M) pretraining throughput on TinyStories, batch 32, sequence length 1024, bfloat16, single GPU. llm.c: make train_gpt2cu USE_CUDNN=1 && ./train_gpt2cu -i data/TinyStories -v 250 -s 250 -g 144 -b 32. PyTorch: python train_gpt2.py --compile=1 --tensorcores=1 --dtype=bfloat16 --flash=1 --batch_size=32 --sequence_length=1024 (torch.compile and flash attention on). |
| **Metric** | throughput |
| **Hardware** | NVIDIA A100 40GB PCIe (Lambda), CUDA 12.2; host CPU not stated |
| **Compiler and flags** | nvcc via the repo Makefile (CUDA 12.2, USE_CUDNN=1); the current Makefile uses --use_fast_math -std=c++17 -O3. The flags at the May 2024 commit and the host compiler were not stated in the post. |
| **Adoption** | 31.1k stars |
| **Last commit** | 2025-05-10 |
| **Links** | [repository](https://github.com/karpathy/llm.c) · [benchmark](https://github.com/karpathy/llm.c/discussions/344) |

## Verdict

Karpathy's May 3, 2024 'State of the Union' (Discussion #344) measured GPT-2 124M training on TinyStories, batch 32 x 1024 tokens, bf16, on one A100 40GB PCIe (CUDA 12.2, driver 535.129.03): llm.c about 167K tok/s (160K on master) against train_gpt2.py with torch.compile and flash attention at about 150K tok/s, or about 156K with the vocab padded to 50304, so about 7% ahead of PyTorch nightly. The nightly build and host CPU are not identified; the PyTorch script is described in #481 as lacking full feature parity.

## Use it when

- Pretraining GPT-2 or GPT-3-style decoder-only models (124M up to the 1.6B reproduction target) on NVIDIA GPUs where you want a dependency-light binary and a few percent over torch.compile.
- Reproducing GPT-2 124M cheaply: Discussion #481 reports about 90 minutes and about \$20 on an 8x A100 80GB SXM node at about 60% MFU.
- Learning or teaching how each transformer layer's forward and backward pass maps to CUDA, using dev/cuda's progression of kernels and the doc/layernorm tutorial.
- Borrowing specific fused kernels (fused classifier, fused residual+LayerNorm, bf16 AdamW) as reference code for your own engine.

## Skip it when

- Any architecture outside the GPT-2/GPT-3 family: there is no general autodiff, so a new layer means hand-writing its forward and backward kernels.
- Serving or production inference: it is a training loop whose only inference is sampling inside the binary (-g genT); use an inference engine instead.
- Non-NVIDIA hardware: mainline is CUDA only, cuDNN attention is not supported on macOS per the Makefile, and AMD, Metal, OpenCL support exist only as third-party forks.
- If you need an actively maintained stack: the last commit is from May 2025, with 93 open issues and 133 open pull requests on the repo page.
- Expecting a large margin over current PyTorch: the 7% was measured in May 2024 against a nightly build, and it shrinks to that only after padding PyTorch's vocab by hand (46% was against stable 2.3.0).

## How it is fast

No framework or Python overhead, bf16 mixed precision, and kernel fusion: a fused classifier computes the cross-entropy loss without materializing the full softmax and starts the backward pass in the same kernel, a fused residual-plus-LayerNorm forward, optional GELU fused into cuBLASLt matmul epilogues, and Packed128 128-bit vectorized loads and stores. Attention uses cuDNN's flash attention (USE_CUDNN=1), matmuls go through cuBLASLt, the vocabulary is padded internally to 50304 for GPU-friendly shapes, and recomputing GELU in the backward pass saves activation memory so larger batches fit.

## Compared with alternatives

Pick llm.c when you want to own the whole GPT-2 training stack in C/CUDA; Liger-Kernel is the drop-in choice for speeding up existing Hugging Face PyTorch training, FlashAttention-3 or ThunderKittens give faster individual attention/GEMM kernels, and yalm is the from-scratch C++/CUDA counterpart for inference rather than training.

## Integration

| | |
|---|---|
| **Form** | source-drop (single-file training program built with the repo Makefile; llmc/\*.cuh headers) |
| **Dependencies** | CUDA toolkit with cuBLAS and cuBLASLt and NVML (-lnvidia-ml); optional cuDNN plus the header-only cudnn-frontend for flash attention (USE_CUDNN=1); optional NCCL and OpenMPI for multi-GPU; Python with PyTorch only to prepare data and the initial checkpoint; CPU build uses OpenMP if found |
| **Minimum toolchain** | nvcc with -std=c++17 (CUDA 12.x in the published runs; the cuDNN path on Windows uses C++20); CPU reference builds with clang or gcc -Ofast |
| **Platforms** | Linux x86-64 with NVIDIA GPUs (multi-GPU and multi-node via NCCL); Windows build path in the Makefile; CPU fp32 reference on any OS including Apple Silicon |
| **Thread safety** | not documented; it is a single training process per GPU, with multi-GPU coordination through MPI/NCCL processes |
| **Drop-in for the baseline** | no |

## Gotchas

- cuDNN flash attention is off by default (USE_CUDNN=0) because it raises compile time from seconds to about a minute; the published speed comparison was built with USE_CUDNN=1, and the FP32 test path does not support cuDNN.
- The usage text says GELU fusion (-ge) defaults to 2 on SM90+, but the code currently forces the default to 0 ('off for now'), so pass -ge explicitly if you want it.
- The build uses --use_fast_math for nvcc and -Ofast for the CPU reference, so results match PyTorch only within the tolerances test_gpt2 checks.
- Open issues include 'inf loss at big batch' (#263), 'Possible bugs in the data loading functions' (#321) and a multi-GPU dataloader shuffle_rng question (#792).

## Known shortcomings

- The comparison (\~167K tok/s vs PyTorch nightly \~156K with padded vocab, A100 40GB PCIe, CUDA 12.2; discussion #344) used an unmerged PR; host CPU and PyTorch nightly build not stated.
- Help text says -ge (GELU fusion) defaults to 2 on SM90+, but the code forces 0. Open issues: #263 inf loss at large batch, #321 dataloader bugs. Discussion #481 says train_gpt2.py lacks feature parity with llm.c's training loop, which weakens the PyTorch baseline.

## Caveats and trade-offs

First-party measurement from May 2024 (Discussion #344): the \~7% margin is \~167K tok/s on a then-unmerged PR vs PyTorch nightly at \~156K tok/s with the vocab padded by hand (master llm.c \~160K vs unpadded PyTorch \~150K). The PyTorch nightly build is not identified, the host CPU is not stated, and the margin may have changed since; the repo went quiet in May 2025. The win comes from fused custom kernels, cuDNN flash attention and no framework overhead, while matmuls still go through cuBLAS/cuBLASLt.

GPT-2/GPT-3 family only; hand-written forward and backward passes (no general autodiff); the README says mainline uses cuBLAS for matmuls and keeps the root code simple, with experimental faster kernels in dev/cuda; a reference CPU fp32 version is in train_gpt2.c.

## Maintenance

Stale since the last commit on 2025-05-10 but MIT-licensed, widely studied (31.1k stars, 3.8k forks, many language ports) and easy to vendor as reference code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README sentence only says 'a bit faster than PyTorch Nightly (by about 7%)', but Discussion #344 (Karpathy, 2024-05-03) gives the first-party numbers (llm.c \~167K tok/s vs PyTorch \~150K, \~156K with padded vocab) with both commands, A100 40GB PCIe and CUDA 12.2. The code is public (train_gpt2.cu vs train_gpt2.py), but the host CPU, PyTorch nightly build and exact flags at that commit are not stated, so C rather than A.
- **Verifier notes:** README claim verified verbatim; the real numbers page is Discussion #344 (benchmark_url corrected). Metadata confirmed on github.com: MIT, 31.1k stars, not a fork or archived, last commit 2025-05-10, so stale.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/karpathy/llm.c/HEAD/README.md>
  - <https://github.com/karpathy/llm.c>
  - <https://github.com/karpathy/llm.c/commits/master>
  - <https://github.com/karpathy/llm.c/discussions/344>
  - <https://raw.githubusercontent.com/karpathy/llm.c/HEAD/Makefile>
- **Sources the enricher read:**
  - <https://github.com/karpathy/llm.c>
  - <https://raw.githubusercontent.com/karpathy/llm.c/HEAD/README.md>
  - <https://raw.githubusercontent.com/karpathy/llm.c/HEAD/Makefile>
  - <https://raw.githubusercontent.com/karpathy/llm.c/HEAD/train_gpt2.cu>
  - <https://github.com/karpathy/llm.c/tree/master/llmc>
  - <https://raw.githubusercontent.com/karpathy/llm.c/HEAD/llmc/matmul.cuh>
  - <https://raw.githubusercontent.com/karpathy/llm.c/HEAD/llmc/fused_classifier.cuh>
  - <https://github.com/karpathy/llm.c/discussions/344>
  - <https://github.com/karpathy/llm.c/discussions/481>
  - <https://github.com/karpathy/llm.c/issues?q=is%3Aissue+bug>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/karpathy/llm.c`) · [data/wave8/enrich/raw/github_com_karpathy_llm_c.json](../../../data/wave8/enrich/raw/github_com_karpathy_llm_c.json) (enrichment confidence 0.75)

</details>
