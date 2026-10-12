# Axiom (C++ tensor library)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Lazy-evaluated C++20 NumPy/PyTorch-style tensor library for CPU and Metal GPU; beats Eigen3 on some unary math ops, loses on others.

| | |
|---|---|
| **Beats** | Eigen3 element-wise Array ops (A.array().sin()/cos()/exp()/log() on float32 MatrixXf) |
| **Claimed result** | sin: 26.0 GB/s (Axiom) vs 11.0 GB/s (Eigen3), \~2.4x (derived from page data); cos: 25.2 vs 11.0, \~2.3x (derived); exp: 23.0 vs 16.4, \~1.4x (derived); log: 17.0 vs 13.1, \~1.3x (derived). Same table shows sqrt and tanh as SLOWER than Eigen3, so the win is op-specific, not universal |
| **Workload** | Element-wise unary math ops (exp, log, sqrt, sin, cos, tanh, abs, neg, relu, sigmoid) over a 4096x4096 tensor, GB/s throughput, vs Eigen3, PyTorch, NumPy |
| **Metric** | throughput |
| **Hardware** | Apple M4 Pro (per README headline); the benchmark doc's own 'Test Environment' section only states 'Darwin 25.3.0, arm64' |
| **Compiler and flags** | Not stated in the benchmark doc. The top-level CMakeLists.txt adds -O3 -DNDEBUG (+ -mcpu=apple-m1 on Apple arm64) for Release builds with Clang/GCC. The compiler version and the build type actually used are not stated. |
| **Adoption** | 114 stars |
| **Last commit** | 2026-05-29 |
| **Links** | [repository](https://github.com/Frikallo/axiom) · [benchmark](https://github.com/Frikallo/axiom/blob/main/docs/BENCHMARKS.md) |

## Verdict

docs/BENCHMARKS.md (auto-generated 2026-02-21; Test Environment states only 'Darwin 25.3.0 arm64', no CPU model or compiler) reports 4096x4096 float32 unary-op GB/s vs Eigen3: sin 26.0 vs 11.0 (\~2.4x), cos 25.2 vs 11.0 (\~2.3x), exp 23.0 vs 16.4 (\~1.4x), log 17.0 vs 13.1 (\~1.3x); the same table shows sqrt (39.0 vs 66.3) and tanh (14.3 vs 21.5) slower than Eigen3. Code confirms macOS sin/cos/exp/log dispatch to Apple Accelerate vForce ahead of Axiom's own Highway kernels, so the measured win largely reflects Accelerate vs Eigen3's own vectorization rather than a novel Axiom algorithm.

## Use it when

- On macOS/Apple Silicon, want NumPy/PyTorch ergonomics in C++ with a Metal GPU path and zero-copy CPU/GPU transfers
- Whole-tensor elementwise math (exp/log/sin/cos) at large sizes (\~4096x4096 float32) where Accelerate vForce or Highway SIMD beats Eigen3's own vectorization
- Want einops-style rearrange/reduce and a lazy fused computation graph instead of hand-rolled expression templates
- Need built-in FFT, numpy/safetensors/flatbuffers IO, or basic NN layers (Linear, Conv, Attention, RNN) alongside tensor math
- Can link a built library (CMake, C++20 toolchain) rather than needing a header-only drop-in

## Skip it when

- Need a scalar, single-value &lt;cmath&gt;-style API — Axiom has no fine-grained per-value math entry point
- The op is sqrt or tanh specifically — Axiom's own benchmark table shows both slower than Eigen3 on the tested hardware
- Off-macOS (Linux/Windows), where the fast path is Highway SIMD + OpenMP, not Accelerate — the published GB/s numbers are macOS/Accelerate-specific and won't transfer as-is
- Need GPU acceleration beyond Apple Metal — no CUDA/ROCm backend
- Production use requiring API stability — v0.5.1, 114 stars, open issue on CPU-only macOS builds failing to link (#28) and a tracked gap in public-interface docs (#9)

## How it is fast

CPU element-wise ops dispatch through three tiers (seen in src/backends/cpu/cpu_operations.cpp): Apple Accelerate/vDSP (vvsinf/vvcosf/vvexpf/vvlogf) on macOS, then Google Highway's portable SIMD kernels (AVX2/AVX-512/NEON/SVE/RVV, see src/backends/cpu/simd/simd_dispatch.hpp) as the cross-platform fallback, then a scalar loop parallelized with OpenMP for large tensors. Matmul/linear algebra route through a BLAS/LAPACK backend (Accelerate, OpenBLAS, or native). A lazy graph compiler fuses chained elementwise operations and reuses buffers to cut materialization and memory traffic.

## Compared with alternatives

trigno_simd_cpp, SLEEF, FABE13-HX, fast_math_cpp, fmath, and VDT are scalar/vector math-function libraries meant to drop into existing loops in place of &lt;cmath&gt;/libm calls; Axiom is a whole-tensor library with a lazy graph and GPU path, so pick it only when you also want NumPy/PyTorch-style tensor ops and fusion — not when you just need a faster std::sin/std::exp replacement, where the siblings are the direct fit and Axiom is not.

## Integration

| | |
|---|---|
| **Form** | static lib \| shared lib (CMake FetchContent source-drop; not header-only) |
| **Dependencies** | bundled: Highway, mimalloc, pocketfft, flatbuffers, nlohmann_json, FP16, FXdiv; optional: OpenBLAS, Apple Accelerate framework (macOS), OpenMP, Metal/MPSGraph (macOS GPU) |
| **Minimum toolchain** | C++20, CMake 3.20+, Clang/GCC/MSVC |
| **Platforms** | macOS (Accelerate + Metal GPU), Linux, Windows; portable SIMD via Highway (SSE2 through AVX-512, NEON, SVE, RVV) |
| **Thread safety** | not documented beyond internally OpenMP-parallelized kernels; no stated guarantee about concurrent access to a single Tensor from multiple threads |
| **Drop-in for the baseline** | false — different API model (whole-tensor NumPy/PyTorch semantics, lazy graph) vs Eigen3's expression templates |

## Gotchas

- On macOS the measured unary-op speedups over Eigen3 come from Apple Accelerate vForce (vvsinf/vvcosf/vvexpf/vvlogf), not Axiom's own SIMD kernels — the win is largely Accelerate's, not portable
- sqrt and tanh are slower than Eigen3 in Axiom's own benchmark table — op-specific, not a blanket win
- Open issue #28: CPU-only builds on macOS can fail to link because some Metal call sites guard on __APPLE__ instead of the AXIOM_METAL_SUPPORT flag
- Library type follows BUILD_SHARED_LIBS (defaults to SHARED); set it explicitly before FetchContent/add_subdirectory if you need a single static archive

## Caveats and trade-offs

On macOS, Axiom's float32 sin/cos/exp/log/sqrt dispatch straight to Apple Accelerate vForce (vvsinf/vvcosf/vvexpf/vvlogf in src/backends/cpu/cpu_operations.cpp and vdsp.cpp). The measured win over Eigen3 is therefore Apple Accelerate's, not Axiom's own kernels. A code comment says Accelerate is internally parallelized, while the Eigen3 comparison binary does not link Accelerate. PyTorch beats Axiom on exp, log, sin, cos, sqrt and sigmoid in the same table. The benchmark is first-party and auto-generated (make benchmark, 2026-02-21). The doc's Test Environment gives only 'Darwin 25.3.0 arm64'. 'M4 Pro' appears only in the README matmul headline. The baseline is Eigen3, not std::transform+&lt;cmath&gt;.

Not a std::-drop-in: NumPy/PyTorch-like whole-tensor API, no scalar single-value entry point; on macOS Axiom itself delegates BLAS-level and possibly vectorized-math work to Apple's Accelerate framework, so part of the win may reflect Accelerate/vForce vs Eigen's own vectorization rather than a novel Axiom algorithm; several unary ops (sqrt, tanh) are slower than Eigen3 in the same table

## Maintenance

Actively maintained (last commit 2026-05-29, v0.5.1, MIT) but young and small (114 stars, 5 open issues); 'copyable' usability means a real CMake build with bundled third-party deps, not a single header to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** docs/BENCHMARKS.md unary table at 4096x4096 matches (sin 26.0 vs Eigen3 11.0 GB/s, cos 25.2 vs 11.0, exp 23.0 vs 16.4, log 17.0 vs 13.1; sqrt and tanh slower). The code is public (benchmarks/compare/unary_axiom.cpp, unary_eigen.cpp), but the doc states only 'Darwin 25.3.0 arm64' with no CPU model or compiler, so it is C.
- **Verifier notes:** Numbers are accurate and tier C is right. The key finding is attribution: on the benchmarked platform the sin/cos/exp/log wins come from calling Apple Accelerate vForce, so the orchestrator may want to treat this as weak or platform-specific evidence.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/Frikallo/axiom/blob/main/docs/BENCHMARKS.md>
  - <https://github.com/Frikallo/axiom>
  - <https://github.com/Frikallo/axiom/blob/main/benchmarks/compare/unary_eigen.cpp>
  - <https://github.com/Frikallo/axiom/blob/main/benchmarks/CMakeLists.txt>
  - <https://github.com/Frikallo/axiom/blob/main/CMakeLists.txt>
  - <https://github.com/Frikallo/axiom/blob/main/src/backends/cpu/cpu_operations.cpp>
  - <https://github.com/Frikallo/axiom/blob/main/src/backends/cpu/vdsp.cpp>
- **Sources the enricher read:**
  - <https://github.com/Frikallo/axiom>
  - <https://github.com/Frikallo/axiom/blob/main/README.md>
  - <https://github.com/Frikallo/axiom/blob/main/docs/BENCHMARKS.md>
  - <https://github.com/Frikallo/axiom/blob/main/CMakeLists.txt>
  - <https://github.com/Frikallo/axiom/blob/main/src/backends/cpu/cpu_operations.cpp>
  - <https://github.com/Frikallo/axiom/blob/main/include/axiom/error.hpp>
  - <https://github.com/Frikallo/axiom/blob/main/src/backends/cpu/simd/simd_dispatch.hpp>
  - <https://github.com/Frikallo/axiom/blob/main/docs/getting-started.md>
  - <https://github.com/Frikallo/axiom/issues>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/frikallo/axiom`) · [data/wave1/enrich/raw/github_com_frikallo_axiom.json](../../../data/wave1/enrich/raw/github_com_frikallo_axiom.json) (enrichment confidence 0.55)

</details>
