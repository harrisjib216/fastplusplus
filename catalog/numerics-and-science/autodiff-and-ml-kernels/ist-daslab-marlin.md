# Marlin (FP16xINT4 LLM matmul kernel)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `CUDA` · `Apache-2.0` · 🟡 stale

> FP16 x INT4 weight-only GEMM for Ampere/Ada GPUs; near-ideal 3.9x over FP16 torch.matmul up to batch 16-32.

| | |
|---|---|
| **Beats** | FP16 PyTorch matmul (calls CUTLASS) and other 4-bit kernels: torch-nightly, exllamav2, AWQ, bitsandbytes |
| **Claimed result** | Approximate plot readings (derived from page data). Peak plot (A10, 72k x 18k matrix, group size 128): Marlin about 3.87x to 3.9x over FP16 PyTorch at batch 1 to 16, 3.8x at 32, 3.1x at 64 and 1.55x at 128, tracking the 'Ideal' line; at batch 16, torch-nightly about 1.4x, exllamav2 about 0.7x, AWQ about 0.3x, bitsandbytes about 0.4x. Model layers at batch 16: about 3.4x to 4.25x on A10, 3090 and A6000, and 2.2x to 3.65x on A100. Sustained plot (A10 at locked base clock): about 3.9x to batch 16, 3.3x at 32, 1.7x at 64 and 1.0x at 128. README text: 'close to ideal (4x)' up to batch 16-32, with a maximum of 3.87x after the group-scale overhead. |
| **Workload** | 16-bit x 4-bit (group size 128) matrix multiplication on a 72k x 18k weight matrix on an NVIDIA A10 across batch sizes 1-128, plus the linear layers of Llama and Falcon models at batch size 16 on A10, 3090, A6000 and A100. |
| **Metric** | throughput |
| **Hardware** | NVIDIA A10 with ECC disabled (peak and sustained plots); A10, RTX 3090, A6000 and A100 (model layers); host CPU not stated; CUDA &gt;= 11.8, torch &gt;= 2.0 |
| **Adoption** | 1.2k stars |
| **Last commit** | 2024-09-04 |
| **Links** | [repository](https://github.com/IST-DASLab/marlin) · [benchmark](https://github.com/IST-DASLab/marlin#benchmarks) |

## Verdict

First-party plots only: on an NVIDIA A10 with ECC disabled, a 72k x 18k group-128 matmul ran about 3.87-3.9x faster than FP16 torch.matmul at batch 1-16, 3.1x at 64 and 1.55x at 128 (about 1.0x at 128 with clocks locked to base), and the linear layers of Llama and Falcon models at batch 16 ran about 3.4-4.25x faster on A10, 3090 and A6000 and 2.2-3.65x on A100 (approximate plot readings, derived from page data); compiler flags and host CPU are not stated. One user report (#21, A6000 Ada) measured 1.16x at 1024 rows and 0.82x at 16384 rows.

## Use it when

- Decode-phase LLM inference with 4-bit GPTQ-style weights on A10, A100, A6000, RTX 3090/4090-class GPUs at 1-32 tokens per step, where the weight read dominates.
- Batched serving, speculative decoding or multi-sample schemes that push the effective batch to 16-32, where older 4-bit kernels (exllamav2, AWQ, bitsandbytes) fall below FP16 speed.
- Embedding a dependency-free FP16xINT4 GEMM in a custom C++/CUDA inference engine (one .cu file, plain pointers plus a stream).
- Fitting larger models in GPU memory: 4-bit weights with group-128 scales use about 4.125 bits per weight instead of 16.

## Skip it when

- Prefill or large batches: the README plots fall to about 1.55x at batch 128 (about 1.0x at locked base clock), and issue #21 reports 0.82x of FP16 on an A6000 Ada at 16x1024 = 16384 rows.
- Hopper or Blackwell GPUs: the README says it is not optimised for Hopper; open issues report failures on RTX 5090 (#40) and an nvcc 13.1 ptxas miscompile of the cp.async cache hint on sm_90 (#44).
- Formats it does not cover: BF16 activations, asymmetric or zero-point quantisation (AWQ format), bias, group sizes other than 128 or per-channel, other bit widths; layer dims must have in_features % 128 == 0 and out_features % 256 == 0.
- Volta, Turing, AMD or CPU targets: it needs compute capability 8.0 or newer, and a ROCm port request (#43) is open.
- Correctness-critical group-128 inference on small GPUs until issue #45 is resolved (see gotchas).

## How it is fast

It is built to stay memory-bound on weights up to larger batches: weights are streamed with cp.async and an L2 evict_first cache policy, activations stay in L2 and registers, and shared-memory tiles are double-buffered in a 4-stage pipeline so loads overlap compute. Weights and scales are permuted offline so int4 values dequantise (via LOP3 bit tricks) directly into mma.sync m16n8k16 tensor-core fragments loaded with conflict-free ldmatrix. A 'striped' partitioning gives each SM a contiguous run of tiles that may span several column slices, keeping all SMs busy on realistic shapes, and the cross-block reduction happens in the L2-resident output buffer guarded by global locks.

## Compared with alternatives

Pick Marlin over BitBLAS when you only need FP16xINT4 on Ampere/Ada and want one small kernel file with no TVM-based tuning stack; pick BitBLAS for INT2/INT1/FP4 or mixed formats. For CPU inference of low-bit models use T-MAC, BitNet or ik_llama.cpp instead; for production serving use vLLM's maintained Marlin fork (gptq_marlin, awq_marlin) rather than this frozen repo.

## Integration

| | |
|---|---|
| **Form** | PyTorch CUDA extension (pip install . from source, no wheel) or source-drop of marlin/marlin_cuda_kernel.cu |
| **Dependencies** | kernel: CUDA runtime only; Python wrapper: torch &gt;= 2.0, numpy; GPTQ example: transformers, datasets, sentencepiece |
| **Minimum toolchain** | CUDA &gt;= 11.8 with nvcc matching torch's CUDA; C++ standard and flags are torch CUDAExtension defaults (not stated) |
| **Platforms** | NVIDIA compute capability &gt;= 8.0 (Ampere, Ada); Hopper works but is not optimised; Linux assumed (not stated) |
| **Thread safety** | not documented; each call needs a zeroed int workspace that the kernel uses as cross-block lock storage, and a marlin.Layer owns one, so concurrent launches sharing a layer's workspace on different streams are not covered |
| **Drop-in for the baseline** | partial — marlin.Layer replaces nn.Linear (no bias) after packing fake-quantised FP16 weights and scales; it is a 4-bit approximation of the FP16 matmul, not a bit-exact replacement |

## Gotchas

- Issue #45 (2026-09-29, unanswered) reports wrong and non-deterministic outputs with groupsize 128 at Llama-2-7B shapes (m=300) on a Jetson Orin Nano (8 SMs), relative errors 1.3e-3 to 2e-2 with whole 64-row blocks corrupted, while per-channel scales stay correct; in test.py, test_llama_shapes starts with a bare return, so the repository's own tests never run those shapes.
- Issue #42 reports a possible async race where the per-channel scale load (cp_async4_stream) followed by thread_block_reduce leaves sh_s zeroed; #27 and #38 report slight non-determinism and batch-size-dependent results. None has a maintainer reply.
- Split-k reduction downcasts FP32 accumulators to FP16 in the output buffer, so results depend on how tiles are partitioned across SMs.
- The README benchmarks ran with ECC disabled on the A10 (10-15% more bandwidth), and bench.py times 10 launches with time.time without synchronising between them.

## Known shortcomings

- Gain comes from 4-bit weight traffic and falls to 1.55x at batch 128; PPoPP '25 paper unreadable here (possible B on retier).
- Correctness: issue #45 (2026-09-29) reports wrong, nondeterministic outputs with groupsize 128 at Llama-7B shapes on sm_87 (rel err 1.3e-3 to 2e-2); possible async race #42; nondeterminism #27/#38; test.py test_llama_shapes starts with a bare return, so those shapes are never tested; #21: 0.82x of FP16 at 16384 rows on A6000 Ada; failures on RTX 5090 (#40); nvcc 13.1 sm_90 miscompile (#44).

## Caveats and trade-offs

First-party README results shown only as plots; bench.py times 1 warmup and 10 iterations with time.time and deliberately does not synchronize between launches; setup.py uses torch CUDAExtension defaults and states no flags; host CPU not stated; ECC was disabled on the A10. The baseline is FP16 PyTorch matmul, labelled as calling CUTLASS. The headline compares 4-bit to 16-bit weights, so the speedup is the memory-traffic saving of weight quantisation (the 'Ideal' curve is 3.87x), not a faster FP16 kernel; it falls to about 1.55x at batch 128 (1.0x at locked base clock) and is lower on A100. The README cites arXiv 2408.11743; search results say the paper appeared at PPoPP '25, but it could not be opened here.

Weight-only FP16xINT4 inference kernel for Ampere/Ada GPUs (compute capability &gt;= 8.0); the README says it is not yet optimised for Hopper; needs quantised, reshuffled weights; PyTorch extension.

## Maintenance

Stale research code (14 commits, last 2024-09-04, 34 open issues mostly unanswered) under Apache-2.0; the kernel is easy to vendor, but the maintained descendants live in vLLM, and the open correctness reports (#45, #42) should be checked against your shapes before use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README plots (assets/peak.png, models.png, sustained.png) of speedup over FP16 PyTorch matmul on named GPUs, produced by the public bench.py. setup.py builds with torch CUDAExtension defaults and states no flags, and the host CPU is not stated, so it is not A. The paper was published at PPoPP '25 (per search results; ACM DOI 10.1145/3710848.3710871), which could support B, but every host serving it was blocked here.
- **Verifier notes:** Metadata confirmed on the GitHub page: Apache-2.0 (LICENSE file), 1.2k stars, 93 forks, 14 commits, last commit 2024-09-04 ('Update README.md to point to arxiv paper'), not archived or a fork; stale. Search snippets of the paper abstract mention up to 2.8x end-to-end speedup inside vLLM. Retier to B is possible if a check can open the PPoPP '25 paper.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/IST-DASLab/marlin>
  - <https://github.com/IST-DASLab/marlin/commits>
  - <https://raw.githubusercontent.com/IST-DASLab/marlin/HEAD/README.md>
  - <https://raw.githubusercontent.com/IST-DASLab/marlin/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/IST-DASLab/marlin/HEAD/assets/peak.png>
  - <https://raw.githubusercontent.com/IST-DASLab/marlin/HEAD/assets/models.png>
  - <https://raw.githubusercontent.com/IST-DASLab/marlin/HEAD/assets/sustained.png>
  - <https://raw.githubusercontent.com/IST-DASLab/marlin/HEAD/bench.py>
  - <https://raw.githubusercontent.com/IST-DASLab/marlin/HEAD/setup.py>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/IST-DASLab/marlin/HEAD/README.md>
  - <https://raw.githubusercontent.com/IST-DASLab/marlin/HEAD/setup.py>
  - <https://raw.githubusercontent.com/IST-DASLab/marlin/HEAD/bench.py>
  - <https://raw.githubusercontent.com/IST-DASLab/marlin/HEAD/test.py>
  - <https://raw.githubusercontent.com/IST-DASLab/marlin/HEAD/marlin/__init__.py>
  - <https://raw.githubusercontent.com/IST-DASLab/marlin/HEAD/marlin/marlin_cuda.cpp>
  - <https://raw.githubusercontent.com/IST-DASLab/marlin/HEAD/marlin/marlin_cuda_kernel.cu>
  - <https://github.com/IST-DASLab/marlin/issues?q=is%3Aissue>
  - <https://github.com/IST-DASLab/marlin/issues/45>
  - <https://github.com/IST-DASLab/marlin/issues/42>
  - <https://github.com/IST-DASLab/marlin/issues/21>
  - <https://github.com/IST-DASLab/marlin/issues/24>
  - WebSearch snippets: vLLM Marlin integration (docs.vllm.ai marlin and awq_marlin pages, arXiv 2408.11743 text, Red Hat developer article)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ist-daslab/marlin`) · [data/wave8/enrich/raw/github_com_ist_daslab_marlin.json](../../../data/wave8/enrich/raw/github_com_ist_daslab_marlin.json) (enrichment confidence 0.8)

</details>
