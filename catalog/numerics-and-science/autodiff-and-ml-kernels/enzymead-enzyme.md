# Enzyme

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Autodiff and ML kernels](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0 WITH LLVM-exception` · 🟢 active

> LLVM/MLIR compiler plugin that generates gradients of optimized IR; matched or beat Tapenade and Adept in its NeurIPS 2020 study.

| | |
|---|---|
| **Beats** | Adept and Tapenade (and AD on unoptimized IR) |
| **Claimed result** | geometric mean 4.5x speedup over AD on IR before optimization; outperforms Tapenade and Adept across tested benchmarks (no per-test ratio read) |
| **Workload** | LLVM-level reverse-mode AD on ADBench (BA, LSTM, GMM) and integrator/FFT/Brusselator tests. |
| **Metric** | throughput |
| **Hardware** | AWS c4.8xlarge, hyperthreading and Turbo Boost disabled |
| **Adoption** | 1.7k stars |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/EnzymeAD/Enzyme) · [benchmark](https://arxiv.org/abs/2010.01709) |

## Verdict

The NeurIPS 2020 paper measures reverse-mode AD on ADBench (BA, LSTM, GMM) plus Euler/RK4 integrators, FFT and a 2D Brusselator on an AWS c4.8xlarge with hyperthreading and Turbo Boost disabled, taking geometric means over inputs: differentiating after optimization gives a 4.5x geomean speedup over differentiating unoptimized IR, and results vs Tapenade and Adept are given per benchmark only. LLVM version and flags are not stated in the evaluation, and the paper does not say where the benchmark code lives.

## Use it when

- You need reverse-mode gradients of an existing C/C++/Fortran/Rust numerical kernel (simulations, integrators, bundle adjustment, LSTMs) without rewriting it in an AD type.
- Loop-heavy code where compiler optimizations shrink the primal before differentiation (the paper reports a 4.5x geomean gain from optimizing first).
- Mixed-language or GPU/parallel code: the authors' later SC'21/SC'22 papers add CUDA/ROCm kernels, OpenMP, MPI and Julia tasks.
- You already build with Clang/LLVM 15+ and can add a compiler plugin to the build.

## Skip it when

- Code that relies on C++ exceptions, runtime-loaded or self-modifying code, or shared libraries without IR: the paper requires IR for every differentiated function and exceptions disabled.
- Code with type punning (unions of differing types, copies of undefined memory) that defeats type analysis; you get errors or must use loose-type flags.
- Toolchains that are not LLVM-based (MSVC, stock GCC) or builds where loading an LLVM plugin is impractical.
- Quick prototyping where a header-only operator-overloading library (XAD, FastAD, Adept) is easier to set up and debug.
- When you need per-benchmark proof that it beats Tapenade: the paper attributes GMM and Bruss differences to tape structure and does not give a uniform win ratio.

## How it is fast

It differentiates after the normal LLVM optimization pipeline has run, so loop-invariant code motion, inlining and dead-code elimination have already simplified the primal; the paper's norm example drops from O(N^2) to O(N) gradient work this way. Interprocedural type analysis (seeded from TBAA metadata) and activity analysis skip adjoints for values that cannot affect the output. Shadow memory mirrors active allocations, and cache minimization stores only the forward values the reverse pass needs. Being source-transformation AD, it avoids the runtime tape that operator-overloading tools such as Adept record.

## Compared with alternatives

Pick Enzyme over XAD or FastAD when you cannot or will not rewrite code into an active scalar type, when the code spans languages or runs on GPU, or when compiler optimization of the primal matters; pick XAD or FastAD for a header-only C++ library with no compiler-plugin build step.

## Integration

| | |
|---|---|
| **Form** | shared lib (LLVM pass plugin: LLVMEnzyme-&lt;ver&gt;.so, ClangEnzyme-&lt;ver&gt;.so, LLDEnzyme-&lt;ver&gt;.so) |
| **Dependencies** | LLVM 15+ built with plugin support (CMake aborts below 15); CMake 3.13+; Ninja or Make. Packages on Homebrew, Spack and Nix. |
| **Minimum toolchain** | C++17 to build the plugin; Clang/LLVM 15 or newer (CI matrix tests LLVM 15 and 16) |
| **Platforms** | Linux and macOS in CI; any target LLVM supports in principle; GPU (CUDA/ROCm) per the SC'21 paper |
| **Thread safety** | not documented for the generated code; parallel AD (OpenMP, MPI, Julia tasks) is covered by the SC'22 paper |
| **Drop-in for the baseline** | partial — replaces Adept/Tapenade as the AD engine but uses a different API (__enzyme_autodiff calls plus argument annotations) and a compiler-plugin build step |

## Gotchas

- ClangEnzyme works on one translation unit only; if the differentiated function calls code in other files you need LLDEnzyme with LTO.
- Requires TBAA metadata and statically deducible types for active memory; enzyme-loose-types and enzyme-emptyfn-inactive exist to paper over ambiguous cases, at your own risk.
- The docs warn that LLVM's plugin infrastructure can be flaky or not built by default, and recommend building LLVM from source when loading segfaults.
- Indirect calls into code Enzyme cannot analyze need user-supplied custom gradients.

## Known shortcomings

- The 4.5x is Enzyme vs its own AD on unoptimized code; vs Tapenade and Adept only per-benchmark results, no overall ratio; no compiler flags or benchmark code location stated.
- 'Outperforms Tapenade and Adept across tested benchmarks' overstates the paper (GMM/Bruss differences attributed to tape structure; \~0.8x Tapenade on GMM per Fig. 9 summary, unchecked); plugin needs LLVM 15+ while docs say 11-16; exceptions must be off and every differentiated function needs its IR.

## Caveats and trade-offs

NeurIPS 2020 paper; compiler versions/flags not stated and benchmark code location not given in the paper. The headline 4.5x is Enzyme vs its own AD on unoptimized IR; vs Tapenade and Adept the paper gives per-benchmark results only, no single ratio. Baselines are AD tools, not ML kernels. License: Apache-2.0 with LLVM Exceptions (LICENSE file).

Compiler plugin on statically analyzable LLVM/MLIR; works across C/C++/Rust/Julia/Fortran.

## Maintenance

Actively developed (1.7k stars, about 209 open issues) under Apache-2.0 with LLVM exceptions; usable today through Homebrew/Spack/Nix packages or a source build against LLVM 15+, with Julia, Rust and Fortran front ends.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed NeurIPS 2020 paper (arXiv 2010.01709) reports a 4.5x geometric-mean speedup of AD on optimized IR over AD before optimization and benchmark-by-benchmark comparisons against Tapenade and Adept on a quiesced AWS c4.8xlarge; no compiler flags or public benchmark code path stated, so not A.
- **Verifier notes:** License identified from the LICENSE file (Apache v2.0 with LLVM Exceptions), so usability moves to copyable. GitHub commits page is blocked by robots.txt, so last_commit (2026-10-01) could not be checked and is left as is.
- **Fields the verifier corrected:** `license`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2010.01709>
  - <https://arxiv.org/html/2010.01709>
  - <https://github.com/EnzymeAD/Enzyme>
  - <https://raw.githubusercontent.com/EnzymeAD/Enzyme/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/EnzymeAD/Enzyme/HEAD/Readme.md>
  - <https://raw.githubusercontent.com/EnzymeAD/Enzyme/HEAD/enzyme/CMakeLists.txt>
  - <https://raw.githubusercontent.com/EnzymeAD/Enzyme/HEAD/.github/workflows/enzyme-ci.yml>
  - <https://github.com/EnzymeAD/Enzyme>
  - <https://enzyme.mit.edu/Installation/>
  - <https://enzyme.mit.edu/getting_started/UsingEnzyme/>
  - <https://arxiv.org/html/2010.01709>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/enzymead/enzyme`) · [data/wave8/enrich/raw/github_com_enzymead_enzyme.json](../../../data/wave8/enrich/raw/github_com_enzymead_enzyme.json) (enrichment confidence 0.7)

</details>
