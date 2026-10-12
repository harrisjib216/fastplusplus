# llamafile tinyBLAS CPU matmul kernels

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `Apache-2.0` · 🟢 active

> tinyBLAS: register-tiled CPU GEMM kernels from llamafile; 1.3-5x faster LLM prompt eval than March-2024 llama.cpp, upstreamed since.

| | |
|---|---|
| **Beats** | llama.cpp CPU matmul (prior kernels); Intel MKL sgemm |
| **Claimed result** | 'prompt eval time with llamafile should go anywhere between 30% and 500% faster when using F16 and Q8_0 weights on CPU'; Mistral 7B f16 on Threadripper 7995WX: llamafile-0.7 485 vs llama.cpp 2024-03-29 197 prompt tok/s (eval 17 vs 16); TinyLlama f16 on Raspberry Pi 5: 62 vs 28 prompt tok/s (eval 5 vs 5); 810 GFLOPS on i9-14900K for a 513x512 \* 512x512 matmul vs MKL 295 GFLOPS at that size |
| **Workload** | LLM prompt-evaluation (prefill) tokens/sec on CPU with F16 and Q8_0 weights; also a raw GEMM GFLOPS comparison vs MKL. |
| **Metric** | throughput |
| **Hardware** | AMD Threadripper 7995WX; Raspberry Pi 5; Intel i9-14900K (plus others on the page) |
| **Compiler and flags** | -O3 -ffast-math -march=native mentioned for the example kernel; flags for the tok/s runs not stated |
| **Adoption** | 26.1k stars |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/mozilla-ai/llamafile) · [benchmark](https://justine.lol/matmul/) |

## Verdict

The author's blog (justine.lol/matmul, March 2024) compares llamafile 0.7 to llama.cpp builds from 2024-03-26/29 on an i9-9900, i9-14900K, Raspberry Pi 4/5, M2 Ultra and Threadripper 7995WX. Prompt tok/s improved by up to 3.8x (14900K f16) and 2.5x (7995WX f16), and by about 1.1-1.6x on Q8_0, while generation tok/s was flat. A single 513x512x512 GEMM on the i9-14900K hit 810 vs MKL's 295 GFLOPS. PR #6414 reports about 2x on F16 and 40% on Q4_0/Q8_0. Flags for the tok/s runs are not stated; first-party only.

## Use it when

- CPU-only LLM inference where prompt processing (prefill, batch n&gt;1) dominates: long prompts, RAG, summarization, LLaVA image tokens.
- F16/BF16/F32 weights on x86 with AVX2 or AVX-512, where the blog shows the largest gains (e.g. i9-14900K Mistral 7B f16 50 vs 13 prompt tok/s; 7995WX 485 vs 197).
- Small to mid GEMMs that fit in L2 (author's best case: under \~1000 prompt tokens, 512-wide matrices) where MKL's packing overhead dominates.
- Shipping one binary that runs on many OSes and CPUs: llamafile dispatches the right kernel at runtime.
- Borrowing a compact, MIT-licensed register-tiled GEMM micro-kernel design for your own C++ code (ggml/src/ggml-cpu/llamafile/sgemm.cpp in llama.cpp).

## Skip it when

- Token generation (n=1 matvec): memory-bound, and the tables show eval tok/s unchanged (e.g. 17 vs 16 on 7995WX).
- Large GEMMs: the author says that at 1024 'MKL wins once more'; use MKL/OpenBLAS/BLIS for general dense linear algebra.
- Apple Silicon: off by default on M2 in the upstream PR; on M2 Ultra TinyLlama q8_0 it was slower (457 vs 564 prompt tok/s).
- K-quants and other formats outside its supported set: the kernel returns false and you get the regular ggml path.
- If you already run a current llama.cpp: the kernels were merged there (default on), so the 2024 speedup is no longer an advantage over upstream.

## How it is fast

It unrolls both outer loops of the matmul into a fixed RM x RN tile of accumulator registers (outer-product register tiling, e.g. mnpack&lt;4,6&gt; with 32 vector registers, &lt;4,3&gt; with 16). Each loaded A vector is reused across several B columns, which cuts loads per FMA. It skips the cache-blocking/packing and malloc that MKL-style BLAS does, so it wins on cache-resident matrices. Threads take tile jobs from ggml's own threadpool and barrier, avoiding a second BLAS thread pool, and llamafile picks per-microarchitecture builds at runtime (AVX2, AVX-512F, Zen 4 AVX-512 BF16/VNNI, NEON).

## Compared with alternatives

Choose tinyBLAS for F16/BF16/Q8_0 prefill on x86 or ARM inside a ggml-based stack. Choose T-MAC for 2-4-bit weights or BitNet decoding, and the AVX512 DGEMM tutorial kernels or MKL for double-precision or large general GEMMs.

## Integration

| | |
|---|---|
| **Form** | source-drop (one sgemm.cpp/sgemm.h inside ggml), or the whole llamafile executable |
| **Dependencies** | ggml internals (ggml_compute_params, threadpool, quant block types); llamafile builds also need Cosmopolitan Libc |
| **Minimum toolchain** | C++17 (if constexpr); GCC or Clang with target intrinsics; the blog's example used -O3 -ffast-math -march=native; Clang takes about 45 s to compile the kernels (PR #6414) |
| **Platforms** | x86-64 (AVX/AVX2/AVX-512F/AVX512-BF16), aarch64 NEON (fp16 arithmetic optional); upstream also has POWER (MMA/VSX), s390x VXE and RISC-V RVV variants |
| **Thread safety** | Meant to be called by every ggml worker thread with its ith/nth; it coordinates through ggml barriers, so it is not a standalone thread-safe API |
| **Drop-in for the baseline** | partial — transparent inside llama.cpp/ggml (GGML_USE_LLAMAFILE, default on), but not a BLAS (sgemm/cblas) interface for other code |

## Gotchas

- Silent fallback: it handles only shapes where k is a multiple of the vector width and m a multiple of 4 (n &gt;= 2 except on POWER MMA), and only an F32 output; otherwise it returns false and the slower generic path runs.
- No bound on rounding error: the source says error 'grows along with k', and the blog warns ARMv8.2 fp16 accumulation without Kahan summation adds error.
- The repo now lives at github.com/mozilla-ai/llamafile; v0.10 rebuilt on a newer llama.cpp and dropped some features (pledge sandbox, localscore, stable diffusion).
- LLAMAFILE_DISABLE_SGEMM=1 turns the kernels off in llamafile; use it when you A/B test.

## Known shortcomings

- Gains are in prompt eval only (token generation barely changes); the March-2024 llama.cpp baseline has since merged these kernels.
- Kernels now in llama.cpp upstream (ggml/src/ggml-cpu/llamafile/sgemm.cpp, on by default), so the gain over current llama.cpp is gone; MKL wins at 1024-size GEMMs; on M2 Ultra TinyLlama q8_0 slower (457 vs 564 prompt tok/s); repo moved to mozilla-ai/llamafile.

## Caveats and trade-offs

Author's own blog post; PR https://github.com/ggml-org/llama.cpp/pull/6414 reports \~40% on Q4_0/Q8_0 and 2x on F16 with user reports. Gains are on prompt eval (prefill) only; token generation is roughly unchanged (memory-bound). Baseline is the March-2024 llama.cpp, which has since merged these kernels. MKL comparison is a single matrix size.

Kernels were upstreamed to llama.cpp (MIT); gains target prompt eval, not token generation; disabled by default on Apple M2.

## Maintenance

Active (Mozilla.ai, 26.1k stars, commits in Sept 2026); llamafile is Apache-2.0, but the kernels are MIT and already live in llama.cpp, so copy them from there.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** Author's own blog post with tok/s tables vs llama.cpp and a GFLOPS figure vs MKL on named CPUs; kernels are public but compiler version/flags for the reported runs and a runnable benchmark harness are not fully stated, so not A; first-party, so C.
- **Verifier notes:** Record said 790 GFLOPS; page says 810 GFLOPS on i9-14900K. Metadata confirmed: Apache-2.0, 26.1k stars, last commit 2026-09-30, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://justine.lol/matmul/>
  - <https://github.com/Mozilla-Ocho/llamafile>
  - <https://github.com/Mozilla-Ocho/llamafile/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Mozilla-Ocho/llamafile/HEAD/README.md>
  - <https://raw.githubusercontent.com/mozilla-ai/llamafile/HEAD/README_0.10.0.md>
  - <https://github.com/mozilla-ai/llamafile>
  - <https://raw.githubusercontent.com/mozilla-ai/llamafile/HEAD/llamafile/sgemm.cpp>
  - <https://raw.githubusercontent.com/ggml-org/llama.cpp/HEAD/ggml/src/ggml-cpu/llamafile/sgemm.cpp>
  - <https://justine.lol/matmul/>
  - <https://github.com/ggml-org/llama.cpp/pull/6414>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/mozilla-ocho/llamafile`) · [data/wave8/enrich/raw/github_com_mozilla_ocho_llamafile.json](../../../data/wave8/enrich/raw/github_com_mozilla_ocho_llamafile.json) (enrichment confidence 0.8)

</details>
