# FlashQLA

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Python (TileLang-generated CUDA kernels)` · `MIT` · 🟢 active

> TileLang-built fused CUDA kernels for Gated DeltaNet chunked prefill; about 2x faster forward and 2.5-3x faster backward than FLA Triton.

| | |
|---|---|
| **Beats** | FLA Triton kernels (flash-linear-attention chunk_gated_delta_rule) and FlashInfer GDN prefill kernel |
| **Claimed result** | README: '2-3x forward speedup and 2x backward speedup over the FLA Triton kernel'. benchmark_results_H200.txt, forward, 397B/122B TP8, 1x32768: FlashQLA 0.348 ms vs FLA 1.019 ms (2.93x) vs FlashInfer 1.645 ms (4.73x); 1x4096: 1.19x vs FLA; TP4 4096x8: 3.18x vs FLA but 0.64x vs FlashInfer. H200 across 171 forward rows: 1.18x to 3.32x vs FLA (geometric mean 2.07x, derived from page data), FlashInfer faster in 56 rows (as low as 0.62x); 32 backward rows: 1.38x to 5.47x vs FLA (geometric mean 2.56x, derived from page data). benchmark_results_GB200.txt (torch 2.11.0, fla 0.5.1, flashinfer 0.6.12, tilelang 0.1.12): 171 forward rows 1.07x to 3.58x vs FLA (geometric mean 2.17x, derived from page data), FlashInfer faster in 85 rows (as low as 0.48x; geometric mean vs FlashInfer 1.07x, derived from page data); 32 backward rows 1.94x to 6.44x vs FLA (geometric mean 3.24x, derived from page data). |
| **Workload** | Gated DeltaNet (GDN) chunked-prefill forward and backward kernels at Qwen3.5/Qwen3.6 head configurations (TP1 to TP8, d=128), single-sequence and varlen batches up to 32768 tokens, CUDA-graph timing on H200 and GB200. |
| **Metric** | latency |
| **Hardware** | NVIDIA H200 (benchmark_results_H200.txt) and NVIDIA GB200 (benchmark_results_GB200.txt); host CPU not stated |
| **Compiler and flags** | H200 file: torch 2.8.0+cu128, fla 0.5.1, flashinfer 0.6.13, tilelang 0.1.12; GB200 file: torch 2.11.0, fla 0.5.1, flashinfer 0.6.12, tilelang 0.1.12; both Warmup=10, Repeats=100, Backend=cudagraph (README text names FLA 0.5.0, Triton 3.5.1, FlashInfer 0.6.9, TileLang 0.1.8). No compiler flags stated. |
| **Adoption** | 716 stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/QwenLM/FlashQLA) · [benchmark](https://github.com/QwenLM/FlashQLA/blob/HEAD/benchmark/benchmark_results_H200.txt) |

## Verdict

First-party per-shape CUDA-graph timings (10 warmup, 100 repeats, bf16, d=128) from the public benchmark/bench_gated_delta_rule.py on H200 (torch 2.8.0+cu128, FLA 0.5.1, FlashInfer 0.6.13, TileLang 0.1.12) and GB200: forward 1.18-3.32x vs FLA Triton on H200 (geometric mean about 2.1x) and 1.07-3.58x on GB200, but only roughly at parity with FlashInfer's GDN prefill (as low as 0.48x on GB200 small-batch varlen); backward 1.38-5.47x (H200) and 1.94-6.44x (GB200) vs FLA. Host CPU and compiler flags are not stated.

## Use it when

- Training or prefill of GDN-based models (Qwen3.5/3.6, Qwen3-Next style linear-attention layers) at head dim 128 in bf16 on H100/H200, B200/GB200 or RTX 50-series
- Long single sequences with few heads per GPU (tensor parallel TP4-TP8): H200 1x32768 at TP8 forward 0.348 ms vs FLA 1.019 ms and FlashInfer 1.645 ms
- Backward pass / pretraining: 32 backward shapes on H200 run 1.38x to 5.47x faster than FLA (geometric mean about 2.6x); FlashInfer has no GDN backward to compare
- Already on FLA: switch via FLA's FlashQLA backend or the same-signature chunk_gated_delta_rule without changing model code

## Skip it when

- Inference serving with many short varlen sequences and FlashInfer available: FlashInfer's GDN prefill beats FlashQLA in 56 of 171 H200 forward rows and 85 of 171 GB200 rows (down to 0.48x), so FlashQLA is roughly at parity there
- Decode / token-by-token generation or MTP: only chunked prefill is implemented (decode and MTP kernels are an open feature request, issue #11)
- Ampere, Ada, AMD or Ascend hardware: import raises ValueError on anything other than sm90, sm100, sm103, sm120 or sm121
- Packed varlen batches whose segments are shorter than one 64-token chunk on B200: issue #43 measured L32 at 4.4x and L63 at 7.7x slower than padding to L64 (incomplete chunks fall back from TMA to guarded elementwise loads)
- RTX 5090 / sm120 varlen workloads in production: issue #35 (open) reports four forward tests on varlen/padding configs with relative errors of 1e16-1e25

## How it is fast

Instead of FLA's chain of separate Triton kernels, it fuses gate, decay and matmul stages into a few warp-specialized TileLang kernels that overlap TMA data movement, Tensor Core and CUDA Core work, with separate Hopper (sm90), Blackwell (sm100/103) and sm120 code paths. An algebraic reformulation of the GDN chunked forward/backward cuts Tensor Core, CUDA Core and SFU (exp) work. When heads per GPU are few (high TP) or sequences are long, it uses the exponential decay of the gate to split one sequence across SMs (gate-driven intra-card context parallelism), which is why the biggest gains are at TP8 with long single sequences.

## Compared with alternatives

Pick FlashQLA for GDN (gated delta rule) layers, training or long-context prefill; pick FlashKDA for Kimi Delta Attention (KDA) layers, and FlashInfer's GDN prefill for batched short-sequence serving where it is as fast or faster. FlashAttention-3 and SageAttention cover softmax attention, not linear attention.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | PyTorch &gt;= 2.8, TileLang &gt;= 0.1.12 (kernels compiled through TileLang), CUDA 12.8+; FLA and FlashInfer only for benchmarks and tests |
| **Minimum toolchain** | Python 3.10, CUDA 12.8, PyTorch 2.8 |
| **Platforms** | NVIDIA sm90 (Hopper), sm100/sm103 (B200, GB200, B300), sm120/sm121 (RTX 50-series, DGX Spark GB10); Linux; no CPU or AMD path |
| **Thread safety** | not documented (module-level tensor_cache with mutable shared entries and no lock) |
| **Drop-in for the baseline** | partial — same argument layout as FLA's chunk_gated_delta_rule and selectable as an FLA backend, but bf16/fp16 only, head_first=True unsupported, B must be 1 when cu_seqlens is given, and inter+intra CP is rejected on sm120 |

## Gotchas

- The kernel set is chosen at import time from tilelang's detected compute capability, so a process with mixed GPU generations or no supported GPU fails on import
- Numerics differ from FLA: tests check a 2% relative error against an fp64 reference; issue #15 (closed, no explanation shown) reported max abs diff 0.047 vs FLA Triton that flipped greedy tokens on 2 of 3 prompts. Validate end-to-end outputs before switching inference
- Issue #23 (B200 integrator) found heap-corruption risks from an id()-keyed tensor cache and from zero-length cu_seqlens segments; the current utils/index.py keys on object identity instead, but check zero-length segments on your version
- Benchmarks and tests use bf16 inputs; open issue #38 reports NaNs in fp16 forward beyond 32k tokens (reporter's H100/CUDA 12.4/PyTorch 2.4 setup is below the stated requirements, so unconfirmed). Prefer bf16

## Known shortcomings

- On GB200 FlashInfer is faster in 85 of 171 forward rows; H200 stats check out.
- Open #35: sm120 varlen forward tests fail with relative error 1e16-1e25 (RTX 5090); #15 (closed, no fix shown): max diff 0.047 vs FLA flipped greedy tokens on 2 of 3 prompts; #43: B200 packed varlen L&lt;64 4.4-7.7x slower; import fails on GPUs other than sm90/100/103/120/121.

## Caveats and trade-offs

First-party benchmark; host CPU and compiler flags not stated (benchmark script benchmark/bench_gated_delta_rule.py and the result files are public). Baselines are the FLA Triton and FlashInfer GDN kernels, not oneDNN/cuDNN/XNNPACK/Eigen. Speedup is shape dependent: on H200 FlashInfer is faster than FlashQLA in 56 of 171 forward rows (as low as 0.62x) and on GB200 in 85 of 171 (as low as 0.48x), mostly small-batch varlen rows, so against FlashInfer FlashQLA is roughly at parity on GB200 forward. Backward is compared only with FLA (FlashInfer has no backward in the table). The README's quoted library versions differ from those printed in the result files. Result files were updated on 2026-09-30.

Specific to Gated DeltaNet chunked prefill (Qwen3.5/3.6 linear-attention layers), not general attention. Needs Hopper or Blackwell GPUs (SM120 forward only) and the TileLang toolchain. Uses an algebraic reformulation of the GDN forward/backward flow that the authors say keeps numerical precision.

## Maintenance

Very active Qwen/Alibaba project (v0.1.3, last commit 2026-09-30, 716 stars), MIT-licensed and pip-installable as flash-qla; young (first release April 2026) with open correctness issues on sm120 varlen.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** benchmark/benchmark_results_H200.txt and _GB200.txt list first-party per-shape latencies against FLA Triton and FlashInfer with library versions, produced by the public benchmark/bench_gated_delta_rule.py; host CPU and build flags are not stated, so C, not A.
- **Verifier notes:** H200 row statistics in the record reproduced exactly from the file; GB200 statistics added. Metadata confirmed via github.com: MIT (Copyright 2026 Qwen, Alibaba), 716 stars, 78 forks, 191 commits, not archived/fork, last commit 2026-09-30 ('Update version to v0.1.3').
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/QwenLM/FlashQLA>
  - <https://github.com/QwenLM/FlashQLA/commits>
  - <https://raw.githubusercontent.com/QwenLM/FlashQLA/HEAD/README.md>
  - <https://raw.githubusercontent.com/QwenLM/FlashQLA/HEAD/benchmark/benchmark_results_H200.txt>
  - <https://raw.githubusercontent.com/QwenLM/FlashQLA/HEAD/benchmark/benchmark_results_GB200.txt>
  - <https://raw.githubusercontent.com/QwenLM/FlashQLA/HEAD/benchmark/bench_gated_delta_rule.py>
  - <https://raw.githubusercontent.com/QwenLM/FlashQLA/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/QwenLM/FlashQLA/HEAD/README.md>
  - <https://raw.githubusercontent.com/QwenLM/FlashQLA/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/QwenLM/FlashQLA/HEAD/setup.py>
  - <https://raw.githubusercontent.com/QwenLM/FlashQLA/HEAD/benchmark/bench_gated_delta_rule.py>
  - <https://raw.githubusercontent.com/QwenLM/FlashQLA/HEAD/benchmark/benchmark_results_H200.txt>
  - <https://raw.githubusercontent.com/QwenLM/FlashQLA/HEAD/benchmark/benchmark_results_GB200.txt>
  - <https://raw.githubusercontent.com/QwenLM/FlashQLA/HEAD/flash_qla/__init__.py>
  - <https://raw.githubusercontent.com/QwenLM/FlashQLA/HEAD/flash_qla/ops/gated_delta_rule/chunk/__init__.py>
  - <https://raw.githubusercontent.com/QwenLM/FlashQLA/HEAD/flash_qla/utils/index.py>
  - <https://raw.githubusercontent.com/QwenLM/FlashQLA/HEAD/tests/test_gdr_unit.py>
  - <https://raw.githubusercontent.com/QwenLM/FlashQLA/HEAD/tests/gdr_common.py>
  - <https://github.com/QwenLM/FlashQLA/tree/main/flash_qla>
  - <https://github.com/QwenLM/FlashQLA/tree/main/flash_qla/ops/gated_delta_rule>
  - <https://github.com/QwenLM/FlashQLA/tree/main/flash_qla/ops/gated_delta_rule/chunk>
  - <https://github.com/QwenLM/FlashQLA/issues?q=is%3Aissue>
  - <https://github.com/QwenLM/FlashQLA/issues/15>
  - <https://github.com/QwenLM/FlashQLA/issues/23>
  - <https://github.com/QwenLM/FlashQLA/issues/35>
  - <https://github.com/QwenLM/FlashQLA/issues/38>
  - <https://github.com/QwenLM/FlashQLA/issues/43>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/qwenlm/flashqla`) · [data/wave8/enrich/raw/github_com_qwenlm_flashqla.json](../../../data/wave8/enrich/raw/github_com_qwenlm_flashqla.json) (enrichment confidence 0.8)

</details>
