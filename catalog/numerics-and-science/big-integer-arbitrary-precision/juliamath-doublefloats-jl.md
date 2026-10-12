# DoubleFloats.jl

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Big integers and arbitrary precision](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Julia` · `MIT` · 🟢 active

> Julia double-double floats (Double64, about 106-bit significand) running 6-25x faster than 128-bit BigFloat/MPFR on vector and matrix kernels.

| | |
|---|---|
| **Beats** | MPFR (via Julia BigFloat at 128-bit precision, 'Big128') |
| **Claimed result** | Relative time, smaller is faster, Double64 = 1. Versus Big128 (BigFloat/MPFR at 128 bits): dot(v,v) 7, v .+ v 16, v .\* v 25, exp.(m) 6, m \* m 9, det(m) 11. Versus Float128 (libquadmath via Quadmath.jl): dot(v,v) 3, v .+ v 7, v .\* v 12, exp.(m) 2, m \* m 3, det(m) 5. Vectors of 1000 values, 50x50 matrices. |
| **Workload** | BenchmarkTools timings on vectors of 1000 values and 50x50 matrices for dot, elementwise add and multiply, exp, matrix multiply and determinant, Double64 vs Float128 (libquadmath) and Big128 (BigFloat with setprecision 128). |
| **Metric** | throughput |
| **Adoption** | 172 stars |
| **Last commit** | 2026-07-28 |
| **Links** | [repository](https://github.com/JuliaMath/DoubleFloats.jl) · [benchmark](https://github.com/JuliaMath/DoubleFloats.jl) |

## Verdict

The README's first-party table (BenchmarkTools on unnamed hardware, Julia version unstated) shows Double64 taking 6-25x less time than BigFloat at 128-bit precision and 2-12x less than Quadmath Float128 on 1000-element vectors and 50x50 matrices; the repo's own docs/reports/benchmarks.jl run (Julia 1.12.6, CPU not stated) adds scalar multiply 2 ns vs 41 ns and 64x64 matmul 136 us vs 15.8 ms against 256-bit BigFloat. Neither comparison is precision-matched or names the CPU.

## Use it when

- Julia code that needs roughly 30-32 significant digits for ill-conditioned sums, dot products, LU/QR solves or eigenproblems: README reports 6x (elementwise exp) to 25x (elementwise multiply) less time than BigFloat at 128 bits.
- Arrays and 50x50-to-64x64 matrices where BigFloat's per-element allocation dominates: the 2026 benchmark report shows 64x64 matmul at 136 us vs 15.8 ms for 256-bit BigFloat.
- Mixed-precision refinement: map Float64 inputs to Double64 for the numerically sensitive part, then convert back, as the README recommends.
- Replacing Quadmath.jl Float128 when 106 bits suffice: README shows 2-12x less time than Float128 on the same kernels.

## Skip it when

- You need more than about 106 bits, an exponent range wider than Float64, or MPFR-style correct rounding: use BigFloat/MPFR (or Float128 for the wider exponent).
- Dense linear algebra where Float64 accuracy is enough: Double64 runs pure-Julia generic algorithms, 9-32x slower than Float64 LAPACK/BLAS in the project's report (n = 32-64).
- Double32: the README itself says Float64 is better for most purposes, and 64x64 matrix exp is 1017x slower than Float32 in the report.
- C or C++ projects: this is a Julia package; a C++ double-double library or a quad-precision library such as TLFloat fits there.
- Hot loops calling sin/cos on large arguments, or asin/acos at all: those take Float128 paths at about 600-1,100 ns per call (input-timing report).

## How it is fast

Each value is a non-overlapping (hi, lo) pair of hardware floats, and every operation is built from error-free transformations: two_sum (Knuth) and FMA-based two_prod (s = a\*b; t = fma(a, b, -s)), so an add or multiply is a handful of native Float64 instructions with no heap allocation. Values are immutable bits types stored inline in arrays, which the project's benchmark notes name as the main advantage over BigFloat (each BigFloat is a heap-allocated MPFR object). Elementary functions use argument reduction plus fused Horner polynomial kernels, with Float128 (libquadmath) fallbacks for hard ranges.

## Compared with alternatives

Pick DoubleFloats over MultiFloats.jl when you want the broader function library (elementary, special, complex, matrix functions, generic eigen/SVD) and accept that MultiFloats claims to be 2x faster; pick BigFloat/MPFR or APFP-style accelerators when you need more than 106 bits, and TLFloat or MPLAPACK's double-double backend when the code is C++.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | GenericLinearAlgebra, GenericSchur, Quadmath (GNU libquadmath), SpecialFunctions, plus stdlib LinearAlgebra, Printf, Random |
| **Minimum toolchain** | Julia 1.10 (Project.toml compat) |
| **Platforms** | not documented beyond Julia's own platforms; needs a working Quadmath.jl, which is a hard dependency |
| **Thread safety** | not documented; values are immutable bits types (src/Double.jl, benchmark report notes), so arithmetic has no shared state |
| **Drop-in for the baseline** | partial — Double64 can replace BigFloat in generic Julia code, but precision is fixed at about 106 bits (setprecision does not apply), results are not correctly rounded, and some functions BigFloat has are missing (loggamma/lgamma are exported but undefined, issue #323) |

## Gotchas

- Float64 literals are converted exactly as binary doubles: Double64(0.2) is 0.2000000000000000111..., so use df64"0.2" or Double64(2)/10 for decimal constants (README).
- Large-argument trig and deep-negative exp leave the fast path: sin/cos for abs(x) &gt;= 6.28125 go from 65 ns to about 630 ns, exp(-650) from 55 ns to 1,254 ns, and infinite inputs to sin/cos throw DomainError (docs/reports/input_timing_report.md).
- Versions 1.8.0-1.9.1 computed inv with only Float64-level accuracy for inputs whose low word is zero, degrading Double64 LU residuals from 1.8e-31 to 7.9e-19 (issue #291); a muladd allocation regression from v1.10 was fixed in July 2026. Use the current 1.11 line.
- Open accuracy and semantics issues: cos just below pi (#164), overflow behaviour that differs from Float64 (#151), subnormals (#181), and isapprox with tolerances beyond Float64 precision (#206).

## Known shortcomings

- Unequal precision: about 106-bit double-double vs correctly rounded 128-bit MPFR; no hardware or Julia version stated; Julia-only, not callable from C++.
- Correctness: v1.8.0-1.9.1 inv loses accuracy (LU residual 1.8e-31 becomes 7.9e-19, #291); open #164 (cos near pi), #151 (overflow), #323 (loggamma exported but undefined); sin/cos on large arguments and asin/acos fall back to Float128 (\~10x slower).

## Caveats and trade-offs

Table in the README has no hardware, Julia version, absolute times or benchmark script, only relative ratios from BenchmarkTools 'on one machine'. Not an equal-precision comparison: Double64 carries about 106 significand bits (the README says 85+ accurate bits) with Float64 exponent range and no correct rounding, while Big128 is correctly rounded 128-bit MPFR and Float128 has 6 more significant bits and a far wider exponent range. Compares against MPFR only through Julia's allocating BigFloat wrapper. Pure Julia package, not callable from C++ without embedding Julia; the like-for-like C++ library is QD (double-double/quad-double). MultiFloats.jl (separate entry) claims to be 2x faster than DoubleFloats.jl.

Double-double arithmetic: about 85-106 accurate bits with the Float64 exponent range, not arbitrary precision. Julia only.

## Maintenance

Actively maintained (last commit 2026-07-28, version 1.11.2), MIT-licensed, and registered in Julia's General registry under JuliaMath; usable only from Julia.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The README table ('More Performant Than Float128, BigFloat') gives first-party relative times for Double64 versus Float128 (libquadmath) and BigFloat at 128 bits (MPFR), produced with BenchmarkTools 'on one machine', with no hardware, Julia version, absolute times or linked benchmark script, so it is C.
- **Verifier notes:** All six Big128 ratios match the README exactly; I added the Float128 column from the same table. Metadata checked on github.com: MIT, 172 stars, not archived, default branch main, last commit 2026-07-28 (active). Julia-only package; the orchestrator may want to tag it as off-language for a C++ list.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/JuliaMath/DoubleFloats.jl>
  - <https://raw.githubusercontent.com/JuliaMath/DoubleFloats.jl/HEAD/README.md>
  - <https://github.com/JuliaMath/DoubleFloats.jl/commits/main>
- **Sources the enricher read:**
  - <https://github.com/JuliaMath/DoubleFloats.jl>
  - <https://raw.githubusercontent.com/JuliaMath/DoubleFloats.jl/HEAD/README.md>
  - <https://raw.githubusercontent.com/JuliaMath/DoubleFloats.jl/HEAD/Project.toml>
  - <https://raw.githubusercontent.com/JuliaMath/DoubleFloats.jl/HEAD/src/DoubleFloats.jl>
  - <https://raw.githubusercontent.com/JuliaMath/DoubleFloats.jl/HEAD/src/Double.jl>
  - <https://raw.githubusercontent.com/JuliaMath/DoubleFloats.jl/HEAD/src/math/errorfree.jl>
  - <https://raw.githubusercontent.com/JuliaMath/DoubleFloats.jl/HEAD/src/math/ops.jl>
  - <https://github.com/JuliaMath/DoubleFloats.jl/tree/main/docs/reports>
  - <https://raw.githubusercontent.com/JuliaMath/DoubleFloats.jl/HEAD/docs/reports/benchmark_report.md>
  - <https://raw.githubusercontent.com/JuliaMath/DoubleFloats.jl/HEAD/docs/reports/benchmarks.jl>
  - <https://raw.githubusercontent.com/JuliaMath/DoubleFloats.jl/HEAD/docs/reports/input_timing_report.md>
  - <https://raw.githubusercontent.com/JuliaMath/DoubleFloats.jl/HEAD/docs/reports/accuracy_report.md>
  - <https://github.com/JuliaMath/DoubleFloats.jl/commits/main>
  - <https://github.com/JuliaMath/DoubleFloats.jl/issues>
  - <https://github.com/JuliaMath/DoubleFloats.jl/issues/291>
  - <https://github.com/JuliaMath/DoubleFloats.jl/issues/164>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/juliamath/doublefloats.jl`) · [data/wave8/enrich/raw/github_com_juliamath_doublefloats_jl.json](../../../data/wave8/enrich/raw/github_com_juliamath_doublefloats_jl.json) (enrichment confidence 0.8)

</details>
