# HipKittens (AMD) / ThunderKittens sibling

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C++ (HIP)` · `MIT` · 🟢 active

> C++ tile-primitive kernel DSL for AMD Instinct GPUs; its GQA attention backward runs about 3x faster than AITER on MI355X.

| | |
|---|---|
| **Beats** | AITER (AMD hand-tuned assembly attention kernels); also Composable Kernel, PyTorch SDPA, Triton and hipBLASLt in other plots |
| **Claimed result** | GQA non-causal backward (B=16, 64 Q heads, 8 KV heads, D=128) on MI355X, from benchmark/mi355x_gqa_bkwd_non_causal.json and plot.py: HipKittens 881 / 1007 / 1106 / 1155 / 1176 TFLOPS at N = 1024 / 2048 / 4096 / 8192 / 16384 vs AITER 300 / 351 / 375 / 384 / 389, Composable Kernel 368 / 428 / 447 / 463 / 465 and PyTorch SDPA 220 / 273 / 301 / 309 / 312; 2.93x to 3.02x over AITER (derived from page data). GQA causal backward: 2.98x to 4.33x over AITER (588 vs 151 TFLOPS at N=1024, 995 vs 334 at 16384; derived from page data). The win is GQA-specific: for MHA (B=16, H=16, D=128) HipKittens is at parity or slower than AITER beyond short sequences: non-causal 734 vs 590 (1.24x) at N=1024, 1027 vs 1056 (0.97x) at 4096, 1119 vs 1201 (0.93x) at 16384; causal 462 vs 389 (1.19x) at 1024, 941 vs 1034 (0.91x) at 8192, 1028 vs 1109 (0.93x) at 16384 (derived from benchmark/mi355x_mha_bkwd_\*.json). |
| **Workload** | GQA non-causal attention backward pass on one AMD Instinct MI355X: batch 16, 64 query heads, 8 KV heads, head dim 128, sequence length 1024 to 16384, TFLOPS (repo's analysis/attn/bkwd plot). |
| **Metric** | throughput |
| **Hardware** | AMD Instinct MI355X (gfx950, CDNA4); host CPU not stated; CDNA3 branch also covers MI300X/MI325X |
| **Compiler and flags** | hipcc (\$ROCM_PATH/bin/hipcc) inside the ROCm 7.0 preview image the README names (rocm/7.0-preview:rocm7.0_preview_pytorch_training_mi35x_beta); analysis/attn/bkwd/benchmark/Makefile builds the kernels as pybind11 extensions with -DKITTENS_CDNA4 --offload-arch=gfx950 -DHIP_ENABLE_WARP_SYNC_BUILTINS -ffast-math -std=c++20 -w -shared -fPIC (no explicit -O level in that Makefile; the newer kernels/common.mk adds -O3). test_python.py: 500 warmup and 100 timed iterations with torch.cuda events, BF16. CK baselines from ck_tile tile_example_fmha_bwd with -warmup=500 -repeat=100 (analysis/baselines/README.md). |
| **Adoption** | 472 stars, 81 forks; MLSys 2026 paper; README says HK kernels landed in AMD AITER (March 2026) and AMD Transformer Engine (June 2026) as backends |
| **Last commit** | 2026-09-22 |
| **Links** | [repository](https://github.com/HazyResearch/HipKittens) · [benchmark](https://github.com/HazyResearch/HipKittens/tree/main/analysis/attn/bkwd) |

## Verdict

On one AMD Instinct MI355X with BF16 inputs, the repo's committed results for GQA attention backward (batch 16, 64 query heads, 8 KV heads, head dim 128) give HipKittens 881 to 1176 TFLOPS for sequence length 1024 to 16384 against AITER's 300 to 389 TFLOPS (about 2.9-3.0x; causal 3.0-4.3x), timed with torch.cuda events over 100 iterations after 500 warmups, kernels built with hipcc in the ROCm 7.0 preview image (-ffast-math, C++20, gfx950). AITER is timed through a PyTorch autograd backward call while HK times its three kernels directly, and on MHA shapes HK falls 3-9% behind AITER at longer sequences.

## Use it when

- Training or fine-tuning with grouped-query attention (e.g. 64 query heads, 8 KV heads, head dim 128) on MI350X/MI355X, where the backward pass is about 3x AITER's in the committed results
- Writing your own fused AMD kernel and wanting MFMA-shaped tile abstractions instead of raw HIP intrinsics or Composable Kernel templates
- Fixed, known shapes (batch, heads, sequence a multiple of the 256-row block) that you can bake into a build
- Studying how to schedule compute and memory on CDNA3/CDNA4 (the analysis/ directory has the sweep scripts, plots and baseline recipes from the paper)
- Consuming the HK kernels indirectly: AITER merged an HK-based 128-head MLA decode kernel (ROCm/aiter PR 2039, March 2026) and the README says AMD Transformer Engine has an HK backend

## Skip it when

- MHA (H_KV = H) attention backward at sequence length 2048-4096 and above: the same harness shows HK 3-9% slower than AITER
- NVIDIA or RDNA GPUs: CDNA3/CDNA4 (and initial CDNA5/gfx1250) only; RDNA4 support is an open question (issue 13)
- Ragged or unaligned shapes (MoE experts, variable-length batches): grids are computed with integer division, so partial edge tiles are silently dropped and results are wrong without padding (open issue 74)
- When you need deterministic gradients: dQ is accumulated with BF16 atomics
- When you want a stable, documented API: docs/README.md has an empty HipKittens documentation link, and kernels are research code tuned per shape

## How it is fast

Tiles are sized to the CDNA matrix-core (MFMA) shapes and loaded with coalesced, bank-conflict-free layouts and direct buffer loads into shared memory to hide address computation. Kernels overlap compute and memory with two schedules the authors name 8-wave ping-pong and 4-wave interleave, and order thread blocks for the chiplet (XCD) layout; the inner loops use explicit s_waitcnt lgkmcnt/vmcnt counts and sched_barrier hints instead of relying on the compiler. The GQA backward kernel launches one block per (KV head, 256-row KV block, batch), loops over all query heads in the group and accumulates dQ with packed BF16 atomic adds.

## Compared with alternatives

Pick HipKittens when the target is AMD Instinct hardware; ThunderKittens, FlashAttention-3, SageAttention and FFPA in this category are NVIDIA-only, and HK is the same tile-DSL idea as ThunderKittens ported to CDNA. On NVIDIA use ThunderKittens or FlashAttention-3 instead.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | ROCm with hipcc (README uses the rocm/7.0-preview PyTorch Docker images), pybind11 and Python for the shipped kernels; PyTorch and AITER for the tests and benchmarks |
| **Minimum toolchain** | C++20 (common.mk sets -std=c++20), hipcc from ROCm 7.0 preview images |
| **Platforms** | AMD CDNA4 gfx950 (MI350X/MI355X) on main; CDNA3 gfx942 (MI300X/MI325X) via the cdna3 branch per README (include/cdna3 also exists on main); CDNA5 gfx1250 unit tests on main |
| **Thread safety** | not documented (GPU kernels; dQ uses atomic adds within a launch) |
| **Drop-in for the baseline** | partial — the kernels replace AITER/CK attention or hipBLASLt GEMM calls only after you build each one for your exact shapes and wire it into PyTorch yourself; no torch.nn.functional-compatible wrapper ships in the repo |

## Gotchas

- Batch, query heads, KV heads and sequence length are -D compile-time constants (ATTN_B, ATTN_H, ATTN_H_KV, ATTN_N); a new shape means a rebuild, and the backward grid uses ATTN_N / 256
- The backward pass is three launches (prep, combined dK/dV/dQ, dQ shuffle) and expects pre-zeroed output buffers in specific layouts
- Hand-tuned s_waitcnt counts are fragile: a race in the 8-wave FP8 GEMM epilogue was fixed in commit 20cd6bb and issue 42 asks whether the 4-wave FP8 kernel has the same bug (open, unverified)
- Gradients match AITER only to BF16 rounding (the verifier saw max abs error 0.0039 at N=1024), and -ffast-math is on for the attention builds

## Known shortcomings

- The \~3x win over AITER is GQA-only; on MHA backward HipKittens is 0.91-0.97x of AITER from N=2048-4096 up. Timing is asymmetric: AITER is timed through torch autograd .backward() while HipKittens times its kernels directly. PyTorch SDPA bars in the GQA plots copy the MHA values.
- Open #74: ragged/unaligned shapes silently drop partial edge tiles (wrong results, no error). dQ is accumulated with BF16 atomics, so gradients are not deterministic. Open #42: possible vmcnt race in the 4-wave FP8 GEMM (same bug fixed in the 8-wave kernel, commit 20cd6bb). Shapes are compile-time -D constants; docs link is empty.

## Caveats and trade-offs

Baselines are AMD libraries (AITER, hipBLASLt, Composable Kernel) plus Triton and PyTorch, none of which are in the category's baseline list (oneDNN, cuDNN, XNNPACK, Eigen tensor), and this is a GPU kernel library, so it fits the category only loosely. The roughly 3x attention-backward win holds only for GQA; on MHA backward the same harness shows HipKittens 3-9% slower than AITER from N=2048-4096 upward (benchmark/mi355x_mha_bkwd_non_causal.json and mi355x_mha_bkwd_causal.json), which suggests AITER's GQA backward path, not its tuned MHA path, is what HipKittens beats by 3x. Timing is not symmetric: AITER is timed as one autograd out.backward(dO) call through PyTorch (dispatch overhead and any GQA dK/dV reduction included), while HipKittens times its three kernels (prep, combined backward, dQ shuffle) directly. In plot.py the PyTorch SDPA values for the GQA plots are identical to the MHA values (220.27 / 273.06 / ... non-causal, 109.51 / 156.71 / ... causal), so the PyTorch bars in the GQA figures were copied, not measured on GQA shapes. The GQA N=16384 lines in mi355x_benchmark.sh are commented out (with ATTN_B=15), so how that JSON row was produced is not shown. HipKittens gradients differ from AITER within BF16 rounding (max abs error 0.0039; 103 dK and 1452 dV elements outside a 0.001 + 5% tolerance at N=1024). The BF16 GEMM plot (analysis/bf16_gemm) shows parity with AMD's libraries rather than a win (numbers from the search record, not re-checked here). Baseline numbers were collected by the authors in October/November 2025 and the README warns the frameworks keep evolving; AITER now includes HipKittens kernels (March 2026), so a re-run may differ. The paper (arXiv 2511.08083, MLSys 2026) and the Hazy Research and AMD blogs could not be opened (hosts blocked).

AMD CDNA3/CDNA4 GPUs only (MI355X/MI350X on main, MI300X/MI325X on the cdna3 branch), needs ROCm and hipcc. A tile-primitive DSL in C++ rather than a drop-in library: kernels are written per operation and shape configuration (matrix sizes are Makefile constants). Covers BF16/FP8/FP6 GEMM, MHA/GQA attention forward and backward, rotary and layernorm.

## Maintenance

Actively developed (last commit 2026-09-22, MLSys 2026 paper, CDNA5 support landing) and MIT-licensed, but it is research code with per-shape kernels and no API docs, so expect to read and adapt kernels rather than link a library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Public harness analysis/attn/bkwd/benchmark/test_python.py driven by mi355x_benchmark.sh times HipKittens and AITER (aiter.flash_attn_func backward) in one script, and the raw results are committed (benchmark/mi355x_gqa_bkwd_non_causal.json: tflops 880.7/1006.6/1106.0/1155.5/1176.0 vs tflops_ref 300.3/350.9/374.8/383.8/389.3); compiler (hipcc in the README's ROCm 7.0 preview image), flags (benchmark/Makefile) and the device (AMD Instinct MI355X, gfx950) are stated. For a GPU kernel the GPU model is the relevant hardware.
- **Verifier notes:** Numbers re-derived exactly from the committed JSON (HK and AITER) and plot.py (CK times converted with the script's FLOP formula, PyTorch hard-coded). Headline is the best case: HipKittens loses slightly to AITER on MHA backward at N&gt;=4096, and the PyTorch bars in the GQA plots reuse MHA values. Record shortcoming: GQA-only win, asymmetric timing, copied PyTorch baseline values.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/HazyResearch/HipKittens>
  - <https://github.com/HazyResearch/HipKittens/tree/main/analysis/attn/bkwd>
  - <https://github.com/HazyResearch/HipKittens/tree/main/analysis/attn/bkwd/benchmark>
  - <https://github.com/HazyResearch/HipKittens/commits/main>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/main/README.md>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/main/analysis/attn/bkwd/README.md>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/main/analysis/attn/bkwd/plot.py>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/main/analysis/attn/bkwd/benchmark/mi355x_gqa_bkwd_non_causal.json>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/main/analysis/attn/bkwd/benchmark/mi355x_gqa_bkwd_causal.json>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/main/analysis/attn/bkwd/benchmark/mi355x_mha_bkwd_non_causal.json>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/main/analysis/attn/bkwd/benchmark/mi355x_mha_bkwd_causal.json>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/main/analysis/attn/bkwd/benchmark/Makefile>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/main/analysis/attn/bkwd/benchmark/mi355x_benchmark.sh>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/main/analysis/attn/bkwd/benchmark/test_python.py>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/main/analysis/baselines/README.md>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/main/analysis/bf16_gemm/README.md>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/main/kernels/cdna4/attn/gqa_backwards/Makefile>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/main/kernels/common.mk>
- **Sources the enricher read:**
  - <https://github.com/HazyResearch/HipKittens>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/HEAD/README.md>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/HEAD/analysis/attn/bkwd/README.md>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/HEAD/analysis/attn/bkwd/benchmark/test_python.py>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/HEAD/analysis/attn/bkwd/benchmark/Makefile>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/HEAD/analysis/baselines/README.md>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/HEAD/analysis/bf16_gemm/README.md>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/HEAD/kernels/common.mk>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/HEAD/kernels/cdna4/attn/gqa_backwards/Makefile>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/HEAD/kernels/cdna4/attn/gqa_backwards/test_python.py>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/HEAD/kernels/cdna4/attn/gqa_backwards/attn_bkwd_non_causal.cpp>
  - <https://raw.githubusercontent.com/HazyResearch/HipKittens/HEAD/docs/README.md>
  - <https://github.com/HazyResearch/HipKittens/tree/main/include>
  - <https://github.com/HazyResearch/HipKittens/tree/main/include/cdna4>
  - <https://github.com/HazyResearch/HipKittens/tree/main/kernels/cdna4>
  - <https://github.com/HazyResearch/HipKittens/issues>
  - <https://github.com/HazyResearch/HipKittens/issues?q=is%3Aissue+is%3Aclosed>
  - <https://github.com/HazyResearch/HipKittens/issues/74>
  - <https://github.com/HazyResearch/HipKittens/issues/42>
  - <https://github.com/HazyResearch/HipKittens/issues/34>
  - <https://github.com/HazyResearch/HipKittens/issues/12>
  - <https://github.com/ROCm/aiter/pull/2039>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/hazyresearch/hipkittens`) · [data/wave8/enrich/raw/github_com_hazyresearch_hipkittens.json](../../../data/wave8/enrich/raw/github_com_hazyresearch_hipkittens.json) (enrichment confidence 0.75)

</details>
