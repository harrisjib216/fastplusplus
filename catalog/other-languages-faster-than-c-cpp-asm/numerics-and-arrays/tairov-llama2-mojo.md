# llama2.mojo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Mojo` · `MIT` · 🟢 active

> Single-file Mojo port of karpathy's llama2.c fp32 CPU inference; 1.1-1.5x llama2.c tok/s in the author's same-session runs.

| | |
|---|---|
| **Beats** | llama2.c (karpathy/llama2.c, OpenMP build); also llama.cpp CPU |
| **Claimed result** | README (last run 2026-09-12, Mojo 1.0.0, PR #102 build). Same-session 4 vCPU Intel Xeon Skylake AVX-512 VM: llama2.c OpenMP 4 threads 292/117/53/5.2 tok/s vs llama2.mojo -j 4 327/150/66/6.8 for stories15M/42M/110M/TinyLlama-1.1B (1.12x/1.28x/1.25x/1.31x, derived from page data); single-threaded llama2.c 105/40/16/1.7 vs llama2.mojo -j 1 154/54/22 (1.35-1.47x, derived from page data). upgradelog.md reports another run of the same build at -j 4 400/159/58 and -j 1 143/51/21 against the same llama2.c figures, and the author states +-10% run-to-run noise with both sides at the VM's \~20 GB/s memory-bandwidth ceiling. The Mac M1 Max table (llama2.mojo 1283/506/218 tok/s with 8 workers vs llama2.c 730/270/102 and llama.cpp 890/420/187) pairs a 2026 Mojo run with llama2.c and llama.cpp figures carried over unchanged from the Nov 2023 README (then labelled 6 threads, Mojo 1025/490/195), so its 1.8-2.1x ratio is cross-run. i7-8700 (2023 run): parity, 440 vs 435, 63 vs 64 and 7.25 vs 7.25 tok/s. The headline 'outperforms llama2.c by 30% ... llama.cpp by 20%' dates from the 2023 M1 Max figures. |
| **Workload** | CPU inference of llama2 models (TinyStories 15M/42M/110M and TinyLlama-1.1B) in tokens per second, multi-threaded. |
| **Metric** | throughput |
| **Hardware** | Apple M1 Max (Mojo column 2026 with 8 workers; llama2.c and llama.cpp columns from a Nov 2023 run with 6 threads); 4 vCPU Intel Xeon Skylake AVX-512 VM, Ubuntu 26.04 (same-session 2026 table); Intel Core i7-8700 3.2 GHz, Ubuntu 20.04 (2023 table). |
| **Compiler and flags** | Mojo 1.0.0 (Modular 26.5) for the 2026-09 runs (the README now targets Mojo 1.1.0, whose threading change was not re-benchmarked); llama2.c compiler, flags and commit not stated for any table (upstream 'make runomp' is gcc -Ofast -fopenmp -march=native); llama.cpp version, build and model format not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | README: the Mojo version 'leverages Mojo's SIMD & vectorization primitives' and parallelizes the matmul (explicit SIMD plus a worker pool) instead of relying on C compiler auto-vectorization. |
| **Adoption** | 2.1k stars |
| **Last commit** | 2026-09-19 |
| **Links** | [repository](https://github.com/tairov/llama2.mojo) · [benchmark](https://github.com/tairov/llama2.mojo) |

## Verdict

The author measured, in the same session on a 4 vCPU Intel Xeon Skylake AVX-512 VM (Ubuntu 26.04, Mojo 1.0.0, PR #102 build, greedy decoding, 256 tokens, best of 3), 327/150/66/6.8 tok/s at -j 4 against llama2.c OpenMP at 4 threads 292/117/53/5.2 for stories15M/42M/110M/TinyLlama-1.1B (1.12-1.31x). Single-threaded it measured 154/54/22 against 105/40/16 (1.35-1.47x), with byte-identical greedy output and the llama2.c build flags unstated. The README's 30% and llama.cpp +20% headline and its M1 Max 1.8-2.1x table are cross-run comparisons, and a 2023 i7-8700 run showed parity.

## Use it when

- Experimenting with Mojo for CPU inference, or reading a compact (about 1100-line) reference transformer forward pass with explicit SIMD and manual thread partitioning
- Tiny fp32 llama2 checkpoints (15M-110M parameters) on multi-core x86-64 with AVX-512 or Apple Silicon, where the author measured 1.12-1.31x llama2.c OpenMP at 4 threads and 1.35-1.47x single-threaded on a Skylake VM
- As a template for replacing per-call OpenMP fork/join with a persistent worker pool and barriers in a memory-bandwidth-bound decode loop

## Skip it when

- Production or larger-model inference: the code is fp32-only, with no quantization, no GGUF and no 7B/13B support (TODO issues #52, #64 and #65 are closed; the README lists only the stories models and TinyLlama-1.1B); llama.cpp or llama2.c's int8 runq fit better
- Anywhere you need the published numbers to hold for the code you install: the README targets Mojo 1.1.0, but its tables come from the Mojo 1.0.0 PR #102 build, and the Mojo 1.1 rewrite was not re-benchmarked
- Projects that cannot follow Mojo toolchain churn: each release from 0.25 to 0.26 to 1.0 to 1.1 needed source changes (upgradelog.md), and MAX is now a hard dependency for parallelize
- GPU inference (not supported) or batched or server workloads (one sequence, one process)

## How it is fast

The matmul is explicit SIMD (vectorize at nelts = max(16, native float32 width)) with up to three weight matrices fused per pass over the activation vector (matmul_rows[n] for Q/K/V and w1/w3). The PR #102 build that was benchmarked used a persistent worker pool: each worker owns fixed row and head slices for the whole forward pass, stages are separated by a sense-reversing spin barrier (31 per token on stories15M), and RMSNorm is recomputed per worker to drop barriers. llama2.c instead runs an OpenMP parallel-for per matmul and per attention loop. Both techniques can be reproduced in C; the gain is design, not language.

## Compared with alternatives

Pick it over llama2.zig (cgbur), whose claim is single-threaded against gcc -Ofast llama2.c, when you want a multi-threaded port with an explicit worker-pool design to study. Pick llm.mojo for training rather than inference, and fastGPT (Fortran) for GPT-2 rather than llama2. For actual deployment none of these beats llama.cpp.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Mojo 1.1.0 and MAX 26.6.0 (max.algorithm.parallelize) from PyPI; a host C compiler to link executables |
| **Minimum toolchain** | Mojo 1.1.0 / MAX 26.6.0 (current master); the benchmarked build needed Mojo 1.0.0 (Modular 26.5) |
| **Platforms** | Linux x86-64 and macOS Apple Silicon per the README tables; others not documented |
| **Thread safety** | Not documented; one Transformer owns one shared worker state and one KV cache, so it serves one generation stream at a time |
| **Drop-in for the baseline** | partial: reads llama2.c's .bin checkpoints and tokenizer.bin and gives byte-identical greedy output, but it is a Mojo program with its own CLI (-j, -pc), not a C library |

## Gotchas

- The benchmarked code is not the shipped code. The 2026-09-12 tables were measured on the PR #102 build, which started workers-1 persistent threads once via std.runtime.asyncrt.TaskGroup. The Mojo 1.1 commit (2026-09-19) replaced that with one max.algorithm.parallelize dispatch per token, and upgradelog.md itself measured about 200 us per parallelize dispatch on the same VM because MAX pool threads sleep and wake slowly. If that cost recurs once per token, it is roughly 6-8% of a 2.5-3 ms stories15M token, which would cut the 1.12x 4-thread margin over llama2.c (327 vs 292 tok/s) to about 1.05x, inside the stated noise.
- The 4-thread margins sit inside the author's stated +-10% run-to-run noise: stories15M -j 4 is reported as both 327 and 400 tok/s for the same build against one llama2.c figure of 292. The llama2.c build (make target, compiler, flags, commit) and OMP_NUM_THREADS handling are not stated in the README, PR #102 or agents-optimization.md. The M1 Max table pairs a 2026 Mojo run with 2023 llama2.c and llama.cpp columns.
- The current code runs spin barriers inside a parallelize dispatch, so it relies on MAX co-scheduling all -j workers at once. If the pool has fewer free threads than workers, waiting workers spin, with a sched_yield every 4096 iterations. -j is silently clamped to num_performance_cores().
- The tok/s methodology matches llama2.c (the timer starts after the first token; the rate is (pos-1)/elapsed, prompt tokens included), except that llama2.c fflushes stdout after every token and llama2.mojo's print does not flush.

## Known shortcomings

- The M1 Max 1.8-2.1x headline is cross-run (llama2.c and llama.cpp columns are November 2023 figures at 6 threads, only the Mojo column was re-run in 2026 with 8 workers); the valid Xeon VM table gives 1.12-1.31x at 4 threads (within the author's own 10% noise) and 1.35-1.47x single-threaded; llama2.c flags unstated; the speedup comes from threading and tiling, not Mojo; Mojo 1.1 code not re-benchmarked.
- Benchmarked build differs from the shipped code: the tables come from the PR #102 TaskGroup persistent pool (Mojo 1.0), while the Mojo 1.1 commit does one max.algorithm.parallelize per token and the author's own upgradelog measured about 200 us per dispatch; if that cost recurs each token, the 15M 4-thread margin falls from 1.12x to about 1.05x, inside the stated +-10% noise. Spin barriers now run inside parallelize, so all -j workers must be co-scheduled. llama2.c build flags are still unstated; the timing method otherwise matches llama2.c.

## Caveats and trade-offs

First-party numbers. The M1 Max headline table is a cross-run comparison: the llama2.c and llama.cpp columns are the Nov 2023 figures (6 threads) left unchanged when only the Mojo column was re-measured on 2026-09-12 with 8 workers, so its 1.8-2.1x ratio and the llama.cpp comparison are not valid evidence; the 2023 i7-8700 table shows parity. The valid same-session evidence is the Xeon Skylake 4 vCPU VM table: 1.12-1.31x at 4 threads (the author notes both sides sit at the VM's \~20 GB/s memory-bandwidth ceiling with +-10% noise, and another run in upgradelog.md shows 400 vs 292 tok/s on stories15M) and 1.35-1.47x single-threaded, with the llama2.c compiler, flags and commit unstated. Greedy output is byte-identical to llama2.c, so the work is the same. The multi-thread win comes from a persistent spin-barrier worker pool (31 barriers per token, per-worker redundant RMSNorm) against llama2.c's per-call OpenMP parallel for, and the single-thread win from tuned SIMD tiling (nelts), both reproducible in C; the optimisation was done by coding agents (agents-optimization.md). The Mojo 1.1 update (2026-09-19) replaced the TaskGroup pool with one max.algorithm.parallelize dispatch per forward pass and was not re-benchmarked. The linked engiware.com M1 Max comparison does not resolve (DNS failure) and arXiv 2502.01651 is blocked here, so no independent numbers were read. [retier] The tables come from the PR #102 TaskGroup persistent pool (Mojo 1.0); the Mojo 1.1 commit does one max.algorithm.parallelize per token, which the author's upgradelog measured at about 200 us per dispatch, so the 15M 4-thread margin could fall from 1.12x to about 1.05x, inside the stated +-10% noise. Spin barriers now run inside parallelize, so all -j workers must be co-scheduled. llama2.c build flags are unstated.

Needs the Mojo toolchain and MAX (parallelize), and tracks Mojo releases closely (updated for Mojo 1.1); single-file inference tool, not a general tensor library.

## Maintenance

Active (last commit 2026-09-19, Mojo 1.1 port), MIT-licensed single file with 2.1k stars. All visible issues are closed; it tracks each Mojo release, and the current threading code is untimed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party README tables. The only same-session comparison is the 4 vCPU Xeon Skylake VM table (2026-09, Mojo 1.0.0, llama2.c OpenMP 4 threads vs llama2.mojo -j 4 and both single-threaded; best of 3 and byte-identical greedy output per agents-optimization.md), with the llama2.c compiler, flags and commit unstated, so C. The headline M1 Max table is a cross-run comparison: README history (3c556c3, f6ce354 vs 0baf4d4) shows the llama2.c and llama.cpp columns unchanged since the Nov 2023 6-thread run while only the Mojo column was re-measured in 2026 with 8 workers.
- **Verifier notes:** Keep at C, but stop quoting the M1 Max 1.8-2.1x and the 'llama.cpp by 20%' line: they compare a 2026 Mojo run (8 workers) with 2023 llama2.c/llama.cpp figures (6 threads). Valid evidence is the Xeon VM table, 1.12-1.31x at 4 threads (near the author's stated +-10% noise on stories15M) and 1.35-1.47x single-threaded, with llama2.c flags unstated; the win comes from threading and tiling design, not Mojo itself, and the current Mojo 1.1 code was not re-benchmarked.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-04 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/tairov/llama2.mojo/master/README.md>
  - <https://github.com/tairov/llama2.mojo>
  - <https://github.com/tairov/llama2.mojo/commits/master>
  - <https://github.com/tairov/llama2.mojo/commits/master/README.md>
  - <https://github.com/tairov/llama2.mojo/tree/master/tests>
  - <https://raw.githubusercontent.com/tairov/llama2.mojo/master/agents-optimization.md>
  - <https://raw.githubusercontent.com/tairov/llama2.mojo/master/upgradelog.md>
  - <https://raw.githubusercontent.com/tairov/llama2.mojo/3c556c3/README.md>
  - <https://raw.githubusercontent.com/tairov/llama2.mojo/f6ce354/README.md>
  - <https://raw.githubusercontent.com/tairov/llama2.mojo/0baf4d4/README.md>
  - <https://raw.githubusercontent.com/karpathy/llama2.c/master/Makefile>
- **Sources the enricher read:**
  - <https://github.com/tairov/llama2.mojo>
  - <https://raw.githubusercontent.com/tairov/llama2.mojo/master/README.md>
  - <https://raw.githubusercontent.com/tairov/llama2.mojo/master/llama2.mojo>
  - <https://raw.githubusercontent.com/tairov/llama2.mojo/master/agents-optimization.md>
  - <https://raw.githubusercontent.com/tairov/llama2.mojo/master/upgradelog.md>
  - <https://github.com/tairov/llama2.mojo/pull/102>
  - <https://github.com/tairov/llama2.mojo/issues?q=is%3Aissue>
  - <https://github.com/tairov/llama2.mojo/commits/master>
  - <https://raw.githubusercontent.com/karpathy/llama2.c/master/run.c>
  - <https://raw.githubusercontent.com/karpathy/llama2.c/master/Makefile>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/tairov/llama2.mojo`) · [data/wave14/enrich/raw/github_com_tairov_llama2_mojo.json](../../../data/wave14/enrich/raw/github_com_tairov_llama2_mojo.json) (enrichment confidence 0.7)

</details>
