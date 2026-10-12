# muFFT

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `MIT` · 🔴 abandoned

> Small MIT C99 single-precision power-of-two FFT with runtime SSE/SSE3/AVX dispatch; 5-9x faster than KissFFT, near FFTW.

| | |
|---|---|
| **Beats** | KissFFT |
| **Claimed result** | 1D C2C n=512: muFFT 719 ns (SIMD) / 4024 ns (no SIMD) vs KissFFT 6553 ns; 2D 256x256 muFFT NS 1092 us vs kissfft NS 1583 us. Versus FFTW3 (meas.) muFFT is competitive: 259 us vs 306 us (2D 256x256), 719 vs 588 ns (1D 512, slower) |
| **Workload** | 1D complex FFT n=512 and 2D complex FFT 256x256, single precision, in the gemmi shootout |
| **Metric** | throughput |
| **Hardware** | Intel i7-5600U, 4 threads @ 3200 MHz, L1 32K L2 256K L3 4096K |
| **Compiler and flags** | GCC 8 (g++-8) -O3 -Wall -Wextra -pedantic, no -march (per Makefile); FFTW3 from Ubuntu 18.04 packages |
| **Adoption** | 201 stars |
| **Last commit** | 2019-02-15 |
| **Links** | [repository](https://github.com/Themaister/muFFT) · [benchmark](https://github.com/project-gemmi/benchmarking-fft) |

## Verdict

The independent gemmi benchmark (public 1d.cpp/2d.cpp, GCC 8 -O3, i7-5600U, Ubuntu 18.04 FFTW packages, single precision) measured muFFT at 719 ns vs KissFFT 6553 ns for 1D C2C n=512, 4024 ns with SIMD disabled (1.6x like-for-like). In 2D 256x256 it took 259 us vs KissFFT 1583 us and FFTW measured-plan 306 us. 1D R2C n=512 took 511 ns vs FFTW meas. 681 ns and pffft 597 ns.

## Use it when

- Single-precision power-of-two FFTs of moderate size (hundreds to a few thousand points) on x86-64 where FFTW's GPL is not acceptable
- Block-based overlap-add FIR convolution for audio, including interleaved stereo signals and zero-padded inputs, via the built-in conv API
- Replacing KissFFT on x86: in the gemmi shootout (i7-5600U, GCC 8 -O3) 1D C2C n=512 took 719 ns against KissFFT's 6553 ns, and the 2D 256x256 transform took 259 us against 1583 us
- One portable binary that should use AVX where present and fall back to SSE or scalar code otherwise

## Skip it when

- Non-power-of-two sizes (n=384, 480 or primes): not supported; PocketFFT, pffft or FFTW cover them
- Double precision or 3D transforms: not implemented
- ARM/NEON targets: NEON was still listed as 'expected soon' when the last commit landed in 2019, so ARM gets the scalar path only
- Peak 1D throughput: FFTW with a measured plan was faster at n=512 (588 vs 719 ns) on the same machine
- Very large out-of-cache FFTs or tiny N=2/4/8 transforms: the README says neither is specially optimised

## How it is fast

The Stockham autosort formulation removes the bit-reversal permutation pass. Hand-vectorised radix-2, radix-4 and radix-8 butterflies come in separate no-SIMD, SSE, SSE3 and AVX translation units, and the widest set the CPU supports is picked at runtime. Decompositions are chosen statically, so there is no FFTW-style measuring planner. Real transforms run as an N/2 complex FFT plus a final butterfly pass.

## Compared with alternatives

Pick muFFT over PFFFT when you need 2D transforms or an AVX path (pffft is SSE/NEON-only and was \~1.7x slower at n=512 C2C SIMD), or a ready-made convolution API. Pick PocketFFT for arbitrary lengths, double precision, 3D or ARM, and VkFFT for GPUs.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none for the library (libm); FFTW3f via pkg-config only for the optional bench/test binaries |
| **Minimum toolchain** | C99; CMake 3.5+; GCC, Clang or MSVC |
| **Platforms** | any (scalar C); SIMD paths on x86/x86-64 only (SSE, SSE3, AVX) |
| **Thread safety** | Not documented. Each plan owns a scratch buffer (tmp_buffer) that execute writes to, so one plan must not run concurrently on several threads; use a plan per thread |
| **Drop-in for the baseline** | false — different API from KissFFT (plan/execute with aligned buffers); data layout is compatible |

## Gotchas

- Input and output buffers must be SIMD-aligned (use mufft_alloc/mufft_calloc/mufft_free), and execute declares them restrict, so in-place transforms are not supported
- Transforms are unnormalised, so forward followed by inverse scales by N; the convolution output, by contrast, is normalised
- Do not build with -ffast-math: the CMake file warns that the code relies on -0.0f behaviour
- The 2D R2C/C2R output uses a padded row stride for alignment, not the plain Nx/2+1 layout

## Known shortcomings

- 1D speedup compares SIMD muFFT with scalar KissFFT (fair scalar: 4024 vs 6553 ns); power-of-two sizes only; loses to FFTW at n=512; abandoned (2019-02-15).
- Power-of-two and single precision only, no 3D; no NEON (ARM gets scalar); SIMD-aligned out-of-place buffers only; one plan cannot run from several threads; measured FFTW faster for 1D C2C n=512 (588 vs 719 ns).

## Caveats and trade-offs

1D KissFFT figure (6553 ns) is scalar; SIMD muFFT vs scalar KissFFT inflates the ratio (muFFT NS 4024 ns vs 6553 ns is the like-for-like). 2D 256x256: muFFT 259 us vs kissfft 1583 us (SIMD) / muFFT NS 1092 us. Slower than FFTW meas. in 1D n=512 (719 vs 588 ns); power-of-two sizes only. GitHub shows MIT (COPYING is MIT; page also mentions GPL-2.0 dual licensing). No commits since Feb 2019.

Power-of-two only (n/a for 384/480); radix 4/8 only; SSE/SSE3/AVX paths, NEON planned; muFFT-bench/test binaries are GPL-2.0+ because of FFTW linkage.

## Maintenance

Abandoned since February 2019 (no NEON, no new sizes), but MIT-licensed, about 2.5 KLOC of C99 and easy to vendor; only the optional bench/test binaries fall under the GPL because they link FFTW.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** Third-party gemmi shootout with public benchmark code (1d.cpp, 2d.cpp, Makefile building libmuFFT SSE/SSE3/AVX variants and kissfft), GCC 8 -O3 stated, CPU i7-5600U stated; muFFT and KissFFT rows match the record.
- **Verifier notes:** Numbers verified on the gemmi README. Last commit 2019-02-15, so abandoned.
- **Fields the verifier corrected:** `last_commit`, `maintenance_status`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** gemmi shootout: 1D R2C n=512 511 vs FFTW 681 ns; 2D 256x256 259 vs 306 us
- **Pages the verifier opened:**
  - <https://github.com/project-gemmi/benchmarking-fft>
  - <https://raw.githubusercontent.com/project-gemmi/benchmarking-fft/HEAD/README.md>
  - <https://raw.githubusercontent.com/project-gemmi/benchmarking-fft/HEAD/Makefile>
  - <https://github.com/Themaister/muFFT>
  - <https://raw.githubusercontent.com/Themaister/muFFT/HEAD/COPYING>
  - <https://github.com/Themaister/muFFT/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/Themaister/muFFT/HEAD/README.md>
  - <https://raw.githubusercontent.com/Themaister/muFFT/HEAD/fft.h>
  - <https://raw.githubusercontent.com/Themaister/muFFT/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/Themaister/muFFT/HEAD/fft.c>
  - <https://raw.githubusercontent.com/project-gemmi/benchmarking-fft/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/themaister/mufft`) · [data/wave8/enrich/raw/github_com_themaister_mufft.json](../../../data/wave8/enrich/raw/github_com_themaister_mufft.json) (enrichment confidence 0.8)

</details>
