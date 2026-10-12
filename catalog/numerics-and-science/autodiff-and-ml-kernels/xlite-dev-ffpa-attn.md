# FFPA (ffpa-attn, Faster Flash Prefill Attention for large head dimension)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `CUDA/Python (CUDA, Triton and CuTe-DSL backends)` · `Apache-2.0` · 🟢 active

> Exact GPU attention kernels for head dims 320-1024 (beyond FlashAttention-2's 256); 1.5x-15x faster than PyTorch SDPA.

| | |
|---|---|
| **Beats** | PyTorch SDPA (F.scaled_dot_product_attention); FlashAttention-2 supports head dim only up to 256, FP8/FP4 variants also compared with SageAttention 2/3 |
| **Claimed result** | README: '1.5x\~15x speedup over PyTorch SDPA' for D 320 to 1024. bench/README.md (D=512, PyTorch 2.11, CUDA 13.0): B200 CuTe-DSL forward 6.45x to 8.41x over SDPA (up to 1517 TFLOPS, 16K non-aligned bf16) and backward 8.21x to 14.69x (up to 763 TFLOPS); H200 CuTe-DSL forward 1.81x to 3.46x and backward 4.09x to 6.00x; L20 Triton forward 1.03x (decode) to 1.67x and backward 1.63x to 2.21x; H20 Triton forward 1.57x to 3.46x. README news: FP4 on RTX 5090 850-980 TOPS (D=128-256), '3.8x\~4.4x' over PyTorch SDPA (FlashAttention-2 backend); FP8 on L20 '1.5x\~1.8x' over PyTorch SDPA (BF16) for D=64\~224. Third-party: NVIDIA-NeMo Automodel PR #2436 reports 1.4x\~1.5x end-to-end training throughput for Gemma4-31B on 8xH200 (per the README; PR not opened). End-to-end FLUX.1-dev on RTX PRO 5000: 17.19 s (SDPA) vs 16.08 s (FFPA-FP8) and 15.99 s (FFPA-FP4) at 1024x1024; 91.25 s vs 79.91 s and 75.73 s at 2048x2048. |
| **Workload** | Exact attention for large head dimension (D 320 to 1024) forward and backward, plus FP8/FP4 attention for D 64 to 256, on L20, RTX 5090, H800, H200, B200 and RTX PRO 5000 (for example B1 H32 N8192 D512). |
| **Metric** | throughput |
| **Hardware** | NVIDIA L20 (Ada), RTX 5090 (Blackwell), H800 PCIe and H200 SXM (Hopper), B200 (Blackwell), RTX PRO 5000; host CPU not stated |
| **Adoption** | 335 stars |
| **Last commit** | 2026-09-26 |
| **Links** | [repository](https://github.com/xlite-dev/ffpa-attn) · [benchmark](https://github.com/xlite-dev/ffpa-attn/blob/HEAD/bench/README.md) |

## Verdict

bench/README.md (first-party; PyTorch 2.11, CUDA 13.0, D=512, B=1, fp16/bf16) reports latency against torch SDPA, which cannot use its flash backend at D=512. Results: B200 CuTe-DSL forward 6.45-8.41x and backward 8.21-14.69x (up to 1517/763 TFLOPS); H200 CuTe-DSL forward 1.81-3.46x and backward 4.09-6.00x; L20 Triton forward 1.03-1.67x and backward 1.63-2.21x. No host CPU, driver or build flags are given, and the README's H200 peak (535 TFLOPS) does not match bench/README (427 TFLOPS, table max 426).

## Use it when

- Training or prefill with head dim 320-1024 in fp16/bf16 on NVIDIA sm_80 or newer, where SDPA falls back to its slower efficient/math backends: about 1.5-1.7x forward on L20 (Triton) and 2.6-3.5x forward / 4-6x backward on H200 (CuTe-DSL) at D=512.
- B200 (sm_100a) with D=512 exactly, where the CuTe-DSL tcgen05 path reports 6.5-8.4x forward and 8-15x backward over SDPA.
- Models that mix a few large-D full-attention layers with ordinary layers (the README cites a NeMo Automodel PR reporting 1.4-1.5x end-to-end Gemma4-31B training throughput on 8xH200 with FFPA on the 10 of 60 D=512 layers; PR not opened).
- Long sequences only: each of Nq and Nkv must be at least 512 (Nq below 8 is also accepted, for decode); anything else goes to SDPA anyway.
- Diffusion inference on RTX 50 / RTX PRO Blackwell (sm_120) if you can accept FP8/FP4 accuracy loss and test quality yourself; the end-to-end FLUX.1-dev gain is about 7% at 1024x1024 and 12-17% at 2048x2048.

## Skip it when

- Head dim 256 or less in bf16/fp16: those shapes fall straight through to SDPA, so FlashAttention-2/3 or cuDNN are what actually run.
- Short sequences: if Nkv &lt; 512, or 8 &lt;= Nq &lt; 512, the call falls back to SDPA. FP8/FP4 are also documented as not suitable for small models or short sequences.
- Production stability: the code changes several times a day (dozens of commits in Sept 2026 alone), the CuTe-DSL backend is described as 'early stage', a varlen backward hang on H100 with D=512 (#298) was closed as not planned, and a cross-causal misalignment issue (#311) lists CUDA, Triton and CuTe-DSL but links only a Triton fix (PR #300).
- fp32 inputs, non-NVIDIA hardware other than AMD through the Triton backend, or code that needs attn_mask or dropout on the CuTe-DSL backend (rejected with NotImplementedError).
- Expecting the largest speedups to carry over: on B200 they are measured against SDPA's non-flash fallback at D=512, a weak baseline.

## How it is fast

It keeps FlashAttention's online-softmax tiling and adds two changes that stop SRAM and register use growing with D. Split-D tiles the head dimension, so Q, K and V shared-memory tiles stay a fixed Br x 16 instead of O(D). A TiledMMA M4N2 warp layout for the PV GEMM halves the per-thread O accumulator to O(D/4) registers, which avoids the register spilling the FA-2-style M8N1 layout hits at D=512 and keeps D=1024 feasible (README: 1.55x over M8N1 at D=1024 on RTX 5090, 154 vs 100 TFLOPS). There are three implementations: Triton with persistent autotune configs, CuTe-DSL kernels using TMA/WGMMA on sm_90a and tcgen05 2-CTA on sm_100a, and a forward-only CUDA extension with FP8/FP4 quantized variants.

## Compared with alternatives

Pick FFPA over FlashAttention-3 or ThunderKittens only when head dim is above 256, which they do not target. At D&lt;=256, FFPA just calls SDPA (bf16) or competes with SageAttention on FP8/FP4, where SageAttention-2 is the more established choice at D=128 and FFPA's edge is head dims Sage does not cover (README: Sage-2/3 support D&lt;=128).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | torch&gt;=2.10, Triton (via PyTorch), nvidia-cutlass-dsl==4.6.2, quack-kernels==0.6.4, apache-tvm-ffi (&gt;=0.1.11,&lt;0.2), ray, numpy, ninja, packaging; the optional CUDA extension (ffpa_attn._C) is built from source with build.sh plus git submodules |
| **Minimum toolchain** | Python 3.10+, PyTorch 2.10+ (pyproject); the README says the PyPI wheel needs CUDA 13.0+ and PyTorch 2.11+ |
| **Platforms** | NVIDIA sm_80+ for Triton and CuTe-DSL (fastest on sm_90a for D 320-512 and sm_100a for D=512); CUDA forward backend sm_80+; FP8 on sm_89 and sm_120; FP4 on sm_120 only; Triton backend also runs on AMD ROCm/HIP (PR #268) |
| **Thread safety** | not documented (kernels are registered as torch.library custom ops and are torch.compile-traceable) |
| **Drop-in for the baseline** | partial — same signature as F.scaled_dot_product_attention and can be monkey-patched over it, but only fp16/bf16 run on the FFPA path, causal masking is bottom-right aligned when Nq != Nkv (SDPA is top-left), and the CuTe-DSL backend rejects masks and dropout |

## Gotchas

- Silent semantic change when monkey-patching: with is_causal=True and Nq != Nkv, FFPA aligns the mask to the KV tail (FlashAttention convention), while SDPA aligns it top-left, so cross-causal outputs differ from what SDPA would have returned.
- Hardware or head-dim mismatches fall back to SDPA with only a warning_once log line, so you can believe FFPA is running when it is not. Set FFPA_FORCE_NO_SDPA_FALLBACK=1 when testing.
- Dtype, dropout and mask constraints raise exceptions instead of falling back, so a monkey-patched model with fp32 attention at D&gt;256 will throw.
- The FP8/FP4 kernels quantize Q, K and V internally from bf16 inputs. Their 3.8-4.9x 'speedup over SDPA' compares low precision with BF16 SDPA; against SageAttention-2 (also FP8) the README says only 'comparable or slightly better'.

## Known shortcomings

- For head_dim &gt; 256 SDPA falls back to slower backends, so the baseline is weak there; FP8/FP4 measured against BF16.
- is_causal is bottom-right aligned when Nq != Nkv while SDPA is top-left, so the monkey-patch silently changes cross-causal output; varlen backward hang on H100 D=512 (#298) closed not-planned; silent SDPA fallback when Nkv&lt;512 or D&lt;=256; README H200 peak 535T vs bench README 427T.

## Caveats and trade-offs

For D&gt;256 PyTorch SDPA cannot use its flash backend and falls back to slower backends, so the largest ratios (6x to 15x on B200) are against a weak baseline; FlashAttention-2 does not support D&gt;256 and cuDNN SDPA is not a stated baseline. For D&lt;=256 the speedups are only for FP8/FP4 kernels compared with BF16 SDPA, i.e. lower precision vs higher precision; against SageAttention-2 (FP8) FFPA is only 'comparable or slightly better'. End-to-end diffusion gains are small (about 7% at 1024x1024). First-party; no host CPU or build flags; CUDA backend is forward-only.

Targets head dimensions above 256 where FlashAttention-2 does not apply; CUDA backend is forward only, Triton and CuTe-DSL backends cover forward and backward. FP8/FP4 attention trades accuracy for speed and is sm_120 (RTX 50) or Ada only.

## Maintenance

Very active (last commit 2026-09-26, several commits a day) and Apache-2.0, so it is copyable, but APIs and kernels are moving fast and parts (CuTe-DSL, FP8/FP4) are labelled experimental or early stage.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** bench/README.md gives first-party latency/TFLOPS tables against PyTorch SDPA (PyTorch 2.11, CUDA 13.0, L20/H200/B200/H20), produced by the public bench CLI (python -m ffpa_attn.bench; bench/bench_fp8.py, bench/bench_fp4.py). No host CPU or build flags are stated, so C, not A.
- **Verifier notes:** Metadata confirmed via github.com: Apache-2.0, 335 stars, 27 forks, 544 commits, not archived/fork, last commit 2026-09-26 ('docs: correct sm89 FP8 benchmark GPU (#372)'). benchmark_url moved from the repo root to bench/README.md, which holds the numeric tables. Shortcoming: weak SDPA fallback baseline for D&gt;256 and mixed-precision comparisons for FP8/FP4.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/xlite-dev/ffpa-attn>
  - <https://github.com/xlite-dev/ffpa-attn/commits>
  - <https://github.com/xlite-dev/ffpa-attn/tree/main/bench>
  - <https://raw.githubusercontent.com/xlite-dev/ffpa-attn/HEAD/README.md>
  - <https://raw.githubusercontent.com/xlite-dev/ffpa-attn/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/xlite-dev/ffpa-attn/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/xlite-dev/ffpa-attn/HEAD/README.md>
  - <https://raw.githubusercontent.com/xlite-dev/ffpa-attn/HEAD/bench/README.md>
  - <https://raw.githubusercontent.com/xlite-dev/ffpa-attn/HEAD/pyproject.toml>
  - <https://raw.githubusercontent.com/xlite-dev/ffpa-attn/HEAD/setup.py>
  - <https://raw.githubusercontent.com/xlite-dev/ffpa-attn/HEAD/src/ffpa_attn/__init__.py>
  - <https://raw.githubusercontent.com/xlite-dev/ffpa-attn/HEAD/src/ffpa_attn/ffpa_attn_interface.py>
  - <https://raw.githubusercontent.com/xlite-dev/ffpa-attn/HEAD/src/ffpa_attn/functional.py>
  - <https://github.com/xlite-dev/ffpa-attn/tree/main/src/ffpa_attn>
  - <https://github.com/xlite-dev/ffpa-attn/commits/main>
  - <https://github.com/xlite-dev/ffpa-attn/issues?q=is%3Aissue>
  - <https://github.com/xlite-dev/ffpa-attn/issues/298>
  - <https://github.com/xlite-dev/ffpa-attn/issues/311>
  - <https://github.com/xlite-dev/ffpa-attn/issues/320>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/xlite-dev/ffpa-attn`) · [data/wave8/enrich/raw/github_com_xlite_dev_ffpa_attn.json](../../../data/wave8/enrich/raw/github_com_xlite_dev_ffpa_attn.json) (enrichment confidence 0.8)

</details>
