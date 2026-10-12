# PFFFT (marton78 fork)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `C` · `FFTPACK/NCAR (UCAR) BSD-style license (no SPDX id; terms equivalent to BSD-3-Clause)` · 🟢 active

> Small BSD-licensed SIMD 1D FFT (float/double) plus fast convolution, about 5x faster than KissFFT, about half FFTW's speed.

| | |
|---|---|
| **Beats** | KissFFT |
| **Claimed result** | 1D C2C n=512: pffft 1255 ns (SIMD) vs KissFFT 6553 ns (derived 5.2x); pffft NS 3792 ns vs 6553 ns; R2C n=512: pffft 597 ns vs kissfft NS 2985 ns. Roughly on par with FFTW est.: 585 ns vs 321 ns at n=256 (slower than FFTW) |
| **Workload** | 1D complex FFT n=256..512 and real FFT, single precision, in the gemmi shootout |
| **Metric** | throughput |
| **Hardware** | Intel i7-5600U, 4 threads @ 3200 MHz, L1 32K L2 256K L3 4096K |
| **Compiler and flags** | GCC 8 (gcc-8) -O3 -Wall -Wextra -pedantic, no -march (per Makefile) |
| **Adoption** | 373 stars |
| **Last commit** | 2026-09-29 |
| **Links** | [repository](https://github.com/marton78/pffft) · [benchmark](https://github.com/project-gemmi/benchmarking-fft) |

## Verdict

In project-gemmi's benchmarking-fft (GCC 8 -O3, i7-5600U, single precision), Pommier's original pffft ran a 512-point complex FFT in 1255 ns with SSE vs KissFFT's 6553 ns (5.2x, derived), and 3792 ns with SIMD disabled. Real 512-point took 597 ns vs KissFFT 2985 ns. FFTW was faster at every size (588 ns measured at n=512). The fork's own additions were not measured there.

## Use it when

- Real-time audio/DSP on CPUs, where you need 1D float FFTs with no allocation in the transform call
- FIR filtering or convolution: the unordered transform plus pffft_zconvolve_accumulate skips the reorder pass
- Sizes of the form 2^a\*3^b\*5^c, best between 128 and 8192 points (per pffft.h)
- Proprietary products that cannot take FFTW's GPL and want a small library to vendor
- ARM NEON, PowerPC AltiVec or WebAssembly targets where KissFFT's scalar code is too slow

## Skip it when

- You need the fastest x86 FFT: FFTW measured 274-321 ns vs pffft 585 ns at n=256 complex in the gemmi benchmark; the README says the goal is only at least 50% of the fastest
- Lengths with prime factors above 5, or lengths below the SIMD minimum: there is no Bluestein fallback
- 2D/3D transforms, DCT/DST, or batched strided data: 1D only
- Double precision on NEON or SSE-only CPUs: the double SIMD paths are AVX and WASM only (scalar otherwise, per CMakeLists)
- 32-bit ARM built with GCC: the README measures much worse code and recommends Clang

## How it is fast

It is FFTPACK v4 (Swarztrauber) translated to C and rewritten so every butterfly works on 4-wide SIMD vectors (SSE1, AltiVec, NEON, WASM SIMD; AVX for double), using radix 2/3/4/5 codelets. Skipping the final reorder ('unordered' output) saves a pass when you only need to multiply spectra for convolution. Transforms do no allocation: the caller passes a work buffer, or stack is used.

## Compared with alternatives

Pick it over muFFT when you need a mature, allocation-free 1D real/complex FFT with built-in convolution and ARM/PowerPC/WASM SIMD. Pick it over PocketFFT for SIMD 1D transforms (PocketFFT's 1D path is scalar) when your lengths are 5-smooth. Use PocketFFT for multi-D, arbitrary lengths or DCT/DST.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | none (CMake build; FFTW/MKL/KissFFT/PocketFFT only for optional benchmarks) |
| **Minimum toolchain** | C compiler (C99-era) + CMake; C++ wrapper needs C++ with &lt;complex&gt;; exact minimum not documented |
| **Platforms** | x86/x86-64 (SSE1, AVX for double; FMA opt-in via -DTARGET_C_ARCH=haswell), ARM/AArch64 NEON incl. Apple Silicon, PowerPC AltiVec, WASM SIMD, scalar fallback elsewhere; open issue #55 reports a powerpc64le build failure |
| **Thread safety** | PFFFT_Setup is read-only after creation and may be shared by threads; each thread needs its own work buffer (per pffft.h) |
| **Drop-in for the baseline** | no |

## Gotchas

- All float buffers must be SIMD-aligned (16 bytes on x86/PowerPC); use pffft_aligned_malloc
- Transforms are unscaled: backward(forward(x)) = N\*x
- Real forward output packs DC and Nyquist into the first complex slot; pffft_transform output is in an internal order unless you use the _ordered variant or pffft_zreorder
- With work=NULL the transform uses the stack; large N on small thread stacks can overflow, so pass a heap work buffer

## Known shortcomings

- Benchmark measured Pommier's original bitbucket code, not this fork; FFTPACK/UCAR BSD-style license has no SPDX id; slower than FFTW.
- Lengths must be 2^a\*3^b\*5^c, no Bluestein fallback; 1D only; double-precision SIMD only on AVX and WASM; issue #55 powerpc64le build failure; GCC much slower on 32-bit ARM (README recommends Clang).

## Caveats and trade-offs

Benchmark measured Julien Pommier's original bitbucket pffft, not this fork's additions (double precision, etc.). SIMD pffft 1255 ns vs scalar KissFFT 6553 ns at n=512 C2C is 5.2x (derived from page data); like-for-like scalar pffft NS 3792 ns vs 6553 ns. Slower than FFTW (585 vs 321 ns est. at n=256). License is the FFTPACK/UCAR BSD-style text, not a standard SPDX id. Complex sizes must be multiples of 16 (real: 32) with SIMD.

Size must be a multiple of 16 (complex) or 32 (real) with SIMD; single precision (fork adds double); README says goal is &gt;=50% of fastest FFT, not records. Output ordering differs.

## Maintenance

Actively maintained (commits in 2026, upstream fixes cherry-picked and logged in the README); FFTPACK/UCAR BSD-style license allows vendoring into closed-source code.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification A, tier now A.
- **Tier reason:** gemmi shootout code (1d.cpp, 1d-r.cpp, Makefile compiling pffft/pffft.c with -O3) is public with GCC 8 and i7-5600U stated; pffft and KissFFT rows match the record. The measured code was Pommier's bitbucket original, whose single-precision core this fork carries.
- **Verifier notes:** Fork of Pommier's bitbucket pffft (README says so); active (commit 2026-09-29). hayguen/pffft_benchmarks could offer per-CPU results for the fork itself.
- **Fields the verifier corrected:** `is_fork_of`, `last_commit`, `maintenance_status`, `license`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/project-gemmi/benchmarking-fft>
  - <https://raw.githubusercontent.com/project-gemmi/benchmarking-fft/HEAD/README.md>
  - <https://raw.githubusercontent.com/project-gemmi/benchmarking-fft/HEAD/Makefile>
  - <https://github.com/marton78/pffft>
  - <https://raw.githubusercontent.com/marton78/pffft/HEAD/LICENSE.txt>
  - <https://github.com/marton78/pffft/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/marton78/pffft/HEAD/README.md>
  - <https://raw.githubusercontent.com/marton78/pffft/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/marton78/pffft/HEAD/include/pffft/pffft.h>
  - <https://raw.githubusercontent.com/marton78/pffft/HEAD/include/pffft/pffft.hpp>
  - <https://github.com/marton78/pffft/issues>
  - <https://raw.githubusercontent.com/project-gemmi/benchmarking-fft/HEAD/README.md>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/marton78/pffft`) · [data/wave8/enrich/raw/github_com_marton78_pffft.json](../../../data/wave8/enrich/raw/github_com_marton78_pffft.json) (enrichment confidence 0.8)

</details>
