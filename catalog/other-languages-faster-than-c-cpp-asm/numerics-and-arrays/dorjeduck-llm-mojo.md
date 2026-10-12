# llm.mojo (Mojo port of llm.c, CPU)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Mojo` · `MIT` · 🟢 active

> Single-file Mojo port of llm.c's GPT-2 CPU training loop; about 1.17x faster per step than the May-2024 train_gpt2.c with OpenMP on one M2 MacBook Pro.

| | |
|---|---|
| **Beats** | llm.c train_gpt2.c (karpathy/llm.c, with and without OpenMP) |
| **Claimed result** | README table (M2 MacBook Pro, average training-step time, B=4 x T=64 = 256 tokens per step): train_gpt2.mojo 1704 ms (150 tok/s) vs train_gpt2.c with OpenMP at OMP_NUM_THREADS=10 1987 ms (128 tok/s), about 1.17x (derived from page data); train_gpt2.c without OpenMP 7405 ms (34 tok/s). Commit b28eb10 (2026-07-18) replaced an earlier run with OMP_NUM_THREADS=64 (Mojo 1721 ms vs C 1836 ms, about 1.07x, derived from page data). variants.md reports a separate run of the same train_gpt2.mojo at 1716 ms. |
| **Workload** | GPT-2 124M CPU training steps (next_batch, forward, zero_grad, backward, AdamW update; B=4, T=64, steps 0-40, fp32) for train_gpt2.mojo vs llm.c train_gpt2.c on an M2 MacBook Pro. Both programs time the same region per step. Mojo prints a running average that includes step 0; how the C average was computed (train_gpt2.c prints only per-step times) is not stated. |
| **Metric** | throughput |
| **Hardware** | M2 MacBook Pro |
| **Compiler and flags** | Mojo 1.0.0b2 at measurement time: the table was refreshed in commit b28eb10 (2026-07-18), whose pixi.toml pins mojo ==1.0.0b2. The repo moved to Mojo 1.0.0 and max 26.5.0 on 2026-08-13 without re-running the table. Run as 'mojo train_gpt2.mojo', with B=4 and T=64 as compile-time constants. C side: compiler, flags and llm.c revision not stated; OMP_NUM_THREADS=10. llm.c's Makefile at 2d43e5b defaults to clang -Ofast -march=native with -Xclang -fopenmp on macOS, but the README does not say that build was used. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 383 stars |
| **Last commit** | 2026-10-04 |
| **Links** | [repository](https://github.com/dorjeduck/llm.mojo) · [benchmark](https://github.com/dorjeduck/llm.mojo) |

## Verdict

On an unspecified M2 MacBook Pro, the average time of a GPT-2 124M fp32 training step (B=4, T=64, 41 steps) was 1704 ms for train_gpt2.mojo on Mojo 1.0.0b2 versus 1987 ms for llm.c's May-2024 train_gpt2.c with OpenMP at 10 threads (about 1.17x, derived from page data) and 7405 ms without OpenMP; compiler, flags and run count for the C build are not given and the author calls the figures a general comparison.

## Use it when

- You want a readable, C-style reference of a full GPT-2 forward, backward and AdamW step in Mojo with raw pointers and manual memory management.
- Studying how Mojo's vectorize and parallelize compare with C plus OpenMP on the same loop nests (Apple silicon or Linux x86-64 and aarch64).
- Small-batch fp32 CPU training experiments at B=4, T=64 on GPT-2 124M where you control the Mojo toolchain version.
- As a starting point for MAX-kernel experiments: variants.md reports the same program at 232 ms per step (7.44x) once forward and backward matmuls go through linalg.matmul.

## Skip it when

- Real CPU training throughput: the naive matmul loops leave most of the speed on the table (the repo's own linalg V2 variant is 7.4x faster), and upstream llm.c has since added register tiling to matmul_forward.
- GPU training: CPU only; the README points to ulmentflam/llm.mojo for CUDA and Metal kernels.
- When you need bitwise agreement with llm.c or PyTorch: test.md says some logits and parameter tensors differ because vectorization reorders float sums; only the losses match within tolerance.
- Long-lived production code: the author says there are no concrete plans to develop it further, it pins one exact Mojo release, and changelog.md shows a source migration at each Mojo release (24.3 through 1.0.0).
- Batch size or sequence length other than the compile-time B=4, T=64 without editing the source; matmul_forward parallelism scales with B only.

## How it is fast

Every layer loop is written with Mojo's vectorize (SIMD width 4x the native fp32 width on Apple silicon, 2x elsewhere, unroll factor 4) and parallelize. The port parallelizes kernels that llm.c at 2d43e5b runs serially: encoder, layernorm, GELU, residual, attention backward, cross-entropy and the AdamW update over all 124M parameters (8 fixed chunks), while llm.c's OpenMP covers only matmul, attention forward and softmax and compiles gelu_backward in precise mode with scalar tanhf and coshf. Matmul uses the same naive loop nest as llm.c, but matmul_forward is split only over B=4 batch rows, where C's OpenMP spreads B\*T=256 rows. The win is therefore plausibly more parallel coverage of the cheap layers than better matmul code; the README gives no profile.

## Compared with alternatives

Pick llm.mojo over llama2.mojo, fastGPT or llama2.zig when you need the training side (backward pass and AdamW) rather than inference; those siblings only run generation and have stronger, repeatable inference comparisons against llama2.c or PyTorch.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Mojo 1.0.0 and max 26.5.0 (for parallelize) via pixi; Python with torch, transformers, tiktoken, numpy and tqdm to produce gpt2_124M.bin, the tokenizer file and the token datasets |
| **Minimum toolchain** | Mojo 1.0.0 (pinned exactly; benchmark measured on Mojo 1.0.0b2) |
| **Platforms** | osx-arm64, linux-64, linux-aarch64 (pixi.toml); CPU only |
| **Thread safety** | not documented (single-process training program; parallelism is internal) |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the comparison is not like-for-like in parallel coverage. llm.c train_gpt2.c at 2d43e5b runs AdamW, GELU, layernorm, residual, encoder, attention backward and cross-entropy backward single-threaded, while the Mojo port parallelizes all of them; the 1.17x step-time edge can come from that rather than from Mojo codegen, and Mojo's own matmul_forward uses only 4 workers.
- The reported margin is unstable: the earlier README run read 1721 ms vs 1836 ms (1.07x); commit b28eb10 says it 'corrected' the OpenMP thread count label from 64 to 10, and between the two runs the C time moved 8% while the Mojo time moved 1%. One run, no repetitions, and the C compiler, flags and average method are not stated.
- The M2 variant and core count are not named; OMP_NUM_THREADS=10 oversubscribes a base 8-core M2, and an even OpenMP split over mixed performance and efficiency cores can slow the C build, so the thread setting alone may explain part of the gap.
- Elementwise kernels split N into N // 8 chunks and drop any remainder; harmless for GPT-2 widths (multiples of 8) but wrong for shapes where B\*T\*C is not a multiple of 8.

## Known shortcomings

- C compiler, flags and llm.c revision unstated and the author disclaims precision; measured on Mojo 1.0.0b2 against a stale May 2024 llm.c; the earlier run was 1.07x at 64 threads, now 1.17x at 10.
- Harness asymmetry: llm.c train_gpt2.c at 2d43e5b runs AdamW (124M parameters), GELU, layernorm, residual, encoder, attention backward and cross-entropy single-threaded while the Mojo port parallelises all of them (its matmul_forward splits over only B=4), so the 1.17x step-time edge likely comes from parallel coverage, not codegen. Commit b28eb10 only relabelled OMP_NUM_THREADS 64 to 10; the C time moved 8% between runs and Mojo 1%; the M2 core count is not stated (10 threads oversubscribe a base 8-core M2). test.md shows some logits and parameters differing from the reference with only losses matching. The repo's own linalg V2 variant is 7.44x faster than the measured port.

## Caveats and trade-offs

The README calls the figures 'a general comparison rather than precise, repeatable metrics'. One machine, no run count, and a 1.17x edge that earlier read 1.07x at a different OpenMP thread count. It ports llm.c train_gpt2.c at 2d43e5b (May 2024); the README notes that upstream llm.c has since added register tiling to its CPU matmul, so the baseline is stale. The C compiler, flags and revision built are not stated (the commit message calls it the 'naive train_gpt2.c'). The numbers were measured on Mojo 1.0.0b2, not the 1.0.0 the repo now pins. A use-after-free in read_to_dtype_pointer (checkpoint loading, outside the timed loop) was fixed on 2026-08-13, after the benchmark. Mojo exposes only B=4-way parallelism in matmul_forward while C's OpenMP spreads B\*T=256 rows over 10 threads, so the comparison mixes scheduling and codegen differences. The project's stated aim is matching C, and the gap is within what thread settings changed between runs. [retier] Harness asymmetry: llm.c train_gpt2.c at 2d43e5b runs AdamW, GELU, layernorm, residual, encoder, attention backward and cross-entropy single-threaded while the Mojo port parallelises all of them (its matmul_forward splits over only B=4), so the 1.17x step-time edge likely comes from parallel coverage. Commit b28eb10 only relabelled the OMP thread count 64 to 10; the C time moved 8% between runs; the M2 core count is unstated (10 threads oversubscribe a base 8-core M2). test.md shows some logits and parameters differing from the reference, only losses match.

Needs Mojo 1.0 and max 26.5.0 (pinned in pixi.toml); CPU only; the README says no concrete plans to develop it further.

## Maintenance

Maintained in tracking mode (last commit 2026-10-04 fixed TinyStories shard order; Mojo 1.0.0 migration 2026-08-13 also fixed a use-after-free in checkpoint loading), MIT-licensed and small enough to copy, but the author has no plans to extend it and the benchmark numbers predate the Mojo 1.0.0 migration and rest on a baseline whose serial non-matmul kernels inflate the gap.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The first-party README Benchmarks table (M2 MacBook Pro) compares train_gpt2.mojo with llm.c's train_gpt2.c, and both programs are public. The C compiler, flags, the llm.c revision actually built and how the C average was computed are not stated, and the author calls the figures 'a general comparison rather than precise, repeatable metrics', so C.
- **Verifier notes:** Numbers match the README; metadata (MIT, 383 stars, 17 forks, last commit 2026-10-04, active) checks out, and llm.c is listed (wave 8), so baseline_in_list stays true. Kept at C. Shortcomings to record: C flags, compiler and revision unstated; author disclaims precision; stale May-2024 llm.c baseline that upstream has since optimised; measured on Mojo 1.0.0b2 before the 1.0.0 migration; margin moved from 1.07x (64 OpenMP threads) to 1.17x (10 threads) between runs; no mechanism stated (why_faster filled from reading the source). Not a duplicate: it is a Mojo port, not a wrapper of llm.c. same_algorithm stays true (same loop nests, different SIMD reduction order), same_opt_level stays null.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-22 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/dorjeduck/llm.mojo>
  - <https://github.com/dorjeduck/llm.mojo/commits>
  - <https://github.com/dorjeduck/llm.mojo/commit/b28eb109f7512eb90566e7dd8fbdbbe37d1b5464>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/HEAD/README.md>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/HEAD/train_gpt2.mojo>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/HEAD/variants.md>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/HEAD/changelog.md>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/HEAD/usage_instructions.md>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/HEAD/pixi.toml>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/b28eb109f7512eb90566e7dd8fbdbbe37d1b5464/pixi.toml>
  - <https://raw.githubusercontent.com/karpathy/llm.c/2d43e5b/Makefile>
  - <https://raw.githubusercontent.com/karpathy/llm.c/2d43e5b/train_gpt2.c>
- **Sources the enricher read:**
  - <https://github.com/dorjeduck/llm.mojo>
  - <https://github.com/dorjeduck/llm.mojo/commits>
  - <https://github.com/dorjeduck/llm.mojo/issues?q=is%3Aissue>
  - <https://github.com/dorjeduck/llm.mojo/pulls?q=is%3Apr>
  - <https://github.com/dorjeduck/llm.mojo/commit/b28eb109f7512eb90566e7dd8fbdbbe37d1b5464>
  - <https://github.com/dorjeduck/llm.mojo/commit/95674f6>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/HEAD/README.md>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/HEAD/train_gpt2.mojo>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/HEAD/variants.md>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/HEAD/changelog.md>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/HEAD/usage_instructions.md>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/HEAD/test.md>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/HEAD/pixi.toml>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/HEAD/requirements.txt>
  - <https://raw.githubusercontent.com/dorjeduck/llm.mojo/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/karpathy/llm.c/2d43e5b/train_gpt2.c>
  - <https://raw.githubusercontent.com/karpathy/llm.c/2d43e5b/Makefile>
  - <https://raw.githubusercontent.com/karpathy/llm.c/master/train_gpt2.c>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/dorjeduck/llm.mojo`) · [data/wave14/enrich/raw/github_com_dorjeduck_llm_mojo.json](../../../data/wave14/enrich/raw/github_com_dorjeduck_llm_mojo.json) (enrichment confidence 0.35)

</details>
