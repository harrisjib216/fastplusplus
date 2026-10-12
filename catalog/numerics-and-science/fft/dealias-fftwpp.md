# FFTW++ (implicit dealiased convolutions on FFTW3)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [FFT](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `LGPL-3.0-or-later` · 🟢 active

> C++ layer over FFTW3 whose implicitly/hybrid-dealiased convolutions beat explicit zero-padded FFT convolutions in 2D and 3D.

| | |
|---|---|
| **Beats** | FFTW 3 with explicit zero-padded convolutions (and FFTW's MPI transpose for the distributed code) |
| **Claimed result** | README: 'in 2D and 3D implicit zero-padding substantially reduces memory usage and computation time' (no numbers on the repository). Per a WebSearch summary of Bowman and Roberts, SIAM J. Sci. Comput. 33:1 (2011) / arXiv 1008.1366 (the paper itself was not opened): increased data locality 'significantly enhanced performance by as much as a factor of 2', and an implicit complex convolution needs one-half the memory of a zero-padded one in 2D and one-quarter in 3D (centered Hermitian: 2/3 in 2D, 4/9 in 3D). |
| **Workload** | 2D and 3D dealiased (zero-padded) convolutions and FFTs built on FFTW3; implicit padding avoids transforming the padded zeros. |
| **Metric** | throughput |
| **Adoption** | 140 stars, 17 forks; vcpkg port fftwpp (version-date 2019-12-19) |
| **Last commit** | 2026-08-12 |
| **Links** | [repository](https://github.com/dealias/fftwpp) · [benchmark](https://arxiv.org/pdf/1008.1366) |

## Verdict

The baseline is explicit zero padding run through the same FFTW plans (tests/timing.py has -r implicit/explicit run types for the hybridconv\* tests), so the win is algorithmic rather than a faster FFT kernel. Per WebSearch summaries of the papers (not opened; hosts blocked), the 2011 SIAM paper reports compute savings of about a factor of two from data locality and memory 1/2^(d-1) of explicit padding in d dimensions, and the 2024 hybrid paper reports matching or beating explicit dealiasing in 1-D and greatly outperforming it in 2-D and 3-D; no CPU, compiler or result data are committed to the repository.

## Use it when

- Pseudospectral PDE solvers (for example Navier-Stokes or turbulence codes) that evaluate quadratic nonlinearities as dealiased convolutions with the 2/3 or 1/2 padding rule, in 2-D or 3-D, where explicit zero padding costs memory and time.
- Large 3-D convolutions that barely fit in RAM: per the 2011 paper implicit padding asymptotically needs 1/2^(d-1) of the memory of explicit padding.
- Centered Hermitian-symmetric (real-field) spectral data, which has dedicated routines (fftPadHermitian, Convolution2/3 with Hermitian symmetrization helpers).
- Distributed-memory runs with MPI plus OpenMP where FFTW's own MPI transpose is the bottleneck.
- You want a small C++ RAII interface around double-precision FFTW3 with automatic wisdom and threading, regardless of convolutions.

## Skip it when

- Plain FFTs: the fft classes call FFTW plans directly, so there is no speedup over FFTW itself.
- Single precision, GPUs or non-FFTW back ends: everything is double-precision FFTW3 (no fftwf calls) on the CPU.
- Closed-source products without a commercial FFTW licence: FFTW++ is LGPL-3.0-or-later but links FFTW, which is GPL.
- 1-D convolutions where speed is the goal: the 2024 paper reports hybrid dealiasing only matching or modestly beating explicit padding in 1-D; the big gains are in 2-D and 3-D.
- Code that must not exit the process on error or write files: invalid parameters and failed plans call exit(), and planning reads and writes a wisdom file in the working directory.

## How it is fast

Implicit dealiasing (Bowman and Roberts, SIAM J. Sci. Comput. 2011) never transforms the padded zeros: it splits the padded transform into residue subtransforms and decouples work arrays from data arrays, so higher-dimensional convolutions need much less memory and gain data locality. Hybrid dealiasing (Murasko and Bowman, SIAM J. Sci. Comput. 2024) generalises this to arbitrary padding ratios, with explicit padding as a special case, and picks the subtransform size m, the number of residues processed at once D and in-place versus out-of-place by timing candidate configurations when the fftPad object is constructed. Multidimensional convolutions are decomposed into lower-dimensional ones, and the MPI code uses an adaptive hybrid OpenMP/MPI transpose instead of FFTW's MPI transpose.

## Compared with alternatives

Among the catalogued FFT entries it is the only CPU library aimed at dealiased convolutions for spectral solvers; pick FlashFFTConv instead for long 1-D convolutions in deep learning on NVIDIA GPUs, and FINUFFT when samples are nonuniform rather than needing a padded uniform convolution. For plain FFTs, a faster kernel such as Admiral or SFFT3 (3-D FFT built from FFTW 1-D transforms) matters more than this wrapper.

## Integration

| | |
|---|---|
| **Form** | static lib |
| **Dependencies** | FFTW3 double precision plus libfftw3_omp (CMake requires both), OpenMP; MPI for mpi/; optional Array class (Array.h is bundled); Python, C and Fortran wrappers optional |
| **Minimum toolchain** | C++11 (CMake sets CMAKE_CXX_STANDARD 11), CMake 3.15; flag sets for GCC, Clang, AppleClang, Intel and IBM XL |
| **Platforms** | Linux and macOS documented in CMake; x86-64 builds use -msse2 -march=native and an SSE2 complex-multiply path (cmult-sse2.h) with a generic fallback; Windows builds have needed fixes (issue #17) |
| **Thread safety** | not documented; transforms and convolutions run multithreaded internally (OpenMP, fftw::maxthreads), but plan construction goes through FFTW's planner and a shared wisdom file without calling fftw_make_planner_thread_safe, so construct objects from one thread |
| **Drop-in for the baseline** | partial — the FFT wrappers sit on FFTW but use their own C++ classes; the dealiased convolutions replace hand-written explicit zero-padding code and need the Application/fftPad/Convolution API |

## Gotchas

- Constructing an fftPad object runs a timing search over subtransform sizes (repeated timed convolutions until the median stabilises within 2%), so construction is slow and the chosen m and D can differ between runs and machines; pass m, D and I to Application to pin them.
- Planner() loads and saves FFTW wisdom in a file named wisdom3.txt in the current working directory (written via a temporary wisdom3.txt_&lt;pid&gt; and renamed), and fftw::effort defaults to FFTW_MEASURE.
- Issue #26 (fixed 2026-08-12): Hermitian two-loop convolutions with more inputs than outputs (A &gt; B, for example 15 to 3 channels) returned outputs with about 50% relative error; use a build from after that fix.
- The CMake flags are -Ofast -ffast-math -march=native, so default builds are not portable across CPUs and relax IEEE semantics; the vcpkg port is a 2019 snapshot that predates the hybrid convolution code entirely.

## Known shortcomings

- Numbers only in papers (unreadable here); the 'up to 2x' comes from a search summary.
- Correctness bug fixed: issue #26, Hermitian convolution with A&gt;B gave \~50% relative error until the 2026-08-12 fix; baseline is explicit padding through the library's own code; double precision only; plan creation writes wisdom3.txt to the working directory and errors call exit().

## Caveats and trade-offs

No numbers on the repository page; the speedup (up to about 2x over explicit zero-padded convolutions, plus 2-4x less memory in 2D/3D) comes from the peer-reviewed papers, seen here only through a WebSearch summary because arxiv.org, math.ualberta.ca, archive.org and doi.org are blocked in this container. The baseline is explicit zero padding implemented by the same authors on top of FFTW, so this is an algorithmic win for dealiased convolutions, not a faster FFT kernel. Timing scripts are public (tests/timing.py, tests/timing/timing) but no timing data, CPU, compiler or flags are committed. GitHub shows GPL-3.0 and LGPL-3.0 files (LICENSE, LICENSE.LESSER); the README states LGPL v3 or later. The vcpkg port is pinned to a 2019 snapshot.

Header library and MPI transposes on top of FFTW3 (so FFTW's GPL licence applies unless a commercial FFTW licence is used); the gain is specific to dealiased convolutions in 2D/3D, plain FFTs are plain FFTW calls; C, Fortran and Python wrappers for the convolution routines; mpi/fftw directory benchmarks the adaptive transpose against FFTW's MPI transpose.

## Maintenance

Actively maintained (2,942 commits, last commit 2026-08-12 fixing issue #26, header version 3.04) by its University of Alberta authors; LGPL-3.0-or-later, but any binary that links FFTW falls under the GPL unless FFTW is licensed commercially.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** The repository README has no numbers, but it cites three peer-reviewed papers (SIAM J. Sci. Comput. 2011 and 2024, J. Comput. Phys. 2018) that compare implicit against explicit zero-padded FFTW convolutions; a WebSearch summary of the 2011 paper (arXiv 1008.1366) states the gain as 'by as much as a factor of 2'. Timing code is public (tests/timing.py, tests/timing/timing, hybridconv\* tests) but no CPU, compiler or flags are given on any page opened, so not A.
- **Verifier notes:** README and the tests/ and tests/timing/ listings checked; no committed results. Papers unreachable (EGRESS_BLOCKED for math.ualberta.ca and archive.org); the 'factor of 2' figure comes from a WebSearch summary, so an enricher with paper access should confirm it. Metadata matches: 140 stars, not a fork or archived, last commit 2026-08-12 (fix for issue #26).
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/dealias/fftwpp>
  - <https://raw.githubusercontent.com/dealias/fftwpp/HEAD/README.md>
  - <https://github.com/dealias/fftwpp/commits>
  - <https://github.com/dealias/fftwpp/tree/master/tests>
  - <https://github.com/dealias/fftwpp/tree/master/tests/timing>
  - <https://raw.githubusercontent.com/dealias/fftwpp/HEAD/LICENSE.LESSER>
  - <https://raw.githubusercontent.com/microsoft/vcpkg/master/ports/fftwpp/vcpkg.json>
- **Sources the enricher read:**
  - <https://github.com/dealias/fftwpp>
  - <https://raw.githubusercontent.com/dealias/fftwpp/HEAD/README.md>
  - <https://raw.githubusercontent.com/dealias/fftwpp/HEAD/CMakeLists.txt>
  - <https://raw.githubusercontent.com/dealias/fftwpp/HEAD/fftw++.h>
  - <https://raw.githubusercontent.com/dealias/fftwpp/HEAD/fftw++.cc>
  - <https://raw.githubusercontent.com/dealias/fftwpp/HEAD/convolve.h>
  - <https://raw.githubusercontent.com/dealias/fftwpp/HEAD/convolve.cc>
  - <https://raw.githubusercontent.com/dealias/fftwpp/HEAD/parallel.h>
  - <https://raw.githubusercontent.com/dealias/fftwpp/HEAD/cmult-sse2.h>
  - <https://raw.githubusercontent.com/dealias/fftwpp/HEAD/TODO>
  - <https://raw.githubusercontent.com/dealias/fftwpp/HEAD/examples/exampleconv2.cc>
  - <https://raw.githubusercontent.com/dealias/fftwpp/HEAD/tests/timing.py>
  - <https://raw.githubusercontent.com/dealias/fftwpp/HEAD/tests/options.cc>
  - <https://raw.githubusercontent.com/dealias/fftwpp/HEAD/tests/hybridconv2.cc>
  - <https://github.com/dealias/fftwpp/issues?q=is%3Aissue>
  - <https://github.com/dealias/fftwpp/issues/26>
  - <https://github.com/dealias/fftwpp/issues/23>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/dealias/fftwpp`) · [data/wave8/enrich/raw/github_com_dealias_fftwpp.json](../../../data/wave8/enrich/raw/github_com_dealias_fftwpp.json) (enrichment confidence 0.7)

</details>
