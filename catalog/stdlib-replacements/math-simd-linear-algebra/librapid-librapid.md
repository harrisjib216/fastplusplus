# LibRapid

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟡 stale

> Templated C++20/23 array/tensor library with SIMD, OpenMP, CUDA and OpenCL backends; beats naive std::vector loops on elementwise math.

| | |
|---|---|
| **Beats** | std::vector (nested-loop elementwise array/matrix operations) |
| **Claimed result** | Page reports 'Speedup: 558.71%' for res = aa \* bb - cc on 1000x1000 double arrays: STL (nested std::vector&lt;std::vector&lt;double&gt;&gt; loops) 1.589ms vs LibRapid Array 284.405us per iteration. The 558.71% figure is the time ratio, \~5.59x, not '558.71% faster' (derived from page data). The post's summary says 'a speedup of over 500%'. |
| **Workload** | Elementwise matrix expression res = aa \* bb - cc on 1000x1000 double matrices, run repeatedly (\~15,000 iterations) and timed |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 3950X, Windows 10 Pro |
| **Compiler and flags** | MSVC 19.33, default project settings; LibRapid 'Optimise Small Arrays' option OFF |
| **Adoption** | 179 stars |
| **Last commit** | 2025-08-21 |
| **Links** | [repository](https://github.com/LibRapid/librapid) · [benchmark](https://dev.to/librapid/writing-faster-shorter-code-with-librapid-38lf) |

## Verdict

First-party dev.to benchmark: elementwise res = aa\*bb-cc on 1000x1000 double arrays, run repeatedly (\~15,000 iterations), averaged 1.589ms/iteration for naive nested std::vector&lt;std::vector&lt;double&gt;&gt; loops vs 284.405us/iteration for LibRapid's Array, a \~5.59x ratio (the page's '558.71%' is that ratio expressed as a percentage, not '558.71% faster'). Measured on MSVC 19.33 with default project settings, AMD Ryzen 9 3950X, Windows 10 Pro, with LibRapid's 'Optimise Small Arrays' option off.

## Use it when

- Elementwise or linear-algebra-heavy numeric code currently written as nested std::vector loops, on x86-64 with AVX/SSE
- Willing to standardize on one array/tensor type across CPU, CUDA and OpenCL backends via a template parameter instead of separate GPU code paths
- C++20/23 toolchain available and OK pulling in a CMake build with several optional native dependencies (fmt, Vc, CLBlast, pocketfft, OpenBLAS, MPIR/MPFR, FFTW)
- Want BLAS-backed GEMM, FFT, complex/multiprecision arithmetic and NN activation functions from one library instead of assembling Eigen + FFTW + Boost.Multiprecision
- Prototyping or research code where a small, actively-evolving (though currently stalled) single-maintainer library is an acceptable risk

## Skip it when

- Need a drop-in replacement for std::vector/std::valarray: requires rewriting to lrc::Array&lt;T&gt; and its own Shape/indexing API, not a header swap
- Need OpenCL on Apple Silicon: issue #245 (open since 2023) tracks OpenCL support on macOS Mx as unresolved
- Rely on array slicing or generic array views: slicing (#139) and OpenCL GeneralArrayView (#253) are both open and labeled 'Requires Rewrite' since 2023
- Need automatic differentiation or trig functions to be bug-free: open issues from Aug 2025 report bugs in the AD product-rule implementation (#273) and in trig functions (#270), filed the week before the project's last commit
- Need active maintenance: solo student-maintainer project, last commit 2025-08-21, 15 open issues including 4 unresolved bugs filed just before that final commit

## How it is fast

Elementwise expressions like aa \* bb - cc are built as an expression tree and evaluated in one fused pass instead of allocating a temporary per operator, then dispatched to SIMD kernels (via the bundled Vc library) and OpenMP threads, or offloaded to CUDA/OpenCL/BLAS backends chosen with a template parameter. Linear-algebra expressions get compile-time rewriting into a single BLAS-style call, e.g. dot(3\*a, 2\*transpose(b)) becomes one GEMM with alpha/beta/transpose flags folded in. The one verified benchmark compares this fused, vectorized path against naive triple-nested std::vector&lt;std::vector&lt;double&gt;&gt; loops, which allocate a temporary per operator and get no fusion.

## Compared with alternatives

Pick LibRapid over the sibling scalar-math libraries (SLEEF, VDT, fmath, trigno_simd_cpp, FABE13-HX, fast_math_cpp) when the need is a whole array/tensor container with fused elementwise expressions and optional GPU backends, not a faster std::sin/exp/log drop-in; pick Axiom instead if the goal is specifically an Eigen-compatible elementwise-math replacement, since Axiom benchmarks against Eigen3's array ops rather than raw std::vector loops.

## Integration

| | |
|---|---|
| **Form** | source-drop, CMake build (not header-only — CMakeLists globs .hpp under librapid/include plus .cpp/.cxx under librapid/src and cxxblas into a compiled target) |
| **Dependencies** | bundled submodules: fmt, Vc (SIMD), pocketfft, scnlib, CLBlast, Jitify; optional external: OpenMP, CUDA, OpenCL, OpenBLAS, MPIR, MPFR, FFTW, toggled via CMake options |
| **Minimum toolchain** | C++20 minimum (CMake enforces this with a FATAL_ERROR check), C++23 used by default when built standalone; CMake &gt;= 3.16 |
| **Platforms** | x86-64 primary target (bundles Vc SIMD, LIBRAPID_NATIVE_ARCH on by default); Linux/macOS/Windows for CPU backend; CUDA and OpenCL backends optional and platform-gated, with OpenCL on Apple Silicon macOS unresolved (issue #245) |
| **Thread safety** | not documented — OpenMP is used internally to parallelize array operations, but no stated guarantee for concurrent access to the same Array from multiple threads |
| **Drop-in for the baseline** | false — replaces std::vector-based code with LibRapid's own Array&lt;T&gt;/Shape/expression-template API; call sites must be rewritten, it is not a header swap |

## Gotchas

- 'Optimise Small Arrays' is a separate opt-in CMake option (LIBRAPID_OPTIMISE_SMALL_ARRAYS, OFF by default and OFF in the published benchmark), so small-array performance without it is untested by the cited numbers
- The benchmark's std::vector baseline is naive nested loops, not std::valarray or a vectorization-friendly std::transform/std::reduce pipeline, so the measured ratio likely overstates the gap versus a tuned STL baseline
- Array slicing and generic array views are flagged 'Requires Rewrite' in open issues (#139, #253) rather than treated as stable
- The top-level CMakeLists forces BUILD_SHARED_LIBS off on Windows, so shared-library builds aren't exercised on that platform

## Caveats and trade-offs

First-party blog-post benchmark from the project's own account; single workload, single hardware/compiler configuration, and only 'default settings' given for MSVC flags (not fully enumerated); baseline is std::vector rather than the specific std::valarray/std::transform/std::reduce facilities named for this category, hence baseline_in_list=false.

Baseline used is naive nested std::vector&lt;std::vector&lt;double&gt;&gt; loops rather than std::valarray or a vectorization-friendly std::transform/std::reduce pipeline, so the comparison is somewhat favorable to LibRapid; large template-based array/tensor library with its own memory layout and (optional) Python bindings, so adoption is a bigger commitment than a header drop-in.

## Maintenance

Stale: solo student-maintainer project, last commit 2025-08-21, with 4 unresolved bug reports (autodiff product rule, indexing, trig functions, CUDA typo) filed the week before that last commit; MIT-licensed, but its CMake build with multiple optional native/GPU dependencies makes it a heavier vendor than a header-only library.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The first-party dev.to post (Feb 2023) includes benchmark code inline and states MSVC 19.33 and a Ryzen 9 3950X. Flags are given only as 'Default settings', so build config and optimization level are unknown. That makes it C, not A.
- **Verifier notes:** Numbers, compiler, CPU and OS all match the post. The only fix is the wording: 558.71% is the ratio (1.589ms / 284.405us = 5.587), not a percentage gain. Metadata checks out: MIT license, 179 stars, last commit 2025-08-21, so stale.
- **Fields the verifier corrected:** `claimed_speedup`
- **Pages the verifier opened:**
  - <https://dev.to/librapid/writing-faster-shorter-code-with-librapid-38lf>
  - <https://github.com/LibRapid/librapid>
- **Sources the enricher read:**
  - <https://github.com/LibRapid/librapid>
  - <https://dev.to/librapid/writing-faster-shorter-code-with-librapid-38lf>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/librapid/librapid`) · [data/wave1/enrich/raw/github_com_librapid_librapid.json](../../../data/wave1/enrich/raw/github_com_librapid_librapid.json) (enrichment confidence 0.6)

</details>
