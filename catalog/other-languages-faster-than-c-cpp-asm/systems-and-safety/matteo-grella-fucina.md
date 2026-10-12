# Fucina (Zig tensor runtime and LLM inference engine)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Zig` · `MIT` · 🟢 active

> Pure-Zig CPU tensor/autograd runtime and GGUF LLM engine; outruns llama.cpp's CPU backend on most dense Qwen3 prefill shapes.

| | |
|---|---|
| **Beats** | llama.cpp CPU backend (ggml kernels, llama-bench with -ngl 0), same GGUF file and thread count |
| **Claimed result** | docs/BENCHMARK.md (snapshot 2026-07-04, updates 2026-07-10), ratio = Fucina / llama.cpp tok/s. Apple M1 Max, 8 threads: of 236 sweep cells Fucina faster in 221, parity 13, llama.cpp faster 2; dense prefill per-format geomeans 1.18-1.81x (Qwen3 0.6B seven formats and 1.7B; Qwen3.5-0.8B 1.07x on 4 lengths); Qwen3-30B-A3B MoE prefill pp64-256 1.44-2.09x; dense decode Q4_K_M/Q4_K_S +15 %, Q8_0 +14 %. Intel i9-13950HX (AVX2 + AVX-VNNI, no BLAS either side): dense Qwen3-0.6B paired-gate median ratios 1.32-1.95 per quantized format (maxima up to 2.56); 2026-07-10 dispatch fix took x86 dense decode Q5_K_M to 1.016, Q5_K_S 1.055, Q6_K 1.057; 30B MoE mid-batch pp15-33 moved from 0.36-0.52x to Q5_K_M 1.15-1.22x and Q6_K 0.97-1.05x. llama.cpp wins or open gaps: Qwen3.5-0.8B Q8_0 pp32 0.86x, 30B Q6_K decode 0.88x on M1 (no page-cache prewarm), MoE decode 0.87-0.95x on M1 and 0.971-0.972x on x86, Q6_K 30B pp31-33 0.965-0.987x and pp64-256 0.93-0.97x on x86, Gemma-4-26B pp1-9 0.85-0.99x on x86, Gemma-4-26B mid-batch prefill on M1 0.72-0.91x cool (listed as an open gap, while the scoreboard reports 1.17-2.15x from a session in which llama.cpp ran below its own best values), and pp256 with Q4_K-transcoded experts about 15-17 % behind. |
| **Workload** | Prompt prefill (pp) and decode (tg) tokens per second for Qwen3 0.6B/1.7B, Qwen3.5, Qwen3-30B-A3B MoE and Gemma-4-26B-A4B GGUF models in several quantizations, CPU-only on both sides, paired same-machine runs over many prompt lengths. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Max (arm64, 8 threads, macOS) and Intel Core i9-13950HX (Raptor Lake 8P+16E, AVX2 + AVX-VNNI, no AVX-512, Linux) |
| **Compiler and flags** | Fucina: Zig 0.16.0, zig build -Doptimize=ReleaseFast with the default native target (no -Dtarget); off macOS the default is -Dblas=none, on macOS the default build uses Accelerate CBLAS for f32 GEMMs at m &gt;= 16. llama.cpp: build 30af6e2 pinned in tools/fetch_refs.sh, whose --build step runs cmake -DCMAKE_BUILD_TYPE=Release -DGGML_METAL=OFF -DLLAMA_CURL=OFF (CPU-only, Accelerate BLAS left on under macOS). The x86 llama-bench build was verified as GGML_BLAS=OFF, GGML_NATIVE=ON (-march=native), GGML_LLAMAFILE=ON, GGML_CPU_REPACK=ON, GGML_OPENMP=ON, but its binary reported build_commit unknown; the x86 leg of another record says both engines were compiled on the box with gcc-12 / zig native. The C/C++ compiler for the M1 llama.cpp build is not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Author attributes wins to its own CPU kernels and scheduling (for example phased-chain MoE scheduling and f32-accumulate f16 GEMM) and, on M1, to llama.cpp's cost at the Accelerate/AMX switch; no language-level mechanism is claimed. |
| **Adoption** | 21 stars |
| **Last commit** | 2026-09-09 |
| **Links** | [repository](https://github.com/matteo-grella/fucina) · [benchmark](https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/docs/BENCHMARK.md) |

## Verdict

Author-run paired comparisons against llama.cpp build 30af6e2 (llama-bench -ngl 0, same GGUF, 8 threads), snapshot 2026-07-04 with 2026-07-10 updates. On an M1 Max (llama.cpp with Accelerate) Fucina led in 221 of 236 prompt-length and decode cells, with dense Qwen3 prefill geomeans of 1.18-1.81x (partly llama's Accelerate switch at batch 32) and dense decode up to +15%. On an i9-13950HX with no BLAS on either side, dense Qwen3-0.6B per-format medians were 1.32-1.95x, while MoE decode, Q4_K-expert pp256 and small-batch Gemma prefill still favour llama.cpp.

## Use it when

- CPU-only Qwen3 dense GGUF inference (0.6B-1.7B measured) on Apple Silicon or AVX2/AVX-VNNI x86, where prompt prefill at 1-256 tokens dominates: dense prefill geomeans 1.18-1.81x on M1 Max and per-format medians 1.32-1.95x on an i9-13950HX
- Zig projects that want an in-process tensor, autograd and LLM stack with no C/C++ build system and no Python runtime
- CPU training and fine-tuning experiments on the same weights you serve (LoRA on a quantized Qwen3 GGUF at about 932 ms/step for 0.6B on M1 Max, per README)
- MoE checkpoints larger than RAM through --moe-stream (README: Qwen3-235B and DeepSeek V4 Flash decode on a 64 GB machine)
- Copy-heavy generation (grounded copy, code edits), where its draft-free lossless speculative decoding gave 1.12-2.3x

## Skip it when

- GPU serving: the runtime is eager and offloads to Metal or CUDA only at the GEMM seam, and the README says it will never reach TensorRT-class GPU throughput
- MoE decode or Q4_K-expert models: llama.cpp stays ahead on MoE decode (0.87-0.95x on M1, 0.971-0.972x on x86) and on pp256 with Q4_K-transcoded experts (about 15-17% behind); Gemma-4-26B small-batch prefill is 0.85-0.99x on x86, and mid-batch prefill on M1 is listed as an open gap at 0.72-0.91x
- Architectures outside its model list; llama.cpp covers far more families and backends
- Code that needs a stable API or toolchain: pre-1.0 ('Expect churn') and pinned to Zig 0.16.0 exactly
- Memory-tight hosts: experts are copied into resident packed buffers rather than mmap'd, and dense Q5_K weights are held twice (GGUF blocks plus the Q5_Kx8 pack)

## How it is fast

Hand-written Zig @Vector kernels are specialised at compile time for the host ISA (NEON/sdot on Apple Silicon, AVX2/AVX-VNNI on x86). Quantized weights are repacked into interleaved RHS layouts (for example Q5_Kx8) whose arithmetic is byte-exact with ggml's block formats, f16 GEMMs accumulate in f32, and attention is query-tiled with an online softmax. MoE layers use a 'phased chain' scheduler over routed token-expert pairs (engaged from 64 pairs) with small-m column chunking, and experts are copied into resident packed buffers at load instead of read through mmap. Execution is eager with a reusable buffer pool and no graph or fusion pass. On the M1, part of the prefill margin is llama.cpp's own switch to Accelerate/AMX at batch &gt;= 32, which costs it heavily at pp32-129.

## Compared with alternatives

Pick Fucina over mistral.rs when inference is CPU-only or you want a Zig-native library that also trains: mistral.rs's record is CUDA against llama.cpp's CUDA backend, while Fucina's is ggml's CPU backend. For NVIDIA GPU serving, mistral.rs is the better fit.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none required (build.zig.zon has no dependencies); optional BLAS (Accelerate default on macOS; MKL, OpenBLAS or BLIS auto-detected on native Linux), optional Metal or CUDA offload (cuBLAS loaded with dlopen, vendored PTX), optional vendored llguidance (-Dllguidance=true) |
| **Minimum toolchain** | Zig 0.16.0 exactly (minimum_zig_version in build.zig.zon; README: other versions will not build) |
| **Platforms** | Tuned for aarch64 NEON/dotprod (Apple Silicon) and x86-64 AVX2/AVX-VNNI; a scalar reference backend covers other CPUs; CI runs ubuntu-latest and macos-15; the build targets the host CPU, so cross builds need -Dcpu |
| **Thread safety** | Not documented beyond a thread-safe reusable buffer pool (README Design) and a bounded worker team (default 8, build-time ceiling 1-64) |
| **Drop-in for the baseline** | partial — it reads the same GGUF files and lmserve speaks the OpenAI chat-completions and responses API, but there is no llama.h-compatible C API and only the listed model families load |

## Gotchas

- Harness asymmetry on MoE rows: tools/bench_gate.py feeds Fucina a 4-token seed repeated to length N (ids_repeated), while llama-bench feeds uniformly random token IDs (std::rand() % n_vocab in test_prompt). Dense compute does not depend on token content, but MoE routing does. BENCHMARK.md's own profile counters saw only about 52 of 128 Qwen3-30B-A3B experts active per pp256 batch on that prompt, where uniform routing predicts about 124. Fucina therefore streams fewer expert matrices and runs fuller per-expert GEMMs than llama.cpp does on its random prompt, so the MoE prefill ratios (Qwen3-30B-A3B 1.44-2.09x on M1, x86 Q5_K_M pp64-256 1.24-1.30x, Gemma-4-26B) are likely flattered by an unquantified amount; the dense rows are unaffected.
- The 'biases every ratio against Fucina' note is overstated. benchOnePass stops the prefill timer before the sampler runs, and the last layer computes only the last query row. llama-bench's generation loop requests logits for every token (batch.add(..., true) in test_gen). The only extra work on Fucina's side is one greedy sample per decode step.
- Build defaults matter. -Dmax-threads is a compile-time ceiling defaulting to 8 workers (FUCINA_MAX_THREADS can only lower it), so rebuild for bigger CPUs. Native Linux builds auto-link MKL, OpenBLAS or BLIS when ldconfig lists one, although BENCHMARK.md calls -Dblas=none the default off macOS, so pass -Dblas=none to reproduce the no-BLAS x86 record. Binaries are tuned to the build host, and a bare -Dtarget silently drops the fast kernels.
- M1 protocols are mixed. The Gemma-4 and Qwen3.5 rows are Fucina best-of against llama means, and Gemma ran a fresh Fucina process per length against one warm llama process. The Gemma mid-batch scoreboard (1.17-2.15x) comes from a session where llama ran below its own best (pp16 58.4 vs 82.1 tok/s), while the open-gaps list gives 0.72-0.91x.

## Known shortcomings

- fetch_refs.sh builds llama.cpp Release, so optimisation levels match, but Fucina's macOS build also uses Accelerate for f32 at m&gt;=16; the Gemma M1 scoreboard's 1.17-2.15x contradicts the 0.72-0.91x open gap in the same document; the x86 llama-bench build_commit is unknown; claims updated for the 2026-07-10 fixes.
- Harness flaw on the MoE rows: bench_gate.py feeds Fucina a 4-token seed repeated (ids_repeated) while llama-bench feeds random IDs (std::rand() % n_vocab); the document's own counters show about 52 of 128 experts active at pp256 against about 124 under uniform input, so the MoE prefill ratios are likely flattered by an unknown amount (dense rows unaffected). The 'biased against Fucina' note is overstated: the prefill timer stops before the sampler. The native Linux build auto-links MKL, OpenBLAS or BLIS; the thread ceiling is 8 at build time.

## Caveats and trade-offs

Author-run, first-party record with one dated snapshot (2026-07-04) against a pinned llama.cpp build, so results age as llama.cpp advances. On the M1 llama.cpp's Accelerate/AMX path switches on at batch &gt;= 32 and the document says that transition costs it heavily at pp32-129 (up to 7.2x at f16 pp32), so part of the prefill win is a llama.cpp threshold effect; Fucina's own macOS default build also routes f32 GEMMs at m &gt;= 16 to Accelerate, so the M1 rows are not BLAS-free on either side (the x86 rows are). Gemma-4 and Qwen3.5 M1 rows use best-of Fucina numbers (flagged by the author as favourable to Fucina), and the Gemma mid-batch session had llama.cpp below its strongest recorded values; the same document lists Gemma-4-26B mid-batch prefill on M1 as an open gap at 0.72-0.91x cool, contradicting the scoreboard's 1.17-2.15x. The x86 llama-bench binary reported build_commit unknown, so its commit rests on the recorded build flags. Laptop thermals and page cache move results by several percent; some cells are same-day reruns after a 2026-07-10 scheduler fix. Fucina's loops include logits/sampler work llama-bench skips (biases against Fucina). Different kernels and scheduling from ggml, so this is not a Zig-versus-C++ language comparison. tools/gen_optim_goldens.py is under CC-BY-NC-4.0 (rest MIT). [retier] MoE prefill rows are not like-for-like: bench_gate.py feeds Fucina a 4-token seed repeated (ids_repeated) while llama-bench feeds random IDs (std::rand() % n_vocab); the document's own counters show about 52 of 128 experts active at pp256 against about 124 under uniform input, so those ratios are likely flattered (dense rows unaffected). The 'biased against Fucina' note is overstated: the prefill timer stops before the sampler. The native Linux build auto-links MKL, OpenBLAS or BLIS; the thread ceiling is 8 at build time.

CPU-first runtime written in pure Zig (needs Zig 0.16); covers GGUF Qwen3, Qwen3.5 and Gemma-4 families plus training, speculative decoding and ASR/TTS runners; llama.cpp still wins several MoE decode and small-batch cells.

## Maintenance

Active: v0.5.1, last commit 2026-09-09, 684 commits, 21 stars, no issues filed. MIT except tools/gen_optim_goldens.py (CC-BY-NC-4.0). The API is pre-1.0 and tied to Zig 0.16.0, and the README says development leans heavily on coding agents with human review.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** docs/BENCHMARK.md compares against llama.cpp build 30af6e2 on the same GGUF files and thread counts, with public harness code (tools/bench_gate.py paired gate driving llama-bench -ngl 0; tools/fetch_refs.sh pins llama.cpp and builds it with cmake -DCMAKE_BUILD_TYPE=Release -DGGML_METAL=OFF -DLLAMA_CURL=OFF), Fucina built with Zig 0.16.0 ReleaseFast native, verified x86 GGML flags, and named CPUs (Apple M1 Max, Intel i9-13950HX); the headline numbers in the record appear on the page.
- **Verifier notes:** Numbers checked against the BENCHMARK.md scoreboard and full tables; fetch_refs.sh shows llama.cpp built CMAKE_BUILD_TYPE=Release, so same_opt_level is effectively true (Release with -march=native vs ReleaseFast native), while same_algorithm stays false (own quantized kernels and MoE scheduling vs ggml; Accelerate on M1 on both sides for some f32 shapes). Corrected claimed_speedup for the 2026-07-10 updates (Q5_K/Q6_K x86 decode now wins, MoE x86 band flipped) and added the Q4_K-experts pp256 loss and the internal Gemma M1 contradiction. Metadata (MIT, 21 stars, 2 forks, last commit 2026-09-09, active) checked.
- **Fields the verifier corrected:** `compiler_and_flags`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-64 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/docs/BENCHMARK.md>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/README.md>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/tools/fetch_refs.sh>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/tools/bench_gate.py>
  - <https://github.com/matteo-grella/fucina>
  - <https://github.com/matteo-grella/fucina/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/README.md>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/docs/BENCHMARK.md>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/tools/bench_gate.py>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/tools/fetch_refs.sh>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/build.zig>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/apps/qwen3/bench.zig>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/apps/qwen3/main.zig>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/apps/qwen3/generate.zig>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/apps/qwen3/options.zig>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/src/models/qwen3/model.zig>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/src/models/qwen3/runner.zig>
  - <https://raw.githubusercontent.com/matteo-grella/fucina/HEAD/.github/workflows/ci.yml>
  - <https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/llama-bench/llama-bench.cpp>
  - <https://github.com/matteo-grella/fucina>
  - <https://github.com/matteo-grella/fucina/tree/main/apps/qwen3>
  - <https://github.com/matteo-grella/fucina/commits/main>
  - <https://github.com/matteo-grella/fucina/issues?q=is%3Aissue>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/matteo-grella/fucina`) · [data/wave14/enrich/raw/github_com_matteo_grella_fucina.json](../../../data/wave14/enrich/raw/github_com_matteo_grella_fucina.json) (enrichment confidence 0.8)

</details>
