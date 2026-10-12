# Notorious-FFT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🟢 active

> Header-only C FFT with an FFTW-shaped API and minfft-style split-radix core; 8-13% faster than minfft on ARM, far behind FFTW.

| | |
|---|---|
| **Beats** | minfft (aimukhin/minfft, small power-of-two FFT library; not one of the listed incumbents) |
| **Claimed result** | README: v1.0.0 beats minfft by 1.08-1.13x on complex forward DFT for N&gt;=256 (N=1024 13.86 us vs 15.23 us; N=4096 68.95 us vs 77.59 us); inverse up to 1.18x at N=4096; real DFT 1.01-1.07x for N&gt;=256; N=16 tied (0.97x); slightly slower at some small real sizes (0.83x at N=16). |
| **Workload** | Forward and inverse complex DFT, real DFT and DCT-2 in double precision at N=16 to 65536, built with the repo's bench target. |
| **Metric** | latency |
| **Hardware** | ARM Cortex-A78AE (Jetson Orin) |
| **Compiler and flags** | GCC 11.4.0 -O3 -march=armv8.2-a+fp16, double precision |
| **Adoption** | 0 stars |
| **Last commit** | 2026-08-22 |
| **Links** | [repository](https://github.com/NotoriousLOB/Notorious-FFT) · [benchmark](https://raw.githubusercontent.com/NotoriousLOB/Notorious-FFT/HEAD/README.md) |

## Verdict

The repository's bench.c times notoriousfft against minfft in one binary (CLOCK_MONOTONIC, two warm-up calls, one timed batch of 500-100,000 repetitions per size, minfft run first), built with GCC 11.4.0 -O3 for armv8.2-a on a Jetson Orin Cortex-A78AE in double precision. v1.0.0 was 1.08-1.13x faster on forward complex DFT for N &gt;= 256 (N=4096: 68.95 us vs 77.59 us), up to 1.18x on inverse, 1.01-1.07x on real DFT, and slightly slower at N=16 for real DFT and DCT-2; with a single timed batch, margins under \~5% are within run-to-run noise.

## Use it when

- You already use minfft and want a near drop-in with more transform types and arbitrary lengths: same aux-object calling style, 1.08-1.13x faster complex DFTs at N &gt;= 256 on a Cortex-A78AE
- Embedded or edge aarch64 (Jetson-class) code that wants one MIT header with no dependencies beyond libc and libm
- Prototyping against an FFTW-like API with a permissive license, for a subset of FFTW calls, when FFTW-level speed is not required
- Small DCT-2/3/4 or DST-2/3/4 transforms where a header-only implementation is more convenient than linking a library

## Skip it when

- As an FFTW replacement for speed: in the author's FastAndFourier benchmarks on an x86 AVX2 Mac (Feb 2026, older build, one run, -ffast-math) it ran at 0.57-0.76x of KissFFT's throughput and 10x-30x slower than FFTW_MEASURE (e.g. N=1024 45.7 us vs 1.79 us; ratios derived from page data)
- x86 users who need published numbers: only an ARM Cortex-A78AE table exists for this repository; the AVX2/AVX-512 paths have no results
- Small real transforms and DCT-2 at N=16-64, where it was 0.83-0.97x of minfft's speed
- Projects needing a mature dependency: 7 commits, 0 stars, no releases on GitHub, and a Bluestein AVX inverse bug fixed only on 2026-08-22, after v1.0.0
- Calling one plan from several threads at once: plans own scratch buffers, so concurrent execute on the same plan is unsupported

## How it is fast

Powers of two use a recursive split-radix 2/4 decimation-in-frequency kernel with unrolled terminals for N &lt;= 32 and no bit-reversal pass; header comments say it uses the same structure and twiddle layout as minfft's rs_dft_1d. Under MEASURE planning it may instead pick a DIT combine or iterative Cooley-Tukey, and it switches to a four-step algorithm at N &gt;= 2^20. Factors 3/5/7 are peeled by mixed-radix passes, primes with 7-smooth N-1 use Rader, and other lengths use Bluestein. Compile-time NEON, AVX2 and AVX-512 paths exist (the README's summary lists NEON for f64 and f32, AVX2 for the inverse and AVX-512 for the forward transform), and each plan's memory is one 64-byte-aligned slab.

## Compared with alternatives

Pick it over minfft when you want the same small-library style plus non-power-of-two sizes, DCT/DST variants and an FFTW-like planner; for speed, PocketFFT, PFFFT or muFFT are better-measured permissive choices, and FFTW was 10x-30x faster on x86 in the author's own sibling benchmark.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none at runtime (libc, libm); OpenMP optional and switched on by default in the CMake build; the bundled tests and benchmarks fetch minfft (master) via FetchContent; Python 3 is needed by CMake to regenerate the amalgamated header |
| **Minimum toolchain** | C11 (C++17 for the C++ wrapper and tests), CMake 3.14+ |
| **Platforms** | any C11 target with a scalar path; NEON on aarch64/ARMv7, AVX2+FMA or AVX-512F/DQ on x86-64, all chosen at compile time from compiler flags (no runtime dispatch) |
| **Thread safety** | Documented: concurrent execute on the same plan is not supported (plans own scratch); distinct plans may run in parallel |
| **Drop-in for the baseline** | partial — notorious_fft_fftw.h aliases a subset of the FFTW3 API by macro (no wisdom, no guru interface, plan_many_dft fully only for rank 1), and must not be combined with linking libfftw3 in the same translation unit |

## Gotchas

- Precision is a build-wide switch: in the FFTW compatibility header fftwf_complex is typedef'd to the same type as fftw_complex, so float and double FFTW code cannot coexist in one build
- NOTORIOUS_FFT_FAST_MATH swaps in Bhaskara I sin/cos approximations with \~0.1% twiddle error that grows with N; the README also warns against -ffast-math
- Multi-dimensional c2r / invrealdft may overwrite its input
- CMake regenerates include/notorious_fft.h in the source tree from the src/ modules whenever they change, and the published minfft comparison builds against minfft master without a pinned commit

## Known shortcomings

- Only baseline is minfft, and its core is minfft-compatible without crediting minfft; the FAF README shows it slower than KissFFT on x86 AVX2 (0.57-0.76x), faster only on aarch64.
- bench.c times one batch per library with minfft always first and no interleaving, so the 1-13% margins are fragile; minfft fetched at unpinned master; the author's FastAndFourier x86 table shows it 10-30x slower than FFTW_MEASURE (older build).

## Caveats and trade-offs

Baseline minfft is a small niche library (53 stars), not FFTW, MKL or KissFFT; margins are 8-13% on complex DFT and 1-7% on real DFT, with losses at N=16-64 for real DFT and DCT-2. Only an ARM machine is measured; the AVX2/AVX-512 paths have no published numbers. The README names a comprehensive benchmark against FFTW3, KissFFT, PocketFFT and muFFT but publishes no results. The core is minfft-compatible (header comments: same split-radix 2/4 structure and twiddle layout as minfft's rs_dft_1d); the README does not credit minfft. The same author's FastAndFourier benchmarks/README.md gives two KissFFT comparisons: on an x86_64 AVX2 Mac (2026-02-22, older build) Notorious-FFT was slower than KissFFT at every size (0.57-0.76x relative throughput) and 10-17x behind FFTW_MEASURE; on Linux aarch64 (2026-09-03, v1.0.1) it beat KissFFT at every size (e.g. N=1024 13.8 vs 21.7 us, N=65536 1620 vs 2735 us). A Bluestein AVX inverse-twiddle double-conjugation bug was fixed on 2026-08-22, after the v1.0.0 release.

FFTW3-shaped planner API and FFTW compatibility header, split-radix DIF with mixed radix 3/5/7, Rader and Bluestein, DCT/DST types 2-4, NEON, AVX2 and AVX-512 paths selected at compile time.

## Maintenance

Young single-author project (7 commits, 2026-02-20 to 2026-08-22, 0 stars, MIT); small enough to vendor as one header, but treat it as experimental and expect FFTW-class libraries to be much faster on x86.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** The README table (v1.0.0) times Notorious-FFT against minfft in the same binary built from the public benchmarks/bench.c (CLOCK_MONOTONIC, warm-up, 100-100000 reps); it names the compiler (GCC 11.4.0), flags (-O3 -march=armv8.2-a+fp16) and CPU (Cortex-A78AE, Jetson Orin), so it meets A. Every number in claimed_speedup appears in the table.
- **Verifier notes:** Numbers and metadata check out (MIT, 0 stars, not a fork, last commit 2026-08-22). Tier A rests on a weak baseline (minfft); the FastAndFourier README shows it losing to KissFFT on x86 and beating it on aarch64, worth recording as a shortcoming.
- **Fields the verifier corrected:** `caveats`
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/NotoriousLOB/Notorious-FFT/HEAD/README.md>
  - <https://github.com/NotoriousLOB/Notorious-FFT>
  - <https://github.com/NotoriousLOB/Notorious-FFT/commits>
  - <https://github.com/NotoriousLOB/Notorious-FFT/tree/master/benchmarks>
  - <https://raw.githubusercontent.com/NotoriousLOB/Notorious-FFT/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/NotoriousLOB/Notorious-FFT/HEAD/benchmarks/bench.c>
  - <https://raw.githubusercontent.com/NotoriousLOB/Notorious-FFT/HEAD/include/notorious_fft.h>
  - <https://raw.githubusercontent.com/NotoriousLOB/FastAndFourier/HEAD/benchmarks/README.md>
- **Sources the enricher read:**
  - <https://github.com/NotoriousLOB/Notorious-FFT>
  - <https://github.com/NotoriousLOB/Notorious-FFT/commits>
  - <https://raw.githubusercontent.com/NotoriousLOB/Notorious-FFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/NotoriousLOB/Notorious-FFT/HEAD/benchmarks/README.md>
  - <https://raw.githubusercontent.com/NotoriousLOB/Notorious-FFT/HEAD/benchmarks/bench.c>
  - <https://raw.githubusercontent.com/NotoriousLOB/Notorious-FFT/HEAD/include/notorious_fft.h>
  - <https://raw.githubusercontent.com/NotoriousLOB/Notorious-FFT/HEAD/include/notorious_fft_fftw.h>
  - <https://raw.githubusercontent.com/NotoriousLOB/Notorious-FFT/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/NotoriousLOB/Notorious-FFT/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/NotoriousLOB/FastAndFourier/HEAD/benchmarks/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/notoriouslob/notorious-fft`) · [data/wave8/enrich/raw/github_com_notoriouslob_notorious_fft.json](../../../data/wave8/enrich/raw/github_com_notoriouslob_notorious_fft.json) (enrichment confidence 0.75)

</details>
