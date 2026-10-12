# mistral.rs (Rust LLM inference engine, CUDA)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust LLM inference engine on Candle whose CUDA build out-runs llama.cpp's CUDA backend on Gemma 4 prefill and decode.

| | |
|---|---|
| **Beats** | llama.cpp (GGUF Q8_0 and Q4_K_M, llama-bench -ngl 99 -fa 1, CUDA backend); report also compares vLLM BF16 |
| **Claimed result** | Report headline, Gemma 4 E4B, mistral.rs UQFF q8 vs llama.cpp GGUF Q8_0: prefill 1.382x-2.113x (GB10) and 1.246x-2.793x (B200), decode 1.086x-1.097x (GB10) and 1.210x-1.263x (B200); mean prefill 1.828x (GB10) and 2.194x (B200), mean decode 1.090x and 1.242x. The appendix is less uniform: Gemma 4 26B-A4B 128-token prefill on B200 favours llama.cpp (0.771x Q4_K_M, 0.788x Q8_0), H100 26B-A4B Q4_K_M is a tie or loss at the edges (0.996x prefill at 128, 0.984x decode at depth 16384), GB10 26B-A4B Q8 decode is 1.000x-1.017x, and in BF16 mistral.rs is 0.075x-0.413x of vLLM prefill for 26B-A4B on all three GPUs. |
| **Workload** | Gemma 4 E4B and 26B-A4B prefill and decode tokens per second at prompt lengths and decode depths of 128 to 16384, 256 generated tokens, 1 warmup and 3 measured iterations, on NVIDIA GB10, B200 and H100 SXM. |
| **Metric** | throughput |
| **Hardware** | NVIDIA GB10 (driver 580.126.09), NVIDIA B200 (CUDA 13.0, driver 580.126.20), NVIDIA H100 80GB HBM3 SXM (CUDA 12.8, driver 570.124.06) |
| **Compiler and flags** | mistral.rs v0.8.2 (commit 8b49f963 on branch cuda_graphs_v1) built with cargo release and features cuda,cudnn,flash-attn,cutile; rustc 1.96.0 recorded for the H100 host only. llama.cpp commit 751ebd17 run with llama-bench -ngl 99 -fa 1 (default batch and ubatch); llama.cpp build flags not stated. vLLM 0.21.0 with torch 2.11.0+cu130 (H100 rows: vLLM 0.19.0, torch 2.10.0+cu128). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: paged-attention and MoE optimizations (plus CUDA graphs on the benchmarked branch); no Rust-specific mechanism is claimed. |
| **Adoption** | 7.7k stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/EricLBuehler/mistral.rs) · [benchmark](https://raw.githubusercontent.com/EricLBuehler/mistral.rs/HEAD/releases/v0.8.2/report.md) |

## Verdict

The first-party v0.8.2 report covers Gemma 4 E4B at Q8, mistral.rs UQFF q8_0 against llama.cpp GGUF Q8_0 (commit 751ebd17, llama-bench -ngl 99 -fa 1, CUDA). mistral.rs prefill is 1.38-2.11x on GB10 and 1.25-2.79x on B200, and decode is 1.09x and 1.21-1.26x, over 128-16,384 tokens, with each value the mean of 3 runs after 1 warmup. The llama.cpp and vLLM rows come from a sweep run a day earlier. The appendix shows mixed 26B-A4B results and mistral.rs far behind vLLM on BF16 26B-A4B prefill.

## Use it when

- Single-request NVIDIA GPU inference of dense Gemma 4 E4B with long prompts. In the v0.8.2 report, Q8 prefill at 2,048-16,384 tokens runs 2.3-2.8x llama.cpp on B200 and H100 SXM, and decode runs about 1.2x at every depth.
- DGX Spark (GB10) local inference of Gemma 4 E4B: prefill 1.38-2.11x and decode 1.09-1.10x llama.cpp at Q8 (1.10-1.11x decode at Q4).
- Rust or Python applications that want an in-process engine (Python `Runner`, Rust `ModelBuilder`) or one binary that serves OpenAI and Anthropic Messages endpoints with paged attention, prefix caching and continuous batching.
- Multimodal Gemma 4 (image, video and audio input) or tool-calling and agent loops, where llama.cpp would need extra glue.

## Skip it when

- BF16 MoE serving. For Gemma 4 26B-A4B in BF16, mistral.rs prefill is 0.075-0.413x vLLM on GB10, B200 and H100 (for example 592 vs 3,879 tok/s mean on GB10), and B200 decode is 0.65-0.88x vLLM.
- Short-prompt MoE prefill. 26B-A4B at 128 tokens on B200 runs at 0.771x (Q4_K_M) and 0.788x (Q8_0) of llama.cpp, H100 Q4 is a tie or a loss at the edges (0.996x prefill at 128, 0.984x decode at depth 16,384), and GB10 Q8 decode is 1.000-1.017x.
- Consumer Blackwell (RTX 50, compute capability 12.0) with paged attention. Issue #2093 (open, triaged) reports Gemma 4 E4B q8_0 UQFF decoding at about 25 tok/s with paged attention vs about 128 without on an RTX 5080 under v0.8.1; the benchmark command forces `--paged-attn on`.
- AMD GPUs: there is no ROCm backend, and feature request #431 has been open since 2024.
- As evidence that Rust beats C++. Both sides run CUDA C++ kernels, and mistral.rs's quantized GEMMs are adapted from llama.cpp's MMQ kernels, so the gap comes from attention kernels, CUDA graphs, scheduling and harness settings, not from the language.

## How it is fast

The GPU work runs in nvcc-compiled CUDA kernels. Attention uses a paged KV cache with FlashInfer-backed paged decode and prefill kernels, plus FlashAttention v2/v3 as Cargo features. Single-token decode steps are replayed as CUDA graphs: the benchmarked commit was on the `cuda_graphs_v1` branch, and the HEAD docs say graphs are on by default. Quantized matmuls go through `mistralrs-quant/kernels/mmq_gguf` and `mmvq_gguf`, which are adapted from llama.cpp's own ggml-cuda MMQ code (`ggml_cuda_mma` namespace, `ggml_type` enums, `MMQ_ITER_K`). MoE layers use dedicated kernels (cutlass_moe, moe_grouped, indexed_moe and a cuTile grouped GEMM). Rust is only the host and scheduling language, and the project claims no Rust-specific mechanism for the speedup.

## Compared with alternatives

Pick mistral.rs over Fucina (the Zig engine that beats llama.cpp's CPU backend) when you serve on NVIDIA GPUs and want paged attention, multimodal Gemma 4 and an OpenAI-compatible server; pick Fucina for CPU-only inference from the same GGUF file. The other siblings (sorts, compilers, file tools) solve unrelated problems.

## Integration

| | |
|---|---|
| **Form** | crate workspace (git; crates.io `mistralrs` stops at 0.8.1), CLI binary with prebuilt per-GPU builds, Python package `mistralrs` 0.9.4 on PyPI |
| **Dependencies** | candle-core/candle-nn pinned to a git revision, tokio, tokenizers, hf-hub, axum, llguidance and many more; CUDA builds need the CUDA toolkit and nvcc; optional cuDNN, flash-attn, NCCL and cuTile (NVIDIA `tileiras`) |
| **Minimum toolchain** | Rust 1.94 (workspace rust-version at 0.9.4; crates.io 0.8.1 declares 1.88); flash-attn needs compute capability 8.0+, flash-attn-v3 needs Hopper |
| **Platforms** | Linux CUDA (prebuilt per-GPU binaries), macOS Metal, CPU on x86-64 and aarch64, Windows CPU binaries; no ROCm |
| **Thread safety** | The engine runs as its own loop that takes requests over a channel; the `Arc<MistralRs>` handle is shared, and concurrent requests are continuously batched |
| **Drop-in for the baseline** | partial — it loads GGUF files and serves an OpenAI-compatible HTTP API like llama-server, but it has no llama.cpp C API, uses different CLI flags, and its benchmarked fast path uses UQFF/ISQ artifacts |

## Gotchas

- Harness flaw found in the benchmarked bench.rs (commit 8b49f963). Prefill tok/s is the prompt length divided by the step time truncated to whole milliseconds (`Duration::as_millis`), so short prompts are overstated. The B200 E4B Q8 128-token value of 7,529.4 tok/s is exactly 128 / 17 ms, so the true figure lies between 7,111 and 7,529, and the 1.259x ratio vs llama.cpp could be as low as 1.19x. Several other rows are also exact integer-millisecond quotients (2048/58 ms, 4096/107 ms, 4096/125 ms). Decode counts 256 tokens over 255 decode steps (+0.4%), and a single 32-token warmup covers every case. HEAD has since rewritten bench.rs to use streaming TTFT measured with Instant and per-case warmups, so reruns will not match these numbers.
- llama.cpp was run with only `-ngl 99 -fa 1`, which leaves llama-bench's default micro-batch in place. Its prefill flattens after 512 tokens (B200 Q8: 12,092 tok/s at 512, then 13,515-13,705 at 2,048-8,192), while mistral.rs keeps climbing to 38,280 at 4,096. The headline 2x+ long-prompt prefill gap is therefore consistent with an untuned baseline batch size and was not tested with a larger -ub. The llama.cpp rows were also copied from the 2026-05-31 sweep rather than rerun.
- Quantization: on CUDA, `--quant 8` resolves to the `q8_0` UQFF shard, which uses the same Q8_0 block format as the GGUF it is compared with. `--quant 4` resolves to uniform Q4K (`IsqBits::Four`), compared against llama.cpp's mixed Q4_K_M recipe, so the Q4 rows do not compare identical weight layouts.
- `cargo add mistralrs` gets 0.8.1 (2026-04-02), which predates the v0.8.2 CUDA work, because the workspace now pins Candle by git revision. Use a git dependency, the prebuilt binary or the PyPI wheel (0.9.4) for current code.

## Known shortcomings

- Hot path is CUDA C++ kernels (paged attention, FlashInfer, FA3, cuDNN), not Rust; different quantisation formats; the llama.cpp rows are copied from an earlier run with flags unstated; the appendix shows losses at 26B-A4B. Not a Rust-language win.
- Harness flaw in the benchmarked bench.rs (commit 8b49f963): prefill tok/s divides prompt tokens by a step time truncated with Duration::as_millis, so short prompts are overstated (the B200 E4B Q8 128-token 7,529.4 tok/s is exactly 128/17 ms; the 1.259x ratio could be 1.19x); decode counts 256 tokens over 255 steps (+0.4%); HEAD's bench.rs has since been rewritten. llama-bench ran the default ubatch, and llama.cpp's prefill is flat after 512 tokens (about 13.5k tok/s on B200) while mistral.rs climbs to 38k, so the 2x+ long-prompt gap is consistent with an untuned baseline batch size. The quantized GEMMs (mmq_gguf) are adapted from llama.cpp's own ggml-cuda MMQ kernels; --quant 8 resolves to Q8_0 UQFF (same block format) while --quant 4 is uniform Q4K against mixed Q4_K_M. Issue #2093: RTX 5080 paged-attention decode 25 vs 128 tok/s; crates.io is stuck at 0.8.1.

## Caveats and trade-offs

GPU-bound workload whose hot code is CUDA C++ on both sides: mistral.rs ships nvcc-compiled kernels (mistralrs-paged-attn/src/cuda: pagedattention_v1/v2 .cu, flashinfer_decode.cu, fa3 and flashinfer directories) and enables flash-attn and cuDNN, so Rust is only the host language and the win is not a Rust-over-C++ effect. Different quantisation formats (UQFF q8/q4 vs GGUF Q8_0/Q4_K_M), so the per-token work is not shown to be equal. Cross-run comparison: llama.cpp and vLLM rows were copied from the 2026-05-31 sweep, while mistral.rs rows were rerun on 2026-06-01 after a Gemma 4 KV-sharing correctness fix. llama-bench was run with only -ngl 99 -fa 1 recorded (no batch or ubatch tuning) and its build flags are unstated. The benchmarked commit sits on the cuda_graphs_v1 branch. Headline covers only Gemma 4 E4B; the appendix shows llama.cpp ahead at 26B-A4B short-prompt prefill on B200 and mistral.rs far behind vLLM in BF16 for 26B-A4B. First-party; 1 warmup and 3 measured iterations. [retier] The benchmarked bench.rs (8b49f963) divides prompt tokens by a step time truncated with Duration::as_millis, so short prompts are overstated (B200 E4B Q8 128-token 7,529.4 tok/s is exactly 128/17 ms; the 1.259x could be 1.19x); decode counts 256 tokens over 255 steps. llama-bench ran the default ubatch and llama.cpp's prefill is flat after 512 tokens while mistral.rs climbs, so the 2x+ long-prompt gap fits an untuned baseline batch size. The quantized GEMMs (mmq_gguf) are adapted from llama.cpp's own ggml-cuda MMQ kernels; --quant 4 is uniform Q4K against mixed Q4_K_M. Issue #2093: RTX 5080 paged-attention decode 25 vs 128 tok/s.

GPU inference through CUDA; uses its own UQFF quantization format for the Q4/Q8 rows; the README table shows near parity for 26B-A4B decode against llama.cpp (46.8 vs 46.4 tok/s on GB10) and mistral.rs behind vLLM BF16 on 26B-A4B prefill (592.2 vs 3878.6 tok/s on GB10).

## Maintenance

Very active (release v0.9.4 on 2026-09-24, last commit 2026-10-01, 7.7k stars, MIT) and easy to try through prebuilt binaries or the PyPI wheel. However, the measured v0.8.2 numbers come from a side branch and a benchmark harness that has since been rewritten, so treat the speedups as first-party and approximate.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party release report (releases/v0.8.2/report.md) with commands, commits and GPU models, but llama.cpp's build flags (CUDA architectures, GGML options) are not stated and the llama.cpp rows were copied from an earlier sweep, so not A; no independent measurement, so C.
- **Verifier notes:** Numbers match the report exactly; metadata correct (7.7k stars, MIT, last commit 2026-10-01). Shortcomings to record: hot path is CUDA C++ kernels (partly wrapped FlashInfer/FlashAttention/cuDNN), so it is off-thesis for a Rust-vs-C++ wave; different quantisation formats; cross-run baseline rows; llama.cpp flags and batch settings unstated; appendix losses at 26B-A4B and vs vLLM BF16.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-68 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/EricLBuehler/mistral.rs/HEAD/releases/v0.8.2/report.md>
  - <https://raw.githubusercontent.com/EricLBuehler/mistral.rs/HEAD/README.md>
  - <https://github.com/EricLBuehler/mistral.rs>
  - <https://github.com/EricLBuehler/mistral.rs/commits/master>
  - <https://github.com/EricLBuehler/mistral.rs/tree/master/mistralrs-paged-attn/src>
  - <https://github.com/EricLBuehler/mistral.rs/tree/master/mistralrs-paged-attn/src/cuda>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/EricLBuehler/mistral.rs/HEAD/releases/v0.8.2/report.md>
  - <https://raw.githubusercontent.com/EricLBuehler/mistral.rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/EricLBuehler/mistral.rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/EricLBuehler/mistral.rs/HEAD/mistralrs-cli/src/commands/bench.rs>
  - <https://raw.githubusercontent.com/EricLBuehler/mistral.rs/8b49f96392a767ea25a08af27669999a20e8a59e/mistralrs-cli/src/commands/bench.rs>
  - <https://raw.githubusercontent.com/EricLBuehler/mistral.rs/8b49f96392a767ea25a08af27669999a20e8a59e/mistralrs-core/src/engine/mod.rs>
  - <https://raw.githubusercontent.com/EricLBuehler/mistral.rs/8b49f96392a767ea25a08af27669999a20e8a59e/mistralrs-core/src/sequence.rs>
  - <https://raw.githubusercontent.com/EricLBuehler/mistral.rs/8b49f96392a767ea25a08af27669999a20e8a59e/mistralrs-cli/src/commands/serve.rs>
  - <https://raw.githubusercontent.com/EricLBuehler/mistral.rs/8b49f96392a767ea25a08af27669999a20e8a59e/mistralrs-cli/src/commands/quant.rs>
  - <https://raw.githubusercontent.com/EricLBuehler/mistral.rs/8b49f96392a767ea25a08af27669999a20e8a59e/mistralrs-core/src/pipeline/isq.rs>
  - <https://raw.githubusercontent.com/EricLBuehler/mistral.rs/8b49f96392a767ea25a08af27669999a20e8a59e/mistralrs-quant/src/lib.rs>
  - <https://raw.githubusercontent.com/EricLBuehler/mistral.rs/HEAD/mistralrs-quant/kernels/mmq_gguf/mmq_gguf.cuh>
  - <https://raw.githubusercontent.com/EricLBuehler/mistral.rs/HEAD/docs/src/content/docs/guides/perf/paged-attention.mdx>
  - <https://raw.githubusercontent.com/EricLBuehler/mistral.rs/HEAD/docs/src/content/docs/reference/environment-variables.md>
  - <https://github.com/EricLBuehler/mistral.rs>
  - <https://github.com/EricLBuehler/mistral.rs/tree/master/mistralrs-cli/src>
  - <https://github.com/EricLBuehler/mistral.rs/tree/master/mistralrs-quant/kernels>
  - <https://github.com/EricLBuehler/mistral.rs/tree/master/mistralrs-quant/kernels/mmq_gguf>
  - <https://github.com/EricLBuehler/mistral.rs/tree/master/mistralrs-paged-attn/src/cuda>
  - <https://github.com/EricLBuehler/mistral.rs/tree/master/docs>
  - <https://github.com/EricLBuehler/mistral.rs/releases>
  - <https://github.com/EricLBuehler/mistral.rs/issues?q=is%3Aissue+gemma+4+slow>
  - <https://github.com/EricLBuehler/mistral.rs/issues?q=is%3Aissue+llama.cpp+slower>
  - <https://github.com/EricLBuehler/mistral.rs/issues/2093>
  - <https://crates.io/api/v1/crates/mistralrs>
  - <https://pypi.org/pypi/mistralrs/json>
  - <https://pypi.org/pypi/mistralrs-cuda/json>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/ericlbuehler/mistral.rs`) · [data/wave14/enrich/raw/github_com_ericlbuehler_mistral_rs.json](../../../data/wave14/enrich/raw/github_com_ericlbuehler_mistral_rs.json) (enrichment confidence 0.72)

</details>
