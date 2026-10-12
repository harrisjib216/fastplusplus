# D (gdc, ldc2) matmul with std.numeric.dotProduct in kostya/benchmarks

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Numerics and arrays](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `D` · `MIT` · 🟢 active

> D matmul in kostya/benchmarks: Phobos dotProduct's two partial sums run about 2x faster than the suite's single-accumulator C loop.

| | |
|---|---|
| **Beats** | C/gcc 16.1.0 and C/clang 22.1.8 (-O3 -march=native -flto=auto, -std=c23) transposed dot-product matmul of 1500x1500 doubles |
| **Claimed result** | kostya/benchmarks matmul table (median, Xeon E-2324G, README updated 2026-07-19): D/gdc 1.505 s, D/ldc2 1.722 s, D/dmd 1.880 s versus C/gcc 3.034 s and C/clang 3.067 s, i.e. gdc about 2.0x, ldc2 about 1.76x and dmd about 1.61x faster than gcc C (derived from page data). Rust 3.067 s, Zig 3.071 s and Nim/gcc 3.091 s tie with C. Not like for like: the D program calls std.numeric.dotProduct (two partial sums) while every tied language runs the single-accumulator loop; in the like-for-like plb2 matmul (same i-k-j loop in D and C, Apple M1) D ldc2 1.35.0 takes 0.57 s versus C clang 15.0.0 0.54 s, so D is about 5% slower there (derived from page data). BLAS-backed rows (D lubeck 0.042 s, C++ Eigen 0.081 s, NumPy, Arraymancer) are library comparisons and excluded. |
| **Workload** | Allocate, generate and multiply two 1500x1500 double matrices; the D version transposes b and calls std.numeric.dotProduct per output cell, the C version transposes b and runs one scalar accumulation loop. |
| **Metric** | throughput |
| **Hardware** | Intel(R) Xeon(R) E-2324G, Debian forky/sid Docker image, README updated 2026-07-19 |
| **Compiler and flags** | From common/commands.mk: C gcc 16.1.0 / clang 22.1.8 '-Wall -Wextra -pedantic -Wcast-align -O3 -march=native -flto=auto -Wa,-mbranches-within-32B-boundaries -std=c23'; D ldc2 1.41.0 '-O5 -release -boundscheck=off', gdc 14.2.0 '-O3 -frelease -finline -fbounds-check=off', dmd v2.111.0 '-O -release -inline -boundscheck=off'. The D builds carry no -march=native and no LTO, so the flag difference favours C. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Why it wins** | Derived by the searcher from the source, not stated by the suite: Phobos std.numeric.dotProduct (std/numeric.d) unrolls 16-wide with two partial sums (sum0, sum1), a different floating-point reduction order; the C loop keeps one strict-FP accumulator and is built without -ffast-math, so the compiler cannot reassociate or vectorize it. |
| **Adoption** | 2.9k stars; widely cited cross-language benchmark |
| **Last commit** | 2026-07-19 |
| **Links** | [repository](https://github.com/kostya/benchmarks) · [benchmark](https://github.com/kostya/benchmarks/blob/master/README.md) |

## Verdict

kostya/benchmarks (README updated 2026-07-19, Intel Xeon E-2324G, medians) times 1500x1500 double matmul at 1.505 s for D/gdc 14.2.0, 1.722 s for D/ldc2 1.41.0 and 1.880 s for D/dmd 2.111.0 versus 3.034 s for C/gcc 16.1.0 and 3.067 s for C/clang 22.1.8 (-O3 -march=native -flto=auto), so about 2.0x, 1.76x and 1.61x (derived from page data); the gap comes from Phobos dotProduct's two partial sums against a one-accumulator strict-FP C loop.

## Use it when

- As a demonstration that multiple partial sums matter for strict-FP reductions: any dot-product or sum loop compiled without -ffast-math is latency-bound on one accumulator
- D code that needs a portable, dependency-free dot product of double or float slices: std.numeric.dotProduct is already in Phobos and beats a hand-written single-accumulator loop
- Small or medium vectors where linking BLAS is not worth it and a few-ulp change in summation order is acceptable

## Skip it when

- As evidence that D beats C: in attractivechaos/plb2, with the same i-k-j loop in both languages on Apple M1, D ldc2 1.35.0 takes 0.57 s versus C clang 15.0.0 0.54 s
- Real matrix multiplication: in the same table the BLAS-backed D/ldc2 (lubeck) row runs in 0.042 s and C++ Eigen in 0.081 s, about 36x and 19x faster than D/gdc
- When bit-for-bit agreement with a sequential reference sum is required: two partial sums change rounding
- When the C side can be changed: two or more accumulators, or -ffast-math or -fassociative-math, in C give the same effect without switching language

## How it is fast

dotProduct (std/numeric.d) walks the arrays through raw pointers in 16-element blocks, alternating products into two accumulators (sum0, sum1), then 4-element blocks, then a scalar tail, so the loop carries two independent floating-point add chains instead of one. The C, Rust, Zig and Nim loops keep a single accumulator under strict IEEE semantics (no -ffast-math), so the compiler can neither reassociate nor vectorize the reduction and every iteration waits on the previous add. Halving the dependency chain roughly halves the time: C at 3.034 s versus gdc at 1.505 s (derivation from the table, not stated by the suite).

## Compared with alternatives

Unlike the Fortran plb2 sibling (same i-k-j loop as C, 0.51 s versus 0.54 s) this is not a language-level win, so pick it only as the two-accumulator lesson or when you are already writing D; for actual matrix products, BLAS wrappers and Julia packages in the category (Gaius.jl and the lubeck row) are far faster.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none beyond Phobos and druntime (std.numeric); the benchmark program also uses the GC for its matrices |
| **Minimum toolchain** | any current D compiler; measured with gdc 14.2.0, ldc2 1.41.0 and dmd v2.111.0 |
| **Platforms** | any (portable scalar D, no intrinsics); measured on x86-64 Intel Xeon E-2324G |
| **Thread safety** | not documented; the function reads two const slices and keeps only local state |
| **Drop-in for the baseline** | no |

## Gotchas

- Not like for like: the C, Rust, Zig and Nim versions that tie at about 3.03-3.12 s each use one accumulator, while the D program calls a hand-unrolled two-accumulator library kernel; the results therefore differ in the last bits, and the harness self-test only checks calc(101) within 0.1 of -18.67.
- Flags favour C, not D: C gets -O3 -march=native -flto=auto from common/commands.mk, the D builds have no -march and no LTO, so the D lead is not a codegen advantage.
- The D/gdc row reports a peak RSS increase of 4.00 MiB while D/ldc2 and D/dmd report 70.38 MiB for the same four 1500x1500 matrices (xtime.rb samples /proc/PID/statm every 10 ms); the suite gives no explanation, so treat the gdc memory column as unreliable.
- The timed region (between the notify start and stop messages) includes matrix generation, GC allocation and the transpose, not only the multiply.

## Known shortcomings

- The 2x comes from Phobos dotProduct's two partial sums against a single-accumulator C loop, not the language; like for like (plb2) D ldc2 0.57 s is slower than C 0.54 s; D builds lack -march and -flto.
- The JSON3.jl enricher found that kostya/benchmarks' 2026-07-19 update re-measured only the Primes table and the environment table: the Json table rows kept their 2025-08-17 values (gcc 14.2.0, clang 19.1.7), so the compiler versions recorded here (gcc 16.1.0, clang 22.1.8) describe the current environment table and may not be the toolchain behind this table's rows; whether this table was re-run on 2026-07-19 was not checked.
- Confirmed: Phobos dotProduct uses two partial sums while the C, Rust, Zig and Nim loops use one accumulator, and C 3.034 s vs gdc 1.505 s fits a halved add chain (derived). New anomaly: the D/gdc memory column shows +4.00 MiB against +70.38 MiB for ldc2 and dmd on the same matrices, cause not found, so the gdc memory column is unreliable.

## Caveats and trade-offs

Not a language or compiler advantage: the high-level algorithm (transpose plus dot products) is the same, but the timed D path is Phobos' hand-unrolled two-accumulator dotProduct against a naive single-accumulator C loop, so summation order and results differ in the last bits (the harness only checks within 0.1 at n=101). Like for like (plb2, same loop in both languages) D ldc2 is slower than C. The C row is deliberately plain ('written as the average developer would'); C gets -march=native and -flto=auto that the D builds lack. gcc 16.1 and clang 22 are newer than the GCC 14 and LLVM bases of gdc and ldc2. Time includes allocation (D uses GC-allocated jagged arrays, C malloc/calloc rows) and matrix generation. [retier] Phobos dotProduct uses two partial sums while the C, Rust, Zig and Nim loops use one accumulator, and C 3.034 s vs gdc 1.505 s fits a halved add chain. The D/gdc memory column shows +4.00 MiB against +70.38 MiB for ldc2 and dmd on the same matrices (cause not found), so it is unreliable.

Gain comes from one standard-library kernel, so a C programmer can match it by writing two or more accumulators or using -ffast-math; D's runtime and GC are not involved in the timed loop.

## Maintenance

kostya/benchmarks is active (2.9k stars, MIT, results refreshed 2026-07-19) and std.numeric.dotProduct ships with every D compiler, but the entry documents a kernel difference rather than a reusable D advantage.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** The kostya/benchmarks README (UPDATE 2026-07-19, Xeon E-2324G, versions listed) shows D/gdc 1.505 s, D/ldc2 1.722 s, D/dmd 1.880 s against C/gcc 3.034 s and C/clang 3.067 s, with code (matmul/matmul.c, matmul/matmul.d) and flags (common/commands.mk) public, so the harness is A-grade; capped at C because the comparison is not like for like: matmul.d calls Phobos std.numeric.dotProduct, a hand-unrolled 16-wide kernel with two partial sums, against a single-accumulator strict-FP C loop, and the like-for-like D port in attractivechaos/plb2 (same i-k-j loop in D and C) is slower than C (ldc2 0.57 s versus clang 0.54 s on Apple M1), so the 2x is a kernel difference, not a D advantage (asymmetric-comparison precedent, as TensorFlow and GStreamer B to C).
- **Verifier notes:** Numbers match the README row for row and the flags match common/commands.mk. Shortcoming to record: the 2x comes from std.numeric.dotProduct's two partial sums (different accumulator structure and FP order) against a single-accumulator C loop; like-for-like plb2 shows D ldc2 0.57 s slower than C 0.54 s, so it is not a D language win. Held at C rather than D because the C build is fully optimised (-O3 -march=native -flto) and both programs follow the suite's common reference implementation; the orchestrator may treat the tuned library kernel as the crippled-baseline case if it prefers.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-02 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/README.md>
  - <https://github.com/kostya/benchmarks/tree/master/matmul>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/matmul.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/matmul.d>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/commands.mk>
  - <https://raw.githubusercontent.com/dlang/phobos/master/std/numeric.d>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/d/matmul.d>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/d/Makefile>
  - <https://github.com/kostya/benchmarks>
  - <https://github.com/kostya/benchmarks/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/README.md>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/matmul.d>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/matmul.c>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/Makefile>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/common/commands.mk>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/xtime.rb>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/matmul.rs/src/main.rs>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/matmul.zig>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/matmul.nim>
  - <https://raw.githubusercontent.com/kostya/benchmarks/master/matmul/matmul.cpp>
  - <https://github.com/kostya/benchmarks/tree/master/common>
  - <https://github.com/kostya/benchmarks/issues?q=matmul>
  - <https://raw.githubusercontent.com/dlang/phobos/master/std/numeric.d>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/README.md>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/d/matmul.d>
  - <https://raw.githubusercontent.com/attractivechaos/plb2/master/src/d/Makefile>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `lang:d/kostya/benchmarks#matmul`) · [data/wave14/enrich/raw/lang_d_kostya_benchmarks_matmul.json](../../../data/wave14/enrich/raw/lang_d_kostya_benchmarks_matmul.json) (enrichment confidence 0.8)

</details>
