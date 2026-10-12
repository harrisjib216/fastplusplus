# Mooncake.jl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Julia` · `MIT` · 🟢 active

> Julia source-to-source AD compiler (forward, reverse, Hessians) that roughly halves warm gradient time versus Zygote on CPU Flux models.

| | |
|---|---|
| **Beats** | Zygote.jl (default reverse-mode AD behind Flux) |
| **Claimed result** | Flux benchmark README: on CPU, 'Mooncake is 2.03 times faster on warm gradients by geometric mean' (Mooncake/Zygote time ratio 0.493) across 19 models; LSTM(3 =&gt; 5) warm 4.04 ms Zygote vs 1.75 ms Mooncake; RNN(3 =&gt; 2) 1.62 ms vs 313 us. GPU only 1.05x faster warm (ratio 0.952). First gradient is slower: geometric-mean ratio 10.57 on CPU and 3.26 on GPU. |
| **Workload** | Gradient evaluation of 19 small Flux models (Dense, Conv, BatchNorm, LayerNorm, MultiHeadAttention, RNN, LSTM, GRU and chains) on CPU and GPU, inputs enlarged 32x, first-gradient time and warm-gradient time measured separately. |
| **Metric** | throughput |
| **Hardware** | aarch64-linux-gnu; CPU: Cortex-A725 + Cortex-X925; GPU: NVIDIA GB10 |
| **Compiler and flags** | Julia 1.12.7, Flux 0.16.11, Mooncake 0.5.51 (ed99f98b0-dirty), CUDA 6.3.1, cuDNN 6.3.1; 1 Julia thread, BLAS lbt 1 thread; 2.0-second warm budget, 32x input workload. Run with: julia --project=test/integration_testing/flux test/integration_testing/flux/benchmarks.jl. No explicit compiler flags (Julia JIT). |
| **Adoption** | 409 stars, 38 forks; main README: 'On one system, Flux benchmarks found Mooncake gradient evaluations after warm-up were 2.03 times as fast as Zygote on CPU across 19 models, with comparable GPU performance.' |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/chalk-lab/Mooncake.jl) · [benchmark](https://github.com/chalk-lab/Mooncake.jl/blob/HEAD/test/integration_testing/flux/README.md) |

## Verdict

The repository's auto-generated Flux benchmark (Julia 1.12.7, Flux 0.16.11, Mooncake 0.5.51 at a dirty commit, 1 Julia thread, 1 BLAS thread, inputs enlarged 32x, median of at least 10 warm samples in a 2 s budget, first gradient in a fresh process) on an Arm GB10 machine (Cortex-X925 + Cortex-A725, NVIDIA GB10 GPU) found Mooncake's warm gradients 2.03x faster than Zygote by geometric mean over 19 small Flux models on CPU and 1.05x on GPU, with first gradients 10.57x (CPU) and 3.26x (GPU) slower. The baseline is Zygote, not a vendor kernel library, and the run is first-party on one machine.

## Use it when

- Julia training or inference loops that call the gradient of the same function on same-shaped inputs many times, so the one-off cache preparation is amortised
- Small, recurrent or allocation-heavy CPU models where Zygote spends time on run-time overhead: in the Flux benchmark RNN gradients were about 5x faster (1.62 ms vs 313 us) and Maxout about 12x (136 us vs 11.4 us)
- Numerical Julia code that mutates arrays in place, which the README names as the main coverage gain over Zygote, ReverseDiff and ForwardDiff
- Projects that need forward mode, reverse mode and Hessians (forward-over-reverse) from one package

## Skip it when

- Short-lived scripts or one-shot gradients: first gradients were about 10x slower than Zygote on CPU by geometric mean (Dense(2 =&gt; 4): 12.5 s vs 693 ms) and about 3x slower on GPU
- GPU-bound models: warm GPU gradients were only 1.05x faster by geometric mean, and about half the GPU rows were slightly slower than Zygote
- Normalisation and attention layers on CPU: LayerNorm (1.38x slower), MultiHeadAttention (1.37x slower) and Flux.Scale (1.26x slower) lost to Zygote warm
- Code using try/catch in reverse mode, mutation of globals, threads/tasks, KernelAbstractions-style foreign-call CUDA kernels, or self-referential types; the known-limitations page lists these, some as silent wrong-gradient cases
- Anything outside Julia: it cannot be called from C++; C/C++ projects should look at Enzyme or the C++ tape libraries instead

## How it is fast

It runs AD on Julia's type-inferred, optimised IRCode instead of tracing at run time: each primal statement becomes a forward fragment and a pullback fragment, these are assembled into separate forward and pullback CFGs (with block stacks and edge-specific reverse blocks for phi nodes), lowered back to IRCode, optimised by the Julia compiler and wrapped in opaque closures. The prepared cache owns all gradient buffers and reuses them in place on every call, so warm calls avoid most allocation. The cost is compile time: the first gradient includes building and compiling the derived rule.

## Compared with alternatives

Pick Mooncake when your model is in Julia and you want a pure-Julia reverse-mode backend that handles mutation and beats Zygote warm; for C/C++ code it is not an option, and Enzyme (LLVM-level AD, also usable from Julia) or the C++ tape libraries XAD, FastAD and Adept-2 are the catalogued choices.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | ADTypes, ChainRulesCore, DispatchDoctor, ExprTools, MistyClosures, PrecompileTools, plus stdlib LinearAlgebra, Random, Test; optional package extensions for CUDA, cuDNN, Flux, NNlib, LuxLib, Distributions, SpecialFunctions and others |
| **Minimum toolchain** | Julia 1.10.8 (compat '\~1.10.8, \~1.11.6, \~1.12.1, \~1.13.0'); only the current LTS (1.10) and latest stable (1.13) are officially supported and CI-tested |
| **Platforms** | any platform Julia runs on; GPU through the CUDA/cuDNN extensions (benchmark run on aarch64 with an NVIDIA GB10) |
| **Thread safety** | Not guaranteed: the known-limitations page says there are no thread-safety guarantees for differentiating code that uses tasks or threads. A cache owns mutable gradient buffers, so sharing one cache across threads is unsafe (inferred from the in-place buffer design). |
| **Drop-in for the baseline** | partial: a different API (prepare a cache, then value_and_gradient!!) rather than Zygote.gradient, but it differentiates the same Flux models without model changes |

## Gotchas

- The returned gradient aliases the cache's own buffers; the next value_and_gradient!! call overwrites it, so copy it if you keep it
- A cache is tied to its input types and sizes; a differently sized input raises an error, so variable batch sizes need one cache per shape
- args_to_zero = false skips cotangent zeroing and can silently corrupt gradients of other arguments (issue #1238) unless the argument has no differentiable data
- Reverse mode can stop LLVM from vectorising loops that vectorise in the primal; the docs recommend hand-written rrule!! rules for hot SIMD loops (as done for kron)

## Known shortcomings

- Julia only, not callable from C++; first gradient 3-10x slower (compilation); benchmarks run from a '-dirty' tree.
- Docs list silent wrong-gradient cases: global/NoTangent aliasing (#1295), type-parameter data, explicit invoke (#1300), args_to_zero=false corrupting gradients (#1238). No thread-safety guarantee. Julia only, not callable from C++.

## Caveats and trade-offs

Single system (Arm GB10 machine: Cortex-X925 + Cortex-A725, NVIDIA GB10) and tiny Flux layers enlarged 32x. Several warm CPU rows are slower than Zygote (LayerNorm(2) 1.38x, MultiHeadAttention(16) 1.37x, Flux.Scale 1.26x, SkipConnection 1.03x). On GPU the warm gain is only 1.05x by geometric mean, and several layers are slower. First gradient is much slower (geometric-mean ratio 10.57 on CPU, 3.26 on GPU; for example Dense(2 =&gt; 4) 12.5 s vs 693 ms) because Mooncake's measurement includes prepare_gradient_cache. The recorded revision is 'ed99f98b0-dirty' (benchmarks.jl marks any git status output as dirty, so the run may include uncommitted changes). Baseline is Zygote.jl, not oneDNN/cuDNN/XNNPACK/Eigen. Julia library, not callable from C++.

Julia only. Very high first-call (compilation) latency: first gradient about 10x slower than Zygote on CPU. Supports mutation without hand-written rules, forward and reverse mode. README says performance varies by workload.

## Maintenance

Actively developed (last commit 2026-09-30, version 0.5.61 in Project.toml, 409 stars, no open bug-labelled issues), MIT-licensed, installable through the Julia package manager; the maintainers state a conservative, correctness-first scope and plan to move rules for non-Base packages out of the repository.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The auto-generated Flux README gives per-model first-gradient and warm-gradient times for Mooncake vs Zygote on CPU and GPU. The harness is public (test/integration_testing/flux/benchmarks.jl: median of at least 10 samples within a 2-second budget, fresh process for first-gradient runs), the toolchain is stated (Julia 1.12.7 JIT, 1 thread, exact run command; Julia takes no compiler flags) and the hardware is named (Cortex-X925 + Cortex-A725 CPU, NVIDIA GB10).
- **Verifier notes:** All quoted numbers verified in the Flux README (2.03x CPU warm, 0.493 and 10.57 CPU ratios, 0.952 and 3.26 GPU ratios, LSTM 4.04 ms vs 1.75 ms, RNN 1.62 ms vs 313 us); benchmarks.jl opened. Metadata matches: MIT, 409 stars, not a fork, last commit 2026-09-30. Scope: Julia-only; keep as a non-C++ entry or flag for the language filter.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/chalk-lab/Mooncake.jl>
  - <https://raw.githubusercontent.com/chalk-lab/Mooncake.jl/HEAD/test/integration_testing/flux/README.md>
  - <https://raw.githubusercontent.com/chalk-lab/Mooncake.jl/HEAD/test/integration_testing/flux/benchmarks.jl>
  - <https://raw.githubusercontent.com/chalk-lab/Mooncake.jl/HEAD/LICENSE>
  - <https://github.com/chalk-lab/Mooncake.jl/commits>
- **Sources the enricher read:**
  - <https://github.com/chalk-lab/Mooncake.jl>
  - <https://raw.githubusercontent.com/chalk-lab/Mooncake.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/chalk-lab/Mooncake.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/chalk-lab/Mooncake.jl/HEAD/SUPPORT_POLICY.md>
  - <https://raw.githubusercontent.com/chalk-lab/Mooncake.jl/HEAD/test/integration_testing/flux/README.md>
  - <https://raw.githubusercontent.com/chalk-lab/Mooncake.jl/HEAD/test/integration_testing/flux/benchmarks.jl>
  - <https://raw.githubusercontent.com/chalk-lab/Mooncake.jl/HEAD/docs/make.jl>
  - <https://raw.githubusercontent.com/chalk-lab/Mooncake.jl/HEAD/docs/src/known_limitations.md>
  - <https://raw.githubusercontent.com/chalk-lab/Mooncake.jl/HEAD/docs/src/developer_documentation/reverse_mode_design.md>
  - <https://raw.githubusercontent.com/chalk-lab/Mooncake.jl/HEAD/docs/src/interface.md>
  - <https://raw.githubusercontent.com/chalk-lab/Mooncake.jl/HEAD/docs/src/tutorial.md>
  - <https://github.com/chalk-lab/Mooncake.jl/issues?q=is%3Aissue+is%3Aopen+performance>
  - <https://github.com/chalk-lab/Mooncake.jl/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/chalk-lab/mooncake.jl`) · [data/wave8/enrich/raw/github_com_chalk_lab_mooncake_jl.json](../../../data/wave8/enrich/raw/github_com_chalk_lab_mooncake_jl.json) (enrichment confidence 0.8)

</details>
