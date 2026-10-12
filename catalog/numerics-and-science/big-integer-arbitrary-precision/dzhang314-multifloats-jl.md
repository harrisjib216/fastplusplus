# MultiFloats.jl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `MIT` · 🟢 active

> Julia double/triple/quad-Float64 expansion arithmetic (about 106-212 bits) claimed 30x faster than BigFloat (MPFR) at 30 digits.

| | |
|---|---|
| **Beats** | MPFR (via Julia BigFloat) |
| **Claimed result** | README: 'At 30-digit precision, MultiFloats.jl is 30x faster than BigFloat, 6x faster than Quadmath.jl, and 2x faster than DoubleFloats.jl.' |
| **Workload** | Extended-precision (128-256 bit, 30-60 digit) floating-point arithmetic, e.g. +, -, \*, / and linear algebra such as 400x400 QR, versus Julia BigFloat (MPFR), Quadmath.jl and DoubleFloats.jl. |
| **Metric** | throughput |
| **Adoption** | 159 stars |
| **Last commit** | 2026-09-16 |
| **Links** | [repository](https://github.com/dzhang314/MultiFloats.jl) · [benchmark](https://github.com/dzhang314/MultiFloats.jl) |

## Verdict

The only package-level evidence is a first-party README sentence: at 30-digit precision it is 30x faster than Julia BigFloat (MPFR), 6x faster than Quadmath.jl (libquadmath) and 2x faster than DoubleFloats.jl. No table, hardware, Julia version or package version accompanies it, and the earlier QR/pseudoinverse benchmark gist has code but no recorded output. Search snippets say the peer-reviewed SC25 paper (not opened, host blocked) measures a C++ prototype of the same algorithms against GMP 6.3.0, MPFR 4.2.1 and FLINT 3.2.1, not this Julia package.

## Use it when

- Julia numerical code (linear algebra, ODEs, SDP or least-squares refinement) that loses accuracy in Float64 but needs only 30-60 digits.
- Element-wise kernels over large arrays where BigFloat's per-value heap allocation dominates; MultiFloat values are isbits tuples that pack into plain arrays.
- GPU kernels in Julia that need more than double precision (Float64x2), or more than single precision on Float32-only hardware (Float32x2-x4).
- Explicit SIMD code through the MultiFloatVec types (Vec2-Vec32 lanes), for example batched dot products.
- As a reference design for a C++ port: the author's MultiprecisionBenchmarks repo has a 373-line header-only C++ MultiFloat&lt;T,N&gt; with + and \* over double, __m128d, __m256d and __m512d.

## Skip it when

- You need more than about 212 bits, or a precision you choose at run time: Float64x5-Float64x8 were removed in v3.0 because the v2.0 algorithms for them were 'fundamentally broken', and no replacement exists yet.
- You need IEEE semantics for infinities: most operations treat +-Inf inputs as NaN (Float64x4(Inf) + 1.0 returns NaN), and the exponent range is only Float64's.
- Trigonometric, hyperbolic and inverse functions (sin, cos, atan, sinh and others) raise an error unless you call MultiFloats.use_bigfloat_transcendentals(), which converts to BigFloat on every call and loses the speed advantage. Open issues #90 (atan) and #74 (sin/cos) track this.
- Code in C++: the package is pure Julia. The C++ header in MultiprecisionBenchmarks covers only + and \* and needs x86 SSE/AVX/AVX-512 intrinsics plus FMA.
- Non-IEEE hardware or rounding modes other than round-to-nearest; the README says obscure architectures may need extra setup.

## How it is fast

Each value is an unevaluated sum of 2-4 machine floats (a floating-point expansion, as in double-double and QD quad-double). Arithmetic is fixed, branch-free networks of two_sum, fast_two_sum and FMA-based two_prod error-free transformations, fully inlined. Per the README these are new algorithms found by computer search (Zhang and Aiken, CAV25 and SC25 papers). There is no heap allocation and no data-dependent branching, so the code vectorises through SIMD.jl and runs as-is in CUDA, AMDGPU and oneAPI kernels via package extensions. exp2 and log2 are native polynomial and table kernels with expansion coefficients, not MPFR calls.

## Compared with alternatives

Pick it over DoubleFloats.jl when you need triple or quad-double (Float64x3/x4), SIMD vector types or GPU kernels, or the claimed 2x speedup at double-double. Pick TLFloat or simd-f128 instead when you need C or C++ code (TLFloat when you also need IEEE binary128 semantics), and MPLAPACK's dd/qd backends for C++ BLAS/LAPACK at this precision.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | Julia stdlib LinearAlgebra, Printf and Random; MPFR_jll 4 (conversions and the optional transcendental fallback); SIMD.jl 3. Weak dependencies: CUDA.jl, AMDGPU.jl and oneAPI.jl for GPU extensions. |
| **Minimum toolchain** | Julia 1.6 (Project.toml compat), package version 3.3.2 |
| **Platforms** | Any IEEE 754 CPU in round-to-nearest mode (x86 and ARM work out of the box per the README); FMA hardware needed for speed; NVIDIA, AMD and Intel GPUs through extensions |
| **Thread safety** | not documented; values are immutable isbits structs and the arithmetic is pure, but use_bigfloat_transcendentals() redefines Base methods through eval and should be called once at startup |
| **Drop-in for the baseline** | partial: a drop-in AbstractFloat for BigFloat or Float128 in generic Julia code at fixed 106/159/212-bit precision, but with no Inf semantics, no arbitrary or run-time precision, and trigonometric functions only through the opt-in BigFloat fallback |

## Gotchas

- Rare non-unique representations: about 1 in 2^53 values has several normalized forms, so use MultiFloats.canonize before bitwise hashing or equality on limbs.
- Mixed-type promotion: multiplying Float64x4 by UInt8 or Float32 promotes to the full Float64x4 product (open issue #34: about 250 us vs 170 us for a Float64 scalar). Convert small scalars to Float64 first.
- Generic LinearAlgebra solver paths can be slower than with DoubleFloats.jl despite faster matmul (open issue #85: 20x20 SDP 3.42 s vs 2.95 s for Double64).
- v3.0 fixed correctness bugs from v2.0: denormalized results that caused spurious accuracy loss (issues #42 and #45), prevfloat and nextfloat skipping values, and non-commutative multiplication. Pin v3 or later.

## Known shortcomings

- 30x/6x/2x claim in README with no method; correctness history: v2.0 Float64x5-x8 'fundamentally broken' (removed), v2.0 lost accuracy from denormalization, prevfloat/nextfloat skipped values before v3.0; Julia-only.
- README says transcendentals go through MPFR, but sin/cos/atan raise an error unless use_bigfloat_transcendentals() is called (exp/log are native); open perf issues #85 (LinearAlgebra solver slower than DoubleFloats, 3.42 vs 2.95 s) and #34.

## Caveats and trade-offs

README gives bare ratios ('at 30-digit precision ... 30x faster than BigFloat, 6x faster than Quadmath.jl, 2x faster than DoubleFloats.jl') without a table, hardware, Julia version or version of the package measured. The current v3.0 README no longer links the benchmark gist (gist.github.com/dzhang314/3e10463843f4ab5f5a4a2206c877771b, MultiFloatsBenchmark.jl: QR of 400x400 and pseudoinverse of 250x400 at about 106 bits); the gist has code but no recorded output. Correctness history: the README says the v2.0 algorithms for Float64x5-Float64x8 were 'fundamentally broken' (types removed in v3.0), v2.0 had denormalization issues causing spurious accuracy losses, and prevfloat/nextfloat skipped values before v3.0. Treats +-Inf inputs as NaN; transcendental functions go through MPFR. Compared against MPFR only through Julia's allocating BigFloat. Pure Julia package, not callable from C++ without embedding Julia. The SC25 paper (Zhang and Aiken, doi 10.1145/3712285.3759876) reportedly measures a C++ prototype of the same algorithms against QD, CAMPARY, MPFR and FLINT, but it was not opened.

Fixed small number of Float64 limbs (Float64x2/x3/x4, Float32x2-4), so precision is limited to roughly 106-212 bits rather than arbitrary; no dynamic allocation, branch-free algorithms usable on CPU and GPU in Julia. Transcendental functions fall back to MPFR. Julia only, so C++ use means a port.

## Maintenance

Actively maintained (v3.3.2, last commit 2026-09-16, 159 stars) and MIT-licensed, but usable only from Julia; C++ users would port the published networks or start from the benchmark header.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README's 30x/6x/2x claims against BigFloat (MPFR), Quadmath.jl and DoubleFloats.jl are first-party with no table, hardware, Julia version or linked script. The peer-reviewed SC25 paper could not be opened (theory.stanford.edu, dl.acm.org and arxiv.org are blocked here), and its public harness (dzhang314/MultiprecisionBenchmarks) benchmarks a separate C++ header rather than this Julia package, so it stays C.
- **Verifier notes:** Claim text matches the README verbatim; metadata checked on github.com: MIT, 159 stars, not archived, last commit 2026-09-16 (active). Strong lead for a separate C++ entry: github.com/dzhang314/MultiprecisionBenchmarks (MIT) contains a header-only C++ MultiFloats.hpp (multifloats/) plus Google Benchmark harnesses for MPFR, GMP, FLINT, CLN, QD, CAMPARY, Boost and libquadmath, built with g++-14 / clang++-20 '-O3 -march=native -flto -ffp-contract=off -fopenmp' (build_linux.sh). Search snippets credit the SC25 paper with up to 35.6x over MPFR, 11.7x over QD, 34.4x over CAMPARY and 41.4x over FLINT on AMD Zen 5. That could reach B, or A if the paper names the CPU model, but I did not open the paper.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://github.com/dzhang314/MultiFloats.jl>
  - <https://raw.githubusercontent.com/dzhang314/MultiFloats.jl/HEAD/README.md>
  - <https://github.com/dzhang314/MultiFloats.jl/commits/master>
  - <https://gist.github.com/dzhang314/3e10463843f4ab5f5a4a2206c877771b>
  - <https://github.com/dzhang314?tab=repositories>
  - <https://github.com/dzhang314/MultiprecisionBenchmarks>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/build_linux.sh>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/compile_flags.txt>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/multifloats/main.cpp>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/multifloats/MultiFloats.hpp>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/dzhang314/MultiFloats.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/dzhang314/MultiFloats.jl/HEAD/Project.toml>
  - <https://github.com/dzhang314/MultiFloats.jl/tree/master/src>
  - <https://raw.githubusercontent.com/dzhang314/MultiFloats.jl/HEAD/src/MultiFloats.jl>
  - <https://raw.githubusercontent.com/dzhang314/MultiFloats.jl/HEAD/src/mfadd.jl>
  - <https://raw.githubusercontent.com/dzhang314/MultiFloats.jl/HEAD/src/mfmul.jl>
  - <https://raw.githubusercontent.com/dzhang314/MultiFloats.jl/HEAD/src/exp.jl>
  - <https://raw.githubusercontent.com/dzhang314/MultiFloats.jl/HEAD/src/log.jl>
  - <https://raw.githubusercontent.com/dzhang314/MultiFloats.jl/HEAD/src/Reproducible.jl>
  - <https://github.com/dzhang314/MultiFloats.jl/issues>
  - <https://github.com/dzhang314/MultiFloats.jl/issues/85>
  - <https://github.com/dzhang314/MultiFloats.jl/issues/34>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/dzhang314/MultiprecisionBenchmarks/HEAD/multifloats/MultiFloats.hpp>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/dzhang314/multifloats.jl`) · [data/wave8/enrich/raw/github_com_dzhang314_multifloats_jl.json](../../../data/wave8/enrich/raw/github_com_dzhang314_multifloats_jl.json) (enrichment confidence 0.75)

</details>
