# vek

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `MIT` · 🟡 stale

> Go float32/float64/bool vector library with AVX2+FMA assembly kernels, against its own pure-Go loops.

| | |
|---|---|
| **Beats** | pure-Go fallback of the same library (plain Go loops) |
| **Claimed result** | README: 'Fast, average speedups of 10x for float32 vectors'. Table at 100k elements (CPU and Go version unstated): vek32.Sum 65,007 ns Go vs 3,191 ns SIMD (20x), vek32.Add 6x, vek.Add 2x, vek.MatMul 7x and vek32.MatMul 14x at m = n = p = 1k. The transcendental rows (vek32.Exp 1,120,300 vs 49,694 ns, 22x; vek32.Log 16x; Pow; Sqrt) were measured on inputs drawn from NormFloat64()\*100, so about half of the Log, Sqrt and Pow results are NaN and about 38% of the Exp inputs have \|x\| &gt; 88.7 (Inf, 0 or denormal), a regime the README itself calls undefined for the SIMD path; the vek.And 139x row compares a short-circuit 'x[i] = x[i] && y[i]' loop on random 50% booleans with a bitwise & kernel, and the vek.Maximum 8x row mostly measures branch mispredictions in the if/else baseline. The README's 1k column for Add, Mul, Abs, Round, Sqrt, Pow, Exp, Log, Maximum, Lt and And, and its MatMul p = 1 rows, cannot be produced by the committed go test command (those benchmarks loop over 10k and 100k only since ff9d7ac; MatMul uses p of 100 or 1000). |
| **Workload** | In-place float32 and float64 vector operations (Add, Mul, Abs, Sum, Round, Sqrt, Pow, Exp, Log, Max, Find, comparisons, boolean And/All) on 1k and 100k element slices, plus MatMul and 4x4 matrix multiply. |
| **Metric** | throughput |
| **Compiler and flags** | go test -benchmem -timeout 0 -run=^# -bench=. ./internal/... ; Go version not stated; the AVX2 kernels are assembly generated from C++ (asm/_cpp with Agner Fog's vectorclass/version2 submodule) compiled with -ffast-math according to the README Notes |
| **Adoption** | 204 stars |
| **Last commit** | 2025-09-06 |
| **Links** | [repository](https://github.com/viterin/vek) · [benchmark](https://github.com/viterin/vek) |

## Verdict

These are first-party go test benchmark numbers comparing each AVX2 kernel with the library's own pure-Go loop, on an unstated x86-64 CPU, Go version and run count (README table, probably from 2022). Examples at 100k elements: vek32.Sum 65,007 ns against 3,191 ns (20x), vek32.Exp 22x, vek.Add 2x, vek32.Add 6x. The largest ratios (And 139x, Exp 22x, Log 16x, Maximum 8x) come from branchy scalar baselines or from NaN and Inf-producing inputs, not from typical data.

## Use it when

- Go services on x86-64 servers with AVX2 and FMA (Haswell or Zen 1 and later) that do element-wise float32 math on slices of a few hundred elements or more.
- float32 transcendental-heavy work (exp, log, pow, sqrt over 10k to 100k element slices) that can accept VCL approximation error and has no NaN or Inf inputs.
- Reductions and scans in Go (Sum, Max, Find, Count, All, Dot), where the scalar loop is latency-bound or branchy.
- Mask-style data filtering (comparisons returning []bool, combined with And and Select), much like NumPy boolean indexing.
- Small and medium MatMul in pure-Go deployments with no cgo or BLAS; vek.MatMul splits rows across runtime.NumCPU goroutines.

## Skip it when

- Data that can contain NaN or Inf: the kernels are built with -Ofast, so results are undefined. Issue #11 showed Eq and Neq returning wrong counts with acceleration on, and that was documented, not fixed.
- ARM64 (Graviton, Apple silicon) or macOS: there are no NEON kernels, the maintainer said in issue #12 (Nov 2025) that none are planned, and acceleration is off by default on darwin.
- Very short slices (under about 8 to 16 elements): issue #6 measured Add on [4]float32 at 3.427 ns with SIMD against 2.174 ns in pure Go, a Ryzen 7 7840HS result.
- Integer vectors (only float32, float64 and bool are supported; the ints request in issue #13 was closed), and code that needs bit-for-bit agreement with math.Exp, Log or Pow.
- Serious dense linear algebra: MatMul is a naive i-k-j loop, not a blocked BLAS kernel, so use gonum with OpenBLAS or MKL for large matrices.

## How it is fast

Most kernels are the same plain C++ loops as the Go fallback, auto-vectorized by Clang with -Ofast -mfma -mavx2 -funroll-loops, then translated into Go assembly through avo with the repo's asm2avo.py. Exp, Log, Pow, Sin and Cos come from Agner Fog's Vector Class Library (vectormath_exp.h), as 8-lane float32 or 4-lane float64 polynomial approximations. Two things the Go compiler will not do account for most of the gain. -Ofast lets Clang reassociate reductions into several vector accumulators (Sum is a serial dependency chain in Go), and if-conversion turns branchy scalar code (&&, if y &gt; x) into branchless blends.

## Compared with alternatives

Pick vek over kelindar/simd or tphakala/simd when you want one NumPy-like float32/float64 API that also covers transcendental functions, boolean masks with Select, and MatMul; kelindar/simd's published tables cover integer element types (uint8/uint16/uint32), which vek does not support. Prefer a sibling if you need non-x86 acceleration or strict IEEE results, which vek does not provide.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/chewxy/math32, github.com/viterin/partial, golang.org/x/exp, golang.org/x/sys (testify for tests only); no cgo |
| **Minimum toolchain** | Go 1.19 (go.mod; generics). Builds on Go 1.21 and later only from the Aug 2023 partial v1.1.0 fix onward (issue #4). |
| **Platforms** | Accelerated on amd64 with AVX2 and FMA, except darwin, where acceleration is off by default. Any other GOARCH or OS falls back to pure Go. |
| **Thread safety** | Stateless functions are safe to call concurrently on disjoint slices. SetAcceleration writes a global flag and is documented 'Not thread safe'. _Inplace and _Into destinations must not overlap the other arguments. |
| **Drop-in for the baseline** | partial: it replaces hand-written Go loops over []float32 or []float64 with function calls of the same semantics, apart from fast-math precision and NaN or Inf behaviour. It is not a drop-in for math.Exp, math.Log or math.Pow results. |

## Gotchas

- Harness flaw in the transcendental rows: BenchmarkExpLog, BenchmarkPow and BenchmarkSqrt draw inputs from Random(), which is rand.NormFloat64()\*100. About half of the Log, Sqrt and Pow inputs are negative, which gives NaN; Pow uses non-integer exponents in [-10,10]. About 38% of the Exp inputs have |x| &gt; 88.7, which overflows to +Inf or underflows to 0 or a denormal. The README itself calls that regime undefined for the SIMD path. TestExpLog checks Exp only on [-10,10]. The scalar math32.Exp and math32.Log take data-dependent special-case branches on this input mix (math32.Exp tests float64 overflow limits, so the 88.7 to 709 range goes through its slow Ldexp path). The 22x Exp, 16x Log and 14x Pow numbers therefore come from inputs that are mostly invalid.
- Branchy baselines inflate two rows. And_Go is x[i] = x[i] && y[i], a short-circuit branch on random 50% bools, while the C++ kernel computes the bitwise x[i] & y[i]; that gap is the 139x. Maximum_Go is if y[i] &gt; x[i] on random normal data, about 5.4 ns per element at 100k against 0.58 ns for Add (derived from page data), so the 8x mostly measures branch mispredictions.
- The README's 1k column for Add, Mul, Abs, Round, Sqrt, Pow, Exp, Log, Maximum, Lt and And, and its p=1 MatMul rows, cannot be produced by the committed go test command. Those benchmarks loop over sizes[3:] (10k and 100k only, unchanged since the initial commit ff9d7ac), and BenchmarkMatMul uses only p of 100 or 1000. The README also does not say whether its MatMul rows are the serial or the goroutine-parallel variant. The p=1k SIMD rows imply about 96 GFLOP/s for f64 and 191 GFLOP/s for f32 (derived from page data), more than one core can reach with this i-k-j loop, so they are almost certainly the parallel paths.
- Correctness tests only cover lengths 1 to 200 (size = 1 + i/5), so the unrolled main loops that start past 256 elements are exercised only by benchmarks that never check results. That is how the Any() bug (stale RAX returned for len &gt; 256 with len % 32 &gt; 0) survived from 2022 until an outside PR fixed it in Aug 2025 (commit 0ce8425).

## Known shortcomings

- Benchmark code is public (internal/functions/\*_test.go) but no CPU or Go version is stated; kernels are built with -ffast-math (NaN and Inf undefined); the 139x And row is against a branchy short-circuit Go loop and the MatMul baseline is the package's own pure-Go loop. Go-only. Last commit 2025-09-06.
- Harness flaw: the Exp, Log, Pow and Sqrt benchmarks draw inputs from NormFloat64()\*100, so about 50% of the Log, Sqrt and Pow results are NaN and about 38% of the Exp inputs have |x| &gt; 88.7 (Inf, 0 or denormal), a regime the README calls undefined; TestExpLog checks only [-10, 10]. And_Go uses a short-circuit && on random bools against a bitwise & kernel (the 139x row), and Maximum_Go branch-mispredicts (the 8x row). The README 1k column (Add, Mul, Abs, Round, Sqrt, Pow, Exp, Log, Maximum, Lt, And) and the MatMul p = 1 rows cannot be produced from the committed harness (those benchmarks loop over 10k and 100k only since ff9d7ac; MatMul uses p 100 and 1000). Tests cover lengths 1-200 only, which hid the Any() bug at len &gt; 256 for three years; issue #11: Eq/Neq wrong on NaN, documented, not fixed.

## Caveats and trade-offs

CPU model, Go version and run count are not stated. The speedup column uses the 100k-element sizes; at 1k some gaps are smaller (vek.Add 484 vs 192 ns, vek.Maximum 1,000 vs 517 ns, vek.And 1,172 vs 60 ns, derived from page data). The 139x vek.And row compares against And_Go, a short-circuit loop 'x[i] = x[i] && y[i]' over random 50% booleans: a branchy worst case for a scalar baseline that a branchless Go loop would narrow. BenchmarkLogic clones the input under StopTimer on every iteration. The Go fallback Sum is a single-accumulator serial loop, and the SIMD kernels are built with -ffast-math, which allows reassociation, so results can differ slightly in precision and are undefined for NaN or Inf inputs (README Notes). The MatMul baseline is the library's own pure-Go loop, not gonum or a BLAS. Acceleration needs x86-64 AVX2 and FMA (no ARM path) and is off by default on macOS. An Any() bug (wrong result for len &gt; 256 and len % 32 &gt; 0, stale RAX in the generated assembly) was fixed in August 2025 (commit 0ce8425). It does not touch any benchmarked row. Last commit (2025-09-06) is a README note on fast math. [retier] CPU model, Go version and run count are not stated. Harness flaws: the transcendental benchmarks feed mostly invalid or out-of-range inputs (NaN and Inf regime), And_Go and Maximum_Go are branchy worst cases that a branchless Go loop would narrow, BenchmarkLogic clones the input under StopTimer on every iteration, the Go fallback Sum is a single-accumulator serial loop, and the 1k column and p = 1 MatMul rows have no producing command; the README does not say whether its MatMul rows are the serial or goroutine-parallel variant. Correctness tests cover lengths 1 to 200 only (size = 1 + i/5), so the unrolled main loops past 256 elements are exercised only by benchmarks that never check results, which is how the Any() bug (stale RAX returned for len &gt; 256 with len % 32 &gt; 0) survived from 2022 until commit 0ce8425 (August 2025); issue #11: Eq/Neq wrong on NaN, documented, not fixed. The AVX2 kernels are assembly generated from C++ (asm/_cpp with Agner Fog's VCL).

AVX2 and FMA on x86-64 only (acceleration disabled by default on macOS, no ARM kernels); behavior undefined on NaN or Inf inputs; minor precision differences from math.Exp, Pow and Log.

## Maintenance

Stale but MIT-licensed and small (19 commits, 204 stars). The last code fix was the Aug 2025 Any() patch, and the last commit (Sep 2025) added a README note on fast math. The maintainer still answers issues (Nov 2025) but has ruled out ARM64 SIMD. Dgraph, per cross-references on issue #12, replaced vek with in-tree SIMD distance kernels in 2026.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** The benchmark code is public (internal/functions/\*_test.go: BenchmarkSumProd, BenchmarkAdd, BenchmarkLogic and others, each running the \*_Go and \*_AVX2 variants), and the README gives the go test command, but neither the CPU model nor the Go version is stated, so the evidence falls short of A. These are first-party numbers, so tier C.
- **Verifier notes:** All claimed numbers appear in the README table (vek32.Sum 65,007 vs 3,191 ns 20x; vek32.Exp 22x; vek32.Log 16x; vek32.Add 6x; vek.Add 2x; MatMul 7x and 14x; vek.And 139x; Quantile 1x). The baseline is the library's own pure-Go fallback (plain Go loops), a reasonable stand-in for idiomatic Go. Shortcomings: Go, not C++; no CPU or Go version; fast-math semantics; the 139x And row is inflated by a branchy short-circuit baseline. Metadata checked: MIT, 204 stars, 19 commits, not a fork, last commit 2025-09-06 (stale).
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-60 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/viterin/vek>
  - <https://github.com/viterin/vek/commits>
  - <https://github.com/viterin/vek/tree/master/internal/functions>
  - <https://github.com/viterin/vek/commit/0ce8425>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/README.md>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/aggregates_test.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/boolean_test.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/arithmetic_test.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/boolean.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/aggregates.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/viterin/vek>
  - <https://github.com/viterin/vek/commits/master>
  - <https://github.com/viterin/vek/tree/master/internal/functions>
  - <https://github.com/viterin/vek/tree/master/asm>
  - <https://github.com/viterin/vek/tree/master/asm/_cpp>
  - <https://github.com/viterin/vek/commit/0ce8425>
  - <https://github.com/viterin/vek/issues?q=is%3Aissue>
  - <https://github.com/viterin/vek/issues/1>
  - <https://github.com/viterin/vek/issues/6>
  - <https://github.com/viterin/vek/issues/11>
  - <https://github.com/viterin/vek/issues/12>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/README.md>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/go.mod>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/vek.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/info.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/asm/README.md>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/asm/gen.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/asm/_cpp/special.cpp>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/asm/_cpp/aggregates.cpp>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/asm/_cpp/boolean.cpp>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/asm/_cpp/matrix.cpp>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/accel_amd64.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/random.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/arithmetic.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/arithmetic_test.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/aggregates.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/aggregates_test.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/boolean.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/boolean_test.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/comparison.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/max.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/max_test.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/find.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/find_test.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/special.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/special_test.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/matrix.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/matrix_test.go>
  - <https://raw.githubusercontent.com/viterin/vek/HEAD/internal/functions/construct_test.go>
  - <https://raw.githubusercontent.com/viterin/vek/ff9d7ac/internal/functions/aggregates_test.go>
  - <https://raw.githubusercontent.com/viterin/vek/ff9d7ac/internal/functions/arithmetic_test.go>
  - <https://raw.githubusercontent.com/chewxy/math32/master/exp.go>
  - <https://raw.githubusercontent.com/chewxy/math32/master/log.go>
  - <https://raw.githubusercontent.com/chewxy/math32/v1.10.1/ldexp.go>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/viterin/vek`) · [data/wave13/enrich/raw/github_com_viterin_vek.json](../../../data/wave13/enrich/raw/github_com_viterin_vek.json) (enrichment confidence 0.78)

</details>
