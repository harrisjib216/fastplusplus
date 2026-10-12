# meow_fft

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `0BSD` · 🟡 stale

> Single-header C99 float FFT (0BSD), scalar radix-8 mixed-radix, 1.1-1.5x faster than KissFFT on power-of-two sizes.

| | |
|---|---|
| **Beats** | KissFFT |
| **Claimed result** | gemmi C2C (GCC8 -O3, i7-5600U): n=256 2120 vs KissFFT 2536 ns, n=384 4718 vs 4929, n=480 5745 vs 6030, n=512 4342 vs 6553 ns (\~1.04-1.5x, derived from page data). R2C mixed: n=480 3591 vs 3140 ns (slower), n=512 2660 vs 2985 ns. Author README (i7-4790, GCC -O2 -g): N=1024 8.89 vs 13.12 us, N=8192 84.72 vs 119.38 us; N=64 slower (0.73 vs 0.58 us). |
| **Workload** | Complex FFT N=1024 and N=8192 vs kiss_fft and pffft |
| **Metric** | throughput |
| **Hardware** | gemmi: Intel i7-5600U; author README: Intel i7-4790 @ 3.60GHz (also Core2 Duo P8400, ARMv7) |
| **Compiler and flags** | gemmi: GCC 8 -O3; author README: GCC 6.3.1 -O2 -g |
| **Adoption** | 126 stars |
| **Last commit** | 2024-07-01 |
| **Links** | [repository](https://github.com/JodiTheTigger/meow_fft) · [benchmark](https://github.com/project-gemmi/benchmarking-fft) |

## Verdict

gemmi's independent single-precision shootout (1d.cpp, GCC 8 -O3, Intel i7-5600U) timed meow_fft complex FFTs at 2120/4718/5745/4342 ns against KissFFT's 2536/4929/6030/6553 ns for n=256/384/480/512 (1.04-1.51x, derived from page data). In the same run its real FFT was slower at n=480 (3591 against 3140 ns) and faster at n=512 (2660 against 2985 ns). The author's own table (i7-4790, GCC 6.3.1 -O2 -g, benchmark code not published) shows N=1024 at 8.89 against 13.12 us and N=8192 at 84.72 against 119.38 us; accuracy after a round trip was about the same as KissFFT's.

## Use it when

- You want a GPL-free FFT as one 0BSD file with no build system, and KissFFT is what you would use otherwise
- Power-of-two float transforms from about 256 to 32768 points (for example audio frames): the author's i7-4790 table shows 1.07-1.50x over KissFFT, and gemmi measured 1.2-1.5x at n=256 and 512
- Targets where SIMD code is unavailable or unwanted (scalar builds, WebAssembly without SIMD, ARMv7): on a 1 GHz ARMv7 the author measured 1.1-1.75x over KissFFT for N=64-32768
- Reading a compact, commented mixed-radix FFT to learn how one is put together (one of the author's stated goals)

## Skip it when

- Whenever a SIMD FFT is allowed: pffft ran N=1024 in 2.19 us against meow's 8.89 us (i7-4790), and muFFT, FFTW and vDSP are also faster according to the author
- When a scalar FFT faster than KissFFT is enough: in gemmi's C2C run, PocketFFT (scalar, double precision) and pffft or FFTW with SIMD disabled all beat meow at every size tested (for example n=256: 1690-1826 ns against 2120 ns)
- Very small or non-power-of-two sizes: KissFFT is faster at N=64 (0.58 against 0.73 us), level or faster at N=100 and 500, and faster for gemmi's real FFT at n=480 (3140 against 3591 ns)
- Sizes with prime factors other than 2, 3 and 5: radix 7 and larger primes go through an O(p^2) generic DFT, and a prime factor above 2048 aborts the process
- Double precision, 2D/3D transforms, odd-length real FFTs or in-place transforms: none is supported

## How it is fast

It is a recursive decimation-in-time mixed-radix FFT that factors N greedily by 8, 5, 4, 3 and 2. Each stage's twiddles are precomputed in the order they are read. The author says the radix-8 butterfly, generated with FFTW's codelet generator, is the only reason it beats KissFFT. The real-input transform runs a half-length complex FFT and then a symmetric post-processing mix (the two-for-one trick). The code uses no explicit SIMD.

## Compared with alternatives

Against the catalogued siblings, muFFT and PFFFT are 3.5-6.5x faster with SIMD in gemmi's run, and PocketFFT (C++ branch) is faster even in scalar code while adding double precision, any size via Bluestein, and 2D/3D. Pick meow_fft only when the constraints are a single 0BSD C99 file and arbitrary 1D float sizes (PFFFT's SIMD path needs multiples of 16 complex or 32 real), and your sizes are mostly powers of two.

## Integration

| | |
|---|---|
| **Form** | header-only |
| **Dependencies** | none (libc and libm only) |
| **Minimum toolchain** | C99 (also compiles as C++ via extern "C" guards); MSVC before VS2022 (_MSC_VER &lt; 1930) gets a volatile work-around for optimiser bugs |
| **Platforms** | any (portable scalar C); author benchmarked x86-64 (i7-4790, Core2 Duo P8400) and ARMv7 |
| **Thread safety** | not documented; the transforms take the plan as const and keep no global state (scratch is on the stack or in caller buffers), so one plan can probably be shared across threads |
| **Drop-in for the baseline** | no |

## Gotchas

- The real FFT writes N/2 complex values and stores the Nyquist bin's real part in out[0].j. The header comment still says countof(out) == countof(in), which predates the July 2024 change, and issue #14 (open) asks how to read the output. Inverse transforms are not scaled, so divide by N yourself.
- The plan generator accepts any N &gt;= 2 (complex), or any even N &gt;= 4 (real), and returns 0 otherwise. A prime factor above 2048 is not rejected at plan time: meow_dft_n_dit calls abort() during the transform (for example N = 4099). meow_fft_is_slow() reports when the slow generic DFT will be used.
- The plan is one caller-allocated block holding absolute pointers into itself, so do not memcpy or realloc it; allocate it where it will live. The internal helpers (meow_radix_2_dit, meow_add and others) have external linkage, and several are plain C99 `inline`, so define MEOW_FFT_IMPLEMENTATION in exactly one translation unit. Per C99 inline rules, an unoptimised C build may fail to link (from reading the code, not tested).
- Compiler flags can move performance either way: the author saw -march=native speed up sizes above 2048 but run sizes below 2048 twice as slow, and got mixed results with -ffast-math. The README example (void main(char\*\* argv, int argv), &lt;malloc.h&gt;) does not compile as written.

## Known shortcomings

- Slower than KissFFT at N=64 and on real-to-complex n=480; author says his FFTW column is wrong; stale (2024-07-01).
- Robustness bug: N with a prime factor &gt;2048 (e.g. 4099) is not rejected at plan time and the transform calls abort(); slower than KissFFT at N=64, R2C n=480 and some non-power-of-two sizes; header comment on real-FFT output size stale (#14 open); README example does not compile; plain C99 inline helpers may fail to link at -O0 (code reading).

## Caveats and trade-offs

Scalar code only (no SIMD); author states it is slower than pffft, FFTW, muFFT, vDSP. Margin over KissFFT is small at many sizes; slower than KissFFT for N=64 (author) and R2C n=480 (gemmi). Author's FFTW3 column is flagged by the author as wrong (Hartley transform). Gemmi did not check accuracy. Repo has no benchmark code; gemmi plan setup times are similar to KissFFT.

C99 single header, no explicit SIMD, radix-8 kernel; slower than pffft, muFFT, vDSP and FFTW by author's own statement; no 2D/3D.

## Maintenance

Stale: 15 commits, the last in July 2024 (real-FFT buffers halved), with two open PRs unmerged, including a 2025 sign-type fix. It is 0BSD and a single header, so it is easy to vendor and patch.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now A.
- **Tier reason:** Upgraded: the independent gemmi shootout (project-gemmi/benchmarking-fft, code 1d.cpp/1d-r.cpp, GCC8 -O3, i7-5600U, single precision) shows meow_fft faster than KissFFT for C2C at n=256/384/480/512. The author's own README table (i7-4790, GCC 6.3.1 -O2 -g) has no public benchmark code, so on its own it would be C.
- **Verifier notes:** Tier upgraded C/B -&gt; A based on gemmi's reproducible third-party shootout. Baseline KissFFT is correct; win is modest (up to \~1.5x).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `last_commit`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/JodiTheTigger/meow_fft>
  - <https://raw.githubusercontent.com/JodiTheTigger/meow_fft/HEAD/README.md>
  - <https://github.com/JodiTheTigger/meow_fft/commits>
  - <https://raw.githubusercontent.com/project-gemmi/benchmarking-fft/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/JodiTheTigger/meow_fft>
  - <https://raw.githubusercontent.com/JodiTheTigger/meow_fft/HEAD/README.md>
  - <https://raw.githubusercontent.com/JodiTheTigger/meow_fft/HEAD/meow_fft.h>
  - <https://github.com/JodiTheTigger/meow_fft/commits>
  - <https://github.com/JodiTheTigger/meow_fft/issues?q=is%3Aissue>
  - <https://github.com/JodiTheTigger/meow_fft/issues/12>
  - <https://github.com/JodiTheTigger/meow_fft/issues/14>
  - <https://github.com/JodiTheTigger/meow_fft/pulls>
  - <https://github.com/JodiTheTigger/meow_fft/pull/15>
  - <https://raw.githubusercontent.com/project-gemmi/benchmarking-fft/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/jodithetigger/meow_fft`) · [data/wave8/enrich/raw/github_com_jodithetigger_meow_fft.json](../../../data/wave8/enrich/raw/github_com_jodithetigger_meow_fft.json) (enrichment confidence 0.75)

</details>
