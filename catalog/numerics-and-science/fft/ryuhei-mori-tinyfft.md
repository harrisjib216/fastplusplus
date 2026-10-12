# tinyfft

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `BSD-2-Clause` · 🔴 abandoned

> Two tiny C files for power-of-two complex FFT and real convolution; author says the AVX version beats FFTW_MEASURE at 2^17-2^20.

| | |
|---|---|
| **Beats** | FFTW3 (FFTW_MEASURE planner) |
| **Claimed result** | README: 'Empirically, for vectors of length between 2^17 and 2^20, Tiny FFT is faster than FFTW3 with FFTW_MEASURE. For other cases, Tiny FFT is slower than FFTW3.' No numbers are given anywhere in the repo. |
| **Workload** | In-place power-of-two complex double FFT (AVX variant) at lengths 2^17 to 2^20; the README gives no further workload detail. |
| **Metric** | throughput |
| **Compiler and flags** | README build lines only: 'clang -O3 example.c tinyfft.c -lm' and 'clang -O3 example.c tinyfft_avx.c -lm -march=native'; the flags used for the FFTW comparison are not stated. |
| **Adoption** | 15 stars |
| **Last commit** | 2018-07-24 |
| **Links** | [repository](https://github.com/ryuhei-mori/tinyfft) · [benchmark](https://github.com/ryuhei-mori/tinyfft) |

## Verdict

There is only one claim, a single README sentence with no numbers: the AVX variant is 'faster than FFTW3 with FFTW_MEASURE' for lengths 2^17 to 2^20 and slower for all other lengths. No benchmark program, CPU, compiler version or FFTW version is published, and the comparison skips the bit-reversal permutation that FFTW performs.

## Use it when

- FFT-based convolution or polynomial/big-integer multiplication on power-of-two sizes, where bit-reversed spectra never need to be read
- Lengths around 2^17 to 2^20 on an x86 CPU with AVX and FMA3, the only range where the author says it beats FFTW3 with FFTW_MEASURE
- Projects that cannot take FFTW's GPL license or its build: BSD-2-Clause, two .c files and no dependencies beyond libm
- Contest or teaching code that needs a readable radix-4 FFT of about 130 lines (scalar) or 340 lines (AVX)

## Skip it when

- Any size outside 2^17-2^20: by the author's own README it is slower than FFTW3 there, and no numbers are published for any size
- Code that needs natural-order spectra, non-power-of-two lengths, single precision, real-input transforms, multi-dimensional transforms or threads; none of these are provided
- Builds for CPUs without FMA3, or for non-x86 targets, using the AVX variant: it calls _mm256_fmadd_pd and _mm256_fmsub_pd (FMA3), not plain AVX as the README implies
- Very small transforms in the AVX variant: for odd k the radix-2 stage always loads and stores 4 doubles, so k=1 (and tfft_convolver_avx with k=2, which calls the inverse at k=1) reads and writes past the arrays (read from the source, not reported upstream)
- Projects that need upstream support: last commit 2018-07-24, 19 commits, no tests, no benchmark program and no releases

## How it is fast

An iterative in-place radix-4 transform, with one radix-2 stage when k is odd. Input is in natural order and output is in bit-reversed order, and the twiddle table is stored in bit-reversed order (built recursively by tfft_genw), so each butterfly block uses one twiddle triple. The AVX file broadcasts that triple and runs the inner loop four doubles at a time on split real/imaginary arrays, using FMA for the complex multiplies. The inverse runs the stages in reverse, so fft, pointwise product and ifft never need a bit-reversal permutation. tfft_convolver adds the 'two real sequences in one complex FFT' trick and finishes with a half-length inverse. Large sizes stay competitive because the code is short and streams through memory; there is no cache blocking or codelet generation like FFTW's (inferred from the source).

## Compared with alternatives

Pick tinyfft over minfft, meow_fft or PocketFFT only when you want one small BSD file for power-of-two convolution and bit-reversed spectra are acceptable. For a general FFT with natural-order output, any size or measured wins over KissFFT and FFTW, PocketFFT, PFFFT or meow_fft are better documented.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (libm; &lt;immintrin.h&gt; for the AVX file) |
| **Minimum toolchain** | C99 compiler with &lt;complex.h&gt; (README builds with clang -O3); the AVX file needs AVX and FMA enabled (-mavx -mfma or -march=native). MSVC lacks C99 double complex, so it is not usable as-is there. |
| **Platforms** | Scalar file: any C99 target. AVX file: x86-64 with AVX and FMA3 (Intel Haswell or newer, AMD Piledriver/Zen or newer). |
| **Thread safety** | not documented; the functions keep no global state and only read the twiddle table, so separate buffers can be transformed concurrently with a shared table (inferred from the source) |
| **Drop-in for the baseline** | no |

## Gotchas

- Output of tfft_fft and tfft_fft_avx is in bit-reversed order and tfft_ifft is unnormalized: example.c divides by 2^k by hand, while tfft_convolver scales internally by 1/(4m)
- The AVX file uses aligned _mm256_load_pd and _mm256_store_pd, so xr and xi must be 32-byte aligned (aligned_alloc or posix_memalign), or it crashes
- The headers use C99 'double complex' and have no extern "C" guards, so they do not compile when included from C++; compile the .c files as C and declare the functions yourself (std::complex&lt;double&gt; has the same layout)
- Output layout of tfft_convolver (the length-2^k real result packed into 2^(k-1) complex slots, read back as real and imaginary parts in example.c) is not documented beyond the example; precision limits for exact integer convolution are not documented either

## Known shortcomings

- Verifier rejected as not notable at tier D: README speed claim with no numbers and no benchmark code.
- Output stays bit-reversed, so it is not like-for-like with FFTW. 15 stars; README claim has no numbers.
- AVX file (source reading): for odd k=1, and in the convolver at k=2, loads and stores 4 doubles past the arrays. Needs FMA3, not just AVX. Aligned loads require 32-byte buffers; the header does not compile as C++.

## Caveats and trade-offs

No benchmark program, results file, CPU model, compiler version or FFTW version is in the repo (example.c only reads integers from stdin and runs fft/ifft/convolution); the claim is a qualitative author statement and the README itself says 'comparable to FFTW3 for some length' near the top. Not like-for-like: tfft_fft and tfft_fft_avx leave the output in bit-reversed order (README), whereas FFTW returns natural order, so the comparison skips the permutation; fine for convolution, not for a general FFT. Narrow range (2^17 to 2^20), FFTW_MEASURE rather than FFTW_PATIENT or MKL, slower than FFTW at all other sizes. Last commit 2018-07-24, single author, 15 stars, 0 forks.

Tiny code base (tinyfft.c 132 lines, tinyfft_avx.c 342 lines). Power-of-two lengths only, double precision complex only, output left in bit-reversal order (so the transform is meant for convolution-style use, not a drop-in FFTW replacement). The AVX variant uses split real/imaginary arrays and needs -march=native. Slower than FFTW3 outside 2^17-2^20 by the author's own statement.

## Maintenance

Abandoned since 2018-07-24 (15 stars, 0 forks, no issues), but BSD-2-Clause and only two short C files, so it is easy to vendor and maintain yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): reject; tier before verification D, tier now D.
- **Tier reason:** The README states only that the AVX variant is faster than FFTW3 with FFTW_MEASURE for lengths 2^17 to 2^20 and slower elsewhere; there is no benchmark program, no numbers, no CPU, compiler version or FFTW version anywhere in the repo, so D.
- **Verifier notes:** Record accurate (BSD-2-Clause confirmed from LICENSE, 15 stars, 19 commits, last commit 2018-07-24). Rejected under the prompt's tier-D/not-notable rule; the claim is genuine, not fabricated, so the keep-and-document policy can keep it as a D entry with the bit-reversed-output caveat.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier; enrichment
- **Pages the verifier opened:**
  - <https://github.com/ryuhei-mori/tinyfft>
  - <https://github.com/ryuhei-mori/tinyfft/commits>
  - <https://raw.githubusercontent.com/ryuhei-mori/tinyfft/HEAD/README.md>
  - <https://raw.githubusercontent.com/ryuhei-mori/tinyfft/HEAD/example.c>
  - <https://raw.githubusercontent.com/ryuhei-mori/tinyfft/HEAD/tinyfft_avx.c>
  - <https://raw.githubusercontent.com/ryuhei-mori/tinyfft/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/ryuhei-mori/tinyfft>
  - <https://github.com/ryuhei-mori/tinyfft/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/ryuhei-mori/tinyfft/HEAD/README.md>
  - <https://raw.githubusercontent.com/ryuhei-mori/tinyfft/HEAD/tinyfft.h>
  - <https://raw.githubusercontent.com/ryuhei-mori/tinyfft/HEAD/tinyfft.c>
  - <https://raw.githubusercontent.com/ryuhei-mori/tinyfft/HEAD/tinyfft_avx.h>
  - <https://raw.githubusercontent.com/ryuhei-mori/tinyfft/HEAD/tinyfft_avx.c>
  - <https://raw.githubusercontent.com/ryuhei-mori/tinyfft/HEAD/example.c>
  - <https://raw.githubusercontent.com/ryuhei-mori/tinyfft/HEAD/LICENSE>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/ryuhei-mori/tinyfft`) · [data/wave8/enrich/raw/github_com_ryuhei_mori_tinyfft.json](../../../data/wave8/enrich/raw/github_com_ryuhei_mori_tinyfft.json) (enrichment confidence 0.75)

</details>
