# FlashAttention-4 (CuTeDSL, Hopper/Blackwell)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Python (CuTe-DSL, kernels JIT-compiled; flash_attn/cute)` · `BSD-3-Clause` · 🟢 active

> Blackwell/Hopper exact attention kernels in CuTe-DSL; beat cuDNN 9.13 by 1.04-1.29x on B200, roughly tie cuDNN 9.19.

| | |
|---|---|
| **Beats** | cuDNN 9.13.0 fused attention (also benchmarked: cuDNN 9.19.1.2, Triton 3.6.0, Gluon 3.6.0, FlashAttention 2.8.3) |
| **Claimed result** | Paper abstract: 'up to 1.3x speedup over cuDNN 9.13 and 2.7x over Triton on B200 GPUs with BF16, reaching up to 1613 TFLOPs/s (71% utilization)'. Figure 4 (forward, head dim 128, TFLOPs/s, seq 1K/2K/4K/8K/16K/32K): non-causal FA4 1355, 1468, 1532, 1579, 1601, 1613; cuDNN 9.13.0 1157, 1328, 1413, 1460, 1488, 1517 (FA4 1.06-1.17x, derived from page data); cuDNN 9.19.1.2 1346, 1474, 1552, 1585, 1609, 1613 (0.99-1.01x, derived); Triton 3.6.0 507 to 703 (FA4 2.29-2.67x, derived); FA2 383 to 432. Causal FA4 744, 1053, 1279, 1426, 1526, 1576; cuDNN 9.13.0 717, 929, 1076, 1168, 1285, 1266 (1.04-1.24x, derived); cuDNN 9.19.1 822, 1103, 1295, 1430, 1509, 1540 (0.91-1.02x, derived: cuDNN ahead up to 8K); Triton 351 to 670 (2.12-2.36x, derived). Figure 5 (forward causal, head dim 192/128): FA4 812, 1121, 1357, 1506, 1600, 1654 vs cuDNN 9.13.0 769, 999, 1167, 1276, 1375, 1382 (1.06-1.20x, derived) vs cuDNN 9.19.1.2 860, 1133, 1311, 1415, 1515, 1563 (0.94-1.06x, derived). Figure 6 (backward, head dim 128): non-causal FA4 936, 1166, 1331, 1430, 1457, 1412 vs cuDNN 9.13.0 857, 1016, 1116, 1171, 1212, 1107 (1.09-1.28x, derived) vs cuDNN 9.19.1.2 928, 1108, 1231, 1300, 1280, 1274 (1.01-1.14x, derived); causal FA4 614, 887, 1102, 1284, 1402, 1446 vs cuDNN 9.13.0 543, 732, 893, 1008, 1085, 1142 (1.13-1.29x, derived) vs cuDNN 9.19.1 651, 894, 1090, 1218, 1293, 1337 (0.94-1.08x, derived). So the 'up to 1.3x over cuDNN 9.13' is reached only in the backward pass (forward peaks at 1.24x), and the only remaining lead over current cuDNN 9.19 is in the backward pass at long sequences (up to about 1.14x). |
| **Workload** | Attention forward (and backward) in BF16 on B200: head dim 64, 128 and (192,128), causal and non-causal, sequence 1K to 32K with total tokens fixed at 32K, hidden dimension 2048 (32 or 16 heads); TFLOPs/s from 4 \* seqlen^2 \* head_dim \* heads (halved for causal, backward = 2.5x forward). |
| **Metric** | throughput |
| **Hardware** | NVIDIA B200 (the main text says B200; Appendix A.1 writes 'B100 180GB SXM6 (1000W)', apparently a typo); CPU model not stated. |
| **Compiler and flags** | Paper Appendix A.1: CUDA 13.1, CuTe-DSL 4.4.1, PyTorch 2.10.0, Triton 3.6, FlashAttention 2.8.3, cuDNN 9.13 and 9.19.1.2; 5 warmup runs then 10 repeats averaged. CuTe-DSL kernels are JIT compiled; compile options are fixed in flash_attn/cute/interface.py (cute.compile options '--enable-tvm-ffi', plus a kernel's ptxas_options where set). HEAD's flash_attn/cute/pyproject.toml now requires nvidia-cutlass-dsl&gt;=4.6.2, so a HEAD build does not match the paper's CuTe-DSL 4.4.1. |
| **Adoption** | 25.1k stars (whole flash-attention repository, shared with FlashAttention-2 and -3); pip package flash-attn-4; paper by Princeton, Meta, Colfax, NVIDIA, Georgia Tech and Together AI authors, listed in MLSys 2026 proceedings per a WebSearch result |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/Dao-AILab/flash-attention) · [benchmark](https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/assets/fa4_paper.pdf) |

## Verdict

The paper PDF in the repo times FA4 against cuDNN 9.13.0 and 9.19.1.2, Triton 3.6 and FA 2.8.3 on a B200 in BF16 (CUDA 13.1, CuTe-DSL 4.4.1, PyTorch 2.10.0; 5 warmup runs, mean of 10), with total tokens fixed at 32K and head dim 64, 128 or (192,128): FA4 is 1.04-1.24x faster than cuDNN 9.13 forward and 1.09-1.29x backward, peaking at 1613 TFLOPs/s (1654 at head dim 192/128). Against cuDNN 9.19.1.2 the forward is at parity (0.91-1.06x) and only the backward keeps a lead of up to about 1.14x at long sequences (ratios derived from page data).

## Use it when

- Training or prefill on B200/GB200-class GPUs (SM100) in BF16/FP16 with head dim 64, 128 or (192,128), especially sequences of 4K tokens and longer where it leads every baseline in the paper.
- Backward-heavy training at long sequence lengths: the backward pass still leads current cuDNN 9.19.1.2 by up to about 1.14x at 8K-32K tokens (derived from page data).
- You need attention variants (custom score_mod/mask_mod, block sparsity, learnable sinks, MLA head dims 512, softcap) without writing CUDA C++; the paper reports 2.5 s / 1.4 s JIT compile per kernel versus 55 s / 45 s for FA3's C++ templates.
- Reproducible RL or debugging runs that need a deterministic backward (deterministic=True) at a moderate cost on SM90/SM100.
- A Hopper (SM90) codebase that wants one Python-level attention library spanning H100 and B200.

## Skip it when

- Short causal sequences (1K-2K) on B200 when cuDNN 9.19+ is available: cuDNN is ahead there (e.g. 822 vs 744 TFLOPs/s at 1K causal, head dim 128), and the paper's own Figure 4 caption says newer cuDNN reaches similar performance.
- A C or C++ application with no Python runtime: there is no C++ API; kernels are generated through Python, PyTorch and nvidia-cutlass-dsl at run time.
- Pre-Hopper or non-NVIDIA hardware: the README targets Hopper and Blackwell, the interface has SM80/SM120 paths but the paper reports no numbers for them, and AMD needs a different library.
- FP8 training: FP8 is forward-only and only on SM100 (the interface raises NotImplementedError for an FP8 backward).
- Shops that need a stable release: PyPI still ships weekly betas (4.0.0b33 on 2026-09-30) with the classifier 'Development Status :: 3 - Alpha', and several FA4 correctness issues are open.

## How it is fast

On B200 the tensor cores doubled while shared-memory bandwidth and the MUFU exponential unit did not, so the paper attacks the non-matmul bottlenecks: a ping-pong pipeline over fully asynchronous Blackwell MMAs that write to tensor memory (TMEM), with a separate correction warpgroup for output rescaling. For 10-25% of each softmax row, exp2 runs as a polynomial on FMA units after Cody-Waite range reduction, in parallel with the hardware MUFU unit, and online-softmax rescaling is skipped unless the running max grows by more than a threshold (log2 256 = 8). The backward pass keeps more intermediates in TMEM and uses the 2-CTA MMA mode so each CTA stages only half of operand B, which cuts shared-memory traffic and halves the dQ global atomic adds; longest-processing-time-first tile scheduling helps causal and varlen workloads.

## Compared with alternatives

Pick it over FlashAttention-3 when you are on Blackwell (FA3 does not run on B200 per the paper) or want Python-level attention variants with fast JIT builds; pick it over ThunderKittens when you want a maintained pip package with varlen, paged KV and GQA rather than a kernel-authoring framework. Choose SageAttention or SpargeAttn instead only if you accept quantized or sparse approximate attention on consumer GPUs.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | PyTorch, nvidia-cutlass-dsl&gt;=4.6.2 (cu13 extra for CUDA 13), apache-tvm-ffi&gt;=0.1.11,&lt;0.2, torch-c-dlpack-ext, quack-kernels&gt;=0.5.3, einops, typing_extensions |
| **Minimum toolchain** | Python 3.10+; CUDA 12.x (CUDA 13 recommended for B200 via the cu13 extra); nvidia-cutlass-dsl 4.6.2+ at HEAD (the paper used CuTe-DSL 4.4.1 with CUDA 13.1 and PyTorch 2.10.0) |
| **Platforms** | Linux, NVIDIA GPUs: SM90 (H100/H200) and SM100/SM103/SM110 (B200/B300) are the documented targets; the interface also accepts SM80 and SM120 with reduced features (no block-sparse, score_mod or deterministic backward on SM120) |
| **Thread safety** | not documented (compiled kernels are cached in per-process JIT caches keyed by configuration) |
| **Drop-in for the baseline** | partial: same call shape as FlashAttention-2/3 flash_attn_func, but not a drop-in for cuDNN; users of PyTorch SDPA's cuDNN backend must call flash_attn.cute directly, and head-dim support on SM100 is limited to 8-128, (192,128), (256,256) and the MLA 512 shapes |

## Gotchas

- Each new shape or option set JIT-compiles on first call; issue #2635 (closed) reported very slow Qwen3.5-35B-A3B training on 8x B300 caused by CUTLASS JIT compilation during the backward pass, so warm up shapes before timing or serving.
- The default backward is nondeterministic (inter-CTA atomic dQ reductions, and dK/dV for GQA); deterministic=True serializes them with a semaphore and reaches up to 75% of the 1-CTA nondeterministic backward speed per the paper.
- Softmax uses a polynomial exp2 for part of the elements: the degree-3 version has a max FP32 relative error of 8.8e-5 (about 600x the hardware MUFU.EX2) but matches hardware within 1 BF16 ULP; check against a reference softmax if you consume FP32 intermediates or the LSE.
- Version coupling to nvidia-cutlass-dsl matters: issue #2797 (open) reports the FA4 backward never returning with cutlass-dsl 4.6.0/4.6.1 on B300 (sm_103), #2860 (open) an illegal memory access on SM120 with 4+ varlen segments, and #2665/#2886 were hd256 non-contiguous Q/K correctness bugs on SM100 (fixed).

## Known shortcomings

- Upgraded B to A under the FlashAttention-3 precedent (public harness benchmarks/benchmark_attn.py, stated toolchain, named B200). The 1.3x headline is against cuDNN 9.13; against cuDNN 9.19.1.2 the lead is forward parity and backward up to 1.14x only.
- PyPI is still alpha (4.0.0b33, weekly betas). Python-only, no C++ API; JIT compile on first use per shape (#2635: slow B300 training). Tied to nvidia-cutlass-dsl versions (#2797 open: backward never returns on cutlass-dsl 4.6.0/4.6.1, sm_103); #2860 open: SM120 illegal memory access with 4+ varlen segments. FP8 is forward-only and SM100-only; the default backward is nondeterministic. The interface also accepts SM80/SM120, for which the paper gives no numbers. A search snippet puts cuDNN ahead at 1K-2K causal (about 315 vs 208 TFLOPs/s), source unverified.

## Caveats and trade-offs

Paper read from the PDF checked into the repo (assets/fa4_paper.pdf); arXiv, the MLSys proceedings page, the Together AI blog and the Colfax post were not opened (egress-blocked), so the peer-review status rests on a search result and was not checked by me. The Figure 4 caption itself says 'newer versions of cuDNN have incorporated many of the techniques described in this paper, yielding similar performance to FA4', and Appendix A.1 says the authors worked with the cuDNN team to fold FA4 techniques into cuDNN from 9.13/9.14 on: in the forward pass FA4 is at parity with cuDNN 9.19.1.2 (and behind it at short causal sequences, e.g. 744 vs 822 TFLOPs/s at 1K causal), and the 1.1-1.3x lead holds only against cuDNN 9.13.0; in the backward pass FA4 still leads cuDNN 9.19 by up to about 1.14x at long sequences (derived from page data). The forward figures alone peak at 1.24x over cuDNN 9.13, so the abstract's 'up to 1.3x' comes from the backward pass. Figure 5 shows 1654 TFLOPs/s at head dim 192/128, above the abstract's 'up to 1613'. Appendix inconsistencies: it names a 'B100 180GB SXM6 (1000W)' while the text and every figure say B200 (180 GB and 1000 W match B200), and it dates the library versions to 'March 2025', which cannot be right for CUDA 13.1. The public harness covers FA2, FA3, FA4, cuDNN and PyTorch standard attention but not the Triton or Gluon baselines, and no tag marks the commit used for the paper's figures. FlashAttention-3 'does not run on B200' (paper footnote), so there is no FA4 vs FA3 comparison, and the paper has no H100 FA4 numbers. Several authors are from NVIDIA and Colfax, and the cuDNN team is thanked for feedback. Shares the Dao-AILab/flash-attention repository with FlashAttention-3 (use id paper:flashattention-4).

Written in CuTe-DSL embedded in Python (paper claims 20-30x faster compile than C++ templates), so no C++ build step but a Python/CUTLASS-DSL dependency and JIT compile at first use; Hopper (sm90) and Blackwell (sm100/sm120) only, CUDA 13 recommended for best performance (cu13 extra). Forward and backward, GQA, varlen, paged KV, block sparsity and MLA kernels live in flash_attn/cute. Uses software-emulated exponentials and conditional softmax rescaling (paper abstract), which a numerics-sensitive user should check against a reference softmax.

## Maintenance

Very active (last commit 2026-10-02, weekly PyPI betas, 25.1k-star repository shared with FA2/FA3) and BSD-3-Clause, but still labelled Alpha and tied to fast-moving nvidia-cutlass-dsl releases, so pin both versions.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded from B under the wave's GPU-kernel precedent (FA3 retier-01, sgemm.cu): the paper PDF in the repo (assets/fa4_paper.pdf) gives FA4 vs cuDNN 9.13.0 and 9.19.1.2 TFLOPs/s on a named GPU (B200) with the toolchain (CUDA 13.1, CuTe-DSL 4.4.1, PyTorch 2.10.0, Triton 3.6, FA 2.8.3) and timing method (5 warmup, 10 repeats averaged), and the public harness benchmarks/benchmark_attn.py times FA4 and cuDNN (fwd and bwd) with defaults that match the paper (total 32k tokens, 16 heads at head dim 128, warmup 5, rep 10). Compile options are fixed in public source (flash_attn/cute/interface.py: cute.compile options '--enable-tvm-ffi' plus per-kernel ptxas_options).
- **Verifier notes:** All Figure 4 bar labels in the record match the PDF exactly (checked at 330 dpi). Upgraded to A by the same reasoning the orchestrator used for FA3 (public harness + stated toolchain + named GPU); keep at B if the orchestrator prefers to require a pinned commit. Worth recording: the lead over current cuDNN (9.19) is forward parity and backward up to 1.14x only.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/assets/fa4_paper.pdf>
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/README.md>
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/benchmarks/benchmark_attn.py>
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/flash_attn/cute/interface.py>
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/flash_attn/cute/pyproject.toml>
  - <https://github.com/Dao-AILab/flash-attention>
  - <https://github.com/Dao-AILab/flash-attention/commits/main>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/README.md>
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/flash_attn/cute/README.md>
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/flash_attn/cute/pyproject.toml>
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/flash_attn/cute/interface.py>
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/hopper/setup.py>
  - <https://raw.githubusercontent.com/Dao-AILab/flash-attention/HEAD/assets/fa4_paper.pdf>
  - <https://github.com/Dao-AILab/flash-attention>
  - <https://github.com/Dao-AILab/flash-attention/issues?q=is%3Aissue+FA4>
  - <https://pypi.org/pypi/flash-attn-4/json>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `paper:flashattention-4`) · [data/wave8/enrich/raw/paper_flashattention_4.json](../../../data/wave8/enrich/raw/paper_flashattention_4.json) (enrichment confidence 0.85)

</details>
