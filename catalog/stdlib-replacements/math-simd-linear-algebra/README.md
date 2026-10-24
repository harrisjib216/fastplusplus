# Math, SIMD and linear algebra

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md)</sub>

**What these beat:** std::valarray, std::transform, std::reduce, &lt;cmath&gt;  
**32 entries:** 5 tier A · 3 tier B · 21 tier C · 3 tier D · 32 copyable, 0 study only

| # | Project | What it is | Tier | Language | License | Status |
|--:|---|---|:-:|---|---|---|
| 1 | [**Vc (SIMD Vector Classes)**](vcdevel-vc.md) | C++11 SIMD vector types (float_v, double_v) with vectorized math for x86 SSE2-AVX2; beats per-element scalar &lt;cmath&gt; loops. | **A** | C++ | BSD-3-Clause | 🟢 active |
| 2 | [**muParser**](beltoforion-muparser.md) | Runtime math-expression parser that compiles to a bytecode stack machine; beats TinyExpr, Lepton and muParserX, not ExprTk. | **A** | C++ | BSD-2-Clause | 🟢 active |
| 3 | [**trigno_simd_cpp (SIMD trigonometric approximations, Goyal &…**](nikhil0250-trigno-simd-cpp.md) | Piecewise rational sin/cos/tan approximation using AVX2 FMA plus a fast inverse-sqrt hack; beats scalar libm sin/cos/tan. | **A** | C++ | Apache-2.0 | 🟢 active |
| 4 | [**FastMath C++ Library (fast_math_cpp)**](hijimasa-fast-math-cpp.md) | Header-only float math library beating glibc's &lt;cmath&gt; on composed functions (sinh, tanh, atan2, integer pow), not raw trig or exp/log. | **A** | C++ | MIT | 🟢 active |
| 5 | [**ExprTk**](arashpartow-exprtk.md) | Header-only C++ runtime expression parser/evaluator; evaluates pre-compiled expressions about 2-4x faster than muparser 2.2.4. | **A** | C++ | MIT | 🟡 stale |
| 6 | [**SLEEF (SIMD Library for Evaluating Elementary Functions)**](shibatch-sleef.md) | Vectorized C library of libm math functions (sin, cos, exp, log, pow); beats scalar &lt;cmath&gt;/libm when call sites are SIMD-batched. | **B** | C | BSL-1.0 | 🟢 active |
| 7 | [**fastmod**](lemire-fastmod.md) | Header-only C/C++ 32-bit remainder, division and divisibility by a reused divisor (LKK direct remainder); about 3x faster than hardware div. | **B** | C++ | Apache-2.0 | 🟢 active |
| 8 | [**VDT (VectoriseD maTh)**](dpiparo-vdt.md) | Header-only Padé-polynomial libm replacements for exp/log/trig/asin-acos-atan/isqrt, auto-vectorizable, 1.3-13x faster scalar. | **B** | C++ | LGPL-3.0-or-later | 🟡 stale |
| 9 | [**GLM (glm::mat4 add and multiply)**](g-truc-glm.md) | Header-only GLSL-style C++ vector/matrix library; beat a 2011 Eigen snapshot on 4x4 float math, but only on ARM phones. | **C** | C++ | MIT | 🟢 active |
| 10 | [**SIMD Everywhere**](simd-everywhere-simde.md) | Header-only C99 library implementing x86 (MMX to AVX2, parts of AVX-512), Neon and WASM SIMD intrinsics on any target, beating scalar ports. | **C** | C | MIT | 🟢 active |
| 11 | [**NumKong (formerly SimSIMD)**](ashvardanian-simsimd.md) | Header-only SIMD kernel library beating GCC's auto-vectorized f16 loops in dot product and distance metrics 20-118x. | **C** | C++ | Apache-2.0 | 🟢 active |
| 12 | [**FANN (Fast Artificial Neural Network Library)**](libfann-fann.md) | Small C library for training and running multilayer perceptrons; 2003 report shows 164x over jneural, \~1.3x over lwnn. | **C** | C | LGPL-2.1 | 🟢 active |
| 13 | [**libdivide**](ridiculousfish-libdivide.md) | Header-only C/C++ library replacing division by a runtime-invariant integer with multiply-shift sequences; about 6.7x over hardware DIV. | **C** | C++ | Zlib OR BSL-1.0 | 🟢 active |
| 14 | [**CMSIS-DSP (FFT)**](arm-software-cmsis-dsp.md) | Arm's C library of DSP kernels for Cortex-M and Cortex-A; its FFTs beat textbook plain-C radix-2 FFTs on Cortex-M4. | **C** | C | Apache-2.0 | 🟢 active |
| 15 | [**libfixmath**](petteriaimonen-libfixmath.md) | Q16.16 fixed-point math library in C for FPU-less targets; on 8-bit AVR, add/sub beat soft-float about 2x, mul/div lose. | **C** | C | MIT | 🟢 active |
| 16 | [**fmath (herumi)**](herumi-fmath.md) | SIMD array-mode log/exp for float buffers, 9-19x faster than std::logf/std::expf via AVX2/AVX-512. | **C** | C++ | BSD-3-Clause | 🟢 active |
| 17 | [**Axiom (C++ tensor library)**](frikallo-axiom.md) | Lazy-evaluated C++20 NumPy/PyTorch-style tensor library for CPU and Metal GPU; beats Eigen3 on some unary math ops, loses on others. | **C** | C++ | MIT | 🟢 active |
| 18 | [**Cache-blocked double-precision matrix multiply with tile…**](paper-book-the-cpp-programmers-mindset-cache-blocked-gemm.md) | Teaching example: 32x32 cache-blocked scalar dgemm with a tile accumulator, about 1.9x faster than a naive triple loop. | **C** | C++ | MIT | 🟢 active |
| 19 | [**Clamp loop with conditional store instead of std::min (The…**](paper-book-the-cpp-programmers-mindset-clamp-conditional-store.md) | Book micro-idiom: an if-guarded store clamp loop beats a std::min (cmov) clamp loop by about 1.2x, vectorisation off. | **C** | C++ | MIT | 🟢 active |
| 20 | [**LibRapid**](librapid-librapid.md) | Templated C++20/23 array/tensor library with SIMD, OpenMP, CUDA and OpenCL backends; beats naive std::vector loops on elementwise math. | **C** | C++ | MIT | 🟡 stale |
| 21 | [**GPU Programming with C++ and CUDA: CUDA vector addition…**](paper-book-gpu-programming-with-cpp-and-cuda-vector-add-kernel.md) | Textbook one-thread-per-element CUDA float vector add: 44x kernel-only over a scalar CPU loop, 1.02x once copies count. | **C** | C++ | MIT | 🟡 stale |
| 22 | [**GPU Programming with C++ and CUDA: shared-memory tiled…**](paper-book-gpu-programming-with-cpp-and-cuda-tiled-matmul.md) | Textbook CUDA FP32 matrix multiply with 16x16 shared-memory tiles; about 1.42x faster than the book's own naive kernel. | **C** | C++ | MIT | 🟡 stale |
| 23 | [**GPU Programming with C++ and CUDA: two-stream chunked copy…**](paper-book-gpu-programming-with-cpp-and-cuda-stream-overlap.md) | Book CUDA pattern: row chunks copied from pinned memory on two streams so transfers overlap the GEMV kernel. | **C** | C++ | MIT | 🟡 stale |
| 24 | [**FABE13-HX**](farukalpay-fabe.md) | SIMD sin/cos/sincos array kernel for C beating libm; rational Ψ-Hyperbasis approximation, no bit-exact IEEE guarantee. | **C** | C | MIT | 🟡 stale |
| 25 | [**Klein**](jeremyong-klein.md) | Header-only SSE library for 3D projective geometric algebra; its llvm-mca listings show about half GLM's estimated cycles for quaternion and dual-quaternion work. | **C** | C++ | MIT | 🔴 abandoned |
| 26 | [**FastNoiseSIMD**](auburn-fastnoisesimd.md) | SIMD 3D coherent-noise generator (Perlin, simplex, value, cellular, cubic) filling float grids 4-45x faster than libnoise. | **C** | C++ | MIT | 🔴 abandoned |
| 27 | [**Extreme C: cache-friendly row-major matrix summation…**](paper-book-extreme-c-row-major-matrix-traversal.md) | Book example: summing a row-major C int matrix in memory order instead of column by column, for cache locality. | **C** | C | MIT | 🔴 abandoned |
| 28 | [**FastDivide (komrad36)**](komrad36-fastdivide.md) | Branch-free 64-bit unsigned divide and modulo via a Newton-Raphson reciprocal; claims about 30% faster than hardware div on Intel. | **C** | C++ | MIT | 🔴 abandoned |
| 29 | [**FastDivide128 (komrad36)**](komrad36-fastdivide128.md) | Unsigned 128-bit Div/Mod/DivMod for x86-64 with BMI2; author says about 2x faster than compiler-rt's __udivmodti4. | **C** | C++ | MIT | 🔴 abandoned |
| 30 | [**xsimd**](xtensor-stack-xsimd.md) | Header-only C++ SIMD abstraction: portable batch&lt;T,Arch&gt; type replaces scalar loops across x86/ARM/RISC-V/WASM. | **D** | C++ | BSD-3-Clause | 🟢 active |
| 31 | [**Yeppp!**](wdv4758h-yeppp.md) | Abandoned 2013-2015 SIMD array math library (log, exp, sin, dot, sum); hand-tuned assembly only for pre-2015 x86-64 cores. | **D** | C | BSD-3-Clause | 🔴 abandoned |
| 32 | [**fastapprox**](pmineiro-fastapprox.md) | Header-only C/C++ single-precision approximations of exp, log, pow, sigmoid, trig, erf, lgamma and Lambert W, with SSE2 variants; no measured speedup over libm. | **D** | C | BSD-3-Clause | 🔴 abandoned |

<sub>Tiers: **A** reproducible public benchmark (code, compiler, flags and CPU stated) · **B** independent or peer-reviewed measurement · **C** first-party claim · **D** directional, no numbers. Status: 🟢 active · 🔵 finished · 🟡 slow or stale · 🔴 abandoned · ⚪ unknown. *Study only* means no usable open-source license: read the idea, don't copy the code.</sub>
