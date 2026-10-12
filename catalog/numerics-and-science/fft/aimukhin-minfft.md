# minfft

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> Two-file C89 power-of-two FFT/DCT/DST library, about 2x KissFFT's speed; still slower than PocketFFT and FFTW.

| | |
|---|---|
| **Beats** | KissFFT (the README also plots PocketFFT and FFTW with SSE2 for reference) |
| **Claimed result** | README says its speed and accuracy are compared with 'the libraries of similar design - KissFFT and PocketFFT', with 'a highly optimized machine-specific version of the FFTW library' shown for reference; the plot has no numbers in text. Digitised from docs/speed.svg point coordinates (derived from page data, approximate; axes log2(N) 1-20 and Mflops): minfft is above KissFFT at every size, 1.36x to 4.83x, median about 1.96x (N=2^10: about 8,200 vs 5,000 Mflops). Versus PocketFFT minfft is faster only at N&lt;=2^6 and N=2^17 to 2^18 and about 0.74x to 0.96x elsewhere (median about 0.92x). Versus 'fftw sse2' about 0.34x to 0.89x (median about 0.56x). |
| **Workload** | One-dimensional double-precision in-place forward complex DFT of power-of-two size N = 2^1 to 2^20, speed in Mflops (plot docs/speed.svg). |
| **Metric** | throughput |
| **Adoption** | 53 stars |
| **Last commit** | 2025-08-11 |
| **Links** | [repository](https://github.com/aimukhin/minfft) · [benchmark](https://github.com/aimukhin/minfft) |

## Verdict

The author's gnuplot chart (benchFFT harness; per the README's test-environment section, removed in April 2024: GCC 13.2.1 -O2, one isolated core of an Intel Pentium Gold G5420 at 3.8 GHz, FFTW 3.3.10 with configure-chosen flags, KissFFT 1.3.1, PocketFFT 1.0) plots double-precision 1-D complex forward DFT Mflops for N = 2^1 to 2^20. Digitised, minfft runs 1.36x to 4.83x KissFFT (median about 1.96x), about 0.74x to 0.96x PocketFFT at most mid sizes, and 0.34x to 0.89x SSE2 FFTW (derived from page data).

## Use it when

- You want a small, dependency-free, MIT-licensed FFT you can vendor as two files (minfft.c/minfft.h) into C or C++, and power-of-two sizes are enough.
- Replacing KissFFT for power-of-two transforms: the author's plot shows minfft above KissFFT at every size from 2^1 to 2^20 (about 2x at N=1,024).
- You need DCT/DST types 2-4 or multi-dimensional real transforms with no FFTW dependency (FFTW is GPL or commercially licensed).
- Mixed C and Fortran 2003 codebases that want the same library from both languages.
- Accuracy matters: the accuracy plot puts its relative L2 error near FFTW's and PocketFFT's (about 2.9e-16 at N=2^20, about half of KissFFT's 5.8e-16; derived from page data).

## Skip it when

- Non-power-of-two lengths: every aux maker returns NULL unless N is a positive power of two.
- Peak throughput: the same plot has PocketFFT faster at 2^7 to 2^16 and 2^19 to 2^20, and SSE2 FFTW about 1.1x to 2.9x faster at every size; SIMD libraries (PFFFT, muFFT, KFR) or Notorious-FFT, which reports 1.08-1.13x over minfft, are faster.
- Sharing one plan across threads: the aux object holds a scratch buffer that every transform writes, even though the API takes a const pointer.
- Memory-tight settings: the README says it 'does not try to save memory'; a 1-D complex DFT aux takes 2N complex values, type-4 transforms 6N reals, and multi-dimensional transforms add a buffer as large as the input.

## How it is fast

The complex DFT is an explicitly recursive split-radix (2/4) decimation-in-frequency FFT with hand-unrolled leaves for N = 1, 2, 4 and 8 and a precomputed chain of twiddle factors stored in the aux object. Each level touches mostly adjacent memory, which the author credits for cache-friendliness. Real transforms and DCT/DST reduce to a half-length complex transform, and multi-dimensional transforms apply a strided 1-D routine along each axis through a temporary buffer. There is no explicit SIMD; the speed comes from fewer operations than KissFFT's mixed-radix code plus simple, compiler-friendly scalar loops.

## Compared with alternatives

Choose minfft over KissFFT or meow_fft when your sizes are powers of two and you want DCT/DST types 2-4 and multi-dimensional support in a tiny C89 drop-in. Choose PocketFFT for arbitrary lengths or more speed, PFFFT/muFFT for SIMD speed, and Notorious-FFT if you want a slightly faster derivative.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (libm only) |
| **Minimum toolchain** | C89 (C99 complex used if &lt;complex.h&gt; is included first); Fortran 2003 for the Fortran module; the author's benchmark build used GCC 13.2.1 |
| **Platforms** | any (portable scalar C, no SIMD or architecture-specific code) |
| **Thread safety** | Separate aux objects can be used concurrently (no global mutable state seen in minfft.c); a single aux must not be used by two threads at once because its scratch buffer is overwritten on every call. |
| **Drop-in for the baseline** | no |

## Gotchas

- Multi-dimensional inverse real DFT overwrites its input (README note), unlike the 1-D routines, which preserve input when run out of place.
- minfft_cmpl is C99 double complex only if `complex` is defined (i.e. &lt;complex.h&gt; was included before minfft.h); otherwise, including in C++, it is a double[2] array, binary-compatible with std::complex&lt;double&gt; but needing a cast.
- Dimensions for the 2-D/3-D aux makers are given in C (row-major) order; Fortran callers must pass them reversed.
- Transforms are unnormalized like FFTW (no 1/N factor anywhere in minfft.c); scale the inverse yourself.

## Known shortcomings

- Beats KissFFT 1.36-4.83x but is \~0.92x PocketFFT and \~0.56x FFTW (sse2) per its own SVG plot; no bench code, CPU or flags; stale (2025-08-11).
- A README test-environment section removed in commit 82917dd gives benchFFT, GCC 13.2.1 -O2, Pentium Gold G5420 isolated core, FFTW 3.3.10, KissFFT 1.3.1, PocketFFT 1.0, but minfft's benchFFT harness code is unpublished; one aux object is not safe to share across threads.

## Caveats and trade-offs

First-party plot only; no CPU model, compiler or flags, and no benchmark program is documented in the README, so numbers are read off an SVG and approximate. It loses to FFTW (SSE2) at all sizes and to PocketFFT at mid sizes, so the real claim is 'small and faster than KissFFT'.

Power-of-two sizes only; double precision by default (MINFFT_SINGLE for float); scalar C99 code with split-radix kernels, no explicit SIMD; also provides real DFT and DCT/DST types 2-4, multi-dimensional transforms, a Fortran 2003 interface; very small (two source files).

## Maintenance

Stale: code is mature and recent commits (to August 2025) are documentation only; MIT-licensed, two source files, one closed MSVC build issue, easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party gnuplot SVG (docs/speed.svg) compares minfft with KissFFT, PocketFFT and 'fftw sse2'; the repo ships no benchmark code and states no CPU, compiler or flags, so C.
- **Verifier notes:** My own digitisation of the SVG path data reproduces the record's ratios. Faster than KissFFT (a listed fft baseline), not faster than FFTW or PocketFFT at most sizes. Metadata confirmed: MIT, 53 stars, not a fork, last commit 2025-08-11 (stale); repo root holds only minfft.c/.h/.F03, docs and LICENSE, no bench code.
- **Fields the verifier corrected:** `claimed_speedup`
- **Pages the verifier opened:**
  - <https://github.com/aimukhin/minfft>
  - <https://github.com/aimukhin/minfft/commits>
  - <https://raw.githubusercontent.com/aimukhin/minfft/HEAD/README.md>
  - <https://raw.githubusercontent.com/aimukhin/minfft/HEAD/docs/speed.svg>
- **Sources the enricher read:**
  - <https://github.com/aimukhin/minfft/issues?q=is%3Aissue>
  - <https://github.com/aimukhin/minfft/commits>
  - <https://github.com/aimukhin/minfft/commit/82917ddc243d062768c29af8d197a7da5488d28e>
  - <https://raw.githubusercontent.com/aimukhin/minfft/HEAD/README.md>
  - <https://raw.githubusercontent.com/aimukhin/minfft/923838f/README.md>
  - <https://raw.githubusercontent.com/aimukhin/minfft/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/aimukhin/minfft/HEAD/minfft.h>
  - <https://raw.githubusercontent.com/aimukhin/minfft/HEAD/minfft.c>
  - <https://raw.githubusercontent.com/aimukhin/minfft/HEAD/minfft.F03>
  - <https://raw.githubusercontent.com/aimukhin/minfft/HEAD/docs/speed.svg>
  - <https://raw.githubusercontent.com/aimukhin/minfft/HEAD/docs/accuracy.svg>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/aimukhin/minfft`) · [data/wave8/enrich/raw/github_com_aimukhin_minfft.json](../../../data/wave8/enrich/raw/github_com_aimukhin_minfft.json) (enrichment confidence 0.85)

</details>
