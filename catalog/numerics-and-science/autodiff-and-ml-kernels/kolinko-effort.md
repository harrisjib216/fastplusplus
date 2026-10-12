# Effort (bucketMul approximate matrix multiplication for LLM inference on Apple Silicon)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Swift` · `MIT` · 🟡 stale

> Swift/Metal LLM engine whose approximate bucketMul matrix-vector product trades quality for speed against Apple MPS on Apple Silicon.

| | |
|---|---|
| **Beats** | Apple MPS default matrix-vector multiplication (benchmark.swift prints 'Default Apple MPS implementation (comparable to llama.cpp)'); the project page also plots a llama.cpp tokens/s line |
| **Claimed result** | README and project page: 'At 50% effort, it performs as fast as regular matrix multiplications on Apple Silicon chips; at 25% effort, it is twice as fast while still retaining most of the quality.' The 'Pure Matrix Multiplication Performance' chart (docs/ryc/ryc0.1.png, read by eye) puts Apple MPS at about 26 tps and bucketMul at about 15 tps at 100% effort, about 26-27 tps at 50%, about 47-49 tps at 25%, reaching the 2x-MPS line (about 52 tps) only near 22% effort, where the chart marks 'breakdown on Mistral'. docs/gpu.html says parity with MPS is reached 'at 50-70% effort'. The tokens/s chart (ryc0.2.png) shows the actual (unadjusted) eval speed reaching the llama.cpp line (about 25 tok/s) only near 30% effort. |
| **Workload** | Single-token decode matrix-vector multiplication (one state vector times FP16 Mistral weight matrices on the Metal GPU): benchmark.swift times bucketMul (expertMul) on w1 (4096x14336) at several effort levels against MPS basicMul on 3x wq (3x4096x4096) scaled by 4/3, with warm-ups inside timeIt. |
| **Metric** | throughput |
| **Hardware** | Charts name no chip; the author's machine is an M2 Pro per docs/setup.html ('15ms on my M2 Pro'), and docs/gpu.html says bucketMul seems faster on M3 than on M2/M1. |
| **Adoption** | 233 stars |
| **Last commit** | 2024-07-01 |
| **Links** | [repository](https://github.com/kolinko/effort) · [benchmark](https://github.com/kolinko/effort/blob/main/docs/index.html) |

## Verdict

First-party only: on the author's Apple Silicon Mac (M2 Pro per the setup notes; the charts name no chip), FP16 Mistral 7B matrix-vector products timed in benchmarks/benchmark.swift show bucketMul at about 15 tps-equivalent at 100% effort, about 26-27 at 50% (roughly MPS's 26) and about 47-49 at 25% (about 1.85x MPS, read from chart images); 2x is reached only near 22% effort, where the chart marks a quality breakdown on Mistral. No Xcode or compiler settings are given, and actual tokens/s reaches the llama.cpp line (about 25 tok/s) only near 30% effort.

## Use it when

- Research on input-dependent (dynamic) weight skipping for batch-1 decode, where you want a working Metal reference of the bucket/dispatch idea to read or port.
- Experiments on Apple Silicon Macs with enough unified memory for FP16 Mistral 7B, where a 25-50% effort level and its quality loss are acceptable.
- Exploring 'ad hoc distillation' by loading only part of each matrix (percentLoad) to fit a model into less memory without retraining.
- Studying the speed/quality curve of approximate GEMV: the repo ships cosine-similarity, next-token agreement and multiple-choice quiz harnesses across effort levels.

## Skip it when

- Production or quality-sensitive inference: the author's own pages say the current implementation 'seems just broken' (Mistral worse than before, Mixtral 'barely works'), and early KL-divergence tests 'seem to not win against Quantization yet'.
- Anything outside macOS on Apple Silicon: Swift plus Metal only, Xcode project, no Linux/CUDA/CPU path (issue #5 asks for other platforms, unanswered).
- When you need exact results or full speed: at 100% effort bucketMul is slower than MPS (about 15 vs 26 matrix-only tps read from the project chart), and parity needs about 50-70% effort.
- Real end-to-end throughput: every generated token carries about 15 ms of overhead the author could not remove, attention is unoptimised and slows quickly with longer contexts, and only FP16 Mistral is wired up (Q8 incomplete, Q4 'extremely slow').
- Maintained dependencies: last commit 2024-07-01, one-person demo, and the weights repo has gone missing before (issue #3: huggingface kolinko/mistral-buckets returned 404, April 2024).

## How it is fast

Offline, each transposed weight row is cut into buckets of 16, sorted by absolute value, interleaved so that the largest-magnitude weights of every input dimension come first, and annotated with per-bucket mean-|w| statistics plus diagonal 'probe' weights; the 4 low bits of each FP16 weight store its output position. At decode time a GPU kernel estimates the cutoff for the chosen effort from probe x input products (top-k), a second kernel builds a dispatch list of only the bucket rows whose stat x input value clears the cutoff, and the bucketMul Metal kernel streams those rows, accumulating into 16 per-thread registers selected by the embedded position bits. The speedup comes from reading fewer weight bytes in a memory-bound GEMV; the author says the kernel reaches about 50-70% of memory bandwidth and is ALU-limited.

## Compared with alternatives

Among catalogued siblings, PowerInfer also skips weights based on the input (predicted-active neurons, CUDA/CPU on llama.cpp) and FastGEMV is an exact fp16/int GEMV for CUDA; pick Effort only when you want an Apple-Silicon Metal implementation of magnitude-sorted dynamic weight skipping to study or port, and use PowerInfer or an exact quantised kernel when you need working inference.

## Integration

| | |
|---|---|
| **Form** | source-drop (Xcode macOS command-line app in Swift with Metal shaders; no library target) |
| **Dependencies** | Apple Metal and MetalPerformanceShaders (MPS used for the baseline multiply and top-k); Xcode; converted bucketed FP16 Mistral weights (huggingface-cli download kolinko/mistral-buckets, or the built-in convert mode from .safetensors) |
| **Minimum toolchain** | not documented (Xcode project; Swift and Metal versions not stated) |
| **Platforms** | macOS on Apple Silicon only (author's M2 Pro; notes M3 seems faster than M1/M2) |
| **Thread safety** | not documented (single global BucketMul instance and GPU wrapper; dispatch uses atomics) |
| **Drop-in for the baseline** | partial — bucketMul(v:by:...) mirrors basicMul's calling style inside this engine, but it needs pre-bucketed weights, returns an approximation, and has no C/C++ or MPS-compatible API |

## Gotchas

- Output is nondeterministic: the dispatch list is built with atomic counters, so token generation varies between runs at the same effort (author's GPU page).
- The 4 low bits of every FP16 weight hold the output position (kernel reads as_type&lt;ushort&gt;(w) & 15), so stored weights lose mantissa precision even at 100% effort.
- The startup benchmark compares different matrices: MPS times 3 x wq (3 x 4096x4096, 50.3M weights) scaled by 4/3, while bucketMul times one w1 (4096x14336, 58.7M weights); derived from code, that charges the MPS line for about 14% more weights than bucketMul at 100% effort, and the printed 'tps' is matmul-only, not generation speed.
- On machines with 16 GB RAM or less the loader silently loads only 11/16 of each matrix (the message says 75%, or 37% for 8 GB, but both branches set 0xB), which lowers quality before you touch effort; kernels are tuned for 4096x14336 and need per-shape hand-tuning.

## Known shortcomings

- Swift/Metal only, not C++. Claim overstated: the chart shows about 1.85x over Apple MPS at 25% effort and 2x only near 22%, which the chart itself marks as 'breakdown on Mistral'; slower than MPS at 100%. Approximate (lossy) matmul. The author's own pages say the implementation 'seems just broken' for Mixtral and does not beat quantization yet.
- The startup benchmark charges MPS for about 14% more weights than bucketMul (3x wq 50.3M x 4/3 = 67.1M vs w1 58.7M, derived from benchmark.swift and timeit.swift). The 4 low bits of each FP16 weight store position, so precision is lost even at 100% effort; results are nondeterministic (atomic dispatch); machines with 16 GB or less silently load 11/16 of the weights; macOS-only; issue #5 unanswered and the HF weights repo 404'd once (issue #3).

## Caveats and trade-offs

First-party only; the speed charts are images on the project page (repo docs/ folder) with no chip label, raw timings, compiler or Xcode settings; the harness only prints timings when run. Read from the chart, 25% effort is about 1.85x MPS rather than 2x, 2x is reached only around 22% effort where the chart itself marks a quality breakdown on Mistral, and at 100% effort bucketMul is slower than MPS (about 15 vs 26 tps). The baseline timing compares different matrices (3x wq scaled by 4/3 vs one w1). Approximate method: lower effort skips weights, so output differs from exact matmul. The author's own pages say real generation has about 15 ms/token overhead (actual tok/s lower than the 'adjusted' line), that 'the current implementation seems just broken' for quality (Mistral worse than it used to be, Mixtral barely works), that output is nondeterministic (atomic dispatch), and that KL-divergence tests show it 'seems to not win against Quantization yet'. Last commit 2024-07-01. Repo identity inferred from the HN title and README (HN thread not opened).

Approximate computation: it skips the least important weights, so quality drops as effort falls; needs converted weights; written in Swift and Metal for macOS only, with no C++ API; the author describes it as a demo with 'ton of things to fix'.

## Maintenance

Stale since 2024-07-01 and self-described as a buggy demo looking for collaborators, but MIT-licensed; worth reading as a reference for the bucketMul idea rather than vendoring.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party only: the README states the parity/2x claim, and the project page source in the repo (docs/index.html, served as kolinko.github.io/effort) charts bucketMul tokens/s against an 'Apple's MPS speed' line and a llama.cpp line; the harness benchmarks/benchmark.swift (goQuickBucketPerformance, goBucketPerformance) times MPS basicMul against expertMul, but no compiler/flags are given and the charts name no chip, so C.
- **Verifier notes:** kolinko.github.io is blocked, but the same pages are checked into docs/ and were read via raw.githubusercontent.com, including the chart images. Shortcomings worth recording: author-reported quality/correctness regression ('implementation seems just broken', Mixtral barely works) and the 2x claim sits at the chart's own quality-breakdown point. Metadata on github.com: MIT, 233 stars, 17 forks, not a fork or archived, 331 commits, last commit 2024-07-01 (stale is right).
- **Fields the verifier corrected:** `benchmark_url`, `baseline`, `claimed_speedup`, `workload`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier; enricher
- **Pages the verifier opened:**
  - <https://github.com/kolinko/effort>
  - <https://github.com/kolinko/effort/commits>
  - <https://github.com/kolinko/effort/tree/main/benchmarks>
  - <https://github.com/kolinko/effort/tree/main/docs>
  - <https://github.com/kolinko/effort/blob/main/docs/index.html>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/README.md>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/benchmarks/benchmark.swift>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/docs/index.html>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/docs/gpu.html>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/docs/setup.html>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/docs/pesky.html>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/docs/bucketmul.html>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/docs/ryc/ryc0.1.png>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/docs/ryc/ryc0.2.png>
- **Sources the enricher read:**
  - <https://github.com/kolinko/effort>
  - <https://github.com/kolinko/effort/issues?q=is%3Aissue>
  - <https://github.com/kolinko/effort/issues/3>
  - <https://github.com/kolinko/effort/issues/5>
  - <https://github.com/kolinko/effort/tree/main/helpers>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/README.md>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/benchmarks/benchmark.swift>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/main.swift>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/loader.swift>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/bucketMul.swift>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/helpers/timeit.swift>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/helpers/mps.swift>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/docs/index.html>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/docs/equations.html>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/docs/bucketmul.html>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/docs/gpu.html>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/docs/q8.html>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/docs/pesky.html>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/docs/setup.html>
  - <https://raw.githubusercontent.com/kolinko/effort/HEAD/docs/about.html>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/kolinko/effort`) · [data/wave8/enrich/raw/github_com_kolinko_effort.json](../../../data/wave8/enrich/raw/github_com_kolinko_effort.json) (enrichment confidence 0.75)

</details>
