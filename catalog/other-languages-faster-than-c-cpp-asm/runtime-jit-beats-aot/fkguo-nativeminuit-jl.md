# NativeMinuit.jl (pure-Julia port of C++ Minuit2)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Runtime JIT beats ahead-of-time](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `LGPL-2.1-or-later` · 🟢 active

> Pure-Julia port of CERN's Minuit2 minimizer (MIGRAD, HESSE, MINOS) whose low-level MIGRAD kernel beats C++ Minuit2 6.24.0 on microsecond toy fits.

| | |
|---|---|
| **Beats** | C++ Minuit2 (ROOT's standalone Minuit2 built through CMake, default Release, C++17) running MIGRAD on the same objectives |
| **Claimed result** | Julia/C++ time ratios 0.147x (quad_4d: 0.81 us vs 5.50 us), 0.253x (rosenbrock_2d: 9.50 vs 37.62 us), 0.371x (rosenbrock_10d: 58.11 vs 156.62 us), 0.718x (gauss_ll_10_1000: 32.26 vs 44.96 us), 0.888x (gauss_ll_2_100: 20.16 vs 22.71 us): about 1.1x to 6.8x faster (derived from page data). README: 'Faster than C++ Minuit2 on every benchmark in the test corpus'. |
| **Workload** | Wall time of one full MIGRAD minimization with Strategy(0) and no parameter limits, including construction of the cost function and its random data, on five objectives: quad_4d (4 parameters from 1.0, step 0.1), rosenbrock_2d (start -1.2, 1.0), rosenbrock_10d, gauss_ll_10_1000 (10 independent Gaussian means, 100 points each) and gauss_ll_2_100 (mu and sigma of a Gaussian NLL over 100 points). Medians of 50 samples per side. |
| **Metric** | latency |
| **Hardware** | Apple M3 |
| **Compiler and flags** | Julia 1.12 (default -O2) with OpenBLAS 0.3.29 and BLAS threads set to 1 (benchmark/perf-config.toml); Julia times are BenchmarkTools medians of 50 samples (evals policy auto). C++: benchmark/cpp/CMakeLists.txt sets C++17 and CMAKE_BUILD_TYPE Release by default (CMake's Release flags for Clang and GCC are -O3 -DNDEBUG). It builds C++ Minuit2 from reference/Minuit2_cpp, a gitignored checkout that docs/UPSTREAM.md pins to GooFit/Minuit2 commit 57dc936a2b74d0b4dda1254c3dd63e7c61a97c84 (tag 6.24.0). C++ times are medians of 50 single-shot std::chrono samples. The C++ compiler is not named. Minuit2's CMakeLists has no BLAS dependency (it has its own small linear algebra), so 'single-threaded BLAS on both sides' only affects the Julia side. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | Stated by the README: a parametric CostFunction{F} devirtualizes the FCN call site at compile time, whereas C++ Minuit2 pays for shared_ptr ref-counting and ABObj expression-template dispatch. |
| **Adoption** | 14 stars; registered in the Julia General registry |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/fkguo/NativeMinuit.jl) · [benchmark](https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/README.md) |

## Verdict

First-party README table on an Apple M3 with Julia 1.12: one full MIGRAD at Strategy(0) through the low-level Julia migrad kernel took 0.81, 9.50, 58.11, 32.26 and 20.16 μs vs C++ Minuit2 6.24.0 MnMigrad (CMake Release, compiler unnamed) 5.50, 37.62, 156.62, 44.96 and 22.71 μs on quad_4d, rosenbrock_2d, rosenbrock_10d, gauss_ll_10_1000 and gauss_ll_2_100, about 1.1x to 6.8x faster (derived from page data); the timed regions include FCN construction and, on the gauss_ll rows, random data generation with different generators.

## Use it when

- Julia code that fits χ² or likelihood models with Minuit semantics and wants MINOS errors and contours without a Python or ROOT dependency.
- Many small fits (2 to 10 parameters, cheap FCN) in a loop, such as toy Monte Carlo studies, where per-fit optimizer overhead matters.
- Fits whose FCN is generic Julia code, so ForwardDiff gradients (README: 1.6x faster migrad+HESSE than iminuit on a 3-parameter X(3872) fit) or the threaded gradient can be used.
- Replacing IMinuit.jl (PyCall into iminuit) in existing Julia scripts, since Fit/ArrayFit/chisq/Data are exported aliases.

## Skip it when

- C++ or Python callers: it needs the Julia runtime and is not callable as a C++ library; use Minuit2 or iminuit directly.
- Expecting the README's 0.15x to 0.89x ratios from the iminuit-style front end: the table times the low-level migrad(cf, x0, errs) kernel, while CHANGELOG 0.7.1 puts a warm 4-parameter quadratic fit through migrad! at about 11 μs (13 or 51 μs before that fix), against 5.50 μs for C++ MnMigrad in the same README table (different runs; strategy and machine of the 11 μs figure not stated).
- Expensive FCNs (milliseconds or more per call): the optimizer overhead it saves is negligible and call counts match C++ Minuit2 to about 1.6%.
- Proprietary code that cannot accept LGPL-2.1-or-later obligations (it is a derivative work of Minuit2).
- Short-lived processes: first-call JIT compilation is not part of the measured numbers, and CHANGELOG 0.7.1 documents a 4x build-to-build swing in warm fit time on Julia 1.12 precompile images before the fix.

## How it is fast

CostFunction{F,T} is parametric on the user function's type, so Julia compiles a specialised MIGRAD loop with the FCN call inlined, while the C++ benchmark's FCN is called through the virtual FCNBase::operator() on a std::vector&lt;double&gt;; the README also blames Minuit2's shared_ptr ref-counting and ABObj expression-template dispatch. The kernels work on preallocated buffers (the CHANGELOG reports the per-FCN kernels verified allocation-free), so on 2 to 10 parameter fits costing nanoseconds per call the optimizer's own overhead, which is what differs, dominates the wall time. On expensive FCNs the advantage vanishes: the README's 57-parameter fit needs 7562 vs 7446 calls, so wall time is set by the shared FCN.

## Compared with alternatives

No other minimizer is catalogued in this category; the Julia siblings (NonuniformFFTs.jl, Ripserer.jl, EvoTrees.jl, SymbolicUtils.jl) solve unrelated problems. Pick NativeMinuit when the job is Minuit-style fitting with MINOS errors inside Julia; for fits driven from C++ or Python, C++ Minuit2 or iminuit remain the direct choice.

## Integration

| | |
|---|---|
| **Form** | module (Julia package in the General registry, Pkg.add("NativeMinuit")) |
| **Dependencies** | LinearAlgebra, Logging, PrecompileTools, Printf, Random, RecipesBase, Statistics; optional package extensions for ForwardDiff, Optim, AdvancedHMC (with LogDensityProblems, LogDensityProblemsAD, TransformVariables), Plots, DataFrames and Clustering |
| **Minimum toolchain** | Julia 1.11 (Project.toml compat); benchmarks and the 0.7.x fixes target Julia 1.12 |
| **Platforms** | any platform Julia supports (pure Julia, no compiled dependencies); published numbers are from an Apple M3 |
| **Thread safety** | NativeMinuit's own buffers are per-thread; threaded_gradient=true requires a thread-safe user FCN and checks it on first call (ThreadSafetyError); CostFunction's nfcn counters are non-atomic Refs, so one CostFunction must not be called from several threads outside the library's threaded-gradient path |
| **Drop-in for the baseline** | partial — drop-in for IMinuit.jl and close to iminuit's API; not a replacement for C++ Minuit2 callers |

## Gotchas

- Harness flaw: both benchmark drivers generate the gauss_ll random data inside the timed region with different generators (C++ std::mt19937_64 seeded per run plus std::normal_distribution; Julia randn on the global RNG). Measured in this session on a 2.1 GHz Xeon with g++ 13.3 -O3 and libstdc++, the C++ GaussNLLNDim(10,1000) constructor alone takes 13.2 μs median and GaussNLL(100) 1.9 μs, the same order as the README gaps (44.96 - 32.26 = 12.7 μs and 22.71 - 20.16 = 2.55 μs), so the two gauss_ll rows may mostly time random-number generation, not MIGRAD; the M3/libc++ cost was not measured.
- The Julia numbers do not come from BenchmarkTools: scripts/run_perf.jl times a hand loop with time_ns, averaging 1000 back-to-back calls per sample when a probe call takes under 1 μs (quad_4d) and 10 calls up to 1 ms, after 10 discarded probe calls that absorb JIT compilation; the C++ side takes 50 single-shot std::chrono samples. The [blas] num_threads = 1 setting in perf-config.toml is never read by run_perf.jl, so 'single-threaded BLAS on both sides' is not enforced by the runner (C++ Minuit2 uses no BLAS).
- The C++ timed region also builds MnUserParameters with std::string names per run, while the Julia region builds only a CostFunction; nfcn per fit is printed by the C++ driver but not recorded on the Julia side, so equal work per fit is shown only by the CHANGELOG's oracle-parity claims (Quad-4D fval to 1e-15; Rosenbrock within Strategy(0) cross-implementation variance).
- The comparison is pinned to Minuit2 6.24.0 (2021) in docs/UPSTREAM.md and the table matches the 2026-05-25 0.1.0-alpha gate (max ratio 0.887x, mean 0.47x); no rerun for 0.7.x or against current ROOT Minuit2 is published.

## Known shortcomings

- Win is Minuit2 6.24.0 library overhead (a new std::vector per FCN call, virtual FCN), not the language; C++ compiler unnamed; gauss_ll datasets differ between sides; nfcn parity not shown; numbers from the May 2026 0.1.0-alpha gate; C++ upstream pinned in docs/UPSTREAM.md (GooFit/Minuit2 commit 57dc936).
- Harness flaw: the gauss_ll timed regions include random data generation with different generators on each side; a g++ 13.3 -O3 microbenchmark here (Xeon, libstdc++) puts the C++ GaussNLLNDim(10,1000) constructor alone at 13.2 us and GaussNLL(100) at 1.9 us against README gaps of 12.7 and 2.55 us, so those rows may mostly time the RNG (M3/libc++ cost unmeasured). The table times the low-level migrad kernel; CHANGELOG 0.7.1 puts the warm user-facing migrad! on the 4-parameter quadratic at about 11 us against C++ 5.50 us (different runs). The Julia runner is a time_ns loop, not BenchmarkTools (1000 or 10 evaluations per sample), and the perf-config [blas] num_threads=1 is never read by run_perf.jl.

## Caveats and trade-offs

First-party numbers from the port's author, on microsecond toy objectives of 2 to 10 parameters where per-call overhead dominates. The table appears to date from the 0.1.0-alpha Phase 0 gate: the CHANGELOG entry of 2026-05-25 reports 'max ratio 0.887x, mean 0.47x', which matches the README rows, and the repo shows no rerun for the current 0.7.x code. The C++ side is Minuit2 6.24.0 (2021), pinned in docs/UPSTREAM.md, built from a gitignored checkout; newer ROOT Minuit2 releases were not compared. The C++ compiler is not named, though CMake's Release default is -O3 -DNDEBUG. The timed regions differ in setup: C++ builds MnUserParameters with std::string names per run, and Julia builds a CostFunction. The gauss_ll rows use different random datasets (Julia's global-RNG randn, which advances with every sample, vs a C++ mt19937_64 reseeded per run). The CHANGELOG says Rosenbrock results agree only 'within Strategy(0) cross-impl variance', and the README does not show the nfcn per fit, so equal work per fit is not demonstrated. CHANGELOG 0.7.1 records a 4x build-to-build swing in warm fit time across Julia 1.12 precompile images (13 vs 51 us on the migrad! path, since fixed), so microsecond Julia timings are fragile. The README says AI coding agents helped write the port and its documentation. [retier] The gauss_ll timed regions include random data generation with different generators on each side; a g++ 13.3 -O3 microbenchmark on a Xeon puts the C++ GaussNLLNDim(10,1000) constructor alone at 13.2 us and GaussNLL(100) at 1.9 us against README gaps of 12.7 and 2.55 us, so those rows may mostly time the RNG. The table times the low-level migrad kernel; CHANGELOG 0.7.1 puts the warm user-facing migrad! on the 4-parameter quadratic at about 11 us against C++ 5.50 us (different runs). The Julia runner is a time_ns loop, not BenchmarkTools, and the perf-config [blas] num_threads=1 is never read by run_perf.jl.

Needs the Julia runtime and JIT warm-up (the README table does not say whether compile time is excluded); a derivative work of Minuit2, so LGPL applies; not a drop-in for C++ callers.

## Maintenance

Actively developed (v0.7.4 in the CHANGELOG dated 2026-10-08, 310 commits, all 7 filed issues closed, 4,400+ tests per the README) and LGPL-2.1-or-later; usable as a Julia dependency today, with the caveat that the speed claim covers the low-level kernel on tiny fits and the README notes AI coding agents helped draft the port.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table from the port's own public harness (benchmark/bench_migrad_suite.jl, benchmark/cpp/cpp_bench.cxx, benchmark/compare_cpp.jl), with the CPU (Apple M3) and Julia 1.12 stated and the C++ upstream pinned in docs/UPSTREAM.md (GooFit/Minuit2 6.24.0, commit 57dc936). The C++ compiler is not named, and the flags are only implied by CMake's Release default, so it is not A; there is no independent run.
- **Verifier notes:** Confirm at C. The README numbers match exactly (1.1x to 6.8x derived), and the metadata checks out: LGPL-2.1-or-later, 14 stars, 310 commits, last commit 2026-10-08 (active), registered in the Julia General registry. Correction: the C++ Minuit2 version is pinned (docs/UPSTREAM.md: GooFit/Minuit2 6.24.0, commit 57dc936), not unspecified. Shortcomings to record: the win is library overhead (Minuit2's per-FCN-call std::vector allocation and virtual FCN against a specialised Julia call site) on microsecond toy fits, not the language; C++ compiler unnamed; different random datasets on the gauss_ll rows; nfcn parity not shown; numbers from the May 2026 0.1.0-alpha gate against a 2021 upstream.
- **Fields the verifier corrected:** `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-58 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/README.md>
  - <https://github.com/fkguo/NativeMinuit.jl>
  - <https://github.com/fkguo/NativeMinuit.jl/commits/main>
  - <https://github.com/fkguo/NativeMinuit.jl/tree/main/benchmark>
  - <https://github.com/fkguo/NativeMinuit.jl/tree/main/src>
  - <https://github.com/fkguo/NativeMinuit.jl/tree/main/artifacts/runs>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/benchmark/compare_cpp.jl>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/benchmark/bench_migrad_suite.jl>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/benchmark/perf-config.toml>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/benchmark/cpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/benchmark/cpp/cpp_bench.cxx>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/scripts/run_gate.sh>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/src/migrad.jl>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/src/fcn.jl>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/docs/UPSTREAM.md>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/.gitignore>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/BenchmarkExamples/RESULTS.md>
  - <https://raw.githubusercontent.com/GooFit/Minuit2/57dc936a2b74d0b4dda1254c3dd63e7c61a97c84/src/MnFcn.cxx>
  - <https://raw.githubusercontent.com/GooFit/Minuit2/57dc936a2b74d0b4dda1254c3dd63e7c61a97c84/src/MnUserFcn.cxx>
  - <https://raw.githubusercontent.com/GooFit/Minuit2/57dc936a2b74d0b4dda1254c3dd63e7c61a97c84/CMakeLists.txt>
- **Sources the enricher read:**
  - <https://github.com/fkguo/NativeMinuit.jl>
  - <https://github.com/fkguo/NativeMinuit.jl/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/README.md>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/CHANGELOG.md>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/Project.toml>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/LICENSE>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/docs/UPSTREAM.md>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/benchmark/compare_cpp.jl>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/benchmark/bench_migrad_suite.jl>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/benchmark/perf-config.toml>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/benchmark/cpp/CMakeLists.txt>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/benchmark/cpp/cpp_bench.cxx>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/scripts/run_gate.sh>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/scripts/run_perf.jl>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/src/fcn.jl>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/src/migrad.jl>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/src/NativeMinuit.jl>
  - <https://raw.githubusercontent.com/fkguo/NativeMinuit.jl/main/BenchmarkExamples/RESULTS.md>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/fkguo/nativeminuit.jl`) · [data/wave14/enrich/raw/github_com_fkguo_nativeminuit_jl.json](../../../data/wave14/enrich/raw/github_com_fkguo_nativeminuit_jl.json) (enrichment confidence 0.7)

</details>
