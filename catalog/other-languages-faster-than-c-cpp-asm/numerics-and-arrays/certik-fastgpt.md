# fastGPT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Fortran` · `MIT` · 🟢 active

> GPT-2 greedy inference in about 900 lines of Fortran on vendor sgemm; HF transformers/PyTorch takes 4-16% longer on M1 Max.

| | |
|---|---|
| **Beats** | HuggingFace transformers pipeline('text-generation', model='gpt2') on PyTorch, driven from Python by pt.py (transformers 4.26.1 per environment.yml; PyTorch version not pinned), with PyTorch's C++ ATen kernels and the same BLAS (Apple Accelerate or OpenBLAS); also picoGPT (NumPy) |
| **Claimed result** | README Benchmarks (Apple M1 Max, 20 tokens): with KV cache, fastGPT (Accelerate) 0.299 s vs PyTorch (Accelerate) 0.346 s (1.16x, derived from page data); fastGPT (Accelerate, fast_tanh) 0.288 s; OpenBLAS 1/2/4/8 cores fastGPT 0.837/0.514/0.341/0.339 s vs PyTorch 0.873/0.539/0.386/0.392 s. Without cache: Accelerate fastGPT 0.717 s vs PyTorch 0.787 s and picoGPT 0.765 s; OpenBLAS fastGPT 2.343/1.603/1.209/1.018 s vs PyTorch 2.356/1.520/1.104/0.997 s, so PyTorch is faster at 2, 4 and 8 cores. Total run including model load and Python imports: fastGPT (Accelerate, fast_tanh) 0.401 s vs picoGPT (8 cores) 3.445 s and PyTorch (OpenBLAS, 4 cores) 4.867 s. |
| **Workload** | GPT-2 124M inference, 20 generated tokens from a 19-token prompt, greedy decoding with KV cache, on Apple M1 Max at 1 to 8 cores. |
| **Metric** | latency |
| **Hardware** | Apple M1 Max |
| **Compiler and flags** | gfortran, version unstated (a gfortran=14.2.0 pin is commented out in environment.yml and postdates the 2023 numbers); current cmake/UserOverride.cmake Release flags: -O3 -march=native -ffast-math -funroll-loops. PyTorch side: prebuilt binaries, version and build flags unstated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Adoption** | 199 stars |
| **Last commit** | 2026-02-14 |
| **Links** | [repository](https://github.com/certik/fastGPT) · [benchmark](https://raw.githubusercontent.com/certik/fastGPT/HEAD/README.md) |

## Verdict

On an Apple M1 Max, GPT-2 124M generated 20 greedy tokens from a 19-token prompt with a KV cache in 0.299 s with fastGPT (gfortran, Accelerate sgemm) against 0.346 s for an HF transformers 4.26.1 pipeline on PyTorch (version unrecorded) with Accelerate, about 1.16x. With OpenBLAS at 1-8 cores PyTorch takes 4-16% longer, and without the cache PyTorch wins at 2, 4 and 8 cores (ratios derived from page data). Both sides call the same vendor sgemm, so the gap measures Python and HF dispatch overhead plus fastGPT's timer leaving out its own tokenizer, not Fortran code generation.

## Use it when

- You want a small, readable GPT-2 inference reference you can vendor into a Fortran or HPC code base (MIT license, no Python at run time).
- Short one-shot prompts from scripts where startup dominates: the README's total-run row is 0.401 s for fastGPT against 4.867 s for PyTorch, almost all of it Python imports and model loading.
- Apple Silicon with Accelerate, a single sequence, greedy decoding and tens of tokens, which is the setup the README benchmarks.
- Compiler or language work that needs a realistic, self-checking Fortran workload: CI builds it with gfortran and LFortran 0.60.0 and checks generated tokens against reference arrays.

## Skip it when

- Any model other than GPT-2, or anything needing top-k, top-p, temperature sampling, batching, quantised weights or training. None of these is implemented (issues #7 and #8 are open).
- Long generations or throughput serving: main copies the whole KV cache on every token, runs attention heads serially (issue #2 open) and spends most of its BLAS time packing operands. PR #88 measures main at 14.95 tok/s for 20 tokens and 10.92 tok/s for 1000 tokens on one i5-1235U core, and its unmerged fixes report 2.75-4.09x.
- Multi-core OpenBLAS without the KV cache: by the README's own table, PyTorch is faster at 2, 4 and 8 cores.
- Output that must match HF tokenization for arbitrary text: the pre-tokenizer splits only on space, comma and period, not on GPT-2's regex.
- Production embedding: generate() always prints each token to stdout, errors end the process with error stop, context is capped at n_ctx 1024, and the ifort segfault (issue #14) is still open.

## How it is fast

Every matmul (QKV projection, per-head K^T Q and V\*softmax, output projection, MLP, logits) is a cblas_sgemm call on column-major float32 arrays, through Accelerate on macOS or OpenBLAS when chosen. Layer norm, softmax, GELU and embedding are plain Fortran array loops built with -O3 -march=native -ffast-math -funroll-loops. Decoding uses a KV cache, so after the prompt prefill each step pushes one token through. Because PyTorch calls the same BLAS, the measured edge is the missing Python interpreter, HF generate() bookkeeping and per-op dispatch, plus a near-instant model load (raw float32 arrays read straight from the file). The README's fastest row also uses an optional polynomial fast_tanh inside GELU.

## Compared with alternatives

Pick fastGPT over llama2.zig, llama2.mojo or llm.mojo when you need GPT-2 weights or Fortran specifically. Those siblings run Llama-2 or GPT-2 training and are measured against llama2.c/llm.c at -O3, a tighter C baseline than this entry's Python-driven PyTorch.

## Integration

| | |
|---|---|
| **Form** | source-drop (CMake builds a static library `fastgpt` plus the gpt2 and chat executables; there is also an fpm package) |
| **Dependencies** | gfortran; for speed, a BLAS: Accelerate (macOS default) or OpenBLAS (-DFASTGPT_BLAS=OpenBLAS), plus an OpenMP runtime for the timer. The default elsewhere is Fortran intrinsic matmul. Pre-converted GGUF weights download from huggingface.co/certik/fastGPT. Converting weights yourself needs Python 3.9, TensorFlow 2.11 and gguf-py from llama.cpp commit 4e9a7f7. |
| **Minimum toolchain** | CMake 3.13; gfortran (CI pins 14.2.0 on macOS, version unpinned on Ubuntu) or LFortran 0.60.0; ifort is broken (issue #14) |
| **Platforms** | macOS (Accelerate, tested on Apple M1 Max) and Linux (OpenBLAS or intrinsic matmul); CI runs on macos-latest and ubuntu-latest. Release flags use -march=native, so binaries are not portable. |
| **Thread safety** | not documented; generate() takes the model as intent(in) and keeps its KV cache local, but it writes to stdout. The only parallelism is inside BLAS. |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness flaw: the fast_tanh rows (0.288 s, and the 0.401 s total run) cannot be rebuilt from the source as shipped. gpt2.f90 defines fast_tanh, but gelu() calls the intrinsic tanh. Open issue #25 shows that fast_tanh changes the last 9 of 100 greedy tokens on the 1558M model, so those rows do not compute the same output as PyTorch.
- Harness flaw: the timed regions differ. fastGPT's 'Running model' timer leaves out its own tokenizer, while pt.py times the whole pipeline() call, HF tokenization included. The README's example run prints 0.074 s encoding plus 0.304 s generation, 0.378 s, which is slower than PyTorch's 0.346 s (derived from page data). The PyTorch (Accelerate) row came from a conda-forge PyTorch that only ran after libcblas.3.dylib was symlinked over libopenblas.0.dylib (issue #26, PyTorch version unrecorded); none of that setup is in the repo.
- The default builds have no BLAS and a dead timer. The fpm build and the non-Apple CMake default (FASTGPT_BLAS=Fortran) link linalg_f.f90 (intrinsic matmul) and omp_dummy.f90, whose omp_get_wtime returns 0, so the run prints 'Time: 0.000s' and the speed ratio divides by zero. build.sh calls encode_input.py at the repo root, but that file now lives only in comparison/.
- generate() allocates and copies the whole KV cache in and out on every token: 2 x n_embd x 2 x n_layer x 4 bytes, about 147 KB per cached position for 124M, so the cost grows quadratically with length. The chat stop-text check slices output_txt from len-len('User:')+1, which is below 1 while the reply is shorter than 5 characters (an out-of-bounds substring that -fcheck=all Debug builds will trap).

## Known shortcomings

- Baseline is Hugging Face transformers on PyTorch driven from Python, not C/C++ at -O3, with the same BLAS on both sides so the gap is framework overhead; -ffast-math against a prebuilt PyTorch; pt.py hard-codes OMP_NUM_THREADS=1; PyTorch is faster without cache at 2-8 cores; the total-run row is startup-dominated.
- Harness flaws behind the README table: the fast_tanh rows (0.288 s, 0.401 s total) cannot be rebuilt from the shipped code (gelu() calls the intrinsic tanh, fast_tanh is unused) and open issue #25 shows fast_tanh changes the last 9 of 100 tokens on the 1558M model; the PyTorch Accelerate row (0.346 s) came from a conda PyTorch that ran only after symlinking libcblas.3.dylib over libopenblas.0.dylib (issue #26), PyTorch version unrecorded and the setup not in the repo; fastGPT's timer excludes its own tokenizer while pt.py times HF tokenization, and the README's own example (0.074 s encode plus 0.304 s run = 0.378 s) is slower than PyTorch's 0.346 s. fpm and non-Apple CMake builds default to the intrinsic matmul plus omp_dummy (omp_get_wtime returns 0, so the printed time is 0.000); the KV cache is copied in full every token; the chat stop-text substring reads out of bounds; build.sh calls a missing encode_input.py. Unmerged PR #88 reports 2.75-4.09x over main (i5-1235U) with 72% of main's time in OpenBLAS packing.

## Caveats and trade-offs

First-party numbers on one machine with one short prompt. The matmuls run through the same vendor BLAS in both programs, so the 3-16% gap is framework overhead (Python and HF transformers dispatch around each op, generate() bookkeeping) and kernel fusion, not Fortran code generation. The baseline is not a C/C++ program built at -O3: it is HF transformers on PyTorch driven from Python, timed by pt.py around the whole pipeline call (which also tokenizes and decodes), while fastGPT's 'Running model' time excludes its separately timed tokenizer. pt.py hard-codes OMP_NUM_THREADS=1, so the 2-8 core PyTorch rows needed an unrecorded edit. Flags are not equivalent: fastGPT uses -ffast-math (and an optional fast_tanh approximation) against prebuilt PyTorch. Without the KV cache, PyTorch beats fastGPT at 2, 4 and 8 OpenBLAS cores. The 0.401 s vs 4.867 s total-run comparison is dominated by Python imports and model loading. The README says speed comes 'by using Fortran' without a mechanism. [retier] The timed regions differ: fastGPT's 'Running model' timer leaves out its own tokenizer while pt.py times HF tokenization, and the README's own example (0.074 s encode plus 0.304 s run = 0.378 s) is slower than PyTorch's 0.346 s. The fast_tanh rows (0.288 s, 0.401 s total) cannot be rebuilt from the shipped code (gelu() calls the intrinsic tanh) and issue #25 shows fast_tanh changes 9 of 100 tokens on 1558M. The PyTorch Accelerate row ran only after symlinking libcblas.3.dylib over libopenblas.0.dylib (issue #26), PyTorch version unrecorded. Non-Apple default builds link omp_dummy, whose omp_get_wtime returns 0 (printed time 0.000).

GPT-2 only, greedy sampling only, no batching or training, GGUF model conversion script needed; builds with gfortran via fpm or CMake.

## Maintenance

Active but slow-moving (last commit 2026-02-14, mostly CI and LFortran upkeep; PR #88's reported 2.75-4.09x speedup has been open since March 2026 without a maintainer benchmark), MIT and small enough to vendor, but the README table dates from March 2023, before the GGUF loader, the Fortran tokenizer and the 2026 allocation changes, and it rests on harness flaws: fast_tanh rows that need a source edit and change the output (issue #25), a PyTorch Accelerate row from a symlinked conda BLAS (issue #26), a fastGPT timer that leaves out its 0.074 s tokenizer while pt.py's includes HF tokenization, and pt.py hard-coding OMP_NUM_THREADS=1 for the multi-core rows.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** README Benchmarks table (Apple M1 Max) is first-party; both programs are public (gpt2 driver, pt.py) and the current cmake/UserOverride.cmake gives gfortran Release flags, but the gfortran and PyTorch versions used are unstated and pt.py hard-codes OMP_NUM_THREADS=1, so the multi-core PyTorch rows cannot be reproduced from the repo as is. Not A, stays C.
- **Retiered** C to D: Enricher: the timed regions differ (fastGPT's timer excludes its own tokenizer while pt.py times HF tokenization) and the README's own example sums to 0.378 s against PyTorch's 0.346 s, the fast_tanh rows cannot be rebuilt from the shipped code and change the output, and the PyTorch Accelerate row needed an unrecorded library symlink hack; no valid like-for-like measurement remains: C to D.
- **Verifier notes:** Numbers match the README; record's '(1.16x, derived)' relabelled 'derived from page data', and the no-cache rows where PyTorch is faster (2-8 OpenBLAS cores) were added. Shortcomings: off-baseline (Python-driven HF transformers/PyTorch, not C/C++ at -O3), same BLAS on both sides so the gap is framework overhead, -ffast-math vs prebuilt PyTorch, pt.py hard-codes one thread, compiler and PyTorch versions unstated, PyTorch faster without cache at 2-8 cores, total-run row startup-dominated. Metadata checked: MIT, 199 stars, last commit 2026-02-14, active.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-03 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/certik/fastGPT>
  - <https://github.com/certik/fastGPT/commits>
  - <https://github.com/certik/fastGPT/tree/main/comparison>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/README.md>
  - <https://raw.githubusercontent.com/certik/fastGPT/main/CMakeLists.txt>
  - <https://raw.githubusercontent.com/certik/fastGPT/main/cmake/UserOverride.cmake>
  - <https://raw.githubusercontent.com/certik/fastGPT/main/pt.py>
  - <https://raw.githubusercontent.com/certik/fastGPT/main/environment.yml>
  - <https://raw.githubusercontent.com/certik/fastGPT/main/build.sh>
- **Sources the enricher read:**
  - <https://github.com/certik/fastGPT>
  - <https://github.com/certik/fastGPT/commits/main>
  - <https://github.com/certik/fastGPT/issues?q=is%3Aissue>
  - <https://github.com/certik/fastGPT/issues/26>
  - <https://github.com/certik/fastGPT/issues/25>
  - <https://github.com/certik/fastGPT/issues/80>
  - <https://github.com/certik/fastGPT/issues/14>
  - <https://github.com/certik/fastGPT/pulls>
  - <https://github.com/certik/fastGPT/pull/88>
  - <https://github.com/certik/fastGPT/tree/main/src>
  - <https://github.com/certik/fastGPT/tree/main/comparison>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/README.md>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/gpt2.f90>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/driver.f90>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/tokenizer.f90>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/main.f90>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/chat.f90>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/linalg_f.f90>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/linalg_c.f90>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/linalg_accelerate.c>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/linalg_openblas.c>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/omp.f90>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/omp_dummy.f90>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/pt.py>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/create_model.py>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/cmake/UserOverride.cmake>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/cmake/FindOPENBLAS.cmake>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/cmake/FindOMP.cmake>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/environment.yml>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/build.sh>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/ci/build.sh>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/.github/workflows/CI.yml>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/fpm.toml>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/input>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/tests/test_basic_input.f90>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/tests/test_more_inputs.f90>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/src/gpt2.f90>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/src/linalg_f.f90>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/src/omp_dummy.f90>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/app/gpt2.f90>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/app/chatgpt2.f90>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/comparison/encode_input.py>
  - <https://raw.githubusercontent.com/certik/fastGPT/HEAD/LICENSE>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/certik/fastgpt`) · [data/wave14/enrich/raw/github_com_certik_fastgpt.json](../../../data/wave14/enrich/raw/github_com_certik_fastgpt.json) (enrichment confidence 0.75)

</details>
