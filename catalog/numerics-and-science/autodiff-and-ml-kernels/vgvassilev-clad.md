# Clad (Clang-plugin source-transformation AD)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++` · `LGPL-3.0` · 🟢 active

> Clang-plugin source-transformation AD for C++ generating derivative source code; no published timing against other AD tools.

| | |
|---|---|
| **Beats** | Enzyme (LLVM-level AD, run through Clad's own use_enzyme backend); Tapenade planned; none of the listed baselines (oneDNN, cuDNN, XNNPACK, Eigen tensor) apply |
| **Claimed result** | No numbers found: neither the README, the docs (CoreConcepts, FAQ, UsingEnzymeWithinClad, ReleaseNotes) nor the opened repo pages state any speedup or timing versus Adept, CppAD, CoDiPack or Enzyme. |
| **Workload** | Google Benchmark micro-benchmarks in the repo comparing Clad-generated reverse-mode and vector-forward-mode gradients with Enzyme-generated gradients of small functions (array add and multiply, sum), plus Hessian, matrix, tape, multithreading, GPT-2 training (cladtorch) and LULESH and XSBench (CUDA) benchmarks. No results are published. |
| **Metric** | throughput |
| **Compiler and flags** | Benchmarks target is built in release mode; GPT2Training is built with -O3 -ffast-math (from benchmark/CMakeLists.txt); no results to attach flags to. |
| **Adoption** | 421 stars, 212 forks; reported (search results) as used in ROOT/RooFit at CERN |
| **Last commit** | 2026-09-30 |
| **Links** | [repository](https://github.com/vgvassilev/clad) |

## Verdict

Nothing measured: the repo's benchmark/ directory contains Google Benchmark comparisons of Clad against its own Enzyme backend, Tapenade (memory), vector forward mode, Hessians and a GPT-2 training run (built -O3 -ffast-math), but no committed results, hardware or compiler versions. The only numbers seen are snippet-level reports of RooFit gradients (5.5x faster minimization at about 1,000 parameters) versus finite differences, which is not another AD tool.

## Use it when

- Gradients of self-contained numeric C++ kernels (likelihoods, cost functions, physics formulas) with many inputs and one output, where you control the source and compile with upstream Clang 14-23
- When you want to read, debug or ship the derivative as source code (dump(), -fgenerate-source-file) instead of a runtime tape
- ROOT/RooFit users: Clad is the AD engine behind RooFit's code-generation path; the ACAT 2022 paper and ROOT blog report a 5.5x faster minimization for about 1,000 parameters versus numerical gradients (search-result snippets, pages blocked here)
- Interactive work in Jupyter through xeus-cpp/clang-repl (conda-forge packages)
- Floating-point error estimation of a function, which operator-overloading AD libraries do not offer

## Skip it when

- If you need evidence that it beats another AD tool: the repo ships Google Benchmark sources (Enzyme, Tapenade memory, vector mode, Hessians, GPT-2) but publishes no results
- Code that calls functions defined in other translation units or binary-only libraries, uses virtual methods (unsupported per issue 2176), exceptions, goto or reference data members
- GCC, MSVC or Apple Clang builds: the plugin only loads into the exact upstream Clang it was built against
- OpenMP-parallel reverse sweeps: open issue 2114 reports a race that gives a different wrong gradient on each multithreaded run
- Teams that cannot absorb an evolving tool: 144 open issues, several of them wrong-derivative reports opened in September 2026

## How it is fast

Source transformation: the derivative is plain C++ that the compiler optimizes together with the primal, so there is no operator-overloading or tape-interpretation overhead at run time. In reverse mode a to-be-recorded (TBR) analysis decides which overwritten values must be pushed on a clad::tape, so statements like y = y + x\*i store nothing, and activity analysis skips inactive variables. Release 2.5 recomputes counted-loop trip counts in the reverse sweep and accumulates broadcast-read adjoints in registers; 2.3 added a tape that can offload to disk.

## Compared with alternatives

Pick Clad over CoDiPack, XAD or Adept 2 when your code is self-contained C++ compiled with upstream Clang and you want compiler-optimized derivative source without an active type; pick the operator-overloading tools for code spread across libraries, virtual dispatch or GCC/MSVC builds. Pick Enzyme instead when you need multi-language or LLVM-IR-level AD with published speedups (Enzyme reports 4.5x over AD on unoptimized IR); Clad's own Enzyme backend exists mainly for cross-validation.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | LLVM/Clang 14.0.x-23.2.x development libraries (plugin clad.so plus the clad/Differentiator headers); optional Enzyme backend built via -DCLAD_ENABLE_ENZYME_BACKEND; conda-forge package available |
| **Minimum toolchain** | Upstream Clang 14 to 23 (same version Clad was built against); README says Clad needs C++14 features and its examples compile with -std=c++17 |
| **Platforms** | Linux and macOS with upstream LLVM (Apple Clang disables plugins); Windows via WSL2 per README; CUDA device code partly supported (issue 2172) |
| **Thread safety** | not documented; generated derivatives are ordinary functions whose tapes are local variables, but OpenMP-parallel reverse mode has open race and crash issues (2114, 1852) |
| **Drop-in for the baseline** | no |

## Gotchas

- If Clad cannot differentiate a function it silently falls back to numerical (finite-difference) differentiation; compile with -DCLAD_NO_NUM_DIFF to make that an error
- Integer and char variables are differentiated like reals and lossy casts are not warned about, which the README says can give incorrect derivatives
- Open wrong-derivative bugs without diagnostics: reference data members double the gradient (issue 2082), forward mode drops output-parameter tangents (2075), reverse mode drops pointer casts (2099)
- The caller must allocate and zero gradient and Hessian storage; stale values are accumulated into

## Known shortcomings

- No numbers against an AD baseline; kept because ROOT uses it. ACAT 2022 snippets show 5.5-29x only versus finite differences.
- Open wrong-derivative bugs with no diagnostic: #2082 reference members give a 2x gradient, #2075 forward mode drops output tangents, #2099 reverse mode drops pointer casts; #2114 OpenMP reverse race gives a different wrong gradient each run. Silently falls back to finite differences unless -DCLAD_NO_NUM_DIFF. No virtual methods. No published performance results.

## Caveats and trade-offs

Evidence-free record: the repo ships benchmark code (benchmark/EnzymeCladComparison.cpp, built only with CLAD_ENABLE_ENZYME_BACKEND, plus Hessians.cpp, VectorModeComparison.cpp, GPT2Training.cpp built with -O3 -ffast-math, LULESH_diff.patch, XSBench_diff.patch, benchmark_compare.py) but no committed results; the Clad-vs-Enzyme benchmark compares two backends of Clad itself. Issue #1764 and PR #1771 (benchmark::DoNotOptimize fix for 0 ns results) are cited from the search record and were not re-opened. The ACAT 2022 paper 'Automatic Differentiation of Binned Likelihoods With RooFit and Clad' (arXiv 2304.02650) and the ROOT blog 'Automatic differentiation in RooFit with Clad' report, per search-result snippets only (arXiv, root.cern and indico.cern.ch blocked), TFormula gradient speedups of about 10x to 29x and a HistFactory minimization speedup of about 5.5x versus ROOT 6.26's numerical (finite-difference) gradients; that baseline is numerical differentiation, not another AD tool or a listed baseline, and the gain comes from reverse mode needing one sweep instead of n function calls. Tier D kept although the repo has fewer than 1k stars because Clad is the AD engine integrated in ROOT/RooFit at CERN.

Compiler plugin: needs a matching Clang/LLVM (14.0.x to 23.2.x per README), differentiates only code visible to Clang at compile time (custom derivatives needed for external functions), and supports a growing but incomplete set of C++ features. Source transformation can expose optimizations to the compiler, but reverse mode stores intermediates on a tape (memory grows with operation count). LGPL-3.0.

## Maintenance

Very active (release 2.5 on 28 September 2026, last commit 2026-09-30, 2,128 commits) and LGPL-3.0, but correctness bugs are still being filed at a steady rate, so validate derivatives against finite differences before relying on them.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification D, tier now D.
- **Tier reason:** README and repo publish no timing; benchmark/ holds Google Benchmark sources (EnzymeCladComparison.cpp, Hessians.cpp, VectorModeComparison.cpp, GPT2Training.cpp, LULESH/XSBench patches) but no committed results. Kept (not rejected) because Clad is widely referenced as ROOT/RooFit's AD engine.
- **Verifier notes:** Metadata confirmed: LGPL-3.0 (License.txt), 421 stars, 212 forks, last commit 2026-09-30. If the orchestrator counts finite-difference gradients as a baseline, the ACAT 2022 paper could support B once opened; nothing against Adept, CppAD, CoDiPack or Enzyme has numbers.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/vgvassilev/clad>
  - <https://github.com/vgvassilev/clad/tree/master/benchmark>
  - <https://github.com/vgvassilev/clad/commits>
  - <https://raw.githubusercontent.com/vgvassilev/clad/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/vgvassilev/clad/HEAD/License.txt>
- **Sources the enricher read:**
  - <https://github.com/vgvassilev/clad>
  - <https://raw.githubusercontent.com/vgvassilev/clad/HEAD/README.md>
  - <https://raw.githubusercontent.com/vgvassilev/clad/HEAD/benchmark/CMakeLists.txt>
  - <https://raw.githubusercontent.com/vgvassilev/clad/HEAD/benchmark/EnzymeCladComparison.cpp>
  - <https://raw.githubusercontent.com/vgvassilev/clad/HEAD/docs/userDocs/source/user/FAQ.rst>
  - <https://raw.githubusercontent.com/vgvassilev/clad/HEAD/docs/userDocs/source/user/CoreConcepts.rst>
  - <https://raw.githubusercontent.com/vgvassilev/clad/HEAD/docs/userDocs/source/user/UsingEnzymeWithinClad.rst>
  - <https://github.com/vgvassilev/clad/issues>
  - <https://github.com/vgvassilev/clad/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
  - <https://github.com/vgvassilev/clad/issues/2082>
  - <https://github.com/vgvassilev/clad/issues/2114>
  - <https://github.com/vgvassilev/clad/issues/2176>
  - <https://github.com/vgvassilev/clad/releases>
  - WebSearch: RooFit Clad automatic differentiation speedup (snippets of arxiv.org/pdf/2304.02650 and root.cern/blog/roofit-ad; pages not opened)
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/vgvassilev/clad`) · [data/wave8/enrich/raw/github_com_vgvassilev_clad.json](../../../data/wave8/enrich/raw/github_com_vgvassilev_clad.json) (enrichment confidence 0.7)

</details>
