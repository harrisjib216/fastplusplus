# GLM (glm::mat4 add and multiply)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Math, SIMD and linear algebra](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> Header-only GLSL-style C++ vector/matrix library; beat a 2011 Eigen snapshot on 4x4 float math, but only on ARM phones.

| | |
|---|---|
| **Beats** | Eigen (Matrix4f, 2011 snapshot eigen-eigen-13a11181fc5a); CML 1.0.2 also measured |
| **Claimed result** | Android HTC Desire, milliseconds, lower is better. armeabi-v7a: GLM additions 1506 vs Eigen 2181 (1.45x, derived from page data), multiplications 2189 vs 5143 (2.35x, derived from page data). armeabi-v7a with NEON: additions 1407 vs 2145 (1.52x, derived from page data), multiplications 3108 vs 5113 (1.65x, derived from page data). Author: 'GLM is the fastest on the HTC Desire with both ABIs' (plain armeabi is a tie: additions 10256 vs 9944, multiplications 59008 vs 59460). Opposite result on the SSE x86 build: Eigen additions 30 vs GLM 76, multiplications 86 vs 400. |
| **Workload** | Element-wise addition and multiplication of lists of 4x4 float matrices (10 matrices per call, call repeated 1,000,000 times per cell, so 10M matrix operations per cell), wall time with gettimeofday, on a 2011 MacBook Pro and a stock HTC Desire phone. |
| **Metric** | throughput |
| **Hardware** | i7 2.2 GHz early-2011 MacBook Pro (Mac OS X Lion); stock HTC Desire (Android 2.2) with a 1 GHz Qualcomm QSD8250 |
| **Compiler and flags** | GCC, version not stated. CMakeLists Release flags -g0 -O2 (README: all tests -O2 except the non-SSE laptop build, which is -O0); x86 build adds -msse2 -msse3 -mssse3 -msse4.1 -msse4.2 -fopenmp; Android builds (NDK android-9 platform) add -mfloat-abi=softfp -mfpu=neon. |
| **Adoption** | 11.3k stars |
| **Last commit** | 2026-04-07 |
| **Links** | [repository](https://github.com/g-truc/glm) · [benchmark](https://github.com/mfoo/Math-Library-Test) |

## Verdict

mfoo/Math-Library-Test (2011-2012, GCC -O2, version unstated) timed 10 matrices x 1,000,000 repeats of 4x4 float add and multiply for GLM 0.9.3.B against an Eigen 3 snapshot. On a 1 GHz HTC Desire, GLM was 1.45x (add) and 2.35x (multiply) faster in the armeabi-v7a build and 1.52x/1.65x in the NEON build, plain armeabi was a tie, and on an i7 MacBook Pro with SSE Eigen was 2.5x and 4.7x faster.

## Use it when

- OpenGL/Vulkan or software-rendering code where GLSL-named types and functions (mat4, perspective, lookAt, quat) and value_ptr interop matter more than peak throughput.
- Small fixed-size float math on ARM mobile targets, the only setting with a measured win over Eigen: HTC Desire armeabi-v7a, 1.45x on 4x4 adds and 2.35x on 4x4 multiplies.
- Projects that want a dependency-free header-only math library that also compiles under CUDA (experimental) and on any C++17 compiler.
- Construction-heavy camera code: in RasterDuck/vectormathbench (Ryzen 9 3900X, SSE4.2) GLM built a perspective matrix in 2.20 ns versus 14.60 ns for DirectXMath.

## Skip it when

- Throughput-critical 4x4 matrix multiplies on x86: the cited test had Eigen 4.7x faster with SSE, and vectormathbench measured GLM's default mat4\*mat4 at 22.13 ns against 4.70 ns for DirectXMath and 3.68 ns for Realtime Math (SSE4.2).
- Model-matrix construction in hot loops (vectormathbench: 160.76 ns for GLM against 41.89 ns for DirectXMath).
- General or large linear algebra (dynamic sizes, decompositions, solvers, sparse): GLM covers graphics-sized types only; use Eigen or BLAS.
- Code that cannot move to C++17: master requires it, and older standards must stay on the GLM 1.0 branch.
- When you need SIMD without opting in: plain glm::mat4 does not take the intrinsic paths.

## How it is fast

Everything is inline header code on fixed-size types, so the compiler sees whole 4x4 operations with no heap and no expression-template machinery. The default (packed) mat4 multiply is a column-times-scalar loop (detail::mul4x4&lt;..., false&gt;) left to compiler auto-vectorisation. With GLM_FORCE_INTRINSICS (or GLM_FORCE_SSE2 to GLM_FORCE_AVX512) and aligned types, aligned matrices take a splat-and-FMA path and dedicated SSE or NEON code (NEON mul_lane/madd_lane mat4 multiply, SSE inverse, determinant and transpose). The 2011 ARM win most likely reflects GLM 0.9.3's plain scalar code compiling better for ARMv7 VFP/NEON than that Eigen snapshot (an inference; the benchmark author did not analyse it).

## Compared with alternatives

Pick GLM for GLSL-familiar, feature-complete graphics math. Klein (catalogued) composes rotations about 1.85x faster than GLM quaternions by llvm-mca cycle counts, so prefer it for rotor/motor-heavy skinning or kinematics. xsimd or Vc are for SIMD over arrays rather than per-object 4x4 math.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none |
| **Minimum toolchain** | C++17 on master (GCC 8+, Clang 6+, Apple Clang 6+, Visual C++ 2019+, CUDA 9.0+ experimental); the GLM 1.0 branch for older C++ |
| **Platforms** | any; optional SSE2 to AVX-512 and ARM NEON intrinsic paths when enabled by macros |
| **Thread safety** | not documented |
| **Drop-in for the baseline** | no |

## Gotchas

- SIMD is opt-in. You need GLM_FORCE_INTRINSICS or a GLM_FORCE_SSE2...AVX512 define, and the manual says the SIMD optimisations require aligned types. The aligned mat4 multiply only applies to aligned qualifiers, so a default glm::mat4 multiply runs the scalar column loop. Issue #1361 (open since 2025-04) shows users unsure which combination is needed.
- GLM_FORCE_DEFAULT_ALIGNED_GENTYPES changes struct layout: the manual's example struct grows from 32 to 48 bytes. Apply it consistently across translation units and to any data shared with GPU buffers or files.
- Default constructors are '= default' (uninitialised) unless GLM_FORCE_CTOR_INIT is defined. The 2011 benchmark relied on GLM 0.9.3 default-constructing identity matrices, so the same harness on current GLM would read uninitialised floats, just as its Eigen side already did.
- Behaviour churn between patch releases: 1.0.2 changed quaternion rotate direction and 1.0.3 reverted it. Pin a version if rotations matter.

## Known shortcomings

- Not faster on desktop: in mfoo/Math-Library-Test (2011-12) GLM wins only on a 2010 HTC Desire (armeabi-v7a); Eigen is 2.5x/4.7x faster with SSE on x86 and plain armeabi ties; one column was built at -O0, no GCC or NDK version, versions 14 years old. Kept and documented; dual Happy Bunny/MIT licence (MIT copyable); active.
- Enricher (mfoo/Math-Library-Test): Eigen inputs leave 12 of 16 matrix elements unset; EIGEN_TEST_NEON defaults ON and adds -mfpu=neon to every Android build, so the armeabi-v7a vs NEON columns are ambiguous; outputs are never read or checked. GLM's SIMD needs GLM_FORCE_INTRINSICS plus aligned types and the default mat4 multiply is a scalar column loop; in RasterDuck/vectormathbench GLM mat4\*mat4 is 1.7-4.7x slower than DirectXMath and 5.1-6.7x slower than RTM. Default constructors leave values uninitialised; quaternion rotate direction was flipped in 1.0.2 and reverted in 1.0.3; master needs C++17.

## Caveats and trade-offs

Weak and old evidence: a single hobbyist repo (42 stars, 15 commits, no licence shown) from 2011-2012 that vendors GLM 0.9.3.B, CML 1.0.2 and an Eigen 3 snapshot; current GLM 1.0.3 and Eigen 3.4+ behave differently. Only 4x4 float add and multiply were measured. On the tested Intel CPU with SSE, Eigen is 2.5x (additions) and 4.7x (multiplications) faster than GLM, and the author chose Eigen for that reason. The GLM win is on 2010 phone ARM cores (armeabi-v7a) and the plain armeabi column is a tie. The README's non-SSE laptop column is an -O0 build (GLM 2375/7337 vs Eigen 8065/22404) and is not a meaningful comparison. The README says 1 million matrices times 10 repeats but src/Driver.cpp runs 10 matrices times 1,000,000 repeats. The Eigen test matrices set only the diagonal (off-diagonals not initialised in the generator). Compiler and NDK versions not stated, no repeats or variance. Second source (not used for the numbers): RasterDuck/vectormathbench intermediate-benchmarks.md (AMD Ryzen 9 3900X, Windows, compiler not stated, 17 stars, GPL-3.0; BENCHMARKS.md there is empty) shows GLM ahead of DirectXMath on some vector composites (SSE4.2 ns/op: complex operation 1 1.51 vs 3.20, perspective matrix construction 2.20 vs 14.60) but behind on matrix-matrix multiply (22.13 vs 4.70) and model-matrix construction (160.76 vs 41.89); its README concludes Realtime Math and DirectXMath are generally faster than GLM. GLM's own test/perf programs only compare its scalar and SIMD paths and publish no numbers; the GLM README has no benchmark section. [retier] mfoo/Math-Library-Test (2011-12): GLM wins only on a 2010 HTC Desire; Eigen 2.5x/4.7x faster with SSE on x86; Eigen inputs leave 12 of 16 elements unset, NEON flag added to every Android build, outputs never checked, one column at -O0, no GCC/NDK version. GLM SIMD needs GLM_FORCE_INTRINSICS and aligned types; vectormathbench has GLM mat4\*mat4 1.7-4.7x slower than DirectXMath and 5.1-6.7x slower than RTM. Uninitialised default constructors; master needs C++17.

Header-only, GLSL-style API; SIMD paths are opt-in through GLM_FORCE_\* configuration and aligned types; no expression templates or lazy evaluation, so chained operations create temporaries. GLM is a graphics-oriented library and not a general linear-algebra package.

## Maintenance

Actively maintained (GLM 1.0.3 released 2025-12-31, 11.3k stars, not archived), dual MIT or Happy Bunny licensed and header-only, so trivially copyable. The 'faster than Eigen' evidence is one 14-year-old ARM-only hobby test with harness flaws: Eigen inputs have 12 of 16 elements left unset, its EIGEN_TEST_NEON option defaults ON and appends -mfloat-abi=softfp -mfpu=neon to every Android build so the armeabi-v7a vs NEON columns are ambiguous, and outputs are never read or checked. Current independent x86 data has GLM's default mat4 multiply 1.7-4.7x behind DirectXMath and 5.1-6.7x behind Realtime Math across SSE4.2/AVX/AVX2 builds (derived from page data).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** mfoo/Math-Library-Test README times GLM 0.9.3.B against an Eigen 3 snapshot (and CML 1.0.2) with public code (src/Driver.cpp, src/Main.cpp, src/androidactivity.cpp) and CPU models, but no GCC or NDK version is given and the per-column flags are only partly derivable from CMakeLists.txt, so it falls short of A; it is an obscure 42-star hobby test, not a well-known suite, so not B.
- **Verifier notes:** All claimed numbers match the README table exactly, and the record's caveats are accurate: Driver.cpp runs count=10 matrices (Main.cpp default and androidactivity.cpp testLibraries(10)) times NUM_TESTS=1,000,000, the non-SSE laptop column is -O0, and the Eigen generator sets only the diagonal while GLM 0.9.3 default-constructs identity. The GLM win holds only on the 2010 HTC Desire armeabi-v7a builds; on the SSE x86 build Eigen is 2.5x (additions) and 4.7x (multiplications) faster and the author chose Eigen, plain armeabi is a tie, and the versions tested are 14 years old. Metadata checked on github.com: 11.3k stars, not archived, latest release GLM 1.0.3 (2025-12-31), last commit 2026-04-07 (active); the repo states the Happy Bunny License or the MIT License (dual), so MIT/copyable stands. Math-Library-Test has no LICENSE file (404) but it is only the evidence repo.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier batch-63 (wave 1); enricher (wave 1)
- **Pages the verifier opened:**
  - <https://github.com/g-truc/glm>
  - <https://github.com/g-truc/glm/commits>
  - <https://github.com/mfoo/Math-Library-Test>
  - <https://raw.githubusercontent.com/mfoo/Math-Library-Test/HEAD/README.md>
  - <https://raw.githubusercontent.com/mfoo/Math-Library-Test/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mfoo/Math-Library-Test/HEAD/src/Driver.cpp>
  - <https://raw.githubusercontent.com/mfoo/Math-Library-Test/HEAD/src/Main.cpp>
  - <https://raw.githubusercontent.com/mfoo/Math-Library-Test/HEAD/src/androidactivity.cpp>
  - <https://raw.githubusercontent.com/mfoo/Math-Library-Test/HEAD/LIBRARIES.md>
  - <https://raw.githubusercontent.com/RasterDuck/vectormathbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/RasterDuck/vectormathbench/HEAD/intermediate-benchmarks.md>
  - <https://raw.githubusercontent.com/RasterDuck/vectormathbench/HEAD/BENCHMARKS.md>
- **Sources the enricher read:**
  - <https://github.com/g-truc/glm>
  - <https://raw.githubusercontent.com/g-truc/glm/HEAD/readme.md>
  - <https://raw.githubusercontent.com/g-truc/glm/HEAD/manual.md>
  - <https://raw.githubusercontent.com/g-truc/glm/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/g-truc/glm/HEAD/copying.txt>
  - <https://raw.githubusercontent.com/g-truc/glm/HEAD/glm/detail/setup.hpp>
  - <https://raw.githubusercontent.com/g-truc/glm/HEAD/glm/detail/type_mat4x4.inl>
  - <https://raw.githubusercontent.com/g-truc/glm/HEAD/glm/detail/type_mat4x4_simd.inl>
  - <https://raw.githubusercontent.com/g-truc/glm/HEAD/glm/detail/func_matrix_simd.inl>
  - <https://raw.githubusercontent.com/g-truc/glm/HEAD/glm/simd/matrix.h>
  - <https://github.com/g-truc/glm/issues?q=is%3Aissue+SIMD+slow>
  - <https://github.com/g-truc/glm/issues?q=is%3Aissue+GLM_FORCE_INTRINSICS>
  - <https://github.com/g-truc/glm/issues/1361>
  - <https://raw.githubusercontent.com/mfoo/Math-Library-Test/HEAD/README.md>
  - <https://raw.githubusercontent.com/mfoo/Math-Library-Test/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mfoo/Math-Library-Test/HEAD/LIBRARIES.md>
  - <https://raw.githubusercontent.com/mfoo/Math-Library-Test/HEAD/src/Driver.cpp>
  - <https://raw.githubusercontent.com/mfoo/Math-Library-Test/HEAD/src/Main.cpp>
  - <https://raw.githubusercontent.com/mfoo/Math-Library-Test/HEAD/src/androidactivity.cpp>
  - <https://raw.githubusercontent.com/RasterDuck/vectormathbench/HEAD/README.md>
  - <https://raw.githubusercontent.com/RasterDuck/vectormathbench/HEAD/intermediate-benchmarks.md>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/g-truc/glm`) · [data/wave1/enrich/raw/github_com_g_truc_glm.json](../../../data/wave1/enrich/raw/github_com_g_truc_glm.json) (enrichment confidence 0.6)

</details>
