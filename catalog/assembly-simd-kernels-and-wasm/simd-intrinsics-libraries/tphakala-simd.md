# tphakala/simd

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `MIT` · 🟢 active

> Go assembly SIMD kernels (AVX-512/AVX2/AVX/SSE2, NEON) for slice math and audio DSP; 2-16x over the library's own pure-Go loops.

| | |
|---|---|
| **Beats** | pure-Go scalar loops (same binary with SIMD_DISABLE=all, or each operation's \*Go reference function) |
| **Claimed result** | README Performance Notes: 'Explicit SIMD ranges from roughly 2-6x on memory-bound elementwise operations up to 10-16x on reductions and fused kernels'. float64 on i7-1260P, 1024 elements: DotProduct 54 ns vs 887 ns (16.5x), EuclideanDistance 15.4x, Mean 12.7x, Sum 12.1x, Clamp 10.6x, Add 2.4x, Div 2.0x, CumulativeSum 1.0x. ARM64 NEON: float32 3.5x-5.2x, float64 2.4x-2.6x. Activation functions: Exp 19x for f32; the README's 'Tanh: 73x speedup for f32' rests on an inconsistent Go baseline row (tanh32Go is float32(math.Tanh(float64(x))) on the same inputs as the f64 row, yet 28,219 ns against the f64 row's 6,600 ns while the Sigmoid and Exp rows agree within about 10% across widths), so against the f64 baseline the f32 kernel's 385 ns is about 17x (derived from page data). |
| **Workload** | Vectorized slice math (arithmetic, reductions, statistics, distances, activation functions, int8/int16/int32 DSP) on 1024-element float64 and float32 slices, SIMD path versus pure Go, on x86-64 AVX+FMA and ARM64 NEON. |
| **Metric** | throughput |
| **Hardware** | Intel Core i7-1260P (AVX+FMA) and Raspberry Pi 5 (Cortex-A76, NEON) |
| **Compiler and flags** | Go 1.26 toolchain (go.mod minimum 1.25); 'task bench' and 'task bench:compare'; performance CPU governor; best of repeated runs; Variance/StdDev rows re-measured as medians of 9 rounds pinned to one P-core |
| **Adoption** | 26 stars |
| **Last commit** | 2026-10-05 |
| **Links** | [repository](https://github.com/tphakala/simd) · [benchmark](https://github.com/tphakala/simd) |

## Verdict

The README's go test benchmarks (Go 1.26, performance governor, best of repeated runs) time each kernel against the library's own pure-Go reference at 1,024 elements. On an Intel Core i7-1260P (AVX+FMA, no AVX-512) the results are float64 DotProduct 54 vs 887 ns (16.5x), Sum 12.1x, Mean 12.7x, EuclideanDistance 15.4x, Clamp 10.6x, elementwise Add/Sub/Mul 2.4x, Div 2.0x and CumulativeSum 1.0x; float32 is 3.2-22.6x. On a Raspberry Pi 5 (Cortex-A76 NEON) f32 is 3.5-5.2x and f64 2.4-2.6x. Reduction gains are inflated by single-accumulator scalar baselines, and the 73x f32 Tanh row's Go figure is inconsistent with the f64 row for the same math.Tanh calls.

## Use it when

- Go services doing numeric work on float32/float64 slices of a few hundred elements or more (dot products, sums, means, L2 distances, clamps) on amd64 or arm64, where cgo to a C SIMD library is unwanted.
- Go audio and DSP pipelines: FIR filtering and decimation, LPC autocorrelation for FLAC-style encoders (byte-identical to the scalar reference), int16/int32 PCM conversion and interleave, CRC-16, STFT and power spectra.
- Raspberry Pi 5 / Cortex-A76 and Apple Silicon deployments: NEON kernels throughout (README: f32 3.5-5.2x, f64 2.4-2.6x over pure Go on a Pi 5), with FP16 paths in f16.
- Fixed-point codec inner loops (i16 DotProduct at 64-480 elements: 5.8-11.8x on AVX2; XCorr 27-33x), where the README documents bit-exact results.
- Batch ML-style activations (Sigmoid, Exp, Tanh) on float32 where an absolute error around 1e-6 to 1e-7 is acceptable.

## Skip it when

- Very short slices: i16 DotProduct at 8 elements is only 1.5x on AMD64 and 0.97x on the Pi 5, Min/Max/MaxAbs fall back to Go below 4 (f64) or 8 (f32) elements, and per-call dispatch dominates tiny inputs.
- Code that needs results bit-identical to a scalar loop for float reductions (Sum, DotProduct, Variance): lanes reassociate the additions, and the repo's own bench:compare only checks agreement within a tolerance. Bit-exactness is documented only for Autocorrelate, ConvolveValidMaxAbs and the integer kernels.
- Accuracy-sensitive transcendentals: Tanh, Sigmoid and Exp use approximations (Exp max relative error about 7e-6 for f32), and Tanh loses relative accuracy for inputs near zero (see gotchas). Use math.Tanh/math.Exp when relative error matters.
- Other architectures (riscv64, ppc64le, s390x, wasm) get only the pure-Go fallback; SVE/SVE2 is detected but unused, so Graviton 3 runs NEON.
- Projects needing broad adoption or a long track record: 26 stars, one main author, API still growing fast (functions added and removed in 2026, e.g. PolyphaseResampleCubic added then dropped in August).

## How it is fast

Hand-written Go-assembler kernels process 2-16 lanes per instruction and run several independent vector accumulators in the reductions, so DotProduct and Sum escape the one-add-at-a-time dependency chain of a scalar loop (Go's compiler does not auto-vectorize). At package init, CPU-feature detection selects function pointers per tier (AVX-512 F+VL, AVX2, AVX+FMA, AVX, SSE2, NEON, NEON+FP16, SDOT, AVX-VNNI, PCLMULQDQ/PMULL), and the SIMD_DISABLE environment variable can mask tiers. Activation and transcendental kernels swap math.Exp/math.Tanh for range reduction plus a degree-5 polynomial and 2^k reconstruction with integer shifts. Fused kernels (ConvolveDecimate, ConvolveValidMaxAbs, DotProductBatch's 4-row blocking, XCorr's 4-lag blocking) remove per-call dispatch and repeated loads.

## Compared with alternatives

Pick it over kelindar/simd, vek or segmentio/asm when you need float64 and float32 coverage plus audio/DSP kernels (FIR, decimation, LPC autocorrelation, STFT, PCM conversion, CRC-16) with NEON tuned and measured on ARM64, in an actively developed module. Like those siblings, its speedups are measured only against its own pure-Go fallback.

## Integration

| | |
|---|---|
| **Form** | Go module (pure Go plus Go assembler .s files; no cgo) |
| **Dependencies** | golang.org/x/sys and golang.org/x/arch (go.mod); stretchr/testify for tests only |
| **Minimum toolchain** | Go 1.25 (go.mod); README numbers measured with Go 1.26 |
| **Platforms** | amd64 (SSE2 minimum for f32/f64/c128; AVX2 for i8, i32 arithmetic and the activation kernels; AVX-512 F+VL used when present) and arm64 (NEON, optional FP16, SDOT); pure-Go fallback elsewhere |
| **Thread safety** | README: all functions are safe for concurrent use (stateless kernels; dispatch fixed at package init). STFTPlan is a reusable plan object; its concurrent use is not documented here. |
| **Drop-in for the baseline** | partial: replaces hand-written Go loops one call at a time with the same slice-in, slice-out semantics, but floating-point results can differ in the last bits (reassociation) or more (approximate activations) |

## Gotchas

- The '73x' f32 Tanh headline rests on an inconsistent baseline row. tanh32Go is float32(math.Tanh(float64(x))), and BenchmarkTanh feeds both packages the same (i%100 + 0.5 - 50)/10 inputs. The f32 Go time (28,219 ns) is still 4.3x the f64 Go time (6,600 ns) for the same math.Tanh calls, while the Sigmoid and Exp Go rows agree across f32 and f64 within about 10%. At the f64 baseline the f32 kernel's 385 ns would be about 17x, not 73x (derived from page data); the row is probably from a different run or an older reference.
- The f32 AVX2 Tanh kernel (tanhAVX) computes (1 - e^(-2x)) / (1 + e^(-2x)) with a truncated-Taylor exp, so relative error grows as |x| approaches 0 through cancellation in 1 - e^(-2x). By that arithmetic it exceeds the test's own 1e-5 bound below roughly |x| = 0.003 and returns 0 once e^(-2x) rounds to 1.0. TestTanh checks only 0, integers and 2.5 (analysis of the kernel code, not measured). The Tanh doc comments in f32.go and f64.go still describe an older 'x/(1+|x|) ... sign(x) for |x| &gt;= 2.5' approximation, and the f64_go.go comment wrongly says tanh(2.5) saturates to 1 (it is 0.987).
- The reduction baselines are latency-bound single-accumulator loops: dotProductGo chains math.FMA into one sum, and sumGo is 'sum += v'. The table's Go times match one FMA per about 4 cycles (887 ns per 1024 elements) and one add per about 2 cycles (427 ns) at the i7-1260P's turbo clock, so a 4-accumulator scalar loop would likely recover about 4x of DotProduct's 16.5x (estimate, not measured). Clamp's Go reference is an if/else branch chain costing about 4x Add's Go loop per element, so its 10.6x is mostly a branchy-baseline effect.
- Benchmark inputs are a deterministic period-100 ramp (i%100 + 0.5), and the i7-1260P is a hybrid P/E-core part. Only the Variance/StdDev rows were pinned to one P-core (median of 9); the other rows are best-of-repeated-runs without stated pinning, and the f32 table mixes runs. The f64 ReLU row's 240 GB/s does not match its 79 ns (about 207 GB/s from 16 KB moved).

## Known shortcomings

- Only baseline is its own pure-Go loops; the reduction loops use a single accumulator, which inflates the 12-16x wins; Tanh 73x and Exp 19x compare an approximation against exact math. Go-only.
- The '73x' f32 Tanh headline rests on an inconsistent Go row: tanh32Go is float32(math.Tanh(float64)) on the same inputs as f64, yet it takes 28,219 ns against the f64 Go row's 6,600 ns while the Sigmoid and Exp rows agree within 10% across widths; at the f64 baseline the f32 kernel is about 17x (derived). tanhAVX computes (1 - e^-2x)/(1 + e^-2x) with a Taylor exp, so its relative error passes 1e-5 only above about |x| = 0.003 and it returns 0 near zero; TestTanh checks only 0, integers and 2.5; the Tanh doc comments are stale. The reduction and Clamp baselines are latency-bound single-accumulator or branchy loops, so about 4x of DotProduct's 16.5x is likely recoverable by a scalar multi-accumulator loop (estimate); the f64 ReLU row's 240 GB/s does not match its 79 ns (about 207 GB/s derived); unpinned hybrid CPU with mixed runs.

## Caveats and trade-offs

Baseline is the library's own pure-Go loop, and the README notes Go 1.26 generates tighter scalar loops than older toolchains, shrinking elementwise gains. The reduction references are single-accumulator serial loops (f64/f64_go.go: dotProductGo chains math.FMA into one sum even though unrolled by 4; sumGo is a plain 'sum += v' loop), so they are latency-bound and part of the 12-16x reduction speedups comes from breaking that dependency chain, which a multi-accumulator scalar loop would also get; Go's compiler does not auto-vectorize. The 73x Tanh and 19x Exp figures compare a fast approximation (max relative error about 7e-6 for f32) with the exact math.Tanh and math.Exp. The float32 table mixes runs (Variance/StdDev re-measured after fix #214 under a median-of-9 protocol, other rows from one earlier run) and its Variance/StdDev Go figures come from SIMD_DISABLE=all because those benchmarks have no Go sub-benchmark. Exact Go patch version not stated. Hardware is two consumer machines; comparisons shown are against the pure-Go path only, not another Go SIMD library or a C/C++ SIMD library. [retier] Baseline is the library's own pure-Go loop (Go 1.26 toolchain, no auto-vectorization); the README notes newer toolchains shrink elementwise gains. The reduction references are latency-bound single-accumulator loops (dotProductGo chains math.FMA into one sum; sumGo is a plain 'sum += v' loop), so part of the 12-16x reduction speedups comes from breaking that dependency chain, and a 4-accumulator scalar loop would likely recover about 4x of DotProduct's 16.5x (estimate); Clamp's Go reference is branchy. The f32 Tanh row is inconsistent (see claim), and the f32 AVX2 tanh kernel computes (1 - e^-2x)/(1 + e^-2x) with a truncated-Taylor exp, so its relative error exceeds the test's own 1e-5 bound below roughly |x| = 0.003 and it returns 0 once e^-2x rounds to 1.0; TestTanh checks only 0, integers and 2.5, and the Tanh doc comments are stale. Benchmark inputs are a deterministic period-100 ramp on a hybrid P/E-core i7-1260P; only the Variance/StdDev rows were pinned to one P-core (median of 9), the other rows are best-of-repeated-runs without stated pinning, and the f32 table mixes runs. The f64 ReLU row's 240 GB/s does not match its 79 ns (about 207 GB/s from 16 KB moved, derived).

Pure Go assembly (Go assembler, no cgo); AVX-512, AVX+FMA, AVX, SSE2, NEON, NEON+FP16 tiers with runtime detection; amd64 minimum tier differs per package; ARM64 and x86-64 only, pure Go fallback elsewhere; approximate transcendental functions.

## Maintenance

Active (commits through 2026-10-05, 291 commits, issues closed within days) and MIT-licensed, so it is easy to adopt. It has 26 stars and its main known consumer is the author's own BirdNET-Go, and the README's headline multiples should be discounted for the self-written scalar baselines and the Tanh row.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** README Performance section compares each SIMD kernel with its pure-Go scalar reference using public benchmarks (f64/benchmark_test.go and the other packages' benchmark tests, run via Taskfile.yml 'task bench' = go test -bench=. -benchmem), and states the Go 1.26 toolchain, performance governor, best-of-repeated-runs protocol and CPU models (Intel Core i7-1260P, Raspberry Pi 5 Cortex-A76).
- **Verifier notes:** All quoted figures appear in README Performance (DotProduct 54 vs 887 ns 16.5x, EuclideanDistance 15.4x, Mean 12.7x, Sum 12.1x, Clamp 10.6x, Add 2.4x, Div 2.0x, CumulativeSum 1.0x, NEON f32 3.5-5.2x and f64 2.4-2.6x, Tanh 73x, Exp 19x) and in Performance Notes. Shortcomings: self-written scalar baseline with single-accumulator reductions, approximation-vs-exact activation rows, Go not C++, 26 stars. Metadata verified: MIT, last commit 2026-10-05, active, not a fork.
- **Fields the verifier corrected:** `caveats`, `claimed_speedup`
- **Shortcomings recorded by:** verifier batch-57 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/tphakala/simd>
  - <https://github.com/tphakala/simd/commits>
  - <https://github.com/tphakala/simd/blob/main/README.md>
  - <https://github.com/tphakala/simd/blob/main/LICENSE>
  - <https://github.com/tphakala/simd/blob/main/Taskfile.yml>
  - <https://github.com/tphakala/simd/tree/main/f64>
  - <https://github.com/tphakala/simd/blob/main/f64/benchmark_test.go>
  - <https://github.com/tphakala/simd/blob/main/f64/f64_go.go>
- **Sources the enricher read:**
  - <https://github.com/tphakala/simd>
  - <https://github.com/tphakala/simd/tree/main/f64>
  - <https://github.com/tphakala/simd/tree/main/f32>
  - <https://github.com/tphakala/simd/commits/main/f32/f32_go.go>
  - <https://github.com/tphakala/simd/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/tphakala/simd/main/README.md>
  - <https://raw.githubusercontent.com/tphakala/simd/main/go.mod>
  - <https://raw.githubusercontent.com/tphakala/simd/main/Taskfile.yml>
  - <https://raw.githubusercontent.com/tphakala/simd/main/LICENSE>
  - <https://raw.githubusercontent.com/tphakala/simd/main/f64/f64.go>
  - <https://raw.githubusercontent.com/tphakala/simd/main/f64/f64_go.go>
  - <https://raw.githubusercontent.com/tphakala/simd/main/f64/f64_amd64.go>
  - <https://raw.githubusercontent.com/tphakala/simd/main/f64/f64_amd64.s>
  - <https://raw.githubusercontent.com/tphakala/simd/main/f64/benchmark_test.go>
  - <https://raw.githubusercontent.com/tphakala/simd/main/f64/f64_test.go>
  - <https://raw.githubusercontent.com/tphakala/simd/main/f32/f32.go>
  - <https://raw.githubusercontent.com/tphakala/simd/main/f32/f32_go.go>
  - <https://raw.githubusercontent.com/tphakala/simd/main/f32/f32_amd64.go>
  - <https://raw.githubusercontent.com/tphakala/simd/main/f32/f32_amd64.s>
  - <https://raw.githubusercontent.com/tphakala/simd/main/f32/benchmark_test.go>
  - <https://raw.githubusercontent.com/tphakala/simd/main/f32/f32_test.go>
  - <https://raw.githubusercontent.com/tphakala/birdnet-go/main/go.mod>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/tphakala/simd`) · [data/wave13/enrich/raw/github_com_tphakala_simd.json](../../../data/wave13/enrich/raw/github_com_tphakala_simd.json) (enrichment confidence 0.75)

</details>
