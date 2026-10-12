# go-fft

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Go` · `BSD-3-Clause` · 🟢 active

> Pure-Go (no cgo) float64 FFT for any length; fastest pure-Go option, behind FFTW on most single-core 1-D sizes.

| | |
|---|---|
| **Beats** | FFTW 3.3.11 (native C, FFTW_MEASURE, threads=1); also numpy.fft, scipy.fft (pocketfft) and gonum/dsp/fourier |
| **Claimed result** | June snapshot tables (Apple M4 Max), go-fft vs FFTW: lags FFTW 1.17x to 3.28x on complex 1-D rows (e.g. N=1,024 3,395 ns vs 2,127 ns); faster only on the 2-D multicore rows: 256x256 208,437 ns vs 271,098 ns; 512x512 633,920 ns vs 1,247,215 ns; 1024x1024 2,784,623 ns vs 6,301,688 ns. Vs scipy.fft (pocketfft) complex 1-D: N=256 716 ns vs 2,302 ns; N=1,024 3,395 ns vs 4,470 ns; N=65,536 377,784 ns vs 499,500 ns (slower at N=1,048,576: 13.36 ms vs 8.04 ms). Summary of that snapshot: at or above parity with FFTW on 3 of 24 ops and with gonum on 19 of 19; 'typically 3-5x on composite N' faster than gonum. Fresh single-threaded 1-D runs of 2026-09-30 (go-fft time / FFTW time, below 1 = go-fft faster): complex 2^20 0.81 on M4 Max and 0.67 on Neoverse-N1; prime 1009 0.53 (M4 Max), 0.75 (EPYC 7773X), 0.54 (Neoverse-N1); RFFT 2^20 0.92 on Neoverse-N1; complex 65536 1.00 on Neoverse-N1; most other 1-D rows still lag 1.07x to 2.92x; 2-D 512^2/1024^2 multicore 0.43/0.45 (M4 Max), 1.63/0.87 (EPYC 7773X), 0.51/0.25 (Neoverse-N1). |
| **Workload** | Steady-state (plan reused) complex 1-D, real 1-D and complex 2-D FFTs in float64 on an Apple M4 Max, ns/op and GFLOP/s, with go-fft's 2-D path using several goroutines and every reference single-threaded. |
| **Metric** | latency |
| **Hardware** | Apple M4 Max (12P+4E), macOS 26.5, for the main tables; fresh 2026-09-30 runs also on AMD EPYC 7773X (Zen 3, GCC Compile Farm cfarm420, 128 threads) and ARM Neoverse-N1 (cfarm424, 64 cores) |
| **Compiler and flags** | go1.26.4 (CGO=0 pure Go; cross-compiled for the Linux hosts), go test -benchtime=1s; FFTW 3.3.11 Homebrew arm64 bottle with NEON on the M4 Max and FFTW 3.3.10 built from source with SSE2/AVX/AVX2/FMA (Zen 3) or NEON (N1) on the Linux hosts, plans FFTW_MEASURE threads=1 from a C harness; numpy 2.5.0 and scipy 1.18.0 pinned single-threaded (2.5.3 / 1.18.1 on the Linux hosts) |
| **Adoption** | 1 star, 1 fork, 48 commits |
| **Last commit** | 2026-10-01 |
| **Links** | [repository](https://github.com/go-fft/fft) · [benchmark](https://github.com/go-fft/fft/blob/main/BENCHMARKS.md) |

## Verdict

The author's public harness (benchmarks/run.sh plus a C FFTW driver) times steady-state float64 transforms with reused plans against FFTW 3.3.11 (Homebrew NEON, FFTW_MEASURE, one thread) on an Apple M4 Max and FFTW 3.3.10 built from source on an EPYC 7773X (Zen 3) and Neoverse-N1, with go1.26.4. In the June snapshot go-fft beat FFTW only on the 512x512 and 1024x1024 2-D rows, where it used all cores against single-threaded FFTW; the 2026-09-30 runs add single-threaded wins at complex 2^20 (0.81x on M4 Max, 0.67x on N1), prime 1009 on all three hosts (0.53x-0.75x) and RFFT 2^20 on N1 (0.92x), with most other 1-D rows 1.07x-2.92x slower than FFTW.

## Use it when

- Go programs that need FFTs with CGO_ENABLED=0 (static or cross-compiled binaries on amd64, arm64, riscv64, ppc64le, loong64 or s390x) and cannot link FFTW
- Replacing gonum/dsp/fourier: faster at every size measured, typically 3-5x on composite N and 30x-200x on primes, where gonum uses a naive Bluestein
- Large 2-D double-precision transforms (512x512 and up) on a multicore host, where its goroutine fan-out beat single-threaded FFTW (0.43-0.51x FFTW's time on M4 Max, 0.25x at 1024x1024 on Neoverse-N1)
- Workloads that create many plans or use many distinct lengths: NewPlan at N=1,024 cost 14,808 ns vs 3,434,000 ns for an FFTW_MEASURE plan
- Code that needs bit-reproducible results across amd64 builds: the SIMD kernels avoid FMA and are tested bit-identical to the scalar Go path

## Skip it when

- C++ projects: it is a Go module, so FFTW, PocketFFT, KFR or Admiral are the native choices
- Single-core 1-D throughput against FFTW: in the fresh 2026-09-30 runs most 1-D rows still take 1.07x-2.92x FFTW's time, especially on Zen 3, where FFTW uses AVX2+FMA codelets and go-fft deliberately skips FMA
- Single precision: only complex128/float64 is supported
- Small 2-D shapes (64x64, 128x128): they ran 1.39x-3.20x slower than FFTW in the June snapshot, and on 64-128-thread hosts the GC cost of FFT2/FFTN's freshly allocated result slice dominates
- Teams that need a stable API: there is no tagged release, the repo started in June 2026, and an allocation-free N-D entry point is still an open design decision

## How it is fast

Lengths whose prime factors are all &lt;= 13 run an iterative Stockham autosort engine modelled on pocketfft's passes (radix 8/4/2/3/5/7 straight-line passes, a general pass for 11 and 13, unit-stride inner loops, no bit-reversal, bounds-check-free loops). Large powers of two use an iterative radix-4 kernel; primes whose N-1 is 7-smooth use Rader's algorithm, and other lengths use Bluestein's chirp-z at a cost-model-chosen smooth convolution length. On amd64 the butterfly, Stockham pass and real-FFT untangle kernels are generated AVX2/SSE2 assembly (via go-asmgen) picked at run time; on arm64 the gc autovectorizer is used. Real transforms pack N reals into an N/2-point complex FFT, and 2-D/N-D transforms fan rows and columns across goroutines.

## Compared with alternatives

Pick it only when you are writing Go and must stay cgo-free; among the catalogued FFTs, PocketFFT, KFR and Admiral are the C++ choices, and RustFFT/PhastFT play the same role for Rust that go-fft plays for Go.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (the library module has no dependencies; gonum is isolated in the separate benchmarks/ module) |
| **Minimum toolchain** | Go 1.26.4 (go.mod) |
| **Platforms** | any Go 64-bit target; SIMD on amd64 (SSE2 baseline, AVX2 when CPU and OS allow, chosen at run time); arm64 relies on autovectorized Go; riscv64/s390x have only a SIMD complex-multiply kernel; ppc64le/loong64 run scalar code |
| **Thread safety** | Plans are immutable after construction and safe for concurrent use by multiple goroutines (plan.go); per-call scratch comes from a sync.Pool; the package-level functions share an internal plan cache |
| **Drop-in for the baseline** | no |

## Gotchas

- Plan.FFT/IFFT require dst and src to be exactly Len() long (behaviour on a wrong length is not documented), and FFT2/FFTN panic when the shape product does not equal len(data)
- The package-level FFT, RFFT, FFT2 and FFTN allocate a new output slice on every call; use NewPlan/NewRealPlan for zero-allocation steady state (only 1-D has a dst-taking API)
- On amd64 the AVX2 path keeps separately rounded multiply and add (no FMA) to stay bit-identical to the scalar code, which costs speed against FMA-using libraries
- The README status paragraph still describes 'radix-2 Cooley-Tukey plus Bluestein', while its Performance section and BENCHMARKS.md describe the newer Stockham/Rader engines; the README tables are the June snapshot

## Known shortcomings

- 2-D wins are multicore against single-thread baselines; 1-D single-thread wins only at a few sizes (runs dated 2026-09-30); Go, not callable from C++.
- README's 'wins outright' at small N holds only vs pocketfft through Python; FFTW is faster there (N=256: 0.42 vs 0.72 us); float64 only.

## Caveats and trade-offs

Pure Go library, not callable from C++ without cgo; listed for the FFTW comparison. In the June M4 Max snapshot it does not beat FFTW on any single-threaded row; the fresh 2026-09-30 runs show single-threaded wins only at a few sizes (complex 2^20 on M4 Max and Neoverse-N1, prime N=1009 on all three hosts, RFFT 2^20 on N1), while most 1-D rows still lag FFTW by 1.07x to 2.92x and the M4 Max run was under background load (load average 3.4-5). The 2-D wins come from go-fft fanning rows and columns across goroutines while FFTW, numpy and scipy run single-threaded, so the 2-D comparison is not apples-to-apples; the 2-D fresh rows also predate a fan-out fix. FFT2/FFTN return a newly allocated slice, which the report says skews 2-D comparisons against FFTW on many-core hosts via GC cost. The README attributes part of the scipy gap at small N to Python FFI overhead, so the scipy comparison there is not like-for-like. The README tables still show the June snapshot. Very young repository (oldest commit on the first commits page 2026-06-20).

Pure Go with no cgo, so not callable from C++ without a wrapper. Arbitrary lengths: mixed radix for 13-smooth lengths, Rader for primes whose N-1 is 7-smooth, large-prime convolution otherwise (BENCHMARKS.md shows FFTW ahead at primes 1,009 and 10,007 by 1.26x and 2.15x). AVX2 and NEON SIMD butterflies. Plan creation is far cheaper than FFTW_MEASURE (e.g. 14,808 ns vs 3,434,000 ns at N=1,024).

## Maintenance

Very active single-org project (48 commits from 2026-06-20 to 2026-10-01, 1 star, no releases); BSD-3-Clause, so easy to vendor in Go, but young and with no external users visible.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** BENCHMARKS.md is regenerated by public code (benchmarks/run.sh, benchmarks/cbench/fftw_bench.c, Go benchmarks) and states go1.26.4, FFTW 3.3.11 Homebrew NEON bottle with FFTW_MEASURE threads=1, and Apple M4 Max; the 2026-09-30 fresh runs add EPYC 7773X and Neoverse-N1 with FFTW 3.3.10 built from source, raw data in benchmarks/results/.
- **Verifier notes:** June-snapshot numbers in the record match BENCHMARKS.md, but the file now also carries fresh 2026-09-30 three-host runs in which go-fft beats single-threaded FFTW at a few 1-D sizes, so the record's 'not faster than FFTW in 1-D' line was outdated and is corrected. Language is Go, so this is out of the C++ catalog's core scope; the orchestrator may prefer to file it as off-language.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `compiler_and_flags`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/go-fft/fft>
  - <https://github.com/go-fft/fft/commits/main>
  - <https://raw.githubusercontent.com/go-fft/fft/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/go-fft/fft/HEAD/README.md>
  - <https://raw.githubusercontent.com/go-fft/fft/HEAD/benchmarks/results/README.md>
- **Sources the enricher read:**
  - <https://github.com/go-fft/fft>
  - <https://github.com/go-fft/fft/issues?q=is%3Aissue>
  - <https://github.com/go-fft/fft/commits/main>
  - <https://raw.githubusercontent.com/go-fft/fft/HEAD/README.md>
  - <https://raw.githubusercontent.com/go-fft/fft/HEAD/BENCHMARKS.md>
  - <https://raw.githubusercontent.com/go-fft/fft/HEAD/go.mod>
  - <https://raw.githubusercontent.com/go-fft/fft/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/go-fft/fft/HEAD/benchmarks/results/README.md>
  - <https://raw.githubusercontent.com/go-fft/fft/HEAD/benchmarks/run.sh>
  - <https://raw.githubusercontent.com/go-fft/fft/HEAD/benchmarks/cbench/fftw_bench.c>
  - <https://raw.githubusercontent.com/go-fft/fft/HEAD/plan.go>
  - <https://raw.githubusercontent.com/go-fft/fft/HEAD/fft.go>
  - <https://raw.githubusercontent.com/go-fft/fft/HEAD/stockham.go>
  - <https://raw.githubusercontent.com/go-fft/fft/HEAD/route_amd64.go>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/go-fft/fft`) · [data/wave8/enrich/raw/github_com_go_fft_fft.json](../../../data/wave8/enrich/raw/github_com_go_fft_fft.json) (enrichment confidence 0.8)

</details>
