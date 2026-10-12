# atJIT (autotuning JIT on Easy::jit)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Interpreters and VMs](../README.md) › [JIT compilers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `BSD-3-Clause` · 🔴 abandoned

> Research JIT for C++ that specialises a function at runtime and autotunes LLVM knobs online; up to 1.48x over its own default on matmul.

| | |
|---|---|
| **Beats** | untuned default configuration of the same code as labelled 'Default' on the author's slide (optimisation level not stated, so not shown to be clang -O3 ahead-of-time or Easy::jit) |
| **Claimed result** | 'Up to 1.48x Speedup, aka 32.7% improvement!' on matrix multiply (slide 11 of doc/slides/ANL_Summer_Status_Update.pdf); bar chart reads roughly 660 microseconds for Default and roughly 445 for configuration G (read off the chart image, not printed numbers). |
| **Workload** | Square matrix multiply (MatMul template kernel) tuned online by random search over compiler knobs, slide 'Matrix Multiply Random Tuning Results' with configurations Default and A to G, running time in microseconds. |
| **Metric** | throughput |
| **Adoption** | 53 stars, 1 fork |
| **Last commit** | 2019-08-29 |
| **Links** | [repository](https://github.com/kavon/atJIT) · [benchmark](https://github.com/kavon/atJIT/blob/master/doc/slides/ANL_Summer_Status_Update.pdf) |

## Verdict

First-party July 2018 status-talk slides (doc/slides/ANL_Summer_Status_Update.pdf): slide 10 prints mean call times of 662,929 ns for atJIT's default knob configuration (inlining threshold 225, no loop hints) and 445,898 ns for the best random-search configuration (inlining threshold 976 plus unroll, vectorize width 8, interleave and distribute loop metadata), 1.487x derived from slide data, charted on slide 11 as 'up to 1.48x'. The kernel is a naive templated square matrix multiply specialised on DIM; matrix size, element type, CPU, compiler and flags are not stated, and no clang -O3 ahead-of-time or Easy::jit baseline was measured.

## Use it when

- A long-running process that calls the same hot numeric kernel (hundreds of microseconds or more per call) thousands of times, so per-call timing and background JIT compiles amortise.
- Kernels whose best unroll, vectorisation width or inlining choice depends on sizes that are fixed at runtime but unknown at build time (pass them as runtime values so they are specialised).
- Choosing among algorithm variants online via a tuned integer parameter (IntRange) measured on real inputs.
- Research or teaching on online autotuning: the knob set, random/Bayes/annealing tuners and the measurement policy are small and readable.

## Skip it when

- Short or rarely called functions: every reoptimize call builds a context and an Optimizer object and does a map lookup, every call is wrapped in steady_clock timing, and the first call per specialisation waits for an LLVM compile.
- Production code: abandoned since 2019-08-29 with open crash reports (#14 segfault calling a reoptimized function after repeated Bayes reoptimize, #13 stat-dumping segfault, #10 possible double free when an LLVM Module outlives its LLVMContext).
- Current toolchains: get-llvm.sh pins llvmorg-8.0.1 (X86 target only), CMake requires LLVM with RTTI and the libLLVM dylib, and CI only tested Ubuntu with LLVM 8; expect porting work on newer LLVM.
- When an ahead-of-time -O3 build or a library routine may already be as fast: the only published result compares the tuner's best variant with the JIT's own untuned default, on one naive triple-loop matrix multiply.
- When run-to-run reproducibility matters: the random tuner seeds from the system clock and tuned configurations are not persisted (listed as a TODO), so each process re-tunes from scratch.

## How it is fast

Runtime specialisation (constant-folding runtime values into the JIT-compiled LLVM IR, as in Easy::jit) plus online empirical autotuning: each new variant applies a knob configuration (LLVM loop metadata llvm.loop.unroll.count/full, vectorize.enable/width, interleave.count, distribute.enable, licm_versioning.disable; inlining threshold; optimizer and codegen opt levels; FastISel; IPRA; Polly tiling only in the deprecated POLLY_KNOBS build). Calls are timed with steady_clock until the standard error falls under pct_err (default 2%), and the best variant is kept. Search strategies are random search, Bayesian optimisation (XGBoost is a build requirement) and simulated annealing; compile jobs run on libdispatch serial queues so callers keep getting the current best while new variants compile.

## Compared with alternatives

Pick atJIT over Easy::jit, which it is built on, only when you want the JIT to search compiler knobs per specialised kernel rather than just specialise on runtime values, and can accept LLVM 8, XGBoost, libdispatch and open crash bugs; for plain runtime specialisation Easy::jit is the lighter choice. RapidUDF and the copy-and-patch JITs in this category solve expression or language compilation, not autotuning of existing C++ functions.

## Integration

| | |
|---|---|
| **Form** | shared lib (ATJitRuntime) plus a clang plugin pass, used through the atjitc clang++ wrapper |
| **Dependencies** | LLVM and Clang 8 built from source with RTTI and libLLVM dylib (get-llvm.sh, llvmorg-8.0.1), libdispatch (Grand Central Dispatch), XGBoost (xgboost/get.sh); optional out-of-tree LLVM+Polly for loop knobs (deprecated, sources out of sync per issue #11); Google Benchmark for benchmarks; Python 2.7, lit and Valgrind for tests; OpenCV for examples |
| **Minimum toolchain** | C++17 (README: GCC &gt;= 7 or Clang &gt;= 4 to build), LLVM 8+ (CMake refuses LLVM &lt; 8), CMake 3.8 (CMakeLists.txt; README says 3.5) |
| **Platforms** | x86-64 Linux (Ubuntu in GitLab CI; get-llvm.sh builds only the X86 target); TODO.md lists ARM and macOS as untested |
| **Thread safety** | not documented; ATDriver keeps per-function state in a std::unordered_map with no locking, so use one driver per thread; compile jobs run on libdispatch serial queues, and Optimizer::status() is documented as imprecise under concurrent recompile. |
| **Drop-in for the baseline** | false: the program must be built with atjitc (clang plugin) and every call site rewritten to call AT.reoptimize(...) and then the returned wrapper. |

## Gotchas

- The auto const& returned by reoptimize refers to the driver's internal Trial or Best slot, which is moved or swapped on the next reoptimize call; tuning only progresses if you call reoptimize before (ideally every) call, so do not cache the returned reference.
- Open crash bugs: #14 (2019-04-29) segfault calling a function reoptimized repeatedly with AT_Bayes and an IntRange parameter; #13 segfault when dumping stats; #10 potential double free of an LLVM Module outliving its context. None has a fix or comment.
- Tuning is nondeterministic and not persisted: RandomTuner seeds std::mt19937_64 from system_clock, its first trial is always the default configuration, and exporting or reloading tuned configs is only a TODO.
- Harness and evidence flaws: the slide's Default mean (662,929 ns) is from 5 measurements and the best (445,898 ns) from 129; the slide kernel (T\*\* MatMul that callocs its result inside the timed call) is not the repo's benchmark/matmul.h (flat __restrict__ arrays, DIM 200), and DIM, element type, CPU and build flags are not given; the bars fall monotonically from Default to G, so slower random trials and tuning cost are not shown. In benchmark/matmul.h the only correctness check is assert(verifyCheck(...)) on one element, which the default Release build (NDEBUG) compiles out, so benchmark runs do not verify tuned variants.

## Known shortcomings

- One 2018 slide: the 1.48x is the best of random-search configurations over the project's own untuned 'Default', not a named incumbent; a single matmul kernel; no compiler, flags or CPU; the chart y-axis starts at 400 us. Abandoned 2019.
- Enricher: the slide's Default mean (662,929 ns) is from 5 measurements and the best (445,898 ns) from 129; the slide kernel (T\*\* MatMul that callocs its result inside the timed call) is not the repo's benchmark/matmul.h; DIM, element type, CPU and flags are not given; slower random trials and tuning cost are not shown. The only correctness check, assert(verifyCheck(...)) on one element, is compiled out by the default Release build. Open segfaults #14 and #13, potential double free #10, none answered; tuning is nondeterministic and not persisted; the auto const& returned by reoptimize is invalidated by the next call. Tied to LLVM 8.0.1.

## Caveats and trade-offs

The only numbers are one slide from a July 2018 status talk: a single kernel (matrix multiply), 'Default' baseline not defined on the slide, no compiler, flags, CPU model or matrix size, and the 1.48x is 'up to', i.e. the best of the random-search configurations; the slide does not say whether tuning time and JIT compile cost are included, and its y-axis starts at 400 microseconds, which visually exaggerates the gap. In the current code (include/tuner/RandomTuner.h) the first configuration the random tuner tries is genDefaultConfig, with the codegen optimisation level defaulting to 3 (CodegenOptions.h), so 'Default' is probably the JIT's own untuned pipeline rather than an ahead-of-time clang -O3 build, but the 2018 code behind the slide is not pinned. The README calls the project 'an early-phase experiment in online autotuning' and gives no speedups. The repo has benchmark sources (benchmark/benchmark.cpp with Google Benchmark; CMake builds atjit-benchmark-O0/O1/O2/O3 AOT variants) but no committed results, so a run would be needed to compare against clang -O3 ahead-of-time or Easy::jit. No thesis or paper with numbers was found. Last commit 2019-08-29; CI moved to gitlab.com/kavon1/atJIT.

Needs a source-built LLVM and Clang 8 or newer with RTTI, libdispatch, XGBoost and a clang plugin pass ('atjitc' wrapper); API is a single reoptimize() call that must be called repeatedly so the tuner can measure variants; only suitable for long-running hot kernels because tuning needs many timed runs plus JIT compile time; the Polly loop-transform knobs are deprecated (issue 15).

## Maintenance

Abandoned research prototype (last commit 2019-08-29, 53 stars, no releases, 4 open issues including two segfaults) under BSD-3-Clause, tied to LLVM 8.0.1; copy its knob set and online-tuning policy as a design, not as a dependency.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-06): confirm; tier before verification C, tier now C.
- **Tier reason:** Only numbers are one first-party status-talk slide (doc/slides/ANL_Summer_Status_Update.pdf, slide 11, 23.07.2018): matrix-multiply bar chart with Default about 660 microseconds and best random-search configuration G about 445, captioned 'Up to 1.48x Speedup, aka 32.7% improvement!'; no compiler, flags, CPU, matrix size or committed results, and the baseline is the tool's own untuned configuration.
- **Verifier notes:** Slide 11 rendered and read: chart matches the record (Default about 660 us, G about 445 us, 1.48x). Shortcomings to record: baseline is the tool's own untuned config, not a named incumbent; single kernel; best-of-random-search 'up to' figure; no methodology; truncated y-axis; early experiment, abandoned since 2019.
- **Fields the verifier corrected:** `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** comparison with clang -O3 ahead-of-time on stated hardware
- **Pages the verifier opened:**
  - <https://github.com/kavon/atJIT>
  - <https://github.com/kavon/atJIT/commits>
  - <https://github.com/kavon/atJIT/tree/master/doc>
  - <https://github.com/kavon/atJIT/tree/master/doc/slides>
  - <https://github.com/kavon/atJIT/tree/master/include/tuner>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/doc/slides/ANL_Summer_Status_Update.pdf>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/README.md>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/benchmark/benchmark.cpp>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/include/tuner/RandomTuner.h>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/include/tuner/CodegenOptions.h>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/include/tuner/optimizer.h>
- **Sources the enricher read:**
  - <https://github.com/kavon/atJIT>
  - <https://github.com/kavon/atJIT/issues?q=is%3Aissue>
  - <https://github.com/kavon/atJIT/issues/14>
  - <https://github.com/kavon/atJIT/issues/10>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/README.md>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/TODO.md>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/.gitlab-ci.yml>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/get-llvm.sh>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/benchmark/benchmark.cpp>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/benchmark/matmul.h>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/benchmark/qsort.h>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/include/tuner/driver.h>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/include/tuner/Feedback.h>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/include/tuner/RandomTuner.h>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/include/tuner/CodegenOptions.h>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/include/tuner/optimizer.h>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/include/tuner/LoopKnob.h>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/include/tuner/KnobConfig.h>
  - <https://raw.githubusercontent.com/kavon/atJIT/HEAD/doc/slides/ANL_Summer_Status_Update.pdf>
- **Raw records:** [data/wave12/verified.json](../../../data/wave12/verified.json) (id `https://github.com/kavon/atjit`) · [data/wave12/enrich/raw/github_com_kavon_atjit.json](../../../data/wave12/enrich/raw/github_com_kavon_atjit.json) (enrichment confidence 0.8)

</details>
